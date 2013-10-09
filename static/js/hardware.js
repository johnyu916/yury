//fill wires
var primitives = ['resistor', 'source', 'ground', 'switch', 'bridge'];

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
        var type = device_data['type'];
        if (type in primitives){
            if (type == 'resistor'){

            }
            else if (type == ''){

            }
        }
        else{
            children = device.devices;
            for (var i = 0; i < children.length; i++){
                child = children[i];
                
            }
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
