"""Check that an answer's citations point at passages that actually say the claim.

Cheap, deterministic checks per sentence:
  - every [S#] refers to a passage that was retrieved
  - every number in the sentence appears in a cited passage (the check that
    catches the classic fluent-but-wrong answer: right source, wrong figure)
  - enough of the sentence's content words appear in the cited passages
Optionally, a second Gemma call judges each (sentence, passages) pair.

A citation is not proof by itself; this is a filter that says where to look.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from . import llm
from .config import Config
from .index import Hit, tokens

CITE = re.compile(r"\[(S\d+(?:\s*,\s*S\d+)*)\]")
NUM = re.compile(r"(?<![A-Za-z])\d[\d,]*(?:\.\d+)?")
INSUFFICIENT = "INSUFFICIENT EVIDENCE"
# a sentence reporting missing evidence is not a claim that needs a citation
ABSENCE = re.compile(r"insufficient evidence|(do|does) not (contain|state|mention|include|say|report)|not (in|covered by) the (passages|sources)|no (passage|source)s? (states?|mentions?|contains?)", re.I)

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["supported", "partial", "unsupported"]},
        "reason": {"type": "string"},
    },
    "required": ["verdict", "reason"],
}


@dataclass
class ClaimCheck:
    sentence: str
    cited: list[str]
    status: str  # supported | weak | unsupported | uncited | bad-citation
    missing_numbers: list[str] = field(default_factory=list)
    overlap: float = 0.0
    judge: str | None = None


@dataclass
class Report:
    insufficient: bool
    claims: list[ClaimCheck]

    @property
    def ok(self) -> bool:
        return self.insufficient or (
            bool(self.claims) and all(c.status == "supported" for c in self.claims)
        )

    def summary(self) -> str:
        if self.insufficient:
            return "model reported insufficient evidence"
        counts: dict[str, int] = {}
        for c in self.claims:
            counts[c.status] = counts.get(c.status, 0) + 1
        return ", ".join(f"{n} {s}" for s, n in sorted(counts.items())) or "no claims"

    def to_dict(self) -> dict:
        return {
            "insufficient": self.insufficient,
            "ok": self.ok,
            "summary": self.summary(),
            "claims": [asdict(c) for c in self.claims],
        }


def sentences(text: str) -> list[str]:
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.M)
    # sentence ends, but not after "Ms." / "Dr." / "e.g." / "i.e."
    parts = re.split(r"(?<!\b[A-Z][a-z]\.)(?<!\be\.g\.)(?<!\bi\.e\.)(?<=[.!?])\s+(?=[A-Z(\"'`*])|\n+",
                     text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 3]


def _norm_num(n: str) -> str:
    return n.replace(",", "").rstrip(".")


def check(
    answer: str, hits: list[Hit], cfg: Config | None = None, judge: bool = False
) -> Report:
    if answer.strip().upper().startswith(INSUFFICIENT):
        return Report(True, [])
    # Judge by meaning, not only the exact token: an answer made entirely of
    # "the passages do not mention X" sentences is an insufficient-evidence answer.
    parts = sentences(answer)
    if parts and all(ABSENCE.search(CITE.sub("", s)) for s in parts):
        return Report(True, [])
    ids = {f"S{i}": h.passage for i, h in enumerate(hits, 1)}
    claims: list[ClaimCheck] = []
    for s in sentences(answer):
        cited = [c.strip() for m in CITE.finditer(s) for c in m.group(1).split(",")]
        bare = CITE.sub("", s).strip()
        if not cited:
            factual = bool(NUM.search(bare)) or len(bare.split()) >= 6
            if factual and not ABSENCE.search(bare):
                claims.append(ClaimCheck(bare, [], "uncited"))
            continue
        if any(c not in ids for c in cited):
            claims.append(ClaimCheck(bare, cited, "bad-citation"))
            continue
        evidence = "\n".join(ids[c].text for c in cited)
        ev_nums = {_norm_num(n) for n in NUM.findall(evidence)}
        missing = [n for n in NUM.findall(bare) if _norm_num(n) not in ev_nums]
        st = set(tokens(bare))
        overlap = len(st & set(tokens(evidence))) / len(st) if st else 1.0
        status = (
            "supported"
            if not missing and overlap >= 0.5
            else ("weak" if not missing and overlap >= 0.3 else "unsupported")
        )
        cc = ClaimCheck(bare, cited, status, missing, round(overlap, 2))
        # Lexical checks are a cheap filter; the judge only settles the ambiguous ones.
        # Missing numbers are never overruled: a wrong figure stays wrong.
        if judge and cfg is not None and cc.status != "supported" and not missing:
            cc.judge = _judge(cfg, bare, evidence)
            cc.status = {"supported": "supported", "partial": "weak"}.get(cc.judge, "unsupported")
        claims.append(cc)
    return Report(False, claims)


def _judge(cfg: Config, claim: str, evidence: str) -> str:
    msgs = [
        {
            "role": "system",
            "content": "You check whether a claim is fully stated by the evidence. "
            "Judge only from the evidence text.",
        },
        {"role": "user", "content": f"EVIDENCE:\n{evidence}\n\nCLAIM: {claim}"},
    ]
    try:
        data, _ = llm.chat_json(
            cfg, msgs, JUDGE_SCHEMA, temperature=0.0, max_tokens=200
        )
        return data["verdict"]
    except llm.ModelError:
        return "error"
