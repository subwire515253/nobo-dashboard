import pandas as pd

def parse_nobo_file(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)
    
    # Always select the 3rd sheet as NOBO list (index 2)
    target_sheet_name = xls.sheet_names[2]
    sheet = pd.read_excel(xls, sheet_name=target_sheet_name, header=None)

    # Dynamically find the header row containing 'Name' and 'Share'
    header_row_index = None
    for idx, row in sheet.iterrows():
        row_str = row.astype(str).str.lower()
        if any("name" in cell for cell in row_str) and any("share" in cell for cell in row_str):
            header_row_index = idx
            break

    if header_row_index is None:
        raise ValueError("❌ Could not locate header row in sheet.")

    # Reload sheet with proper header row
    sheet = pd.read_excel(xls, sheet_name=target_sheet_name, header=header_row_index)

    # Rename first 7 known columns only
    expected_cols = ['Shares', 'Name', 'Address1', 'Address2', 'Address3', 'Address4', 'Address5']
    rename_map = {}
    for i, name in enumerate(expected_cols):
        if i < len(sheet.columns):
            rename_map[sheet.columns[i]] = name
    sheet.rename(columns=rename_map, inplace=True)

    # Drop rows without share counts
    share_col = rename_map.get(sheet.columns[0], 'Shares')
    sheet = sheet.dropna(subset=[share_col])

    # Remove totals or summary rows
    sheet = sheet[~sheet[share_col].astype(str).str.contains("Total", case=False, na=False)]

    # Parse address block
    sheet['Full Address'] = sheet[['Address1', 'Address2', 'Address3', 'Address4', 'Address5']].fillna('').agg(' '.join, axis=1)
    sheet['Full Address'] = sheet['Full Address'].str.replace(r'\s+', ' ', regex=True).str.strip()

    # Split address into components
    sheet['City'] = sheet['Full Address'].str.extract(r'([A-Za-z\s]+),')
    sheet['State'] = sheet['Full Address'].str.extract(r',\s*([A-Z]{2})\s')
    sheet['Zip Code'] = sheet['Full Address'].str.extract(r'(\d{5}(-\d{4})?)')
    sheet['Country'] = sheet['Full Address'].str.extract(r'(USA|Canada|United Kingdom|UAE|India|Singapore|Hong Kong)', expand=False)

    # Tag holder type
    def tag_holder_type(name):
        name = str(name).lower()
        if any(x in name for x in ['llc', 'lp', 'inc', 'fund', 'capital', 'trust', 'bank']):
            return 'Institutional'
        return 'Retail'

    sheet['holder_type'] = sheet['Name'].apply(tag_holder_type)

    # Return final structured DataFrame
    return sheet
