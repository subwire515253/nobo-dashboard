# app.py (final version with NOBO/OBO summary integration)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from nobo_parser import parse_nobo_file
from sec_scraper import fetch_sec_data
from alerts import generate_alerts
from report_builder import build_unified_report
from utils import plot_holder_distribution, plot_zip_distribution, export_csv

st.set_page_config(layout="wide")
st.title("📊 Shareholder Intelligence Dashboard")

uploaded_file = st.file_uploader("Upload Broadridge NOBO Excel", type=["xlsx"])
ticker = st.text_input("Enter Ticker Symbol (for SEC scraping)", "FAAS")

if uploaded_file:
    st.subheader("📋 Parsed NOBO Data")
    nobo_df, summary_nobo_df, summary_obo_df = parse_nobo_file(uploaded_file)
    st.dataframe(nobo_df)

    col1, col2 = st.columns(2)
    with col1:
        plot_holder_distribution(nobo_df)
    with col2:
        plot_zip_distribution(nobo_df)

    csv = export_csv(nobo_df)
    st.download_button("⬇️ Download Cleaned NOBO CSV", csv, "nobo_clean.csv", "text/csv")

    # Show NOBO/OBO Summary Tabs
    st.subheader("📊 Share Range Summary (NOBO Holders)")
    st.dataframe(summary_nobo_df)

    st.subheader("📊 Share Range Summary (OBO Holders)")
    st.dataframe(summary_obo_df)

    # Visualize share ranges
    if 'Share Range' in summary_nobo_df.columns and '# of Holders' in summary_nobo_df.columns:
        try:
            fig, ax = plt.subplots()
            summary_nobo_df.plot(kind='bar', x='Share Range', y='# of Holders', ax=ax, color='skyblue', legend=False)
            ax.set_title("NOBO Share Range Distribution")
            ax.set_ylabel("Number of Holders")
            st.pyplot(fig)
        except Exception:
            st.warning("📉 Could not render NOBO range chart.")

    if 'Share Range' in summary_obo_df.columns and '# of Holders' in summary_obo_df.columns:
        try:
            fig, ax = plt.subplots()
            summary_obo_df.plot(kind='bar', x='Share Range', y='# of Holders', ax=ax, color='lightgreen', legend=False)
            ax.set_title("OBO Share Range Distribution")
            ax.set_ylabel("Number of Holders")
            st.pyplot(fig)
        except Exception:
            st.warning("📉 Could not render OBO range chart.")

    if ticker:
        st.subheader("📄 SEC Filing Intelligence")
        sec_data = fetch_sec_data(ticker)
        for form, df in sec_data.items():
            if not df.empty:
                with st.expander(f"{form} Filings ({len(df)})"):
                    st.dataframe(df)

        st.subheader("🔎 Unified Risk Intelligence View")
        report_df = build_unified_report(nobo_df, sec_data)

        def highlight_risk(row):
            if row['risk_flag'] == "⚠️":
                return ['background-color: #fff3cd'] * len(row)
            elif row['risk_flag'] == "🧨":
                return ['background-color: #f8d7da'] * len(row)
            return [''] * len(row)

        def inject_emojis(row):
            tag = row['matched_filing']
            if tag == "S-1":
                return "⚠️ PIPE"
            elif tag == "F-1":
                return "⚠️ Foreign Resale"
            elif tag == "4":
                return "🧨 Insider"
            elif tag == "SC 13D":
                return "🏴 Activist"
            return "✅ Clean"

        report_df['🧠 Risk Tag'] = report_df.apply(inject_emojis, axis=1)

        # Filters
        st.subheader("🔍 Filter by Region or Holder Type")
        zip_filter = st.multiselect("Filter by Zip Code", sorted(report_df['Zip Code'].dropna().unique().tolist()))
        state_filter = st.multiselect("Filter by State", sorted(report_df['State'].dropna().unique().tolist()))
        holder_type_filter = st.multiselect("Filter by Holder Type", ['Retail', 'Institutional'])

        if zip_filter:
            report_df = report_df[report_df['Zip Code'].isin(zip_filter)]
        if state_filter:
            report_df = report_df[report_df['State'].isin(state_filter)]
        if holder_type_filter:
            report_df = report_df[report_df['holder_type'].isin(holder_type_filter)]

        styled_df = report_df.style.apply(highlight_risk, axis=1)

        st.markdown("""
        ### 🧾 Risk Alert Legend
        - ⚠️ **Yellow Row** → Potential PIPE or resale (S-1/F-1)
        - 🧨 **Red Row** → Insider trading activity (Form 4)
        - 🏴 **Tag** → Activist investor (SC 13D)
        - ✅ **Clean** → No flagged filings
        """)

        st.dataframe(styled_df, use_container_width=True)

        csv_report = export_csv(report_df)
        st.download_button("⬇️ Download Full Risk Report", csv_report, "shareholder_risk_report.csv", "text/csv")

        st.subheader("📊 Risk Distribution Charts")

        if '🧠 Risk Tag' in report_df.columns:
            col1, col2 = st.columns(2)
            with col1:
                fig1, ax1 = plt.subplots()
                report_df['🧠 Risk Tag'].value_counts().plot(kind='bar', ax=ax1, color='coral')
                ax1.set_title("Holder Count by Risk Tag")
                ax1.set_ylabel("Number of Holders")
                st.pyplot(fig1)
            with col2:
                fig2, ax2 = plt.subplots()
                report_df['🧠 Risk Tag'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax2, startangle=90)
                ax2.set_ylabel("")
                ax2.set_title("Risk Tag Share (Pie Chart)")
                st.pyplot(fig2)

        if 'Zip Code' in report_df.columns:
            top_zip_risks = report_df.groupby('Zip Code')['🧠 Risk Tag'].apply(lambda x: (x != '✅ Clean').sum()).sort_values(ascending=False).head(10)
            fig3, ax3 = plt.subplots()
            top_zip_risks.plot(kind='bar', ax=ax3, color='salmon')
            ax3.set_title("Top ZIP Codes by Risk Flag Count")
            ax3.set_ylabel("Risk Holder Count")
            st.pyplot(fig3)

        if 'holder_type' in report_df.columns:
            fig5, ax5 = plt.subplots()
            pd.crosstab(report_df['holder_type'], report_df['🧠 Risk Tag']).plot(kind='bar', stacked=True, ax=ax5)
            ax5.set_title("Risk Tag Distribution by Holder Type")
            ax5.set_ylabel("Number of Holders")
            st.pyplot(fig5)

        if 'matched_filing_date' in report_df.columns:
            try:
                trend_df = report_df.copy()
                trend_df['filing_date'] = pd.to_datetime(trend_df['matched_filing_date'], errors='coerce')
                trend_df = trend_df.dropna(subset=['filing_date'])
                trend_df['week'] = trend_df['filing_date'].dt.to_period('W').astype(str)
                trend_series = trend_df.groupby('week')['🧠 Risk Tag'].apply(lambda x: (x != '✅ Clean').sum())
                fig4, ax4 = plt.subplots()
                trend_series.plot(ax=ax4, marker='o', color='firebrick')
                ax4.set_title("📈 Weekly Risk Filing Trend")
                ax4.set_ylabel("Risky Filings")
                ax4.set_xlabel("Week")
                st.pyplot(fig4)
            except Exception:
                st.warning("Filing trendline unavailable due to date parse error.")
