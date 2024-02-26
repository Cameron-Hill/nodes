import requests
from nodes.base import Node
from nodes.datatypes import Undefined
from pydantic import BaseModel, Field
from pydantic.networks import AnyHttpUrl
from typing import Annotated, Optional


class InputHTTPGetRequest(BaseModel):
    url: AnyHttpUrl = Field(..., description="The URL to send the request to")
    query_params: dict[str, str] = Field(
        {}, description="The query parameters to send with the request"
    )
    headers: dict[str, str] = Field(
        {}, description="The headers to send with the request"
    )


RequestQueryParams = Optional[dict[str, str]]
RequestHeaders = Optional[dict[str, str]]


class OutputHTTPGetRequest(BaseModel):
    status_code: int = Field(..., description="The status code of the response")
    reason: str = Field(..., description="The reason for the status code")
    content: Annotated[dict, Undefined] = Field(
        ...,
        description="The json content of the response. This has an undefined schema.",
    )


class HTTPGetRequest(Node):
    __label__ = "HTTP Get Request"
    __group__ = "Connectivity"

    def run(
        self, url: str, params: RequestQueryParams, headers: RequestHeaders
    ) -> OutputHTTPGetRequest:
        """
        :param url: The url that will be called, should be in the format: http://example.com
        :param params: Any query parameters. Should be passed in as an object, e.g. {"param1": "value1", "param2": "value2"}
        :param headers: Any headers. Should be passed in as an object, e.g. {"header1": "value1", "header2": "value2"}
        :return: The json response from the request
        """
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return OutputHTTPGetRequest(
            status_code=response.status_code,
            reason=response.reason,
            content=response.json(),
        )

    def error_handler(self, exception: Exception) -> OutputHTTPGetRequest:
        if isinstance(exception, requests.exceptions.HTTPError) and exception.response:
            content = exception.response.json()
            if not content:
                content = {"body": exception.response.content.decode()}
            return OutputHTTPGetRequest(
                status_code=exception.response.status_code,
                reason=exception.response.reason,
                content=content,
            )
        raise exception
