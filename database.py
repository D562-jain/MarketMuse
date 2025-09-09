from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# 1. Set up the connection to the SQLite database.
# This will create a file called 'news.db' in your project directory.
engine = create_engine('sqlite:///news.db', echo=True)
# 'echo=True' makes the database operations show in the terminal - great for learning!

# 2. Create a base class for our table definitions
Base = declarative_base()

# 3. Define what a "NewsArticle" looks like in our database
class NewsArticle(Base):
    __tablename__ = 'news_articles' # Name of the table in the database

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    url = Column(String, unique=True)  # 'unique=True' prevents storing the same article twice
    source = Column(String)
    published_at = Column(DateTime, default=datetime.utcnow)
    
    sentiment_label = Column(String)
    sentiment_score = Column(Integer)

    def __repr__(self):
        return f"<NewsArticle(title='{self.title}', source='{self.source}')>"

# 4. This line creates the table in the database.
Base.metadata.create_all(engine)

# 5. Create a "Session" class to interact with the database
Session = sessionmaker(bind=engine)
print("Database and 'news_articles' table created successfully!")