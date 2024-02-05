from fastapi import APIRouter, Depends
from server.objects import Workflows

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.get("/")
def get_workflows():
    return Workflows.Workflow.scan()
