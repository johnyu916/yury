POINTER_SIZE = 4;

var BlockStack = {
    offset: 0,
    variable_dicts: []
};

var WaffleWriter = {
    block_stack: null;
    insns: [];
};

WaffleWriter.process = function(code){
    if (code.classname === 'Statement'){
        this.write_statement(code, this.block_stack)
    }
    return [];
}

WaffleWriter.set_sp_offset(register, offset, temp_reg){
    this.insns.push(set_int(register, offset*-1));
    this.insns.push(subtract_int(register, this.sp_register, temp_reg))
}

WaffleWriter.write_expression = function(expression, block_stack){
    var return_types = expression.get_types();
    data = expression.data
    var return_vars = {}
    var block_begin_offset = block_stack.offset;

    for (var i = 0; i < return_types.length; i++){
        block_stack.offest -= POINTER_SIZE;
        return_var = {
            variable: VariableMake(return_types[i], String(i));
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
    for (int i = 0; i < dests.length; i++){
        var dest = dests[i];
        // well actually need to insert if they aren't already there.
        var variable_dict =  block_stack.get_variable_dict(dest);
        if (variable_dict === null){
            throw ("Variable doesn't exist " + dest);
        }
    }
    this.write_expression(block_stack, statement.expression);

    for (var i = 0; i < dests.length; i++){
        var dest = dests[i];
        var variable_dict = block_stack.get_variable_dict(dest);

    }
}

function WaffleWriterMake(){
    var writer = object(WaffleWriter);
    writer.block_stack = object(BlockStack);
    return writer;
}
