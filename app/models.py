from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class RawData(Base):
    __tablename__ = "raw_data"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    trends = relationship("Trend", back_populates="category")

class Trend(Base):
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    summary = Column(String)
    velocity = Column(Float) # Trend momentum (up/down)
    rank = Column(Integer)
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="trends")
    sources = relationship("Source", back_populates="trend")

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    trend_id = Column(Integer, ForeignKey("trends.id"))
    title = Column(String)
    url = Column(String)
    source_type = Column(String) # news, tiktok, youtube, instagram
    embed_html = Column(String, nullable=True)
    quality_score = Column(Float, default=0.0)

    trend = relationship("Trend", back_populates="sources")
