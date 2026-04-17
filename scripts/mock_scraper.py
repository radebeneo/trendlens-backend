import requests
import json
import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "domain-expansion-infinite-void")

def ingest_sample_data():
    sample_data = {
        "content": {
            "source": "tiktok",
            "trending_hashtags": ["#demure", "#brat", "#devinai"],
            "video_urls": ["https://tiktok.com/v1", "https://tiktok.com/v2"],
            "scraped_at": "2024-04-14T12:00:00Z"
        }
    }
    
    headers = {
        "access_token": API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"Sending data to {API_URL}/ingest/raw...")
    try:
        response = requests.post(f"{API_URL}/ingest/raw", json=sample_data, headers=headers)
        if response.status_code == 200:
            print("Successfully ingested data!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Failed to ingest data. Status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Is it running?")

if __name__ == "__main__":
    ingest_sample_data()
