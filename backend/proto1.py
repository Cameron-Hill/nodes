from nodes.main import handle_request
from nodes.proto1.actions import DummyAction
from nodes.proto1.tasks import Selector
from pprint import pprint
import sys
import logging
logger = logging.getLogger()

logger.addHandler(logging.StreamHandler(sys.stdout))

response = handle_request(DummyAction, {})

print(f'Action response:')
pprint(response)

dummy_action_output_schema = DummyAction.handler.__annotations__.get('return')


selector = Selector()
selector_options = selector.options(dummy_action_output_schema)

a=1
