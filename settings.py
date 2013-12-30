import path

DATABASE = {
    'HOST': '127.0.0.1',
    'PORT': 27017,
    'NAME' : 'yury'
}
SERVER = {
    'HOST': '127.0.0.1',
    'PORT': 5000
}

DEBUG = True

CPU = {
    "MEMORY_SIZE_LOG": 18,  # 24-bit address space.
    "NUM_INSNS_LOG": 12  # log of number of insns.
}
CPU["INSN_SIZE"] = CPU['MEMORY_SIZE_LOG'] + CPU['NUM_INSNS_LOG'] + 2
CPU["PC_ADDR"] = CPU['INSN_SIZE']*power(CPU['INSN_SIZE_LOG'])  # pc is stored right after all insns?
CPU["PC_SIGNAL_ADDR"] = CPU['PC_ADDR'] + CPU['INSN_SIZE_LOG']  # pc in interrupt
CPU["IDLE_ADDR"] = CPU['PC_SIGNAL_ADDR'] + CPU['INSN_SIZE_LOG']  # currently idle, interrupt is right after.


DEVICE_PRIMITIVES = ['resistor', 'source', 'ground', 'switch', 'bridge'];

ROOT = path.path(__file__).dirname()
STATIC = ROOT / 'static'
LESS_DIR = STATIC / 'less'
CSS_DIR = STATIC / 'css'

DEVICE_DIR = ROOT / 'descriptions'
DEVICE_TESTS_DIR = DEVICE_DIR / 'tests'
TESTS_DIR = ROOT / 'tests'

BAM_DIR = ROOT / 'bam'
