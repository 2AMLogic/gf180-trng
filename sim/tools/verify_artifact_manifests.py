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
     `__init__.py` would match; entries named for a harness input snapshot --
     `spinit`, `tb.fragment.spice`, `dut.netlist.spice`, `tb.manifest.json`,
     `pdk-models.json` -- are skipped too, as is an entry the citing record
     declares in its `inputs.netlist_dependencies`, because those are byte
     copies of tracked inputs by construction, DR-0032 amendment of
     2026-10-24; the dependency exemption is per manifest and per declared
     name);
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
import re
import sys
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR))

from harness import evidence_store, pdk_models, startup, testbench  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _git_files import GitError, tracked_files  # noqa: E402

MANIFESTS_ROOT = "manifests"
STAGE_PREFIX = "sim/.work/"

#: Names of the per-run input snapshots the harness stores beside the output.
#: Each is a byte copy of a tracked file, so matching bytes in git is expected.
INPUT_SNAPSHOT_NAMES = frozenset(
    {
        startup.SNAPSHOT_NAME,
        testbench.FRAGMENT_SNAPSHOT_NAME,
        testbench.DUT_SNAPSHOT_NAME,
        testbench.MANIFEST_SNAPSHOT_NAME,
        pdk_models.MANIFEST_NAME,
    }
)

RECORDS_DIR = "sim/records"
_MANIFEST_LINE = re.compile(r"^\s+manifest:\s*(\S+)\s*$")
_DEPENDENCIES_LINE = re.compile(r"^\s+netlist_dependencies:\s*(.+?)\s*$")


def declared_dependencies(repo: Path) -> dict[str, set[str]]:
    """Manifest path -> dependency names its record declares in ``inputs``.

    Dependency snapshots keep the basename of an arbitrary tracked file, so no
    fixed name list covers them; the record that cites the manifest says which
    entries they are. Only the leading frontmatter is read.
    """
    declared: dict[str, set[str]] = {}
    for path in sorted((repo / RECORDS_DIR).glob("*.md")):
        try:
            lines = path.read_text(errors="replace").splitlines()
        except OSError:
            continue
        if not lines or lines[0] != "---":
            continue
        manifest = None
        names: set[str] = set()
        for line in lines[1:]:
            if line == "---":
                break
            if (m := _MANIFEST_LINE.match(line)) and manifest is None:
                manifest = m.group(1)
            elif m := _DEPENDENCIES_LINE.match(line):
                names |= {n.strip() for n in m.group(1).split(",") if n.strip()}
        if manifest:
            declared.setdefault(manifest, set()).update(names)
    return declared


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
        dependencies = declared_dependencies(repo)
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
            exempt = INPUT_SNAPSHOT_NAMES | dependencies.get(rel, set())
            for entry in data["entries"]:
                if entry["size"] > 0 and entry["name"] not in exempt:
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
