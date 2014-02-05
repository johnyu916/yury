from parser import read_expression, Name, Constant, Operator
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


def test_expression_mix():
    line = "5"
    expression, line = read_expression(line)
    assert expression is not None
    assert isinstance(expression.data, Constant)
    assert len(expression.children) == 0
    print "expression tested: {0}".format(expression)
    assert line == '', "line is: {0}".format(line)

    line = "add(add(one), two+three)"
    expression, line = read_expression(line)
    assert expression is not None
    assert line == '', "line is: {0}".format(line)
    print "expression tested: {0}".format(expression)


def test_expression_functions():

    line = "add()"
    expression, line = read_expression(line)
    assert expression is not None
    assert isinstance(expression.data, Name)
    assert len(expression.children) == 0
    print "expression tested: {0}".format(expression)
    assert line == '', "line is: {0}".format(line)


    line = "add(one, two)"
    expression, line = read_expression(line)
    assert expression is not None
    assert isinstance(expression.data, Name)
    assert len(expression.children) == 2
    print "expression tested: {0}".format(expression)
    assert line == '', "line is: {0}".format(line)

    line = "add(add(one))"
    expression, line = read_expression(line)
    assert expression is not None
    assert isinstance(expression.data, Name)
    assert len(expression.children) == 1
    #pdb.set_trace()
    print "expression tested: {0}".format(expression)
    assert line == '', "line is: {0}".format(line)

    line = "add(add(one), two)"
    expression, line = read_expression(line)
    assert expression is not None
    assert isinstance(expression.data, Name)
    assert len(expression.children) == 2
    print "expression tested: {0}".format(expression)
    assert line == '', "line is: {0}".format(line)


def test_expression_operations():
    line = "5 + 6"
    expression, line = read_expression(line)
    assert expression is not None
    assert isinstance(expression.data, Operator)
    assert len(expression.children) == 2
    print "expression tested: {0}".format(expression)
    assert line == '', "line is: {0}".format(line)

    line = "5 + 7 - 8"
    expression, line = read_expression(line)
    assert expression is not None
    assert isinstance(expression.data, Operator)
    assert len(expression.children) == 2
    print "expression tested: {0}".format(expression)
    assert line == '', "line is: {0}".format(line)


def test_expression_parenthesis():
    line = "(5 + 6)"
    expression, line = read_expression(line)
    assert expression is not None
    assert isinstance(expression.data, Operator)
    assert len(expression.children) == 2
    print "expression tested: {0}".format(expression)

    line = "5 + (6 + 7)"
    expression, line = read_expression(line)
    assert expression is not None
    assert isinstance(expression.data, Operator)
    assert len(expression.children) == 2
    print "expression tested: {0}".format(expression)

    line = "5 + add(6 + (7+ bob))"
    expression, line = read_expression(line)
    assert expression is not None
    assert isinstance(expression.data, Operator)
    assert len(expression.children) == 2
    print "expression tested: {0}".format(expression)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_expression_functions()
    test_expression_operations()
    test_expression_mix()
    test_expression_parenthesis()
