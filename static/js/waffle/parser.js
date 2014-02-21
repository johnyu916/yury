var VARIABLE_PATTERN = '[a-zA-z][a-zA-Z0-9_]*';
var OPERATORS_PATTERN = '==|!=|\\+|-';

function DottedName(tokens){
    this.classname = 'DottedName';
    this.tokens = tokens; 
}

function Operator(value){
    this.classname = 'Operator';
    this.value = value;
}

function LeftPar(){
    this.classname = 'LeftPar';
}


function ExpressionText(data, children){
    this.classname = 'ExpressionText';
    this.data = data;
    this.children = children;
}

function StatementTextMake(dests, exp){
    var statement = object(StatementText);
    statement.expression = exp;
    statement.destinations = dests;
    return statement;
}

function ConstantTextMake(value){
    var con = object(ConstantText);
    con.value = value;
    return con;
}

var ConstantText = {
    classname: 'ConstantText',
    value: null
};

var StatementText = {
    classname: 'StatementText',
    expression: null,
    destinations: []
};

function Expressions(values){
    this.classname = 'Expressions';
    for (var i = 0; i < values.length; i++){
        assert(values[i].classname, 'ExpressionText');
    }
    this.values = values;
}

// Return matching portion of text, and remainter of text.
// Only matches from beginning.
function re_match(regex, text){
    var pattern = RegExp('^'+regex);
    var result = pattern.exec(text);
    if (result === null) return [null, text];
    else{
        var matching = result[0];
        return [matching, text.substr(matching.length, text.length)];
    }
}

/* if orig is in the form 'bob.dole.jr', then 
 * make a DottedName and return it.
 * Returns [DottedName, text_left]
 */
function read_dotted_name(orig){
    var text = orig;
    var result = re_match(VARIABLE_PATTERN, text);
    var matched = result[0]; text = result[1];

    if (matched === null) return [null, orig];

    var tokens = [matched];
    while(true){
        result = re_match('.'+VARIABLE_PATTERN, text);
        matched = result[0]; text = result[1];
        if (matched === null) break;
        else {
            tokens.push(matched.substr(1, matched.length));
        }
    }
    return [new DottedName(tokens), text];
}

/* Read string
 * return [expression, text_left]. expression is null
 * if orig is not an expression.
 */
function read_expression(orig){
    text=orig;
    var result = null;
    var stack = [];
    while (text.length > 0){
        result = re_match(' *', text);
        text = result[1];

        result = re_match('\\(', text);
        text = result[1];
        if (result[0] !== null){
            stack.push(new LeftPar());
            continue;
        }

        result = re_match('[0-9]+', text);
        text = result[1];
        if (result[0] !== null){
            // NOTE: assuming int for now. add more later.
            stack.push(ConstantTextMake(parseInt(result[0])));
            continue;
        }

        result = read_dotted_name(text);
        text = result[1];
        if (result[0] !== null){
            stack.push(result[0]);
            continue;
        }

        result = re_match(',',text);
        text = result[1];
        if (result[0] !== null){
            stack.push(result[0]);
            continue;
        }
        result = re_match(OPERATORS_PATTERN,text);
        text = result[1];
        if (result[0] !== null){
            stack.push(new Operator(result[0]));
            continue;
        }
        result = re_match('\\)',text);
        text = result[1];
        if (result[0] !== null){
            var text_node = build_text_node(stack);
            if (text_node !== null){
                stack.push(text_node);
            }
            continue;
        }

        result = re_match(':', text);
        if (result[0] !== null){
            text = ':'+text;
            break;
        }

    }

    stack.unshift(new LeftPar());
    var exps = build_text_node(stack);
    if (exps.values.length !== 1){
        return [null, orig];
    }

    expression = exps.values[0];
    return [expression, text];
}

/* Stack has a bunch of tokens, so go back down until
 * Left parenthesis is hit. Then try to build an
 * expression from it. This returns a Expressions.
 */
