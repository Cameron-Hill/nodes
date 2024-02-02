import os
import pytest
from pydantic import BaseModel, PydanticUserError, ValidationError
from nodes.manager import NodeManager
from contextlib import contextmanager
from inspect import isclass
from nodes.base import Node

USER_NODES = os.path.join(os.path.dirname(__file__), "user_nodes", "user_nodes.py")


@contextmanager
def expect_exception(exception_or_any):
    exception_class = isclass(exception_or_any) and (
        issubclass(exception_or_any, Exception) or exception_or_any == Exception
    )
    if exception_class or isinstance(exception_or_any, Exception):
        with pytest.raises(exception_or_any) as e:  # type: ignore
            yield e
    else:
        yield None


@pytest.fixture
def manager():
    return NodeManager()


@pytest.fixture
def UserNode(manager) -> Node:
    manager.add_source(USER_NODES)
    return manager.get_node_by_id("user_nodes.UserNode")


@pytest.mark.parametrize(
    "node_id,input,options,expected",
    [
        (
            "user_nodes.UserNode",
            {"input": {"a": "test", "b": 1, "c": 1.0}},
            {"test_option": True},
            {"x": "test", "y": 1, "z": 1.0, "option": True},
        ),
        (
            "user_nodes.UserNodeWithMultipleInputs",
            {"a": "test", "b": 1, "c": 1.0},
            {},
            {"x": "test", "y": 1, "z": 1.0, "option": None},
        ),
        (
            "user_nodes.UserNodeNoOptions",
            {"input": {"a": "test", "b": 1, "c": 1.0}},
            {},
            {"x": "test", "y": 1, "z": 1.0, "option": None},
        ),
        (
            "user_nodes.UserNodeWithOptionAnnotationMismatch",
            {"input": {"a": "test", "b": 1, "c": 1.0}},
            {},
            PydanticUserError,
        ),
        (
            "user_nodes.UserNodeWithMissingAnnotation",
            {"a": "test", "b": 1, "c": 1.0},
            {},
            ValidationError,
        ),
        (
            "user_nodes.UserNodeWithNoInputsOrOptions",
            {},
            {},
            None,
        ),
    ],
)
def test_call_node_with_input_and_options(manager, node_id, input, options, expected):
    with expect_exception(expected):
        manager.add_source(USER_NODES)
        node = manager.get_node_by_id(node_id)
        node = node()
        output = node.call(options=options, **input)
        if isinstance(output, BaseModel):
            output = output.model_dump()
        assert output == expected


def test_schema_generation_from_user_node_class(UserNode):
    schema = UserNode.schema()
    assert schema.address == "user_nodes.UserNode"
    assert schema.label == "UserNode"
    assert schema.version == 0


def test_schema_generation_for_builtin_node_classes(manager):
    for node in manager.nodes:
        schema = node.schema()
        assert schema.address == node.address()
        assert schema.label == node.label()
        assert schema.version == node.__version__


def test_initialize_user_node_with_input_data(UserNode):
    node = UserNode()
    with pytest.raises(AssertionError):
        assert node.data["input"].value.a == "test"


def test_call_node(UserNode):
    node = UserNode()
    output = node.call(input={"a": "test", "b": 1, "c": 1.0})
    assert output.x == "test"
    assert output.y == 1
    assert output.z == 1.0
    assert output.option is False


def test_call_node_with_no_options(manager):
    manager.add_source(USER_NODES)
    node = manager.get_node_by_id("user_nodes.UserNodeNoOptions")
    node = node()
    output = node.call(input={"a": "test", "b": 1, "c": 1.0})
    assert output.x == "test"
    assert output.y == 1
    assert output.z == 1.0
    assert output.option is None


def test_call_user_node_with_multiple_inputs(manager):
    manager.add_source(USER_NODES)
    node = manager.get_node_by_id("user_nodes.UserNodeWithMultipleInputs")
    node = node()
    output = node.call(**{"a": "test", "b": 1, "c": 1.0})
    assert output.x == "test"
    assert output.y == 1
    assert output.z == 1.0
    assert output.option is None
    assert isinstance(output, BaseModel)


def test_node_with_no_type_def(manager):
    manager.add_source(USER_NODES)
    node = manager.get_node_by_id("user_nodes.UserNodeWithNoInputsOrOptions")
    node = node()
    output = node.call()
    assert output is None


def test_nod_get_options(manager):
    manager.add_source(USER_NODES)
    node = manager.get_node_by_id("user_nodes.UserNode")
    node = node()
    assert node.options
