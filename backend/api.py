from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from textblob import TextBlob
import logging
import uvicorn

app = FastAPI()

# Configure CORS to allow requests from Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.post("/sentiment-pie")
async def sentiment_pie(file: UploadFile = File(...)):
    """
    Analyze sentiment in the provided file and return sentiment distribution.
    """
    try:
        # Read the uploaded file
        contents = await file.read()
        try:
            df = pd.read_csv(BytesIO(contents))  # Try CSV first
        except:
            df = pd.read_excel(BytesIO(contents))  # Fallback to Excel

        # Extract text columns
        text_columns = df.select_dtypes(include=['object']).columns.tolist()
        if not text_columns:
            raise ValueError("No text columns found in the file")

        # Sentiment analysis
        sentiments = {"positive": 0, "neutral": 0, "negative": 0}
        for col in text_columns:
            for text in df[col].dropna():
                sentiment = TextBlob(str(text)).sentiment.polarity
                if sentiment > 0.1:
                    sentiments["positive"] += 1
                elif sentiment < -0.1:
                    sentiments["negative"] += 1
                else:
                    sentiments["neutral"] += 1

        return {
            "labels": list(sentiments.keys()),
            "values": list(sentiments.values())
        }
    except Exception as e:
        logging.error(f"Error in sentiment_pie: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/wordcloud")
async def wordcloud(request: dict):
    """
    Generate a word cloud from the provided text data.
    """
    try:
        texts = request.get("texts", [])
        if not texts:
            raise ValueError("No text data provided")
        
        text = " ".join(str(t) for t in texts)
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        
        img_byte_arr = BytesIO()
        wordcloud.to_image().save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        
        return StreamingResponse(img_byte_arr, media_type="image/png")
    except Exception as e:
        logging.error(f"Error in wordcloud: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)