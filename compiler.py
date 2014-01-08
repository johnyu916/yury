import sys
from code_writer import Converter
from parser import Parser
from code_semantics import Semantics

class Compiler(object):
    # TODO: should decide whether machine only runs
    # compiled code, real-time, or some combination.
    # 1. run parser with everything.
    # 2. run semantics and converter as needed.
    def __init__(self, text):
        self.lines = text.split('\n')
        self.parser = Parser(self.lines)
        self.semantics = Semantics(self.parser.program)
        program = self.semantics.program
        self.converter = Converter(program, {})


if __name__ == '__main__':
    filename = sys.argv[1]
    #with open(BAM_DIR / filename) as f:
    with open(filename) as f:
        text = f.read()
        compiler = Compiler(text)
