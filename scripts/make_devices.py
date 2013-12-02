from shared.common import write_json, get_uint, get_bools, power
import math
from copy import copy
import itertools
import sys
import string
from settings import DEVICE_DIR

def set_wire(wires, name, from_list=[], to_list=[], is_dual=False):
    '''
    Make wire. If not dual, then returns a single wire.
    Else, returns 2 wires, up and down.
    '''
    if is_dual:
        for spin in ['down', 'up']:
            froms = [pin+spin for pin in from_list]
            tos = [pin+spin for pin in to_list]
            wire = {
                "name": name+spin,
                "from": froms,
                "to": tos
            }
            wires[name+spin]=wire
    else:
        wires[name] = {
            "name": name,
            "from": from_list,
            "to": to_list
        }

def get_wire(wires, name):
    for wire in wires:
        if wire['name'] == name:
            return wire
    return None


def append_bridge(devices, name, is_dual=False):
    if is_dual:
        for spin in ["down","up"]:
            device = {
                "name": name + spin,
                "type": "bridge"
            }
            devices.append(device)
    else:
        devices.append({
            "name": name,
            "type": "bridge"
        })


def new_device(device_name, device_type, is_dual=False):
    
    if is_dual:
        device_type += "dual"
    return {
        "name": device_name,
        "type": device_type
    }

def append_name(pin, text):
    pin_list = pin.split('/')
    pin_list[0] = pin_list[0]+text
    return string.join(pin_list,'/')


def make_input_and_nots(number_inputs, is_dual=False):
    '''
    Make input bridges, not gates, and wires from them.
    '''
    devices = []
    for index in range(number_inputs):
        i = str(index)
        name = "in"+i
        append_bridge(devices, name, is_dual)
        devices.append(new_device("not"+i, "not", is_dual ))
    return devices


def make_wires(number_inputs, is_dual=False):
    '''
    wire 
    '''
    wires = []
    for index in range(number_inputs):
        i = str(index)
        set_wire(wires, "wirein"+i, ["in"+i], ["not"+i+"/in"], is_dual)
        # wire from not
        set_wire(wires, "wirenot"+i, ["not"+i+"/out"], [], is_dual)
    return wires


def get_mux_type(number_selects, is_dual):
    number_inputs = int(math.pow(2, number_selects))
    device_type = "mux_"+str(number_inputs)
    if is_dual:
        device_type += "dual"
    return device_type


def get_selects(total):
    '''
    inputs = 2^selects
    2^selects + selects = total
    '''
    current = 0
    selects = 1
    while(True):
        current = power(selects) + selects
        if current >= total:
            break
        selects += 1

    return selects


def get_select_sets(lengths):
    select_sets = []
    count = 0
    for length in lengths:
        selects = []
        for index in range(length):
            selects.append('select'+str(count))
            count +=1
            select_sets.append(selects)
    return select_sets

def mux_truth(inputs):
    '''
    inputs, then selects
    '''
    number_selects = get_selects(len(inputs))
    number_ins = len(inputs) - number_selects
    #print "num selects: {0}, inputs: {1}".format(number_selects,inputs)
    ins = inputs[0:number_ins]
    selects = inputs[number_ins:]
    select_index = get_uint(selects)
    #print "select: ", select_index
    return [ins[select_index]]

def decoder_truth(inputs):
    '''
    convert inputs to a number.
    '''
    number = get_uint(inputs)
    outputs = [False]*int(math.pow(2, len(inputs)))
    outputs[number] = True
    return outputs


def make_mux(number_selects, is_dual):
    mux = new_mux(number_selects, is_dual)
    device_type = get_mux_type(number_selects, is_dual)
    device_file_path = str(DEVICE_DIR) + '/' + device_type + '.json'
    write_json(mux, device_file_path)


def new_mux_bad(number_selects, is_dual=False, in_pre='in', select_pre='select', out='out'):
    number_ins = power(number_selects)
    ins = []
    for index in range(number_ins):
        ins.append('in_'+str(index))
    for index in range(number_selects):
        ins.append('select_'+str(index))
    outs = ['out']

    return new_boolean(ins,outs, mux_truth, 'mux_'+str(number_ins))

