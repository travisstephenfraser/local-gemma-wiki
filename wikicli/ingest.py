"""`wiki ingest`: raw sources -> local Gemma -> linked wiki notes.

Two stages, so re-ingesting can never create duplicates:

  extract  For each new or changed source, send its text + prompts/ingest.md to
           Gemma with a JSON schema. Cache the JSON in state_dir/extractions/.
           Unchanged sources (same SHA-256) are skipped; no model call.
  render   Rebuild the wiki from every cached extraction:
             wiki/Projects/<Project>.md  one note per raw/ subfolder, a section per source
             wiki/Concepts|Tools/<Name>.md  one note per idea, merged across projects
             index.md, Source Catalog.md
           Filenames come from the manifest, so they stay stable across runs. A note
           whose file changed since the harness last wrote it was edited by hand; it is
           left alone and reported, never overwritten.
"""

from __future__ import annotations

import hashlib
import tomllib
import json
import re
import time
from collections import defaultdict
from pathlib import Path

from . import llm
from .config import ROOT, Config, prompt
from .notes import canonical, clean_title, frontmatter

ROLES = ["assignment brief", "project write-up", "course material", "supporting data"]
KINDS = {"concept": "Concepts", "tool": "Tools"}
# Names that mean the model echoed the schema or instructions instead of reading the source.
ECHOES = {
    "definition",
    "name",
    "concept",
    "tool",
    "kind",
    "summary",
    "source",
    "project",
    "document",
    "key fact",
    "role",
    "in thi source",
}

SCHEMA = {
    "type": "object",
    "properties": {
        "project_title": {"type": "string"},
        "role": {"type": "string", "enum": ROLES},
        "summary": {"type": "string"},
        "key_facts": {"type": "array", "items": {"type": "string"}, "maxItems": 8},
        "concepts": {
            "type": "array",
            "maxItems": 5,
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "kind": {"type": "string", "enum": list(KINDS)},
                    "definition": {"type": "string"},
                    "in_this_source": {"type": "string"},
                },
                "required": ["name", "kind", "definition", "in_this_source"],
            },
        },
    },
    "required": ["project_title", "role", "summary", "key_facts", "concepts"],
}


def sha256(data: bytes | str) -> str:
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()


# ---------------------------------------------------------------- manifest
def load_manifest(cfg: Config) -> dict:
    f = cfg.state_dir / "manifest.json"
    m = json.loads(f.read_text()) if f.exists() else {}
    for k in ("sources", "projects", "rendered"):
        m.setdefault(k, {})
    return m


def save_manifest(cfg: Config, m: dict) -> None:
    cfg.state_dir.mkdir(parents=True, exist_ok=True)
    (cfg.state_dir / "manifest.json").write_text(
        json.dumps(m, indent=2, sort_keys=True) + "\n"
    )


def extraction_path(cfg: Config, sid: str) -> Path:
    return cfg.state_dir / "extractions" / f"{sha256(sid)[:16]}.json"


# ---------------------------------------------------------------- extract
def run(cfg: Config, target: Path, *, force: bool = False, log=print) -> dict:
    if not cfg.writable:
        raise PermissionError(
            f"profile {cfg.profile!r} is read-only; ingest would write into {cfg.vault}"
        )
    raw, target = cfg.raw_dir.resolve(), target.resolve()
    if not target.exists():
        raise FileNotFoundError(f"no such source: {target}")
    if raw not in (target, *target.parents):
        raise ValueError(
            f"sources must live under {raw} so they stay traceable; copy them there first"
        )
    files = sorted(
        f
        for f in (target.rglob("*") if target.is_dir() else [target])
        if f.suffix in (".md", ".txt") and f.is_file()
    )
    manifest = load_manifest(cfg)
    stats = {"extracted": 0, "unchanged": 0, "model_seconds": 0.0}
    for gone in [sid for sid in manifest["sources"] if not (cfg.vault / sid).exists()]:
        extraction_path(cfg, gone).unlink(missing_ok=True)
        manifest["sources"].pop(gone)
        log(f"  - {gone}  no longer in raw/, forgotten")

    for f in files:
        sid = f.relative_to(cfg.vault).as_posix()
        digest = sha256(f.read_bytes())
        prev = manifest["sources"].get(sid)
        if (
            prev
            and prev["sha256"] == digest
            and not force
            and extraction_path(cfg, sid).exists()
        ):
            log(f"  = {sid}  unchanged, skipped")
            stats["unchanged"] += 1
            continue
        if prev and prev["sha256"] == digest and _reviewed(cfg, sid):
            log(
                f"  = {sid}  human-reviewed and unchanged; --force does not overwrite reviews"
            )
            stats["unchanged"] += 1
            continue
        log(f"  > {sid}  -> {cfg.ingest_model}")
        data, secs = extract(cfg, f, sid, manifest)
        ep = extraction_path(cfg, sid)
        ep.parent.mkdir(parents=True, exist_ok=True)
        ep.write_text(json.dumps(data, indent=2) + "\n")
        manifest["sources"][sid] = {
            "sha256": digest,
            "model": cfg.ingest_model,
            "seconds": round(secs, 1),
            "extracted": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "extraction": ep.relative_to(cfg.state_dir).as_posix(),
        }
        project = project_key(sid)
        manifest["projects"].setdefault(
            project, {"title": clean_title(data["project_title"], 5)}
        )
        save_manifest(cfg, manifest)
        stats["extracted"] += 1
        stats["model_seconds"] += secs
        log(f"    {data['role']}, {len(data['concepts'])} concepts ({secs:.1f}s)")

    report = render(cfg, manifest)
    save_manifest(cfg, manifest)
    for line in report:
        log(line)
    return stats


