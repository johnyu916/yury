# load devices
# try to load devices from the descriptions directory.
# if device already exists, don't load again.
# 'type' is a unique index.
from settings import DEVICE_DIR, DEVICE_TESTS_DIR, TESTS_DIR, DEVICE_PRIMITIVES
from shared.utilities import write_json

from database import database
import json
import itertools
import math
import sys
import traceback

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


def make_test_devices(input_limit=6):
    # if there are 6 inputs, then 2^6=64 files will be created.
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
            if len(input_names) > input_limit:
                print "Not creating tests, too many inputs: {0}".format(len(input_names))
                continue

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
                device_file_path = str(DEVICE_TESTS_DIR) + '/' + test_type + '.json'
                write_json(device_dict, device_file_path)

def get_wire(wires, name):
    for wire in wires:
        if wire['name'] == name:
            return wire
    return None


def check_devices(dont_stop=True):
    for filepath in DEVICE_DIR.walkfiles('*.json'):
        try:
            check_device(filepath)
        except Exception as e:
            print traceback.print_exc()
            print "Failed device check"
            if dont_stop:
                continue
            else:
                raise e

def check_device(filepath):
    with open(filepath) as f:
        print "Reading {0}".format(filepath)
        content = f.read()
        device = json.loads(content)
        # make sure it has name and type
        name = device['name']
        device_type = device['type']
        file_name = str(filepath.name).split('.')[0]
        assert device_type == file_name, "{0} not equal to {1}".format(device_type, file_name)
        devices = device['devices']
        child_infos = {}
        for child in devices:
            # device name is unique
            child_name = child['name']
            assert not child_name in child_infos, "{0} is already defined".format(child_name)
            child_type = child['type']
            child_infos[child_name] = child_type
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
                name = names[0]
                assert name in child_infos, "{0} not one of the devices".format(name)
                child_type = child_infos[name]
                if not child_type in DEVICE_PRIMITIVES:
                    assert len(names) == 2, "{0} needs port".format(from_device)
                if len(names) == 2:
                    port = names[1]
                    if child_type in DEVICE_PRIMITIVES:
                        assert port == 'to', '{0} invalid'.format(from_device)

            for to_device in wire['to']:
                names = to_device.split('/')
                assert len(names) in (1,2)
                name = names[0]
                assert names[0] in child_infos, "{0} not in device names".format(names[0])
                child_type = child_infos[name]
                if not child_type in DEVICE_PRIMITIVES:
                    assert len(names) == 2, "{0}, type {1} needs port".format(to_device, child_type)
                if len(names) == 2:
                    port = names[1]
                    if child_type in DEVICE_PRIMITIVES:
                        if child_type == 'switch':
                            #can be either from or button
                            assert port in ('from', 'button')
                        else:
                            assert port == 'from', "{0} invalid".format(to_device)


def main():
    if len(sys.argv) == 1:
        check_devices(dont_stop=False)
        update_db()
        make_test_devices()
        update_db()
        update_tests()
        return

    option = sys.argv[1]
    if option == 'check_devices':
        check_devices()
    if option == 'update_db':
        update_db()
    elif option == 'make_test_devices':
        make_test_devices()
    elif option == 'update_tests':
        update_tests()

if __name__ == '__main__':
    main()
