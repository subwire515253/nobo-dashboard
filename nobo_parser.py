# nobo_parser.py

import pandas as pd

def parse_nobo_file(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)

    # ✅ Load the NOBO list from the 3rd worksheet regardless of name
    raw = xls.parse(xls.sheet_names[2], header=5)

    # Clean column names
    raw.columns = [str(col).strip() for col in raw.columns]

    # Extract core fields
    df = pd.DataFrame()
    df["Shares"] = pd.to_numeric(raw.iloc[:, 0], errors="coerce")
    df["Name"] = raw.iloc[:, 1].astype(str)
    df["Address"] = raw.iloc[:, 2].fillna("").astype(str) + ", " + \
                    raw.iloc[:, 3].fillna("").astype(str) + ", " + \
                    raw.iloc[:, 4].fillna("").astype(str) + ", " + \
                    raw.iloc[:, 5].fillna("").astype(str)
    df["Zip Code"] = raw.iloc[:, 8]
    df["State"] = raw.iloc[:, 6]

    df = df.dropna(subset=["Shares", "Name"])
    df["Shares"] = df["Shares"].astype(int)

    # 🔍 Tag holder type
    def tag_holder(name):
        name = name.lower()
        if any(x in name for x in ["trust", "bank", "llc", "ltd", "fund", "capital", "advisor", "partners", "corp", "inc"]):
            return "Institutional"
        return "Retail"

    df["holder_type"] = df["Name"].apply(tag_holder)

    # 📊 Also parse summary tabs
    summary_nobo = xls.parse(xls.sheet_names[0])
    summary_obo = xls.parse(xls.sheet_names[1])

    return df, summary_nobo, summary_obo
