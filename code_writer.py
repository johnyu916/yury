from code_semantics import Expression, Statement, Variable, While, get_type
from parser import OPERATORS
from instruction import Translator, write_insn, write_ass
from shared.common import get_object
USHORT_SIZE = 16


class Block(object):
    '''
    Represents a block of code (function and segmented block)
    '''
    def __init__(self):
        #self.sp_position = 0  # sp current position. Expressed from beginning (0).
        self.offset = 0 # position (initially at top).
        self.variables = {}
        # self.function_calls = []  # list of  (insn_index, funtion_calling)
    def new_variable(self, variable):
        self.offset -= variable.type.size
        vari = {
            'variable': variable,
            'offset' : self.offset
        }
        self.variables[variable.name] = vari

    def get_variable(self, name):
        for _, variable in self.variables.iteritems():
            if variable['variable'].name == name:
                return variable
        return None

'''
Function stack:
output variables
input variables
return pc (32-bit)
'''

class Converter(object):
    '''
    Read objects and spit out bytecode.

    '''
    def __init__(self, program, hardware_config, output_file_name):
        '''
        '''
        self.memory_size = 4096
        self.insns = [] # instructions.
        self.builder = Translator(4096, self.insns)
        self.sp_addr = 1000 # address of stack pointer
        self.zero_register = 0
        self.sp_addr_register = 63 # register that contains address of stack pointer
        self.sp_register = 62 # register that contains stack pointer value
        self.pc_return_register = 61 # pc to return to after its done.
        self.sp_return_register = 60 # previous stack pointer value.
        self.function_begin = {}  # which insn # does function begin?
        self.function_calls = []  # which function is being called where?
        self.output_file_name = output_file_name
        self.program = program

        # some special instructions.
    
        # set register 0 to zero pointer
        self.builder.set_int(0, 0)
        # set stack pointer address register
        self.builder.set_int(self.sp_addr_register, self.sp_addr)
        self.builder.set_int(self.sp_register, self.memory_size)

        for function in program.functions:
            self.function_begin[function.name] = len(self.insns)
            self.spit_function(function)

        for index, name in self.function_calls:
            self.builder.jumpi_set(index, self.function_begin[name], 3)

        # now convert all insns into
        self.write_insns(output_file_name)


    def write_insns(self, output_file_name):
        assf = open(output_file_name + '.ass', 'w')
        binf = open(output_file_name + '.bin', 'w')
        for insn in self.insns:
            binf.write(write_insn(insn))
            assf.write(write_ass(insn))
        binf.close()
        assf.close()


    def spit_function(self, function):
        '''
        stack contains:
        1. outputs
        2. inputs
        3. return address
        '''
        # print a single function
        builder = self.builder
        block = Block()
        inputs = function.inputs
        outputs = function.outputs
        local_vars = function.local_variables


        return_pc = Variable(get_type('int'), 'return_pc', 0)
        for input in outputs+inputs+[return_pc]+local_vars:
            block.new_variable(input)

        # load stack pointer
        # self.builder.load(self.sp_register, self.sp_addr_register)

        # write code now
        self.write_code_block(block, function)

        # return to some address.
        offset = block.variables['return_pc']['offset']
        self.set_offset_address(4, offset, 3)
        builder.jump(4)

    def write_code_block(self, block, code_block):
        for chunk in code_block.code:
            b_type = type(chunk)
            if b_type == Expression:
                self.spit_expression(block, chunk)
            elif b_type == Statement:
                self.spit_statement(block, chunk)
            elif b_type == While:
                self.spit_while(block, chunk)


    def spit_expression(self, block, expression):
        '''
        perform whatever operation. at the end,
        block offset will be returned to what it was.
        '''
        # perform operation and store in temporary variable
        #self.builder.store_short(vars[exp.dest], exp.ex
        # 1 level expression
        print "spitting expression"
        return_types = expression.get_types()
        builder = self.builder
        return_vars = {}

        for count, return_type in enumerate(return_types):
            # make room for return value
            block.offset -= return_type.size
            return_var = {
                'variable': Variable(return_type, count, 0),
                'offset': block.offset
            }
            return_vars[count] = return_var


        data_type = type(expression.data)
        data = expression.data
        if data_type == Variable:
            # setting to constant or variable
            var = data
            dest_offset = return_vars[0]['offset']
            self.set_offset_address(4, dest_offset, 3) # 4 has addr of dest+offset
            if var.name != None:
                src_offset = block.variables[var.name]['offset']
                self.set_offset_address(6, src_offset, 5) # 6 has addr of src_offset 
                builder.copy(4, 6, var.type.size, 7)
            else:
                builder.store_inti(4, var.value, 5)  # immediate

        elif data_type == str:
            # has children, so run them first.
            for child in expression.children:
                self.spit_expression(block, child)

            # operator or string
            if data in OPERATORS:
                # operators return only one thing
                dest_offset = return_vars[0]['offset']
                self.set_offset_address(4, dest_offset, 3) # 4 has addr of dest_offset
                self.set_offset_address(6, dest_offset-4, 5) # operand one
                self.set_offset_address(8, dest_offset-8, 7) # operand two
                if data == '+':
                    builder.add_int(4, 6, 8)
                elif data == '-':
                    builder.subtract_int(4, 6, 8)
            else:
                # call function. before, set the 
                self.call_function(block, data)

                # call function changed the stack pointer, so change it back
                builder.add_inti(self.sp_register, self.sp_register, block.offset, 4)
                #copy over output to return values
                operand_offset = block.offset
                for count in range(len(return_types)):
                    return_var = return_vars[count]
                    self.set_offset_address(4, return_var['offset'], 3)
                    self.set_offset_address(6, operand_offset, 5)
                    operand_offset += return_var['variable'].type.size


        # TODO: return block offset and free memory

    def set_offset_address(self, register, offset, worker_register):
        '''
        set worker_register to offset.
        set register = sp - worker_register
        Offset is always <= 0.
        Convert to positive number and subtract.

        '''
        self.builder.set_int(worker_register, offset*-1)
        self.builder.subtract_int(register, self.sp_register, worker_register)

    def call_function(self, block, function_name):
        builder = self.builder
        function = self.program.get_function(function_name)
        if not function:
            raise Exception("Unknown function name: {0}".format(function_name))
        # save return register on stack
        self.set_offset_address(3, block.variables['return_pc']['offset'], 4)
        builder.store_int(self.pc_return_register, 3)
        
        # set stack pointer to offset
        builder.subtract_inti(self.sp_register, self.sp_register, block.offset, 3)

        # need to give return pc.
        builder.set_int(self.pc_return_register, len(self.insns))
        # jump to function. temporarily 0, later set to funciton's beginning index.
        self.builder.jumpi(0, 5)
        self.function_calls.append((len(self.insns), function_name))

        # variable setting and calling:
        # stack pointer is at top of function stack. 
        # keep a map of variable name to offset.
        # then add offset to sp and store in register ADDR.
        # set some value to another register VAL.
        # store VAL ADDR. 

    def spit_statement(self, block, statement):
        '''
        variables should contain all variables.
        '''
        print "spitting statement"
        builder = self.builder
        dests = statement.destinations
        expression = statement.expression

        # find the destinations
        for dest in dests:
            variable = block.get_variable(dest.name)
            if not variable:
                block.new_variable(variable)

        #dest_addr = block.vars[dest.name]
        self.spit_expression(block, expression)
        return_start = block.offset
        # copy addrs to destinations
        for dest in dests:
            self.set_offset_address(3, block.variables[dest.name]['offset'],4)
            self.set_offset_address(5, return_start,6)
            # 3 is the destination. 5 is the source.
            builder.load(7, 5)
            builder.store_int(3, 7)
            return_start += dest.type.size


    def spit_while(self, block, while_cond):
        # if condition met, enter loop, else exit.
        # must clear any unused variables after its done.
        loop_start = len(self.builder.insns)
        self.spit_expression(block, while_cond.condition)

        offset = block.offset - 1
        addr_reg = 3
        self.set_offset_address(addr_reg, offset, 4)
        value_reg = 5
        self.builder.load(value_reg, addr_reg)
        loop_end_index = len(self.builder.insns)
        self.builder.branch(value_reg, 0, 6)  # temporarily set to 0, later to loop_end

        self.write_code_block(block, while_cond)

        # end loop
        self.builder.jumpi(loop_start, 6)
        loop_end = len(self.builder.insns)
        # loop conclusion
        self.builder.branch_set(loop_end_index, value_reg, loop_end, 6)
        #self.builder.insns[loop_end_index].branch_to = loop_end


def test():
    # set memory to 4k
    #memory_size = 4096
    block = Block()
    insns = Translator(block)
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
    insns.jumpi(loop_start, 4)
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

