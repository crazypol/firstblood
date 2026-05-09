from __future__ import annotations

"""
GitHub API client for supplementing repository data.

Used to fetch additional details that aren't available from
the Trending page (e.g., exact topics, star history, etc.).
"""

import time
from typing import Optional

import httpx

from config import settings
from src.models import RepoData


class GitHubAPIClient:
    """Thin client for GitHub REST API."""

    BASE_URL = settings.github_api_base

    def __init__(self, token: str = ""):
        token = token or settings.github_token
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Trend-Daily/1.0",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers=headers,
            follow_redirects=True,
            timeout=settings.request_timeout,
        )
        self.remaining_requests = 5000
        self.reset_time = 0

    def _check_rate_limit(self):
        """Check rate limit and wait if needed."""
        if self.remaining_requests < 10:
            wait = max(0, self.reset_time - time.time()) + 1
            if wait > 0:
                time.sleep(wait)

    def _update_rate_limit(self, response):
        """Update rate limit info from response headers."""
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        if remaining:
            self.remaining_requests = int(remaining)
        if reset:
            self.reset_time = int(reset)

    def get_repo_details(self, full_name: str) -> dict | None:
        """Fetch repository details from GitHub API.

        Args:
            full_name: "owner/repo" format

        Returns:
            Repository data dict, or None on failure
        """
        self._check_rate_limit()
        try:
            resp = self.client.get(f"/repos/{full_name}")
            self._update_rate_limit(resp)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 403:
                time.sleep(60)
                return None
            return None
        except httpx.HTTPError:
            return None

    def get_repo_topics(self, full_name: str) -> list[str]:
        """Fetch topics for a repository.

        Uses the GitHub Topics API.
        """
        self._check_rate_limit()
        try:
            resp = self.client.get(
                f"/repos/{full_name}/topics",
                headers={"Accept": "application/vnd.github.mercy-preview+json"},
            )
            self._update_rate_limit(resp)
            if resp.status_code == 200:
                return resp.json().get("names", [])
            return []
        except httpx.HTTPError:
            return []

    def enhance_repo(self, repo: RepoData) -> RepoData:
        """Enhance a RepoData with additional info from API.

        Supplements topics and other fields not available from
        the trending page.
        """
        details = self.get_repo_details(repo.name)
        if not details:
            return repo

        # Supplement topics if trending page didn't have them
        if not repo.topics:
            topics = self.get_repo_topics(repo.name)
            if topics:
                repo.topics = topics

        # Supplement description if trending was empty
        if not repo.description and details.get("description"):
            repo.description = details["description"]

        # More accurate star/fork counts
        repo.stars = max(repo.stars, details.get("stargazers_count", 0))
        repo.forks = max(repo.forks, details.get("forks_count", 0))

        return repo

    def close(self):
        self.client.close()
