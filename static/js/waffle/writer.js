POINTER_SIZE = 4;

var BlockStack = {
    offset: 0,
    variable_dicts: []
};

// dest is a dottedname
BlockStack.get_variable_dict = function(dest){
    assert(dest.tokens.length, 1, "get_variable_dict fail");
    var name = dest.tokens[0];
    for (var i = 0; i < this.variable_dicts.length; i++){
        var dict = this.variable_dicts[i];
        if (dict.variable.name === name) return dict;
    }
    return null;
};

BlockStack.new_variable = function(variable){
    this.offset -= POINTER_SIZE;
    var var_dict = {
        'variable': variable,
        'offset': this.offset
    };
    this.variable_dicts.push(var_dict);
}

var WaffleWriter = {
    block_stack: null,
    insns: []
};

WaffleWriter.process = function(code){
    if (code.classname === 'Statement'){
        this.write_statement(code, this.block_stack)
    }
    return [];
}

WaffleWriter.set_sp_offset = function(register, offset, temp_reg){
    this.insns.push(BigInstruction.set_int(register, offset*-1));
    this.insns.push(BigInstruction.subtract_int(register, this.sp_register, temp_reg))
}

WaffleWriter.write_expression = function(expression, block_stack){
    var return_types = expression.types;
    data = expression.data
    var return_vars = {}
    var block_begin_offset = block_stack.offset;

    for (var i = 0; i < return_types.length; i++){
        block_stack.offest -= POINTER_SIZE;
        return_var = {
            variable: VariableMake(return_types[i], String(i)),
            offset: block_stack.offset
        }
        return_vars[i] = return_var;
    }

    if (data.classname === 'Constant'){
        var dest_offset = return_vars[0].offset;
        this.set_sp_offset(4, dest_offset, 3);
    }
    else if (data.classname === 'DottedName'){
    }
    else{

    }
}

WaffleWriter.write_statement = function(statement, block_stack){
    var dests = statement.destinations;
    for (var i = 0; i < dests.length; i++){
        var dest = dests[i];
        // well actually need to insert if they aren't already there.
        var variable_dict =  block_stack.get_variable_dict(dest);
        if (variable_dict === null){
            //add to block_stack
            var new_var = VariableMake(statement.expression.types[i], dest.tokens[0]);
            block_stack.new_variable(new_var);
        }
    }
    this.write_expression(statement.expression, block_stack);
}

function WaffleWriterMake(){
    var writer = object(WaffleWriter);
    writer.block_stack = object(BlockStack);
    return writer;
}
