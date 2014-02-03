import json
import logging
import copy
import re
import string
from shared.common import get_bools
from collections import namedtuple
from settings import BAM_DIR
USHORT_SIZE = 16
PRIMITIVE_TYPES = ['int', 'double', 'string', 'list', 'dict']
CONDITIONAL_WORDS = ['if', 'elif', 'else', 'while']
OPERATORS = ['==', '!=', '+', '-']
OPERATORS_PATTERN = '==|!=|\+|-'
RESERVED_WORDS = copy.copy(PRIMITIVE_TYPES)
RESERVED_WORDS.extend(CONDITIONAL_WORDS)
VARIABLE_PATTERN = '[a-zA-z][a-zA-Z0-9_]*'
# insns is a set of instructions.



#int_type = VariableText('int', 4)
#double_type = VariableText('double', 8)

class Object(object):
    def __init__(self, name):
        self.name = name

    def get_dict(self):
        return {
            'name': self.name
        }



class Token(object):
    KINDS = ['left_par', 'right_par', 'operator', 'constant', 'name']
    def __init__(self, value):
        self.value = value

class LeftPar(Token):
    def __init__(self):
        super(Token, self).__init__(None)

class RightPar(Token):
    def __init__(self):
        super(RightPar, self).__init__(None)

class Comma(Token):
    def __init__(self):
        super(RightPar, self).__init__(None)

class Operator(Token):
    def __init__(self, value):
        super(RightPar, self).__init__(value)

class Constant(Token):
    def __init__(self, value):
        super(RightPar, self).__init__(value)

class Name(Token):
    def __init__(self, value):
        super(RightPar, self).__init__(value)

class VariableText(object):
    '''
    Type, name and value. Type can be primitive or defined from library. Constant is also represented as variable
    '''
    def __init__(self, arg_type, name, value):
        self.name = name
        self.arg_type = arg_type
        self.value = value

    def get_dict(self):
        return {
            'arg_type': self.arg_type,
            'name': self.name,
            'value': self.value
        }


class BlockText(object):
    def __init__(self):
        self.code = []  # code is expressions and blocks

    def get_dict(self):
        codes = []
        for line in self.code:
            codes.append(line.get_dict())
        return {
            'code': codes
        }


class FunctionText(BlockText):

    def __init__(self, name, inputs=[], outputs=[]):
        '''
        name is the function name (string).
        inputs is a list of variables. ditto outputs.
        '''
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        super(FunctionText, self).__init__()


    def get_dict(self):
        inputs = []
        for inpu in self.inputs:
            inputs.append(inpu.get_dict())

        outputs = []
        for output in self.outputs:
            outputs.append(output.get_dict())

        block_dict = super(FunctionText, self).get_dict()

        this_dict = {
            'name': self.name,
            'inputs': inputs,
            'outputs': outputs
        }
        this_dict.update(block_dict)
        return this_dict


class ConditionalText(BlockText):
    def __init__(self, condition):
        self.condition = condition
        super(ConditionalText, self).__init__()

    def get_dict(self):
        this_dict = {
            'condition': self.condition.get_dict()
        }
        codes = super(ConditionalText, self).get_dict()
        this_dict.update(codes)
        return this_dict


class WhileText(ConditionalText):
    def __init__(self, expression):
        super(WhileText, self).__init__(expression)


class IfBlock(ConditionalText):
    def __init__(self, expression):
        super(IfBlock, self).__init__(expression)
        self.name = 'if'

class ElIfBlock(ConditionalText):
    def __init__(self, expression):
        super(ElIfBlock, self).__init__(expression)


class ElseBlock(ConditionalText):
    def __init__(self, expression):
        super(ElseBlock, self).__init__(expression)


class StatementText(object):
    def __init__(self, dests, expression):
        '''
        a = add(3,5)
        dests is a list of VariableText
        expression is ExpressionText
        '''
        self.dests = dests  # dests is a list
        self.expression = expression

    def get_dict(self):
        dest_list = []
        for dest in self.dests:
            dest_dict = dest.get_dict()
            dest_list.append(dest_dict)
        return {
            'dests': dest_list,
            'expression': self.expression.get_dict()
        }

