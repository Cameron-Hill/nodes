from server.database import Table, Item, SortKey, PartitionKey
from shortuuid import uuid
from pydantic import Field, BaseModel, validator
from pydantic.fields import computed_field
from typing import Any, Annotated

UUID_PATTERN = r"([a-zA-Z0-9]{22}|[a-zA-Z0-9-]{36})"  # Change this to shortuuid's only

_WorkflowID = Field(pattern=rf"Workflow\-{UUID_PATTERN}", alias="WorkflowID")
_NodeID = Field(
    pattern=rf"Node\-{UUID_PATTERN}",
    validate_default=True,
    alias="NodeID",
)

_NodeDataID = Field(
    pattern=rf"Node\-{UUID_PATTERN}#Data\-{UUID_PATTERN}",
    alias="NodeDataID",
)

_EdgeID = Field(
    # pattern=rf"Edge\-{UUID_PATTERN}",   # Need to update the db to use this pattern
    default_factory=lambda: f"Edge-{uuid()}",
    validate_default=True,
    alias="EdgeID",
)


class WorkflowTable(Table):
    __tablename__ = "Workflows"
    __billing_mode__ = "PAY_PER_REQUEST"
    partition_key = PartitionKey("PartitionKey", "S")
    sort_key = SortKey("SortKey", "S")

    class Workflow(Item):
        PartitionKey: str = _WorkflowID
        SortKey: str = _WorkflowID
        Name: str
        Owner: str

        @computed_field
        def ID(self) -> str:
            return self.PartitionKey.replace("Workflow-", "")

        @validator("PartitionKey")
        def default_partition_key(cls, key) -> str:
            if not key:
                return f"Workflow-{uuid()}"
            else:
                return key

        @validator("SortKey")
        def validate_sort_key(cls, key: str, values):
            return values.get("PartitionKey")

    class Node(Item):
        PartitionKey: str = _WorkflowID
        SortKey: Annotated[
            str,
            Field(
                default_factory=lambda: f"Node-{uuid()}",
            ),
        ] = _NodeID
        Version: int
        Address: str
        Manifest: dict[str, Any] = {}

        def ID(self) -> str:
            return self.PartitionKey.replace("Node-", "")

    class Edge(Item):
        PartitionKey: str = _WorkflowID
        SortKey: str = _EdgeID
        From: str
        To: str

    class NodeData(Item):
        PartitionKey: str = _WorkflowID
        ID: str = Field(pattern=UUID_PATTERN, default_factory=lambda: uuid())
        NodeID: str = Field(pattern=UUID_PATTERN)
        Data: dict[str, Any] = Field(
            default_factory=lambda: {}, description="Persisted Node Data"
        )

        def SortKey(self) -> Annotated[str, _NodeDataID]:
            return f"Node-{self.NodeID}#Data-{self.ID}"


def get_workflow_table() -> WorkflowTable:
    return WorkflowTable()
