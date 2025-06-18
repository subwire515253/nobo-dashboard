# nobo_parser.py
import pandas as pd
import re

KEYWORDS_INSTITUTIONAL = ["trust", "llc", "inc", "bank", "custodian", "ira", "corp"]
KEYWORDS_BROKERS = ["charles schwab", "fidelity", "td ameritrade", "etrade"]

def classify_holder(name, shares):
    name_lower = str(name).lower()
    if any(kw in name_lower for kw in KEYWORDS_INSTITUTIONAL):
        return "Institutional"
    elif any(kw in name_lower for kw in KEYWORDS_BROKERS):
        return "Retail Platform"
    elif shares >= 100000:
        return "Likely Institutional"
    elif shares <= 25000:
        return "Retail"
    else:
        return "Unclassified"

def extract_zip(address):
    match = re.search(r"\b(\d{5})(?:[-\s]\d{4})?\b", str(address))
    return match.group(1) if match else None

def parse_nobo_file(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)
    sheet = xls.parse("DigiAsia - Broadridge NOBO LIST", skiprows=2)
    sheet = sheet.dropna(subset=["Total Shares Held"])
    sheet["Full Address"] = sheet[["Name and Address Line 1", "Name and Address Line 2", "Name and Address Line 3"]].fillna("").agg(" ".join, axis=1).str.strip()
    sheet["Zip Code"] = sheet["Full Address"].apply(extract_zip)
    sheet["Shares"] = pd.to_numeric(sheet["Total Shares Held"], errors='coerce')
    sheet["Holder Type"] = sheet.apply(lambda row: classify_holder(row["Full Address"], row["Shares"]), axis=1)
    return sheet[["Full Address", "Zip Code", "Shares", "Holder Type"]].dropna(subset=["Shares"])
