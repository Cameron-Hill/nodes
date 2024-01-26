import os
import pytest
from nodes.manager import NodeManager, File

USER_NODES = os.path.join(os.path.dirname(__file__), "user_nodes", "user_nodes.py")


@pytest.fixture
def manager():
    return NodeManager()


def test_automatic_collection_of_built_in_sources(manager):
    assert len(manager.sources) == 1
    assert list(manager.sources)[0].source == "nodes.builtins"


def test_add_user_source_from_file(manager):
    assert len(manager.sources) == 1
    original_nodes_len = len(manager.nodes)
    manager.add_source(USER_NODES)
    assert len(manager.sources) == 2 
    user_node_source = [x for x in manager.sources if x.source == USER_NODES][0]
    assert isinstance(user_node_source, File)
    assert len(manager.nodes) > original_nodes_len
    assert "UserNode" in [x.label() for x in manager.nodes]


def test_get_node_by_id(manager):
    manager.add_source(USER_NODES)
    node = manager.get_node_by_id("user_nodes.UserNode")
    assert node.label() == "UserNode"
