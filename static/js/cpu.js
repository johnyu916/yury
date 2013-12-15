//has everything
function World(){
    
}
var block_size_log = 5;
var block_size = Math.pow(2, block_size_log);
// computer for any intelligent beings.
function CPU(args){
    //need memory.
    //each number stores 32-bits. so we need bits - 5.
    this.memory_size_log = arg['MEMORY_SIZE_LOG'];
    var num_bits = args['MEMORY_SIZE_LOG'] - block_size_log;
    var len_ints = Math.pow(2, num_bits);
    var memory = new Array();
    this.pc = args['PC'];
    this.pc_signal = args['PC_INT'];
    this.pc_size = args['PC_SIZE'];

    // idle address must be even.
    this.idle = args['IDLE'];

    // precalculations
    this.idle_block = this.idle / this.block_size;
    this.idle_off = this.idle % this.block_size;

    this.pc_block = this.pc / this.block_size;
    this.pc_off = this.pc % this.block_size;

    this.pc_signal_block = this.pc_signal / this.block_size;
    this.pc_signal_off = this.pc_signal % this.block_size;
    // return list of booleans
    function signal_and_idle(){
        var memory = this.memory[this.idle_block];
        if (value(memory, this.idle_off, 2) == 3) return true;
        else return false;
    }

    function run_cycle(){
        //1. which pc should i read?
        var block = this.memory[this.pc_block];
        var pc_off = this.pc_off;

        if (this.signal_and_idle()){
            block = this.memory[this.pc_signal_block];
            pc_off = this.pc_signal_off;
        }
        var pc = value(block, pc_off, this.pc_size);

        //2. read next instruction.
        // NOTE THIS ASSUMES INSN FITS IN ONE BLOCK.
        var insn = cpu.memory[pc];

        var read_addr = get_int_value(insn, 0, this.memory_size_log);
        var branch = get_int_value(insn, this.memory_size_log, this.pc_size);
        var r_and_b = this.memory_size_log + this.pc_size;
        var on_one = get_int_value(insn, r_and_b, 1);
        var on_zero = get_int_value(insn, r_and_b+1, 1);

        //3. read memory
        var read_addr_block = read_addr / block_size;
        var read_addr_block_off = read_addr % block_size;
        var read = get_int_value(this.memory[read_addr_block], read_addr_block_off, 1);

        //4. write and set next pc
        if (read == 1) {
            cpu.memory[this.pc] = branch;
            cpu.memory[read_addr] = on_one;
        }
        else {
            cpu.memory[this.pc] = pc + 1;
            cpu.memory[read_addr] = on_zero;
        }
    }
}

/* get the mask as a 2's compleemnt integer given the
 * offset and size.
 */

function get_mask(offset, size){
    var value = 0;
    if (offset == 0){
        value -= math.pow(2, block_size - 1);
    }
    var end = offset+size;
    for (var i = 
}

// return some bits
function get_int_value(memory, offset, size){
    var temp = memory << offset;
    var last = temp >> (block_size - size);
    return last;
}

function set_int_value(memory, offset, size, value){
    var end = offset + size;
    var value_new = value << (block_size - end);
    var left = memory >> (block_size - offset);
    left = left <<
    var temp = memory << offset;
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
