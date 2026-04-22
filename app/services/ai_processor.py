import os
import json
from sqlalchemy.orm import Session
from .. import models
from .oembed import get_oembed_html
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0)

def process_raw_data(db: Session, raw_data_id: int):
    """
    Background task to process raw, scraped data.
    Extracts MULTIPLE trends from a single batch and maps relevant sources.
    1. Fetches raw data from DB.
    2. Clusters/Analyzes content via LLM.
    3. Categorizes and creates Trend entries.
    4. Automatically adds sources and oEmbed HTML.
    """
    raw_item = db.query(models.RawData).filter(models.RawData.id == raw_data_id).first()
    if not raw_item:
        return

    content = raw_item.content # This is the JSON content

    # Initial processing prompt for Gemini
    # prompt = PromptTemplate.from_template(
    #     """
    #     Analyze the following raw scraped data from social media/web:
    #     {data}
    #
    #     Tasks:
    #     1. Identify the core trend or topic.
    #     2. Write a 1-sentence summary of what it means.
    #     3. Assign a velocity (0.0 to 100.0) based on perceived viral potential.
    #     4. Select a category name from this list: [Tech, Gen-Z Slang, Fashion, Politics, Pop Culture, Other].
    #
    #     Return the result in JSON format with keys:
    #     trend_name, summary, velocity, category_name
    #     """
    # )

    prompt = PromptTemplate.from_template(
        """
        You are TrendLens, an expert data analyst and cultural trend predictor.
        Analyze the following raw scraped data payload from social media/news:

        {data}

        Tasks:
        1. Identify the SINGLE most dominant and impactful trend or topic within this data batch. Ignore the noise.
        2. Write a concise, engaging 1-sentence summary of what this trend is and why it matters right now.
        3. Assign a velocity score (float from 0.0 to 100.0). Calculate this based on any available metrics in the data (e.g., views, likes, upvotes, rank) and its explosive cultural/news potential.
        4. Select the most accurate category from this exact list: 
           [Technology, Artificial Intelligence, Business, Pop Culture, Politics, Fashion, Science, Gen-Z Culture, Gaming, Other]

        Format the output strictly as a JSON object with exactly these keys:
        {{
               trends:[ 
                   {{
                        "trend_name": "string (A catchy, concise name for the trend)",
                        "summary": "string (1-sentence explanation)",
                        "velocity": float (0.0 to 100.0),
                        "category_name": "string (Must be from the provided list)"
                        "relevant_urls": ["url1", "url2"]
                    }}
                ]
        }}
        """
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:

        # Pass the raw JSON to Gemini
        result = chain.invoke({"data": json.dumps(content)})
        extracted_trends = result.get("trends", [])

        print(f"--- AI Extracted {len(extracted_trends)} Trends ---")
        
        # Loop through every trend Gemini found
        for trend_data in extracted_trends:
            print(f"Processing: {trend_data.get('trend_name')}")
        
            # 1. Handle Category
            category_name = trend_data.get("category_name", "Other")
            db_category = db.query(models.Category).filter(models.Category.name == category_name).first()
            if not db_category:
                db_category = models.Category(name=category_name, description=f"{category_name} related trends")
                db.add(db_category)
                db.commit()
                db.refresh(db_category)

            # 2. Create Trend
            db_trend = models.Trend(
                name=trend_data.get("trend_name", "Unknown Trend"),
                summary=trend_data.get("summary", ""),
                velocity=trend_data.get("velocity", 0.0),
                rank=1, # Default rank
                category_id=db_category.id
            )
            db.add(db_trend)
            db.commit()
            db.refresh(db_trend)

            # 3. Handle Sources (Only attach URLs relevant to THIS specific trend)
            urls = trend_data.get("relevant_urls",[])

            for url in urls:
                embed_html = get_oembed_html(url)
                db_source = models.Source(
                    trend_id=db_trend.id,
                    title=trend_data.get("trend_name"),
                    url=url,
                    source_type="social", # In a future update, we can have the AI guess the source type
                    embed_html=embed_html,
                    quality_score=80.0
                )
                db.add(db_source)

            db.commit()
        
    except Exception as e:
        print(f"Error processing AI task: {e}")
