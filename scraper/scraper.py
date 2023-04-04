from bs4 import BeautifulSoup
import random
from fake_useragent import UserAgent
import asyncio
import aiohttp
from typing import Dict, List

class Scraper:
    def __init__(self, data):
        self.to_scrape = data
        self.proxy_list = []
    def get_random_user_agent(self):
        return UserAgent().random

    def get_proxy_list(self):
        with open('proxy_list.txt') as f:
            proxy_list = [f'http://{line.strip()}' for line in f]
        self.proxy_list = ['http://' + proxy for proxy in proxy_list]
    def get_random_proxy(self):
        return random.choice(self.proxy_list)

    async def fetch(self, session, url, proxy):
        headers = {'User-Agent': self.get_random_user_agent()}
        if proxy is None:
            async with session.get(url, headers=headers, timeout=10) as response:
                return await response.text()
        else:
            async with session.get(url, headers=headers, proxy=proxy, timeout=10) as response:
                return await response.text()

    async def scrape_url(self, session, url, proxy):
        for i in range(3):
            try:
                async with session.get(url, proxy=proxy) as response:
                    print(response.status)
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        data = {}
                        for css_selector, name in zip(self.to_scrape['selectors'], self.to_scrape['names']):
                            data[name] = [element.text for element in soup.select(css_selector)]
                        self.to_scrape['result'] = data
                        return self.to_scrape
                    else:
                        return response.status
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                if i == 2:
                    return e
                else:
                    await asyncio.sleep(5)
                    proxy = self.get_random_proxy()

    async def scrape(self):
        tasks = []
        async with aiohttp.ClientSession(trust_env=True) as session:
            for url in self.to_scrape['urls']:
                tasks.append(asyncio.ensure_future(self.scrape_url(session, url, None)))
            results = await asyncio.gather(*tasks)
            return results
