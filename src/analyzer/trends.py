from __future__ import annotations

"""
Trend analysis across multiple days.

Computes day-over-day changes, weekly trends,
and identifies rising/falling categories.
"""

from collections import defaultdict
from pathlib import Path
from typing import Optional

from src.models import DailyReport


def compute_category_trend(
    reports: list[DailyReport],
) -> dict[str, list[tuple[str, int]]]:
    """Compute category count trends across multiple reports.

    Args:
        reports: List of DailyReport ordered by date (ascending)

    Returns:
        Dict mapping category name to list of (date, count) tuples
    """
    trends: dict[str, list[tuple[str, int]]] = defaultdict(list)

    for report in reports:
        for cat in report.categories:
            trends[cat.name].append((report.date, cat.count))

    return dict(trends)


def compute_language_trend(
    reports: list[DailyReport],
) -> dict[str, list[tuple[str, float]]]:
    """Compute language percentage trends."""
    trends: dict[str, list[tuple[str, float]]] = defaultdict(list)

    for report in reports:
        for lang in report.languages:
            trends[lang.name].append((report.date, lang.percentage))

    return dict(trends)


def find_rising_categories(
    reports: list[DailyReport],
    lookback: int = 3,
) -> list[tuple[str, float]]:
    """Identify categories with the highest growth rate.

    Args:
        reports: Sorted list of reports (ascending by date)
        lookback: Number of days to compare

    Returns:
        List of (category_name, growth_rate) sorted by growth desc
    """
    if len(reports) < 2:
        return []

    latest = reports[-1]
    earlier = reports[-min(lookback + 1, len(reports))]

    latest_counts = {c.name: c.count for c in latest.categories}
    earlier_counts = {c.name: c.count for c in earlier.categories}

    growth: list[tuple[str, float]] = []
    for name, current in latest_counts.items():
        prev = earlier_counts.get(name, 0)
        if prev > 0:
            rate = round((current - prev) / prev * 100, 1)
        else:
            rate = 100.0 if current > 0 else 0.0
        growth.append((name, rate))

    return sorted(growth, key=lambda x: -x[1])
