PROVIDERS = {
    "linkedin": {
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
    },
    "indeed": {
        "base_url": "https://www.indeed.co.%(country_code)/jobs",
        "login": False,
        "keyword": "q",
        "location": "!",
        "remote": {
            "supported": True,
            "param": "location"
        },
        "page_number": {
            "param": "start",
            "value": 50
        },
        "limit": {
            "param": "limit",
            "value": 50
        },
        "pagination": True
    },
    "github": {
        "base_url": "https://jobs.github.com/positions",
        "login": False,
        "keyword": "description",
        "location": "location",
        "remote": {
            "supported": True,
            "param": "location"
        },
        "page_number": {
            "param": "page",
            "value": 1
        },
        "pagination": True
    },
    "stackoverflow": {
        "base_url": "https://stackoverflow.com/jobs",
        "login": False,
        "keyword": "q",
        "location": "!",
        "remote": {
            "supported": True,
            "param": "r"
        },
        "page_number": {
            "param": "pg",
            "value": 1
        },
        "pagination": True
    },
    "glassdoor": {
        "login": "True"
    },
    # "simplyhired": {
    #     "base_url": "https://www.simplyhired.co.%(country_code)/search",
    #     "keyword": "q",
    #     "location": "!",
    #     "remote": {
    #         "supported": True,
    #         "param": "location"
    #     },
    #     "page_number": {
    #         "param": "pn",
    #         "value": 1
    #     },
    #     "pagination": True
    # }
}
