function Struct(){

}

function Function(){

}

function Program(){
    this.functions = [];
    this.structs = [];
}

function Expression(data, children){
    this.data = data;
    this.children = children;
}

function Type(name, size):
    this.name = name;
    this.size = size;

function Constant(type, value){
    this.type = type;
    this.value = value;
}

function Variable(type, name){
    this.type = type;
    this.name = name;
}

function WaffleSemantics(){
    
    this.program = new Program();
    this.current_block = null;
}

WaffleSemantics.prototype.process = function(construct){
    if (construct.type === 'ExpressionText'){
        this.expression_make(construct);
    }
}

WaffleSemantics.prototype.expression_make = function(expression_text){
    var text_data = expression_text.data;
    var children = [];
    var data = null;
    if (text_data.classname === 'ConstantText'){
        type = get_constant_type(text_data.value);
        if (type === null) throw ("Unknown type: " + data.value);
        else return new Expression(new Constant(type, data.value), null);
    }
    else if (text_data.classname ==== 'DottedName'){
        this.current_block
    }
    return Expression(data, children);
}
