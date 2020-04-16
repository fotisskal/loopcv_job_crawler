PROVIDERS = {
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
