/*
 *
 */
function compute(device){
    
}

function getIsConnected(devices, device, element){
    var wire = get_wire(device.wires, element.name, 'from');
    for (var i = 0; i < wire.to.length; i++){
        var nextElement = wire.to[i];
        var type = nextElement.type;
        if (type == 'resistor'){
            return getIsConnected(devices, device, nextElement);
        }
        else if (type == 'switch'){
            if (wire == element.button){
                //this wire is linked to button
                return false;
            }
            if (element.button.voltage == true){
                return getIsConnected(devices, device, element);
            }
        }
        else if (type == 'ground'){
            return true;
        }
    }
    return false;
}
function getIsConnectedOld(devices, device, element){
    var wire = element.to;
    for (var i = 0; i < element.to.length; i++){
        var nextElement = wire.to.to;
        var type = nextElement.type;
        if (type == 'resistor'){
            return getIsConnected(devices, device, nextElement);
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

function setVoltage(devices, device, source){
    console.log("setVoltage source name: " + source.name);
    var is_connected = getIsConnected(devices, device, source);
    console.log("setVoltage isConnected: " + is_connected);
    spreadVoltage(source.to, true, is_connected);
}

function spreadVoltage(wire, voltage, isConnected){

    wire.voltage = voltage;
    var element = wire.to;
    //TODO: wire has multiple elements
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

function forEachPrimitive(devices, device, type, func){
    // initially power on everything.
    //var display = "foreach: "+JSON.stringify(device);
    //$("#debug-output").text(display);
    for (var i = 0; i < device.devices.length; i++){
        var child = device.devices[i];
        if (in_array(child.type, device_primitives) < 0){
            console.log('inspecting child: ' + child.name);
            device = get_device(devices, child.name);
            forEachPrimitive(devices, device, type, func);
        }
        else{
            console.log("type checking for device: "+device.name);
            if (child.type == type){
                console.log("type matches for device: "+device.name);
                func(devices, device, child);
            }
        }
    }
}


function forEachElementNotUsed(device, type, func){
    // initially power on everything.
    //var display = "foreach: "+JSON.stringify(device);
    //$("#debug-output").text(display);
    if (in_array(device.type, device_primitives) < 0){
        for (var i = 0; i < device.devices.length; i++){
            var child = device.devices[i];
            console.log('inspecting child: ' + child.name);
            is_finished = forEachElement(child, type, func);
            if (is_finished) return true;
        }
    }
    else{
        console.log("type checking for device: "+device.name);
        if (device.type == type){
            console.log("type matches for device: "+device.name);
            var is_finished = func(device);
            if (is_finished) return true;
        }
    }
    return false;
}