def new_mux(number_selects, is_dual=False, in_pre='in', select_pre='select', out='out'):
    '''
    Make mux circuit.
    A mux circuit is the following:
    O = SA + not(S)B

    '''

    number_inputs = int(math.pow(2, number_selects))
    device_type = get_mux_type(number_selects, is_dual)
    devices = []
    
    for index in range(number_inputs):
        #inputs
        i = str(index)
        append_bridge(devices, in_pre+i, is_dual)
        # need and gates
        devices.append(new_device("and"+i, "and"+str(number_selects+1), is_dual))

    for index in range(number_selects):
        # selects
        i = str(index)
        append_bridge(devices, select_pre+i, is_dual)
        # nots
        devices.append(new_device("not"+i, "not", is_dual))

    # or device
    devices.append(new_device("or0", "or"+str(number_inputs), is_dual))
    append_bridge(devices, out, is_dual)

    # wires
    wires = {}
    for i in range(number_inputs):
        index = str(i)
        # input to and
        to_pin = "and"+index+"/in" + str(number_selects)
        wirein = "wirein"+index
        set_wire(wires, wirein, ["in"+index], [to_pin], is_dual)
        # and to or
        wireand = "wireand"+index
        set_wire(wires, wireand, ["and"+index+"/out"], ["or0/in"+index], is_dual)

    for index in range(number_selects):
        # from selector and from not selector
        i = str(index)
        wireselect = "wireselect"+i
        set_wire(wires, wireselect, ["select"+i], ["not"+i+"/in"], is_dual)
        wireselectnot = "wireselectnot"+i
        set_wire(wires, wireselectnot, ["not"+i+"/out"], [], is_dual)

    value_sets = itertools.product([False,True], repeat=number_selects)
    for value_set_index, value_set in enumerate(value_sets):
        value_set = reversed(value_set)
        vi = str(value_set_index)
        for index, value in enumerate(value_set):
            i = str(index)
            if value:
                wire_set(wires, 'wireselect'+i, 'to', 'and'+vi+"/in"+i, is_dual)
            else:
                wire_set(wires, 'wireselectnot'+i, 'to', 'and'+vi+"/in"+i, is_dual)

    set_wire(wires, "wireor0", ["or0/out"], ["out"], is_dual)
    wires_list = [wire for wire in wires.values()]
    return {
        "name": device_type+"0",
        "type": device_type,
        "wires": wires_list,
        "devices": devices
    }


def make_prim_part_dual(number_inputs):
    '''
    Only used by anddual and ordual devices.
    Create input bridges and not gates and bridges.
    '''
    devices = []
    wires = []
    for index in range(number_inputs):
        i = str(index)
        name = "in"+i
        append_bridge(devices, name, True)
        devices.append(new_device("not"+i+"down", "not"))
        devices.append(new_device("not"+i+"up", "not"))

        i = str(index)

        for spin in ['down', 'up']:
            set_wire(wires, "wirein"+i+spin, ["in"+i+spin], ["not"+i+spin+"/in"])
            # wire from not
            set_wire(wires, "wirenot"+i+spin, ["not"+i+spin+"/out"], [] )

    append_bridge(devices, "out", True)
    return devices, wires


def wire_set(wires, wire_name, direction, device_name, is_dual):
    if is_dual:
        for spin in ['down', 'up']:
            wire = wires[wire_name+spin]
            #wire = get_wire(wires, wire_name+spin)
            wire[direction].append(device_name+spin)
    else:
        #wire = get_wire(wires, wire_name)
        wire = wires[wire_name]
        wire[direction].append(device_name)

def new_decoder(number_ins, is_dual):
    ins = []
    for index in range(number_ins):
        ins.append('in_'+str(index))
    number_outs = power(number_ins)
    outs = []
    for index in range(number_outs):
        outs.append('o_'+str(index))
    return new_boolean(ins,outs, decoder_truth, 'decoder_'+str(number_ins))

def new_decoder_old(number_inputs, is_dual):
    number_outputs = int(math.pow(2, number_inputs))
    device_type = "decoder" + str(number_inputs)
    if is_dual:
        device_type += "dual"
    wires = []
    devices = []

    data = {
        "name": device_type+"0",
        "type": device_type,
        "wires": wires,
        "devices": devices
    }

    for index in range(number_inputs):
        # inputs
        i = str(index)
        name = "in"+i
        append_bridge(devices, name, is_dual)
        # not gate for every input
        devices.append(new_device("not"+i, "not", is_dual))

    for index in range(number_outputs):
        # outputs
        i = str(index)
        name = "out"+i
        append_bridge(devices,name, is_dual)
        # and gate for every output
        devices.append(new_device("and"+i, "and"+str(number_inputs), is_dual))

    wires.extend(make_wires(number_inputs, is_dual))

    for index in range(number_outputs):
        # wire from and to out
        i = str(index)
        set_wire(wires, "wireand"+i, ["and"+i+"/out"], ["out"+i], is_dual)

    value_sets = itertools.product([False,True], repeat=number_inputs)
    for value_set_index, value_set in enumerate(value_sets):
        # send wires to vi'th and gate. wires from in or not inputs.
        value_set = reversed(value_set)
        vi = str(value_set_index)

        for index, value in enumerate(value_set):
            i = str(index)
            if value:
                set_wire(wires, 'wirein'+i, 'to', 'and'+vi+"/in"+i, is_dual)
            else:
                set_wire(wires, 'wirenot'+i, 'to', 'and'+vi+"/in"+i, is_dual)

    return data


