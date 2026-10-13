#!/usr/bin/env python3
"""Price a higher raw rate for the entropy source, from committed evidence (#629).

    python3 sim/tools/higher_rate_options.py            # print the option table
    python3 sim/tools/higher_rate_options.py --check    # hold the study's quoted figures

This is the arithmetic behind ``docs/higher-rate-source-options-study.md``, a
design study that commits to nothing. It asks, for a few raw-rate targets well
above the shipped array's, what each of two routes would cost in ring count,
area and active power:

  A. more combined rings of the shipped starved cell, sized by DR-0007 §2's
     law ``Q_array(T_s) = sum_i kappa_i^2 T_s / T0_i^2 >= M * Q_H0`` with
     ``kappa^2 = a * kB * T / P_ring`` (DR-0010's ``(*)``), at the
     jitter-energy constant ``a`` measured on the starved cell; and
  B. the metastability-hybrid tap of ``design/xschem/ro_meta_tap.sch``, for
     which only an upper bound on the *sampling* rate and a power/area cost
     can be stated (DR-0011-metastability-hybrid-tap-claims-and-scope).

Which ``a``
-----------
``A_STARVED`` = 7.322: the asymptotic (accumulating-component) constant of the
starved cell at its entropy-binding measured corner, ss/-40/3.63, from
``sim/tools/starved_cell_jitter_energy.py`` over
``sim/records/2026-08-01-ro-ring5-starved-jitter-long-{01,02,03}.md``. It is
the value DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy §2
chooses, and the one that reproduces the shipped array's ~2.77 kbps edge. The
plain-cell 1.79 that ``array_sizing.py`` still carries as its stated constant
is *not* used: it was fitted to a cell this project does not ship.

Where the inputs come from
--------------------------
* Ring period, per-ring power, XOR-tree power and XOR-node transition rate at
  every covered PVT point: ``sim/tools/array_sizing.py``'s own loaders over
  ``*-ro-array-core-power-*`` and ``*-ro-array-core-pvt-q-*``. Rings are sized
  at the minimum-Q (entropy-binding) point; power is quoted at the
  maximum-power (power-binding) point -- the two corners the README rows bind
  at -- so no option is evaluated at a corner that flatters it.
* Ring and XOR footprints: ``layout/floorplan/reports/area.json`` (the ring's
  guarded area is read from its committed assembled GDS; the xor2 and
  sampler flop are priced from the standard-cell LEF there).
* Per-ring sampler data-input charge (option A-post only):
  ``*-sampler-core-liveness-active-*`` (one corner, tt/27/3.30).
* Metastability tap power and strobe rate:
  ``*-ro-array-core-meta-power-*``; trim sensitivity ``*-ro-meta-tap-skew-*``.

What ``--check`` enforces
-------------------------
* ``A_STARVED`` agrees with the live derivation to within ``A_TOLERANCE``.
* The law, applied to the shipped array, still asks for exactly the shipped
  ring count at the shipped array's own highest passing rate -- the
  arithmetic here and ``array_sizing.py``'s cannot have drifted apart.
* Every figure ``QUOTED`` below (which the study document quotes) is
  reproduced by the records within ``QUOTE_TOLERANCE`` (ring counts exactly).

What this does NOT do
---------------------
It measures no entropy and claims no ``H``. ``Q_H0`` is DR-0007 §2's target,
not a measurement; DR-0004's tiering is unchanged and #12 owns ``H``. The
metastability option is given **no** rate figure beyond an upper bound on how
often it can be strobed: DR-0011-metastability establishes no entropy figure
for it, so none is derived here. Stdlib only; no ngspice, no PDK.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import array_sizing as sizing  # noqa: E402
from _record_parsing import current_records  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
AREA_JSON = REPO_ROOT / "layout" / "floorplan" / "reports" / "area.json"

#: Starved-cell jitter-energy constant (asymptotic, ss/-40/3.63). See module
#: docstring; held to its derivation by --check.
A_STARVED = 7.322
A_TOLERANCE = 0.01
#: The measured corner A_STARVED is taken at.
A_CORNER = "ss/-40/3.63"

#: Raw-rate targets considered, bits per second. 100 kbps is an intermediate
#: point; 1 Mbps and 4 Mbps are DR-0003's original row and stretch values.
TARGETS_BPS = (100e3, 1e6, 4e6)

#: DR-0010 §3 measured E_cycle(11 stages) / E_cycle(5 stages) = 2.21 on this
#: cell at tt/27/3.30. Used only to show the size of the E_cycle lever.
E_CYCLE_RATIO_11_TO_5 = 2.21

QUOTE_TOLERANCE = 0.01

#: Figures the study document quotes, keyed by (option, rate_bps).
#: N: rings. P: microwatts. Area: um^2. Ring counts are compared exactly.
QUOTED = {
    ("A", 100e3): {"n": 73, "p_rings_uw": 9969.0, "p_tree_uw": 27119.0,
                   "p_floor_bind_uw": 4093.0, "p_floor_5stage_uw": 838.0,
                   "area_um2": 51620.0, "xo_interval_ps": 63.30},
    ("A", 1e6): {"n": 722, "p_rings_uw": 98598.0, "p_tree_uw": 411473.0,
                 "p_floor_bind_uw": 40926.0, "p_floor_5stage_uw": 8380.0,
                 "area_um2": 510776.0, "xo_interval_ps": 6.40},
    ("A", 4e6): {"n": 2885, "p_rings_uw": 393983.0, "p_tree_uw": 1990219.0,
                 "p_floor_bind_uw": 163706.0, "p_floor_5stage_uw": 33518.0,
                 "area_um2": 2041059.0, "xo_interval_ps": 1.60},
    ("A-post", 100e3): {"n": 73, "p_samplers_uw": 1275.0, "area_um2": 57068.0},
    ("A-post", 1e6): {"n": 722, "p_samplers_uw": 12608.0, "area_um2": 564664.0},
    ("A-post", 4e6): {"n": 2885, "p_samplers_uw": 50380.0, "area_um2": 2256387.0},
}
QUOTED_SCALARS = {
    "rate_shipped_bps": 2774.0,         # shipped array's highest passing rate
    "g_per_ring": 8.3217,               # Q per second of T_s, per ring, min-Q corner
    "p_floor_per_kbps_uw": 40.93,       # (*) ring-power floor, 11-stage, min-Q corner
    "tap_e_strobe_fj": 194.8,           # metastability tap energy per strobe, ff/-40/3.63
    "tap_strobe_rate_min": 5.780e8,     # slowest strobe rate in the meta-power records
    "tap_p_4mbps_uw": 0.779,            # tap power if strobed at 4 MHz
    "trim_res_min_af": 0.157,           # trim step for a 3 fs window at 19.12 ps/fF
    "trim_res_max_af": 22.7,            # trim step for a 300 fs window at 13.23 ps/fF
    "strobe_rate_slowest": 3.376e8,     # slowest XOR-node rate of the shipped array
    "inv_delay_ps_fastest": 52.4,       # tap strobe path / 3 at ff/-40/3.63
    "e_cycle": 5.2397e-13,              # P_ring * T0, mean ring, min-Q corner
    "tap_cell_um2": 74.6,               # 6 inv_1 + 2 nand2_1 equivalents
}


# --------------------------------------------------------------------- arithmetic

def rings_needed(rate_bps: float, g_per_ring: float) -> int:
    """Smallest N with N * g_per_ring / rate >= M * Q_H0 (DR-0007 §2)."""
    return max(1, math.ceil(sizing.MARGIN_M * sizing.Q_H0 * rate_bps / g_per_ring - 1e-9))


def ring_power_floor(rate_bps: float, e_cycle_j: float, a: float, temp_k: float) -> float:
    """DR-0010 (*) solved for P_rings: the total ring power any array of
    rings with energy-per-cycle ``e_cycle_j`` needs to reach ``rate_bps``."""
    return sizing.MARGIN_M * sizing.Q_H0 * rate_bps * e_cycle_j ** 2 / (a * sizing.KB * temp_k)


def tree_power(n: int, e_per_transition_j: float, ring_transitions_per_s: float) -> float:
    """XOR-tree power for an N-input balanced tree (ASSUMED model).

    Each tree level carries, summed over its gates, the transitions of all N
    ring outputs (an XOR output toggles whenever one input does, absent
    coincidences), and there are log2(N) levels, so the tree switches
    ~N * r * log2(N) times per second for per-ring transition rate r. At N = 2
    that is the one measured xor2, exactly. Pulse swallowing at deep levels
    is ignored: where it would happen the topology has already failed (see
    :func:`root_interval_s`), so this is the cost of a tree that works.
    """
    if n < 2:
        return 0.0
    return e_per_transition_j * ring_transitions_per_s * n * math.log2(n)


def root_interval_s(n: int, ring_transitions_per_s: float) -> float:
    """Mean time between transitions at the XOR root for N rings."""
    return 1.0 / (n * ring_transitions_per_s)


def trim_resolution_f(tau_s: float, dt_per_farad: float) -> float:
    """Trim-capacitance step that moves the tap's release skew by ``tau_s``."""
    return tau_s / dt_per_farad


