from shared.utilities import write_json
import math
import itertools
import sys
import string
from settings import DEVICE_DIR

def get_mux_type(number_selects, is_dual):
    number_inputs = int(math.pow(2, number_selects))
    device_type = "mux"+str(number_inputs)
    if is_dual:
        device_type += "dual"
    return device_type

def make_mux(number_selects, is_dual):
    mux = new_mux(number_selects, is_dual)
    device_type = get_mux_type(number_selects, is_dual)
    device_file_path = str(DEVICE_DIR) + '/' + device_type + '.json'
    write_json(mux, device_file_path)

def new_mux(number_selects, is_dual=False, in_pre='in', select_pre='select' out='out'):
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



def make_insn_read():
    '''
    Make insn reader.
    It is basically 28 muxes with a single set of selectors.
    
    '''
    pc_size = 10
    read_size = 16
    branch_size = 10

    number_insns = math.pow(2, pc_size)

    devices = []
    wires = []

    for index in range(pc_size):
        devices.append(make_bridge("pc_"+i))
    
    read_muxs = []
    for index in range(read_size):
        i = str(index)
        read_muxs.append(new_mux(pc_size, is_dual=True))
        devices.append(make_bridge("ro_"+i))
        for child_index in range(number_insns):
            ci = i+'_'+str(child_index)

            devices.append(make_bridge("ri_"+i+"_"+ci))
            wires.append(make_wire('wireri_'+i+'_'+ci,[],[])


    branch_muxs = []
    for index in range(branch_size):
        branch_muxs.append(new_mux(pc_size, is_dual=True))
        devices.append(make_bridge("bo_"+i))
        for child_index in range(number_insns):
            ci = str(child_index)
            devices.append(make_bridge("bi_"+i+"_"+ci))

    wone_mux = new_mux(pc_size, is_dual=True)
    devices.append(make_bridge("woneo_"+i))
    for child_index in range(number_insns):
        ci = str(child_index)
        devices.append(make_bridge("wonei_"+i+"_"+ci))

    wzero_mux = new_mux(pc_size, is_dual=True)
    devices.append(make_bridge("wzeroo_"+i))
    for child_index in range(number_insns):
        ci = str(child_index)
        devices.append(make_bridge("wzeroi_"+i+"_"+ci))

    # make wire connections and outputs

def make_pc_add():
    pass

def make_pc_select():
    pass

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


if __name__ == '__main__':
    main()
