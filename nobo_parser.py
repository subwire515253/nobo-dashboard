# nobo_parser.py
import pandas as pd
import re

def classify_holder(name, shares):
    name_lower = str(name).lower()
    institutional_keywords = ["trust", "llc", "inc", "bank", "custodian", "ira", "corp", "fund", "capital", "partners"]
    broker_keywords = ["charles schwab", "fidelity", "td ameritrade", "etrade", "robinhood"]

    if any(kw in name_lower for kw in institutional_keywords):
        return "Institutional"
    elif any(kw in name_lower for kw in broker_keywords):
        return "Retail Platform"
    elif shares >= 100000:
        return "Likely Institutional"
    elif shares <= 25000:
        return "Retail"
    else:
        return "Unclassified"

def extract_zip(zip_val):
    zip_str = str(zip_val)
    match = re.search(r"\b(\d{5})\b", zip_str)
    return match.group(1) if match else None

def parse_nobo_file(uploaded_file):
    # Target specific sheet used by Broadridge
    sheet_name = "DigiAsia - Broadridge NOBO LIST"
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name, skiprows=4)

    # Assign proper column names
    df.columns = [
        "shares",
        "name_line_1",
        "name_line_2",
        "name_line_3",
        "name_line_4",
        "name_line_5",
        "name_line_6",
        "name_line_7",
        "zip_code"
    ]

    # Clean and convert share values
    df["shares"] = pd.to_numeric(df["shares"], errors="coerce")
    df = df.dropna(subset=["shares"])

    # Combine address lines
    address_fields = [f"name_line_{i}" for i in range(1, 8)]
    df["full_address"] = df[address_fields].astype(str).agg(" ".join, axis=1).str.strip()

    # Normalize ZIP code
    df["zip_code"] = df["zip_code"].apply(extract_zip)

    # Classify holders
    df["holder_type"] = df.apply(lambda row: classify_holder(row["full_address"], row["shares"]), axis=1)

    return df.rename(columns={"holder_type": "Holder Type"})[["full_address", "zip_code", "shares", "Holder Type"]]

