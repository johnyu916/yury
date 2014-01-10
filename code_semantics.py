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

    def get_function(self, name):
        for function in self.functions:
            if function.name == name:
                return function
        return None


class Block(object):
    def __init__(self):
        self.variables = []


class Expression(object):
    def __init__(self, expression_text, function, program):
        data = expression_text.data
        data_type = type(data)
        if data_type == VariableText:
            var_text = text.data
            if var_text.name:
                var = function.get_variable(var_text.name)
                if var:
                    self.data = var
                    return
        elif data_type == str:
            # does function name or operator exist?
            if data in OPERATORS:
                self.data = data
            else:
                function = program.get_function(data)
                if function:
                    self.data = data
            else:
                raise Exception("no function with that name")


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
        self.function_text = function_text
        for inpu in function_text.inputs:
            var = Variable(inpu)
            self.inputs.append(var)

        for inpu in function_text.outputs:
            var = Variable(t_type, inpu.name)
            self.outputs.append(var)

    def process_code(self):
        function_text = self.function_text
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

    def get_variable(self, name):
        for var in self.inputs + self.outputs + self.variables:
            if var.name == name:
                return var
        return None


def get_object(objects, name):
    for object in objects:
        if object.name == name:
            return object
    return None


class Semantics:
    def __init__(self, program):
        function_semantics = []

        # first pass. just get the function name and inputs and outputs
        for function in program.functions:
            if get_object(function_semantics, function.name):
                raise Exception("function: {0} exists".format(function.name))
            function_sem = Function(function)
            function_semantics.append(function_sem)

        # second pass. process the code.
        for function in function_semantics:
            function.process_code()

        self.program = Program(function_semantics)
