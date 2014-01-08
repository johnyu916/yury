from parser import Expression, Statement, Conditional, Variable
from shared.common import get_bools
USHORT_SIZE = 16

def size_of_type(type_str):
    if type_str == 'int':
        return 4
    return 0

class Instruction(object):
    def __init__(self, read_addr = 0, branch_to = 0, on_one = False, on_zero = False):
        '''
        if read is one, branch and set to on_one, else next insn and set to on_zero.
        '''
        self.read_addr = read_addr
        self.branch_to = branch_to
        self.on_one = on_one
        self.on_zero = on_zero



class Builder(object):
    '''
    Instruction builder. It creates requested instructions.
    '''

    #def __init__(self, block=None):
    def __init__(self, sp_addr):
        '''
        Memory size in bits.
        '''
        #self.block = block
        self.sp_addr = sp_addr


    def _new_insn(self, read_addr, branch_to, on_one, on_zero):
        i = Instruction(read_addr, branch_to, on_one, on_zero)
        self.block.insns.append(i)


    def write_int(self, addr, value):
        '''
        write value in address.
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
        # reached end


    def new_memory(self, size):
        # need to look at current stack pointer and bump it down.
        self.subtract_int(self.sp_addr, self.sp_addr, size)
        return self.sp_addr


    def new_short(self, value):
        # create on stack
        self.block.stack_pointer -= USHORT_SIZE
        self.store_short(self.stack_pointer, value)


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

    def subtract_int(self, result, one, two):
        '''
        result = one - two. parameters are all addrs.
        all locations are 32 bits.
        '''
        pass

    def subtract_inti(self, result, one, imm):
        '''
        result = one - imm. result and one are addrs, imm is a integer.
        '''

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


class Block(object):
    '''
    Represents a block of code (function and segmented block)
    '''
    def __init__(self, sp_addr=0):
        self.insns = []
        self.stack = []  # what's in the stack?
        self.sp_addr = sp_addr  # stack pointer's address.
        self.vars = {}


class Converter(object):
    '''
    Read objects and spit out bytecode.
    '''
    def __init__(self, program, hardware_config):
        '''

        '''
        self.memory_size = 4096
        self.blocks = []
        self.builder = Builder(self.memory_size)
        for function in program.functions:
            self.current_block = Block()
            self.blocks.append(self.current_block)
            self.spit_function(function)


    def spit(self):
        pass


    def spit_function(self, function):
        block = self.current_block
        # print a single function

        # 1 add inputs to stack
        for inpu in function.inputs:
            block.vars[inpu.name] = self.builder.new_memory(size_of_input(inpu.size))

        # 2 add outputs to stack
        for output in function.outputs:
            block.vars[output.name] = self.builder.new_memory(size_of_input(output.size))

        # 3 
        for chunk in function.code:
            b_type = type(chunk)
            if b_type == Expression:
                self.spit_expression(self, chunk)
            elif b_type == Statement:
                self.spit_statement(self, chunk)
            elif b_type == Conditional:
                self.spit_conditional(chunk)

        # return statement
        self.builder.copy_short(self.vars['return'], self.vars['current'])


    def spit_expression(self, exp):
        # perform operation and store in temporary variable
        #self.builder.store_short(vars[exp.dest], exp.ex
        # 1 level expression
        pass

    def spit_statement(self, statement):
        block = self.current_block
        builder = self.builder
        dest = statement.dest
        expression = statement.expression

        # find the
        if not dest in block.vars:
            block.vars[dest.name] = builder.new_memory(dest.type.size)

        dest_addr = block.vars[dest.name]
        
        if type(expression.data) == Variable:
            # setting to constant or variable
            var = expression.data
            if var.name != None:
                src_var = block.vars[var.name]
                builder.store_int(dest_addr, src_var)
            else:
                # int
                builder.store_inti(dest_addr, var.value)


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

