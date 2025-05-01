from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from io import BytesIO
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from textblob import TextBlob  # For sentiment analysis
import logging

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.post("/sentiment-pie")
async def sentiment_pie(file: UploadFile = File(...)):
    """
    Analyze sentiment in the provided file and return sentiment distribution (positive, neutral, negative).
    """
    try:
        # Read the uploaded file into a pandas DataFrame
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))  # Assuming CSV format

        # Extract text columns (columns with 'object' dtype)
        text_columns = df.select_dtypes(include=['object']).columns.tolist()

        if not text_columns:
            raise ValueError("No text columns found in the file")

        # Simple sentiment analysis using TextBlob
        sentiments = {"positive": 0, "neutral": 0, "negative": 0}

        # Process each text column and analyze sentiment
        for col in text_columns:
            for text in df[col].dropna():
                sentiment = TextBlob(str(text)).sentiment.polarity
                if sentiment > 0:
                    sentiments["positive"] += 1
                elif sentiment < 0:
                    sentiments["negative"] += 1
                else:
                    sentiments["neutral"] += 1

        # Prepare the sentiment data for the pie chart
        sentiment_data = {
            "labels": list(sentiments.keys()),
            "values": list(sentiments.values())
        }

        return sentiment_data
    except Exception as e:
        logging.error(f"Error in /sentiment-pie: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Error in generating sentiment pie chart: {str(e)}"})


@app.post("/wordcloud")
async def wordcloud(request: dict):
    """
    Generate a word cloud from the provided text data and return it as an image.
    """
    try:
        texts = request.get("texts", [])
        
        if not texts:
            raise ValueError("No text data provided for word cloud")

        # Generate word cloud
        text = " ".join(texts)
        wordcloud = WordCloud(width=800, height=400).generate(text)

        # Save word cloud image to a BytesIO object
        img_byte_arr = BytesIO()
        wordcloud.to_image().save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        # Return the word cloud image as a streaming response
        return StreamingResponse(img_byte_arr, media_type="image/png")
    except Exception as e:
        logging.error(f"Error in /wordcloud: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Error in generating word cloud: {str(e)}"})
