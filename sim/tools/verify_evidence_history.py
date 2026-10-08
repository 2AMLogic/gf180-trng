#!/usr/bin/env python3
"""Enforce "sim/records/ is append-only" against a base revision.

`verify_record_checksums.py` checks that the *current tree* is internally
consistent. That cannot detect history rewrites: editing a record's prose,
rewriting raw output together with its recorded hashes, or deleting a record
and its raw directory all leave a self-consistent tree. This tool compares the
committed blobs under `sim/records/` at HEAD with those at a base revision and
fails on anything but an append.

Rules (sim/README.md, "Superseding a record"):

  * a file added under sim/records/ (a new record or new raw output) passes;
  * a modified, deleted, renamed (seen as delete + add) or type-changed file
    under sim/records/raw/ -- or any other non-record file -- fails;
  * a modified, deleted or renamed record `sim/records/<stem>.md` fails, with
    exactly one exception, the documented supersession edit: `status: valid`
    becomes `status: superseded` and one `superseded_by: <stem>` line is
    added, and NOTHING else changes. The check is byte-exact: undoing those two
    edits must reproduce the base bytes. The replacement record must exist at
    HEAD and carry `supersedes: <old stem>`.

Only the two endpoint trees are compared (merge-base .. HEAD), so an edit that
is later reverted on the same branch nets to nothing.

Base selection is explicit and never silently empty: the base must resolve to a
commit and share history with HEAD (`git merge-base`), otherwise the tool exits
2. A shallow clone that lacks the base, an all-zero SHA (first push of a ref) or
an unknown revision are therefore failures, not passes. CI checks out full
history and passes the PR base SHA (pull_request) or the pushed-from SHA (push).

Usage:
  python3 sim/tools/verify_evidence_history.py                 # vs origin/main
  python3 sim/tools/verify_evidence_history.py --base REV      # vs REV
  python3 sim/tools/verify_evidence_history.py --head REV      # default HEAD
  python3 sim/tools/verify_evidence_history.py --repo DIR      # other checkout

Exit 0 = append-only, 1 = violations, 2 = base/head could not be loaded.
Stdlib only; no ngspice and no PDK.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS_PREFIX = "sim/records/"
STEM_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class HistoryError(Exception):
    """The base or head revision could not be loaded (exit 2)."""


def _git(repo: Path, *args: str, text: bool = True, check: bool = True):
    proc = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=text, check=False
    )
    if check and proc.returncode != 0:
        err = proc.stderr if text else proc.stderr.decode(errors="replace")
        raise HistoryError(f"git {' '.join(args)} failed: {err.strip()}")
    return proc


def resolve_commit(repo: Path, rev: str, what: str) -> str:
    proc = _git(repo, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}", check=False)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise HistoryError(
            f"{what} revision {rev!r} cannot be resolved to a commit "
            "(shallow checkout? all-zero SHA? fetch full history, e.g. "
            "actions/checkout fetch-depth: 0)"
        )
    return proc.stdout.strip()


def merge_base(repo: Path, base: str, head: str) -> str:
    proc = _git(repo, "merge-base", base, head, check=False)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise HistoryError(
            f"no merge-base between {base} and {head}: history is missing "
            "(shallow clone?) or unrelated; refusing to pass an unchecked diff"
        )
    return proc.stdout.strip()


def changed_entries(repo: Path, base: str, head: str) -> list[tuple[str, str, str, str, str, str]]:
    """(old_mode, new_mode, old_sha, new_sha, status, path); no renames.

    Rename detection is off so a rename shows as delete + add and the delete
    fails.
    """
    proc = _git(
        repo, "diff-tree", "-r", "--raw", "--no-renames", "-z", "--no-abbrev",
        base, head, "--", RECORDS_PREFIX.rstrip("/"), text=False,
    )
    parts = proc.stdout.split(b"\0")
    entries = []
    i = 0
    while i + 1 < len(parts) and parts[i]:
        meta = parts[i].decode().lstrip(":").split()
        path = parts[i + 1].decode(errors="surrogateescape")
        if len(meta) != 5:
            raise HistoryError(f"unexpected diff-tree output: {parts[i]!r}")
        old_mode, new_mode, old_sha, new_sha, status = meta
        entries.append((old_mode, new_mode, old_sha, new_sha, status, path))
        i += 2
    return entries


def _blob(repo: Path, rev: str, path: str) -> bytes | None:
    proc = _git(repo, "cat-file", "blob", f"{rev}:{path}", text=False, check=False)
    return proc.stdout if proc.returncode == 0 else None


def _is_record_path(path: str) -> bool:
    rest = path[len(RECORDS_PREFIX):]
    return path.startswith(RECORDS_PREFIX) and "/" not in rest and rest.endswith(".md")


def _front_value(lines: list[bytes], key: str) -> list[str]:
    """Values of front-matter lines `key: value` (front matter = between ---)."""
    out = []
    if not lines or lines[0].rstrip(b"\r\n") != b"---":
        return out
    for raw in lines[1:]:
        line = raw.rstrip(b"\r\n")
        if line == b"---":
            break
        text = line.decode(errors="replace")
        if text.startswith(key + ":"):
            out.append(text[len(key) + 1:].strip())
    return out


def check_supersession(repo: Path, head: str, old_path: str, old: bytes, new: bytes) -> list[str]:
    """Problems with a modified record; empty if it is the permitted edit only."""
    stem = old_path[len(RECORDS_PREFIX):-len(".md")]
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)

    old_status = _front_value(old_lines, "status")
    if old_status != ["valid"]:
        return [f"{old_path}: modified but base status is {old_status!r}, not a single "
                "'status: valid'; only valid -> superseded is permitted"]
    if _front_value(old_lines, "superseded_by"):
        return [f"{old_path}: modified but base already has superseded_by"]
    if _front_value(new_lines, "status") != ["superseded"]:
        return [f"{old_path}: modified without a single 'status: superseded' "
                "(only the documented supersession edit is permitted)"]
    pointers = _front_value(new_lines, "superseded_by")
    if len(pointers) != 1 or not STEM_RE.match(pointers[0]):
        return [f"{old_path}: expected exactly one 'superseded_by: <record-stem>', got {pointers!r}"]
    target = pointers[0]

    # Undo the two permitted edits and demand the base bytes back, exactly.
    status_line = b"status: superseded"
    pointer_line = f"superseded_by: {target}".encode()
    undone: list[bytes] = []
    status_done = pointer_done = False
    in_front = False
    for idx, raw in enumerate(new_lines):
        bare = raw.rstrip(b"\r\n")
        if idx == 0 and bare == b"---":
            in_front = True
        elif in_front and bare == b"---":
            in_front = False
        if in_front and bare == status_line and not status_done:
            undone.append(raw.replace(status_line, b"status: valid", 1))
            status_done = True
        elif in_front and bare == pointer_line and not pointer_done:
            pointer_done = True
        else:
            undone.append(raw)
    if b"".join(undone) != old:
        return [f"{old_path}: changed beyond the documented supersession edit "
                "(status valid -> superseded plus one superseded_by line)"]

    # The replacement must exist at HEAD and point back at the old stem.
    repl_path = f"{RECORDS_PREFIX}{target}.md"
    repl = _blob(repo, head, repl_path)
    if repl is None:
        return [f"{old_path}: superseded_by {target!r} but {repl_path} does not exist at HEAD"]
    back = _front_value(repl.splitlines(keepends=True), "supersedes")
    if len(back) != 1 or back[0].split()[:1] != [stem]:
        return [f"{old_path}: replacement {repl_path} does not declare 'supersedes: {stem}'"]
    return []


def check_history(repo: Path, base: str, head: str = "HEAD") -> list[str]:
    """Violations between merge-base(base, head) and head. Raises HistoryError."""
    head_sha = resolve_commit(repo, head, "head")
    base_sha = resolve_commit(repo, base, "base")
    if base_sha == head_sha:
        mb = base_sha
    else:
        mb = merge_base(repo, base_sha, head_sha)

    problems: list[str] = []
    for old_mode, new_mode, old_sha, new_sha, status, path in changed_entries(repo, mb, head_sha):
        if status == "A":
            if new_mode not in ("100644", "100755"):
                problems.append(f"{path}: added with unsupported mode {new_mode} (symlink/submodule)")
            continue
        if status == "D":
            problems.append(f"{path}: historical evidence deleted or renamed")
            continue
        if status == "T":
            problems.append(f"{path}: file type changed ({old_mode} -> {new_mode})")
            continue
        if status != "M":
            problems.append(f"{path}: unexpected change status {status!r}")
            continue
        if not _is_record_path(path):
            problems.append(f"{path}: historical raw/non-record evidence modified")
            continue
        if old_mode != new_mode:
            problems.append(f"{path}: mode changed ({old_mode} -> {new_mode})")
            continue
        old = _blob(repo, mb, path)
        new = _blob(repo, head_sha, path)
        if old is None or new is None:
            raise HistoryError(f"cannot read {path} at base or head")
        problems.extend(check_supersession(repo, head_sha, path, old, new))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verify_evidence_history.py",
        description="Fail if sim/records/ history was rewritten relative to a base revision.",
    )
    parser.add_argument("--base", default="origin/main", help="base revision (default origin/main)")
    parser.add_argument("--head", default="HEAD", help="head revision (default HEAD)")
    parser.add_argument("--repo", default=str(REPO_ROOT), help="git checkout to inspect")
    parser.add_argument("--quiet", action="store_true", help="print failures only")
    args = parser.parse_args(argv)
    repo = Path(args.repo)

    try:
        problems = check_history(repo, args.base, args.head)
    except HistoryError as exc:
        print(f"ERROR: cannot load evidence history: {exc}", file=sys.stderr)
        return 2
    if problems:
        for p in problems:
            print(f"FAIL {p}")
        print(f"{len(problems)} append-only violation(s) against {args.base}")
        return 1
    if not args.quiet:
        print(f"ok: sim/records/ is append-only relative to {args.base}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
