"""Readable note names, frontmatter, and the files Obsidian shows.

Gemma proposes titles; this module decides the final filename. A name is 2-6
Title Case words with no hashes, dates, or IDs, and a canonical key
("row level security") catches near-duplicates before a second file appears.
"""

from __future__ import annotations

import re
from pathlib import Path

ILLEGAL = re.compile(r'[\\/:*?"<>|#^\[\]{}]')
MACHINE = re.compile(
    r"\b([0-9a-f]{8,}|\d{4}-\d{2}-\d{2}|chunk\s*\d+|task\s*\d+)\b", re.I
)
SMALL = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "vs",
}


class NameError_(ValueError):
    pass


def canonical(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
    return re.sub(r"\b(\w{4,}?)s\b", r"\1", s)  # crude singular: "Evals" == "Eval"


def clean_title(raw: str, max_words: int = 6) -> str:
    t = ILLEGAL.sub(" ", raw)
    t = MACHINE.sub(" ", t)
    t = re.sub(r"[_]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip(" .-")
    words = t.split(" ")[:max_words]
    out = []
    for i, w in enumerate(words):
        if w.isupper() or any(c.isupper() for c in w[1:]):
            out.append(w)  # keep acronyms / camelCase / "Q4_0" as written
        elif i and w.lower() in SMALL:
            out.append(w.lower())
        else:
            out.append(w[:1].upper() + w[1:])
    title = " ".join(out)
    if len(title) < 3:
        raise NameError_(f"unusable note title from model: {raw!r}")
    return title


def frontmatter(fields: dict) -> str:
    lines = ["---"]
    for k, v in fields.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            lines.extend(f"  - {_yaml(x)}" for x in v)
        else:
            lines.append(f"{k}: {_yaml(v)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def _yaml(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    s = str(v)
    return f'"{s}"' if re.search(r'[:#\[\]{},&*!|>\'"%@`]', s) or s != s.strip() else s


def read_frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    out: dict = {}
    key = None
    for line in text[4:end].splitlines():
        if line.startswith("  - ") and key:
            out.setdefault(key, []).append(line[4:].strip().strip('"'))
        elif ":" in line:
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip().strip('"')
            out[key] = val if val else []
    return out


class NoteRegistry:
    """Every note already in wiki/, keyed by canonical name, so new titles reuse old files."""

    def __init__(self, wiki_dir: Path):
        self.wiki_dir = wiki_dir
        self.by_key: dict[str, Path] = {}
        for f in wiki_dir.rglob("*.md"):
            self.by_key[canonical(f.stem)] = f
            for alias in read_frontmatter(f.read_text()).get("aliases", []) or []:
                self.by_key.setdefault(canonical(alias), f)

    def find(self, title: str) -> Path | None:
        return self.by_key.get(canonical(title))

    def claim(self, title: str, folder: str) -> Path:
        existing = self.find(title)
        if existing:
            return existing
        path = self.wiki_dir / folder / f"{title}.md"
        self.by_key[canonical(title)] = path
        return path

    def names(self, folder: str | None = None) -> list[str]:
        return sorted(
            {
                p.stem
                for p in self.by_key.values()
                if folder is None or p.parent.name == folder
            }
        )