def make_decoder(number_inputs, is_dual=False):
    data = new_decoder(number_inputs, is_dual)
    device_file_path = str(DEVICE_DIR) + '/' + data['type'] + '.json'
    write_json(data, device_file_path)


def get_or(inputs):
    for value in inputs:
        if value: return True
    return False

def get_and(inputs):
    for value in inputs:
        if not value: return False
    return True


def new_boolean(inputs, outputs, function, device_type):
    '''
    inputs - list of input names
    outputs - list of output names
    function - a truth table. 
        it takes 1 parameter, a list of booleans.
        it return a list of booleans, one for each output.
    device_type - device_type
    ex: device = new_boolean(['a0','a1'], ['o0', o1'], add_truth, 'add1')
    '''
    devices = []
    wires = {}
    number_inputs = len(inputs)

    print "making inputs and nots"
    for in_name in inputs:
        # construct inputs
        append_bridge(devices, in_name)
        # not gates for every input
        not_name = 'not_'+in_name
        not_dev = new_device(not_name, 'not')
        devices.append(not_dev)

        # wire from input
        wire_in = 'wire_'+in_name
        set_wire(wires, wire_in, [in_name],[not_name+"/in"])
        # wire from not gate
        wire_not = 'wire_'+not_name
        set_wire(wires, wire_not, [not_name+"/out"],[])

    print "making outputs"
    for out_name in outputs:
        # outputs
        append_bridge(devices, out_name)

    # wire from input to and gates
    print "wiring inputs to gates"
    input_sets = itertools.product([False,True], repeat=number_inputs)
    output_sets= []
    for input_set_index, input_set in enumerate(input_sets):
        # the input_set is a single row on truth table
        set_i = str(input_set_index)
        output_sets.append(function(input_set))

        for index, value in enumerate(input_set):
            # each value in the input row need to be and'ed
            i = str(index)
            if value:
                wire = wires['wire_'+inputs[index]]
                wire['to'].append('and_'+set_i+"/in"+i)
                #wiredown = get_wire(wires, 'wirenot'+i+"down")
                #wireup = get_wire(wires, 'wirein'+i+"up")
            else:
                wire = wires['wire_not_'+inputs[index]]
                wire['to'].append('and_'+set_i+"/in"+i)
                #wiredown = get_wire(wires, 'wirein'+i+"down")
                #wireup = get_wire(wires, 'wirenot'+i+"up")
            #wire['to'].append('and_'+set_i+"/in"+str(2*index))
            #wireup['to'].append('and_'+set_i+"/in"+str(2*index+1))

    # each output is an or of one or more and gates.
    # ones is necessary to see whether an or gate is necessary.
    ones = [0]* len(outputs)  #track how many '1's for every output.
    zeros = [0]*len(outputs)
    print "counting ones"
    for output_set in output_sets:
        # for each row in truth table
        for index, output in enumerate(output_set):
            #for each output in row
            if output:
                ones[index] += 1
            #else:
            #    zeros[index] += 1

    print "create or gates and wire them"
    for index, one in enumerate(ones):
        # create or gate and connect to out
        i = "_"+str(index)
        if one > 1:
            devices.append(new_device("or_1"+i, "or"+str(one)))
            wire_name = "wire_or_1"+i
            wire = {
                "name": wire_name,
                "from": ["or_1"+i+"/out"],
                "to": [outputs[index]]
            }
            wires[wire_name] = [wire]

    for zero in zeros:
        i = "_"+str(index)
        if zero > 1:
            devices.append(new_device("or_0"+i, "or"+str(zero)))
            wire_name = "wire_or_0"+i
            wire = {
                "name": wire_name,
                "from": ["or_0"+i+"/out"],
                "to": ["outdown"]
            }
            wires[wire_name]= [wire]

    oneis = [0] * len(outputs)
    zeroi = 0

    # each row in truth table is an 'and' gate
    print "making and gates"
    number_rows = int(math.pow(2,number_inputs))
    for index in range(number_rows):
        i = "_"+str(index)
        and_name = "and"+i
        devices.append(new_device(and_name, "and"+str(number_inputs)))
        wire_name = 'wire_'+and_name
        set_wire(wires, wire_name, [and_name+"/out"], [])

    # and gate to or gate
    print "wire and gate to or gate"
    for set_index, output_set in enumerate(output_sets):
        # for each row in truth table
        set_i = str(set_index)
        for index, value in enumerate(output_set):
            # for each output in the row
            i = "_"+str(index)
            one = ones[index]
            if value:
                output = "out"+i if one <= 1 else "or_1"+i+"/in"+str(oneis[index])
                [wire] = wires["wire_and_"+set_i]
                wire['to'].append(output)
                oneis[index]+=1
            #else:
            #    output = "outdown" if zeros <= 1 else "or_0"+i+"/in"+str(zeroi)
            #    set_wire(wires, "wireand" + i, ["and"+i+"/out"], [output]))
            #    zeroi+=1

    print "setting wires"
    wire_list = []
    for wirel in wires.values():
        wire_list.append(wirel)

    return {
        "name": device_type+"0",
        "type": device_type,
        "wires": wire_list,
        "devices": devices
    }


