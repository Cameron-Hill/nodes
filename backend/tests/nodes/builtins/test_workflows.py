from nodes.workflow import Workflow
from nodes.builtins.requests import HTTPGetRequest
from nodes.builtins.producers import MapProducer, StringProducer


def test_map_producer_to_http_request_workflow():
    """"""
    workflow = Workflow()
    producer = StringProducer()
    request = HTTPGetRequest()
    workflow.add_node(producer)
    workflow.add_node(request)
    workflow.add_edge(producer.output, request.inputs["url"])
    