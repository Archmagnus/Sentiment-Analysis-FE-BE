# app.py
import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go
from PIL import Image
import time
import os

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
MAX_RETRIES = 3
RETRY_DELAY = 2

# Helper functions
def check_backend():
    """Check if backend is available"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=3)
        return response.status_code < 500
    except:
        return False

def safe_api_call(url, method="post", **kwargs):
    """Make API call with retries"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.request(
                method,
                url,
                timeout=10,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(RETRY_DELAY)
    return None

# UI Setup
st.set_page_config(page_title="Sentiment Analysis", layout="wide")
st.title("📊 Sentiment Analysis Dashboard")

# Connection check
if not check_backend():
    st.error("⚠️ Backend service unavailable. Please ensure the API server is running.")
    st.info(f"Trying to connect to: {BACKEND_URL}")
    if st.button("Retry Connection"):
        st.experimental_rerun()
    st.stop()

# Main App
uploaded_file = st.file_uploader("Upload your data file", type=["csv", "xlsx"])

if uploaded_file:
    # Display file preview
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.subheader("Data Preview")
        st.dataframe(df.head())
        
        # Select text column
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        if not text_cols:
            st.error("No text columns found in the data")
            st.stop()
        
        selected_col = st.selectbox("Select text column for analysis", text_cols)
        
        # Analysis sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sentiment Analysis")
            try:
                with st.spinner("Analyzing sentiment..."):
                    response = safe_api_call(
                        f"{BACKEND_URL}/sentiment-pie",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue())}
                    )
                    
                    data = response.json()
                    fig = go.Figure(go.Pie(
                        labels=data["labels"],
                        values=data["values"],
                        hole=0.3
                    ))
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Sentiment analysis failed: {str(e)}")
        
        with col2:
            st.subheader("Word Cloud")
            try:
                with st.spinner("Generating word cloud..."):
                    response = safe_api_call(
                        f"{BACKEND_URL}/wordcloud",
                        json={"texts": df[selected_col].dropna().astype(str).tolist()}
                    )
                    
                    img = Image.open(BytesIO(response.content))
                    st.image(img, caption="Word Cloud", use_container_width=True)
            except Exception as e:
                st.error(f"Word cloud generation failed: {str(e)}")
                
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")