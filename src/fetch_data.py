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
            "startPeriod": "2006-Q1",
            "detail": "dataonly",
        },
    },
    {
        "id": "HK_PROPERTY_INDEX",
        "src": "bis",
        "url": "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_DPP/1.0/M.HK.0.1.0.1.1.0",
        "params": {
            "format": "csv",
            "startPeriod": "2006-01",
        },
    },
    {
        "id": "HK_AGG_BALANCE",
        "src": "hkma",
        "url": "https://api.hkma.gov.hk/public/market-data-and-statistics/daily-monetary-statistics/daily-figures-monetary-base",
        "params": {
            "pagesize": 8000,
            "sortby": "end_of_date",
            "sortorder": "desc",
        },
    },
]


def fetch_data():
    for indicator in indicators:
        max_retries = 3
        retry_delay = 2
        for retry in range(max_retries):
            response = requests.get(indicator["url"], params=indicator["params"])
            if response.status_code == 200:
                break
            elif response.status_code in [429, 500]:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise RuntimeError(f"Could not fetch {indicator['id']}.")
        if indicator["src"] == "bis":
            bis_data = response.text
            bis_results.append(bis_data)
        else:
            hkma_data = response.json()
            hkma_results.append(hkma_data)
        return bis_results, hkma_results
