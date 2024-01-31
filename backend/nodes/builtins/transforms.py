from nodes.base import Node
from pydantic import BaseModel, Field


class StringConcat(Node):
    """Takes 2 strings as an input and joins them together to create a single string output"""

    __label__ = "String Concatenation"
    __group__ = "Transforms"

    class Options(BaseModel):
        delimiter: str = Field("", description="inserted between the 2 input strings.")

    def run(self, string_a: str, string_b: str, options: Options) -> str:
        return f"{string_a}{options.delimiter}{string_b}"
