import logging

from code_semantics import Constant, Expression, Statement, Variable, While, If, ElIf, Else, get_type, get_dotted_type
from parser import OPERATORS, DottedName
from instruction import Translator, write_insn, write_ass, INSN_SIZE
from shared.common import get_object
USHORT_SIZE = 16


class BlockStack(object):
    '''
    Data structure for a block of code
    '''
    def __init__(self):
        self.offset = 0 # position (initially at top).
        self.variables = []

    def new_variable(self, variable):
        logging.debug("variable: {} size: {}".format(variable.name, variable.type.size))
        self.offset -= variable.type.size
        vari = {
            'variable': variable,
            'offset' : self.offset
        }
        self.variables.append(vari)

    def pop_variable(self):
        # remove from the end
        variable_dict = self.variables.pop()
        self.offset += variable_dict['variable'].type.size

    def get_variable(self, dotted_name):
        if len(dotted_name.tokens) == 0: return None
        token = dotted_name.tokens[0]
        print "token: ",token
        for variable_dict in self.variables:
            print "get_variable name: ", variable_dict['variable'].name
            if variable_dict['variable'].name == token:
                return variable_dict
        return None

def get_size(dotted_name, block_stack, structs):
    variable_dict = block_stack.get_variable(dest)
    variable = variable_dict['variable']
    type = get_dotted_type(dotted_name.tokens, variable.type, structs)
    return type.size

