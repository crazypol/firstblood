from __future__ import annotations

"""
Statistical analysis for GitHub trending data.

Computes category distributions, language distributions,
top gainers, and identifies new entrants.
"""

from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from src.models import (
    RepoData,
    DailyReport,
    CategoryDistribution,
    LanguageDistribution,
)


def compute_stats(
    repos: list[RepoData],
    previous_repos: Optional[list[RepoData]] = None,
    report_date: Optional[str] = None,
) -> DailyReport:
    """Compute all statistics from a list of classified repos.

    Args:
        repos: List of classified repository data
        previous_repos: Previously seen repos (for detecting new entrants)
        report_date: Date string (ISO format)

    Returns:
        DailyReport with all statistics
    """
    today = report_date or date.today().isoformat()

    # Filter to AI-related only (exclude uncategorized)
    ai_repos = [r for r in repos if r.ai_category != "uncategorized"]

    # Category distribution
    cat_counter = Counter(r.ai_category for r in ai_repos)
    total_ai = len(ai_repos)
    categories = [
        CategoryDistribution(
            name=name,
            count=count,
            percentage=round(count / total_ai * 100, 1) if total_ai else 0,
        )
        for name, count in cat_counter.most_common()
    ]

    # Language distribution
    lang_counter = Counter(
        r.language for r in repos if r.language
    )
    total_with_lang = sum(lang_counter.values())
    languages = [
        LanguageDistribution(
            name=name,
            count=count,
            percentage=round(count / total_with_lang * 100, 1)
            if total_with_lang else 0,
        )
        for name, count in lang_counter.most_common()
    ]

    # Top repos by stars_today (descending)
    top_repos = sorted(
        repos, key=lambda r: r.stars_today, reverse=True
    )[:20]
    for i, r in enumerate(top_repos, 1):
        r.rank = i

    # Top gainers: repos with highest stars_today
    top_gainers = sorted(
        ai_repos, key=lambda r: r.stars_today, reverse=True
    )[:5]

    # New entrants: repos in current but not in previous
    new_entrants: list[RepoData] = []
    if previous_repos:
        prev_names = {r.name for r in previous_repos}
        new_entrants = [
            r for r in repos
            if r.name not in prev_names
        ]
        new_entrants = sorted(
            new_entrants, key=lambda r: r.stars_today, reverse=True
        )[:5]

    return DailyReport(
        date=today,
        generated_at=datetime.utcnow().isoformat(),
        total_repos=len(repos),
        total_ai_repos=total_ai,
        categories=categories,
        languages=languages,
        top_repos=top_repos,
        new_entrants=new_entrants,
        top_gainers=top_gainers,
    )
