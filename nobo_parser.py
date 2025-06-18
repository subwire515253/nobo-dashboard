import pandas as pd

def parse_nobo_file(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)

    # Always use the 3rd worksheet (index 2) for NOBO list
    target_sheet_name = xls.sheet_names[2]
    sheet = pd.read_excel(xls, sheet_name=target_sheet_name, header=None)

    # Dynamically find the header row (must include 'name' and 'share')
    header_row_index = None
    for idx, row in sheet.iterrows():
        row_str = row.astype(str).str.lower()
        if any("name" in cell for cell in row_str) and any("share" in cell for cell in row_str):
            header_row_index = idx
            break

    if header_row_index is None:
        raise ValueError("❌ Could not locate header row in sheet.")

    # Reload with proper header
    sheet = pd.read_excel(xls, sheet_name=target_sheet_name, header=header_row_index)

    # Rename only the first 7 expected columns
    expected_cols = ['Shares', 'Name', 'Address1', 'Address2', 'Address3', 'Address4', 'Address5']
    rename_map = {}
    for i, col in enumerate(expected_cols):
        if i < len(sheet.columns):
            rename_map[sheet.columns[i]] = col
    sheet.rename(columns=rename_map, inplace=True)

    # Drop rows missing share values
    share_col = 'Shares'
    if share_col not in sheet.columns:
        raise ValueError("❌ Could not find 'Shares' column after renaming.")
    sheet = sheet.dropna(subset=[share_col])

    # Filter out totals/summary lines
    sheet = sheet[~sheet[share_col].astype(str).str.contains("total", case=False, na=False)]

    # ✅ Clean and concatenate address parts safely
    address_cols = ['Address1', 'Address2', 'Address3', 'Address4', 'Address5']
    sheet['Full Address'] = sheet[address_cols].fillna('').astype(str).agg(' '.join, axis=1)
    sheet['Full Address'] = sheet['Full Address'].str.replace(r'\s+', ' ', regex=True).str.strip()

    # Extract city, state, zip, country
    sheet['City'] = sheet['Full Address'].str.extract(r'([A-Za-z\s]+),')
    sheet['State'] = sheet['Full Address'].str.extract(r',\s*([A-Z]{2})\s')
    sheet['Zip Code'] = sheet['Full Address'].str.extract(r'(\d{5}(?:-\d{4})?)')
    sheet['Country'] = sheet['Full Address'].str.extract(r'(USA|Canada|United Kingdom|UAE|India|Singapore|Hong Kong)', expand=False)

    # Holder type tagging
    def tag_holder_type(name):
        name = str(name).lower()
        if any(x in name for x in ['llc', 'lp', 'inc', 'fund', 'capital', 'trust', 'bank']):
            return 'Institutional'
        return 'Retail'

    sheet['holder_type'] = sheet['Name'].apply(tag_holder_type)

    return sheet