def project_key(sid: str) -> str:
    parts = Path(sid).parts  # raw/<project>/file.md
    return parts[1] if len(parts) > 2 else "misc"


def _reviewed(cfg: Config, sid: str) -> bool:
    p = extraction_path(cfg, sid)
    return p.exists() and bool(json.loads(p.read_text()).get("reviewed"))


def extract(cfg: Config, f: Path, sid: str, manifest: dict) -> tuple[dict, float]:
    text = f.read_text(errors="replace")
    words = text.split()
    truncated = len(words) > cfg.max_source_words
    if truncated:
        text = " ".join(words[: cfg.max_source_words])
    known_concepts = sorted(
        {
            c["name"]
            for d in all_extractions(cfg, manifest).values()
            for c in d["concepts"]
        }
    )
    known_project = manifest["projects"].get(project_key(sid), {}).get("title")
    user = (
        f"SOURCE PATH: {sid}\n"
        f"PROJECT FOLDER: {project_key(sid)}"
        f"{f' (already titled {known_project!r}; reuse that title)' if known_project else ''}\n"
        f"EXISTING CONCEPT NAMES (reuse the exact name when the idea matches): "
        f"{', '.join(known_concepts) or '(none yet)'}\n\n"
        f"SOURCE TEXT{' (truncated)' if truncated else ''}:\n<<<\n{text}\n>>>"
    )
    messages = [
        {"role": "system", "content": prompt("ingest.md")},
        {"role": "user", "content": user},
    ]
    retries = 0
    for temperature in (0.1, 0.4):  # a runaway repetition at 0.1 usually clears at 0.4
        try:
            data, reply = llm.chat_json(
                cfg,
                messages,
                SCHEMA,
                model=cfg.ingest_model,
                temperature=temperature,
                max_tokens=4000,
            )
            break
        except llm.ModelError as e:
            if "cut off" not in str(e) or retries:
                raise
            retries += 1
    data["retries"] = retries
    data["source"] = sid
    data["truncated"] = truncated
    data["model"] = reply.model
    return data, reply.seconds


def all_extractions(cfg: Config, manifest: dict) -> dict[str, dict]:
    out = {}
    for sid in sorted(manifest["sources"]):
        p = extraction_path(cfg, sid)
        if p.exists() and (cfg.vault / sid).exists():
            out[sid] = json.loads(p.read_text())
    return out


