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
