import os
import json
from sqlalchemy.orm import Session
from .. import models
from .oembed import get_oembed_html
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Initialize LLM
# Ensure GOOGLE_API_KEY is in your environment
llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0)

def process_raw_data(db: Session, raw_data_id: int):
    """
    Background task to process raw scraped data.
    1. Fetches raw data from DB.
    2. Clusters/Analyzes content via LLM.
    3. Categorizes and creates Trend entries.
    4. Automatically adds sources and oEmbed HTML.
    """
    raw_item = db.query(models.RawData).filter(models.RawData.id == raw_data_id).first()
    if not raw_item:
        return

    content = raw_item.content # This is the JSON content

    # In a real scenario, you'd cluster multiple raw items.
    # For this simplified version, we'll process each raw item as a potential trend.
    
    prompt = PromptTemplate.from_template(
        """
        Analyze the following raw scraped data from social media/web:
        {data}
        
        Tasks:
        1. Identify the core trend or topic.
        2. Write a 1-sentence summary of what it means.
        3. Assign a velocity (0.0 to 100.0) based on perceived viral potential.
        4. Select a category name from this list: [Tech, Gen-Z Slang, Fashion, Politics, Pop Culture, Other].
        
        Return the result in JSON format with keys:
        trend_name, summary, velocity, category_name
        """
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = chain.invoke({"data": json.dumps(content)})
        
        # Log the AI results
        print(f"--- AI Processed Results ---")
        print(f"Trend: {result.get('trend_name')}")
        print(f"Summary: {result.get('summary')}")
        print(f"Category: {result.get('category_name')}")
        print(f"Velocity: {result.get('velocity')}")
        print(f"----------------------------")
        
        # 1. Handle Category
        category_name = result.get("category_name", "Other")
        db_category = db.query(models.Category).filter(models.Category.name == category_name).first()
        if not db_category:
            db_category = models.Category(name=category_name, description=f"{category_name} related trends")
            db.add(db_category)
            db.commit()
            db.refresh(db_category)
        
        # 2. Create Trend
        db_trend = models.Trend(
            name=result.get("trend_name", "Unknown Trend"),
            summary=result.get("summary", ""),
            velocity=result.get("velocity", 0.0),
            rank=1, # Default rank
            category_id=db_category.id
        )
        db.add(db_trend)
        db.commit()
        db.refresh(db_trend)
        
        # 3. Handle Sources (if any URLs are in raw data)
        # Assuming content has a 'urls' list for this example
        urls = content.get("urls", [])
        for url in urls:
            embed_html = get_oembed_html(url)
            db_source = models.Source(
                trend_id=db_trend.id,
                title=result.get("trend_name"),
                url=url,
                source_type="social",
                embed_html=embed_html,
                quality_score=80.0
            )
            db.add(db_source)
        
        db.commit()
        
    except Exception as e:
        print(f"Error processing AI task: {e}")