class TextNode(object):
    def __init__(self, children):
        self.children = children

class ExpressionText(object):
    '''
    ExpressionText is a node that carries data.
    children can be ExpressionTexts or empty.
    data can be a Token (Operator, Name, Constant)
    '''
    def __init__(self, data, children=()):
        if type(children) != tuple:
            children = tuple(children)
        if type(data) == VariableText:
            assert len(children) == 0

        #self.data = 'add'  # data is either function names or variables
        self.data = data
        self.children = children

    def __str__(self):
        return json.dumps(self.get_dict())

    def get_dict(self):
        return get_expression_dict(self)


def get_expression_dict(expression):
    children = []
    for child in expression.children:
        #print child
        children.append(child.get_dict())

    if type(expression.data) == str:
        data = expression.data
    else:
        data = expression.data.get_dict()

    return {
        'data': data,
        'children':children
    }


def get_num_front_spaces(line):
    line2 = line.rstrip()
    line3 = line.strip()
    return len(line2) - len(line3)

def get_stack_index(line):
    '''
    return 0 if 0, 1 if 4, 2 if 8, etc.
    '''
    num = get_num_front_spaces(line)
    if not (num % 4) == 0:
        raise Exception("Wrong number of spaces")
    return num/4

def get_program_dict(program):
    functions = []
    for function in program.functions:
        functions.append(function.get_dict())
    structs = []
    for struct in program.structs:
        structs.append(struct.get_dict())

    return {
        'functions': functions,
        'structs': structs
    }


class ProgramText(object):
    def __init__(self, functions=[], structs=[]):
        '''
        functions is a list of FunctionText objects.
        structs is a list of Struct objects.
        '''
        self.functions = functions
        self.structs = structs
        #main = get_function(functions, '__main__')
        #self.stack = [main]
        #self.index = 0



    def __str__(self):
        return json.dumps(get_program_dict(self))


# Parsing functions
def read_name(text):
    '''
    Read alphanumeric.
    Return "" if nothing read.
    '''
    #text.strip(' ')  # strip beginning spaces
    regex = re.compile('[a-zA-z][a-zA-Z0-9]*')
    match = regex.match(text)
    if match:
        return match.group('name')


def read_space(text):
    par, text = re_match(' ', text)


def read_equals(text):
    return

def read_if(text):
    return None, text


def read_elif(text):
    return None, text


def read_else(text):
    return None, text


def read_while(text):
    # if, elif ,else, while
    print "conditional text matching against: " + text
    orig = text
    whil, text = re_match('while', text)
    if whil == None:
        return None, orig

    # read space
    space, text = re_match(' ', text)
    if space == None:
        return None, orig

    # read left parenthesis
    par, text = re_match('\(', text)
    if par == None:
        return None, orig

    # read expression
    expr, text = read_expression(text)
    if expr == None:
        return None, orig
    print 'while read exp: {0}. text: {1}'.format(expr, text)
    # read right parenthesis and colon
    par, text = re_match('\):', text)
    if par is None:
        return None, orig

    # create while object
    return WhileText(expr), text


def read_expression(text):
    orig = text

    stack = []

    while len(text) > 0:
        par, text = re_match('\(', text)
        if par is not None:
            stack.append(LeftPar())
            continue

        number, text = re_match('[0-9]+', text)
        if number is not None:
            stack.append(Constant(number))
            continue

        variable, text = re_match(VARIABLE_PATTERN, text)
        if variable is not None:
            stack.append(Name(variable))
            continue

        comma, text = re_match(',', text)
        if comma is not None:
            stack.append(Comma())

        par, text = re_match('\)', text)
        if par is not None:
            # time to pop some stuff out
            expression = build_text_node(stack)
            stack.append(expression)
            continue

        colon, text = re_match(':', text)
        if colon is not None:
            text = ':' + text
            break

    stack.insert(0, '(')
    node = build_text_node(stack)

    expression = build_expression(node)
    if expression is not None:
        return expression, text

    else: return None, orig
    # now lets try to do something with the stack.

