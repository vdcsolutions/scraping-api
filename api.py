import aiohttp
from proxy_list import get_proxies, get_random_proxy, get_from_api
from fastapi import FastAPI, Request, BackgroundTasks
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import aiohttp
from typing import Optional, Dict, Any, Union
from fastapi import FastAPI
import configparser
import logging
import random
from typing import List, Dict
from fastapi import FastAPI, Request
from proxy_list import get_proxies, get_random_proxy
import uvicorn
from fake_useragent import UserAgent
from scraper import scrape_url

config = configparser.ConfigParser()
config.read('config.ini')

# Get the list of proxies
timestamp, proxy_list = get_proxies()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Scraping API",
    description="API documentation for scraping",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust the allowed origin accordingly
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the scraping API"}


@app.post("/fetch")
async def fetch_url(request: Request) -> str:
    """
    Fetches the given target URL using a random proxy.

    Args:
        request (Request): FastAPI request object containing the target URL.

    Returns:
        str: Pretty-printed HTML content of the target URL.
    """
    target_url = (await request.json())['url']

    async with aiohttp.ClientSession() as session:
        try:
            # Get a random proxy from the proxy list
            proxy = get_random_proxy(proxy_list)

            # Send a GET request to the URL using the selected proxy
            async with session.get(target_url, proxy=proxy, timeout=10) as response:
                response_text = await response.text()
                soup = BeautifulSoup(response_text, 'html.parser')
                pretty_html = soup.prettify()
                return pretty_html
        except Exception as e:
            logging.debug(f"Error fetching URL {target_url}: {e}")
            return f"Error fetching URL {target_url}: {e}"


async def update_proxy_list():
    get_from_api(config.get('PRODUCTION', 'proxy-api-url'))
    print("Fetching data from API")


async def run_update_proxy_list():
    while True:
        await asyncio.sleep(300)  # sleep for 5 minutes
        print('getting new proxies')
        await update_proxy_list()
        print('yay, got new proxies')


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_update_proxy_list())


@app.post("/scrape")
async def scrape(to_scrape: dict):
    tasks = []
    async with aiohttp.ClientSession(trust_env=True) as session:
        for url in to_scrape['urls']:
            tasks.append(asyncio.ensure_future(scrape_url(session, url, None, to_scrape)))
        results = await asyncio.gather(*tasks)
        return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)