from shared.common import get_object
import logging
from parser import OPERATORS, PRIMITIVE_TYPES, Parameter, ExpressionText, StatementText, FunctionText, WhileText, IfText, ElIfText, ElseText, get_program_dict, get_expression_dict, DottedName, ConstantText, Operator
import json


class Type(object):
    '''
    Type
    '''
    def __init__(self, name, size):
        self.size = size # size is in bytes
        self.name = name

    def get_dict(self):
        return {
            'size': self.size,
            'name': self.name,
        }

TYPES = [
    Type('int',4),
    Type('bool',1),
]

def get_primitive_type(type_str):
    '''
    Return Type objects.
    '''
    for type_o in TYPES:
        if type_o.name == type_str:
            return type_o
    return None


def get_type(type_name, structs=None):
    prim_type = get_primitive_type(type_name)
    if prim_type is not None:
        return prim_type
    if structs is None:
        return None
    struct = get_struct(structs, type_name)
    return struct


def get_dotted_type(tokens, first_type, structs):
    '''
    get the type of dotted_name variable.
    need to know the type name of the first token, because
    it is a name of an instance rather than type.
    '''
    if len(tokens) == 0:
        raise Exception("Can't get type of empty tokens")

    if len(tokens) == 1:
        return first_type

    assert isinstance(first_type, Struct), "tokens is more than size one: {} but first_type is {}".format(tokens, first_type)
# check name of the token
    next_token = tokens[1]
    member = first_type.get_member(next_token)
    if member is None:
        raise Exception("Can't find member: ", next_token)
    return get_dotted_type(tokens[1:], member.type, structs)


def get_constant_type(value):
    # only int
    try:
        va = int(value)
        return get_primitive_type('int')
    except:
        raise Exception("Unknown type")
    return None


def get_struct(structs, name):
    for struct in structs:
        if struct.name == name:
            return struct
    return None

def variable_make(variable_text, structs):
    t_type = get_type(variable_text.arg_type, structs)
    if not t_type:
        raise Exception("Can't make variable")
    return Variable(t_type, variable_text.name)


