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


    def _new_insn(read_addr, branch_to, on_one, on_zero)
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
        for digit, binary in zip(addr, bools):
            self.branch(digit, pc+2)
            # digit is zero
            self.branch(binary, branch_to)
            self.branch(binary, pc+3)
            # digit is one
            self.branch(binary, pc+3)
            self.branch(binary, branch_to)
        # reached end, 


    def new_short(self, value):
        # create on stack
        self.block.stack_pointer -= USHORT_SIZE
        self.store_short(self, self.stack_pointer, value)


    def new_short(self):
        self.block.stack_pointer -= USHORT_SIZE
        return self.stack_pointer


    def store_short(self, addr, value):
        '''
        short is 16 bits long unsigned integer
        '''
        value_bools = get_bools(integer, USHORT_SIZE)
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
        for index range(USHORT_SIZE):
            self.add_bit(one+indx, two+index, carry_in, carry_in, result+index)
        # TODO: All additions can probably be kept in one part of code. with temporary registers.

    def add_bit(self, one, two, carry_in, carry_out, result):
        '''
        parameters are addresses.
        truth table:

        one two carry
        '''
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


class Parser(object):
    # parse program text.
    def __init__(self, text):
        self.variables = []
        self.functions = []
        self.block = Block()
        self.lines = text.split('\n')
        for line in self.lines:
            # syntax checker
            self.check(line)
    
    def check(self, line):
        # just read from beginning.
        line = line.rstrip()

        # Function definition
        is_read = read_function_definition(line)
        if is_read:
            return

        is_read = read_statement(line)

        if is_read:
            return

        is_read = read_function_call(line)

        if is_read:
            return

        # hmm boing

    def is_function_name(name):
        for function in self.functions:
            if function == name:
                return True
        return False

    def is_var_name(name):
        for var in self.variables:
            if var == name:
                return True
        return False

    def name_end('='):
        name = string.join(name_chars, '')
        # is name a function call? variable?
        if self.is_function_name(name):
            state = 'FUNCTION'
        elif self.is_var_name(name):
            state = 'VAR'
        else:
            raise Exception("unknown name")

    def read_function_definition(line):
        '''
        ex1: (int current) fibonacci(int index):
        '''

    def read_function_call(text):
        '''
        ex1: add(a,b)
        '''
        # read text
        # read any spaces
        name = read_name(text)
        if not is_function_name(name):
            raise Exception("Unknown function: {0}".format(name))
        char = text.pop(0)
        assert char == '('
        name = read_name(text)
        if not is_variable_name(name):
            raise Exception("Unknown variable: {1}".format(name))
        assert char == ')'


    def read_name(text):
        name_chars = []
        text.strip(' ')  # strip beginning spaces
        while True:
            char = text.pop()
            alpha = re.compile('[a-zA-Z]')
            numeric = re.compile('[0-9]')
            if alpha.match(char):
                name_chars.append(char)
            elif alpha.match(char):
                name_chars.append(char)
            else:
                return string.join(name_chars, '')

    def read_statement(text):
        '''
        Statement example: counter = 5
        '''
        [dest, exp] = line.split('=')
        read_name(dest)
        read_function_call(exp)


    def read_function_call_old(text):
        # states:
        # INIT, NAME
        name_chars = []
        alpha = re.compile('[a-zA-Z]')
        numric = re.compile('[0-9]')
        state = 'INIT'  # initial state

        char = line.pop()
        if char == '(':
            if state == 'NAME':
                name_end()
        elif char == ')':
            if state == 'NAME':
                name_end()
        elif char == ',':
        elif char == ' ':
            # name ended
            if state == 'NAME':
                name_end()
        elif alpha.match(char):
            if state != 'NAME':
                name_chars = []
                state == 'NAME'
            # read name
            name_chars.push(char)

        elif numeric.match(char):
            name_chars.push(char)



    def read_operation(text):
        operators = ['+', '-', '*', '/', '%']
        stack = []
        for char in line:
            if char == '(':
                pass
            elif char == ')':
                pass
            elif char == ' ':
                pass
            elif char in operators:
                # needs an operand
                pass


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

        else:
            if data == NOT:
                assert len(children) == 1
            else:
                assert len(children) > 1

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


    def permutations(self):
        '''
        Return all permutations of the current Operation Node tree
        '''
        trees = []
        operation_node_permutations(self, trees)
        return trees

    def value():
        pass



def test():
    # set memory to 4k
    memory_size = 4096
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
