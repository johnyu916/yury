/*
 *
 */
function compute(device){
    
}

// Mark resistors as active if there is current flowing through it.
function activate_resistors(device){
    console.log("getisconnec devicename: "+device.name);
    var wire = device.to;
    if (wire == null) return false;
    //console.log("getisconnec wirename: "+wire.name);
    var is_connected = false;
    for (var i = 0; i < wire.to.length; i++){
        var next_device = wire.to[i];
        console.log("getisconnec next devicename: "+next_device.name);
        var type = next_device.type;
        if (type == 'resistor'){
            if (activate_resistors(next_device)) {
                next_device.active = true;
                is_connected = true;
            }
        }
        else if (type == 'switch'){
            if (wire.name == next_device.button.name){
                //this wire is linked to button
            }
            if (next_device.button.voltage == true){
                if (activate_resistors(next_device)) is_connected = true;
            }
        }
        else if (type == 'ground'){
            is_connected = true;
        }
        else if (type == 'bridge'){
            if (activate_resistors(next_device)) is_connected = true;
        }
        else{
            console.log("unknown device type: " + type);
        }
    }
    return is_connected;
}


function lower_voltage(wire){
    wire.voltage = false;
}

function inactivate_resistor(element){
    if (element.type == 'resistor'){
        element.active = false;
    }
}

function get_is_connected_old(device){
    console.log("getisconnec devicename: "+device.name);
    var wire = device.to;
    //console.log("getisconnec wirename: "+wire.name);
    for (var i = 0; i < wire.to.length; i++){
        var next_device = wire.to[i];
        console.log("getisconnec next devicename: "+next_device.name);
        var type = next_device.type;
        if (type == 'resistor'){
            return get_is_connected(next_device);
        }
        else if (type == 'switch'){
            if (wire == next_device.button){
                //this wire is linked to button
                return false;
            }
            if (next_device.button.voltage == true){
                return get_is_connected(next_device);
            }
        }
        else if (type == 'ground'){
            return true;
        }
    }
    return false;
}


function lower_voltage(wire){
    wire.voltage = false;
}

function inactivate_resistor(element){
    if (element.type == 'resistor'){
        element.active = false;
    }
}

function set_voltage(source){
    /* 1. set all voltages and resistor actives to false.
     * 2. find paths and mark resistor active.
     * 3. set new voltage
     */
    for_each_wire([source], lower_voltage);
    for_each_device([source], inactivate_resistor);

    console.log("setVoltage source name: " + source.name);
    var is_connected = activate_resistors(source);
    console.log("setVoltage isConnected: " + is_connected);
    spread_voltage(source.to, true);
}

function spread_voltage(wire, voltage){
    if (wire == null) return;

    console.log('spread_voltage set wire ' + wire.name + ' voltage: ' + voltage);
    wire.voltage = voltage;

    for (var i = 0; i < wire.to.length; i++){
        var element = wire.to[i];
        //TODO: wire has multiple elements
        var type = element.type;
        if (type == 'resistor'){
            if (element.active) spread_voltage(element.to, false);
            else spread_voltage(element.to, voltage);
        }
        else if (type == 'switch'){
            if (element.from.name == wire.name){
                if (element.button.voltage == true){
                    spread_voltage(element.to, voltage);
                }
                else continue;
            }
            else{
                //arrived to button.
                continue;
            }
        }
        else if (type == 'bridge'){
            spread_voltage(element.to, voltage);
        }
        else if (type == 'ground'){
            continue;
        }
        else{
            console.log("Unknown type: " + type + " returning");
            return;
        }
    }
}

function spread_voltage_old(wire, voltage, isConnected){
    if (wire == null) return;

    console.log('spread_voltage set wire ' + wire.name + ' voltage: ' + voltage);
    wire.voltage = voltage;

    for (var i = 0; i < wire.to.length; i++){
        var element = wire.to[i];
        //TODO: wire has multiple elements
        var type = element.type;
        if (type == 'resistor'){
            spread_voltage(element.to, false, isConnected);
        }
        else if (type == 'switch'){
            if (element.from.name == wire.name){
                if (element.button.voltage == true){
                    spread_voltage(element.to, voltage, isConnected);
                }
                else spread_voltage(element.to, false, isConnected);
            }
            else{
                //from button.
                return;
            }
        }
        else if (type == 'bridge'){
            spread_voltage(element.to, voltage, isConnected);
        }
        else if (type == 'ground'){
            return;
        }
        else{
            console.log("Unknown type: " + type + " returning");
            return;
        }
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
