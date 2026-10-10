#!/usr/bin/env python3
"""Integrated fs/sf capture characterization of the ring-array + XOR + sampler path (issue #472).

    python3 sim/tools/fs_sf_capture.py plan             # declared grid + thresholds + runtime estimate
    python3 sim/tools/fs_sf_capture.py emit             # (re)write the committed requests
    python3 sim/tools/fs_sf_capture.py emit --check     # fail if they drifted from the declared grid
    python3 sim/tools/fs_sf_capture.py run NAME --outdir DIR   # OPT-IN: one klt sim submit
    python3 sim/tools/fs_sf_capture.py analyze REPORT... [--json]

What this is
------------
A schematic-level, *deterministic* functional campaign. The DUT is
``design/sampler_core.spice`` instantiated whole. Every simulation unit runs
the 1 Mbps target clock (period 1 us) against the free-running rings, with no
noise and no mismatch, and records the ring duty cycles, the XOR swing and
pulse widths, the reset / ``raw_valid`` behaviour, and the settled ``raw_bit``
after each clock edge against the level of the XOR node at that edge.

It makes no entropy, jitter, silicon or post-layout claim, and a bit pattern
read here is not randomness. It does not replace the isolated-sampler setup /
hold evidence (``sim/tb/sampler-dff-setup-hold/``); it adds the ring + XOR
input path, under the asymmetric MOS corners DR-0006 deferred.

The thresholds below were fixed before any simulation was run. Every threshold
is a named constant so ``plan`` prints it and a reader can see what "pass"
meant. Nothing here relaxes a spec target.

Nothing here runs under ``sim/selftest.sh`` or CI beyond the offline unit tests
(``sim/tests/test_fs_sf_capture.py``) and ``emit --check``. The simulations go to
the batch fleet through ``klt sim`` -- never to a hand-rolled local loop.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TB_DIR = REPO_ROOT / "sim" / "tb" / "sampler-array-fs-sf"
DECK = "tb_sampler_array_fs_sf.sp"
DUT_PATH = "design/sampler_core.spice"

# --------------------------------------------------------------------------
# Declared grid (chosen before any run)
# --------------------------------------------------------------------------

PROCESS_SECTIONS = {
    "tt": ["typical", "bjt_typical", "diode_typical", "res_typical", "moscap_typical", "mimcap_typical"],
    "fs": ["fs", "bjt_typical", "diode_typical", "res_typical", "moscap_typical", "mimcap_typical"],
    "sf": ["sf", "bjt_typical", "diode_typical", "res_typical", "moscap_typical", "mimcap_typical"],
}
ASYM_PROCESSES = ("fs", "sf")
TEMPS_C = (-40, 27, 125)
SUPPLIES_V = (2.97, 3.30, 3.63)

#: Clock phase offsets, seconds, relative to the deck's nominal first edge. The
#: ring periods are 4-8 ns across the grid, so 0..4.5 ns in 1.5 ns steps places
#: the edge at four spread positions of a ring period. Edge k of one unit then
#: also lands at a different ring phase, because 1 us is not a multiple of
#: either ring period.
PHASES_S = (0.0, 1.5e-9, 3.0e-9, 4.5e-9)

TCLK_S = 1e-6  # 1 Mbps, DR-0003's ratified raw target
TCLK0_S = 0.3e-6
TR_S = 1e-9
REL_S = 0.5e-6  # reset release (deck default)
THW_S = 0.5e-6  # clock high time (deck default, 50 % duty)
N_EDGES = 4  # edge 0 occurs under reset; edges 1..3 are post-release captures
READ_DELAYS_S = (8e-9, 50e-9, 300e-9)  # after the *nominal* edge time
TSTOP_S = TCLK0_S + (N_EDGES - 1) * TCLK_S + READ_DELAYS_S[-1] + 20e-9
TSTEP_S = 10e-12

#: Ring / XOR edge-index windows (all inside the first ~0.3 us, before edge 0).
RING_EDGE_RANGE = range(8, 24)
XO_EDGE_RANGE = range(8, 32)

#: Negative controls (tt/27/3.30, phase 0): name -> (vrel, vthw)
NEGATIVE_CONTROLS = {
    "reset-never-released": (1.0, THW_S),
    "clock-high-20ps": (REL_S, 20e-12),
}

# --------------------------------------------------------------------------
# Pass/fail thresholds (fixed before any run; see module docstring)
# --------------------------------------------------------------------------

#: Output swing (ring and XOR) as a fraction of the unit's supply.
SWING_MIN_FRAC = 0.90
#: raw_valid / raw_bit "low" in reset: below this fraction of supply.
LOW_FRAC = 0.10
#: raw_valid "high" after the first post-release edge: above this fraction.
HIGH_FRAC = 0.90
#: Settled-to-a-rail tolerance: |V - nearest rail| <= this fraction of supply,
#: at +8 ns (loose) and at +50 / +300 ns (strict).
RAIL_TOL_8NS_FRAC = 0.10
RAIL_TOL_LATE_FRAC = 0.05
#: raw_bit may not move between +50 and +300 ns by more than this fraction.
DRIFT_TOL_FRAC = 0.05
#: A sample is "decisive" (has a defined expected bit) only when xo, read at the
#: 25 %, 50 % and 80 % levels of the clock edge, is on one side of mid-supply at
#: all three AND the 50 % reading is at least this far from mid-supply. Anything
#: else is "in aperture": counted and checked for resolution, not for value.
DECISIVE_MARGIN_FRAC = 0.20
#: Measured clock edge must be within this of its nominal time (stimulus check).
EDGE_TIME_TOL_S = 50e-12
#: Coverage floor: a PVT point is not coverage-complete with fewer decisive
#: post-release samples than this (of 3 * len(PHASES_S)).
MIN_DECISIVE = 6
#: Informational flags (reported, do not by themselves fail capture).
DUTY_BAND = (0.30, 0.70)
MIN_XO_PULSE_S = 140e-12

LIMITS = (
    "Schematic-level DUT (design/sampler_core.spice), deterministic: no noise, no mismatch, "
    "ideal supply, ideal 1 ns-edge clock. Not an extracted netlist, not silicon.",
    "A functional capture check, not an entropy, jitter or randomness measurement: the bits "
    "read here are the deterministic image of a deterministic waveform.",
    "Phase coverage is 4 declared clock offsets x 3 post-release edges = 12 sampling instants "
    "per PVT point, not a continuous sweep. A sample inside the clock-edge aperture has no "
    "defined expected bit and is checked for resolution to a rail only.",
    "Solver: 10 ps tmax, ngspice default tolerances unless the report says otherwise; edge "
    "times and pulse widths are resolved to about that step (the .meas interpolates "
    "between steps, so sub-step quantities are interpolated, not independently resolved).",
    "The isolated sampler's setup/hold bracketing (sim/tb/sampler-dff-setup-hold/) is not "
    "repeated here; this adds the ring + XOR input path under fs/sf only.",
)


# --------------------------------------------------------------------------
# Request construction
# --------------------------------------------------------------------------


def edge_nominal_s(k: int, phase_s: float = 0.0) -> float:
    """Time the clock's mid-supply crossing occurs for edge k at a given phase."""
    return TCLK0_S + phase_s + k * TCLK_S + TR_S / 2


