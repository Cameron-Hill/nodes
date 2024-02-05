from fastapi import APIRouter, Depends, HTTPException
from server.objects import get_workflow_table, WorkflowTable  # type: ignore
from server.utils import omit
from contextlib import contextmanager
from pydantic import BaseModel
from typing import Optional


@omit("PartitionKey", "SortKey", "WorkflowID", "ID")
class WorkflowPostRequest(WorkflowTable.Workflow): ...


class WorkflowPatchRequest(BaseModel):
    Name: Optional[str]
    Owner: Optional[str]


router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/", response_model=list[WorkflowTable.Workflow])
def get_workflow(table: WorkflowTable = Depends(get_workflow_table)):
    scanned_items = table.Workflow.scan()
    return scanned_items.items


@router.post("/", response_model=WorkflowTable.Workflow)
def create_workflow_table(
    body: WorkflowPostRequest, table: WorkflowTable = Depends(get_workflow_table)
):
    workflow = table.Workflow(**body.model_dump())
    return workflow


@router.get("/{workflow_id}", response_model=WorkflowTable.Workflow)
def get_workflow_by_id(
    workflow_id: str, table: WorkflowTable = Depends(get_workflow_table)
):
    if not workflow_id.startswith("Workflow-"):
        workflow_id = f"Workflow-{workflow_id}"
    workflow = table.Workflow.get(key=workflow_id, sort_key=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=404, detail=f"Workflow not found: {workflow_id}"
        )
    return workflow


@router.patch("/{workflow_id}", response_model=WorkflowTable.Workflow)
def update_workflow_by_id(
    workflow_id: str,
    body: WorkflowPatchRequest,
    table: WorkflowTable = Depends(get_workflow_table),
):
    if not workflow_id.startswith("Workflow-"):
        workflow_id = f"Workflow-{workflow_id}"
    workflow = table.Workflow.get(key=workflow_id, sort_key=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=404, detail=f"Workflow not found: {workflow_id}"
        )
    workflow.put(**body.model_dump())
    return workflow
