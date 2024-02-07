from server.database import Table, Item, SortKey, PartitionKey
from shortuuid import uuid
from pydantic import Field, BaseModel, field_validator
from pydantic.fields import computed_field
from typing import Any, Annotated, Self, Literal
from nodes.base import NodeData as _NodeDataClass, NodeDataTypes as _NodeDataTypes

UUID_PATTERN = r"[a-zA-Z0-9]{22}"  # Change this to shortuuid's only

_WorkflowID = Field(
    pattern=rf"Workflow\-{UUID_PATTERN}",
    alias="WorkflowID",
)
_NodeID = Field(
    pattern=rf"Node\-{UUID_PATTERN}",
    alias="NodeID",
)

_NodeDataID = Field(
    pattern=rf"Node\-{UUID_PATTERN}#Data\-{UUID_PATTERN}",
    alias="NodeDataID",
)

_EdgeID = Field(
    pattern=rf"Edge\-{UUID_PATTERN}",
    alias="EdgeID",
)


class WorkflowTable(Table):
    __tablename__ = "Workflows"
    __billing_mode__ = "PAY_PER_REQUEST"
    partition_key = PartitionKey("PartitionKey", "S")
    sort_key = SortKey("SortKey", "S")

    class Workflow(Item):
        PartitionKey: Annotated[
            str,
            Field(default_factory=lambda: f"Workflow-{uuid()}", validate_default=True),
            _WorkflowID,
        ]
        SortKey: Annotated[
            str, Field(default_factory=lambda: None, validate_default=True), _WorkflowID
        ]  # Sort key is set by validator
        Name: str
        Owner: str

        @computed_field
        def ID(self) -> str:
            return self.PartitionKey

        @field_validator("SortKey", mode="before")
        def set_sort_key(cls, v, values):
            return values["PartitionKey"]

    class Node(Item):
        PartitionKey: str = _WorkflowID
        SortKey: Annotated[
            str,
            Field(default_factory=lambda: f"Node-{uuid()}", validate_default=True),
            _NodeID,
        ]
        Version: int
        Address: str
        Manifest: dict[str, Any] = {}

        @computed_field
        def ID(self) -> str:
            return self.SortKey

    class Edge(Item):
        PartitionKey: str = _WorkflowID
        SortKey: str = _EdgeID
        From: str
        To: str

    class NodeData(Item):
        PartitionKey: str = _WorkflowID
        NodeID: str = Field(pattern=UUID_PATTERN)
        SortKey: Annotated[str, _NodeDataID] = ""
        Key: str
        Type: _NodeDataTypes
        Data: dict[str, Any] = Field(
            default_factory=lambda: {}, description="Persisted Node Data"
        )

        @field_validator("SortKey", mode="before")
        def def_set_sort_key(cls, v, values) -> str:
            if not v:
                node = values.get("NodeID")
                assert node, "SortKey requires NodeID"
                v = f"Node-{cls.NodeID}#Data-{uuid()}"
            return v

        @computed_field
        def ID(self) -> str:
            return self.SortKey.replace(f"{self.NodeID}#", "")

        @classmethod
        def from_node_data(cls, node_data: _NodeDataClass) -> Self:
            return cls(
                NodeID=node_data.node.id,
                Data=node_data.value,
                Key=node_data.key,
                Type=node_data.type,
            )


def get_workflow_table() -> WorkflowTable:
    return WorkflowTable()
