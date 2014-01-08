from parser import PRIMITIVE_TYPES

class Type(object):
    '''
    Type
    '''
    def __init__(self, name, size):
        self.size = 1 # 1 byte
        self.name = 'int'

def get_type(type_str):
    TYPES = [
        Type('int',4)
    ]
    for type_o in TYPES:
        if type_o.name == type_str:
            return type_o
    return None

class Variable(object):
    def __init__(self, type, name, value=None):
        self.type = type
        self.name = name
        self.value = value


class BlockSemantics(object):
    def __init__(self):
        self.vars = []



class FunctionSemantics(BlockSemantics):
    def __init__(self, function_text):
        super(FunctionSemantics, self).__init__()
        self.name = function_text.name
        for inpu in function_text.inputs:
            t_type = get_type(inpu.arg_type)
            var = Variable(t_type, inpu.name)
            self.inputs.append(var)


        for inpu in function_text.outputs:
            t_type = get_type(inpu.arg_type)
            var = Variable(t_type, inpu.name)
            self.outputs.append(var)

        for text in function_text.code:
            if type(text) == ExpressionText:
                if type(text.data) == VariableText:
                    var = text.data
                    if var.name:
                        assert self.is_defined(var)
            elif type(text) == StatementText:
                dest = text.dest
                expr = text.expression
                this_type = dest.arg_type
                for child in expr.children:
                    assert(this_type == child.arg_type)

    def is_defined(self, var_text):
        for var in self.inputs:
            if var.name == var_text.name:
                return True

        # also for outputs and vars

class Semantics:
    def __init__(self, program):
        function_semantics = []
        for function in program.functions:
            function.
