#!/usr/bin/env python3
"""Run `klt lvs` for the digital section against its own as-built netlist.

    python3 layout/digital/lvs.py          # (re)generate the reference,
                                            # extract, compare, write the report

The reference netlist a digital-section LVS has to compare against is
`trng_top.pnr.v` -- the *as-built* gate-level netlist `build.py` already
commits (CTS buffers and resizer swaps included), not `design/trng_top/
trng_top.synth.v`'s pre-place mapping (issue #170). `klt lvs`'s own reference
side, though, is a SPICE netlist read via `NetlistSpiceReader` -- there is no
verb that takes a Verilog reference directly (`docs/cli/lvs.md`'s "Machine-
generated macro-scale fixture" section states this outright: "a true golden-
reference check (translating `klt synthesize`'s gate-level Verilog netlist to
SPICE) is out of scope -- no Verilog->SPICE bridge exists in this repo
today"). This script is that bridge, built once, for this one netlist shape.

Why a **cell-instance-granularity** bridge, not a transistor-level one
-----------------------------------------------------------------------
A literal SPICE translation would have to expand every one of 2499 placed
standard-cell instances into its own transistor-level `.SUBCKT` body (copied
from the library's own CDL) and then rely on `klt extract`'s ordinary flat
extraction to rebuild the same transistors from the merged GDS's drawn
geometry -- workable in principle, intractable to get right for a first pass
at this scale, and it re-derives something the standard-cell layouts
presumably already got right on their own (which is not what this run is
testing).

`klt extract --abstract-cells` (klayout-tools#620, closed 2026-08-11 --
resolved after `docs/cli/lvs.md`'s "no bridge" language above was written)
changes the shape of the problem: every instantiated
`gf180mcu_fd_sc_mcu9t5v0__*` cell extracts as an opaque, pinned black box --
one empty `.SUBCKT <cell type>` per distinct type, one `X<instance>` card per
placed instance -- instead of being flattened to its own transistors. That
is structurally the *same* data `trng_top.pnr.v` already carries: a cell type
name, an instance name, and a set of named-pin connections. So this script's
reference netlist is a direct, mechanical transcription of the Verilog
netlist into that same black-box SPICE shape, and the comparison this
enables is exactly what a first digital LVS run needs to answer: does the
routed layout's cell-to-cell connectivity match what P&R actually built?
Not: is every standard cell's own internal transistor layout DRC/LVS-correct
(that is each cell's own bring-up, out of scope for a 2505-instance macro
netlist).

Power/ground: compared, since #171
------------------------------------------------------------------------
Every standard cell's own GDS view draws real `VDD`/`VSS` pin labels on
Metal1 (verified directly: `klt extract`'s in-cell-label pin resolution
takes priority over `--abstract-cell-lef`, and every checked cell type in
this library labels its functional pins plus `VDD`/`VSS` -- not `VNW`/`VPW`,
which land on layers this deck does not scan for pin labels). So
`--abstract-cells` resolves `VDD`/`VSS` as two more pins on every abstracted
cell type whether this script accounts for them or not, and the only
question is what the reference side says they are connected to.

Until #171 the honest answer was "nothing checkable". That run built no PDN
at all: `global_connect`/`pdngen` never ran, so each cell's local Metal1
rail segment was wired to whatever it happened to physically abut, row by
row, with no continuous net across the design -- and this script gave every
instance's `VDD`/`VSS` its own dangling per-instance reference net, which
reported as a 7694-mismatch `net.split`/`net.merged`/`topology` cascade
attributable entirely to the missing PDN rather than to any signal-routing
defect.

#171 removed that. The committed DEF now carries a `SPECIALNETS` section
with exactly two nets, and `global_connect` wires every cell's PG pin to
them, so there *is* a single continuous power net and a single continuous
ground net to compare against. This script now reads their names from
`reports/place_and_route.json`'s own `power` block -- the record of what the
committed GDS was actually built with, rather than a constant restated here
-- and ties every instance's `VDD` to the first and every `VSS` to the
second. Power connectivity is therefore inside the comparison, not excluded
from it, and a future regression that fragmented the grid would show up here
as a `net.split` cascade instead of being invisible.

The same run also inserts 6136 physical-only instances (tapcells, endcaps
and fillers) that carry no logical function and that OpenROAD's
`write_verilog` deliberately strips from `trng_top.pnr.v` via `-remove_cells`.
They are real drawn geometry in the GDS, so `klt extract` sees them and the
reference has to as well, or every one of their nine cell types is an
unmatchable layout-side circuit. `_def_physical_only_instances()` reads them
back out of the committed DEF's own `COMPONENTS` section and
`_write_reference()` emits one two-pin card per instance onto the same two
supply nets -- the only connection those cells have.

Neither side promotes a supply to a *top-level* pin: `run_extract`'s `--pins`
declares the 109 real chip I/O nets and nothing else, so the DEF's own
`vddd`/`vss` `PINS` entries stay internal nets on both sides and the two
`.SUBCKT trng_top` headers keep matching interfaces.

Pipeline
--------
1. `_yosys_netlist()` -- `yosys -p "read_verilog ...; write_json ..."` turns
   `trng_top.pnr.v` into a structured cell/net graph (issue #170 tried a
   hand-rolled regex parser first and dropped it: Verilog's escaped-
   identifier syntax -- a backslash-led name like escaped "u_conditioner/
   _001_" with its *significant trailing space* -- is exactly the kind of
   thing a text parser gets subtly wrong without a real front end behind
   it).
2. `_write_reference()` walks that graph and writes
   `trng_top.lvs_reference.spice`: one empty `.SUBCKT <cell type>
   <sorted signal pins> VDD VSS` per distinct instantiated cell type (pin
   order alphabetical -- the same convention `klt extract`'s own
   `_resolve_abstract_cell_pins` documents for its in-cell-label path, so
   the two sides describe the same interface even though this script never
   calls that function), and one top-level `.SUBCKT trng_top <109 chip
   pins> ... X<instance> ... .ENDS` transcribing every placed cell
   instance's connections verbatim, plus the physical-only instances read
   from the DEF, with `VDD`/`VSS` on the two supply nets per the section
   above.
3. `klt extract --abstract-cells 'gf180mcu_fd_sc_mcu9t5v0__*' --top-cell-pins
   --def-net-names` over the committed `trng_top.gds` -- the layout side,
   written to `trng_top.extracted.spice` (`--def-net-names` recovers the
   design's own net names from the DEF->GDS merge's own net-name shape
   property instead of KLayout's synthesized `$<id>` placeholders, so a
   mismatch report is readable against the same names `trng_top.pnr.v`
   itself uses).
4. `klt lvs` compares the two, `layout.top`/`reference.top` both pinned to
   `trng_top` explicitly. The report lands at `reports/lvs.json`, the same
   "verdict plus counts, not a full per-mismatch dump" shape `build.py`'s
   own `_drc_summary` uses for the DRC side of this directory.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DIGITAL_DIR = REPO_ROOT / "layout" / "digital"
REPORTS_DIR = DIGITAL_DIR / "reports"
WORK_DIR = REPO_ROOT / "layout" / ".work" / "digital-lvs"

sys.path.insert(0, str(REPO_ROOT))

from layout._klt import _run_klt, klt_origin, klt_version  # noqa: E402

PNR_NETLIST_PATH = DIGITAL_DIR / "trng_top.pnr.v"
GDS_PATH = DIGITAL_DIR / "trng_top.gds"
DEF_PATH = DIGITAL_DIR / "trng_top.def"
PNR_REPORT_PATH = REPORTS_DIR / "place_and_route.json"
REFERENCE_PATH = DIGITAL_DIR / "trng_top.lvs_reference.spice"
EXTRACTED_PATH = DIGITAL_DIR / "trng_top.extracted.spice"
LVS_REQUEST_PATH = DIGITAL_DIR / "trng_top.lvs-request.json"
LVS_REPORT_PATH = REPORTS_DIR / "lvs.json"

HDL_TOPLEVEL = "trng_top"
CELL_PREFIX = "gf180mcu_fd_sc_mcu9t5v0__"
CELL_GLOB = f"{CELL_PREFIX}*"
DECK = "gf180mcu"

#: See the module docstring's "Power/ground" section -- every abstracted cell
#: type resolves these two pins from its own drawn GDS labels regardless of
#: what this script does, so the reference has to declare them too, or every
#: cell type is an instant `device.class_arity` mismatch (wrong pin count)
#: before topology is even compared. These are the *cell pin* names, fixed by
#: the library's own LEF/GDS; the *net* names they are tied to come from the
#: committed P&R report -- see `_power_nets`.
POWER_PINS = ("VDD", "VSS")

#: Matches a `COMPONENTS` entry's `- <instance> <master>` opening line --
#: `_def_physical_only_instances` reads the tapcell/endcap/filler instances
#: back out of the committed DEF through this.
_COMPONENT_ENTRY_RE = re.compile(r"^\s*-\s+(\S+)\s+(\S+)", re.M)


class LvsFlowError(RuntimeError):
    """The reference-generation or extract/compare pipeline could not run."""


def _pnr_power() -> dict:
    """`reports/place_and_route.json`'s own `power` block.

    Read from the committed report rather than restated as a constant here:
    that report is the record of how the committed `trng_top.gds`/
    `trng_top.def` this script compares were actually built, so a reference
    generated against anything else would be describing a different layout.
    """
    if not PNR_REPORT_PATH.is_file():
        raise LvsFlowError(
            f"{PNR_REPORT_PATH.relative_to(REPO_ROOT)} is missing -- run "
            "`python3 layout/digital/build.py` first"
        )
    power = (json.loads(PNR_REPORT_PATH.read_text()) or {}).get("power") or {}
    if not power.get("global_connect"):
        raise LvsFlowError(
            f"{PNR_REPORT_PATH.relative_to(REPO_ROOT)} reports no "
            "`global_connect` -- the committed layout has no power delivery "
            "network, so this script cannot build a reference that describes "
            "it (see this script's 'Power/ground' docstring section, #171)"
        )
    return power


def _power_nets(power: dict) -> dict[str, str]:
    """Map each `POWER_PINS` cell pin onto the net the layout wires it to."""
    return {"VDD": power["power_net"], "VSS": power["ground_net"]}


def _physical_only_masters(power: dict) -> tuple[str, ...]:
    """The tapcell/endcap/filler masters this layout was built with.

    Named by `klt place-and-route`'s own response rather than pattern-matched
    out of the DEF: which masters are physical-only is the tool's fact about
    the cell library, not something a name is allowed to imply here.
    """
    named = [power.get("tapcell_master"), power.get("endcap_master")]
    named += list(power.get("filler_masters") or ())
    return tuple(name for name in named if name)


def _def_physical_only_instances(
    def_path: Path, masters: tuple[str, ...]
) -> list[tuple[str, str]]:
    """`[(master, instance_name), ...]` for every `COMPONENTS` entry in
    `def_path` instantiating one of `masters`, sorted by instance name.

    These are exactly the instances `write_verilog -remove_cells` keeps out
    of `trng_top.pnr.v` (they carry no logical function) while leaving them
    in the DEF and therefore in the merged GDS -- so the DEF is the only
    place a reference generated from the netlist can learn about them.
    """
    if not masters:
        return []
    text = def_path.read_text(errors="replace")
    start = text.find("\nCOMPONENTS ")
    end = text.find("\nEND COMPONENTS", start) if start != -1 else -1
    if start == -1 or end == -1:
        raise LvsFlowError(
            f"{def_path.relative_to(REPO_ROOT)} has no readable COMPONENTS "
            "section -- cannot recover this layout's physical-only instances"
        )
    wanted = set(masters)
    found = [
        (master, instance)
        for instance, master in _COMPONENT_ENTRY_RE.findall(text[start:end])
        if master in wanted
    ]
    if not found:
        raise LvsFlowError(
            f"{def_path.relative_to(REPO_ROOT)} instantiates none of the "
            f"physical-only masters the P&R report names ({', '.join(masters)})"
        )
    return sorted(found, key=lambda entry: entry[1])


def _yosys_netlist(verilog_path: Path, json_path: Path) -> dict:
    """`yosys -p "read_verilog ...; write_json ..."`, parsed.

    Run from `REPO_ROOT` with repo-relative paths (`design/synth.py`'s own
    convention, and required outright for a WASI-sandboxed `yosys` build,
    which only has filesystem access under the invoking directory -- not
    `/tmp`).
    """
    if shutil.which("yosys") is None:
        raise LvsFlowError(
            "yosys is not on PATH -- needed to parse trng_top.pnr.v into a "
            "structured cell/net graph (see this script's module docstring)"
        )
    rel_v = verilog_path.relative_to(REPO_ROOT)
    rel_j = json_path.relative_to(REPO_ROOT)
    script = f"read_verilog {rel_v}; write_json {rel_j}"
    done = subprocess.run(
        ["yosys", "-p", script],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=300,
    )
    if done.returncode != 0 or not json_path.is_file():
        raise LvsFlowError(
            f"yosys could not parse {rel_v}: {(done.stderr or done.stdout)[-2000:]}"
        )
    return json.loads(json_path.read_text())


def _bit_names(module: dict) -> dict[int, str]:
    """Map every bit id in `module` to one canonical net name string.

    Top-level port bits get the chip-pin name a DEF/GDS pin label actually
    uses (`"reg_addr[0]"`, scalar port names bare) -- verified directly
    against `trng_top.def`'s own `PINS` section, which names every one of
    this design's 109 pins the same way. Every other named bit takes the
    shortest, then lexicographically first, `netnames[...]` entry that
    covers it (multiple hierarchical aliases commonly cover the same bit;
    picking one deterministically is all correctness requires -- `klt lvs`
    compares topology, not text). A bit with no covering name at all (never
    observed in this netlist -- OpenROAD's `write_verilog` names every net
    it emits -- but not structurally impossible) falls back to `net<id>`.
    """
    names: dict[int, str] = {}
    for port, spec in module["ports"].items():
        bits = spec["bits"]
        if len(bits) == 1:
            names[bits[0]] = port
        else:
            for index, bit in enumerate(bits):
                names.setdefault(bit, f"{port}[{index}]")

    candidates: dict[int, list[str]] = {}
    for name, spec in module["netnames"].items():
        bits = spec["bits"]
        if len(bits) == 1:
            candidates.setdefault(bits[0], []).append(name)
        else:
            for index, bit in enumerate(bits):
                candidates.setdefault(bit, []).append(f"{name}[{index}]")
    for bit, options in candidates.items():
        names.setdefault(bit, min(options, key=lambda s: (len(s), s)))

    return names


def _cell_instances(module: dict, bit_names: dict[int, str]) -> tuple[
    dict[str, list[str]], list[tuple[str, str, dict[str, str]]]
]:
    """Return `(cell_type -> sorted pin list, [(type, instance, {pin: net})])`.

    `cell_type`'s pin list is the union of every port name any instance of
    that type actually connects (every checked instance of a type uses the
    identical port set in this netlist, so "union" and "first instance's
    set" agree; union is the defensive choice), plus `POWER_PINS`, sorted
    -- see the module docstring for why this exact convention (alphabetical,
    library-declared pins plus VDD/VSS) matches `--abstract-cells`'s own
    resolved interface for the same cell type.
    """
    pins_by_type: dict[str, set[str]] = {}
    instances: list[tuple[str, str, dict[str, str]]] = []
    for inst_name, cell in module["cells"].items():
        cell_type = cell["type"]
        if not cell_type.startswith(CELL_PREFIX):
            raise LvsFlowError(
                f"instance '{inst_name}' has cell type '{cell_type}', which "
                f"does not start with '{CELL_PREFIX}' -- this script only "
                "handles a netlist mapped entirely against that one library"
            )
        connections: dict[str, str] = {}
        for port, bits in cell["connections"].items():
            if len(bits) != 1:
                raise LvsFlowError(
                    f"instance '{inst_name}' port '{port}' is {len(bits)} "
                    "bits wide -- every standard-cell pin in this library "
                    "is scalar; a multi-bit cell port means this script's "
                    "assumptions no longer hold"
                )
            (bit,) = bits
            if isinstance(bit, str):
                raise LvsFlowError(
                    f"instance '{inst_name}' port '{port}' is tied to a "
                    f"Verilog constant ({bit!r}) rather than a real net -- "
                    "not observed in trng_top.pnr.v as of this script's "
                    "writing; add constant-net handling before trusting "
                    "this reference"
                )
            connections[port] = bit_names[bit]
        pins_by_type.setdefault(cell_type, set()).update(connections.keys())
        instances.append((cell_type, inst_name, connections))

    sorted_pins = {
        cell_type: sorted(pins | set(POWER_PINS))
        for cell_type, pins in pins_by_type.items()
    }
    instances.sort(key=lambda entry: entry[1])
    return sorted_pins, instances


def _write_reference(
    module: dict,
    path: Path,
    power_nets: dict[str, str],
    physical_only: list[tuple[str, str]],
) -> dict:
    """Write the reference SPICE and return a small provenance summary."""
    bit_names = _bit_names(module)
    pins_by_type, instances = _cell_instances(module, bit_names)

    top_ports = list(module["ports"].keys())
    top_pins: list[str] = []
    for port in top_ports:
        bits = module["ports"][port]["bits"]
        if len(bits) == 1:
            top_pins.append(port)
        else:
            top_pins.extend(f"{port}[{i}]" for i in range(len(bits)))
    top_pins.sort()

    lines = [
        "* Generated by layout/digital/lvs.py -- do not hand-edit.",
        "* Reference netlist for `klt lvs` (issue #170): a mechanical, "
        "cell-instance-granularity",
        "* transcription of trng_top.pnr.v (the as-built, post-CTS gate-level "
        "netlist), matching",
        "* `klt extract --abstract-cells`'s own black-box interface for each "
        "standard-cell type",
        "* (signal pins, alphabetical, plus VDD/VSS -- see this script's "
        "module docstring).",
        f"* Supply nets: VDD -> {power_nets['VDD']}, VSS -> "
        f"{power_nets['VSS']} (#171), read from reports/place_and_route.json.",
        "",
        f".SUBCKT {HDL_TOPLEVEL} " + " ".join(top_pins),
    ]
    for cell_type, inst_name, connections in instances:
        pins = pins_by_type[cell_type]
        nets = [
            connections.get(pin) or power_nets.get(pin) or f"{pin}${inst_name}"
            for pin in pins
        ]
        lines.append(f"X{inst_name} " + " ".join(nets) + f" {cell_type}")

    # The physical-only instances (tapcells, endcaps, fillers) `write_verilog
    # -remove_cells` keeps out of the netlist but that are drawn in the GDS.
    # Their only connection is to the two supply nets, in the same
    # alphabetical pin order every other cell type here uses.
    physical_only_pins = sorted(POWER_PINS)
    physical_only_nets = " ".join(power_nets[pin] for pin in physical_only_pins)
    for cell_type, inst_name in physical_only:
        lines.append(f"X{inst_name} {physical_only_nets} {cell_type}")

    lines.append(f".ENDS {HDL_TOPLEVEL}")
    lines.append("")

    physical_only_types = sorted({cell_type for cell_type, _ in physical_only})
    for cell_type in sorted(pins_by_type):
        lines.append(f".SUBCKT {cell_type} " + " ".join(pins_by_type[cell_type]))
        lines.append(f".ENDS {cell_type}")
        lines.append("")
    for cell_type in physical_only_types:
        lines.append(f".SUBCKT {cell_type} " + " ".join(physical_only_pins))
        lines.append(f".ENDS {cell_type}")
        lines.append("")

    path.write_text("\n".join(lines) + "\n")
    return {
        "top_pins": top_pins,
        "top_pin_count": len(top_pins),
        "instance_count": len(instances),
        "distinct_cell_types": len(pins_by_type),
        "physical_only_instance_count": len(physical_only),
        "physical_only_cell_types": physical_only_types,
        "supply_nets": dict(power_nets),
    }


def run_extract(top_pins: list[str]) -> dict:
    """`klt extract --abstract-cells ...`.

    `--pins` (a comma-separated list of the 109 real chip I/O net names) is
    load-bearing, not decoration: this design is fully flat once every
    standard cell is abstracted (no hierarchy below the chip boundary at
    all), and the DEF->GDS merge draws a GDS text label for essentially
    every routed net directly in the top cell -- so `--top-cell-pins`'s own
    below-top-label filter has nothing to filter here, and every one of
    those thousands of internal net labels (`clknet_leaf_12_clk` and
    friends) would otherwise promote to a *pin* of the compared `trng_top`
    circuit. `--pins` overrides that unconditionally: only the declared set
    promotes, matching this script's own reference `.SUBCKT trng_top`
    header exactly.
    """
    return _run_klt(
        [
            "extract",
            str(GDS_PATH.relative_to(REPO_ROOT)),
            "--deck",
            DECK,
            "--top",
            HDL_TOPLEVEL,
            "--abstract-cells",
            CELL_GLOB,
            "--top-cell-pins",
            "--pins",
            ",".join(top_pins),
            "--def-net-names",
            "-o",
            str(EXTRACTED_PATH.relative_to(REPO_ROOT)),
        ],
        timeout_s=1800,
    )


def _lvs_request() -> dict:
    return {
        "_comment": (
            "Generated by layout/digital/lvs.py. Paths are relative to this "
            "file. Re-run by hand with: klt lvs "
            "layout/digital/trng_top.lvs-request.json --format json"
        ),
        "layout": {"netlist": "trng_top.extracted.spice", "top": HDL_TOPLEVEL},
        "reference": {
            "netlist": "trng_top.lvs_reference.spice",
            "top": HDL_TOPLEVEL,
        },
    }


def run_lvs() -> dict:
    LVS_REQUEST_PATH.write_text(json.dumps(_lvs_request(), indent=2) + "\n")
    return _run_klt(
        ["lvs", str(LVS_REQUEST_PATH.relative_to(REPO_ROOT))], timeout_s=1800
    )


def _committed_view(payload: dict, reference_summary: dict) -> dict:
    return {
        "status": payload.get("status"),
        "mismatch_count": payload.get("mismatch_count"),
        "category_counts": payload.get("category_counts"),
        "counts": payload.get("counts"),
        "device_classes": payload.get("device_classes"),
        "reference": {
            "path": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
            "source": str(PNR_NETLIST_PATH.relative_to(REPO_ROOT)),
            "generator": "layout/digital/lvs.py",
            **reference_summary,
        },
        "environment": payload.get("environment"),
    }


def build() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    if not GDS_PATH.is_file():
        print(
            f"ERROR  {GDS_PATH.relative_to(REPO_ROOT)} is missing -- run "
            "`python3 layout/digital/build.py` first (#170)",
            file=sys.stderr,
        )
        return 3
    if not PNR_NETLIST_PATH.is_file():
        print(
            f"ERROR  {PNR_NETLIST_PATH.relative_to(REPO_ROOT)} is missing",
            file=sys.stderr,
        )
        return 3
    if not DEF_PATH.is_file():
        print(
            f"ERROR  {DEF_PATH.relative_to(REPO_ROOT)} is missing -- it is "
            "where this script recovers the physical-only tapcell/endcap/"
            "filler instances the netlist does not carry (#171)",
            file=sys.stderr,
        )
        return 3

    yosys_json_path = WORK_DIR / "trng_top_pnr.json"
    try:
        power = _pnr_power()
        physical_only = _def_physical_only_instances(
            DEF_PATH, _physical_only_masters(power)
        )
        module = _yosys_netlist(PNR_NETLIST_PATH, yosys_json_path)["modules"][
            HDL_TOPLEVEL
        ]
        reference_summary = _write_reference(
            module, REFERENCE_PATH, _power_nets(power), physical_only
        )
    except LvsFlowError as exc:
        print(f"ERROR  {exc}", file=sys.stderr)
        return 3

    try:
        extract_payload = run_extract(reference_summary["top_pins"])
    except Exception as exc:  # noqa: BLE001 - FlowError from _run_klt
        print(f"FAILED  klt extract: {exc}", file=sys.stderr)
        return 4

    try:
        lvs_payload = run_lvs()
    except Exception as exc:  # noqa: BLE001 - FlowError from _run_klt
        print(f"FAILED  klt lvs: {exc}", file=sys.stderr)
        return 4

    report = _committed_view(lvs_payload, reference_summary)
    LVS_REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print(f"klt:  {klt_version()}")
    origin = klt_origin()
    if origin and origin.get("commit"):
        print(f"      built from {origin['commit']}")
    print(
        f"extract: {extract_payload.get('device_count')} devices, "
        f"{extract_payload.get('net_count')} nets, "
        f"{len(extract_payload.get('abstracted_cells') or [])} abstracted "
        "cell types"
    )
    print(
        f"lvs:  status={report['status']}  mismatch_count="
        f"{report['mismatch_count']}  category_counts={report['category_counts']}"
    )
    print(f"wrote  {REFERENCE_PATH.relative_to(REPO_ROOT)}")
    print(f"wrote  {EXTRACTED_PATH.relative_to(REPO_ROOT)}")
    print(f"wrote  {LVS_REQUEST_PATH.relative_to(REPO_ROOT)}")
    print(f"wrote  {LVS_REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="lvs.py",
        description=(
            "Generate the trng_top digital-section LVS reference from "
            "trng_top.pnr.v, run klt extract/klt lvs against the committed "
            "GDS, and commit the result (#170)."
        ),
    )
    parser.parse_args(argv)
    return build()


if __name__ == "__main__":
    raise SystemExit(main())
