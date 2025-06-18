# sec_scraper.py
import requests
import pandas as pd
import time

HEADERS = {
    "User-Agent": "nobo-dashboard/1.0 subir@example.com"
}

def get_cik(ticker):
    url = f"https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise ValueError("Failed to fetch ticker-CIK mapping from SEC.")
    
    data = response.json()
    for item in data.values():
        if item["ticker"].lower() == ticker.lower():
            return str(item["cik_str"]).zfill(10)
    raise ValueError(f"CIK not found for ticker: {ticker}")

def fetch_filings(cik, form_type):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return pd.DataFrame()
    
    data = response.json()
    filings = data.get("filings", {}).get("recent", {})
    df = pd.DataFrame(filings)

    if df.empty:
        return df

    df = df[df["form"] == form_type]

    if "accessionNumber" not in df.columns or "primaryDocument" not in df.columns:
        df["url"] = None
    else:
        df["url"] = df.apply(
            lambda row: f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{str(row['accessionNumber']).replace('-', '')}/{row['primaryDocument']}",
            axis=1
        )

    return df[["accessionNumber", "form", "filingDate", "url"]]

def fetch_sec_data(ticker):
    cik = get_cik(ticker)
    forms_to_fetch = ["S-1", "F-1", "4", "SC 13D"]
    sec_data = {}

    for form in forms_to_fetch:
        time.sleep(0.5)
        try:
            sec_data[form] = fetch_filings(cik, form)
        except Exception as e:
            sec_data[form] = pd.DataFrame()
            print(f"Error fetching {form}: {e}")

    return sec_data
