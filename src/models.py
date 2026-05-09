from __future__ import annotations

"""
Shared data models for the AI Trend Daily pipeline.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class RepoData(BaseModel):
    """A single repository entry from GitHub Trending."""
    rank: int = 0
    name: str  # owner/repo
    url: str = ""
    description: str = ""
    language: str = ""
    topics: list[str] = Field(default_factory=list)
    stars: int = 0
    stars_today: int = 0
    forks: int = 0
    author: str = ""
    author_url: str = ""
    ai_category: str = "uncategorized"
    ai_subcategories: list[str] = Field(default_factory=list)
    summary_zh: str = ""
    summary_en: str = ""
    first_seen: str = ""
    fetched_at: str = ""


class CategoryDistribution(BaseModel):
    name: str
    count: int
    percentage: float = 0.0


class LanguageDistribution(BaseModel):
    name: str
    count: int
    percentage: float = 0.0


class DailyReport(BaseModel):
    """The daily trend report."""
    date: str
    generated_at: str = ""
    total_repos: int = 0
    total_ai_repos: int = 0
    categories: list[CategoryDistribution] = Field(default_factory=list)
    languages: list[LanguageDistribution] = Field(default_factory=list)
    top_repos: list[RepoData] = Field(default_factory=list)
    new_entrants: list[RepoData] = Field(default_factory=list)
    top_gainers: list[RepoData] = Field(default_factory=list)
    insight_zh: str = ""
    insight_en: str = ""


class RawScrapeResult(BaseModel):
    """Raw output from the scraper."""
    date: str
    fetched_at: str
    repos: list[RepoData] = Field(default_factory=list)
    source: str = "github_trending"
