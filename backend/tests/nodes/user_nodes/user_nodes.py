from nodes.base import Node
from pydantic import Field, BaseModel


class Input(BaseModel):
    a: str = Field(..., description="Test value: a")
    b: int = Field(..., description="Test value: b")
    c: float = Field(..., description="Test value: c")


class Output(BaseModel):
    x: str = Field(..., description="Test Output value: x")
    y: int = Field(..., description="Test Output value: y")
    z: float = Field(..., description="Test Output value: z")
    option: bool | None = Field(default=None, description="Test Output value: option")


class UserNode(Node):
    class Options(BaseModel):
        test_option: bool = Field(False, description="Test option")

    def run(self, input: Input, options: Options) -> Output:
        """Run method for UserNode

        :param input: the input object, consists of a, b, and c
        :param options: driver options
        :return: the output object, consists of x, y, z, and option
        """
        return Output(x=input.a, y=input.b, z=input.c, option=options.test_option)


class UserNodeWithMultipleInputs(Node):
    def run(self, a: str, b: int, c: float = 20) -> Output:
        """_summary_

        :param  a: the a parameter
        :param b: the b parameter
        :param c: the c parameter, defaults to 20
        :return: the output object, consists of x, y, z
        """
        return Output(x=a, y=b, z=c)


class UserNodeNoOptions(Node):
    def run(self, input: Input) -> Output:
        return Output(x=input.a, y=input.b, z=input.c)


class UserNodeWithOptionAnnotationMismatch(Node):
    """Need to figure out how to handle this case"""

    class Options(BaseModel):
        test_option: bool = Field(False, description="Test option")

    def run(self, input: Input, options: BaseModel) -> Output:
        return Output(x=input.a, y=input.b, z=input.c, option=options.test_option)  # type: ignore # Intentional bad typing


class UserNodeWithMissingAnnotation(Node):
    def run(self, a, b, c) -> Output:
        return Output(x=a, y=b, z=c)


class UserNodeWithNoInputsOrOptions(Node):
    def run(self):
        return None
