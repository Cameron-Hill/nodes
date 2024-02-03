from fastapi import APIRouter
from server.app import get_node_manager, NodeSchema

router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.get("/", response_model=list[NodeSchema])
def get_nodes():
    nodes = get_node_manager().nodes
    return [node.schema() for node in nodes]
