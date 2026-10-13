import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .client import make_client
from .providers import ModelSpec

MAX_TOKENS = 600


@dataclass
class Result:
    label: str
    text: str = ""
    error: str | None = None
    ttft: float | None = None  # segundos hasta el primer token
    total: float | None = None
    tokens: int = 0

    @property
    def tokens_per_s(self) -> float | None:
        if not self.total or not self.tokens:
            return None
        gen_time = self.total - (self.ttft or 0)
        return self.tokens / gen_time if gen_time > 0 else None


def run_one(spec: ModelSpec, system: str, prompt: str, client_factory: Callable = make_client) -> Result:
    res = Result(label=spec.label)
    start = time.perf_counter()
    try:
        client = client_factory(spec)
        stream = client.chat.completions.create(
            model=spec.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            max_tokens=MAX_TOKENS,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                if res.ttft is None:
                    res.ttft = time.perf_counter() - start
                res.text += delta
                res.tokens += 1  # aproximación: 1 chunk ≈ 1 token
    except Exception as e:  # un fallo (p.ej. 429) no debe romper a los demás
        res.error = f"{type(e).__name__}: {e}"
    res.total = time.perf_counter() - start
    return res


def run_all(specs: list[ModelSpec], system: str, prompt: str, client_factory: Callable = make_client) -> list[Result]:
    with ThreadPoolExecutor(max_workers=max(1, len(specs))) as pool:
        futures = [pool.submit(run_one, s, system, prompt, client_factory) for s in specs]
        return [f.result() for f in futures]
