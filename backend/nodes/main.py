from nodes.base import Node, Node
from logging import getLogger
from pydantic import BaseModel

logger = getLogger(__name__)


def handle_request(node: Node, raw_data: dict, options: BaseModel = None):
    logger.info(f"Initializing action: {node}")
    node = node()
    input_model = node.handler.__annotations__.get("data", BaseModel)
    output_model = node.handler.__annotations__.get("return", BaseModel)
    data = input_model(**raw_data)
    result = node.handler(data)
    result = output_model(**result)
    return result
