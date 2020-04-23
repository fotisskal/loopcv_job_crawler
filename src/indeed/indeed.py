import sys
import requests
import re
import urllib.parse as urlparse
import pycountry
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from torrequest import TorRequest

app = FastAPI()

PROVIDER = {
    "base_url": "https://indeed.com",
    "base_url_A": "https://%s.indeed.com",
    "base_url_B": "https://indeed.%s",
    "base_url_C": "https://indeed.co.%s",
    "keyword": "q",
    "location": "!",
    "limit": 50,
    "date_posted": "fromage",
    "job_type": "jt"
}

COUNTRIES_SUFFIX = ("ch", "ae", "es", "pt", "nl", "fr", "cl")

COUNTRIES_SPECIAL = ("za", "uk", "in", "my", "mx", "pk", "pe", "ph", "br")

GRANULARITIES = {
    "yesterday": "1",
    "3_days": "3",
    "1_week": "7",
    "2_weeks": "15"
}

JOB_TYPES = {
    "Full-time": "fulltime",
    "Permanent": "permanent",
    "Contract": "contract",
    "Part-time": "parttime",
    "Temporary": "temporary",
    "Internship": "internship",
    "Commission": "commission",
    "New-Grad": "newgrad"
}


def get_request(url):
    url = url.replace("https", "http")
    return requests.get(url, timeout=30)


@app.get("/")
async def root():
    return {"message": "Welcome to Indeed Job Board API"}


class JobSearch(BaseModel):
    country: str
    search_term: str
    location: str
    get_description: str
    date_posted: str
    remote: bool
    job_type: str
    level: str


@app.post("/indeed")
async def indeed_search_jobs(request: JobSearch):
    return find_indeed_jobs(request)


def find_indeed_jobs(request):
    jobs = []
    start = 0
    current_page = 1
    total_page_number = 1
    iso_code = get_iso_code(request.country)

    base_url = get_base_url(iso_code)

    if request.remote:
        request.search_term = "Remote " + request.search_term

    proxy_port = 9050
    ctrl_port = 9051
    password = "PASSWORD"

    while current_page <= total_page_number:

        # with TorRequest(proxy_port=proxy_port, ctrl_port=ctrl_port, password=password) as tr:
        #     tr.reset_identity()

        url = base_url % iso_code + "/jobs" \
              + '?' + PROVIDER['keyword'] + '=' + urlparse.quote(request.search_term) \
              + '&' + PROVIDER['location'] + '=' + request.location \
              + '&limit=' + str(PROVIDER['limit']) \
              + '&start=' + str(start)

        if request.date_posted in GRANULARITIES.keys():
            url += '&' + PROVIDER['date_posted'] + '=' + GRANULARITIES[request.date_posted]

        if request.job_type in JOB_TYPES.keys():
            url += '&' + PROVIDER['job_type'] + '=' + JOB_TYPES[request.job_type]

        try:
            source = get_request(url)
        except Exception as e:
            print('{}')
            sys.stderr.write(str(e))
            return

        text = source.text

        to_crawl = BeautifulSoup(text, "lxml")

        total_results_num = to_crawl.find('div', {'id': 'searchCountPages'}).text.split()[3].replace('.', '')
        total_page_number = int(total_results_num) // 50

        job_info = to_crawl.findAll('a', {'class': 'jobtitle turnstileLink'})

        company_name = to_crawl.findAll('span', {'class': 'company'})

        location = to_crawl.findAll('span', {'class': 'location accessible-contrast-color-location'})

        time = to_crawl.findAll('span', {'class': 'date'})

        keywords_list = request.search_term.split()

        for link1, link2, link3, link4 in zip(job_info, company_name, location, time):
            if request.remote:
                y = link1.text.lower()
                if 'remote' not in y:
                    continue

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

            data_dict['title'] = link1['title']
            data_dict['url'] = base_url % iso_code + link1['href']

            # parsed = urlparse.urlparse(job_url)
            # data_dict['jobId'] = parse_qs(parsed.query)['jk']

            data_dict['company'] = link2.text.strip()
            data_dict['provider'] = "Indeed"
            data_dict['location'] = link3.text

            data_dict['postDate'] = link4.text

            if str(request.get_description) == "1":
                try:
                    source_new = get_request(data_dict['url'])
                except Exception as e:
                    print('{}')
                    sys.stderr.write(str(e))
                    return

                text_new = source_new.text
                to_crawl_new = BeautifulSoup(text_new, "lxml")
                divs = to_crawl_new.findAll('div', {'class': 'jobsearch-jobDescriptionText'})
                if len(divs) == 0:
                    print('{}')
                    sys.stderr.write("Divs are empty")
                    return

                job_desc = divs[0]
                data_dict['summary'] = job_desc.text

                email_in_description = re.findall(r'[\w.-]+@[\w.-]+', job_desc.text)
                data_dict['emailInSummary'] = email_in_description
            jobs.append(data_dict)
        start += PROVIDER['limit']
        current_page += 1

    print(jobs.__len__())
    json_compatible_item_data = jsonable_encoder(jobs)
    return JSONResponse(content=json_compatible_item_data)


def get_iso_code(country):
    return pycountry.countries.get(name=country.title()).alpha_2.lower()


def get_base_url(iso_code):
    if iso_code == "us":
        return PROVIDER["base_url"]
    elif iso_code in COUNTRIES_SUFFIX:
        return PROVIDER["base_url_B"]
    elif iso_code in COUNTRIES_SPECIAL:
        return PROVIDER["base_url_C"]
    else:
        return PROVIDER["base_url_A"]