class Constant(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def get_dict(self):
        return {
            'type': self.type.get_dict(),
            'value': self.value,
        }

class Variable(object):
    '''
    Variable has type and name.
    Type can be primitive or struct.
    '''
    def __init__(self, type, name):
        self.type = type
        self.name = name

    def get_dict(self):
        return {
            'type': self.type.get_dict(),
            'name': self.name,
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

    def get_struct(self, name):
        return get_struct(self.structs, name)

    def __str__(self):
        return json.dumps(self.get_dict())

    def get_dict(self):
        return get_program_dict(self)


class Block(object):
    def __init__(self, parent, program):
        self.code = []
        self.variables = []
        self.parent = parent
        self.program = program

    def process_code(self, code):
        '''
        code is text.code
        '''
        for text in code:
            logging.debug("Processing code: {}".format(text))
            if isinstance(text, ExpressionText):
                expr = expression_make(text, self, self.program)
                self.code.append(expr)
            elif isinstance(text, StatementText):
                statement = Statement(text, self, self.program)
                self.code.append(statement)
            elif isinstance(text, WhileText):
                condition = make_condition(text.condition, self, self.program)
                whilev = While(condition, self, self.program)
                whilev.process_code(text.code)
                self.code.append(whilev)
                # need to shift context.
            elif isinstance(text, IfText):
                prev_block = self.code[-1]
                assert not isinstance(prev_block, If) and not isinstance(prev_block, ElIf), "Prev should not be be if or elif but is: {}".format(prev_block)
                condition = make_condition(text.condition, self, self.program)
                ifcon = If(condition, self, self.program)
                ifcon.process_code(text.code)
                self.code.append(ifcon)
            elif isinstance(text, ElIfText):
                prev_block = self.code[-1]
                assert isinstance(prev_block, If) or isinstance(prev_block, ElIf), "Prev needs to be if or elif but is: {}".format(prev_block)
                condition = make_condition(text.condition, self, self.program)
                elifcon = ElIf(condition, self, self.program)
                elifcon.process_code(text.code)
                self.code.append(elifcon)
            elif isinstance(text, ElseText):
                prev_block = self.code[-1]
                assert isinstance(prev_block, If) or isinstance(prev_block, ElIf), "Prev needs to be if or elif but is: {}".format(prev_block)
                elsecon = Else(None, self, self.program)
                elsecon.process_code(text.code)
                self.code.append(elsecon)
            else:
                raise Exception("Can't process code: ", text)

    def variables_append(self, variable):
        self.variables.append(variable)

    def get_variable(self, dotted_name):
        tokens = dotted_name.tokens
        root_name = tokens[0]
        for var in self.variables:
            if var.name == root_name:
                # now ensure rest of names are okay.
                dotted_type = get_dotted_type(tokens, var.type, self.program.structs)
                return var

        if self.parent:
            return self.parent.get_variable(dotted_name)
        else:
            return None

    def get_dict(self):
        codes = []
        variables = [var.get_dict() for var in self.variables]
        for line in self.code:
            codes.append(line.get_dict())
        return {
            'code': codes,
            'variables': variables
        }

    def __str__(self):
        return json.dumps(self.get_dict())

def make_expression_children(expression_text, block, program):
    '''
    build expression from children of functions/operators.
    '''
    children = []
    for child in expression_text.children:
        child_exp = expression_make(child, block, program)
        types = child_exp.get_types()
        assert len(types) == 1, "Each operands must return 1 value, but returns: {0}".format(len(child_exp))
        children.append(child_exp)
    return children

def expression_make(expression_text, block, program):
    data = expression_text.data
    e_data = None
    children = []
    if isinstance(data, ConstantText):
        # constant variable
        c_type = get_constant_type(data.value)
        if c_type:
            e_data = Constant(c_type, data.value)
        else:
            raise Exception("Unknown type: {0}".format(data.value))
    elif isinstance(data, DottedName):
        # name could be variable or function
        var = block.get_variable(data)
        if var:
            e_data = data
        else:
            assert len(data.tokens) == 1, "Only support single token function names"
            token = data.tokens[0]
            function = program.get_function(token)
            if function is not None:
                e_data = token
                children = make_expression_children(expression_text, block, program)

                for index, child in enumerate(children):
                    child_type  = child.get_types()[0]
                    def_name = function.inputs[index].type.name
                    assert def_name == child_type.name, "Function input type {} does not match child type: {}".format(def_name, child_type.name)
            else:
                struct = program.get_struct(token)
                if struct is not None:
                    e_data = token
                else:
                    raise Exception("no function or struct with that name: {0}".format(data))

    elif isinstance(data, Operator):
        # operator is like a function call
        e_data = data.value
        children = make_expression_children(expression_text, block, program)

        assert len(children) == 2, "Can only handle 2 operands in operation, but returns: {0}".format(len(children))
        my_type = None
        for child in children:
            child_type  = child.get_types()[0]
            if my_type == None:
                my_type = child_type
            else:
                assert my_type.name == child_type.name, "My type: {0}, child_type: {1}".format(my_type, child_type)

    else:
        raise Exception("Unknown data: {0}".format(data))

    return Expression(e_data, children, block, program)

class Expression(object):
    '''
    Node.
    self.data is either DottedName or Constant or string (function name or operator)
    self.children is a list of expression objects.
    '''
    def __init__(self, data, children, block, program):
        self.children = children
        self.block = block
        self.program = program
        self.data = data


    def get_types(self):
        '''
        What is the type of the ExpressionText?
        Note this can be more than one, so return an array
        '''
        data = self.data
        if isinstance(data, DottedName):
            variable = self.block.get_variable(data)
            return [get_dotted_type(data.tokens, variable.type, self.program.structs)]
        elif isinstance(data, Constant):
            return [data.type]
        elif isinstance(data, str):
            # either function name or operator
            function = self.program.get_function(data)
            if function is not None:
                return function.get_types()
            struct = self.program.get_struct(data)
            if struct is not None:
                return [struct]
            if data in OPERATORS:
                if data == '==' or data == '!=':
                    return [get_primitive_type('bool')]
                else:
                    return self.children[0].get_types()
            raise Exception("Unknown type of string function: ", data)
        else:
            raise Exception("Cannot determine type of expression: {}".format(data))

    def get_dict(self):
        return get_expression_dict(self)

    def __str__(self):
        return json.dumps(self.get_dict())


class Statement(object):
    def __init__(self, statement_text, block, program):
        '''
        destinations is a list of DottedName objects.
        '''
        dests = statement_text.dests
        expr = statement_text.expression
        expression = expression_make(expr, block, program)
        dest_types = expression.get_types()
        destinations = []
        for dest, type in zip(dests,dest_types):
            destination = block.get_variable(dest)
            if destination:
                dotted_type = get_dotted_type(dest.tokens, destination.type, program.structs)
                assert dotted_type.name == type.name, "{0} not equal to {1}".format(dotted_type.name, type.name)
            else:
                destination = Variable(type, dest.tokens[0])
                block.variables_append(destination)
            destinations.append(dest)

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
    def __init__(self, condition, parent, program):
        self.condition = condition
        super(Conditional, self).__init__(parent, program)

    def get_dict(self):
        this_dict = {}
        if self.condition is not None:
            this_dict['condition']= self.condition.get_dict()
        codes = super(Conditional, self).get_dict()
        this_dict.update(codes)
        return this_dict


def make_condition(condition_text, parent, program):
    condition = expression_make(condition_text, parent, program)
    types = condition.get_types()
    # condition is an expression. it must return boolean
    assert len(types) == 1 and types[0].name == 'bool'
    return condition


class While(Conditional):
    pass

class If(Conditional):
    pass

class ElIf(Conditional):
    pass

class Else(Conditional):
    pass

def struct_append(struct_text, structs):
    name = struct_text.name
    size = 0
    members = []
    for member_text in struct_text.members:
        member_text.arg_type
        type = get_type(member_text.arg_type, structs)
        if type is None:
            raise Exception("couldn't find type for: " + member_text.arg_type)
        size += type.size
        member = Variable(type, member_text.name)
        members.append(member)
    struct = Struct(name, size, members)
    structs.append(struct)

class Struct(Type):
    def __init__(self, name, size, members=[]):
        '''
        Each member is a Variable.
        '''
        super(Struct, self).__init__(name, size)
        self.members = members

    def get_dict(self):
        basic = super(Struct, self).get_dict()
        members = []
        for member in self.members:
            members.append(member.get_dict())

        return_dict = {
            'members': members
        }
        return_dict.update(basic)
        return return_dict

    def get_member(self, member_name):
        for member in self.members:
            if member.name == member_name:
                return member
        return None

    def get_member_offset(self, member_name):
        offset = 0
        for member in self.members:
            if member.name == member_name:
                return (member, offset)
            offset += member.type.size
        return None

    def __str__(self):
        return json.dumps(self.get_dict())


def function_make(function_text, program):
    inputs = []
    outputs = []
    name = function_text.name
    for inpu in function_text.inputs:
        var = variable_make(inpu, program.structs)
        inputs.append(var)
        print "adding input to function: {0} {1}".format(name, var.get_dict())

    for inpu in function_text.outputs:
        var = variable_make(inpu, program.structs)
        print "adding output to function: {0} {1}".format(name, var.get_dict())
        outputs.append(var)

    return Function(name, inputs, outputs, program)

class Function(Block):
    def __init__(self, name, inputs, outputs, program):
        '''
        name is a string
        Inputs and outputs are lists of Variable objects.
        '''
        super(Function, self).__init__(None, program)
        self.name = name
        self.inputs = []
        self.outputs = []
        self.variables = inputs + outputs
        self.local_variables = []

        logging.debug("function constructor variables: ")
        for var in self.variables:
            print var.get_dict()

    def variables_append(self, variable):
        self.variables.append(variable)
        self.local_variables.append(variable)


    def get_types(self):
        types = []
        for output in self.outputs:
            types.append(output.type)
        return types

    def get_dict(self):
        inputs = [inpu.get_dict() for inpu in self.inputs]
        outputs = [output.get_dict() for output in self.outputs]
        local_variables = [var.get_dict() for var in self.local_variables]

        codes = super(Function, self).get_dict()
        return_dict = {
            'name': self.name,
            'inputs': inputs,
            'outputs': outputs,
            'local_variables': local_variables,
        }
        return_dict.update(codes)
        return return_dict


class Semantics:
    def __init__(self, program_text):
        function_semantics = []
        structs = []
        self.program = Program(function_semantics, structs)

        for struct_text in program_text.structs:
            struct_append(struct_text, structs)

        # first pass. just get the function name and inputs and outputs
        for function_text in program_text.functions:
            if get_object(function_semantics, function_text.name):
                raise Exception("function: {0} exists".format(function_text.name))
            function_sem = function_make(function_text, self.program)
            function_semantics.append(function_sem)

        # second pass. process the code.
        for function_text, function in zip(program_text.functions, function_semantics):
            function.process_code(function_text.code)
