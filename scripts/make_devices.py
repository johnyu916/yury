from shared.utilities import write_json


def make_mux(number_selects):
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


def make_mux_dual(number_selects):
    number_inputs = int(math.pow(2, number_selects))
    device_type = "mux"+str(number_inputs)
    devices = []

def make_decoder(number_inputs):
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

def make_decoder_dual(number_inputs):
    number_outputs = int(math.pow(2, number_inputs))
    device_type = "decoder" + str(number_inputs) + "dual"
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
            "name": "in"+i+"down",
            "type": "bridge"
        }
        devices.append(device)
        device = {
            "name": "in"+i+"up",
            "type": "bridge"
        }
        # not gate for every input
        devices.append(device)
        device = {
            "name": "not"+i,
            "type": "notdual"
        }
        devices.append(device)

    for index in range(number_outputs):
        # outputs
        i = str(index)
        device = {
            "name": "out"+i+"down",
            "type": "bridge"
        }
        device = {
            "name": "out"+i+"up",
            "type": "bridge"
        }
        devices.append(device)
        # and gate for every output
        device = {
            "name": "and"+i,
            "type": "and2dual"
        }
        devices.append(device)

    for index in range(number_inputs):
        # wire between input and not 
        i = str(index)
        wire = {
            "name": "wirein"+i+"down",
            "from": ["in"+i+"down"],
            "to": ["not"+i+"/indown"]
        }
        wires.append(wire)

        wire = {
            "name": "wirein"+i+"up",
            "from": ["in"+i+"up"],
            "to": ["not"+i+"/inup"]
        }
        wires.append(wire)

        # wire from not
        wire = {
            "name": "wirenot"+i+"down",
            "from": ["not"+i+"/outdown"],
            "to": []
        }
        wires.append(wire)
        wire = {
            "name": "wirenot"+i+"up",
            "from": ["not"+i+"/outup"],
            "to": []
        }
        wires.append(wire)

    for index in range(number_outputs):
        # wire from and to out
        i = str(index)
        wire = {
            "name": "wireand"+i+"down",
            "from":["and"+i+"/outdown"],
            "to":["out"+i+"down"]
        }
        wires.append(wire)
        wire = {
            "name": "wireand"+i+"up",
            "from":["and"+i+"/outup"],
            "to":["out"+i+"up"]
        }
        wires.append(wire)

    value_sets = itertools.product([False,True], repeat=number_inputs)
    for value_set_index, value_set in enumerate(value_sets):
        # send wires to vi'th and gate. wires from in or not inputs.
        value_set = reversed(value_set)
        vi = str(value_set_index)

        for index, value in enumerate(value_set):
            i = str(index)
            if value:
                wire = get_wire(wires,'wirein'+i+'down')
                wire['to'].append("and"+vi+"/in"+i+'down')
                wire = get_wire(wires,'wirein'+i+'up')
                wire['to'].append("and"+vi+"/in"+i+'up')
            else:
                wire = get_wire(wires,'wirenot'+i+'down')
                wire['to'].append("and"+vi+"/in"+i+'down')
                wire = get_wire(wires,'wirenot'+i+'up')
                wire['to'].append("and"+vi+"/in"+i'up')

    device_file_path = str(DEVICE_DIR) + '/' + device_type + '.json'
    write_json(data, device_file_path)


def main():
    option = sys.argv[1]
    if option == 'make_mux':
        number_selects = int(sys.argv[2])
        make_mux(number_selects)
    elif option == 'make_decoder':
        number_inputs = int(sys.argv[2])
        make_decoder(number_inputs)

if __name__ == '__main__':
    main()
