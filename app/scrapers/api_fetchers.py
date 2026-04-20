import os
from newsapi import NewsApiClient
import praw
from datetime import datetime

class APIFetchers:
    """
    Fetchers for official APIs (NewsAPI, Reddit).
    """
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        self.reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.reddit_user_agent = os.getenv("REDDIT_USER_AGENT", "TrendLens/0.1")

    def fetch_trending_news(self, category='technology'):
        """
        Fetches trending news using NewsAPI.
        """
        if not self.news_api_key:
            print("NEWS_API_KEY not found in environment.")
            return None
        
        try:
            newsapi = NewsApiClient(api_key=self.news_api_key)
            top_headlines = newsapi.get_top_headlines(category=category, language='en', country='us')
            
            articles = []
            for art in top_headlines.get('articles', []):
                articles.append({
                    "title": art['title'],
                    "url": art['url'],
                    "source": art['source']['name'],
                    "description": art['description']
                })
            
            return {
                "source": "NewsAPI",
                "category": category,
                "scraped_at": datetime.utcnow().isoformat(),
                "data": articles[:10]
            }
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return None

    def fetch_reddit_trends(self, subreddit='popular'):
        """
        Fetches trending posts from a subreddit using PRAW.
        """
        if not self.reddit_client_id or not self.reddit_client_secret:
            print("Reddit API credentials not found in environment.")
            return None
        
        try:
            reddit = praw.Reddit(
                client_id=self.reddit_client_id,
                client_secret=self.reddit_client_secret,
                user_agent=self.reddit_user_agent
            )
            
            posts = []
            for submission in reddit.subreddit(subreddit).hot(limit=10):
                posts.append({
                    "title": submission.title,
                    "url": submission.url,
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "source": f"reddit/r/{subreddit}"
                })
            
            return {
                "source": "Reddit",
                "subreddit": subreddit,
                "scraped_at": datetime.utcnow().isoformat(),
                "data": posts
            }
        except Exception as e:
            print(f"Error fetching from Reddit: {e}")
            return None

if __name__ == "__main__":
    fetcher = APIFetchers()
    # Note: These will fail without API keys
    print("Testing API fetchers (will fail without keys)...")
    print(fetcher.fetch_trending_news())
