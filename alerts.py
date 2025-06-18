
def generate_alerts(nobo_df, sec_data):
    def match_names(nobo_df, filings_dict):
        name_field = "Full Address"
        matches = []
        for form, df in filings_dict.items():
            if df.empty:
                continue
            sec_names = df["companyName"].str.lower().fillna("")
            sec_dates = df["filingDate"]
            for idx, row in nobo_df.iterrows():
                name = str(row.get(name_field, "")).lower()
                for sec_name, sec_date in zip(sec_names, sec_dates):
                    if name[:10] in sec_name:
                        matches.append((idx, form, sec_date))
                        break
        return matches

    matched = match_names(nobo_df, sec_data)
    nobo_df["matched_filing"] = ""
    nobo_df["matched_filing_date"] = ""
    nobo_df["risk_flag"] = ""

    for idx, form, date in matched:
        nobo_df.at[idx, "matched_filing"] = form
        nobo_df.at[idx, "matched_filing_date"] = date
        if form in ["S-1", "F-1"]:
            nobo_df.at[idx, "risk_flag"] = "⚠️"
        elif form == "4":
            nobo_df.at[idx, "risk_flag"] = "🧨"
        elif form == "SC 13D":
            nobo_df.at[idx, "risk_flag"] = "🏴"
    return nobo_df
