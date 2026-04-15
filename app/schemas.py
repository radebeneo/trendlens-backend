from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

# Raw Data Schemas
class RawDataBase(BaseModel):
    content: dict

class RawDataCreate(RawDataBase):
    pass

class RawData(RawDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Source Schemas
class SourceBase(BaseModel):
    title: str
    url: str
    source_type: str
    embed_html: Optional[str] = None
    quality_score: Optional[float] = 0.0

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    id: int
    trend_id: int

    class Config:
        from_attributes = True

# Trend Schemas
class TrendBase(BaseModel):
    name: str
    summary: str
    velocity: float
    rank: int
    category_id: int

class TrendCreate(TrendBase):
    pass

class Trend(TrendBase):
    id: int
    created_at: datetime
    updated_at: datetime
    sources: List[Source] = []

    class Config:
        from_attributes = True

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    trends: List[Trend] = []

    class Config:
        from_attributes = True
