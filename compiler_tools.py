import json
import re
import string
import sys
from shared.common import get_bools
from settings import BAM_DIR
USHORT_SIZE = 16
# insns is a set of instructions.
class Instruction(object):
    def __init__(self, read_addr = 0, branch_to = 0, on_one = False, on_zero = False):
        '''
        if read is one, branch and set to on_one, else next insn and set to on_zero.
        '''
        self.read_addr = read_addr
        self.branch_to = branch_to
        self.on_one = on_one
        self.on_zero = on_zero


class Block(object):
    '''
    Represents a block of code (function and segmented block)
    '''
    def __init__(self, stack_pointer=0):
        self.stack_pointer = stack_pointer
        self.insns = []


class Builder(object):
    '''
    Instruction builder.
    '''
    
    def __init__(self, block=None):
        '''
        Memory size in bits.
        '''
        self.block = block


    def _new_insn(self, read_addr, branch_to, on_one, on_zero):
        i = Instruction(read_addr, branch_to, on_one, on_zero)
        self.block.insns.append(i)


    def write(self, addr, value):
        '''
        value is boolean
        '''
        num_insns = len(self.insns)
        self._new_insn(addr, num_insns, value, value) 


    def branch(self, read_addr, branch_to):
        '''
        if value at read_addr is 1, then go to branch_to.
        else, go to pc+1
        '''
        self._new_insn(read_addr, branch_to, True,False)


    def branch_short(self, addr, value, branch_to):
        '''
        if value at addr is value, then branch_to.
        else go to pc+1.
        '''
        # turn value into a bool array
        bools = get_bools(value, USHORT_SIZE)
        pc = len(self.builder.insns)
        for digit, binary in zip(addr, bools):
            self.branch(digit, pc+2)
            # digit is zero
            self.branch(binary, branch_to)
            self.branch(binary, pc+3)
            # digit is one
            self.branch(binary, pc+3)
            self.branch(binary, branch_to)
            pc = len(self.builder.insns)
        # reached end, 


    def new_short(self, value):
        # create on stack
        self.block.stack_pointer -= USHORT_SIZE
        self.store_short(self, self.stack_pointer, value)


    def store_short(self, addr, value):
        '''
        short is 16 bits long unsigned integer
        '''
        value_bools = get_bools(value, USHORT_SIZE)
        num_insns = len(self.insns)
        # convert value into bits
        for binary in value_bools:
            self._new_insn(addr, num_insns, binary, binary)
            num_insns += 1


    def copy_short(self, dest, src):
        num_insns = len(self.insns)
        for index in range(USHORT_SIZE):
            self.branch(src+index, num_insns+1)
            # src is zero
            self.write(dest+index, True)
            self.write(dest+index, False)
            # TODO: can make a loop rather than having insns be linaer to size.

    def add_short(self, result, one, two):
        '''
        result = one + two.
        '''
        carry_in = 0
        for index in range(USHORT_SIZE):
            self.add_bit(one+index, two+index, carry_in, carry_in, result+index)
        # TODO: All additions can probably be kept in one part of code. with temporary registers.

    def add_bit(self, one, two, carry_in, carry_out, result):
        '''
        parameters are addresses.
        truth table:

        one two carry
        '''
        pc = len(self.builder.insns)
        three = carry_in
        self.branch(one, pc+10)
        # one = 0
        self.branch(two, pc+10)
        # one = 0, two = 1
        self.branch(three, pc+10)
        # one = 0, two = 1, three = 1
        self.write(carry_out, 1)
        self.write(result, 0)
        # one = 0, two = 1, three = 0
        self.write(carry_out, 0)
        self.write(result, 1)
        # one = 0, two = 0
        self.branch(three, pc+10)
        # one = 0, two = 0, three = 1
        self.write(carry_out, 0)
        self.write(result, 1)
        # one = 0, two = 0, three = 0
        self.write(carry_out, 0)
        self.write(result, 0)

        # one = 1
        self.branch(two, pc+10)
        # one = 1, two = 1
        self.branch(carry_in, pc+10)
        # one = 1, two = 1, carry_in = 1
        self.write(carry_out, True)
        self.write(result, True)
        # one = 1, two = 1, carry_in = 0
        self.write(carry_out, True)
        self.write(result, False)
        # one = 1, two = 0
        self.branch(three, pc+10)
        # one = 1, two = 0, three = 1
        self.write(carry_out, 1)
        self.write(result, 0)
        # one = 1, two = 0, three = 0
        self.write(carry_out, 0)
        self.write(result, 1)


    def complement_short_i(self, dest, value):
        '''
        Return complement of value
        '''
        # convert value into bools
        bools = get_bools(value)
        for index, binary in enumerate(bools):
            self.write(index, not binary)


    def jump(jump_to):
        Instruction(0, jump_to, True, False)