def build_text_node(stack):
    childs = []
    while len(stack) > 0:
        token = stack.pop()
        if isinstance(token, LeftPar):
            # we're done, but it might be a function call.
            return TextNode(childs)
        else:
            childs.append(token)

    logging.debug("build_text_node stack: {0}".format(stack))
    raise Exception("Should have hit left parenthesis.")

def build_expression(node):
    tokens = node.children
    expression = build_function_call(tokens)
    if expression is not None:
        return expression

    expression = build_operation(tokens)
    if expression is not None:
        return expression

    expression = build_constant_or_variable(tokens)
    if expression is not None:
        return expression

    return None


def build_constant_or_variable(orig_tokens):
    node_childs = orig_tokens
    if len(node_childs) != 1: return None

    node_child = node_childs.pop()
    value = None
    childs = []
    if isinstance(node_child, Name):
        value = Name
    elif isinstance(node_child, Constant):
        value = node_child
    elif isinstance(node_child, TextNode):
        expression = build_expression(node_child)
        childs.append(expression)
    else:
        return None
    return ExpressionText(value, childs)


def build_function_call(orig_tokens):
    # read name
    node_tokens = copy.copy(orig_tokens)
    function_name = node_tokens.pop()
    if not isinstance(function_name, Name):
        return None

    node_enclosed = node_tokens.pop()
    if not isinstance(node_enclosed, TextNode):
        return None

    node_childs = node_enclosed.children()
    childs = []
    while True:
        if len(node_childs) == 0: break
        node_child = node_childs.pop()
        variable = build_constant_or_variable(node_child)
        if variable is None:
            return None

        if len(node_childs) == 0: break
        node_comma = node_childs.pop()
        if not isinstance(node_comma, Comma):
            return None

    return ExpressionText(function_name, childs)


def build_operation(orig_tokens):
    node_tokens = copy.copy(orig_tokens)
    childs = []
    node_first = node_tokens.pop()

    node_child = node_tokens.pop()
    variable = build_constant_or_variable(node_child)
    if variable is None:
        return None

    operator = node_tokens.pop()
    if not isinstance(operator, Operator):
        return None

    node_child = node_tokens.pop()
    variable = build_constant_or_variable(node_child)
    if variable is None:
        return None

    return ExpressionText(operator, childs)


def build_expression_old(node):
    '''
    By this point stack doesn't have any left or right
    parentheses. It only has nodes and tokens.
    '''
    # now try building an expression.
    childs = []
    data = None

    items = node.children
    item = items.pop()

    DEFAULT = 0 # default state
    NAME_READ = 1 # name was read
    state = DEFAULT
    last_item = None
    for item in node.children:
        if isinstance(item, Operator):
            if last_item is None:
                raise Exception("operator before any operand")
            else:
                data = item
        elif isinstance(item, Constant):
            if last_item is not None:
                assert (isinstance(last_item, Operator) or isinstance(last_item, Comma)), "constant must be after operator or comma"
            child = ExpressionText(item)
            childs.append(child)
        elif isinstance(item, Name):
            pass
            # could be variable or function call.
        if isinstance(item, TextNode):
            if last_item is not None:
                if isinstance(last_item, Operator):
                    child = build_expression(item)
                    childs.append(child)
                elif isinstance(last_item, Name):
                    # function call.
                    data = last_item
                    children = build_function_parameters(item)

        last_item = item

def build_function_parameters(node):
    '''
    This is a list of expression texts
    '''
    texts = []
    last_item = None
    for item in node.children:
        if isinstance(item, Constant):
            child = ExpressionText(item)
            texts.append(child)
        elif isinstance(item, Comma):
            assert last_item is not None
            assert (isinstance(last_item, Constant) or isinstance(last_item, Name)), "comma must be after a variable"
        else:
            pass
        last_item = item


def read_expression_old(orig):
    """
    TODO: include ()
    (a)
    """
    text = orig
    function_call, text = read_function_call(orig)
    if function_call != None:
        return function_call, text

    operation, text = read_operation(orig)
    if operation != None:
        return operation, text

    constant, text = read_constant_or_variable(orig)
    if constant != None:
        return ExpressionText(constant), text

    return None, orig


