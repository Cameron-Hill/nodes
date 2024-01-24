import os
from nodes.base import Node, NodeSource
from importlib import import_module
from inspect import getmembers, isclass
from logging import getLogger
from contextlib import contextmanager

logger = getLogger(__name__)

__all__ = ["NodeEngine"]


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
    def resolve_nodes(self) -> set[Node]:
        logger.debug(f"Resolving nodes from module {self.source}")
        module = import_module(self.source)
        members = getmembers(module, _is_node_class)
        for _, node in members:
            logger.debug(f"Adding node {node} from module {self.source}")
            self.add(node)


class File(NodeSource):
    def resolve_nodes(self) -> set[Node]:
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


class NodeEngine:
    DEFAULT_SOURCES = ["nodes.builtins"]

    def __init__(self) -> None:
        self._sources: set[NodeSource] = set()

        for source in self.DEFAULT_SOURCES:
            self.add_source(source)

    @property
    def sources(self) -> set[str]:
        return self._sources

    @property
    def nodes(self) -> set[Node]:
        return {node for source in self._sources for node in source.nodes}

    def add_source(self, source: str) -> None:
        self._sources.add(source_factory(source))
