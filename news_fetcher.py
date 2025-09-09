# news_fetcher.py (Updated to accept dynamic queries)
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from database import Session, NewsArticle
import sys  # To accept command line arguments

load_dotenv()
api_key = os.getenv('NEWS_API_KEY')

def fetch_news_for_query(search_query):
    """Fetches news for a given search query and stores it in the database."""
    yesterday = datetime.now() - timedelta(days=1)
    date_string = yesterday.strftime('%Y-%m-%d')

    url = "https://newsapi.org/v2/everything"
    params = {
        'q': search_query,
        'from': date_string,
        'sortBy': 'popularity',
        'apiKey': api_key,
        'pageSize': 15  # Get more articles
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        session = Session()

        new_article_count = 0
        for article in data['articles']:
            exists = session.query(NewsArticle).filter_by(url=article['url']).first()
            if not exists:
                new_article = NewsArticle(
                    title=article['title'],
                    description=article['description'],
                    url=article['url'],
                    source=article['source']['name'],
                    published_at=datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                )
                session.add(new_article)
                new_article_count += 1

        session.commit()
        session.close()
        print(f"Success! Added {new_article_count} new articles for '{search_query}' to the database.")
        return new_article_count
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return 0

if __name__ == "__main__":
    # Get search query from command line argument or use default
    query = sys.argv[1] if len(sys.argv) > 1 else "Artificial Intelligence"
    fetch_news_for_query(query)