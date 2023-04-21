from proxy_list import get_proxies, get_random_proxy
from fastapi import FastAPI, Request
import aiohttp
import random
import configparser
import logging
import uvicorn


config = configparser.ConfigParser()
config.read('config.ini')

timestamp, proxy_list = get_proxies()
print(proxy_list)

app = FastAPI()
@app.post("/fetch")
async def fetch_urls(request: Request):
    target_urls = await request.json()
    responses = []

    async with aiohttp.ClientSession() as session:
        for url in target_urls['target_urls']:
            try:
                proxy = get_random_proxy(proxy_list)
                async with session.get(url, proxy=proxy, timeout=10) as response:
                    response_text = await response.text()
                    responses.append({'url': url, 'response': response_text})
            except Exception as e:
                logging.debug(f"Error fetching URL {url}: {e}")
                responses.append({'url': url, 'response': f"Error fetching URL {url}: {e}"})

    return responses




