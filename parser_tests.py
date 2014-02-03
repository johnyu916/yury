from parser import read_expression
def function_call_test():
    pass

def expression_test():
    line = "add(one, two)"
    expression, line = read_expression(line)
    assert expression is not None
    assert line == '', "line is: {0}".format(line)

    line = "add(add(one))"
    expression, line = read_expression(line)
    assert expression is not None
    assert line == '', "line is: {0}".format(line)

    line = "add(add(one), two)"
    expression, line = read_expression(line)
    assert expression is not None
    assert line == '', "line is: {0}".format(line)

    line = "add(add(one), two+three)"
    expression, line = read_expression(line)
    assert expression is not None
    assert line == '', "line is: {0}".format(line)
    print expression

if __name__ == '__main__':
    expression_test()
