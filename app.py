import streamlit as st
import os
import pandas as pd
from datetime import datetime
from backend.api import load_data, sentiment_pie_chart, generate_wordcloud, generate_geo_map

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="CSV Analyzer App", layout="wide")

st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Choose the view:", ["User Upload", "Admin Dashboard"])

# ---------------------- USER UPLOAD PAGE ----------------------
if app_mode == "User Upload":
    st.title("📊 Upload CSV/Excel for Analysis")
    
    # Accept both CSV and Excel files
    uploaded_file = st.file_uploader("Upload CSV/Excel File", type=["csv", "xlsx", "xls"])

    if uploaded_file:
        # Save file to disk with a timestamp to avoid overwriting
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded and saved as {filename}")

        # Load and process data based on file type
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(file_path)
        else:
            data = pd.read_excel(file_path)

        if data is not None:
            st.subheader("Data Preview")
            st.write(data.head())

            # Choose column for text analysis
            text_column = st.selectbox("Select a column for sentiment/word cloud:", options=data.columns)

            if text_column:
                st.subheader("Sentiment Pie Chart")
                fig = sentiment_pie_chart(data[text_column])
                st.plotly_chart(fig)

                st.subheader("Word Cloud")
                wc_plt = generate_wordcloud(data[text_column])
                st.pyplot(wc_plt)

                # Optional geo map (if lat/lon present)
                if 'latitude' in data.columns and 'longitude' in data.columns:
                    st.subheader("Geo Map")
                    geo_map = generate_geo_map(data['latitude'], data['longitude'])
                    st.write(geo_map)
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
            
            # Load and process data based on file type
            if selected_file.endswith(".csv"):
                data = pd.read_csv(full_path)
            else:
                data = pd.read_excel(full_path)

            if data is not None:
                st.subheader(f"Preview of: {selected_file}")
                st.write(data.head())
            else:
                st.error("Could not load this file.")
    else:
        st.info("No uploaded files found.")
