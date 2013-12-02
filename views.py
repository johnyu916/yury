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
    test_names = database()['tests'].find({},{'name':1})
    context = {'devices': devices, 'test_names': test_names}
    return context


def fill_devices(device_documents, device_type, prefix=''):
    '''
    Actually returns list of devices. The device itself
    and the dependent devices
    '''
    def type_in_documents(device_type):
        for document in device_documents:
            if document['type'] == device_type:
                return True
        return False
    if type_in_documents(device_type): return

    print "looking for type: {0}".format(device_type)
    document = database()['devices'].find_one({'type':device_type})
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

def get_test(test_name):
    document = database()['tests'].find_one({'name':test_name})
    return get_test_package(document)


def get_tests():
    '''
    Get a list of tests.
    First get test documents
    '''
    return_docs = []
    documents = database()['tests'].find()
    for test_document in documents:
        return_docs.append(get_test_package(test_document))
    return return_docs


def get_test_package(test_document):
    ''' 
    Return all documents necessary for test
    '''
    test_document['_id'] = str(test_document['_id'])
    test_name = test_document['name']
    device_types = [test_name+str(index) for index in range(len(test_document['tests']))]
    #device_types = [test['device'] for test in test_document['tests']]
    device_documents = []
    for device_type in device_types:
        fill_devices(device_documents, device_type)
    return {
        'config': test_document,
        'devices': device_documents
    }