def make_prim_dual(prim_type, number_inputs):
    devices = []
    wires = []
    device_type = prim_type+str(number_inputs)+"dual"
    (ds, ws) = make_prim_part_dual(number_inputs)
    devices.extend(ds)
    wires.extend(ws)
    value_sets = itertools.product([False,True], repeat=number_inputs)
    and_values= []
    logic_function = get_or if prim_type =='or' else get_and
    for value_set_index, value_set in enumerate(value_sets):
        set_i = str(value_set_index)
        and_values.append(logic_function(value_set))

        for index, value in enumerate(value_set):
            i = str(index)
            if value:
                wiredown = get_wire(wires, 'wirenot'+i+"down")
                wireup = get_wire(wires, 'wirein'+i+"up")
            else:
                wiredown = get_wire(wires, 'wirein'+i+"down")
                wireup = get_wire(wires, 'wirenot'+i+"up")
            wiredown['to'].append('and'+set_i+"/in"+str(2*index))
            wireup['to'].append('and'+set_i+"/in"+str(2*index+1))

    ones = 0
    zeros = 0
    for value in and_values:
        if value:
            ones += 1
        else:
            zeros += 1

    if ones > 1:
        devices.append(new_device("or1", "or"+str(ones)))
        wire = {
            "name": "wireor1",
            "from": ["or1/out"],
            "to": ["outup"]
        }
        wires.append(wire)
    if zeros > 1:
        devices.append(new_device("or0", "or"+str(zeros)))
        wire = {
            "name": "wireor0",
            "from": ["or0/out"],
            "to": ["outdown"]
        }
        wires.append(wire)

    onei = 0
    zeroi = 0
    for index, value in enumerate(and_values):
        i = str(index)
        devices.append(new_device("and"+i, "and"+str(number_inputs*2)))
        if value:
            output = "outup" if ones <= 1 else "or1/in"+str(onei)
            set_wire(wires, "wireand" + i, ["and"+i+"/out"], [output])
            onei+=1
        else:
            output = "outdown" if zeros <= 1 else "or0/in"+str(zeroi)
            set_wire(wires, "wireand" + i, ["and"+i+"/out"], [output])
            zeroi+=1
        #TODO only have or gate if there is more than one output

    data = {
        "name": device_type+"0",
        "type": device_type,
        "wires": wires,
        "devices": devices
    }

    device_file_path = str(DEVICE_DIR) + '/' + device_type + '.json'
    write_json(data, device_file_path)


def make_and(number_inputs):
    device_data = make_prim_part("and", number_inputs)
    wires = device_data['wires']
    set_wire(wires, "sourcetoswitch", ['source0'], ['switch0'])
    for index in range(number_inputs-1):
        i = str(index)
        inext = str(index+1)
        set_wire(wires, "wireswitch"+i+"to"+inext, ['switch'+i], ['switch'+inext])

    set_wire(wires, "switchtoresistor", ['switch'+str(number_inputs-1)], ['resistor0', 'out'])
    device_file_path = str(DEVICE_DIR) + '/' + 'and' + str(number_inputs) + '.json'
    write_json(device_data, device_file_path)


