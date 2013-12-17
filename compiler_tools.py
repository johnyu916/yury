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


class Instructions(object):
    
    def __init__(self, memory_size):
        '''
        Memory size in bits.
        '''
        self.stack_pointer = memory_size
        self.pc = 0  # program counter. may not be very useful
        self.insns = []

    def _new_insn(read_addr, branch_to, on_one, on_zero)
        i = Instruction(read_addr, branch_to, on_one, on_zero)
        self.insns.append(i)
    
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
        Instruction(read_addr, branch_to, True,False)


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
        self.stack_pointer -= USHORT_SIZE
        self.store_short(self, self.stack_pointer, value)


    def new_short(self):
        self.stack_pointer -= USHORT_SIZE
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
        self.lines = text.split('\n')
        for line in self.lines:
            

def test():
    # set memory to 4k
    memory_size = 4096
    insns = Instructions(memory_size)
    variables = {}
    variables['counter'] = insns.new_short()

    f_vars = {}
    sys_vars = {}  # vars only used internally. not referenced by program.
    variables['fibonacci'] = f_vars
    f_vars['return'] = insns.new_short()
    f_vars['index'] = insns.new_short()
    insns.copy_short(f_vars['index'], variables['counter'])
    f_vars['last'] = insns.new_short()
    insns.store_short(f_vars['last'], 1)
    f_vars['current'] = insns.new_short()
    insns.store_short(f_vars['current'], 1)

    # while loop
    # if condition met, enter loop, else exit.
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
    insns.copy_short(f_vars['return'], f_vars['current'])

    variables['value'] = insns.new_short()
    insns.copy_short(variables['value'], f_vars['return'])

    # TODO: clean up after function complete. 
    #  save and jump to original insn after function complete.
    #  list the function insns first, then main line. jump in first insn.
