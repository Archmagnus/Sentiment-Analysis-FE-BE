# api.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from io import BytesIO
import pandas as pd
from wordcloud import WordCloud
from textblob import TextBlob
import logging
import uvicorn
from typing import Dict, List
import numpy as np
from PIL import Image
import time

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Sentiment Analysis API",
    description="API for analyzing text sentiment and generating word clouds",
    version="1.0.0",
    openapi_tags=[{
        'name': 'analysis',
        'description': 'Text analysis endpoints'
    }]
)

# Configure CORS (more secure in production)
origins = [
    "http://localhost",
    "http://localhost:8501",  # Streamlit default port
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

@app.on_event("startup")
async def startup_event():
    """Initialize resources when the app starts"""
    logger.info("Starting Sentiment Analysis API")
    # Add any initialization code here

@app.post("/sentiment-pie", tags=["analysis"])
async def analyze_sentiment(file: UploadFile = File(...)):
    """
    Analyze sentiment distribution in uploaded file.
    
    Supports CSV and Excel files with text columns.
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

        # Read file content
        content = await file.read()
        
        # Process file based on type
        try:
            if file.filename.lower().endswith('.csv'):
                df = pd.read_csv(BytesIO(content))
            else:
                df = pd.read_excel(BytesIO(content))
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")

        # Validate dataframe
        if df.empty:
            raise ValueError("Uploaded file is empty")

        # Get text columns
        text_cols = df.select_dtypes(include=['object']).columns
        if len(text_cols) == 0:
            raise ValueError("No text columns found in the file")

        # Sentiment analysis
        results = {"positive": 0, "neutral": 0, "negative": 0}
        
        for col in text_cols:
            # Clean text data
            texts = df[col].dropna().astype(str).str.strip()
            texts = texts[texts != ""]  # Remove empty strings
            
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

        logger.info(f"Analysis completed in {time.time()-start_time:.2f}s")
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

@app.post("/wordcloud", tags=["analysis"])
async def generate_wordcloud(request: Request):
    """
    Generate word cloud from provided texts.
    
    Expects JSON with format:
    {
        "texts": ["array", "of", "texts"]
    }
    Returns PNG image.
    """
    try:
        data = await request.json()
        texts = data.get("texts", [])
        
        if not texts:
            raise ValueError("No texts provided")
        
        if not isinstance(texts, list):
            raise ValueError("Texts should be an array")
            
        # Clean texts
        texts = [str(t).strip() for t in texts if str(t).strip()]
        
        if not texts:
            raise ValueError("No valid texts provided after cleaning")

        # Generate word cloud with improved parameters
        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            max_words=200,
            colormap='viridis',
            stopwords=None,
            contour_width=1,
            contour_color='steelblue'
        ).generate(" ".join(texts))

        # Convert to image
        img_bytes = BytesIO()
        wordcloud.to_image().save(img_bytes, format="PNG", quality=95)
        img_bytes.seek(0)
        
        return StreamingResponse(
            img_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": "attachment; filename=wordcloud.png",
                "X-WordCloud-Words": str(len(set(" ".join(texts).split())))
            }
        )
        
    except Exception as e:
        logger.error(f"Wordcloud generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    """Endpoint for health checks"""
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