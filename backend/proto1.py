from nodes.main import handle_request
from nodes.proto1.actions import DummyAction
from nodes.proto1.tasks import Selector
from pprint import pprint
import sys
import logging
logger = logging.getLogger()

logger.addHandler(logging.StreamHandler(sys.stdout))

workflow = {
    "name": "Test Workflow",
    "nodes": [
        {
            "name": "Dummy Action",
            "type": "action",
            "action": "DummyAction",
            "inputs": {},
            "outputs": {
                "a": "a",
                "b": "b",
                "c": "c"
            }
        },
        {
            "name": "Selector",
            "type": "task",
            "task": "Selector",
            "inputs": {
                "a": "a",
                "b": "b",
                "c": "c"
            },
            "outputs": {
                "selected": "selected"
            }
        }
    ]
}

dummy_action_response = handle_request(DummyAction, {})
print(f'Action response: { dummy_action_response}')

selector_response = handle_request(Selector, dummy_action_response)
print(f'Selector response: {selector_response}')

