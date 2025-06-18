
import pandas as pd
from fuzzywuzzy import fuzz

def build_unified_report(nobo_df, sec_data):
    all_records = []
    for form, df in sec_data.items():
        if df.empty: continue
        for _, row in df.iterrows():
            all_records.append({
                "form": form,
                "accession": row["accession"],
                "filing_date": row["filing_date"],
                "name_fuzzy": row["accession"]
            })
    filing_df = pd.DataFrame(all_records)

    matched = []
    for _, row in nobo_df.iterrows():
        name = row["Name"]
        best_match = ""
        best_score = 0
        matched_form = ""
        for form, fdf in sec_data.items():
            for _, srow in fdf.iterrows():
                score = fuzz.partial_ratio(name.lower(), srow["accession"].lower())
                if score > best_score and score > 70:
                    best_score = score
                    best_match = srow["accession"]
                    matched_form = form
        row = row.copy()
        row["matched_filing"] = matched_form
        row["matched_filing_date"] = None
        row["risk_flag"] = "🧨" if matched_form == "4" else ("⚠️" if matched_form in ["S-1", "F-1"] else "")
        matched.append(row)

    return pd.DataFrame(matched)
