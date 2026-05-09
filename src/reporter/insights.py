"""
AI-powered insights generator for daily trend reports.

Uses LLM to generate human-readable summaries and insights
from the daily statistics.
"""

from config import settings
from src.models import DailyReport, RepoData

CATEGORY_LABELS = {
    "llm": "大语言模型",
    "agent": "AI Agent",
    "rag": "RAG检索增强",
    "mcp": "MCP协议",
    "multimodal": "多模态",
    "ai_tooling": "AI开发工具",
    "ai_infra": "AI基础设施",
    "ai_safety": "AI安全",
    "ml_platform": "ML平台",
    "reasoning": "推理",
    "code_generation": "代码生成",
}


def _build_insight_prompt(report: DailyReport) -> str:
    """Build a simple, reliable prompt for daily insight."""
    top_3 = report.top_repos[:3]
    top_lines = "\n".join(
        f"{i+1}. {r.name} (+{r.stars_today}⭐) - {r.description[:60]}"
        for i, r in enumerate(top_3)
    )

    cat_lines = "\n".join(
        f"- {CATEGORY_LABELS.get(c.name, c.name)}: {c.count}个 ({c.percentage}%)"
        for c in report.categories[:5]
    )

    new_lines = ""
    if report.new_entrants:
        new_lines = "首次上榜:\n" + "\n".join(
            f"- {r.name}" for r in report.new_entrants[:3]
        )

    return f"""Analyze today's GitHub AI trending data and write 2-3 short sentences in Chinese.

Data ({report.date}):
AI项目总数: {report.total_ai_repos}

热门项目:
{top_lines}

分类分布:
{cat_lines}

{new_lines}

Write in Chinese, be specific with names and numbers. Under 150 characters."""


def _build_repo_summary_prompt(repo: RepoData) -> str:
    """Build a prompt for detailed repo summary."""
    desc = repo.description[:200] if repo.description else "暂无描述"
    return f"""用2-3句纯文本介绍这个GitHub仓库（不要markdown格式）：它是什么项目？核心功能是什么？技术亮点是什么？

{repo.name}: {desc}"""


def generate_insight(report: DailyReport) -> str:
    """Generate daily trend insight."""
    if not settings.anthropic_api_key and not settings.openai_api_key:
        return _generate_fallback_insight(report)

    try:
        result = _generate_llm_insight(report)
        if result and len(result) > 10:
            return result
    except Exception:
        pass

    return _generate_fallback_insight(report)


def generate_repo_summary(repo: RepoData) -> str:
    """Generate a short summary for a repo."""
    if not settings.anthropic_api_key and not settings.openai_api_key:
        return ""

    try:
        result = _generate_llm_repo_summary(repo)
        if result and len(result) > 5:
            return result
    except Exception:
        pass

    return ""


def _generate_llm_insight(report: DailyReport) -> str:
    """Generate insight using LLM via OpenAI-compatible API."""
    if settings.llm_provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=settings.llm_model or "claude-sonnet-4-20250514",
            max_tokens=300,
            temperature=0.3,
            messages=[{"role": "user", "content": _build_insight_prompt(report)}],
        )
        return response.content[0].text.strip()

    from openai import OpenAI
    client = OpenAI(
        api_key=settings.openai_api_key or settings.anthropic_api_key,
        base_url=settings.openai_base_url or None,
    )
    response = client.chat.completions.create(
        model=settings.llm_model or "deepseek-chat",
        max_tokens=300,
        temperature=0.3,
        messages=[{"role": "user", "content": _build_insight_prompt(report)}],
    )
    content = (response.choices[0].message.content or "").strip()
    return content


def _generate_llm_repo_summary(repo: RepoData) -> str:
    """Generate single repo summary using LLM."""
    if settings.llm_provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=settings.llm_model or "claude-sonnet-4-20250514",
            max_tokens=500,
            temperature=0.3,
            messages=[{"role": "user", "content": _build_repo_summary_prompt(repo)}],
        )
        return response.content[0].text.strip()

    from openai import OpenAI
    client = OpenAI(
        api_key=settings.openai_api_key or settings.anthropic_api_key,
        base_url=settings.openai_base_url or None,
    )
    response = client.chat.completions.create(
        model=settings.llm_model or "deepseek-chat",
        max_tokens=500,
        temperature=0.3,
        messages=[{"role": "user", "content": _build_repo_summary_prompt(repo)}],
    )
    content = (response.choices[0].message.content or "").strip()
    return content


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
