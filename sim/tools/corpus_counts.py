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

The same --check also holds the `npm run check:spec` gate inventory to its
single source (#360). package.json's check:spec script is the list; the
tool names and their count are derived from its `sim/tools/<name>.py --check`
invocations, and three restatements must agree with it:

  README.md                   "<N> spec-arithmetic self-checks" and the set
                              of `<name>.py` names in that bullet
  .github/workflows/ci.yml    every "list of [all] <N>" count, and the set of
                              header lines `#   sim/tools/<name>.py --check`
  package.json description    optional; a "<N> spec-arithmetic ..." count
                              there, if present, must match too

Adding, removing or renaming a gate without updating those prose lists fails
the gate. No gate is added by this: the guard rides on corpus_counts.py's own
entry in the chain.

Usage:
  python3 sim/tools/corpus_counts.py           # print derived totals
  python3 sim/tools/corpus_counts.py --check   # exit 1 on any disagreement

Read-only. Stdlib only; no ngspice and no PDK.
"""

from __future__ import annotations

import argparse
import json
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


_GATE = re.compile(r"python3\s+sim/tools/([A-Za-z0-9_]+)\.py\s+--check\b")
_README_COUNT = re.compile(
    r"([\w,-]+)\s+spec-arithmetic\s+(?:self-checks|derivations)\b",
    re.IGNORECASE)
_CI_COUNT = re.compile(r"\blist\s+of\s+(?:all\s+)?([\w,-]+)", re.IGNORECASE)
_CI_NAME = re.compile(
    r"^#\s+sim/tools/([A-Za-z0-9_]+)\.py\s+--check\s*$", re.MULTILINE)
_NAME_IN_PROSE = re.compile(r"`([A-Za-z0-9_]+)\.py`")


def spec_gates(package_json_text: str) -> list[str]:
    """Tool names chained by package.json's check:spec script, in order."""
    script = json.loads(package_json_text).get("scripts", {}).get(
        "check:spec", "")
    return _GATE.findall(script)


def _counts(pattern: re.Pattern[str], text: str) -> list[int]:
    plain = re.sub(r"(?m)^\s*#", " ", _MD_LINK.sub(r"\1", text))
    return [v for m in pattern.finditer(plain)
            if (v := parse_number(m.group(1))) is not None]


def _name_diff(document: str, quoted: set[str], gates: list[str]) -> list[str]:
    want = set(gates)
    out = []
    if want - quoted:
        out.append(f"{document}: gate list omits "
                   f"{', '.join(sorted(want - quoted))}")
    if quoted - want:
        out.append(f"{document}: gate list names "
                   f"{', '.join(sorted(quoted - want))}, not in check:spec")
    return out


def check_gate_inventory(root: Path) -> list[str]:
    """Diagnostics for the check:spec count/name restatements (#360)."""
    pkg = root / "package.json"
    if not pkg.is_file():
        return ["package.json: document missing"]
    try:
        pkg_text = pkg.read_text(encoding="utf-8")
        gates = spec_gates(pkg_text)
        description = json.loads(pkg_text).get("description", "")
    except ValueError as e:
        return [f"package.json: unparseable ({e})"]
    if not gates:
        return ["package.json: check:spec lists no --check gates"]
    n = len(gates)
    problems: list[str] = []
    if len(set(gates)) != n:
        problems.append("package.json: check:spec repeats a gate")

    def count_problems(doc: str, found: list[int], required: bool) -> None:
        if not found and required:
            problems.append(f"{doc}: gate count quoted missing/unparseable, "
                            f"check:spec has {n}")
        for q in found:
            if q != n:
                problems.append(f"{doc}: gate count quoted {q}, "
                                f"check:spec has {n}")

    readme = root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        count_problems("README.md", _counts(_README_COUNT, text), True)
        m = re.search(r"(?ms)^- \*\*`npm run check:spec`\*\*.*?(?=^- |\Z)",
                      text)
        if m is None:
            problems.append("README.md: check:spec bullet missing")
        else:
            problems += _name_diff("README.md",
                                   set(_NAME_IN_PROSE.findall(m.group(0))),
                                   gates)
    else:
        problems.append("README.md: document missing")

    ci = root / ".github" / "workflows" / "ci.yml"
    if ci.is_file():
        text = ci.read_text(encoding="utf-8")
        count_problems(".github/workflows/ci.yml",
                       _counts(_CI_COUNT, text), True)
        problems += _name_diff(".github/workflows/ci.yml",
                               set(_CI_NAME.findall(text)), gates)
    else:
        problems.append(".github/workflows/ci.yml: document missing")

    count_problems("package.json description",
                   _counts(_README_COUNT, description), False)
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any quoted corpus total disagrees")
    ap.add_argument("--root", type=Path, default=REPO_ROOT,
                    help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    counts, problems = check_tree(args.root.resolve())
    problems += check_gate_inventory(args.root.resolve())
    for category in CATEGORIES:
        print(f"{category}: {counts[category]}")
    if not args.check:
        return 0
    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        return 1
    print("OK: corpus totals quoted in README.md agree with the tree; "
          "check:spec gate inventory agrees with package.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
