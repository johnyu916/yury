from shared.common import get_object
import logging
from parser import OPERATORS, PRIMITIVE_TYPES, Parameter, ExpressionText, StatementText, FunctionText, ConditionalText, WhileText, get_program_dict, get_expression_dict, Name, Constant
import json


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
    '''
    Return Type objects.
    '''
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

    def __str__(self):
        return json.dumps(self.get_dict())

    def get_dict(self):
        return get_program_dict(self)


class Block(object):
    def __init__(self, text, parent, program):
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


    def get_variable(self,name):
        if self.parent:
            return self.parent.get_variable(name)

    def get_dict(self):
        codes = []
        for line in self.code:
            codes.append(line.get_dict())
        return {
            'code': codes
        }

    def __str__(self):
        return json.dumps(self.get_dict())


class Expression(object):
    '''
    Node.
    self.data is either Variable or string (function name or operator)
    self.children is a list of expression objects.
    '''
    def __init__(self, expression_text, function, program):
        self.children = []
        self.function = function
        self.program = program
        data = expression_text.data

        if isinstance(data, Constant):
            # constant variable
            c_type = get_constant_type(data.value)
            if c_type:
                self.data = Variable(c_type, None, data.value)
            else:
                raise Exception("Unknown type: {0}".format(var_text.value))
        elif isinstance(data, Name):
            # name could be variable or function
            var = function.get_variable(data.value)
            if var:
                self.data = var
                return

            func = program.get_function(data.value)
            if func:
                self.data = data.value
            else:
                raise Exception("no function with that name: {0}".format(data))
            self._set_children(expression_text)

            for index, child in enumerate(self.children):
                child_type  = child.get_types()[0]
                def_name = function.inputs[index].type.name
                assert def_name == child_type.name, "Function input type {0} does not match child type: {1}".format(def_name, child_type.name)
            # could be function
            raise Exception("Undefined var: {0}".format(data.get_dict()))
        elif isinstance(data, Operator):
            # operator is like a function call
            self.data = data.value
            self._set_children(expression_text)

            assert len(self.children) == 2, "Can only handle 2 operands in operation, but returns: {0}".format(len(self.children))
            my_type = None
            for child in self.children:
                child_type  = child.get_types()[0]
                if my_type == None:
                    my_type = child_type
                else:
                    assert my_type.name == child_type.name, "My type: {0}, child_type: {1}".format(my_type, child_type)

        else:
            raise Exception("Unknown data: {0}".format(data))

    def _set_children(self, expression_text):
        for child in expression_text.children:
            child_exp = Expression(child, self.function, self.program)
            types = child_exp.get_types()
            assert len(types) == 1, "Each operands must return 1 value, but returns: {0}".format(len(child_exp))
            self.children.append(child_exp)

    def get_types(self):
        '''
        What is the type of the ExpressionText?
        Note this can be more than one, so return an array
        '''
        data = self.data
        if type(data) == Variable:
            #print "exp get_type var: {0}".format(data.get_dict())
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

    def get_dict(self):
        return get_expression_dict(self)

    def __str__(self):
        return json.dumps(self.get_dict())


class Statement(object):
    def __init__(self, statement_text, function, program):
        dests = statement_text.dests
        expr = statement_text.expression
        expression = Expression(expr, function, program)
        dest_types = expression.get_types()
        destinations = []
        for dest, type in zip(dests,dest_types):
            destination = function.get_variable(dest.value)
            if destination:
                assert destination.type.name == type.name, "{0} not equal to {1}".format(destination.type.name, type.name)
            else:
                destination = Variable(type, dest.value, None)
                function.variables_append(destination)
            destinations.append(destination)

        self.destinations = destinations
        self.expression = expression

    def get_dict(self):
        dest_list = []
        for dest in self.destinations:
            dest_dict = dest.get_dict()
            dest_list.append(dest_dict)
        return {
            'destinations': dest_list,
            'expression': self.expression.get_dict()
        }
    def __str__(self):
        return json.dumps(self.get_dict())


class Conditional(Block):
    def __init__(self, condition, text, parent, program):
        self.condition = condition
        super(Conditional, self).__init__(text, parent, program)

    def get_dict(self):
        this_dict = {
            'condition': self.condition.get_dict()
        }
        codes = super(Conditional, self).get_dict()
        this_dict.update(codes)
        return this_dict


class While(Conditional):
    def __init__(self, while_text, function, program):
        cond_text = while_text.condition
        condition = Expression(cond_text, function, program)
        # condition is an expression. it must return boolean
        types = condition.get_types()
        assert len(types) == 1 and types[0].name == 'bool'
        super(While, self).__init__(condition, while_text, function, program)

class Struct(object):
    def __init__(self, name, members=[]):
        self.name = name
        self.members = members

    def get_dict(self):
        members = []
        for member in self.members:
            members.append(member.get_dict())
        return {
            'name': self.name,
            'members': members
        }

    def __str__(self):
        return json.dumps(self.get_dict())


class Function(Block):
    def __init__(self, function_text, program):
        super(Function, self).__init__(function_text, None, program)
        self.name = function_text.name
        self.inputs = []
        self.outputs = []
        self.variables = []
        self.local_variables = []
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

    def variables_append(self, variable):
        self.variables.append(variable)
        self.local_variables.append(variable)

    def get_variable(self, name):
        for var in self.variables:
            print "looking at var: {0}".format(var.get_dict())
            if var.name == name:
                return var
        if self.parent:
            return self.parent.get_variable(name)
        else:
            return None


    def get_types(self):
        types = []
        for output in self.outputs:
            types.append(output.type)
        return types

    def get_dict(self):
        inputs = [inpu.get_dict() for inpu in self.inputs]
        outputs = [output.get_dict() for output in self.outputs]
        local_variables = [var.get_dict() for var in self.local_variables]
        variables = [var.get_dict() for var in self.variables]

        codes = super(Function, self).get_dict()
        return_dict = {
            'name': self.name,
            'inputs': inputs,
            'outputs': outputs,
            'local_variables': local_variables,
            'variables': variables,
        }
        return_dict.update(codes)
        return return_dict


class Semantics:
    def __init__(self, program_text):
        function_semantics = []
        structs = []
        self.program = Program(function_semantics, structs)

        # first pass. just get the function name and inputs and outputs
        for function in program_text.functions:
            if get_object(function_semantics, function.name):
                raise Exception("function: {0} exists".format(function.name))
            function_sem = Function(function, self.program)
            function_semantics.append(function_sem)

        # second pass. process the code.
        for function in function_semantics:
            logging.debug("function variables for {0}".format(function.name))
            for var in function.variables:
                logging.debug(var.get_dict())
            function.process_code()

        for struct_text in program_text.structs:
            struct = Struct(struct.text, struct.members)
            structs.append(struct)
