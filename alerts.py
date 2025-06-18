# alerts.py
import pandas as pd
from fuzzywuzzy import fuzz

def match_names(nobo_df, sec_df, name_field="Full Address", threshold=85):
    matches = []
    nobo_names = nobo_df[name_field].str.lower().fillna("")
    for idx, row in sec_df.iterrows():
        sec_name_field = str(row.get("url", "")).lower()
        for nobo_name in nobo_names:
            score = fuzz.partial_ratio(nobo_name, sec_name_field)
            if score >= threshold:
                matches.append({
                    "nobo_name": nobo_name,
                    "sec_url": sec_name_field,
                    "match_score": score
                })
                break
    return pd.DataFrame(matches)

def generate_alerts(nobo_df, sec_data):
    alerts = {}

    # Unlock Risk → S-1 and F-1 matches
    resale_forms = pd.concat([sec_data.get("S-1", pd.DataFrame()), sec_data.get("F-1", pd.DataFrame())])
    if not resale_forms.empty:
        unlock_alerts = match_names(nobo_df, resale_forms)
        if not unlock_alerts.empty:
            alerts["🚨 PIPE Unlock Risk"] = unlock_alerts

    # Insider Selling → Form 4s
    form4 = sec_data.get("4", pd.DataFrame())
    if not form4.empty:
        alerts["🧨 Insider Activity (Form 4)"] = form4

    # Activist Accumulation → SC 13D
    sc13d = sec_data.get("SC 13D", pd.DataFrame())
    if not sc13d.empty:
        alerts["🏴 Activist Accumulation (SC 13D)"] = sc13d

    return alerts
