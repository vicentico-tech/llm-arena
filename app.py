import os

import gradio as gr
from dotenv import load_dotenv

load_dotenv()

from arena.prompts import ROLES  # noqa: E402
from arena.providers import available_models  # noqa: E402
from arena.runner import run_all  # noqa: E402

MAX_PROMPT_CHARS = 4000
MODELS = available_models()
SLOTS = max(len(MODELS), 1)


def compare(prompt: str, role: str, selected: list[str]):
    empty = [gr.update(visible=False, value="")] * SLOTS
    if not prompt.strip():
        raise gr.Error("Escribe un prompt.")
    if len(prompt) > MAX_PROMPT_CHARS:
        raise gr.Error(f"Prompt demasiado largo (máx. {MAX_PROMPT_CHARS} caracteres).")
    if not selected:
        raise gr.Error("Selecciona al menos un modelo.")

    results = run_all([MODELS[s] for s in selected], ROLES[role], prompt)

    rows = [
        [
            r.label,
            "error" if r.error else "ok",
            f"{r.ttft:.2f}" if r.ttft is not None else "-",
            f"{r.total:.2f}" if r.total is not None else "-",
            r.tokens,
            f"{r.tokens_per_s:.1f}" if r.tokens_per_s else "-",
        ]
        for r in results
    ]
    boxes = list(empty)
    for i, r in enumerate(results):
        boxes[i] = gr.update(visible=True, label=r.label, value=r.error or r.text)
    return [rows, *boxes]


with gr.Blocks(title="LLM Arena") as demo:
    gr.Markdown("# LLM Arena\nCompara modelos gratuitos con el mismo prompt.")
    if not MODELS:
        gr.Markdown("⚠️ No hay modelos disponibles. Configura al menos una API key en `.env`.")
    with gr.Row():
        role = gr.Dropdown(list(ROLES), value="Libre", label="Rol (system prompt)")
        selected = gr.CheckboxGroup(list(MODELS), value=list(MODELS)[:2], label="Modelos")
    prompt = gr.Textbox(lines=5, label="Prompt", max_length=MAX_PROMPT_CHARS)
    btn = gr.Button("Comparar", variant="primary")
    table = gr.Dataframe(
        headers=["Modelo", "Estado", "TTFT (s)", "Total (s)", "Tokens*", "Tokens/s*"],
        interactive=False,
    )
    with gr.Row():
        boxes = [gr.Textbox(visible=False, lines=14, interactive=False) for _ in range(SLOTS)]
    gr.Markdown("*Tokens aproximados (chunks de streaming).")
    btn.click(compare, [prompt, role, selected], [table, *boxes], concurrency_limit=2)

if __name__ == "__main__":
    auth = None
    if os.getenv("APP_USER") and os.getenv("APP_PASSWORD"):
        auth = (os.environ["APP_USER"], os.environ["APP_PASSWORD"])
    demo.queue(max_size=10).launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"),
        server_port=int(os.getenv("PORT", "7860")),
        auth=auth,
    )
