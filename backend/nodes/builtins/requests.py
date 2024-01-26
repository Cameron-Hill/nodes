import requests
from nodes.base import Node
from nodes.datatypes import UndefinedMap
from pydantic import BaseModel, Field
from pydantic.networks import AnyHttpUrl


class InputHTTPGetRequest(BaseModel):
    url: AnyHttpUrl = Field(..., description="The URL to send the request to")
    query_params: dict[str, str] = Field(
        {}, description="The query parameters to send with the request"
    )
    headers: dict[str, str] = Field(
        {}, description="The headers to send with the request"
    )


class OutputHTTPGetRequest(UndefinedMap):
    status_code: int = Field(..., description="The status code of the response")
    reason: str = Field(..., description="The reason for the status code")
    content: UndefinedMap = Field(
        ...,
        description="The json content of the response. This has an undefined schema.",
    )


class HTTPGetRequest(Node):
    __label__ = "HTTP Get Request"
    __group__ = "Connectivity"

    def run(self, input: InputHTTPGetRequest) -> OutputHTTPGetRequest:
        response = requests.get(
            input.url, params=input.query_params, headers=input.headers
        )
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "reason": response.reason,
            "content": response.json(),
        }

    def error_handler(self, exception: Exception):
        if isinstance(exception, requests.exceptions.HTTPError):
            return {
                "status_code": exception.response.status_code,
                "reason": exception.response.reason,
                "content": exception.response.content,
            }
