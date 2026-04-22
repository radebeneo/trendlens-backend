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

    def scrape_reddit_community(self, subreddit="popular"):
        """
        Scrapes Reddit communities via backdoor, using their public JSON endpoints
        """
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
        # Reddit strictly requires a custom User-Agent to avoid rate limiting
        custom_headers = {"User-Agent": "TrendLens-Scraper/1.0 (Contact: admin@localhost)"}

        try:
            response = requests.get(url, headers=custom_headers)
            response.raise_for_status()
            data = response.json()

            posts=[]

            for item in data.get['data', {}]['children', []]:
                post_data = item.get('data', {})
                posts.append({
                    "title": post_data.get('title'),
                    "url": f"https://www.reddit.com{post_data.get('permalink')}",
                    "score": post_data.get('score'),
                    "source": f"Reddit /r/{subreddit}"
                })

            return {
                "source": f"Reddit /r/{subreddit}",
                "scraped_at": datetime.utcnow().isoformat(),
                "data": posts[:10]
            }
        except Exception as e:
            print(f"Error scraping Reddit: {e}")
            return None

    def scrape_yomzansi(self):
        """
        Scrapes the latest culture, sneaker, and music news from Yomzansi.
        Great for capturing South African/African youth trends.
        """

        url = "https://www.yomzansi.com/"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            stories = []
            # Yomzansi typically uses standard Word-Press article markup
            for article in soup.select('article')[:10]:
                title_node = article.select_one('.entry-title a, h2 a, h3 a')
                if title_node:
                    title = title_node.text.strip()
                    link =title_node.get('href')

                    if title and link:
                        stories.append({
                            "title": title,
                            "url": link,
                            "source": "Yomzansi"
                        })

            return{
                "source": "Yomzansi",
                "scraped_at": datetime.utcnow().isoformat(),
                "data": stories
            }
        except Exception as e:
            print(f"Error scraping Yomzansi: {e}")
            return None

    def scrape_mag_generic(self, name, url, selector):
        """
        A generic scraper for standard digital magazines (like Freshmenmag, Hypebeast, etc.)
        Pass target URL and CSS selector for the article headlines.
        """

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            stories = []

            for item in soup.select(selector)[:10]:
                # Find the first anchor tag within the selected element
                link_node = item if item.name == 'a' else item.select_one('a')
                if link_node and link_node.get('href'):
                    title = link_node.text.strip() or item.text.strip()
                    if title:
                        stories.append({
                            "title": title,
                            "url": link_node['href'],
                            "source": name
                        })

            return {
                "source": name,
                "scraped_at": datetime.utcnow().isoformat(),
                "data": stories
            }

        except Exception as e:
            print(f"Error scraping {name}: {e}")
            return None

    def scrape_mybroadband(self):
        """
        Scrapes top stories from SA's largest tech site.
        """
        url = "https://www.mybroadband.co.za/news/"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            stories = []
            # MyBroadband uses article tags with a title class
            for article in soup.select('article')[:10]:
                title_node = article.select_one('.title a, h2 a')
                if title_node:
                    title = title_node.text.strip()
                    link = title_node.get('href')
                    if title and link:
                        stories.append({
                            "title": title,
                            "url": link,
                            "source": "MyBroadband"
                        })

            return {
                "source": "MyBroadband",
                "scraped_at": datetime.utcnow().isoformat(),
                "data": stories
            }

        except Exception as e:
            print(f"Error scraping MyBroadband: {e}")
            return None

    def scrape_techcentral(self):
        """
        Scrapes top B@B tech and telecom news from techcentral.co.za
        """
        url = "https://www.techcentral.co.za/"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            stories = []
            # TechCentral is a standard Word-Press site
            for article in soup.select('article')[:10]:
                title_node = article.select_one('.entry-title a, h3 a')
                if title_node:
                    title = title_node.text.strip()
                    link = title_node.get('href')
                    if title and link:
                        stories.append({
                            "title": title,
                            "url": link,
                            "source": "TechCentral"
                        })

            return {
                "source": "TechCentral",
                "scraped_at": datetime.utcnow().isoformat(),
                "data": stories
            }

        except Exception as e:
            print(f"Error scraping TechCentral: {e}")
            return None



if __name__ == "__main__":
    scraper = NewsScraper()
    print(json.dumps(scraper.scrape_reddit_community("artificial"), indent=2))
