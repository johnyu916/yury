
int_to_base16 = {
    0: '0',
    1: '1',
    2: '2',
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: 'a',
    11: 'b',
    12: 'c',
    13: 'd',
    14: 'e',
    15: 'f'
};

var OPCODES = {
    'store_word': 0,
    'jump': 1,
    'move': 2,
    'branch_on_z': 3,
    'add': 4,
    'subtract': 5,
    'load_word': 6,
    'set': 7,
    'branch_on_ltz': 8,
    'store_byte': 9,
    'load_byte': 10,
    'multiply': 11,
};

function insn_to_integer(insn){
    var sizes = get_insn_sizes(insn[0]);
    var shift = 0;
    var integer = 0;
    for (var i = 0; i < sizes.length; i++){
        var value = insn[i] << shift;
        integer += value;
        shift += 8*sizes[i];
    }
    return integer;
}

/* lowest byte is op-code
 * 
 */
function integer_to_insn(integer) {
    console.log("integer_to_insn integer: " + integer);
    var opcode = integer & 255;
    integer = integer >>> 8;
    var two = integer & 255;
    integer = integer >>> 8;
    if (opcode == OPCODES.set || opcode == OPCODES.jump){
        var three = integer & 65535;
        var insn = [opcode, two, three];
        console.log("integer_to_insn read insn: " + insn);
        return insn;
    }
    else{
        var three = integer & 255;
        integer = integer >>> 8;
        var four = integer;
        var insn = [opcode, two, three, four];
        console.log("integer_to_insn read insn2: " + insn);
        return insn;
    }
}

function get_insn_sizes(opcode){
    if (opcode === OPCODES.set || opcode === OPCODES.jump){
        return [1,1,2];
    }
    else{
        return [1,1,1,1];
    }
}

function tokens_to_insn(tokens){
    var opcode = OPCODES[tokens[0]];
    var one = parseInt(tokens[1]);
    var two = parseInt(tokens[2]);
    if (opcode == OPCODES.set || opcode == OPCODES.jump){
        return [opcode, one, two];
    }
    else{
        var three = parseInt(tokens[3]);
        return [opcode, one, two, three];
    }
}

// need to go from array to int.

function branch_on_z_insn(value_register, branch_register){
    return [
        OPCODES['branch_on_z'],
        value_register,
        branch_register,
        0
    ];
}

function set_insn(value_register, immediate){
    return [
        OPCODES['set'],
        value_register,
        immediate
    ];
}

function write_insn(insn){
    // 0 is opcode
    var code = insn[0];
    var sizes = [1,1,1,1];
    if (code === OPCODES['store_word']){}
    else if (code === OPCODES['jump']){
        sizes = [1,1,2];
    }
    else if (code === OPCODES['branch_on_z']){}
    else if (code === OPCODES['add']){}
    else if (code === OPCODES['subtract']){}
    else if (code === OPCODES['load_word']){}
    else if (code === OPCODES['set']){
        sizes = [1,1,2];
    }
    else if (code === OPCODES['branch_on_ltz']){}
    else if (code === OPCODES['store_byte']){}
    else if (code === OPCODES['load_byte']){}
    else if (code === OPCODES['multiply']){}
    else{
        console.log("Unknown instruction: " + code);
    }
    return get_insn_text(insn, sizes);
}

function get_insn_text(insn, sizes){
    var text = '';
    for (var i = 0; i < insn.length; i++){
        text += get_base16(insn[i], sizes[i]);
    }
    return text;
}

function get_two(integer){
    var low = integer % 16;
    var high = integer >> 4;
    return int_to_base16[low] + int_to_base16[high];
}

function get_base16(integer, size){
    if (size === 1){
        return get_two(integer);
    }
    else if (size === 2){
        var first = integer % 256;
        var second = integer >> 8;
        return get_two(first) + get_two(second);
    }
    else{
        console.log("ERROR: Can't handle this: " + integer);
    }
}
