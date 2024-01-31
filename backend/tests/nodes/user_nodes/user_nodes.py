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
    option: bool | None = Field(None, description="Test Output value: option")


class UserNode(Node):
    class Options(BaseModel):
        test_option: bool = Field(False, description="Test option")

    def run(self, input: Input, options: Options) -> Output:
        return Output(x=input.a, y=input.b, z=input.c, option=options.test_option)


class UserNodeWithMultipleInputs(Node):
    def run(self, a: str, b: int, c: float = 20) -> Output:
        return Output(x=a, y=b, z=c)


class UserNodeNoOptions(Node):
    def run(self, input: Input) -> Output:
        return Output(x=input.a, y=input.b, z=input.c)


class UserNodeWithOptionAnnotationMismatch(Node):
    """Need to figure out how to handle this case"""

    class Options(BaseModel):
        test_option: bool = Field(False, description="Test option")

    def run(self, input: Input, options: BaseModel) -> Output:
        return Output(x=input.a, y=input.b, z=input.c, option=options.test_option)


class UserNodeWithMissingAnnotation(Node):
    def run(self, a, b, c) -> Output:
        return Output(x=a, y=b, z=c)


class UserNodeWithNoInputsOrOptions(Node):
    def run(self):
        return None
