import requests
import time

bis_results = []
hkma_results = []
indicators = [
    {
        "id": "HK_CREDIT_GAP",
        "src": "bis",
        "url": "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CREDIT_GAP/1.0/Q.HK.P.A.B",
        "params": {
            "format": "csv",
            "startPeriod": "1988-Q4",
            "detail": "dataonly",
        },
    },
    {
        "id": "HK_PROPERTY_INDEX",
        "src": "bis",
        "url": "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_DPP/1.0/M.HK.0.1.0.1.1.0",
        "params": {
            "format": "csv",
            "startPeriod": "1993-01",
        },
    },
    {
        "id": "HK_AGG_BALANCE",
        "src": "hkma",
        "url": "https://api.hkma.gov.hk/public/market-data-and-statistics/daily-monetary-statistics/daily-figures-monetary-base",
        "params": {
            "pagesize": 1000,
            "offset": 0,
            "sortby": "end_of_date",
            "sortorder": "desc",
        },
    },
]


def fetch_with_retry(url, params, max_retries=3):
    retry_delay = 2
    for retry in range(max_retries):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response
        elif response.status_code in [429, 500, 502, 503, 504]:
            time.sleep(retry_delay)
            retry_delay *= 2
        else:
            response.raise_for_status()
    response.raise_for_status()


def fetch_data():
    for indicator in indicators:
        if indicator["src"] == "hkma":
            # HKMA API returns max 1000 records/page; 9 pages covers ~25 years of daily data
            for page in range(9):
                indicator["params"]["offset"] = page * 1000
                response = fetch_with_retry(indicator["url"], indicator["params"])
                hkma_results.append(response.json())
        else:
            response = fetch_with_retry(indicator["url"], indicator["params"])
            bis_results.append(response.text)

    return bis_results, hkma_results
