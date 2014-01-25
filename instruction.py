import logging
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
  value_register - 8-bit address of register that contains value.
  address_register - 8-bit address of register that contains address.
  index - 8-bit positive offset

store value_register address_register index
  value_register - 8-bit address of register that contains value.
  address_register - 8-bit address of register that contains address.
  index - 8-bit positive offset.

set register immediate
  register - 8-bit address of register.
  immediate - 16-bit positive offset.

jump register
  register - 8-bit address of register that contains insn location (pc) to jump to.

branch register branch_to
  if value at register is 0, branch to pc.
  register - 8-bit address of register that contains value
  branch_to - 8-bit address of register that contains pc to branch to.

add result one two
  add 2 32-bit integers
  result - 8-bit address of register that contains result
  one - 8-bit address of register that contains first operand
  two - 8-bit address of register that contains second operand.

subtract result one two
  result = one - two. 32-bit subtraction.
  result - 8-bit address of register that contains result
  one - 8-bit address of register that contains first operand.
  two - 8-bit address of register that contains second operand.

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

def load_insn(value_register, address_register, index=0):
    logging.debug('load_insn {0} {1}'.format(value_register, address_register, index))
    return (
        OPCODES['load'],
        value_register,
        address_register,
        index
    )

def store_insn(value_register, address_register, index=0):
    logging.debug('store_insn {0} {1}'.format(value_register, address_register, index))
    return (
        OPCODES['store'],
        value_register,
        address_register,
        index
    )

def set_insn(value_register, immediate):
    assert type(value_register) == int
    assert type(immediate) == int
    logging.debug('set_insn {0} {1}'.format(value_register, immediate))
    return (
        OPCODES['set'],
        value_register,
        immediate
    )

def jump_insn(register):
    logging.debug('jump_insn {0}'.format(register))
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

def branch_insn(value_register, branch_register):
    '''
    if value_register is 0, then branch to pc at branch_register
    '''
    logging.debug('branch_insn {0} {1}'.format(value_register, branch_register))
    return (
        OPCODES['branch'],
        value_register,
        branch_register,
        0
    )

def add_insn(result, one, two):
    logging.debug('add_insn {0} {1} {2}'.format(result, one, two))
    return (
        OPCODES['add'],
        result,
        one,
        two
    )

def subtract_insn(result, one, two):
    logging.debug('subtract_insn {0} {1} {2}'.format(result, one, two))
    return (
        OPCODES['subtract'],
        result,
        one,
        two
    )

base16_to_int = {
    0: '0',
    1: '1',
    2: '2',
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: 'a',
    11: 'b',
    12: 'c',
    13: 'd',
    14: 'e',
    15: 'f'
}

def get_two(integer):
    low = integer % 16
    high = integer >> 4
    return base16_to_int[low] + base16_to_int[high]

def get_base16(integer, size=1):
    if size == 1:
        # need two characters
        return get_two(integer)
    elif size == 2:
        first = integer % 256
        second = integer >> 8
        return get_two(first) + get_two(second)
    else:
        raise Exception("Can't handl this")


def get_insn_text(insn, sizes):
    '''
    opcode is in position 0.
    registers are next.
    if a value is more than a byte, then lower byte is first,
    then higher byte.
    '''
    print "texting insn: {0}".format(insn)
    text = ''
    for integer, size in zip(insn, sizes):
        text += get_base16(integer, size)
    return text

