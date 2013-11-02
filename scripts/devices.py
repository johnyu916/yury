# load devices
# try to load devices from the descriptions directory.
# if device already exists, don't load again.
# 'type' is a unique index.
from settings import DEVICE_DIR, DEVICE_TESTS_DIR, TESTS_DIR

from database import database
import json
import itertools
import math
import sys

def update_db():
    db = database()
    for filepath in DEVICE_DIR.walkfiles('*.json'):
        with open(filepath) as f:
            print "Reading {0}".format(filepath)
            data = f.read()
            json_dict = json.loads(data)
            # TODO: should check device here to see if it is valid
            db['devices'].update({'type': json_dict['type']},json_dict,upsert=True)

def update_tests():
    db = database()
    for filepath in TESTS_DIR.walkfiles('*.json'):
        with open(filepath) as f:
            print "Reading {0}".format(filepath)
            data = f.read()
            json_dict = json.loads(data)
            db['tests'].update({'name': json_dict['name']}, json_dict, upsert=True)


def get_bridge_type(bridge_name, wires):
    for wire in wires:
        wire_from = wire['from']
        for device_name in wire_from:
            if device_name == bridge_name:
                return 'input'
    return 'output'


def make_test_devices():
    for filepath in DEVICE_DIR.files('*.json'):
        with open(filepath) as f:
            print "Reading {0}".format(filepath)
            json_dict = json.loads(f.read())
            # look for input_names
            bridge_names = [child['name'] for child in json_dict['devices'] if child['type'] == 'bridge']
            wires = json_dict['wires']
            input_names = []
            outputs = []
            for bridge_name in bridge_names:
                if get_bridge_type(bridge_name, wires) == 'input':
                    input_names.append(bridge_name)
                else:
                    outputs.append(bridge_name)
            value_sets = itertools.product([False,True], repeat=len(input_names))
            for value_set_index, value_set in enumerate(value_sets):
                value_set = reversed(value_set)
                device_type = json_dict['type']
                test_type = device_type + 'test' + str(value_set_index)
                device_dict = {
                    'name': test_type + '0',
                    'type': test_type
                }
                device_name = device_type + '0'
                devices = [
                    {
                        'name': device_name,
                        'type': device_type
                    }
                ]
                wires = []
                for index, input_name in enumerate(input_names):
                    device = { 'name': 'input'+ str(index), 'type':'input' }
                    devices.append(device)
                    wire = {
                        'name': 'wire'+str(index),
                        'from': [],
                        'to': [device_name + '/' + input_name]
                    }
                    wires.append(wire)
                for index, value in enumerate(value_set):
                    wire = wires[index]
                    if value:
                        out = 'out1'
                    else:
                        out = 'out0'
                    wire['from'].append('input' + str(index) + '/' + out)
                device_dict['devices'] = devices
                device_dict['wires'] = wires
                json_str = json.dumps(device_dict)
                with open(str(DEVICE_TESTS_DIR) + '/' + test_type + '.json', 'w') as t:
                    t.write(json_str)

