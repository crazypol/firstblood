from __future__ import annotations

"""
GitHub Trending page scraper.

Fetches trending repositories from github.com/trending
for daily, weekly, and monthly time ranges.
"""

import re
import json
from datetime import date, datetime
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from config import settings
from src.models import RepoData, RawScrapeResult


class TrendingScraper:
    """Scrape GitHub Trending page for popular repositories."""

    BASE_URL = settings.github_trending_url
    TIMEOUT = settings.request_timeout

    def __init__(self):
        self.client = httpx.Client(
            follow_redirects=True,
            timeout=self.TIMEOUT,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            },
        )

    def fetch_trending(
        self,
        since: str = "daily",
        language: str = "",
        spoken_language: str = "",
    ) -> list[RepoData]:
        """Fetch trending repos for a given time range.

        Args:
            since: "daily", "weekly", or "monthly"
            language: programming language filter (e.g. "python")
            spoken_language: spoken language filter (e.g. "zh")

        Returns:
            List of RepoData objects
        """
        url = self.BASE_URL
        params = {}
        if since and since != "daily":
            params["since"] = since
        if language:
            url = f"{url}/{language}"
        if spoken_language:
            params["spoken_language_code"] = spoken_language

        response = self.client.get(url, params=params)
        response.raise_for_status()
        return self._parse_html(response.text)

    def _parse_html(self, html: str) -> list[RepoData]:
        """Parse the GitHub Trending HTML page."""
        soup = BeautifulSoup(html, "html.parser")
        articles = soup.select("article.Box-row")
        repos = []

        for article in articles:
            try:
                repo = self._parse_article(article)
                if repo:
                    repos.append(repo)
            except Exception as e:
                continue

        return repos

    def _parse_article(self, article) -> RepoData | None:
        """Parse a single repository article element."""
        # Repository name
        h2 = article.select_one("h2")
        if not h2:
            return None
        link = h2.select_one("a")
        if not link:
            return None

        href = link.get("href", "").strip("/")
        # href is "owner/repo"
        parts = href.split("/")
        if len(parts) < 2:
            return None
        owner, repo_name = parts[0], parts[1]
        full_name = f"{owner}/{repo_name}"

        # Description
        desc_elem = article.select_one("p")
        description = desc_elem.text.strip() if desc_elem else ""

        # Language
        lang_elem = article.select_one("[itemprop='programmingLanguage']")
        language = lang_elem.text.strip() if lang_elem else ""

        # Stars
        stars = 0
        stars_elem = article.select_one(
            ".d-inline-block.float-sm-right"
        )
        if stars_elem:
            stars_text = stars_elem.text.strip().replace(",", "")
            stars_match = re.search(r"(\d[\d,]*)\s*stars", stars_text)
            if stars_match:
                stars = self._parse_number(stars_match.group(1))

        # Stars today
        stars_today = 0
        stars_today_elem = article.select_one(
            ".d-inline-block.float-sm-right"
        )
        if stars_today_elem:
            today_text = stars_today_elem.text.strip()
            today_match = re.search(r"([\d,]+)\s*stars\s+today", today_text)
            if today_match:
                stars_today = self._parse_number(today_match.group(1))

        # Forks
        forks = 0
        forks_elem = article.select_one("a[href$='/forks']")
        if forks_elem:
            forks_text = forks_elem.text.strip().replace(",", "")
            forks_match = re.search(r"(\d[\d,]*)", forks_text)
            if forks_match:
                forks = self._parse_number(forks_match.group(1))

        # Topics
        topics = []
        topic_elems = article.select("a[href^='/topics/']")
        for t in topic_elems:
            topic = t.text.strip()
            if topic:
                topics.append(topic)

        # Author / org avatar link
        avatar_link = article.select_one("a[href^='/'] img")
        author_url = f"https://github.com/{owner}" if owner else ""

        now = datetime.utcnow().isoformat()

        return RepoData(
            name=full_name,
            url=f"https://github.com/{full_name}",
            description=description,
            language=language,
            topics=list(set(topics)),
            stars=stars,
            stars_today=stars_today,
            forks=forks,
            author=owner,
            author_url=author_url,
            fetched_at=now,
        )

    def _parse_number(self, text: str) -> int:
        """Parse a number string (e.g. '1,482' -> 1482)."""
        return int(text.replace(",", ""))

    def close(self):
        self.client.close()


def run(since: str = "daily", output_dir: str | None = None) -> RawScrapeResult:
    """Run the scraper and optionally save results.

    Args:
        since: "daily", "weekly", "monthly"
        output_dir: if provided, save raw JSON to this directory

    Returns:
        RawScrapeResult with fetched repos
    """
    scraper = TrendingScraper()
    try:
        repos = scraper.fetch_trending(since=since)
        today = date.today().isoformat()
        now = datetime.utcnow().isoformat()

        result = RawScrapeResult(
            date=today,
            fetched_at=now,
            repos=repos,
            source=f"github_trending_{since}",
        )

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            filepath = output_path / f"{today}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(result.model_dump_json(indent=2, exclude_none=True))

        return result
    finally:
        scraper.close()


if __name__ == "__main__":
    result = run(output_dir=settings.data_dir + "/raw")
    print(f"Fetched {len(result.repos)} trending repos")
