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
function Wire(from, to, voltage){
    this.from = from;
    this.to = to;
    this.voltage = typeof voltage != 'undefined' ? voltage : false;
}

//do we need this?
function Pin(element, name){
    this.element = element;
    this.name = name;
    this.wire = null;
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

//do we need bridges? let's try to do without
function Bridge(name){
    this.name=name;
    this.from = null;
    this.to = null;
}

function Switch(name){
    this.name=name;
    this.from = null;
    this.to = null;
    this.button = null;
}

function Device(name){
    this.name = name;
    this.devices = null;
    this.sources = null;
    this.grounds = null;
    this.resistors = null;
    this.switches = null;
    this.wires = null;
}
