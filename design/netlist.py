#!/usr/bin/env python3
"""Deterministic SPICE export of the xschem schematics in ``design/xschem/``.

    python3 design/netlist.py            # (re-)export every top cell
    python3 design/netlist.py --check    # export to a temp dir and diff; never writes
    python3 design/netlist.py --lint     # brace-in-T{}-block guard only; no xschem/PDK

``--check`` is the staleness guard: it fails if the committed ``.spice``
netlist does not match what the current schematics produce. That is what
makes a committed netlist evidence rather than a snapshot someone forgot to
refresh -- ``sim/README.md`` records a ``netlist.sha`` in every evidence
record, and that SHA is only meaningful if the netlist provably comes from
the schematic it claims to.

Text-block brace guard
-----------------------
Every schematic carries one or more ``T {...}`` free-text elements -- the
prose headers that document each cell's rationale. That block has no
electrical meaning, but xschem's own line/element parser miscounts when the
block's *content* contains a literal ``{`` or ``}`` character, even a
balanced pair, and silently drops parts of the exported netlist with no
error from xschem or from this script (#61). ``--lint`` (and every other
invocation of this script, which runs the same guard before shelling out to
xschem) scans every ``design/xschem/*.sch`` file's text directly for stray
braces inside ``T {...}`` blocks. That scan is pure Python over the
schematic's own text -- no xschem, no PDK -- so unlike ``--check`` it can run
in the PR-blocking CI job, catching the problem at the point of authorship
instead of the next scheduled ``pdk-nightly.yml`` run.

Determinism
-----------
xschem writes absolute filesystem paths into the netlist header comments
(``** sch_path:``/``** sym_path:``) and resolves the PDK symbol library
through an rc file. Both are machine-specific, so this script:

* generates the xschem rc file itself, resolving the gf180mcu PDK through
  the same chain ``sim/harness/pdk.py`` uses (``GF180_PDK_PATH`` /
  ``PDK_ROOT`` + ``PDK`` / ``sim/pdk.local.json`` / ``sim/pdk.json`` /
  built-in search roots), so nothing here hardcodes a path; and
* rewrites every absolute path in the output to a repo-relative one; and
* re-wraps every SPICE continuation (``+``) line itself, at a width this
  file owns, instead of inheriting xschem's. Line *breaks* carry no
  circuit meaning -- a continuation is glued back on by any SPICE parser --
  but they are the part of xschem's output that has actually moved between
  releases. xschem 3.4.4 emits a device line broken after ``as=``; 3.4.7
  reflows the same tokens and breaks after ``pd=``. Same netlist, different
  bytes, and ``--check`` cannot tell that apart from a real schematic edit.
  Canonicalising the wrap here removes the whole class of difference, so
  the guard fires on circuit changes and only on circuit changes.

The result is byte-identical on any machine with the same PDK symbol set,
across xschem releases that differ only in line-wrapping. A change in what
xschem actually *emits* -- different tokens, different hierarchy -- still
makes ``--check`` say so loudly rather than letting the netlist and the
schematic drift apart silently.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DESIGN_DIR = REPO_ROOT / "design"
SCHEMATIC_DIR = DESIGN_DIR / "xschem"

#: Schematics exported as stand-alone netlists. Cells not listed here are
#: still netlisted, but only as subcircuits inside a top cell that uses them.
#:
#: A cell earns a place here when a testbench needs to instantiate it
#: directly, because ``sim/README.md``'s ``netlist.path``/``netlist.sha``
#: should name the netlist that defines the DUT and nothing more. That is
#: why ``meta_arb`` and ``ro_meta_tap`` are exported separately from
#: ``ro_array_core_meta``: they are characterized on their own, and a
#: record that pointed at the whole array netlist would overstate what was
#: simulated.
TOP_CELLS = (
    "meta_arb",
    "ro_array_core",
    "ro_array_core_meta",
    "ro_array_sanity",
    "ro_meta_tap",
    "sampler_core",
)

XSCHEM = "xschem"

#: Column at which this script re-wraps SPICE continuation lines. Any value
#: works as long as it is fixed here rather than inherited from xschem --
#: see the module docstring. 120 keeps device lines to roughly the shape
#: xschem 3.4.4 produced, so the committed netlists stay readable diffs.
WRAP_COLUMN = 120

EXIT_OK = 0
EXIT_STALE = 1
EXIT_ENVIRONMENT = 3


class ExportError(RuntimeError):
    pass


def _display_path(path: Path) -> str:
    """*path* relative to :data:`REPO_ROOT` when possible, else as given.

    Schematics under :data:`SCHEMATIC_DIR` always resolve relative to the
    repo; a fixture schematic under a test's own temp directory (see
    ``sim/tests/test_netlist_export.py``) does not, and should still print
    something readable rather than raising.
    """
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _text_block_violations(text: str) -> list[tuple[int, str]]:
    """Find stray braces inside every ``T {...}`` free-text block of *text*.

    Returns a list of ``(line_number, message)`` pairs, in document order.

    This walks the schematic's raw text with a simple brace-depth counter
    rather than trying to reproduce whatever xschem's own parser does --
    that parser is exactly what miscounts here (#61). Depth starts at 1 right
    after a line-initial ``T {``; any ``{`` or ``}`` seen while depth is
    already >= 1 is, by construction, inside the block's content, so it is
    flagged unconditionally -- a balanced nested pair corrupts xschem's
    export just as surely as an unbalanced one, so this guard does not try
    to distinguish them. The counter still lets it find the block's true
    (depth == 0) end, so a single scan both locates the block and flags
    every stray brace inside it.
    """
    violations: list[tuple[int, str]] = []
    i = 0
    n = len(text)
    line = 1
    while i < n:
        if text.startswith("T {", i) and (i == 0 or text[i - 1] == "\n"):
            block_start_line = line
            j = i + len("T {")
            depth = 1
            while j < n and depth > 0:
                ch = text[j]
                if ch == "\n":
                    line += 1
                if ch == "{":
                    depth += 1
                    if depth > 1:
                        violations.append((line, "stray '{' inside a T {...} text block"))
                elif ch == "}":
                    depth -= 1
                    if depth > 0:
                        violations.append((line, "stray '}' inside a T {...} text block"))
                j += 1
            if depth != 0:
                violations.append(
                    (block_start_line, "T {...} text block starting here never closes")
                )
            i = j
            continue
        if text[i] == "\n":
            line += 1
        i += 1
    return violations


def text_block_violations(schematic: Path) -> list[tuple[int, str]]:
    """``_text_block_violations`` over one schematic file's committed text."""
    return _text_block_violations(schematic.read_text())


def lint_schematics(paths: list[Path] | None = None) -> int:
    """Fail loudly if any schematic has a stray brace in a ``T {...}`` block.

    Pure Python over the schematics' own text: no xschem, no PDK. *paths*
    defaults to every ``design/xschem/*.sch`` file.
    """
    status = EXIT_OK
    for schematic in paths if paths is not None else sorted(SCHEMATIC_DIR.glob("*.sch")):
        rel = _display_path(schematic)
        for lineno, message in text_block_violations(schematic):
            print(f"BRACE  {rel}:{lineno}: {message}")
            status = EXIT_STALE
    if status == EXIT_OK:
        print(f"ok     no stray braces in any T {{...}} text block under {_display_path(SCHEMATIC_DIR)}")
    return status


def _pdk_symbol_dir() -> Path:
    """The gf180mcu xschem symbol library, resolved like the sim harness does."""
    sys.path.insert(0, str(REPO_ROOT / "sim"))
    try:
        from harness.pdk import PdkNotFound, find_pdk  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - repo layout is fixed
        raise ExportError(f"cannot import the sim harness PDK resolver: {exc}") from exc
    try:
        pdk = find_pdk()
    except PdkNotFound as exc:
        raise ExportError(str(exc)) from exc
    symbols = pdk.path / "libs.tech" / "xschem" / "symbols"
    if not symbols.is_dir():
        raise ExportError(
            f"{pdk.path} has no libs.tech/xschem/symbols directory -- this PDK "
            "install does not carry the xschem symbol library"
        )
    return symbols


def _write_rcfile(target: Path, symbol_dir: Path, netlist_dir: Path) -> None:
    target.write_text(
        "# generated by design/netlist.py -- do not edit, do not commit\n"
        "set XSCHEM_LIBRARY_PATH {}\n"
        "append XSCHEM_LIBRARY_PATH :${XSCHEM_SHAREDIR}/xschem_library/devices\n"
        f"append XSCHEM_LIBRARY_PATH :{symbol_dir}\n"
        f"append XSCHEM_LIBRARY_PATH :{SCHEMATIC_DIR}\n"
        f"set netlist_dir {netlist_dir}\n"
        "set netlist_type spice\n"
        "set hspice_netlist 0\n"
    )


def _tokens(line: str) -> list[str]:
    """Split a SPICE line on whitespace, keeping quoted expressions whole.

    ``ad='int((nf+1)/2) * W/nf * 0.18u'`` is one token even though it
    contains spaces: breaking a line inside it would produce a netlist that
    no longer parses.
    """
    out: list[str] = []
    current: list[str] = []
    quote = ""
    for char in line:
        if quote:
            current.append(char)
            if char == quote:
                quote = ""
        elif char in "'\"":
            quote = char
            current.append(char)
        elif char.isspace():
            if current:
                out.append("".join(current))
                current = []
        else:
            current.append(char)
    if current:
        out.append("".join(current))
    return out


def _rewrap(line: str) -> list[str]:
    """Re-wrap one logical SPICE line at :data:`WRAP_COLUMN`.

    Greedy, and deliberately so: the rule has to be reproducible by reading
    this function, not by matching a particular xschem release's output.
    A token longer than the column is emitted on its own line rather than
    split, because splitting it would change the netlist.
    """
    tokens = _tokens(line)
    if not tokens:
        return [line]
    wrapped: list[str] = []
    current = tokens[0]
    for token in tokens[1:]:
        candidate = f"{current} {token}"
        if len(candidate) <= WRAP_COLUMN:
            current = candidate
            continue
        wrapped.append(current)
        current = f"+ {token}"
    wrapped.append(current)
    return wrapped


def _join_continuations(lines: list[str]) -> list[str]:
    """Glue ``+`` continuation lines back onto the line they continue."""
    joined: list[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("+") and joined:
            joined[-1] = f"{joined[-1]} {stripped[1:].strip()}".rstrip()
        else:
            joined.append(line)
    return joined


def _schematic_params(schematic: Path) -> str:
    """The top schematic's own parameter block (the xschem ``G {...}`` line).

    xschem treats a top schematic as a deck, so it drops that block from the
    ``.subckt`` line it comments out -- which leaves a parameterised top cell
    exporting instance lines that reference names nothing declares
    (``xtap ... cta=cta`` with no ``cta``). Restoring the block alongside the
    ``.subckt`` wrapper is the same fix, for the same reason: here the top
    cell IS a cell, and a testbench needs to override its parameters.
    """
    text = schematic.read_text()
    match = re.search(r"^G \{(.*?)\}\s*$", text, re.MULTILINE | re.DOTALL)
    if not match:
        return ""
    return " ".join(match.group(1).split())


def _normalize(text: str, top_params: str = "") -> str:
    """Make the netlist machine-independent and stable line-for-line."""
    out = []
    for line in text.splitlines():
        # xschem stamps absolute paths into header comments.
        line = re.sub(r"(?<=[ :])/[^\s]*/(?=[^/\s]+\.(?:sch|sym))", "", line)
        line = line.replace(str(REPO_ROOT) + "/", "")
        # The export is a library of subcircuits that a testbench deck
        # `.include`s, not a deck of its own: a bare `.end` would truncate
        # every deck that includes it. `.ends` is kept, obviously.
        if line.strip().lower() == ".end":
            continue
        # xschem comments out the TOP cell's own .subckt/.ends wrapper,
        # because from its point of view the top schematic is a deck rather
        # than a cell. Here the top cell is exactly what a testbench wants
        # to instantiate, so the wrapper is restored. Every lower-level cell
        # is already emitted uncommented and is untouched by this.
        if line.startswith("**.subckt ") or line.strip() == "**.ends":
            line = line[2:]
            if top_params and line.startswith(".subckt "):
                line = f"{line} {top_params}"
        out.append(line.rstrip())
    while out and not out[-1]:
        out.pop()
    reflowed: list[str] = []
    for line in _join_continuations(out):
        if line.startswith("*") or not line.strip():
            reflowed.append(line)
        else:
            reflowed.extend(_rewrap(line))
    return "\n".join(reflowed) + "\n"


def export(top: str, outdir: Path) -> str:
    schematic = SCHEMATIC_DIR / f"{top}.sch"
    if not schematic.is_file():
        raise ExportError(f"no schematic {schematic}")
    # Refuse before ever invoking xschem: a stray brace in any schematic's
    # T {...} block corrupts xschem's own parse silently (#61), and `top`'s
    # export can pull in any other schematic in SCHEMATIC_DIR hierarchically,
    # so the whole directory is in scope here, not just `top`.sch.
    violations = [
        (sch, lineno, message)
        for sch in sorted(SCHEMATIC_DIR.glob("*.sch"))
        for lineno, message in text_block_violations(sch)
    ]
    if violations:
        detail = "\n".join(
            f"  {_display_path(sch)}:{lineno}: {message}" for sch, lineno, message in violations
        )
        raise ExportError(
            "stray brace(s) found in a T {...} text block -- xschem's own "
            "parser miscounts these and silently corrupts the exported "
            f"netlist (#61); run `python3 design/netlist.py --lint` for detail:\n{detail}"
        )
    if shutil.which(XSCHEM) is None:
        raise ExportError(
            "xschem not found on PATH.\n"
            "  Debian/Ubuntu: apt-get install xschem\n"
            "  or build from https://github.com/StefanSchippers/xschem"
        )
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        rcfile = tmpdir / "xschemrc"
        _write_rcfile(rcfile, _pdk_symbol_dir(), tmpdir)
        env = dict(os.environ)
        env.pop("XSCHEM_LIBRARY_PATH", None)
        proc = subprocess.run(
            [
                XSCHEM, "-n", "-q", "-x", "-s", "-r",
                "--rcfile", str(rcfile),
                "-o", str(tmpdir),
                "-N", f"{top}.spice",
                str(schematic),
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            env=env,
            check=False,
        )
        produced = tmpdir / f"{top}.spice"
        if not produced.is_file():
            raise ExportError(
                f"xschem produced no netlist for {top}\n"
                f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}"
            )
        text = _normalize(produced.read_text(), _schematic_params(schematic))
    header = (
        f"* {top} -- GENERATED by design/netlist.py from design/xschem/{top}.sch\n"
        "* Do not edit by hand: `python3 design/netlist.py --check` fails if this\n"
        "* file and the schematic disagree. Regenerate with `python3 design/netlist.py`.\n"
    )
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"{top}.spice").write_text(header + text)
    return header + text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="netlist.py",
        description="Export (or verify) the SPICE netlists of design/xschem/.",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="do not write: re-export and fail if the committed netlist is stale",
    )
    parser.add_argument(
        "--lint", action="store_true",
        help=(
            "only run the T {...} text-block brace guard over every schematic "
            "and exit; needs neither xschem nor the PDK (#61)"
        ),
    )
    parser.add_argument("--top", action="append", metavar="CELL", help="cell to export (repeatable)")
    args = parser.parse_args(argv)

    if args.lint:
        return lint_schematics()

    tops = tuple(args.top) if args.top else TOP_CELLS
    status = EXIT_OK
    for top in tops:
        committed = DESIGN_DIR / f"{top}.spice"
        try:
            if args.check:
                with tempfile.TemporaryDirectory() as tmp:
                    fresh = export(top, Path(tmp))
                if not committed.is_file():
                    print(f"STALE  {top}: {committed.relative_to(REPO_ROOT)} does not exist")
                    status = EXIT_STALE
                    continue
                current = committed.read_text()
                if current != fresh:
                    diff = difflib.unified_diff(
                        current.splitlines(True), fresh.splitlines(True),
                        fromfile=f"committed/{top}.spice", tofile=f"regenerated/{top}.spice",
                    )
                    print(f"STALE  {top}: committed netlist does not match the schematic")
                    sys.stdout.writelines(diff)
                    status = EXIT_STALE
                else:
                    print(f"ok     {top}: committed netlist matches design/xschem/{top}.sch")
            else:
                export(top, DESIGN_DIR)
                print(f"wrote  design/{top}.spice")
        except ExportError as exc:
            print(f"ERROR  {top}: {exc}", file=sys.stderr)
            return EXIT_ENVIRONMENT
    return status


if __name__ == "__main__":
    raise SystemExit(main())
