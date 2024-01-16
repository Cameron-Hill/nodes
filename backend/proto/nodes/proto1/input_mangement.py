"""
How do we define the number of inputs and outputs for an action?
How do we define the types of an action's inputs and outputs?
"""

########### TYPES ###########

class Type:
    """"""

class ComplexType(Type):
    """"""

class Object(ComplexType):
    """"""

class Array(ComplexType):
    """"""

class PrimitiveType(Type):
    """"""

class Int(PrimitiveType):
    """"""

class Float(PrimitiveType):
    """"""  

class String(PrimitiveType):
    """"""  

class Boolean(PrimitiveType):
    """"""  

class Null(PrimitiveType):
    """"""  


########### ACTIONS ###########

class Action:
    """"""
    def handler(self) -> Null:
        return None

class Action1:
    def handler(self, input1: Object, input2: Array, input3: Int) -> Object:
        return input1