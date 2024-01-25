import os
import pytest
from pydantic import BaseModel
from nodes.manager import NodeManager
from nodes.base import Node

USER_NODES = os.path.join(os.path.dirname(__file__), "user_nodes", "user_nodes.py")


@pytest.fixture
def manager():
    return NodeManager()


@pytest.fixture
def UserNode(manager) -> Node:
    manager.add_source(USER_NODES)
    return manager.get_node_by_id("user_nodes.UserNode")


def test_schema_generation_from_user_node_class(UserNode):
    schema = UserNode.schema()
    assert schema.id == "user_nodes.UserNode"
    assert schema.label == "UserNode"
    assert schema.version == 0


def test_schema_generation_for_builtin_node_classes(manager):
    for node in manager.nodes:
        schema = node.schema()
        assert schema.id == node.id()
        assert schema.label == node.label()
        assert schema.version == node.__version__


def test_initialize_user_node_with_input_data(UserNode):
    node = UserNode(inputs={"a": "test", "b": 1, "c": 1.0})
    assert node._inputs.input == "test"


def test_call_node(UserNode):
    node = UserNode(input={"a": "test", "b": 1, "c": 1.0})
    output = node.call()
    assert isinstance(output, BaseModel)
    assert output.x == "test"
    assert output.y == 1
    assert output.z == 1.0
    assert output.option is False
