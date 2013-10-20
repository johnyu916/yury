# load devices
# try to load devices from the descriptions directory.
# if device already exists, don't load again.
# 'type' is a unique index.
from settings import DEVICE_DIR

from database import database
import json

def update_database():
    db = database()
    for filepath in DEVICE_DIR.walkfiles('*.json'):
        with open(filepath) as f:
            print "Reading {0}".format(filepath)
            data = f.read()
            json_dict = json.loads(data)
            db['devices'].update({'type': json_dict['type']},json_dict,upsert=True)

def get_bridge_type(bridge, wires):
    for wire in wires:
        wire_from = wire['from']
        for device_name in wire_from:
            if device_name == bridge['name']:
                return 'input'
    return 'output'

def make_test():
    for filepath in DEVICE_DIR.files('*.json'):
        with open(filepath) as f:
            print "Reading {0}".format(filepath)
            json_dict = json.loads(f.read())
            # look for inputs
            bridges = [child['type'] for child in json_dict['devices'] if child['type'] == 'bridge']
            wires = json_dict['wires']
            for bridge in bridges:
                bridge['bridge_type'] = get_bridge_type(bridge, wires)
            #TODO: fill out inputs
            #inputs = 
    

if __name__ == '__main__':
    main()
