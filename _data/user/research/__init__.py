"""
Pydantic models for researching topics using Google Trends, Exploding Topics, and Reddit (popular for trend discovery).
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum

class ResearchSource(str, Enum):
    google_trends = "google_trends"
    exploding_topics = "exploding_topics"
    reddit = "reddit"

class TopicResearchRequest(BaseModel):
    """Request model for researching a topic across multiple sources."""
    topic: str = Field(..., description="The topic or keyword to research.")
    sources: List[ResearchSource] = Field(default_factory=lambda: [ResearchSource.google_trends], description="Sources to research from.")
    region: Optional[str] = Field(None, description="Region/country code for research.")
    language: Optional[str] = Field(None, description="Language code (e.g., 'en').")
    timeframe: Optional[str] = Field(None, description="Timeframe for trends (e.g., 'now 7-d', 'today 12-m').")

class TrendDataPoint(BaseModel):
    """Single data point for a trend over time."""
    date: str = Field(..., description="Date or time period.")
    value: float = Field(..., description="Trend metric value (e.g., search interest, score).")

class SourceTrendResult(BaseModel):
    """Result from a single source for a topic."""
    source: ResearchSource
    topic: str
    trend_over_time: List[TrendDataPoint] = Field(default_factory=list)
    related_topics: List[str] = Field(default_factory=list)
    summary: Optional[str] = Field(None, description="Short summary or insight from this source.")
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict, description="Extra metadata from the source.")

class TopicResearchResult(BaseModel):
    """Aggregated research results for a topic from all sources."""
    topic: str
    results: List[SourceTrendResult] = Field(default_factory=list)
    overall_summary: Optional[str] = Field(None, description="Combined summary/insight across all sources.")
