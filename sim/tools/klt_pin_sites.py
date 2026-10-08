#!/usr/bin/env python3
"""Hold every restated klt/klayout pin to signoff/check.py (#344).

The normative klayout-tools build (DR-0026) is a pair: a klayout-tools
release and the KLayout engine release it is installed with. The pair is
defined once, as two constants in signoff/check.py:

  KLT_PIN       the klayout-tools release  (``klayout-tools==<KLT_PIN>``)
  KLAYOUT_PIN   the KLayout engine release (``klayout==<KLAYOUT_PIN>``)

It is also restated by hand wherever a reader or a workflow needs the
install command: CI workflow steps, READMEs, docstrings, DR-0026 itself. A
pin bump must touch all of them, and a missed one means CI installs a
different build than the grader expects, or a README tells a reader to
install a build that cannot reproduce the committed reports. This script
finds every restatement and fails if any disagrees with the constants.

Scanned files (tracked in git only):

  .github/workflows/*.yml, *.yaml
  every *.md and *.py file

except the append-only evidence areas, which record what was true when
they were written and are never edited: sim/records/, signoff/evidence/,
signoff/records/ and layout/reports/.

A pin mention is the literal string ``klayout-tools==X.Y.Z`` or
``klayout==X.Y.Z``. Other spellings (a git URL, ``klt 0.6.0`` in prose, a
version alone) are not pins and are not matched.

Historical mentions
-------------------
Some text deliberately narrates an older build, e.g. a past experiment run
under klayout-tools 0.2.0. Mark such a line with the literal token

  klt-pin: historical

anywhere on the same line (an HTML comment in Markdown, a ``#`` comment in
YAML or Python, or plain text inside a docstring). The marker exempts the
pin mentions on that one line only. A marker on a line with no mismatching
pin fails the check, so a marker cannot outlive the mention it was for or
silently pre-exempt a line that is in fact current.

Usage:
  python3 sim/tools/klt_pin_sites.py           # list every pin mention
  python3 sim/tools/klt_pin_sites.py --check   # exit 1 on any disagreement

Read-only. Stdlib only (plus ``git ls-files``); no klt, no PDK.
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

#: The file whose constants are the source of truth, relative to the root.
PIN_SOURCE = "signoff/check.py"

#: package name -> constant in PIN_SOURCE that pins it.
PIN_CONSTANTS = {
    "klayout-tools": "KLT_PIN",
    "klayout": "KLAYOUT_PIN",
}

#: Append-only evidence areas: never scanned (they are never edited).
EXCLUDED_PREFIXES = (
    "sim/records/",
    "signoff/evidence/",
    "signoff/records/",
    "layout/reports/",
)

WORKFLOW_DIR = ".github/workflows/"

MARKER = "klt-pin: historical"

#: This module documents the marker in prose, so the unused-marker rule
#: skips it (it carries no pin mentions to exempt).
_SELF_REL = "sim/tools/klt_pin_sites.py"

# `klayout-tools==X.Y.Z` or `klayout==X.Y.Z`, not preceded by a name
# character (so `foo-klayout==1.0` is not a klayout pin). The version is
# dotted digits with an optional PEP 440 pre/post/dev/local suffix; a
# sentence-ending period is not swallowed because each dot must be
# followed by a digit.
_PIN = re.compile(
    r"(?<![\w.-])(klayout-tools|klayout)==("
    r"\d+(?:\.\d+)*(?:(?:a|b|rc|\.post|\.dev)\d+)*(?:\+[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*)?"
    r")"
)


@dataclass(frozen=True)
class Mention:
    path: str
    line: int
    package: str
    version: str
    marked: bool


def read_pins(root: Path) -> dict[str, str]:
    """The pinned version per package, read from PIN_SOURCE's constants.

    Parsed (not imported) so that a synthetic tree can be checked and so
    that a non-literal assignment is caught rather than evaluated.
    """
    source = root / PIN_SOURCE
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    found: dict[str, str] = {}
    wanted = set(PIN_CONSTANTS.values())
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name) and target.id in wanted:
                value = node.value
                if not (isinstance(value, ast.Constant)
                        and isinstance(value.value, str)):
                    raise ValueError(
                        f"{PIN_SOURCE}: {target.id} must be a string literal")
                found[target.id] = value.value
    missing = sorted(wanted - found.keys())
    if missing:
        raise ValueError(f"{PIN_SOURCE}: missing {', '.join(missing)}")
    return {pkg: found[const] for pkg, const in PIN_CONSTANTS.items()}


def is_scanned(rel: str) -> bool:
    if rel.startswith(EXCLUDED_PREFIXES):
        return False
    if rel.startswith(WORKFLOW_DIR):
        return rel.endswith((".yml", ".yaml"))
    return rel.endswith((".md", ".py"))


def tracked_files(root: Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True, capture_output=True, text=True,
    ).stdout
    return sorted(p for p in out.split("\0") if p and is_scanned(p))


def find_mentions(rel: str, text: str) -> list[Mention]:
    mentions = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        marked = MARKER in line
        for m in _PIN.finditer(line):
            mentions.append(Mention(rel, lineno, m.group(1), m.group(2),
                                    marked))
    return mentions


def marker_lines(text: str) -> list[int]:
    return [n for n, line in enumerate(text.splitlines(), start=1)
            if MARKER in line]


def check_text(rel: str, text: str, pins: dict[str, str]
               ) -> tuple[list[Mention], list[str]]:
    """Every pin mention in one file, and the diagnostics for it."""
    mentions = find_mentions(rel, text)
    problems = []
    exempted_lines = set()
    for m in mentions:
        if m.version == pins[m.package]:
            continue
        if m.marked:
            exempted_lines.add(m.line)
            continue
        problems.append(
            f"{rel}:{m.line}: {m.package}=={m.version}, but {PIN_SOURCE} "
            f"pins {m.package}=={pins[m.package]} (update it, or mark a "
            f"deliberately historical line with '{MARKER}')")
    # A marker must be earning its keep.
    if rel != _SELF_REL:
        for line in marker_lines(text):
            if line not in exempted_lines:
                problems.append(
                    f"{rel}:{line}: '{MARKER}' marker exempts no "
                    f"mismatching pin on its line; remove it")
    return mentions, problems


def check_tree(root: Path) -> tuple[dict[str, str], list[Mention], list[str]]:
    pins = read_pins(root)
    mentions: list[Mention] = []
    problems: list[str] = []
    for rel in tracked_files(root):
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        found, bad = check_text(rel, text, pins)
        mentions += found
        problems += bad
    return pins, mentions, problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any restated pin disagrees")
    ap.add_argument("--root", type=Path, default=REPO_ROOT,
                    help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    try:
        pins, mentions, problems = check_tree(args.root.resolve())
    except (OSError, ValueError, SyntaxError,
            subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    for pkg, version in pins.items():
        print(f"pinned: {pkg}=={version}  ({PIN_SOURCE} "
              f"{PIN_CONSTANTS[pkg]})")
    for m in mentions:
        tag = " [historical]" if m.marked else ""
        print(f"  {m.path}:{m.line}: {m.package}=={m.version}{tag}")
    if not args.check:
        return 0
    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        return 1
    print(f"OK: {len(mentions)} pin mentions agree with {PIN_SOURCE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
