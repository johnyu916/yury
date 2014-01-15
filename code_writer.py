from code_semantics import Function, Expression, Statement, Conditional, Variable
from shared.common import get_bools
USHORT_SIZE = 16


class Builder(object):
    '''
    Instruction builder. It creates requested instructions.
    '''

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
        if value at read_addr is 0, then go to branch_to.
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


    def copy(self, dest, src, size):
        pass

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
    def __init__(self):
        self.sp_position = 0  # sp current position. Expressed from beginning (0).
        self.sp_bottom = 0 # bottom of stack (initially at top).
        self.function_calls = []  # list of  (insn_index, funtion_calling)


class Converter(object):
    '''
    Read objects and spit out bytecode.
    '''
    def __init__(self, program, hardware_config, filename):
        '''

        '''
        self.memory_size = 4096
        self.insns = []
        self.blocks = []
        self.builder = Builder(4096)
        self.function_begin = {}
        self.filename = filename
        self.program = program
        for function in program.functions:
            self.function_begin[function.name] = len(self.builder.insns)
            self.current_block = Block()
            self.blocks.append(self.current_block)
            self.spit_function(function)

        for index, name in function_calls:
            self.block.insns[index].jump_to = self.function_begin[name]

        # now convert all insns into
        self.write_insns(filename)

    
    def write_insns(self, filename):
        f = open(filename, 'w')
        for insn in self.insns:
            f.write(write_insn(insn))
        f.close()


    def spit(self):
        pass


    def new_variable(self, block, variable):
        '''
        Return the sp_bottom
        '''
        size = variable.type.size
        self.builder.new_memory(size)
        block.sp_bottom -= size
        block.vars[variable.name] = block.sp_bottom
        return block.sp_bottom


    def spit_function(self, function):
        '''
        stack contains:
        1. outputs
        2. inputs
        '''
        # print a single function
        vars = {}

        # 3 
        for chunk in function.code:
            b_type = type(chunk)
            if b_type == Expression:
                self.spit_expression(vars, chunk)
            elif b_type == Statement:
                self.spit_statement(vars, chunk)
            elif b_type == Conditional:
                self.spit_conditional(vars, chunk)

        # return statement
        self.builder.copy_short(vars['return'], vars['current'])


    def spit_expression(self, vars, expression):
        '''
        perform whatever operation. the result should begin
        at the current sp_bottom.
        '''
        # perform operation and store in temporary variable
        #self.builder.store_short(vars[exp.dest], exp.ex
        # 1 level expression
        return_types = expression.get_types()
        builder = self.builder

        for return_type in return_types:
            # make room for return value
            self.new_variable(block, return_type)

        data_type = type(expression.data)
        data = expression.data
        if data_type == Variable:
            # setting to constant or variable
            var = data
            dest_addr = block.vars[return_types[0].name]
            if var.name != None:
                src_addr = block.vars[var.name]
                builder.copy(dest_addr, src_addr)
            else:
                builder.store_inti(dest_addr, var.value)
        elif data_type == str:
            # has children, so run them first.
            addrs = []
            for child in expression.children:
                addrs.append(self.spit_expression(block, child))
            # operator or string
            if data in OPERATORS:
                # operators return only one thing
                dest_addr = block.vars[return_types[0].name]
                if data == '+':
                    builder.add_int(dest_addr, addrs[0], addrs[1])
                elif data == '-':
                    builder.subtract_int(dest_addr, addrs[0], addrs[1])
            else:
                # call function.
                self.call_function(block, data)
                #copy over output to return values
                for return_type in return_types:
                    self.copy(block.var[return_type[0].name], block.sp_position)
        return addrs


    def call_function(self, block, function_name):
        function = self.program.get_function(function_name)
        if not function:
            raise Exception("Unknown function name: {0}".format(function_name))

        # need to give return address
        ret_var = Variable('int', '__return__')
        ret_addr = self.new_variable(block, ret_var)
        self.builder.store_int(ret_addr, len(block.insns))

        # also add room to pass inputs and outputs
        # 1 add outputs to stack
        for output in function.outputs:
            self.new_variable(block, output)

        # 2 add inputs to stack
        for inpu in function.inputs:
            self.new_variable(block, inpu)

        # jump to function. temporarily 0, later set to funciton's beginning index.
        self.builder.jump(0)
        block.function_calls.append((len(block.insns), function_name))



    def spit_statement(self, statement):
        block = self.current_block
        builder = self.builder
        dests = statement.destinations
        expression = statement.expression

        # find the destinations
        for dest in dests:
            if not dest in block.vars:
                self.new_variable(block, dest)

        #dest_addr = block.vars[dest.name]
        addrs = self.spit_expression(self, expression)

        # copy addrs to destinations


    def spit_while(self, while_block):
        # if condition met, enter loop, else exit.
        # must clear any unused variables after its done.
        loop_start = len(self.builder.insns)
        addr = self.spit_expression(self.block.condition)
        loop_end_index = len(self.builder.insns)
        self.builder.branch(addr, 0)  # temporarily set to 0, later to loop_end

        for block in while_block:
            self.spit_statement(block)

        # end loop
        self.builder.jump(loop_start)
        loop_end = len(self.builder.insns)
        # loop conclusion
        self.builder.insns[loop_end_index].branch_to = loop_end


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

