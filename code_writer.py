from code_semantics import Function, Expression, Statement, Conditional, Variable
from instruction import Translator
from shared.common import get_bools
USHORT_SIZE = 16


class Block(object):
    '''
    Represents a block of code (function and segmented block)
    '''
    def __init__(self):
        #self.sp_position = 0  # sp current position. Expressed from beginning (0).
        self.sp = 0 # position (initially at top).
        # self.function_calls = []  # list of  (insn_index, funtion_calling)

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
        self.blocks = []
        self.builder = Translator(4096)
        self.function_begin = {}  # record PC where functions begin.
        self.output_file_name = output_file_name
        self.program = program
        for function in program.functions:
            self.function_begin[function.name] = len(self.builder.insns)
            self.current_block = Block()
            self.blocks.append(self.current_block)
            self.spit_function(function)

        for index, name in function_calls:
            self.block.insns[index].jump_to = self.function_begin[name]

        # now convert all insns into
        self.write_insns(output_file_name)

    
    def write_insns(self, output_file_name):
        f = open(output_file_name, 'w')
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

    def spit_statement(self, variables, statement):
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
                variables.append(variable)
                

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

