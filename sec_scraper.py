
import requests
import pandas as pd

def fetch_sec_data(ticker):
    cik_lookup_url = f"https://www.sec.gov/files/company_tickers.json"
    cik_data = requests.get(cik_lookup_url).json()

    matched = None
    for entry in cik_data.values():
        if entry["ticker"].lower() == ticker.lower():
            matched = entry
            break
    if not matched:
        return {}

    cik = str(matched["cik_str"]).zfill(10)
    forms_to_fetch = ["S-1", "F-1", "4", "SC 13D"]

    def fetch_filings(cik, form):
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        headers = {"User-Agent": "NOBO Intelligence"}
        resp = requests.get(url, headers=headers)
        if not resp.ok:
            return pd.DataFrame()

        data = resp.json()
        recent = data.get("filings", {}).get("recent", {})
        df = pd.DataFrame(recent)
        df = df[df["form"] == form]
        df['url'] = df.apply(lambda row: f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{row['accessionNumber'].replace('-', '')}/{row['primaryDocument']}", axis=1)
        return df[["form", "filingDate", "url", "companyName", "accessionNumber", "primaryDocument"]]

    filings = {}
    for form in forms_to_fetch:
        filings[form] = fetch_filings(cik, form)
    return filings
