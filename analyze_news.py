from textblob import TextBlob
from database import Session, NewsArticle
import time

def get_sentiment(text):
    if text is None:
        return "NEUTRAL", 0.0
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        label = "POSITIVE"
    elif polarity < -0.1:
        label = "NEGATIVE"
    else:
        label = "NEUTRAL"
    confidence = abs(polarity)
    return label, confidence

print("Starting to analyze news articles in the database...")

# 1. Connect to the database
session = Session()

# 2. Find all articles that have not been analyzed yet (where sentiment_label is NULL)
articles_to_analyze = session.query(NewsArticle).filter(NewsArticle.sentiment_label == None).all()
# If you just recreated your DB, this list might be empty. Let's add a new article first.
if not articles_to_analyze:
    print("No unanalyzed articles found. Adding a test article...")
    # Add a test article to analyze
    test_article = NewsArticle(
        title="New AI stock plummets after poor earnings report",
        description="The company's value dropped 20% in after-hours trading.",
        url="https://example.com/test-article",
        source="Test Source"
    )
    session.add(test_article)
    session.commit()
    print("Added test article.")
    # Now query again to get the article we just added
    articles_to_analyze = session.query(NewsArticle).filter(NewsArticle.sentiment_label == None).all()

print(f"Found {len(articles_to_analyze)} article(s) to analyze.")

# 3. Analyze each article and update its database record
for article in articles_to_analyze:
    print(f"\nAnalyzing: {article.title}")
    # Use the article's title for sentiment analysis (you could also use description)
    label, score = get_sentiment(article.title)
    print(f"Result: {label} (score: {score:.2f})")

    # Update the article object with the results
    article.sentiment_label = label
    # Store confidence score as an integer between 0-100 for easier handling
    article.sentiment_score = int(score * 100)

    time.sleep(0.1)  # Tiny delay

# 4. Save all the changes to the database
session.commit()
session.close()

print("\nAnalysis complete! Results saved to the database.")