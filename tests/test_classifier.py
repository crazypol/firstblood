from __future__ import annotations

"""Tests for the rules-based classifier."""

from src.models import RepoData
from src.classifier.rules import classify_repo, batch_classify


def _make_repo(
    name: str = "test/repo",
    desc: str = "",
    topics: list[str] | None = None,
) -> RepoData:
    return RepoData(
        rank=0,
        name=name,
        url=f"https://github.com/{name}",
        description=desc,
        topics=topics or [],
    )


def test_classify_llm_by_topic():
    repo = _make_repo(topics=["llm", "transformer"])
    category, subs, conf = classify_repo(repo)
    assert category == "llm"


def test_classify_agent_by_name():
    repo = _make_repo(name="awesome-ai-agent", topics=[])
    category, subs, conf = classify_repo(repo)
    assert category == "agent"


def test_classify_rag_by_description():
    repo = _make_repo(
        name="some/project",
        desc="A retrieval augmented generation framework for enterprise search",
    )
    category, subs, conf = classify_repo(repo)
    assert category == "rag"


def test_classify_mcp():
    repo = _make_repo(
        name="anthropic/mcp-server",
        topics=["mcp", "model-context-protocol"],
    )
    category, subs, conf = classify_repo(repo)
    assert category == "mcp"


def test_classify_uncategorized():
    repo = _make_repo(
        name="some/react-app",
        desc="A todo app built with React",
    )
    category, subs, conf = classify_repo(repo)
    assert category == "uncategorized"


def test_batch_classify():
    repos = [
        _make_repo(name="llm-project", desc="Large language model", topics=[]),
        _make_repo(name="gui-tool", desc="A simple GUI app", topics=[]),
    ]
    results = batch_classify(repos)
    assert results[0].ai_category == "llm"
    assert results[1].ai_category == "uncategorized"
