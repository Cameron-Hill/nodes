import os
import pytest
from nodes.engine import NodeEngine, File

USER_NODES = os.path.join(os.path.dirname(__file__), "user_nodes", "user_nodes.py")


@pytest.fixture
def engine():
    return NodeEngine()


def test_automatic_collection_of_built_in_sources(engine):
    assert len(engine.sources) == 1
    assert list(engine.sources)[0].source == "nodes.builtins"


def test_add_user_source_from_file(engine):
    assert len(engine.sources) == 1
    original_nodes_len = len(engine.nodes)
    engine.add_source(USER_NODES)
    assert len(engine.sources) == 2
    user_node_source = [x for x in engine.sources if x.source == USER_NODES][0]
    assert isinstance(user_node_source, File)
    assert len(engine.nodes) == original_nodes_len + 1
    assert "UserNode" in [x.label() for x in engine.nodes]
