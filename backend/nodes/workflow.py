from nodes.base import Node


class Workflow:
    def __init__(self) -> None:
        pass

    def add_node(self, node: Node) -> None:
        raise NotImplemented
    
    def add_edge(self, source:Node, target:Node):
        raise NotImplemented

