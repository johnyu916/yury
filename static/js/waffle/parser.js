var VARIABLE_PATTERN = '[a-zA-z][a-zA-Z0-9_]*';
var OPERATORS_PATTERN = '==|!=|\+|-'

function DottedName(tokens){
    this.type = 'DottedName';
    this.tokens = tokens; 
}

function LeftPar(){
    this.type = 'LeftPar';
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

function read_dotted_name(orig){
    var text = orig;
    var result = re_match(VARIABLE_PATTERN, text);
    var matched = result[0]; text = result[1];

    if (matched === null) return [null, orig];

    var tokens = [matched];
    while(true){
        result = re_match('.'+VARIABLE_PATTERN, text);
        matched = result[0]; text = result[1];
        if (matched.length === 0) break;
        else {
            tokens.push(matched.substr(1, matched.length));
        }
    }
    return [new DottedName(tokens), text];
}

function read_expression(orig){
    text=orig;
    var result = null;

    while (text.length > 0){
        result = re_match(' *', text);

        result = re_match('\\(', text);
        text = result[0];
        if (result[0] !== null){
            stack.push(LeftPar());
            continue;
        }

        result = re_match('[0-9]+', text);
        text = result[1];
        if (result[0] !== null){
            // NOTE: assuming int for now. add more later.
            stack.push(ConstantText(parseInt(result[0])));
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
            stack.push(Operator(result[0]));
            continue;
        }
        result = re_match('\\)',text);
        text = result[1];
        if (result[0] !== null){
            var text_node = build_text_node(stack);
            if (text_node !== null){
                stack.push(new Operator(text_node));
            }
            continue;
        }

        result = re_match(':', text);
        if (result[0] !== null){
            text = ':'+text;
            break;
        }

    }

    stack.insert(0, new LeftPar());
    var exps = build_text_node(stack);
    if (len(exps) != 1){
        return [null, orig];
    }

    expression = exps[0];
    return [expression, text];
}

function build_text_node(stack){
    var tokens = [];
    var is_left_hit = false;

}

function read_statement(orig){
    var text = orig;
    var result = read_dotted_name(text);
    if (result[0] === null) return [null, orig];
    result = re_match(' *', text);

    result = re_match('=', text);
    if (result[0] === null) return [null, orig];

    result = re_match(' *', text);

    result = read_expression(text);
    if result[0] === null) return [null, orig];

    return result;
}

function WaffleParser(){
    
}

WaffleParser.prototype.parse = function(line){
    expression, line = read_expression(line)
}
