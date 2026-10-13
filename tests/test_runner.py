from types import SimpleNamespace

from arena.providers import ModelSpec, available_models
from arena.runner import run_all, run_one

SPEC = ModelSpec("fake", "http://x", "FAKE_KEY", "m")


def chunk(text):
    return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=text))])


class FakeClient:
    def __init__(self, behavior):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=behavior))


def ok_factory(_spec):
    return FakeClient(lambda **kw: iter([chunk("Hola"), chunk(" mundo")]))


def err_factory(_spec):
    def boom(**kw):
        raise RuntimeError("429 rate limit")

    return FakeClient(boom)


def test_run_one_collects_text_and_metrics():
    r = run_one(SPEC, "sys", "hi", ok_factory)
    assert r.text == "Hola mundo" and r.error is None
    assert r.tokens == 2 and r.ttft is not None and r.total >= r.ttft


def test_error_is_isolated():
    r = run_one(SPEC, "sys", "hi", err_factory)
    assert r.error and "429" in r.error


def test_run_all_one_failure_does_not_break_others():
    good = ModelSpec("good", "u", "K", "m")
    bad = ModelSpec("bad", "u", "K", "m")
    factory = lambda s: ok_factory(s) if s.label == "good" else err_factory(s)  # noqa: E731
    results = run_all([good, bad], "sys", "hi", factory)
    assert results[0].text and results[1].error


def test_provider_without_key_is_disabled(monkeypatch):
    for k in ("GROQ_API_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY", "OLLAMA_BASE_URL"):
        monkeypatch.delenv(k, raising=False)
    assert available_models() == {}
    monkeypatch.setenv("GROQ_API_KEY", "x")
    assert all(k.startswith("Groq") for k in available_models())
