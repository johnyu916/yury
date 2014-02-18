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

function test_build_constant_or_variable(){
    var result = read_dotted_name("mike.name.first");
    var dotted_name = result[0];
    result = build_constant_or_variable([dotted_name]);
    assert(result.length, 2);
    assert(result[0].type, 'ExpressionText');
    assert(result[1].length, 0);
}

function test_build_function_call(){
    var result = read_dotted_name("mike.name.first");
    var dotted_name = result[0];
    var expressions = new Expressions([]);
    result = build_function_call([dotted_name, expressions]);
    assert(result.length, 2);
    assert(result[0].type, 'ExpressionText');
    assert(result[1].length, 0);
}

function test_build_operation(){
    var result = read_dotted_name("mike.name.first");
    var left = result[0];
    var operator = new Operator('+');
    result = read_dotted_name("john.yu");
    assert(result.length, 2);
    assert(result[0].type, 'DottedName');
    var right = result[0];
    result = build_operation([left, operator, right]);
    assert(result.length, 2);
    assert(result[0].type, 'ExpressionText');
    assert(result[1].length, 0);
}

function test_build_expression(){
    var result = read_dotted_name("mike.name.first");
    var left = result[0];
    var operator = new Operator('+');
    result = read_dotted_name("john.yu");
    var right = result[0];
    result = build_expression([left, operator, right]);
    assert(result.length, 2);
    assert(result[0].type, 'ExpressionText');
    assert(result[1].length, 0);
}

function test_read_expression(){
    var sentence = 'mike.name + john.yu';
    var result = read_expression(sentence);
    assert(result.length, 2);
    assert(result[0].type, 'ExpressionText');
    console.log(JSON.stringify(result[0]));
}

function run_waffle_tests(){
    test_read_dotted_name();
    test_build_constant_or_variable();
    test_build_function_call();
    test_build_operation();
    test_build_expression();
    test_read_expression();
}
