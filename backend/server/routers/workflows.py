from fastapi import APIRouter, Depends, HTTPException
from server.database.tables import get_workflow_table, WorkflowTable  # type: ignore
from server.utils import omit
from contextlib import contextmanager
from pydantic import BaseModel
from typing import Optional


@omit("PartitionKey", "SortKey", "WorkflowID", "ID")
class WorkflowPostRequest(WorkflowTable.Workflow):
    ...


@omit("PartitionKey", "SortKey", "WorkflowID", "NodeID", "ID")
class WorkflowNodePostRequest(WorkflowTable.Node):
    ...


class WorkflowPatchRequest(BaseModel):
    Name: Optional[str]
    Owner: Optional[str]


router = APIRouter(prefix="/workflows", tags=["workflows"])


def get_workflow_object(
    workflow_id: str, table: WorkflowTable
) -> WorkflowTable.Workflow:
    if not workflow_id.startswith("Workflow-"):
        workflow_id = f"Workflow-{workflow_id}"
    workflow = table.Workflow.get(key=workflow_id, sort_key=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=404, detail=f"Workflow not found: {workflow_id}"
        )
    return workflow


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
):
    workflow = get_workflow_object(workflow_id, table)
    node = table.Node(**body.model_dump())
    node.put()
    return node
