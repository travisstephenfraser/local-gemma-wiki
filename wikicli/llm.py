"""Thin client for LM Studio's OpenAI-compatible server (stdlib only).

Everything the model sees is assembled by the harness and passed in `messages`;
this module only moves bytes and turns transport failures into readable errors.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from .config import Config


class ModelError(Exception):
    pass


@dataclass
class Reply:
    text: str
    model: str
    seconds: float
    prompt_tokens: int
    completion_tokens: int
    reasoning_tokens: int = 0


def _post(cfg: Config, route: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{cfg.endpoint}{route}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=cfg.timeout_s) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        if "not found" in detail.lower() or e.code == 404:
            raise ModelError(
                f"model {body.get('model')!r} is not available in LM Studio. "
                f"Download it with `lms get {body.get('model')}` or change [model] in config.toml."
            ) from e
        raise ModelError(f"LM Studio returned HTTP {e.code}: {detail}") from e
    except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
        raise ModelError(
            f"cannot reach the local model server at {cfg.endpoint} ({e}). "
            "Start it with `lms server start` (LM Studio > Developer > Start Server)."
        ) from e


def available(cfg: Config) -> list[str]:
    """Model ids the local server can serve; raises ModelError if it is down."""
    req = urllib.request.Request(f"{cfg.endpoint}/models")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return [m["id"] for m in json.loads(resp.read())["data"]]
    except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
        raise ModelError(
            f"cannot reach the local model server at {cfg.endpoint} ({e}). "
            "Start it with `lms server start`."
        ) from e


def chat(
    cfg: Config,
    messages: list[dict],
    *,
    model: str | None = None,
    schema: dict | None = None,
    temperature: float | None = None,
    max_tokens: int = 1200,
) -> Reply:
    body = {
        "model": model or cfg.chat_model,
        "messages": messages,
        "temperature": cfg.temperature if temperature is None else temperature,
        # Gemma 4 thinks before answering unless told not to, and reasoning tokens count
        # against max_tokens: with thinking on, the budget grows so the answer still fits.
        "max_tokens": max_tokens + (cfg.thinking_budget if cfg.thinking else 0),
        "reasoning_effort": "medium" if cfg.thinking else "none",
    }
    if schema is not None:
        body["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "out", "strict": True, "schema": schema},
        }
    t0 = time.perf_counter()
    data = _post(cfg, "/chat/completions", body)
    choice = data["choices"][0]
    if choice.get("finish_reason") == "length":
        raise ModelError(f"model output hit max_tokens={max_tokens} and was cut off; raise the limit")
    msg = choice["message"]
    usage = data.get("usage", {})
    return Reply(
        text=(msg.get("content") or "").strip(),
        model=data.get("model", cfg.chat_model),
        seconds=time.perf_counter() - t0,
        prompt_tokens=usage.get("prompt_tokens", 0),
        completion_tokens=usage.get("completion_tokens", 0),
        reasoning_tokens=(usage.get("completion_tokens_details") or {}).get("reasoning_tokens", 0),
    )


def chat_json(
    cfg: Config, messages: list[dict], schema: dict, **kw
) -> tuple[dict, Reply]:
    reply = chat(cfg, messages, schema=schema, **kw)
    try:
        return json.loads(reply.text), reply
    except json.JSONDecodeError as e:
        raise ModelError(f"model returned invalid JSON: {reply.text[:200]!r}") from e


def embed(cfg: Config, texts: list[str], batch: int = 64) -> list[list[float]]:
    out: list[list[float]] = []
    for i in range(0, len(texts), batch):
        data = _post(
            cfg,
            "/embeddings",
            {"model": cfg.embed_model, "input": texts[i : i + batch]},
        )
        out.extend(
            d["embedding"] for d in sorted(data["data"], key=lambda d: d["index"])
        )
    return out
