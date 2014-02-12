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
load_word value_register address_register index
  value_register - 8-bit address of register that contains value.
  address_register - 8-bit address of register that contains address.
  index - 8-bit positive offset

store_word value_register address_register index
    store 4 bytes of data starting from address. 
  value_register - 8-bit address of register that contains value.
  address_register - 8-bit address of register that contains address.
  index - 8-bit positive offset.

store_byte value_register address_register index
    store 1 byte of data. lowest byte of value_register. starting from address.
  value_register - 8-bit address of register that contains value.
  address_register - 8-bit address of register that contains address.
  index - 8-bit positive offset.

load_byte value_register address_register index
    load 1 byte of data. lowest byte of value_register. starting from address.
  value_register - 8-bit address of register that contains value.
  address_register - 8-bit address of register that contains address.
  index - 8-bit positive offset.

set register immediate
  register - 8-bit address of register.
  immediate - 16-bit positive offset.

jump register
  register - 8-bit address of register that contains insn location (pc) to jump to.

branch_on_z register branch_to
  if value at register is 0, branch to pc.
  register - 8-bit address of register that contains value
  branch_to - 8-bit address of register that contains pc to branch to.

branch_on_ltz register branch_to
  if value at register is less than 0, branch to pc.
  register - 8-bit address of register that contains value
  branch_to - 8-bit address of register that contains pc to branch to.

add result one two
  add 2 32-bit signed integers
  result - 8-bit address of register that contains result
  one - 8-bit address of register that contains first operand
  two - 8-bit address of register that contains second operand.

subtract result one two
  result = one - two. 32-bit signed integer subtract.
  result - 8-bit address of register that contains result
  one - 8-bit address of register that contains first operand.
  two - 8-bit address of register that contains second operand.

multiply result one two
  result = one - two. 32-bit signed integer multiplication.
  result - 8-bit address of register that contains result
  one - 8-bit address of register that contains first operand.
  two - 8-bit address of register that contains second operand.

op codes: 8 bits long. longest parameters is a few of them (24-bit)
each instruction is 32-bits long.

use byte for opcode

