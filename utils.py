
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from io import StringIO

def plot_holder_distribution(df):
    if 'holder_type' in df.columns:
        counts = df['holder_type'].value_counts()
        fig, ax = plt.subplots()
        counts.plot(kind='bar', ax=ax)
        ax.set_title("Holder Type Distribution")
        ax.set_ylabel("Count")
        st.pyplot(fig)

def plot_zip_distribution(df):
    if 'Zip Code' in df.columns:
        zip_counts = df['Zip Code'].value_counts().head(10)
        fig, ax = plt.subplots()
        zip_counts.plot(kind='bar', ax=ax)
        ax.set_title("Top Zip Codes")
        ax.set_ylabel("Count")
        st.pyplot(fig)

def export_csv(df):
    return df.to_csv(index=False)
