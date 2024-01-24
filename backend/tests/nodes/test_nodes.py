import os
import pytest
from nodes.manager import NodeManager

USER_NODES = os.path.join(os.path.dirname(__file__), "user_nodes", "user_nodes.py")


@pytest.fixture
def UserNode():
    manager = NodeManager()
    manager.add_source(USER_NODES)
    return manager.get_node_by_id("user_nodes.UserNode")


def test_schema_generation_from_user_node_class(UserNode):
    schema = UserNode.node_json_schema()
    assert schema.id == "user_nodes.UserNode"
    assert schema.label == "UserNode"
    assert schema.version == 0
