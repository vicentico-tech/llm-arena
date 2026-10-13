"""Registro de modelos gratuitos. Verifica nombres y límites en la web de cada proveedor: cambian a menudo."""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    label: str
    base_url: str
    api_key_env: str | None  # None = no requiere clave (Ollama)
    model: str
    enabled_env: str | None = None  # variable que debe existir para habilitarlo


MODELS: list[ModelSpec] = [
    ModelSpec("Groq · GPT-OSS 20B", "https://api.groq.com/openai/v1", "GROQ_API_KEY", "openai/gpt-oss-20b"),
    ModelSpec("Groq · GPT-OSS 120B", "https://api.groq.com/openai/v1", "GROQ_API_KEY", "openai/gpt-oss-120b"),
    ModelSpec("Groq · Qwen3.8 27B", "https://api.groq.com/openai/v1", "GROQ_API_KEY", "qwen/qwen3.8-27b"),
    ModelSpec("Groq · Llama promp guard", "https://api.groq.com/openai/v1", "GROQ_API_KEY", "meta-llama/llama-prompt-guard-2-22m"),
    ModelSpec(
        "Gemini · Flash",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
        "GEMINI_API_KEY",
        "gemini-3.8-flash",
    ),
    ModelSpec(
        "OpenRouter · Nemotron (free)",
        "https://openrouter.ai/api/v1",
        "OPENROUTER_API_KEY",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
    ),
    ModelSpec("Ollama · Qwen2.5 Coder (local)", "", None, "qwen2.5-coder:3b", enabled_env="OLLAMA_BASE_URL"),
    ModelSpec("Ollama · Llama 3.2 (local)", "", None, "llama3.2:3b", enabled_env="OLLAMA_BASE_URL"),
]


def is_available(spec: ModelSpec) -> bool:
    if spec.enabled_env and not os.getenv(spec.enabled_env):
        return False
    if spec.api_key_env and not os.getenv(spec.api_key_env):
        return False
    return True


def available_models() -> dict[str, ModelSpec]:
    return {m.label: m for m in MODELS if is_available(m)}
