"""Load config.toml and resolve the active profile into concrete paths."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"


class ConfigError(Exception):
    pass


@dataclass
class Config:
    profile: str
    vault: Path
    state_dir: Path
    runs_dir: Path
    writable: bool
    index_globs: list[str]
    exclude_globs: list[str]
    evidence_globs: list[str]
    persona: str
    router: str
    endpoint: str
    chat_model: str
    ingest_model: str
    embed_model: str
    embed_query_prefix: str
    embed_doc_prefix: str
    context_length: int
    temperature: float
    thinking: bool
    thinking_budget: int
    timeout_s: int
    chunk_words: int
    overlap_lines: int
    top_k: int
    chat_top_k: int
    rrf_k: int
    query_planning: bool
    two_hop: bool
    max_source_words: int

    @property
    def raw_dir(self) -> Path:
        return self.vault / "raw"

    @property
    def wiki_dir(self) -> Path:
        return self.vault / "wiki"


def _path(value: str) -> Path:
    p = Path(value).expanduser()
    return p if p.is_absolute() else ROOT / p


def load(
    profile: str | None = None,
    model: str | None = None,
    path: Path = ROOT / "config.toml",
) -> Config:
    if not path.exists():
        raise ConfigError(f"config not found: {path}")
    data = tomllib.loads(path.read_text())
    name = profile or data.get("default_profile", "class")
    profiles = data.get("profiles", {})
    if name not in profiles:
        raise ConfigError(
            f"unknown profile {name!r}; choose from: {', '.join(profiles)}"
        )
    p, m, r = profiles[name], data["model"], data["retrieval"]
    vault = _path(p["vault"])
    if not vault.is_dir():
        raise ConfigError(f"vault folder missing for profile {name!r}: {vault}")
    return Config(
        profile=name,
        vault=vault,
        state_dir=_path(p["state_dir"]),
        runs_dir=_path(p["runs_dir"]),
        writable=bool(p.get("writable", False)),
        index_globs=list(p.get("index_globs", ["**/*.md"])),
        exclude_globs=list(p.get("exclude_globs", [])),
        evidence_globs=list(p.get("evidence_globs", ["raw/**"])),
        persona=p.get("persona", "persona.md"),
        router=p.get("router", "router.md"),
        endpoint=m["endpoint"].rstrip("/"),
        chat_model=model or m["chat_model"],
        ingest_model=m.get("ingest_model", m["chat_model"]),
        embed_model=m["embed_model"],
        embed_query_prefix=m.get("embed_query_prefix", ""),
        embed_doc_prefix=m.get("embed_doc_prefix", ""),
        context_length=int(m.get("context_length", 32768)),
        temperature=float(m.get("temperature", 0.2)),
        thinking=bool(m.get("thinking", False)),
        thinking_budget=int(m.get("thinking_budget", 4000)),
        timeout_s=int(m.get("timeout_s", 300)),
        chunk_words=int(r["chunk_words"]),
        overlap_lines=int(r["overlap_lines"]),
        top_k=int(r["top_k"]),
        chat_top_k=int(r["chat_top_k"]),
        rrf_k=int(r["rrf_k"]),
        query_planning=bool(r.get("query_planning", False)),
        two_hop=bool(r.get("two_hop", False)),
        max_source_words=int(data.get("ingest", {}).get("max_source_words", 9000)),
    )


def prompt(name: str) -> str:
    """Instruction files are plain Markdown the harness loads per mode."""
    f = PROMPTS / name
    if not f.exists():
        raise ConfigError(f"instruction file missing: {f}")
    return f.read_text().strip()
