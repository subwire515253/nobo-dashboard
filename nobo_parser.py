
import pandas as pd
import re

def parse_nobo_file(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)
    sheet = xls.parse(xls.sheet_names[2], header=5)

    # Drop unnamed and empty columns
    sheet = sheet.loc[:, ~sheet.columns.str.contains('^Unnamed')]

    # Rename expected columns
    sheet.columns = ['Shares', 'Name', 'Address1', 'Address2', 'Address3', 'Address4', 'Address5']
    sheet = sheet.dropna(subset=["Shares"])
    sheet = sheet.reset_index(drop=True)

    def classify_line(line):
        line = str(line).strip().lower()
        if any(x in line for x in ["trust", "plan", "fbo", "custodian"]):
            return "custodian"
        if re.match(r'\d{5}(-\d{4})?$', line):
            return "zip"
        if any(x in line for x in ["usa", "united states", "singapore", "canada", "uk", "uae"]):
            return "country"
        if any(x in line for x in ["st", "ave", "rd", "dr", "ln", "blvd"]):
            return "street"
        return "misc"

    parsed_rows = []
    for _, row in sheet.iterrows():
        lines = [row[f"Address{i}"] for i in range(1, 6) if pd.notnull(row[f"Address{i}"])]
        line_tags = [classify_line(line) for line in lines]
        addr_map = dict(zip(line_tags, lines))

        parsed_rows.append({
            "Shares": row["Shares"],
            "Name": row["Name"],
            "Street": addr_map.get("street", ""),
            "City": addr_map.get("misc", ""),
            "State": "",
            "Zip Code": addr_map.get("zip", ""),
            "Country": addr_map.get("country", "USA"),
            "holder_type": "Institutional" if "bank" in row["Name"].lower() or "trust" in row["Name"].lower() else "Retail"
        })

    return pd.DataFrame(parsed_rows)
