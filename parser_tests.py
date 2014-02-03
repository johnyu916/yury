from parser import read_expression
import logging
import pdb

def function_call_test():
    pass

def expression_test2():
    line = "add(add(one))"
    expression, line = read_expression(line)
    assert expression is not None
    #pdb.set_trace()
    print "expression tested: {0}".format(expression)
    assert line == '', "line is: {0}".format(line)
    

def expression_test():
    line = "5"
    expression, line = read_expression(line)
    assert expression is not None
    print "expression tested: {0}".format(expression)
    assert line == '', "line is: {0}".format(line)

    line = "add()"
    expression, line = read_expression(line)
    assert expression is not None
    print "expression tested: {0}".format(expression)
    assert line == '', "line is: {0}".format(line)


    line = "add(one, two)"
    expression, line = read_expression(line)
    assert expression is not None
    print "expression tested: {0}".format(expression)
    assert line == '', "line is: {0}".format(line)

    line = "add(add(one))"
    expression, line = read_expression(line)
    assert expression is not None
    #pdb.set_trace()
    print "expression tested: {0}".format(expression)
    assert line == '', "line is: {0}".format(line)

    line = "add(add(one), two)"
    expression, line = read_expression(line)
    assert expression is not None
    print "expression tested: {0}".format(expression)
    assert line == '', "line is: {0}".format(line)

    #line = "add(add(one), two+three)"
    #expression, line = read_expression(line)
    #assert expression is not None
    #assert line == '', "line is: {0}".format(line)
    #print expression

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    expression_test2()
