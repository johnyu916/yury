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
    "PC_SIZE": 12
}
CPU["PC"] = (CPU['MEMORY'] + CPU['PC_SIZE']+2)*power(CPU['PC_SIZE'])  # where is pc stored?
CPU["PC_INT"] = CPU['PC'] + CPU['PC_SIZE']  # pc in interrupt
CPU["IDLE"] = CPU['PC_INT'] + CPU['PC_SIZE']  # currently idle, interrupt is right after.

# CPU
CPU = {
    "STORAGE": {
        "ROWS" : 3, # log of actual size. i.e, if ROWS = 3, then size = 2^3 = 8
        "COLUMNS": 3 # ditto.
    },
    "INSTRUCTIONS": 4 # ditto.
}

DEVICE_PRIMITIVES = ['resistor', 'source', 'ground', 'switch', 'bridge'];

ROOT = path.path(__file__).dirname()
STATIC = ROOT / 'static'
LESS_DIR = STATIC / 'less'
CSS_DIR = STATIC / 'css'

DEVICE_DIR = ROOT / 'descriptions'
DEVICE_TESTS_DIR = DEVICE_DIR / 'tests'
TESTS_DIR = ROOT / 'tests'
