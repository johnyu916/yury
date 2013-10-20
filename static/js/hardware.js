//fill wires
var sources = [];

function run_step(sources){
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
        var device_name = prefix + tokens[0];
        if (tokens.length == 2) {
            if (array_index(device_primitives, tokens[0]) >=0){
                //compound element inside.
                device_name += tokens[1];
            }
            else{
                device_pin = tokens[1];
            }
        }

        //console.log("device name: " + device_name);
        var device = device_map[device_name];
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
        sources = construct_device(devices_data);
        //also populate devices with wires.
        callback(sources);
    }).error(function(){
        console.log("load_device failed for " + device_type);
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
    $('#step').click(function(){
        //var display = "step: "+JSON.stringify(device.devices);
        //$("#debug-output").text(display);
        run_step(sources);
        for_each_wire(sources, print_wire_values);
    });
});
