"""Local retrieval: BM25 keyword search + embedding search, merged by RRF.

The index lives in the profile's state_dir (outside the vault):
  passages.jsonl   one Passage per line
  vectors.npy      float32 matrix aligned with passages.jsonl (optional)
  index.json       build metadata (embed model, passage hashes, timestamp)

Search needs no language model. If the embedding server is unreachable it
degrades to BM25 only and says so, rather than failing.
"""

from __future__ import annotations

import json
import math
import re
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import numpy as np

from . import llm
from .chunking import Passage, split
from .config import Config

TOKEN = re.compile(r"[a-z0-9_]+(?:[.\-/][a-z0-9_]+)*")
STOP = set(
    """a an and are as at be by for from has have how i in is it its of on or
that the this to was were what when where which who why will with did do does my me""".split()
)


class RetrievalError(Exception):
    pass


def tokens(text: str) -> list[str]:
    """Keeps compound tokens (0.0001, auth.user_id) and also their parts."""
    out: list[str] = []
    for t in TOKEN.findall(text.lower()):
        if t in STOP:
            continue
        out.append(t)
        parts = re.split(r"[.\-/]", t)
        if len(parts) > 1:
            out.extend(p for p in parts if p and p not in STOP)
    return out


def _files(cfg: Config) -> list[Path]:
    seen: dict[Path, None] = {}
    for g in cfg.index_globs:
        for f in sorted(cfg.vault.glob(g)):
            rel = f.relative_to(cfg.vault)
            if f.is_file() and not any(
                rel.match(x) or rel.full_match(x) for x in cfg.exclude_globs
            ):
                seen[f] = None
    return list(seen)


@dataclass
class Hit:
    passage: Passage
    score: float  # fused RRF score
    bm25_rank: int | None
    vec_rank: int | None
    bm25: float
    cosine: float | None


