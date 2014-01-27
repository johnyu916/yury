import math
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
    "NUM_REGISTERS": 64,
    "INSN_SIZE": 4, # 4 bytes
    "PC_SIGNAL_ADDR": 500, # TODO: this should be in a register?
    "IDLE_ADDR": 501 # TODO: this shouldbe in a register?
}


DEVICE_PRIMITIVES = ['resistor', 'source', 'ground', 'switch', 'bridge'];

ROOT = path.path(__file__).dirname()
STATIC = ROOT / 'static'
LESS_DIR = STATIC / 'less'
CSS_DIR = STATIC / 'css'

DEVICE_DIR = ROOT / 'descriptions'
DEVICE_TESTS_DIR = DEVICE_DIR / 'tests'
TESTS_DIR = ROOT / 'tests'

BAM_DIR = ROOT / 'bam'
