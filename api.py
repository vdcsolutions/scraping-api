from proxy_list import get_proxies, get_random_proxy
from fastapi import BackgroundTasks
import asyncio
from bs4 import BeautifulSoup
import aiohttp
from typing import Optional, Dict, Any, Union
from fastapi import FastAPI
import configparser

from fake_useragent import UserAgent
from fastapi_utils.tasks import repeat_every

config = configparser.ConfigParser()
config.read('config.ini')

user_agent = UserAgent()

app = FastAPI()


def update_proxy_list():
    timestamp, proxy_list = get_proxies()
    app.state.proxy_updated = timestamp
    app.state.proxy_list = proxy_list
    print('Proxy list updated')


@app.on_event("startup")
@repeat_every(seconds=5 * 60)
async def startup_event():
    background_tasks = BackgroundTasks()
    background_tasks.add_task(update_proxy_list())


@app.post("/scrape")
async def scrape(to_scrape: dict):
    tasks = []
    async with aiohttp.ClientSession(trust_env=True) as session:
        for url in to_scrape['urls']:
            tasks.append(asyncio.ensure_future(scrape_url(session, url, None, to_scrape)))
        results = await asyncio.gather(*tasks)
        return results


async def scrape_url(session: aiohttp.ClientSession, url: str, proxy: Optional[str], to_scrape: Dict[str, Any]) -> \
        Union[int, Dict[str, Any]]:
    for i in range(3):
        try:
            proxy = get_random_proxy(app.state.proxy_list)
            async with session.get(url, proxy=proxy, headers={'User-Agent': user_agent.random}) as response:
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
                proxy = get_random_proxy(app.state.proxy_list)
