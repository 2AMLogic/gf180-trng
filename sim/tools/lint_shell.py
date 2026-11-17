#!/usr/bin/env python3
"""Run shellcheck over the tracked first-party shell scripts (#591).

`bash -n` only catches parse errors; shellcheck (warning severity) also finds
unquoted expansions, unchecked `cd`, masked exit statuses and similar.

File selection is tracked `*.sh` files, plus tracked files under
`.github/scripts/` whose first line is a shell shebang (`^#!.*\\b(ba)?sh\\b`,
e.g. `#!/usr/bin/env bash`) — an executable script without a `.sh` extension
is invisible to a suffix-only rule (#993). Both sets minus the vendored
`.loom/` and `.claude/` trees. When shellcheck is not installed the step
prints a clear "shellcheck unavailable" message and exits 0, unless
`--require-tools` is given, in which case it exits 1 (the repo's usual
skip-vs-fail convention).

  python3 -m sim.tools.lint_shell                  # skip if unavailable
  python3 -m sim.tools.lint_shell --require-tools  # fail if unavailable
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _git_files  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
VENDORED_PREFIXES = (".loom/", ".claude/")
SEVERITY = "warning"
SHELL_SHEBANG_RE = re.compile(r"^#!.*\b(ba)?sh\b")


def read_first_line(path: str, root: Path = ROOT) -> str:
    """First line of a repo file, or ``""`` when empty or unreadable."""
    try:
        with open(root / path, encoding="utf-8", errors="replace") as fh:
            return fh.readline()
    except OSError:
        return ""


def select_scripts(tracked: list[str],
                   first_line: Callable[[str], str] | None = None) -> list[str]:
    """Tracked first-party shell scripts, sorted.

    A path is selected when it ends in ``.sh`` or its first line is a shell
    shebang, so extension-less scripts such as the ``.github/scripts/``
    helpers are covered too. Vendored trees are always excluded.
    """
    read = read_first_line if first_line is None else first_line
    return sorted(p for p in tracked
                  if not p.startswith(VENDORED_PREFIXES)
                  and (p.endswith(".sh") or SHELL_SHEBANG_RE.match(read(p) or "")))


def tracked_files() -> list[str]:
    return _git_files.tracked_files(ROOT, "*.sh", ".github/scripts/*")


def run(require_tools: bool, which=shutil.which, files=None) -> int:
    exe = which("shellcheck")
    if exe is None:
        if require_tools:
            print("FAIL: shellcheck unavailable and --require-tools was given")
            return 1
        print("SKIP: shellcheck unavailable; shell lint not run "
              "(pass --require-tools to fail instead)")
        return 0
    try:
        scripts = select_scripts(tracked_files() if files is None else files)
    except _git_files.GitError as exc:
        print(f"FAIL: {exc}")
        return 1
    if not scripts:
        print("FAIL: no tracked shell scripts found; file selection is broken")
        return 1
    rc = subprocess.run([exe, f"--severity={SEVERITY}", *scripts],
                        cwd=ROOT).returncode
    if rc == 0:
        print(f"shellcheck: {len(scripts)} script(s) clean at "
              f"{SEVERITY} severity")
    return 1 if rc else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--require-tools", action="store_true",
                    help="fail instead of skipping when shellcheck is absent")
    return run(ap.parse_args(argv).require_tools)


if __name__ == "__main__":
    sys.exit(main())