def measurements() -> list[dict]:
    m: list[dict] = []

    def add(name: str, spice: str, unit: str) -> None:
        m.append({"name": name, "spice": spice, "unit": unit})

    for ring, node in ((1, "xs.ro1"), (2, "xs.ro2")):
        for k in RING_EDGE_RANGE:
            add(f"r{ring}_rise_{k}", f".meas tran r{ring}_rise_{k} when v({node})=v(vth) rise={k}", "s")
            add(f"r{ring}_fall_{k}", f".meas tran r{ring}_fall_{k} when v({node})=v(vth) fall={k}", "s")
        add(f"r{ring}_max", f".meas tran r{ring}_max max v({node}) from=100n to=290n", "V")
        add(f"r{ring}_min", f".meas tran r{ring}_min min v({node}) from=100n to=290n", "V")
    for k in XO_EDGE_RANGE:
        add(f"xo_rise_{k}", f".meas tran xo_rise_{k} when v(xs.xo)=v(vth) rise={k}", "s")
        add(f"xo_fall_{k}", f".meas tran xo_fall_{k} when v(xs.xo)=v(vth) fall={k}", "s")
    add("xo_max", ".meas tran xo_max max v(xs.xo) from=100n to=290n", "V")
    add("xo_min", ".meas tran xo_min min v(xs.xo) from=100n to=290n", "V")
    for k in range(N_EDGES):
        n = k + 1
        add(f"te_{k}", f".meas tran te_{k} when v(clk)=v(vth) rise={n}", "s")
        add(f"xl_{k}", f".meas tran xl_{k} find v(xs.xo) when v(clk)=v(vlo) rise={n}", "V")
        add(f"xm_{k}", f".meas tran xm_{k} find v(xs.xo) when v(clk)=v(vth) rise={n}", "V")
        add(f"xh_{k}", f".meas tran xh_{k} find v(xs.xo) when v(clk)=v(vhi) rise={n}", "V")
        for d in READ_DELAYS_S:
            t = TCLK0_S + k * TCLK_S + d
            tag = f"{round(d * 1e9)}"
            add(f"rb_{k}_{tag}", f".meas tran rb_{k}_{tag} find v(raw_bit) at={t * 1e9:.1f}n", "V")
            add(f"rv_{k}_{tag}", f".meas tran rv_{k}_{tag} find v(raw_valid) at={t * 1e9:.1f}n", "V")
    return m


