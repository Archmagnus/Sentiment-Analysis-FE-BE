# UPDATED app.py
import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time
import os
from typing import Optional, Dict, Any

# 1. PAGE CONFIG
st.set_page_config(
    page_title="Sentiment Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stAlert { border-left: 4px solid #ff4b4b; }
    .stSpinner > div { justify-content: center; }
    .stProgress > div > div > div { background-color: #1f77b4; }
    </style>
""", unsafe_allow_html=True)

# Sidebar: dummy backend health
with st.sidebar:
    st.title("Connection Status")
    st.success("✅ Frontend standalone", icon="🟢")
    st.info("Word cloud and sentiment are now processed on the frontend.")

# Main App
st.title("📊 Sentiment Analysis Dashboard")
st.markdown("Upload a CSV or Excel file containing text data for analysis")

# File Upload
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "xlsx"],
    accept_multiple_files=False,
    help="Supported formats: CSV, Excel (xlsx, xls)"
)

if uploaded_file:
    try:
        with st.spinner("Processing your file..."):
            file_ext = uploaded_file.name.split(".")[-1].lower()
            if file_ext == "csv":
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

        with st.expander("📂 File Preview", expanded=True):
            st.dataframe(df.head(), use_container_width=True)
            st.caption(f"Total rows: {len(df)} | Columns: {', '.join(df.columns)}")

        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        if not text_cols:
            st.error("No text columns found in the uploaded file")
            st.stop()

        selected_col = st.selectbox(
            "Select text column for analysis",
            text_cols,
            help="Choose the column containing the text you want to analyze"
        )

        from textblob import TextBlob

        # Tabs
        tab1, tab2 = st.tabs(["Sentiment Analysis", "Word Cloud"])

        with tab1:
            st.subheader("Sentiment Distribution")
            try:
                texts = df[selected_col].dropna().astype(str).tolist()
                sentiments = [TextBlob(text).sentiment.polarity for text in texts]

                sentiment_labels = ['Positive' if s > 0.1 else 'Negative' if s < -0.1 else 'Neutral' for s in sentiments]
                sentiment_counts = pd.Series(sentiment_labels).value_counts()

                fig = go.Figure(go.Pie(
                    labels=sentiment_counts.index,
                    values=sentiment_counts.values,
                    hole=0.3,
                    marker_colors=['#2ca02c', '#ff7f0e', '#d62728'],
                    textinfo='percent+value'
                ))
                fig.update_layout(
                    legend_title="Sentiment",
                    margin=dict(t=0, b=0, l=0, r=0)
                )
                st.plotly_chart(fig, use_container_width=True)

                # Metrics
                for label in ['Positive', 'Neutral', 'Negative']:
                    st.metric(label, sentiment_counts.get(label, 0))
            except Exception as e:
                st.error(f"Sentiment analysis failed: {str(e)}")

        with tab2:
            st.subheader("Word Cloud Visualization")
            try:
                texts = df[selected_col].dropna().astype(str).tolist()
                full_text = " ".join(texts)
                wc = WordCloud(width=800, height=400, background_color="white").generate(full_text)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
                st.caption(f"Analyzed {len(texts)} text entries")
            except Exception as e:
                st.error(f"Word cloud generation failed: {str(e)}")

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.stop()

# Footer
st.markdown("---")
st.caption("Sentiment Analysis Dashboard v1.0 | Standalone Streamlit App")
