import json
import logging
import copy
import re
import string
from shared.common import get_bools
USHORT_SIZE = 16
PRIMITIVE_TYPES = ['int', 'double', 'string', 'list', 'dict']
CONDITIONAL_WORDS = ['if', 'elif', 'else', 'while']
OPERATORS = ['==', '!=', '+', '-']
OPERATORS_PATTERN = '==|!=|\+|-'
RESERVED_WORDS = copy.copy(PRIMITIVE_TYPES)
RESERVED_WORDS.extend(CONDITIONAL_WORDS)
VARIABLE_PATTERN = '[a-zA-z][a-zA-Z0-9_]*'

class Token(object):
    KINDS = ['left_par', 'right_par', 'operator', 'constant', 'name']
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return json.dumps(self.get_dict())

    def get_dict(self):
        return {
            'value': self.value
        }

class LeftPar(Token):
    def __init__(self):
        super(LeftPar, self).__init__('(')

class RightPar(Token):
    def __init__(self):
        super(RightPar, self).__init__(')')

class Comma(Token):
    def __init__(self):
        super(Comma, self).__init__(',')

class Operator(Token):
    pass

class ConstantText(Token):
    pass

class Name(Token):
    pass

class DottedName(object):
    def __init__(self, tokens):
        '''
        '''
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        self.tokens = tokens

    def get_dict(self):
        return {
            'type': str(DottedName),
            'tokens': self.tokens
        }

    def __str__(self):
        return json.dumps(self.get_dict())


