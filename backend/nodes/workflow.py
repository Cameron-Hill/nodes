from nodes.base import Node, NodeData, Edge
from nodes.patches import jsonsubschema


class NodeDataException(Exception):
    """"""


class NodeDataSchemaValidationException(NodeDataException):
    """
    Raised when a node data is not valid.
    """


class NodeDataNotSetException(NodeDataException):
    """
    Raised when a node data is not set.
    """


class Workflow:
    """
    There can only be once instance of a node within a workflow.
    Many edges can be created from an output.
    An input may only have one edge.

    We traverse the graph, breadth first, to determine the order of execution.
    """

    def __init__(self) -> None:
        self.nodes: set[Node] = set()
        self.edges: set[Edge] = set()

    @property
    def roots(self) -> set[Node]:
        roots = self.nodes.copy()
        for edge in self.edges:
            roots.discard(edge.target.node)
        return roots

    def add_node(self, node: Node) -> None:
        self.nodes.add(node)

    def add_edge(self, source: NodeData, target: NodeData):
        assert source.type == "output", "Source must be a node output"
        assert target.type == "input", "Target must be a node input"
        assert self._is_compatible(
            source, target
        ), "Source and target are not compatible"
        self.edges.add(Edge(source, target))

    @staticmethod
    def _is_compatible(source: NodeData, target: NodeData) -> bool:
        return jsonsubschema.isSubschema(
            source.adapter.json_schema(), target.adapter.json_schema()
        )

    def validate(self):
        for edge in self.edges:
            if not self._is_compatible(edge.source, edge.target):
                raise NodeDataSchemaValidationException(
                    f"Source {edge.source.node} and target {edge.target.node} are not compatible"
                )

    def run(self):
        self.validate()
        nodes = self.roots
