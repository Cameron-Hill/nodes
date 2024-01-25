from nodes.base import Node, Option
from pydantic import Field, BaseModel


class StringProducer(Node):
    """
    This node takes a string, provided as an option and sends it to the output
    """

    __label__ = "String Producer"
    __group__ = "Producers"

    class Options(BaseModel):
        value: Option[str] = Field(..., description="The value to produce")

    def run(self, input: None, options: Options):
        return options.value


class IntProducer(Node):
    """
    This node takes an integer, provided as an option and sends it to the output
    """

    __label__ = "Integer Producer"
    __group__ = "Producers"

    class Options(BaseModel):
        value: Option[int] = Field(..., description="The value to produce")

    def run(self, input: None, options: Options):
        return options.value


class FloatProducer(Node):
    """
    This node takes a float, provided as an option and sends it to the output
    """

    __label__ = "Float Producer"
    __group__ = "Producers"

    class Options(BaseModel):
        value: Option[float] = Field(..., description="The value to produce")

    def run(self, input: None, options: Options):
        return options.value


class BoolProducer(Node):
    """
    This node takes a boolean, provided as an option and sends it to the output
    """

    __label__ = "Boolean Producer"
    __group__ = "Producers"

    class Options(BaseModel):
        value: Option[bool] = Field(..., description="The value to produce")

    def run(self, input: None, options: Options):
        return options.value
