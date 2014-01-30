function assert(actual, expected){
    if (!(expected === actual)) {
        throw ("assert FAIL: expected: " + expected + ", but actual: " + actual);
    }
}


function assert_message(condition, message){
    if (!condition) {
        throw ("assert FAIL: " + message) || "assert FAIL";
    }
}


function test_load_binary() {
    var memory = load_binary('70000000');
    assert(memory.length, 1);
    assert(memory[0], 7);

    // subtract insn: subtract 255 - 255 and put into 255
    memory = load_binary('50ffffff');
    assert(memory.length, 1);

    // current -251
    /*
    assert(memory[0] === 5, 'exp: 4294967045, act: ' + memory[0]);

    // set insn contains 2 byte immediate
    memory = load_binary('70f0236e');
    assert(memory.length === 1, 'exp: 1, act: ' + memory.length);
    assert(memory[0] === 7, 'exp: 3862040327, act: ' + memory[0]);

    // 2 insns
    memory = load_binary('70005FFF');
    */
}

function test_get_insn() {
    var insn = get_insn(7);
    assert(insn.length, 3);
    assert(insn[0], 7);
    assert(insn[1], 0);
    assert(insn[2], 0);

    // subtract insn: subtract 255 - 255 and put into 255
    var insn = get_insn(-251);
    assert(insn.length, 4);
    assert(insn[0], 5);
    assert(insn[1], 255);
    assert(insn[2], 255);
    assert(insn[3], 255);

    // set insn contains 2 byte immediate
    var insn = get_insn(-432926969);
    assert(insn.length, 3);
    assert(insn[0], 7);
    assert(insn[1], 15);
    assert(insn[2], 58930);
}

function test_memory_get_block_bytes(){
    memory = [0,1,2,3,4,5,6,7];
    var bytes = memory_get_block_bytes(memory, 0, 5);
    exps = [0,0,0,0,1,0,0,0];
    for (var i = 0; i < bytes.length; i++){
        assert_message(exps[i] === bytes[i], 'at: ' + i + ', exp: ' + exps[i] + ' but act: ' + bytes[i]);
    }
}

function test_memory_set(){
    var memory = [];
    memory_set(memory, 4, [6,0,0,0]);
    assert(memory[1], 6);

    memory_set(memory, 7, [5,0,0,0]);
    assert(memory[1], 83886086);
}

function test_memory_get(){
    var memory = [1280];
    var bytes = memory_get(memory, 1, 1);
    assert(bytes.length, 1);
    assert(bytes[0], 5); 
}

function test_byte_array_to_integer(){
    var bytes = [6,0,0,6];
    var integer = byte_array_to_integer(bytes);
    assert(integer, 100663302);
}

function run_tests(){
    test_load_binary();
    test_get_insn();
    test_byte_array_to_integer();
    test_memory_get_block_bytes();
    test_memory_set();
    test_memory_get();
}
