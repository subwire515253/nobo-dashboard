
import pandas as pd

def parse_nobo_file(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)
    if "DigiAsia - Broadridge NOBO LIST" not in xls.sheet_names:
        raise ValueError("Expected sheet not found in uploaded file.")

    sheet = xls.parse("DigiAsia - Broadridge NOBO LIST", skiprows=1)
    sheet = sheet.rename(columns=lambda x: str(x).strip())

    sheet = sheet.rename(columns={
        "Securityholder Name and Address": "Full Address",
        "Total Shares Held": "Shares",
        "Zip": "Zip Code",
        "State": "State"
    })

    sheet = sheet.dropna(subset=["Shares"])
    sheet["Shares"] = pd.to_numeric(sheet["Shares"], errors="coerce")
    sheet["Shares"] = sheet["Shares"].fillna(0).astype(int)

    def tag_holder_type(address):
        if pd.isna(address):
            return "Unknown"
        inst_keywords = ["LLC", "LP", "Capital", "Fund", "Advisors", "Partners", "Investments", "Asset", "Management", "Bank"]
        return "Institutional" if any(k in address for k in inst_keywords) else "Retail"

    sheet["holder_type"] = sheet["Full Address"].apply(tag_holder_type)

    return sheet
