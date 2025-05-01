from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from io import BytesIO
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import logging

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.post("/sentiment-pie")
async def sentiment_pie(file: UploadFile = File(...)):
    """
    Analyze sentiment in the provided file and return sentiment distribution.
    """
    try:
        # Read the uploaded file into a pandas DataFrame
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))  # Assuming CSV format

        # Example sentiment analysis logic (can be replaced with a real model)
        sentiment_data = {
            "labels": ["Positive", "Negative", "Neutral"],
            "values": [50, 30, 20]  # These would be dynamically calculated based on text analysis
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


@app.post("/geo-map")
async def geo_map(request: dict):
    """
    Generate a geo map from latitude and longitude data and return it as a map image.
    """
    try:
        latitude = request.get("latitude", [])
        longitude = request.get("longitude", [])

        if not latitude or not longitude:
            raise ValueError("Latitude or Longitude data is missing")

        # Example of basic geo map creation (real-world scenario may involve more logic)
        plt.figure(figsize=(10, 6))

        # Simulate plotting geo map
        plt.scatter(longitude, latitude, c=np.random.rand(len(latitude)), cmap='viridis', s=100)
        plt.title("Geo Map")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.colorbar()

        # Save the plot as a PNG image
        img_byte_arr = BytesIO()
        plt.savefig(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Return the geo map image as a streaming response
        return StreamingResponse(img_byte_arr, media_type="image/png")
    except Exception as e:
        logging.error(f"Error in /geo-map: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Error in generating geo map: {str(e)}"})


@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file and return some basic information about it.
    """
    try:
        # Read the uploaded file into a pandas DataFrame
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))  # Assuming CSV format

        # Example: return the first few rows of the CSV file
        return {"filename": file.filename, "data_preview": df.head().to_dict()}
    except Exception as e:
        logging.error(f"Error in /upload-file: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Error in file upload: {str(e)}"})

