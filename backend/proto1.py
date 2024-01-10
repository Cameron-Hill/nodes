from nodes.main import handle_request
from nodes.proto1.actions import DummyAction
from nodes.proto1.tasks import Selector
from pprint import pprint
import sys
import logging
logger = logging.getLogger()

logger.addHandler(logging.StreamHandler(sys.stdout))

dummy_action_response = handle_request(DummyAction, {})

print(f'Action response:')
pprint(dummy_action_response)

dummy_action_output_schema = DummyAction.handler.__annotations__.get('return')


selector = Selector()
SelectorOptions = selector.options(dummy_action_output_schema)
options = SelectorOptions(selected='c')

selector_response = handle_request(Selector, dummy_action_response, options)
