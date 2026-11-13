#!/usr/bin/env python3
"""Fixtures and a normaliser for the power tools' record front matter (issue #834).

``power_retention``, ``power_switch``, ``power_switch_decay`` and
``liveness_sampler_power`` render their record front matter through one skeleton,
``_power_cli.render_header``, so a change to one tool's header is a change to all four.
Each tool's own test module pins its rendered front matter as a golden string and
compares it through :func:`front_matter`, which masks the three values that are
properties of the host and the checkout rather than of the renderer: the git blob SHAs
of the testbench and netlist, the ``repo_commit``, and ``platform.platform()``.
Everything else -- field order, field names, indentation, and the blank lines between
blocks -- is pinned literally, because that is the evidence format `sim/README.md`
defines and records already committed under `sim/records/` are written in.

The fixtures here are fixed by construction (a fixed ``now``, a fixed fake git state, a
fake one-job fleet) so the goldens are reproducible on any host. Nothing here runs
ngspice, reads the PDK or calls ``klt``.
"""

from __future__ import annotations

import datetime as _dt
import re

NOW = _dt.datetime(2026, 1, 2, 3, 4, 5)
GIT = {"commit": "0" * 40, "dirty": False}
RAW_FILES = [("probe.sp", "a" * 64), ("probe.log", "b" * 64)]
NOTE = "The batch submit was refused by the fleet; nothing ran."

#: A submitting host's own provenance, as ``klt sim`` reports it.
PROVENANCE = {"klt_version": "9.9.9",
              "pdk": {"name": "gf180mcuD", "version": "open_pdks 1.0.test"}}

#: One batch job whose worker reports its own PDK stamp and ngspice banner, so
#: ``report.fleet_provenance`` resolves to the fleet's versions, not the host's.
ENVIRONMENT = {
    "engine_version": "99",
    "models_lib_sha256": "c" * 64,
    "remote": {
        "job_id": "job-0001",
        "instance_type": "c7g.large",
        "lifecycle": "spot",
        "runner_klt_version": "9.9.9",
        "client_klt_version": "9.9.8",
        "runner_compatibility": "ok",
        "fleet": [{
            "job_id": "job-0001",
            "worker_environment": {
                "pdk": {"stamp_text": "open_pdks 1.0.test"},
                "simulator": {"version_banner": "ngspice\n** ngspice-99 test build\n"},
            },
        }],
    },
}


def unit(values: dict, *, process: str = "tt", temperature_c: int = 27, vdd: float = 3.3,
         supply_key: str = "vsup", runtime_s: float = 12.5) -> dict:
    """One grid unit of a ``klt sim`` report, carrying ``values`` as its measurements."""
    return {"process": process, "temperature_c": temperature_c, "supply_v": {supply_key: vdd},
            "status": "ok", "runtime_s": runtime_s,
            "measurements": [{"name": k, "value": v} for k, v in values.items()]}


def report(*units: dict) -> dict:
    """A one-job batch report over ``units``."""
    return {"provenance": PROVENANCE, "environment": ENVIRONMENT, "corners": list(units)}


_MASKS = (
    # Content hashes of the raw slice and of the PDK model library.
    (re.compile(r"sha256:[0-9a-f]{64}"), "sha256:<SHA256>"),
    # Git blob SHAs of the testbench and netlist: they move with the deck, not the header.
    (re.compile(r"(?m)^  sha: [0-9a-f]{40}$"), "  sha: <BLOB>"),
    (re.compile(r"(?m)^(  also: \S+) sha [0-9a-f]{40}$"), r"\1 sha <BLOB>"),
    (re.compile(r"(?m)^repo_commit: .*$"), "repo_commit: <COMMIT>"),
    (re.compile(r"(?m)^  platform: .*$"), "  platform: <PLATFORM>"),
)


def front_matter(text: str) -> str:
    """The record's front matter (both ``---`` fences included), host values masked.

    Raises ``AssertionError`` rather than returning something partial if the text does
    not open and close a front-matter block, since that is itself a header regression.
    """
    lines = text.split("\n")
    assert lines and lines[0] == "---", "record does not open with a front-matter fence"
    end = next((i for i, ln in enumerate(lines[1:], 1) if ln == "---"), None)
    assert end is not None, "front matter is never closed"
    out = "\n".join(lines[:end + 1]) + "\n"
    for pattern, repl in _MASKS:
        out = pattern.sub(repl, out)
    return out
