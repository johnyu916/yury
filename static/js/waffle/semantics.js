var Struct = {};

var Block = {
    code: []
    variables:[]
    parent:null
    program:null
};

var Func = object(Block);


function FuncMake

var Program = {
    functions: [],
    structs: []
};

var Expression = {
    data: null,
    children: null
};

Expression.get_types = function(){
    return [];
}

var Statement = {
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
    var dest_types = expression.get_types();
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
    return StatementMake(destinations, expression);
}

var Type = {
    name: "",
    size: 0
}

var Constant = {
    type: null,
    value: null
}

var Variable = {
    type: null,
    name: ""
}

var WaffleSemantics = {
    program: null,
    block: null
}

WaffleSemantics.process = function(construct){
    if (construct.type === 'ExpressionText'){
        return expression_make(construct, this.block, this.program);
    }
    else if (construct.type === 'StatementText'){
        return StatementMakeFromText(construct, this.block, this.program);
    }
}

function WaffleSemanticsMake(){
    var semantics = object(WaffleSemantics);
    semantics.program = object(Program);
    semantics.block = FuncMake();
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
    var data = null;
    if (text_data.classname === 'ConstantText'){
        type = get_constant_type(text_data.value);
        if (type === null) throw ("Unknown type: " + data.value);
        else return new Expression(new Constant(type, data.value), null);
    }
    else if (text_data.classname === 'DottedName'){
        // name could be variable, struct, or function.
        if (text_children === null){
            // must be variable
            var variable = block.get_variable(text_data);
            if (variable !== null) return new Expression(variable, null);
            else throw ("Unknown variable: "+ text_data);
        }
        else{
            assert(text_data.tokens.length, 1);
            var token = text_data.tokens[0];
            var func = program.get_function(token);
            if (func !== null){
                children = make_expression_children(expression_text, block, program);
                return new Expression(token, children);
            }
            var struct = program.get_struct(token);
            if (struct !== null){
                return new Expression(token, []);
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
        return new Expression(token, children);
    }
    else{
        throw ("Unknown data: " + text_data);
    }
}

