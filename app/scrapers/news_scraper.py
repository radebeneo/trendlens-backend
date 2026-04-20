import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class NewsScraper:
    """
    Scraper for tech blogs and news sites using BeautifulSoup.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape_hacker_news(self):
        """
        Scrapes top stories from Hacker News.
        """
        url = "https://news.ycombinator.com/"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        stories = []
        for item in soup.select('.athing'):
            title_node = item.select_one('.titleline > a')
            if title_node:
                stories.append({
                    "title": title_node.text,
                    "url": title_node['href'],
                    "source": "HackerNews"
                })
        
        return {
            "source": "HackerNews",
            "scraped_at": datetime.utcnow().isoformat(),
            "data": stories[:10]  # Top 10 stories
        }

    def scrape_tech_crunch(self):
        """
        Scrapes latest stories from TechCrunch.
        """
        url = "https://techcrunch.com/"
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            stories = []
            # TechCrunch structure might vary, this is a common pattern for their post-titles
            for post in soup.select('h2.post-block__title a'):
                stories.append({
                    "title": post.text.strip(),
                    "url": post['href'],
                    "source": "TechCrunch"
                })
            
            return {
                "source": "TechCrunch",
                "scraped_at": datetime.utcnow().isoformat(),
                "data": stories[:10]
            }
        except Exception as e:
            print(f"Error scraping TechCrunch: {e}")
            return None

if __name__ == "__main__":
    scraper = NewsScraper()
    print(json.dumps(scraper.scrape_hacker_news(), indent=2))
