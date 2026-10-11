#!/usr/bin/env python3
"""Stop hand-copied path-based module loaders from coming back (#553).

`sim/tools/pathload.py` owns the one correct way to load a file by path
(`load_module_from_path`: registers in `sys.modules` before executing, undoes
it on failure). This check, wired into `npm run lint`, fails when a tracked
first-party file other than that helper references
`importlib.util.spec_from_file_location`.

`ALLOWLIST` is the set of files that have not been migrated yet. It must list
exactly the unmigrated files: a file that still uses the pattern but is not
listed is a new copy (fail), and a listed file that no longer uses it is a
stale entry (fail, delete the line). The list only shrinks.

Detection is by AST (a call or reference to the name), so a docstring or
comment that merely mentions the function is not a finding.

  python3 -m sim.tools.pathload_guard --check
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from sim.tools.unused_names import ROOT, select_files, tracked_files

HELPER = "sim/tools/pathload.py"
NAME = "spec_from_file_location"

#: Unmigrated files (issue #553, batches 2 and 3: layout/tests, sim/tests).
ALLOWLIST = frozenset({
    "layout/tests/test_block_geometry.py",
    "layout/tests/test_digital_build_checks.py",
    "layout/tests/test_digital_lvs_reference.py",
    "layout/tests/test_digital_reports.py",
    "layout/tests/test_digital_tap_distance.py",
    "layout/tests/test_floorplan_erc.py",
    "layout/tests/test_floorplan_netlist.py",
    "layout/tests/test_gdsii.py",
    "layout/tests/test_gen_sdf.py",
    "layout/tests/test_mos_row.py",
    "layout/tests/test_synth.py",
    "layout/tests/test_tap_distance_ci_wiring.py",
    "layout/tests/test_verify.py",
})


def uses_loader(source: str, path: str = "<source>") -> bool:
    """True when `source` references `spec_from_file_location` in code."""
    for node in ast.walk(ast.parse(source, filename=path)):
        if isinstance(node, ast.Attribute) and node.attr == NAME:
            return True
        if isinstance(node, ast.Name) and node.id == NAME:
            return True
        if isinstance(node, ast.alias) and node.name == NAME:
            return True
    return False


def problems(users: set[str], allowlist: frozenset[str] = ALLOWLIST,
             helper: str = HELPER) -> list[str]:
    """Findings for the set of files that use the raw loader."""
    users = users - {helper}
    out = [f"{p}: hand-copied spec_from_file_location; use "
           f"load_module_from_path from {helper}"
           for p in sorted(users - allowlist)]
    out += [f"{p}: stale pathload_guard ALLOWLIST entry (no longer uses "
            f"spec_from_file_location); delete it"
            for p in sorted(allowlist - users)]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", required=True)
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)

    files = select_files(tracked_files(args.root))
    users = set()
    for rel in files:
        try:
            src = (args.root / rel).read_text(encoding="utf-8")
            if uses_loader(src, rel):
                users.add(rel)
        except (OSError, SyntaxError, UnicodeDecodeError) as exc:
            print(f"pathload_guard: cannot scan {rel}: {exc}", file=sys.stderr)
            return 2
    found = problems(users)
    for line in found:
        print(line)
    if found:
        print(f"pathload_guard: {len(found)} finding(s)", file=sys.stderr)
        return 1
    print(f"pathload_guard: OK ({len(files)} file(s) scanned, "
          f"{len(ALLOWLIST)} allowlisted)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
