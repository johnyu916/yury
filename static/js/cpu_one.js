//has everything
function World(){
    this.cpu = null;
    this.router = null;
    this.booter = null;
}


function Router(args){
    //Router's responsibility is to route packets.
}

function boot_insns(){

}

function load_boot_disk(cpu){
    var memory = cpu.memory;
    // 1. set idle to 0
    // 2. copy everything to memory.
    // 3. read state.
    // 4. if reading src_address, read.
}

function Instruction(read, branch, on_one, on_zero){
    this.read = read;
    this.branch = branch;
    this.on_one = on_one;
    this.on_zero = on_zero;
}

var block_size_log = 5;
var block_size = Math.pow(2, block_size_log);
// computer for any intelligent beings. old version
function CPU(args){
    //need memory.
    //each number stores 32-bits. so we need bits - 5.
    this.memory_size_log = arg['MEMORY_SIZE_LOG'];
    var size_log = args['MEMORY_SIZE_LOG'] - block_size_log;
    var memory_size = Math.pow(2, size_log);
    this.memory = new Array();
    this.pc_addr = args['PC_ADDR'];
    this.pc_signal_addr = args['PC_SIGNAL_ADDR'];
    this.pc_size = args['NUM_INSNS_LOG'];
    this.insn_size = args['INSN_SIZE'];

    // idle address must be even.
    this.idle_addr = args['IDLE_ADDR'];

    // precalculations
    this.idle_block_addr = this.idle_addr / this.block_size;
    this.idle_off = this.idle_addr % this.block_size;

    this.pc_block_addr = this.pc_addr / this.block_size;
    this.pc_off = this.pc_addr % this.block_size;

    this.pc_signal_block_addr = this.pc_signal_addr / this.block_size;
    this.pc_signal_off = this.pc_signal_addr % this.block_size;
    // return list of booleans
    function signal_and_idle(){
        var memory = this.memory[this.idle_block];
        if (value(memory, this.idle_off, 2) == 3) return true;
        else return false;
    }

    function run_cycle(){
        //1. which pc should i read?
        var pc_block_value = this.memory[this.pc_block_addr];
        var pc_off = this.pc_off;

        if (this.signal_and_idle()){
            pc_block_value = this.memory[this.pc_signal_block_addr];
            pc_off = this.pc_signal_off;
        }
        var pc_value = get_int_value(block, pc_off, this.pc_size);
        var insn_addr = pc_value * this.insn_size;
        var insn_block_addr = insn_addr / this.block_size;
        var insn_off = insn_addr % this.block_size;

        //2. read next instruction.
        // NOTE THIS ASSUMES INSN FITS IN ONE BLOCK.
        var insn_block_value = this.memory[insn_block_addr];
        var insn = get_int_value(insn_block_value, insn_off, this.insn_size);

        var read_addr = get_int_value(insn, 0, this.memory_size_log);
        var branch_addr = get_int_value(insn, this.memory_size_log, this.pc_size);
        var r_and_b = this.memory_size_log + this.pc_size;
        var on_one = get_int_value(insn, r_and_b, 1);
        var on_zero = get_int_value(insn, r_and_b+1, 1);

        //3. read memory
        var read_block_addr = read_addr / block_size;
        var read_off = read_addr % block_size;
        var read_block_value = this.memory[read_block_addr];
        var read_value = get_int_value(read_block_value, read_off, 1);

        //4. write and set next pc
        var new_pc_block, new_read_block;
        if (read_value == 1) {
            new_pc_block = new_int_value(pc_block_value, pc_off, this.pc_size, branch_addr);
            new_read_block = new_int_value(read_block_value, read_off, 1, on_one);
        }
        else {
            new_pc_block = new_int_value(pc_block_value, pc_off, this.pc_size, pc_value + 1);
            new_read_block = new_int_value(read_block_value, read_off, 1, on_zero);
        }
        cpu.memory[pc_block_addr] = new_pc_block;
        cpu.memory[read_block_addr] = new_read_block;
    }
}

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

// return some bits. read from lowest to highest.
function get_int_value(memory, offset, size){
    //clear the more significant bits
    var last = temp << (block_size - (size+offset));
    //slide all the way to 0
    var temp = memory >> (block_size - size);
    return last;
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



/*
 * Return true if both signal and idle are set
 *
 */

function cpu_get_memory(cpu, addr, size){

}

function cpu_set_memory(cpu, addr, size){

}


function main_iteration(world){

    cpu_run_cycle(world.cpu);
    return true;
}

$(document).ready(function(){
    //get some settings.
    var args = $('#cpu-info').data('cpu');
    var data = jQuery.parseJSON(args.replace(/'/g, '"'));
    var world = new World();
    var cpu = new CPU(data);
    world.cpu = cpu;
    //just loop as quickly as possible
    while (true){
        if (!main_iteration(world)){
            break;
        }
    }
});