# ---------------------------------------------------------------- render
def render(cfg: Config, manifest: dict) -> list[str]:
    ex = all_extractions(cfg, manifest)
    projects: dict[str, list[dict]] = defaultdict(list)
    for sid, d in ex.items():
        projects[project_key(sid)].append(d)

    # Merge concepts across sources by canonical name; the first spelling seen wins.
    concepts: dict[str, dict] = {}
    echoes: list[str] = []
    for sid, d in ex.items():
        title = manifest["projects"][project_key(sid)]["title"]
        for c in d["concepts"][:5]:
            try:
                name = clean_title(c["name"], 4)
            except ValueError:
                continue
            key = canonical(name)
            if key == canonical(title):
                continue
            if key in ECHOES:
                echoes.append(
                    f"  ! dropped concept {name!r} from {sid}: echoes the schema, not the source"
                )
                continue
            entry = concepts.setdefault(
                key,
                {
                    "name": name,
                    "kind": c["kind"],
                    "definition": c["definition"],
                    "uses": {},
                },
            )
            entry["uses"].setdefault(title, []).append((c["in_this_source"], sid))
            c["_name"] = entry["name"]

    files: dict[Path, str] = {}
    by_project_concepts: dict[str, list[str]] = defaultdict(list)
    for key, c in sorted(concepts.items()):
        for t in c["uses"]:
            by_project_concepts[t].append(c["name"])
    for key, c in concepts.items():
        files[cfg.wiki_dir / KINDS.get(c["kind"], "Concepts") / f"{c['name']}.md"] = (
            render_concept(c, by_project_concepts)
        )
    for pk, docs in sorted(projects.items()):
        title = manifest["projects"][pk]["title"]
        files[cfg.wiki_dir / "Projects" / f"{title}.md"] = render_project(
            title, pk, docs, concepts, by_project_concepts
        )
    files[cfg.vault / "index.md"] = render_index(cfg, manifest, projects, concepts)
    files[cfg.vault / "Source Catalog.md"] = render_catalog(manifest, ex)
    return echoes + write_all(cfg, manifest, files)


def write_all(cfg: Config, manifest: dict, files: dict[Path, str]) -> list[str]:
    """Write rendered files, but never clobber a note a human edited after the last render."""
    report, rendered = [], manifest["rendered"]
    for path, text in files.items():
        rel = path.relative_to(cfg.vault).as_posix()
        last = rendered.get(rel)
        if path.exists() and last and sha256(path.read_text()) != last:
            report.append(
                f"  ! {rel}: edited by hand since last render; kept your version"
            )
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        # case-only rename ("NanoGPT" -> "nanoGPT") on a case-insensitive filesystem
        on_disk = next(
            (p for p in path.parent.iterdir() if p.name.lower() == path.name.lower()),
            None,
        )
        if on_disk is not None and on_disk.name != path.name:
            on_disk.rename(path)
        if not path.exists() or path.read_text() != text:
            path.write_text(text)
        rendered[rel] = sha256(text)
    for rel in [r for r in rendered if (cfg.vault / r) not in files]:
        stale = cfg.vault / rel
        if stale.exists() and sha256(stale.read_text()) == rendered[rel]:
            stale.unlink()  # a note the harness wrote that no source produces any more
            report.append(f"  - removed {rel} (no source produces it now)")
        rendered.pop(rel)
    notes = [p for p in files if p.parent.parent == cfg.wiki_dir]
    report.append(
        f"render: {len(notes)} notes ({sum('Projects' in p.parts for p in notes)} projects), "
        f"index.md, Source Catalog.md"
    )
    return report


def _link(sid: str, depth: int = 2) -> str:
    return f"[{sid}]({'../' * depth}{sid.replace(' ', '%20')})"


ROLE_HEADINGS = {
    "assignment brief": "The assignment brief",
    "project write-up": "My write-up",
    "course material": "Course material",
    "supporting data": "Supporting data",
}


def render_project(
    title: str, pk: str, docs: list[dict], concepts: dict, by_project: dict
) -> str:
    order = {r: i for i, r in enumerate(ROLES)}
    docs = sorted(docs, key=lambda d: (order.get(d["role"], 9), d["source"]))
    lead = next((d for d in docs if d["role"] == "project write-up"), docs[0])
    out = [
        frontmatter(
            {
                "type": "project",
                "project_folder": pk,
                "sources": [d["source"] for d in docs],
                "generated_by": sorted({d["model"] for d in docs}),
                "tags": ["project"],
            }
        ),
        f"# {title}\n",
        lead["summary"].strip(),
        "",
    ]
    for d in docs:
        out += [f"## {ROLE_HEADINGS[d['role']]}: `{Path(d['source']).name}`", ""]
        if d is not lead:  # the lead summary already opens the note
            out += [d["summary"].strip(), ""]
        out += [f"- {x.strip()}" for x in d["key_facts"] if x.strip()]
        out += [
            "",
            f"Source: {_link(d['source'])}"
            + (
                " (first part only; longer than the ingest limit)"
                if d.get("truncated")
                else ""
            ),
            "",
        ]
    names = by_project.get(title, [])
    if names:
        out += ["## Concepts and tools", ""]
        for n in names:
            c = concepts[canonical(n)]
            out.append(f"- [[{n}]]: {c['uses'][title][0][0].strip()}")
        out.append("")
    related = []
    for other, other_names in sorted(by_project.items()):
        shared = sorted(set(names) & set(other_names))
        if other != title and shared:
            related.append(
                f"- [[{other}]]: also uses {', '.join(f'[[{s}]]' for s in shared)}"
            )
    if related:
        out += ["## Related projects", "", *related, ""]
    out += ["---", "See [[Source Catalog]] for file hashes and ingest details.", ""]
    return "\n".join(out)


