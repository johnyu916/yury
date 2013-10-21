//fill wires
var sources = [];

function run_step(sources){
    console.log("Running step");
    var i = sources.length;
    while (i--){
        set_voltage(sources[i])
    }
}
function run_step_old(devices){
    //find root
    forEachElement(devices, get_root(devices), 'source', setVoltage);
    var wires = device.wires;
    var wires = $(".wire-list");
    print_wire_values(wires);
}

function fill_wires(wire, wires){
    wires.push({
        'name': wire.name,
        'voltage': wire.voltage
    });
}

function print_wire_values(wire){
    console.log('wire: ' + wire.name + ' voltage: ' + wire.voltage);
}
function print_wire_values_old(wires){
    for (var i = 0; i < wires.length; i++){
        var wire = wires[i];
        var wire_id = "#wire-" + i;
        $(wire_id).text(JSON.stringify(wire_dict(wire)));
    }
}

function reset_wires(length){
    var wires = $("#wire-list");
    wires.empty();
    for (var i = 0; i < length; i++){
        var wire_id = "wire-" + i;
        var text = '<li><div id="'+wire_id+'"></div></li>';
        wires.append(text);
    }
}

function get_wires(wires_data){
    var wires = [];
    for (var i = 0; i < wires_data.length; i++){
        var wire = new Wire(wires_data['name'])
        wires.push(name);
    }
    return wires;
}

// get the list of devices that wire points to.
// also update device's wires.
function parse_wire_links(wire, path_list, device_map, device_pin, prefix){
    device_list = [];
    for (var i = 0; i < path_list.length; i++){
        var path = path_list[i];
        var tokens = path.split('/');
        var device_name = prefix + path;
        if (!(device_name in device_map)){
            //console.log("parse_wire not in device map: " + device_name);
            var length = tokens.length;
            device_name = prefix + tokens[length-2];
            device_pin = tokens[length-1];
        }
        var device = device_map[device_name];

        //console.log("parse_wire device name: " + device_name);
        device[device_pin] = wire;
        device_list.push(device);
    }
    return device_list;
}

function load_device(device_type, callback){
    $.ajax({
        url: '/device?type='+device_type
    }).done(function(server_data){
        var devices_data = server_data['device'];
        var sources = construct_device(devices_data, device_type);
        //also populate devices with wires.
        callback(sources);
    }).error(function(){
        console.log("load_device failed for " + device_type);
    });
}

function find_element(element, args){
    var search_name = args['name'];
    //console.log('looking into element: '+element.name);
    if (element.name == search_name) {
        //console.log('search name found: ' + search_name);
        args.element = element;
    }
}

function run_test(test_package){
    var config = test_package['config'];
    var devices_data = test_package['devices'];
    var tests = config['tests'];
    var steps = config.steps;
    var passed = 0;
    for (var i = 0; i < tests.length; i++){
        var test = tests[i];
        var sources = construct_device(devices_data, test.device);
        //now run steps
        var counter = steps;
        while (counter--){
            run_step(sources);
        }
        var device_data = get_device_data(devices_data, test.device);
        var output_name = '/' + device_data.name + '/' + config.output;
        console.log("output name " + output_name);
        args = {
            'name': output_name,
            'element': null
        };
        for_each_device(sources, find_element, args);
        console.log('expected_value: ' + test.expected_value + ' actual: ' + args.element.from.voltage);
        if (test.expected_value == args.element.from.voltage){
            console.log("test passed");
            passed += 1;
        }
        else{
            console.log("test failed");
        }
    }
    console.log("passed " + passed + " of " + tests.length);
}

function run_tests(){
    $.ajax({
        url: '/tests'
    }).done(function(server_data){
        test_packages = server_data['test_packages']
        for (var i = 0; i < test_packages.length; i++){
            run_test(test_packages[i]);
        }
    }).error(function(){
        console.log("run_tests failed");
    });
}

function test_input(bridge_name, value){
    var type = 'ground';
    if (value) type = 'source';
    return new Device(bridge_name + type, type);
}

/*
function test(device, input0, input1){
    var in0 = device_map['in0'];
    var in1 = device_map['in1'];
    var test0 = test_input(in0.name, input0);
    var wire0 = new Wire(in0.name+'wire',
    var test1 = test_input(in1.name, input1);
}
*/
function test(device){
    run_step(device);
}

$(document).ready(function() {
    $('#device-type-button').click(function(){
        /* load the device */
        var selected = $('#device-type-select').val();
        load_device(selected, function(sources){
            $("#debug-output").text(sources_json(sources));
            //reset_wires(device.wires.length);
            for_each_wire(sources, print_wire_values);
        });
    });
    $('#test-type-select').on('change', function(){
        var selected = $('#test-type-select').val();
        if (selected == 'andtest'){
            load_device('andtest', function(device_data){
                test(device_data);
                /*
                inputs = get_inputs(2);
                for (var i = 0; i < inputs.length; i++){
                    test(device, inputs[i][0], inputs[i][1]);              
                }
                */
            });
        }
    });
    $('#run-tests').on('click', function(){
        run_tests();
    });
    $('#step').click(function(){
        //var display = "step: "+JSON.stringify(device.devices);
        //$("#debug-output").text(display);
        run_step(sources);
        for_each_wire(sources, print_wire_values);
    });
});