'''
OPCODES = {
    'store_word': 0,
    'jump': 1,
    'move': 2,
    'branch_on_z': 3,
    'add': 4,
    'subtract': 5,
    'load_word': 6,
    'set': 7,
    'branch_on_ltz': 8,
    'store_byte': 9,
    'load_byte': 10,
    'multiply': 11,
}

INSN_SIZE = 4 # in bytes
def load_word_insn(value_register, address_register, index=0):
    logging.debug('load_word_insn {0} {1}'.format(value_register, address_register, index))
    return (
        OPCODES['load_word'],
        value_register,
        address_register,
        index
    )

def store_word_insn(value_register, address_register, index=0):
    logging.debug('store_word_insn {0} {1}'.format(value_register, address_register, index))
    return (
        OPCODES['store_word'],
        value_register,
        address_register,
        index
    )

def store_byte_insn(value_register, address_register, index=0):
    logging.debug('store_byte_insn {0} {1}'.format(value_register, address_register, index))
    return (
        OPCODES['store_byte'],
        value_register,
        address_register,
        index
    )

def load_byte_insn(value_register, address_register, index=0):
    logging.debug('load_byte_insn {0} {1}'.format(value_register, address_register, index))
    return (
        OPCODES['load_byte'],
        value_register,
        address_register,
        index
    )

def set_insn(register_no, immediate):
    assert type(register_no) == int
    assert type(immediate) == int
    logging.debug('set_insn {0} {1}'.format(register_no, immediate))
    return (
        OPCODES['set'],
        register_no,
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

def branch_on_z_insn(value_register, branch_register):
    '''
    if value_register is 0, then branch to pc at branch_register
    '''
    logging.debug('branch_on_z_insn {0} {1}'.format(value_register, branch_register))
    return (
        OPCODES['branch_on_z'],
        value_register,
        branch_register,
        0
    )

def branch_on_ltz_insn(value_register, branch_register):
    '''
    if value_register is less than zero, then branch to pc at branch_register
    '''
    logging.debug('branch_on_ltz_insn {0} {1}'.format(value_register, branch_register))
    return (
        OPCODES['branch_on_ltz'],
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

def multiply_insn(result, one, two):
    logging.debug('multiply_insn {0} {1} {2}'.format(result, one, two))
    return (
        OPCODES['multiply'],
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


int_to_base16 = {
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
    return int_to_base16[low] + int_to_base16[high]

def get_base16(integer, size=1):
    if size == 1:
        # need two characters
        return get_two(integer)
    elif size == 2:
        first = integer % 256
        second = integer >> 8
        return get_two(first) + get_two(second)
    else:
        raise Exception("Can't handle this {0}".format(integer))


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
    if code == OPCODES['store_word']:
        text = 'store_word {0} {1} {2}'.format(insn[1], insn[2], insn[3])
    elif code == OPCODES['jump']:
        text = 'jump {0}'.format(insn[1]) 
    elif code == OPCODES['branch_on_z']:
        text = 'branch_on_z {0} {1}'.format(insn[1], insn[2])
    elif code == OPCODES['add']:
        text = 'add {0} {1} {2}'.format(insn[1], insn[2], insn[3])
    elif code == OPCODES['subtract']:
        text = 'subtract {0} {1} {2}'.format(insn[1], insn[2], insn[3])
    elif code == OPCODES['load_word']:
        text = 'load_word {0} {1} {2}'.format(insn[1], insn[2], insn[3])
    elif code == OPCODES['set']:
        text = 'set {0} {1}'.format(insn[1], insn[2])
    elif code == OPCODES['branch_on_ltz']:
        text = 'branch_on_ltz {0} {1} '.format(insn[1], insn[2])
    elif code == OPCODES['store_byte']:
        text = 'store_byte {0} {1} {2}'.format(insn[1], insn[2], insn[3])
    elif code == OPCODES['load_byte']:
        text = 'load_byte {0} {1} {2}'.format(insn[1], insn[2], insn[3])
    elif code == OPCODES['multiply']:
        text = 'multiply {0} {1} {2}'.format(insn[1], insn[2], insn[3])
    else:
        raise Exception("Unknown instruction: {0}".format(code))
    print 'writing insn: ' + text
    return text + '\n'


def write_insn(insn):
    # 0 is opcode
    code = insn[0]
    sizes = [1,1,1,1]
    if code == OPCODES['store_word']:
        pass
    elif code == OPCODES['jump']:
        sizes = [1,1,2]
    elif code == OPCODES['branch_on_z']:
        pass
    elif code == OPCODES['add']:
        pass
    elif code == OPCODES['subtract']:
        pass
    elif code == OPCODES['load_word']:
        pass
    elif code == OPCODES['set']:
        sizes = [1,1,2]
    elif code == OPCODES['branch_on_ltz']:
        pass
    elif code == OPCODES['store_byte']:
        pass
    elif code == OPCODES['load_byte']:
        pass
    elif code == OPCODES['multiply']:
        pass
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


    def branch_on_z_imm(self, value_reg, immediate, free_reg):
        '''
        if value at value_reg is 0, then jump to immediate
        else, go to pc+1
        '''
        self.set_int(free_reg, immediate)
        insn_two = branch_on_z_insn(value_reg, free_reg)
        self.insns.append(insn_two)


    def branch_on_z_pc_offset(self, value_reg, pc_offset, free_reg):
        '''
        if value at value_reg is 0, then jump to pc + offset.
        '''
        num = len(self.insns)
        self.branch_on_z_imm(self, value_reg, num + pc_offset, free_reg)


    def branch_on_z_imm_set(self, insn_index, value_reg=None, immediate=None, free_reg=None):
        '''
        insn_index is beginning of branch insns. basically resetting the branch_on_z_insns.
        '''
        old_one = self.insns[insn_index]
        old_two = self.insns[insn_index+1]

        if value_reg is None:
            value_reg = old_two[1]
        if immediate is None:
            immediate = old_one[2]
        if free_reg is None:
            free_reg = old_one[1]

        insn_one = set_insn(free_reg, immediate)
        insn_two = branch_on_z_insn(value_reg, free_reg)
        self.insns[insn_index] = insn_one
        self.insns[insn_index+1] = insn_two


    def new_memory_deprecated(self, size):
        # need to look at current stack pointer and bump it down.
        self.subtract_int(self.sp_addr, self.sp_addr, size)


    def load_int(self, val_reg, addr_reg, imm=0):
        '''

        '''
        self.insns.append(load_word_insn(val_reg, addr_reg, imm))


    def load_byte(self, val_reg, addr_reg, imm=0):
        self.insns.append(load_byte_insn(val_reg, addr_reg, imm))

    def store_int(self, dest_reg, value_reg):
        '''
        Store value in value_reg to address in dest_reg
        '''
        insn = store_word_insn(value_reg, dest_reg)
        self.insns.append(insn)

    def store_byte(self, dest_reg, value_reg):
        '''
        Store lowest byte in value_reg to address in dest_reg
        '''
        insn = store_byte_insn(value_reg, dest_reg)
        self.insns.append(insn)

    def store_inti(self, dest_reg, value, free_reg):
        insn = set_insn(free_reg, value)
        insn2 = store_word_insn(free_reg, dest_reg)
        self.insns.extend([insn, insn2])

    def copy(self, dest, src, size, free_reg):
        '''
        memory copy src addr to dest addr
        size is in bytes.
        '''
        insn = load_word_insn(free_reg, src, 0)
        insn2 = store_word_insn(free_reg, dest, 0)
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

    def jump_and_link(self, immediate, return_register_no, free_reg):
        # if contents of this file changes, then also update the jump_and_link_set
        # do the same as jumpi_set here. first set the return retuster to whatever, then do the jump, then set the return_registes
        set_insn_idx = len(self.insns)
        self.set_int(return_register_no, 0)
        self.jumpi(immediate, free_reg)
        self.set_int_set(set_insn_idx, value=(len(self.insns)*4))

    def jump_and_link_set(self, insn_idx, immediate=None, return_register_no=None, free_reg_no=None):
        set_insn = self.insns[insn_idx]

        if return_register_no == None:
            return_registet_no = set_insn[1]
        # value is never updated for the set insn
        value = set_insn[2]
        self.set_int_set(insn_idx, return_register_no, value)

        self.jumpi_set(insn_idx+1, immediate, free_reg_no)


    def jumpi_set(self, insn_index, immediate=None, free_reg=None):
        old_one = self.insns[insn_index]
        old_two = self.insns[insn_index+1]

        if immediate is None:
            immediate = old_one[2]
        if free_reg is None:
            free_reg = old_one[1]

        insn_one = set_insn(free_reg, immediate)
        insn_two = jump_insn(free_reg)
        self.insns[insn_index] = insn_one
        self.insns[insn_index+1] = insn_two


    def jump_pc_offset(self, pc_offset, free_reg):
        self.jumpi(pc_offset + len(self.insns), free_reg)


    def set_int(self, register_no, value):
        self.insns.append(set_insn(register_no, value))

    def set_int_set(self, insn_idx, register_no=None, value=None):
        insn = self.insns[insn_idx]
        if register_no is None:
            register_no = insn[1]
        if value is None:
            value = insn[2]
        self.insns[insn_idx] = set_insn(register_no, value)



    def __add_inverse(self, one, two, f_one, f_two, f_three):
        '''
        f_three holds the result of one + (-1*two)
        '''
        self.set_int(f_one, 1)
        self.subtract_int(f_one, 0, f_one)
        i2 = multiply_insn(f_two, two, f_one)
        i3 = add_insn(f_three, one, f_two)
        self.insns.extend([i2, i3])


    def set_on_ne(self, dest, one, two, f_one, f_two):
        '''
        if one != two, set dest to 1. else set dest to 0.
        '''
        self.set_on(dest, one, two, f_one, f_two, 'ne')


    def set_on_e(self, dest, one, two, f_one, f_two):
        '''
        if one != two, set dest to 1. else set dest to 0.
        '''
        self.set_on(dest, one, two, f_one, f_two, 'e')


    def set_on(self, dest, one, two, f_one, f_two, equality):
        '''
        if one == two, set dest to 1. else set dest to 0.
        Multiplies two by -1, and if one + two = 0, then they are equal,
        so set to 1. Else set to 0.
        '''
        self.subtract_int(f_one, one, two)

        if equality=='e':
            on_z = 1
            on_nz = 0
        else:
            on_z = 0
            on_nz = 1

        branch_insn_idx = len(self.insns)
        self.branch_on_z_imm(f_one, 0, f_two)
        self.set_int(dest, on_nz)
        jump_insn_idx = len(self.insns)
        self.jumpi(0, f_two)

        self.branch_on_z_imm_set(branch_insn_idx, immediate=(len(self.insns)*INSN_SIZE))
        self.set_int(dest, on_z)
        self.jumpi_set(jump_insn_idx, immediate=(len(self.insns)*INSN_SIZE))


    def subtract_int(self, result, one, two):
        self.insns.append(subtract_insn(result,one,two))
