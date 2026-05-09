from __future__ import annotations

"""
JSON exporter for daily reports and raw data.
"""

import json
from datetime import date
from pathlib import Path

from src.models import DailyReport, RawScrapeResult


def export_report(report: DailyReport, output_dir: str | Path) -> Path:
    """Export the daily report as JSON.

    Args:
        report: DailyReport to export
        output_dir: Output directory

    Returns:
        Path to the saved file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filepath = output_path / f"{report.date}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2, exclude_none=True))

    # Also update latest.json
    latest_path = output_path / "latest.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2, exclude_none=True))

    return filepath


def export_raw(result: RawScrapeResult, output_dir: str | Path) -> Path:
    """Export raw scrape result as JSON."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filepath = output_path / f"{result.date}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(result.model_dump_json(indent=2, exclude_none=True))

    return filepath


def load_latest_report(reports_dir: str | Path) -> DailyReport | None:
    """Load the latest report from JSON."""
    reports_path = Path(reports_dir)
    latest_file = reports_path / "latest.json"
    if not latest_file.exists():
        return None

    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return DailyReport(**data)
    except (json.JSONDecodeError, KeyError, ValueError):
        return None
