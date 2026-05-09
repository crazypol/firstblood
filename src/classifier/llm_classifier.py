from __future__ import annotations

"""
LLM-based classifier for AI domain classification.

Used as a second pass to improve accuracy for repos where
the rules-based classifier has low confidence.
"""

from typing import Optional

from config import settings
from src.models import RepoData

CATEGORIES = [
    "llm", "agent", "rag", "mcp", "multimodal", "ai_tooling",
    "ai_infra", "ai_safety", "ml_platform", "reasoning", "code_generation",
]

CATEGORY_LABELS = {
    "llm": "LLM / Foundation Models",
    "agent": "AI Agent / Autonomous Agent",
    "rag": "RAG / Retrieval Augmented Generation",
    "mcp": "MCP / Model Context Protocol",
    "multimodal": "Multimodal / Vision / Speech / Image",
    "ai_tooling": "AI Developer Tools",
    "ai_infra": "AI Infrastructure / MLOps",
    "ai_safety": "AI Safety / Alignment / Security",
    "ml_platform": "ML Platform / Deep Learning Framework",
    "reasoning": "Reasoning / Chain-of-Thought",
    "code_generation": "Code Generation / AI Coding",
}


def _build_classification_prompt(repo: RepoData) -> str:
    """Build the prompt for LLM classification."""
    topics_str = ", ".join(repo.topics) if repo.topics else "none"
    categories_str = "\n".join(
        f"  - {k}: {v}" for k, v in CATEGORY_LABELS.items()
    )

    return f"""Classify this GitHub repository into one or more AI categories.

Repository: {repo.name}
Description: {repo.description[:200]}
Topics: {topics_str}
Language: {repo.language}

Available categories:
{categories_str}

Return ONLY a JSON object:
{{"category": "best_match", "subcategories": ["sub1", "sub2"], "confidence": 0.95}}"""


def classify_with_llm(repo: RepoData) -> tuple[str, list[str], float]:
    """Classify a repo using an LLM API.

    Falls back to rules-based result if LLM is unavailable.
    """
    if settings.classifier_rules_only:
        raise NotImplementedError("LLM classifier disabled by config")

    provider = settings.llm_provider

    if provider == "anthropic":
        return _classify_anthropic(repo)
    elif provider == "openai":
        return _classify_openai(repo)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def _classify_anthropic(repo: RepoData) -> tuple[str, list[str], float]:
    """Classify using Anthropic Claude API."""
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed")

    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    prompt = _build_classification_prompt(repo)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}],
    )

    return _parse_llm_response(response.content[0].text)


def _classify_openai(repo: RepoData) -> tuple[str, list[str], float]:
    """Classify using OpenAI-compatible API."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package not installed")

    client = OpenAI(
        api_key=settings.openai_api_key or settings.anthropic_api_key,
        base_url=settings.openai_base_url or None,
    )
    prompt = _build_classification_prompt(repo)

    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=200,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}],
    )

    return _parse_llm_response(response.choices[0].message.content or "{}")


def _parse_llm_response(text: str) -> tuple[str, list[str], float]:
    """Parse the JSON response from the LLM."""
    import json
    import re

    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if not json_match:
        return ("uncategorized", [], 0.0)

    try:
        data = json.loads(json_match.group())
        category = data.get("category", "uncategorized")
        subcategories = data.get("subcategories", [])
        confidence = float(data.get("confidence", 0.5))
        return (category, subcategories[:3], confidence)
    except (json.JSONDecodeError, ValueError, TypeError):
        return ("uncategorized", [], 0.0)
