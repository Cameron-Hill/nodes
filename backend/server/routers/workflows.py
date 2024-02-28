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
from nodes.workflow import Workflow, WorkflowSchema
from boto3.dynamodb.conditions import Key, And
from server.responses import Error404, Error500

logger = getLogger(__name__)


@omit("PartitionKey", "SortKey", "WorkflowID", "ID")
class WorkflowPostRequest(WorkflowTable.Workflow): ...


class WorkflowNodePostRequest(BaseModel):
    Address: str = Field(
        ..., title="Node Address", examples=["nodes.builtins.producers.StringProducer"]  # type: ignore
    )
    Version: int


class WorkflowPatchRequest(BaseModel):
    Name: Optional[str]
    Owner: Optional[str]


class NodeDataHandle(BaseModel):
    NodeID: Annotated[str, NodeID]
    Key: str


class NodeDataPostRequest(BaseModel):
    Key: str
    Type: Literal["options"]
    Data: Any


class EdgePostRequest(BaseModel):
    From: NodeDataHandle
    To: NodeDataHandle


router = APIRouter(prefix="/workflows", tags=["workflows"], redirect_slashes=True)


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


def get_edge_object(
    edge_id: str,
    workflow_id: str,
    table: WorkflowTable
) -> WorkflowTable.Edge:
    edge = table.Edge.get(key=workflow_id, sort_key=edge_id)
    if not edge:
        raise HTTPException(
            status_code=404, detail=f"edge not found: {workflow_id}  {edge_id}"
        )
    return edge


def get_node_instance_by_id(
    node_id: str, workflow_id: str, table: WorkflowTable, registry: NodeRegistry
) -> Node:
    node = get_node_object(node_id, workflow_id, table)
    return get_node_class(node.Address, node.Version, registry)(id=node_id)


def get_node_data_from_instance(node: Node, key: str) -> NodeData:
    try:
        return node.data[key]
    except KeyError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Node {node.address()} has no data with key: {key}.  Available Keys: {list(node.data)}",
        )


def _set_data_on_node(node: Node, key: str, type: NodeDataTypes, value: Any) -> None:
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


@router.get("/", response_model=list[WorkflowTable.Workflow], responses={500: Error500})
def get_workflows(table: WorkflowTable = Depends(get_workflow_table)):
    scanned_items = table.Workflow.scan()
    return scanned_items.items


@router.post("/", response_model=WorkflowTable.Workflow, responses={500: Error500})
def create_workflow(
    body: WorkflowPostRequest, table: WorkflowTable = Depends(get_workflow_table)
):
    workflow = table.Workflow(**body.model_dump())
    workflow.put()
    return workflow


@router.get(
    "/{workflow_id}",
    response_model=WorkflowTable.Workflow,
    responses={404: Error404, 500: Error500},
)
def get_workflow_by_id(
    workflow_id: str, table: WorkflowTable = Depends(get_workflow_table)
):
    workflow = get_workflow_object(workflow_id, table)
    return workflow


@router.delete("/{workflow_id}", responses={404: Error404, 500: Error500})
def delete_workflow_by_id(
    workflow_id: str,
    dryRun: bool = False,
    table: WorkflowTable = Depends(get_workflow_table),
) -> list[WorkflowTable.Node | WorkflowTable.Edge | WorkflowTable.Workflow]:
    get_workflow_object(workflow_id, table)  # Raises 404 if not found
    response = table.query(Key(table.partition_key.name).eq(workflow_id))
    for item in response.items:
        if not dryRun:
            item.delete()
        logger.debug(
            f"{'DRY_RUN:  'if dryRun else ''}delete {workflow_id}: Deleted: {item}"
        )
    return response.items  # type: ignore


@router.get("/{workflow_id}/all", responses={404: Error404, 500: Error500})
def get_all_workflow_elements(
    workflow_id: str, table: WorkflowTable = Depends(get_workflow_table)
) -> list[WorkflowTable.Workflow | WorkflowTable.Node | WorkflowTable.Edge]:
    items = table.query(Key(table.partition_key.name).eq(workflow_id))
    return items.items  # type: ignore


@router.patch(
    "/{workflow_id}",
    response_model=WorkflowTable.Workflow,
    responses={404: Error404, 500: Error500},
)
def update_workflow_by_id(
    workflow_id: str,
    body: WorkflowPatchRequest,
    table: WorkflowTable = Depends(get_workflow_table),
):
    workflow = get_workflow_object(workflow_id, table)
    workflow.put(**body.model_dump())
    return workflow


