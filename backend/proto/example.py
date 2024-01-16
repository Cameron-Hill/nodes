from nodes.base import Node, Data
from nodes.main import handle_request
import requests
import logging
import sys

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))

def get_session() -> requests.Session:
    return requests.Session()



class GetRequestInput(Data):
    url: str
    params: dict = {}

class GenericOutputType(Data):
    url: str
    params: dict
    responseBody: dict
    responseCode: int

class TodoItemType(Data):
    completed: bool
    id: int
    title: str 
    userId: int


class GetRequest(Node):
    def handler(self, data: GetRequestInput) -> GenericOutputType:
        session = get_session()
        response = session.get(url= data.url, params=data.params)
        response.raise_for_status()
        return {
            'url': data.url,
            'params': data.params,
            'responseBody': response.json(),
            'responseCode': response.status_code
        }

class Transform(Node):
    """
    The transform action requires three things, data to be transformed, an input data schema and a target data schema.
    We have 2 options for sourcing these properties. We either take all three as inputs to the action. Maybe we can define some sort of
    'Schema Generator/Producer' that would produce a schema object that can be passed in. Or we could have the input/output schema be 'Properties' on the action.
    We would need to define in detail the difference between properties and inputs. Something like 'Properties are always the same for each execution of an action whereas inputs can change between executions.' 
    Regardless of which option we pick we still need to come up with some kind of 
    """
    def handler(self, data: Data) -> Data:
        return 
    

result = handle_request(GetRequest, {'url': 'https://jsonplaceholder.typicode.com/todos/1'})
print(result)