class Type(object):
    '''
    Type
    '''
    types = ['int', 'double', 'string', 'list', 'dict']
    def __init__(self, name, size):
        self.size = 1 # 1 byte
        self.name = 'int'

#int_type = Variable('int', 4)
#double_type = Variable('double', 8)


class Variable(object):
    '''
    Type and name. Type can be primitive or defined from library.
    '''
    def __init__(self, arg_type, name):
        self.arg_type = arg_type
        self.name = name


class Function(object):

    def __init__(self, name, inputs=[], outputs=[]):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.code = []  # code is expressions and blocks

    def get_dict(self):
        return {
            'name': self.name,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'code': self.code,
        }


class Conditional(object):
    def __init__(self):
        pass

class While(object):
    def __init__(self):
        pass

class IfBlock(Conditional):
    def __init__(self):
        self.code = []

class ElIfBlock(Conditional):
    def __init__(self):
        self.code = []


class ElseBlock(Conditional):
    def __init__(self):
        self.code = []


class WhileBlock(Conditional):
    def __init__(self):
        self.code = []


class Statement(object):
    def __init__(self, expression):
        self.dest = Variable()
        self.expression = expression


class Expression(object):
    '''
    Function call node (could be nested)
    data is a function name or the variables/constant.
    arguments are also expression objects.
    '''
    def __init__(self, data, arguments=()):
        if type(arguments) != tuple:
            arguments = tuple(arguments)
        if type(data) != Operator:
            assert len(arguments) == 0

        #self.data = 'add'  # data is either function names or variables
        self.data = data
        self.arguments = arguments


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


class Program(object):
    def __init__(self, functions=[], structs=[]):
        self.functions = []
        self.structs = []
        self.counter = 0
        #main = get_function(functions, '__main__')
        #self.stack = [main]
        #self.index = 0


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
    pass


def read_statement(text):
    '''
    Statement example: counter = 5
    '''
    dest = read_name(text)
    read_equals(text)
    function_call = read_function_call(text)
    return Statement(Variable(dest), Expression(function_call))


def read_function_definition(text):
    '''
    ex1: (int current) fibonacci(int index):
    return None if not function
    '''
    print "text matching against: " + text
    outputs, text = read_arguments_definition(text)
    if outputs == None:
        return None, text
    print outputs
    print ' text: ' + text
    # try reading space
    space, text = re_match(' ', text)
    if space == None:
        return None, text

    function_name, text = re_match('[a-zA-z][a-zA-Z0-9]*', text)
    if function_name == None:
        return None, text
    print 'function_name: ' + function_name + ' text: ' + text
    inputs, text = read_arguments_definition(text)
    if inputs == None:
        return None, text
    print inputs
    print ' text: ' + text
        
    return Function(function_name, inputs, outputs), text


def read_arg_definition(text):
    '''
    Read int continue
    '''
    pattern = '[a-zA-z][a-zA-Z0-9]*'

    # type
    arg_type, text = re_match(pattern, text)
    if arg_type == None:
        return None, text

    print "arg_type: " + arg_type + " text: " + text
    # space
    space, text = re_match(' ', text)
    if space == None:
        return None, text
    print "soace: " + space+ " text: " + text

    # name
    name, text = re_match(pattern, text)
    if name == None:
        return None, text
    print "name: " + name+ " text: " + text
    var = Variable(arg_type, name)
    return var, text

