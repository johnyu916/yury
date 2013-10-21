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
def fill_devices(device_documents, device_type, prefix=''):
    def type_in_documents(device_type):
        for document in device_documents:
            if document['type'] == device_type:
                return True
        return False
    if type_in_documents(device_type): return

    print "type: {0}".format(device_type)
    document = database()['devices'].find_one({'type':device_type})
    print document
    document['_id'] = str(document['_id'])
    device_documents.append(document)
    for child_data in document['devices']:
        device_type = child_data['type']
        if not device_type in DEVICE_PRIMITIVES:
            #need to load recursively
            fill_devices(device_documents, child_data['type'], document['name']+'/')

def get_device_documents(device_type):
    documents = []
    fill_devices(documents, device_type)
    return documents

def get_tests():
    '''
    Get a list of tests.
    First get test documents
    '''
    return_docs = []
    documents = database()['tests'].find()
    for test_document in documents:
        test_document['_id'] = str(test_document['_id'])
        device_types = [test['device'] for test in test_document['tests']]
        device_documents = []
        for device_type in device_types:
            fill_devices(device_documents, device_type)
        return_doc = {
            'config': test_document,
            'devices': device_documents
        }
        return_docs.append(return_doc)
    return return_docs
