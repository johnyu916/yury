import json
import copy
import re
import string
from shared.common import get_bools
from settings import BAM_DIR
USHORT_SIZE = 16
PRIMITIVE_TYPES = ['int', 'double', 'string', 'list', 'dict']
CONDITIONAL_WORDS = ['if', 'elif', 'else', 'while']
OPERATORS = ['==', '!=', '+', '-']
OPERATORS_PATTERN = '==|!=|\+|-'
RESERVED_WORDS = copy.copy(PRIMITIVE_TYPES)
RESERVED_WORDS.extend(CONDITIONAL_WORDS)
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
    def __init__(self, code=[]):
        self.code = code  # code is expressions and blocks

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

        codes = super(FunctionText, self).get_dict()

        this_dict = {
            'name': self.name,
            'inputs': inputs,
            'outputs': outputs
        }
        this_dict.update(codes)
        return this_dict


class ConditionalText(BlockText):
    def __init__(self, condition):
        self.condition = condition
        super(ConditionalText, self).__init__()

    def get_dict(self):
        codes = super(FunctionText, self).get_dict()
        return codes


class WhileText(ConditionalText):
    def __init__(self, expression):
        super(WhileText, self).__init__(expression)


    def get_dict(self):
        return {
            'expression': self.condition.get_dict()
        }


class IfBlock(ConditionalText):
    def __init__(self, expression):
        super(IfBlock, self).__init__(expression)

class ElIfBlock(ConditionalText):
    def __init__(self, expression):
        super(ElIfBlock, self).__init__(expression)


class ElseBlock(ConditionalText):
    def __init__(self, expression):
        super(ElseBlock, self).__init__(expression)


class StatementText(object):
    def __init__(self, dest, expression):
        '''
        a = add(3,5)
        dest is VariableText
        expression is ExpressionText
        '''
        self.dest = dest
        self.expression = expression

    def get_dict(self):
        return {
            'dest': self.dest.get_dict(),
            'expression': self.expression.get_dict()

        }


class ExpressionText(object):
    '''
    ExpressionText is a node that carries data.
    arguments can be ExpressionTexts or empty.
    data can be function name/operator (both string) or VariableText
    '''
    def __init__(self, data, children=()):
        if type(children) != tuple:
            children = tuple(children)
        if type(data) == VariableText:
            assert len(children) == 0

        #self.data = 'add'  # data is either function names or variables
        self.data = data
        self.children = children

    def get_dict(self):
        children = []
        for child in self.children:
            #print child
            children.append(child.get_dict())

        if type(self.data) == str:
            data = self.data
        else:
            data = self.data.get_dict()

        return {
            'data': data,
            'children':children
        }


class Operator(object):
    def __init__(self,operation):
        self.operation = operation
    def __str__(self):
        return self.operation


class OperationNode(object):
    '''
    The leaves are variables or immediates or functioncalls
    The parents are Operations
    '''
    def __init__(self, data, children=()):
        if type(children) != tuple:
            children = tuple(children)
        if type(data) != Operator:
            assert len(children) == 0

        self.data = data
        self.children = children

    def dictionary(self):
        data = self.data
        if type(self.data) == Operator:
            data = str(self.data)
        children = []
        for child in self.children:
            #print child
            children.append(child.dictionary())
        return {
            'data':data,
            'children':children
        }

    def __str__(self):
        return json.dumps(self.dictionary())


    def value():
        pass

def get_num_front_spaces(line):
    line2 = line.rstrip()
    line3 = line.strip()
    return len(line2) - len(line3)

def get_stack_index(line):
    num = get_num_front_spaces(line)
    if not (num % 4) == 0:
        raise Exception("Wrong number of spaces")
    return num/4


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

    def get_dict(self):
        functions = []
        for function in self.functions:
            functions.append(function.get_dict())
        structs = []
        for struct in self.structs:
            structs.append(struct.get_dict())

        return {
            'functions': functions,
            'structs': structs
        }


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


def read_conditional(text):
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
    if par == None:
        return None, orig

    # create while object
    return WhileText(expr), text


def read_expression(orig):
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
        return StatementText(dest_var, expression), text

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
        return VariableText('int', None, dest), text
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
    ex1: add(a,b)
    return (ExpressionText, text_left)
    return (None, arg_text) if not expression
    '''
    # read text
    # read any spaces
    orig = text
    pattern = '[a-zA-z][a-zA-Z0-9]*'
    function_name, text = re_match(pattern, text)
    if function_name == None:
        return None, orig

    par, text = re_match('\(', text)
    if par == None:
        return None, orig

    # one or more parameters
    params = []
    while True:
        # match type name
        name, text = re_match(pattern, text)
        if name != None:
            var = VariableText(None, name, None)
            params.append(ExpressionText(var))

        # try reading comma
        com, text = re_match(',', text)
        if com == None:
            break

        # try reading space
        space, text = re_match(' ', text)
        if space == None:
            continue

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

        print "Parser finished. Code: {0}".format(self.program.get_dict())


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

        # FunctionText definition
        if stack_index == 0:
            function, line = read_function_definition(line)
            if function:
                print "function_definition: {0}".format(function.get_dict())
                self.program.functions.append(function)
                self.stack.append(function)
                return

        block = self.stack[-1]

        statement, line = read_statement(line)
        if  statement:
            print "statement read: {0}".format(statement)
            block.code.append(statement)
            return

        expression, line = read_expression(line)
        if expression:
            print "expression read: {0}".format(expression)
            block.code.append(expression)
            return


        # conditional (if, elif, else, while)
        if_clause, line = read_conditional(line)
        if if_clause:
            print "conditional read: {0}".format(if_clause.get_dict())
            block.code.append(if_clause)
            self.stack.append(if_clause)
            return

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


