var Struct = {};

var Block = {
    code: [],
    variables: [],
    parent: null,
    program: null
};

var Func = object(Block);
Func.name = '';


function FuncMake(name, inputs, outputs, program){
    var func = object(Func);
    func.name = name;
    func.inputs = inputs;
    func.outputs = outputs;
    func.program = program;
    func.parent = null;
    return func;
}

var Program = {
    functions: [],
    structs: []
};

var Expression = {
    classname: "Expression",
    data: null,
    children: null
};

Expression.get_types = function(){
    return [];
}

function ExpressionMake(data, children){
    var expression = object(Expression);
    expression.data = data;
    expression.children=children;
    return expression;
}

var Statement = {
    classname: 'Statement',
    destinations: null,
    expression: null
};

function StatementMake(destinations, expression){
    var statement = object(Statement);
    statement.destinations = destinations;
    statement.expression = expression;
    return statement;
}

function StatementMakeFromText(statement_text, block, program){
    var text_dests = statement_text.dests;
    var text_exp = statement_text.expression;
    var exp = expression_make(text_exp, block, program);
    var dest_types = exp.get_types();
    var destinations = [];
    for (var i = 0; i < dest_types.length; i++){
        var text_dest = text_dests[i];
        var type = dest_types[i];
        var destination = block.get_variable(text_dest);
        if (destination !== null){
            var dotted_type = get_dotted_type(dest.tokens, destination.type);
            assert_message(dotted_type, type.name, "dest types must be equal");
        }
        else{
            destination = VariableMake(type, text_dest.tokens[0]);
            block.variables_append(destination);
        }
        destinations.push(destination);
    }
    return StatementMake(destinations, exp);
}

var Type = {
    name: "",
    size: 0
}

var Constant = {
    classname: 'Constant',
    type: null,
    value: null
}

function ConstantMake(type, value){
    var constant = object(Constant);
    constant.type = type;
    constant.value = value;
    return constant;
}

var Variable = {
    classname: 'Variable',
    type: null,
    name: ""
}

function VariableMake(type, name){
    var variable = object(Variable);
    variable.type = type;
    variable.name = name;
    return variable;
}

var WaffleSemantics = {
    program: null,
    block: null
}

TYPES = [
    {
        name:'int',
        size:4
    }
]

function get_primitive_type(type_str){
    for (var i = 0; i < TYPES.length; i++){
        var type = TYPES[i];
        if (type.name === type_str) return type;
    }
    return null;
}

function get_constant_type(value){
    if (typeof(value) === 'number'){
        return get_primitive_type('int')
    }
    
}

WaffleSemantics.process = function(construct){
    if (construct.classname === 'ExpressionText'){
        return expression_make(construct, this.block, this.program);
    }
    else if (construct.classname === 'StatementText'){
        return StatementMakeFromText(construct, this.block, this.program);
    }
}

function WaffleSemanticsMake(){
    var semantics = object(WaffleSemantics);
    semantics.program = object(Program);
    semantics.block = FuncMake('__main__', [], [], semantics.program);
    semantics.program.functions.push(semantics.block)
    return semantics;
}


function make_expression_children(expression_text, block, program){
    //build expression from children of functions/operators.
    var children = [];
    for (var i = 0; i < expression_text.children.length; i++){
        var child = expression_text.children[i];
        var child_exp = expression_make(child, block, program);
        var types = child_exp.get_types();
        assert(types.length, 1) //"Each operands must return 1 value, but returns: {0}".format(len(child_exp))
        children.append(child_exp);
    }
    return children;
}

function expression_make(expression_text, block, program){
    var text_data = expression_text.data;
    var text_children = expression_text.children;
    var children = [];
    if (text_data.classname === 'ConstantText'){
        type = get_constant_type(text_data.value);
        if (type === null) throw ("Unknown type: " + data.value);
        else return ExpressionMake(ConstantMake(type, text_data.value), null);
    }
    else if (text_data.classname === 'DottedName'){
        // name could be variable, struct, or function.
        if (text_children === null){
            // must be variable
            var variable = block.get_variable(text_data);
            if (variable !== null) return ExpressionMake(variable, null);
            else throw ("Unknown variable: "+ text_data);
        }
        else{
            assert(text_data.tokens.length, 1);
            var token = text_data.tokens[0];
            var func = program.get_function(token);
            if (func !== null){
                children = make_expression_children(expression_text, block, program);
                return ExpressionMake(token, children);
            }
            var struct = program.get_struct(token);
            if (struct !== null){
                return ExpressionMake(token, []);
            }
            else{
                throw ("No function or struct: " + text_data);
            }
        }
    }
    else if (text_data.classname === 'Operator'){
        children = make_expression_children(expression_text, block, program);
        assert(children.length, 2);
        var my_type = null;
        for (var i = 0; i < children.length; i++){
            var child_type = children[0].get_types()[0];
            if (my_type === null) my_type = child_type;
            else{
                assert (my_type.name === child_type.name);
            }
        }
        return ExpressionMake(token, children);
    }
    else{
        throw ("Unknown data: " + text_data);
    }
}
