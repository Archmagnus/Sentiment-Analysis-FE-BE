# backend/api.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

app = FastAPI()

# Enable CORS for frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/sentiment-pie")
async def sentiment_pie(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    df['Sentiment'] = df.iloc[:, 0].apply(lambda text: TextBlob(str(text)).sentiment.polarity)
    df['Sentiment Label'] = df['Sentiment'].apply(lambda p: 'positive' if p > 0 else 'negative' if p < 0 else 'neutral')
    sentiment_counts = df['Sentiment Label'].value_counts().to_dict()
    return JSONResponse(content=sentiment_counts)

@app.post("/generate-wordcloud")
async def generate_wordcloud(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    text = ' '.join(df.iloc[:, 0].astype(str).tolist())
    wc = WordCloud(width=800, height=400, background_color='white').generate(text)
    img = BytesIO()
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(img, format='PNG', bbox_inches='tight')
    img.seek(0)
    return StreamingResponse(img, media_type="image/png")
