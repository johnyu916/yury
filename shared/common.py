#from settings import LESS_DIR, CSS_DIR
import shlex
import subprocess
import json
import math

def get_object(objects, name):
    for object in objects:
        if object.name == name:
            return object
    return None


def power(exponent):
    '''
    Return 2^exponent.
    '''
    return int(math.pow(2,exponent))


def log(integer):
    return int(math.log(integer,2))

def get_uint(bools):
    '''
    Get unsigned integer from list of True/False.
    '''
    r = 0
    for index, val in enumerate(bools):
        if val:
            number = power(index)
            #print "index: {0} uint number: {1}".format(index, number)
            r += number
    return r

def get_bools(integer, number_digits):
    '''
    Get list of bools from integer
    keep decreasing integer as binary digits are filled.
    '''
    bools = [False]*number_digits
    while(True):
        if integer == 0: break
        #highest = int(math.log(integer,2))
        highest = log(integer)
        if highest < number_digits:
            bools[highest] = True
        #integer -= int(math.pow(2,highest))
        integer -= power(highest)
    return bools


def get_bridge_type(bridge_name, wires_data):
    for wire in wires_data:
        wire_from = wire['from']
        for device_name in wire_from:
            if device_name == bridge_name:
                return 'input'
    return 'output'


def get_inputs_outputs(device_data):
    inputs = []
    outputs = []
    bridge_names = [child['name'] for child in device_data['devices'] if child['type'] == 'bridge']
    wires = device_data['wires']
    for bridge_name in bridge_names:
        if get_bridge_type(bridge_name, wires) == 'input':
            inputs.append(bridge_name)
        else:
            outputs.append(bridge_name)
    return (inputs, outputs)


def get_primitive_dict():
    '''
    Convert MongoDB document into string
    '''
    pass


def write_json(dict_data, file_path):
    '''
    Write json_str to file at file_path
    '''
    json_str = json.dumps(dict_data, indent=4)
    json_str_list = json_str.split('\n')
    print("Writing to file: {0}".format(file_path))
    with open(file_path, 'w') as t:
        for json_st in json_str_list:
            t.write(json_st+'\n')

#def update_css():
#    '''
#    If any less files changed, recompile css.
#    Currently does not suport subdirectories.
#    '''
#    names = {}
#    for filepath in LESS_DIR.files('*.less'):
#        name = filepath.name.split('.')[0]
#        names[name] = filepath
#
#    for name in names:
#        css_path = CSS_DIR / (name + '.css')
#        if css_path.exists():
#            css_time = css_path.getmtime()
#        else:
#            css_time = -1  # no css file, so create it
#        less_path = names[name]
#        if less_path.getmtime() >= css_time:
#            command = "recess {0} --compress".format(less_path)
#            print("calling command: {0}".format(command))
#            process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, shell=False)
#            (stdout, stderr) = process.communicate()
#            exit_status = process.wait()
#            if exit_status != 0 or stderr:
#                print("Error during compilation of less: {0}".format(less_path))
#                continue
#            with open(css_path, 'w') as css_file:
#                css_file.write(stdout)
            #print "calling recess on {0} and {1}".format(less_path, css_path)
            #subprocess.call(['recess', less_path, '--compress', '>', css_path], shell=False)