# --------------------------------------------------------------------- evidence

def array_points(a: float = A_STARVED) -> list:
    shipped_n = sizing.shipped_ring_count()
    pts = [sizing.ArrayPoint(r, a=a) for r in sizing.load_array_records()]
    pts = sizing.dedupe_by_corner([p for p in pts if p.n == shipped_n])
    if not pts:
        raise RuntimeError("no shipped-array records found")
    return pts


def area_inputs(path: Path = AREA_JSON) -> dict:
    data = json.loads(path.read_text())
    regions = {r["id"]: r for r in data["regions"]}
    ring = regions["ring1"]
    unit = {b["cell"]: b["unit_um2"] for b in regions["combiner_sampler"]["breakdown"]}
    channel = data["rollup"]["isolation_channel_um"]
    rollup = data["rollup"]
    return {
        # one more ring = its guarded region plus one isolation channel along
        # its short side, as ring1/ring2 are tiled today (ASSUMED to tile 1-D)
        "ring_slot_um2": ring["guarded_area_um2"] + channel * ring["guarded_h_um"],
        "xor2_um2": unit["xor2"],
        "dff_um2": unit["sampler_dff"],
        "inv_um2": unit["ro_buf"],  # inv_1
        # ro_nand2 is priced as nand2_1 + the two starve devices
        "nand2_um2": next(b["unit_um2"] for b in ring["breakdown"] if b["cell"] == "ro_nand2")
        - sum(d["footprint_um2"] for k, d in data["device_footprints"].items()
              if k.endswith("w0.220_l2.000")),
        "analog_um2": rollup["subtotals"]["analog"]["area_um2"],
        "block_um2": rollup["floorplan_area_um2"],
        "budget_um2": rollup["budget_um2"],
    }


