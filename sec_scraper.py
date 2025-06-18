# sec_scraper.py

import requests
import pandas as pd

headers = {
    "User-Agent": "ShareholderDashboard/1.0 (contact@yourdomain.com)",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

def fetch_sec_data(ticker):
    base_url = "https://data.sec.gov"
    cik_lookup_url = "https://www.sec.gov/files/company_tickers.json"

    try:
        response = requests.get(cik_lookup_url, headers=headers)
        data = response.json()
        cik_entry = next((entry for entry in data.values() if entry["ticker"].upper() == ticker.upper()), None)
        if not cik_entry:
            raise ValueError("CIK not found for ticker.")
        cik = str(cik_entry["cik_str"]).zfill(10)
    except Exception as e:
        print(f"Error fetching CIK: {e}")
        return {}

    filings_url = f"{base_url}/submissions/CIK{cik}.json"
    tr
