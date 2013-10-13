//fill wires
var primitives = ['resistor', 'source', 'ground', 'switch', 'bridge'];
var device_map = {};
var load_counter = 0;

function run_step(device){
    forEachElement(device, 'source', setVoltage);
    var wires = device.wires;
    var wires = $(".wire-list");
    set_wire_values(wires);
}

function set_wire_values(wires){
    for (var i = 0; i < wires.length; i++){
        var wire = wires[i];
        var wire_id = "#wire-" + i;
        $(wire_id).text(JSON.stringify(wire));
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
    load_counter++;
    $.ajax({
        url: '/device?type='+device_type
    }).done(function(server_data){
        var device_data = server_data['device'];
        var wires_data = device_data['wires'];
        var wires = get_wires(wires_data);
        var device = new Device(device_data['name'], device_data['type']);
        device_map[device.name] = device;
        var type = device_data['type'];
        children_data = device_data.devices;

        //sub-devices.
        var children = []
        for (var i = 0; i < children_data.length; i++){
            child_data = children_data[i];
            child = new Device(child_data['name'], child_data['type']);
            if (in_array(child.type, primitives) < 0){
                load_device(child.type, callback);
            }
            device_map[child.name] = child;
            children.push(child);
        }
        device.devices = children;

        //wires.
        var wires_data = device_data.wires;
        for (var i = 0; i < wires_data.length; i++){
            var wire_data = wires_data[i];
            var wire = new Wire(wire_data.name);
            //from devices
            var from = parse_wire_links(wire, wire_data.from, device_map, 'to');
            var to = parse_wire_links(wire, wire_data.to, device_map, 'from');
            wire.from = from;
            wire.to = to;
        }

        load_counter--;
        if (load_counter == 0){
            callback();
        }
        return device;
    }).error(function(){
        console.log("load_device failed for " + device_type);
    });
}

$(document).ready(function() {
    var device = null;
    $('#device-type-button').click(function(){
        /* load the device */
        var selected = $('#device-type-select').val();
        device = load_device(selected, function(){
            $("#debug-output").text(JSON.stringify(device));
            reset_wires(device.wires.length);
            set_wire_values(device.wires);
        });
    });
    $('#step').click(function(){
        //var display = "step: "+JSON.stringify(device.devices);
        var display = device.devices.length;
        //$("#debug-output").text(display);
        run_step(device);
    });
});
