"""Calibration: retrieval checked against facts established outside the pipeline.

Unit tests prove the pieces agree with each other; these prove retrieval finds
passages a human located by hand in the originals (tests/questions.toml).
Keyword-only on purpose so it runs without LM Studio.
"""

from __future__ import annotations

import tomllib
from dataclasses import replace

import pytest

from wikicli import config
from wikicli.config import ROOT
from wikicli.index import Index

QUESTIONS = tomllib.loads((ROOT / "tests" / "questions.toml").read_text())["question"]


@pytest.fixture(scope="module")
def raw_index(tmp_path_factory):
    cfg = config.load()
    cfg = replace(
        cfg, state_dir=tmp_path_factory.mktemp("state"), index_globs=["raw/**/*.md"]
    )
    return Index.build(cfg, embed=False, log=lambda *a: None)


def test_known_answer_anchor_ranks_first(raw_index):
    hits = raw_index.bm25("REPLAY_CAPACITY replay buffer 2,500,000")
    best = raw_index.passages[int(hits.argmax())]
    assert best.path == "raw/assign2/README.md"
    assert "`REPLAY_CAPACITY`, 5,000 to 2,500,000" in best.text


def test_unrelated_queries_retrieve_different_projects(raw_index):
    # a descent must not read as a climb: different questions -> different sources
    tops = {
        q: raw_index.passages[int(raw_index.bm25(q).argmax())].path
        for q in (
            "row level security policy contacts",
            "replay buffer DQN",
            "nanoGPT negation corpus",
        )
    }
    assert len(set(tops.values())) == 3, tops


@pytest.mark.parametrize(
    "q", [q for q in QUESTIONS if q["expect_evidence"]], ids=lambda q: q["id"]
)
def test_expected_evidence_exists_verbatim_in_raw(q, raw_index):
    # guards the eval itself: an answer key pointing at text that is not there scores nothing
    for snippet in q["expect_evidence"]:
        assert any(snippet in p.text for p in raw_index.passages), snippet


def test_vault_integrity():
    """Obsidian-facing checks on the real vault: H1 == filename, links and source refs resolve."""
    import re

    vault = ROOT / "vault"
    notes = [p for p in vault.rglob("*.md") if "raw" not in p.relative_to(vault).parts]
    names = {p.stem for p in notes}
    problems = []
    for p in notes:
        text = p.read_text()
        h1 = re.search(r"^# (.+)$", text, re.M)
        if p.name != "index.md" and (not h1 or h1.group(1) != p.stem):
            problems.append(f"{p.name}: heading does not match filename")
        problems += [f"{p.name}: broken [[{l}]]" for l in re.findall(r"\[\[([^\]|#]+)", text) if l not in names]
        for link in re.findall(r"\]\(((?:\.\./)*raw/[^)]+)\)", text):
            if not (p.parent / link.replace("%20", " ")).resolve().exists():
                problems.append(f"{p.name}: missing source {link}")
    assert not problems, problems
