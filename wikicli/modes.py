"""The three interaction modes. Each builds its own context; none shares state.

search: retrieval only. No model call, no answer.
ask:    fresh context every time -> retrieve (raw/ originals only) -> research rules + passages -> Gemma
        -> citation check. Never sees chat history or the persona.
chat:   persona + rolling conversation. A router call decides per turn whether
        to retrieve; retrieved passages are attached to that turn only.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from . import citations, llm
from .config import Config, prompt
from .index import Hit, Index

ROUTER_SCHEMA = {
    "type": "object",
    "properties": {
        "retrieve": {"type": "boolean"},
        "query": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": ["retrieve", "query", "reason"],
}


def render_passages(hits: list[Hit]) -> str:
    """The exact evidence block Gemma sees: numbered, labeled with path, lines, section."""
    return "\n\n".join(
        f"[S{i}] {h.passage.cite}\n{h.passage.text}" for i, h in enumerate(hits, 1)
    )


def log_run(cfg: Config, record: dict) -> Path:
    cfg.runs_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    f = cfg.runs_dir / f"{stamp}-{record['mode']}.json"
    f.write_text(json.dumps(record, indent=2, default=str) + "\n")
    return f


def hit_dict(i: int, h: Hit) -> dict:
    return {
        "id": f"S{i}",
        "cite": h.passage.cite,
        "path": h.passage.path,
        "kind": h.passage.kind,
        "rrf": round(h.score, 4),
        "bm25_rank": h.bm25_rank,
        "vector_rank": h.vec_rank,
        "text": h.passage.text,
    }


# ---------------------------------------------------------------- search
def search(cfg: Config, query: str, k: int | None = None) -> tuple[list[Hit], str]:
    return Index.load(cfg).search(query, k or cfg.top_k)


# ---------------------------------------------------------------- ask
@dataclass
class AskResult:
    question: str
    hits: list[Hit]
    method: str
    answer: str
    report: citations.Report
    model: str
    seconds: float
    retrieval_seconds: float
    prompt_tokens: int
    queries: list[str] = field(default_factory=list)
    thinking: bool = False
    reasoning_tokens: int = 0
    hop2: dict | None = None
    messages: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "mode": "ask",
            "execution": "local",
            "question": self.question,
            "model": self.model,
            "retrieval": self.method,
            "search_queries": self.queries,
            "two_hop": self.hop2,
            "retrieval_seconds": round(self.retrieval_seconds, 2),
            "passages": [hit_dict(i, h) for i, h in enumerate(self.hits, 1)],
            "answer": self.answer,
            "citation_check": self.report.to_dict(),
            "generation_seconds": round(self.seconds, 2),
            "prompt_tokens": self.prompt_tokens,
            "thinking": self.thinking,
            "reasoning_tokens": self.reasoning_tokens,
        }


LEAK = re.compile(r"</?s>|<\|?[a-z_]+\|?>|\[/?thought\]|[{}\[\]]{2}")

def clean_query(q: str) -> str | None:
    """Cut a model-written search query at the first leaked template/reasoning token."""
    m = LEAK.search(q)
    q = (q[: m.start()] if m else q).strip(" ,.;:'\"")
    return q if len(q.split()) >= 2 else None


PLAN_SCHEMA = {
    "type": "object",
    "properties": {"queries": {"type": "array", "items": {"type": "string"}}},
    "required": ["queries"],
}


def plan_queries(cfg: Config, question: str) -> list[str]:
    """One small Gemma call: split a question into 1-3 search queries."""
    data, _ = llm.chat_json(
        cfg,
        [
            {"role": "system", "content": prompt("query-planner.md")},
            {"role": "user", "content": question},
        ],
        PLAN_SCHEMA,
        temperature=0.0,
        max_tokens=200,
    )
    # Leaked chat-template or reasoning tokens ("]} </s><s>[thought]...") would make planning
    # look successful while it silently searches for garbage; clean_query cuts them off.
    return [q for q in (clean_query(x) for x in data["queries"]) if q][:3]


def retrieve(idx: Index, queries: list[str], k: int, kinds: tuple[str, ...] | None = None) -> tuple[list[Hit], str]:
    """Search each query, then interleave the ranked lists so every sub-question gets slots."""
    ranked = []
    method = ""
    for q in queries:
        hits, method = idx.search(q, k, kinds)
        ranked.append(hits)
    merged: dict[str, Hit] = {}
    for rank in range(k):
        for hits in ranked:
            if rank < len(hits) and len(merged) < k:
                merged.setdefault(hits[rank].passage.id, hits[rank])
    return list(merged.values()), method


GAP_SCHEMA = {
    "type": "object",
    "properties": {"complete": {"type": "boolean"}, "missing": {"type": "string"},
                   "referenced_value": {"type": "string"}, "follow_up_query": {"type": "string"}},
    "required": ["complete", "missing", "referenced_value", "follow_up_query"],
}


def check_gap(cfg: Config, question: str, hits: list[Hit]) -> dict:
    """One small Gemma call: do these passages cover every part of the question?"""
    data, _ = llm.chat_json(
        cfg,
        [{"role": "system", "content": prompt("gap-check.md")},
         {"role": "user", "content": f"PASSAGES:\n\n{render_passages(hits)}\n\nQUESTION: {question}"}],
        GAP_SCHEMA, temperature=0.0, max_tokens=200,
    )
    return data


def ask(cfg: Config, question: str, *, judge: bool = False) -> AskResult:
    t0 = time.perf_counter()
    idx = Index.load(cfg)
    queries = [question] + (plan_queries(cfg, question) if cfg.query_planning else [])
    # Evidence is the unchanged originals only; generated notes are for browsing and chat.
    hits, method = retrieve(idx, queries, cfg.top_k, kinds=("source",))
    if cfg.query_planning:
        method += f" · query planning ({len(queries) - 1} sub-queries)"
    hop2 = None
    if cfg.two_hop and hits:
        # Hop 2: a question like "...at that same learning rate" can't be searched until
        # hop 1 has found the rate. Search again with the value only when something is missing.
        gap = check_gap(cfg, question, hits)
        follow = gap["follow_up_query"].strip()
        value = gap["referenced_value"].strip()
        if value and value not in follow:  # the harness, not the model, carries the value over
            follow = f"{follow} {value}"
        if not gap["complete"] and follow and not LEAK.search(follow):
            hop2 = {"missing": gap["missing"], "query": follow}
            queries.append(follow)
            hits, _ = retrieve(idx, [follow, *queries[:-1]], cfg.top_k, kinds=("source",))
            method += " · two-hop"
    rt = time.perf_counter() - t0
    if not hits:  # nothing matched at all: do not ask the model to improvise
        answer = "INSUFFICIENT EVIDENCE: no passage in the wiki matched this question."
        return AskResult(
            question,
            [],
            method,
            answer,
            citations.check(answer, []),
            "(not called)",
            0.0,
            rt,
            0,
            queries,
        )
    messages = [
        {"role": "system", "content": prompt("wiki-instructions.md")},
        {
            "role": "user",
            "content": f"PASSAGES:\n\n{render_passages(hits)}\n\nQUESTION: {question}",
        },
    ]
    try:
        reply = llm.chat(cfg, messages, temperature=0.0, max_tokens=1000)
    except llm.ModelError as e:  # small models occasionally loop at temperature 0; retry once
        if "cut off" not in str(e):
            raise
        reply = llm.chat(cfg, messages, temperature=0.3, max_tokens=1000)
    report = citations.check(reply.text, hits, cfg, judge=judge)
    return AskResult(
        question,
        hits,
        method,
        reply.text,
        report,
        reply.model,
        reply.seconds,
        rt,
        reply.prompt_tokens,
        queries,
        messages=messages,
        thinking=cfg.thinking,
        reasoning_tokens=reply.reasoning_tokens,
        hop2=hop2,
    )


# ---------------------------------------------------------------- chat
class ChatSession:
    HISTORY_WORDS = 1800  # rolling budget for past turns sent back to Gemma

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.persona = prompt(cfg.persona)
        self.router_rules = prompt(cfg.router)
        self.history: list[dict] = []
        self.last_hits: list[Hit] = []
        self.transcript: list[dict] = []
        self._index: Index | None = None

    @property
    def index(self) -> Index:
        if self._index is None:
            self._index = Index.load(self.cfg)
        return self._index

    def _recent(self) -> list[dict]:
        kept, words = [], 0
        for m in reversed(self.history):
            words += len(m["content"].split())
            if words > self.HISTORY_WORDS and kept:
                break
            kept.append(m)
        return list(reversed(kept))

    def route(self, user: str) -> dict:
        recent = "\n".join(
            f"{m['role']}: {m['content'][:300]}" for m in self.history[-4:]
        )
        msgs = [
            {"role": "system", "content": self.router_rules},
            {
                "role": "user",
                "content": f"RECENT CONVERSATION:\n{recent or '(none)'}\n\nNEW MESSAGE: {user}",
            },
        ]
        data, _ = llm.chat_json(
            self.cfg, msgs, ROUTER_SCHEMA, temperature=0.0, max_tokens=150
        )
        return data

    def turn(self, user: str) -> dict:
        t0 = time.perf_counter()
        decision = self.route(user)
        hits: list[Hit] = []
        if decision["retrieve"]:
            query = clean_query(decision["query"]) or user
            decision["query"] = query
            hits, _ = self.index.search(query, self.cfg.chat_top_k)
        self.last_hits = hits
        system = self.persona
        if hits:
            system += (
                "\n\nPASSAGES retrieved from the wiki for this message only "
                "(cite as [S#] when you use them):\n\n" + render_passages(hits)
            )
        else:
            system += "\n\nNo wiki passages were retrieved for this message."
        messages = [
            {"role": "system", "content": system},
            *self._recent(),
            {"role": "user", "content": user},
        ]
        reply = llm.chat(self.cfg, messages, temperature=0.5, max_tokens=900)
        self.history += [
            {"role": "user", "content": user},
            {"role": "assistant", "content": reply.text},
        ]
        report = citations.check(reply.text, hits) if hits else None
        rec = {
            "user": user,
            "router": decision,
            "passages": [hit_dict(i, h) for i, h in enumerate(hits, 1)],
            "reply": reply.text,
            "model": reply.model,
            "seconds": round(time.perf_counter() - t0, 2),
            "citation_check": report.to_dict() if report else None,
            "history_messages_sent": len(messages) - 2,
        }
        self.transcript.append(rec)
        return rec

    def save_last(self, drafts_dir: Path) -> Path | None:
        """Explicit /save: the last reply becomes a draft OUTSIDE the vault, never evidence."""
        last = next(
            (m["content"] for m in reversed(self.history) if m["role"] == "assistant"),
            None,
        )
        if not last:
            return None
        drafts_dir.mkdir(parents=True, exist_ok=True)
        first = (
            re.sub(r"[^A-Za-z0-9 ]+", "", last.split("\n")[0])[:40].strip() or "draft"
        )
        f = drafts_dir / f"{time.strftime('%Y%m%d-%H%M')} {first}.md"
        f.write_text(
            f"<!-- chat draft, generated by {self.cfg.chat_model}; not source evidence -->\n\n{last}\n"
        )
        return f
