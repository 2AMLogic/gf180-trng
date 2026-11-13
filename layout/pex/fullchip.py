#!/usr/bin/env python3
"""Full-chip (inter-region) delta composition (issue #232, DR-0025).

The third of the three composition paths `layout/pex/build.py` runs, moved
out of it unchanged (issue #848) because it is a self-contained block that
only `build()` and `main()` reach into, and a reader fixing a
port-resolution or noise-tap problem should not have to scroll past it.

**The design prose for this path stays in `layout/pex/build.py`'s own
module docstring**, section "Full-chip (inter-region) delta composition" --
read that first. It is cited by location and section name from committed
evidence (`spec/decision-records/DR-0024-extracted-netlist-record-level.md`,
`sim/characterization-post-layout-extracted.md`, `layout/verify.py` and many
`sim/tb/*/tb.json` notes), so it is deliberately not duplicated or moved
here.

This module has no CLI of its own and is never run directly; the entry
point is still `layout/pex/build.py`:

    python3 layout/pex/build.py --fullchip-extract   # refresh the committed
                                                     # delta report (EXPENSIVE)
    python3 layout/pex/build.py                      # compose from it
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

# `layout/pex/build.py` owns this flow's sys.path bootstrap (issue #520) as
# well as its CLI, and this module is only ever reached through it -- so it
# is imported FIRST, deliberately: its preamble is what puts the repo root
# and `design/` on sys.path for the imports below. `build.py` in turn
# imports this module lazily, inside `build()`/`main()`, which is what keeps
# the two from forming an import cycle.
from layout.pex.build import (
    ASSEMBLED_RINGS,
    COMBINER_SAMPLER_GDS,
    COMBINER_SAMPLER_TOP,
    DECK,
    FRICTION_ISSUE,
    LEAF_CELLS,
    PDK_VARIANT,
    PEX_DIR,
    REPO_ROOT,
    _resolve_combiner_sampler_ports,
    _resolve_ring_ports,
    extract_assembled,
    extract_leaf,
)
from layout._klt import FlowError, _run_klt, klt_version
import layout.blocks.combiner_sampler.build as _cs_mod
from design.floorplan_netlist import INTER_REGION_NETS
from layout.floorplan.floorplan import _reference_top_pins
from layout.floorplan.interregion import route_net_labels

FULLCHIP_GDS = "layout/floorplan/trng_floorplan.gds"
FULLCHIP_TOP = "trng_floorplan"
FULLCHIP_LVS_REFERENCE = REPO_ROOT / "layout" / "floorplan" / "trng_floorplan.lvs_reference.spice"
#: Same glob `layout/floorplan/floorplan.py`'s own `run_extract_composed`
#: uses (`COMPOSED_ABSTRACT_CELLS`) -- kept as a literal here rather than
#: imported, the same "don't import a caller's constant, restate the deck
#: fact" discipline `layout/tests/test_pex_noise_tap.py`'s own `TAP_PREFIX`
#: follows, so a rename of one does not silently desync the other.
FULLCHIP_ABSTRACT_CELLS = "gf180mcu_fd_sc_mcu9t5v0__*"
#: DR-0025's own measured cost input: the full-chip `--parasitics` extraction
#: had not completed after ~19.5 minutes (partly CPU-contended, single
#: uninstrumented observation) on the host that record was written on.
#: 3600s leaves headroom above that without being unbounded. Every other
#: `_run_klt` call in `layout/pex/` keeps `_run_klt`'s own 600s default --
#: this is the one deliberate exception, and it is never on `build()`'s own
#: unconditional path (see `main()`'s `--fullchip-extract`).
FULLCHIP_TIMEOUT_S = 3600
FULLCHIP_REPORT = PEX_DIR / "reports" / "fullchip_parasitics.json"
#: Raw `klt extract` response of the last `--fullchip-extract` run, under the
#: gitignored scratch tree -- never committed, and never read unless
#: `--reuse-cache` asks for it. This is the iteration cache DR-0025's own
#: runtime note anticipated: composing, re-composing and debugging the delta
#: arithmetic against a fixed extraction costs seconds instead of the
#: tens-of-minutes the extraction itself does. See `extract_fullchip`.
FULLCHIP_CACHE = REPO_ROOT / "layout" / ".work" / "pex-fullchip" / "fullchip_extraction_cache.json"
#: Scratch directory `--fullchip-extract` extracts into. Deliberately NOT
#: `WORK_DIR`: `--check` globs `*.spice` out of `WORK_DIR` and requires a
#: committed counterpart for each, so a multi-megabyte
#: `trng_floorplan.fullchip.extracted.spice` left there by an earlier
#: `--fullchip-extract` run would make the next `--check` fail demanding a
#: file `layout/pex/build.py` never composes (`layout/pex/` holds composed
#: drop-ins, not raw full-chip extractions). Found the hard way while
#: building #232.
FULLCHIP_WORK_DIR = FULLCHIP_CACHE.parent

#: DR-0025's own load-bearing filter: a full-chip inter-region trunk is
#: SIMULATED only when both its endpoints are already transistor-level in
#: `layout/pex/build.py`'s intra-region extractions -- today exactly the two
#: nets `design/floorplan_netlist.INTER_REGION_NETS` tags `role:
#: "entropy_tap"` (`ro1`: ring1.ro -> combiner_sampler.rn1; `ro2`: ring2.ro
#: -> combiner_sampler.rn2). Derived from that declared data, not
#: hardcoded, so a future net gaining a transistor-level receiver (DR-0025's
#: own "Revisit if") is picked up here without an edit.
_SIMULATED_ROLES = ("entropy_tap",)
#: Roles whose driver is transistor-level (a real `sampler_dff` inside
#: `combiner_sampler`) but whose receiver is `digital`, abstracted --
#: DR-0025 prices these as a disclosed, driver-side-only OUTPUT LOAD (a
#: capacitor at the driver's own pin), never as a simulated two-ended net
#: (no receiver gate capacitance is modelled -- see `layout/pex/build.py`'s
#: own module docstring).
_DRIVER_SIDE_LOAD_ROLES = ("raw_tap", "liveness_tap")

#: Absolute tolerance the delta arithmetic must close within (float rounding
#: only -- `klt extract`'s own JSON already rounds `resistance_ohm` to 4
#: decimals and `capacitance_ff` to 6, so this is generous against that
#: alone). A full-chip merged net's own R/C can only be >= the sum of its
#: already-extracted intra-region parts (more wire only adds parasitics);
#: anything below `-`(tolerance) means a labelling/positional-identification
#: bug, not physical reality, and `_reconcile_delta` raises rather than
#: composing from it.
_CLOSE_TOLERANCE_OHM = 1e-3
_CLOSE_TOLERANCE_FF = 1e-4


def _entropy_tap_nets() -> list[dict]:
    """The full-chip inter-region nets DR-0025's filter actually simulates
    (today: `ro1`, `ro2`) -- see `_SIMULATED_ROLES`."""
    return [net for net in INTER_REGION_NETS if net["role"] in _SIMULATED_ROLES]


def _driver_side_load_nets() -> list[dict]:
    """The full-chip inter-region nets DR-0025 prices as an added,
    driver-side-only output load (today: `raw_bit`, `raw_valid`,
    `ring_bit1`, `ring_bit2`) -- see `_DRIVER_SIDE_LOAD_ROLES`."""
    return [net for net in INTER_REGION_NETS if net["role"] in _DRIVER_SIDE_LOAD_ROLES]


def _net_id_at_pin_index(payload: dict, pin_index: int) -> int:
    """The `net_id` (`net.cluster_id`) of the `nets[]` entry promoted to
    `.SUBCKT` position `pin_index` in this extraction -- the stable key that
    joins a resolved port position back to its own `parasitics.nets[]`
    entry (which is indexed by `net_id`, not `pin_index`)."""
    for net in payload["nets"]:
        if net.get("pin_index") == pin_index:
            return net["net_id"]
    raise FlowError(f"no net at pin_index {pin_index} in this extraction's own nets[]")


def _parasitics_entry_by_net_id(payload: dict, net_id: int) -> dict:
    parasitics = payload.get("parasitics")
    if not parasitics:
        raise FlowError(
            "this extraction has no `parasitics` block -- was `--parasitics` given?"
        )
    matches = [net for net in parasitics["nets"] if net["net_id"] == net_id]
    if len(matches) != 1:
        raise FlowError(
            f"expected exactly one parasitics.nets[] entry for net_id {net_id}, "
            f"found {len(matches)}"
        )
    return matches[0]


#: KLayout joins every drawn label on one net into a single net name -- `'|'`
#: between labels of a flat extraction (`layout/floorplan/interregion.
#: extracted_net_name`'s own documented convention) and `','` in the
#: LEF/DEF-merged case. A full-chip inter-region net therefore never arrives
#: under its own bare name: `ro1` comes back as `a|ro1|y` (the ring's own `ro
#: _stage` `y` pin label, `interregion.py`'s own trunk label, and `ro_buf`'s
#: own `a` pin label, all merged onto one electrical net), and `ring_bit1` as
#: `q|ring_bit1|ring_bit[0]`. Measured, not assumed -- see
#: `_parasitics_entry_by_label`.
_NET_LABEL_SEPARATORS = re.compile(r"[|,]")


def _net_labels(name: str) -> set[str]:
    """Every drawn label KLayout joined into one extracted net name."""
    return {part for part in _NET_LABEL_SEPARATORS.split(name) if part}


def _parasitics_entry_by_label(payload: dict, label: str, aliases=()) -> dict:
    """Like `_parasitics_entry_by_net_id`, but for a full-chip net identified
    by one of its own drawn labels.

    `aliases` are the other names the same net may legitimately arrive
    under. `--def-net-names` (which `_fullchip_extract_args` passes) names a
    net containing `digital`'s DEF-annotated routing by its DEF net name and
    drops the drawn text labels, so `ring_bit1` comes back as just
    `ring_bit[0]` (`interregion.route_net_labels`, measured under klt 0.8.0
    on the committed stream). A net matches if it carries `label` OR any
    alias; the exactly-one check below still applies to the union, so an
    alias can never paper over an open (a split net would match twice).

    Positional resolution is not needed here, and exact-name matching does
    not work: flat extraction of the composed stream merges every label on a
    net into one joined name (`_NET_LABEL_SEPARATORS`), so the net
    `design/floorplan_netlist.py` calls `ro1` arrives as `a|ro1|y`. What IS
    unique is the label itself -- `interregion.py` draws exactly one `ro1`
    text, on the trunk, and no other net carries that label. That uniqueness
    is CHECKED here rather than assumed: zero or more than one match raises
    `FlowError` instead of composing, the same discipline
    `_match_positional`/`_unique_pin_index` follow for the routing-level
    path.
    """
    parasitics = payload.get("parasitics")
    if not parasitics:
        raise FlowError(
            "this extraction has no `parasitics` block -- was `--parasitics` given?"
        )
    wanted = {label, *aliases}
    matches = [net for net in parasitics["nets"] if wanted & _net_labels(net["net"])]
    if len(matches) != 1:
        raise FlowError(
            f"expected exactly one parasitics.nets[] entry carrying the drawn label "
            f"{label!r} (or its DEF net name, {sorted(wanted - {label})}) in the full-chip extraction, found {len(matches)} "
            f"({[net['net'] for net in matches]}) -- see {FRICTION_ISSUE} and this "
            "module's own docstring, 'Full-chip (inter-region) delta composition'"
        )
    return matches[0]


def _label_aliases(net: dict) -> set[str]:
    """The DEF net names of `net`'s `digital` endpoints -- every other label
    the full-chip extraction may report it under (see
    `_parasitics_entry_by_label`). Empty for a net with no `digital` end."""
    return route_net_labels(net) - {net["name"]}


def _coupling_total_ff(entry: dict) -> float:
    """This net's total net-to-net (vertical-overlap) coupling capacitance,
    which is reported ALONGSIDE the delta and deliberately NOT folded into
    it.

    `klt extract --parasitics` keeps a net's own ground capacitance
    (`capacitance_ff`) separate from the net-to-net capacitors it shares with
    the nets it crosses (`coupled[]`), and only the first is a quantity the
    subtraction in `_reconcile_delta` can close over -- a coupling capacitor
    belongs to a *pair* of nets, so it has no intra-region counterpart to
    subtract. Recording it is how this module keeps
    `sim/characterization-post-layout-extracted.md` section 0.1's "floor, not
    ceiling" framing honest: the coupled term is real added load that this
    composition does not carry, so the composed netlist under-reports rather
    than over-reports.
    """
    return round(sum(c["capacitance_ff"] for c in (entry.get("coupled") or [])), 6)


def _reconcile_delta(name: str, fullchip: dict, parts: list[dict]) -> dict:
    """DR-0025's own arithmetic: `fullchip`'s merged R/C, less every already-
    extracted intra-region `parts` entry's own R/C for that same physical
    net. Raises `FlowError` (composes nothing) rather than returning a
    negative delta beyond float-rounding tolerance -- see
    `_CLOSE_TOLERANCE_OHM`/`_CLOSE_TOLERANCE_FF`.
    """
    delta_r = fullchip["resistance_ohm"] - sum(p["resistance_ohm"] for p in parts)
    delta_c = fullchip["capacitance_ff"] - sum(p["capacitance_ff"] for p in parts)
    if delta_r < -_CLOSE_TOLERANCE_OHM or delta_c < -_CLOSE_TOLERANCE_FF:
        raise FlowError(
            f"{name}: the full-chip extraction's merged net (R={fullchip['resistance_ohm']} "
            f"ohm, C={fullchip['capacitance_ff']} fF) is SMALLER than the sum of its own "
            f"already-extracted intra-region parts (R={sum(p['resistance_ohm'] for p in parts)} "
            f"ohm, C={sum(p['capacitance_ff'] for p in parts)} fF) -- the arithmetic does not "
            "close. Parasitics are only ever added by more wire, never removed, so this can "
            "only mean a labelling/positional-identification bug upstream of this function, "
            "not physical reality. Composing from this would double-count or undercount; see "
            "`layout/pex/build.py`'s own module docstring, 'Full-chip "
            "(inter-region) delta composition'."
        )
    # A tiny negative residual inside tolerance is float rounding, not signal
    # -- clamp rather than writing a (physically meaningless) negative R/C
    # card into the composed netlist.
    return {
        "resistance_ohm": round(max(delta_r, 0.0), 6),
        "capacitance_ff": round(max(delta_c, 0.0), 6),
    }


def _fullchip_extract_args(outdir: Path) -> list[str]:
    """`layout/floorplan/floorplan.py`'s own `run_extract_composed` argument
    list, plus `--parasitics` -- DR-0025 step 1, verbatim. Built in one place
    so the run, the cache key and the provenance line in the committed report
    can never describe three different invocations."""
    pins = _reference_top_pins(FULLCHIP_LVS_REFERENCE, FULLCHIP_TOP)
    out_path = outdir / "trng_floorplan.fullchip.extracted.spice"
    return [
        "extract",
        FULLCHIP_GDS,
        "--deck",
        DECK,
        "--top",
        FULLCHIP_TOP,
        "--parasitics",
        "--pdk",
        PDK_VARIANT,
        "--abstract-cells",
        FULLCHIP_ABSTRACT_CELLS,
        "--pins",
        ",".join(pins),
        "--def-net-names",
        "-o",
        str(out_path.relative_to(REPO_ROOT)),
    ]


def _fullchip_cache_key(args: list[str]) -> list[str]:
    """`args` with the `-o <path>` pair dropped.

    Everything else in the invocation changes what the extractor computes;
    where the netlist is written does not. Keying the cache on the full list
    would miss on a pure scratch-directory move, which is a false negative
    that costs tens of minutes."""
    out: list[str] = []
    skip = False
    for arg in args:
        if skip:
            skip = False
            continue
        if arg in ("-o", "--output"):
            skip = True
            continue
        out.append(arg)
    return out


def extract_fullchip(
    outdir: Path, timeout_s: int = FULLCHIP_TIMEOUT_S, *, reuse_cache: bool = False
) -> tuple[dict, dict]:
    """`klt extract --parasitics` over the composed, routed floorplan
    (DR-0025) -- the SAME run shape `layout/floorplan/floorplan.py`'s own
    `run_extract_composed` is held to (the extraction the composed LVS is
    already checked against), plus `--parasitics`. Returns
    `(payload, meta)`.

    Expensive (see `FULLCHIP_TIMEOUT_S`'s own docstring) and NOT part of
    `build()`'s unconditional path -- only ever invoked by `main()`'s
    `--fullchip-extract`.

    Every run writes its raw response to `FULLCHIP_CACHE` (under the
    gitignored `layout/.work/`), and `reuse_cache=True` reads that back
    instead of re-running -- the "equivalent cache" DR-0025's own runtime
    note says whoever built this would need, so the composition step can be
    iterated without re-paying a tens-of-minutes extraction. The cache is
    keyed on the full argument list, so a changed flag, pin set or input path
    misses it rather than silently composing from the wrong run. A cached
    run's own measured `runtime_s` travels with it, and the report it
    produces says `from_cache: true` -- a cache hit never re-dates or
    re-attributes someone else's measurement as a fresh one.
    """
    args = _fullchip_extract_args(outdir)
    if reuse_cache and FULLCHIP_CACHE.is_file():
        cached = json.loads(FULLCHIP_CACHE.read_text())
        if _fullchip_cache_key(cached.get("args") or []) != _fullchip_cache_key(args):
            raise FlowError(
                f"{FULLCHIP_CACHE.relative_to(REPO_ROOT)} was written by a DIFFERENT "
                "extraction invocation than the one this module now builds -- refusing "
                "to compose from it. Re-run without --reuse-cache to refresh it."
            )
        meta = dict(cached["meta"])
        meta["from_cache"] = True
        return cached["payload"], meta

    start = time.monotonic()
    payload = _run_klt(args, timeout_s=timeout_s)
    runtime_s = time.monotonic() - start
    meta = {
        "command": "klt " + " ".join(args),
        "runtime_s": round(runtime_s, 1),
        "klt_version": klt_version(),
        "pdk_variant": PDK_VARIANT,
        "host_load_average_1min": _load_average_1min(),
        "cpu_count": os.cpu_count(),
        "from_cache": False,
    }
    FULLCHIP_CACHE.parent.mkdir(parents=True, exist_ok=True)
    FULLCHIP_CACHE.write_text(json.dumps({"args": args, "meta": meta, "payload": payload}))
    return payload, meta


def _load_average_1min() -> float | None:
    """The host's 1-minute load average at the moment an extraction finished,
    recorded next to its wall-clock runtime.

    DR-0025's own runtime probe had to be discounted precisely because it was
    partly CPU-contended and nobody wrote down by how much. A wall-clock
    figure with no load figure beside it is not reproducible evidence about
    the tool -- it is evidence about the host that day."""
    try:
        return round(os.getloadavg()[0], 2)
    except (OSError, AttributeError):  # pragma: no cover - platform-dependent
        return None


def compute_fullchip_report(
    fullchip_payload: dict,
    ring_payloads: dict[str, dict],
    ring_ports: dict[str, dict[int, str]],
    cs_payload: dict,
    cs_ports: dict[int, str],
) -> dict:
    """DR-0025's own delta arithmetic for every inter-region net this flow
    prices, keyed by net name. See `layout/pex/build.py`'s own module
    docstring, "Full-chip (inter-region) delta composition"."""
    region_payload = {"ring1": ring_payloads["ro_ring11"], "ring2": ring_payloads["ro_ring11_ring2"]}
    region_ports = {"ring1": ring_ports["ro_ring11"], "ring2": ring_ports["ro_ring11_ring2"]}

    def _pin_index(port_map: dict[int, str], pin: str) -> int:
        for idx, name in port_map.items():
            if name == pin:
                return idx
        raise FlowError(f"no resolved port named {pin!r} in {port_map!r}")

    def _entry_for(payload: dict, port_map: dict[int, str], pin: str) -> dict:
        net_id = _net_id_at_pin_index(payload, _pin_index(port_map, pin))
        return _parasitics_entry_by_net_id(payload, net_id)

    entropy: dict[str, dict] = {}
    for net in _entropy_tap_nets():
        name = net["name"]
        ring_region = next(r for r, _p in net["endpoints"] if r in region_payload)
        ring_pin = next(p for r, p in net["endpoints"] if r == ring_region)
        cs_pin = next(p for r, p in net["endpoints"] if r == "combiner_sampler")

        ring_entry = _entry_for(region_payload[ring_region], region_ports[ring_region], ring_pin)
        cs_entry = _entry_for(cs_payload, cs_ports, cs_pin)
        fc_entry = _parasitics_entry_by_label(
            fullchip_payload, name, _label_aliases(net)
        )

        delta = _reconcile_delta(name, fc_entry, [ring_entry, cs_entry])
        entropy[name] = {
            "ring_region": ring_region,
            "ring_pin": ring_pin,
            "cs_pin": cs_pin,
            "fullchip_net_name": fc_entry["net"],
            "fullchip_coupling_capacitance_ff": _coupling_total_ff(fc_entry),
            "fullchip": {
                "resistance_ohm": fc_entry["resistance_ohm"],
                "capacitance_ff": fc_entry["capacitance_ff"],
            },
            "ring_intra_region": {
                "resistance_ohm": ring_entry["resistance_ohm"],
                "capacitance_ff": ring_entry["capacitance_ff"],
            },
            "combiner_sampler_intra_region": {
                "resistance_ohm": cs_entry["resistance_ohm"],
                "capacitance_ff": cs_entry["capacitance_ff"],
            },
            "delta": delta,
        }

    loads: dict[str, dict] = {}
    for net in _driver_side_load_nets():
        name = net["name"]
        cs_pin = next(p for r, p in net["endpoints"] if r == "combiner_sampler")
        cs_entry = _entry_for(cs_payload, cs_ports, cs_pin)
        fc_entry = _parasitics_entry_by_label(
            fullchip_payload, name, _label_aliases(net)
        )
        delta = _reconcile_delta(name, fc_entry, [cs_entry])
        loads[name] = {
            "cs_pin": cs_pin,
            "fullchip_net_name": fc_entry["net"],
            "fullchip_coupling_capacitance_ff": _coupling_total_ff(fc_entry),
            "fullchip": {
                "resistance_ohm": fc_entry["resistance_ohm"],
                "capacitance_ff": fc_entry["capacitance_ff"],
            },
            "combiner_sampler_intra_region": {
                "resistance_ohm": cs_entry["resistance_ohm"],
                "capacitance_ff": cs_entry["capacitance_ff"],
            },
            # Driver-side-only (DR-0025): no receiver device exists to size
            # a series R against (an R ending in an open node passes no
            # current and changes nothing electrically), so only the added
            # capacitance is carried forward into the composed netlist.
            "delta": delta,
        }

    return {"entropy_tap": entropy, "driver_side_load": loads}


def write_fullchip_report(report: dict, extraction_meta: dict, path: Path = FULLCHIP_REPORT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_comment": (
            "GENERATED by layout/pex/build.py --fullchip-extract -- do not edit by "
            "hand. DR-0025's own inter-region delta arithmetic -- see "
            "layout/pex/build.py's module docstring, 'Full-chip (inter-region) "
            "delta composition'."
        ),
        "extraction": extraction_meta,
        **report,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def run_fullchip_extraction_and_report(outdir: Path, *, reuse_cache: bool = False) -> dict:
    """The expensive step (DR-0025's own measured tens-of-minutes cost) --
    ONLY invoked by `main()`'s `--fullchip-extract`, never by `build()`'s own
    unconditional path. Re-runs the cheap intra-region assembled extractions
    too (ring1/ring2/combiner_sampler), since the delta needs both sides
    fresh to reconcile against, then writes the committed derived report
    `layout/pex/reports/fullchip_parasitics.json` that `build()`'s own
    default path reads back cheaply (no new `klt` call) on every
    run/`--check`, reconciling it against a FRESH intra-region extraction
    each time -- see `layout/pex/build.py`'s own module docstring.

    `reuse_cache=True` composes from the last run's cached raw response
    (`FULLCHIP_CACHE`) instead of re-extracting -- for iterating on the
    composition, not for producing the committed report.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    leaf_payloads: dict[str, dict] = {}
    for name, gds, top in LEAF_CELLS:
        leaf_payloads[name] = extract_leaf(name, gds, top, outdir)

    ring_payloads: dict[str, dict] = {}
    ring_ports: dict[str, dict[int, str]] = {}
    for name, gds, top, mod, nand_leaf, stage_leaf in ASSEMBLED_RINGS:
        payload = extract_assembled(name, gds, top, outdir)
        ring_payloads[name] = payload
        ring_ports[name] = _resolve_ring_ports(payload, leaf_payloads[nand_leaf], leaf_payloads[stage_leaf], mod)

    cs_payload = extract_assembled("combiner_sampler", COMBINER_SAMPLER_GDS, COMBINER_SAMPLER_TOP, outdir)
    cs_ports = _resolve_combiner_sampler_ports(
        cs_payload, leaf_payloads["ro_buf"], leaf_payloads["sampler_dff"], _cs_mod
    )

    fullchip_payload, meta = extract_fullchip(outdir, reuse_cache=reuse_cache)
    report = compute_fullchip_report(fullchip_payload, ring_payloads, ring_ports, cs_payload, cs_ports)
    write_fullchip_report(report, meta)
    return report


def _reconcile_cached_report(
    cached: dict,
    ring_payloads: dict[str, dict],
    ring_ports: dict[str, dict[int, str]],
    cs_payload: dict,
    cs_ports: dict[int, str],
) -> None:
    """Hold the COMMITTED `fullchip_parasitics.json` report to a FRESH
    intra-region extraction, every `build()`/`--check` run -- the cheap half
    of the reconciliation `layout/pex/build.py`'s own module docstring
    describes (the expensive half, re-running the full-chip extraction
    itself, is
    `run_fullchip_extraction_and_report`'s job, invoked separately). Raises
    `FlowError` if the cached report's own recorded intra-region R/C no
    longer matches a fresh extraction -- meaning the committed report is
    stale relative to the current drawn geometry and `--fullchip-extract`
    needs re-running, not that this module should silently keep composing
    from a number that no longer describes what is on disk.
    """
    region_payload = {"ring1": ring_payloads["ro_ring11"], "ring2": ring_payloads["ro_ring11_ring2"]}
    region_ports = {"ring1": ring_ports["ro_ring11"], "ring2": ring_ports["ro_ring11_ring2"]}

    def _pin_index(port_map: dict[int, str], pin: str) -> int:
        for idx, name in port_map.items():
            if name == pin:
                return idx
        raise FlowError(f"no resolved port named {pin!r} in {port_map!r}")

    def _fresh_entry(payload: dict, port_map: dict[int, str], pin: str) -> dict:
        net_id = _net_id_at_pin_index(payload, _pin_index(port_map, pin))
        return _parasitics_entry_by_net_id(payload, net_id)

    def _check(name: str, cached_entry: dict, fresh: dict) -> None:
        if (
            abs(fresh["resistance_ohm"] - cached_entry["resistance_ohm"]) > _CLOSE_TOLERANCE_OHM
            or abs(fresh["capacitance_ff"] - cached_entry["capacitance_ff"]) > _CLOSE_TOLERANCE_FF
        ):
            raise FlowError(
                f"{name}: {FULLCHIP_REPORT.relative_to(REPO_ROOT)}'s cached intra-region "
                f"R/C (R={cached_entry['resistance_ohm']} ohm, C={cached_entry['capacitance_ff']} "
                f"fF) no longer matches a fresh extraction (R={fresh['resistance_ohm']} ohm, "
                f"C={fresh['capacitance_ff']} fF) -- the committed report is stale relative to "
                "the current drawn geometry. Re-run `python3 layout/pex/build.py "
                "--fullchip-extract` to refresh it."
            )

    for name, entry in cached["entropy_tap"].items():
        ring_region = entry["ring_region"]
        fresh_ring = _fresh_entry(region_payload[ring_region], region_ports[ring_region], entry["ring_pin"])
        _check(f"{name} (ring)", entry["ring_intra_region"], fresh_ring)
        fresh_cs = _fresh_entry(cs_payload, cs_ports, entry["cs_pin"])
        _check(f"{name} (combiner_sampler)", entry["combiner_sampler_intra_region"], fresh_cs)

    for name, entry in cached["driver_side_load"].items():
        fresh_cs = _fresh_entry(cs_payload, cs_ports, entry["cs_pin"])
        _check(f"{name} (combiner_sampler)", entry["combiner_sampler_intra_region"], fresh_cs)


FULLCHIP_HEADER = """* GENERATED by layout/pex/build.py -- do not edit by hand.
* Post-layout, FULL-CHIP-DELTA-annotated drop-in replacement for {source},
* extending sampler_core.routed.extracted.spice with the two-net inter-
* region delta DR-0025 authorises: klt extract --parasitics --pdk {pdk}
* over the composed, routed layout/floorplan/trng_floorplan.gds, less what
* ro_ring11(_ring2).routed.extracted.spice and
* combiner_sampler.routed.extracted.spice already carry for that same
* physical net (see layout/pex/reports/fullchip_parasitics.json and this
* file's own module docstring, "Full-chip (inter-region) delta
* composition", for what this captures and what it does not -- DR-0025's
* own stated coverage hole).
* Regenerate with: python3 layout/pex/build.py --fullchip-extract && python3 layout/pex/build.py
"""


def _pi_delta_lines(prefix: str, from_node: str, to_node: str, delta: dict) -> list[str]:
    """A symmetric pi-model two-terminal lumped RC segment (`C/2` at each
    end, `R` in series between them) for one net's own delta -- the
    standard lumped approximation of a distributed line when only the net's
    own total R and total C (not a per-position breakdown) are available.
    See `layout/pex/build.py`'s own module docstring, "Full-chip
    (inter-region) delta composition".
    """
    c_half_f = delta["capacitance_ff"] * 1e-15 / 2
    return [
        f"c{prefix}a {from_node} vsubs {c_half_f:.6e}",
        f"r{prefix} {from_node} {to_node} {delta['resistance_ohm']:.6f}",
        f"c{prefix}b {to_node} vsubs {c_half_f:.6e}",
    ]


def _sampler_core_fullchip_subckt(report: dict) -> str:
    """`sampler_core.routed.extracted.spice`'s own topology
    (`_sampler_core_routed_subckt`), with DR-0025's `ro1`/`ro2` delta
    inserted between each ring wrapper's `ro` port and
    `combiner_sampler_routed_extracted`'s `rn1`/`rn2` port, plus the
    disclosed driver-side-only output load on `raw_bit`/`raw_valid`/
    `ring_bit1`/`ring_bit2` (a grounded capacitor at each pin -- no series R,
    since no receiver device exists on the other end of that trunk to
    justify one -- see `layout/pex/build.py`'s own module docstring)."""
    entropy = report["entropy_tap"]
    loads = report["driver_side_load"]
    ro1 = next(n for n in _entropy_tap_nets() if n["name"] == "ro1")
    ro2 = next(n for n in _entropy_tap_nets() if n["name"] == "ro2")

    lines = [
        ".subckt sampler_core_fullchip_extracted en1 en2 vddr1 vddr2 vdd vss "
        "clk rst_n raw_bit raw_valid ring_bit1 ring_bit2"
    ]
    lines.append("xr1 en1 dro1 vddr1 vss ro_ring11_routed_extracted")
    lines.append("xr2 en2 dro2 vddr2 vss ro_ring11_ring2_routed_extracted")
    lines += _pi_delta_lines("delta1", "dro1", "rn1", entropy[ro1["name"]]["delta"])
    lines += _pi_delta_lines("delta2", "dro2", "rn2", entropy[ro2["name"]]["delta"])
    lines.append(
        "xcs rn1 rn2 vdd vss clk rst_n raw_bit raw_valid ring_bit1 ring_bit2 "
        "combiner_sampler_routed_extracted"
    )
    for name, port in (
        ("raw_bit", "raw_bit"),
        ("raw_valid", "raw_valid"),
        ("ring_bit1", "ring_bit1"),
        ("ring_bit2", "ring_bit2"),
    ):
        c_f = loads[name]["delta"]["capacitance_ff"] * 1e-15
        lines.append(f"cload_{name} {port} vsubs {c_f:.6e}")
    lines.append(".ends")
    return "\n".join(lines) + "\n"
