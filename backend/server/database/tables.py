from server.database import Table, Item, SortKey, PartitionKey
from shortuuid import uuid
from pydantic import Field, BaseModel, ValidationError, field_validator, ValidationInfo
from pydantic.fields import computed_field
from typing import Any, Annotated, Self, Literal
from nodes.base import (
    NodeData as _NodeDataClass,
    NodeDataTypes,
    NodeDataSchema,
    NodeSchema,
    NodeSchema,
)
from functools import cached_property

UUID_PATTERN = r"[a-zA-Z0-9]{22}"  # Change this to shortuuid's only


WorkflowID = Field(
    pattern=rf"Workflow\-{UUID_PATTERN}",
    alias="WorkflowID",
)
NodeID = Field(
    pattern=rf"Node\-{UUID_PATTERN}",
    alias="NodeID",
)

NodeDataID = Field(
    pattern=rf"Node\-{UUID_PATTERN}#Data\-{UUID_PATTERN}",
    alias="NodeDataID",
)

EdgeID = Field(
    pattern=rf"Edge\-{UUID_PATTERN}",
    alias="EdgeID",
)


class NodeDataHandle(BaseModel):
    NodeID: Annotated[str, NodeID]
    Key: str


class WorkflowTable(Table):
    __tablename__ = "Workflows"
    __billing_mode__ = "PAY_PER_REQUEST"
    partition_key = PartitionKey("PartitionKey", "S")
    sort_key = SortKey("SortKey", "S")

    class Workflow(Item):
        PartitionKey: Annotated[
            str,
            Field(default_factory=lambda: f"Workflow-{uuid()}", validate_default=True),
            WorkflowID,
        ]
        SortKey: Annotated[
            str, Field(default_factory=lambda: None, validate_default=True), WorkflowID
        ]  # Sort key is set by validator
        Name: str
        Owner: str
        Resource: Literal["Workflow"] = "Workflow"

        @computed_field
        @cached_property
        def ID(self) -> str:
            return self.PartitionKey

        @field_validator("SortKey", mode="before")
        def set_sort_key(cls, v, info: ValidationInfo):
            return info.data["PartitionKey"]

    class Node(Item, NodeSchema):
        PartitionKey: str = WorkflowID
        SortKey: Annotated[
            str,
            Field(default_factory=lambda: f"Node-{uuid()}", validate_default=True),
            NodeID,
        ]
        Resource: Literal["Node"] = "Node"

        @computed_field
        @property
        def ID(self) -> str:
            return self.SortKey

    class Edge(Item):
        PartitionKey: str = WorkflowID
        SortKey: Annotated[str, EdgeID, Field(validate_default=True)] = ""
        From: NodeDataHandle
        To: NodeDataHandle
        IsSubset: bool
        Resource: Literal["Edge"] = "Edge"

        @field_validator("SortKey", mode="before")
        def set_sort_key(cls, v, info: ValidationInfo) -> str:
            if not v:
                v = f"Edge-{uuid()}"
            return v

        @computed_field
        @property
        def ID(self) -> str:
            return self.SortKey


def get_workflow_table() -> WorkflowTable:
    return WorkflowTable()
