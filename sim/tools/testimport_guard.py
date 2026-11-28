#!/usr/bin/env python3
"""Fail on a sim/tests module that does not import from the repository root (#1085).

The documented single-file form

    python3 -m unittest sim/tests/<file>.py

imports the file as ``sim.tests.<name>`` (Python 3.12). That import does
not put ``sim/tests`` on ``sys.path``, so a test module that imports a
sibling (``_record_golden``, ``_tool_gate``, ``_fake_store``, ...) has to
put the directory on ``sys.path`` itself, at module level. ``npm test``
does not notice a module that forgot to:
``unittest discover -s sim/tests -t sim/tests`` adds that directory for
every module. That is how four modules reached ``main`` broken under the
root-level form with every suite green (#1082).

This check, wired into `npm run lint`, imports every tracked
``sim/tests/test_*.py`` as ``sim.tests.<name>`` from the repository root,
the way that command does, and fails naming every module whose import
raises. Importing a module runs its module-level code only; no test runs.

Each module is imported by its own interpreter, started with ``-I`` so that
an ambient ``PYTHONPATH`` or user site directory cannot stand in for a
missing insert. One shared process would be order-dependent: the first
module to insert ``sim/tests`` into ``sys.path`` makes every later sibling
import succeed. Measured on ``main`` before #1084 landed (``a1a30e27``): one
process reported 96 of 96 modules importable where the per-module form
failed 4. Inside the child the module's stdout is sent to stderr, so a
module that prints at import cannot be mistaken for the child's verdict.

  python3 -m sim.tools.testimport_guard --check
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from sim.tools._git_files import GitError, tracked_files

ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = "sim/tests"
PACKAGE = "sim.tests"

#: Seconds a module's import may take before it is reported as not
#: finished. The slowest module of the tree this was written for imports in
#: about 0.1 s.
TIMEOUT_S = 30.0

#: First field of the child's verdict line, which is the last line of the
#: child's stdout: tag, ``ok`` or ``fail``, exception type, line number in
#: the module (empty if none), message.
TAG = "TESTIMPORT_GUARD"
FIELDS = 5

#: Run as ``python3 -I -c PROBE <tag> <root> <module>``.
PROBE = """\
import contextlib, importlib, sys, traceback

tag, root, name = sys.argv[1:4]
sys.path.insert(0, root)
status, kind, line, message = "ok", "", "", ""
try:
    with contextlib.redirect_stdout(sys.stderr):
        importlib.import_module(name)
except BaseException as exc:
    status = "fail"
    kind = type(exc).__name__
    if isinstance(exc, SyntaxError):
        message = exc.msg
    else:
        message = " ".join(str(exc).split())[:200]
    for frame, _ in traceback.walk_tb(exc.__traceback__):
        if frame.f_globals.get("__name__") == name:
            line = str(frame.f_lineno)
            break
    if not line and isinstance(exc, SyntaxError):
        line = str(exc.lineno or "")
print("\\t".join((tag, status, kind, line, message)))
sys.exit(0 if status == "ok" else 1)
"""


def probe(root: Path, module: str, timeout: float = TIMEOUT_S) -> str | None:
    """Import ``module`` in a fresh interpreter with ``root`` on ``sys.path``.

    Returns ``None`` when the import succeeds, else what follows the module's
    path in its finding: ``:<line>: <type>: <message>`` for an exception
    raised while importing, or ``: <why>`` when no verdict was obtained.
    """
    root = Path(root).resolve()
    cmd = [sys.executable, "-I", "-c", PROBE, TAG, str(root), module]
    try:
        proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True,
                              errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return f": import did not finish within {timeout:g} s"
    except OSError as exc:
        return f": cannot start {sys.executable}: {exc}"
    stdout = proc.stdout.rstrip("\n")
    verdict = stdout.rsplit("\n", 1)[-1] if stdout.strip() else ""
    fields = verdict.split("\t")
    if len(fields) != FIELDS or fields[0] != TAG:
        return (f": import process exited with status {proc.returncode} "
                f"without reporting a verdict")
    if fields[1] == "ok":
        return None
    line = f":{fields[3]}" if fields[3] else ""
    message = f": {fields[4]}" if fields[4] else ""
    return f"{line}: {fields[2]}{message}"


def test_modules(files: list[str]) -> list[tuple[str, str]]:
    """``(path, module)`` for the ``sim/tests/test_*.py`` entries of a tracked
    listing, sorted by module name so the output does not follow git's
    order. Only direct children map to ``sim.tests.<name>``."""
    out = []
    for rel in files:
        path = Path(rel)
        if (path.parent == Path(TESTS_DIR) and path.name.startswith("test_")
                and path.suffix == ".py"):
            out.append((rel, f"{PACKAGE}.{path.stem}"))
    return sorted(out)


def check(root: Path, files: list[str], timeout: float = TIMEOUT_S) -> list[str]:
    """Findings: one line per test module in ``files`` that does not import
    from ``root`` as ``sim.tests.<name>``."""
    found = []
    for rel, module in test_modules(files):
        problem = probe(root, module, timeout)
        if problem is not None:
            found.append(f"{rel}{problem}")
    return found


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", required=True)
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)

    try:
        files = tracked_files(args.root, TESTS_DIR)
    except GitError as exc:
        print(f"testimport_guard: {exc}", file=sys.stderr)
        return 2
    targets = test_modules(files)
    if not targets:
        print(f"testimport_guard: no tracked {TESTS_DIR}/test_*.py under "
              f"{args.root}", file=sys.stderr)
        return 2
    found = check(args.root, files)
    for line in found:
        print(line, flush=True)
    if found:
        print(f"testimport_guard: {len(found)} of {len(targets)} module(s) "
              f"do not import from the repository root as {PACKAGE}.<name>. "
              f"`python3 -m unittest {TESTS_DIR}/<file>.py` imports each file "
              f"that way, so a module must put every directory its sibling "
              f"imports need on sys.path itself (#1082)", file=sys.stderr)
        return 1
    print(f"testimport_guard: OK ({len(targets)} module(s) imported from the "
          f"repository root)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
