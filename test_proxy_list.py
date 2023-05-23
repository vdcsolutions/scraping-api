import pytest
from unittest import mock
from requests import Response
import sys
import os

# Get the parent directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory (project directory) to the sys.path
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)

# Now you can import the module
from proxy_list import (
    get_from_api,
    get_timestamp,
    get_proxies_from_json,
    get_proxies,
    get_random_proxy,
)


@pytest.fixture
def mock_get_response():
    response = Response()
    response.status_code = 200
    response.json = mock.Mock(return_value={'timestamp': '2023-05-11', 'proxies': [{'ip': '127.0.0.1', 'port': 8080}]})
    return response


@mock.patch('requests.get')
def test_get_from_api(mock_get, mock_get_response):
    mock_get.return_value = mock_get_response

    api_url = 'http://example.com/api'
    data = get_from_api(api_url)

    assert data == {'timestamp': '2023-05-11', 'proxies': [{'ip': '127.0.0.1', 'port': 8080}]}
    mock_get.assert_called_once_with(api_url)


def test_get_proxies_from_json():
    data = [{'ip': '127.0.0.1', 'port': 8080}, {'ip': '192.168.0.1', 'port': 8888}]
    urls = get_proxies_from_json(data)

    assert urls == ['http://127.0.0.1:8080', 'http://192.168.0.1:8888']


def test_get_random_proxy():
    proxy_list = ['http://127.0.0.1:8080', 'http://192.168.0.1:8888']
    proxy = get_random_proxy(proxy_list)

    assert proxy in proxy_list


if __name__ == '__main__':
    pytest.main()
