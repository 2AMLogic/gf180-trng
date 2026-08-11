#!/usr/bin/env python3
"""Build and check the entropy-source floorplan abstract, and its area rollup.

    python3 layout/floorplan/floorplan.py                # build, check, report
    python3 layout/floorplan/floorplan.py --write        # ... and refresh reports/
    python3 layout/floorplan/floorplan.py --require-tools  # fail, don't skip
    python3 layout/floorplan/floorplan.py --list         # print the region table

This is the machine-checkable half of `layout/floorplan/README.md`, which is
the written isolation rationale issue #16 asks for. Every number that document
quotes is produced here, so a reader can re-derive it instead of trusting it --
the same arrangement `design/conditioner/area_estimate.py` has with DR-0008 and
`sim/tools/array_sizing.py` has with DR-0007 section 2.

What it produces, in order:

1. **A cell inventory per isolation region**, expanded from the *committed*
   netlists (`design/ro_array_core.spice`, `design/sampler_core.spice`) rather
   than typed in here, so an array-size or stage-count change moves this
   estimate. The digital side reuses the inventories
   `design/digital_power_estimate.py` already maintains (and that
   `sim/tests/test_power_rollups.py` already guards), so there is exactly one
   copy of that list in the repository.
2. **A cell-area estimate** for each region: standard-cell LEF areas out of the
   installed PDK for every gate-shaped cell, plus a measured footprint for the
   two long-channel starve devices per ring stage, which no standard cell
   represents. See `AREA MODEL` below for what that does and does not mean.
3. **A DRC-clean floorplan abstract**: one `klt gen guard_ring` per region,
   sized to that region's placed area -- or, for a region with a real
   committed assembly (`ring1`/`ring2` as of issue #119, see
   `ASSEMBLED_RING_GDS`), to that assembly's own bounding box instead --
   composed into a single stream by `klt gen-compose` with a declared
   isolation channel between neighbours, and run through `klt drc` with the
   same deck `layout/verify.py` uses.
3b. **A ring-fit check** (issue #119) for every region sized from a real
   assembly: composes that region's own guard ring with the real ring GDS,
   aligned to the tightest legal placement, and runs `klt drc` over the pair
   (`check_ring_fit`) -- confirming the assembled geometry actually fits
   where the floorplan reserves it, which nothing checked before this.
4. **An area rollup against the README `Area` row** (< 0.05 mm^2).

AREA MODEL -- what this is and is not
-------------------------------------
It is a **bottom-up inventory estimate with a stated method**, not a synthesis
or a layout result. No synthesiser, placer or router has been run on this
block, and none of the analog cells has been drawn. Specifically:

- Gate-shaped cells (`ro_stage`'s core inverter, `ro_nand2`, `xor2`,
  `sampler_dff`) are priced at their nearest `gf180mcu_fd_sc_mcu7t5v0`
  equivalent's LEF area. That library is 7-track and uses wider devices than
  these hand-drawn cells do, so this **over-estimates** the analog cells --
  the conservative direction for a budget.
- The series starve devices (`L = 2 um`) have no standard-cell analogue and are
  priced at a real generated footprint from `klt gen mos_array`, DRC-checked
  by this script at the same time as everything else.
- Placement utilisation is a **range**, not a number: 60 % and 80 % are both
  printed, matching DR-0008's convention.

The floorplan abstract is a **floorplan**, not a layout. Its guard rings are
real, generated, DRC-clean geometry; the regions they enclose are empty. A
clean DRC here says the isolation structures and their spacings are legal at
these dimensions. It says nothing whatever about the cells that will go inside
them, because those cells do not exist yet.

Standard library only, and everything that touches KLayout goes through the
`klt` command line -- same rule as `layout/verify.py`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import struct
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LAYOUT_DIR = REPO_ROOT / "layout"
FLOORPLAN_DIR = LAYOUT_DIR / "floorplan"
REPORT_DIR = FLOORPLAN_DIR / "reports"

#: Scratch space, git-ignored, shared with layout/verify.py. Every tool that
#: writes a file writes it here in both modes, so a check run can never
#: overwrite a committed artefact.
WORK_DIR = LAYOUT_DIR / ".work"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "sim"))
sys.path.insert(0, str(REPO_ROOT / "design"))
sys.path.insert(0, str(REPO_ROOT / "design" / "conditioner"))

import area_estimate  # noqa: E402  (design/conditioner/area_estimate.py)
import digital_power_estimate as digital  # noqa: E402  (design/)

#: The DRC deck name `klt` knows this PDK family by -- per-family, not
#: per-variant. Same value layout/verify.py uses, for the same reason.
DECK = "gf180mcu"

EXIT_OK = 0
EXIT_FAIL = 1

#: The README `Area` row this block is budgeted against, in um^2.
AREA_BUDGET_UM2 = 0.05 * 1e6

#: Placement utilisation range. Both ends are reported; the floorplan geometry
#: is built at the conservative end. Same convention as DR-0008.
UTILISATION = (0.60, 0.80)
GEOMETRY_UTILISATION = 0.60

#: Width of the isolation channel left between neighbouring guarded regions,
#: in um. This is a **routing-derived floor, not a coupling-derived one**: it
#: is what each supply domain needs to reach its own region without sharing a
#: channel with another domain's straps. No substrate-coupling attenuation is
#: claimed for it -- see README.md, "What this floorplan does not establish".
ISOLATION_CHANNEL_UM = 20.0

#: Guard-ring tap thickness, um, and the target spacing between tap contacts
#: along a ring side. 2 um keeps the ring's series resistance low enough that
#: the ring behaves as one node at the frequencies here without spending area
#: on a solid contact row.
GUARD_RING_WIDTH_UM = 1.0
GUARD_CONTACT_PITCH_UM = 2.0

#: Committed, real, DRC-clean assembled-ring geometry that sizes `ring1`'s
#: and `ring2`'s guarded-region footprint below, instead of the area/
#: utilisation estimate's sqrt(area) square (issue #119, Option A). Both
#: rings share the same cell inventory and the same row layout
#: (`layout/rings/ro_ring11/build.py`), so both bounding boxes happen to be
#: identical, but each is read from its own committed stream rather than
#: assumed equal.
#:
#: `combiner_sampler` (`xor2` + 4x `sampler_dff`) has no entry here: it is
#: not assembled yet (issue #110's own Dependencies), so it keeps the area
#: estimate's square footprint until a committed GDS exists for it -- adding
#: it here, once it does, is the natural follow-up this issue's own Scope
#: section calls out rather than a new decision.
ASSEMBLED_RING_GDS: dict[str, Path] = {
    "ring1": LAYOUT_DIR / "rings" / "ro_ring11" / "ro_ring11.gds",
    "ring2": LAYOUT_DIR / "rings" / "ro_ring11_ring2" / "ro_ring11_ring2.gds",
}

#: `klt gen mos_array` refuses w_um below this. The gf180mcu 3.3 V core
#: devices go to 0.22 um, and the curated DRC deck's own Comp minimum is
#: 0.22 um -- `layout/testcells/build.py` says so and draws against it. So a
#: minimum-width device cannot be generated, and the starve devices below are
#: measured at this floor instead of at their drawn width. That makes their
#: footprint an over-estimate, which is the safe direction, and it is filed
#: upstream rather than worked around silently (README.md, "Tool friction").
GEN_MIN_W_UM = 0.42


# --------------------------------------------------------------------------- #
# The design cells, and what each is priced as
# --------------------------------------------------------------------------- #
#
# `stdcell` is the nearest gf180mcu_fd_sc_mcu7t5v0 equivalent, priced at its
# LEF area. `starve` counts the long-channel series devices the cell adds on
# top of that shape, which no standard cell has; each is measured with
# `klt gen mos_array`.
CELL_MODEL: dict[str, dict] = {
    "ro_stage": {
        "stdcell": "inv_1",
        "starve": ["nfet", "pfet"],
        "note": "minimum-width 3.3 V inverter + two always-on series starve devices",
    },
    "ro_nand2": {
        "stdcell": "nand2_1",
        "starve": ["nfet", "pfet"],
        "note": "the ring's stoppable stage: same cell with a second input",
    },
    "xor2": {
        "stdcell": "xor2_1",
        "starve": [],
        "note": "the combining gate -- static CMOS, minimum width",
    },
    "sampler_dff": {
        "stdcell": "dffrnq_1",
        "starve": [],
        "note": "transmission-gate master-slave DFF, async reset (DR-0014)",
    },
}

#: Isolation regions, in the order they are placed. `cells` is resolved from
#: the netlists at run time for the analog regions; the digital region reads
#: `design/digital_power_estimate.py`'s inventories.
#:
#: `supply` names the region's own supply node. Regions with different supply
#: names are separate branches of the star -- that is what "star routing" means
#: here, and the schematic already provides the pins (`vddr1`, `vddr2`).
REGIONS = [
    {
        "id": "ring1",
        "title": "Entropy ring 1",
        "source": ("netlist", "ro_array_core", "xr1"),
        "supply": "vddr1",
        "role": "entropy",
    },
    {
        "id": "ring2",
        "title": "Entropy ring 2",
        "source": ("netlist", "ro_array_core", "xr2"),
        "supply": "vddr2",
        "role": "entropy",
    },
    {
        "id": "combiner_sampler",
        "title": "XOR combiner + samplers",
        "source": ("netlist+", ("ro_array_core", "xa1"), ("sampler_core", "sampler_dff")),
        "supply": "vdd",
        "role": "boundary",
    },
    {
        "id": "digital",
        "title": "Conditioner + health tests + interface",
        "source": ("digital",),
        "supply": "vddd",
        "role": "deterministic",
    },
]


class FlowError(Exception):
    """A tool invocation could not produce a verdict at all."""


# --------------------------------------------------------------------------- #
# Netlist reading -- the analog inventory comes from the committed netlist
# --------------------------------------------------------------------------- #

_UNITS = {"t": 1e12, "g": 1e9, "meg": 1e6, "k": 1e3, "m": 1e-3, "u": 1e-6, "n": 1e-9,
          "p": 1e-12, "f": 1e-15, "a": 1e-18}


def _to_float(token: str, env: dict[str, float]) -> float:
    """Resolve a SPICE numeric token, following one level of parameter name."""
    token = token.strip()
    if token in env:
        return env[token]
    match = re.fullmatch(r"([+-]?[\d.]+(?:[eE][+-]?\d+)?)\s*([a-zA-Z]*)", token)
    if not match:
        raise FlowError(f"cannot read numeric token {token!r}")
    value = float(match.group(1))
    suffix = match.group(2).lower()
    if suffix:
        for name, scale in sorted(_UNITS.items(), key=lambda kv: -len(kv[0])):
            if suffix.startswith(name):
                return value * scale
        raise FlowError(f"unknown unit suffix in {token!r}")
    return value


def read_subckts(path: Path) -> dict[str, list[str]]:
    """Return {subckt name: body lines}, with `+` continuations joined."""
    text = re.sub(r"\n\+\s*", " ", path.read_text())
    blocks: dict[str, list[str]] = {}
    for match in re.finditer(r"^\.subckt\s+(\S+)(.*?)^\.ends", text, re.M | re.S):
        name = match.group(1)
        body = [
            line.strip()
            for line in match.group(2).splitlines()
            if line.strip() and not line.strip().startswith("*")
        ]
        blocks[name] = body
    return blocks


def _params(tokens: list[str], env: dict[str, float]) -> dict[str, float]:
    out: dict[str, float] = {}
    for token in tokens:
        if "=" in token:
            key, _, value = token.partition("=")
            out[key.strip().lower()] = _to_float(value, env)
    return out


def expand_instance(
    subckts: dict[str, list[str]], name: str, env: dict[str, float]
) -> Counter:
    """Count `CELL_MODEL` leaf cells beneath one subcircuit instance."""
    if name in CELL_MODEL:
        return Counter({name: 1})
    counts: Counter = Counter()
    for line in subckts.get(name, []):
        tokens = line.split()
        if not tokens or not tokens[0].lower().startswith("x"):
            continue
        positional = [t for t in tokens[1:] if "=" not in t]
        if not positional:
            continue
        child = positional[-1]
        if child not in subckts and child not in CELL_MODEL:
            continue  # a primitive device card, not a subcircuit instance
        child_env = dict(env)
        child_env.update(_params(tokens[1:], env))
        counts.update(expand_instance(subckts, child, child_env))
    return counts


def instance_counts(subckts: dict[str, list[str]], parent: str, instance: str) -> Counter:
    """Expand exactly one named instance inside `parent` (e.g. `xr1`)."""
    for line in subckts.get(parent, []):
        tokens = line.split()
        if not tokens or tokens[0] != instance:
            continue
        positional = [t for t in tokens[1:] if "=" not in t]
        return expand_instance(subckts, positional[-1], _params(tokens[1:], {}))
    raise FlowError(f"instance {instance!r} not found in .subckt {parent}")


def all_instances_of(subckts: dict[str, list[str]], parent: str, child: str) -> Counter:
    """Expand every instance of `child` directly inside `parent`."""
    counts: Counter = Counter()
    found = False
    for line in subckts.get(parent, []):
        tokens = line.split()
        if not tokens or not tokens[0].lower().startswith("x"):
            continue
        positional = [t for t in tokens[1:] if "=" not in t]
        if positional and positional[-1] == child:
            found = True
            counts.update(expand_instance(subckts, child, _params(tokens[1:], {})))
    if not found:
        raise FlowError(f"no instance of {child!r} inside .subckt {parent}")
    return counts


def starve_geometry(subckts: dict[str, list[str]], parent: str, instance: str) -> dict:
    """The drawn W/L of the starve devices under one ring instance."""
    for line in subckts.get(parent, []):
        tokens = line.split()
        if not tokens or tokens[0] != instance:
            continue
        params = _params(tokens[1:], {})
        # Rounded because these come back through a float unit conversion
        # (0.220u -> 0.21999999999999997) and they end up in a committed
        # artefact; 1 nm is well under the PDK's 5 nm grid.
        return {
            "w_um": round(params["wstv"] * 1e6, 3),
            "l_um": round(params["lstv"] * 1e6, 3),
        }
    raise FlowError(f"instance {instance!r} not found in .subckt {parent}")


# --------------------------------------------------------------------------- #
# klt invocations
# --------------------------------------------------------------------------- #


def _run_klt(args: list[str]) -> dict:
    argv = ["klt", *args, "--format", "json"]
    done = subprocess.run(
        argv, capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=900
    )
    raw = done.stdout.strip() or done.stderr.strip()
    if not raw:
        raise FlowError(f"`{' '.join(argv)}` produced no output (exit {done.returncode})")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FlowError(f"`{' '.join(argv)}` emitted unparseable JSON: {exc}") from exc
    if "error" in payload:
        raise FlowError(f"`{' '.join(argv)}` failed: {payload['error'].get('message')}")
    return payload


def read_gds_bbox(gds_path: Path) -> dict:
    """The real bounding box of a committed GDS's own top cell, in um.

    Reads it through `klt stats`, never `klayout.db` directly -- the same
    rule every other tool interaction in this module follows. Returns
    ``{"x0", "y0", "x1", "y1", "cell_name"}``; `klt stats`'s own
    `bbox_um` uses `left`/`bottom`/`right`/`top` keys, translated here to
    this module's `x0`/`y0`/`x1`/`y1` convention (the same one `klt gen`'s
    responses already use, which is what `gen_guard_ring` and `compose`
    below expect).
    """
    response = _run_klt(["stats", str(gds_path.relative_to(REPO_ROOT))])
    box = response["bbox_um"]
    return {
        "x0": box["left"],
        "y0": box["bottom"],
        "x1": box["right"],
        "y1": box["top"],
        "cell_name": response["top_cell"],
    }


def gen_mos(flavor: str, w_um: float, l_um: float, variant: str, stem: str) -> dict:
    """One isolated device, so its drawn footprint can be measured."""
    params = {
        "w_um": max(w_um, GEN_MIN_W_UM),
        "l_um": l_um,
        "rows": 1,
        "cols": 1,
        "dummy": 0,
        "flavor": flavor,
        "topology": "array",
    }
    return _run_klt([
        "gen", "mos_array",
        "--params", json.dumps(params),
        "--pdk", variant,
        "--cell-name", stem,
        "-o", f"layout/.work/{stem}.gds",
    ])


def gen_guard_ring(region_id: str, w_um: float, h_um: float, variant: str) -> dict:
    """A substrate-tap guard ring sized to enclose one region.

    `contacts_per_side` is derived from the region's *shorter* side, not the
    longer one. `klt gen guard_ring` applies one `contacts_per_side` count to
    every side, so deriving it from the longer side -- fine when every
    region was a square, which is all this ever priced before issue #119 --
    asks for more contacts than a short side can physically hold once a
    region is elongated, which `ring1`/`ring2`'s real assembled-row
    footprint (~78.9 x 4.75 um) now is. The generator refuses that request
    outright rather than drawing invalid geometry (`contacts_per_side=N does
    not fit along inner_height_um=...um without overlapping contacts`), so
    getting this wrong is a hard failure here, not a silent DRC surprise
    later.
    """
    per_side = max(4, int(round(min(w_um, h_um) / GUARD_CONTACT_PITCH_UM)))
    params = {
        "inner_width_um": round(w_um, 3),
        "inner_height_um": round(h_um, 3),
        "ring_width_um": GUARD_RING_WIDTH_UM,
        "contacts_per_side": per_side,
        # A p-substrate tap ring tied to the region's own vss. `add_well`
        # would make it an n-well tie instead, which is a different structure
        # for a different job.
        "add_well": False,
    }
    return _run_klt([
        "gen", "guard_ring",
        "--params", json.dumps(params),
        "--pdk", variant,
        "--cell-name", f"fp_guard_{region_id}",
        "-o", f"layout/.work/fp_guard_{region_id}.gds",
    ])


def compose(order: list[str], variant: str) -> dict:
    # `blocks[].generator_report` resolves against the *request file's own
    # directory* (klayout-tools#328), the same rule a `klt lvs` request
    # already followed -- so that path is written relative to wherever this
    # request document itself ends up, not to the repo root or the invoking
    # working directory. The request is always written to `WORK_DIR`,
    # alongside the `fp_guard_*.json` generator reports it references, so
    # plain filenames are correct and self-consistent here.
    #
    # `options.output` is unaffected by `request_dir`: gen-compose resolves
    # it against the process's current working directory regardless of where
    # the request document lives (`gen_compose.compose`'s docstring says so
    # explicitly). This flow always runs `klt` with `cwd=REPO_ROOT`, so that
    # path stays repo-root-relative.
    path = WORK_DIR / "compose-request.json"
    request = {
        "_comment": (
            "Generated by layout/floorplan/floorplan.py. Re-run by hand with: "
            f"klt gen-compose {path.relative_to(REPO_ROOT)} (from the repo root, "
            "so options.output lands at layout/.work/trng_floorplan.gds)"
        ),
        "blocks": [
            {"id": rid, "generator_report": f"fp_guard_{rid}.json"}
            for rid in order
        ],
        "placement": {
            "strategy": "row",
            "order": order,
            "spacing_um": ISOLATION_CHANNEL_UM,
        },
        "pdk": {"variant": variant},
        "options": {
            "cell_name": "trng_floorplan",
            "output": "layout/.work/trng_floorplan.gds",
        },
    }
    path.write_text(json.dumps(request, indent=2) + "\n")
    return request, _run_klt(["gen-compose", str(path.relative_to(REPO_ROOT))])


def run_drc(gds: str) -> dict:
    return _run_klt(["drc", gds, "--deck", DECK])


def _drc_summary(response: dict) -> dict:
    return {
        "status": response.get("status"),
        "violation_count": response.get("violation_count"),
        "rule_counts": response.get("rule_counts"),
    }


def check_ring_fit(region: dict, gds_path: Path, variant: str) -> dict:
    """Compose one region's own guard ring with its real assembled ring GDS,
    aligned so the ring's own bbox exactly fills the guard ring's declared
    inner cavity, and run `klt drc` over the pair -- the check issue #119
    itself named as missing: nothing before this confirmed the assembled
    geometry the floorplan reserves a region for actually *fits* inside it.

    `klt drc` is run twice: once on the composed pair, once on the ring GDS
    alone. A rule violated in both is already present in the committed ring
    geometry on its own and has nothing to do with this region's sizing or
    placement; a rule violated only in the composed run is new, introduced
    by the fit itself, and is what this check exists to catch. Only the
    latter is treated as this function's own pass/fail signal -- the former
    is reported for visibility but is a different question (whether
    `ring_gds` is DRC-clean by itself), out of this issue's scope.

    Placement uses `placement.strategy: "explicit"` (#321) with the ring's
    own reported bbox translated so its low corner lands at
    `(GUARD_RING_WIDTH_UM, GUARD_RING_WIDTH_UM)` -- the guard ring's own
    inner-cavity corner, since `gen_guard_ring`'s bbox always starts at
    `(0, 0)`. That is the tightest legal placement (zero clearance between
    the ring's own drawn edge and the region's guard ring) and so the
    hardest case for this check to pass, not an arbitrary one.
    """
    rid = region["id"]
    source = region["footprint_source"]
    bbox = source["bbox_um"]

    ring_report = {
        "generator": "committed_ring_geometry",
        "cell_name": source["cell_name"],
        "gds_path": str(gds_path.relative_to(REPO_ROOT)),
        "bbox_um": bbox,
    }
    (WORK_DIR / f"fp_ring_fit_{rid}_ring.json").write_text(
        json.dumps(ring_report, indent=2) + "\n"
    )

    origin_x = round(GUARD_RING_WIDTH_UM - bbox["x0"], 3)
    origin_y = round(GUARD_RING_WIDTH_UM - bbox["y0"], 3)
    request = {
        "_comment": (
            "Generated by layout/floorplan/floorplan.py's ring-fit check "
            f"(issue #119) for region '{rid}'. Re-run by hand with: "
            "klt gen-compose <this file's path> (from the repo root)."
        ),
        "blocks": [
            {"id": "guard", "generator_report": f"fp_guard_{rid}.json"},
            {"id": "ring", "generator_report": f"fp_ring_fit_{rid}_ring.json"},
        ],
        "placement": {
            "strategy": "explicit",
            "order": ["guard", "ring"],
            "origins_um": {
                "guard": {"x": 0.0, "y": 0.0},
                "ring": {"x": origin_x, "y": origin_y},
            },
        },
        "pdk": {"variant": variant},
        "options": {
            "cell_name": f"fp_ring_fit_{rid}",
            "output": f"layout/.work/fp_ring_fit_{rid}.gds",
        },
    }
    request_path = WORK_DIR / f"fp_ring_fit_{rid}_request.json"
    request_path.write_text(json.dumps(request, indent=2) + "\n")

    _run_klt(["gen-compose", str(request_path.relative_to(REPO_ROOT))])
    composed_drc = run_drc(f"layout/.work/fp_ring_fit_{rid}.gds")
    ring_drc = run_drc(str(gds_path.relative_to(REPO_ROOT)))

    composed_rules = Counter(composed_drc.get("rule_counts") or {})
    ring_rules = Counter(ring_drc.get("rule_counts") or {})
    new_rules = {rule: count for rule, count in (composed_rules - ring_rules).items()}

    return {
        "region": rid,
        "ring_gds": str(gds_path.relative_to(REPO_ROOT)),
        "ring_bbox_um": bbox,
        "guard_inner_um": {"w_um": region["inner_w_um"], "h_um": region["inner_h_um"]},
        "fit_offset_um": {"x": origin_x, "y": origin_y},
        "composed": _drc_summary(composed_drc),
        "ring_standalone": _drc_summary(ring_drc),
        "new_violation_rule_counts_from_fit": new_rules,
        "new_violations_from_fit": sum(new_rules.values()),
    }


# --------------------------------------------------------------------------- #
# GDSII timestamp normalisation
# --------------------------------------------------------------------------- #
#
# `klt gen` / `klt gen-compose` stamp wall-clock time into the GDSII BGNLIB
# and BGNSTR records, so two runs of the same generator on the same inputs
# produce different bytes. A golden-artefact flow cannot byte-compare that, and
# this repository's own writer (`layout/testcells/gdsii.py`) zeroes the same
# fields for the same reason -- see layout/README.md. Filed upstream; until it
# lands, the streams committed here are normalised on the way in.

_BGNLIB = 0x0102
_BGNSTR = 0x0502


def normalise_gds(raw: bytes) -> bytes:
    """Return `raw` with every BGNLIB/BGNSTR timestamp field zeroed."""
    out = bytearray(raw)
    offset = 0
    while offset + 4 <= len(out):
        length, record = struct.unpack_from(">HH", out, offset)
        if length < 4:
            break
        if record in (_BGNLIB, _BGNSTR):
            for index in range(offset + 4, offset + length):
                out[index] = 0
        offset += length
    return bytes(out)


# --------------------------------------------------------------------------- #
# Area model
# --------------------------------------------------------------------------- #


def load_stdcell_areas(pdk) -> tuple[dict[str, float], Path]:
    lef = (
        pdk.path
        / "libs.ref"
        / area_estimate.STDCELL_LIB
        / "lef"
        / f"{area_estimate.STDCELL_LIB}.lef"
    )
    if not lef.is_file():
        raise FlowError(f"standard-cell LEF not found at {lef}")
    return area_estimate.load_cell_areas(lef), lef


def stdcell_area(areas: dict[str, float], suffix: str) -> float:
    key = f"{area_estimate.STDCELL_LIB}__{suffix}"
    if key not in areas:
        raise FlowError(f"{key} not found in the LEF")
    return areas[key]


def digital_inventory() -> tuple[Counter, list[tuple[str, Counter, bool]]]:
    """The three digital blocks' cell inventories, from the one copy of them."""
    per_block: list[tuple[str, Counter, bool]] = []
    shipped: Counter = Counter()
    for name, inventory, is_shipped in digital.BLOCKS:
        counts: Counter = Counter()
        for entry in inventory:
            counts.update(entry[1])
        per_block.append((name, counts, is_shipped))
        if is_shipped:
            shipped.update(counts)
    return shipped, per_block


# --------------------------------------------------------------------------- #
# Environment
# --------------------------------------------------------------------------- #


def klt_version() -> str | None:
    if shutil.which("klt") is None:
        return None
    try:
        done = subprocess.run(["klt", "--version"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return (done.stdout or done.stderr).strip() or None


def resolve_pdk():
    try:
        from sim.harness import pdk as pdk_mod
    except ImportError:  # pragma: no cover
        return None
    try:
        return pdk_mod.find_pdk()
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# The flow
# --------------------------------------------------------------------------- #


def build(pdk) -> dict:
    """Run every stage and return the report that gets committed/compared."""
    variant = pdk.variant
    stdcells, lef = load_stdcell_areas(pdk)

    core = read_subckts(REPO_ROOT / "design" / "ro_array_core.spice")
    sampler = read_subckts(REPO_ROOT / "design" / "sampler_core.spice")

    # --- 1. per-region cell inventories -----------------------------------
    inventories: dict[str, Counter] = {
        "ring1": instance_counts(core, "ro_array_core", "xr1"),
        "ring2": instance_counts(core, "ro_array_core", "xr2"),
        "combiner_sampler": (
            instance_counts(core, "ro_array_core", "xa1")
            + all_instances_of(sampler, "sampler_core", "sampler_dff")
        ),
    }
    digital_cells, digital_blocks = digital_inventory()

    starve = {
        "ring1": starve_geometry(core, "ro_array_core", "xr1"),
        "ring2": starve_geometry(core, "ro_array_core", "xr2"),
    }

    # --- 2. starve-device footprints, measured ----------------------------
    print("== starve devices ==")
    device_footprints: dict[str, dict] = {}
    for region_id, geometry in starve.items():
        for flavor in ("nfet", "pfet"):
            key = f"{flavor}_w{geometry['w_um']:.3f}_l{geometry['l_um']:.3f}"
            if key in device_footprints:
                continue
            stem = f"fp_dev_{key}".replace(".", "p")
            response = gen_mos(flavor, geometry["w_um"], geometry["l_um"], variant, stem)
            box = response["bbox_um"]
            area = (box["x1"] - box["x0"]) * (box["y1"] - box["y0"])
            drc = run_drc(f"layout/.work/{stem}.gds")
            device_footprints[key] = {
                "flavor": flavor,
                "drawn_w_um": geometry["w_um"],
                "generated_w_um": max(geometry["w_um"], GEN_MIN_W_UM),
                "l_um": geometry["l_um"],
                "footprint_um2": round(area, 4),
                "drc_status": drc.get("status"),
                "drc_rule_counts": drc.get("rule_counts"),
            }
            print(
                f"  {flavor} W={geometry['w_um']:.3f} (generated at "
                f"{max(geometry['w_um'], GEN_MIN_W_UM):.2f}) L={geometry['l_um']:.2f}"
                f" -> {area:8.3f} um^2   drc {drc.get('status')}"
            )
    print()

    def starve_area(region_id: str, flavor: str) -> float:
        geometry = starve[region_id]
        key = f"{flavor}_w{geometry['w_um']:.3f}_l{geometry['l_um']:.3f}"
        return device_footprints[key]["footprint_um2"]

    # --- 3. per-region cell area ------------------------------------------
    regions: list[dict] = []
    for spec in REGIONS:
        rid = spec["id"]
        if rid == "digital":
            cell_area = sum(stdcell_area(stdcells, k) * v for k, v in digital_cells.items())
            breakdown = [
                {
                    "cell": name,
                    "count": sum(counts.values()),
                    "area_um2": round(
                        sum(stdcell_area(stdcells, k) * v for k, v in counts.items()), 2
                    ),
                    "shipped": is_shipped,
                }
                for name, counts, is_shipped in digital_blocks
            ]
            contents = f"{sum(digital_cells.values())} standard cells"
            cell_count = sum(digital_cells.values())
        else:
            cell_area = 0.0
            breakdown = []
            for cell, count in sorted(inventories[rid].items()):
                model = CELL_MODEL[cell]
                unit = stdcell_area(stdcells, model["stdcell"])
                for flavor in model["starve"]:
                    unit += starve_area(rid if rid.startswith("ring") else "ring1", flavor)
                cell_area += unit * count
                breakdown.append({
                    "cell": cell,
                    "count": count,
                    "priced_as": model["stdcell"]
                    + ("".join(f" + {f} starve" for f in model["starve"])),
                    "unit_um2": round(unit, 3),
                    "area_um2": round(unit * count, 2),
                    "shipped": True,
                })
            contents = " + ".join(
                f"{c}x {n}" for n, c in sorted(inventories[rid].items())
            )
            cell_count = sum(inventories[rid].values())

        placed = {f"{int(u * 100)}pct": cell_area / u for u in UTILISATION}
        side = round(math.sqrt(cell_area / GEOMETRY_UTILISATION), 2)

        # The guarded-region footprint below: real assembled geometry where
        # it exists (issue #119, Option A), the area/utilisation estimate's
        # sqrt(area) square everywhere else (`combiner_sampler`, `digital`,
        # not yet assembled). Either way this is what `gen_guard_ring` below
        # actually encloses -- `footprint_source` records which one, and why.
        if rid in ASSEMBLED_RING_GDS:
            gds_path = ASSEMBLED_RING_GDS[rid]
            bbox = read_gds_bbox(gds_path)
            inner_w_um = round(bbox["x1"] - bbox["x0"], 3)
            inner_h_um = round(bbox["y1"] - bbox["y0"], 3)
            footprint_source = {
                "kind": "assembled_gds",
                "note": (
                    "sized from the committed, DRC/LVS-clean assembled "
                    "row's own bounding box (issue #119), not from the "
                    "area/utilisation estimate's sqrt(cell_area_um2 / "
                    "geometry_utilisation) square -- see this region's own "
                    "cell_area_um2/placed_area_um2 above for what that "
                    f"estimate alone would have given ({side:.2f} x "
                    f"{side:.2f} um)"
                ),
                "gds": str(gds_path.relative_to(REPO_ROOT)),
                "cell_name": bbox["cell_name"],
                "bbox_um": {
                    "x0": bbox["x0"], "y0": bbox["y0"],
                    "x1": bbox["x1"], "y1": bbox["y1"],
                },
            }
        else:
            inner_w_um = inner_h_um = side
            footprint_source = {
                "kind": "area_estimate",
                "note": (
                    "sqrt(cell_area_um2 / geometry_utilisation) -- see this "
                    "module's own AREA MODEL docstring. Not yet assembled, "
                    "so no committed GDS exists to size this region from "
                    "instead (issue #119's own Scope note)."
                ),
            }

        regions.append({
            **{k: v for k, v in spec.items() if k != "source"},
            "contents": contents,
            "cell_count": cell_count,
            "breakdown": breakdown,
            "cell_area_um2": round(cell_area, 2),
            "placed_area_um2": {k: round(v, 2) for k, v in placed.items()},
            "footprint_source": footprint_source,
            "inner_w_um": inner_w_um,
            "inner_h_um": inner_h_um,
        })

    # --- 4. guard rings, composition, DRC ---------------------------------
    print("== guard rings ==")
    for region in regions:
        response = gen_guard_ring(
            region["id"], region["inner_w_um"], region["inner_h_um"], variant
        )
        box = response["bbox_um"]
        region["guarded_w_um"] = round(box["x1"] - box["x0"], 3)
        region["guarded_h_um"] = round(box["y1"] - box["y0"], 3)
        region["guarded_area_um2"] = round(
            region["guarded_w_um"] * region["guarded_h_um"], 2
        )
        region["guard_taps"] = response.get("device_count")
        (WORK_DIR / f"fp_guard_{region['id']}.json").write_text(
            json.dumps(response, indent=2) + "\n"
        )
        print(
            f"  {region['id']:<18} inner {region['inner_w_um']:8.2f} x "
            f"{region['inner_h_um']:8.2f} -> guarded {region['guarded_w_um']:8.2f} x "
            f"{region['guarded_h_um']:8.2f} um ({region['guard_taps']} taps)"
        )
    print()

    # --- 4b. ring fit -- does the real geometry fit where it's reserved? --
    # The area/utilisation estimate never checked that the geometry it
    # priced actually fits where the floorplan reserves it for -- that gap
    # is what issue #119 opened. For every region whose guarded footprint
    # above came from a real assembled GDS (`ASSEMBLED_RING_GDS`), compose
    # that region's own guard ring with the real ring geometry and run
    # `klt drc` over the pair (`check_ring_fit`).
    print("== ring fit (issue #119) ==")
    ring_fit: dict[str, dict] = {}
    for region in regions:
        rid = region["id"]
        if rid not in ASSEMBLED_RING_GDS:
            continue
        fit = check_ring_fit(region, ASSEMBLED_RING_GDS[rid], variant)
        ring_fit[rid] = fit
        print(
            f"  {rid:<10} composed drc {fit['composed']['status']} "
            f"({fit['composed']['violation_count']} violations), "
            f"{fit['new_violations_from_fit']} introduced by the fit "
            f"(ring alone: {fit['ring_standalone']['status']}, "
            f"{fit['ring_standalone']['violation_count']})"
        )
    print()

    print("== composition ==")
    order = [region["id"] for region in regions]
    request, composed = compose(order, variant)
    box = composed["bbox_um"]
    print(
        f"  row bbox {box['x1'] - box['x0']:.2f} x {box['y1'] - box['y0']:.2f} um, "
        f"{ISOLATION_CHANNEL_UM:.0f} um channels"
    )

    drc = run_drc("layout/.work/trng_floorplan.gds")
    print(f"  drc {drc.get('status')} ({drc.get('violation_count')} violations)")
    print()

    # --- 5. the rollup ----------------------------------------------------
    # A channel is charged at its declared width times the height of the
    # taller of the two regions it separates. Charging every channel the full
    # row height instead would bill the two 17 um rings for the digital
    # block's 354 um -- an artefact of the 1-D row the composer supports, not
    # a property of the floorplan.
    channels = []
    for left, right in zip(regions, regions[1:]):
        span = max(left["guarded_h_um"], right["guarded_h_um"])
        channels.append({
            "between": [left["id"], right["id"]],
            "width_um": ISOLATION_CHANNEL_UM,
            "span_um": span,
            "area_um2": round(ISOLATION_CHANNEL_UM * span, 2),
        })

    def _subtotal(predicate) -> dict:
        picked = [r for r in regions if predicate(r)]
        ids = {r["id"] for r in picked}
        channel_area = sum(
            c["area_um2"] for c in channels if set(c["between"]) <= ids
        )
        guarded = sum(r["guarded_area_um2"] for r in picked)
        return {
            "regions": sorted(ids),
            "cell_area_um2": round(sum(r["cell_area_um2"] for r in picked), 2),
            "guarded_area_um2": round(guarded, 2),
            "isolation_channel_area_um2": round(channel_area, 2),
            "area_um2": round(guarded + channel_area, 2),
            "share_of_budget_pct": round(
                100.0 * (guarded + channel_area) / AREA_BUDGET_UM2, 2
            ),
        }

    guarded_total = sum(region["guarded_area_um2"] for region in regions)
    channel_total = sum(channel["area_um2"] for channel in channels)
    cell_total = sum(region["cell_area_um2"] for region in regions)

    rollup = {
        "budget_um2": AREA_BUDGET_UM2,
        "cell_area_um2": round(cell_total, 2),
        "isolation_channel_um": ISOLATION_CHANNEL_UM,
        "channels": channels,
        "guarded_region_area_um2": round(guarded_total, 2),
        "isolation_channel_area_um2": round(channel_total, 2),
        "floorplan_area_um2": round(guarded_total + channel_total, 2),
        "row_bbox_um": {
            "w": round(box["x1"] - box["x0"], 3),
            "h": round(box["y1"] - box["y0"], 3),
        },
        "placed_area_um2": {
            f"{int(u * 100)}pct": round(sum(r["placed_area_um2"][f"{int(u*100)}pct"] for r in regions), 2)
            for u in UTILISATION
        },
        "subtotals": {
            "analog": _subtotal(lambda r: r["role"] in ("entropy", "boundary")),
            "digital": _subtotal(lambda r: r["role"] == "deterministic"),
        },
    }
    rollup["share_of_budget_pct"] = round(
        100.0 * rollup["floorplan_area_um2"] / AREA_BUDGET_UM2, 1
    )

    # The DR-0016 per-ring liveness monitor is shipped RTL (#71) but
    # `digital_power_estimate.BLOCKS` still carries it as not-shipped, so it
    # is not in the totals above. Priced separately rather than either
    # silently included or silently dropped.
    liveness = next(
        (counts for name, counts, shipped in digital_blocks if not shipped), Counter()
    )
    liveness_area = sum(stdcell_area(stdcells, k) * v for k, v in liveness.items())
    rollup["excluded"] = {
        "ring_liveness_monitor_DR0016": {
            "cells": sum(liveness.values()),
            "cell_area_um2": round(liveness_area, 2),
            "note": (
                "shipped by #71 but flagged shipped=False in "
                "design/digital_power_estimate.BLOCKS; excluded from the "
                "totals above so this script reports exactly what that "
                "inventory declares"
            ),
        }
    }

    gds = normalise_gds((WORK_DIR / "trng_floorplan.gds").read_bytes())
    (WORK_DIR / "trng_floorplan.norm.gds").write_bytes(gds)

    return {
        "_comment": (
            "Generated by layout/floorplan/floorplan.py -- re-run it to reproduce. "
            "This is an inventory estimate with a stated method, not a synthesis "
            "or a layout result; see that script's module docstring and "
            "layout/floorplan/README.md."
        ),
        "deck": DECK,
        "stdcell_library": area_estimate.STDCELL_LIB,
        "stdcell_lef": str(lef.relative_to(pdk.path)),
        "utilisation": list(UTILISATION),
        "geometry_utilisation": GEOMETRY_UTILISATION,
        "device_footprints": device_footprints,
        "regions": regions,
        "rollup": rollup,
        "composition": {
            "request": request,
            "response": composed,
            "gds_sha256_timestamp_normalised": hashlib.sha256(gds).hexdigest(),
        },
        "drc": drc,
        "ring_fit": ring_fit,
    }


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #


def print_report(report: dict) -> None:
    print("== area ==")
    header = (
        f"| {'region':<24} | {'cells':>7} | {'cell um^2':>10} | "
        f"{'placed 60%':>11} | {'guarded':>10} |"
    )
    print(header)
    print("|" + "-" * (len(header) - 2) + "|")
    for region in report["regions"]:
        cells = region["cell_count"]
        print(
            f"| {region['title'][:24]:<24} | {cells:>7} | {region['cell_area_um2']:>10.1f} | "
            f"{region['placed_area_um2']['60pct']:>11.1f} | "
            f"{region['guarded_area_um2']:>10.1f} |"
        )
    print("|" + "-" * (len(header) - 2) + "|")
    rollup = report["rollup"]
    print(
        f"| {'TOTAL':<24} | {'':>7} | {rollup['cell_area_um2']:>10.1f} | "
        f"{rollup['placed_area_um2']['60pct']:>11.1f} | "
        f"{rollup['guarded_region_area_um2']:>10.1f} |"
    )
    print()
    for channel in rollup["channels"]:
        left, right = channel["between"]
        print(f"  channel {left} | {right}: {channel['width_um']:.0f} um x "
              f"{channel['span_um']:.1f} um = {channel['area_um2']:.1f} um^2")
    print()
    analog = rollup["subtotals"]["analog"]
    dig = rollup["subtotals"]["digital"]
    print(f"  entropy source + isolation : {analog['area_um2']:>9.1f} um^2 "
          f"= {analog['share_of_budget_pct']:>6.2f}% of the Area row")
    print(f"  digital section            : {dig['area_um2']:>9.1f} um^2 "
          f"= {dig['share_of_budget_pct']:>6.2f}% of the Area row")
    print(f"  floorplan area             : {rollup['floorplan_area_um2']:>9.1f} um^2 "
          f"= {rollup['floorplan_area_um2'] / 1e6:.5f} mm^2 "
          f"= {rollup['share_of_budget_pct']:.1f}% of the "
          f"{rollup['budget_um2'] / 1e6:.3f} mm^2 row")
    print(f"  composed row bbox          : {rollup['row_bbox_um']['w']:.1f} x "
          f"{rollup['row_bbox_um']['h']:.1f} um (DRC {report['drc'].get('status')})")
    excluded = rollup["excluded"]["ring_liveness_monitor_DR0016"]
    print(f"  excluded: DR-0016 ring-liveness monitor, {excluded['cells']} cells, "
          f"{excluded['cell_area_um2']:.1f} um^2 cell area")
    print()
    for rid, fit in report.get("ring_fit", {}).items():
        print(
            f"  ring fit {rid:<10}: composed drc {fit['composed']['status']}, "
            f"{fit['new_violations_from_fit']} new violation(s) from the fit "
            f"(ring alone: {fit['ring_standalone']['status']}, "
            f"{fit['ring_standalone']['violation_count']} pre-existing)"
        )
    if report.get("ring_fit"):
        print()


def print_table() -> None:
    print(f"{'region':<20} {'supply':<8} {'role':<14} contents")
    print("-" * 78)
    for spec in REGIONS:
        source = spec["source"][0]
        print(f"{spec['id']:<20} {spec['supply']:<8} {spec['role']:<14} from {source}")
    print()
    print(f"isolation channel between neighbouring regions: {ISOLATION_CHANNEL_UM:.0f} um")
    print(f"guard ring: {GUARD_RING_WIDTH_UM:.1f} um tap, contacts every "
          f"{GUARD_CONTACT_PITCH_UM:.0f} um, p-substrate tie (no well)")


# --------------------------------------------------------------------------- #
# Committed artefacts
# --------------------------------------------------------------------------- #

#: `klt` echoes absolute or scratch paths back into its own responses, and the
#: PDK path is machine state. Both are dropped before a report is committed or
#: compared -- nothing else is.
_VOLATILE_KEYS = ("gds_path", "file", "generated_at", "path")


def _stable(payload):
    if isinstance(payload, dict):
        return {
            key: _stable(value)
            for key, value in payload.items()
            if key not in _VOLATILE_KEYS
        }
    if isinstance(payload, list):
        return [_stable(item) for item in payload]
    return payload


ARTEFACTS = {
    "area.json": lambda report: {
        key: report[key]
        for key in ("_comment", "stdcell_library", "stdcell_lef", "utilisation",
                    "geometry_utilisation", "device_footprints", "regions", "rollup")
    },
    "compose.json": lambda report: report["composition"],
    "floorplan.drc.json": lambda report: report["drc"],
    # Issue #119's own check: does the real, committed ring geometry
    # actually fit inside the region its own guarded footprint reserves?
    # One entry per region in `ASSEMBLED_RING_GDS`.
    "ring_fit.json": lambda report: report["ring_fit"],
}

_REGENERATE = "-- re-run `python3 layout/floorplan/floorplan.py --write`"


def write_artefacts(report: dict) -> list[Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, project in ARTEFACTS.items():
        path = REPORT_DIR / name
        path.write_text(json.dumps(_stable(project(report)), indent=2) + "\n")
        written.append(path)
    gds = FLOORPLAN_DIR / "trng_floorplan.gds"
    gds.write_bytes((WORK_DIR / "trng_floorplan.norm.gds").read_bytes())
    written.append(gds)
    return written


def compare_artefacts(report: dict) -> list[str]:
    drift: list[str] = []
    for name, project in ARTEFACTS.items():
        path = REPORT_DIR / name
        if not path.exists():
            drift.append(f"{path.relative_to(REPO_ROOT)} is missing {_REGENERATE}")
            continue
        if json.loads(path.read_text()) != json.loads(
            json.dumps(_stable(project(report)))
        ):
            drift.append(
                f"{path.relative_to(REPO_ROOT)} does not match this run {_REGENERATE}"
            )
    gds = FLOORPLAN_DIR / "trng_floorplan.gds"
    if not gds.exists():
        drift.append(f"{gds.relative_to(REPO_ROOT)} is missing {_REGENERATE}")
    elif gds.read_bytes() != (WORK_DIR / "trng_floorplan.norm.gds").read_bytes():
        drift.append(f"{gds.relative_to(REPO_ROOT)} does not match this run {_REGENERATE}")
    return drift


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true",
                        help="refresh the committed artefacts under layout/floorplan/")
    parser.add_argument("--require-tools", action="store_true",
                        help="fail instead of skipping when klt or the PDK is absent")
    parser.add_argument("--list", action="store_true",
                        help="print the region table and exit")
    args = parser.parse_args(argv)

    if args.list:
        print_table()
        return EXIT_OK

    version = klt_version()
    pdk = resolve_pdk()
    missing = []
    if version is None:
        missing.append("klayout-tools (`klt`) is not on PATH")
    if pdk is None:
        missing.append("no gf180mcu PDK install found (see sim/harness/pdk.py)")
    if missing:
        for line in missing:
            print(f"  - {line}")
        if args.require_tools:
            print("FAIL: --require-tools was given and the flow cannot run")
            return EXIT_FAIL
        print(
            "SKIP: floorplan build -- the tools above are not available.\n"
            "      Install them to rebuild the floorplan (see layout/README.md)."
        )
        return EXIT_OK

    print(f"klt:  {version}")
    print(f"pdk:  {pdk.variant} @ {pdk.version} ({pdk.source})")
    print(f"deck: {DECK}")
    print()

    WORK_DIR.mkdir(parents=True, exist_ok=True)

    try:
        report = build(pdk)
    except FlowError as exc:
        print(f"FAIL: {exc}")
        return EXIT_FAIL

    print_report(report)

    failures: list[str] = []
    if report["drc"].get("status") != "clean":
        failures.append(
            f"floorplan DRC is {report['drc'].get('status')}, expected clean: "
            f"{report['drc'].get('rule_counts')}"
        )

    # The pass/fail signal from issue #119's ring-fit check is specifically
    # "did the fit introduce a new violation", not "is the committed ring
    # GDS itself DRC-clean against whatever deck this run happens to
    # resolve" -- that is a question about `ring_gds`, not about this
    # region's sizing, and `ring_standalone` is reported (not enforced) so
    # it stays visible without conflating the two.
    for rid, fit in report.get("ring_fit", {}).items():
        if fit["new_violations_from_fit"]:
            failures.append(
                f"region '{rid}': composing it with its real assembled ring "
                f"geometry ({fit['ring_gds']}) introduces "
                f"{fit['new_violations_from_fit']} new DRC violation(s) not "
                f"present in the ring GDS alone: "
                f"{fit['new_violation_rule_counts_from_fit']}"
            )

    if args.write:
        written = write_artefacts(report)
        print(f"== artefacts ==\n  wrote {len(written)} files under layout/floorplan/")
    else:
        drift = compare_artefacts(report)
        print("== artefacts ==")
        if drift:
            for line in drift:
                print(f"  FAIL {line}")
            failures.extend(drift)
        else:
            print("  ok   committed artefacts match this run")
    print()

    if failures:
        print(f"FAIL: {len(failures)} check(s) not met")
        return EXIT_FAIL
    print("PASS: floorplan abstract is DRC-clean and its area rollup is reproducible.")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
