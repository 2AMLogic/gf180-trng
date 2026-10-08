#!/usr/bin/env python3
"""Hold the corpus totals quoted in README.md to the tree (#320).

The top-level README states three corpus sizes in prose: how many decision
records there are, how many characterization summaries, and how many
evidence records. Those figures drifted after landings again and again
(#149, #155, #158, #197, #250, #252, #265, #279), each time fixed by hand.
This script derives the three totals from the tree and compares them to the
figures the prose quotes, so the drift fails CI instead of waiting for a
reader to notice.

The three populations, each counted over direct children only:

  decision records            distinct numeric ids among
                              spec/decision-records/DR-NNNN-*.md (two files
                              sharing an id count once; TEMPLATE.md and any
                              other non-DR file is ignored)
  characterization summaries  sim/characterization-*.md
  evidence records            sim/records/*.md -- the same population
                              verify_record_checksums.py walks; nested raw
                              output and other extensions are not records

Claims recognised in prose (Markdown links and line wrapping allowed, the
number in digits or spelled out up to ninety-nine):

  "<N> decision records"
  "<N> characterization summaries"
  "<N> [append-only] evidence records"

README.md must carry each of the three claims; a missing or unparseable one
fails rather than silently stops being guarded. sim/README.md is checked
too, but only if it repeats a total -- absence there is fine. Phrases with a
non-number in front ("the decision records", "no evidence records") are not
claims, and per-campaign sizes ("fifteen records") are not matched at all.

Usage:
  python3 sim/tools/corpus_counts.py           # print derived totals
  python3 sim/tools/corpus_counts.py --check   # exit 1 on any disagreement

Read-only. Stdlib only; no ngspice and no PDK.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DECISION = "decision records"
SUMMARIES = "characterization summaries"
EVIDENCE = "evidence records"
CATEGORIES = (DECISION, SUMMARIES, EVIDENCE)

# (document path relative to the repo root, whether every claim is required)
DOCUMENTS = (
    ("README.md", True),
    ("sim/README.md", False),
)

_UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90,
}

_DR_NAME = re.compile(r"^DR-(\d{4})-.+\.md$")

# The token immediately before the category noun phrase. Whitespace includes
# newlines, so a claim wrapped across lines still matches.
_CLAIM_PATTERNS = {
    DECISION: re.compile(r"(\S+)\s+decision\s+records\b", re.IGNORECASE),
    SUMMARIES: re.compile(
        r"(\S+)\s+characteri[sz]ation\s+summaries\b", re.IGNORECASE),
    EVIDENCE: re.compile(
        r"(\S+)\s+(?:append-only\s+)?evidence\s+records\b", re.IGNORECASE),
}
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def parse_number(token: str) -> int | None:
    """Return the integer a digit or spelled-out token names, else None.

    Accepts "975", "1,024", "twelve" and "twenty-one". Leading/trailing
    Markdown emphasis or bracket characters are ignored.
    """
    tok = token.strip("[]*_`(\"'").lower()
    if re.fullmatch(r"\d{1,3}(?:,\d{3})+|\d+", tok):
        return int(tok.replace(",", ""))
    if tok in _UNITS:
        return _UNITS[tok]
    if tok in _TENS:
        return _TENS[tok]
    m = re.fullmatch(r"([a-z]+)-([a-z]+)", tok)
    if m and m.group(1) in _TENS and m.group(2) in _UNITS \
            and 1 <= _UNITS[m.group(2)] <= 9:
        return _TENS[m.group(1)] + _UNITS[m.group(2)]
    return None


def find_claims(text: str) -> dict[str, list[int]]:
    """Every numeric corpus-total claim in ``text``, by category."""
    plain = _MD_LINK.sub(r"\1", text)
    claims: dict[str, list[int]] = {c: [] for c in CATEGORIES}
    for category, pattern in _CLAIM_PATTERNS.items():
        for m in pattern.finditer(plain):
            value = parse_number(m.group(1))
            if value is not None:
                claims[category].append(value)
    return claims


def derive_counts(root: Path) -> dict[str, int]:
    """The three corpus totals, derived from the tree under ``root``."""
    dr_dir = root / "spec" / "decision-records"
    dr_ids = {
        m.group(1)
        for p in dr_dir.iterdir()
        if p.is_file() and (m := _DR_NAME.match(p.name))
    } if dr_dir.is_dir() else set()
    sim = root / "sim"
    summaries = [p for p in sim.glob("characterization-*.md") if p.is_file()]
    records_dir = sim / "records"
    records = [p for p in records_dir.glob("*.md") if p.is_file()]
    return {
        DECISION: len(dr_ids),
        SUMMARIES: len(summaries),
        EVIDENCE: len(records),
    }


def check_text(document: str, text: str, counts: dict[str, int],
               required: bool) -> list[str]:
    """Diagnostics for one document's claims; empty means it agrees."""
    problems = []
    claims = find_claims(text)
    for category in CATEGORIES:
        actual = counts[category]
        if not claims[category]:
            if required:
                problems.append(
                    f"{document}: {category}: quoted missing/unparseable, "
                    f"derived {actual}")
            continue
        for quoted in claims[category]:
            if quoted != actual:
                problems.append(
                    f"{document}: {category}: quoted {quoted}, "
                    f"derived {actual}")
    return problems


def check_tree(root: Path) -> tuple[dict[str, int], list[str]]:
    counts = derive_counts(root)
    problems: list[str] = []
    for rel, required in DOCUMENTS:
        path = root / rel
        if not path.is_file():
            if required:
                problems.append(f"{rel}: document missing")
            continue
        problems += check_text(rel, path.read_text(encoding="utf-8"),
                               counts, required)
    return counts, problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any quoted corpus total disagrees")
    ap.add_argument("--root", type=Path, default=REPO_ROOT,
                    help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    counts, problems = check_tree(args.root.resolve())
    for category in CATEGORIES:
        print(f"{category}: {counts[category]}")
    if not args.check:
        return 0
    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        return 1
    print("OK: corpus totals quoted in README.md agree with the tree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
