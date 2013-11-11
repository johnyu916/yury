from shared.utilities import write_json
import math
import itertools
import sys
from settings import DEVICE_DIR

def make_mux_old(number_selects):
    '''
    Make mux circuit.
    A mux circuit is the following:
    O = SA + not(S)B
    '''
    number_inputs = int(math.pow(2, number_selects))
    device_type = "mux"+str(number_inputs)
    devices = []

    for index in range(number_inputs):
        #inputs
        device = {
            "name": "in"+str(index),
            "type": "bridge"
        }
        devices.append(device)
        # need and gates
        device = {
            "name": "and"+str(index),
            "type": "and"
        }
        devices.append(device)

    for index in range(number_selects):
        # selects
        device = {
            "name": "select"+str(index),
            "type": "bridge"
        }
        devices.append(device)
        # nots
        device ={
            "name": "not"+str(index),
            "type": "not"
        }
        devices.append(device)

        # or devices
    device ={
        "name": "or0",
        "type": "or"+str(number_inputs)
    }
    devices.append(device)
    device ={
        "name": "out",
        "type": "bridge"
    }
    devices.append(device)

    # wires
    wires = []
    for i in range(number_inputs):
        index = str(i)
        # input to and
        wire = {
            "name": "wirein"+index,
            "from": ["in"+index],
            "to": ["and"+index+"/in" + str(number_selects)]
        }
        wires.append(wire)
        # and to or
        wire = {
            "name": "wireand"+index,
            "from":["and"+index+"/out"],
            "to":["or0/in"+index]
        }
        wires.append(wire)

    for index in range(number_selects):
        # from selector and from not selector
        wire = {
            "name": "wireselect"+str(index),
            "from": ["select"+str(index)],
            "to": ["not"+str(index)+"/in"]
        }
        wires.append(wire)
        wire = {
            "name": "wireselectnot"+str(index),
            "from": ["not"+str(index)+"/out"],
            "to": []
        }
        wires.append(wire)

    
    value_sets = itertools.product([False,True], repeat=number_selects)
    for value_set_index, value_set in enumerate(value_sets):
        value_set = reversed(value_set)
        vi = str(value_set_index)
        for index, value in enumerate(value_set):
            i = str(index)
            if value:
                wire = get_wire(wires, 'wireselect'+i)
                wire['to'].append("and"+vi+"/in"+i)
            else:
                wire = get_wire(wires, 'wireselectnot'+i)
                wire['to'].append("and"+vi+"/in"+i)

    wire = {
        "name": "wireor0",
        "from": ["or0/out"],
        "to": ["out"]
    }
    wires.append(wire)
    data = {
        "name": device_type+"0",
        "type": device_type,
        "wires": wires,
        "devices": devices
    }

    device_file_path = str(DEVICE_DIR) + '/' + device_type + '.json'
    write_json(data, device_file_path)


def make_mux(number_selects, is_dual):
    '''
    Make mux circuit.
    A mux circuit is the following:
    O = SA + not(S)B
    '''
    number_inputs = int(math.pow(2, number_selects))
    device_type = "mux"+str(number_inputs)
    if is_dual:
        device_type += "dual"
    devices = []
    
    for index in range(number_inputs):
        #inputs
        i = str(index)
        devices.extend(make_bridge("in"+i, is_dual))
        # need and gates
        devices.append(make_device("and"+i, "and"+str(number_selects+1), is_dual))

    for index in range(number_selects):
        # selects
        i = str(index)
        devices.extend(make_bridge("select"+i, is_dual))
        # nots
        devices.append(make_device("not"+i, "not", is_dual))

    # or device
    devices.append(make_device("or0", "or"+str(number_inputs), is_dual))
    devices.extend(make_bridge("out", is_dual))

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
    data = {
        "name": device_type+"0",
        "type": device_type,
        "wires": wires,
        "devices": devices
    }

    device_file_path = str(DEVICE_DIR) + '/' + device_type + '.json'
    write_json(data, device_file_path)

