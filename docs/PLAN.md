# Assignment 4 Plan: Personal Wiki CLI on Local Gemma

Goal: a fresh repo that meets the brief (chat / ask / search / ingest / help over local Gemma,
offline, with evidence), then reuse the same harness read-only on the personal vault.

## Decisions made

| Decision | Choice | Why |
|---|---|---|
| Repo | Fresh, `assign4-wiki/` | Brief requires "your own"; old framework has no harness and a personal vault |
| Runtime | LM Studio server, OpenAI-compatible API, stdlib client | Already installed; JSON-schema output works |
| Models on disk | Gemma 4 E2B, E4B, 26B-A4B QAT (all MLX 4-bit), 31B | |
| Ingest model | 26B-A4B QAT | Batch job, quality over speed; E4B mislabeled roles and concepts (decided 2026-09-25) |
| Answer model | Smallest that passes the ladder (E2B / E4B / 26B) | Brief: justify the smallest model that works |
| Corpus | All 10 class files in `vault/raw/` (4 briefs, 4 READMEs, assign3 summary + evals README) | Checked for secrets; briefs are course material, README credits them (decided 2026-09-25) |
| Embeddings | EmbeddingGemma 300M (nomic kept as fallback) | All-Gemma stack; comparable retrieval on the tests |
| Retrieval | BM25 + vectors, RRF merge, heading-aware passages with line ranges | Citations point at `path:lines § section` |
| Ask retrieval fix | Query planning (Gemma splits question into 1-3 queries), behind a flag | Baseline misses T2 (paraphrase) and T3 (cross-source); keep baseline as evidence |
| Wiki shape | `Projects/` (one note per raw subfolder, section per source), `Concepts/`, `Tools/` | Brief says merge same-subject notes; first attempt produced duplicates |
| Ingest design | extract (Gemma to cached JSON) then render (deterministic) | Re-ingest idempotent; hand edits never overwritten |
| Personal vault | `--profile brain`, read-only, state in `~/.cache` | Same harness, nothing private in the repo |
| Project titles | Real names: Strada Networking Tracker, Ms Pac-Man DQN Agent, Custom nanoGPT Model, Class Signup Frontend | Match repos; set in manifest (decided 2026-09-25) |
| Raw paths | Mirror originals (`assign3/evals/README.md`, `assign3/experiments/summary.md`); provenance in `sources.toml` | evals README is course material (Rafael Alonso), not Travis's |
| Review | Four fact-check agents, corrections in `evidence/review/corrections.json`, applied to extraction JSON by `scripts/apply_review.py`; weak concepts replaced, all logged | 29 corrections / 187 claims, incl. 2 wrong numbers; Travis spot-checks 2 notes |
| Ask evidence | `raw/` originals only; wiki notes serve chat and browsing | Notes crowded originals out of T1 (v0 run kept) |
| Answer model | 26B-A4B QAT, thinking off | Only config passing 3/4; MoE latency ~ E4B (ladder) |
| Two-hop | Gap check; harness appends the referenced value to the follow-up query | Model dropped the value when asked in the prompt |
| Thinking | Off by default (`reasoning_effort: none`); ladder measures on vs off | Reasoning tokens silently ate `max_tokens`: root cause of every "runaway" error |

## Built so far

`wikicli/`: config, llm, chunking, index (+ degeneracy guard), ingest (two-stage), notes,
modes (search / ask / chat with router), citations (numbers + overlap + optional judge),
evals (cards, mode checks, ladder), sysinfo (network probe, memory), cli.
`tests/questions.toml`: 4 questions written before retrieval.

Findings so far (all kept under `evidence/ask/history/`): wiki notes crowd out originals (v0);
wide table rows made near-duplicate chunks; E4B planner leaked `</s><s>[thought]` as a query (now
rejected); baseline T3 answered a different question with every citation "supported"; Gemma 4
thinking consumed the token budget. MLX ignores `lms load -c` (KV cache grows on demand).

## Remaining steps (each ends with a check)

1. ✅ **Fix ingest wiring.** KeyError, context-length flag. Check: `wiki ingest` twice; second run
   says 0 extracted and `git status` shows no wiki changes.
2. ✅ **Ingest with 26B-A4B.** Add `ingest_model` to config; re-ingest all. Check: roles correct for
   all 10 sources; keep the E4B extraction as a before/after note for the README.
3. ✅ **Human review** (Travis spot-check pending). Read every project note against its source, fix errors by hand-editing
   (render keeps edits). Check: log each correction in `evidence/review.md`.
4. ✅ **Unit + calibration tests.** Chunk line ranges, title cleaning, citation checker flags a wrong
   number, retrieval anchor (T1 passage in top 3). Check: `pytest` green.
5. ✅ **Baseline eval** on 26B-A4B: 2/4 (T2, T3 retrieval misses) (`query_planning = false`). Check: cards in `evidence/ask/baseline/`, failures
   explained, not hidden.
6. ✅ **Query planning** 3/4 (T2 fixed) → **two-hop** retrieval (T3 retrieved; answer omits 4-8/48, judged partial) 3/4, rerun. Check: T2/T3 retrieval hits; before/after table.
7. ✅ **Mode checks** (`wiki eval --modes`). Check: capabilities without retrieval, "make that shorter"
   uses history, ask ignores the chat-only 9,999 claim.
8. ✅ **Model ladder** → 26B-A4B, thinking off (3/4, 1.9s, 20.7 GB); thinking adds 4-8x latency, no accuracy. E2B / E4B / 26B-A4B × thinking off/on, planning on, judge on. Check: `evidence/model-ladder.md`; config set to smallest passing.
9. ✅ **Brain profile smoke test** (3,673 passages / 274 pages, per-profile persona + evidence scope). Index the real vault read-only; one ask, one chat. Nothing committed.
10. ✅ **README** via `create-readme`: setup, specs, architecture trace, design choices, evidence links, reflection.

## Needs Travis

- Offline run: Wi-Fi off, restart CLI, `scripts/offline_demo.sh` (ingest, 4 asks, mode checks), record terminal.
  (I cannot do this: turning off the network cuts my own connection.)
- Three Obsidian screenshots: open note with source refs, index/page list, graph (`path:wiki/`).
- Confirm before creating and pushing the public GitHub repo.