def read_statement(orig):
    '''
    StatementText example: counter = 5
    '''
    text = orig
    dest, text = re_match('[a-zA-z][a-zA-Z0-9]*', text)
    if dest == None:
        return None, orig

    # try reading space
    space, text = re_match(' ', text)

    equ, text = re_match('=', text)
    if equ == None:
        return None, orig

    dest_var = VariableText(None, dest, None)
    # either constant, variable, function call, or operation
   
    # try reading space
    space, text = re_match(' ', text)

    expression, text = read_expression(text)
    if expression != None:
        return StatementText([dest_var], expression), text

    return None, orig

def read_function_definition(orig):
    '''
    ex1: (int current) fibonacci(int index):
    return (FunctionText, text_left)
    return (None, orig) if not function
    '''
    text = orig
    print "text matching against: " + text
    outputs, text = read_arguments_definition(text)
    if outputs == None:
        return None, orig
    print outputs
    print ' text: ' + text
    # try reading space
    space, text = re_match(' ', text)
    if space == None:
        return None, orig

    function_name, text = re_match('[a-zA-z][a-zA-Z0-9]*', text)
    if function_name == None:
        return None, orig
    print 'function_name: ' + function_name + ' text: ' + text

    inputs, text = read_arguments_definition(text)
    if inputs == None:
        return None, orig
    print inputs
    print ' text: ' + text
        
    return FunctionText(function_name, inputs, outputs), text


def read_arg_definition(orig):
    '''
    Read int continue
    Return VariableText()
    '''
    pattern = '[a-zA-z][a-zA-Z0-9]*'
    text = orig

    # type
    arg_type, text = re_match(pattern, text)
    if arg_type == None:
        return None, orig

    print "arg_type: " + arg_type + " text: " + text
    # space
    space, text = re_match(' ', text)
    if space == None:
        return None, orig
    print "soace: " + space+ " text: " + text

    # name
    name, text = re_match(pattern, text)
    if name == None:
        return None, orig
    print "name: " + name+ " text: " + text
    var = VariableText(arg_type, name, None)
    return var, text


def re_match(regex, text):
    m = re.match(regex, text)
    if m:
        return m.group(), text[m.end():]
    else:
        return None, text


def read_arguments_definition(orig):
    '''
    (int a)
    ()
    (int a, string b)
    return variabes, text_left
    return None, text if not matched.
    '''
    text = orig
    # left paren
    par, text = re_match('\(', text)
    if par == None:
        return None, orig

    print "par: " + par + " text: " + text

    # arguments
    variables = []
    while True:
        # match type name
        var, text = read_arg_definition(text)
        if var != None:
            variables.append(var)

        # try reading comma
        com, text = re_match(',', text)
        if com == None:
            break

        # try reading space
        space, text = re_match(' ', text)
        if space == None:
            continue

    # see if ended
    print "text: " + text
    par, text = re_match('\)', text)
    if par == None:
        return None, orig 
    print "par: " + par + " text: " + text
    return variables, text

def is_reserved(text):
    return text in RESERVED_WORDS

def read_constant(orig):
    '''
    Return VariableText with name set to None
    '''
    text = orig
    dest, text = re_match('[0-9]+', text)
    if dest != None:
        print "read_constant dest: {0}".format(dest)
        return VariableText('int', None, int(dest)), text
    else:
        return None, orig


def read_variable(orig):
    text = orig
    dest, text = re_match('[a-zA-Z][a-zA-Z0-9]*', orig)
    if dest != None and not is_reserved(dest):
        return VariableText(None, dest, None), text
    else:
        return None, orig


def read_constant_or_variable(text):
    '''
    Constant is a integer or variable name.
    '''
    # read int
    orig = text
    variable, text = read_constant(text)
    if variable != None:
        return variable, text

    variable, text = read_variable(text)
    if variable != None:
        return variable, text

    # read variable name
    return None, orig


