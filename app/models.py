"""
SEO Health Checker - Data Models
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional


class ScanRequest(BaseModel):
    """What the frontend sends to start a scan"""
    url: str


class PageResult(BaseModel):
    """SEO results for a single page"""
    url: str
    status: int
    load_ms: Optional[int] = None
    score: int
    passed: list[str]
    issues: list[str]
    title: str
    h1: str


class ScanResponse(BaseModel):
    """Complete scan report sent back to frontend"""
    url: str
    pages_crawled: int
    overall_score: int
    grade: str
    results: list[PageResult]
    top_issues: list[dict]
    recommendations: list[str]
