function array_index(array, token){
    var i = array.length;
    while (i--){
        if (token == array[i]) return i;
    }
    return -1;
}

function array_extend(array, values){
    console.log("array: " + array + " values: " + values);
    for (var i = 0; i < values.length; i++){
        console.log("value: " + values[i]);
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

function get_device_data_root(devices){
    var name = devices[0].name.split('/')[0];
    return get_device_data(devices, name);
}

//from list of device dicts, get the dict of interest
function get_device_data(devices, name){
    for (var i = 0; i < devices.length; i++){
        var device = devices[i];
        if (device.name == name) return device;
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

function get_wire(wires, device_name, direction){
    var wires = device.wires;
    for (var i = 0; i < wires.length; i++){
        var wire = wires[i];
        var elements = wire.direction;
        for (var j = 0; j < elements.length; j++){
            
        }
    }
}

function traverse_path(element, callback){
    var wire = element.to;
    if (wire == null) return;
    callback(wire);
    for (var i = 0; i < wire.to.length; i++){
        var next_element = wire.to[i];
        traverse_path(next_element, callback);
    }

}

function for_each_wire(sources, callback){
    for (var i = 0; i < sources.length; i++){
        traverse_path(sources[i], callback);
    }
}
