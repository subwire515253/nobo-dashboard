# utils.py
import pandas as pd
import matplotlib.pyplot as plt
import io
import streamlit as st

def plot_holder_distribution(df):
    counts = df['Holder Type'].value_counts()
    fig, ax = plt.subplots()
    counts.plot(kind='bar', ax=ax)
    ax.set_title('Holder Type Distribution')
    ax.set_ylabel('Count')
    st.pyplot(fig)

def plot_zip_distribution(df):
    zip_counts = df['Zip Code'].value_counts().head(10)
    fig, ax = plt.subplots()
    zip_counts.plot(kind='bar', ax=ax)
    ax.set_title('Top 10 ZIP Codes by Holder Count')
    ax.set_ylabel('Number of Holders')
    st.pyplot(fig)

def export_csv(df):
    csv = df.to_csv(index=False)
    return io.BytesIO(csv.encode())