function build_text_node(stack){
    var tokens = [];
    var is_left_hit = false;
    var token = null;
    while (stack.length > 0){
        token = stack.pop();
        if (token.classname === 'LeftPar'){
            is_left_hit = true;
        }
        else{
            tokens.unshift(token); //add to beginning
        }
    }

    if (!is_left_hit){
        throw ("should have hit left parenthesis but didn't" + stack);
    }

    /* Here are some patterns that can be read by below:
     *
     */
    var result = null;
    var expressions = [];
    while (true){
        if (tokens.length === 0) break;
        result = build_expression(tokens);
        tokens = result[1];
        if (result[0] === null){
            throw ("unable to build expression from: "+ tokens);
        }
        else{
            expressions.push(result[0]);
        }
        if (tokens.length > 0){
            comma = tokens.pop();
            if (comma.classname !== 'Comma'){
                throw ("Tokens left but not comma: " + comma);
            }
        }
    }

    return new Expressions(expressions);
}

// Returns expression and tokens remaining. If no
// expression was found, then return null, original tokens.
function build_expression(orig){
    var tokens = orig.slice();
    var result = build_operation(tokens);
    if (result[0] !== null){
        return result;
    }
    result = build_function_call(tokens);
    if (result[0] !== null){
        return result;
    }
    result = build_constant_or_variable(tokens);
    if (result[0] !== null){
        return result;
    }
    return [null, orig];
}

/*
 * Return [expression, tokens_left];
 */
function build_operation(orig){
    var tokens = orig.slice(0);
    var result = build_function_call(tokens);
    if (result[0] === null){
        result = build_constant_or_variable(tokens);
    }
    if (result[0] === null){
        return [null, orig];
    }

    left_ex = result[0];
    tokens = result[1];

    // you can have many operators, for example x+y+z.
    var op_terms = [];
    while (true){
        if (tokens.length === 0){
            if (op_terms.length > 0) break;
            else return [null, orig];
        }
        operator = tokens.shift();
        if (operator.classname !== 'Operator'){
            return [null, orig];
        }

        result = build_function_call(tokens);
        if (result[0] === null){
            result = build_constant_or_variable(tokens);
        }
        if (result[0] === null){
            return [null, orig];
        }
        right_ex = result[0];
        tokens = result[1];
        op_terms.push([operator, right_ex]);
    }

    for (var i = 0; i < op_terms.length; i++){
        var op_term = op_terms[i];
        left_ex = new ExpressionText(op_term[0], [left_ex, op_term[1]]);
    }
    return [left_ex, tokens];
}

function build_function_call(orig){
    var tokens = orig.slice(0);
    var expression = null;
    if (tokens.length === 0) return [null, orig];
    var name = tokens.shift();
    if (name.classname === "DottedName"){
        // okay get another one.
        if (tokens.length === 0) return [null, orig];
        var params = tokens.shift();
        if (params.classname === 'Expressions'){
            expression = new ExpressionText(name, params.values);
        }
        else{
            return [null, orig];
        }
    }
    else{
        return [null, orig];
    }
    return [expression, tokens];
}

/* Tokens are list of objects (dottedname, constant, expressions, operator).
 * Return [expression, tokens_left]
 * expression is null if not found.
 */
function build_constant_or_variable(orig){
    var tokens = orig.slice(0);
    var expression = null;
    var name = tokens.shift();
    if (name.classname === "DottedName"){
        expression = new ExpressionText(name, null);
    }
    else if (name.classname === "ConstantText"){
        expression = new ExpressionText(name, null);
    }
    else if (name.classname === 'Expressions'){
        // parenthesis inside parenthesis ((left + right))
        assert(name.values.length, 1);
        expression = name.values[0];
    }
    else{
        return [null, orig];
    }
    return [expression, tokens];
}


function read_statement(orig){
    var text = orig;
    console.log("text 0: " + text);
    var result = read_dotted_name(text);
    if (result[0] === null) return [null, orig];
    var dest = result[0];
    text = result[1];
    console.log("text: " + text);
    result = re_match(' *', text);
    text = result[1];
    console.log("text: " + text);

    result = re_match('=', text);
    if (result[0] === null) return [null, orig];
    text = result[1];
    console.log("text: " + text);

    result = re_match(' *', text);
    text = result[1];
    console.log("text: " + text);

    result = read_expression(text);
    if (result[0] === null) return [null, orig];
    var expression = result[0];
    text = result[1];
    console.log("dest: " + dest + " " + expression);
    return [StatementTextMake([dest], expression), text];
}

var WaffleParser = {

};

WaffleParser.parse = function(line){
    var result = read_statement(line);
    if (result[0] !== null){
        return result[0];
    }
}

function WaffleParserMake(){
    var parser = object(WaffleParser);
    return parser;
}
