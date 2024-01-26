from nodes.base import Node, Option
from pydantic import Field, BaseModel
from nodes.datatypes import UndefinedMap, PrimitiveType


class StringProducer(Node):
    """
    This node takes a string, provided as an option and sends it to the output
    """

    __label__ = "String Producer"
    __group__ = "Producers"

    class Options(BaseModel):
        value: str = Field(..., description="The value to produce")

    def run(self, input: None, options: Options) -> str:
        return options.value


class IntProducer(Node):
    """
    This node takes an integer, provided as an option and sends it to the output
    """

    __label__ = "Integer Producer"
    __group__ = "Producers"

    class Options(BaseModel):
        value: int = Field(..., description="The value to produce")

    def run(self, input: None, options: Options) -> int:
        return options.value


class FloatProducer(Node):
    """
    This node takes a float, provided as an option and sends it to the output
    """

    __label__ = "Float Producer"
    __group__ = "Producers"

    class Options(BaseModel):
        value: float = Field(..., description="The value to produce")

    def run(self, input: None, options: Options) -> float:
        return options.value


class BoolProducer(Node):
    """
    This node takes a boolean, provided as an option and sends it to the output
    """

    __label__ = "Boolean Producer"
    __group__ = "Producers"

    class Options(BaseModel):
        value: bool = Field(..., description="The value to produce")

    def run(self, input: None, options: Options) -> bool:
        return options.value


class MapProducer(Node):
    """
    This node will generate a map of any number of keys to primitive values.
    Primitive values are strings, integers, floats, and booleans.
    """

    __label__ = "Map Producer"
    __group__ = "Producers"

    class Options(BaseModel):
        value: dict[str, PrimitiveType] = Field(..., description="The value to produce")

    def run(self, input: None, options: Options) -> dict[str, PrimitiveType]:
        return options.value
