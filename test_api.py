import pytest
import httpx
from fastapi.testclient import TestClient
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory (project directory) to the sys.path
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)
from api import app
client = TestClient(app)


@pytest.fixture
def mock_aiohttp_get(monkeypatch):
    async def mock_get(url, **kwargs):
        return httpx.Response(200, json={'url': url, 'response': 'Mock response'})

    monkeypatch.setattr(httpx, 'get', mock_get)


def test_fetch_urls(mock_aiohttp_get):
    target_urls = {'target_urls': ['https://example.com']}
    response = client.post('/fetch', json=target_urls)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['url'] == 'https://example.com'
    assert data[0]['response'] == 'Mock response'


def test_scrape_urls(mock_aiohttp_get):
    to_scrape = {'urls': ['https://example.com']}
    response = client.post('/scrape', json=to_scrape)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['url'] == 'https://example.com'
    assert data[0]['response'] == 'Mock response'
