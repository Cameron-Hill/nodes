from __future__ import annotations
import pytest
from nodes.workflow import Workflow
from nodes.builtins.requests import HTTPGetRequest
from nodes.builtins.producers import MapProducer, StringProducer
from pydantic import create_model, Field, BaseModel, conlist
from annotated_types import Len
from nodes.base import NodeData
from typing import Annotated
from nodes.errors import NodeDataSchemaValidationException, NodeDataNotSetException
from unittest import mock


@pytest.fixture
def mocked_request():
    with mock.patch("requests.get") as mocked_get:
        mocked_response = mock.MagicMock()
        mocked_response.json.return_value = {"some": "content"}
        mocked_response.reason = "OK"
        mocked_response.status_code = 200
        mocked_get.return_value = mocked_response
        yield mocked_get


class ModelComponent(BaseModel):
    a: int
    b: str
    c: float = Field(default=0.0, description="This is a float", ge=0.0, lt=10.0)


class ComplexModel(BaseModel):
    components: Annotated[list[ModelComponent], Len(min_length=1, max_length=10)]
    object: dict[str, str]


def test_map_producer_to_http_request_workflow(mocked_request):
    """"""
    workflow = Workflow()
    producer = StringProducer()
    request = HTTPGetRequest()
    workflow.add_node(producer)
    workflow.add_node(request)
    workflow.add_edge(producer.output, request.inputs["url"])
    producer.options["options"].set({"value": "http://example.com"})
    workflow.run()
    mocked_request.assert_called_once_with("http://example.com", params={}, headers={})


def test_running_a_workflow_with_unset_options_raises_validation_error():
    """"""
    workflow = Workflow()
    producer = StringProducer()
    request = HTTPGetRequest()
    workflow.add_node(producer)
    workflow.add_node(request)
    workflow.add_edge(producer.output, request.inputs["url"])
    with pytest.raises(NodeDataNotSetException):
        workflow.run()


def test_get_roots():
    """"""
    workflow = Workflow()
    producer = StringProducer()
    request = HTTPGetRequest()
    workflow.add_node(producer)
    workflow.add_node(request)
    workflow.add_edge(producer.output, request.inputs["url"])
    assert workflow.roots == {producer}


def test_get_roots_many_producers():
    """"""
    workflow = Workflow()
    producers = []
    producers.append(producer1 := StringProducer())
    producers.append(producer2 := StringProducer())
    producers.append(producer3 := StringProducer())
    producers.append(producer4 := StringProducer())
    producers.append(producer5 := StringProducer())
    for producer in producers:
        workflow.add_node(producer)
    assert workflow.roots == set(producers)
    requests = []
    requests.append(request1 := HTTPGetRequest())
    requests.append(request2 := HTTPGetRequest())
    requests.append(request3 := HTTPGetRequest())
    requests.append(request4 := HTTPGetRequest())
    requests.append(request5 := HTTPGetRequest())
    for request in requests:
        workflow.add_node(request)
    for producer, request in zip(producers, requests):
        workflow.add_edge(producer.output, request.inputs["url"])
    assert workflow.roots == set(producers)


@pytest.mark.parametrize(
    "annotation_a, annotation_b, expected",
    [
        (int, int, True),
        (int, str, False),
        (str, str, True),
        (str, int, False),
        (int, None, False),
        (None, int, False),
        (None, None, True),
        (dict, dict, True),
        (dict, list, False),
        (list, dict, False),
        (list, list, True),
        (
            create_model("Source", a=(int, ...)),
            create_model("Target", a=(int, ...)),
            True,
        ),
        (
            create_model("Source", a=(int, ...)),
            create_model("Target", a=(str, ...)),
            False,
        ),
        (
            create_model("Source", a=(int, ...), b=(str, ...)),
            create_model("Target", a=(int, ...)),
            True,
        ),
        (
            create_model("Source", a=(int, ...)),
            create_model("Target", a=(int, ...), b=(str, ...)),
            False,  # This is not valid because the target has an attribute that is not compatible
        ),
        (
            create_model("Source", a=(int, ...), b=(str, ...)),
            create_model("Target", a=(int, ...), b=(str, ...)),
            True,
        ),
        (
            create_model("Source", a=(int, Field(..., description="Source A"))),
            create_model("Target", a=(int, Field(..., description="Target A"))),
            True,
        ),
        (
            create_model("Source", a=(int, Field(..., description="Source A", lt=10))),
            create_model("Target", a=(int, Field(..., description="Target A", lt=15))),
            True,
        ),
        (
            create_model("Source", a=(int, Field(..., description="Source A", lt=15))),
            create_model("Target", a=(int, Field(..., description="Target A", lt=10))),
            False,  # This is not valid because 15 is not necessarily less than 10
        ),
        (
            create_model("Source", a=(int, Field(..., description="Source A", lt=10))),
            create_model("Target", a=(int, Field(..., description="Target A", lt=10))),
            True,
        ),
        (  # Nested models
            create_model(
                "Source", a=(int, ...), b=(create_model("Nested", c=(str, ...)), ...)
            ),
            create_model(
                "Target", a=(int, ...), b=(create_model("Nested", c=(str, ...)), ...)
            ),
            True,
        ),
        (
            create_model(
                "Source", a=(int, ...), b=(create_model("Nested", c=(str, ...)), ...)
            ),
            create_model(
                "Target", a=(int, ...), b=(create_model("Nested", c=(int, ...)), ...)
            ),
            False,  # This is not valid because the nested model has an attribute that is not compatible
        ),
        (
            create_model(
                "Source",
                a=(str, Field(..., description="Source A", pattern=r".*-\d{4}")),
            ),
            create_model(
                "Target",
                a=(str, Field(..., description="Target A", pattern=r".*-\d{4}")),
            ),
            True,
        ),
        (
            create_model(
                "Source",
                a=(str, Field(..., description="Source A", pattern=r".*-\d{4}")),
            ),
            create_model(
                "Target",
                a=(str, Field(..., description="Target A", pattern=r".*-ABC")),
            ),
            False,  # This is not valid because the pattern is not compatible
        ),
        (
            create_model(
                "Source",
                a=(str, Field(..., description="Source A", pattern=r".*\d{2}-\d{4}")),
            ),
            create_model(
                "Target",
                a=(str, Field(..., description="Target A", pattern=r".*-\d{4}")),
            ),
            True,  # These are different, but compatible patterns
        ),
    ],
)
def test_is_compatible(annotation_a, annotation_b, expected):
    """"""
    workflow = Workflow()
    source = NodeData(..., "source", annotation_a, type="output")  # type: ignore
    target = NodeData(..., "target", annotation_b, type="input")  # type: ignore
    assert workflow._is_compatible(source, target) == expected
