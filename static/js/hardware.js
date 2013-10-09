//fill wires

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

$(document).ready(function() {
    var device = null;
    $('#device-type-button').click(function(){
        /* load the device */
        var selected = $('#device-type-select').val();
        $.ajax({
            url: '/device?type='+selected
        }).done(function(server_data){
            device = server_data['device']
            $("#debug-output").text(JSON.stringify(device));
            reset_wires(device.wires.length);
            set_wire_values(device.wires);
            //construct device with it
        });
    });
    $('#step').click(function(){
        //var display = "step: "+JSON.stringify(device.devices);
        var display = device.devices.length;
        //$("#debug-output").text(display);
        run_step(device);
    });
});
