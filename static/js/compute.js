/*
 *
 */
function compute(device){
    
}

function getIsConnected(element){
    var wires = element.to;
    for (var i = 0; i < element.to.length; i++){
        var nextElement = wire.to.to;
        var type = nextElement.type;
        if (type == 'resistor'){
            return getIsConnected(nextElement);
        }
        else if (type == 'switch'){
            if (wire == element.button){
                //this wire is linked to button
                return false;
            }
            if (element.button.voltage == true){
                return getIsConnected(element);
            }
        }
        else if (type == 'ground'){
            return true;
        }
    }
    return false;
}

function setVoltage(source){
    var is_connected = getIsConnected(source);
    spreadVoltage(source.to, true, isConnected);
}

function spreadVoltage(wire, voltage, isConnected){
    wire.voltage = voltage;
    var element = wire.to;
    var type = element.type;
    if (type == 'resistor'){
        if (isConnected) spreadVoltage(element.to, voltage, isConnected);
        else spreadVoltage(element.to, false, isConnected);
    }
    if (type == 'switch'){
        if (element.button.voltage == true){
            spreadVoltage(element.to, voltage, isConnected);
        }
        else spreadVoltage(element.to, false, isConnected);
    }
    if (type == 'ground'){
        return;
    }
}


function forEachElement(device, type, func){
    // initially power on everything.
    var display = "foreach: "+JSON.stringify(device);
    $("#debug-output").text(display);
    if ('devices' in device){
        for (var i = 0; i < device.devices.length; i++){
            var child = device.devices[i];
            var is_finished = forEachElement(child);
            if (is_finished) return true;
        }
    }
    else{
        if (device.type == type){
            var is_finished = func(element);
            if (is_finished) return true;
        }
    }
    return false;
}
