import os
from nodes.base import Node, NodeSource
from importlib import import_module
from inspect import getmembers, isclass
from logging import getLogger
from contextlib import contextmanager

logger = getLogger(__name__)

__all__ = ["NodeManager"]


@contextmanager
def syspath(path):
    import sys

    sys.path.insert(0, path)
    yield
    sys.path.remove(path)


def _is_node_class(member):
    return (
        isclass(member)
        and issubclass(member, Node)
        and member != Node
        and member != NodeSource
    )


class Module(NodeSource):
    def resolve_nodes(self) -> None:
        logger.debug(f"Resolving nodes from module {self.source}")
        module = import_module(self.source)
        members = getmembers(module, _is_node_class)
        for _, node in members:
            logger.debug(f"Adding node {node} from module {self.source}")
            self.add(node)


class File(NodeSource):
    def resolve_nodes(self) -> None:
        if self.source.endswith(".py"):
            logger.debug(f"Resolving nodes from file {self.source}")
            dirname = os.path.dirname(self.source)
            basename = os.path.basename(self.source)
            module_name = os.path.splitext(basename)[0]
            with syspath(dirname):
                module = import_module(module_name)
                members = getmembers(module, _is_node_class)
                for _, node in members:
                    logger.debug(f"Adding node {node} from file {self.source}")
                    self.add(node)


def source_factory(source: str) -> NodeSource:
    if os.path.isfile(source):
        return File(source)
    else:
        return Module(source)


class NodeManager:
    DEFAULT_SOURCES = ["nodes.builtins"]

    def __init__(self) -> None:
        self._sources: set[NodeSource] = set()
        self._nodes: set[Node] = set()

        for source in self.DEFAULT_SOURCES:
            self.add_source(source)

    @property
    def sources(self) -> set[NodeSource]:
        return self._sources

    @property
    def nodes(self) -> set[Node]:
        return {node for source in self._sources for node in source.nodes}.union(
            self._nodes
        )

    def get_node_by_id(self, id: str) -> Node:
        for node in self.nodes:
            if node.address() == id:
                return node
        raise ValueError(f"Node with id {id} not found")

    def add_source(self, source: str) -> None:
        self._sources.add(source_factory(source))

    def add_node(self, node: Node):
        self._nodes.add(node)