def read_operation(text):
    '''
    ex1: index == 0
    Operation is like a function in that it can return something.
    supported:
    ==
    !=
    '''
    orig = text
    left, text = read_constant_or_variable(text)
    if left == None:
        return None, orig

    # read space
    space, text = re_match(' ', text)
    
    # operator
    # TODO: fix here
    #oper, text = re_match('==|!=|\+|-', text)
    oper, text = re_match(OPERATORS_PATTERN, text)
    if oper == None:
        return None, orig

    # read_space
    space, text = re_match(' ', text)
    # right
    right, text = read_constant_or_variable(text)
    if right == None:
        return None, orig


    left_ex = ExpressionText(left)
    right_ex = ExpressionText(right)

    return ExpressionText(oper, [left_ex, right_ex]), text
    

def read_function_call(text):
    '''
    ex1: add(a,b), add(add(a,b), c), add(a+b, c)
    return (ExpressionText, text_left)
    return (None, arg_text) if not expression
    '''
    # read text
    # read any spaces
    orig = text
    function_name, text = re_match(VARIABLE_PATTERN, text)
    if function_name == None:
        return None, orig

    par, text = re_match('\(', text)
    if par == None:
        return None, orig

    # one or more parameters
    params = []
    while True:
        # match type name
        child_expression, text = read_expression(text)
        if child_expression != None:
            params.append(child_expression)

            # try reading comma
            com, text = re_match(',', text)
            if com == None:
                break

        # try reading space
        space, text = re_match(' ', text)
        if space == None:
            continue

    par, text = re_match('\)', text)
    if par == None:
        return None, orig

    # only reads one level deep
    return ExpressionText(function_name, params), text


def is_function_name_old(functions, name):
    for function in functions:
        if function == name:
            return True
    return False

def is_var_name_old(variables, name):
    for var in variables:
        if var == name:
            return True
    return False


def name_end_old(name_chars):
    name = string.join(name_chars, '')
    # is name a function call? variable?
    if is_function_name_old(name):
        state = 'FUNCTION'
    elif is_var_name_old(name):
        state = 'VAR'
    else:
        raise Exception("unknown name")


class Parser(object):
    # parse program text.
    def __init__(self, lines):
        self.variables = []
        main_function = FunctionText("__main__", [],[])
        self.program = ProgramText(functions=[main_function])
        self.lines = lines
        self.stack = [main_function]
        for line in self.lines:
            # syntax checker
            self.check(line)


    def check(self, line):
        # just read from beginning.
        line = line.rstrip()
        print "processing: '{0}'".format(line)

        # how many spaces are in front?
        stack_index = get_stack_index(line)
        if stack_index < len(self.stack) - 1:
            num_pop = (len(self.stack) - 1) - stack_index
            while num_pop > 0:
                self.stack.pop()
                num_pop -= 1
        elif stack_index >= len(self.stack):
            raise Exception("spaced too much")

        line = line.strip()
        if line == '':
            return

        # Could be FunctionText definition
        if stack_index == 0:
            function, line = read_function_definition(line)
            if function:
                print "function_definition: {0}".format(function.get_dict())
                self.program.functions.append(function)
                self.stack.append(function)
                return

        block = self.stack[-1]

        statement, line = read_statement(line)
        if statement:
            print "statement read: {0}. appending to: {1}".format(statement, block)
            block.code.append(statement)
            return

        expression, line = read_expression(line)
        if expression:
            print "expression read: {0}".format(expression)
            block.code.append(expression)
            return


        # conditional (if, elif, else, while)
        while_clause, line = read_while(line)
        if while_clause:
            print "while read: {0}".format(while_clause.get_dict())
            block.code.append(while_clause)
            self.stack.append(while_clause)
            return

        if_clause, line = read_if(line)

        elif_clause, line = read_elif(line)

        else_claus, line = read_else(line)

        # read return, break

        raise Exception("Something wrong bud")


    def read_operation_old(text):
        operators = ['+', '-', '*', '/', '%']
        for char in text:
            if char == '(':
                pass
            elif char == ')':
                pass
            elif char == ' ':
                pass
            elif char in operators:
                # needs an operand
                pass

def get_function(functions, data):
    return None

def get_variable(variables, data):
    return None


def expression_check(exp, variables, functions):
    function = get_function(functions, exp.data)
    if function:
        # read children
        pass

    elif get_variable(variables, exp.data):
        pass

    else:
        raise Exception("Undeclared name: {0}".format(exp.data))


