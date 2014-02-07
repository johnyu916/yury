import logging
import sys
from code_writer import Converter
from parser import Parser
from code_semantics import Semantics

class Compiler(object):
    # TODO: should decide whether machine only runs
    # compiled code, real-time, or some combination.
    # 1. run parser with everything.
    # 2. run semantics and converter as needed.
    def __init__(self, text, output_file_name):
        self.lines = text.split('\n')
        self.parser = Parser(self.lines)
        print "Parser finished. Code: {0}".format(self.parser.program)
        self.semantics = Semantics(self.parser.program)
        print "Semantics finished. Program: {}".format(self.semantics.program)
        program = self.semantics.program
        self.converter = Converter(program, {}, output_file_name)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    filename = sys.argv[1]
    if len(sys.argv) == 3:
        output_file_name = sys.argv[2]
    else:
        output_file_name = filename.split('.')[-1]
    #with open(BAM_DIR / filename) as f:
    with open(filename) as f:
        text = f.read()
        compiler = Compiler(text, output_file_name)
