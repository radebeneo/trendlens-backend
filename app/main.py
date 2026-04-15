from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from sqlalchemy.orm import Session
from typing import List
import os
from . import models, schemas, database
from .database import get_db

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

@app.get("/")
def read_root():
    return {"message": "Welcome to TrendLens API"}

# Categories
@app.get("/categories", response_model=List[schemas.Category])
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
    db_source = models.Source(**source.dict(), trend_id=trend_id)
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

# Raw Data Ingestion
@app.post("/ingest/raw", response_model=schemas.RawData)
def ingest_raw_data(raw_data: schemas.RawDataCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    db_raw_data = models.RawData(content=raw_data.content)
    db.add(db_raw_data)
    db.commit()
    db.refresh(db_raw_data)
    return db_raw_data
