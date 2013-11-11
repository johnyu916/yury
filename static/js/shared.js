/*
 * Return -1 if token not found in array
 */
function array_index(array, token){
    var i = array.length;
    while (i--){
        if (token == array[i]) return i;
    }
    return -1;
}

function array_extend(array, values){
    //console.log("array: " + array + " values: " + values);
    for (var i = 0; i < values.length; i++){
        //console.log("value: " + values[i]);
        array.push(values[i]);
    }
}

/*binary inputs. return array of arrays.
 * [
 * [0,0],
 * [0,1],
 * [1,0],
 * [1,1]
 * ]
 */
function get_inputs(size){
    var arrays = [];
    var values = [true,false];
    for (var i = 0; i < values.length; i++){
        var array = [values[i]];
        if (size > 0){
            var sub_arrays = get_inputs(size-1);
            for (var j = 0; j < sub_arrays.length; j++){
                array.push.apply(array, sub_arrays[j]);
            }
        }
        arrays.push(array);
    }
    return arrays;
}

function get_device(devices){

}

function get_device_data_root(devices){
    //var type = devices[0].name.split('/')[0];
    //return get_device_data(devices, name);
    return devices[0];
}

//from list of device dicts, get the dict of interest
function get_device_data(devices, type){
    for (var i = 0; i < devices.length; i++){
        var device = devices[i];
        if (device.type == type) return device;
    }
}

//return index of child device inside a device dict
function get_device_index(devices, name){
    for (var i = 0; i < devices.length; i++){
        if (devices[i].name == name) return i;
    }
    return -1;
}


function parse_wire(device, wire, data, device_pin){
    for (var i = 0; i < data.length; i++){
        var path = data[i];
        var tokens = path.split('/');
        var device_name = tokens[0];
        if (tokens.length == 2) device_pin = tokens[1];
        console.log('device_name ' + device_name + ' pin: ' + device_pin);
        var index = get_device_index(device.devices, device_name);
        device.devices[index][device_pin] = wire.name;
    }
}

function add_wire_data(device){
    var wires = device.wires;
    for (var i = 0; i < wires.length; i++){
        var wire = wires[i];
        var elements = wire.from;
        parse_wire(device, wire, wire.from, 'to');
        parse_wire(device, wire, wire.to, 'from');
    }
}

function get_wire(wires, wire_name){
    for (var i = 0; i < wires.length; i++){
        if (wires[i].name == wire_name) return wires[i];
    }
    return null;
}

/*
function get_wire(wires, device_name, direction){
    var wires = device.wires;
    for (var i = 0; i < wires.length; i++){
        var wire = wires[i];
        var elements = wire.direction;
        for (var j = 0; j < elements.length; j++){
            
        }
    }
}*/

function traverse_wire(wire, callback, object){
    if (wire == null) return;
    callback(wire, object);
    for (var i = 0; i < wire.to.length; i++){
        var next_element = wire.to[i];
        if (next_element.type =='switch' && wire.name == next_element.button.name) continue;
        else traverse_wire(next_element.to, callback, object);
    }
}

function traverse_wire_old(element, callback, object){
    var wire = element.to;
    if (wire == null) return;
    callback(wire, object);
    for (var i = 0; i < wire.to.length; i++){
        var next_element = wire.to[i];
        traverse_wire(next_element, callback, object);
    }
}

//for each wire that is potentially reachable
function for_each_wire(sources, callback, object){
    for (var i = 0; i < sources.length; i++){
        traverse_wire(sources[i].to, callback, object);
    }
}

//for each element that is potentially reachable
function traverse_element(element, callback, object){
    callback(element, object);
    var wire = element.to;
    if (wire == null) return;
    for (var i = 0; i < wire.to.length; i++){
        var next_element = wire.to[i];
        if (next_element.type =='switch' && wire.name == next_element.button.name) continue;
        else traverse_element(next_element, callback, object);
    }
}

function for_each_device(sources, callback, object){
    for (var i = 0; i < sources.length; i++){
        traverse_element(sources[i], callback, object);
    }
}