@router.get(
    "/{workflow_id}/nodes",
    response_model=list[WorkflowTable.Node],
    responses={404: Error404, 500: Error500},
)
def get_nodes_by_workflow(
    workflow_id: str, table: WorkflowTable = Depends(get_workflow_table)
):
    response = table.Node.query(key=workflow_id)
    return response.items


@router.get(
    "/{workflow_id}/nodes/{node_id}",
    response_model=WorkflowTable.Node,
    responses={404: Error404, 500: Error500},
)
def get_node_by_id(
    workflow_id: str,
    node_id: str,
    table: WorkflowTable = Depends(get_workflow_table),
):
    node = get_node_object(node_id, workflow_id, table)
    return node


@router.post("/{workflow_id}/nodes", responses={404: Error404, 500: Error500})
def add_node_to_workflow(
    workflow_id: str,
    body: WorkflowNodePostRequest,
    table: WorkflowTable = Depends(get_workflow_table),
    node_registry: NodeRegistry = Depends(get_node_registry),
):
    get_workflow_object(workflow_id, table)  # Raises 404 if not found
    node_obj = get_node_class(body.Address, body.Version, registry=node_registry)

    node = table.Node(PartitionKey=workflow_id, **node_obj.class_schema().model_dump())
    node.put()
    return node


@router.delete(
    "/{workflow_id}/nodes/{node_id}", responses={404: Error404, 500: Error500}
)
def delete_node_from_workflow(
    workflow_id: str, node_id: str, table: WorkflowTable = Depends(get_workflow_table)
) -> list[WorkflowTable.Node]:
    expression = And(
        Key(table.partition_key.name).eq(workflow_id),
        Key(table.sort_key.name).begins_with(node_id),
    )
    items: list[WorkflowTable.Node] = table.query(expression).items  # type: ignore
    nodes = [x for x in items if isinstance(x, table.Node)]

    if len(nodes) < 1 or len(nodes) > 1:
        raise HTTPException(
            status_code=404, detail=f"Node not found: {workflow_id}/{node_id}"
        )

    if len(nodes) > 1:
        logger.warning(f"Delete Node: {workflow_id}/{node_id} returned multiple nodes")
        raise HTTPException(
            status_code=404, detail=f"Node not found: {workflow_id}/{node_id}"
        )

    node = nodes[0]
    if node.PartitionKey != workflow_id or node.SortKey != node_id:
        logger.warning(
            f"Delete Node: {workflow_id}/{node_id} returned a node with a different key. {node.PartitionKey}/{node.SortKey}"
        )
        raise HTTPException(
            status_code=404, detail=f"Node not found: {workflow_id}/{node_id}"
        )

    for item in items:
        logger.debug(f"delete {workflow_id}/{node_id}: Deleted: {item}")
        item.delete()

    return items


@router.put("/{workflow_id}/nodes", responses={404: Error404, 500: Error500})
def update_nodes(
    workflow_id: str,
    body: list[WorkflowTable.Node],
    table: WorkflowTable = Depends(get_workflow_table),
) -> list[WorkflowTable.Node]:
    workflow = get_workflow_object(workflow_id, table)
    updated: list[WorkflowTable.Node] = []
    with table.batch_writer() as batch:
        for node in body:
            if node.PartitionKey == workflow.ID and node.Resource == "Node":
                batch.put_item(Item=node)
                updated.append(node)
            else:
                logger.warning(
                    f"Attempted to update resource that is not a node belonging to {workflow.ID}: {node.PartitionKey}/{node.SortKey}"
                )
    return updated

@router.post(
    "/{workflow_id}/nodes/{node_id}/data", responses={404: Error404, 500: Error500}
)
def set_data_on_node(
    workflow_id: str,
    node_id: str,
    body: NodeDataPostRequest,
    registry: NodeRegistry = Depends(get_node_registry),
    table: WorkflowTable = Depends(get_workflow_table),
) -> WorkflowTable.Node:
    node = get_node_object(node_id, workflow_id, table)
    instance = get_node_class(node.Address, node.Version, registry=registry)(id=node_id)
    _set_data_on_node(instance, body.Key, body.Type, body.Data)
    node = WorkflowTable.Node(
        PartitionKey=workflow_id, SortKey=node_id, **instance.schema().model_dump()
    )
    node.put()
    return node


