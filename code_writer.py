from code_semantics import Function, Expression, Statement, Conditional, Variable
from instruction import load_insn
from shared.common import get_bools, get_object
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
        block.variables[variable.name] = variable
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
        self.sp_addr_reg = 1 # register that contains address of stack pointer
        self.sp_register = 2 # register that contains stack pointer value
        self.function_begin = {}  # which insn # does function begin?
        self.function_calls = []  # which function is being called where?
        self.output_file_name = output_file_name
        self.program = program

        # some special instructions.
    
        # set register 0 to stack pointer address
        self.builder.set_int(0, 0)
        self.builder.set_int(self.sp_addr_reg, self.sp_addr)

        for function in program.functions:
            self.function_begin[function.name] = len(self.insns)
            self.blocks.append(self.current_block)
            self.spit_function(function)

        for index, name in self.function_calls:
            self.insns[index].jump_to = self.function_begin[name]

        # now convert all insns into
        self.write_insns(output_file_name)


    def write_insns(self, output_file_name):
        f = open(output_file_name, 'w')
        for insn in self.insns:
            f.write(write_insn(insn))
        f.close()


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
        builder = self.builder
        block = Block()
        inputs = function.inputs
        outputs = function.outputs
        local_vars = function.local_variables


        return_pc = Variable(get_type('int'), 'return', 0)
        for input in outputs+inputs+[return_pc]+local_vars:
            block.new_variable(input)
        
        # load stack pointer
        self.builder.load(self.sp_register, self.sp_address_register)

        # 3 
        for chunk in function.code:
            b_type = type(chunk)
            if b_type == Expression:
                self.spit_expression(block, chunk)
            elif b_type == Statement:
                self.spit_statement(block, chunk)
            elif b_type == Conditional:
                self.spit_conditional(block, chunk)

        # return to some address.
        offset = variables['return']['offset']
        builder.set_int(3, offset)
        builder.subtract_int(4, 2, 3)
        builder.jump(4)

    def spit_expression(self, block, expression):
        '''
        perform whatever operation. the result should begin
        at the current sp_bottom.
        '''
        # perform operation and store in temporary variable
        #self.builder.store_short(vars[exp.dest], exp.ex
        # 1 level expression
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
                builder.store_int(4, var.value)  # immediate

        elif data_type == str:
            # has children, so run them first.
            for child in expression.children:
                self.spit_expression(block, child)

            # operator or string
            if data in OPERATORS:
                # operators return only one thing
                dest_offset = return_vars[0]['offset']
                self.set_offset_address(4, dest_offset, 3) # 4 has addr of dest_offset
                operand_one = self.set_offset_address(6, dest_offset-4, 5)
                operand_two = self.set_offset_address(8, dest_offset-8, 7)
                if data == '+':
                    builder.add_int(4, 6, 8)
                elif data == '-':
                    builder.subtract_int(4, 6, 8)
            else:
                # call function.
                self.call_function(block, data)
                #copy over output to return values
                operand_offset = block.offset
                for return_var in return_vars:
                    self.set_offset_address(4, return_var['offset'], 3)
                    self.set_offset_address(6, operand_offset, 5)
                    operand_offset += return_var.type.size

        # TODO: return block offset and free memory
    
    def set_offset_address(register, offset, worker_register):
        '''
        set offset to some register A
        set register B = sp - A
        
        '''
        builder.set_int(worker_register, offset)
        builder.subtract_int(register, self.sp_register, worker_register)

    def call_function(self, block, function_name):
        function = self.program.get_function(function_name)
        if not function:
            raise Exception("Unknown function name: {0}".format(function_name))


        # also add room to pass inputs and outputs
        # 1 add outputs to stack
        for output in function.outputs:
            self.new_variable(block, output)

        # 2 add inputs to stack
        for inpu in function.inputs:
            self.new_variable(block, inpu)

        # need to give return pc.
        ret_var = Variable('int', '__return__')
        ret_addr = self.new_variable(block, ret_var)
        self.builder.store_int(ret_addr, len(block.insns))
        # jump to function. temporarily 0, later set to funciton's beginning index.
        self.builder.jump(0)
        block.function_calls.append((len(block.insns), function_name))

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
        builder = self.builder
        dests = statement.destinations
        expression = statement.expression

        # find the destinations
        for dest in dests:
            variable = get_object(variables, dest.name)
            if not variable:
                block.new_variable(variable)


        #dest_addr = block.vars[dest.name]
        addrs = self.spit_expression(variables, expression)

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

