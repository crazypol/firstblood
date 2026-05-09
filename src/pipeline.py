from __future__ import annotations

"""
Main pipeline for AI Trend Daily.

Orchestrates: scrape → classify → analyze → report → notify
"""

import json
import sys
from datetime import date
from pathlib import Path

from config import settings
from src.models import DailyReport
from src.scraper.trending import TrendingScraper, run as run_scraper
from src.scraper.github_api import GitHubAPIClient
from src.classifier.rules import batch_classify, classify_repo
from src.analyzer.stats import compute_stats
from src.reporter.markdown import generate_markdown
from src.reporter.json_exporter import (
    export_report, export_raw, load_latest_report,
)
from src.reporter.insights import generate_insight, generate_repo_summary


def run_pipeline(
    since: str = "daily",
    enhance_api: bool = False,
    generate_ai: bool = False,
    output_dir: str | None = None,
) -> DailyReport:
    """Run the full data pipeline.

    Args:
        since: "daily", "weekly", or "monthly"
        enhance_api: Whether to supplement with GitHub API
        generate_ai: Whether to generate AI summaries (requires API key)
        output_dir: Output directory (default: settings.data_dir)

    Returns:
        DailyReport with all results
    """
    output_base = Path(output_dir or settings.data_dir)
    raw_dir = output_base / "raw"
    processed_dir = output_base / "processed"
    reports_dir = output_base / "reports"

    # Step 1: Scrape
    print(f"[1/5] Scraping GitHub Trending ({since})...")
    scrape_result = run_scraper(since=since, output_dir=str(raw_dir))
    repos = scrape_result.repos
    print(f"       → {len(repos)} repositories fetched")

    if not repos:
        print("       ⚠ No repos found, aborting")
        return DailyReport(date=date.today().isoformat())

    # Step 1.5: Enhance with GitHub API (optional)
    if enhance_api:
        print("[1.5/5] Enhancing with GitHub API...")
        api_client = GitHubAPIClient()
        enhanced = []
        for repo in repos[:30]:  # Limit to top 30 to stay within rate limits
            enhanced.append(api_client.enhance_repo(repo))
        api_client.close()
        repos = enhanced + repos[30:]
        print(f"       → Enhanced {min(30, len(repos))} repos")

    # Step 2: Classify
    print(f"[2/5] Classifying {len(repos)} repos into AI categories...")
    repos = batch_classify(repos)
    ai_count = sum(1 for r in repos if r.ai_category != "uncategorized")
    print(f"       → {ai_count} classified as AI-related")

    # Step 3: Analyze
    print("[3/5] Computing statistics...")
    previous = load_latest_report(str(reports_dir))
    prev_repos = previous.top_repos if previous else None
    report = compute_stats(
        repos, previous_repos=prev_repos
    )
    print(f"       → {report.total_ai_repos} AI repos across "
          f"{len(report.categories)} categories")

    # Step 4: Generate AI insights (optional)
    if generate_ai:
        print("[4/5] Generating AI insights...")
        report.insight_zh = generate_insight(report)
        for repo in report.top_repos[:10]:
            if not repo.summary_zh:
                repo.summary_zh = generate_repo_summary(repo)
        print(f"       → Insight generated")
    else:
        print("[4/5] Skipping AI insights (use --ai to enable)")

    # Step 5: Export
    print("[5/5] Exporting reports...")
    md_content = generate_markdown(report)
    md_path = reports_dir / f"{report.date}.md"
    reports_dir.mkdir(parents=True, exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    json_path = export_report(report, output_dir=str(reports_dir))

    # Also save processed data
    processed_dir.mkdir(parents=True, exist_ok=True)
    with open(processed_dir / f"{report.date}.json", "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2, exclude_none=True))

    print(f"       → Markdown: {md_path}")
    print(f"       → JSON: {json_path}")
    print(f"\n✅ Pipeline complete!")

    return report


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Trend Daily — GitHub AI trending pipeline"
    )
    parser.add_argument(
        "--since", choices=["daily", "weekly", "monthly"],
        default="daily", help="Time range"
    )
    parser.add_argument(
        "--api", action="store_true",
        help="Enhance data with GitHub API"
    )
    parser.add_argument(
        "--ai", action="store_true",
        help="Generate AI summaries (requires API key)"
    )
    parser.add_argument(
        "--output", default=None,
        help="Output directory"
    )

    args = parser.parse_args()
    run_pipeline(
        since=args.since,
        enhance_api=args.api,
        generate_ai=args.ai,
        output_dir=args.output,
    )


if __name__ == "__main__":
    main()
