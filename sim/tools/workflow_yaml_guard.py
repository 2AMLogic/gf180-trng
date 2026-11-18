#!/usr/bin/env python3
"""Fail on the workflow YAML trap that produces a zero-job startup failure.

A plain ``name:`` mapping value that contains ``": "`` -- or ends in ``:`` --
is read by every YAML parser as the start of a nested mapping ("mapping
values are not allowed here"). A .github/workflows file with one fails to
parse before any job is defined: the run is a startup failure with zero
jobs, no required context ever reports, and nothing in the local gate
notices, because the workflow is the thing that runs the gate (issue #1003,
measured on a PR head whose whole local check chain was green).

This guard, wired into `npm run lint`, flags that defect class by line
scanning over the tracked workflow files. It is not a YAML parser and
claims no coverage beyond it: only plain (unquoted, non-block) values of
mapping keys named exactly ``name`` are examined. Quoted values, block
scalars (``|``/``>``), flow collections, anchors and aliases, ``#`` comments
and ``://`` URL colons are left alone -- a document that parses cannot
contain a plain ``name:`` value with ``": "`` in it, so a finding is always
a file that does not parse.

A line opens a block scalar only when the value after the line's FIRST
colon -- the key's own -- is exactly a block indicator: ``run: |``,
``- name: >-``, ``- - run: |`` at any sequence depth (bounded by the key's
column, where the mapping's sibling keys live), or a quoted/flow key by
shape (``"a: b": |``, whose colons are its own). A plain value that merely
ends in an indicator (``name: build a: |``) is therefore a member of the
defect class and is scanned, not opened as a block (issue #1011).

  python3 -m sim.tools.workflow_yaml_guard --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from sim.tools._git_files import GitError, tracked_files

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = ".github/workflows"

# A mapping key named exactly `name` with its value: `name: v`, `- name: v`,
# `- - name: v`. Indented to any depth, at any sequence-dash depth, the dash
# needs a following space (`-name:` is a different, invalid key), and spaces
# before the colon are legal YAML (`name : v`).
NAME_KEY = re.compile(r"^[ \t]*(?:-[ \t]+)*name[ \t]*:(?P<value>.*)$")

# Block scalar header after a key colon or a sequence dash: `|`, `>-`,
# `|2`, `|2-`, `>-+`, ... (indent indicator digit and chomping indicator in
# either order).
BLOCK_HDR = r"[|>](?:\d?[+-]?|[+-]?\d)?"

# A line whose value after its FIRST colon -- the key's own, since the key
# and the dash lead cannot contain one -- is exactly a block header:
# `run: |`, `- name: >-`, `- - run: |`, any depth of sequence dashes.
# Anchored there, `name: build a: |` is NOT a header: its value is the
# plain scalar `build a: |`, a member of the defect class, so the line is
# scanned below instead of opening a block. `lead` ends at the key's
# column, where the sibling keys of the same mapping live -- the indent a
# line must dedent to before it is scanned again.
KEY_BLOCK = re.compile(
    rf"^(?P<lead>[ \t]*(?:-[ \t]+)*)(?P<key>[^ \t:][^:]*?)[ \t]*:"
    rf"(?P<value>[ \t]*{BLOCK_HDR})$"
)

# Quoted and flow keys (`"a: b": |`) carry colons of their own, so the
# first colon on the line is not the key separator; recognized by shape so
# their block bodies are still skipped. A plain key never starts with a
# quote or a flow indicator, so this never masks a defective plain value.
QUOTED_KEY_BLOCK = re.compile(
    rf'^(?P<lead>[ \t]*(?:-[ \t]+)*)'
    rf'(?P<key>"[^"]*"|\'[^\']*\'|\{{.*\}}|\[.*\])[ \t]*:'
    rf"(?P<value>[ \t]*{BLOCK_HDR})$"
)

# A sequence item that is itself a block scalar -- `- |`, `- - >` -- with
# no key. `dash` is bounded at the innermost dash's column.
BARE_BLOCK = re.compile(rf"^(?P<dash>[ \t]*(?:-[ \t]+)+){BLOCK_HDR}$")


def strip_comment(line: str) -> str:
    """Cut the line at the first ``#`` that starts a YAML comment.

    A ``#`` begins a comment at line start or when preceded by whitespace;
    a ``#`` glued to a preceding character is plain-scalar content
    (``http://x#y``).
    """
    cut = len(line)
    for i, ch in enumerate(line):
        if ch == "#" and (i == 0 or line[i - 1] in " \t"):
            cut = i
            break
    return line[:cut]


def plain_defect(value: str) -> bool:
    """True when a plain scalar value would parse as a nested mapping.

    ``value`` is the comment-stripped, whitespace-stripped text after the
    key colon. Quoted values, block scalar and flow headers, and aliases
    are fine; an anchored value is inspected after its ``&anchor`` token.
    """
    if not value or value[0] in "\"'":
        return False
    if value[0] in "|>[{*":
        return False
    if value[0] == "&":
        parts = value.split(None, 1)
        return plain_defect(parts[1]) if len(parts) == 2 else False
    return ": " in value or value.endswith(":")


def finding_message(path: str, lineno: int, value: str) -> str:
    tail = 'ends in ":"' if value.endswith(":") else 'contains ": "'
    return (f"{path}:{lineno}: - name value {tail} -- YAML reads it as a "
            f"nested mapping, so the workflow fails to parse (zero-job "
            f"startup failure); quote the value or use a block scalar "
            f"(issue #1003): {value.strip()!r}")


def findings(text: str, path: str = "<doc>") -> list[str]:
    """File:line findings for the ``name:``-scalar trap in ``text``."""
    out: list[str] = []
    block_indent: int | None = None
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip()
        indent = len(line) - len(line.lstrip(" "))
        if block_indent is not None:
            # Inside a block scalar: blank lines and deeper-indented lines
            # are literal content; the first line dedented to the key's
            # indent (or less) ends the block and is processed normally.
            if not line.strip() or indent > block_indent:
                continue
            block_indent = None
        stripped = strip_comment(line).rstrip()
        hdr = KEY_BLOCK.match(stripped) or QUOTED_KEY_BLOCK.match(stripped)
        if hdr:
            # `run: |` / `- name: >-` / `- - run: |`: the block is bounded
            # by the key's column -- after every sequence dash -- where the
            # sibling keys of the same mapping live.
            block_indent = len(hdr.group("lead"))
            continue
        bare = BARE_BLOCK.match(stripped)
        if bare:
            # Bare `- |` item: the block is bounded by the innermost
            # dash's column.
            block_indent = len(bare.group("dash").rstrip()) - 1
            continue
        m = NAME_KEY.match(stripped)
        if not m:
            continue
        value = m.group("value")
        # `name:foo` is a longer key, not a `name` mapping: the mapping form
        # needs whitespace after the colon (or nothing at all).
        if value and value[0] not in " \t":
            continue
        if plain_defect(value.strip()):
            out.append(finding_message(path, lineno, value))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", required=True)
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)

    try:
        files = [f for f in tracked_files(args.root, WORKFLOW_DIR)
                 if f.endswith((".yml", ".yaml"))]
    except GitError as exc:
        print(f"workflow_yaml_guard: {exc}", file=sys.stderr)
        return 2
    found: list[str] = []
    for rel in files:
        try:
            text = (args.root / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"workflow_yaml_guard: cannot read {rel}: {exc}",
                  file=sys.stderr)
            return 2
        found += findings(text, rel)
    for line in found:
        print(line)
    if found:
        print(f"workflow_yaml_guard: {len(found)} finding(s)", file=sys.stderr)
        return 1
    print(f"workflow_yaml_guard: OK ({len(files)} workflow file(s) scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
