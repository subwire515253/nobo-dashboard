
from alerts import generate_alerts

def build_unified_report(nobo_df, sec_data):
    enriched = generate_alerts(nobo_df.copy(), sec_data)
    return enriched
