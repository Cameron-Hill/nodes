from fastapi import APIRouter
from server.app import get_node_manager, NodeSchema
from server.responses import Error500

router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.get("/", response_model=list[NodeSchema], responses={500: Error500})
def get_nodes():
    nodes = get_node_manager().nodes
    return [node.class_schema() for node in nodes]
