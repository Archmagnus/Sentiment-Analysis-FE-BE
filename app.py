import streamlit as st
import os
import pandas as pd
from datetime import datetime
import requests
from io import BytesIO
import plotly.graph_objects as go
from PIL import Image

UPLOAD_DIR = "uploaded_files"
BACKEND_URL = "https://your-backend-url.com"  # Replace with your actual backend URL
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="CSV Analyzer App", layout="wide")

st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Choose the view:", ["User Upload", "Admin Dashboard"])

# ---------------------- USER UPLOAD PAGE ----------------------
if app_mode == "User Upload":
    st.title("📊 Upload CSV/Excel for Analysis")

    uploaded_file = st.file_uploader("Upload CSV/Excel File", type=["csv", "xlsx", "xls"])

    if uploaded_file:
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded and saved as {filename}")

        # Load file into dataframe
        if filename.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        st.subheader("Data Preview")
        st.write(df.head())

        # Text columns selection
        text_columns = df.select_dtypes(include=['object']).columns.tolist()
        text_column = st.selectbox("Select a column for sentiment/word cloud:", options=text_columns)

        if text_column:
            # -------- Sentiment Pie Chart API --------
            st.subheader("Sentiment Pie Chart")
            response = requests.post(f"{BACKEND_URL}/sentiment-pie", files={"file": uploaded_file})

            if response.status_code == 200:
                try:
                    pie_data = response.json()
                    if "labels" in pie_data and "values" in pie_data:
                        fig = go.Figure(data=[go.Pie(labels=pie_data["labels"], values=pie_data["values"])]))
                        st.plotly_chart(fig)
                    else:
                        st.error("Invalid JSON structure received for the pie chart.")
                except ValueError:
                    st.error("Received invalid JSON response from the backend.")
            else:
                st.error(f"Failed to generate sentiment chart. Status Code: {response.status_code}")

            # -------- Word Cloud API --------
            st.subheader("Word Cloud")
            response = requests.post(f"{BACKEND_URL}/wordcloud", json={"texts": df[text_column].dropna().tolist()})
            if response.status_code == 200:
                try:
                    image_bytes = BytesIO(response.content)
                    image = Image.open(image_bytes)
                    st.image(image)
                except Exception as e:
                    st.error(f"Failed to generate word cloud: {e}")
            else:
                st.error(f"Failed to generate word cloud. Status Code: {response.status_code}")

            # -------- Geo Map if latitude and longitude exist --------
            if "latitude" in df.columns and "longitude" in df.columns:
                st.subheader("Geo Map")
                response = requests.post(f"{BACKEND_URL}/geo-map", json={
                    "latitude": df["latitude"].dropna().tolist(),
                    "longitude": df["longitude"].dropna().tolist()
                })
                if response.status_code == 200:
                    geo_data = response.json()
                    fig = go.Figure(data=go.Scattergeo(
                        lon=geo_data["longitude"],
                        lat=geo_data["latitude"],
                        mode='markers',
                        marker=dict(size=6)
                    ))
                    fig.update_layout(geo=dict(scope="world"))
                    st.plotly_chart(fig)
                else:
                    st.warning("Failed to generate geo map.")
            else:
                st.info("No latitude/longitude columns found.")

# ---------------------- ADMIN DASHBOARD ----------------------
elif app_mode == "Admin Dashboard":
    st.title("🛠️ Admin Dashboard – View Uploaded Files")

    file_list = sorted(os.listdir(UPLOAD_DIR), reverse=True)

    if file_list:
        selected_file = st.selectbox("Select a previously uploaded file", file_list)

        if selected_file:
            full_path = os.path.join(UPLOAD_DIR, selected_file)

            if selected_file.endswith(".csv"):
                df = pd.read_csv(full_path)
            else:
                df = pd.read_excel(full_path)

            st.subheader(f"Preview of: {selected_file}")
            st.write(df.head())
    else:
        st.info("No uploaded files found.")