def get_offset(tokens, first_type, offset=0):
    if len(tokens) == 0:
        raise Exception("Can't get type of empty tokens")

    if len(tokens) == 1:
        return offset

    next_token = tokens[1]
    (member, member_offset) = first_type.get_member_offset(next_token)

    return get_offset(tokens[1:], member.type, offset + member_offset)

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
        self.function_begin = {}  # which insn # does function begin?
        self.function_calls = []  # which function is being called where?
        self.output_file_name = output_file_name
        self.program = program

        # some special instructions.

        # set register 0 to zero pointer
        self.builder.set_int(self.zero_register, 0)
        # set stack pointer address register
        self.builder.set_int(self.sp_addr_register, self.sp_addr)
        self.builder.set_int(self.sp_register, self.memory_size)
        self.builder.set_int(self.pc_return_register, 0)

        for function in program.functions:
            self.function_begin[function.name] = len(self.insns)
            self.spit_function(function)

        for index, name in self.function_calls:
            self.builder.jump_and_link_set(index, immediate=self.function_begin[name]*4)

        # now convert all insns into
        self.write_insns(output_file_name)


    def write_insns(self, output_file_name):
        def function_key(item):
            return item[0]
        functions = [(number, name) for name, number in self.function_begin.iteritems()]
        functions.sort(key=function_key)

        current_no, current_name = functions.pop(0)
        assf = open(output_file_name + '.ass', 'w')
        binf = open(output_file_name + '.bin', 'w')
        for index, insn in enumerate(self.insns):
            binf.write(write_insn(insn))
            if index == current_no:
                text = current_name + ": "
                if len(functions) > 0:
                    current_no, current_name = functions.pop(0)
            else:
                text = ""
            assf.write(text + write_ass(insn))
        binf.close()
        assf.close()


    def spit_function(self, function):
        '''
        stack contains:
        1. outputs
        2. inputs
        3. return address
        '''
        logging.debug("spitting function: {0}".format(function.name))
        # print a single function
        builder = self.builder
        block_stack = BlockStack()
        inputs = function.inputs
        outputs = function.outputs
        local_vars = function.local_variables

        return_pc = Variable(get_type('int'), 'return_pc')
        for input in outputs+inputs+[return_pc]+local_vars:
            block_stack.new_variable(input)

        # load stack pointer
        # self.builder.load(self.sp_register, self.sp_addr_register)

        # write code now
        self.write_code_block(block_stack, function)

        # return to some address.
        #offset = block.variables['return_pc']['offset']
        #self.set_offset_address(4, offset, 3)
        builder.jump(self.pc_return_register)
        logging.debug("spitting function done: {0}".format(function.name))

    def write_code_block(self, block_stack, code_block):
        for chunk in code_block.code:
            if isinstance(chunk, Expression):
                self.spit_expression(block_stack, chunk)
            elif isinstance(chunk, Statement):
                self.spit_statement(block_stack, chunk)
            elif isinstance(chunk, While):
                self.spit_while(block_stack, chunk)
            elif isinstance(chunk, If):
                self.spit_if(block_stack, chunk)
            elif isinstance(chunk, ElIf):
                self.spit_elif(block_stack, chunk)
            elif isinstance(chunk, Else):
                self.spit_else(block_stack, chunk)
            else:
                raise Exception("Don't know what to do with: ", chunk)



    def spit_expression(self, block_stack, expression):
        '''
        Allocates space for return types.
        Perform the operation. at the end,
        block offset will be returned to what it was.
        After finish,
        The "return value" starts just below the block offset.
        '''
        # perform operation and store in temporary variable
        #self.builder.store_short(vars[exp.dest], exp.ex
        # 1 level expression
        logging.debug("spitting expression: {0}".format(expression))
        return_types = expression.get_types()
        builder = self.builder
        return_vars = {}
        block_begin_offset = block_stack.offset

        for count, return_type in enumerate(return_types):
            # make room for return value
            block_stack.offset -= return_type.size
            return_var = {
                'variable': Variable(return_type, count),
                'offset': block_stack.offset
            }
            return_vars[count] = return_var

        data = expression.data
        if isinstance(data, Constant):
            # setting to constant or variable
            dest_offset = return_vars[0]['offset']
            self.set_offset_address(4, dest_offset, 3) # 4 has addr of dest+offset
            # constant. store to 4 (destination)
            # TODO: currently only handle integers
            builder.store_inti(4, data.value, 5)  # immediate

        elif isinstance(data, DottedName):
            # first get the source address
            variable_dict = block_stack.get_variable(data)
            variable_offset = variable_dict['offset']
            member_offset = get_offset(data.tokens, variable_dict['variable'].type)
            src_offset = variable_offset + member_offset
            var_size = get_dotted_type(data.tokens, variable_dict['variable'].type).size
            self.set_offset_address(6, src_offset, 5) # 6 has addr of src_offset

            # now get destination offset
            dest_offset = return_vars[0]['offset']
            self.set_offset_address(4, dest_offset, 3) # 4 has addr of dest+offset
            # copy from 6 to 4.
            builder.copy(4, 6, var_size, 7)

        elif isinstance(data, str):
            # has children.
            # if necessary, allocate additional space for intermediary.
            # so run them first.
            children = expression.children
            for child in children:
                self.spit_expression(block_stack, child)
                # need to save the child somewhere.
                child_return_types = child.get_types()
                for child_type in child_return_types:
                    block_stack.offset -= child_type.size

            # operator or string
            if data in OPERATORS:
                if len(return_vars) != 1:
                    raise Exception("operation returns 1 value, but returns: {0}".format(len(return_vars)))
                # operators return only one thing. assume 2 return values.
                dest_offset = return_vars[0]['offset']
                operand_one_size = children[0].get_types()[0].size
                operand_two_size = children[1].get_types()[0].size
                self.set_offset_address(4, dest_offset, 3) # 4 has addr of dest_offset
                self.set_offset_address(5, dest_offset-operand_one_size, 3) # 5 has address of operand one
                self.set_offset_address(6, dest_offset - operand_one_size - operand_two_size, 3) # 6 has address of operand two

                builder.load_int(8, 5)
                builder.load_int(9, 6)
                if data == '+':
                    builder.add_int(7, 8, 9)
                    builder.store_int(4, 7) # store result in 4
                elif data == '-':
                    builder.subtract_int(7,8,9)
                    builder.store_int(4, 7) # store result in 4
                elif data == '!=':
                    builder.set_on_ne(7,8,9, 10, 11)
                    builder.store_byte(4, 7) # store result in 4
                elif data == '==':
                    builder.set_on_e(7,8,9, 10, 11)
                    builder.store_byte(4, 7) # store result in 4

            elif self.program.get_struct(data) is not None:

                # a struct constructor. then we don't need to do anything
                pass
            else:
                # call function. Note we already allocated space for the 
                # output (return_vars) and input (child_return_types).
                # save return register on stack, because the child is going to use it now.
                dotted_name= DottedName(['return_pc'])
                return_pc_offset = block_stack.get_variable(dotted_name)['offset']
                self.set_offset_address(3, return_pc_offset, 4)
                builder.store_int(3, self.pc_return_register)

                # set stack pointer to offset
                builder.subtract_inti(self.sp_register, self.sp_register, block_begin_offset *-1, 3)
                self.call_function(data)

                # call function changed the stack pointer, so change it back
                builder.add_inti(self.sp_register, self.sp_register, block_begin_offset * -1, 4)
                # set return address back to return register
                self.set_offset_address(3, return_pc_offset, 4)
                builder.load_int(self.pc_return_register, 3)


        block_stack.offset = block_begin_offset
        logging.debug("spitting expression done")

    def set_offset_address(self, register, offset, worker_register):
        '''
        set worker_register to offset.
        set register = sp - worker_register
        Offset is always <= 0.
        Convert to positive number and subtract.

        '''
        assert offset <= 0
        self.builder.set_int(worker_register, offset*-1)
        self.builder.subtract_int(register, self.sp_register, worker_register)

    def call_function(self, function_name):
        builder = self.builder
        function = self.program.get_function(function_name)
        if not function:
            raise Exception("Unknown function name: {0}".format(function_name))

        self.function_calls.append((len(self.insns), function_name))
        # need to give return pc and jump
        builder.jump_and_link(0, self.pc_return_register, 5)

        # variable setting and calling:
        # stack pointer is at top of function stack. 
        # keep a map of variable name to offset.
        # then add offset to sp and store in register ADDR.
        # set some value to another register VAL.
        # store VAL ADDR. 

    def spit_statement(self, block_stack, statement):
        '''
        Destinations should already be in the stack, so does not
        allocate additional memory (but expressions inside
        probably will use the stack).
        After expression is done, memory is copied from the 
        return values to the destinations.
        '''
        logging.debug("spitting statement: {0}".format(statement))
        builder = self.builder
        destinations = statement.destinations
        expression = statement.expression

        # find the destinations
        for dest in destinations:
            variable = block_stack.get_variable(dest)['variable']
            if not variable:
                raise Exception("didn't find variable %s" % dest)

        self.spit_expression(block_stack, expression)
        return_start = block_stack.offset
        # copy addrs to destinations
        for dest in destinations:
            variable_dict = block_stack.get_variable(dest)
            variable = variable_dict['variable']
            dest_size = get_dotted_type(dest.tokens, variable.type).size
            dest_offset = get_offset(dest.tokens, variable.type, variable_dict['offset'])
            logging.debug("var_offset: {} offset with member: {}".format(variable_dict['offset'], dest_offset))
            return_start -= dest_size

            self.set_offset_address(3, dest_offset,4)
            self.set_offset_address(5, return_start,6)
            #copy. 3 is the destination. 5 is the source.
            builder.copy(3, 5, dest_size, 7)

        logging.debug("spitting statement done. block.offset: %s" % block_stack.offset)

    def _load_condition_result(self, block_stack):
        offset = block_stack.offset - 1
        addr_reg = 3
        self.set_offset_address(addr_reg, offset, 4)
        value_reg = 5
        self.builder.load_byte(value_reg, addr_reg)

    def spit_while(self, block_stack, while_cond):
        # if condition met, enter loop, else exit.
        # must clear any unused variables after its done.
        logging.debug("spitting while: {0}".format(while_cond.condition))
        loop_start = len(self.builder.insns)
        self.spit_expression(block_stack, while_cond.condition)

        self._load_condition_result(block_stack)
        loop_end_index = len(self.builder.insns)

        # if condition doesn't hold, exit.
        self.builder.branch_on_z_imm(5, 0, 6)  # temporarily set to 0, later to loop_end

        self.write_code_block(block_stack, while_cond)

        # end loop
        self.builder.jumpi(loop_start*4, 6)
        loop_end = len(self.builder.insns)
        # loop conclusion
        self.builder.branch_on_z_imm_set(loop_end_index, value_reg=None, immediate=loop_end*4, free_reg=None)
        #self.builder.insns[loop_end_index].branch_to = loop_end
        logging.debug("spitting while done")

    def spit_if(self, block_stack, if_cond):
        for variable in if_cond.variables:
            block_stack.new_variable(variable)

        self.spit_expression(block_stack, if_cond.condition)

        # load result of expression into reg 5
        self._load_condition_result(block_stack)

        # branch to next guy
        branch_index = len(self.builder.insns)
        self.builder.branch_on_z_imm(5, 0, 6)

        self.write_code_block(block_stack, if_cond)
        block_end = len(self.builder.insns)
        self.builder.branch_on_z_imm_set(branch_index, value_reg=None, immediate=block_end*4, free_reg=None)

        # pop stack
        for _ in if_cond.variables:
            block_stack.pop_variable()

    def spit_elif(self, block_stack, elif_cond):
        self.spit_if(block_stack, elif_cond)

    def spit_else(self, block_stack, else_cond):
        for variable in else_cond.variables:
            block_stack.new_variable(variable)
        self.write_code_block(block_stack, else_cond)
        for _ in else_cond.variables:
            block_stack.pop_variable()
