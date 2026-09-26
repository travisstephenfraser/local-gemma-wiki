"""`wiki`: command-line entry point. Parses the command, picks the mode, prints results.

One path end to end, `wiki ask "..."`:
  main() -> config.load() -> modes.ask()
    -> Index.load().search()        BM25 + embeddings over state_dir, RRF merge
    -> render_passages()             numbered [S#] evidence block
    -> llm.chat()                    prompts/wiki-instructions.md + passages -> LM Studio -> Gemma
    -> citations.check()             every claim vs. the passage it cites
  -> print answer, citations, check; modes.log_run() saves the full record
"""

from __future__ import annotations

import argparse
import sys
import textwrap
import time
from pathlib import Path

from . import citations, config, evals, ingest, llm, modes, sysinfo
from .config import ROOT
from .index import Index, RetrievalError

DIM, BOLD, RED, GREEN, YELLOW, RESET = (
    ("\033[2m", "\033[1m", "\033[31m", "\033[32m", "\033[33m", "\033[0m")
    if sys.stdout.isatty()
    else ("",) * 6
)

HELP = f"""\
Personal wiki CLI over local Gemma (LM Studio). Local execution is the default and only mode.

commands:
  ingest [PATH]        read sources under vault/raw (default: all), have Gemma write linked
                       notes in vault/wiki, update index.md, then rebuild the search index.
                       Unchanged sources are skipped; --force regenerates in place.
  index                rebuild the retrieval index only (no language model needed)
  search "QUERY"       show matching original passages with paths and line ranges. No answer
                       is generated and the chat model is not called.
  ask "QUESTION"       standalone factual answer from retrieved passages, with [S#] citations
                       and a citation check, or INSUFFICIENT EVIDENCE. Ignores chat history.
  chat                 personal assistant with conversation memory; retrieves notes only when
                       a turn needs them. In-chat: /sources /save /reset /help /exit
  eval                 run tests/questions.toml in ask mode and write evidence cards
                       (--modes: chat/search/ask boundary checks; --ladder M1 M2: compare models)
  status               model, endpoint, index, network state

configuration: {ROOT / "config.toml"}
  profiles: class (default, writable vault/) · brain (personal vault, read-only)
  instructions: prompts/persona.md (chat) · prompts/wiki-instructions.md (ask) ·
                prompts/router.md (chat retrieval decision) · prompts/ingest.md
required: LM Studio server running (`lms server start`) with the chat and embedding
models from config.toml downloaded. `search` and `index` work without the chat model.
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="wiki",
        description=HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--profile", help="config profile (default from config.toml)")
    ap.add_argument("--model", help="override the chat model id for this run")
    sub = ap.add_subparsers(dest="cmd", metavar="command")
    p = sub.add_parser("ingest", help="generate wiki notes from raw sources")
    p.add_argument(
        "path", nargs="?", help="file or folder under vault/raw (default: all of raw/)"
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="regenerate even if the source is unchanged",
    )
    sub.add_parser("index", help="rebuild the retrieval index")
    p = sub.add_parser("search", help="show original passages, no answer")
    p.add_argument("query")
    p.add_argument("-k", type=int, default=None)
    p = sub.add_parser("ask", help="grounded answer with citations")
    p.add_argument("question")
    p.add_argument(
        "--mode", choices=["local"], default="local", help="execution mode (local only)"
    )
    p.add_argument(
        "--judge", action="store_true", help="also have Gemma judge each cited claim"
    )
    sub.add_parser("chat", help="conversational assistant")
    p = sub.add_parser("eval", help="run the evidence tests")
    p.add_argument(
        "--modes", action="store_true", help="run the chat/search/ask boundary checks"
    )
    p.add_argument(
        "--ladder", nargs="+", metavar="MODEL", help="compare models on the ask tests"
    )
    p.add_argument("--judge", action="store_true")
    p.add_argument("--label", help="evidence folder name (default: model name)")
    p.add_argument("--two-hop", choices=["on", "off"], help="override retrieval.two_hop")
    p.add_argument(
        "--planning", choices=["on", "off"], help="override retrieval.query_planning"
    )
    sub.add_parser("status", help="show model, index, and network state")
    sub.add_parser("help", help="show this help")
    args = ap.parse_args(argv)

    if args.cmd in (None, "help"):
        ap.print_help()
        return 0
    try:
        cfg = config.load(args.profile, args.model)
        return COMMANDS[args.cmd](cfg, args)
    except (
        config.ConfigError,
        llm.ModelError,
        RetrievalError,
        FileNotFoundError,
        PermissionError,
        ValueError,
    ) as e:
        print(f"{RED}error:{RESET} {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


def header(cfg, mode: str) -> None:
    print(f"{DIM}[{mode} · local · {cfg.chat_model} · profile {cfg.profile}]{RESET}")


def cmd_ingest(cfg, args) -> int:
    print(f"{DIM}[ingest · local · {cfg.ingest_model} · profile {cfg.profile}]{RESET}")
    llm.available(cfg)
    sysinfo.load_model(cfg.ingest_model, cfg.context_length)
    target = Path(args.path) if args.path else cfg.raw_dir
    t0 = time.perf_counter()
    stats = ingest.run(cfg, target, force=args.force)
    print(
        f"ingest: {stats['extracted']} extracted by {cfg.ingest_model}, {stats['unchanged']} unchanged "
        f"({time.perf_counter() - t0:.1f}s)"
    )
    return cmd_index(cfg, args)


def cmd_index(cfg, args) -> int:
    t0 = time.perf_counter()
    idx = Index.build(cfg)
    m = idx.meta
    print(
        f"index: {m['passages']} passages from {m['files']} files · embeddings: {m['embeddings']} "
        f"· {time.perf_counter() - t0:.1f}s → {cfg.state_dir}"
    )
    return 0


def cmd_search(cfg, args) -> int:
    print(f"{DIM}[search · no model call · profile {cfg.profile}]{RESET}")
    hits, method = modes.search(cfg, args.query, args.k)
    print(f"{DIM}{method} · {len(hits)} passages{RESET}\n")
    if not hits:
        print("no matching passages")
    for i, h in enumerate(hits, 1):
        print(
            f"{BOLD}[S{i}] {h.passage.cite}{RESET}  {DIM}({h.passage.kind}, bm25 #{h.bm25_rank}, "
            f"vector #{h.vec_rank}){RESET}"
        )
        print(textwrap.indent(_clip(h.passage.text, 900), "    "), "\n")
    modes.log_run(
        cfg,
        {
            "mode": "search",
            "query": args.query,
            "method": method,
            "network_online": sysinfo.network_online(),
            "passages": [modes.hit_dict(i, h) for i, h in enumerate(hits, 1)],
        },
    )
    return 0


def cmd_ask(cfg, args) -> int:
    header(cfg, "ask")
    r = modes.ask(cfg, args.question, judge=args.judge)
    print(f"\n{r.answer}\n")
    if r.hits:
        print(f"{BOLD}Sources{RESET} {DIM}({r.method}){RESET}")
        for i, h in enumerate(r.hits, 1):
            print(f"  [S{i}] {h.passage.cite}")
    print_check(r.report)
    print(
        f"{DIM}retrieval {r.retrieval_seconds:.2f}s · generation {r.seconds:.1f}s · "
        f"{r.prompt_tokens} prompt tokens{RESET}"
    )
    rec = r.to_dict() | {"network_online": sysinfo.network_online()}
    print(
        f"{DIM}saved {modes.log_run(cfg, rec).relative_to(ROOT) if cfg.runs_dir.is_relative_to(ROOT) else 'run log'}{RESET}"
    )
    return 0


def print_check(report: citations.Report) -> None:
    colour = GREEN if report.ok else YELLOW
    print(f"{colour}citation check: {report.summary()}{RESET}")
    for c in report.claims:
        if c.status != "supported":
            why = (
                f"missing {c.missing_numbers}"
                if c.missing_numbers
                else f"overlap {c.overlap}"
            )
            print(f"  {YELLOW}{c.status}{RESET} ({why}): {_clip(c.sentence, 140)}")


def cmd_chat(cfg, args) -> int:
    llm.available(cfg)
    session = modes.ChatSession(cfg)
    header(cfg, "chat")
    print(
        f"Marginalia here ({cfg.profile} wiki). Ask me to draft, plan, or dig through your notes. /help for commands.\n"
    )
    while True:
        try:
            user = input(f"{BOLD}you ›{RESET} ").strip()
            if not sys.stdin.isatty():
                print(
                    user
                )  # piped input (the recorded demo): echo it so transcripts read naturally
        except EOFError:
            break
        if not user:
            continue
        if user in ("/exit", "/quit"):
            break
        if user == "/help":
            print(
                "/sources  passages used last turn\n/save     save last reply to outputs/drafts (not evidence)\n"
                "/reset    clear conversation\n/exit     leave"
            )
            continue
        if user == "/reset":
            session = modes.ChatSession(cfg)
            print(f"{DIM}conversation cleared{RESET}")
            continue
        if user == "/sources":
            for i, h in enumerate(session.last_hits, 1):
                print(f"  [S{i}] {h.passage.cite}")
            if not session.last_hits:
                print(f"{DIM}no notes were retrieved last turn{RESET}")
            continue
        if user == "/save":
            f = session.save_last(ROOT / "outputs" / "drafts")
            print(f"{DIM}saved draft → {f}{RESET}" if f else "nothing to save yet")
            continue
        try:
            rec = session.turn(user)
        except llm.ModelError as e:
            print(f"{RED}error:{RESET} {e}")
            continue
        note = (
            f"searched notes: “{rec['router']['query']}”"
            if rec["router"]["retrieve"]
            else "no notes needed"
        )
        print(f"\n{rec['reply']}\n")
        if rec["passages"]:
            for p in rec["passages"]:
                print(f"  {DIM}[{p['id']}] {p['cite']}{RESET}")
        print(f"{DIM}{note} · {rec['seconds']}s{RESET}\n")
    if session.transcript:
        f = modes.log_run(
            cfg,
            {
                "mode": "chat",
                "network_online": sysinfo.network_online(),
                "model": cfg.chat_model,
                "turns": session.transcript,
            },
        )
        print(f"{DIM}transcript saved → {f}{RESET}")
    return 0


def cmd_eval(cfg, args) -> int:
    llm.available(cfg)
    if args.planning:
        cfg.query_planning = args.planning == "on"
    if args.two_hop:
        cfg.two_hop = args.two_hop == "on"
    if args.ladder:
        out = evals.run_ladder(cfg, args.ladder, judge=args.judge)
        print(out.read_text())
        return 0
    header(cfg, "eval")
    sysinfo.load_model(cfg.chat_model, cfg.context_length)
    if args.modes:
        evals.run_mode_checks(cfg)
        print(f"mode checks → evidence/modes/{evals.slug(cfg.chat_model)}.md")
        return 0
    s = evals.run_questions(cfg, judge=args.judge, label=args.label)
    print(
        f"\n{s['passed']}/{s['total']} passed · LM Studio footprint {s['memory_footprint_gb']} GB "
        f"→ evidence/ask/{args.label or evals.slug(cfg.chat_model)}/"
    )
    return 0


def cmd_status(cfg, args) -> int:
    print(
        f"profile     {cfg.profile} ({'writable' if cfg.writable else 'read-only'}) · vault {cfg.vault}"
    )
    print(f"endpoint    {cfg.endpoint} (local)")
    print(f"network     {'online' if sysinfo.network_online() else 'OFFLINE'}")
    try:
        ids = llm.available(cfg)
        ok = lambda m: (
            f"{GREEN}available{RESET}" if m in ids else f"{RED}missing{RESET}"
        )
        print(f"chat model  {cfg.chat_model} · {ok(cfg.chat_model)}")
        print(f"embeddings  {cfg.embed_model} · {ok(cfg.embed_model)}")
    except llm.ModelError as e:
        print(f"server      {RED}{e}{RESET}")
    info = sysinfo.model_info(cfg.chat_model)
    if info.get("loaded") is not False:
        print(f"loaded      {info}")
        print(f"memory      LM Studio physical footprint {sysinfo.lmstudio_footprint_gb()} GB")
    try:
        m = Index.load(cfg).meta
        print(
            f"index       {m['passages']} passages / {m['files']} files · embeddings {m['embeddings']} · built {m['built']}"
        )
    except RetrievalError as e:
        print(f"index       {e}")
    return 0


def _clip(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


COMMANDS = {
    "ingest": cmd_ingest,
    "index": cmd_index,
    "search": cmd_search,
    "ask": cmd_ask,
    "chat": cmd_chat,
    "eval": cmd_eval,
    "status": cmd_status,
}

if __name__ == "__main__":
    sys.exit(main())
