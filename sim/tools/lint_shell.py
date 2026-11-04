#!/usr/bin/env python3
"""Run shellcheck over the tracked first-party shell scripts (#591).

`bash -n` only catches parse errors; shellcheck (warning severity) also finds
unquoted expansions, unchecked `cd`, masked exit statuses and similar.

File selection is `git ls-files '*.sh'` minus the vendored `.loom/` and
`.claude/` trees. When shellcheck is not installed the step prints a clear
"shellcheck unavailable" message and exits 0, unless `--require-tools` is
given, in which case it exits 1 (the repo's usual skip-vs-fail convention).

  python3 -m sim.tools.lint_shell                  # skip if unavailable
  python3 -m sim.tools.lint_shell --require-tools  # fail if unavailable
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _git_files  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
VENDORED_PREFIXES = (".loom/", ".claude/")
SEVERITY = "warning"


def select_scripts(tracked: list[str]) -> list[str]:
    """Tracked *.sh paths that are first-party (not vendored), sorted."""
    return sorted(p for p in tracked
                  if p.endswith(".sh") and not p.startswith(VENDORED_PREFIXES))


def tracked_files() -> list[str]:
    return _git_files.tracked_files(ROOT, "*.sh")


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
