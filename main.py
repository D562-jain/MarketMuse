from fastapi.responses import HTMLResponse 
from fastapi.staticfiles import StaticFiles
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Session, NewsArticle
from pydantic import BaseModel
from typing import List
import subprocess
import threading

# 1. Create a FastAPI application instance
app = FastAPI(title="MarketMuse API", description="API for AI-powered news analysis", version="1.0")

# 2. Add CORS middleware to allow frontend to talk to backend
# (We'll need this later for our React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],  # Specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# 3. Define a Pydantic model for the response
# This ensures the data we send is structured correctly
class ArticleResponse(BaseModel):
    id: int
    title: str
    source: str
    sentiment_label: str
    sentiment_score: int

    class Config:
        from_attributes = True  # Allows ORM mode

# 4. Define our API endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to the MarketMuse API! Go to /docs to see the documentation."}

@app.get("/articles", response_model=List[ArticleResponse])
async def get_articles():
    """Get all analyzed news articles from the database."""
    session = Session()
    articles = session.query(NewsArticle).filter(NewsArticle.sentiment_label != None).all()
    session.close()
    
    # Convert each SQLAlchemy ORM object to a dictionary
    # containing only the fields defined in ArticleResponse
    result = []
    for article in articles:
        result.append({
            "id": article.id,
            "title": article.title,
            "source": article.source,
            "sentiment_label": article.sentiment_label,
            "sentiment_score": article.sentiment_score
        })
    
    return result

@app.get("/stats")
async def get_stats():
    """Get basic statistics about the analyzed news."""
    session = Session()
    # Count articles by sentiment
    positive_count = session.query(NewsArticle).filter(NewsArticle.sentiment_label == "POSITIVE").count()
    negative_count = session.query(NewsArticle).filter(NewsArticle.sentiment_label == "NEGATIVE").count()
    neutral_count = session.query(NewsArticle).filter(NewsArticle.sentiment_label == "NEUTRAL").count()
    session.close()

    return {
        "total_analyzed_articles": positive_count + negative_count + neutral_count,
        "positive_articles": positive_count,
        "negative_articles": negative_count,
        "neutral_articles": neutral_count
    }
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard page."""
    # Simple way to read the HTML file and return its content
    with open(os.path.join("templates", "index.html"), "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
@app.post("/analyze/{topic}")
async def analyze_topic(topic: str):
    """Trigger news analysis for a specific topic."""
    
    def run_analysis():
        """Helper function to run the analysis in the background."""
        try:
            print(f"Starting analysis for topic: {topic}")
            # Step 1: Fetch news for the topic
            subprocess.run(["python", "news_fetcher.py", topic], check=True)
            # Step 2: Analyze the new articles
            subprocess.run(["python", "analyze_news.py"], check=True)
            print(f"Completed analysis for topic: {topic}")
        except subprocess.CalledProcessError as e:
            print(f"Error during analysis: {e}")
    
    # Run the analysis in a background thread so the API doesn't block
    thread = threading.Thread(target=run_analysis)
    thread.start()
    
    return {"message": f"Started analysis for topic: '{topic}'. This may take a minute."}