def render_concept(c: dict, by_project: dict) -> str:
    out = [
        frontmatter(
            {
                "type": c["kind"],
                "sources": sorted({s for u in c["uses"].values() for _, s in u}),
                "tags": [c["kind"]],
            }
        ),
        f"# {c['name']}\n",
        c["definition"].strip(),
        "",
        "## Where it appears",
        "",
    ]
    for project, uses in sorted(c["uses"].items()):
        out.append(f"### [[{project}]]")
        for how, sid in uses:
            out.append(f"- {how.strip()} ({_link(sid)})")
        siblings = [n for n in by_project.get(project, []) if n != c["name"]]
        if siblings:
            out.append(
                f"- Used alongside {', '.join(f'[[{s}]]' for s in siblings)} in this project."
            )
        out.append("")
    return "\n".join(out)


def render_index(cfg: Config, manifest: dict, projects: dict, concepts: dict) -> str:
    out = [
        "# Class Notes Wiki",
        "",
        "My coursework for the class, turned into linked notes by a local Gemma harness and reviewed "
        "by hand. Start with a project, follow a concept or tool into the other projects that use it, "
        "and follow any note back to its original in `raw/`.",
        "",
        "- [[Source Catalog]]: every original file, its hash, and the note it feeds",
        "",
        "## Projects",
        "",
    ]
    for pk in sorted(projects):
        title = manifest["projects"][pk]["title"]
        lead = next(
            (d for d in projects[pk] if d["role"] == "project write-up"),
            projects[pk][0],
        )
        out.append(f"- [[{title}]] (`raw/{pk}/`): {_first_sentence(lead['summary'])}")
    for kind, heading in (("concept", "Concepts"), ("tool", "Tools")):
        items = sorted(
            (c for c in concepts.values() if c["kind"] == kind),
            key=lambda c: c["name"].lower(),
        )
        if items:
            out += ["", f"## {heading}", ""]
            out += [
                f"- [[{c['name']}]]: {_first_sentence(c['definition'])}" for c in items
            ]
    return "\n".join(out) + "\n"


def render_catalog(manifest: dict, ex: dict) -> str:
    rows = [
        "# Source Catalog",
        "",
        "Originals in `raw/` are never edited. Each row maps a source file to the project note it "
        "feeds. The hash is how re-ingest knows a file is unchanged.",
        "",
        "| Source | Author | Origin | Role | Project note | SHA-256 | Model |",
        "|---|---|---|---|---|---|---|",
    ]
    prov = _provenance()
    for sid, e in sorted(manifest["sources"].items()):
        if sid not in ex:
            continue
        title = manifest["projects"][project_key(sid)]["title"]
        rows.append(
            f"| {_link(sid, 0)} | {prov.get(sid, {}).get('author', '?')} | "
            f"{prov.get(sid, {}).get('origin', '?')} | {ex[sid]['role']}"
            f"{' (reviewed)' if ex[sid].get('reviewed') else ''} | [[{title}]] | "
            f"`{e['sha256'][:12]}` | {e['model']} |"
        )
    return "\n".join(rows) + "\n"


def _provenance() -> dict:
    f = ROOT / "sources.toml"
    return tomllib.loads(f.read_text()) if f.exists() else {}


def _first_sentence(s: str) -> str:
    # split at sentence ends, but not after short abbreviations like "Ms." or "e.g."
    first = re.split(
        r"(?<!\b[A-Z][a-z]\.)(?<!\be\.g\.)(?<!\bi\.e\.)(?<=[.!?])\s+(?=[A-Z])",
        s.strip(),
    )[0]
    return first if len(first) < 200 else first[:197] + "..."
