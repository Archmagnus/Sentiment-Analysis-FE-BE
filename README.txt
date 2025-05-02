Sentiment Analysis Dashboard with File Upload and History
==========================================================

📊 Overview
-----------
This is a full-stack web application for performing sentiment analysis on uploaded CSV/Excel files.
Users can upload a dataset, select a text column, visualize sentiment distribution (positive, neutral, negative),
and also view a history of previously uploaded files.

🔗 GitHub Repository
--------------------
https://github.com/Archmagnus/Sentiment-Analysis-FE-BE

🚀 Tech Stack
-------------
- Backend API      : FastAPI
- Frontend UI      : Streamlit
- Sentiment Engine : TextBlob
- File Processing  : Pandas
- Deployment       : Render / Localhost

🔧 Features
----------
- ✅ Upload .csv, .xlsx, or .xls files
- ✅ Auto-detect text columns for sentiment analysis
- ✅ Visualize sentiment as a pie chart
- ✅ See list of previously uploaded files
- ✅ Logging and error handling

🛠️ How to Run Locally
----------------------
1. Clone the Repository
   ---------------------
   git clone https://github.com/Archmagnus/Sentiment-Analysis-FE-BE.git
   cd Sentiment-Analysis-FE-BE

2. Create and Activate a Virtual Environment
   ------------------------------------------
   python -m venv venv
   source venv/bin/activate        # On Windows: venv\Scripts\activate
   pip install -r requirements.txt

3. Run the Backend (FastAPI)
   --------------------------
   cd backend
   uvicorn api:app --host 0.0.0.0 --port 8000 --reload

4. Run the Frontend (Streamlit)
   -----------------------------
   cd ..
   streamlit run app.py

📂 Folder Structure
-------------------
Sentiment-Analysis-FE-BE/
│
├── backend/
│   ├── api.py            -> FastAPI backend
│   └── uploads/          -> Stores uploaded files
│
├── app.py                -> Streamlit frontend
├── requirements.txt
└── README.txt

🌐 API Endpoints
----------------
Method | Endpoint           | Description
-------|--------------------|-------------------------------
POST   | /sentiment-pie     | Upload file & return sentiment stats
GET    | /uploaded-files    | List all uploaded files
GET    | /health            | Backend health check

📌 Notes
--------
- Only CSV and Excel files are supported (.csv, .xlsx, .xls)
- Uploaded files must contain at least one text column
- Files are saved to backend/uploads/

👨‍💻 Author
-----------
Built by Archit Xavier
