# api.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from io import BytesIO
import pandas as pd
from wordcloud import WordCloud
from textblob import TextBlob
import logging
import uvicorn

app = FastAPI(title="Sentiment Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Sentiment Analysis API")

@app.post("/sentiment-pie")
async def analyze_sentiment(file: UploadFile = File(...)):
    try:
        # Read file content
        content = await file.read()
        
        # Try both CSV and Excel formats
        try:
            df = pd.read_csv(BytesIO(content))
        except:
            df = pd.read_excel(BytesIO(content))
        
        # Sentiment analysis
        results = {"positive": 0, "neutral": 0, "negative": 0}
        text_cols = df.select_dtypes(include=['object']).columns
        
        for col in text_cols:
            for text in df[col].dropna().astype(str):
                polarity = TextBlob(text).sentiment.polarity
                if polarity > 0.1:
                    results["positive"] += 1
                elif polarity < -0.1:
                    results["negative"] += 1
                else:
                    results["neutral"] += 1
        
        return {"labels": list(results.keys()), "values": list(results.values())}
    
    except Exception as e:
        logging.error(f"Sentiment analysis failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/wordcloud")
async def generate_wordcloud(request: dict):
    try:
        texts = request.get("texts", [])
        if not texts:
            raise ValueError("No texts provided")
        
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(texts))
        
        img_bytes = BytesIO()
        wordcloud.to_image().save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        return StreamingResponse(img_bytes, media_type="image/png")
    
    except Exception as e:
        logging.error(f"Wordcloud generation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)