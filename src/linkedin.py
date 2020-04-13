import json
import sys

import requests
import re
from bs4 import BeautifulSoup
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

PROVIDER = {
    "base_url": "https://in.linkedin.com/jobs/search",
    "keyword": "keywords",
    "location": "location",
    "page_number": "pageNum",
    "limit": {
        "param": "count",
        "value": 25
    },
    "date_posted": "f_TP",
    "job_type": "f_JT",
    "level": "f_E"
}

GRANULARITIES = {
    "last_day": "1",
    "last_week": "1,2",
    "last_month": "1,2,3,4"
}

JOB_TYPES = {
    "Full-time": "F",
    "Contract": "C",
    "Part-time": "P",
    "Temporary": "T",
    "Internship": "I"
}

LEVELS = {
    "Entry level": "2",
    "Associate": "3",
    "Mid-Senior level": "4",
    "Director": "5",
    "Executive": "6"
}


def get_request(url):
    url = url.replace("https", "http")
    return requests.get(url, timeout=30)


@app.get("/")
async def root():
    return {"message": "Welcome to Linkedin Job Board API"}


class JobSearch(BaseModel):
    search_term: str
    location: str
    get_description: str
    date_posted: str
    remote: bool
    job_type: str
    level: str


@app.post("/linkedin")
async def linkedin_search_jobs(request: JobSearch):
    return find_linkedin_jobs(request)


def find_linkedin_jobs(request):
    start = 0
    jobs = []
    offset = 25
    page = 0

    while start < offset:

        url = PROVIDER['base_url'] + '?' + PROVIDER['keyword'] + '=' + str(request.search_term) \
              + '&' + PROVIDER['location'] + '=' + request.location \
              + '&' + PROVIDER['page_number'] + '=0' \
              + '&start=26'

        if request.date_posted in GRANULARITIES.keys():
            url += '&' + PROVIDER['date_posted'] + '=' + GRANULARITIES[request.date_posted]

        if request.job_type in JOB_TYPES.keys():
            url += '&' + PROVIDER['job_type'] + '=' + JOB_TYPES[request.job_type]

        if request.level in LEVELS.keys():
            url += '&' + PROVIDER['level'] + '=' + LEVELS[request.level]

        try:
            source = get_request(url)
        except Exception as e:
            print('{}')
            sys.stderr.write(str(e))
            return

        text = source.text

        to_crawl = BeautifulSoup(text, "lxml")
        job_title = to_crawl.findAll('h3', {'class': 'result-card__title job-result-card__title'})

        job_url = to_crawl.findAll('a', {'class': 'result-card__full-card-link'})

        company_name = to_crawl.findAll('h4', {'class': 'result-card__subtitle job-result-card__subtitle'})

        location = to_crawl.findAll('span', {'class': 'job-result-card__location'})

        time = to_crawl.findAll('time', {'class': 'job-result-card__listdate'})

        keywords_list = request.search_term.split()
        print(keywords_list)

        index = 0
        for link1, link2, link3, link4, link5 in zip(job_title, company_name, location, time, job_url):
            index += 1
            counter = 0
            for x in keywords_list:
                y = link1.text.lower()
                if str(x).lower() in y:
                    counter += 1

            data_dict = dict()
            data_dict['KeywordsMatch'] = float(
                "{0:.2f}".format(float(float(counter) / float(len(request.search_term.split())))))
            data_dict['searchKeywords'] = str(len(request.search_term.split()))
            data_dict['keywordsMatches'] = str(counter)
            data_dict['title'] = link1.text
            data_dict['url'] = link5['href']

            # https://www.linkedin.com/jobs/view/motion-graphic-designer-at-forthnet-1689655674?refId=b6e07afc-a8df-4b4b-a9a0-f3b92a81d8f6&position=18&pageNum=0&trk=guest_job_search_job-result-card_result-card_full-click&originalSubdomain=gr
            job_url = data_dict['url']
            if job_url:
                v = job_url.find('view/')
                if v > -1:
                    v = v + 5
                    x = job_url.find('?', v)
                    if x > -1:
                        data_dict['jobId'] = job_url[v:x]

            try:
                data_dict['company'] = link2['a'].text
            except Exception:
                data_dict['company'] = link2.text

            data_dict['provider'] = "Linkedin"
            data_dict['location'] = link3.text

            days_string = link4.text.split(" ")
            num_days = 0

            if days_string[1] == "weeks" or days_string[1] == "week":
                num_days = int(days_string[0]) * 7
            elif days_string[1] == "month" or days_string[1] == "months":
                num_days = int(days_string[0]) * 30
            elif days_string[1] == "hours" or days_string[1] == "minutes":
                num_days = 0
            elif days_string[1] == "days":
                num_days = int(days_string[0])
            data_dict['postDate'] = link4['datetime']
            data_dict['numDaysAgo'] = str(num_days)

            if str(request.get_description) == "1":
                try:
                    source_new = get_request(link5["href"])
                except Exception as e:
                    print('{}')
                    sys.stderr.write(str(e))
                    return

                text_new = source_new.text
                to_crawl_new = BeautifulSoup(text_new, "lxml")
                divs = to_crawl_new.findAll('div', {'class': 'description__text description__text--rich'})
                if len(divs) == 0:
                    print('{}')
                    sys.stderr.write("Divs are empty")
                    return

                job_desc = divs[0]
                data_dict['summary'] = job_desc.text
                # dataDict['summaryhtml'] = str(job_desc)

                email_in_description = re.findall(r'[\w.-]+@[\w.-]+', job_desc.text)
                data_dict['emailInSummary'] = email_in_description
            # ======================================================
            # add the job
            jobs.append(data_dict)
        page += 1
        start += 25

    print(json.dumps(jobs, indent=2))
    print(jobs.__len__())