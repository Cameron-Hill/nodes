from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Union


__all__ = ["Data", "Node", "Node"]

class Data(BaseModel):
    def _inspect():
        a=1


class Options(BaseModel):
    """"""

class Node(ABC):
    @abstractmethod
    def handler(self, data:Data):
        pass



class Action(Node):
    """"""


class Task(Node):
    """What is the correct pattern for this"""

    def handler(self, data:Data, options:Options):
        pass

