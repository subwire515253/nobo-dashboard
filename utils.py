
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from io import StringIO

def plot_holder_distribution(df):
    if 'holder_type' in df.columns:
        counts = df['holder_type'].value_counts()
        fig, ax = plt.subplots()
        counts.plot(kind='bar', ax=ax)
        ax.set_title("Retail vs Institutional Holders")
        st.pyplot(fig)

def plot_zip_distribution(df):
    if 'Zip Code' in df.columns:
        zip_counts = df['Zip Code'].value_counts().head(10)
        fig, ax = plt.subplots()
        zip_counts.plot(kind='bar', ax=ax)
        ax.set_title("Top 10 ZIP Codes by Holder Count")
        st.pyplot(fig)

def export_csv(df):
    buffer = StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue()
