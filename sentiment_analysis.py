from textblob import TextBlob
from database import Session, NewsArticle
import time

print("TextBlob is ready for sentiment analysis!")

# 1. Create a function to analyze a headline and return the sentiment
def get_sentiment(text):
    if text is None:
        return "NEUTRAL", 0.0
    analysis = TextBlob(text)
    # TextBlob returns a polarity score between -1 (negative) and +1 (positive)
    polarity = analysis.sentiment.polarity

    # Convert the numeric score to a label
    if polarity > 0.1:
        label = "POSITIVE"
    elif polarity < -0.1:
        label = "NEGATIVE"
    else:
        label = "NEUTRAL"
    # We use the absolute value of the polarity as a simple "confidence" score
    confidence = abs(polarity)
    return label, confidence

# 2. Test the model on some sample headlines first
sample_headlines = [
    "Quantum computing breakthrough achieves new record!",
    "Company faces major losses in latest financial quarter.",
    "The weather will be nice tomorrow."
]

print("\nTesting model on sample headlines:")
for headline in sample_headlines:
    label, confidence = get_sentiment(headline)
    print(f"Headline: {headline}")
    print(f"Sentiment: {label} (Confidence: {confidence:.4f})\n")
    time.sleep(0.5)  # Small delay