def sampler_charge_per_transition() -> float:
    recs = current_records(sizing.RECORDS, "*-sampler-core-liveness-active-[0-9]*.md",
                           make=sizing.Record)
    recs = [r for r in recs if "q_per_transition1_c" in r.values]
    if not recs:
        raise RuntimeError("no sampler-core-liveness-active record with q_per_transition")
    v = recs[-1].values
    return 0.5 * (abs(v["q_per_transition1_c"]) + abs(v["q_per_transition2_c"]))


def meta_points() -> list:
    recs = current_records(sizing.RECORDS, "*-ro-array-core-meta-power-[0-9]*.md",
                           make=sizing.Record)
    return [r for r in recs if "p_tap_w" in r.values]


def skew_points() -> list:
    recs = current_records(sizing.RECORDS, "*-ro-meta-tap-skew-[0-9]*.md", make=sizing.Record)
    return [r for r in recs if "dt_per_ff_s" in r.values]


def derived_a() -> float:
    import starved_cell_jitter_energy as sce  # noqa: PLC0415

    points, _ = sce.load_points()
    for p in points:
        if p.rec.corner == A_CORNER:
            return p.a(p.kappa2_asym)
    raise RuntimeError(f"no starved-cell record at {A_CORNER}")


# --------------------------------------------------------------------- the study

