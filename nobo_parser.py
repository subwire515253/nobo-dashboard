import pandas as pd
import streamlit as st

def parse_nobo_file(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)

    # Confirm target sheet exists
    target_sheet = "DigiAsia - Broadridge NOBO LIST"
    if target_sheet not in xls.sheet_names:
        st.error(f"❌ Sheet '{target_sheet}' not found in uploaded file.")
        st.stop()

    sheet = xls.parse(target_sheet, skiprows=1)
    sheet.columns = sheet.columns.map(lambda x: str(x).strip())

    st.write("📄 Columns detected:", sheet.columns.tolist())

    # Flexible column matching (case-insensitive)
    col_map = {}
    for col in sheet.columns:
        if "total shares held" in col.lower():
            col_map[col] = "Shares"
        elif "securityholder" in col.lower():
            col_map[col] = "Full Address"
        elif "zip" in col.lower():
            col_map[col] = "Zip Code"
        elif "state" in col.lower():
            col_map[col] = "State"

    if not col_map:
        st.error("❌ Could not find required columns in the NOBO sheet.")
        st.stop()

    sheet = sheet.rename(columns=col_map)

    if "Shares" not in sheet.columns:
        st.error("❌ 'Shares' column not found after renaming. Cannot proceed.")
        st.stop()

    sheet["Shares"] = pd.to_numeric(sheet["Shares"], errors="coerce")
    sheet = sheet.dropna(subset=["Shares"])
    sheet["Shares"] = sheet["Shares"].astype(int)

    # Tag retail vs institutional
    def tag_holder_type(addr):
        if pd.isna(addr):
            return "Unknown"
        inst_keywords = ["LLC", "LP", "Capital", "Fund", "Advisors", "Partners", "Investments", "Asset", "Management", "Bank"]
        return "Institutional" if any(k in addr for k in inst_keywords) else "Retail"

    sheet["holder_type"] = sheet["Full Address"].apply(tag_holder_type)

    return sheet
