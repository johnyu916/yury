function test_read_dotted_name(){
    var result = read_dotted_name('mike.name.first');
    assert(result.length, 2);
    assert(result[0].type, 'DottedName');
    assert(result[0].tokens.length, 3);
    assert(result[1].length, 0);

    var result = read_dotted_name('3bob');
    assert(result.length, 2);
    assert(result[0], null);
    assert(result[1], '3bob');
}

function run_waffle_tests(){
    test_read_dotted_name();
};