def make_or(number_inputs):
    device_data = make_prim_part("or", number_inputs)
    switch_list = ['switch'+str(i) for i in range(number_inputs)]
    wires = device_data['wires']
    set_wire(wires, "sourcetoswitch", ['source0'], switch_list)
    set_wire(wires, "switchtoresistor", switch_list, ['resistor0', 'out'])
    device_file_path = str(DEVICE_DIR) + '/' + 'or' + str(number_inputs) + '.json'
    write_json(device_data, device_file_path)


def make_prim_part(prim_type, number_inputs):
    device_type = prim_type+str(number_inputs)
    devices = []
    for index in range(number_inputs):
        #inputs
        i = str(index)
        append_bridge(devices,"in"+i)
        devices.append(new_device("switch"+i, "switch"))

    devices.append(new_device("source0", "source"))
    devices.append(new_device("resistor0", "resistor"))
    devices.append(new_device("ground0", "ground"))
    append_bridge(devices,"out")

    wires = []
    set_wire(wires, "wireresistor", ['resistor0'], ['ground0'])
    for index in range(number_inputs):
        i = str(index)
        set_wire(wires, 'wireinput'+i, ['in'+i], ['switch'+i+"/button"])
    
    return {
        "name": device_type+"0",
        "type": device_type,
        "wires": wires,
        "devices": devices
    }


def make_device(new_function, *args):
    device = new_function(*args)
    device_file_path = str(DEVICE_DIR) + '/' + device['type'] + '.json'
    write_json(device, device_file_path)


def new_tree_decoder(lengths):
    '''
    basically how this works is that the child
    decoders are turned on or off by the parent decoder.
    each of the parent decoder's output is AND'd with 
    all child inputs.
    lengths - a list of numbers. number of inputs at each level.
    '''
    ranges = []
    index = 0
    device_type = 'decoder'
    for length in lengths:
        ranges.append((index, index+length))
        index += length
        device_type += ('_'+str(length))

    devices = []

    # create inputs that will be reused by decoders in the
    # same level
    wire_map = {}
    for index in range(ranges[-1][1]):
        in_name = 'in'+ str(index)
        append_bridge(devices, in_name)
        set_wire(wire_map, 'wire'+in_name, [in_name], [])


    new_tree_decoder_help(ranges, devices, wire_map)
    wires = [wire for wire in wire_map.values()]
    return {
        'devices': devices,
        'wires': wires,
        'type': device_type,
        'name': device_type+'_0'
    }

    # add output
   
def new_tree_decoder_help(ranges, devices, wires, parent_index=0, level=0, index=0):
    sindex = str(index)
    '''
    Root parent is one decoder and starts at level 0.
    Ranges is a list of input index i.e [(0,2),(2,6)]
    '''

    # if not root, create wire from parent to self.
    if level>0:
        sparentl = str(parent_index)
        ins_per_parent = ranges[level-1][1] - ranges[level-1][0]
        outs_per_parent = power(ins_per_parent)
        out_index = index %outs_per_parent
        parent_name = 'decoder_'+str(level-1)+'_'+ sparentl+'/out'+str(out_index)
        wire_name = 'wiredecoder'+str(level-1)+'_'+ sparentl
        set_wire(wires,  wire_name, [parent_name],[])
        wire = wires[wire_name]


    # if past last level, make outputs
    if level >= len(ranges):
        # write outputs
        out_name = 'out'+str(index)
        append_bridge(devices, out_name)
        wire['to'].append(out_name)
        return

    in_range = ranges[level]
    num_ins= in_range[1] - in_range[0]
    slevel = str(level)
    num_outs = power(num_ins)
    # wire from parent output

    name = 'decoder_'+slevel+'_'+sindex
   
    # level < end
    decoder = {
        'type': 'decoder'+str(num_ins),
        'name': name
    }
    devices.append(decoder)

    if level>0:
        for idx, offset in enumerate(range(*in_range)):
            i = str(idx)
            soff = str(offset)
            and_name = 'and_'+slevel+'_'+sindex+'_'+i
            and_device = new_device(and_name, 'and2')
            devices.append(and_device)
            wire['to'].append(and_name+'/in0')

            in_name = 'in'+ soff
            in_wire = wires['wire'+in_name]
            in_wire['to'].append(and_name+'/in1')
            set_wire(wires, 'wire'+and_name, [and_name+'/out'], [name+'/in'+i])
    else:
        # root level. input to decoder input
        for offset in range(*in_range):
            in_name = 'in'+ str(offset)
            in_wire = wires['wire'+in_name]
            in_wire['to'].append(name+'/in'+str(offset))

    child_range = [index*num_outs, (index+1)*num_outs]
    for child_index in range(*child_range):
        new_tree_decoder_help(ranges, devices, wires, index, level+1, child_index)



