from nodes.base import Node
from pydantic import BaseModel, Field


class StringConcat(Node):
    """
    Takes 2 strings as an input and joins them together to create a single string output
    """

    __label__ = "String Concatenation"
    __group__ = "Transforms"

    class Options(BaseModel):
        delimiter: str = Field("", description="inserted between the 2 input strings.")

    def run(self, a: str, b: str, options: Options) -> str:
        return f"{a}{options.delimiter}{b}"


class ToString(Node):
    """
    Takes any string, int, float or boolean and converts it to a string
    """

    __label__ = "To String"
    __group__ = "Transforms"

    def run(self, value: str | int | float | bool) -> str:
        return str(value)
