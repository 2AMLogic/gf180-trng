#!/usr/bin/env python3
"""Shared ``git ls-files`` wrapper for ``sim/tools/*.py`` (issue #721).

Six lint/verify scripts each carried their own ``git ls-files -z`` +
split-on-NUL function, and had drifted into three different failure
conventions for the same condition (a typed error, ``SystemExit``, and a raw
``CalledProcessError`` traceback). This module is the one place that runs it
and always reports failure the same way: ``GitError``. Each caller maps that
single exception onto its own exit behaviour.

Callers import it the way ``_record_parsing`` is imported: put this directory
on ``sys.path`` first, so it resolves whether the script is run by path or
as ``python3 -m sim.tools.<name>``.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


class GitError(RuntimeError):
    """``git ls-files`` could not run, or exited nonzero."""


def tracked_files(root: Path, *pathspec: str) -> list[str]:
    """Repo-relative paths git tracks under ``root``, in git's order.

    ``pathspec`` is passed after ``--`` to restrict the listing. Raises
    ``GitError`` if git cannot be run or exits nonzero, so a failure is never
    mistaken for "nothing is tracked".
    """
    cmd = ["git", "ls-files", "-z"]
    if pathspec:
        cmd += ["--", *pathspec]
    try:
        proc = subprocess.run(cmd, cwd=root, capture_output=True, check=False)
    except OSError as exc:
        raise GitError(f"cannot run git in {root}: {exc}") from exc
    if proc.returncode != 0:
        raise GitError(
            f"git ls-files in {root} failed (exit {proc.returncode}): "
            f"{proc.stderr.decode(errors='replace').strip()}"
        )
    return [p.decode(errors="surrogateescape") for p in proc.stdout.split(b"\0") if p]