class Parameter(object):
    '''
    For parsing function definition parameters.
    Defined by type, name. Type can be primitive or defined from library. ConstantText is also represented as variable
    '''
    def __init__(self, arg_type, name):
        '''
        arg_type and name are both strings.
        '''
        self.name = name
        self.arg_type = arg_type

    def get_dict(self):
        return {
            'arg_type': self.arg_type,
            'name': self.name,
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

class StructText(object):
    def __init__(self, name, members=[]):
        '''
        name is string.
        members is list of Parameters
        '''
        self.name = name
        self.members = members

    def get_dict(self):
        members = []
        for member in self.members:
            members.append(member.get_dict())
        return {
            'name': self.name,
            'members': members
        }

    def __str__(self):
        return json.dumps(self.get_dict())


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
    def __init__(self, condition=None):
        self.condition = condition
        super(ConditionalText, self).__init__()

    def get_dict(self):
        this_dict = {}
        if self.condition is not None:
            this_dict['condition'] = self.condition.get_dict()
        codes = super(ConditionalText, self).get_dict()
        this_dict.update(codes)
        return this_dict


class WhileText(ConditionalText):
    pass


class IfText(ConditionalText):
    pass

class ElIfText(ConditionalText):
    pass

class ElseText(ConditionalText):
    def __init__(self):
        super(ElseText, self).__init__()


class StatementText(object):
    def __init__(self, dests, expression):
        '''
        a = add(3,5)
        dests is a list of DottedName objects
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

    def __str__(self):
        return json.dumps(self.get_dict())


class ExpressionText(object):
    '''
    ExpressionText is a node that carries data.
    children can be ExpressionTexts or empty.
    data can be a Token (Operator, Name, ConstantText)
    '''
    def __init__(self, data, children=()):
        if type(children) != tuple:
            children = tuple(children)

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
        return json.dumps(self.get_dict())

    def get_dict(self):
        return get_program_dict(self)


def read_if(text):
    orig = text
    if_word, text = re_match('if', text)
    if if_word is None:
        return None, orig

    # read expression
    expr, text = read_expression(text)
    if expr is None:
        return None, orig

    colon, text = re_match(':', text)
    if colon is None:
        return None, orig

    return IfText(expr), text


def read_elif(text):
    orig = text
    if_word, text = re_match('elif', text)
    if if_word is None:
        return None, orig

    # read expression
    expr, text = read_expression(text)
    if expr is None:
        return None, orig

    colon, text = re_match(':', text)
    if colon is None:
        return None, orig

    return IfText(expr), text


def read_else(text):
    orig = text
    else_word, text = re_match('else:', text)
    if else_word is None:
        return None, orig
    return ElseText(), text


def read_while(text):
    # if, elif ,else, while
    print "while text matching against: " + text
    orig = text
    whil, text = re_match('while', text)
    if whil is None:
        return None, orig

    # read expression
    expr, text = read_expression(text)
    if expr is None:
        return None, orig

    print 'while read exp: {0}. text: {1}'.format(expr, text)
    colon, text = re_match(':', text)
    if colon is None:
        return None, orig

    # create while object
    return WhileText(expr), text


def read_expression(text):
    orig = text

    stack = []

    while len(text) > 0:
        #print "read_expression text: " + text
        space, text = re_match(' *', text)
        # don't care whether a space was read or not

        par, text = re_match('\(', text)
        if par is not None:
            stack.append(LeftPar())
            continue

        number, text = re_match('[0-9]+', text)
        if number is not None:
            # NOTE: assuming int for now. add more later.
            stack.append(ConstantText(int(number)))
            continue

        variable, text = read_dotted_name(text)
        if variable is not None:
            stack.append(variable)
            continue

        comma, text = re_match(',', text)
        if comma is not None:
            stack.append(Comma())
            continue

        operator, text = re_match(OPERATORS_PATTERN, text)
        if operator is not None:
            stack.append(Operator(operator))
            continue

        par, text = re_match('\)', text)
        if par is not None:
            # time to pop some stuff out
            text_node = build_text_node(stack)
            if text_node is not None:
                stack.append(text_node)
            continue

        colon, text = re_match(':', text)
        if colon is not None:
            text = ':' + text
            break

        space, text = re_match(' ', text)
        if space is not None:
            continue

        # some unknown thing
        return None, orig

    stack.insert(0, LeftPar())
    exps = build_text_node(stack)

    if len(exps) != 1:
        print "Exps should not be one"
        return None, orig

    expression = exps[0]
    #print "Built text node: {0}".format(expression)

    return expression, text
    # now lets try to do something with the stack.

def build_text_node(stack):
    tokens = []
    is_left_hit = False
    while len(stack) > 0:
        token = stack.pop()
        #print "build_text_node token: {}".format(token)
        if isinstance(token, LeftPar):
            is_left_hit = True
            break
        else:
            tokens.insert(0, token)

    if not is_left_hit:
        logging.debug("build_text_node stack: {0}".format(stack))
        raise Exception("Should have hit left parenthesis.")

    if len(tokens) == 0:
        return None

    # now go through tokens.
    expression_list = []
    while True:
        if len(tokens) == 0:
            break

        expression, tokens = build_simple_expression(tokens)
        if expression is not None:
            expression_list.append(expression)

        # any commas?
        if len(tokens) > 0:
            comma = tokens.pop(0)
            if not isinstance(comma, Comma):
                raise Exception("Tokens left but not comma: {0}".format(comma))

    return expression_list


def build_simple_expression(tokens):
    tokens_copy = copy.deepcopy(tokens)
    expression, left_tokens = build_simple_operation(tokens_copy)
    if expression is not None:
        return expression, left_tokens

    tokens_copy = copy.deepcopy(tokens)
    expression, left_tokens = build_simple_constant_or_variable(tokens_copy)
    if expression is not None:
            return expression, left_tokens
    return None, tokens


def list_pop(objects, index=None):
    if len(objects) == 0:
        return None
    if index is None:
        return objects.pop()
    else:
        return objects.pop(index)


def build_simple_operation(orig):
    tokens = copy.copy(orig)
    left_expression, tokens = build_simple_constant_or_variable(tokens)
    if left_expression is None:
        return None, orig

    op_terms = []
    while True:
        if len(tokens) < 1:
            if len(op_terms) > 0:
                break
            else:
                return None, orig

        operator = tokens.pop(0)
        if not isinstance(operator, Operator):
            return None, orig

        right_expression, tokens = build_simple_constant_or_variable(tokens)
        if right_expression is None:
            return None, orig

        op_terms.append((operator, right_expression))

    # now make expressions out of them.
    for (operator, right) in op_terms:
        left_expression = ExpressionText(operator, [left_expression, right])

    return left_expression, tokens


def build_simple_constant_or_variable(orig):
    tokens = copy.copy(orig)
    name = list_pop(tokens, 0)
    expression = None
    if isinstance(name, DottedName):
        # could be a function
        params = list_pop(tokens, 0)
        if isinstance(params, list):
            expression = ExpressionText(name, params)
        else:
            if params is not None:
                # put it back cuz we didn't consume it
                tokens.insert(0, params)
            expression = ExpressionText(name)
    elif isinstance(name, ConstantText):
        expression = ExpressionText(name)
    elif isinstance(name, list):
        if len(name) == 1:
            expression = name[0]
        else:
            logging.debug('child expression must be list')
            return None, orig
    else:
        logging.debug('not a constant or variable')
        return None, orig

    return expression, tokens


def read_dotted_name(orig):
    text = orig

    dest, text = re_match(VARIABLE_PATTERN, text)
    if dest is None:
        return None, orig

    tokens = [dest]

    while(True):
        token, text = re_match('.'+VARIABLE_PATTERN, text)
        if token is None:
            break
        else:
            token = token[1:] # token without period
            tokens.append(token)

    return DottedName(tokens), text


def read_statement(orig):
    '''
    StatementText example: counter = 5
    '''
    text = orig
    dotted_name, text = read_dotted_name(text)
    # try reading space
    space, text = re_match(' *', text)

    equ, text = re_match('=', text)
    if equ is None:
        return None, orig

    # either constant, variable, function call, or operation
   
    # try reading space
    space, text = re_match(' *', text)

    expression, text = read_expression(text)
    if expression != None:
        return StatementText([dotted_name], expression), text

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
    if outputs is None:
        return None, orig
    print outputs
    print ' text: ' + text
    # try reading space
    space, text = re_match(' ', text)
    if space is None:
        return None, orig

    function_name, text = re_match(VARIABLE_PATTERN, text)
    if function_name is None:
        return None, orig
    print 'function_name: ' + function_name + ' text: ' + text

    inputs, text = read_arguments_definition(text)
    if inputs is None:
        return None, orig
    print inputs
    print ' text: ' + text

    return FunctionText(function_name, inputs, outputs), text


def read_struct_definition(orig):
    text = orig
    struct_name, text = re_match(VARIABLE_PATTERN, text)
    if struct_name is None:
        return None, orig

    colon, text = re_match(':', text)
    if colon is None:
        return None, orig

    return StructText(struct_name), text

def read_arg_definition(orig):
    '''
    Read int continue
    Return Parameter()
    '''
    text = orig

    # type
    arg_type, text = re_match(VARIABLE_PATTERN, text)
    if arg_type is None:
        return None, orig

    # space
    space, text = re_match(' *', text)
    if space is None:
        return None, orig

    # name
    name, text = re_match(VARIABLE_PATTERN, text)
    if name is None:
        return None, orig
    var = Parameter(arg_type, name)
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
    par, text = re_match(' *\(', text)
    if par is None:
        return None, orig

    # arguments
    variables = []
    while True:
        # match type name
        var, text = read_arg_definition(text)
        if var != None:
            variables.append(var)

        # try reading comma
        com, text = re_match(',', text)
        if com is None:
            break

        # try reading space
        space, text = re_match(' ', text)
        if space is None:
            continue

    # see if ended
    par, text = re_match('\)', text)
    if par is None:
        return None, orig 
    return variables, text

def is_reserved(text):
    return text in RESERVED_WORDS


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


        block = self.stack[-1]

        if isinstance(block, StructText) and stack_index == 1:
            # struct members
            argument, line = read_arg_definition(line)
            if argument:
                logging.debug('struct arg read: {}'.format(argument))
                block.members.append(argument)
                return


        # conditional (if, elif, else, while)
        while_clause, line = read_while(line)
        if while_clause:
            print "while read: {0}".format(while_clause.get_dict())
            block.code.append(while_clause)
            self.stack.append(while_clause)
            return

        if_clause, line = read_if(line)
        if if_clause:
            print "if read: {0}".format(if_clause.get_dict())
            block.code.append(if_clause)
            self.stack.append(if_clause)
            return

        elif_clause, line = read_elif(line)
        if elif_clause:
            print "elif read: {0}".format(elif_clause.get_dict())
            block.code.append(elif_clause)
            self.stack.append(elif_clause)
            return

        else_clause, line = read_else(line)
        if else_clause:
            print "else read: {0}".format(else_clause.get_dict())
            block.code.append(else_clause)
            self.stack.append(else_clause)
            return

        # Could be function or struct definition
        if stack_index == 0:
            struct, line = read_struct_definition(line)
            if struct:
                print "struct_definition: {}".format(struct.get_dict())
                self.program.structs.append(struct)
                self.stack.append(struct)
                return

            function, line = read_function_definition(line)
            if function:
                print "function_definition: {0}".format(function.get_dict())
                self.program.functions.append(function)
                self.stack.append(function)
                return

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

        raise Exception("Something wrong bud")
