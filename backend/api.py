import pandas as pd
from textblob import TextBlob
import plotly.express as px
from flask import Flask, jsonify, request
import io

app = Flask(__name__)

# Load the dataset
def load_data(uploaded_file):
    try:
        # Read the CSV or Excel file into a dataframe
        if uploaded_file.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# Sentiment pie chart
@app.route('/sentiment-pie', methods=['POST'])
def sentiment_pie_chart():
    try:
        # Get the file from the request
        file = request.files['file']
        if file.filename.endswith('.csv') or file.filename.endswith('.xlsx'):
            # Load data into DataFrame
            data = load_data(file)
            
            # Combine all text columns into one series for sentiment analysis
            text_data = data.select_dtypes(include=['object']).fillna('')
            text_column = text_data.apply(lambda row: ' '.join(row), axis=1)

            sentiment_counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0}

            # Sentiment analysis
            for text in text_column:
                blob = TextBlob(str(text))
                sentiment = blob.sentiment.polarity
                if sentiment > 0:
                    sentiment_counts['Positive'] += 1
                elif sentiment < 0:
                    sentiment_counts['Negative'] += 1
                else:
                    sentiment_counts['Neutral'] += 1

            labels = list(sentiment_counts.keys())
            values = list(sentiment_counts.values())

            # Generate pie chart
            fig = px.pie(names=labels, values=values, title="Sentiment Distribution")
            # Convert chart to JSON response
            chart_data = fig.to_dict()

            return jsonify(chart_data)

        else:
            return jsonify({"error": "Invalid file format. Only CSV and Excel files are supported."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
