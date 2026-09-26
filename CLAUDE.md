# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`wiki`: a personal-wiki CLI and RAG harness over a **local** Gemma 4 model served by LM Studio (Assignment 4, Haas AI-build class). The README is the grading surface; `feed/` (gitignored) holds the assignment brief, and `docs/PLAN.md` records decisions and their reasons.

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'   # one dependency: numpy
lms server start                        # LM Studio must be serving on :1234
.venv/bin/wiki status                   # server, models, loaded quantization, memory, index, network
.venv/bin/wiki index                    # rebuild passages + embeddings (vectors.npy is gitignored)
.venv/bin/wiki ingest [path] [--force]  # extract (Gemma) + render the vault; unchanged sources skip
.venv/bin/wiki search|ask|chat ...
.venv/bin/wiki eval --judge [--label X] [--planning on|off] [--two-hop on|off]   # 4 ask tests -> evidence/ask/<label>/
.venv/bin/wiki eval --modes             # chat/search/ask boundary checks -> evidence/modes/
.venv/bin/wiki eval --judge --ladder google/gemma-4-e2b google/gemma-4-e4b google/gemma-4-26b-a4b-qat
.venv/bin/wiki --profile brain ...      # same harness, read-only, over Travis's private vault

.venv/bin/pytest -q                                   # hermetic: no model, no network
.venv/bin/pytest -q tests/test_harness.py -k two_hop  # single test
.venv/bin/python scripts/apply_review.py && .venv/bin/wiki ingest   # apply review corrections, re-render
scripts/offline_demo.sh                 # only runs with the network OFF; Travis runs it
```

## Architecture

`cli.py` parses the command and dispatches; each mode in `modes.py` builds its **own** context, and the separation between them is the point of the assignment:

- **search**: `Index.search` only (BM25 + EmbeddingGemma cosine, RRF-fused). No chat-model call; degrades to BM25 if embeddings are down.
- **ask**: no history, no persona. `plan_queries` (1-3 sub-queries) → `retrieve` over **`raw/` originals only** (`evidence_globs`) → `check_gap` two-hop (the harness, not the model, appends the referenced value to the follow-up query) → `prompts/wiki-instructions.md` + numbered `[S#]` passages → `citations.check`.
- **chat**: `prompts/persona.md` + rolling history; a router call (`prompts/router.md`) decides per turn whether to retrieve. Profiles can swap persona/router (`persona-brain.md`).

Ingest (`ingest.py`) is two-stage so re-ingest cannot duplicate: **extract** (Gemma JSON per changed source, cached in `state/<profile>/extractions/`, keyed by SHA-256 in `manifest.json`) then **render** (deterministic: `wiki/Projects/` one note per `raw/<folder>`, `wiki/Concepts|Tools/` merged across sources, `index.md`, `Source Catalog.md`). Render tracks each file's hash in the manifest: hand-edited notes are kept, orphaned notes deleted. Project titles live in `manifest.projects`.

Human review edits the **extraction JSON**, not the notes: add entries to `evidence/review/corrections.json`, run `scripts/apply_review.py`, re-render. Reviewed extractions are skipped even by `--force`.

`config.toml` holds models, retrieval knobs, and profiles (vault, state dir, writable, index/exclude/evidence globs, persona). `sources.toml` is provenance for every `raw/` file. `tests/questions.toml` is the answer key and must stay outside the vault.

## Rules that are easy to break

- `vault/raw/` is evidence: never edit those files. Fix wiki errors through the review layer.
- Do not change `tests/questions.toml` expectations after seeing results; failures are documented, and every superseded run is moved to `evidence/ask/history/` rather than deleted.
- Gemma 4 **thinks unless told not to**, and reasoning tokens count against `max_tokens` (an empty or cut-off answer means this). `llm.chat` sends `reasoning_effort: "none"` unless `model.thinking = true`, which also adds `thinking_budget`.
- Model-written search queries can contain leaked template tokens (`</s><s>[thought]`, `}}`); always pass them through `modes.clean_query`.
- `AskResult` has defaulted fields after `prompt_tokens`; construct it with keywords past that point.
- macOS is case-insensitive: a case-only note rename is handled in `ingest.write_all`; keep it.
- Anything that measures (citation check, eval scoring, degeneracy guard) must be able to fail: `test_calibration.py` anchors retrieval to known passages in the real vault, and the README's falsification shows the number check is load-bearing.
- MLX models ignore `lms load -c`; the harness bounds context by what it sends (about 2,500 prompt tokens per ask).