def study(a: float = A_STARVED) -> dict:
    pts = array_points(a)
    n0 = pts[0].n
    bind = min(pts, key=lambda p: p.g)            # entropy-binding (min Q)
    hot = max(pts, key=lambda p: p.p_total)       # power-binding (max P)
    area = area_inputs()

    g_ring = bind.g / n0
    e_cycle = bind.p_rings / n0 * (sum(bind.periods) / n0)   # P_ring * T0, mean ring
    r_ring_bind = bind.xo_rate / n0                           # per-ring transitions/s
    r_ring_hot = hot.xo_rate / n0
    e_tree = hot.p_tree / hot.xo_rate                         # J per XOR-node transition
    p_ring_hot = hot.p_rings / n0
    q_samp = sampler_charge_per_transition()

    out = {
        "a": a, "n_shipped": n0, "bind": bind, "hot": hot, "area": area,
        "g_per_ring": g_ring, "e_cycle": e_cycle,
        "rate_shipped_bps": bind.max_rate_bps(),
        "p_floor_per_kbps_uw": ring_power_floor(1e3, e_cycle, a, bind.rec.temp_k) * 1e6,
        "options": {},
    }
    for rate in TARGETS_BPS:
        n = rings_needed(rate, g_ring)
        p_rings = n * p_ring_hot
        p_tree = tree_power(n, e_tree, r_ring_hot)
        a_rings = n * area["ring_slot_um2"]
        out["options"][("A", rate)] = {
            "n": n,
            "p_rings_uw": p_rings * 1e6,
            "p_tree_uw": p_tree * 1e6,
            "area_um2": a_rings + (n - 1) * area["xor2_um2"],
            "p_floor_bind_uw": ring_power_floor(rate, e_cycle, a, bind.rec.temp_k) * 1e6,
            "p_floor_5stage_uw": ring_power_floor(
                rate, e_cycle / E_CYCLE_RATIO_11_TO_5, a, bind.rec.temp_k) * 1e6,
            "xo_interval_ps": root_interval_s(n, r_ring_bind) * 1e12,
        }
        out["options"][("A-post", rate)] = {
            "n": n,
            "p_rings_uw": p_rings * 1e6,
            # one flop per ring, its D pin toggled by the ring (ASSUMED: the
            # tt/27/3.30 charge per transition holds at the power corner)
            "p_samplers_uw": n * q_samp * r_ring_hot * hot.rec.vdd * 1e6,
            "area_um2": a_rings + n * area["dff_um2"] + (n - 1) * area["xor2_um2"],
        }
    out["xo_interval_ps_1mbps"] = out["options"][("A", 1e6)]["xo_interval_ps"]

    meta = meta_points()
    e_strobe = {r.corner: abs(r.values["p_tap_w"]) / r.values["xo_trans_per_s"] for r in meta}
    hot_meta = max(meta, key=lambda r: abs(r.values["p_tap_w"]))
    skew = skew_points()
    dt_lo = min(r.values["dt_per_ff_s"] for r in skew) / 1e-15   # s per F
    dt_hi = max(r.values["dt_per_ff_s"] for r in skew) / 1e-15
    out["meta"] = {
        "records": meta,
        "e_strobe": e_strobe,
        "tap_e_strobe_fj": e_strobe[hot_meta.corner] * 1e15,
        "tap_p_asbuilt_uw": {r.corner: abs(r.values["p_tap_w"]) * 1e6 for r in meta},
        "tap_strobe_rate": {r.corner: r.values["xo_trans_per_s"] for r in meta},
        "tap_strobe_rate_min": min(r.values["xo_trans_per_s"] for r in meta),
        "tap_p_at_rate_uw": {rate: e_strobe[hot_meta.corner] * rate * 1e6 for rate in TARGETS_BPS},
        # 6x meta_inv + 2x meta_nand2, priced as inv_1 / nand2_1 (ASSUMED)
        "tap_cell_um2": 6 * area["inv_um2"] + 2 * area["nand2_um2"],
        "dt_per_ff": (dt_lo * 1e-15, dt_hi * 1e-15),
        "trim_res_min_af": trim_resolution_f(3e-15, dt_hi) * 1e18,
        "trim_res_max_af": trim_resolution_f(300e-15, dt_lo) * 1e18,
    }
    out["tap_e_strobe_fj"] = out["meta"]["tap_e_strobe_fj"]
    out["tap_strobe_rate_min"] = out["meta"]["tap_strobe_rate_min"]
    out["tap_p_4mbps_uw"] = out["meta"]["tap_p_at_rate_uw"][4e6]
    out["trim_res_min_af"] = out["meta"]["trim_res_min_af"]
    out["trim_res_max_af"] = out["meta"]["trim_res_max_af"]
    out["tap_cell_um2"] = out["meta"]["tap_cell_um2"]
    # the tap is strobed by the XOR node, so its decision rate is bounded by
    # the slowest XOR transition rate over the covered grid of the array as
    # shipped (not the meta-power records' older core)
    slow = min(pts, key=lambda p: p.xo_rate)
    out["strobe_rate_slowest"] = slow.xo_rate
    out["strobe_slowest_point"] = slow
    # one minimum unstarved meta_inv stage: the tap's three-stage strobe path
    # delay over three, at the fastest measured corner (a scale for the XOR
    # root interval; NOT an xor2 delay, which no record measures)
    out["inv_delay_ps_fastest"] = min(r.values["t_path_s"] for r in skew) / 3 * 1e12
    return out


