# frontend/app.py
import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# 🟢 Update this with actual backend URL
BACKEND_URL = "http://localhost:8000"  # change if hosted e.g., "https://your-backend.onrender.com"

st.title("📊 Sentiment Analysis Dashboard")

uploaded_file = st.file_uploader("Upload a CSV with text data", type=["csv"])

if uploaded_file is not None:
    # -------- Sentiment Pie Chart --------
    st.subheader("Sentiment Pie Chart")
    try:
        response = requests.post(f"{BACKEND_URL}/sentiment-pie", files={"file": uploaded_file.getvalue()})
        if response.status_code == 200:
            data = response.json()
            st.write(data)
            st.bar_chart(data)
        else:
            st.error("Failed to get sentiment data.")
    except Exception as e:
        st.error(f"Connection error: {e}")

    uploaded_file.seek(0)  # Reset for reuse

    # -------- Word Cloud --------
    st.subheader("Word Cloud")
    try:
        response = requests.post(f"{BACKEND_URL}/generate-wordcloud", files={"file": uploaded_file.getvalue()})
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            st.image(image, caption='Word Cloud', use_column_width=True)
        else:
            st.error("Failed to generate word cloud.")
    except Exception as e:
        st.error(f"Connection error: {e}")
