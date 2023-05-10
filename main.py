import aiohttp
import configparser
import logging
import random
from typing import List, Dict
from fastapi import FastAPI, Request
from proxy_list import get_proxies, get_random_proxy
import uvicorn


config = configparser.ConfigParser()
config.read('config.ini')

# Get the list of proxies
timestamp, proxy_list = get_proxies()
print(proxy_list)

app = FastAPI()

@app.post("/fetch")
async def fetch_urls(request: Request) -> List[Dict[str, str]]:
    """
    Fetches the given target URLs using random proxies.

    Args:
        request (Request): FastAPI request object containing the target URLs.

    Returns:
        List[Dict[str, str]]: List of dictionaries containing the URL and its corresponding response.
    """
    target_urls = await request.json()
    responses = []

    async with aiohttp.ClientSession() as session:
        for url in target_urls['target_urls']:
            try:
                # Get a random proxy from the proxy list
                proxy = get_random_proxy(proxy_list)

                # Send a GET request to the URL using the selected proxy
                async with session.get(url, proxy=proxy, timeout=10) as response:
                    response_text = await response.text()
                    responses.append({'url': url, 'response': response_text})
            except Exception as e:
                logging.debug(f"Error fetching URL {url}: {e}")
                responses.append({'url': url, 'response': f"Error fetching URL {url}: {e}"})

    return responses


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
