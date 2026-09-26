"""Split Markdown into heading-aware passages that remember where they came from.

A passage never crosses a heading, keeps table rows whole (it splits on lines,
not words), and records its file path, heading trail, and 1-based line range so
a citation can point at `raw/assign2/README.md:86-97`.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


@dataclass
class Passage:
    id: str
    path: str  # vault-relative, e.g. raw/assign2/README.md
    kind: str  # "source" (raw/) or "note" (wiki/ and everything else)
    section: str  # heading trail, "Setup > Hyperparameters"
    start: int  # first line, 1-based
    end: int  # last line, inclusive
    text: str

    @property
    def cite(self) -> str:
        where = f"{self.path}:{self.start}-{self.end}"
        return f"{where} § {self.section}" if self.section else where

    def to_dict(self) -> dict:
        return asdict(self)


def _strip_frontmatter(lines: list[str]) -> int:
    """Index of the first body line (skips a leading YAML block)."""
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return i + 1
    return 0


def split(
    path: str, text: str, chunk_words: int = 220, overlap_lines: int = 2, kind: str | None = None
) -> list[Passage]:
    kind = kind or ("source" if path.startswith("raw/") else "note")
    lines = text.splitlines()
    body_start = _strip_frontmatter(lines)

    # 1. sections: runs of lines under the same heading trail
    trail: list[tuple[int, str]] = []
    sections: list[tuple[str, int, list[str]]] = []  # (trail, first_line_no, lines)
    cur: list[str] = []
    cur_start = body_start + 1
    in_fence = False

    def flush() -> None:
        if any(l.strip() for l in cur):
            sections.append((" > ".join(t for _, t in trail), cur_start, cur.copy()))

    for i, line in enumerate(lines[body_start:], start=body_start + 1):
        if FENCE.match(line):
            in_fence = not in_fence
        m = None if in_fence else HEADING.match(line)
        if m:
            flush()
            level = len(m.group(1))
            trail = [(lv, t) for lv, t in trail if lv < level] + [(level, m.group(2))]
            cur, cur_start = [line], i
        else:
            cur.append(line)
    flush()

    # 2. windows inside each section, cut on line boundaries
    out: list[Passage] = []
    for section, first, sec_lines in sections:
        i = 0
        while i < len(sec_lines):
            words, j = 0, i
            while j < len(sec_lines) and (words < chunk_words or j == i):
                words += len(sec_lines[j].split())
                j += 1
            window = sec_lines[i:j]
            body = "\n".join(window).strip()
            if body:
                start, end = first + i, first + j - 1
                pid = hashlib.sha1(f"{path}:{start}:{end}:{body}".encode()).hexdigest()[
                    :12
                ]
                out.append(Passage(pid, path, kind, section, start, end, body))
            if j >= len(sec_lines):
                break
            # overlap only when the window is long enough; wide table rows would otherwise
            # step one line at a time and flood the index with near-duplicate passages
            i = j - overlap_lines if j - overlap_lines > i + overlap_lines else j
    return out
