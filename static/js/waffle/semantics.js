var Type = {
    classname: 'Type',
    name: "",
    size: 0
}
var Struct = object(Type);
Struct.members = [];
Struct.classname = 'Struct';

Struct.get_member = function(name){
    for (var i = 0; i < this.members.length; i++){
        if (this.members[i].name === name) return this.member[i];
    }
    return null;
}

var Block = {
    code: [],
    variables: [],
    parent: null,
    program: null
};

Block.variables_append = function(variable){
    this.variables.push(variable);
}

Block.get_variable = function(dotted_name){
    var root_name = dotted_name.tokens[0];
    for (var i =0; i < this.variables.length; i++){
        var variable = this.variables[i];
        return variable;
    }
    if (this.parent !== null) return this.parent.get_variable(dotted_name);
    else return null;
}

var Func = object(Block);
Func.name = '';

Func.get_types = function(){
    var types = [];
    for (var i = 0; i < this.outputs.length; i++){
        types.append(this.outputs[i].type);
    }
    return types;
}

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
    children: null,
    types: []
};


function ExpressionMake(data, children, types){
    var expression = object(Expression);
    expression.data = data;
    expression.children=children;
    expression.types = types;
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
    var text_dests = statement_text.destinations;
    var text_exp = statement_text.expression;
    var exp = expression_make(text_exp, block, program);
    var dest_types = exp.types;
    var destinations = [];
    for (var i = 0; i < text_dests.length; i++){
        var text_dest = text_dests[i];
        var type = dest_types[i];
        var destination = block.get_variable(text_dest);
        if (destination !== null){
            var dotted_type = get_dotted_type(dest.tokens, destination.type);
            assert_message(dotted_type, type.name, "dest types must be equal");
        }
        else{
            //add a new variable.
            destination = VariableMake(type, text_dest.tokens[0]);
            block.variables_append(destination);
        }
        destinations.push(text_dest);
    }
    return StatementMake(destinations, exp);
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

function get_dotted_type(tokens, this_type){
    if (tokens.length === 0) return null;
    if (tokens.length === 1) return this_type;
    if (this_type.classname !== 'Struct') return null;
    var member = this_type.get_member(tokens[1]);
    if (member === null) return null;
    return get_dotted_type(tokens.slice(1));
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
        var type = get_constant_type(text_data.value);
        if (type === null) throw ("Unknown type: " + data.value);
        else return ExpressionMake(ConstantMake(type, text_data.value), null, [type]);
    }
    else if (text_data.classname === 'DottedName'){
        // name could be variable, struct, or function.
        if (text_children === null){
            // must be variable
            var variable = block.get_variable(text_data);
            var type = get_dotted_type(text_data.tokens, variable.type);
            if (variable !== null) return ExpressionMake(variable, null, [type]);
            else throw ("Unknown variable: "+ text_data);
        }
        else{
            assert(text_data.tokens.length, 1);
            var token = text_data.tokens[0];
            var func = program.get_function(token);
            if (func !== null){
                children = make_expression_children(expression_text, block, program);
                return ExpressionMake(token, children, func.get_types());
            }
            var struct = program.get_struct(token);
            if (struct !== null){
                return ExpressionMake(token, [], [struct]);
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
        return ExpressionMake(token, children, children[0].types);
    }
    else{
        throw ("Unknown data: " + text_data);
    }
}
