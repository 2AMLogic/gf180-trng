#!/usr/bin/env python3
"""Deterministic supply-ripple susceptibility of the buffered RO array (issue #414).

    python3 sim/tools/supply_ripple.py plan            # declared grid + runtime estimate
    python3 sim/tools/supply_ripple.py emit            # (re)write the committed requests
    python3 sim/tools/supply_ripple.py emit --check    # fail if they drifted from the grid
    python3 sim/tools/supply_ripple.py run NAME --outdir DIR   # OPT-IN: one klt sim submit
    python3 sim/tools/supply_ripple.py analyze REPORT... [--json]

What this is
------------
A *schematic-level, deterministic, synthetic-aggressor* experiment. The DUT is
``design/ro_array_core.spice`` (the DR-0018 buffered two-ring array). A
declared sinusoid is put in series with one ring supply pin, or both, and the
response of the ring edge timing at the injected frequency is read out. The
zero-amplitude unit of every request is the control: same netlist, corner,
window and solver settings.

It does **not** model a supply network, a substrate, an aggressor block, or any
noise. It does not feed the sizing law, claim a min-entropy, size a filter, or
change a spec target or a signoff verdict. Every number it reports is a
*susceptibility* (edge-time displacement or fractional-frequency modulation per
volt of injected rail ripple), and :data:`LIMITS` is printed with every table.

Nothing here runs under ``sim/selftest.sh`` or CI beyond the offline unit tests
(``sim/tests/test_supply_ripple.py``) and ``emit --check``. The simulations go
to the batch fleet through ``klt sim`` -- never to a hand-rolled local loop.

The request grid
----------------
Each committed ``sim/tb/ro-array-supply-ripple/request-*.json`` is one ``klt sim``
request for one PVT corner and one ripple frequency. Its ``corners.supply_v``
carries, *moving together by index*, the supply and four DC-source parameters
(``vamp``/``vfrq``/``vm1``/``vm2``) that the deck turns into the sinusoid, so
one request lists a whole (mode, amplitude) grid. Edge times are ``.meas``
rows (13 significant digits via ``measureprec``); everything else is offline.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TB_DIR = REPO_ROOT / "sim" / "tb" / "ro-array-supply-ripple"
DECK = "tb_ro_array_supply_ripple.sp"
DUT_PATH = "design/ro_array_core.spice"

# --------------------------------------------------------------------------
# Declared grid (chosen before any run; changing it changes the committed
# requests, which `emit --check` then flags).
# --------------------------------------------------------------------------

#: Peak ripple amplitudes, volts. 0 is the control and is always present.
AMPS_V = (0.010, 0.050, 0.150)

#: Ripple placement: (label, m1, m2). Common-mode (same phase) on both rails.
MODES = (("ring1", 1, 0), ("both", 1, 1))

#: Supply envelope the covered PVT grid is stated over (DR-0006): nominal 3.30 V
#: +/-10 %. A perturbed rail outside it is labelled, not hidden.
ENVELOPE_V = (2.97, 3.63)

#: PVT corners. ``periods_s`` are the buffered array's own ring periods at that
#: corner (1/f_r1, 1/f_r2 from sim/records/2026-08-02-ro-array-core-pvt-q-32.md
#: and -54.md), used only to size how many edges to request; ``f_beat_hz`` is
#: the observed |f_r1 - f_r2| of those same records, rounded to 50 kHz.
CORNERS = {
    "nominal": {
        "process": "tt",
        "temp_c": 27,
        "vdd": 3.30,
        "periods_s": (1 / 1.497549e8, 1 / 1.602393e8),
        "f_beat_hz": 10.50e6,
        "provenance": "tt/27/3.30; ring frequencies from "
        "sim/records/2026-08-02-ro-array-core-pvt-q-32.md (f_r1 149.755 MHz, "
        "f_r2 160.239 MHz, difference 10.484 MHz)",
    },
    "binding": {
        "process": "ss",
        "temp_c": 125,
        "vdd": 3.63,
        "periods_s": (1 / 1.043706e8, 1 / 1.120239e8),
        "f_beat_hz": 7.65e6,
        "provenance": "ss/125/3.63, the entropy-binding corner of "
        "sim/characterization-worst-corner-and-mc-mismatch.md section 2; "
        "ring frequencies from sim/records/2026-08-02-ro-array-core-pvt-q-54.md "
        "(f_r1 104.371 MHz, f_r2 112.024 MHz, difference 7.653 MHz)",
    },
}

#: gf180mcuD corner sections, as sim/tb/ro-ring11-pex/request.json.
PROCESS_SECTIONS = {
    "tt": ["typical", "bjt_typical", "diode_typical", "res_typical", "moscap_typical", "mimcap_typical"],
    "ss": ["ss", "bjt_ss", "diode_ss", "res_ss", "moscap_ss", "mimcap_ss"],
    "ff": ["ff", "bjt_ff", "diode_ff", "res_ff", "moscap_ff", "mimcap_ff"],
}

LOW_F_HZ = 2.0e6

#: Simulation start-up allowance: edges before this are not fitted.
T_FIT_START_S = 100e-9

#: Window (tstop) and solver step per frequency point.
TSTOP_S = {"lowf": 2.7e-6, "beat": 0.7e-6}
TSTEP_MAIN_S = 10e-12

#: Edge-count safety margin: a ring may slow by this factor under ripple.
SLOWDOWN_MARGIN = 1.10

#: (request name, corner, freq key, tstep). The convergence requests re-run the
#: control and the "both"/50 mV unit of binding-beat at finer solver steps.
REQUESTS = (
    ("nominal-lowf", "nominal", "lowf", TSTEP_MAIN_S),
    ("nominal-beat", "nominal", "beat", TSTEP_MAIN_S),
    ("binding-lowf", "binding", "lowf", TSTEP_MAIN_S),
    ("binding-beat", "binding", "beat", TSTEP_MAIN_S),
    ("conv-binding-beat-5p", "binding", "beat", 5e-12),
    ("conv-binding-beat-2p5", "binding", "beat", 2.5e-12),
)
CONVERGENCE_UNITS = ((0.0, 0, 0), (0.050, 1, 1))

#: Host seconds per solver step, measured 2026-10-09 on a dispatch worker with a
#: single-corner local probe of this deck (30k steps tt/27/3.30 in 20-22 s).
#: An ESTIMATE for planning; the fleet report's runtime_s replaces it.
SECONDS_PER_STEP = 7.0e-4

LIMITS = (
    "Schematic-level DUT (design/ro_array_core.spice), deterministic (no noise, no "
    "mismatch), ideal series sinusoid: not an extracted supply network, not a "
    "physical aggressor.",
    "Only the ring supply pins (vddr1/vddr2) are perturbed; the output buffers and "
    "XOR combiner on `vdd`, the enable, ground and substrate are not.",
    "Reports susceptibility (timing response per volt). It is not a jitter, a "
    "min-entropy, a filter-sizing or an impedance-target result, and "
    "ripple-induced timing variation must not enter the sizing law as random jitter.",
    "A grid of 3 amplitudes x 2 placements x 2 frequency classes x 2 PVT corners: "
    "other corners, frequencies and phases between the two rails are untested.",
)


# --------------------------------------------------------------------------
# Request construction
# --------------------------------------------------------------------------


def frequency_hz(corner: str, freq_key: str) -> float:
    return LOW_F_HZ if freq_key == "lowf" else CORNERS[corner]["f_beat_hz"]


def edge_counts(corner: str, tstop_s: float) -> tuple[int, int]:
    """Edges to request per ring: those that fit the window with margin."""
    out = []
    for period in CORNERS[corner]["periods_s"]:
        out.append(int((tstop_s - 5e-9) / (period * SLOWDOWN_MARGIN)))
    return out[0], out[1]


def units(name: str) -> list[tuple[float, int, int]]:
    """(amplitude_V, m1, m2) per grid point; the control (0, 0, 0) is first."""
    if name.startswith("conv-"):
        return list(CONVERGENCE_UNITS)
    grid = [(0.0, 0, 0)]
    for _, m1, m2 in MODES:
        for amp in AMPS_V:
            grid.append((amp, m1, m2))
    return grid


def build_request(name: str, corner: str, freq_key: str, tstep_s: float) -> dict:
    c = CORNERS[corner]
    tstop = TSTOP_S[freq_key]
    f = frequency_hz(corner, freq_key)
    pts = units(name)
    k1, k2 = edge_counts(corner, tstop)
    meas = []
    for ring, kmax in ((1, k1), (2, k2)):
        for k in range(1, kmax + 1):
            meas.append(
                {
                    "name": f"e{ring}_{k}",
                    "spice": f".meas tran e{ring}_{k} when v(ro{ring})=v(vth) rise={k}",
                    "unit": "s",
                }
            )
    t0 = f"{T_FIT_START_S * 1e9:g}n"
    t1 = f"{tstop * 1e9:g}n"
    for ring in (1, 2):
        for op, tag in (("max", "max"), ("min", "min"), ("avg", "avg")):
            meas.append(
                {
                    "name": f"r{ring}_{tag}",
                    "spice": f".meas tran r{ring}_{tag} {op} v(vddr{ring}) from={t0} to={t1}",
                    "unit": "V",
                }
            )
    return {
        "_comment": (
            f"issue #414 supply-ripple susceptibility, {corner} corner "
            f"({c['provenance']}), ripple {f / 1e6:g} MHz, solver step "
            f"{tstep_s * 1e12:g} ps. Generated by sim/tools/supply_ripple.py; "
            "do not edit by hand (`emit --check` fails if this drifts)."
        ),
        "netlist": DECK,
        "engine": "ngspice",
        "models": {"pdk": "gf180mcuD", "lib": "libs.tech/ngspice/sm141064.ngspice"},
        "corners": {
            "process": [{"name": c["process"], "sections": PROCESS_SECTIONS[c["process"]]}],
            "supply_v": {
                "vsupply": [c["vdd"]] * len(pts),
                "vamp": [p[0] for p in pts],
                "vfrq": [f] * len(pts),
                "vm1": [p[1] for p in pts],
                "vm2": [p[2] for p in pts],
            },
            "temperature_c": [c["temp_c"]],
        },
        "analysis": {
            "kind": "tran",
            "args": f"{tstep_s * 1e12:g}p {tstop * 1e9:g}n 0 {tstep_s * 1e12:g}p",
        },
        "measurements": meas,
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
    return {n: build_request(n, c, fk, ts) for n, c, fk, ts in REQUESTS}


def estimate_seconds(name: str, corner: str, freq_key: str, tstep_s: float) -> float:
    steps = TSTOP_S[freq_key] / tstep_s
    return steps * SECONDS_PER_STEP * len(units(name))


def plan_text() -> str:
    lines = [
        "Supply-ripple susceptibility campaign (issue #414): declared grid",
        "",
        f"amplitudes (V peak): {', '.join(f'{a:g}' for a in AMPS_V)} plus a 0 V control per request",
        f"placements: {', '.join(m[0] for m in MODES)} (both = same phase on vddr1 and vddr2)",
        f"supply envelope for the statement 'in-envelope': {ENVELOPE_V[0]:g}-{ENVELOPE_V[1]:g} V",
        "",
        f"{'request':24} {'corner':8} {'f_ripple':>9} {'tstop':>7} {'tstep':>7} {'units':>5} {'est CPU-s':>10}",
    ]
    total = 0.0
    n_units = 0
    for name, corner, fk, ts in REQUESTS:
        est = estimate_seconds(name, corner, fk, ts)
        total += est
        n_units += len(units(name))
        lines.append(
            f"{name:24} {corner:8} {frequency_hz(corner, fk) / 1e6:7.2f}MHz "
            f"{TSTOP_S[fk] * 1e6:5.2f}us {ts * 1e12:5.1f}ps {len(units(name)):5d} {est:10.0f}"
        )
    lines += [
        "",
        f"total: {len(REQUESTS)} requests, {n_units} simulation units, ~{total / 3600:.1f} CPU-hours "
        f"at {SECONDS_PER_STEP * 1e3:.2f} ms/step (an estimate from one local single-corner probe;",
        "the batch fleet runs a request's units in parallel, so wall time is dominated by the",
        "longest unit plus Spot acquisition, not by this sum). Not run by CI or selftest.",
        "Submit one request at a time:  python3 sim/tools/supply_ripple.py run NAME --outdir DIR",
    ]
    return "\n".join(lines)


def dut_blob_sha() -> str:
    data = (REPO_ROOT / DUT_PATH).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


# --------------------------------------------------------------------------
# Tone extraction (stdlib only)
# --------------------------------------------------------------------------


def _solve(a: list[list[float]], b: list[float]) -> list[float]:
    """Gaussian elimination with partial pivoting (small dense systems)."""
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[piv][col]) < 1e-300:
            raise ValueError("singular tone-fit system (window too short or degenerate)")
        m[col], m[piv] = m[piv], m[col]
        for r in range(col + 1, n):
            fac = m[r][col] / m[col][col]
            for c in range(col, n + 1):
                m[r][c] -= fac * m[col][c]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        x[r] = (m[r][n] - sum(m[r][c] * x[c] for c in range(r + 1, n))) / m[r][r]
    return x


def fit_tone(t: list[float], y: list[float], f_hz: float, poly_order: int = 2) -> dict:
    """Least-squares fit ``y = poly(t) + a cos(wt) + b sin(wt)``.

    ``w = 2 pi f_hz`` and the phase is referenced to ``t = 0``, the instant the
    deck's sinusoid starts at zero phase, so ``phase_rad`` is the lead of the
    fitted tone over ``sin(w t)``. The polynomial (default quadratic, in a
    window-normalised time) absorbs the ring's own period, any slow start-up
    drift, and a constant beat; it is *not* allowed to absorb the tone.

    Returns ``amp`` (same unit as ``y``), ``phase_rad``, ``resid_rms``,
    ``sigma_amp`` (white-residual estimate ``resid_rms * sqrt(2/n)`` of the
    amplitude's standard error), ``n``, ``cycles`` and ``frac_explained``
    (fraction of the post-polynomial variance the tone removes).
    """
    n = len(t)
    if n != len(y):
        raise ValueError("t and y differ in length")
    if n < poly_order + 4:
        raise ValueError(f"need at least {poly_order + 4} samples, got {n}")
    t0, t1 = t[0], t[-1]
    mid, half = 0.5 * (t0 + t1), 0.5 * (t1 - t0)
    if half <= 0:
        raise ValueError("zero-length window")
    w = 2.0 * math.pi * f_hz

    def row(ti: float) -> list[float]:
        s = (ti - mid) / half
        return [s**k for k in range(poly_order + 1)] + [math.cos(w * ti), math.sin(w * ti)]

    rows = [row(ti) for ti in t]
    p = len(rows[0])
    ata = [[sum(r[i] * r[j] for r in rows) for j in range(p)] for i in range(p)]
    aty = [sum(r[i] * yi for r, yi in zip(rows, y)) for i in range(p)]
    coef = _solve(ata, aty)
    resid = [yi - sum(c * v for c, v in zip(coef, r)) for r, yi in zip(rows, y)]
    rms = math.sqrt(sum(e * e for e in resid) / max(n - p, 1))
    a, b = coef[-2], coef[-1]

    # Variance left after the polynomial alone, to say how much the tone explains.
    pp = poly_order + 1
    ata0 = [[ata[i][j] for j in range(pp)] for i in range(pp)]
    coef0 = _solve(ata0, aty[:pp])
    resid0 = [yi - sum(c * v for c, v in zip(coef0, r[:pp])) for r, yi in zip(rows, y)]
    ss0 = sum(e * e for e in resid0)
    ss1 = sum(e * e for e in resid)
    return {
        "amp": math.hypot(a, b),
        "phase_rad": math.atan2(a, b),
        "resid_rms": rms,
        "sigma_amp": rms * math.sqrt(2.0 / n),
        "n": n,
        "cycles": (t1 - t0) * f_hz,
        "frac_explained": (1.0 - ss1 / ss0) if ss0 > 0 else 0.0,
    }


def integer_cycle_window(edges: list[float], f_hz: float, t_start: float) -> list[float]:
    """Edges in ``[t_start, t_start + N/f]`` for the largest whole N that fits."""
    kept = [e for e in edges if e >= t_start]
    if not kept:
        return []
    n_cyc = math.floor((kept[-1] - t_start) * f_hz)
    if n_cyc < 1:
        return []
    t_end = t_start + n_cyc / f_hz
    return [e for e in kept if e <= t_end]


def ring_displacement_fit(edges: list[float], f_hz: float, t_start: float = T_FIT_START_S,
                          max_cycles: int | None = None) -> dict:
    """Edge-time displacement tone of one ring.

    Fits edge time against a quadratic in edge index plus the tone in absolute
    time; the tone amplitude is the edge-time displacement in seconds. A later
    edge means a slower ring, so fractional-frequency modulation is
    ``2 pi f * amp`` (dimensionless), returned as ``ffm_amp``.
    """
    sel = integer_cycle_window(edges, f_hz, t_start)
    if max_cycles is not None and sel:
        sel = [e for e in sel if e <= t_start + max_cycles / f_hz]
    if not sel:
        raise ValueError("no edges inside a whole-cycle window")
    first = edges.index(sel[0])
    # Fit t_n against the *index* polynomial: it absorbs the ring period exactly.
    idx = [float(first + i) for i in range(len(sel))]
    fit = _fit_index_poly(idx, sel, f_hz)
    fit["ffm_amp"] = 2.0 * math.pi * f_hz * fit["amp"]
    return fit


def _fit_index_poly(idx: list[float], t: list[float], f_hz: float, poly_order: int = 2) -> dict:
    """Edge time ``t`` modelled as poly(edge index) + tone(t). See ring_displacement_fit."""
    n = len(t)
    if n < poly_order + 4:
        raise ValueError(f"need at least {poly_order + 4} edges in the window, got {n}")
    i0, i1 = idx[0], idx[-1]
    mid, half = 0.5 * (i0 + i1), 0.5 * (i1 - i0)
    w = 2.0 * math.pi * f_hz

    def row(i: float, ti: float) -> list[float]:
        s = (i - mid) / half
        return [s**k for k in range(poly_order + 1)] + [math.cos(w * ti), math.sin(w * ti)]

    rows = [row(i, ti) for i, ti in zip(idx, t)]
    p = len(rows[0])
    ata = [[sum(r[i] * r[j] for r in rows) for j in range(p)] for i in range(p)]
    aty = [sum(r[i] * yi for r, yi in zip(rows, t)) for i in range(p)]
    coef = _solve(ata, aty)
    resid = [yi - sum(c * v for c, v in zip(coef, r)) for r, yi in zip(rows, t)]
    rms = math.sqrt(sum(e * e for e in resid) / max(n - p, 1))
    a, b = coef[-2], coef[-1]
    pp = poly_order + 1
    coef0 = _solve([[ata[i][j] for j in range(pp)] for i in range(pp)], aty[:pp])
    resid0 = [yi - sum(c * v for c, v in zip(coef0, r[:pp])) for r, yi in zip(rows, t)]
    ss0 = sum(e * e for e in resid0)
    ss1 = sum(e * e for e in resid)
    return {
        "amp": math.hypot(a, b),
        "phase_rad": math.atan2(a, b),
        "resid_rms": rms,
        "sigma_amp": rms * math.sqrt(2.0 / n),
        "n": n,
        "cycles": (t[-1] - t[0]) * f_hz,
        "frac_explained": (1.0 - ss1 / ss0) if ss0 > 0 else 0.0,
    }


def interpolate_phase(edges: list[float], t: float) -> float | None:
    """Cycle phase of a ring at time ``t`` (edge n = n whole cycles), linear
    between edges; ``None`` outside the edge span."""
    if t < edges[0] or t > edges[-1]:
        return None
    lo, hi = 0, len(edges) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if edges[mid] <= t:
            lo = mid
        else:
            hi = mid
    return lo + (t - edges[lo]) / (edges[lo + 1] - edges[lo])


def beat_phase_fit(edges1: list[float], edges2: list[float], f_hz: float,
                   t_start: float = T_FIT_START_S) -> dict:
    """Tone in the relative phase of the two rings, sampled at ring-1 edges.

    ``phi(t) = phase1(t) - phase2(t)`` is, for two free-running rings, a
    steady ramp (the beat) plus whatever the injected tone does to the
    *difference*; the fit absorbs the ramp and any slow drift with a quadratic
    and reports the tone amplitude in cycles of ring 1 (``amp``) and as a time
    ``amp / f_ring1`` in ``amp_s``. Common-mode rail ripple that moves both rings alike
    shows up here only through the rings' unequal sensitivity.
    """
    t_hi = min(edges1[-1], edges2[-1])
    e1 = [e for e in edges1 if e <= t_hi]
    sel = integer_cycle_window(e1, f_hz, t_start)
    ts, ys = [], []
    for e in sel:
        p2 = interpolate_phase(edges2, e)
        if p2 is None:
            continue
        ts.append(e)
        ys.append(float(edges1.index(e)) - p2)
    fit = fit_tone(ts, ys, f_hz)
    f1 = (len(sel) - 1) / (sel[-1] - sel[0]) if len(sel) > 1 else float("nan")
    fit["amp_s"] = fit["amp"] / f1
    fit["f_ring1_hz"] = f1
    return fit


# --------------------------------------------------------------------------
# Report analysis
# --------------------------------------------------------------------------


def tone_detected(fit: dict, k_sigma: float = 5.0) -> bool:
    """A tone is called detected only if it exceeds ``k_sigma`` standard errors
    of the white residual. Deterministic residual structure (a start-up
    remnant, solver-step steps) is *not* white, so this is a floor to compare
    controls against, not a proof that anything beneath it is noise."""
    return fit["sigma_amp"] > 0 and fit["amp"] > k_sigma * fit["sigma_amp"]


def unit_edges(measurements: dict[str, float], ring: int) -> list[float]:
    out = []
    k = 1
    while f"e{ring}_{k}" in measurements:
        out.append(measurements[f"e{ring}_{k}"])
        k += 1
    return out


def analyse_unit(corner: dict, f_hz: float) -> dict:
    """Tone fits for one report corner (one grid unit)."""
    m = {x["name"]: x["value"] for x in corner["measurements"] if x.get("value") is not None}
    sv = corner["supply_v"]
    e1, e2 = unit_edges(m, 1), unit_edges(m, 2)
    amp = float(sv["vamp"])
    res = {
        "corner_id": corner["corner_id"],
        "amp_v": amp,
        "m1": int(sv["vm1"]),
        "m2": int(sv["vm2"]),
        "vdd": float(sv["vsupply"]),
        "status": corner.get("status"),
        "runtime_s": corner.get("runtime_s"),
        "n_edges": (len(e1), len(e2)),
    }
    for ring in (1, 2):
        lo, hi, avg = (m.get(f"r{ring}_{k}") for k in ("min", "max", "avg"))
        res[f"rail{ring}"] = {"min": lo, "max": hi, "avg": avg}
        if lo is not None and hi is not None:
            res[f"rail{ring}"]["pp_half"] = 0.5 * (hi - lo)
            res[f"rail{ring}"]["in_envelope"] = lo >= ENVELOPE_V[0] - 1e-6 and hi <= ENVELOPE_V[1] + 1e-6
    try:
        res["ring1"] = ring_displacement_fit(e1, f_hz)
        res["ring2"] = ring_displacement_fit(e2, f_hz)
        res["beat"] = beat_phase_fit(e1, e2, f_hz)
        # Window check: refit on one fewer whole ripple cycle (>= 3 cycles kept).
        cyc = math.floor(res["ring1"]["cycles"] + 1e-6)
        if cyc >= 4:
            res["ring1_short"] = ring_displacement_fit(e1, f_hz, max_cycles=cyc - 1)
    except ValueError as err:
        res["error"] = str(err)
    return res


def analyse_report(report: dict, f_hz: float | None = None) -> dict:
    corners = report["corners"]
    if f_hz is None:
        f_hz = float(corners[0]["supply_v"]["vfrq"])
    units_ = [analyse_unit(c, f_hz) for c in corners]
    env = report.get("environment", {})
    return {
        "f_hz": f_hz,
        "units": units_,
        "netlist_sha256": env.get("netlist_sha256"),
        "engine_version": env.get("engine_version"),
        "klt_version": report.get("provenance", {}).get("klt_version"),
        "pdk_version": report.get("provenance", {}).get("pdk", {}).get("version"),
        "models_lib_sha256": env.get("models_lib_sha256"),
        "remote": env.get("remote"),
    }


def _fmt(x: float | None, spec: str = ".3g") -> str:
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else format(x, spec)


def sensitivity_rows(an: dict) -> list[str]:
    """Markdown rows: per unit, tone response and the control it is read against."""
    rows = []
    ctrl = next((u for u in an["units"] if u["amp_v"] == 0.0), None)
    for u in an["units"]:
        if "error" in u:
            rows.append(f"| {u['corner_id']} | error: {u['error']} |")
            continue
        mode = "control" if u["amp_v"] == 0 else ("ring1" if (u["m1"], u["m2"]) == (1, 0)
                                                 else "both" if (u["m1"], u["m2"]) == (1, 1) else "other")
        env = "-"
        if u["amp_v"] > 0:
            ok = all(u[f"rail{r}"].get("in_envelope", True) for r in (1, 2) if (u["m1"], u["m2"])[r - 1])
            env = "in" if ok else "OUT"
        a = u["amp_v"]
        cells = [
            mode, f"{a * 1e3:g}", env,
            _fmt(u["ring1"]["amp"] * 1e12), _fmt(u["ring2"]["amp"] * 1e12),
            _fmt(u["beat"]["amp_s"] * 1e12),
            _fmt(u["ring1"]["ffm_amp"] / a * 1e-3 * 1e6 if a else None),
            _fmt(u["ring1"]["resid_rms"] * 1e12),
            _fmt(u["ring1"]["amp"] / u["ring1"]["sigma_amp"], ".1f"),
            _fmt(u["ring1"]["frac_explained"], ".4f"),
        ]
        rows.append("| " + " | ".join(cells) + " |")
    _ = ctrl
    return rows


TABLE_HEAD = (
    "| placement | amp (mV) | rails | ring1 x (ps) | ring2 x (ps) | beat-phase x (ps) | "
    "ring1 ffm (ppm/mV) | ring1 resid rms (ps) | ring1 tone/sigma | tone explains |\n"
    "|---|---|---|---|---|---|---|---|---|---|"
)


def convergence_text(main: dict, finer: dict[str, dict]) -> str:
    """Compare the both/50 mV and control units of binding-beat across solver steps."""
    def pick(an: dict, ctrl: bool) -> dict | None:
        for u in an["units"]:
            if "error" in u:
                continue
            if ctrl and u["amp_v"] == 0.0:
                return u
            if not ctrl and abs(u["amp_v"] - 0.05) < 1e-12 and (u["m1"], u["m2"]) == (1, 1):
                return u
        return None

    lines = ["| solver step | control ring1 x (ps) | 50 mV both ring1 x (ps) | rel. change vs 10 ps |", "|---|---|---|---|"]
    ref = pick(main, False)
    for label, an in [("10 ps", main)] + sorted(finer.items()):
        c, s = pick(an, True), pick(an, False)
        if c is None or s is None or ref is None:
            lines.append(f"| {label} | n/a | n/a | n/a |")
            continue
        rel = (s["ring1"]["amp"] - ref["ring1"]["amp"]) / ref["ring1"]["amp"]
        lines.append(f"| {label} | {c['ring1']['amp'] * 1e12:.3g} | {s['ring1']['amp'] * 1e12:.3g} | {rel:+.2%} |")
    return "\n".join(lines)


def cmd_analyze(paths: list[str], as_json: bool) -> int:
    results = {}
    for p in paths:
        with open(p) as fh:
            rep = json.load(fh)
        results[Path(p).name] = analyse_report(rep)
    if as_json:
        print(json.dumps(results, indent=1, default=str))
        return 0
    print(f"DUT blob sha (design/ro_array_core.spice): {dut_blob_sha()}\n")
    for name, an in results.items():
        print(f"## {name}  (ripple {an['f_hz'] / 1e6:g} MHz)")
        print(f"netlist_sha256={an['netlist_sha256']} engine={an['engine_version']} klt={an['klt_version']}")
        print(f"pdk={an['pdk_version']} models_lib_sha256={an['models_lib_sha256']}\n")
        print(TABLE_HEAD)
        print("\n".join(sensitivity_rows(an)))
        print()
    print("Limits of interpretation:")
    for line in LIMITS:
        print(f"- {line}")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def cmd_emit(check: bool) -> int:
    bad = 0
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
    if name not in {r[0] for r in REQUESTS}:
        print(f"unknown request {name!r}; choices: {', '.join(r[0] for r in REQUESTS)}", file=sys.stderr)
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
                   help="klt command; e.g. 'uvx --from klayout-tools==X.Y.Z klt' when the "
                   "fleet runner pins a different klt than the installed client")
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
