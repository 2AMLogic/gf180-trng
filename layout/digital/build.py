#!/usr/bin/env python3
"""Drive the digital section's synthesized netlist through `klt
place-and-route` against gf180mcu, check what came back, and commit it.

    python3 layout/digital/build.py            # run P&R, check, write the report

This is issue #111's own bring-up: `design/trng_top/trng_top.synth.v`
(`design/synth.py`, #143 -- 2505 standard-cell instances mapped against
`gf180mcu_fd_sc_mcu9t5v0`) driven through `klt place-and-route`
(klayout-tools#629/#631 -- OpenROAD under the hood) as far as the tool gets,
followed by this script's own checks over the artefacts it returns. Per the
issue's own framing, **an explicit, measured failure is a complete outcome of
this script**, not a bug in it: `main()` records whatever `klt
place-and-route` actually reports, including a documented failure, rather
than only handling the success path.

What is committed, and what is gated behind a check
-------------------------------------------------
`klt place-and-route` returns three artefacts. This script commits all three,
the third only when `_gds_geometry_check` below passes:

- **`trng_top.def`** -- the routed DEF, OpenROAD's own output. Committed.
- **`trng_top.pnr.v`** -- the *as-built* gate-level netlist (`write_verilog`
  after CTS, resizing and antenna-diode insertion), which is what a
  post-route gate-level simulation (#147) or a golden-reference LVS run has
  to use as its reference rather than `klt synthesize`'s pre-CTS netlist.
  Committed.
- **`trng_top.gds`** -- the DEF merged with the standard cells' own GDS
  views. `_gds_geometry_check` below compares the merged stream's own extent
  against the DEF's own `DIEAREA`, and only commits the GDS (plus runs `klt
  drc` over it, gated behind the same check) when the ratio is 1:1. From
  when this script was first written until #170, that check always failed:
  every DEF-derived shape (placement coordinates, routing, vias) came out at
  exactly 2x its true size while the standard-cell geometry stayed at 1x, so
  the cells sat on a stretched grid that no longer abutted its own power
  rails -- a database-unit defect in the DEF->GDS merge, reproduced in eight
  lines and filed generically upstream as klayout-tools#1090 (see
  `layout/digital/README.md`'s "Two defects this bring-up found" section).
  Fixed upstream by klayout-tools#1114; this repository re-pinned `klt` past
  that fix in #170, and the GDS (plus `klt drc`'s report) has been committed
  since.

Why this differs from `design/synth.py`'s shape
-------------------------------------------------
`design/synth.py` doubles as a CI staleness guard (`--check`, wired into
`.github/workflows/pdk-nightly.yml`) because Yosys's mapped netlist is
byte-reproducible for the same RTL + liberty (verified empirically in that
script's own docstring). Place-and-route has no equivalent claim: OpenROAD's
global placement and detailed routing are seeded but not guaranteed
bit-identical run to run, even with `seed` held fixed, across different
`openroad` builds, thread counts or host architectures. So this script has
no `--check` mode -- there is no meaningful "is the committed result stale"
question to ask of a stochastic build step the way there is for a
deterministic synthesis pass. What is committed is the result of one
recorded run, with enough provenance (`openroad` version + pinned Docker
image digest, `klt` version, resolved PDK, liberty corner, `seed`) that a
different run can be compared against it, not assumed identical to it.

OpenROAD provisioning
----------------------
`klt place-and-route` shells out to `openroad` as a subprocess -- it is not
a Python dependency of `klt` the way `klayout`'s own bindings are.
`openroad` has no Homebrew formula and no common Linux-distro package, so
this script falls back to `layout/openroad_docker.sh` (the pinned
`openroad/orfs` Docker image) whenever a native `openroad` is not already on
`$PATH` -- see that script's own header and `layout/digital/README.md`'s
"OpenROAD" section for the pinned version and digest.

What this is not
------------------
Not signoff timing and not a finished physical implementation.
`worst_slack_ns`/`fmax_mhz` are OpenROAD's own pre-signoff STA over an
ideal, SDC-only clock with global-routing-estimated parasitics -- no
extraction, no SPEF. `floorplan.utilization_pct` and `clock_period_ns` below
are this run's own inputs, not ratified spec targets. The flow builds **no
power distribution network**: it never runs `global_connect`/`pdngen`, so
the standard cells' `VDD`/`VSS` pins belong to no net, the DEF carries no
`SPECIALNETS` section, and nothing here connects a rail to a supply pin.
Corner characterization (Fmax/area/power across the corner set) is #145's
job, not this script's; a post-route gate-level functional re-run is #147's.
`layout/digital/README.md` states all of this at length, including what a
reader may and may not cite from the committed report.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DIGITAL_DIR = REPO_ROOT / "layout" / "digital"
REPORTS_DIR = DIGITAL_DIR / "reports"

#: `klt place-and-route`'s scratch directory. Deliberately **under**
#: `layout/.work/` (the same gitignored scratch root `layout/verify.py`
#: uses) rather than the system tempdir: `layout/openroad_docker.sh` bind-
#: mounts `$(pwd)` (== `REPO_ROOT`, since `_run_klt` runs `klt` with
#: `cwd=REPO_ROOT`, and `openroad` inherits that cwd as its own subprocess
#: of `klt`) into the container at the identical absolute path, so every
#: absolute path OpenROAD's generated Tcl scripts reference (the request's
#: own `.klt/place-and-route/` output directory among them) must resolve
#: *inside* that mount -- the system tempdir (`/tmp/...` on Linux) does not.
WORK_DIR = REPO_ROOT / "layout" / ".work" / "place-and-route"

sys.path.insert(0, str(REPO_ROOT))

from layout._klt import (  # noqa: E402
    FlowError,
    _run_klt,
    klt_origin,
    klt_version,
    normalise_gds,
    resolve_pdk,
)

#: The already-committed, already-synthesized digital-section netlist
#: (design/synth.py, #143) -- read-only input to this script.
NETLIST_PATH = REPO_ROOT / "design" / "trng_top" / "trng_top.synth.v"
HDL_TOPLEVEL = "trng_top"

#: Same standard-cell library `design/synth.py` synthesized against -- NOT
#: sky130 (klayout-tools#629, resolved upstream via klayout-tools#631).
CELL_LIBRARY = "gf180mcu_fd_sc_mcu9t5v0"

#: The liberty corner every stage of this run is timed against, named
#: explicitly rather than left to `klt`'s own nominal-corner resolution.
#:
#: This library is characterised at three separate supplies (1.8 V, 3.3 V
#: and 5.0 V, 15 `.lib` files in all), and `klt`'s nominal pick is
#: documented to return the **lowest** of them -- `tt_025C_1v80`. This block
#: does not run at 1.8 V: `design/README.md` calls 3.3 V "the block's
#: ratified supply", and the raw-rate row's own binding corner
#: ([DR-0003](../../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md))
#: is `ss` / -10 % supply / +125 degC. `ss_125C_3v00` is this library's
#: closest shipped deck to exactly that corner (slow process, 3.00 V =
#: 3.3 V - 10 %, 125 degC), so it is the corner this run implements and
#: reports against. `design/synth.py` (#143, #169) pins its own liberty
#: corner explicitly too -- `tt_025C_3v30`, deliberately *not* this corner;
#: see `layout/digital/README.md`'s "Corners" section for why a pre-place
#: synthesis mapping step and this timing-closing P&R run land on different
#: decks on purpose.
CORNER = "ss_125C_3v00"

#: Floorplan/IO/constraint inputs for this run. None of these is a ratified
#: spec value -- see the module docstring's "What this is not".
#:
#: - `site`/`layer_h`/`layer_v`: ORFS's own `platforms/gf180/config.mk`
#:   reference values for `gf180mcu_fd_sc_mcu9t5v0` (`PLACE_SITE ?=
#:   GF018hv5v_green_sc9` for the `9t` track option, `IO_PLACER_H/V ?=
#:   Metal3/Metal4`), chosen so this request mirrors a real gf180 platform
#:   run rather than carrying sky130's site/layer names under a gf180mcu
#:   label.
#: - `utilization_pct`/`aspect_ratio`/`core_margin_um`: a conservative
#:   starting point at this scale (2505 instances, 708 flip-flops, two
#:   8x32-bit output FIFOs among the wide structures) -- low enough
#:   utilization to leave routing headroom for a first attempt whose
#:   question is whether this design routes at all, not how small the die
#:   can be. The die area that falls out is a consequence of this number and
#:   must not be read as an area result; `layout/digital/README.md`'s "Area"
#:   section says what may be compared against the floorplan estimate.
#: - `clock_period_ns`: 50 ns (20 MHz). No issue in this repository has set
#:   a digital-section Fmax requirement, but the ratified raw-rate row
#:   (README.md, DR-0003) needs > 1 Mbps sustained at the sampler output --
#:   one raw bit per `clk` edge, so > 1 MHz, with the stretch row at
#:   > 4 MHz. 20 MHz is 5-20x that, chosen so the timing-driven placement,
#:   CTS and routing stages have a target with real headroom to optimize
#:   toward; the reported slack is against *this* constraint, not against a
#:   spec row.
FLOORPLAN = {
    "method": "utilization",
    "utilization_pct": 40,
    "aspect_ratio": 1.0,
    "core_margin_um": 10.0,
    "site": "GF018hv5v_green_sc9",
}
IO = {"layer_h": "Metal3", "layer_v": "Metal4"}
CONSTRAINTS = {"clock_port": "clk", "clock_period_ns": 50.0}
SEED = 1
TARGET_STAGE = "route"

#: How far the merged GDS's own extent may differ from the DEF's own
#: `DIEAREA` before `_gds_geometry_check` calls it a mismatch. The GDS
#: legitimately overhangs the die by the standard cells' own well/implant
#: margins (0.43 um per side for this library), which is well inside this
#: tolerance at a ~550 um die; the defect it is there to catch is a factor
#: of two.
GDS_EXTENT_TOLERANCE_PCT = 5.0

REPORT_PATH = REPORTS_DIR / "place_and_route.json"
DRC_REPORT_PATH = REPORTS_DIR / "drc.json"
DEF_PATH = DIGITAL_DIR / f"{HDL_TOPLEVEL}.def"
GDS_PATH = DIGITAL_DIR / f"{HDL_TOPLEVEL}.gds"
PNR_NETLIST_PATH = DIGITAL_DIR / f"{HDL_TOPLEVEL}.pnr.v"

DECK = "gf180mcu"

EXIT_OK = 0
EXIT_ENVIRONMENT = 3
EXIT_FLOW_FAILURE = 4


class PrError(RuntimeError):
    """A place-and-route run could not even be attempted."""


def _openroad_on_path() -> bool:
    return shutil.which("openroad") is not None


def _ensure_openroad_reachable() -> list[str]:
    """Return human-readable reasons `openroad` cannot be reached, or `[]`.

    Mutates `os.environ["PATH"]` (this process only, inherited by every
    subprocess it spawns -- including `klt`'s own `openroad` subprocess
    call) to prepend a directory containing an `openroad` shim pointed at
    `layout/openroad_docker.sh`, if and only if no native `openroad` is
    already on `$PATH` and `docker` is available. Never overrides a native
    `openroad` -- a real local install always wins.
    """
    if _openroad_on_path():
        return []
    if shutil.which("docker") is None:
        return [
            "openroad is not on PATH and docker is not on PATH either -- "
            "see layout/digital/README.md's 'OpenROAD' section"
        ]
    shim_dir = Path(tempfile.mkdtemp(prefix="klt-openroad-shim-"))
    shim = shim_dir / "openroad"
    shim.symlink_to(REPO_ROOT / "layout" / "openroad_docker.sh")
    os.environ["PATH"] = f"{shim_dir}{os.pathsep}{os.environ.get('PATH', '')}"
    return []


def _check_environment() -> list[str]:
    missing = []
    if klt_version() is None:
        missing.append("klayout-tools (`klt`) is not on PATH")
    if resolve_pdk() is None:
        missing.append("no gf180mcu PDK install found (see sim/harness/pdk.py)")
    if not NETLIST_PATH.is_file():
        missing.append(
            f"{NETLIST_PATH.relative_to(REPO_ROOT)} is missing -- run "
            "`python3 design/synth.py` first (#143)"
        )
    missing += _ensure_openroad_reachable()
    return missing


def _write_request(request_path: Path) -> None:
    request = {
        "schema": "klt.place_and_route.request/1",
        "engine": "openroad",
        "netlist": str(NETLIST_PATH),
        "hdl_toplevel": HDL_TOPLEVEL,
        "pdk": {"cell_library": CELL_LIBRARY, "corner": CORNER},
        "floorplan": dict(FLOORPLAN),
        "io": dict(IO),
        "constraints": dict(CONSTRAINTS),
        "seed": SEED,
        "target_stage": TARGET_STAGE,
    }
    request_path.write_text(json.dumps(request, indent=2) + "\n")


# --------------------------------------------------------------------------- #
# Checks over what the tool returned
# --------------------------------------------------------------------------- #

_DIEAREA_RE = re.compile(
    r"^DIEAREA\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)\s*;",
    re.M,
)
_UNITS_RE = re.compile(r"^UNITS\s+DISTANCE\s+MICRONS\s+(\d+)\s*;", re.M)
_COMPONENTS_RE = re.compile(r"^COMPONENTS\s+(\d+)\s*;", re.M)
#: A `SPECIALNETS` section is how a DEF carries power/ground geometry. Its
#: *absence* is the recorded evidence that this flow builds no power
#: delivery at all (klayout-tools#1091) -- see `layout/digital/README.md`.
_SPECIALNETS_RE = re.compile(r"^SPECIALNETS\s+\d+\s*;", re.M)


def _def_summary(def_path: Path) -> dict:
    """Die extent (um), database units and component count, read from the
    DEF's own header -- the reference every check below compares against,
    because the DEF is OpenROAD's own direct output and the GDS is a
    downstream merge of it."""
    text = def_path.read_text(errors="replace")
    units = _UNITS_RE.search(text)
    die = _DIEAREA_RE.search(text)
    components = _COMPONENTS_RE.search(text)
    dbu_per_um = int(units.group(1)) if units else None
    summary: dict = {
        "database_units_per_um": dbu_per_um,
        "component_count": int(components.group(1)) if components else None,
        "die_width_um": None,
        "die_height_um": None,
        "special_nets": _SPECIALNETS_RE.search(text) is not None,
    }
    if die is not None and dbu_per_um:
        x0, y0, x1, y1 = (int(v) for v in die.groups())
        summary["die_width_um"] = round((x1 - x0) / dbu_per_um, 4)
        summary["die_height_um"] = round((y1 - y0) / dbu_per_um, 4)
    return summary


def _gds_extent_um(gds_path: Path) -> tuple[float, float]:
    """Top-cell bounding box of `gds_path`, in microns.

    Read through `klt stats`, never `klayout.db` directly -- the same rule
    `layout/floorplan/floorplan.py`'s own `read_gds_bbox` follows, and for
    the same reason: one tool, one resolved PDK, one set of numbers.
    """
    box = _run_klt(
        ["stats", str(gds_path.relative_to(REPO_ROOT))], timeout_s=900
    )["bbox_um"]
    return (box["width"], box["height"])


def _gds_geometry_check(gds_path: Path, def_summary: dict) -> dict:
    """Does the merged GDS describe the same design the DEF does?

    The DEF is OpenROAD's own output and is the reference; the GDS is a
    downstream merge of that DEF with the standard cells' GDS views, and a
    merge that silently rescales one side of that merge relative to the
    other produces a file that opens fine, passes a cell-name check, and is
    geometrically meaningless. Comparing the merged stream's own extent
    against the DEF's own `DIEAREA` is the cheapest check that catches it:
    a correct merge lands within a standard cell's well overhang of the die
    (0.43 um per side for this library), and the defect this exists to catch
    is a factor of two.

    Returns a dict recorded verbatim in the committed report -- `status` is
    `"ok"`, `"mismatch"`, or `"skipped"` (no DEF reference to compare
    against).
    """
    expected_w = def_summary.get("die_width_um")
    expected_h = def_summary.get("die_height_um")
    if expected_w is None or expected_h is None:
        return {
            "status": "skipped",
            "reason": "DEF declares no parseable DIEAREA/UNITS to compare against",
        }
    width_um, height_um = _gds_extent_um(gds_path)
    ratios = (width_um / expected_w, height_um / expected_h)
    worst = max(abs(ratio - 1.0) for ratio in ratios)
    return {
        "status": "ok" if worst * 100.0 <= GDS_EXTENT_TOLERANCE_PCT else "mismatch",
        "def_die_um": [expected_w, expected_h],
        "gds_extent_um": [round(width_um, 4), round(height_um, 4)],
        "gds_over_def_ratio": [round(ratios[0], 4), round(ratios[1], 4)],
        "tolerance_pct": GDS_EXTENT_TOLERANCE_PCT,
    }


def _netlist_instance_count(netlist_path: Path) -> int | None:
    """Count `CELL_LIBRARY` instantiations in a gate-level netlist.

    Every instance in either netlist here is a flat standard-cell
    instantiation of the form `<library>__<cell> <name> (...)`, one per
    statement, so counting the instantiated master names counts the
    instances -- no Verilog parse needed, and nothing else in the file
    mentions a master name at statement start.
    """
    if not netlist_path.is_file():
        return None
    pattern = re.compile(rf"^\s*{re.escape(CELL_LIBRARY)}__\S+\s+\S+", re.M)
    return len(pattern.findall(netlist_path.read_text(errors="replace")))


def _component_check(def_summary: dict) -> dict:
    """Do the DEF and the as-built netlist describe the same instance set?

    That is the invariant worth checking, and it is not the same as "the DEF
    has at least as many components as the synthesized netlist had
    instances": OpenROAD's own `repair_design`/`repair_timing` legitimately
    *removes* redundant buffers as well as adding CTS buffers and resizes, so
    the placed count can land either side of the synthesized one. What must
    hold is that `write_def` and `write_verilog` -- the two artefacts this
    script commits, which downstream consumers (#145's STA, #147's
    gate-level re-run) have to be able to use together -- agree with each
    other. The delta against the synthesized input is recorded alongside as
    information, not as a verdict.
    """
    placed = def_summary.get("component_count")
    as_built = _netlist_instance_count(PNR_NETLIST_PATH)
    synth_report = REPO_ROOT / "design" / HDL_TOPLEVEL / f"{HDL_TOPLEVEL}.synth.json"
    synthesized = None
    if synth_report.is_file():
        try:
            synthesized = json.loads(synth_report.read_text()).get("instance_count")
        except (OSError, json.JSONDecodeError):
            synthesized = None
    if placed is None or as_built is None:
        return {
            "status": "skipped",
            "reason": "no COMPONENTS count in the DEF, or no as-built netlist",
            "placed": placed,
            "as_built_netlist": as_built,
            "synthesized": synthesized,
        }
    return {
        "status": "ok" if placed == as_built else "mismatch",
        "placed": placed,
        "as_built_netlist": as_built,
        "synthesized": synthesized,
        "delta_vs_synthesized": (
            placed - synthesized if synthesized is not None else None
        ),
    }


def run_drc(gds_path: Path) -> dict:
    """`klt drc` over the merged GDS, the same deck and invocation shape
    `layout/verify.py` runs over every other cell in this repository."""
    return _run_klt(
        ["drc", str(gds_path.relative_to(REPO_ROOT)), "--deck", DECK], timeout_s=1800
    )


def _drc_summary(payload: dict) -> dict:
    """The committed view of a `klt drc` payload: the verdict and the
    per-rule counts, without the full per-violation polygon dump (which runs
    to megabytes over a design this size and says nothing a rule count and a
    re-run do not)."""
    return {
        "status": payload.get("status"),
        "deck": payload.get("deck"),
        "violation_count": payload.get("violation_count"),
        "rule_counts": payload.get("rule_counts"),
    }


# --------------------------------------------------------------------------- #
# The run
# --------------------------------------------------------------------------- #


def _committed_view(payload: dict) -> dict:
    """The form of `klt place-and-route`'s response that belongs in the
    committed report -- restates `def_path`/`gds_path`/`verilog_path` (all
    scratch-directory, machine-local absolute paths under `WORK_DIR` in the
    raw payload) to the *committed* `layout/digital/` locations `build()`
    copies them to, the same "restate the one field that names a scratch
    location" discipline `design/synth.py`/`layout/verify.py` apply to
    `netlist_path`/`extract`'s own scratch paths. Also drops
    `provenance.pdk.source` (machine-local, not part of what was verified --
    `design/synth.py`'s own `_committed_view` does the same for the
    identical field) and `layer_map.path` (an absolute host path into the
    local PDK install, not a repository-relative one).
    """
    restated = dict(payload)
    layer_map = restated.get("layer_map")
    if isinstance(layer_map, dict):
        restated["layer_map"] = {"resolution": layer_map.get("resolution")}
    provenance = dict(restated.get("provenance") or {})
    pdk = provenance.get("pdk")
    if isinstance(pdk, dict):
        pdk = dict(pdk)
        pdk.pop("source", None)
        provenance["pdk"] = pdk
    restated["provenance"] = provenance
    restated["request"] = {
        "pdk": {"cell_library": CELL_LIBRARY, "corner": CORNER},
        "floorplan": FLOORPLAN,
        "io": IO,
        "constraints": CONSTRAINTS,
        "seed": SEED,
        "target_stage": TARGET_STAGE,
    }
    return restated


def place_and_route(work_dir: Path) -> tuple[dict, Path | None, Path | None, Path | None]:
    """Run `klt place-and-route` with `work_dir` as the request's own
    directory. Returns `(payload, def_path, gds_path, verilog_path)` with the
    three paths pointing into the scratch directory. Raises `PrError` for a
    missing tool/PDK/input; a documented engine failure (the run does not
    reach `TARGET_STAGE`) is *not* a `PrError` -- `klt`'s own `{"error":
    ...}` payload propagates as a `FlowError` from `_run_klt`, which `main()`
    below catches and records as a valid, complete outcome (see the module
    docstring)."""
    missing = _check_environment()
    if missing:
        raise PrError("; ".join(missing))

    request_path = work_dir / "request.json"
    _write_request(request_path)

    args = ["place-and-route", str(request_path)]
    pdk = resolve_pdk()
    if pdk is not None:
        args += ["--pdk", pdk.variant]

    payload = _run_klt(args, timeout_s=7200)

    def _path(key: str) -> Path | None:
        value = payload.get(key)
        return Path(value) if value else None

    return payload, _path("def_path"), _path("gds_path"), _path("verilog_path")


def build() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)
    try:
        payload, def_path, gds_path, verilog_path = place_and_route(WORK_DIR)
    except PrError as exc:
        print(f"ERROR  {exc}", file=sys.stderr)
        return EXIT_ENVIRONMENT
    except FlowError as exc:
        print(f"FAILED  {exc}", file=sys.stderr)
        print(
            "       an explicit, measured failure is a complete, documented "
            "outcome for this run (issue #111) -- see layout/digital/README.md",
            file=sys.stderr,
        )
        return EXIT_FLOW_FAILURE

    report = _committed_view(payload)
    checks: dict = {}
    written: list[Path] = []
    warnings: list[str] = []

    # The as-built netlist lands first: `_component_check` compares the DEF
    # against it, so it has to be on disk before the DEF's own checks run.
    if verilog_path is not None and verilog_path.is_file():
        shutil.copyfile(verilog_path, PNR_NETLIST_PATH)
        written.append(PNR_NETLIST_PATH)
        report["verilog_path"] = str(PNR_NETLIST_PATH.relative_to(REPO_ROOT))
    else:
        report["verilog_path"] = None

    if def_path is not None and def_path.is_file():
        shutil.copyfile(def_path, DEF_PATH)
        written.append(DEF_PATH)
        def_summary = _def_summary(DEF_PATH)
        checks["def"] = def_summary
        checks["components"] = _component_check(def_summary)
        if checks["components"]["status"] == "mismatch":
            warnings.append(
                "the routed DEF and the as-built netlist disagree on instance "
                f"count ({checks['components']['placed']} vs "
                f"{checks['components']['as_built_netlist']})"
            )
    else:
        def_summary = {}
        checks["def"] = {"status": "skipped", "reason": "no DEF returned"}
        checks["components"] = {"status": "skipped", "reason": "no DEF returned"}

    drc: dict | None = None
    if gds_path is not None and gds_path.is_file():
        geometry = _gds_geometry_check(gds_path, def_summary)
        checks["gds_geometry"] = geometry
        if geometry["status"] == "mismatch":
            warnings.append(
                "the merged GDS does not match the DEF's own DIEAREA "
                f"(ratio {geometry['gds_over_def_ratio']}) -- not committed; "
                "see layout/digital/README.md's 'Two defects this bring-up found'"
            )
        else:
            # Zero the BGNLIB/BGNSTR wall-clock timestamp fields the
            # DEF->GDS merge's KLayout writer stamps in, same as every other
            # stream in this repository (klayout-tools#320, layout/_klt.py's
            # own docstring) -- one axis of run-to-run nondeterminism
            # removed, though (per the module docstring) OpenROAD's own
            # placement/routing is not claimed byte-reproducible beyond that.
            GDS_PATH.write_bytes(normalise_gds(gds_path.read_bytes()))
            written.append(GDS_PATH)
            drc = _drc_summary(run_drc(GDS_PATH))
            DRC_REPORT_PATH.write_text(json.dumps(drc, indent=2) + "\n")
            written.append(DRC_REPORT_PATH)
            if drc.get("status") != "clean":
                warnings.append(
                    f"klt drc over the merged GDS: {drc.get('status')} "
                    f"({drc.get('violation_count')} violations)"
                )
    else:
        checks["gds_geometry"] = {"status": "skipped", "reason": "no GDS returned"}

    report["gds_path"] = (
        str(GDS_PATH.relative_to(REPO_ROOT)) if GDS_PATH in written else None
    )
    report["def_path"] = (
        str(DEF_PATH.relative_to(REPO_ROOT)) if DEF_PATH in written else None
    )
    report["checks"] = checks
    report["drc"] = drc
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    written.append(REPORT_PATH)

    origin = klt_origin()
    commit = (origin or {}).get("commit")
    print(f"klt:  {klt_version()}" + (f" (built from {commit})" if commit else ""))
    print(f"corner:        {CELL_LIBRARY}__{CORNER}")
    print(f"stage_reached: {report.get('stage_reached')}")
    print(f"worst_slack:   {report.get('worst_slack_ns')} ns @ {CORNER}")
    print(
        f"swept setup/hold: {report.get('worst_setup_slack_ns')} / "
        f"{report.get('worst_hold_slack_ns')} ns (all shipped corners)"
    )
    for path in written:
        print(f"wrote  {path.relative_to(REPO_ROOT)}")
    for warning in warnings:
        print(f"WARNING  {warning}")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="build.py",
        description=(
            "Run the trng_top digital-section place-and-route against "
            "gf180mcu (#111), check the artefacts, and commit the result."
        ),
    )
    parser.parse_args(argv)
    return build()


if __name__ == "__main__":
    raise SystemExit(main())