def write_ass(insn):
    # 0 is opcode
    code = insn[0]
    if code == OPCODES['store']:
        text = 'store {0} {1} {2}'.format(insn[1], insn[2], insn[3])
    elif code == OPCODES['jump']:
        text = 'jump {0}'.format(insn[1]) 
    elif code == OPCODES['branch']:
        text = 'branch {0} {1}'.format(insn[1], insn[2])
    elif code == OPCODES['add']:
        text = 'add {0} {1} {2}'.format(insn[1], insn[2], insn[3])
    elif code == OPCODES['subtract']:
        text = 'subtract {0} {1} {2}'.format(insn[1], insn[2], insn[3])
    elif code == OPCODES['load']:
        text = 'load {0} {1} {2}'.format(insn[1], insn[2], insn[3])
    elif code == OPCODES['set']:
        text = 'set {0} {1}'.format(insn[1], insn[2])
    else:
        raise Exception("Unknown instruction: {0}".format(code))
    print 'writing insn: ' + text
    return text + '\n'


def write_insn(insn):
    # 0 is opcode
    code = insn[0]
    sizes = [1,1,1,1]
    if code == OPCODES['store']:
        pass
    elif code == OPCODES['jump']:
        sizes = [1,1,2]
    elif code == OPCODES['branch']:
        pass
    elif code == OPCODES['add']:
        pass
    elif code == OPCODES['subtract']:
        pass
    elif code == OPCODES['load']:
        pass
    elif code == OPCODES['set']:
        sizes = [1,1,2]
    else:
        raise Exception("Unknown instruction: {0}".format(code))
    return get_insn_text(insn, sizes)


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


    def branch(self, value_reg, immediate, free_reg):
        '''
        if value at read_addr is 0, then go to pc at branch_to.
        else, go to pc+1
        '''
        self.set_int(free_reg, immediate)
        insn_two = branch_insn(value_reg, free_reg)
        self.insns.append(insn_two)


    def branch_set(self, insn_index, value_reg, immediate, free_reg):
        '''
        insn_index is beginning
        '''
        insn_one = set_insn(free_reg, immediate)
        insn_two = branch_insn(value_reg, free_reg)
        self.insns[insn_index] = insn_one
        self.insns[insn_index+1] = insn_two


    def new_memory_deprecated(self, size):
        # need to look at current stack pointer and bump it down.
        self.subtract_int(self.sp_addr, self.sp_addr, size)


    def load_int(self, val_reg, addr_reg, imm=0):
        '''

        '''
        self.insns.append(load_insn(val_reg, addr_reg, imm))

    def store_int(self, dest_reg, value_reg):
        '''
        Store value in value_reg to address in dest_reg
        '''
        insn = store_insn(value_reg, dest_reg)
        self.insns.append(insn)

    def store_inti(self, dest_reg, value, free_reg):
        insn = set_insn(free_reg, value)
        insn2 = store_insn(free_reg, dest_reg)
        self.insns.extend([insn, insn2])

    def copy(self, dest, src, size, free_reg):
        '''
        copy addr on src to addr on dest
        '''
        insn = load_insn(free_reg, src, 0)
        insn2 = store_insn(free_reg, dest, 0)
        self.insns.extend([insn, insn2])


    def add_int(self, result, one, two):
        self.insns.append(add_insn(result,one,two))

    def add_inti(self, result, one, imm, free_reg):
        self.set_int(free_reg, imm)
        self.add_int(result, one, free_reg)

    def subtract_inti(self, result, one, imm, free_reg):
        '''
        result = one - imm. result and one are addrs, imm is a integer.
        '''
        self.set_int(free_reg, imm)
        self.subtract_int(result, one, free_reg)

    def jump(self, value_reg):
        insn = jump_insn(value_reg)
        self.insns.append(insn)


    def jumpi(self, immediate, free_reg):
        self.set_int(free_reg, immediate)
        insn = jump_insn(free_reg)
        self.insns.append(insn)

    def jumpi_set(self, insn_index, immediate, free_reg):
        insn_one = set_insn(free_reg, immediate)
        insn_two = jump_insn(free_reg)
        self.insns[insn_index] = insn_one
        self.insns[insn_index+1] = insn_two

    def set_int(self, register_no, value):
        self.insns.append(set_insn(register_no, value))

    def subtract_int(self, result, one, two):
        self.insns.append(subtract_insn(result,one,two))
