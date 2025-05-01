import streamlit as st
import os
import pandas as pd
from datetime import datetime
import requests
from io import BytesIO
import plotly.graph_objects as go
from PIL import Image

UPLOAD_DIR = "uploaded_files"
# Use environment variable for backend URL with localhost as fallback
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="CSV Analyzer App", layout="wide")

# Custom CSS to improve error visibility
st.markdown("""
    <style>
    .stAlert {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Choose the view:", ["User Upload", "Admin Dashboard"])

def check_backend_connection():
    """Check if backend is available"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=3)
        return response.status_code == 200
    except:
        return False

# ---------------------- USER UPLOAD PAGE ----------------------
if app_mode == "User Upload":
    st.title("📊 Upload CSV/Excel for Analysis")

    # Backend connection check
    if not check_backend_connection():
        st.error("⚠️ Backend service is not available. Please ensure the backend server is running.")
        if st.button("Retry Connection"):
            st.experimental_rerun()

    uploaded_file = st.file_uploader("Upload CSV/Excel File", type=["csv", "xlsx", "xls"])

    if uploaded_file:
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded and saved as {filename}")

        # Load file into dataframe
        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.stop()

        st.subheader("Data Preview")
        st.write(df.head())

        # Extract text columns
        text_columns = df.select_dtypes(include=['object']).columns.tolist()
        if not text_columns:
            st.error("No text columns found in the uploaded file")
            st.stop()

        text_column = st.selectbox("Select a column for sentiment/word cloud:", options=text_columns)

        if text_column:
            # Sentiment Pie Chart
            st.subheader("Sentiment Pie Chart")
            try:
                with st.spinner("Analyzing sentiment..."):
                    response = requests.post(
                        f"{BACKEND_URL}/sentiment-pie",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue())},
                        timeout=10
                    )
                    response.raise_for_status()
                    pie_data = response.json()
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=pie_data["labels"],
                        values=pie_data["values"],
                        hole=0.3
                    )])
                    st.plotly_chart(fig)
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to generate sentiment chart: {str(e)}")

            # Word Cloud
            st.subheader("Word Cloud")
            try:
                with st.spinner("Generating word cloud..."):
                    response = requests.post(
                        f"{BACKEND_URL}/wordcloud",
                        json={"texts": df[text_column].dropna().astype(str).tolist()},
                        timeout=10
                    )
                    response.raise_for_status()
                    image = Image.open(BytesIO(response.content))
                    st.image(image, caption="Generated Word Cloud", use_column_width=True)
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to generate word cloud: {str(e)}")

# ---------------------- ADMIN DASHBOARD ----------------------
elif app_mode == "Admin Dashboard":
    st.title("🛠️ Admin Dashboard – View Uploaded Files")

    file_list = sorted(os.listdir(UPLOAD_DIR), reverse=True)

    if file_list:
        selected_file = st.selectbox("Select a previously uploaded file", file_list)

        if selected_file:
            full_path = os.path.join(UPLOAD_DIR, selected_file)

            try:
                if selected_file.endswith(".csv"):
                    df = pd.read_csv(full_path)
                else:
                    df = pd.read_excel(full_path)

                st.subheader(f"Preview of: {selected_file}")
                st.write(df.head())
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    else:
        st.info("No uploaded files found.")