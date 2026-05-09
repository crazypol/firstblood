"""
AI-powered insights generator for daily trend reports.

Uses LLM to generate human-readable summaries and insights
from the daily statistics.
"""

from config import settings
from src.models import DailyReport, RepoData


def _build_insight_prompt(report: DailyReport) -> str:
    """Build prompt for daily insight generation."""
    top_3 = report.top_repos[:3]
    top_3_str = "\n".join(
        f"- {r.name}: {r.description[:80]} (⭐+{r.stars_today}/天, {r.ai_category})"
        for r in top_3
    )

    cat_trends = "\n".join(
        f"- {c.name}: {c.count} projects ({c.percentage}%)"
        for c in report.categories[:6]
    )

    new_entries = ""
    if report.new_entrants:
        new_entries = "\n值得关注的新项目:\n" + "\n".join(
            f"- {r.name}: {r.description[:80]}"
            for r in report.new_entrants[:3]
        )

    return f"""You are an AI open-source trend analyst. Write a concise daily trend summary in Chinese.

Today's AI open-source data ({report.date}):
- Total AI projects: {report.total_ai_repos}

Top projects:
{top_3_str}

Category breakdown:
{cat_trends}
{new_entries}

Write 2-3 paragraphs:
1. What's hot today (top categories and why)
2. Notable new projects or trends
3. What developers should pay attention to

Keep it under 200 characters. Be specific - mention actual project names and numbers."""


def _build_repo_summary_prompt(repo: RepoData) -> str:
    """Build prompt for a single repo summary."""
    topics_str = ", ".join(repo.topics) if repo.topics else "N/A"
    return f"""Write a very concise 1-sentence Chinese summary of this GitHub repo:

Name: {repo.name}
Description: {repo.description[:200]}
Topics: {topics_str}
Language: {repo.language}
Stars: {repo.stars:,}

Explain what it does and why it matters in the AI ecosystem. Keep under 80 characters."""


def generate_insight(report: DailyReport) -> str:
    """Generate daily trend insight using LLM.

    Falls back to a template-based summary if LLM unavailable.
    """
    if not settings.anthropic_api_key and not settings.openai_api_key:
        return _generate_fallback_insight(report)

    try:
        return _generate_llm_insight(report)
    except Exception:
        return _generate_fallback_insight(report)


def generate_repo_summary(repo: RepoData) -> str:
    """Generate a short Chinese summary for a repo."""
    if not settings.anthropic_api_key and not settings.openai_api_key:
        return ""

    try:
        return _generate_llm_repo_summary(repo)
    except Exception:
        return ""


def _generate_llm_insight(report: DailyReport) -> str:
    """Generate insight using LLM."""
    if settings.llm_provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            temperature=0.3,
            messages=[
                {"role": "user", "content": _build_insight_prompt(report)}
            ],
        )
        return response.content[0].text.strip()

    else:
        from openai import OpenAI
        client = OpenAI(
            api_key=settings.openai_api_key or settings.anthropic_api_key,
            base_url=settings.openai_base_url or None,
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=500,
            temperature=0.3,
            messages=[
                {"role": "user", "content": _build_insight_prompt(report)}
            ],
        )
        return response.choices[0].message.content.strip()


def _generate_llm_repo_summary(repo: RepoData) -> str:
    """Generate single repo summary using LLM."""
    if settings.llm_provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=150,
            temperature=0.3,
            messages=[
                {"role": "user", "content": _build_repo_summary_prompt(repo)}
            ],
        )
        return response.content[0].text.strip()

    else:
        from openai import OpenAI
        client = OpenAI(
            api_key=settings.openai_api_key or settings.anthropic_api_key,
            base_url=settings.openai_base_url or None,
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=150,
            temperature=0.3,
            messages=[
                {"role": "user", "content": _build_repo_summary_prompt(repo)}
            ],
        )
        return response.choices[0].message.content.strip()


def _generate_fallback_insight(report: DailyReport) -> str:
    """Generate a template-based insight when LLM is unavailable."""
    top_cat = report.categories[0] if report.categories else None
    top_repo = report.top_repos[0] if report.top_repos else None

    parts = []
    if top_cat:
        parts.append(
            f"今日 AI 开源趋势中，{top_cat.name} 分类最为活跃，"
            f"共 {top_cat.count} 个项目（占比 {top_cat.percentage}%）。"
        )
    if top_repo:
        parts.append(
            f"最热门项目为 {top_repo.name}，"
            f"今日新增 {top_repo.stars_today} Star。"
        )
    if report.new_entrants:
        names = [r.name for r in report.new_entrants[:3]]
        parts.append(f"值得关注的新入库项目：{'、'.join(names)}。")

    return " ".join(parts)
