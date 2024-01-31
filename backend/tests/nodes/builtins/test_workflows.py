from nodes.workflow import Workflow
from nodes.builtins.requests import HTTPGetRequest
from nodes.builtins.producers import MapProducer 

def test_map_producer_to_http_request_workflow():
    """"""
    workflow = Workflow()
    workflow.add_node(MapProducer())
    

