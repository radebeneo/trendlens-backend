from fastapi import FastAPI, Depends, HTTPException, Security, BackgroundTasks, Request
from fastapi.security.api_key import APIKeyHeader, APIKey
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List
import os
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from . import models, schemas, database
from .database import get_db
from .services import ai_processor, oembed

# models.Base.metadata.create_all(bind=engine)

API_KEY = os.getenv("API_KEY", "super-secret-key")
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=403, detail="Could not validate credentials"
        )

app = FastAPI(title="TrendLens API")

@app.on_event("startup")
async def startup():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis = aioredis.from_url(redis_url, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.get("/")
def read_root():
    return {"message": "Welcome to TrendLens API"}

# Categories
@app.get("/categories", response_model=List[schemas.Category])
@cache(expire=900)
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Category).offset(skip).limit(limit).all()

@app.post("/categories", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    db_category = models.Category(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Trends
@app.get("/trends", response_model=List[schemas.Trend])
@cache(expire=600)
def get_trends(category_id: int = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.Trend)
    if category_id:
        query = query.filter(models.Trend.category_id == category_id)
    return query.order_by(models.Trend.rank).offset(skip).limit(limit).all()

@app.post("/trends", response_model=schemas.Trend)
def create_trend(trend: schemas.TrendCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    db_trend = models.Trend(**trend.dict())
    db.add(db_trend)
    db.commit()
    db.refresh(db_trend)
    return db_trend

# Trend Detail
@app.get("/trends/{trend_id}", response_model=schemas.Trend)
def get_trend(trend_id: int, db: Session = Depends(get_db)):
    db_trend = db.query(models.Trend).filter(models.Trend.id == trend_id).first()
    if not db_trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return db_trend

# Sources for a Trend
@app.post("/trends/{trend_id}/sources", response_model=schemas.Source)
def create_source(trend_id: int, source: schemas.SourceCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    # Automatically get oEmbed HTML if not provided
    embed_html = source.embed_html
    if not embed_html:
        embed_html = oembed.get_oembed_html(source.url)
        
    db_source = models.Source(
        **source.dict(exclude={"embed_html"}),
        trend_id=trend_id,
        embed_html=embed_html
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

# Raw Data Ingestion
@app.post("/ingest/raw", response_model=schemas.RawData)
def ingest_raw_data(
    raw_data: schemas.RawDataCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), 
    api_key: APIKey = Depends(get_api_key)
):
    db_raw_data = models.RawData(content=raw_data.content)
    db.add(db_raw_data)
    db.commit()
    db.refresh(db_raw_data)
    
    # Trigger background AI processing
    background_tasks.add_task(ai_processor.process_raw_data, db, db_raw_data.id)
    
    return db_raw_data

# Search
@app.get("/search", response_model=List[schemas.Trend])
def search_trends(q: str, db: Session = Depends(get_db)):
    """
    Search trends using PostgreSQL Full Text Search.
    """
    # Simple search using ilike for non-Postgres or basic search
    # But user specifically asked for tsvector (Full Text Search)
    
    # query = db.query(models.Trend).filter(
    #     or_(
    #         models.Trend.name.ilike(f"%{q}%"),
    #         models.Trend.summary.ilike(f"%{q}%")
    #     )
    # )
    
    # PostgreSQL native Full Text Search
    search_query = func.to_tsquery('english', q.replace(' ', ' & '))
    query = db.query(models.Trend).filter(
        func.to_tsvector('english', models.Trend.name + ' ' + models.Trend.summary).op('@@')(search_query)
    )
    
    return query.limit(50).all()
