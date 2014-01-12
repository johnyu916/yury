from parser import OPERATORS, PRIMITIVE_TYPES, VariableText, ExpressionText, StatementText, FunctionText, ConditionalText, WhileText

class Type(object):
    '''
    Type
    '''
    def __init__(self, name, size):
        self.size = size
        self.name = name

    def get_dict(self):
        return {
            'size': self.size,
            'name': self.name,
        }

def get_type(type_str):
    TYPES = [
        Type('int',4),
        Type('bool',1),
    ]
    for type_o in TYPES:
        if type_o.name == type_str:
            return type_o
    return None


def get_constant_type(value):
    # only int
    try:
        va = int(value)
        return get_type('int')
    except:
        raise Exception("Unknown type")
    return None

def variable_make(variable_text):
    t_type = get_type(variable_text.arg_type)
    return Variable(t_type, variable_text.name, variable_text.value)

class Variable(object):
    def __init__(self, type, name, value):
        self.type = type
        self.name = name
        self.value = value

    def get_dict(self):
        return {
            'type': self.type.get_dict(),
            'name': self.name,
            'value': self.value
        }

class Program(object):
    def __init__(self, functions, structs):
        self.functions = functions
        self.structs = structs

    def get_function(self, name):
        for function in self.functions:
            if function.name == name:
                return function
        return None


class Block(object):
    def __init__(self, text, parent, program):
        self.variables = []
        self.code = []
        self.text = text
        self.parent = parent
        self.program = program


    def process_code(self):
        for text in self.text.code:
            text_type = type(text)
            if text_type == ExpressionText:
                expr = Expression(text, self, self.program)
                self.code.append(expr)
            elif text_type == StatementText:
                statement = Statement(text, self, self.program)
                self.code.append(statement)
            elif text_type == WhileText:
                whilev = While(text, self, self.program)
                whilev.process_code()
                self.code.append(whilev)
                # need to shift context.


    def get_variable(self, name):
        for var in self.variables:
            print "looking at var: {0}".format(var.get_dict())
            if var.name == name:
                return var
        if self.parent:
            return self.parent.get_variable(name)
        else:
            return None

class Expression(object):
    def __init__(self, expression_text, function, program):
        self.children = []
        self.function = function
        self.program = program
        data = expression_text.data
        data_type = type(data)

        # variables inside expressions must be defined
        if data_type == VariableText:
            var_text = data
            if var_text.name:
                var = function.get_variable(var_text.name)
                if var:
                    self.data = var
                    return
                else:
                    raise Exception("Undefined var: {0}".format(data.get_dict()))
            elif var_text.value:
                c_type = get_constant_type(var_text.value)
                if c_type:
                    self.data = Variable(c_type, None, var_text.value)
                else:
                    raise Exception("Unknown type: {0}".format(var_text.value))
            else:
                raise Exception("Unable to read variable: {0}".format(data))
        elif data_type == str:
            child_types = []
            for child in expression_text.children:
                child_exp = Expression(child, function, program)
                child_types.append(child_exp.get_types)
                self.children.append(child_exp)

            # does function name or operator exist?
            if data in OPERATORS:
                self.data = data
                # only check if they are same an has length 1

            else:
                function_p = program.get_function(data)
                if function_p:
                    self.data = data
                else:
                    raise Exception("no function with that name: {0}".format(data))

        else:
            raise Exception("Unknown data: {0}".format(data))


    def get_types(self):
        '''
        What is the type of the ExpressionText?
        Note this can be more than one, so return an array
        '''
        data = self.data
        if type(data) == Variable:
            print "exp get_type var: {0}".format(data.get_dict())
            if data.type:
                return [data.type]
            elif data.value:
                try:
                    val = int(data.value)
                    return get_type('int')
                except:
                    pass
            elif data.name:
                # try looking for it
                var = get_object(self.function.variables, data.name)
                if var:
                    return [var.type]
            else:
                return None
        elif type(data) == str:
            function = self.program.get_function(data)
            if function:
                return function.get_types()
            elif data in OPERATORS:
                if data == '==' or data == '!=':
                    return [get_type('bool')]
                else:
                    return self.children[0].get_types()
        else:
            raise Exception("Cannot determine type of expression")

class Statement(object):
    def __init__(self, statement_text, function, program):
        dests = statement_text.dests
        expr = statement_text.expression
        expression = Expression(expr, function, program)
        dest_types = expression.get_types()
        destinations = []
        for dest, type in zip(dests,dest_types):
            destination = function.get_variable(dest.name)
            if destination:
                assert destination.type.name == type.name, "{0} not equal to {1}".format(destination.type.name, type.name)
            else:
                destination = Variable(type, dest.name, None)
                function.variables.append(destination)
            destinations.append(destination)

        self.destinations = destinations
        self.expression = expression


class Conditional(Block):
    def __init__(self, condition, text, parent, program):
        self.condition = condition
        super(Conditional, self).__init__(text, parent, program)


class While(Conditional):
    def __init__(self, while_text, function, program):
        cond_text = while_text.condition
        condition = Expression(cond_text, function, program)
        # condition is an expression. it must return boolean
        types = condition.get_types()
        assert len(types) == 1 and types[0].name == 'bool'
        super(While, self).__init__(condition, while_text, function, program)


class Function(Block):
    def __init__(self, function_text, program):
        super(Function, self).__init__(function_text, None, program)
        self.name = function_text.name
        self.inputs = []
        self.outputs = []
        for inpu in function_text.inputs:
            var = variable_make(inpu)
            self.inputs.append(var)
            print "adding input to function: {0} {1}".format(self.name, var.get_dict())
            self.variables.append(var)

        for inpu in function_text.outputs:
            var = variable_make(inpu)
            print "adding output to function: {0} {1}".format(self.name, var.get_dict())
            self.outputs.append(var)
            self.variables.append(var)

        print "function constructor variables: "
        for var in self.variables:
            print var.get_dict()

    def get_types(self):
        types = []
        for output in self.outputs:
            types.append(output.type)
        return types

def get_object(objects, name):
    for object in objects:
        if object.name == name:
            return object
    return None


class Semantics:
    def __init__(self, program_text):
        function_semantics = []
        self.program = Program(function_semantics, [])

        # first pass. just get the function name and inputs and outputs
        for function in program_text.functions:
            if get_object(function_semantics, function.name):
                raise Exception("function: {0} exists".format(function.name))
            function_sem = Function(function, self.program)
            function_semantics.append(function_sem)

        # second pass. process the code.
        for function in function_semantics:
            print "function variables for {0}".format(function.name)
            for var in function.variables:
                print var.get_dict()
            function.process_code()

