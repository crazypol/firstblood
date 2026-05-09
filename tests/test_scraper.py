"""Tests for the GitHub Trending scraper."""

from pathlib import Path
from src.scraper.trending import TrendingScraper


SAMPLE_HTML = """
<article class="Box-row">
  <h2>
    <a href="/langchain-ai/langchain">langchain-ai / langchain</a>
  </h2>
  <p>Building applications with LLMs through composability</p>
  <div itemprop="programmingLanguage">Python</div>
  <div class="d-inline-block float-sm-right">
    128,000 stars 850 stars today
  </div>
  <a href="/langchain-ai/langchain/forks">
    25,000
  </a>
  <a href="/topics/llm">llm</a>
  <a href="/topics/agent">agent</a>
</article>
"""


def test_parse_article():
    scraper = TrendingScraper()
    repos = scraper._parse_html(SAMPLE_HTML)

    assert len(repos) == 1
    repo = repos[0]
    assert repo.name == "langchain-ai/langchain"
    assert repo.stars == 128000
    assert repo.stars_today == 850
    assert repo.forks == 25000
    assert repo.language == "Python"
    assert "llm" in repo.topics
    assert "agent" in repo.topics


def test_parse_number():
    scraper = TrendingScraper()
    assert scraper._parse_number("1,482") == 1482
    assert scraper._parse_number("850") == 850
    assert scraper._parse_number("128,000") == 128000


def test_parse_empty_html():
    scraper = TrendingScraper()
    repos = scraper._parse_html("<html></html>")
    assert repos == []


def test_parse_no_article():
    scraper = TrendingScraper()
    repos = scraper._parse_html("<html><body><p>No repos</p></body></html>")
    assert repos == []
