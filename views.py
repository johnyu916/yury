from settings import CPU, DEVICE_PRIMITIVES
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


# Actually returns list of devices. The device itself
# and the dependent devices
def get_device(device_type, prefix=''):
    def type_in_documents(device_type, documents):
        for document in documents:
            if document['type'] == device_type:
                return True
        return False

    print "type: {0}".format(device_type)
    document = database()['devices'].find_one({'type':device_type})
    print document
    document['_id'] = str(document['_id'])
    documents = [document]
    for child_data in document['devices']:
        device_type = child_data['type']
        if not device_type in DEVICE_PRIMITIVES and not type_in_documents(device_type, documents):
            #need to load recursively
            documents.extend(get_device(child_data['type'], document['name']+'/'))

    return documents