def make_mux_dual(number_selects):
    '''
    Make mux circuit.
    A mux circuit is the following:
    O = SA + not(S)B
    '''
    device_type = "mux"+str(number_inputs)+"dual"
    devices = []

    number_inputs = math.pow(2, number_selects)
    
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
        "name": "or0"
        "type": "or"+str(number_inputs)
    }
    devices.append(device)

    # wires
    wires = []
    for i in range(number_inputs):
        index = str(i)
        # input to and
        wire = {
            "name": "wire"+index,
            "from": ["in"+index],
            "to": ["and"+index+"/in0"]
        }
        # and to or
        wire = {
            "name": "and"+index,
            "from":["and"+index+"/out"],
            "to":["or0/in"+index]
        }

    for index in range(number_selectors):
        # from selector and from not selector
        wire = {
            "name": "wireselect"+str(index),
            "from": ["select"+str(index)],
            "to": ["not"+str(index)]
        }
        wires.append(wire)
        wire = {
            "name": "wireselectnot"+str(index),
            "from": ["not"+str(index)],
            "to": []
        }
        wires.append(wire)

    
    value_sets = itertools.product([False,True], repeat=num_selects)
    for value_set_index, value_set in enumerate(value_sets):
        value_set = reversed(value_set)
        vi = str(value_set_index)
        wire = wires['wirein'+vi]
        wire['to'].append("and"+vi+"/in"+str(num_selects))
        for index, value in enumerate(value_set):
            i = str(index)
            if value:
                wire = wires['select'+i]
                wire['to'].append("and"+vi+"/in"+i)
            else:
                wire = wires['selectnot'+i]
                wire['to'].append("and"+vi+"/in"+i)
            wires.append(wire)

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

    json_str = json.dumps(data)
    with open(str(DEVICE_DIR) + '/' + device_type + '.json', 'w') as t:
        t.write(json_str)

def make_decoder_dual(number_inputs):
    number_outputs = math.pow(2, number_inputs)
    device_type = "decoder" + str(number_outputs) + "dual"
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
            "type": "and2"
        }
        devices.append(device)

    for index in range(number_inputs):
        i = str(index)
        wire = {
            "name": "wirein"+i,
            "from": ["in"+i],
            "to": ["not"+i]
        }
        wires.append(wire)
        wire = {
            "name": "wirenot"+i,
            "from": ["not"+i],
            "to": []
        }
        wires.append(wire)

    for index in range(number_outputs):
        i = str(index)
        wire = {
            "name": "wireand"+i,
            "from":["and"+i],
            "to":["out"+i]
        }
        wires.append(wire)

    value_sets = itertools.product([False,True], repeat=num_selects)
    for value_set_index, value_set in enumerate(value_sets):
        value_set = reversed(value_set)
        vi = str(value_set_index)
        wire = wires['wirein'+vi]

        for index, value in enumerate(value_set):
            i = str(index)
            if value:
                wire = wires['wirein'+i]
            else:
                wire = wires['wirenot'+i]
                wire['to'].append("and"+vi+"/in"+i)
            wires.append(wire)

    json_str = json.dumps(data)
    with open(str(DEVICE_DIR) + '/' + device_type + '.json', 'w') as t:
        t.write(json_str)

def check_devices(dont_stop=True):
    for filepath in DEVICE_DIR.walkfiles('*.json'):
        try:
            check_device(filepath)
        except Exception as e:
            print "Failed device check: {0}".format(str(e))
            if dont_stop:
                continue
            else:
                raise e

def check_device(filepath):
    with open(filepath) as f:
        print "Reading {0}".format(filepath)
        content = f.read()
        device = json.loads(data)
        # make sure it has name and type
        name = device['name']
        device_type = device['type']
        devices = device['devices']
        child_names = {}
        for child in devices:
            child_name = child['name']
            assert not child_name in child_names
            child_names[child_name] = True
            child_type = child['type']
            # ensure type is not recursive
            assert not child_type == device_type

        wires = device['wires']
        wire_names = {}
        for wire in wires:
            wire_name = wire['name']
            assert not wire_name in wire_names
            wire_names[wire_name] = True
            for from_device in wire['from']:
                names = from_device.split('/')
                assert len(names) in (1,2)
                assert names[0] in child_names

            for to_device in wire['to']:
                names = to_device.split('/')
                assert len(names) in (1,2)
                assert names[0] in child_names


def main():
    print sys.argv
    if len(sys.argv) == 1:
        check_devices(dont_stop=False)
        update_db()
        make_test_devices()
        update_db()
        update_tests()
        return

    option = sys.argv[1]
    if option == 'update_db':
        update_db()
    elif option == 'make_test_devices':
        make_test_devices()
    elif option == 'update_tests':
        update_tests()

if __name__ == '__main__':
    main()
