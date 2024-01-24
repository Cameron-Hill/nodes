from nodes.base import Node, Option
from pydantic import Field, BaseModel


class Input(BaseModel):
    a: str = Field(..., description="Test value: a")
    b: int = Field(..., description="Test value: b")
    c: float = Field(..., description="Test value: c")


class Output(BaseModel):
    x: str = Field(..., description="Test Output value: x")
    y: int = Field(..., description="Test Output value: y")
    z: float = Field(..., description="Test Output value: z")
    option: bool = Field(..., description="Test Output value: option")


class UserNode(Node):
    class Options(BaseModel):
        test_option: Option[bool] = Field(False, description="Test option")

    def run(self, input: Input, options: BaseModel | None) -> Output:
        return Output(x=input.a, y=input.b, z=input.c, option=options.test_option)
