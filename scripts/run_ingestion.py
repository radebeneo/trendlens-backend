import requests
import os
import json
from app.scrapers.news_scraper import NewsScraper
from app.scrapers.api_fetchers import APIFetchers
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "domain-expansion-infinite-void")

def ingest_data(payload):
    """
    Sends data to the backend ingestion endpoint.
    """
    headers = {
        "access_token": API_KEY,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(f"{API_URL}/ingest/raw", json={"content": payload}, headers=headers)
        if response.status_code == 200:
            print(f"Successfully ingested data from {payload.get('source')}!")
        else:
            print(f"Failed to ingest data from {payload.get('source')}. Status: {response.status_code}")
    except Exception as e:
        print(f"Connection error: {e}")

def run_all_scrapers():
    """
    Main loop to run all scrapers and ingest data.
    """
    print("Starting Data Ingestion Job...")
    
    news_scraper = NewsScraper()
    api_fetchers = APIFetchers()
    
    # 1. BeautifulSoup Scrapers
    print("Running BeautifulSoup scrapers...")
    hn_data = news_scraper.scrape_hacker_news()
    if hn_data:
        ingest_data(hn_data)
        
    tc_data = news_scraper.scrape_tech_crunch()
    if tc_data:
        ingest_data(tc_data)

    reddit_ai = news_scraper.scrape_reddit_community("artificial")
    if reddit_ai:
        ingest_data(reddit_ai)

    reddit_pop = news_scraper.scrape_reddit_community("popular")
    if reddit_pop:
        ingest_data(reddit_pop)
        
    # 2. Official API Fetchers
    print("Running API fetchers...")
    news_api_data = api_fetchers.fetch_trending_news()
    if news_api_data:
        ingest_data(news_api_data)
        
    youtube_data = api_fetchers.fetch_youtube_trends()
    if youtube_data:
        ingest_data(youtube_data)
        
    print("Ingestion Job Completed.")

if __name__ == "__main__":
    run_all_scrapers()
