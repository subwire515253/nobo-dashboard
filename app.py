import streamlit as st
import pandas as pd
from nobo_parser import parse_nobo_file
from sec_scraper import fetch_sec_data
from alerts import generate_alerts
from utils import plot_holder_distribution, plot_zip_distribution, export_csv

st.set_page_config(layout="wide")
st.title("🧠 NOBO + SEC Shareholder Intelligence Dashboard")

uploaded_file = st.file_uploader("Upload Broadridge NOBO Excel", type=["xlsx"])
ticker = st.text_input("Enter Ticker Symbol (for SEC scraping)", "FAAS")

if uploaded_file:
    st.subheader("📋 Parsed NOBO Data")
    nobo_df = parse_nobo_file(uploaded_file)
    st.dataframe(nobo_df)

    col1, col2 = st.columns(2)
    with col1:
        plot_holder_distribution(nobo_df)
    with col2:
        plot_zip_distribution(nobo_df)

    csv = export_csv(nobo_df)
    st.download_button("Download Cleaned NOBO CSV", csv, "nobo_clean.csv", "text/csv")

    if ticker:
        st.subheader("📄 SEC Filing Intelligence")
        sec_data = fetch_sec_data(ticker)
        for form, df in sec_data.items():
            if not df.empty:
                with st.expander(f"{form} Filings ({len(df)})"):
                    st.dataframe(df)

        st.subheader("🚨 Risk Alerts & Matches")
        alerts = generate_alerts(nobo_df, sec_data)
        if not alerts:
            st.success("No critical alerts or matches found.")
        else:
            for key, val in alerts.items():
                st.error(key)
                st.dataframe(val)
