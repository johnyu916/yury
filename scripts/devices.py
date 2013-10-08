# load devices
# try to load devices from the descriptions directory.
# if device already exists, don't load again.
# 'type' is a unique index.
from settings import DEVICE_DIR

from database import database
import json

def main():
    db = database()
    for filepath in DEVICE_DIR.files('*.json'):
        with open(filepath) as f:
            print "Reading {0}".format(filepath)
            data = f.read()
            json_dict = json.loads(data)
            db['devices'].update({'type': json_dict['type']},json_dict,upsert=True)

if __name__ == '__main__':
    main()
