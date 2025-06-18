# sec_scraper.py
import requests
import pandas as pd
import time

BASE_URL = "https://www.sec.gov"
HEADERS = {"User-Agent": "Aegis Asia IR Analytics (info@aegisasia.com)"}

def get_cik(ticker):
    url = f"https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        for entry in data.values():
            if entry['ticker'].lower() == ticker.lower():
                return str(entry['cik_str']).zfill(10)
    return None

def fetch_filings(cik, form_type, count=10):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return pd.DataFrame()
    data = res.json()
    filings = data.get("filings", {}).get("recent", {})
    df = pd.DataFrame({
        'date': filings.get('filingDate', []),
        'form': filings.get('form', []),
        'accession': filings.get('accessionNumber', []),
        'primary_doc': filings.get('primaryDocument', [])
    })
    df = df[df['form'] == form_type].head(count)
    df['url'] = df.apply(lambda row: f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{row['accession'].replace('-', '')}/{row['primary_doc']}", axis=1)
    return df.reset_index(drop=True)

def fetch_sec_data(ticker):
    cik = get_cik(ticker)
    if not cik:
        return {"Error": pd.DataFrame([{"message": "CIK not found for ticker."}])}
    sec_data = {}
    for form in ["13F-HR", "SC 13D", "SC 13G", "4", "S-1", "F-1"]:
        sec_data[form] = fetch_filings(cik, form)
        time.sleep(0.5)
    return sec_data
