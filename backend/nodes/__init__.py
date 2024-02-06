from .patches import *
from .base import Node
from functools import lru_cache as _lru_cache
from .manager import NodeManager

NodeRegistry = dict[str, dict[int, Node]]


@_lru_cache
def get_node_registry() -> NodeRegistry:
    # Get sources from somewhere
    manager = NodeManager()
    registry = {}
    for node in manager.nodes:
        registry.setdefault(node.address(), {})
        registry[node.address()][node.__version__] = node
    return registry
