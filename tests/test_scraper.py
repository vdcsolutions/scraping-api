import pytest
from unittest.mock import Mock, patch
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import sys, os

current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory (project directory) to the sys.path
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)
from api import scrape_url

@pytest.mark.asyncio
async def test_scrape_url_success():
    url = "http://example.com"
    proxy = "http://proxy.example.com"
    to_scrape = {
        "selector": "css",
        "selectors": ["#title", ".description"],
        "names": ["title", "description"]
    }
    expected_result = {
        "selector": "css",
        "selectors": ["#title", ".description"],
        "names": ["title", "description"],
        "result": {
            "title": ["Example Title"],
            "description": ["Example Description"]
        }
    }

    response = Mock()
    response.status = 200
    response.text = Mock(return_value="<html><body><h1 id='title'>Example Title</h1><p class='description'>Example Description</p></body></html>")

    session = Mock(ClientSession)
    session.get = Mock(return_value=response)

    with patch("scraper.scrape_css", return_value={"title": ["Example Title"], "description": ["Example Description"]}) as mock_scrape_css:
        result = await scrape_url(session, url, proxy, to_scrape)

    session.get.assert_called_once_with(url, proxy=proxy, headers={'User-Agent': user_agent.random})
    mock_scrape_css.assert_called_once_with(BeautifulSoup(response.text, 'html.parser'), to_scrape['selectors'], to_scrape['names'])
    assert result == expected_result


@pytest.mark.asyncio
async def test_scrape_url_failure():
    url = "http://example.com"
    proxy = "http://proxy.example.com"
    to_scrape = {
        "selector": "css",
        "selectors": ["#title", ".description"],
        "names": ["title", "description"]
    }
    expected_result = 404

    response = Mock()
    response.status = 404

    session = Mock(ClientSession)
    session.get = Mock(return_value=response)

    result = await scrape_url(session, url, proxy, to_scrape)

    session.get.assert_called_once_with(url, proxy=proxy, headers={'User-Agent': user_agent.random})
    assert result == expected_result
