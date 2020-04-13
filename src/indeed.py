import json
import sys

import requests
import re
from bs4 import BeautifulSoup
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


def get_request(url):
    url = url.replace("https", "http")
    return requests.get(url, timeout=30)


@app.get("/")
async def root():
    return {"message": "Welcome to Indeed Job Board API"}


class JobSearch(BaseModel):
    search_term: str
    location: str
    get_description: str
    date_posted: str
    remote: bool
    job_type: str
    level: str


@app.post("/linkedin")
async def indeed_search_jobs(request: JobSearch):
    pass