def _fmt_rate(r: float) -> str:
    return f"{r / 1e6:g} Mbps" if r >= 1e6 else f"{r / 1e3:g} kbps"


def report(s: dict) -> None:
    bind, hot, area = s["bind"], s["hot"], s["area"]
    print(f"jitter-energy constant a = {s['a']:g} (starved cell, asymptotic, {A_CORNER})")
    print(f"entropy-binding corner (min Q): {bind.rec.corner}  [{bind.rec.stem}]")
    print(f"power-binding corner (max P):   {hot.rec.corner}  [{hot.rec.stem}]")
    print(f"shipped array: N = {s['n_shipped']}, highest rate meeting DR-0007 §2 at the "
          f"entropy-binding corner = {s['rate_shipped_bps']:.0f} bps")
    print(f"per-ring Q per second of T_s there: g = {s['g_per_ring']:.4f} /s; "
          f"E_cycle (P_ring*T0) = {s['e_cycle']:.4e} J")
    print(f"(*) ring-power floor at that corner: {s['p_floor_per_kbps_uw']:.2f} uW per kbps\n")

    print("Option A: more XOR-combined rings ahead of one sampler (DR-0007 §1 topology)")
    print(f"{'rate':>9} {'N':>5} {'P_rings@hot':>12} {'P_tree@hot':>12} {'floor@bind':>11} "
          f"{'floor 5-stg':>11} {'area um2':>10} {'XOR-root interval':>18}")
    for rate in TARGETS_BPS:
        o = s["options"][("A", rate)]
        print(f"{_fmt_rate(rate):>9} {o['n']:5d} {o['p_rings_uw']:10.0f}uW {o['p_tree_uw']:10.0f}uW "
              f"{o['p_floor_bind_uw']:9.0f}uW {o['p_floor_5stage_uw']:9.0f}uW "
              f"{o['area_um2']:10.0f} {o['xo_interval_ps']:15.2f} ps")
    print("\nOption A-post: same rings, one sampler flop per ring, XOR after sampling")
    print(f"{'rate':>9} {'N':>5} {'P_rings@hot':>12} {'P_samplers@hot':>15} {'area um2':>10}")
    for rate in TARGETS_BPS:
        o = s["options"][("A-post", rate)]
        print(f"{_fmt_rate(rate):>9} {o['n']:5d} {o['p_rings_uw']:10.0f}uW "
              f"{o['p_samplers_uw']:13.0f}uW {o['area_um2']:10.0f}")

    m = s["meta"]
    print("\nOption B: metastability-hybrid tap (NO entropy figure exists; rate is a strobe bound)")
    for r in m["records"]:
        print(f"  {r.corner:<12} strobe rate {m['tap_strobe_rate'][r.corner]:.3e}/s  "
              f"P_tap as built {m['tap_p_asbuilt_uw'][r.corner]:6.1f} uW  "
              f"E/strobe {m['e_strobe'][r.corner] * 1e15:6.1f} fJ  [{r.stem}]")
    for rate in TARGETS_BPS:
        print(f"  if strobed at {_fmt_rate(rate):>9}: P_tap ~ {m['tap_p_at_rate_uw'][rate]:.3f} uW")
    print(f"  cell area (6 inv_1 + 2 nand2_1 equivalents, unlaid-out): {m['tap_cell_um2']:.1f} um2")
    print(f"  trim step to move dt by tau = 3..300 fs at {m['dt_per_ff'][0] * 1e12:.2f}.."
          f"{m['dt_per_ff'][1] * 1e12:.2f} ps/fF: {m['trim_res_min_af']:.3f}..{m['trim_res_max_af']:.1f} aF")
    slow = s["strobe_slowest_point"]
    print(f"  slowest XOR-node (strobe) rate of the shipped array: {s['strobe_rate_slowest']:.4e}/s "
          f"at {slow.rec.corner} [{slow.rec.stem}]")
    print(f"  one minimum unstarved inverter stage (tap strobe path / 3), fastest corner: "
          f"{s['inv_delay_ps_fastest']:.1f} ps")

    print(f"\nbaseline: analog entropy-source area {area['analog_um2']:.1f} um2, block floorplan "
          f"{area['block_um2']:.1f} um2 against a {area['budget_um2']:.0f} um2 row")


