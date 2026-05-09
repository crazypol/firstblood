from __future__ import annotations

"""
Rules-based AI domain classifier.

Classifies GitHub repositories into AI sub-domains using
keyword matching on repository name, description, and topics.
"""

import re
from typing import Optional

from src.models import RepoData


# Keywords mapping: category -> list of (priority, keyword_patterns)
# Priority: 1 = topic match, 2 = name match, 3 = description match
CATEGORY_RULES: dict[str, list[tuple[int, list[str]]]] = {
    "llm": [
        (1, ["llm", "large-language-model", "large-language-models"]),
        (2, ["llm", "gpt", "chatgpt", "claude", "gemini", "deepseek",
              "qwen", "mistral", "llama", "phi-", "olmo", "falcon",
              "yi-", "baichuan", "tongyi", "chatglm"]),
        (3, ["large language model", "llm", "foundation model",
              "language model", "transformer-based"]),
    ],
    "agent": [
        (1, ["agent", "ai-agent", "agents", "multi-agent"]),
        (2, ["agent", "agents", "function-calling", "tool-use",
              "tooluse", "autogpt", "babyagi", "superagent", "agentic"]),
        (3, ["ai agent", "autonomous agent", "agent framework",
              "agentic", "multi-agent", "tool use", "function calling"]),
    ],
    "rag": [
        (1, ["rag", "retrieval-augmented"]),
        (2, ["rag", "ragflow", "vector-store", "vector-db", "embedding",
              "chromadb", "weaviate", "pinecone", "qdrant", "milvus",
              "langchain", "llamaindex", "haystack"]),
        (3, ["retrieval augmented", "retrieval-augmented", "vector database",
              "vector store", "semantic search", "knowledge base",
              "document qa", "document-qa"]),
    ],
    "mcp": [
        (1, ["mcp", "model-context-protocol", "modelcontextprotocol"]),
        (2, ["mcp", "model-context-protocol", "mcp-server", "mcp-client"]),
        (3, ["model context protocol", "mcp protocol", "mcp server"]),
    ],
    "multimodal": [
        (1, ["multimodal", "multi-modal", "vision-language", "image-generation"]),
        (2, ["sdxl", "stable-diffusion", "dall-e", "midjourney", "flux",
              "whisper", "speech-to-text", "text-to-speech", "tts",
              "clip", "blip", "sam-", "segment-anything", "controlnet",
              "diffusion", "vqa", "visual-question"]),
        (3, ["multimodal", "multi-modal", "image generation", "text to image",
              "text-to-image", "speech recognition", "speech to text",
              "vision language", "visual question"]),
    ],
    "ai_tooling": [
        (1, ["ai-tools", "ai-toolkit", "dev-tools", "developer-tools"]),
        (2, ["copilot", "cline", "continue.dev", "aider", "open-interpreter",
              "screenpipe", "cursor", "windsurf", "codeium", "tabby",
              "ollama", "vllm", "triton-inference", "tensorrt",
              "mlx", "llamacpp", "llama.cpp", "ggml", "kobold"]),
        (3, ["developer tool", "ai coding", "code assistant",
              "local inference", "model serving", "llm inference"]),
    ],
    "ai_infra": [
        (1, ["ai-infrastructure", "mlops", "llmops", "ai-ops"]),
        (2, ["kubeflow", "mlflow", "wandb", "weights-biases", "weightsandbiases",
              "dvc", "determined-ai", "ray-", "bentoml", "triton",
              "jupyter", "langfuse", "phoenix", "arize"]),
        (3, ["ml platform", "model deployment", "model monitoring",
              "experiment tracking", "model registry", "ai infrastructure"]),
    ],
    "ai_safety": [
        (1, ["ai-safety", "alignment", "ai-security", "ai-governance"]),
        (2, ["guardrails", "giskard", "rebuff", "llm-guard", "purple-labs",
              "inspect-ai", "evals", "prompt-injection"]),
        (3, ["ai safety", "alignment", "red teaming", "prompt injection",
              "jailbreak", "content safety", "ai governance", "responsible ai"]),
    ],
    "ml_platform": [
        (1, ["machine-learning", "deep-learning", "ml-platform"]),
        (2, ["pytorch", "tensorflow", "jax", "scikit-learn", "xgboost",
              "lightgbm", "transformers", "huggingface", "hugging-face",
              "datasets", "accelerate", "timm", "fastai"]),
        (3, ["machine learning", "deep learning", "ml framework",
              "neural network", "training framework"]),
    ],
    "reasoning": [
        (1, ["reasoning", "chain-of-thought", "thinking"]),
        (2, ["chain-of-thought", "cot", "reasoning", "thinking",
              "tree-of-thought", "graph-of-thought", "langchain"]),
        (3, ["chain of thought", "reasoning model", "step-by-step reasoning",
              "logical reasoning"]),
    ],
    "code_generation": [
        (1, ["code-generation", "code-gen", "codegen"]),
        (2, ["codegen", "codestral", "code llama", "codeqwen", "starcoder",
              "codegeex", "tabnine", "continue", "aider"]),
        (3, ["code generation", "code completion", "program synthesis",
              "code assistant"]),
    ],
}


def _normalize(text: str) -> str:
    """Lowercase and strip text for matching."""
    return text.lower().strip()


def _matches_any(text: str, patterns: list[str]) -> bool:
    """Check if any pattern matches in the text."""
    t = _normalize(text)
    for p in patterns:
        p_lower = p.lower()
        if p_lower in t:
            return True
    return False


def classify_repo(repo: RepoData) -> tuple[str, list[str], float]:
    """Classify a repository into an AI sub-domain.

    Uses multi-level keyword matching:
      Level 1 (high confidence): repository topics
      Level 2 (medium): repository name
      Level 3 (lower): description

    Returns:
        Tuple of (primary_category, subcategories, confidence_score)
    """
    scores: dict[str, float] = {}
    name = f"{repo.author}/{repo.name}" if repo.name else ""
    desc = repo.description or ""
    topics = [t.lower().replace("-", " ") for t in repo.topics]

    for category, rules in CATEGORY_RULES.items():
        for priority, keywords in rules:
            weight = {1: 1.0, 2: 0.6, 3: 0.3}[priority]

            if priority == 1:
                # Match against topics
                for topic in topics:
                    if _matches_any(topic, keywords):
                        scores[category] = scores.get(category, 0) + weight

            elif priority == 2:
                # Match against repo name
                for part in name.lower().split("/"):
                    if _matches_any(part, keywords):
                        scores[category] = scores.get(category, 0) + weight

            elif priority == 3:
                # Match against description
                if _matches_any(desc, keywords):
                    scores[category] = scores.get(category, 0) + weight

    if not scores:
        return ("uncategorized", [], 0.0)

    # Sort by score, pick the best
    sorted_cats = sorted(scores.items(), key=lambda x: -x[1])
    primary = sorted_cats[0][0]
    total_score = sorted_cats[0][1]
    confidence = min(1.0, total_score / 3.0)

    # Subcategories: all categories with score > 0
    subcategories = [
        cat for cat, score in sorted_cats
        if score > 0 and cat != primary
    ]

    return (primary, subcategories[:3], confidence)


def batch_classify(repos: list[RepoData]) -> list[RepoData]:
    """Classify a list of repositories."""
    for repo in repos:
        category, subcategories, _ = classify_repo(repo)
        repo.ai_category = category
        repo.ai_subcategories = subcategories
    return repos