def make_decoder_old(number_inputs):
    number_outputs = int(math.pow(2, number_inputs))
    device_type = "decoder" + str(number_inputs)
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
        device = {
            "name": "in"+i,
            "type": "bridge"
        }
        devices.append(device)
        device = {
            "name": "not"+i,
            "type": "not"
        }
        devices.append(device)

    for index in range(number_outputs):
        i = str(index)
        device = {
            "name": "out"+i,
            "type": "bridge"
        }
        devices.append(device)
        device = {
            "name": "and"+i,
            "type": "and" + str(number_inputs)
        }
        devices.append(device)

    for index in range(number_inputs):
        i = str(index)
        wire = {
            "name": "wirein"+i,
            "from": ["in"+i],
            "to": ["not"+i+"/in"]
        }
        wires.append(wire)
        wire = {
            "name": "wirenot"+i,
            "from": ["not"+i+"/out"],
            "to": []
        }
        wires.append(wire)

    for index in range(number_outputs):
        i = str(index)
        wire = {
            "name": "wireand"+i,
            "from":["and"+i+"/out"],
            "to":["out"+i]
        }
        wires.append(wire)

    value_sets = itertools.product([False,True], repeat=number_inputs)
    for value_set_index, value_set in enumerate(value_sets):
        value_set = reversed(value_set)
        vi = str(value_set_index)
        wire = get_wire(wires,'wirein'+vi)

        for index, value in enumerate(value_set):
            i = str(index)
            if value:
                wire = get_wire(wires,'wirein'+i)
                wire['to'].append("and"+vi+"/in"+i)
            else:
                wire = get_wire(wires,'wirenot'+i)
                wire['to'].append("and"+vi+"/in"+i)

    device_file_path = str(DEVICE_DIR) + '/' + device_type + '.json'
    write_json(data, device_file_path)

def get_wire(wires, name):
    for wire in wires:
        if wire['name'] == name:
            return wire
    return None


def make_bridge(name, is_dual):
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
            froms = [append_name(pin, spin) for pin in from_list]
            tos = [append_name(pin, spin) for pin in to_list]
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

def make_wires_input(number_inputs, is_dual=False):
    wires = []
    for index in range(number_inputs):
        i = str(index)
        wires.extend( make_wire("wirein"+i, ["in"+i], ["not"+i+"/in"], is_dual))

        # wire from not
        wires.extend( make_wire("wirenot"+i, ["not"+i+"/out"], [], is_dual))
    return wires

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

    wires.extend(make_wires_input(number_inputs, is_dual))

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

def make_or_dual(number_inputs):
    devices = []
    and1s = []
    and0s = []
    for index in range(number_inputs):
        i = str(index)
        name = "in"+i
        devices.extend(make_bridge(name, is_dual))
        devices.append(make_device("not"+i+"down", "not"))
        devices.append(make_device("not"+i+"up", "not"))

        if index < number_inputs - 1:
            and1s.append(make_device("and1"+index, "and"+number_inputs))
        else:
            and0s.append(make_device("and00", "and"+number_inputs))
    devices.extend[and1s]
    devices.extend[and0s]
    wires = []
    wires.extend(make_wires_input(number_inputs, True))
    value_sets = itertools.product([False,True], repeat=number_inputs)
    not_index = 0
    for value_set_index, value_set in enumerate(value_sets):
        set_i = str(value_set_index)
        if not get_or(value_set):
            not_index = value_set_index
        for index, value in enumerate(value_set):
            i = str(index)
            if value:
                wire = get_wire(wires, 'wirein'+set_i)
            else:
                wire = get_wire(wires, 'wirenot'+set_i)
            wire['to'].append('and'+vi+"/in"+i)
            
    # and to or gain
    for index, and1 in enumerate(and1s):
        i = str(index)
        wires.append(make_wire("wireand1" + i, ["and1"+i], ["or0"]))
    wires.append(make_wire("wireand00", ["and00"+i], ["outdown"]))
    wire = {
        "name": "wireor0",
        "from": ["or0/out"],
        "to": ["outup"]
    }
    wires.append(wire)
    data = {
        "name": device_type+"0",
        "type": device_type,
        "wires": wires,
        "devices": devices
    }

    device_file_path = str(DEVICE_DIR) + '/' + device_type + '.json'
    write_json(data, device_file_path)

def make_or(number_inputs):
    is_dual = False
    device_type = "or"+str(number_inputs)
    devices = []
    for index in range(number_inputs):
        #inputs
        i = str(index)
        devices.extend(make_bridge("in"+i, is_dual))
        devices.append(make_device("switch"+i, "switch", is_dual))

    devices.append(make_device("source0", "source"))
    devices.append(make_device("resistor0", "resistor"))
    devices.append(make_device("ground0", "ground"))
    devices.extend(make_bridge("out", is_dual))

    wires = []
    switch_list = ['switch'+str(i) for i in range(number_inputs)]
    wires.extend(make_wire("sourcetoswitch", ['source0'], switch_list))
    wires.extend(make_wire("switchtoresistor", switch_list, ['resistor0', 'out']))
    wires.extend(make_wire("wireresistor", ['resistor0'], ['ground0']))
    for index in range(number_inputs):
        i = str(index)
        wires.extend(make_wire('wireinput'+i, ['in'+i], ['switch'+i+"/button"]))
    
    data = {
        "name": device_type+"0",
        "type": device_type,
        "wires": wires,
        "devices": devices
    }

    device_file_path = str(DEVICE_DIR) + '/' + device_type + '.json'
    write_json(data, device_file_path)

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
            make_or_dual(number_inputs)
        else:
            make_or(number_inputs)


if __name__ == '__main__':
    main()
