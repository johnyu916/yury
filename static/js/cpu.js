//has everything
"use strict";
var block_size_log = 5;
var block_size = Math.pow(2, block_size_log);
var OPCODES = {
    'store': 0,
    'jump': 1,
    'move': 2,
    'branch': 3,
    'add': 4,
    'subtract': 5,
    'load': 6,
    'set': 7
};
var base16_to_int = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'a': 10,
    'b': 11,
    'c': 12,
    'd': 13,
    'e': 14,
    'f': 15
};
// return some bits. read from lowest to highest.
function get_int_value(memory, offset, size){
    //clear the more significant bits
    var last = temp << (block_size - (size+offset));
    //slide all the way to 0
    var temp = memory >> (block_size - size);
    return last;
}

function World() {
    this.cpu = null;
    this.router = null;
    this.booter = null;
}

var world = new World();

function Router(args) {
    //Router's responsibility is to route packets.
}

function boot_insns() {

}

function load_boot_disk(cpu) {
    var memory = cpu.memory;
    // 1. set idle to 0
    // 2. copy everything to memory.
    // 3. read state.
    // 4. if reading src_address, read.
}

function Instruction(read, branch, on_one, on_zero) {
    this.read = read;
    this.branch = branch;
    this.on_one = on_one;
    this.on_zero = on_zero;
}


/**
 * Word must be 4 characters. The character is between 0 and F.
 * 
 */
function base16_to_integer(word) {
    var value = 0, offset = 0;
    var i, first, second, first_int, second_int, current, moved;
    for (i = 0; i < word.length; i+=2) {
        first = word[i];
        second = word[i+1];
        first_int = base16_to_int[first];
        second_int = base16_to_int[second];
        current = first_int + second_int * 16;
        moved = current << offset;
        value += moved;
        offset += 8;
    }
    return value;
}
// computer for any intelligent beings.
function CPU(args) {
    //need memory.
    // idle address must be even.
    this.idle_addr = args['IDLE_ADDR'];
    this.pc_signal_addr = args['PC_SIGNAL_ADDR'];
    this.pc = 0;  //program counter.

    //definitely needed
    this.registers = [];
    this.memory = [];

    // precalculations
    this.idle_block_addr = this.idle_addr / this.block_size;
    this.idle_off = this.idle_addr % this.block_size;

    this.pc_block_addr = this.pc_addr / this.block_size;
    this.pc_off = this.pc_addr % this.block_size;

    this.pc_signal_block_addr = this.pc_signal_addr / this.block_size;
    this.pc_signal_off = this.pc_signal_addr % this.block_size;



}

CPU.prototype.run = function(){
    var count = 0;
    while(true){
        this.run_cycle();
        count += 1;
        if (count > 100) break;
    }
};

/* Print CPU state.
 * Mostly for debugging.
 */
function cpu_state(cpu) {
    console.log("words: " + words + words.join('\n'));
    return part;
}

// set one byte
function memory_set(memory, address, some_byte){
    value = memory[address];
}

// get one byte
function memory_get(memory, address){
    //divide by 4 then return.
    return memory[address];
}

function load_binary(text) {
    var memory = [];
    console.log("printing binary text: " + text);
    var word = [], i=0, a, next_byte, insn;
    while ((i+8) <= text.length){
        word = text.slice(i, i+8);
        insn = base16_to_integer(word);
        console.log("word was: " + word + " insn: " + insn);

        // due to byte addressing, you must 
        memory.push(insn);
        i += 8;
    }
    return memory;
}

/* lowest byte is op-code
 * 
 */
function get_insn(integer) {
    var opcode = integer & 255;
    integer = integer >>> 8;
    var two = integer & 255;
    integer = integer >>> 8;
    if (opcode == OPCODES.set || opcode == OPCODES.jump){
        // 2 more
        var three = integer & 65535;
        var insn = [opcode, two, three];
        console.log("read insn: " + insn);
        return insn;
    }
    else{
        var three = integer & 255;
        integer = integer >>> 8;
        var four = integer;
        var insn = [opcode, two, three, four];
        console.log("read insn: " + insn);
        return insn;
    }
}

