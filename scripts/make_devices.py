from shared.common import write_json, get_int, get_bools
import math
import itertools
import sys
import string
from settings import DEVICE_DIR

def make_wire(name, from_list, to_list, is_dual=False):
    wires = []
    if is_dual:
        for spin in ['down', 'up']:
            froms = [pin+spin for pin in from_list]
            tos = [pin+spin for pin in to_list]
            wire = {
                "name": name+spin,
                "from": froms,
                "to": tos
            }
            wires.append(wire)
    else:
        wire = {
            "name": name,
            "from": from_list,
            "to": to_list
        }
        wires.append(wire)
    return wires


def get_mux_type(number_selects, is_dual):
    number_inputs = int(math.pow(2, number_selects))
    device_type = "mux_"+str(number_inputs)
    if is_dual:
        device_type += "dual"
    return device_type


def make_mux(number_selects, is_dual):
    mux = new_mux(number_selects, is_dual)
    device_type = get_mux_type(number_selects, is_dual)
    device_file_path = str(DEVICE_DIR) + '/' + device_type + '.json'
    write_json(mux, device_file_path)


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
        devices.extend(make_bridge(in_pre+i, is_dual))
        # need and gates
        devices.append(make_device("and"+i, "and"+str(number_selects+1), is_dual))

    for index in range(number_selects):
        # selects
        i = str(index)
        devices.extend(make_bridge(select_pre+i, is_dual))
        # nots
        devices.append(make_device("not"+i, "not", is_dual))

    # or device
    devices.append(make_device("or0", "or"+str(number_inputs), is_dual))
    devices.extend(make_bridge(out, is_dual))

    # wires
    wires = []
    for i in range(number_inputs):
        index = str(i)
        # input to and
        to_pin = "and"+index+"/in" + str(number_selects)
        wires.extend( make_wire("wirein"+index, ["in"+index], [to_pin], is_dual))
        # and to or
        wires.extend(make_wire("wireand"+index, ["and"+index+"/out"], ["or0/in"+index], is_dual))

    for index in range(number_selects):
        # from selector and from not selector
        i = str(index)
        wires.extend(make_wire("wireselect"+i, ["select"+i], ["not"+i+"/in"], is_dual))
        wires.extend(make_wire("wireselectnot"+i, ["not"+i+"/out"], [], is_dual))

    value_sets = itertools.product([False,True], repeat=number_selects)
    for value_set_index, value_set in enumerate(value_sets):
        value_set = reversed(value_set)
        vi = str(value_set_index)
        for index, value in enumerate(value_set):
            i = str(index)
            if value:
                wire_append(wires, 'wireselect'+i, 'to', 'and'+vi+"/in"+i, is_dual)
            else:
                wire_append(wires, 'wireselectnot'+i, 'to', 'and'+vi+"/in"+i, is_dual)


    wires.extend(make_wire("wireor0", ["or0/out"], ["out"], is_dual))
    return {
        "name": device_type+"0",
        "type": device_type,
        "wires": wires,
        "devices": devices
    }


def get_wire(wires, name):
    for wire in wires:
        if wire['name'] == name:
            return wire
    return None


def make_bridge(name, is_dual=False):
    devices = []
    if is_dual:
        for spin in ["down","up"]:
            device = {
                "name": name + spin,
                "type": "bridge"
            }
            devices.append(device)
    else:
        device = {
            "name": name,
            "type": "bridge"
        }
        devices.append(device)

    return devices

def make_device(device_name, device_type, is_dual=False):
    
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
        devices.extend(make_bridge(name, is_dual))
        devices.append(make_device("not"+i, "not", is_dual ))
    return devices


def make_wires(number_inputs, is_dual=False):
    '''
    wire 
    '''
    wires = []
    for index in range(number_inputs):
        i = str(index)
        wires.extend( make_wire("wirein"+i, ["in"+i], ["not"+i+"/in"], is_dual))
        # wire from not
        wires.extend( make_wire("wirenot"+i, ["not"+i+"/out"], [], is_dual))
    return wires


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
        devices.extend(make_bridge(name, True))
        devices.append(make_device("not"+i+"down", "not"))
        devices.append(make_device("not"+i+"up", "not"))

        i = str(index)

        for spin in ['down', 'up']:
            wires.extend( make_wire("wirein"+i+spin, ["in"+i+spin], ["not"+i+spin+"/in"]))
            # wire from not
            wires.extend( make_wire("wirenot"+i+spin, ["not"+i+spin+"/out"], [] ))

    devices.extend(make_bridge("out", True))
    return devices, wires


