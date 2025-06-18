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
    try:
        filings_resp = requests.get(filings_url, headers=headers).json()
    except Exception as e:
        print(f"Error fetching filings: {e}")
        return {}

    sec_data = {}
    if "filings" not in filings_resp or "recent" not in filings_resp["filings"]:
        return {}

    recent = filings_resp["filings"]["recent"]
    forms_to_scrape = ["S-1", "F-1", "4", "SC 13D"]

    for form in forms_to_scrape:
        idxs = [i for i, f in enumerate(recent["form"]) if f.upper() == form]
        rows = []
        for i in idxs:
            try:
                acc = recent["accessionNumber"][i]
                doc = recent["primaryDocument"][i]
                url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/{doc}"
                rows.append({
                    "accession": acc,
                    "primary_doc": doc,
                    "filing_date": recent["filingDate"][i],
                    "url": url
                })
            except Exception as e:
                continue
        sec_data[form] = pd.DataFrame(rows)

    return sec_data
