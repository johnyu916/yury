//fill wires
var device_map = {};
var load_counter = 0;

function run_step(devices){
    //find root
    forEachElement(devices, get_root(devices), 'source', setVoltage);
    var wires = device.wires;
    var wires = $(".wire-list");
    print_wire_values(wires);
}

function print_wire_values(wires){
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

function parse_wire_links(wire, data, device_map, device_pin){
    device_list = [];
    for (var i = 0; i < data.length; i++){
        var path = data[i];
        var tokens = path.split('/');
        var device_name = tokens[0];
        if (tokens.length == 2) device_pin = tokens[1];

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
        //also populate devices with wires.
        for (var i = 0; i < devices_data.length; i++){
            add_wire_data(devices_data[i]);
        }
        callback(devices_data);
    }).error(function(){
        console.log("load_device failed for " + device_type);
    });
}


function load_device_old(device, device_type, callback){
    load_counter++;
    $.ajax({
        url: '/device?type='+device_type
    }).done(function(server_data){
        var device_data = server_data['device'];
        var wires_data = device_data['wires'];
        device.name = device_data['name'];
        device.type = device_data['type'];
        device_map[device.name] = device;
        var type = device_data['type'];
        children_data = device_data.devices;

        //sub-devices.
        var children = []
        for (var i = 0; i < children_data.length; i++){
            child_data = children_data[i];
            child_type = child_data['type'];
            var child = null;
            if (in_array(child_type, device_primitives) < 0){
                child = new Device();
                load_device(child, child_type, callback);
            }
            else{
                child = new Device(child_data['name'], child_type);
            }
            device_map[child.name] = child;
            children.push(child);
        }
        device.devices = children;

        //wires.
        var wires_data = device_data.wires;
        var wires = [];
        for (var i = 0; i < wires_data.length; i++){
            var wire_data = wires_data[i];
            var wire = new Wire(wire_data.name);
            //from devices
            var from = parse_wire_links(wire, wire_data.from, device_map, 'to');
            var to = parse_wire_links(wire, wire_data.to, device_map, 'from');
            wire.from = from;
            wire.to = to;
            wires.push(wire);
        }
        device.wires = wires;

        load_counter--;
        if (load_counter == 0){
            callback();
        }
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
    var device = new Device();
    $('#device-type-button').click(function(){
        /* load the device */
        var selected = $('#device-type-select').val();
        load_device(selected, function(){
            $("#debug-output").text(device_json(device));
            reset_wires(device.wires.length);
            print_wire_values(device.wires);
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
        var display = device.devices.length;
        //$("#debug-output").text(display);
        run_step(device);
    });
});