function ass_insn(insn) {
    var opc = insn[0];
    var text = [];
    if (opc == OPCODES['store']){
        text = ['store', insn[1], insn[2], insn[3]];
    }
    else if (opc == OPCODES['jump']){
        text = ['jump', insn[1]];
    }
    else if (opc == OPCODES['branch']){
        text = ['branch', insn[1], insn[2]];
    }
    else if (opc == OPCODES['add']){
        text = ['add', insn[1], insn[2], insn[3]];
    }
    else if (opc == OPCODES['subtract']){
        text = ['subtract', insn[1], insn[2], insn[3]];
    }
    else if (opc == OPCODES['load']){
        text = ['load', insn[1], insn[2], insn[3]];
    }
    else if (opc == OPCODES['set']){
        text = ['set', insn[1], insn[2]];
    }
    return text.join(' ');
}

// return list of booleans
CPU.prototype.signal_and_idle = function() {
    var memory = this.memory[this.idle_block];
    if (get_int_value(memory, this.idle_off, 2) === 3) return true;
    else return false;
};

CPU.prototype.run_cycle = function(){
    //1. which pc should i read?
    if (this.signal_and_idle()){
        pc_block_value = this.memory[this.pc_signal_block_addr];
        pc_off = this.pc_signal_off;
    }
    console.log("pc: " + this.pc);
    // NEW STYLE.
    var insn = get_insn(this.memory[this.pc]);//take integer and return a array
    var next_pc = this.pc + 1;
    var insn_type = insn[0];
    if (insn_type == OPCODES.store){
        var value = insn[1];
        var address = insn[2];
        //call set_memory
        this.memory[this.registers[address]] = this.registers[value];
    }
    else if (insn_type == OPCODES.load){
        var value = insn[1];
        var address = insn[2];
        //call get_memory
        this.registers[value] = this.memory[this.registers[address]];
    }
    else if (insn_type == OPCODES.jump){
        var value = insn[1];
        next_pc = this.registers[value];
    }
    else if (insn_type == OPCODES.branch){
        var vale_reg = insn[1];
        if (this.registers[value_reg] == 0){
            var branch_reg = insn[2];
            next_pc = this.registers[branch_reg];
        }
    }
    else if (insn_type == OPCODES.add){
        var result = insn[1];
        var one = insn[2];
        var two = insn[3];
        this.registers[result] = this.registers[one] + this.registers[two];
    }
    else if (insn_type == OPCODES.subtract){
        var result = insn[1];
        var one = insn[2];
        var two = insn[3];
        this.registers[result] = this.registers[one] - this.registers[two];
    }
    else if (insn_type == OPCODES.set){
        var value_reg = insn[1];
        var imm = insn[2];
        this.registers[value_reg] = imm;
    }
    else{
        console.log("unknown instruction: " + insn);
        return 1;
    }
    //and so on

    this.pc = next_pc;
    return 0;
};

/* get the mask as a 2's compleemnt integer given the
 * offset and size.
 */

function get_mask(offset, size){
    var value = 0;
    for (var i = offset; i < offset+size; i++){
        if (i == block_size - 1) value -= math.pow(2,i);
        else value += math.pow(2, i);
    }
    return value;
}

// get mask. for example that is 000111100
function get_mask(offset, size){
    var value = -1; // all 1's
    var right = value >> (block_size - size);
    var placed = right << offset;
    return placed;
}


function new_int_value(memory, offset, size, value){
    var end = offset + size;
    var value_new = value << offset;
    var right_mask = get_mask(0, offset);
    var right = memory & right_mask;
    var left_mask = get_mask(end, block_size - end);
    var left = memory & left_mask;
    return left+value_new+right;
}



function on_load_click(filename, callback) {
    $.ajax({
        url: '/binary',
        data: {'name':filename}
    }).done(function(response_data){
        var binary = response_data['binary'];
        console.log("Running program" + binary.name);
        var memory = load_binary(binary.data);
        world.cpu.memory = memory;

        callback(world.cpu);
    });
}

function on_run_cycle_click(){
    world.cpu.run_cycle();
}

function on_run_click(){
    world.cpu.run();
}

function cpu_main() {
    var args = $('#cpu-info').data('cpu');
    var data = jQuery.parseJSON(args.replace(/'/g, '"'));
    console.log("cpu data: " + data);
    var cpu = new CPU(data);
    world.cpu = cpu;
    //just loop as quickly as possible
}

