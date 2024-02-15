from server.database import Table, Item, SortKey, PartitionKey
from shortuuid import uuid
from pydantic import Field, BaseModel, ValidationError, field_validator, ValidationInfo
from pydantic.fields import computed_field
from typing import Any, Annotated, Self, Literal
from nodes.base import NodeData as _NodeDataClass, NodeDataTypes, NodeDataSchema, NodeSchema, NodeSchema
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
        @computed_field
        @property
        def ID(self) -> str:
            return self.SortKey

    class Edge(Item):
        PartitionKey: str = WorkflowID
        SortKey: Annotated[str, EdgeID, Field(validate_default=True)] = ""
        From: str
        To: str
        
        @field_validator("SortKey", mode="before")
        def set_sort_key(cls, v, info: ValidationInfo) -> str:
            if not v:
                v = f"#Edge-{uuid()}"
            return v  
 
        @computed_field
        def ID(self) -> str:
            return self.SortKey

#    class NodeData(Item):
#        PartitionKey: str = WorkflowID
#        NodeID: str = Field(pattern=UUID_PATTERN)
#        SortKey: Annotated[str, NodeDataID, Field(validate_default=True)] = ""
#        Key: str
#        Type: NodeDataTypes
#        Data: Any = Field(
#            ...,
#            description="The data value for the node data. This must be compatible with the node data schema",
#        )
#
#        @field_validator("SortKey", mode="before")
#        def set_sort_key(cls, v, info: ValidationInfo) -> str:
#            if not v:
#                node = info.data.get("NodeID")
#                assert node, "NodeData SortKey requires NodeID"
#                v = f"{node}#Data-{uuid()}"
#            return v
#
#        @computed_field
#        def ID(self) -> str:
#            return self.SortKey.replace(f"{self.NodeID}#", "")
#
#        @classmethod
#        def from_node_data(cls, node_data: _NodeDataClass, workflow_id: str) -> Self:
#            return cls(
#                PartitionKey=workflow_id,
#                NodeID=node_data.node.id,
#                Data=node_data.value,
#                Key=node_data.key,
#                Type=node_data.type,
#            )
#
#
def get_workflow_table() -> WorkflowTable:
    return WorkflowTable()