class Index:
    def __init__(
        self,
        cfg: Config,
        passages: list[Passage],
        vectors: np.ndarray | None,
        meta: dict,
    ):
        self.cfg, self.passages, self.vectors, self.meta = cfg, passages, vectors, meta
        self._docs = [Counter(tokens(f"{p.section}\n{p.text}")) for p in passages]
        self._len = [sum(d.values()) for d in self._docs]
        self._avg = (sum(self._len) / len(self._len)) if self._len else 0.0
        df: Counter = Counter()
        for d in self._docs:
            df.update(d.keys())
        n = len(passages)
        self._idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    # ---- build / load -------------------------------------------------
    @classmethod
    def build(cls, cfg: Config, *, embed: bool = True, log=print) -> "Index":
        passages: list[Passage] = []
        for f in _files(cfg):
            rel = f.relative_to(cfg.vault).as_posix()
            passages.extend(
                split(
                    rel,
                    f.read_text(errors="replace"),
                    cfg.chunk_words,
                    cfg.overlap_lines,
                    kind="source" if any(PurePosixPath(rel).full_match(g) for g in cfg.evidence_globs) else "note",
                )
            )
        if not passages:
            raise RetrievalError(
                f"no Markdown found under {cfg.vault} for globs {cfg.index_globs}"
            )
        vectors = None
        embed_note = "skipped"
        if embed:
            try:
                t0 = time.perf_counter()
                docs = [
                    f"{cfg.embed_doc_prefix}{p.section}\n{p.text}" for p in passages
                ]
                vectors = _normalise(np.array(llm.embed(cfg, docs), dtype=np.float32))
                embed_note = f"{cfg.embed_model} in {time.perf_counter() - t0:.1f}s"
            except llm.ModelError as e:
                log(f"  ! embeddings unavailable ({e}); index is keyword-only")
                embed_note = "unavailable"
        meta = {
            "built": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "profile": cfg.profile,
            "passages": len(passages),
            "files": len({p.path for p in passages}),
            "embed_model": cfg.embed_model if vectors is not None else None,
            "embeddings": embed_note,
        }
        idx = cls(cfg, passages, vectors, meta)
        idx.check_not_degenerate()
        idx.save()
        return idx

    def save(self) -> None:
        d = self.cfg.state_dir
        d.mkdir(parents=True, exist_ok=True)
        with open(d / "passages.jsonl", "w") as fh:
            for p in self.passages:
                fh.write(json.dumps(p.to_dict()) + "\n")
        if self.vectors is not None:
            np.save(d / "vectors.npy", self.vectors)
        elif (d / "vectors.npy").exists():
            (d / "vectors.npy").unlink()
        (d / "index.json").write_text(json.dumps(self.meta, indent=2))

    @classmethod
    def load(cls, cfg: Config) -> "Index":
        d = cfg.state_dir
        if not (d / "passages.jsonl").exists():
            raise RetrievalError(
                f"no index for profile {cfg.profile!r}. Run `wiki index` (or `wiki ingest`) first."
            )
        passages = [
            Passage(**json.loads(l))
            for l in (d / "passages.jsonl").read_text().splitlines()
        ]
        vectors = np.load(d / "vectors.npy") if (d / "vectors.npy").exists() else None
        meta = json.loads((d / "index.json").read_text())
        return cls(cfg, passages, vectors, meta)

    # ---- search ------------------------------------------------------
    def bm25(self, query: str, k1: float = 1.4, b: float = 0.75) -> np.ndarray:
        q = tokens(query)
        scores = np.zeros(len(self.passages), dtype=np.float32)
        for i, doc in enumerate(self._docs):
            s = 0.0
            for t in q:
                tf = doc.get(t)
                if tf:
                    s += (
                        self._idf[t]
                        * tf
                        * (k1 + 1)
                        / (tf + k1 * (1 - b + b * self._len[i] / self._avg))
                    )
            scores[i] = s
        return scores

    def cosine(self, query: str) -> np.ndarray | None:
        if self.vectors is None:
            return None
        try:
            qv = _normalise(
                np.array(
                    llm.embed(self.cfg, [f"{self.cfg.embed_query_prefix}{query}"]),
                    dtype=np.float32,
                )
            )
        except llm.ModelError:
            return None
        return self.vectors @ qv[0]

    def search(
        self, query: str, k: int, kinds: tuple[str, ...] | None = None
    ) -> tuple[list[Hit], str]:
        bm = self.bm25(query)
        cos = self.cosine(query)
        method = (
            "bm25+vector (RRF)"
            if cos is not None
            else "bm25 only (embeddings unavailable)"
        )
        allowed = [
            i for i, p in enumerate(self.passages) if kinds is None or p.kind in kinds
        ]
        bm_order = sorted((i for i in allowed if bm[i] > 0), key=lambda i: -bm[i])
        bm_rank = {i: r for r, i in enumerate(bm_order, 1)}
        vec_rank: dict[int, int] = {}
        if cos is not None:
            vec_rank = {
                i: r
                for r, i in enumerate(sorted(allowed, key=lambda i: -cos[i])[:50], 1)
            }
        fused = {
            i: sum(1 / (self.cfg.rrf_k + r[i]) for r in (bm_rank, vec_rank) if i in r)
            for i in set(bm_rank) | set(vec_rank)
        }
        top = sorted(fused, key=lambda i: -fused[i])[:k]
        hits = [
            Hit(
                self.passages[i],
                fused[i],
                bm_rank.get(i),
                vec_rank.get(i),
                float(bm[i]),
                None if cos is None else float(cos[i]),
            )
            for i in top
        ]
        return hits, method

    # ---- measurement sanity -----------------------------------------
    def check_not_degenerate(self) -> None:
        """Raise if unrelated probes retrieve the same passages: the index is reading itself."""
        probes = [
            "database security policy",
            "reinforcement learning replay",
            "frontend layout phone",
            "training loss experiment",
        ]
        tops = []
        for q in probes:
            s = self.bm25(q)
            tops.append(tuple(np.argsort(-s)[:3]) if s.max() > 0 else ())
        nonempty = [t for t in tops if t]
        if len(nonempty) >= 3 and len(set(nonempty)) == 1:
            raise RetrievalError(
                "degenerate index: unrelated probe queries all return the same top passages "
                f"{nonempty[0]}; check index_globs/exclude_globs"
            )


def _normalise(m: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(m, axis=1, keepdims=True)
    n[n == 0] = 1
    return m / n
