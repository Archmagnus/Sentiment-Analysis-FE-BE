import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from PIL import Image
from io import BytesIO

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Sentiment Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# === BACKEND URL ===
BACKEND_URL = "https://sentiment-backend-0nno.onrender.com"

# === Custom CSS ===
st.markdown("""
    <style>
    .stAlert { border-left: 4px solid #ff4b4b; }
    .stSpinner > div { justify-content: center; }
    .stProgress > div > div > div { background-color: #1f77b4; }
    </style>
""", unsafe_allow_html=True)

# === Sidebar: backend health check ===
with st.sidebar:
    st.title("Connection Status")
    try:
        health = requests.get(f"{BACKEND_URL}/health")
        if health.status_code == 200:
            st.success("🟢 Connected to backend")
        else:
            st.warning("🟠 Backend unreachable")
    except:
        st.error("🔴 Cannot reach backend")

# === Main Title ===
st.title("📊 Sentiment Analysis Dashboard")
st.markdown("Upload a CSV or Excel file containing text data for analysis")

# === File Upload ===
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "xlsx"],
    accept_multiple_files=False,
    help="Supported formats: CSV, Excel (xlsx, xls)"
)

if uploaded_file:
    try:
        with st.spinner("Reading your file..."):
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

        # === Tabs ===
        tab1, tab2 = st.tabs(["Sentiment Analysis", "Uploaded Files History"])

        with tab1:
            st.subheader("Sentiment Distribution")
            try:
                with st.spinner("Sending data to backend..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    response = requests.post(f"{BACKEND_URL}/sentiment-pie", files=files)

                if response.status_code == 200:
                    data = response.json()
                    fig = go.Figure(go.Pie(
                        labels=data["labels"],
                        values=data["values"],
                        hole=0.3,
                        marker_colors=['#2ca02c', '#1f77b4', '#d62728'],
                        textinfo='percent+value'
                    ))
                    fig.update_layout(
                        legend_title="Sentiment",
                        margin=dict(t=0, b=0, l=0, r=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Metrics
                    for label, value in zip(data["labels"], data["values"]):
                        st.metric(label.capitalize(), value)
                else:
                    st.error(f"Sentiment analysis failed: {response.text}")

            except Exception as e:
                st.error(f"Request error: {str(e)}")

        with tab2:
            st.subheader("📁 Previously Uploaded Files")
            try:
                with st.spinner("Fetching file history from backend..."):
                    res = requests.get(f"{BACKEND_URL}/uploaded-files")

                if res.status_code == 200:
                    file_data = res.json()
                    files = file_data.get("files", [])
                    if files:
                        for f in files:
                            st.markdown(f"- {f}")
                    else:
                        st.info("No uploaded files found on the server.")
                else:
                    st.error(f"Failed to fetch uploaded files: {res.text}")

            except Exception as e:
                st.error(f"Error retrieving uploaded files: {str(e)}")

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.stop()

# === Footer ===
st.markdown("---")
st.caption("Sentiment Analysis Dashboard v1.0 | Powered by FastAPI + Streamlit")
