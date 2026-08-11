#!/usr/bin/env python3
"""Shared `klt` CLI plumbing for every `layout/` driver script.

`layout/verify.py`, `layout/floorplan/floorplan.py`, and each cell/block/ring
`build.py` all drive the `klt` command line the same way: run it with
`--format json`, read stdout-or-stderr, parse the JSON payload, and raise on
an empty run, unparseable output, or an `{"error": ...}` payload. This module
is the one copy of that boilerplate (issue #137 -- it used to be five
independent, near-byte-identical copies, one per caller).

Not a package member of anything else under `layout/` -- it computes its own
`REPO_ROOT` from its own location (`layout/_klt.py` sits directly under
`layout/`, so one `.parent` up is the repo root) rather than importing a
caller's `REPO_ROOT`, so callers keep resolving their own GDS/report paths
exactly as before.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class FlowError(Exception):
    """A tool invocation could not produce a verdict at all."""


def resolve_pdk():
    """Resolve the gf180mcu install through the repo's one PDK resolver.

    `sim/harness/pdk.py` is that resolver (its own docstring: "No PDK path is
    ever hardcoded ... Everything resolves through this module"), so the
    layout flow uses it rather than re-implementing discovery and risking a
    DRC/LVS run against a different PDK install than the simulations cite.
    Returns None when no install is found.
    """
    try:
        from sim.harness import pdk as pdk_mod
    except ImportError:  # pragma: no cover - repo layout guarantees this
        return None
    try:
        return pdk_mod.find_pdk()
    except Exception:
        return None


def _run_klt(args: list[str], timeout_s: int = 600) -> dict:
    """Run `klt <args> --format json` from the repo root and parse stdout.

    Every path handed to `klt` is repo-root-relative and the working
    directory is the repo root, so the paths echoed back into the reports
    are stable across machines. `timeout_s` defaults to 600 (the value every
    caller but `layout/floorplan/floorplan.py` used); that caller passes 900
    explicitly, since its own `gen-compose` invocations run over more
    geometry than a single cell/block/ring build.
    """
    argv = ["klt", *args, "--format", "json"]
    done = subprocess.run(
        argv, capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=timeout_s
    )
    # klt writes its success payload to stdout and its `{"error": ...}`
    # payload to stderr, so both streams have to be considered before
    # concluding a run produced nothing at all.
    raw = done.stdout.strip() or done.stderr.strip()
    if not raw:
        raise FlowError(
            f"`{' '.join(argv)}` produced no output (exit {done.returncode})"
        )
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FlowError(f"`{' '.join(argv)}` emitted unparseable JSON: {exc}") from exc
    if "error" in payload:
        raise FlowError(f"`{' '.join(argv)}` failed: {payload['error'].get('message')}")
    return payload
