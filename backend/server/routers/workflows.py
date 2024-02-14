from ast import alias
from logging import getLogger
from fastapi import APIRouter, Depends, HTTPException
from nodes import workflow
from server.database.tables import get_workflow_table, WorkflowTable, WorkflowID, NodeDataID, NodeID  # type: ignore
from server.utils import omit
from contextlib import contextmanager
from pydantic import BaseModel, ValidationError, Field
from typing import Annotated, Optional, Literal, Any, Type
from nodes import NodeRegistry, get_node_registry, manager
from nodes.base import Edge, Node, NodeData, NodeDataTypes
from nodes.workflow import Workflow
from boto3.dynamodb.conditions import Key, And

logger = getLogger(__name__)

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
    Data: Any

class EdgePostRequest(BaseModel):
    From: Annotated[str, NodeDataID, Field(alias="From"), ]
    To: Annotated[str, NodeDataID, Field(alias="To"), ]


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


def set_data_on_node(node: Node, key: str, type: NodeDataTypes, value: Any) -> None:
    if type == "options":
        if key not in node.options:
            raise HTTPException(
                status_code=400,
                detail=f"'{key}' is not a valid key for {node.address()}   Available Options: {list(node.options)}",
            )
        node.options[key].set(value)
    else:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid Node Data Type: {type}   Available Types: "options"',
        )


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

@router.get('/{workflow_id}/all')
def get_all_workflow_elements(workflow_id:str, table:WorkflowTable = Depends(get_workflow_table)) -> list[WorkflowTable.Workflow | WorkflowTable.Node | WorkflowTable.Edge | WorkflowTable.NodeData]:
    items = table.query(Key(table.partition_key.name).eq(workflow_id))
    return items.items # type: ignore
            

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
def get_nodes_by_workflow(
    workflow_id: str, table: WorkflowTable = Depends(get_workflow_table)
):
    response = table.Node.query(key=workflow_id)
    return response.items


@router.get("/{workflow_id}/nodes/{node_id}", response_model=WorkflowTable.Node)
def get_node_by_id(
    workflow_id: str,
    node_id: str,
    table: WorkflowTable = Depends(get_workflow_table),
):
    node = get_node_object(node_id, workflow_id, table)
    return node


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

@router.delete("/{workflow_id}/nodes/{node_id}")
def delete_node_from_workflow(workflow_id: str, node_id: str, table: WorkflowTable = Depends(get_workflow_table)) -> list[WorkflowTable.Node | WorkflowTable.NodeData]:
    expression = And(Key(table.partition_key.name).eq(workflow_id), Key(table.sort_key.name).begins_with(node_id))
    items: list[WorkflowTable.NodeData | WorkflowTable.Node] = table.query(expression).items #type: ignore
    nodes = [x for x in items if isinstance(x, table.Node)]

    if len(nodes)<1 or len(nodes)>1: 
        raise HTTPException(status_code=404, detail=f'Node not found: {workflow_id}/{node_id}')

    if len(nodes) > 1:
        logger.warning(f'Delete Node: {workflow_id}/{node_id} returned multiple nodes')
        raise HTTPException(status_code=404, detail=f'Node not found: {workflow_id}/{node_id}')
    
    node = nodes[0]
    if node.PartitionKey != workflow_id or node.SortKey != node_id:
        logger.warning(f'Delete Node: {workflow_id}/{node_id} returned a node with a different key. {node.PartitionKey}/{node.SortKey}')
        raise HTTPException(status_code=404, detail=f'Node not found: {workflow_id}/{node_id}')
    
    for item in items:
        logger.debug(f'delete {workflow_id}/{node_id}: Deleted: {item}')
        item.delete()

    return items

@router.get("/{workflow_id}/nodes/{node_id}/data")
def get_node_data(
    workflow_id: Annotated[str, WorkflowID],
    node_id: Annotated[str, NodeID],
    table: WorkflowTable = Depends(get_workflow_table),
) -> list[WorkflowTable.NodeData]:
    exp = Key(table.sort_key.name).begins_with(f"{node_id}#Data-")
    result = table.NodeData.query(key=workflow_id, key_expression=exp)
    return result.items


@router.post("/{workflow_id}/nodes/{node_id}/data")
def add_node_data_to_workflow(
    workflow_id: str,
    node_id: str,
    body: NodeDataPostRequest,
    registry: NodeRegistry = Depends(get_node_registry),
    table: WorkflowTable = Depends(get_workflow_table),
) -> WorkflowTable.NodeData:
    node = get_node_object(node_id, workflow_id, table)
    instance = get_node_class(node.Address, node.Version, registry=registry)
    instance = instance(id=node_id)
    set_data_on_node(instance, body.Key, body.Type, body.Data)
    node_data = table.NodeData.from_node_data(instance.options[body.Key], workflow_id)
    node_data.put()
    return node_data

@router.get("/{workflow_id}/edges")
def get_edges_by_workflow(
    workflow_id: str, table: WorkflowTable = Depends(get_workflow_table)
):
    response = table.Edge.query(key=workflow_id)
    return response.items

@router.post("/{workflow_id}/edges")
def add_edge_to_workflow(
    workflow_id: str,
    body: EdgePostRequest,
    table: WorkflowTable = Depends(get_workflow_table),
):
    edge = table.Edge(PartitionKey=workflow_id, **body.model_dump())
    edge.put()
    return edge

@router.post("/{workflow_id}/run")
def run_workflow(workflow_id, table: WorkflowTable = Depends(get_workflow_table), registry: NodeRegistry = Depends(get_node_registry)):
    workflow_data = table.query(
        Key(table.partition_key.name).eq(workflow_id),
    
    )
    if not workflow_data:
        raise HTTPException(status_code=404, detail=f'No such workflow: {workflow_id}')
    workflow = Workflow()
    nodes: dict[str, Node] = {}
    for item in workflow_data.items: # type: ignore
        if isinstance(item, WorkflowTable.Node):
            nodes[item.ID] = get_node_class(item.Address, item.Version, registry)(id=item.ID)
    for item in workflow_data.items:
        if isinstance(item, WorkflowTable.NodeData):
            set_data_on_node(nodes[item.NodeID], item.Key, item.Type, item.Data)