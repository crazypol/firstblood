"""Tests for the analyzer module."""

from src.models import RepoData
from src.analyzer.stats import compute_stats


def _make_repo(
    name: str,
    stars: int = 100,
    stars_today: int = 10,
    language: str = "Python",
    category: str = "llm",
) -> RepoData:
    return RepoData(
        name=name,
        url=f"https://github.com/{name}",
        description="Test repo",
        language=language,
        ai_category=category,
        stars=stars,
        stars_today=stars_today,
        forks=10,
    )


def test_compute_stats_counts():
    repos = [
        _make_repo("a/one", stars_today=50),
        _make_repo("b/two", stars_today=30, category="agent"),
        _make_repo("c/three", stars_today=10, category="rag"),
        _make_repo("d/four", stars_today=5, category="uncategorized"),
    ]
    report = compute_stats(repos)

    assert report.total_repos == 4
    assert report.total_ai_repos == 3  # uncategorized excluded


def test_compute_stats_top_repos():
    repos = [
        _make_repo("low/repo", stars_today=5),
        _make_repo("high/repo", stars_today=100),
        _make_repo("mid/repo", stars_today=50),
    ]
    report = compute_stats(repos)
    assert report.top_repos[0].name == "high/repo"
    assert report.top_repos[0].stars_today == 100


def test_compute_stats_language_distribution():
    repos = [
        _make_repo("a/py", language="Python"),
        _make_repo("b/ts", language="TypeScript"),
        _make_repo("c/py2", language="Python"),
    ]
    report = compute_stats(repos)
    lang_map = {l.name: l.count for l in report.languages}
    assert lang_map.get("Python") == 2
    assert lang_map.get("TypeScript") == 1


def test_compute_stats_category_distribution():
    repos = [
        _make_repo("a/llm", category="llm"),
        _make_repo("b/llm2", category="llm"),
        _make_repo("c/agent", category="agent"),
    ]
    report = compute_stats(repos)
    cat_map = {c.name: c.count for c in report.categories}
    assert cat_map.get("llm") == 2
    assert cat_map.get("agent") == 1


def test_new_entrants():
    current = [
        _make_repo("existing/repo"),
        _make_repo("new/repo", stars_today=50),
    ]
    previous = [
        _make_repo("existing/repo"),
    ]
    report = compute_stats(current, previous_repos=previous)
    assert len(report.new_entrants) == 1
    assert report.new_entrants[0].name == "new/repo"
