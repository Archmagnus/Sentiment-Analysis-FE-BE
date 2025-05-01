import pandas as pd
from textblob import TextBlob
import geopandas as gpd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import folium
from io import StringIO

# Load the dataset
def load_data(uploaded_file):
    try:
        # Read the CSV file
        data = pd.read_csv(uploaded_file)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# Sentiment pie chart
def sentiment_pie_chart(text_column):
    sentiment_counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    
    for text in text_column:
        try:
            blob = TextBlob(str(text))
            sentiment = blob.sentiment.polarity
            if sentiment > 0:
                sentiment_counts['Positive'] += 1
            elif sentiment < 0:
                sentiment_counts['Negative'] += 1
            else:
                sentiment_counts['Neutral'] += 1
        except Exception as e:
            print(f"Error processing sentiment: {e}")
    
    labels = sentiment_counts.keys()
    values = sentiment_counts.values()

    # Create pie chart
    fig = px.pie(names=labels, values=values, title="Sentiment Distribution")
    return fig

# Generate Word Cloud
def generate_wordcloud(text_column):
    text = " ".join(str(text) for text in text_column)
    wordcloud = WordCloud(width=800, height=400).generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    return plt

# Generate GeoMap (dummy, requires specific location data)
def generate_geo_map(lat_column, lon_column):
    # This will generate a basic map, for advanced use, you can update this function
    m = folium.Map(location=[lat_column.mean(), lon_column.mean()], zoom_start=6)
    for lat, lon in zip(lat_column, lon_column):
        folium.CircleMarker(location=[lat, lon], radius=5).add_to(m)
    return m
