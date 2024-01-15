from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Union, Set, TypeVar


__all__ = ["Data", "Node", "Action", "Task"]

NodeType = TypeVar("NodeType", bound="Node")


class Data(BaseModel):
    def _inspect():
        a = 1


class Options(BaseModel):
    """"""


class Node(ABC):
    def __init__(self):
        self.children: Set[Node] = set()
        self.parents: Set[Node] = set()

    def add_child(self, child: NodeType):
        self.children.add(child)
        child.parents.add(self)

    def add_parent(self, parent: NodeType):
        self.parents.add(parent)
        parent.children.add(self)

    def remove_child(self, child: NodeType):
        self.children.remove(child)
        child.parents.remove(self)

    def remove_parent(self, parent: NodeType):
        self.parents.remove(parent)
        parent.children.remove(self)

    @abstractmethod
    def handler(self, data: Data, options: Options):
        pass

    def options(self, data_class: type[Data]) -> Options:
        return Options()


class Action(Node):
    """"""


class Task(Node):
    """What is the correct pattern for this"""
