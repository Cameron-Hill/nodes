from nodes.base import Node, Option
from pydantic import BaseModel


class TestNode(Node):
    class Options(BaseModel):
        test: str

    # What should we do if self is not called 'self'?
    def run(self, custom_option_label: Options, a: str, b: int) -> str:
        return f"{a}-{b}"


def test_get_input_params():
    inputs = TestNode._get_input_params()
    assert "a" in inputs
    assert "b" in inputs
    assert inputs["a"].annotation == str
    assert inputs["b"].annotation == int
    assert len(inputs) == 2


def test_get_option_params():
    options = TestNode._get_option_params()
    assert "custom_option_label" in options
    assert options["custom_option_label"].annotation == TestNode.Options
    assert len(options) == 1


def test_get_input_params_from_initialized_object():
    node = TestNode()
    inputs = node._get_input_params()
    assert "a" in inputs
    assert "b" in inputs
    assert inputs["a"].annotation == str
    assert inputs["b"].annotation == int
    assert len(inputs) == 2


def test_get_option_params_from_initialized_object():
    node = TestNode()
    options = node._get_option_params()
    assert "custom_option_label" in options
    assert options["custom_option_label"].annotation == TestNode.Options
    assert len(options) == 1


def test_infer_data_type_of_set_option():
    node = TestNode()
