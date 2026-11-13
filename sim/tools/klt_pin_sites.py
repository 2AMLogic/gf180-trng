#!/usr/bin/env python3
"""Hold every restated klt/klayout pin to signoff/check.py (#344).

The normative klayout-tools build (DR-0026) is a pair: a klayout-tools
release and the KLayout engine release it is installed with. The pair is
defined once, as two constants in signoff/check.py:

  (no KLT_PIN: the producer klayout-tools is not pinned, see below)
  KLAYOUT_PIN   the KLayout engine release (``klayout==<KLAYOUT_PIN>``)
  KLT_GRADER_PIN  optional; the klayout-tools release that GRADES the block
                (``klt signoff``), when it differs from the normative
                producer build KLT_PIN. Absent means the grader is KLT_PIN.

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

Grader mentions
---------------
The producer build (KLT_PIN, DR-0026) and the grader (KLT_GRADER_PIN) are
separate pins: reports are produced by one release and graded by another
whose checklist is newer. A ``klayout-tools==`` mention that restates the
grader (CI's signoff install step, the README's "Running it" line) carries
the literal token

  klt-pin: grader

on the same line and is held to KLT_GRADER_PIN instead of KLT_PIN. The token
must sit on a line that has a ``klayout-tools==`` mention.

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

Recorded engines in committed layout reports
--------------------------------------------
The scan above reads *install lines* -- what a reader or a workflow is told
to install. A committed report records the engine that actually produced
it, as a JSON field rather than a pin string, so the text scan cannot see
it. #858: `8e6fd5e8` regenerated 44 reports on a host whose klt ran KLayout
0.30.13 while KLAYOUT_PIN said 0.30.10, and the only checks that compare a
recorded engine (`layout/verify.py`, `layout/floorplan/floorplan.py`) need
klt and the PDK, so they self-skip on the pull-request path. The drift
reached `main` and stayed there.

So this tool also reads every git-tracked `*.json` file under `layout/` and
holds each recorded engine release to KLAYOUT_PIN:

  klayout_version   always, wherever it appears (`provenance.klayout_version`,
                    `drc.provenance.klayout_version`, ...)
  engine_version    only where the sibling `engine` field is ``klayout``.
                    `layout/digital/reports/place_and_route.json` and
                    `sdf_export.json` record an OpenROAD/OpenSTA
                    `engine_version` that KLAYOUT_PIN says nothing about.

This needs no klt and no PDK, so it runs on the pull-request path (`npm run
check:spec`). It is a *recorded-engine* check, not a freshness check: it
says which engine a report names, never whether re-running the flow would
reproduce it. There is no historical marker here -- JSON carries no
comments, and a committed layout report that names an off-pin engine is the
exact condition this check exists to refuse. Append-only evidence that
names its own producer (`sim/records/`, `signoff/evidence/`,
`signoff/records/`) is outside `layout/` and is not scanned.

Usage:
  python3 sim/tools/klt_pin_sites.py           # list every pin mention
  python3 sim/tools/klt_pin_sites.py --check   # exit 1 on any disagreement

Read-only. Stdlib only (plus ``git ls-files``); no klt, no PDK.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _git_files  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]

#: The file whose constants are the source of truth, relative to the root.
PIN_SOURCE = "signoff/check.py"

#: package name -> constant in PIN_SOURCE that pins it.
#: The producer klayout-tools is deliberately NOT here: the repo tracks the
#: fleet's klt version and carries no producer pin (DR-0026, 2026-11-09
#: amendment). Only the engine and the grader are pinned.
PIN_CONSTANTS = {
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
GRADER_MARKER = "klt-pin: grader"
#: Key under which the optional grader pin is carried in the pins mapping.
GRADER_KEY = "grader"
GRADER_CONSTANT = "KLT_GRADER_PIN"

#: This module documents the marker in prose, so the unused-marker rule
#: skips it (it carries no pin mentions to exempt).
_SELF_REL = "sim/tools/klt_pin_sites.py"

#: Committed JSON reports under this prefix record the engine release that
#: produced them, and are held to KLAYOUT_PIN by the recorded-engine scan
#: (#858). Everything under it is generated by the layout flow; the
#: append-only evidence areas above live elsewhere and are not scanned.
REPORT_PREFIX = "layout/"

#: The JSON field that always names the KLayout engine of the run that
#: wrote the report.
ENGINE_FIELD = "klayout_version"

#: The generic field: it names whatever engine the sibling ``engine`` field
#: identifies, so it is held to KLAYOUT_PIN only for ``klayout``.
GENERIC_ENGINE_FIELD = "engine_version"

#: The sibling field that says which engine GENERIC_ENGINE_FIELD describes,
#: and the one value of it that makes that version a KLayout engine release.
ENGINE_KIND_FIELD = "engine"
KLAYOUT_ENGINE = "klayout"

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
    grader: bool = False


@dataclass(frozen=True)
class Recording:
    """One recorded KLayout engine release in one committed report."""

    path: str
    #: Dotted JSON path of the field, e.g. ``$.provenance.klayout_version``.
    field: str
    version: str


def read_pins(root: Path) -> dict[str, str]:
    """The pinned version per package, read from PIN_SOURCE's constants.

    Parsed (not imported) so that a synthetic tree can be checked and so
    that a non-literal assignment is caught rather than evaluated.
    """
    source = root / PIN_SOURCE
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    found: dict[str, str] = {}
    wanted = set(PIN_CONSTANTS.values()) | {GRADER_CONSTANT}
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
    missing = sorted(wanted - {GRADER_CONSTANT} - found.keys())
    if missing:
        raise ValueError(f"{PIN_SOURCE}: missing {', '.join(missing)}")
    pins: dict[str, str | None] = {"klayout-tools": None}
    pins.update({pkg: found[const] for pkg, const in PIN_CONSTANTS.items()})
    if GRADER_CONSTANT in found:
        pins[GRADER_KEY] = found[GRADER_CONSTANT]
    return pins


def is_scanned(rel: str) -> bool:
    if rel.startswith(EXCLUDED_PREFIXES):
        return False
    if rel.startswith(WORKFLOW_DIR):
        return rel.endswith((".yml", ".yaml"))
    return rel.endswith((".md", ".py"))


def tracked_files(root: Path) -> list[str]:
    return sorted(p for p in _git_files.tracked_files(root) if is_scanned(p))


def find_mentions(rel: str, text: str) -> list[Mention]:
    mentions = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        marked = MARKER in line
        grader = GRADER_MARKER in line
        for m in _PIN.finditer(line):
            mentions.append(Mention(rel, lineno, m.group(1), m.group(2),
                                    marked, grader))
    return mentions


def marker_lines(text: str, marker: str = MARKER) -> list[int]:
    return [n for n, line in enumerate(text.splitlines(), start=1)
            if marker in line]


def check_text(rel: str, text: str, pins: dict[str, str | None]
               ) -> tuple[list[Mention], list[str]]:
    """Every pin mention in one file, and the diagnostics for it."""
    mentions = find_mentions(rel, text)
    problems = []
    exempted_lines = set()
    grader_lines = set()
    for m in mentions:
        want = pins[m.package]
        if m.grader and m.package == "klayout-tools":
            grader_lines.add(m.line)
            want = pins.get(GRADER_KEY, want)
        if want is not None and m.version == want:
            continue
        if m.marked:
            exempted_lines.add(m.line)
            continue
        if want is None:
            problems.append(
                f"{rel}:{m.line}: {m.package}=={m.version}: the producer klt "
                f"is not pinned here (it tracks the fleet version; records "
                f"name their own producer). Write the install line without "
                f"==, or mark a narrated older build with '{MARKER}'"
                + ("" if m.grader else f"; a line restating the grader carries '{GRADER_MARKER}'")
                + ")")
            continue
        problems.append(
            f"{rel}:{m.line}: {m.package}=={m.version}, but {PIN_SOURCE} "
            f"pins {m.package}=={want} (update it, or mark a "
            f"deliberately historical line with '{MARKER}'"
            + ("" if m.grader else f"; a line restating the grader carries '{GRADER_MARKER}'")
            + ")")
    # A marker must be earning its keep.
    if rel != _SELF_REL:
        for line in marker_lines(text):
            if line not in exempted_lines:
                problems.append(
                    f"{rel}:{line}: '{MARKER}' marker exempts no "
                    f"mismatching pin on its line; remove it")
        for line in marker_lines(text, GRADER_MARKER):
            if line not in grader_lines:
                problems.append(
                    f"{rel}:{line}: '{GRADER_MARKER}' marker is on a line "
                    f"with no klayout-tools== mention; remove it")
    return mentions, problems


def is_report(rel: str) -> bool:
    """A git-tracked JSON report the recorded-engine scan covers."""
    return rel.startswith(REPORT_PREFIX) and rel.endswith(".json")


def report_files(root: Path) -> list[str]:
    return sorted(p for p in _git_files.tracked_files(root) if is_report(p))


def find_recordings(rel: str, node, field: str = "$") -> list[Recording]:
    """Every recorded KLayout engine release in one parsed report.

    ``klayout_version`` counts wherever it appears. ``engine_version``
    counts only inside an object whose own ``engine`` field says
    ``klayout`` -- the same field names an OpenROAD or OpenSTA build in
    `layout/digital/reports/`, and KLAYOUT_PIN does not speak for those.

    A field that matches is recorded whatever its value: a report whose
    `klayout_version` is `null` has not recorded the pinned engine either,
    and must not pass by being the wrong JSON type.
    """
    found: list[Recording] = []
    if isinstance(node, dict):
        klayout_engine = node.get(ENGINE_KIND_FIELD) == KLAYOUT_ENGINE
        for key, value in node.items():
            child = f"{field}.{key}"
            if key == ENGINE_FIELD or (key == GENERIC_ENGINE_FIELD
                                       and klayout_engine):
                found.append(Recording(
                    rel, child,
                    value if isinstance(value, str) else json.dumps(value)))
            else:
                found += find_recordings(rel, value, child)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            found += find_recordings(rel, value, f"{field}[{i}]")
    return found


def check_report(rel: str, text: str, pins: dict[str, str | None]
                 ) -> tuple[list[Recording], list[str]]:
    """Every recorded engine in one report, and the diagnostics for it."""
    want = pins["klayout"]
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return [], [f"{rel}: not valid JSON ({exc})"]
    recordings = find_recordings(rel, payload)
    problems = [
        f"{rel}: {r.field} records the KLayout engine as {r.version}, but "
        f"{PIN_SOURCE} pins klayout=={want}. Regenerate the report with the "
        f"pinned engine (pip install \"klayout-tools\" \"klayout=={want}\"), "
        f"or move the pin in {PIN_SOURCE} with a decision record"
        for r in recordings if r.version != want
    ]
    return recordings, problems


def check_tree(root: Path) -> tuple[dict[str, str | None], list[Mention],
                                    list[Recording], list[str]]:
    """Both halves of the contract: restated pins, then recorded engines."""
    pins = read_pins(root)
    mentions: list[Mention] = []
    recordings: list[Recording] = []
    problems: list[str] = []
    for rel in tracked_files(root):
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        found, bad = check_text(rel, text, pins)
        mentions += found
        problems += bad
    for rel in report_files(root):
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        recorded, bad = check_report(rel, text, pins)
        recordings += recorded
        problems += bad
    return pins, mentions, recordings, problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any restated pin disagrees")
    ap.add_argument("--root", type=Path, default=REPO_ROOT,
                    help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    try:
        pins, mentions, recordings, problems = check_tree(
            args.root.resolve())
    except (OSError, ValueError, SyntaxError,
            _git_files.GitError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    for pkg, version in pins.items():
        if version is None:
            print(f"unpinned: {pkg} (tracks the fleet version; DR-0026 amendment 2026-11-09)")
            continue
        const = GRADER_CONSTANT if pkg == GRADER_KEY else PIN_CONSTANTS[pkg]
        name = "klayout-tools (grader)" if pkg == GRADER_KEY else pkg
        print(f"pinned: {name}=={version}  ({PIN_SOURCE} {const})")
    for m in mentions:
        tag = " [historical]" if m.marked else (" [grader]" if m.grader else "")
        print(f"  {m.path}:{m.line}: {m.package}=={m.version}{tag}")
    print(f"recorded engine in {REPORT_PREFIX}**/*.json "
          f"({len(recordings)} field(s)):")
    for r in recordings:
        print(f"  {r.path}: {r.field} = {r.version}")
    if not args.check:
        return 0
    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        return 1
    print(f"OK: {len(mentions)} pin mentions and {len(recordings)} recorded "
          f"engine field(s) agree with {PIN_SOURCE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