def unit_grid(name: str) -> list[dict]:
    """Zipped supply_v rows for a request, in order."""
    rows = []
    if name == "grid":
        for v in SUPPLIES_V:
            for ph in PHASES_S:
                rows.append(dict(vsupply=v, vph=ph, vrel=REL_S, vthw=THW_S))
    elif name == "control-tt":
        for ph in PHASES_S:
            rows.append(dict(vsupply=3.30, vph=ph, vrel=REL_S, vthw=THW_S))
        for rel, thw in NEGATIVE_CONTROLS.values():
            rows.append(dict(vsupply=3.30, vph=0.0, vrel=rel, vthw=thw))
    else:
        raise KeyError(name)
    return rows


def request_axes(name: str) -> tuple[list[str], list[int]]:
    if name == "grid":
        return list(ASYM_PROCESSES), list(TEMPS_C)
    return ["tt"], [27]


REQUESTS = ("grid", "control-tt")


def n_units(name: str) -> int:
    procs, temps = request_axes(name)
    return len(procs) * len(temps) * len(unit_grid(name))


def build_request(name: str) -> dict:
    procs, temps = request_axes(name)
    rows = unit_grid(name)
    return {
        "_comment": (
            f"issue #472 integrated fs/sf capture campaign, request '{name}': "
            f"{n_units(name)} units. Generated by sim/tools/fs_sf_capture.py; do not edit by "
            "hand (`emit --check` fails if this drifts)."
        ),
        "netlist": DECK,
        "engine": "ngspice",
        "models": {"pdk": "gf180mcuD", "lib": "libs.tech/ngspice/sm141064.ngspice"},
        "corners": {
            "process": [{"name": p, "sections": PROCESS_SECTIONS[p]} for p in procs],
            "supply_v": {key: [r[key] for r in rows] for key in ("vsupply", "vph", "vrel", "vthw")},
            "temperature_c": temps,
        },
        "analysis": {
            "kind": "tran",
            "args": f"{TSTEP_S * 1e12:g}p {TSTOP_S * 1e9:g}n 0 {TSTEP_S * 1e12:g}p",
        },
        "measurements": measurements(),
        "options": {
            "timeout_s": 7200,
            "keep_artifacts": True,
            "waveforms": False,
            "ngspice_init": ["set measureprec=12"],
        },
    }


def render(req: dict) -> str:
    return json.dumps(req, indent=1) + "\n"


def request_path(name: str) -> Path:
    return TB_DIR / f"request-{name}.json"


def all_requests() -> dict[str, dict]:
    return {n: build_request(n) for n in REQUESTS}


