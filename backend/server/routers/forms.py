from fastapi import APIRouter, Depends
from nodes import NodeRegistry, get_node_registry, manager
from nodes.base import NodeSchema
from server.database.tables import WorkflowTable

router = APIRouter(prefix="/forms", tags=["forms"], redirect_slashes=True)


extra = {}


@router.get("/")
async def read_forms(
    registry: NodeRegistry = Depends(get_node_registry),
) -> dict[str, NodeSchema]:
    node_schemas = {
        f"{addr}:{ver}": data.class_schema()
        for addr, blob in registry.items()
        for ver, data in blob.items()
    }
    node_schemas.update(extra)
    return node_schemas
