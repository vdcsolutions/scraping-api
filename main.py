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
import uvicorn
from fake_useragent import UserAgent

config = configparser.ConfigParser()
config.read('config.ini')
timestamp, proxy_list = get_proxies()

app = FastAPI()


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

async def scrape_url(session: aiohttp.ClientSession, url: str, proxy: Optional[str], to_scrape: Dict[str, Any]) -> Union[int, Dict[str, Any]]:
    for i in range(3):
        try:
            async with session.get(url, proxy=proxy) as response:
                print(response.status)
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    data = {}
                    for css_selector, name in zip(to_scrape['selectors'], to_scrape['names']):
                        data[name] = [element.text for element in soup.select(css_selector)]
                    to_scrape['result'] = data
                    return to_scrape
                else:
                    return response.status
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            if i == 2:
                return e
            else:
                await asyncio.sleep(5)
                proxy = get_random_proxy()
