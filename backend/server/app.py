from functools import lru_cache
from nodes.manager import NodeManager
from nodes.base import NodeSchema


@lru_cache()
def get_node_manager() -> NodeManager:
    # todo: load custom sources
    return NodeManager()
