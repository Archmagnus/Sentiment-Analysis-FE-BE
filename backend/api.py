from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from io import BytesIO
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
from typing import List

app = FastAPI()

# Define Pydantic model for WordCloud request
class WordCloudRequest(BaseModel):
    texts: List[str]

@app.post("/sentiment-pie")
async def sentiment_pie(file: UploadFile = File(...)):
    # Simulate sentiment analysis (replace this with your actual model)
    try:
        # Simulate response data
        sentiment_data = {
            "labels": ["Positive", "Negative", "Neutral"],
            "values": [50, 30, 20]
        }
        return sentiment_data
    except Exception as e:
        return {"error": f"Error in generating sentiment pie chart: {str(e)}"}

@app.post("/wordcloud")
async def wordcloud(request: WordCloudRequest):
    try:
        # Generate word cloud from text data
        text = " ".join(request.texts)
        wordcloud = WordCloud(width=800, height=400).generate(text)

        # Save image to BytesIO and return it
        img_byte_arr = BytesIO()
        wordcloud.to_image().save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        return StreamingResponse(img_byte_arr, media_type="image/png")
    except Exception as e:
        return {"error": f"Error in generating word cloud: {str(e)}"}

@app.post("/geo-map")
async def geo_map(latitude: List[float], longitude: List[float]):
    try:
        fig = px.scatter_geo(lat=latitude, lon=longitude)
        # Save the map to a file (could be in other formats too, depending on needs)
        geo_map_path = "/path/to/save/geo_map.html"
        fig.write_html(geo_map_path)

        return {"message": "Geo Map generated successfully", "path": geo_map_path}
    except Exception as e:
        return {"error": f"Error in generating geo map: {str(e)}"}
