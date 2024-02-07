from fastapi import APIRouter, Depends, HTTPException
from server.database.tables import get_workflow_table, WorkflowTable  # type: ignore
from server.utils import omit
from contextlib import contextmanager
from pydantic import BaseModel
from typing import Optional, Literal, Any, Type
from nodes import NodeRegistry, get_node_registry
from nodes.base import Node


@omit("PartitionKey", "SortKey", "WorkflowID", "ID")
class WorkflowPostRequest(WorkflowTable.Workflow): ...


@omit("PartitionKey", "SortKey", "WorkflowID", "NodeID", "ID", "Manifest")
class WorkflowNodePostRequest(WorkflowTable.Node): ...


class WorkflowPatchRequest(BaseModel):
    Name: Optional[str]
    Owner: Optional[str]


class NodeDataPostRequest(BaseModel):
    Type: Literal["options"]
    Key: str
    Value: Any


router = APIRouter(prefix="/workflows", tags=["workflows"])


def get_workflow_object(
    workflow_id: str,
    table: WorkflowTable,
) -> WorkflowTable.Workflow:
    workflow = table.Workflow.get(key=workflow_id, sort_key=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=404, detail=f"Workflow not found: {workflow_id}"
        )
    return workflow


def get_node_class(address: str, version: int, registry: NodeRegistry) -> Type[Node]:
    try:
        return registry[address][version]
    except KeyError as e:
        if address in registry:
            versions = ", ".join(str(x) for x in registry[address])
            msg = f'Node version "{version}" not found.  For Node: {address}.  Available Versions: {versions}'
        else:
            msg = f"Node not found: {address}"
        raise HTTPException(status_code=404, detail=msg)


def get_node_object(
    node_id: str,
    workflow_id: str,
    table: WorkflowTable,
) -> WorkflowTable.Node:
    node = table.Node.get(key=workflow_id, sort_key=node_id)
    if not node:
        raise HTTPException(
            status_code=404, detail=f"Node not found: {workflow_id}  {node_id}"
        )
    return node

def get_data_node_instance(type: Literal['options', 'input', 'output'], key: str, instance: Node):


@router.get("/", response_model=list[WorkflowTable.Workflow])
def get_workflows(table: WorkflowTable = Depends(get_workflow_table)):
    scanned_items = table.Workflow.scan()
    return scanned_items.items


@router.post("/", response_model=WorkflowTable.Workflow)
def create_workflow(
    body: WorkflowPostRequest, table: WorkflowTable = Depends(get_workflow_table)
):
    workflow = table.Workflow(**body.model_dump())
    workflow.put()
    return workflow


@router.get("/{workflow_id}", response_model=WorkflowTable.Workflow)
def get_workflow_by_id(
    workflow_id: str, table: WorkflowTable = Depends(get_workflow_table)
):
    workflow = get_workflow_object(workflow_id, table)
    return workflow


@router.patch("/{workflow_id}", response_model=WorkflowTable.Workflow)
def update_workflow_by_id(
    workflow_id: str,
    body: WorkflowPatchRequest,
    table: WorkflowTable = Depends(get_workflow_table),
):
    workflow = get_workflow_object(workflow_id, table)
    workflow.put(**body.model_dump())
    return workflow


@router.get("/{workflow_id}/nodes", response_model=list[WorkflowTable.Node])
def get_nodes_by_workflow_id(
    workflow_id: str, table: WorkflowTable = Depends(get_workflow_table)
):
    response = table.Node.query(key=workflow_id)
    return response.items


@router.post("/{workflow_id}/nodes")
def add_node_to_workflow(
    workflow_id: str,
    body: WorkflowNodePostRequest,
    table: WorkflowTable = Depends(get_workflow_table),
    node_registry: NodeRegistry = Depends(get_node_registry),
):
    workflow = get_workflow_object(workflow_id, table)
    node_obj = get_node_class(body.Address, body.Version, registry=node_registry)
    node = table.Node(
        PartitionKey=workflow_id,
        **body.model_dump(),
        Manifest=node_obj.schema().model_dump(),
    )
    node.put()
    return node

@router.post("/{workflow_id}/nodes/{node_id}/data")
def add_node_data_to_workflow(
    workflow_id: str,
    node_id: str,
    body: NodeDataPostRequest,
    registry: NodeRegistry = Depends(get_node_registry),
    table: WorkflowTable = Depends(get_workflow_table),
):
    node = get_node_object(node_id, workflow_id, table)
    instance = get_node_class(node.Address, node.Version, registry=registry)
    instance = instance(id=node_id)

    if body.Type == "options":
        instance.options[body.Key].set(body.Value)
    else:
        raise HTTPException(
            status_code=400, detail=f"Invalid Node Data Type: {body.Type}   Available Types: \"options\""
        )

    node_data = table.NodeData(
        PartitionKey=workflow_id,
        NodeID=node_id,
    )
    node_data.put()
    return node_data
