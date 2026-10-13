import os

from openai import OpenAI

from .providers import ModelSpec


def make_client(spec: ModelSpec) -> OpenAI:
    if spec.enabled_env == "OLLAMA_BASE_URL":
        base_url = os.environ["OLLAMA_BASE_URL"]
    else:
        base_url = spec.base_url
    api_key = os.getenv(spec.api_key_env) if spec.api_key_env else "ollama"
    return OpenAI(base_url=base_url, api_key=api_key, timeout=60.0, max_retries=0)
