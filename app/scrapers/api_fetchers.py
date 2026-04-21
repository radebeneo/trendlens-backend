import os
from newsapi import NewsApiClient
from googleapiclient.discovery import build
from datetime import datetime

class APIFetchers:
    """
    Fetchers for official APIs (NewsAPI, YouTube).
    """
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")

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

    def fetch_youtube_trends(self, region_code='US', max_results=10):
        """
        Fetches trending videos using YouTube Data API v3.
        """
        if not self.youtube_api_key:
            print("YOUTUBE_API_KEY not found in environment.")
            return None
        
        try:
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode=region_code,
                maxResults=max_results
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                videos.append({
                    "title": item['snippet']['title'],
                    "url": f"https://www.youtube.com/watch?v={item['id']}",
                    "view_count": item['statistics'].get('viewCount'),
                    "channel": item['snippet']['channelTitle'],
                    "source": "YouTube"
                })
            
            return {
                "source": "YouTube",
                "region": region_code,
                "scraped_at": datetime.utcnow().isoformat(),
                "data": videos
            }
        except Exception as e:
            print(f"Error fetching from YouTube: {e}")
            return None

if __name__ == "__main__":
    fetcher = APIFetchers()
    # Note: These will fail without API keys
    print("Testing API fetchers (will fail without keys)...")
    print(fetcher.fetch_trending_news())
