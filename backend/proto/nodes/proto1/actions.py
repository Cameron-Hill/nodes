from pydantic import BaseModel
from nodes.base import Action, Data, Options

class CSchema(BaseModel):
    x: str
    y: str

class DummyActionOutput(BaseModel):
    a: int
    b: str
    c: CSchema

class DummyAction(Action):
    def handler(self, data: Data, options:Options) -> DummyActionOutput:
        return {
            'a': 1,
            'b': '2',
            'c': {
                'x': 'x',
                'y': 'y'
            }   
        }

