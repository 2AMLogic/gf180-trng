#!/usr/bin/env python3
"""Issue #234: the DC offset each region's local `vss` sees, from the
shared 430.23 um `vss` return trunk (`layout/floorplan/interregion.py`'s
one deliberately shared inter-region net -- every other supply branch is a
star, per `layout/floorplan/README.md`'s "supply/ground star point"
section).

    python3 sim/tools/vss_trunk_ir_drop.py            # the two-corner report
    python3 sim/tools/vss_trunk_ir_drop.py --check    # hold the finding to a
                                                       # materiality bound

Like `sim/tools/power_rollup.py` and `sim/tools/digital_corner_characterization.py`
beside it, this is a *derivation*, not a simulation run: it reads the
committed inter-region routing geometry (`layout/floorplan/reports/
compose.json`, `area.json`) through the *real*
`layout.floorplan.interregion.wiring_plan()` function -- the same one
`floorplan.py`'s own `compose()` calls -- and combines the resistances it
implies with current figures already measured/estimated elsewhere in this
repository's `sim/` evidence. It needs no `klt`, no PDK and no ngspice, and
it writes nothing.

Why a resistor NETWORK, not the lumped ~129 ohm DR-0025 already quotes
------------------------------------------------------------------------
DR-0025's ~129 ohm is `sheet_res * trunk_length / WIRE_W` over the whole
430.23 um trunk -- correct as a total, but silent on *where* each region
taps in, which is exactly what an IR-drop verdict needs: `ring1`, `ring2`
and `combiner_sampler` sit at three different points along the trunk, and
`combiner_sampler`'s tap is a few um from the chip pin while `ring1`'s is
the far end. This module walks the trunk's own drawn geometry and builds a
segmented model: one resistor per gap between consecutive taps (including
the chip pin), plus one riser resistor per region, and computes each
region's local `vss` node as a simple series chain hung off the pin.

Where the resistance numbers come from
---------------------------------------
Metal3 (riser) and Metal4 (trunk) share the same curated sheet resistance
in the `klt` gf180mcu deck this repository's own DR-0025 already cites:
`sheet_res = 0.09 ohm/sq` (`spec/decision-records/
DR-0025-full-chip-pex-scope.md`, "the `klt` gf180mcu deck's own curated
parasitics table" -- `klayout_tools.decks.gf180mcu.PARASITICS`, issue
klayout-tools#547, metals index 2 (Metal3) and index 3 (Metal4), both
0.09 ohm/sq). `METAL_SHEET_RES_OHM_SQ` below is that same constant,
restated here rather than imported, because `klayout_tools` is a separate
package this repository does not depend on at run time (it is a build-time
tool, not a library) -- the same reason DR-0025's own arithmetic restates it
inline instead of importing it.

Where the current numbers come from
-------------------------------------
See `CURRENT_PROFILE_UW`'s own docstring below for the exact records each
figure is transcribed from, and the allocation this module makes across
`ring1`/`ring2`/`combiner_sampler` where no existing record already
separates them -- that allocation is engineering judgement, stated as such,
not a fourth measurement.

What this deliberately does not do
-------------------------------------
- Model `vddr1`/`vddr2`/`vdd`/`vddd`, the four supply branches issue #234
  explicitly places out of scope (each its own star, off-die, not a shared
  return).
- Model `digital`'s own `vddd`/`vss` PDN tie (issue #224) -- `digital` is
  not an endpoint of this trunk at all (`interregion.py`'s own docstring,
  "What is drawn, and what deliberately is not").
- Re-run any ngspice testbench. The current figures below are read off
  existing `sim/` evidence, not re-measured with the offset applied; see
  "the digital term from DR-0023" is not needed section below for the
  scope reasoning.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "design"))

from layout.floorplan import interregion  # noqa: E402

COMPOSE_REPORT = REPO_ROOT / "layout" / "floorplan" / "reports" / "compose.json"
AREA_REPORT = REPO_ROOT / "layout" / "floorplan" / "reports" / "area.json"
INTERREGION_REPORT = REPO_ROOT / "layout" / "floorplan" / "reports" / "interregion.json"

#: Metal3 (riser) and Metal4 (trunk) sheet resistance -- see module
#: docstring's "Where the resistance numbers come from".
METAL_SHEET_RES_OHM_SQ = 0.09

#: The one shared-return net this module analyses. Every other inter-region
#: net is either a star supply branch (out of scope, issue #234's own
#: "Out of scope" section) or carries no meaningful DC current profile.
NET = "vss"

#: Active-power binding corner (`sim/characterization-startup-and-power-budget.md`):
#: `ff` / -40 C / 3.63 V. This is the HIGHEST-current corner this repository's
#: own PVT sweep has ever measured for the analog block (fastest process,
#: coldest -- a ring oscillator's active current scales with switching
#: frequency, and this is deliberately the corner where that frequency is
#: highest). Resistance is corner-independent in this model (fixed drawn
#: metal geometry; the curated sheet-resistance table carries no per-corner
#: variation), so the offsets this corner produces upper-bound the offset at
#: every other corner in the covered PVT grid, including the entropy-binding
#: corner (`ss`/+125 C/3.63 V, DR-0015) that DR-0007's jitter-energy margin is
#: evaluated at -- see the "affected rows" note in
#: `sim/characterization-vss-trunk-ir-drop.md`.
ACTIVE_CORNER = {"process": "ff", "temperature_c": -40, "voltage_v": 3.63}

#: Idle-power binding corner (same doc): `ff` / +125 C / 3.63 V -- the
#: highest-leakage corner measured.
IDLE_CORNER = {"process": "ff", "temperature_c": 125, "voltage_v": 3.63}

#: Current profile, by corner and physical region -- see this constant's own
#: derivation, below, for the exact `sim/` sources and the allocation rule.
#:
#: Active corner (`ff`/-40 C/3.63 V):
#:   - `sim/characterization-post-layout-extracted.md` S7.4, "Active":
#:     "Entropy array (measured)" 489.9 uW -- the ro-array-core-power-
#:     extracted-routed record (`sim/records/
#:     2026-09-11-ro-array-core-power-extracted-routed-01.md`). Physically
#:     this is `xr1` (`ring1`'s own 11-device oscillator) + `xr2` (`ring2`'s)
#:     + `xb1`/`xb2` (the two `ro_buf` instances) + `xa1` (the XOR combiner)
#:     -- `design/ro_array_core.spice`'s own `.subckt`. The last three
#:     physically sit inside `combiner_sampler`
#:     (`layout/blocks/combiner_sampler/build.py`'s own docstring,
#:     "Connectivity"), not inside either ring, but no committed record
#:     separates their share from the two rings' own 22 oscillator stages.
#:     This module allocates the whole 489.9 uW to `ring1`/`ring2`, split
#:     50/50 by symmetry (both rings are the same `ro_ring11` schematic
#:     topology; DR-0025's own MC-mismatch section shows a real but small
#:     per-ring spread, not a power asymmetry) -- which *overstates* each
#:     ring's own current a little and *understates* `combiner_sampler`'s,
#:     the conservative direction for the two nodes farther from the chip
#:     pin.
#:   - Same section: "Sampler (measured, unchanged -- see S3.2)" 16.88 uW --
#:     `sim/tools/power_rollup.py`'s own formula-based `xsb`+`xsv` current
#:     (the raw-bit and raw-valid samplers only).
#:   - `sim/characterization-startup-and-power-budget.md`, "Two taps that
#:     are not in the total": the per-ring liveness digitizer (`xsr1`/
#:     `xsr2`, DR-0016), `sim/tb/ring-liveness-tap-power/`, ~81 uW. That
#:     section's own framing ("neither is instantiated by the shipped
#:     sampler_core/trng_top") predates DR-0016's adoption --
#:     `design/sampler_core.spice` now declares `xsr1`/`xsr2` unconditionally
#:     and `layout/blocks/combiner_sampler/build.py` places and wires both,
#:     so the drawn floorplan this issue analyses does carry this current,
#:     and it is included here.
#:   All three terms above physically live in `combiner_sampler`
#:   (16.88 + 81 = 97.88 uW).
#:
#: Idle corner (`ff`/+125 C/3.63 V):
#:   - `sim/characterization-post-layout-extracted.md` S7.4, "Idle": "Analog
#:     (sampler_core, measured)" 136.8 nA -- `sim/tb/
#:     sampler-core-idle-leakage-extracted-routed/`'s own DUT is the WHOLE
#:     `sampler_core` (both rings + all four sampler_dff instances), so this
#:     figure needs no liveness-tap addition, unlike the active-corner one.
#:     No idle-level per-block breakdown exists, so this module apportions
#:     the 136.8 nA total across ring1/ring2/combiner_sampler using the
#:     ACTIVE corner's own power ratio between "the two rings' terms" and
#:     "combiner_sampler's terms" -- an approximation, stated as one, not a
#:     second idle measurement.
CURRENT_PROFILE_UW = {
    "active": {"ring_pair_uw": 489.9, "sampler_flops_uw": 16.88, "liveness_taps_uw": 81.0},
}

#: `sim/characterization-startup-and-power-budget.md`'s own idle-current
#: total for the whole analog block (both rings + combiner_sampler),
#: routed-extracted (`sim/characterization-post-layout-extracted.md` S7.4).
IDLE_TOTAL_NA = 136.8


def resistance_model() -> dict:
    """The segmented resistor network for `NET`, derived from committed
    geometry -- never a hand-transcribed length.

    Calls the real `interregion.wiring_plan()` (the function
    `floorplan.py`'s own `compose()` calls to draw this net) with the
    origins and content bboxes `layout/floorplan/reports/compose.json` and
    `area.json` already committed, exactly as `layout/tests/
    test_interregion.py` does for its own from-committed-artefacts check.
    If issue #222's routing changes, these reports change with it and this
    function's output changes too -- nothing here is a snapshot of today's
    numbers.
    """
    compose = json.loads(COMPOSE_REPORT.read_text())
    origins_um = compose["request"]["placement"]["origins_um"]
    area = json.loads(AREA_REPORT.read_text())

    content_origins: dict[str, dict] = {}
    content_bboxes: dict[str, dict] = {}
    for region in area["regions"]:
        rid = region["id"]
        content_id = f"{rid}_ring"
        if content_id not in origins_um:
            continue
        content_origins[rid] = origins_um[content_id]
        content_bboxes[rid] = region["ring_content_bbox_um"]

    plan = interregion.wiring_plan(content_origins, content_bboxes)

    route = next(r for r in plan["routes"] if r["net"] == NET)
    if not route["chip_pin"]:
        raise RuntimeError(f"{NET!r} has no chip pin -- nothing to reference offsets against")

    net_shapes = [s for s in plan["shapes"] if s.get("_net") == NET]
    riser_len_um: dict[str, float] = {}
    for endpoint in route["endpoints"]:
        rid = endpoint["region"]
        riser_x = endpoint["riser_x_um"]
        # The riser is the METAL3 vertical rect landing at this endpoint's
        # own x (within rounding) -- `_endpoint_geometry()`'s own `_vrect`.
        candidates = [
            s for s in net_shapes
            if s["layer"] == interregion.METAL3
            and abs((s["rect_um"][0] + s["rect_um"][2]) / 2 - riser_x) < 0.01
        ]
        if len(candidates) != 1:
            raise RuntimeError(
                f"{NET!r} endpoint {rid!r}: expected exactly one Metal3 riser "
                f"rect at x={riser_x}, found {len(candidates)}"
            )
        y0, y1 = candidates[0]["rect_um"][1], candidates[0]["rect_um"][3]
        riser_len_um[rid] = round(y1 - y0, 4)

    # Taps in trunk order, nearest-the-pin first -- the chip pin always
    # anchors one end (`chip_pin_x_um`), so sort every endpoint plus the pin
    # by x and read the chain off that order.
    tap_x = {e["region"]: e["riser_x_um"] for e in route["endpoints"]}
    pin_x = route["chip_pin_x_um"]
    order = sorted(tap_x, key=lambda rid: abs(tap_x[rid] - pin_x))

    def seg_r(x_a: float, x_b: float) -> float:
        return METAL_SHEET_RES_OHM_SQ * abs(x_b - x_a) / interregion.WIRE_W

    def riser_r(rid: str) -> float:
        return METAL_SHEET_RES_OHM_SQ * riser_len_um[rid] / interregion.WIRE_W

    chain = []
    prev_x = pin_x
    for rid in order:
        chain.append({
            "region": rid,
            "seg_r_ohm": round(seg_r(prev_x, tap_x[rid]), 6),
            "riser_r_ohm": round(riser_r(rid), 6),
            "riser_len_um": riser_len_um[rid],
        })
        prev_x = tap_x[rid]

    return {"net": NET, "chip_pin_x_um": pin_x, "chain": chain}


def node_offsets(chain: list[dict], currents_a: dict[str, float]) -> dict[str, float]:
    """Local `vss` DC offset (volts, relative to the chip pin) for every
    region in `chain`, given each region's own current draw (amps).

    `chain` is nearest-the-pin-first, each entry `{"region", "seg_r_ohm"
    (from the previous node, or the pin, to this one), "riser_r_ohm"}` --
    exactly `resistance_model()`'s own `"chain"`. Pure series-resistor-tree
    arithmetic, no PDK/geometry dependency, which is what makes it testable
    on a synthetic chain independent of this repository's real floorplan
    (`sim/tests/test_vss_trunk_ir_drop.py`).
    """
    n = len(chain)
    # Current through the segment feeding node i is every node at or beyond
    # i in the (nearest-first) chain -- the chain is a simple series path
    # from the pin outward, so a farther node's current must cross every
    # nearer node's own segment to reach the pin.
    trailing_current = [0.0] * n
    running = 0.0
    for i in range(n - 1, -1, -1):
        running += currents_a[chain[i]["region"]]
        trailing_current[i] = running

    offsets: dict[str, float] = {}
    trunk_v = 0.0
    for i, node in enumerate(chain):
        trunk_v += node["seg_r_ohm"] * trailing_current[i]
        local_v = trunk_v + node["riser_r_ohm"] * currents_a[node["region"]]
        offsets[node["region"]] = local_v
    return offsets


def _active_currents_a(voltage_v: float) -> dict[str, float]:
    p = CURRENT_PROFILE_UW["active"]
    ring_each_w = (p["ring_pair_uw"] * 1e-6) / 2
    cs_w = (p["sampler_flops_uw"] + p["liveness_taps_uw"]) * 1e-6
    return {
        "ring1": ring_each_w / voltage_v,
        "ring2": ring_each_w / voltage_v,
        "combiner_sampler": cs_w / voltage_v,
    }


def _idle_currents_a() -> dict[str, float]:
    p = CURRENT_PROFILE_UW["active"]
    ring_pair_w = p["ring_pair_uw"] * 1e-6
    cs_w = (p["sampler_flops_uw"] + p["liveness_taps_uw"]) * 1e-6
    ring_frac = ring_pair_w / (ring_pair_w + cs_w)
    cs_frac = cs_w / (ring_pair_w + cs_w)
    total_a = IDLE_TOTAL_NA * 1e-9
    return {
        "ring1": total_a * ring_frac / 2,
        "ring2": total_a * ring_frac / 2,
        "combiner_sampler": total_a * cs_frac,
    }


def worst_case_bound_a(currents_a: dict[str, float], farthest_region: str) -> dict[str, float]:
    """A deliberately unphysical bound: every region's own current forced
    through `farthest_region` alone, everything else zeroed. Shows the
    conclusion does not depend on this module's ring1/ring2/combiner_sampler
    allocation rule -- see module docstring."""
    total = sum(currents_a.values())
    return {region: (total if region == farthest_region else 0.0) for region in currents_a}


#: Materiality yardstick: this design's own ratified PVT sweep already spans
#: a +-10 % (330 mV on a 3.3 V nominal rail) supply corner
#: (`sim/README.md`, "voltage: 3.63 V (nominal 3.3 V, +10%)"). An offset that
#: is a small fraction of a range the design is already characterised across
#: is swamped by corners this repository already runs -- not proof of zero
#: effect, but the same style of bound `sim/tools/worst_corner_entropy.py`
#: and friends use elsewhere in this repository.
SUPPLY_CORNER_SPREAD_V = 0.33
MATERIALITY_FRACTION = 0.10  # 10% of the corner spread this module checks against


def _report(model: dict) -> None:
    print(f"Resistance model for {model['net']!r} (chip pin at "
          f"x={model['chip_pin_x_um']} um):")
    for node in model["chain"]:
        print(f"  {node['region']:<18} seg_r={node['seg_r_ohm']:8.3f} ohm  "
              f"riser_r={node['riser_r_ohm']:6.3f} ohm "
              f"(riser {node['riser_len_um']:.2f} um)")
    print()

    for label, currents in (
        ("active (ff/-40C/3.63V)", _active_currents_a(ACTIVE_CORNER["voltage_v"])),
        ("idle (ff/+125C/3.63V)", _idle_currents_a()),
    ):
        offsets = node_offsets(model["chain"], currents)
        print(f"Corner: {label}")
        for region, i_a in currents.items():
            print(f"  {region:<18} I={i_a * 1e6:10.4f} uA  "
                  f"local_vss_offset={offsets[region] * 1e3:9.5f} mV")
        print()

    active_currents = _active_currents_a(ACTIVE_CORNER["voltage_v"])
    farthest = model["chain"][-1]["region"]
    wc_currents = worst_case_bound_a(active_currents, farthest)
    wc_offsets = node_offsets(model["chain"], wc_currents)
    print(f"Conservative bound: 100% of active-corner current forced through "
          f"{farthest!r} alone:")
    for region in wc_currents:
        print(f"  {region:<18} local_vss_offset={wc_offsets[region] * 1e3:9.5f} mV")
    print()
    bound_ohm = SUPPLY_CORNER_SPREAD_V * MATERIALITY_FRACTION * 1000
    print(f"Materiality bound: {bound_ohm:.1f} mV "
          f"({MATERIALITY_FRACTION * 100:.0f}% of the ratified "
          f"+-10% / {SUPPLY_CORNER_SPREAD_V * 1000:.0f} mV supply-corner spread)")


def _check(model: dict) -> int:
    active_currents = _active_currents_a(ACTIVE_CORNER["voltage_v"])
    farthest = model["chain"][-1]["region"]
    wc_currents = worst_case_bound_a(active_currents, farthest)
    wc_offsets = node_offsets(model["chain"], wc_currents)
    bound_v = SUPPLY_CORNER_SPREAD_V * MATERIALITY_FRACTION
    worst = max(wc_offsets.values())
    if worst >= bound_v:
        print(
            f"FAIL: conservative-bound offset {worst * 1e3:.3f} mV is at or "
            f"above the {bound_v * 1e3:.1f} mV materiality bound -- re-run "
            "sim/characterization-vss-trunk-ir-drop.md's analysis before "
            "trusting the 'not material' verdict",
            file=sys.stderr,
        )
        return 1

    # Sanity check against the committed report, so a future #222 routing
    # change that silently drops an endpoint or changes the trunk's own net
    # composition fails loudly here rather than only changing numbers no
    # one is watching.
    committed = json.loads(INTERREGION_REPORT.read_text())
    committed_route = next(r for r in committed["routes"] if r["net"] == NET)
    committed_regions = {e["region"] for e in committed_route["endpoints"]}
    model_regions = {node["region"] for node in model["chain"]}
    if committed_regions != model_regions:
        print(
            f"FAIL: committed interregion.json's {NET!r} endpoints "
            f"{sorted(committed_regions)} no longer match this module's "
            f"resistance-model chain {sorted(model_regions)}",
            file=sys.stderr,
        )
        return 1

    print(f"OK: worst-case bound {worst * 1e3:.3f} mV < "
          f"{bound_v * 1e3:.1f} mV materiality bound; endpoints match "
          "reports/interregion.json")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                         help="assert the conservative bound stays below the "
                              "materiality threshold and matches the "
                              "committed interregion.json")
    args = parser.parse_args()

    model = resistance_model()
    if args.check:
        return _check(model)
    _report(model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