def new_tree_mux(selector_sets):
    '''
    Make a hierarchy of muxes. Ex. instead of having a single mux64 device, make 2 mux 32's, etc.
    '''
    #TODO: move from decoder to mux
    devices = []
    wires = {}

    # make device and wires for selects.
    device_type="mux"
    for select_set in selector_sets:
        device_type += ('_'+str(len(select_set)))
        for select in select_set:
            append_bridge(devices, select)
            set_wire(wires, 'wire_'+select,[select],[])

    new_tree_mux_help(selector_sets, devices, wires, len(selector_sets)-1)
    #ranges = []
    #index = 0
    #for select_set in selector_sets:
    #    num = len(select_set)
    #    ranges.append((index, num))
    #    index += num

    #ins = []

    #num_ins = power(ranges[-1][1])
    #for in_i in range(num_ins):
    #    i = str(in_i)
    #    append_bridge(devices, 'in'+i)
    #    set_wire(wires, 'wirein'+i,[select],[])



    ## inputs. parent gets child inputs. 
    #num_select_sets = len(selector_sets)
    #num_ins = [power(len(select_set)) for select_set in selector_sets]
    #for child in device['devices']:
    #    tokens= int(name.split('_')[1])
    #    level = tokens[1]
    #    index = tokens[2]
    #        # bottom level
    #    ins_per_mux = num_ins[level]
    #    offset = index*ins_per_mux
    #    if level == num_select_sets - 1:
    #        for step, in_i in enumerate(range(offset,ins_per_mux)):
    #            wire= get_wire(wires, 'wirein'+str(in_i))
    #            wire['to'].append(child['name']+'/in'+step)
    #    else:

    #append_bridge(devices,'out')
    #set_wire(wires, 'wireout', ['mux'+level+'_0'],['out'])
    device = {
        'type': device_type,
        'name': device_type + '_0',
        'devices': devices,
        'wires': [wire for wire in wires.values()]
    }
    return device


def new_tree_mux_help(select_sets, devices, wires, level, index=0, parent_index=0):
    select_set = select_sets[level]
    number_selects = len(select_set)
    num_ins = power(number_selects)
    sindex = str(index)

    parent_name = 'mux_'+str(level+1)+'_'+str(parent_index)
    if (level <= -1):
        # create input links
        ins_per_zero = power(len(select_sets[0]))
        parent_in = index%ins_per_zero
        in_name = 'in'+sindex
        append_bridge(devices, in_name)
        wire = set_wire(wires, 'wire_'+in_name,[in_name],[parent_name+'/in'+str(parent_in)])
        return

    name = 'mux_'+str(level)+'_'+str(index)
    mux = {
        'type': 'mux'+str(number_selects),
        'name': name
    }

    # now hookup selects to device selects.
    for idx, select in enumerate(select_set):
        wire = wires['wire_'+select]
        wire['to'].append(name+'/select'+str(idx))

    # wire from output to parent's input
    if level >= len(select_sets) - 1:
        #parent set.
        append_bridge(devices, 'out')
        set_wire(wires, 'wire_'+name, [name+'/out'], ['out'])
    else:
        set_wire(wires, 'wire_'+name, [name+'/out'], [parent_name+'/in'+str(index)])


    devices.append(mux)
    child_range = [index*num_ins, (index+1)*num_ins]
    for child_index in range(*child_range):
        new_tree_mux_help(select_sets, devices, wires, level-1, child_index, index)


def make_group_mux(input_maps, selects):
    '''
    many muxes that share the same selects
    input_maps - map if inputs to output
    make_group_mux( 
        [
            {
                'output':'r_0',
                'inputs':['wone', 'wzero']
            },
            ...
        ]
        ,['pc_0', 'pc_1'])
    '''

    # number of inputs per mux
    number_selects = len(selects)
    devices = []
    wires = []

    #first make selects
    for select in selects:
        append_bridge(devices,select)
        set_wire(wires, 'wire_'+select,[select],[])

    # make mux per input group
    for index, input_map in enumerate(input_maps):
        inputs = input_map['inputs']
        output = input_map['output']
        mux_name = "mux_" + output
        mux = new_device(mux_name, "mux_"+str(len(inputs)))
        devices.append(mux)
        append_bridge(devices,output)
        set_wire(wires, 'wire_'+mux_name, [mux_name+"/out"], [output])

        # make inputs and wires
        for child_index, input_name in enumerate(inputs):
            ci = str(child_index)
            append_bridge(devices,input_name)
            set_wire(wires, 'wire_'+input_name,[input_name],[mux_name+"/in"+ci])

        # wire select to mux
        for index, select in enumerate(selects):
            wire = get_wire(wires, 'wire_'+select)
            wire['to'].append(mux_name+"/select"+str(index))
        
    return {
        'devices': devices,
        'wires': wires
    }


