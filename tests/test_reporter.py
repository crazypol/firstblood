"""Tests for the reporter module."""

from datetime import date
from src.models import DailyReport, CategoryDistribution, LanguageDistribution, RepoData
from src.reporter.markdown import generate_markdown
from src.reporter.json_exporter import export_report
import json
import tempfile


def _make_test_report() -> DailyReport:
    repo = RepoData(
        rank=1,
        name="test/repo",
        url="https://github.com/test/repo",
        description="A test repository",
        language="Python",
        topics=["ai", "test"],
        stars=1000,
        stars_today=100,
        forks=50,
        ai_category="llm",
    )
    return DailyReport(
        date=date.today().isoformat(),
        generated_at="2026-05-09T12:00:00",
        total_repos=10,
        total_ai_repos=8,
        categories=[
            CategoryDistribution(name="llm", count=5, percentage=62.5),
            CategoryDistribution(name="agent", count=3, percentage=37.5),
        ],
        languages=[
            LanguageDistribution(name="Python", count=6, percentage=60.0),
            LanguageDistribution(name="TypeScript", count=4, percentage=40.0),
        ],
        top_repos=[repo],
    )


def test_markdown_generation():
    report = _make_test_report()
    md = generate_markdown(report)

    assert "AI Trend Daily" in md
    assert report.date in md
    assert "test/repo" in md
    assert "llm" in md
    assert "Python" in md


def test_json_export():
    report = _make_test_report()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = export_report(report, tmpdir)
        assert path.exists()

        with open(path) as f:
            data = json.load(f)
        assert data["date"] == report.date
        assert data["total_repos"] == 10
        assert len(data["top_repos"]) == 1
