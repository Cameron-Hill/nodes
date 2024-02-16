import dis
from typing import Generator
from nodes.base import Node, NodeData, Edge
from nodes.patches import jsonsubschema
from nodes.errors import NodeDataSchemaValidationException, NodeDataNotSetException

"""
Rethink how we're doing validations. We should run all validations that we can
and return an exception with a json body that can be passed to downstream systems.
To be honest, we really want a good exception system that can bubble up to the end user.
"""



class Workflow:
    """
    There can only be once instance of a node within a workflow.
    Many edges can be created from an output.
    An input may only have one edge.
    All options in a workflow must be set before it can be run.

    We traverse the graph, breadth first, executing nodes and validating the Node data along the edges.
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

    def reset(self):
        self.seen = set()

    def add_node(self, node: Node) -> None:
        self.nodes.add(node)

    def get_node_by_id(self, id:str) -> Node:
        for node in self.nodes:
            if node.id == id:
                return node
        raise KeyError(id)

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
        for node in self.nodes:
            if not node.options_set:
                raise NodeDataNotSetException(f"Node {node} has unset options.")

    def traverse(self) -> Generator[Node, None, None]:
        """Breadth first traversal,"""
        nodes = self.nodes.copy()
        discard = []
        while len(nodes) > 0:
            for node in nodes:
                if node.ready:
                    yield node
                    discard.append(node)
            if not discard:
                raise Exception("No nodes are ready to run.")
            for node in discard:
                nodes.discard(node)

    def run(self):
        self.validate()
        for node in self.traverse():
            node.call()
            for edge in self.edges:
                if edge.source == node.output:
                    edge.target.set(node.output.value)
        a=1