@router.post("/{workflow_id}/edges", responses={404: Error404, 500: Error500})
def add_edge_to_workflow(
    workflow_id: str,
    body: EdgePostRequest,
    table: WorkflowTable = Depends(get_workflow_table),
    registry: NodeRegistry = Depends(get_node_registry),
) -> WorkflowTable.Edge:
    from_node = get_node_instance_by_id(body.From.NodeID, workflow_id, table, registry)
    to_node = get_node_instance_by_id(body.To.NodeID, workflow_id, table, registry)
    from_data = get_node_data_from_instance(from_node, body.From.Key)
    to_data = get_node_data_from_instance(to_node, body.To.Key)
    edge = Edge(from_data, to_data)

    edge = table.Edge(PartitionKey=workflow_id, **edge.schema().model_dump())
    edge.put()
    return edge


@router.get("/{workflow_id}/edges", responses={404: Error404, 500: Error500})
def get_edges_by_workflow(
    workflow_id: str, table: WorkflowTable = Depends(get_workflow_table)
) -> list[WorkflowTable.Edge]:
    response = table.Edge.query(
        key=workflow_id, key_expression=Key(table.sort_key.name).begins_with("Edge-")
    )
    return response.items


@router.get("/{workflow_id}/edges/{edge_id}", responses={404: Error404, 500: Error500})
def get_edge_by_id(
    workflow_id: str, edge_id: str, table: WorkflowTable = Depends(get_workflow_table)
) -> WorkflowTable.Edge:
    edge = table.Edge.get(key=workflow_id, sort_key=edge_id)
    if not edge:
        raise HTTPException(
            status_code=404, detail=f"Edge not found: {workflow_id}/{edge_id}"
        )
    return edge


@router.put("/{workflow_id}/edges", responses={404: Error404, 500: Error500})
def update_edges(
    workflow_id: str,
    body: list[WorkflowTable.Edge],
    table: WorkflowTable = Depends(get_workflow_table),
) -> list[WorkflowTable.Edge]:
    workflow = get_workflow_object(workflow_id, table)
    updated: list[WorkflowTable.Edge] = []
    with table.batch_writer() as batch:
        for edge in body:
            if edge.PartitionKey == workflow.ID and edge.Resource == "Edge":
                batch.put_item(Item=edge)
                updated.append(edge)
            else:
                logger.warning(
                    f"Attempted to update resource that is not an edge belonging to {workflow.ID}: {edge.PartitionKey}/{edge.SortKey}"
                )
    return updated

@router.delete("/{workflow_id}/edges/{edge_id}", responses={404:Error404, 500:Error500})
def delete_edge_by_id(workflow_id:str, edge_id:str, table: WorkflowTable = Depends(get_workflow_table)) -> WorkflowTable.Edge:
    edge = get_edge_object(edge_id=edge_id, workflow_id=workflow_id, table=table)
    edge.delete()
    return edge

@router.post("/{workflow_id}/run", responses={404: Error404, 500: Error500})
def run_workflow(
    workflow_id,
    table: WorkflowTable = Depends(get_workflow_table),
    registry: NodeRegistry = Depends(get_node_registry),
) -> WorkflowSchema:
    workflow_data = table.query(
        Key(table.partition_key.name).eq(workflow_id),
    )
    if not workflow_data:
        raise HTTPException(status_code=404, detail=f"No such workflow: {workflow_id}")
    workflow = Workflow(workflow_id)
    nodes: dict[str, Node] = {}
    for item in workflow_data.items:  # type: ignore
        if isinstance(item, WorkflowTable.Node):
            node = get_node_class(item.Address, item.Version, registry)(id=item.ID)
            for key, data in item.Data.items():
                if data.Value is not None:
                    node.data[key].set(data.Value)
            workflow.add_node(node)
    for item in workflow_data.items:
        if isinstance(item, WorkflowTable.Edge):
            from_node = workflow.get_node_by_id(item.From.NodeID)
            to_node = workflow.get_node_by_id(item.To.NodeID)
            workflow.add_edge(
                source=from_node.data[item.From.Key], target=to_node.data[item.To.Key]
            )
    workflow.run()
    return workflow.schema()


#        if isinstance(item, WorkflowTable.NodeData):
#            _set_data_on_node(nodes[item.NodeID], item.Key, item.Type, item.Data)