def re_match(regex, text):
    m = re.match(regex, text)
    if m:
        return m.group(), text[m.end():]
    else:
        return None, text


def read_arguments_definition(text):
    '''
    (int a)
    ()
    (int a, string b)
    Either return list of Variable objects, or None
    '''

    # left paren
    par, text = re_match('\(', text)
    if par == None:
        return None, text

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
        return None, text
    print "par: " + par + " text: " + text
    return variables, text


def read_function_call(text):
    '''
    ex1: add(a,b)
    '''
    # read text
    # read any spaces
    regex = re.compile('(?<function_name>)[a-zA-z]+)\(arguments[a-zA-Z]+\)')
    match = regex.match(text)
    if not match:
        return None

    function_name = match.group('function_name')
    arguments = match.group('arguments')

    # only reads one level deep
    return Expression(function_name, arguments)


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
        main_function = Function("__main__", [],[])
        self.program = Program([main_function])
        self.lines = lines
        self.stack = [main_function]
        for line in self.lines:
            # syntax checker
            self.check(line)

    def check(self, line):
        # just read from beginning.
        line = line.rstrip()

        # how many spaces are in front?
        stack_index = get_stack_index(line)
        if stack_index < len(self.stack) - 1:
            num_pop = (len(self.stack) - 1) - stack_index
            while num_pop > 0:
                self.stack.pop()
        elif stack_index >= len(self.stack):
            raise Exception("spaced too much")

        # Function definition
        if stack_index == 0:
            function, line = read_function_definition(line)
            if function:
                print function.get_dict()
                self.program.functions.append(function)
                self.stack.push(function)
                return

        block = self.stack[-1]
        function_call = read_function_call(line)
        if function_call:
            block.code.append(function_call)
            return

        statement = read_statement(line)
        if  statement:
            block.code.append(statement)
            return

        # conditional (if, elif, else, while)
        if_clause = read_conditional(line)
        if if_clause:
            block.code.append(if_clause)
            self.stack.append(if_clause) 

        # read return, break

        raise Exception("Something wrong bud")

    #def read_function_call_old(text):
    #    # states:
    #    # INIT, NAME
    #    name_chars = []
    #    alpha = re.compile('[a-zA-Z]')
    #    numric = re.compile('[0-9]')
    #    state = 'INIT'  # initial state

    #    char = line.pop()
    #    if char == '(':
    #        if state == 'NAME':
    #            name_end()
    #    elif char == ')':
    #        if state == 'NAME':
    #            name_end()
    #    elif char == ',':
    #        pass
    #    elif char == ' ':
    #        # name ended
    #        if state == 'NAME':
    #            name_end()
    #    elif alpha.match(char):
    #        if state != 'NAME':
    #            name_chars = []
    #            state == 'NAME'
    #        # read name
    #        name_chars.push(char)

    #    elif numeric.match(char):
    #        name_chars.push(char)


    def read_operation(text):
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


class Semantics(object):
    '''
    '''
    def __init__(self, program):
        self.program = program
        
        # function names overlap?
        function_names = []
        for function in program.functions:
            if function.name in function_names:
                raise Exception("function: {0} exists".format(function.name))
            function_names.append(function_names)
            
            variables = []

            for input in function.inputs:
                variables.append(input)

            for output in function.outputs:
                variables.append(output)

            for block in function.code:
                b_type = type(block)
                if b_type == Expression:
                    # all functions must be defined, inputs properly defined.
                    pass
                    
                elif b_type == Statement:
                    # in addition to expression, outputs also properly defined.
                    pass
                elif b_type == Function:
                    # inner functions not allowed
                    pass
                elif b_type == Conditional:
                    # check variables are same type
                    pass


