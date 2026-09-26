"""Apply human-review corrections to cached extractions, then log them.

Input:  evidence/review/corrections.json  (list of corrections, each with evidence)
Effect: patches state/class/extractions/*.json, marks them reviewed, writes
        evidence/review.md. Run `wiki ingest` afterwards to re-render the wiki.

Field syntax: "summary", "role", "key_facts[3]", "concepts[2].name",
"concepts[2]" with action "replace" (value = full concept) or "remove".
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wikicli import config, ingest  # noqa: E402

FIELD = re.compile(r"^(?P<key>\w+)(?:\[(?P<i>\d+)\])?(?:\.(?P<sub>\w+))?$")


def main() -> int:
    cfg = config.load("class")
    corrections = json.loads((ROOT / "evidence/review/corrections.json").read_text())
    manifest = ingest.load_manifest(cfg)
    by_file = {
        ingest.extraction_path(cfg, sid).name: sid for sid in manifest["sources"]
    }
    docs = {
        name: json.loads((cfg.state_dir / "extractions" / name).read_text())
        for name in by_file
    }
    removals: dict[str, list[int]] = {}

    for c in corrections:
        d = docs[c["extraction"]]
        m = FIELD.match(c["field"])
        key, i, sub = m["key"], m["i"], m["sub"]
        if c.get("action") == "remove":
            removals.setdefault(c["extraction"], []).append(int(i))
        elif c.get("action") == "keep":
            pass  # reviewed and deliberately left as generated
        elif i is None:
            d[key] = c["value"]
        elif sub is None:
            d[key][int(i)] = c["value"]
        else:
            d[key][int(i)][sub] = c["value"]
    for name, idxs in removals.items():
        for i in sorted(idxs, reverse=True):  # remove after edits so indexes stay valid
            docs[name]["concepts"].pop(i)

    stamp = time.strftime("%Y-%m-%d")
    for name, d in docs.items():
        d["reviewed"] = {
            "by": "Claude Code fact-check against the original, applied by Travis",
            "date": stamp,
            "corrections": sum(c["extraction"] == name for c in corrections),
        }
        (cfg.state_dir / "extractions" / name).write_text(
            json.dumps(d, indent=2) + "\n"
        )

    lines = [
        "# Wiki review log",
        "",
        f"Every generated extraction was checked claim by claim against its original in `vault/raw/` "
        f"({stamp}). Corrections were applied to the cached extraction (the reviewed layer), then the "
        "wiki was re-rendered. Originals were never changed.",
        "",
        f"{len(corrections)} corrections across {len({c['extraction'] for c in corrections})} of "
        f"{len(docs)} sources.",
        "",
        "| Source | Field | Problem | Was | Now | Evidence |",
        "|---|---|---|---|---|---|",
    ]
    for c in corrections:
        now = {"remove": "(removed)", "keep": "(kept)"}.get(
            c.get("action"), _cell(c.get("value"))
        )
        lines.append(
            f"| `{by_file[c['extraction']]}` | `{c['field']}` | {c['problem']} | "
            f"{_cell(c['current'])} | {now} | {_cell(c['evidence'])} |"
        )
    (ROOT / "evidence/review.md").write_text("\n".join(lines) + "\n")
    print(f"applied {len(corrections)} corrections; run `wiki ingest` to re-render")
    return 0


def _cell(v) -> str:
    s = v["name"] + ": " + v["in_this_source"] if isinstance(v, dict) else str(v)
    return s.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    sys.exit(main())