def wire_append(wires, wire_name, direction, device_name, is_dual):
    if is_dual:
        for spin in ['down', 'up']:
            wire = get_wire(wires, wire_name+spin)
            wire[direction].append(device_name+spin)
    else:
        wire = get_wire(wires, wire_name)
        wire[direction].append(device_name)


def make_decoder(number_inputs, is_dual):
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
        devices.extend(make_bridge(name, is_dual))
        # not gate for every input
        devices.append(make_device("not"+i, "not", is_dual))

    for index in range(number_outputs):
        # outputs
        i = str(index)
        name = "out"+i
        devices.extend(make_bridge(name, is_dual))
        # and gate for every output
        devices.append(make_device("and"+i, "and"+str(number_inputs), is_dual))

    wires.extend(make_wires(number_inputs, is_dual))

    for index in range(number_outputs):
        # wire from and to out
        i = str(index)
        wires.extend( make_wire("wireand"+i, ["and"+i+"/out"], ["out"+i], is_dual))

    value_sets = itertools.product([False,True], repeat=number_inputs)
    for value_set_index, value_set in enumerate(value_sets):
        # send wires to vi'th and gate. wires from in or not inputs.
        value_set = reversed(value_set)
        vi = str(value_set_index)

        for index, value in enumerate(value_set):
            i = str(index)
            if value:
                wire_append(wires, 'wirein'+i, 'to', 'and'+vi+"/in"+i, is_dual)
            else:
                wire_append(wires, 'wirenot'+i, 'to', 'and'+vi+"/in"+i, is_dual)

    device_file_path = str(DEVICE_DIR) + '/' + device_type + '.json'
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
    ex: device = new_boolean(['a0','a1'], ['o0', o1'], get_add, 'add1')
    '''
    devices = []
    wires = []
    number_inputs = len(inputs)

    for in_name in inputs:
        # construct inputs
        in_dev = make_bridge(in_name)
        # not gates for every input
        not_name = 'not_'+in_name
        not_dev = make_device(not_name, 'not')
        devices.extend(in_dev)
        devices.append(not_dev)

        # wire from input
        wireas = make_wire('wire_'+in_name, [in_name],[not_name+"/in"])
        # wire from not gate
        wirenots = make_wire('wire_'+not_name, [not_name+"/out"],[])
        wires.extend(wireas)
        wires.extend(wirenots)

    for out_name in outputs:
        # outputs
        out = make_bridge(out_name)
        devices.extend(out)

    # wire from input to and gates
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
                wire = get_wire(wires, 'wire_'+inputs[index])
                wire['to'].append('and_'+set_i+"/in"+i)
                #wiredown = get_wire(wires, 'wirenot'+i+"down")
                #wireup = get_wire(wires, 'wirein'+i+"up")
            else:
                wire = get_wire(wires, 'wire_not_'+inputs[index])
                wire['to'].append('and_'+set_i+"/in"+i)
                #wiredown = get_wire(wires, 'wirein'+i+"down")
                #wireup = get_wire(wires, 'wirenot'+i+"up")
            #wire['to'].append('and_'+set_i+"/in"+str(2*index))
            #wireup['to'].append('and_'+set_i+"/in"+str(2*index+1))

    # each output is an or of one or more and gates.
    # ones is necessary to see whether an or gate is necessary.
    ones = [0]* len(outputs)  #track how many '1's for every output.
    zeros = [0]*len(outputs)
    for output_set in output_sets:
        # for each row in truth table
        for index, output in enumerate(output_set):
            #for each output in row
            if output:
                ones[index] += 1
            #else:
            #    zeros[index] += 1

    for index, one in enumerate(ones):
        # create or gate and connect to out
        i = "_"+str(index)
        if one > 1:
            devices.append(make_device("or_1"+i, "or"+str(one)))
            wire = {
                "name": "wire_or_1"+i,
                "from": ["or_1"+i+"/out"],
                "to": [outputs[index]]
            }
            wires.append(wire)

    for zero in zeros:
        i = "_"+str(index)
        if zero > 1:
            devices.append(make_device("or_0"+i, "or"+str(zero)))
            wire = {
                "name": "wire_or_0"+i,
                "from": ["or_0"+i+"/out"],
                "to": ["outdown"]
            }
            wires.append(wire)

    oneis = [0] * len(outputs)
    zeroi = 0

    # each row in truth table is an 'and' gate
    number_rows = int(math.pow(2,number_inputs))
    for index in range(number_rows):
        i = "_"+str(index)
        and_name = "and"+i
        devices.append(make_device(and_name, "and"+str(number_inputs)))
        wireands = make_wire('wire_'+and_name, [and_name+"/out"], [])
        wires.extend(wireands)

    # and gate to or gate
    for set_index, output_set in enumerate(output_sets):
        # for each row in truth table
        set_i = str(set_index)
        for index, value in enumerate(output_set):
            # for each output in the row
            i = "_"+str(index)
            one = ones[index]
            if value:
                output = "out"+i if one <= 1 else "or_1"+i+"/in"+str(oneis[index])
                wire = get_wire(wires, "wire_and_"+set_i)
                wire['to'].append(output)
                oneis[index]+=1
            #else:
            #    output = "outdown" if zeros <= 1 else "or_0"+i+"/in"+str(zeroi)
            #    wires.extend(make_wire("wireand" + i, ["and"+i+"/out"], [output]))
            #    zeroi+=1

    return {
        "name": device_type+"0",
        "type": device_type,
        "wires": wires,
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
        devices.append(make_device("or1", "or"+str(ones)))
        wire = {
            "name": "wireor1",
            "from": ["or1/out"],
            "to": ["outup"]
        }
        wires.append(wire)
    if zeros > 1:
        devices.append(make_device("or0", "or"+str(zeros)))
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
        devices.append(make_device("and"+i, "and"+str(number_inputs*2)))
        if value:
            output = "outup" if ones <= 1 else "or1/in"+str(onei)
            wires.extend(make_wire("wireand" + i, ["and"+i+"/out"], [output]))
            onei+=1
        else:
            output = "outdown" if zeros <= 1 else "or0/in"+str(zeroi)
            wires.extend(make_wire("wireand" + i, ["and"+i+"/out"], [output]))
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
    wires.extend(make_wire("sourcetoswitch", ['source0'], ['switch0']))
    for index in range(number_inputs-1):
        i = str(index)
        inext = str(index+1)
        wires.extend(make_wire("wireswitch"+i+"to"+inext, ['switch'+i], ['switch'+inext]))

    wires.extend(make_wire("switchtoresistor", ['switch'+str(number_inputs-1)], ['resistor0', 'out']))
    device_file_path = str(DEVICE_DIR) + '/' + 'and' + str(number_inputs) + '.json'
    write_json(device_data, device_file_path)


def make_or(number_inputs):
    device_data = make_prim_part("or", number_inputs)
    switch_list = ['switch'+str(i) for i in range(number_inputs)]
    wires = device_data['wires']
    wires.extend(make_wire("sourcetoswitch", ['source0'], switch_list))
    wires.extend(make_wire("switchtoresistor", switch_list, ['resistor0', 'out']))
    device_file_path = str(DEVICE_DIR) + '/' + 'or' + str(number_inputs) + '.json'
    write_json(device_data, device_file_path)

def make_prim_part(prim_type, number_inputs):
    device_type = prim_type+str(number_inputs)
    devices = []
    for index in range(number_inputs):
        #inputs
        i = str(index)
        devices.extend(make_bridge("in"+i))
        devices.append(make_device("switch"+i, "switch"))

    devices.append(make_device("source0", "source"))
    devices.append(make_device("resistor0", "resistor"))
    devices.append(make_device("ground0", "ground"))
    devices.extend(make_bridge("out"))

    wires = []
    wires.extend(make_wire("wireresistor", ['resistor0'], ['ground0']))
    for index in range(number_inputs):
        i = str(index)
        wires.extend(make_wire('wireinput'+i, ['in'+i], ['switch'+i+"/button"]))
    
    return {
        "name": device_type+"0",
        "type": device_type,
        "wires": wires,
        "devices": devices
    }

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
        devices.extend(make_bridge(select))
        wires.extend(make_wire('wire_'+select,[select],[]))

    # make mux per input group
    for index, input_map in enumerate(input_maps):
        inputs = input_map['inputs']
        output = input_map['output']
        mux_name = "mux_" + output
        mux = make_device(mux_name, "mux_"+str(len(inputs)))
        devices.append(mux)
        devices.extend(make_bridge(output))
        wires.extend(make_wire('wire_'+mux_name, [mux_name+"/out"], [output]))

        # make inputs and wires
        for child_index, input_name in enumerate(inputs):
            ci = str(child_index)
            devices.extend(make_bridge(input_name))
            wires.extend(make_wire('wire_'+input_name,[input_name],[mux_name+"/in"+ci]))

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
            'output': 'pcb'+i,
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
    address_size = 16

    selects = []
    for index in range(address_size):
        selects.append('a_' + str(index))

    number_inputs = int(math.pow(2, address_size))
    inputs = []
    for index in range(number_inputs):
        inputs.append('m_'+str(index))
    input_maps = [{
        'output': 'v',
        'inputs': inputs
    }]
    
    device = make_group_mux(input_maps, selects)
    device.upate({
        'name': 'mem_mux0',
        'type': 'mem_mux'
    })


def make_write_select():
    device = new_mux(1, is_dual=True, in_pre='write', select_pre='select', out='w')
    return device

def make_write_enable():
    number_inputs = 16
    device = make_decoder(number_inputs, True)
    return device

def make_pc_add():
    pass

def get_add(inputs):
    length = len(inputs)
    inputa = inputs[0:length/2]
    inputb = inputs[length/2:length]
    a = get_int(inputa)
    b = get_int(inputb)
    c = a+b
    return get_bools(c, len(inputa))

def new_add(number_inputs):
    '''
    number_inputs is number of digits.
    device = new_add(5) 
    '''
    inputs = []
    for name in ['a_','b_']:
        for index in range(number_inputs):
            inputs.append(name+str(index))

    outputs = []
    for index in range(number_inputs):
        outputs.append("o_"+str(index))

    return new_boolean(inputs, outputs, get_add, "add"+str(number_inputs))

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
#        devices.append(make_bridge("pc_"+i))
#    
#    read_muxs = []
#    for index in range(read_size):
#        i = str(index)
#        read_muxs.append(new_mux(pc_size, is_dual=True))
#        # R output
#        devices.append(make_bridge("ro_"+i))
#        for child_index in range(number_insns):
#            ci = i+'_'+str(child_index)
#            devices.append(make_bridge("ri_"+i+"_"+ci))
#            wires.append(make_wire('wireri_'+i+'_'+ci,[],[]))
#
#    branch_muxs = []
#    for index in range(branch_size):
#        branch_muxs.append(new_mux(pc_size, is_dual=True))
#        devices.append(make_bridge("bo_"+i))
#        for child_index in range(number_insns):
#            ci = str(child_index)
#            devices.append(make_bridge("bi_"+i+"_"+ci))
#
#    wone_mux = new_mux(pc_size, is_dual=True)
#    devices.append(make_bridge("woneo_"+i))
#    for child_index in range(number_insns):
#        ci = str(child_index)
#        devices.append(make_bridge("wonei_"+i+"_"+ci))
#
#    wzero_mux = new_mux(pc_size, is_dual=True)
#    devices.append(make_bridge("wzeroo_"+i))
#    for child_index in range(number_insns):
#        ci = str(child_index)
#        devices.append(make_bridge("wzeroi_"+i+"_"+ci))

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
    elif option == 'pc_select':
        make_pc_select()
    else:
        pass

if __name__ == '__main__':
    main()
