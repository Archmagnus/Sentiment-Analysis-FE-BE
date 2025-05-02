from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from io import BytesIO
import pandas as pd
from textblob import TextBlob
import logging
import uvicorn
import time
import os

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Sentiment Analysis API",
    description="API for analyzing text sentiment",
    version="1.0.0",
    openapi_tags=[{
        'name': 'analysis',
        'description': 'Text analysis endpoints'
    }]
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8501",
    "https://your-production-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Directory to store uploaded files
UPLOAD_DIR = "uploads"

# Ensure upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.on_event("startup")
async def startup_event():
    """Initialize resources when the app starts"""
    logger.info("Starting Sentiment Analysis API")

@app.post("/sentiment-pie", tags=["analysis"])
async def analyze_sentiment(file: UploadFile = File(...)):
    """
    Analyze sentiment distribution in uploaded file.

    Returns:
        {
            "labels": ["positive", "neutral", "negative"],
            "values": [counts]
        }
    """
    start_time = time.time()

    try:
        # Validate file type
        if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
            raise ValueError("Only CSV and Excel files are supported")

        # Save the uploaded file to the server
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Read file content
        with open(file_path, "rb") as f:
            content = f.read()

        # Load data
        try:
            if file.filename.lower().endswith('.csv'):
                df = pd.read_csv(BytesIO(content))
            else:
                df = pd.read_excel(BytesIO(content))
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")

        if df.empty:
            raise ValueError("Uploaded file is empty")

        # Get text columns
        text_cols = df.select_dtypes(include=['object']).columns
        if len(text_cols) == 0:
            raise ValueError("No text columns found in the file")

        # Sentiment analysis
        results = {"positive": 0, "neutral": 0, "negative": 0}
        for col in text_cols:
            texts = df[col].dropna().astype(str).str.strip()
            texts = texts[texts != ""]
            for text in texts:
                try:
                    polarity = TextBlob(text).sentiment.polarity
                    if polarity > 0.1:
                        results["positive"] += 1
                    elif polarity < -0.1:
                        results["negative"] += 1
                    else:
                        results["neutral"] += 1
                except Exception as e:
                    logger.warning(f"Error analyzing text: {text[:50]}... Error: {str(e)}")
                    continue

        logger.info(f"Analysis completed in {time.time() - start_time:.2f}s")
        return {
            "labels": list(results.keys()),
            "values": list(results.values()),
            "total_texts": sum(results.values())
        }

    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@app.get("/uploaded-files", tags=["analysis"])
async def list_uploaded_files():
    """
    List previously uploaded files in the server's 'uploads' directory.
    
    Returns:
        {
            "files": ["file1.csv", "file2.xlsx", ...]
        }
    """
    try:
        # List all files in the upload directory
        files = os.listdir(UPLOAD_DIR)
        return {"files": files}
    
    except Exception as e:
        logger.error(f"Error fetching uploaded files: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error retrieving uploaded files"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=2,
        access_log=True
    )
