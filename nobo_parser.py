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
    sheet = xls.parse(xls.sheet_names[0], skiprows=2)  # Auto-pick first sheet
    sheet.columns = [str(c).strip().lower() for c in sheet.columns]

    # Try to find a column that contains 'share'
    share_col = next((col for col in sheet.columns if 'share' in col), None)
    if not share_col:
        raise ValueError(f"Could not locate a share column. Found columns: {sheet.columns.tolist()}")

    # Try to build full address
    address_fields = [col for col in sheet.columns if "address" in col and "line" in col]
    if not address_fields:
        raise ValueError("Could not locate address columns.")

    sheet = sheet.dropna(subset=[share_col])
    sheet["Full Address"] = sheet[address_fields].fillna("").agg(" ".join, axis=1).str.strip()
    sheet["Zip Code"] = sheet["Full Address"].apply(extract_zip)
    sheet["Shares"] = pd.to_numeric(sheet[share_col], errors='coerce')
    sheet["Holder Type"] = sheet.apply(lambda row: classify_holder(row["Full Address"], row["Shares"]), axis=1)

    return sheet[["Full Address", "Zip Code", "Shares", "Holder Type"]].dropna(subset=["Shares"])
