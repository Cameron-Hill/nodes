import pytest
from nodes.manager import NodeManager


@pytest.fixture
def manager():
    return NodeManager()


"""A collection of tests for the Producer nodes."""

# fmt: off
@pytest.mark.parametrize(
    "node_id, input, options, expected_output",
    [
        ("nodes.builtins.producers.StringProducer", None, {"value": "test"}, "test"),
        ("nodes.builtins.producers.IntProducer", None, {"value": 1}, 1),
        ("nodes.builtins.producers.FloatProducer", None, {"value": 1.0}, 1.0),
        ("nodes.builtins.producers.BoolProducer", None, {"value": True}, True),
    ],
)
def test_producers(manager, node_id, input, options, expected_output):
    """Test the Producer nodes."""
    node = manager.get_node_by_id(node_id)
    node = node()
    output = node.call(input=input, options=options)
    assert output == expected_output
