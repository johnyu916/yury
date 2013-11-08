
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


def make_mux2_test():
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
    number_outputs = int(math.pow(2, number_inputs))
    device_type = "decoder" + str(number_inputs)
    if is_dual:
        device_type += "dual"

    with open(DEVICE_DIR / device_type+'json') as f:
        device_data = json.loads(f.read())

    test = {
        "name": device_type +"test",
        "steps": 5,
    }

    (input_names, output_names) = get_inputs_outputs(device_data)
    test['output'] = [device_type+'0/'+output for output in output_names]
   
    tests = []
    for number in range(len(output_names)):
        values = []
        for inner_number in range(len(output_names)):
            if inner_number == number:
                values.append(True)
            else:
                values.append(False)
        test = {
            'device': device_type + "test" + str(number),
            'expected_value': values
        }
        tests.append(test)
    test['tests'] = tests

def main():
    pass

if __name__ == '__main__':
    main()
