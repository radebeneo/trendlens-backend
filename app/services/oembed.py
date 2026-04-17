import requests
from typing import Optional

def get_oembed_html(url: str) -> Optional[str]:
    """
    Automatically retrieve oEmbed HTML for common social media platforms.
    """
    # Simple registry of oEmbed providers
    providers = {
        "tiktok.com": "https://www.tiktok.com/oembed",
        "twitter.com": "https://publish.twitter.com/oembed",
        "x.com": "https://publish.twitter.com/oembed",
        "instagram.com": "https://api.instagram.com/oembed",
        "youtube.com": "https://www.youtube.com/oembed",
        "youtu.be": "https://www.youtube.com/oembed",
    }
    
    provider_url = None
    for domain, endpoint in providers.items():
        if domain in url:
            provider_url = endpoint
            break
            
    if not provider_url:
        return None
        
    try:
        response = requests.get(provider_url, params={"url": url}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("html")
    except Exception as e:
        print(f"Error fetching oEmbed for {url}: {e}")
        
    return None
