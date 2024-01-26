from nodes.builtins.requests import HTTPGetRequest, InputHTTPGetRequest
import pytest
from unittest.mock import patch, MagicMock

@patch('requests.get')
def test_HTTPGetRequest(mocked_get):
    input: InputHTTPGetRequest = {
        'url': 'http:/notarealurl.com',
    }
    mocked_response = MagicMock()
    mocked_response.json.return_value = {"some": "content"}
    mocked_response.reason = "OK"
    mocked_response.status_code = 200
    mocked_get.return_value = mocked_response
    
    node = HTTPGetRequest(input=input)
    response = node.call()
    assert response.status_code == 200
    assert response.reason == 'OK'

