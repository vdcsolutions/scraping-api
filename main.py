from fastapi import FastAPI, Body
from typing import List, Dict
from scraper.scraper import Scraper
from pydantic import BaseModel

app = FastAPI()

class ScrapeRequest(BaseModel):
    urls: List[str]
    selectors: List[str]
    names: List[str]

@app.post("/scrape")
async def scrape(data_to_scrape: ScrapeRequest):
    scraper = Scraper(data_to_scrape.dict())
    results = await scraper.scrape()
    return results