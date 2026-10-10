#!/usr/bin/env python3
"""Fail if tracked generated JSON embeds an absolute host path.

Scope is deliberately narrow: git-tracked `*.json` files beneath `design/`,
`layout/` and `signoff/`, with every JSON string value (recursively) searched
for `/home/<user>/` and `/Users/<user>/`. This is a JSON-report hygiene check,
not a claim to scrub all public text or every form of absolute path.

Working-tree contents are read, so staged or unstaged edits to tracked files
are checked. Untracked files are not selected.

One historical file is permitted, and only while it is byte-identical: the
published native item-7 response, which is copied byte for byte from an
append-only raw response (see signoff/publish_item7.py). The exception is the
fixed (path, SHA-256) pair below; it is not derived from any publication pin,
and the same bytes at any other path, or different bytes at this path, are
checked like any other file.

Usage:
  python3 sim/tools/verify_report_host_paths.py [--repo DIR]

Exit 0 = clean, 1 = findings or malformed JSON. Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOTS = ("design/", "layout/", "signoff/")
HOST_PATH = re.compile(r"/(?:home|Users)/[^/\s\"']+/")

HISTORICAL_EXEMPTIONS = {
    "signoff/evidence/post-route/gate_klt_response.json": (
        "af63e5193ea6af94003478089aceb4eaeff81faf635ffe538944a12d1c3f17c7"
    ),
}


def tracked_json(repo: Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z"],
        check=True,
        capture_output=True,
    ).stdout
    names = [n.decode("utf-8", "surrogateescape") for n in out.split(b"\0") if n]
    return sorted(n for n in names if n.endswith(".json") and n.startswith(ROOTS))


def find_host_paths(node, field: str = "$"):
    """Yield (field_path, value) for every string value holding a host path."""
    if isinstance(node, str):
        if HOST_PATH.search(node):
            yield field, node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from find_host_paths(value, f"{field}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from find_host_paths(value, f"{field}[{i}]")


def check(repo: Path) -> list[str]:
    problems: list[str] = []
    for rel in tracked_json(repo):
        path = repo / rel
        try:
            data = path.read_bytes()
        except OSError as exc:
            problems.append(f"{rel}: unreadable: {exc}")
            continue
        if HISTORICAL_EXEMPTIONS.get(rel) == hashlib.sha256(data).hexdigest():
            continue
        try:
            doc = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            problems.append(f"{rel}: malformed JSON: {exc}")
            continue
        for field, _ in find_host_paths(doc):
            problems.append(f"{rel}: {field}: absolute host path")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = ap.parse_args(argv)
    problems = check(args.repo)
    for p in problems:
        print(p, file=sys.stderr)
    if problems:
        print(f"FAIL: {len(problems)} host-path finding(s)", file=sys.stderr)
        return 1
    print("ok: no host paths in tracked generated JSON")
    return 0


if __name__ == "__main__":
    sys.exit(main())
