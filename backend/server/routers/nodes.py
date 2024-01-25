from fastapi import APIRouter
from server.app import get_node_manager, NodeSchema

router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.get("/")
def get_nodes(response_model=list[NodeSchema]):
    nodes = get_node_manager().nodes
    return [node.schema() for node in nodes]