def make_insn_read():
    '''
    Make insn reader.
    It is basically 28 muxes with a single set of selectors.
    
    '''
    pc_size = 10
    read_size = 16

    branch_size = pc_size
    number_insns = int(math.pow(2, pc_size))
    input_maps = []

    for name, size in [['r_', read_size], ['b_', branch_size], ['wone', 1], ['wzero', 1]]:
        for index in range(size):
            i = str(index)
            inputs = []
            for number in range(number_insns):
                inputs.append("{0}_{1}_{2}".format(name, i, str(number)))
            input_map = {
                'output': name + i,
                'inputs': inputs
            }
            input_maps.append(input_map)


    selects = []
    for index in range(pc_size):
        selects.append('pc_'+index)
    device = make_group_mux(inputs, selects)
    device.upate({
        'name': 'insn_read0',
        'type': 'insn_read',
    })
    return device


def new_pc_select():
    pc_size = 10  # PC is not selector here.
    input_maps = []
    for index in range(pc_size):
        i = '_'+str(index)
        pc = 'pc'+i
        b = 'b'+i
        input_map = {
            'output': 'out'+i,
            'inputs': [pc, b]
        }
        input_maps.append(input_map)
    device = make_group_mux(input_maps, ['v'])
    device.update({
        'name': 'pc_select0',
        'type': 'pc_select',
    })
    return device

def make_pc_select():
    
    device = new_pc_select()
    device_file_path = str(DEVICE_DIR) + '/' + device['type'] + '.json'
    write_json(device, device_file_path)

def make_mem_mux():
    '''
    64x32x32

    '''
    sizes = [6,5,5]
    select_sets = get_select_sets(sizes)
    device = new_mem_mux(select_sets)
    device_file_path = str(DEVICE_DIR) + '/' + device['type'] + '.json'
    write_json(device, device_file_path)


def new_mem_mux(select_sets):
    '''
    One very large mux
    '''

    device = new_tree_mux(select_sets)
    
    device.update({
        'name': 'mem_mux0',
        'type': 'mem_mux'
    })
    return device


def make_write_select():
    '''
    Select writeone or writeo?
    '''
    device = new_mux(1, is_dual=False, in_pre='write', select_pre='select', out='w')
    device['type'] = 'write_select'
    device['name'] = 'write_select0'
    device_file_path = str(DEVICE_DIR) + '/' + device['type'] + '.json'
    write_json(device, device_file_path)


def make_write_enable():
    number_inputs = 16
    device = new_tree_decoder([8,8])
    #device = new_decoder(number_inputs, False)
    device['type'] = 'write_enable'
    device['name'] = 'write_enable_0'
    device_file_path = str(DEVICE_DIR) + '/' + device['type'] + '.json'
    write_json(device, device_file_path)


def make_cpu_iter():
    # cpu without memory
    pass

def make_cpu():
    # make all components and link them
    pass

def make_pc_add():
    wires = []
    devices = []
    device = {
        'wires': wires,
        'type': 'pc_add',
        'name': 'pc_add0',
        'devices': devices
    }

    digits = 10
    half = digits/2

    wires_map = {}
    first = new_add(half)
    first['name'] = 'first'
    second = new_add(half)
    second['name'] = 'second'

    for index in range(half):
        i = str(index)
        aname = "a_"+i
        bname = 'b_'+i
        append_bridge(devices, aname)
        set_wire(wires_map, [aname], ['first/a_'+i])
        append_bridge(devices, "b_"+i)
        set_wire(wires_map, [bname], ['first/b_'+i])

        out = 'o_'+i
        append_bridge(devices, out)
        set_wire(wires_map, ['first/'+out], [out])

    for index in range(half):
        i = str(index)
        offset = str(index+half)
        aname = "a_"+offset
        bname = 'b_'+offset
        append_bridge(devices, aname)
        set_wire(wires_map, [aname], ['second/a_'+i])
        append_bridge(devices, bname)
        set_wire(wires_map, [bname], ['second/b_'+i])

        set_wire
        out = 'o_'+i
        append_bridge(devices, out)
        set_wire(wires_map, ['second/'+out], ['o_'+offset])

    set_wire(wires_map, ['first/c_out'], ['second/c_in'])


    device_file_path = str(DEVICE_DIR) + '/' + device['type'] + '.json'
    write_json(device, device_file_path)


