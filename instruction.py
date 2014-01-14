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
opcode is first byte.
little-endian - for a multi-byte object (such as a 32-bit integer), least significant byte is stored in lowest memory location.


insn types:
store addr byte
  addr - 32-bit address where to store.
  byte - 8-bit data to store.

jump insn_number
  insn_number - 32-bit insn location (pc) to jump to.

move dst src
  copy a byte.
  dst - 32-bit address where to copy to.
  src - 32-bit address where to copy from.

branch read_addr branch_to
  if byte at read_addr is 0, branch to pc.
  read_addr - 32-bit address to read a byte 
  branch_to - 32-bit insn location to branch to.

add result one two
  add 2 8-bit integers
  result - 32-bit address of result
  one - 32-bit address of first operand
  two - 32-bit address of second operand.

subtract result one two
    result = one - two. 32-bit subtraction.
  result - address of result
  one - address of first operand.
  two - address of second operand.

op codes:
each instruction is 104-bits long.

use byte for opcode

'''
OPCODES = {
    'store': 0,
    'jump': 1,
    'move': 2,
    'branch': 3,
    'add': 4,
    'subtract': 5,
    
}

def write_insn(insn):
    if insn['opcode'] =
