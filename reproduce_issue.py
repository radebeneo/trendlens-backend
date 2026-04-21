
import json
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.services import ai_processor
from app import models

def reproduce():
    # Mock DB Session
    db = MagicMock(spec=Session)
    
    # Mock a RawData entry with a typical scraper format (e.g., NewsAPI)
    # NewsAPI data structure: {"source": "NewsAPI", "data": [{"url": "http://example.com"}]}
    raw_content = {
        "source": "NewsAPI",
        "category": "technology",
        "data": [
            {"title": "News Title 1", "url": "http://example.com/1", "source": "SomeSource"},
            {"title": "News Title 2", "url": "http://example.com/2", "source": "SomeSource"}
        ]
    }
    
    raw_item = models.RawData(id=1, content=raw_content)
    
    # Configure mock DB query to return our raw_item
    db.query.return_value.filter.return_value.first.side_effect = [raw_item, None] # First call for RawData, second for Category
    
    # Mock LLM chain to return a trend
    ai_processor.chain = MagicMock()
    ai_processor.chain.invoke.return_value = {
        "trend_name": "Test Trend",
        "summary": "This is a test summary",
        "velocity": 50.0,
        "category_name": "Tech"
    }

    # Mock get_oembed_html to return something
    ai_processor.get_oembed_html = MagicMock(return_value="<div>Mock Embed</div>")

    print(f"Running process_raw_data with {raw_content.get('source')} format...")
    ai_processor.process_raw_data(db, 1)
    
    # Check if db.add was called for models.Source
    source_adds = [call for call in db.add.call_args_list if isinstance(call.args[0], models.Source)]
    
    print(f"Number of Source entries added: {len(source_adds)}")
    
    if len(source_adds) == 0:
        print("FAILURE: No Source entries were added to the database.")
    else:
        print(f"SUCCESS: {len(source_adds)} Source entries were added.")

    # Test TikTok format
    db.add.reset_mock()
    raw_content_tiktok = {
        "source": "tiktok",
        "video_urls": ["https://tiktok.com/v1", "https://tiktok.com/v2"]
    }
    raw_item.content = raw_content_tiktok
    db.query.return_value.filter.return_value.first.side_effect = [raw_item, MagicMock()]
    
    print(f"Running process_raw_data with tiktok format...")
    ai_processor.process_raw_data(db, 1)
    source_adds_tiktok = [call for call in db.add.call_args_list if isinstance(call.args[0], models.Source)]
    print(f"Number of Source entries added (tiktok): {len(source_adds_tiktok)}")
    if len(source_adds_tiktok) == 2:
        print("SUCCESS: TikTok format handled.")
    else:
        print("FAILURE: TikTok format failed.")

if __name__ == "__main__":
    reproduce()
