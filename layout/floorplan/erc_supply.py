#!/usr/bin/env python3
"""Whole-block supply connectivity ERC over the composed floorplan stream
(issue #447).

`klt erc` is run once over `layout/floorplan/trng_floorplan.gds` with
`layout/floorplan/erc-supply-spec.json` (Metal1-Metal5, Via1-Via4, one
declared name per physical supply: vddr1, vddr2, vdd, vddd, vss). The native
response is committed, trimmed of its per-gate antenna tables, as
`layout/floorplan/reports/erc-supply.json`, pinned to the GDS and the spec
by content hash.

Two entry points:

* `run_erc()` -- executes `klt erc` (slow: minutes on this dense stream) and
  returns the projected report. `floorplan.py --write` calls it.
* `freshness_problems()` -- stdlib only, no `klt`: the committed report must
  pin the committed GDS and spec by hash, name the pinned klt version, be
  clean, and show every declared supply as computed. `floorplan.py`'s check
  path calls it on every run, so a changed stream or spec without a refreshed
  report fails.

The report is evidence of what `klt erc` said; it is not a tier input
(`signoff/block-manifest.json` does not cite it).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FLOORPLAN_DIR = REPO_ROOT / "layout" / "floorplan"
GDS = FLOORPLAN_DIR / "trng_floorplan.gds"
SPEC = FLOORPLAN_DIR / "erc-supply-spec.json"
REPORT = FLOORPLAN_DIR / "reports" / "erc-supply.json"
TOP_CELL = "trng_floorplan"

#: The klt release this repo pins (`signoff/check.py` KLT_PIN); a test holds
#: the two equal.
KLT_PIN = "0.6.0"

#: Supplies the spec must declare and the report must show computed.
DECLARED_SUPPLIES = ("vddr1", "vddr2", "vdd", "vddd", "vss")

_REGENERATE = "re-run `python3 layout/floorplan/floorplan.py --write` with klt 0.6.0"


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def sha256_ref(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def project_report(native: dict) -> dict:
    """Trim a native `klt erc --findings-only` response for committing.

    Dropped: the per-gate tables (`gates`, ~10 MB; `gate_count` is kept) and
    the antenna `coverage` block (every entry is `skipped: findings_only`,
    and the gf180mcu PDK has no antenna table). The per-gate
    `erc.floating_gate` ids in `erc_coverage.checked` collapse to a count;
    the per-supply `erc.net_connectivity` ids are kept verbatim. Everything
    else, including `provenance`, is the tool's own output.
    """
    out = {k: v for k, v in native.items() if k not in ("gates", "coverage")}
    cov = dict(out["erc_coverage"])
    checked = cov.get("checked", [])
    gate_ids = [c for c in checked if c.startswith("erc.floating_gate:")]
    cov["checked"] = [c for c in checked if not c.startswith("erc.floating_gate:")]
    cov["floating_gate_checked_count"] = len(gate_ids)
    out["erc_coverage"] = cov
    out["trimmed"] = {
        "gates": "per-gate antenna tables omitted (gate_count kept)",
        "coverage": "antenna coverage omitted (findings_only run; no antenna PDK table)",
        "erc_coverage.checked": "erc.floating_gate ids collapsed to floating_gate_checked_count",
    }
    return out


def run_erc(run_klt) -> dict:
    """Run the pinned `klt erc` once over the committed stream and return
    the projected report. `run_klt` is `layout._klt._run_klt`."""
    native = run_klt(
        [
            "erc", _rel(GDS), _rel(SPEC),
            "--top", TOP_CELL,
            "--findings-only",
        ],
        timeout_s=3600,
    )
    version = (native.get("provenance") or {}).get("klt_version")
    if version != KLT_PIN:
        raise RuntimeError(
            f"klt erc ran under klt {version}, not the pinned {KLT_PIN}; "
            f'use `uvx --from "klayout-tools=={KLT_PIN}" klt` (on PATH as klt)'
        )
    return project_report(native)


def report_problems(report: dict, *, gds: Path = GDS, spec: Path = SPEC) -> list[str]:
    """Everything wrong with `report` as evidence for `gds` + `spec`."""
    problems: list[str] = []
    prov = report.get("provenance") or {}
    if prov.get("klt_version") != KLT_PIN:
        problems.append(
            f"provenance.klt_version is {prov.get('klt_version')!r}, not the pinned {KLT_PIN!r}"
        )
    if (prov.get("input") or {}).get("content_hash") != sha256_ref(gds):
        problems.append(
            f"provenance.input.content_hash does not match {_rel(gds)} "
            "-- the stream changed since the ERC run"
        )
    if (prov.get("spec") or {}).get("content_hash") != sha256_ref(spec):
        problems.append(
            f"provenance.spec.content_hash does not match {_rel(spec)} "
            "-- the spec changed since the ERC run"
        )
    if report.get("erc_status") != "clean" or report.get("erc_finding_count") != 0 \
            or report.get("erc_findings"):
        problems.append(
            f"erc_status is {report.get('erc_status')!r} with "
            f"{report.get('erc_finding_count')} finding(s), not clean"
        )
    cov = report.get("erc_coverage") or {}
    checked = set(cov.get("checked", []))
    for net in DECLARED_SUPPLIES:
        if f'erc.net_connectivity:["{net}"]' not in checked:
            problems.append(f"supply {net!r} is not in erc_coverage.checked (zero coverage)")
    if cov.get("skipped"):
        problems.append(f"erc_coverage.skipped is not empty: {cov['skipped']}")
    if cov.get("nothing_checked"):
        problems.append("erc_coverage.nothing_checked is set")
    disclosure = report.get("ties_disclosure")
    spec_disclosure = json.loads(spec.read_text()).get("ties_disclosure")
    if not spec_disclosure or disclosure != spec_disclosure:
        problems.append(
            "ties_disclosure must carry the spec's own disclosure (ties and "
            "substrate are unexpressible here and must stay disclosed)"
        )
    declared = [n["name"] for n in json.loads(spec.read_text()).get("nets", [])]
    if declared != list(DECLARED_SUPPLIES):
        problems.append(f"spec declares nets {declared}, expected {list(DECLARED_SUPPLIES)}")
    return problems


def freshness_problems(report_path: Path = REPORT, **kw) -> list[str]:
    if not report_path.is_file():
        return [f"{_rel(report_path)} is missing -- {_REGENERATE}"]
    problems = report_problems(json.loads(report_path.read_text()), **kw)
    return [f"{_rel(report_path)}: {p} -- {_REGENERATE}" for p in problems]
