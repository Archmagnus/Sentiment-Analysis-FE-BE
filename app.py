# app.py
import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go
from PIL import Image
import time
import os
from typing import Optional, Dict, Any

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
MAX_RETRIES = 3
RETRY_DELAY = 2
TIMEOUT = 15  # Increased timeout for large files

# Custom CSS for better UI
st.markdown("""
    <style>
    .stAlert { border-left: 4px solid #ff4b4b; }
    .stSpinner > div { justify-content: center; }
    .stProgress > div > div > div { background-color: #1f77b4; }
    </style>
""", unsafe_allow_html=True)

def check_backend_health() -> bool:
    """Check if backend is available and healthy"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=3
        )
        return response.status_code == 200 and response.json().get("status") == "healthy"
    except Exception:
        return False

def safe_api_call(
    endpoint: str,
    method: str = "post",
    **kwargs
) -> Optional[Dict[str, Any]]:
    """Enhanced API call with retries, timeout, and better error handling"""
    url = f"{BACKEND_URL}{endpoint}"
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.request(
                method,
                url,
                timeout=TIMEOUT,
                **kwargs
            )
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.json().get("detail", str(e)) if e.response.content else str(e)
            if attempt == MAX_RETRIES - 1:
                raise Exception(f"API Error: {error_detail}")
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise Exception(f"Connection Error: {str(e)}")
        time.sleep(RETRY_DELAY)
    return None

# UI Setup
st.set_page_config(
    page_title="Sentiment Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Sidebar with connection info
with st.sidebar:
    st.title("Connection Status")
    if check_backend_health():
        st.success("✅ Backend connected", icon="🟢")
    else:
        st.error("⚠️ Backend unavailable", icon="🔴")
        if st.button("Retry Connection"):
            st.experimental_rerun()
        st.stop()
    
    st.info(f"Backend URL: `{BACKEND_URL}`")

# Main App
st.title("📊 Sentiment Analysis Dashboard")
st.markdown("Upload a CSV or Excel file containing text data for analysis")

# File Upload Section
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "xlsx"],
    accept_multiple_files=False,
    help="Supported formats: CSV, Excel (xlsx, xls)"
)

if uploaded_file:
    try:
        # File Processing
        with st.spinner("Processing your file..."):
            file_ext = uploaded_file.name.split(".")[-1].lower()
            if file_ext == "csv":
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        
        # Display file preview
        with st.expander("📂 File Preview", expanded=True):
            st.dataframe(df.head(), use_container_width=True)
            st.caption(f"Total rows: {len(df)} | Columns: {', '.join(df.columns)}")

        # Column Selection
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        if not text_cols:
            st.error("No text columns found in the uploaded file")
            st.stop()
        
        selected_col = st.selectbox(
            "Select text column for analysis",
            text_cols,
            help="Choose the column containing the text you want to analyze"
        )

        # Analysis Tabs
        tab1, tab2 = st.tabs(["Sentiment Analysis", "Word Cloud"])

        with tab1:
            st.subheader("Sentiment Distribution")
            try:
                with st.spinner("Analyzing sentiment patterns..."):
                    result = safe_api_call(
                        "/sentiment-pie",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue())}
                    )
                    
                    if result:
                        fig = go.Figure(go.Pie(
                            labels=result["labels"],
                            values=result["values"],
                            hole=0.3,
                            marker_colors=['#2ca02c', '#ff7f0e', '#d62728'],  # Green, Orange, Red
                            textinfo='percent+value'
                        ))
                        fig.update_layout(
                            legend_title="Sentiment",
                            margin=dict(t=0, b=0, l=0, r=0)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Display metrics
                        cols = st.columns(3)
                        cols[0].metric("Positive", result["values"][0])
                        cols[1].metric("Neutral", result["values"][1])
                        cols[2].metric("Negative", result["values"][2])
            except Exception as e:
                st.error(f"Sentiment analysis failed: {str(e)}")

        with tab2:
            st.subheader("Word Cloud Visualization")
            try:
                with st.spinner("Generating word cloud..."):
                    texts = df[selected_col].dropna().astype(str).tolist()
                    response = requests.post(
                        f"{BACKEND_URL}/wordcloud",
                        json={"texts": texts},
                        timeout=TIMEOUT
                    )
                    response.raise_for_status()
                    
                    img = Image.open(BytesIO(response.content))
                    st.image(
                        img,
                        caption=f"Word Cloud from '{selected_col}' column",
                        use_container_width=True
                    )
                    st.caption(f"Analyzed {len(texts)} text entries")
            except Exception as e:
                st.error(f"Word cloud generation failed: {str(e)}")

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.stop()

# Footer
st.markdown("---")
st.caption("Sentiment Analysis Dashboard v1.0 | Powered by FastAPI & Streamlit")