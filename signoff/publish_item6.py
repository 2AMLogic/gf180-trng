#!/usr/bin/env python3
"""Publish the sized mismatch Monte Carlo campaign as T1 item 6's analog citation.

    uv venv .venv-klt && uv pip install --python .venv-klt/bin/python "klayout-tools[yield]==0.9.0"
    KLT=.venv-klt/bin/klt python3 signoff/publish_item6.py
    python3 signoff/check.py --write

What it does (issue #1025; the pre-sizing flow read per-seed lines from the
2026-08-17 harness logs -- see git history for that version):

* It reads the four fleet-run ``klt sim`` Monte Carlo reports of the sized
  campaign (``sim/records/raw/2026-11-21-*/``, read only, nothing is
  re-simulated) and pairs each nominal report with its known-bad companion.
* For each measurement it derives the sample set with ``klt yield-samples``
  (klayout-tools 0.9.0, see ``YIELD_PIN``): the nominal report's draw becomes
  the samples, the known-bad companion's draw becomes the measurement's
  ``negative_control`` -- graded against the nominal's limits, never
  hand-assembled.
* It renames each derived measurement to the DR-0033 key
  (``period_r1@tt_27c_3.30v`` ...; a request measurement name cannot carry
  ``@``, so the requests use ``m_*`` names and the DR key is applied here)
  and attaches the ratified limits from ``signoff/evidence/mc-yield/limits.json``
  verbatim -- including the ``dtrip_v`` exclusivity flags the requests' own
  inclusive bounds cannot express. The limits are never edited to make a
  report pass.
* It runs ``klt yield`` over the merged document with its default confidence
  and sample-size target, and writes the native response to
  ``signoff/evidence/mc-yield/klt_yield_response.json``. The response's own
  ``sample_size.verdict`` and ``negative_control`` verdicts are recorded as
  they come.

``publication.json`` pins every fleet report the sample set was derived from
by sha256; ``publication_problems()`` re-reads them (and re-extracts each
measurement's draw, unit, source corners and errored counts with an
independent reader, and checks the campaign's zero-count flags and control
descriptions) so a stale or hand-edited sample set can be refused.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402

REPO_ROOT = check.REPO_ROOT
OUT = REPO_ROOT / "signoff" / "evidence" / "mc-yield"
YIELD_PIN = "0.9.0"

#: DR-0033 measurement key -> (raw record stem, request stem, value name).
#: One entry per measurement per corner: the nominal request and its known-bad
#: companion share a stem directory (sim/records/raw/<stem>/), each request's
#: fleet report landing as <request>.report.json inside it.
CAMPAIGN = {
    "period_r1@tt_27c_3.30v": ("2026-11-21-ro-array-core-mc-freq-sized-01", "mc-tt", "m_period_r1"),
    "period_r1@ss_125c_3.63v": ("2026-11-21-ro-array-core-mc-freq-sized-01", "mc-ss", "m_period_r1"),
    "dtrip_v@tt_27c_3.30v": ("2026-11-21-sampler-dff-mc-offset-sized-01", "mc-tt", "m_dtrip_v"),
    "dtrip_v@ss_125c_3.63v": ("2026-11-21-sampler-dff-mc-offset-sized-01", "mc-ss", "m_dtrip_v"),
}

CONTROL_DESCRIPTIONS = {
    "m_period_r1": "Ring 1 per-stage channel length (ro_lstv) increased from 2 to 3.4 µm.",
    "m_dtrip_v": "A -2.2 V input-referred offset (voff) shifts the sampler threshold above the supply rail.",
}


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def report_path(stem: str, request: str) -> Path:
    return REPO_ROOT / "sim" / "records" / "raw" / stem / f"{request}.report.json"


def control_request(request: str) -> str:
    return request.replace("mc-", "mc-control-", 1)


class Draw(NamedTuple):
    """What read_draw() extracts from one report for one measurement."""

    values: list[float | None]
    errored: int
    unit: str | None
    source_corners: list[str]


def read_draw(report: Path, value: str) -> Draw:
    """The measurement's draw out of a klt sim Monte Carlo report.

    Mirrors ``klt yield``'s sim-report reader for the shapes this campaign
    produces: only corners carrying a ``monte_carlo`` block are samples, a
    ``null`` value is an errored draw, and this campaign declares no
    plausibility bounds or fail_on_diagnostic so nothing is inconclusive.
    Beside the draw it returns what those same corners say about the
    measurement's ``unit`` (None if the report is inconsistent about it)
    and the base corner ids (each Monte Carlo repetition's trailing
    ``/mc<N>`` stripped, de-duplicated in first-seen order) -- the
    report-derivable metadata publication_problems() compares against the
    published sample set. Used by ``publication_problems()`` as an
    independent cross-check of the ``klt yield-samples`` derivation, never
    as a substitute for it.
    """
    doc = json.loads(report.read_text())
    values: list[float | None] = []
    units: set[str] = set()
    source_corners: list[str] = []
    for corner in doc.get("corners", []):
        if not corner.get("monte_carlo"):
            continue
        base = re.sub(r"/mc[0-9]+$", "", corner.get("corner_id", ""))
        if base not in source_corners:
            source_corners.append(base)
        for m in corner.get("measurements", []):
            if m["name"] == value:
                values.append(m.get("value"))
                units.add(m.get("unit"))
    unit = next(iter(units)) if len(units) == 1 else None
    return Draw(values, values.count(None), unit, source_corners)


def build(klt: str) -> tuple[dict, dict[str, str]]:
    """Derive the merged sample set through the pinned klt, plus its pins.

    Runs ``klt yield-samples`` once per measurement (nominal report against
    its known-bad companion) and merges the four derived measurements under
    their DR-0033 keys with the ratified limits attached.
    """
    limits = json.loads((OUT / "limits.json").read_text())["measurements"]
    measurements, pins = [], {}
    for dr_name, (stem, request, value) in CAMPAIGN.items():
        nominal = report_path(stem, request)
        control = report_path(stem, control_request(request))
        pins[nominal.relative_to(REPO_ROOT).as_posix()] = sha256(nominal)
        pins[control.relative_to(REPO_ROOT).as_posix()] = sha256(control)
        argv = [
            *shlex.split(klt), "yield-samples",
            nominal.relative_to(REPO_ROOT).as_posix(),
            "--negative-control", control.relative_to(REPO_ROOT).as_posix(),
            "--description", CONTROL_DESCRIPTIONS[value],
            "--measurement", value,
            "--format", "json",
        ]
        print(shlex.join(argv), file=sys.stderr)
        done = subprocess.run(argv, cwd=REPO_ROOT, capture_output=True, text=True)
        if not done.stdout.strip():
            print(done.stderr, file=sys.stderr)
            raise SystemExit(f"klt yield-samples failed for {dr_name} (exit {done.returncode}); nothing published")
        derived = json.loads(done.stdout)
        entry = derived["measurements"][0]
        entry["name"] = dr_name
        entry["limits"] = limits[dr_name]
        measurements.append(entry)
    return {"measurements": measurements}, pins


def publication_problems() -> list[str]:
    """Problems with the committed sample set / publication (stdlib only)."""
    pub = json.loads((OUT / "publication.json").read_text())
    problems: list[str] = []
    for rel, pin in pub.get("raw_reports", {}).items():
        path = REPO_ROOT / rel
        if not path.exists():
            problems.append(f"{rel}: pinned report is gone")
        elif sha256(path) != pin:
            problems.append(f"{rel}: pinned report hash differs from the tree")
    sample_set = json.loads((OUT / "sample_set.json").read_text())
    measurements = sample_set.get("measurements", [])
    got = {m["name"]: m for m in measurements}
    if len(measurements) != len(CAMPAIGN) or set(got) != set(CAMPAIGN):
        problems.append("sample_set.json: measurements differ from the declared campaign")
        return problems
    ratified = json.loads((OUT / "limits.json").read_text())["measurements"]
    for dr_name, (stem, request, value) in CAMPAIGN.items():
        entry = got[dr_name]
        if entry.get("limits") != ratified[dr_name]:
            problems.append(f"{dr_name}: published limits differ from limits.json")
        nominal = report_path(stem, request)
        control = report_path(stem, control_request(request))
        if not nominal.exists() or not control.exists():
            problems.append(f"{dr_name}: a source report is missing from the tree")
            continue
        draw = read_draw(nominal, value)
        ctl_draw = read_draw(control, value)
        have = list(entry.get("samples", []))
        nulls = sum(1 for v in have if v is None)
        if [v for v in have if v is not None] != [v for v in draw.values if v is not None] or nulls != draw.errored:
            problems.append(f"{dr_name}: samples no longer match the nominal report's draw")
        ctl = entry.get("negative_control") or {}
        ctl_have = [v for v in ctl.get("samples", []) if v is not None]
        if ctl_have != [v for v in ctl_draw.values if v is not None]:
            problems.append(f"{dr_name}: negative_control samples no longer match the companion report's draw")
        if entry.get("unit") != draw.unit:
            problems.append(f"{dr_name}: published unit differs from the nominal report")
        if entry.get("source_corners") != draw.source_corners:
            problems.append(f"{dr_name}: published source_corners differ from the nominal report")
        if entry.get("errored") != draw.errored:
            problems.append(f"{dr_name}: published errored count differs from the nominal report")
        if ctl.get("errored") != ctl_draw.errored:
            problems.append(f"{dr_name}: negative_control errored count differs from the companion report")
        for field in ("failed_unmeasurable", "censored", "inconclusive"):
            if entry.get(field) != 0:
                problems.append(f"{dr_name}: published {field} must be 0 for this campaign")
        for field in ("failed_unmeasurable", "censored"):
            if ctl.get(field) != 0:
                problems.append(f"{dr_name}: negative_control {field} must be 0 for this campaign")
        if ctl.get("description") != CONTROL_DESCRIPTIONS[value]:
            problems.append(f"{dr_name}: negative_control description differs from the declared defect")
    return problems


def main() -> int:
    klt = os.environ.get("KLT", "klt")
    doc, pins = build(klt)
    (OUT / "sample_set.json").write_text(json.dumps(doc, indent=2) + "\n")
    argv = [*shlex.split(klt), "yield", (OUT / "sample_set.json").relative_to(REPO_ROOT).as_posix(), "--format", "json"]
    print(shlex.join(argv), file=sys.stderr)
    done = subprocess.run(argv, cwd=REPO_ROOT, capture_output=True, text=True)
    if not done.stdout.strip():
        print(done.stderr, file=sys.stderr)
        print(f"klt yield failed (exit {done.returncode}); nothing published", file=sys.stderr)
        return 1
    resp = json.loads(done.stdout)
    (OUT / "klt_yield_response.json").write_text(json.dumps(resp, indent=2) + "\n")
    (OUT / "publication.json").write_text(
        json.dumps(
            {
                "klayout_tools_yield_pin": YIELD_PIN,
                "klt_exit": done.returncode,
                "raw_reports": pins,
                "derivation": "klt yield-samples <nominal> --negative-control <control> --description <defect> --measurement <value>, one per measurement, seeds and jobs in the pinned reports",
            },
            indent=2,
        )
        + "\n"
    )
    print(f"klt yield exit {done.returncode}; response written", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