def plan_text() -> str:
    total = sum(n_units(n) for n in REQUESTS)
    lines = [
        "Integrated fs/sf capture campaign (issue #472): declared grid",
        "",
        f"processes (asymmetric): {', '.join(ASYM_PROCESSES)}; temperatures C: {', '.join(map(str, TEMPS_C))}; "
        f"supplies V: {', '.join(f'{v:g}' for v in SUPPLIES_V)}  -> 18 PVT points",
        "control: tt / 27 C / 3.30 V through the same deck",
        f"clock: {TCLK_S * 1e6:g} us period (1 Mbps), edge {TR_S * 1e9:g} ns, phase offsets (ns) "
        f"{', '.join(f'{p * 1e9:g}' for p in PHASES_S)}",
        f"edges per unit: {N_EDGES} (edge 0 under reset, edges 1..{N_EDGES - 1} captures); "
        f"window {TSTOP_S * 1e6:.3f} us, tmax {TSTEP_S * 1e12:g} ps",
        f"negative controls (tt/27/3.30): {', '.join(NEGATIVE_CONTROLS)}",
        "",
        f"{'request':12} {'units':>6}",
    ]
    for n in REQUESTS:
        lines.append(f"{n:12} {n_units(n):6d}")
    lines += [
        f"total simulation units: {total}",
        "",
        "thresholds (fixed before any run):",
        f"  swing (ring, xo) >= {SWING_MIN_FRAC:g} x supply",
        f"  reset: raw_valid, raw_bit < {LOW_FRAC:g} x supply through edge 0",
        f"  raw_valid > {HIGH_FRAC:g} x supply after every post-release edge",
        f"  raw_bit within {RAIL_TOL_8NS_FRAC:g} x supply of a rail at +8 ns, "
        f"{RAIL_TOL_LATE_FRAC:g} at +50/+300 ns, drift +50->+300 ns <= {DRIFT_TOL_FRAC:g}",
        f"  decisive sample: xo on one side of mid-supply at 25/50/80 % clock, |xo50 - mid| >= "
        f"{DECISIVE_MARGIN_FRAC:g} x supply; decisive => raw_bit(+300 ns) must equal it",
        f"  coverage: >= {MIN_DECISIVE} decisive post-release samples per PVT point",
        f"  informational flags: duty outside {DUTY_BAND[0]:g}-{DUTY_BAND[1]:g}, "
        f"xo pulse < {MIN_XO_PULSE_S * 1e12:g} ps",
        "",
        "Not run by CI or selftest. Submit one request at a time:",
        "  python3 sim/tools/fs_sf_capture.py run NAME --outdir DIR",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------


def _vals(corner: dict) -> dict[str, float]:
    return {x["name"]: x["value"] for x in corner.get("measurements", []) if x.get("value") is not None}


def pulse_widths(rises: list[float], falls: list[float]) -> tuple[list[float], list[float]]:
    """High and low durations from unordered rise/fall crossing times."""
    ev = sorted([(t, "r") for t in rises] + [(t, "f") for t in falls])
    hi, lo = [], []
    for (t0, k0), (t1, k1) in zip(ev, ev[1:]):
        if k0 == "r" and k1 == "f":
            hi.append(t1 - t0)
        elif k0 == "f" and k1 == "r":
            lo.append(t1 - t0)
    return hi, lo


def _stats(xs: list[float]) -> dict | None:
    if not xs:
        return None
    return {"n": len(xs), "min": min(xs), "max": max(xs), "mean": sum(xs) / len(xs)}


def rail_distance(v: float, vdd: float) -> float:
    return min(abs(v), abs(v - vdd))


def check_edges(v: dict[str, float], vdd: float, phase_s: float) -> dict:
    """Reset / raw_valid / capture checks for one unit. Returns edge records and failure list."""
    fails: list[str] = []
    edges = []
    mid = 0.5 * vdd
    for k in range(N_EDGES):
        e: dict = {"k": k}
        te = v.get(f"te_{k}")
        e["te"] = te
        if te is None:
            fails.append(f"edge{k}: no clock crossing measured")
        elif abs(te - edge_nominal_s(k, phase_s)) > EDGE_TIME_TOL_S:
            fails.append(f"edge{k}: clock edge at {te:.4e} s, nominal {edge_nominal_s(k, phase_s):.4e} s")
        tags = [str(round(d * 1e9)) for d in READ_DELAYS_S]
        rb = {t: v.get(f"rb_{k}_{t}") for t in tags}
        rv = {t: v.get(f"rv_{k}_{t}") for t in tags}
        e["rb"], e["rv"] = rb, rv
        if any(x is None for x in list(rb.values()) + list(rv.values())):
            fails.append(f"edge{k}: missing raw_bit/raw_valid readout")
            edges.append(e)
            continue
        if k == 0:
            for t in tags:
                if rv[t] >= LOW_FRAC * vdd:
                    fails.append(f"edge0: raw_valid {rv[t]:.3g} V not low under reset (+{t} ns)")
                if rb[t] >= LOW_FRAC * vdd:
                    fails.append(f"edge0: raw_bit {rb[t]:.3g} V not low under reset (+{t} ns)")
            edges.append(e)
            continue
        for t in tags:
            if rv[t] <= HIGH_FRAC * vdd:
                fails.append(f"edge{k}: raw_valid {rv[t]:.3g} V not high (+{t} ns)")
        tol = {tags[0]: RAIL_TOL_8NS_FRAC, tags[1]: RAIL_TOL_LATE_FRAC, tags[2]: RAIL_TOL_LATE_FRAC}
        for t in tags:
            if rail_distance(rb[t], vdd) > tol[t] * vdd:
                fails.append(f"edge{k}: raw_bit {rb[t]:.3g} V not at a rail (+{t} ns)")
        if abs(rb[tags[2]] - rb[tags[1]]) > DRIFT_TOL_FRAC * vdd:
            fails.append(f"edge{k}: raw_bit drifts {rb[tags[2]] - rb[tags[1]]:.3g} V between +{tags[1]} and +{tags[2]} ns")
        xs = [v.get(f"xl_{k}"), v.get(f"xm_{k}"), v.get(f"xh_{k}")]
        e["xo"] = xs
        if any(x is None for x in xs):
            e["decisive"] = None
            fails.append(f"edge{k}: xo not measured at the clock edge")
        else:
            sides = {x > mid for x in xs}
            decisive = len(sides) == 1 and abs(xs[1] - mid) >= DECISIVE_MARGIN_FRAC * vdd
            e["decisive"] = decisive
            if decisive:
                expect = xs[1] > mid
                got = rb[tags[2]] > mid
                e["expect"], e["got"] = int(expect), int(got)
                if expect != got:
                    fails.append(f"edge{k}: captured {int(got)} but xo at the edge was {int(expect)} ({xs[1]:.3g} V)")
        edges.append(e)
    return {"edges": edges, "fails": fails}


def analyse_unit(corner: dict) -> dict:
    v = _vals(corner)
    sv = corner.get("supply_v", {})
    vdd = float(sv.get("vsupply", 3.3))
    phase = float(sv.get("vph", 0.0))
    res: dict = {
        "corner_id": corner.get("corner_id"),
        "process": corner.get("process"),
        "temperature_c": corner.get("temperature_c"),
        "vdd": vdd,
        "phase_s": phase,
        "vrel": float(sv.get("vrel", REL_S)),
        "vthw": float(sv.get("vthw", THW_S)),
        "status": corner.get("status"),
        "runtime_s": corner.get("runtime_s"),
        "n_measured": len(v),
        "notes": [],
        "fails": [],
        "flags": [],
    }
    missing_core = [n for n in ("xo_max", "xo_min", "r1_max", "r1_min", "r2_max", "r2_min") if n not in v]
    if not v or missing_core:
        res["verdict"] = "UNMEASURED"
        res["notes"].append(f"missing core measurements: {', '.join(missing_core) or 'all'}; status={corner.get('status')}")
        return res
    for r in ("r1", "r2", "xo"):
        sw = v[f"{r}_max"] - v[f"{r}_min"]
        res[f"{r}_swing_v"] = sw
        if sw < SWING_MIN_FRAC * vdd:
            res["fails"].append(f"{r} swing {sw:.3g} V < {SWING_MIN_FRAC:g} x supply")
    for r in (1, 2):
        rises = [v[f"r{r}_rise_{k}"] for k in RING_EDGE_RANGE if f"r{r}_rise_{k}" in v]
        falls = [v[f"r{r}_fall_{k}"] for k in RING_EDGE_RANGE if f"r{r}_fall_{k}" in v]
        hi, lo = pulse_widths(rises, falls)
        res[f"r{r}_high_s"], res[f"r{r}_low_s"] = _stats(hi), _stats(lo)
        if hi and lo:
            duties = []
            for h in hi:
                duties.append(h)
            mh, ml = sum(hi) / len(hi), sum(lo) / len(lo)
            res[f"r{r}_duty"] = mh / (mh + ml)
            res[f"r{r}_period_s"] = mh + ml
            if not DUTY_BAND[0] <= res[f"r{r}_duty"] <= DUTY_BAND[1]:
                res["flags"].append(f"ring{r} duty {res[f'r{r}_duty']:.3f} outside {DUTY_BAND[0]:g}-{DUTY_BAND[1]:g}")
        else:
            res["fails"].append(f"ring{r}: no complete high/low pair measured")
    xr = [v[f"xo_rise_{k}"] for k in XO_EDGE_RANGE if f"xo_rise_{k}" in v]
    xf = [v[f"xo_fall_{k}"] for k in XO_EDGE_RANGE if f"xo_fall_{k}" in v]
    xh, xl = pulse_widths(xr, xf)
    res["xo_high_s"], res["xo_low_s"] = _stats(xh), _stats(xl)
    allp = xh + xl
    if allp:
        res["xo_min_pulse_s"] = min(allp)
        if min(allp) < MIN_XO_PULSE_S:
            res["flags"].append(f"xo pulse {min(allp) * 1e12:.0f} ps < {MIN_XO_PULSE_S * 1e12:g} ps")
    else:
        res["fails"].append("xo: no complete pulse measured")
    chk = check_edges(v, vdd, phase)
    res["edges"] = chk["edges"]
    res["fails"] += chk["fails"]
    post = [e for e in chk["edges"] if e["k"] >= 1]
    res["n_decisive"] = sum(1 for e in post if e.get("decisive"))
    res["n_in_aperture"] = sum(1 for e in post if e.get("decisive") is False)
    res["n_edges_post"] = len(post)
    res["ones"] = sum(1 for e in post if e.get("got") == 1)
    if res["n_decisive"] < MIN_DECISIVE and not res["fails"]:
        res["notes"].append("fewer decisive samples than the coverage floor in this unit alone (pooled per PVT point)")
    res["verdict"] = "FUNCTIONAL_MISS" if res["fails"] else ("FLAGGED" if res["flags"] else "OK")
    return res


def pvt_key(u: dict) -> tuple:
    return (u.get("process"), u.get("temperature_c"), u.get("vdd"))


def pool_points(units: list[dict]) -> list[dict]:
    """Pool the phase units of one PVT point into a coverage-aware outcome."""
    pts: dict[tuple, list[dict]] = {}
    for u in units:
        pts.setdefault(pvt_key(u), []).append(u)
    out = []
    for key, us in pts.items():
        verdicts = [u["verdict"] for u in us]
        measured = [u for u in us if u["verdict"] != "UNMEASURED"]
        dec = sum(u.get("n_decisive", 0) for u in measured)
        apert = sum(u.get("n_in_aperture", 0) for u in measured)
        if len(measured) < len(us) or not measured:
            verdict = "UNMEASURED"
        elif "FUNCTIONAL_MISS" in verdicts:
            verdict = "FUNCTIONAL_MISS"
        elif dec < MIN_DECISIVE:
            verdict = "INSUFFICIENT_COVERAGE"
        elif "FLAGGED" in verdicts:
            verdict = "FLAGGED"
        else:
            verdict = "OK"
        agg: dict = {"process": key[0], "temperature_c": key[1], "vdd": key[2], "verdict": verdict,
                     "units": len(us), "units_measured": len(measured), "decisive": dec, "in_aperture": apert}
        for f in ("r1_duty", "r2_duty", "xo_swing_v", "r1_swing_v", "r2_swing_v", "xo_min_pulse_s", "r1_period_s", "r2_period_s"):
            xs = [u[f] for u in measured if f in u]
            agg[f] = (min(xs), max(xs)) if xs else None
        agg["ones"] = sum(u.get("ones", 0) for u in measured)
        agg["fails"] = sorted({f for u in measured for f in u["fails"]})
        agg["flags"] = sorted({f for u in measured for f in u["flags"]})
        out.append(agg)
    return out


def analyse_report(report: dict) -> dict:
    units_ = [analyse_unit(c) for c in report.get("corners", [])]
    env = report.get("environment", {})
    return {
        "units": units_,
        "netlist_sha256": env.get("netlist_sha256"),
        "engine_version": env.get("engine_version"),
        "klt_version": report.get("provenance", {}).get("klt_version"),
        "pdk_version": report.get("provenance", {}).get("pdk", {}).get("version"),
        "models_lib_sha256": env.get("models_lib_sha256"),
        "remote": env.get("remote"),
    }


def _rng(t: tuple | None, scale: float = 1.0, spec: str = ".3f") -> str:
    if t is None:
        return "n/a"
    lo, hi = t[0] * scale, t[1] * scale
    return format(lo, spec) if format(lo, spec) == format(hi, spec) else f"{format(lo, spec)}-{format(hi, spec)}"


POINT_HEAD = (
    "| process | T (C) | VDD (V) | verdict | ring1 duty | ring2 duty | xo swing (V) | xo min pulse (ps) | "
    "decisive / in-aperture | ones |\n|---|---|---|---|---|---|---|---|---|---|"
)


def point_rows(points: list[dict]) -> list[str]:
    rows = []
    for p in sorted(points, key=lambda p: (p["process"], p["temperature_c"], p["vdd"])):
        rows.append(
            f"| {p['process']} | {p['temperature_c']} | {p['vdd']:.2f} | {p['verdict']} | "
            f"{_rng(p['r1_duty'])} | {_rng(p['r2_duty'])} | {_rng(p['xo_swing_v'], 1, '.2f')} | "
            f"{_rng(p['xo_min_pulse_s'], 1e12, '.0f')} | {p['decisive']} / {p['in_aperture']} | {p['ones']} |"
        )
    return rows


def classify_negative(u: dict) -> bool:
    """A negative-control unit must NOT be OK; True means the checker caught it."""
    return u["verdict"] in ("FUNCTIONAL_MISS", "UNMEASURED")


def cmd_analyze(paths: list[str], as_json: bool) -> int:
    allunits: list[dict] = []
    results = {}
    for p in paths:
        with open(p) as fh:
            rep = json.load(fh)
        an = analyse_report(rep)
        results[Path(p).name] = an
        allunits += an["units"]
    if as_json:
        print(json.dumps(results, indent=1, default=str))
        return 0
    neg = [u for u in allunits if u["vrel"] > 0.9 * 1.0 or u["vthw"] < 1e-9]
    norm = [u for u in allunits if u not in neg]
    for name, an in results.items():
        print(f"## {name}")
        print(f"netlist_sha256={an['netlist_sha256']} engine={an['engine_version']} klt={an['klt_version']}")
        print(f"pdk={an['pdk_version']} models_lib_sha256={an['models_lib_sha256']} remote={an['remote']}\n")
    print(POINT_HEAD)
    print("\n".join(point_rows(pool_points(norm))))
    if neg:
        print("\nNegative controls (must be caught):")
        for u in neg:
            print(f"- vrel={u['vrel']:g} vthw={u['vthw']:g}: {u['verdict']} "
                  f"({'caught' if classify_negative(u) else 'NOT CAUGHT'}); {'; '.join(u['fails'][:3]) or u['notes']}")
    print("\nLimits of interpretation:")
    for line in LIMITS:
        print(f"- {line}")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def cmd_emit(check: bool) -> int:
    bad = 0
    TB_DIR.mkdir(parents=True, exist_ok=True)
    for name, req in all_requests().items():
        path = request_path(name)
        text = render(req)
        if check:
            if not path.exists() or path.read_text() != text:
                print(f"DRIFT: {path.relative_to(REPO_ROOT)} does not match the declared grid")
                bad += 1
        else:
            path.write_text(text)
            print(f"wrote {path.relative_to(REPO_ROOT)}")
    if check and not bad:
        print(f"ok: {len(REQUESTS)} requests match the declared grid")
    return 1 if bad else 0


def cmd_run(name: str, outdir: str, backend: str, klt_cmd: str = "klt") -> int:
    if name not in REQUESTS:
        print(f"unknown request {name!r}; choices: {', '.join(REQUESTS)}", file=sys.stderr)
        return 2
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    report = out / f"{name}.report.json"
    cmd = [*shlex.split(klt_cmd), "sim", str(request_path(name)), "--backend", backend, "-o", str(out / name),
           "--format", "json"]
    print("running:", " ".join(cmd))
    with open(report, "w") as fh, open(out / f"{name}.stderr.txt", "w") as err:
        rc = subprocess.call(cmd, stdout=fh, stderr=err)
    print(f"klt exit {rc}; report: {report}; stderr: {out / (name + '.stderr.txt')}")
    return rc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    e = sub.add_parser("emit")
    e.add_argument("--check", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("name")
    r.add_argument("--outdir", required=True)
    r.add_argument("--backend", default="batch", choices=("batch", "local"))
    r.add_argument("--klt", default="klt", dest="klt_cmd",
                   help="klt command; e.g. 'uvx --from klayout-tools==X.Y.Z klt'")
    a = sub.add_parser("analyze")
    a.add_argument("reports", nargs="+")
    a.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "plan":
        print(plan_text())
        return 0
    if args.cmd == "emit":
        return cmd_emit(args.check)
    if args.cmd == "run":
        return cmd_run(args.name, args.outdir, args.backend, args.klt_cmd)
    return cmd_analyze(args.reports, args.json)


if __name__ == "__main__":
    sys.exit(main())
