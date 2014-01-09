from parser import PRIMITIVE_TYPES, ExpressionText, StatementText, FunctionText, ConditionalText

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
    def __init__(self, variable_text):
        t_type = get_type(variable_text.arg_type)
        self.type = t_type
        self.name = variable_text.name
        self.value = value


class Program(object):
    def __init__(self, functions, structs):
        self.functions = functions


class Block(object):
    def __init__(self):
        self.variables = []


class Expression(object):
    def __init__(self, expression_text, function):
        data_type = type(expression_text.data)
        if data_type == VariableText:
            var = text.data
            if var.name:
                assert function.is_defined(var)
        elif type(
            # need to look at children



    def get_type(expression):
        '''
        What is the type of the ExpressionText?
        Note this can be more than one, so return an array
        '''
        data = expression.data
        if type(data) == Variable:
            if data.arg_type:
                return get_type(data.arg_type)
            elif data.value:
                try:
                    val = int(data.value)
                    return get_type('int')
                except:
                    pass
            elif data.name:
                # try looking for it
                var = get_object(function.inputs + function.outputs + function.variables, data.name)
                if var:
                    return [var.type]
            else:
                return None
        else:
            # get child types
            # then look into function. validate inputs then get outputs.
            pass

        return None


class Statement(object):
    def __init__(self, statement_text, function):
        dest = statement_text.dest
        expr = statement_text.expression

        # look for dest
        if not self.is_defined(dest.name):
            # need to add this variable. what type is it?
            type = get_type(dest.arg_type)
            if type:
                new_var = Variable(type, dest.name)
                self.variables.append(new_var)
            else:
                # determine from expression
                pass

        this_type = dest.arg_type
        #print "expression: {0}".format(expr.get_dict())
        for child in expr.children:
            assert(this_type == child.data.arg_type)


class Function(Block):
    def __init__(self, function_text):
        super(Function, self).__init__()
        self.name = function_text.name
        self.inputs = []
        self.outputs = []
        self.code = []
        for inpu in function_text.inputs:
            var = Variable(inpu)
            self.inputs.append(var)

        for inpu in function_text.outputs:
            var = Variable(t_type, inpu.name)
            self.outputs.append(var)

        for text in function_text.code:
            text_type = type(text)
            if text_type == ExpressionText:
                expr = Expression(text)
                self.code.append(expr)
            elif text_type == StatementText:
                statement = Statement(text)
                self.code.append(statement)
            elif text_type == ConditionalText:
                # check variables are same type
                pass

    def is_defined(self, var_text):
        for var in self.inputs + self.outputs + self.variables:
            if var.name == var_text.name:
                return True
        return False


def get_object(objects, name):
    for object in objects:
        if object.name == name:
            return object
    return None


class Semantics:
    def __init__(self, program):
        function_semantics = []
        for function in program.functions:
            if get_object(function_semantics, function.name):
                raise Exception("function: {0} exists".format(function.name))
            function_sem = Function(function)
            function_semantics.append(function_sem)
        self.program = Program(function_semantics)
