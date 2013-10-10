//fill wires
var primitives = ['resistor', 'source', 'ground', 'switch', 'bridge'];
var device_map = {};

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

function load_device(device_type, callback){
    $.ajax({
        url: '/device?type='+selected
    }).done(function(server_data){
        var device_data = server_data['device'];
        var wires_data = device_data['wires'];
        var wires = get_wires(wires_data);
        device = new Device(device_data['name'], device_data['type']);
        device_map[device.name] = device;
        var type = device_data['type'];
        children_data = device_data.devices;
        for (var i = 0; i < children_data.length; i++){
            child_data = children_data[i];
            child = new Device(child_data['name'], child_data['type']);
            if (!(child.type in primitives)){
                load_device(child.type);
            }
            device_map[child.name] = child;
        }
        var wires_data = device_data.children;
        for (var i = 0; i < wires_data.length; i++){
            var wire_data = wires_data[i];
            var froms_data = wire_data.from;
            for (var j = 0; j < froms_data.length; j++){
                var from_data = froms_data[j];
                device = device_map[from_data];
                // get from data.
            }
            var to_data = wire_data.to;
            var wire = new Wire(wires_dtata.name, from, to);
        }
    }).error(function(){
        console.log("load_device failed for " + device_type);
    });
}

$(document).ready(function() {
    var device = null;
    $('#device-type-button').click(function(){
        /* load the device */
        var selected = $('#device-type-select').val();
        load_device(selected, function(){
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
