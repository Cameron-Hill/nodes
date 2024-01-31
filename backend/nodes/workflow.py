from nodes.base import Node, NodeData


class Workflow:
    def __init__(self) -> None:
        self.nodes: set[Node] = set()
        self.edges: set[tuple[NodeData, NodeData]] = set()

    def add_node(self, node: Node) -> None:
        self.nodes.add(node)

    def add_edge(self, source: NodeData, target: NodeData):
        self.edges.add((source, target))
