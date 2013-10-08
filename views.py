from settings import CPU
from database import database

def cpu():
    # Include settings
    context = {
        'CPU' : CPU
    }
    return context

def hardware():
    devices = database()['devices'].find({},{'type':1})
    context = {'devices': devices}
    return context

def get_device(device_type):
    document = database()['devices'].find_one({'type':device_type})
    document['_id'] = str(document['_id'])
    return document


