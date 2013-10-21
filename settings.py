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
