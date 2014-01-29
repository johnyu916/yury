function assert(condition, message){
    if (!condition) {
        throw ("assert FAIL: " + message) || "assert FAIL";
    }
}

function test_load_binary() {
    var memory = load_binary('70000000');
    assert(memory.length === 1);
    assert(memory[0] === 7, 'exp: 7, act: ' + memory[0]);

    // subtract insn: subtract 255 - 255 and put into 255
    memory = load_binary('50ffffff');
    assert(memory.length === 1);

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
    assert(insn.length === 3, 'exp: 3, act: ' + insn.length);
    assert(insn[0] === 7, 'exp: 7, act: ' + insn[0]);
    assert(insn[1] === 0, 'exp: 0, act: ' + insn[1]);
    assert(insn[2] === 0, 'exp: 0, act: ' + insn[2]);

    // subtract insn: subtract 255 - 255 and put into 255
    var insn = get_insn(-251);
    assert(insn.length === 4, 'exp: 4, act: ' + insn.length);
    assert(insn[0] === 5, 'exp: 5, act: ' + insn[0] );
    assert(insn[1] === 255, 'exp: 255, act: ' + insn[1]);
    assert(insn[2] === 255, 'exp: 255, act: ' + insn[2]);
    assert(insn[3] === 255, 'exp: 255, act: ' + insn[3]);

    // set insn contains 2 byte immediate
    var insn = get_insn(-432926969);
    assert(insn.length === 3, 'exp: 3, act: ' + insn.length);
    assert(insn[0] === 7, 'exp: 7, act: ' + insn[0]);
    assert(insn[1] === 15, 'exp: 15, act: ' + insn[1]);
    assert(insn[2] === 58930, 'exp: 58930, act: ' + insn[2]);
}

function test_memory_set(){
    var memory = [];
    memory_set(memory, 4, [6,0,0,0]);
    assert(memory[1] === 6, 'exp: 6, act: ' + memory[1]);

    memory_set(memory, 7, [6,0,0,0]);
    console.log('memory: ' + memory);
}

function run_tests(){
    test_load_binary();
    test_get_insn();
    test_memory_set();
}
