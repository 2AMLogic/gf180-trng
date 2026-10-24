#!/usr/bin/env python3
"""Check the stored-evidence manifests under manifests/artifacts/ (#686).

New sim evidence keeps its raw bytes in the fleet's artifact store; git holds
a manifest per run (`manifests/artifacts/<stem>.manifest.json`) and the record
that cites it. This is the cheap, offline half of keeping that honest:

  1. every manifest parses and has the expected schema (schema_version, a
     non-empty `entries` list; each entry a unique relative `name`, a 64-hex
     `sha256`, an integer `size`, `kind: evidence`);
  2. every entry `uri` starts with `artifact:` and names its sha256;
  3. no file under `manifests/` contains `s3://` or `arn:aws:` -- a manifest
     names objects, never a bucket or an account;
  4. no committed file holds the bytes of a stored object: the sha256 of every
     git-tracked file whose size equals a stored object's is compared with the
     manifest digests (empty files are skipped: nothing to leak, and every
     `__init__.py` would match);
  5. nothing under the git-ignored staging area `sim/.work/` is tracked.

Re-hashing the objects against the store is `klt artifact verify <manifest>`,
which needs the broker and so runs on a fleet worker, not in CI.

Usage:
  python3 sim/tools/verify_artifact_manifests.py check [--repo DIR]

Exit 0 if every check passes, 1 on a violation, 2 if git cannot list the
tracked files. Stdlib only; no ngspice, no PDK, no broker.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR))

from harness import evidence_store  # noqa: E402

MANIFESTS_ROOT = "manifests"
STAGE_PREFIX = "sim/.work/"


class GitError(RuntimeError):
    """git could not list the tracked files."""


def tracked_files(repo: Path) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "ls-files", "-z"], cwd=repo, capture_output=True, check=False
        )
    except OSError as exc:
        raise GitError(f"cannot run git in {repo}: {exc}") from exc
    if proc.returncode != 0:
        raise GitError(
            f"git ls-files in {repo} failed (exit {proc.returncode}): "
            f"{proc.stderr.decode(errors='replace').strip()}"
        )
    return [p.decode(errors="surrogateescape") for p in proc.stdout.split(b"\0") if p]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(repo: Path, tracked: list[str]) -> list[str]:
    """Every violation under ``repo``; empty means the manifests are sound."""
    problems: list[str] = []
    root = repo / MANIFESTS_ROOT
    stored: dict[int, dict[str, str]] = {}  # size -> {sha256: "<manifest>:<name>"}

    if root.is_dir():
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            rel = path.relative_to(repo).as_posix()
            try:
                text = path.read_text(errors="replace")
            except OSError as exc:
                problems.append(f"{rel}: cannot read: {exc}")
                continue
            for marker in evidence_store.FORBIDDEN_MARKERS:
                if marker in text:
                    problems.append(f"{rel}: contains {marker!r}; manifests name objects, never storage")
        for path in sorted(root.glob(f"artifacts/*{evidence_store.MANIFEST_SUFFIX}")):
            rel = path.relative_to(repo).as_posix()
            data, schema = evidence_store.load_manifest(path)
            problems += [f"{rel}: {p}" for p in schema]
            if data is None:
                continue
            for entry in data["entries"]:
                if entry["size"] > 0:
                    stored.setdefault(entry["size"], {})[entry["sha256"]] = f"{rel}:{entry['name']}"

    for name in tracked:
        if name.startswith(STAGE_PREFIX):
            problems.append(f"{name}: tracked file under the git-ignored staging area {STAGE_PREFIX}")
            continue
        if not stored:
            continue
        path = repo / name
        try:
            if path.is_symlink() or not path.is_file():
                continue
            size = path.stat().st_size
            if size not in stored:
                continue
            digest = _sha256(path)
        except OSError:
            continue
        if digest in stored[size]:
            problems.append(
                f"{name}: committed bytes equal stored object {stored[size][digest]} "
                "(raw evidence must not be committed)"
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verify_artifact_manifests.py",
        description="Validate manifests/artifacts/ and that no stored bytes are committed.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser("check", help="offline manifest and no-committed-bytes check")
    check_parser.add_argument("--repo", default=str(REPO_ROOT), help="git checkout to inspect")
    args = parser.parse_args(argv)

    repo = Path(args.repo)
    try:
        tracked = tracked_files(repo)
    except GitError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    problems = check(repo, tracked)
    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        print(f"{len(problems)} artifact-manifest violation(s)")
        return 1
    count = len(list((repo / "manifests" / "artifacts").glob(f"*{evidence_store.MANIFEST_SUFFIX}")))
    print(f"ok: {count} artifact manifest(s); no stored bytes committed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
