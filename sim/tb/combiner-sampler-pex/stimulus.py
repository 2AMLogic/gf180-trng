#!/usr/bin/env python3
"""Render the combiner/sampler `klt pex` testbench body and request from one schedule.

    python3 sim/tb/combiner-sampler-pex/stimulus.py           # write tb_combiner_sampler_pex.sp + request.json
    python3 sim/tb/combiner-sampler-pex/stimulus.py --check   # fail if either would change
    python3 sim/tb/combiner-sampler-pex/stimulus.py --table   # print the scenario table

Stdlib only; no klt, ngspice or PDK.

What is checked, and against what
---------------------------------
The block's contract, from design/sampler_core.spice and
design/ro_array_core.spice:

* `ro1 = not rn1`, `ro2 = not rn2` (the two `ro_buf` inverters);
* `xo = ro1 xor ro2` (`xor2`);
* four rising-edge D flip-flops with an active-low reset that forces Q low
  asynchronously and dominates the clock: `raw_bit` samples `xo`,
  `ring_bit1`/`ring_bit2` sample `ro1`/`ro2`, `raw_valid` samples `vdd`
  (so it is low from reset until the first rising edge after release).

`SCHEDULE` drives `rn1`, `rn2`, `clk` and `rst_n` with deterministic
full-swing steps. `expected()` evaluates the contract above in plain Python
at every sample time; each expectation becomes one `.meas tran ... find
v(<node>n) at=<t>` row on a supply-normalised copy of the node, with a
`limits` block of `min 0.9` (logic high) or `max 0.1` (logic low) -- 90 %/
10 % of the corner's own supply. Nothing in the request is hand-typed per
row: change the schedule and the expectations follow.

Settling windows (explicit, by construction):

* inputs change only at falling clock edges, 20 ns before the next rising
  (capture) edge and 20 ns after the previous one;
* `xo`, `ro1`, `ro2` are sampled 1 ns before each capture edge;
* flip-flop outputs are sampled 15 ns after a capture edge, 5 ns before the
  next falling edge and input change;
* reset is released 30 ns before the first capture edge after it (mid clock-
  high phase) and asserted mid clock-low phase, 15 ns from either edge.

Boundary and metastability cases (data or reset changing near a clock edge)
are outside this test.

Four informational rows (`tcq_*`, `trst_*`) measure clock-to-Q and reset-to-Q
50 % crossings with no `limits`; their `pass` means only "measured on both
sides".
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESTBENCH = HERE / "tb_combiner_sampler_pex.sp"
REQUEST = HERE / "request.json"
DUT_FILE = "combiner_sampler_schematic.spice"

NS = 1e-9
PERIOD = 40.0  # ns
EDGE = 0.1  # ns, every stimulus transition
STOP = 370.0  # ns
#: Rising (capture) edges at 20 + 40k ns, falling at 40k ns.
RISES = [20.0 + PERIOD * k for k in range(9)]
HIGH_MIN = 0.9
LOW_MAX = 0.1

#: Port order of the extraction's header, as the DUT renders it. build_dut.py
#: checks the testbench's xdut line against the committed DUT.
XDUT_PORTS = ["rn1", "rn2", "ro1", "ro2", "clk", "vdd", "xo", "raw_bit", "raw_valid",
              "ring_bit1", "ring_bit2", "rst_n", "vss", "vsubs"]

#: (time ns, rn1, rn2) -- input levels from that time on (changes at falling edges).
INPUTS = [
    (0.0, 0, 1),     # reset phase, edge e1: raw_bit/ring_bit1 would capture 1
    (40.0, 0, 0),    # reset phase, edge e2: ring_bit2 would capture 1
    (80.0, 1, 1),    # e3: ro=(0,0) xo=0
    (120.0, 0, 0),   # e4: ro=(1,1) xo=0
    (160.0, 1, 0),   # e5: ro=(0,1) xo=1
    (200.0, 0, 1),   # e6: ro=(1,0) xo=1
    (240.0, 1, 1),   # e7: ro=(0,0) xo=0 (1 -> 0 captures)
    (280.0, 1, 0),   # e8: ro=(0,1) xo=1
    (320.0, 0, 1),   # e9 under reset: raw_bit/ring_bit1 would capture 1
]
#: (time ns, level) for rst_n.
RESET = [(0.0, 0), (70.0, 1), (325.0, 0)]

FLOPS = ("raw_bit", "raw_valid", "ring_bit1", "ring_bit2")
COMB = ("xo", "ro1", "ro2")

#: (scenario name, sample time ns, nodes sampled)
SAMPLES = [
    ("rst_hold_e1", RISES[0] + 15, FLOPS),
    ("rst_hold_e2", RISES[1] + 15, FLOPS),
    ("startup_pre_e3", 95.0, FLOPS),
    *[
        item
        for k in range(2, 8)
        for item in (
            (f"pre_e{k + 1}", RISES[k] - 1, COMB),
            (f"cap_e{k + 1}", RISES[k] + 15, FLOPS),
        )
    ],
    ("rst_async", 330.0, FLOPS),
    ("rst_hold_e9", RISES[8] + 15, FLOPS),
]

#: Informational timing rows (no limits): (name, spice).
TIMING_ROWS = [
    ("tcq_raw_valid_e3",
     f".meas tran tcq_raw_valid_e3 trig v(clkn) val=0.5 td={RISES[2] - 5:g}n rise=1 "
     f"targ v(raw_validn) val=0.5 td={RISES[2] - 5:g}n rise=1"),
    ("tcq_raw_bit_e5",
     f".meas tran tcq_raw_bit_e5 trig v(clkn) val=0.5 td={RISES[4] - 5:g}n rise=1 "
     f"targ v(raw_bitn) val=0.5 td={RISES[4] - 5:g}n rise=1"),
    ("tcq_raw_bit_e7",
     f".meas tran tcq_raw_bit_e7 trig v(clkn) val=0.5 td={RISES[6] - 5:g}n rise=1 "
     f"targ v(raw_bitn) val=0.5 td={RISES[6] - 5:g}n fall=1"),
    ("trst_raw_valid",
     ".meas tran trst_raw_valid trig v(rst_nn) val=0.5 td=320n fall=1 "
     "targ v(raw_validn) val=0.5 td=320n fall=1"),
]


def _level(events: list[tuple], t: float, col: int = 1):
    val = None
    for ev in events:
        if ev[0] <= t:
            val = ev[col]
    return val


def clk_at(t: float) -> int:
    phase = t % PERIOD
    return 1 if 20.0 <= phase < 40.0 else 0


def expected() -> dict[str, int]:
    """Contract-model value of every sampled node at every SAMPLES time."""
    events = sorted(
        {t for t, *_ in INPUTS} | {t for t, _ in RESET} | set(RISES) | {s[1] for s in SAMPLES}
    )
    q = {f: 0 for f in FLOPS}  # value is irrelevant: reset is asserted from t=0
    out: dict[str, int] = {}
    for t in events:
        rn1, rn2 = _level(INPUTS, t, 1), _level(INPUTS, t, 2)
        ro1, ro2 = 1 - rn1, 1 - rn2
        xo = ro1 ^ ro2
        rst_n = _level(RESET, t)
        if t in RISES and rst_n == 1:
            # Data sampled just before the edge: inputs never change at a rise.
            q = {"raw_bit": xo, "raw_valid": 1, "ring_bit1": ro1, "ring_bit2": ro2}
        if rst_n == 0:
            q = {f: 0 for f in FLOPS}
        for name, ts, nodes in SAMPLES:
            if ts == t:
                comb = {"xo": xo, "ro1": ro1, "ro2": ro2}
                for n in nodes:
                    out[f"{name}_{n}"] = comb[n] if n in comb else q[n]
    return out


def _check_schedule() -> None:
    for t, *_ in INPUTS[1:]:
        if t % PERIOD != 0:
            raise ValueError(f"input change at {t} ns is not on a falling edge")
    for t, _ in RESET[1:]:
        if any(abs(t - r) < 10 for r in RISES) or any(abs(t - f) < 5 for f in range(0, int(STOP), 40)):
            raise ValueError(f"reset edge at {t} ns is within the settling window of a clock edge")
    for name, ts, _ in SAMPLES:
        if any(0 <= ts - c < 1 for c, *_ in INPUTS) or ts >= STOP:
            raise ValueError(f"sample {name} at {ts} ns is not settled")


def _pwl(points: list[tuple[float, int]]) -> str:
    """Step list -> PWL with EDGE-ns transitions starting at each step time."""
    out = [(0.0, points[0][1])]
    for t, v in points[1:]:
        prev = out[-1][1]
        if v == prev:
            continue
        out += [(t, prev), (t + EDGE, v)]
    return " ".join(f"{t:g}n {v}" for t, v in out)


def _clk_points() -> list[tuple[float, int]]:
    pts = [(0.0, 0)]
    for r in RISES:
        pts += [(r, 1), (r + 20.0, 0)]
    return [p for p in pts if p[0] < STOP]


def render_testbench() -> str:
    _check_schedule()
    monitors = FLOPS + COMB
    lines = [
        "* combiner-sampler-pex -- the assembled combiner/sampler block (combiner_sampler)",
        "* under a deterministic two-input, clock and reset schedule, for `klt pex` (#418).",
        "* GENERATED by sim/tb/combiner-sampler-pex/stimulus.py -- do not edit by hand.",
        "*",
        "* A circuit body for `klt sim`: no .control/.end. klt sim appends the corner's",
        "* .lib/.temp cards, the .meas cards from request.json, `alter vsupply=<V>` for",
        "* the supply corner, and the analysis. The one .include below is the schematic",
        "* DUT; `klt pex` re-points exactly that line at the netlist it extracts from",
        "* layout/blocks/combiner_sampler/combiner_sampler.gds and reuses everything",
        "* else byte for byte on both sides.",
        "*",
        "* rn1/rn2 stand in for the two ring outputs: deterministic logic steps, not",
        "* oscillators. Every driven input is a 0/1 schedule (l* sources) scaled by",
        "* the corner's own vdd, so a step is full-swing at every supply corner. The",
        "* *n monitors are supply-normalised copies of DUT nodes; they draw no current.",
        "",
        f'.include "{DUT_FILE}"',
        "",
        "* switches design.ngspice sets (its values, verbatim)",
        ".param sw_stat_global=0 sw_stat_mismatch=0 mc_skew=3 res_mc_skew=3 cap_mc_skew=3 fnoicor=0",
        "",
        "vsupply vdd 0 dc 3.3",
        "vvss vss 0 dc 0",
        "vvsubs vsubs 0 dc 0",
        "",
        f"vlrn1 lrn1 0 pwl({_pwl([(t, a) for t, a, _b in INPUTS])})",
        f"vlrn2 lrn2 0 pwl({_pwl([(t, b) for t, _a, b in INPUTS])})",
        f"vlclk lclk 0 pwl({_pwl(_clk_points())})",
        f"vlrst lrst 0 pwl({_pwl(RESET)})",
        "brn1 rn1 0 v='v(vdd)*v(lrn1)'",
        "brn2 rn2 0 v='v(vdd)*v(lrn2)'",
        "bclk clk 0 v='v(vdd)*v(lclk)'",
        "brst rst_n 0 v='v(vdd)*v(lrst)'",
        "",
        f"xdut {' '.join(XDUT_PORTS)} combiner_sampler",
        "",
        "bclkn clkn 0 v='v(clk)/v(vdd)'",
        "brst_nn rst_nn 0 v='v(rst_n)/v(vdd)'",
        *[f"b{n}n {n}n 0 v='v({n})/v(vdd)'" for n in monitors],
        "",
    ]
    return "\n".join(lines)


def render_request() -> dict:
    exp = expected()
    measurements = []
    for name, ts, nodes in SAMPLES:
        for n in nodes:
            row = f"{name}_{n}"
            want = exp[row]
            measurements.append({
                "name": row,
                "spice": f".meas tran {row} find v({n}n) at={ts:g}n",
                "unit": "V/V",
                "limits": {"min": HIGH_MIN} if want else {"max": LOW_MAX},
            })
    for name, spice in TIMING_ROWS:
        measurements.append({"name": name, "spice": spice, "unit": "s"})
    return {
        "netlist": TESTBENCH.name,
        "engine": "ngspice",
        "models": {"pdk": "gf180mcuD", "lib": "libs.tech/ngspice/sm141064.ngspice"},
        "corners": {
            "process": [
                {"name": "tt", "sections": ["typical", "bjt_typical", "diode_typical", "res_typical", "moscap_typical", "mimcap_typical"]},
                {"name": "ff", "sections": ["ff", "bjt_ff", "diode_ff", "res_ff", "moscap_ff", "mimcap_ff"]},
                {"name": "ss", "sections": ["ss", "bjt_ss", "diode_ss", "res_ss", "moscap_ss", "mimcap_ss"]},
            ],
            "supply_v": {"vsupply": [2.97, 3.3, 3.63]},
            "temperature_c": [-40, 27, 125],
        },
        "analysis": {"kind": "tran", "args": f"10p {STOP:g}n"},
        "measurements": measurements,
        "options": {"timeout_s": 900, "keep_artifacts": False, "waveforms": False},
    }


def render_request_text() -> str:
    return json.dumps(render_request(), indent=2) + "\n"


def contract_rows() -> dict[str, dict]:
    """name -> {"min"/"max"} for every limited row, from the committed request."""
    req = json.loads(REQUEST.read_text())
    return {m["name"]: m["limits"] for m in req["measurements"] if m.get("limits")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--table", action="store_true")
    args = ap.parse_args(argv)
    tb, req = render_testbench(), render_request_text()
    if args.table:
        exp = expected()
        for name, ts, nodes in SAMPLES:
            print(f"{name:16s} t={ts:6g} ns  " + "  ".join(f"{n}={exp[f'{name}_{n}']}" for n in nodes))
        return 0
    if args.check:
        stale = [p.name for p, want in ((TESTBENCH, tb), (REQUEST, req))
                 if not p.is_file() or p.read_text() != want]
        if stale:
            print(f"stimulus: {', '.join(stale)} stale; re-run stimulus.py", file=sys.stderr)
            return 1
        print("stimulus: testbench and request are current")
        return 0
    TESTBENCH.write_text(tb)
    REQUEST.write_text(req)
    print(f"stimulus: wrote {TESTBENCH.name} and {REQUEST.name} ({len(json.loads(req)['measurements'])} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
