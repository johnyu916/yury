import struct

class InstructionOld(object):
    def __init__(self, read_addr = 0, branch_to = 0, on_one = False, on_zero = False):
        '''
        if read is one, branch and set to on_one, else next insn and set to on_zero.
        '''
        self.read_addr = read_addr
        self.branch_to = branch_to
        self.on_one = on_one
        self.on_zero = on_zero


'''
address is a 32-bit unsigned integer. 
byte addressing.
opcode is first byte of the instruction.
little-endian - for a multi-byte object (such as a 32-bit integer), least significant byte is stored in lowest memory location.
register 0 is 0
register 1 has the stack pointer's address

insn types:
load value_register address_register index
  value_register - 8-bit address where value will be loaded to.
  address_register - 8-bit address where the address is stored.
  index - 8-bit index

store value_register address_register index
  value_register - 8-bit address where value currently is.
  address_register - 8-bit address where the address is stored.
  index - 8-bit index

set register immediate
  register - 8-bit
  immediate - 16-bit

jump register
  register - 8-bit insn location (pc) to jump to.

branch register branch_to
  if value at register is 0, branch to pc.
  register - 8-bit address to read a byte 
  branch_to - 8-bit register contains insn to branch to.

add result one two
  add 2 32-bit integers
  result - 8-bit address of result
  one - 8-bit address of first operand
  two - 8-bit address of second operand.

subtract result one two
    result = one - two. 32-bit subtraction.
  result - 8-bit address of result
  one - 8-bit address of first operand.
  two - 8-bit address of second operand.

op codes: 8 bits long. longest parameters is a few of them (24-bit)
each instruction is 32-bits long.

use byte for opcode

'''
OPCODES = {
    'store': 0,
    'jump': 1,
    'move': 2,
    'branch': 3,
    'add': 4,
    'subtract': 5,
    'load': 6,
    'set': 7
}

def load_insn(value_register, address_register, index):
    return (
        OPCODES['load'],
        value_register,
        address_register,
        index
    )

def store_insn(value_register, address_register, index):
    return (
        OPCODES['store'],
        value_register,
        address_register,
        index
    )

def set_insn(value_register, immediate):
    return (
        OPCODES['set'],
        value_register,
        immediate
    )

def jump(register):
    return (
        OPCODES['jump'],
        register,
        0
    )

def move_deprecated(destination, source):
    return (
        OPCODES['move'],
        destination,
        source
    )

def branch(value_register, branch_register):
    return (
        OPCODES['branch'],
        value_register,
        branch_register
    )

def add_insn(result, one, two):
    return (
        OPCODES['add'],
        result,
        one,
        two
    )

def subtract_insn(result, one, two):
    return (
        OPCODES['subtract'],
        result,
        one,
        two
    )

def write_insn(insn):
    # 0 is opcode
    code = insn[0]
    if code == OPCODES['store']:
        text = stuff.pack('BBBB', *insn)
    elif code == OPCODES['jump']:
        text = stuff.pack('BBH', *insn)
    else:
        text = ''
    return text


class Translator(object):
    '''
    Primitive to real instruction.
    Instruction builder. It creates requested instructions.
    '''

    def __init__(self, sp_addr, insns):
        '''
        Memory size in bits.
        '''
        #self.block = block
        self.sp_addr = sp_addr
        self.insns = insns


    #def _new_insn(self, read_addr, branch_to, on_one, on_zero):
    #    i = Instruction(read_addr, branch_to, on_one, on_zero)
    #    self.block.insns.append(i)


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

    def store_int(self, dest_reg, value, free_reg):
        set_insn(free_reg, value)
        store_insn(free_reg, dest_reg)

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


    def copy(self, dest, src, size, free_reg):
        '''
        copy addr on src to addr on dest
        '''
        load_insn(val_reg, src, 0)
        store_insn(val_reg, dest, 0)

    def copy_short(self, dest, src):
        num_insns = len(self.insns)
        for index in range(USHORT_SIZE):
            self.branch(src+index, num_insns+1)
            # src is zero
            self.write(dest+index, True)
            self.write(dest+index, False)
            # TODO: can make a loop rather than having insns be linaer to size.

    def add_int(self, result, one, two):
        self.insn.append(add_insn(result,one,two))

    def add_short(self, result, one, two):
        '''
        result = one + two.
        '''
        carry_in = 0
        for index in range(USHORT_SIZE):
            self.add_bit(one+index, two+index, carry_in, carry_in, result+index)
        # TODO: All additions can probably be kept in one part of code. with temporary registers.


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


    def jump(address_with_value):
        Instruction(0, jump_to, True, False)

    def load(self, val_reg, addr_reg, imm=0):
        self.insn.append(load_insn(val_reg, addr_reg, imm))

    def set_int(self, register_no, value):
        self.insn.append(set_insn(register_no, value))

    def subtract_int(self, result, one, two):
        self.insn.append(subtract_insn(result,one,two))
