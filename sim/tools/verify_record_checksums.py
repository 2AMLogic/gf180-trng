#!/usr/bin/env python3
"""Mechanical check for sim/README.md's "raw output committed under
sim/records/raw/<stem>/ with checksums listed" pre-commit item.

For every record under sim/records/ this re-derives, rather than trusts:

  1. the raw directory the record cites exists;
  2. every file listed in `raw.files` is there and still hashes to the
     SHA-256 the record claims;
  3. the directory holds nothing the record failed to list (a stray deck or
     log means some other run wrote into this record's raw directory);
  4. every one of those files is tracked by git, i.e. actually committed --
     `--no-git` skips this, e.g. for a record minted seconds ago.

Written after #60, where two concurrent `run_corners.py` invocations were
handed overlapping record stems and the second silently overwrote the
first's raw output *after* it had been hashed: 30 records that said
`status: valid`, carried checksums matching nothing on disk, and a run that
exited OK. The harness now refuses to write or finish such a record; this
script is the same check applied to what is already on disk, so the
pre-commit item is a command rather than an eyeball.

Usage:
  python3 sim/tools/verify_record_checksums.py                 # every record
  python3 sim/tools/verify_record_checksums.py <record.md>...  # named records
  python3 sim/tools/verify_record_checksums.py --changed       # records this
                                                               # branch adds
  python3 sim/tools/verify_record_checksums.py --no-git        # skip (4)
  python3 sim/tools/verify_record_checksums.py --quiet         # failures only

Exit 0 if every checked record verifies, 1 otherwise. Stdlib only; no
ngspice and no PDK.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR))

from harness import report  # noqa: E402

RECORDS_DIR = SIM_DIR / report.RECORDS_DIRNAME


def git_tracked_raw_files() -> set[str]:
    """Repo-relative paths under sim/records/raw/ that git knows about.

    One `git ls-files` for the whole tree, not one per record: at ~600
    records that difference is two minutes of process spawning versus a
    tenth of a second. Staged-but-uncommitted files count as tracked, which
    is what a pre-commit check wants.
    """
    raw_root = RECORDS_DIR / report.RAW_DIRNAME
    out = subprocess.run(
        ["git", "ls-files", "--", str(raw_root)],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    return {line for line in out.stdout.splitlines() if line}


def _changed_records(base: str) -> list[Path]:
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=A", f"{base}...HEAD", "--",
         f"{report.RECORDS_DIRNAME}/*.md"],
        cwd=SIM_DIR, capture_output=True, text=True, check=False,
    )
    return [SIM_DIR / line for line in out.stdout.splitlines() if line]


def verify_one(path: Path, tracked: set[str] | None = None) -> list[str]:
    """Every problem with one record; empty list means it verifies.

    ``tracked`` is the output of ``git_tracked_raw_files()``; pass None to
    skip the committed-to-git half of the check.
    """
    problems = report.verify_record_file(path, REPO_ROOT)
    if tracked is not None:
        raw_path, raw_files = report.parse_raw_section(path.read_text())
        if raw_path:
            raw_dir = REPO_ROOT / raw_path
            for name, _digest in raw_files:
                candidate = raw_dir / name
                if not candidate.is_file():
                    continue  # already reported as missing above
                rel = str(candidate.relative_to(REPO_ROOT))
                if rel not in tracked:
                    problems.append(f"{name}: not committed (git add {rel})")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verify_record_checksums.py",
        description="Re-hash every record's raw output against its raw.files checksums.",
    )
    parser.add_argument("records", nargs="*", metavar="RECORD", help="record .md paths")
    parser.add_argument(
        "--changed", nargs="?", const="origin/main", metavar="BASE",
        help="only records this branch adds relative to BASE (default origin/main)",
    )
    parser.add_argument("--no-git", action="store_true", help="skip the committed-to-git check")
    parser.add_argument("--quiet", action="store_true", help="print failures only")
    args = parser.parse_args(argv)

    if args.records:
        records = [Path(r) for r in args.records]
    elif args.changed:
        records = _changed_records(args.changed)
    else:
        records = sorted(RECORDS_DIR.glob("*.md"))

    if not records:
        print("no records to check")
        return 0

    tracked = None if args.no_git else git_tracked_raw_files()

    failures = 0
    for path in records:
        if not path.is_file():
            print(f"FAIL {path}: no such record", file=sys.stderr)
            failures += 1
            continue
        problems = verify_one(path, tracked)
        if problems:
            failures += 1
            print(f"FAIL {path.name}", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
        elif not args.quiet:
            print(f"ok   {path.name}")

    print()
    if failures:
        print(
            f"FAIL: {failures} of {len(records)} record(s) did not verify. A record "
            "whose checksums disagree with sim/records/raw/ is not evidence: it "
            "cannot tie its numbers to the run that produced them.",
            file=sys.stderr,
        )
        return 1
    scope = "raw output" if args.no_git else "committed raw output"
    print(f"PASS: {len(records)} record(s) match their {scope}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
