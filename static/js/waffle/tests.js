var Animal = {};
Animal.run = function(){
    console.log("running");
}
Animal.sleep = function(){
    console.log("sleeping");
}
var Dog = object(Animal);
Dog.age = 5;
Dog.bark = function(){
    console.log("barking age: " + this.age);
}
Dog.sleep = function(){
    console.log("dog sleeping");
}

function test_object(){
    var terrier = object(Dog);
    terrier.bark();
    terrier.sleep();
    terrier.run();

    console.log("age " + terrier.age);
    terrier.age = 7;
    console.log("terrier age " + terrier.age);
    Dog.age = 6;
    console.log("terrier age " + terrier.age);

    var chiwa = object(Dog);
    console.log("age " + chiwa.age);

}

function test_read_dotted_name(){
    var result = read_dotted_name('mike.name.first');
    assert(result.length, 2);
    assert(result[0].classname, 'DottedName');
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
    assert(result[0].classname, 'ExpressionText');
    assert(result[1].length, 0);
}

function test_build_function_call(){
    var result = read_dotted_name("mike.name.first");
    var dotted_name = result[0];
    var expressions = new Expressions([]);
    result = build_function_call([dotted_name, expressions]);
    assert(result.length, 2);
    assert(result[0].classname, 'ExpressionText');
    assert(result[1].length, 0);
}

function test_build_operation(){
    var result = read_dotted_name("mike.name.first");
    var left = result[0];
    var operator = new Operator('+');
    result = read_dotted_name("john.yu");
    assert(result.length, 2);
    assert(result[0].classname, 'DottedName');
    var right = result[0];
    result = build_operation([left, operator, right]);
    assert(result.length, 2);
    assert(result[0].classname, 'ExpressionText');
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
    assert(result[0].classname, 'ExpressionText');
    assert(result[1].length, 0);
}

function test_read_expression(){
    var sentence = 'mike.name + john.yu';
    var result = read_expression(sentence);
    assert(result.length, 2);
    assert(result[0].classname, 'ExpressionText');
    console.log(JSON.stringify(result[0]));
}

function run_waffle_tests(){
    test_object();
    console.log('1');
    test_read_dotted_name();
    console.log('2');
    test_build_constant_or_variable();
    console.log('3');
    test_build_function_call();
    console.log('4');
    test_build_operation();
    console.log('5');
    test_build_expression();
    console.log('6');
    test_read_expression();
    console.log('7');

}