def check(s: dict) -> list[str]:
    errors = []
    try:
        a_live = derived_a()
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        errors.append(f"A_STARVED could not be re-derived: {exc}")
    else:
        if abs(a_live - A_STARVED) / A_STARVED > A_TOLERANCE:
            errors.append(f"A_STARVED = {A_STARVED} but starved_cell_jitter_energy.py derives "
                          f"{a_live:.4f} at {A_CORNER}")
    n_edge = rings_needed(s["rate_shipped_bps"] * (1 - 1e-6), s["g_per_ring"])
    if n_edge != s["n_shipped"]:
        errors.append(f"the law asks for N = {n_edge} at the shipped array's own edge "
                      f"({s['rate_shipped_bps']:.0f} bps), not the shipped {s['n_shipped']}")

    def close(label: str, got: float, want: float) -> None:
        if abs(got - want) > QUOTE_TOLERANCE * abs(want):
            errors.append(f"{label}: records give {got:.6g}, study quotes {want:.6g}")

    for key, want in QUOTED.items():
        got = s["options"][key]
        for field, value in want.items():
            if field == "n":
                if got["n"] != value:
                    errors.append(f"{key} N: records give {got['n']}, study quotes {value}")
            else:
                close(f"{key} {field}", got[field], value)
    for field, value in QUOTED_SCALARS.items():
        close(field, s[field], value)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="higher_rate_options.py",
        description="Price higher raw-rate options from committed evidence (#629).",
    )
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero unless the study's quoted figures still reproduce")
    args = parser.parse_args(argv)
    s = study()
    report(s)
    if args.check:
        errors = check(s)
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        if errors:
            return 1
        print(f"\nOK: a = {A_STARVED} matches its derivation, the law reproduces the shipped "
              f"N = {s['n_shipped']}, and every quoted figure reproduces within "
              f"{QUOTE_TOLERANCE:.0%}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
