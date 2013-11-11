import json
import itertools
import sys
from settings import DEVICE_DIR, TESTS_DIR
from shared.utilities import get_inputs_outputs, write_json


def get_mux_results(number_selects):
    number_inputs = pow(2,number_selects)
    mux_sets = itertools.product[True,False], repeat=len(number_selects)
    value_sets = itertools.product([False,True], repeat=len(number_selects + 1))
    outputs = []
    for value_set_index, value_set in enumerate(value_sets):
        #inputs are first few, selects are next
        inputs = value_set[:number_inputs]
        selects = value_set[number_inputs:]
        # now do mux operation
        or_val = True
        for input_value, mux_set in zip(inputs, mux_sets):
            and_val = True
            for select, mux in zip(selects, mux_set):
                if mux:
                    and_val = and_val and select
                else:
                    and_val = and_val and not select
            or_val = or_val or and_val
        output = or_val and input_value
        outputs.append(output)
    return outputs


def make_mux2_test(number_selects):
    device_type = "mux2"
    with open(DEVICE_DIR / device_type + 'json') as f:
        device_data =json.loads(f.read())

    results = get_mux_results(number_selects)
    tests = []
    for index, value in enumerate(results):
        test = {'device': device_type+'test'+str(index),
                'expected_value':[value]
                }
        tests.append(test)
    (input_names, output_names) = get_inputs_outputs(device_data)
    outputs = [device_type+'0/'+output for output in output_names]

    test = {
        "name": device_type+'test',
        'steps': 5,
        'output': outputs,
        'tests': tests
    }


def make_decoder_test(number_inputs, is_dual):
    # should be able to make dual and normal versions 
    # also varying number of inputs
    device_type = "decoder" + str(number_inputs)
    if is_dual:
        device_type += "dual"

    with open(DEVICE_DIR / device_type+'.json') as f:
        device_data = json.loads(f.read())

    (input_names, output_names) = get_inputs_outputs(device_data)
    test = {
        "name": device_type +"test",
        "device": device_type,
        "steps": 5,
    }

    test['input'] = [input_name for input_name in input_names]
    test['output'] = [output for output in output_names]
   
    tests = []
    value_sets = itertools.product([0,1], repeat=len(input_names))
    for number, inputs in enumerate(value_sets):
        inputs = inputs[::-1]
        values = []
        for inner_number in range(len(output_names)):
            if inner_number == number:
                values.append(1)
            else:
                values.append(0)
        test_case = {
            'i': inputs,
            'o': values
        }
        tests.append(test_case)
    test['tests'] = tests
    test_file_path = str(TESTS_DIR) + '/' + device_type + '.json'
    write_json(test, test_file_path)

def main():
    option = sys.argv[1]
    if option == 'decoder':
        number_inputs = int(sys.argv[2])
        if len(sys.argv) > 3:
            is_dual = True
        else:
            is_dual = False
        make_decoder_test(number_inputs, is_dual)

if __name__ == '__main__':
    main()