def add_truth(inputs):
    '''
    Split inputs into two and return sum that is half length.
    First is carry.
    For the output, last bit is carry
    '''
    length = len(inputs)
    c = inputs[0]
    half = (length-1)/2
    inputa = inputs[0:half]
    inputb = inputs[half:length]
    a = get_uint(inputa)
    b = get_uint(inputb)
    result = a+b
    return get_bools(result, half+1)

def new_add(number_inputs):
    '''
    number_inputs is number of digits.
    device = new_add(5)
    device has 5 inputs a_0-a_4, 5 inputs b_0-b_4, and c_in
    device has 5 outputs o_0-o_4, and c_out
    '''
    inputs = []
    #carry
    inputs.append('c_in')
    for name in ['a_','b_']:
        for index in range(number_inputs):
            inputs.append(name+str(index))
    outputs = []
    for index in range(number_inputs):
        outputs.append("o_"+str(index))
    outputs.append('c_out')

    return new_boolean(inputs, outputs, add_truth, "add"+str(number_inputs))

def make_add(number_inputs):
    device = new_add(number_inputs)
    device_file_path = str(DEVICE_DIR) + '/' + device['type'] + '.json'
    write_json(device, device_file_path)


#def temp():
#    devices = []
#    wires = []
#
#    for index in range(pc_size):
#        #PC inputs
#        devices.append(append_bridge("pc_"+i))
#    
#    read_muxs = []
#    for index in range(read_size):
#        i = str(index)
#        read_muxs.append(new_mux(pc_size, is_dual=True))
#        # R output
#        devices.append(append_bridge("ro_"+i))
#        for child_index in range(number_insns):
#            ci = i+'_'+str(child_index)
#            devices.append(append_bridge("ri_"+i+"_"+ci))
#            wires.append(make_wire('wireri_'+i+'_'+ci,[],[]))
#
#    branch_muxs = []
#    for index in range(branch_size):
#        branch_muxs.append(new_mux(pc_size, is_dual=True))
#        devices.append(append_bridge("bo_"+i))
#        for child_index in range(number_insns):
#            ci = str(child_index)
#            devices.append(append_bridge("bi_"+i+"_"+ci))
#
#    wone_mux = new_mux(pc_size, is_dual=True)
#    devices.append(append_bridge("woneo_"+i))
#    for child_index in range(number_insns):
#        ci = str(child_index)
#        devices.append(append_bridge("wonei_"+i+"_"+ci))
#
#    wzero_mux = new_mux(pc_size, is_dual=True)
#    devices.append(append_bridge("wzeroo_"+i))
#    for child_index in range(number_insns):
#        ci = str(child_index)
#        devices.append(append_bridge("wzeroi_"+i+"_"+ci))

    # make wire connections and outputs


def main():
    option = sys.argv[1]
    if option == 'mux':
        number_selects = int(sys.argv[2])
        if len(sys.argv) > 3:
            is_dual = True
        else:
            is_dual = False
        make_mux(number_selects, is_dual)
    elif option == 'decoder':
        number_inputs = int(sys.argv[2])
        if len(sys.argv) > 3:
            is_dual = True
        else:
            is_dual = False
        make_decoder(number_inputs, is_dual)
    elif option == 'or':
        number_inputs = int(sys.argv[2])
        if len(sys.argv) > 3:
            make_prim_dual("or", number_inputs)
        else:
            make_or(number_inputs)
    elif option == 'and':
        number_inputs = int(sys.argv[2])
        if len(sys.argv) > 3:
            make_prim_dual("and", number_inputs)
        else:
            make_and(number_inputs)
    elif option == 'add':
        number_inputs = int(sys.argv[2])
        make_add(number_inputs)
    elif option == 'tree_decoder':
        lengths = [int(arg) for arg in sys.argv[2:]]
        make_device(new_tree_decoder, lengths)
    elif option == 'tree_mux':
        lengths = [int(arg) for arg in sys.argv[2:]]
        select_sets = get_select_sets(lengths)
        make_device(new_tree_mux, select_sets)


    # cpu components
    elif option == 'insn_read':
        make_insn_read()
    elif option == 'pc_select':
        make_pc_select()
    elif option == 'pc_add':
        make_pc_add()
    elif option == 'mem_mux':
        make_mem_mux()
    elif option == 'write_select':
        make_write_select()
    elif option == 'write_enable':
        make_write_enable()
    elif option == 'cpu':
        make_cpu()

if __name__ == '__main__':
    main()