class Converter(object):
    '''
    Read objects and spit out bytecode.
    '''
    def __init__(self):
        self.memory_size = 4096
        self.block = Block()
        self.builder = Builder(self.block)
        self.vars = {}


    def spit(self):
        pass


    def spit_function(self, function):
        # print a single function
        self.vars = {}
        for input in function.inputs:
            vars[input] = self.builder.new_pointer()

        for output in function.outputs:
            vars[input] = self.builder.new_pointer()
        
        for block in function.code:
            b_type = type(block)
            if b_type == Expression:
                self.spit_expression(self, block)
            elif b_type == Statement:
                self.spit_statement(self,block)
            elif b_type == Function:
                self.spit_function(block)
            elif b_type == Conditional:
                self.spit_conditional(block)
            elif b_type == While:
                self.spit_while(block)

        # return statement
        self.builder.copy_short(self.vars['return'], self.vars['current'])

    def spit_expression(self, exp):
        # perform operation and store in temporary variable
        #self.builder.store_short(vars[exp.dest], exp.ex 
        pass

    def spit_statement(self, statement):
        self.builder.store_short(self.vars[statement.dest], statement.exp)

    def spit_while(self, while_block):
        # if condition met, enter loop, else exit.
        # must clear any unused variables after its done.
        loop_start = len(self.builder.insns)
        self.spit_condition(self.block.condition)
        self.builder.branch_short(self.vars['index'], 0, 1000)

        for block in while_block:
            self.spit_statement(block)

        # end loop
        self.builder.jump(loop_start)
        loop_end = len(self.builder.insns)
        # function conclusion
        self.builder.insns[loop_start].branch_to = loop_end


class Compiler(object):
    # TODO: should decide whether machine only runs
    # compiled code, real-time, or some combination.
    # 1. run parser with everything.
    # 2. run semantics and converter as needed.
    def __init__(self, text):
        self.lines = text.split('\n')
        self.parser = Parser(self.lines)
        self.semantics = Semantics(self.parser.program)
        self.converter = Converter(self.parser.program)

    def run(self):
        self.semantics.run()
        self.converter.run()


def test():
    # set memory to 4k
    #memory_size = 4096
    block = Block()
    insns = Builder(block)
    variables = {}

    f_vars = {}
    sys_vars = {}  # vars only used internally. not referenced by program.
    variables['fibonacci'] = f_vars

    # memory for return variable
    f_vars['return'] = insns.new_short()
    # memory for parameters
    f_vars['index'] = insns.new_short()
    # copy from parent variable to child
    insns.copy_short(f_vars['index'], variables['counter'])
    # entered function
    f_vars['last'] = insns.new_short()
    insns.store_short(f_vars['last'], 1)
    f_vars['current'] = insns.new_short()
    insns.store_short(f_vars['current'], 1)

    # while loop
    # if condition met, enter loop, else exit.
    # must clear any unused variables after its done.
    loop_start = len(insns.insns)
    insns.branch_short(f_vars['index'], 0, 1000)
    insns.add_short(f_vars['current'], f_vars['current'], f_vars['last'])
    sys_vars['complement'] = insns.new_short()
    insns.complement(sys_vars['complement'], 1)
    insns.add_short(f_vars['index'], f_vars['index'], sys_vars['complement'])
    insns.jump(loop_start)
    loop_end = len(insns.insns)

    # set the branch point
    insns.insns[loop_start].branch_to = loop_end
    # return statement
    insns.copy_short(f_vars['return'], f_vars['current'])


    # back in main function.
    variables['counter'] = insns.new_short()
    insns.store_short(variables['counter'], 5)
    variables['value'] = insns.new_short()
    insns.copy_short(variables['value'], f_vars['return'])


    # TODO: clean up after function complete. 
    #  save and jump to original insn after function complete.
    #  list the function insns first, then main line. jump in first insn.


if __name__ == '__main__':
    filename = sys.argv[1]
    #with open(BAM_DIR / filename) as f:
    with open(filename) as f:
        text = f.read()
        compiler = Compiler(text)
