from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Project paths
    project_root: str = str(Path(__file__).parent)
    data_dir: str = str(Path(__file__).parent / "data")

    # GitHub
    github_token: str = ""
    github_trending_url: str = "https://github.com/trending"
    github_api_base: str = "https://api.github.com"

    # AI / LLM
    llm_provider: str = "anthropic"  # "anthropic" | "openai"
    llm_model: str = "deepseek-chat"  # model name (mimo-v2.5-pro, deepseek-chat, etc.)
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = ""

    # Classification
    classifier_rules_only: bool = False  # True = skip LLM classification

    # Reporting
    report_language: str = "zh"  # "zh" | "en" | "both"
    top_n_repos: int = 30

    # Notification
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    wework_webhook_url: str = ""

    # Pipeline
    max_repos_per_run: int = 200
    request_timeout: int = 30
    retry_times: int = 3

    model_config = {"env_prefix": "AI_TREND_", "env_file": ".env"}


settings = Settings()
