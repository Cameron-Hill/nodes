import logging
from traceback import format_exc
from shortuuid import uuid
from pydantic import BaseModel, Field
from typing import Generator, Annotated, Literal
from nodes.base import Node, NodeData, Edge, NodeSchema, EdgeSchema
from nodes.patches import jsonsubschema
from nodes.errors import NodeDataSchemaValidationException, NodeDataNotSetException
from datetime import datetime

logger = logging.getLogger(__name__)

UUID_PATTERN = r"[a-zA-Z0-9]{22}"  # Change this to shortuuid's only
"""
Rethink how we're doing validations. We should run all validations that we can
and return an exception with a json body that can be passed to downstream systems.
To be honest, we really want a good exception system that can bubble up to the end user.
"""

RunStatusTypes = Literal["Running", "Success", "Failed", "Cancelled"]


class ErrorDetails(BaseModel):
    Message: str
    Class: str
    Traceback: str


class RunDetails(BaseModel):
    ID: Annotated[
        str,
        Field(
            pattern=f"Run-{UUID_PATTERN}",
            default_factory=lambda: f"Run-{uuid()}",
            validate_default=True,
        ),
    ] = ""
    StartedOn: datetime
    FinishedOn: datetime
    Status: RunStatusTypes
    FailureDetails: ErrorDetails | None = None
    NodesExecuted: int


class WorkflowSchema(BaseModel):
    ID: Annotated[
        str,
        Field(
            pattern=f"Workflow-{UUID_PATTERN}",
            default_factory=lambda: f"Workflow-{uuid()}",
            validate_default=True,
        ),
    ] = ""
    Nodes: list[NodeSchema]
    Edges: list[EdgeSchema]
    LastRunDetails: RunDetails | None = None


class Workflow:
    """
    There can only be once instance of a node within a workflow.
    Many edges can be created from an output.
    An input may only have one edge.
    All options in a workflow must be set before it can be run.

    We traverse the graph, breadth first, executing nodes and validating the Node data along the edges.
    """

    def __init__(self, id=None) -> None:
        self.id = id
        self.nodes: set[Node] = set()
        self.edges: set[Edge] = set()
        self.last_run_details: RunDetails | None = None

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

    def get_node_by_id(self, id: str) -> Node:
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

    def run(self) -> RunDetails:
        logger.info(f'Validating workflow: {self.id if self.id else ""}')
        started_on = datetime.now()
        executed = 0
        try:
            self.validate()
            for node in self.traverse():
                node.call()
                executed += 1
                for edge in self.edges:
                    if edge.source == node.output:
                        edge.target.set(node.output.value)
            run_details = RunDetails(
                StartedOn=started_on,
                FinishedOn=datetime.now(),
                Status="Success",
                NodesExecuted=executed,
            )
        except Exception as e:
            run_details = RunDetails(
                StartedOn=started_on,
                FinishedOn=datetime.now(),
                Status="Failed",
                FailureDetails=ErrorDetails(
                    Message=str(e),
                    Class=type(e).__name__,
                    Traceback=format_exc(),
                ),
                NodesExecuted=executed,
            )
        self.last_run_details = run_details
        return run_details

    def schema(self) -> WorkflowSchema:
        return WorkflowSchema(
            ID=self.id or uuid(),
            Nodes=[node.schema() for node in self.nodes],
            Edges=[edge.schema() for edge in self.edges],
            LastRunDetails=self.last_run_details,
        )
