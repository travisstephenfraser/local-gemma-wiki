"""Unit tests: no model, no network. Run with `pytest`."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from wikicli import config, ingest
from wikicli.chunking import split
from wikicli.citations import check
from wikicli.index import Hit, Index, RetrievalError
from wikicli.notes import canonical, clean_title

DOC = """---
title: x
---
# Project

Intro line one.

## Settings

| name | value |
|---|---|
| lr | 0.0001 |
| buffer | 2,500,000 |

## Results

The score rose from 492 to 1,342.
"""


# ---------------------------------------------------------------- chunking
def test_passages_cite_real_line_ranges():
    lines = DOC.splitlines()
    for p in split("raw/x/README.md", DOC, chunk_words=8, overlap_lines=0):
        assert "\n".join(lines[p.start - 1 : p.end]).strip() == p.text
        assert p.kind == "source"


def test_passages_never_cross_headings_and_keep_table_rows_whole():
    ps = split("raw/x/README.md", DOC, chunk_words=1000)
    assert [p.section for p in ps] == [
        "Project",
        "Project > Settings",
        "Project > Results",
    ]
    assert "| buffer | 2,500,000 |" in ps[1].text


def test_frontmatter_is_not_indexed():
    assert all("title: x" not in p.text for p in split("wiki/Note.md", DOC))


# ---------------------------------------------------------------- naming
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("class4-gpu task 1 c8d92e24fd", "Class4-gpu"),
        ("row level security", "Row Level Security"),
        ("Notes from 2026-09-25 on RLS", "Notes From on RLS"),
        (
            "a very long title that keeps going on and on",
            "A Very Long Title That Keeps",
        ),
    ],
)
def test_clean_title_strips_machine_ids_and_caps_words(raw, expected):
    assert clean_title(raw) == expected


def test_canonical_merges_near_duplicates():
    assert canonical("Row-Level Security") == canonical("row level security")
    assert canonical("Evals") == canonical("Eval")


# ---------------------------------------------------------------- citations
def _hits(*texts):
    from wikicli.chunking import Passage

    return [
        Hit(Passage(f"p{i}", "raw/a.md", "source", "S", 1, 2, t), 0.1, 1, 1, 1.0, 0.5)
        for i, t in enumerate(texts)
    ]


EVIDENCE = _hits(
    "REPLAY_CAPACITY was raised from 5,000 to 2,500,000 transitions.",
    "Learning rate stayed at 0.0001.",
)


def test_supported_claim_passes():
    r = check("The replay capacity was raised from 5,000 to 2,500,000 [S1].", EVIDENCE)
    assert r.ok and r.claims[0].status == "supported"


def test_wrong_number_is_flagged_even_with_a_real_citation():
    # the flattering failure: right source, fluent sentence, wrong figure
    r = check("The replay capacity was raised from 5,000 to 1,000,000 [S1].", EVIDENCE)
    assert not r.ok
    assert r.claims[0].status == "unsupported" and r.claims[0].missing_numbers == [
        "1,000,000"
    ]


def test_citation_to_a_passage_that_was_not_retrieved():
    assert (
        check("The learning rate was 0.0001 [S7].", EVIDENCE).claims[0].status
        == "bad-citation"
    )


def test_uncited_factual_sentence_is_flagged():
    r = check(
        "The learning rate was 0.0001 [S2]. The agent scored 9,999 points.", EVIDENCE
    )
    assert [c.status for c in r.claims] == ["supported", "uncited"]


def test_insufficient_evidence_is_recognised():
    r = check("INSUFFICIENT EVIDENCE: no source records a grade.", EVIDENCE)
    assert r.insufficient and r.ok and not r.claims


def test_empty_answer_is_not_ok():
    assert not check("", EVIDENCE).ok


# ---------------------------------------------------------------- ingest render
@pytest.fixture
def tmp_cfg(tmp_path: Path):
    (tmp_path / "vault" / "raw" / "proj").mkdir(parents=True)
    (tmp_path / "vault" / "wiki").mkdir()
    cfg = config.load()
    return replace(
        cfg,
        vault=tmp_path / "vault",
        state_dir=tmp_path / "state",
        runs_dir=tmp_path / "runs",
    )


def _seed(cfg, sid: str, concepts: list[dict], role="project write-up"):
    (cfg.vault / sid).write_text("original text")
    data = {
        "project_title": "Demo Project",
        "role": role,
        "summary": "It does a thing. More.",
        "key_facts": ["Fact one."],
        "concepts": concepts,
        "source": sid,
        "model": "test",
    }
    p = ingest.extraction_path(cfg, sid)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data))
    m = ingest.load_manifest(cfg)
    m["sources"][sid] = {"sha256": "x", "model": "test"}
    m["projects"]["proj"] = {"title": "Demo Project"}
    return m


C = {
    "name": "Replay Buffer",
    "kind": "concept",
    "definition": "Stores experience.",
    "in_this_source": "Used.",
}


def test_render_is_idempotent_and_drops_schema_echoes(tmp_cfg):
    echo = {
        "name": "Definition",
        "kind": "concept",
        "definition": "A general sentence.",
        "in_this_source": "x",
    }
    m = _seed(tmp_cfg, "raw/proj/README.md", [C, echo])
    report = ingest.render(tmp_cfg, m)
    assert any("Definition" in line and "echoes" in line for line in report)
    first = {p: p.read_text() for p in tmp_cfg.vault.rglob("*.md")}
    ingest.render(tmp_cfg, m)
    assert {p: p.read_text() for p in tmp_cfg.vault.rglob("*.md")} == first
    names = sorted(
        p.relative_to(tmp_cfg.vault / "wiki").as_posix()
        for p in (tmp_cfg.vault / "wiki").rglob("*.md")
    )
    assert names == ["Concepts/Replay Buffer.md", "Projects/Demo Project.md"]


def test_hand_edited_note_is_never_overwritten(tmp_cfg):
    m = _seed(tmp_cfg, "raw/proj/README.md", [C])
    ingest.render(tmp_cfg, m)
    note = tmp_cfg.wiki_dir / "Projects" / "Demo Project.md"
    note.write_text(note.read_text() + "\nMy correction.\n")
    report = ingest.render(tmp_cfg, m)
    assert "My correction." in note.read_text()
    assert any("edited by hand" in line for line in report)


def test_project_note_links_concept_and_source(tmp_cfg):
    m = _seed(tmp_cfg, "raw/proj/README.md", [C])
    ingest.render(tmp_cfg, m)
    text = (tmp_cfg.wiki_dir / "Projects" / "Demo Project.md").read_text()
    assert "[[Replay Buffer]]" in text and "../../raw/proj/README.md" in text
    assert text.count("It does a thing.") == 1  # lead summary is not repeated


def test_read_only_profile_refuses_ingest(tmp_cfg):
    with pytest.raises(PermissionError):
        ingest.run(replace(tmp_cfg, writable=False), tmp_cfg.raw_dir)


# ---------------------------------------------------------------- degeneracy guard
def test_index_that_reads_itself_raises(tmp_cfg):
    from wikicli.chunking import Passage

    same = "database security policy reinforcement learning replay frontend layout phone training loss experiment"
    ps = [Passage(f"p{i}", "raw/a.md", "source", "", i, i, same) for i in range(5)]
    with pytest.raises(RetrievalError, match="degenerate"):
        Index(tmp_cfg, ps, None, {}).check_not_degenerate()


def test_wide_table_rows_do_not_create_near_duplicate_passages():
    row = "| " + " | ".join(["0.12 / 0.34 / 0.56 / 0.78"] * 30) + " |"  # one row > chunk_words
    doc = "# Results\n\n" + "\n".join([row] * 6)
    ps = split("raw/x.md", doc, chunk_words=220, overlap_lines=2)
    assert all(b.start > a.end for a, b in zip(ps, ps[1:]))  # short windows never overlap


def test_reporting_missing_evidence_is_not_an_uncited_claim():
    r = check("The rate was 0.0001 [S2]. The passages do not contain how the custom LLM performed.", EVIDENCE)
    assert [c.status for c in r.claims] == ["supported"]


def test_leaked_template_tokens_are_not_search_queries():
    from wikicli.modes import LEAK
    assert LEAK.search("']} </s><s>[thought]The user is asking about")
    assert not LEAK.search("Contacts tracker row level security policy")
    assert not LEAK.search("nanoGPT learning rate 0.0001 [custom LLM]")


def test_abbreviations_do_not_split_claims():
    r = check("The Ms. Pac-Man agent used a capacity of 2,500,000 [S1].", EVIDENCE)
    assert len(r.claims) == 1 and r.claims[0].missing_numbers == []


def test_absence_only_answer_counts_as_insufficient():
    r = check("The provided passages do not mention a grade received on the assignment [S1, S2].", EVIDENCE)
    assert r.insufficient
    # ...but an answer with a real claim plus an absence note is not
    assert not check("The rate was 0.0001 [S2]. The passages do not mention a grade.", EVIDENCE).insufficient


def test_number_cited_to_the_wrong_passage_is_unsupported():
    # the number exists in S1, but the sentence cites S2
    r = check("The capacity was 2,500,000 [S2].", EVIDENCE)
    assert r.claims[0].status == "unsupported" and r.claims[0].missing_numbers == ["2,500,000"]


def test_two_hop_searches_again_with_the_value_hop_one_found(tmp_cfg, monkeypatch):
    from wikicli import modes
    from wikicli.chunking import Passage
    ps = [Passage("a", "raw/dqn.md", "source", "Settings", 1, 2, "The DQN learning rate was 0.0001."),
          Passage("b", "raw/llm.md", "source", "Results", 1, 2, "At 0.0001 nanoGPT barely learned: 4-8/48."),
          *[Passage(f"n{i}", "raw/dqn.md", "source", "Other", 10 + i, 10 + i, f"DQN learning rate note {i}") for i in range(8)]]
    idx = Index(replace(tmp_cfg, top_k=2), ps, None, {})
    cfg = replace(tmp_cfg, top_k=2, query_planning=False, two_hop=True)
    monkeypatch.setattr(modes.Index, "load", classmethod(lambda cls, c: idx))
    monkeypatch.setattr(modes, "check_gap", lambda c, q, h: {
        "complete": False, "missing": "language model result", "referenced_value": "0.0001", "follow_up_query": "nanoGPT result"})
    seen = {}
    def fake_chat(c, messages, **kw):
        seen["prompt"] = messages[-1]["content"]
        from wikicli.llm import Reply
        return Reply("The DQN used 0.0001 [S2]. The language model scored 4-8/48 [S1].", "m", 0.1, 10, 5)
    monkeypatch.setattr(modes.llm, "chat", fake_chat)
    q = "What learning rate did the DQN use, and how did the language model do at that same rate?"
    one_hop = modes.ask(replace(cfg, two_hop=False), q)
    assert "raw/llm.md" not in [h.passage.path for h in one_hop.hits]  # hop 1 alone misses it
    r = modes.ask(cfg, q)
    assert r.hop2 == {"missing": "language model result", "query": "nanoGPT result 0.0001"}  # value appended by the harness
    assert "raw/llm.md" in [h.passage.path for h in r.hits]
    assert "barely learned" in seen["prompt"]


def test_clean_query_cuts_leaked_reasoning_but_keeps_the_useful_prefix():
    from wikicli.modes import clean_query
    assert clean_query("PM growth gaps project notes}}thought}I don't have access") == "PM growth gaps project notes"
    assert clean_query("']} </s><s>[thought]The user is asking") is None
    assert clean_query("row level security policy") == "row level security policy"
