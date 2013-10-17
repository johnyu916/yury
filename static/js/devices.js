/*
 * Classes for electornic circuit components.
 * Current flows in a direction from source to ground.
 * the wires "plug" into pins.
 * everybody has a type and a name. devices and others
 * JSON structure is:
 {
    name: 'and0',
    type: 'and',
    devices: [{
        name: 'res0',
        type: 'resistor',
    },
    {
        name: 'wire0',
        type: 'wire',
        to: ' ',
    ]

 }
 */

var device_primitives = ['resistor', 'source', 'ground', 'switch', 'bridge'];

function Apple (type) {
    this.type = type;
    this.color = "red";
}
 
Apple.prototype.getInfo = function() {
    return this.color + ' ' + this.type + ' apple';
};
/*
wire always has at least two devices connected to it. some conditions:
        //1. only one of the devices can be power.
        //2. only one of the devices can be ground.
        //3. only one of the devices can be input.
        //4. only one of the devices can be output.
*/
function Wire(name, from, to, voltage){
    this.name = name;
    this.from = from;
    this.to = to;
    this.voltage = typeof voltage != 'undefined' ? voltage : false;
}

//pins are either in pins or out pins. curren only
//flows in one direction.
//similarly, wires have directionality.
function Resistor(name){
    this.name = name;
    this.from = null;
    this.to = null;
}

function Meter(name){
    this.from = null;
}

function Source(name){
    this.name = name;
    this.to = null;
}

function Ground(name){
    this.name = name;
    this.from = null;
}

function Switch(name){
    this.name=name;
    this.from = null;
    this.to = null;
    this.button = null;
}

function Device(name, type){
    this.name = name;
    this.type = type;
    this.devices = [];
    this.wires = [];
}

function Bridge(name){
    this.name = name;
}

function get_device(device_data){
    if ('devices' in device_data){

    }
    else{

    }
}

function device_names(devices){
    var names = [];
    for (var j = 0; j < devices.length; j++){
        var name = devices[j].name;
        names.push(name);
    }
    return names;
}

function get_element_dict(source){
    var components = [];
    var data = {
        "name": source.name,
        "type": source.type
    };
    console.log("device name: " + source.name);
    components.push(data);
    var wire = source.to;
    if (wire == null) return components;
    
    var wire_data = {
        "name": wire.name,
        "value": wire.voltage
    }

    console.log("wire name: " + wire.name);
    var froms = [];
    for (var i = 0; i < wire.from.length; i++){
        var next_element = wire.from[i];
        froms.push(next_element.name);
    }
    var tos = [];
    for (var i = 0; i < wire.to.length; i++){
        var next_element = wire.to[i];
        tos.push(next_element.name);
    }
    wire_data.from = froms;
    wire_data.to = tos;
    components.push(wire_data);


    for (var j = 0; j < wire.to.length; j++){
        var next_element = wire.to[j];
        array_extend(components, get_element_dict(next_element));
    }
    return components;
}

function sources_json(sources){
    var data = [];
    for (var i = 0; i < sources.length; i++){
        var element_dict = get_element_dict(sources[i]);
        data.push(element_dict);
    }
    return JSON.stringify(data);
}

function device_json(device){
    //recursive print
    //first construct dictionary
    var dict = device_dict(device);
    return JSON.stringify(dict);
}

function wire_dict(wire){
    var from_data = device_names(wire.from);
    var to_data = device_names(wire.to);
    return {'name':wire.name, 'from':from_data, 'to':to_data, 'voltage': wire.voltage};
}


function device_dict(device){
    var data = {
        'name': device.name,
        'type': device.type,
    }

    var devices = device.devices;
    var devices_data = [];
    for (var i = 0; i < devices.length; i++){
        var device_data = {'name': devices[i].name, 'type': devices[i].type}
        devices_data.push(device_data);
    }
    data['devices'] = devices_data;
    
    var wires = device.wires;
    var wires_data = [];
    for (var i = 0; i < wires.length; i++){
        var wire = wires[i];
        var wire_data = wire_dict(wire);
        wires_data.push(wire_data);
    }
    data['wires'] = wires_data;
    return data;
}


function construct_device(devices_data, device_data){
    var name = device_data['name'];
    var children_data = device_data['devices'];
    var device_map = {};
    var srouces = [];
    for (var i = 0; i < children_data.length; i++){
        var child_data = children_data[i];
        var child = null;
        if (array_index(device_primitives, child_data.type) >= 0){
            child = new Device(child_data.name, child_data.type);
            if (child_data.type == 'source'){
                sources.push(child);
            }
        }
        else{
            //find child
            var child_data = get_device_data(devices_data, child_data.name);
            array_extend(sources, construct_device_inner(devices_data, child_data));
        }
        device_map[child.name] = child;
    }


    var wires_data = device_data.wires;
    var wires = [];
    for (var i = 0; i < wires_data.length; i++){
        var wire_data = wires_data[i];
        var wire = new Wire(wire_data.name);
        var from = parse_wire_links(wire, wire_data.from, device_map, 'to');
        var to = parse_wire_links(wire, wire_data.to, device_map, 'from');
        wire.from = from;
        wire.to = to;
        wires.push(wire);
    }
    return sources;
}
