"""`wiki eval`: run the fixed question set and mode checks, write evidence cards.

Retrieval and answers are scored separately, as the brief asks:
  retrieval_hit  does each expected evidence snippet appear in a retrieved passage?
  behavior_ok    answered vs. INSUFFICIENT EVIDENCE, as expected
  facts_ok       expected exact strings (numbers, identifiers) appear in the answer
  citations_ok   every claim sentence passed the citation check
The expected answers live in tests/questions.toml, outside the vault.
"""

from __future__ import annotations

import json
import time
import tomllib
from pathlib import Path

from . import citations, llm, modes, sysinfo
from .config import ROOT, Config

QUESTIONS = ROOT / "tests" / "questions.toml"
EVIDENCE = ROOT / "evidence"


def slug(model: str) -> str:
    return model.split("/")[-1]


def environment(cfg: Config) -> dict:
    return {
        "execution": "local",
        "endpoint": cfg.endpoint,
        "network_online": sysinfo.network_online(),
        "model": sysinfo.model_info(cfg.chat_model),
        "embed_model": cfg.embed_model,
        "lmstudio_cli": sysinfo.lms_version(),
        "device": sysinfo.device(),
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }


def run_questions(cfg: Config, judge: bool = False, label: str | None = None, log=print) -> dict:
    qs = tomllib.loads(QUESTIONS.read_text())["question"]
    out_dir = EVIDENCE / "ask" / (label or slug(cfg.chat_model))
    out_dir.mkdir(parents=True, exist_ok=True)
    env = environment(cfg)
    rows = []
    for q in qs:
        log(f"  {q['id']}: {q['question']}")
        try:
            r = modes.ask(cfg, q["question"], judge=judge)
        except llm.ModelError as err:  # record the failure; never drop a test from the evidence
            r = modes.AskResult(q["question"], [], "error", f"ERROR: {err}",
                                citations.Report(False, []), cfg.chat_model, 0.0, 0.0, 0)
        paths = [h.passage.path for h in r.hits]
        expect_insufficient = q["expect_behavior"] == "insufficient_evidence"
        score = {
            # every expected evidence snippet must be inside some retrieved passage
            "retrieval_hit": all(
                any(snip in h.passage.text for h in r.hits) for snip in q["expect_evidence"]
            ),
            "behavior_ok": r.report.insufficient == expect_insufficient,
            "facts_ok": all(f in r.answer for f in q["expect_facts"]),
            "citations_ok": r.report.ok,
        }
        score["pass"] = all(score.values())
        card = {
            "test": q,
            "environment": env,
            "result": r.to_dict(),
            "score": score,
            "memory_footprint_gb": sysinfo.lmstudio_footprint_gb(),
        }
        (out_dir / f"{q['id']}.json").write_text(json.dumps(card, indent=2) + "\n")
        (out_dir / f"{q['id']}.md").write_text(render_card(card))
        rows.append(
            {
                "id": q["id"],
                **score,
                "seconds": round(r.seconds, 1),
                "total_seconds": round(r.seconds + r.retrieval_seconds, 1),
                "reasoning_tokens": r.reasoning_tokens,
                "retrieval_seconds": round(r.retrieval_seconds, 2),
            }
        )
        log(f"    -> {'PASS' if score['pass'] else 'FAIL'} {score}  ({r.seconds:.1f}s)")
    summary = {
        "model": cfg.chat_model,
        "label": label,
        "query_planning": cfg.query_planning,
        "two_hop": cfg.two_hop,
        "thinking": cfg.thinking,
        "environment": env,
        "rows": rows,
        "passed": sum(r["pass"] for r in rows),
        "total": len(rows),
        "memory_footprint_gb": sysinfo.lmstudio_footprint_gb(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def render_card(card: dict) -> str:
    q, r, s, env = card["test"], card["result"], card["score"], card["environment"]
    m = env["model"]
    lines = [
        f"# Evidence card: {q['id']}",
        "",
        f"**Question:** {q['question']}  ",
        f"**Kind:** {q['kind']}  ",
        f"**Mode:** ask · **Execution:** local ({env['endpoint']}) · "
        f"**Network online during run:** {env['network_online']}  ",
        f"**Model:** `{m.get('model')}` {m.get('format', '')} {m.get('quantization', '')} · "
        f"embeddings `{env['embed_model']}` · run {env['run_at']}",
        "",
        "## Expected (written before the run)",
        "",
        f"- Behavior: `{q['expect_behavior']}`",
        f"- Sources: {', '.join(f'`{x}`' for x in q['expect_sources']) or 'none'}",
        f"- Passage: {q['expect_passage']}",
        "",
        f"**Search queries:** {' · '.join(f'`{x}`' for x in r.get('search_queries', []))}  ",
        f"**Two-hop:** {('missing ' + repr(r['two_hop']['missing']) + ' -> searched `' + r['two_hop']['query'] + '`') if r.get('two_hop') else 'not needed'}",
        "",
        f"## Retrieved passages ({r['retrieval']}, {r['retrieval_seconds']}s)",
        "",
    ]
    for p in r["passages"]:
        text = p["text"] if len(p["text"]) < 900 else p["text"][:900] + " …"
        lines += [
            f"**[{p['id']}]** `{p['cite']}` · bm25 rank {p['bm25_rank']} · vector rank {p['vector_rank']}",
            "",
            "```text",
            text,
            "```",
            "",
        ]
    lines += [
        "## Gemma's answer",
        "",
        r["answer"],
        "",
        f"*{r['generation_seconds']}s generation, {r['prompt_tokens']} prompt tokens*",
        "",
        f"## Citation check: {r['citation_check']['summary']}",
        "",
    ]
    for c in r["citation_check"]["claims"]:
        extra = (
            f" · missing numbers {c['missing_numbers']}" if c["missing_numbers"] else ""
        )
        lines.append(
            f"- **{c['status']}** ({', '.join(c['cited']) or 'no citation'}, "
            f"overlap {c['overlap']}{extra}): {c['sentence']}"
        )
    lines += [
        "",
        "## Score",
        "",
        "| retrieval hit | behavior | exact facts | citations | PASS |",
        "|---|---|---|---|---|",
        "| "
        + " | ".join(
            "✅" if s[k] else "❌"
            for k in (
                "retrieval_hit",
                "behavior_ok",
                "facts_ok",
                "citations_ok",
                "pass",
            )
        )
        + " |",
        "",
        "## Assessment",
        "",
        "_Human review: see README evidence section._",
        "",
    ]
    return "\n".join(lines)


MODE_SCRIPT = [
    (
        "chat",
        "what can you help me with?",
        "capabilities; no retrieval; no insufficient-evidence refusal",
    ),
    ("chat", "what can we do?", "capabilities; no retrieval"),
    (
        "chat",
        "Draft a short study plan for reviewing my Pac-Man DQN project before a quiz.",
        "draft; may retrieve; wiki facts cited",
    ),
    ("chat", "make that shorter", "uses the previous draft; no new retrieval"),
    (
        "chat",
        "By the way, my Pac-Man agent's best score was 9,999 points.",
        "chat accepts it as conversation only",
    ),
    (
        "search",
        "replay buffer capacity",
        "original passages + paths, no generated answer",
    ),
    (
        "ask",
        "What was the Pac-Man agent's best score?",
        "cites sources only; must not repeat 9,999 from chat",
    ),
]


def run_mode_checks(cfg: Config, log=print) -> dict:
    env = environment(cfg)
    session = modes.ChatSession(cfg)
    results = []
    for mode, text, expect in MODE_SCRIPT:
        log(f"  [{mode}] {text}")
        if mode == "chat":
            rec = session.turn(text)
            results.append(
                {
                    "mode": mode,
                    "input": text,
                    "expect": expect,
                    "retrieved": rec["router"]["retrieve"],
                    "router": rec["router"],
                    "passages": [p["cite"] for p in rec["passages"]],
                    "output": rec["reply"],
                    "seconds": rec["seconds"],
                }
            )
        elif mode == "search":
            t0 = time.perf_counter()
            hits, method = modes.search(cfg, text, 3)
            results.append(
                {
                    "mode": mode,
                    "input": text,
                    "expect": expect,
                    "method": method,
                    "seconds": round(time.perf_counter() - t0, 2),
                    "output": [modes.hit_dict(i, h) for i, h in enumerate(hits, 1)],
                }
            )
        else:
            r = modes.ask(cfg, text)
            results.append(
                {
                    "mode": mode,
                    "input": text,
                    "expect": expect,
                    "output": r.answer,
                    "passages": [h.passage.cite for h in r.hits],
                    "citation_check": r.report.summary(),
                    "contains_chat_claim": "9,999" in r.answer or "9999" in r.answer,
                    "seconds": round(r.seconds, 1),
                "total_seconds": round(r.seconds + r.retrieval_seconds, 1),
                "reasoning_tokens": r.reasoning_tokens,
                }
            )
    out_dir = EVIDENCE / "modes"
    out_dir.mkdir(parents=True, exist_ok=True)
    data = {"environment": env, "checks": results}
    (out_dir / f"{slug(cfg.chat_model)}.json").write_text(
        json.dumps(data, indent=2) + "\n"
    )
    (out_dir / f"{slug(cfg.chat_model)}.md").write_text(render_modes(data))
    return data


def render_modes(data: dict) -> str:
    env = data["environment"]
    lines = [
        f"# Mode boundary checks: {env['model'].get('model')}",
        "",
        f"Execution: local ({env['endpoint']}) · network online during run: **{env['network_online']}** · "
        f"{env['run_at']}",
        "",
    ]
    for c in data["checks"]:
        lines += [
            f"## `{c['mode']}` · {c['input']}",
            "",
            f"*Expected:* {c['expect']}  ",
        ]
        if c["mode"] == "chat":
            lines += [
                f"*Router:* retrieve={c['router']['retrieve']} query=`{c['router']['query']}` "
                f"({c['router']['reason']})  ",
                f"*Passages:* {', '.join(f'`{p}`' for p in c['passages']) or 'none'} · {c['seconds']}s",
                "",
                *[f"> {l}" if l else ">" for l in c["output"].splitlines()],
                "",
            ]
        elif c["mode"] == "search":
            lines += [f"*Method:* {c['method']} · {c['seconds']}s · no model call", ""]
            for p in c["output"]:
                lines += [
                    f"**[{p['id']}]** `{p['cite']}`",
                    "",
                    "```text",
                    p["text"][:600],
                    "```",
                    "",
                ]
        else:
            lines += [
                f"*Passages:* {', '.join(f'`{p}`' for p in c['passages'])}  ",
                f"*Citation check:* {c['citation_check']} · *repeats chat-only claim:* "
                f"{c['contains_chat_claim']}",
                "",
                *[f"> {l}" if l else ">" for l in c["output"].splitlines()],
                "",
            ]
    return "\n".join(lines)


def run_ladder(cfg: Config, models: list[str], judge: bool = False, log=print) -> Path:
    """Same four questions per model size, thinking off and on; memory measured with only
    that model loaded. Time is end to end: planning + retrieval + generation."""
    rows = []
    for m in models:
        sysinfo.load_model(m, cfg.context_length)
        for thinking in (False, True):
            log(f"== {m} · thinking {'on' if thinking else 'off'}")
            cfg.chat_model, cfg.thinking = m, thinking
            s = run_questions(cfg, judge=judge, label=f"ladder-{slug(m)}-think-{'on' if thinking else 'off'}", log=log)
            n = len(s["rows"])
            rows.append((m, "on" if thinking else "off", s["passed"], n, s["environment"]["model"].get("weights_gb"),
                         s["memory_footprint_gb"], round(sum(r["total_seconds"] for r in s["rows"]) / n, 1),
                         round(sum(r["reasoning_tokens"] for r in s["rows"]) / n),
                         [r["id"] for r in s["rows"] if not r["pass"]]))
    out = EVIDENCE / "model-ladder.md"
    lines = ["# Model ladder: the same four ask-mode tests per Gemma size", "",
             f"Query planning {'on' if cfg.query_planning else 'off'}, citation judge {'on' if judge else 'off'}, "
             f"embeddings `{cfg.embed_model}`, run {time.strftime('%Y-%m-%d %H:%M')}.", "",
             "| Model | Thinking | Passed | Weights (GB) | LM Studio footprint (GB) | Avg ask, end to end (s) "
             "| Avg reasoning tokens | Failed |",
             "|---|---|---|---|---|---|---|---|"]
    lines += [f"| `{m}` | {th} | {p}/{n} | {w} | {f} | {a} | {rt} | {', '.join(x) or '-'} |"
              for m, th, p, n, w, f, a, rt, x in rows]
    out.write_text("\n".join(lines) + "\n")
    return out
