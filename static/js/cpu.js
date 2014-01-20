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
 */
function base16_to_integer(word) {
    var value = 0, i, letter, current, moved;
    for (i = 0; i < word.length; i++) {
        letter = word[i];
        current = base16_to_int.character;
        moved = current << 2;
        value += moved;
    }
    return value;
}
// computer for any intelligent beings.
function CPU(args) {
    //need memory.
    //each number stores 32-bits. so we need bits - 5.
    this.memory_size_log = args['MEMORY_SIZE_LOG'];
    var size_log = args['MEMORY_SIZE_LOG'] - block_size_log;
    var memory_size = Math.pow(2, size_log);
    //this.pc_addr = args['PC_ADDR'];  // memory address where pc is stored.
    // idle address must be even.
    this.idle_addr = args['IDLE_ADDR'];
    this.pc_signal_addr = args['PC_SIGNAL_ADDR'];
    //this.pc_size = args['NUM_INSNS_LOG'];
    this.insn_size = args['INSN_SIZE'];
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
    while(true){
        this.run_cycle();
    }
};

CPU.prototype.load_binary = function(text) {
    var count = 0, word = [], i, a, next_byte, insn;
    for (i=0; i < text.length; i+=1){
        a = text[i];
        next_byte = parseInt(a, 10);
        word[count] = next_byte;
        count+=1;
        if (count === 3){
            insn = base16_to_integer(word);
            this.memory.push(insn);
            count = 0;
        }
    }
};
/* lowest byte is op-code
 * 
 */
CPU.prototype.get_insn = function(integer) {
    var opcode = integer % 256;
    integer = integer >> 8;
    var two = integer % 256;
    integer = integer >> 8;
    if (opcode == OPCODES.set || opcode == OPCODES.jump){
        // 2 more
        var three = integer;
        return [opcode, two, three];
    }
    else{
        var three = integer % 256;
        integer = integer >> 8;
        var four = integer;
        return [opcode, two, three, four];
    }
};

// return list of booleans
CPU.prototype.signal_and_idle = function() {
    var memory = this.memory[this.idle_block];
    if (get_int_value(memory, this.idle_off, 2) === 3) return true;
    else return false;
};

CPU.prototype.run_cycle = function(){
    //1. which pc should i read?
    var pc_block_value = this.memory[this.pc_block_addr];
    var pc_off = this.pc_off;

    if (this.signal_and_idle()){
        pc_block_value = this.memory[this.pc_signal_block_addr];
        pc_off = this.pc_signal_off;
    }
    var pc_value = get_int_value(pc_block_value, pc_off, this.pc_size);
    var insn_addr = pc_value * this.insn_size;
    var insn_block_addr = insn_addr / this.block_size;
    var insn_off = insn_addr % this.block_size;

    var insn_block = this.memory[insn_block_addr];

    // NEW STYLE.
    var insn = this.get_insn(this.memory[this.pc]);//take integer and return a array
    var next_pc = this.pc + 1;
    var insn_type = insn[0];
    if (insn_type == OPCODES.store){
        var value = insn[1];
        var address = insn[2];
        this.memory[this.registers[address]] = this.registers[value];
    }
    else if (insn_type == OPCODES.load){
        var value = insn[1];
        var address = insn[2];
        this.registers[address] = this.memory[this.registers[value]];
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
    //and so on

    this.pc = next_pc;
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


function on_run_click(filename) {
    $.ajax({
        url: '/binary',
        data: {'name':filename}
    }).done(function(response_data){
        var binary = response_data['binary'];
        console.log("Running program" + binary.name);
        world.cpu.load_binary(binary.data);
        world.cpu.run();
    });

}

function cpu_main() {
    var args = $('#cpu-info').data('cpu');
    var data = jQuery.parseJSON(args.replace(/'/g, '"'));
    console.log("cpu data: " + data);
    var cpu = new CPU(data);
    world.cpu = cpu;
    //just loop as quickly as possible
}

