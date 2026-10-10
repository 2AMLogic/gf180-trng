#!/usr/bin/env python3
"""Active power of the shipped per-ring liveness samplers (issue #463).

    python3 sim/tools/liveness_sampler_power.py plan             # declared grid, method, runtime note
    python3 sim/tools/liveness_sampler_power.py emit             # (re)write the committed request
    python3 sim/tools/liveness_sampler_power.py emit --check     # fail if it drifted from the grid
    python3 sim/tools/liveness_sampler_power.py run --outdir DIR # OPT-IN: one klt sim submit
    python3 sim/tools/liveness_sampler_power.py analyze REPORT [--json]
    python3 sim/tools/liveness_sampler_power.py record REPORT... [--note TEXT]   # mint append-only records

What this is
------------
``design/sampler_core.spice`` instantiates four ``sampler_dff`` cells: ``xsb``
(raw bit), ``xsv`` (raw valid, D tied high) and the DR-0016 per-ring liveness
samplers ``xsr1``/``xsr2`` whose D inputs are the BUFFERED ring outputs
``ro1``/``ro2``. ``power_rollup.py`` accounted for the first two only. The deck
``sim/tb/sampler-core-liveness-active/`` puts every flop on its own supply
branch next to an in-run control array without the ``xsr`` taps, and records raw
branch charges over four ring periods per PVT point. This module turns those raw
charges into the terms the ledger needs, with the arithmetic in code rather than
in ``.meas`` expressions so it can be unit-tested.

Terms (all per PVT point, V = the unit's supply):

    Q_d1 = Q(xsr1) - Q(xsv)      ring-1 data charge, 2 * N_PER transitions
    Q_d2 = Q(xsr2) - Q(xsv)      ring-2 data charge (xsv read in ring 2's window)
    I_data  = Q_d1 / W1 + Q_d2 / W2
    I_clk   = 2 * f_clk * q_clk                 q_clk = one clock-cycle charge
    P_live  = V * (I_data + I_clk)              the flops themselves
    dP_load = V * [(I_r1 + I_r2 + I_tree) - (I_r1c + I_r2c + I_treec)]
                                                 what the taps do to the array

``xsv`` is a pure clock-cycle load (D tied high), so subtracting its window
charge from ``xsr``'s removes the clock term INSIDE the run, over the same
window and clock phases. That leaves ``xsr``'s data-driven charge. ``q_clk``
for the ledger's clock term is taken from ``sampler-dff-active-current``'s
directly measured one-period charge (the same value ``power_rollup.py`` uses for
``xsb``/``xsv``) so a fractional clock cycle in the window never enters it; the
in-run per-cycle estimate is reported only as a cross-check.

Why ``dP_load`` is a separate, signed term: the array records the ledger already
reads (``ro-array-core-pvt-q``) were taken WITHOUT the ``xsr`` taps, so the
taps' extra load on ``ro1``/``ro2`` and the buffers is not in them. The control
array in the same run isolates exactly that delta. It is added to ``P_array``'s
side of the ledger, never folded into ``P_live``, so neither is counted twice.

Nothing here relaxes a spec target or changes DR-0016's status (Proposed); this
measures circuitry the netlist already contains. The simulations go to the batch
fleet through ``klt sim`` -- never to a hand-rolled local loop.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import platform
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import report as _report  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
TB_DIR = REPO_ROOT / "sim" / "tb" / "sampler-core-liveness-active"
DECK = "tb_sampler_core_liveness_active.sp"
REQUEST_NAME = "request-grid.json"

# --------------------------------------------------------------------------
# Declared grid (chosen before any run)
# --------------------------------------------------------------------------

PROCESS_SECTIONS = {
    "tt": ["typical", "bjt_typical", "diode_typical", "res_typical", "moscap_typical", "mimcap_typical"],
    "ff": ["ff", "bjt_ff", "diode_ff", "res_ff", "moscap_ff", "mimcap_ff"],
    "ss": ["ss", "bjt_ss", "diode_ss", "res_ss", "moscap_ss", "mimcap_ss"],
}
PROCESSES = ("tt", "ff", "ss")
TEMPS_C = (-40, 27, 125)
SUPPLIES_V = (2.97, 3.30, 3.63)

TSTEP_S = 5e-12
TSTOP_S = 120e-9
#: Rising mid-supply crossings that open and close the charge window (the same
#: 2nd..6th convention as sim/tb/ro-array-core-pvt-q/), i.e. four ring periods.
RISE_A, RISE_B = 2, 6
N_PER = RISE_B - RISE_A
#: The deck's local clock period (see the deck header: not DR-0012's 1 MHz).
TCLK_DECK_S = 10e-9

#: Sample-clock rates the ledger is evaluated at: DR-0003's ratified 1 MHz and
#: a half-rate point so the rate dependence of the clock term is visible. The
#: data term is set by the ring rates and does not move with either.
DECLARED_RATES_HZ = (1.0e6, 5.0e5)

# Raw measurement names ------------------------------------------------------
#: (node, window) pairs read at the window's two crossings. Window "1"/"2" are
#: the tapped array's ring 1/ring 2; "c1"/"c2" the control array's.
CHARGES = (
    ("q1", "1"), ("qt", "1"), ("qsb", "1"), ("qsv", "1"), ("qs1", "1"),
    ("q2", "2"), ("qsv", "2"), ("qs2", "2"),
    ("cq1i", "c1"), ("cqt", "c1"), ("cqsb", "c1"), ("cqsv", "c1"),
    ("cq2i", "c2"),
)
CROSSINGS = (("t1", "ro1", "1"), ("t2", "ro2", "2"), ("ct1", "cro1", "c1"), ("ct2", "cro2", "c2"))


def measurements() -> list[dict]:
    m: list[dict] = []

    def add(name: str, spice: str, unit: str) -> None:
        m.append({"name": name, "spice": spice, "unit": unit})

    ring_node = {"1": "ro1", "2": "ro2", "c1": "cro1", "c2": "cro2"}
    for win, node in ring_node.items():
        tag = "t" + win
        for ab, k in (("a", RISE_A), ("b", RISE_B)):
            add(f"{tag}{ab}", f".meas tran {tag}{ab} when v({node})=v(vth) rise={k}", "s")
    for node, win in CHARGES:
        ring = ring_node[win]
        for ab, k in (("a", RISE_A), ("b", RISE_B)):
            add(f"{node}_{win}{ab}", f".meas tran {node}_{win}{ab} find v({node}) when v({ring})=v(vth) rise={k}", "V")
    add("ring1_max", ".meas tran ring1_max max v(ro1) from=60n to=118n", "V")
    add("ring1_min", ".meas tran ring1_min min v(ro1) from=60n to=118n", "V")
    add("ring2_max", ".meas tran ring2_max max v(ro2) from=60n to=118n", "V")
    add("ring2_min", ".meas tran ring2_min min v(ro2) from=60n to=118n", "V")
    return m


def parse_only(spec: str) -> tuple[str, int, float]:
    """``tt/27/3.30`` -> ("tt", 27, 3.3); must be a point of the declared grid."""
    try:
        proc, temp, vdd = spec.split("/")
        key = (proc, int(temp), float(vdd))
    except ValueError as exc:
        raise ValueError(f"--only expects PROCESS/TEMP_C/VDD like tt/27/3.30, got {spec!r}") from exc
    if key[0] not in PROCESSES or key[1] not in TEMPS_C or not any(abs(key[2] - v) < 1e-9 for v in SUPPLIES_V):
        raise ValueError(f"{spec!r} is not a point of the declared grid")
    return key


def build_request(only: str | None = None) -> dict:
    """The declared request; ``only`` restricts it to ONE grid point (a debug
    probe, which is the only thing allowed to run locally on a shared worker)."""
    req = _build_full_request()
    if only is None:
        return req
    proc, temp, vdd = parse_only(only)
    req["corners"]["process"] = [x for x in req["corners"]["process"] if x["name"] == proc]
    req["corners"]["temperature_c"] = [temp]
    req["corners"]["supply_v"] = {"vsupply": [vdd]}
    req["_comment"] = f"issue #463 single-point probe {only}: 1 unit. Generated; not committed."
    return req


def _build_full_request() -> dict:
    return {
        "_comment": (
            f"issue #463 liveness-sampler active-power request: {len(PROCESSES) * len(TEMPS_C) * len(SUPPLIES_V)} "
            "units. Generated by sim/tools/liveness_sampler_power.py; do not edit by hand "
            "(`emit --check` fails if this drifts)."
        ),
        "netlist": DECK,
        "engine": "ngspice",
        "models": {"pdk": "gf180mcuD", "lib": "libs.tech/ngspice/sm141064.ngspice"},
        "corners": {
            "process": [{"name": p, "sections": PROCESS_SECTIONS[p]} for p in PROCESSES],
            "supply_v": {"vsupply": list(SUPPLIES_V)},
            "temperature_c": list(TEMPS_C),
        },
        "analysis": {"kind": "tran", "args": f"{TSTEP_S * 1e12:g}p {TSTOP_S * 1e9:g}n"},
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


def request_path() -> Path:
    return TB_DIR / REQUEST_NAME


def n_units() -> int:
    return len(PROCESSES) * len(TEMPS_C) * len(SUPPLIES_V)


# --------------------------------------------------------------------------
# Arithmetic (pure; unit-tested)
# --------------------------------------------------------------------------

CQ = 1e-9  # the deck's integrator capacitor, farads


class DerivationError(ValueError):
    """A required raw measurement is missing or non-physical."""


def _need(v: dict, *names: str) -> None:
    missing = [n for n in names if n not in v]
    if missing:
        raise DerivationError(f"missing raw measurements: {', '.join(missing)}")


def charge(v: dict, node: str, win: str) -> float:
    """Charge delivered on a branch over a window, coulombs (positive).

    The 0 V sense sources report charge INTO the branch as a negative number
    under ngspice's branch-current convention (design/README.md, 'Reading the
    recorded currents'), so the sign is flipped here once.
    """
    a, b = f"{node}_{win}a", f"{node}_{win}b"
    _need(v, a, b)
    return -CQ * (v[b] - v[a])


def window(v: dict, win: str) -> float:
    ta, tb = f"t{win}a", f"t{win}b"
    _need(v, ta, tb)
    w = v[tb] - v[ta]
    if not w > 0:
        raise DerivationError(f"window {win}: non-positive length {w!r}")
    return w


def derive(v: dict, vdd: float, q_clk_c: float | None = None) -> dict:
    """Ledger terms for one PVT point from the raw measurements ``v``.

    ``q_clk_c`` is the one-period clock charge from sampler-dff-active-current
    for the same corner (the ledger's clock-term source). When absent the
    in-run per-cycle estimate is used instead and ``clk_source`` says so.
    """
    w1, w2 = window(v, "1"), window(v, "2")
    cw1, cw2 = window(v, "c1"), window(v, "c2")
    qs1, qs2 = charge(v, "qs1", "1"), charge(v, "qs2", "2")
    qsv1, qsv2 = charge(v, "qsv", "1"), charge(v, "qsv", "2")
    qd1, qd2 = qs1 - qsv1, qs2 - qsv2
    n_trans = 2 * N_PER
    i_data = qd1 / w1 + qd2 / w2
    # In-run cross-check of the clock-cycle charge: xsv's window charge over the
    # window's (possibly fractional) number of deck clock periods.
    q_clk_run = 0.5 * (qsv1 / (w1 / TCLK_DECK_S) + qsv2 / (w2 / TCLK_DECK_S))
    clk_source = "sampler-dff-active-current" if q_clk_c is not None else "in-run xsv (fractional-cycle windows)"
    q_clk = q_clk_c if q_clk_c is not None else q_clk_run

    i_arr_tapped = charge(v, "q1", "1") / w1 + charge(v, "q2", "2") / w2 + charge(v, "qt", "1") / w1
    i_arr_ctl = charge(v, "cq1i", "c1") / cw1 + charge(v, "cq2i", "c2") / cw2 + charge(v, "cqt", "c1") / cw1
    out = {
        "vdd": vdd,
        "w1_s": w1, "w2_s": w2, "cw1_s": cw1, "cw2_s": cw2,
        "f_r1_hz": N_PER / w1, "f_r2_hz": N_PER / w2,
        "f_r1_ctl_hz": N_PER / cw1, "f_r2_ctl_hz": N_PER / cw2,
        "q_xsr1_c": qs1, "q_xsr2_c": qs2, "q_xsv1_c": qsv1, "q_xsv2_c": qsv2,
        "q_data1_c": qd1, "q_data2_c": qd2,
        "q_per_transition1_c": qd1 / n_trans, "q_per_transition2_c": qd2 / n_trans,
        "i_data_a": i_data,
        "q_clk_c": q_clk, "q_clk_run_c": q_clk_run, "clk_source": clk_source,
        "i_arr_tapped_a": i_arr_tapped, "i_arr_ctl_a": i_arr_ctl,
        "dp_load_w": vdd * (i_arr_tapped - i_arr_ctl),
        "p_live_data_w": vdd * i_data,
    }
    for f in DECLARED_RATES_HZ:
        out[f"p_live_w@{f:g}"] = live_power(out, f)
    return out


def live_power(d: dict, f_clk: float) -> float:
    """Liveness-sampler power at sample-clock rate ``f_clk`` (the flops only)."""
    return d["vdd"] * (d["i_data_a"] + 2.0 * f_clk * d["q_clk_c"])


def checks(d: dict) -> list[str]:
    """Sanity problems with one derived point; empty means it is usable."""
    bad = []
    if d["q_data1_c"] <= 0 or d["q_data2_c"] <= 0:
        bad.append("non-positive ring-data charge: xsr is not drawing more than the tied-D xsv")
    if d["q_xsv1_c"] <= 0 or d["q_xsv2_c"] <= 0:
        bad.append("non-positive xsv window charge: the clock never ran")
    qr = d["q_clk_run_c"]
    if d["q_clk_c"] > 0 and qr > 0 and not (0.2 < qr / d["q_clk_c"] < 5):
        bad.append(f"in-run clock charge {qr:.3e} C disagrees with the record's {d['q_clk_c']:.3e} C by >5x")
    return bad


# --------------------------------------------------------------------------
# Report reading
# --------------------------------------------------------------------------


def _vals(corner: dict) -> dict[str, float]:
    return {x["name"]: x["value"] for x in corner.get("measurements", []) if x.get("value") is not None}


def analyse_report(report: dict, q_clk_by_corner: dict[str, float] | None = None) -> list[dict]:
    rows = []
    for c in report.get("corners", []):
        v = _vals(c)
        sv = c.get("supply_v", {})
        vdd = float(sv.get("vsupply", 3.3))
        key = f"{c.get('process')}/{c.get('temperature_c')}/{vdd:.2f}"
        row = {"corner": key, "process": c.get("process"), "temperature_c": c.get("temperature_c"),
               "vdd": vdd, "status": c.get("status")}
        try:
            qc = (q_clk_by_corner or {}).get(key)
            row.update(derive(v, vdd, qc))
            row["problems"] = checks(row)
            row["verdict"] = "OK" if not row["problems"] else "SUSPECT"
        except DerivationError as exc:
            row["problems"] = [str(exc)]
            row["verdict"] = "UNMEASURED"
        rows.append(row)
    return rows


def _uw(x: float) -> str:
    return f"{x * 1e6:8.3f} uW"


def table(rows: list[dict]) -> str:
    out = ["| corner | verdict | f_r1 MHz | f_r2 MHz | q/trans fC | P_live 1MHz | P_live 500kHz | dP_load |",
           "|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["process"], r["temperature_c"], r["vdd"])):
        if r["verdict"] == "UNMEASURED":
            out.append(f"| {r['corner']} | UNMEASURED | | | | | | |")
            continue
        out.append(
            f"| {r['corner']} | {r['verdict']} | {r['f_r1_hz'] / 1e6:.1f} | {r['f_r2_hz'] / 1e6:.1f} |"
            f" {0.5 * (r['q_per_transition1_c'] + r['q_per_transition2_c']) * 1e15:.2f} |"
            f" {_uw(r['p_live_w@1e+06'])} | {_uw(r['p_live_w@500000'])} | {_uw(r['dp_load_w'])} |"
        )
    return "\n".join(out)


def plan_text() -> str:
    return "\n".join([
        "liveness-sampler active power (issue #463)",
        f"  deck        : sim/tb/sampler-core-liveness-active/{DECK}",
        f"  units       : {n_units()} = {len(PROCESSES)} MOS corners {PROCESSES} x {len(TEMPS_C)} temps {TEMPS_C} C"
        f" x {len(SUPPLIES_V)} supplies {SUPPLIES_V} V",
        f"  window      : ring crossings {RISE_A}..{RISE_B} ({N_PER} ring periods), tstop {TSTOP_S * 1e9:g} ns",
        f"  deck clock  : {TCLK_DECK_S * 1e9:g} ns (local; per-event charges, rate applied by the ledger)",
        f"  rates       : {', '.join(f'{f:g} Hz' for f in DECLARED_RATES_HZ)}",
        "  backend     : batch via klt sim (KLT_SIM_BACKEND=batch); never a local loop",
    ])


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def cmd_emit(check: bool) -> int:
    path, text = request_path(), render(build_request())
    if check:
        if not path.exists() or path.read_text() != text:
            print(f"DRIFT: {path.relative_to(REPO_ROOT)} does not match the declared grid")
            return 1
        print(f"ok: {path.relative_to(REPO_ROOT)} matches the declared grid ({n_units()} units)")
        return 0
    TB_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


def cmd_run(outdir: str, backend: str, klt_cmd: str, only: str | None = None) -> int:
    if only is not None and backend != "local":
        print("--only is a single-point debug probe and runs with --backend local", file=sys.stderr)
        return 2
    if only is None and backend == "local":
        print("refusing to run the whole grid locally: use --backend batch (shared-host rule), "
              "or --only PROCESS/TEMP/VDD for one probe point", file=sys.stderr)
        return 2
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    stem = "grid" if only is None else "probe-" + only.replace("/", "_")
    report = out / f"{stem}.report.json"
    req = request_path()
    tmp = None
    if only is not None:
        # klt resolves `netlist` relative to the request file, so the restricted
        # request has to sit next to the deck for the duration of the run.
        tmp = TB_DIR / f".{stem}.request.json"
        tmp.write_text(render(build_request(only)))
        req = tmp
    cmd = [*shlex.split(klt_cmd), "sim", str(req), "--backend", backend,
           "-o", str(out / stem), "--format", "json"]
    print("running:", " ".join(cmd))
    try:
        with open(report, "w") as fh, open(out / f"{stem}.stderr.txt", "w") as err:
            rc = subprocess.call(cmd, stdout=fh, stderr=err)
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)
    print(f"klt exit {rc}; report: {report}; stderr: {out / (stem + '.stderr.txt')}")
    return rc


SLUG = "sampler-core-liveness-active"
#: Attempt records (batch refused, runner skew, ...) carry no measurement. Their
#: slug deliberately does not match power_rollup.LIVENESS_GLOB's `-[0-9]` rule, so
#: a record without numbers can never be read as a measured corner.
SLUG_ATTEMPT = "sampler-core-liveness-active-attempt"

#: Result bullets a measured record carries (the ledger and the tests read these).
RECORD_FIELDS = (
    "i_data_a", "dp_load_w", "p_live_data_w", "q_clk_run_c",
    "q_xsr1_c", "q_xsr2_c", "q_xsv1_c", "q_xsv2_c", "q_data1_c", "q_data2_c",
    "q_per_transition1_c", "q_per_transition2_c",
    "f_r1_hz", "f_r2_hz", "f_r1_ctl_hz", "f_r2_ctl_hz",
    "i_arr_tapped_a", "i_arr_ctl_a", "w1_s", "w2_s", "cw1_s", "cw2_s",
)


def _sanitize(text: str) -> str:
    """Strip this host's absolute paths from a raw artifact before it is hashed."""
    return text.replace(str(REPO_ROOT), "<repo>").replace(str(Path.home()), "~")


def _fmt(x: float) -> str:
    return f"{x:.6e}"


def _voltage_label(vdd: float) -> str:
    return _report._voltage_label(vdd, 3.3)


def render_measured(stem: str, row: dict, corner: dict, rep: dict, raw_files: list[tuple[str, str]],
                    now: _dt.datetime, git: dict) -> str:
    env, prov = rep.get("environment", {}), rep.get("provenance", {})
    tb = TB_DIR / DECK
    netlist = REPO_ROOT / "design" / "sampler_core.spice"
    remote = env.get("remote")
    where = (f"fleet job {remote['job_id']}" if remote else "local ngspice (single-point debug probe)")
    lines = [
        "---", f"record: {stem}", f"date: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}", "status: valid", "",
        "testbench:", f"  path: {tb.relative_to(REPO_ROOT)}", f"  sha: {_report.blob_sha(REPO_ROOT, tb)}",
        "netlist:", f"  path: {netlist.relative_to(REPO_ROOT)}", f"  sha: {_report.blob_sha(REPO_ROOT, netlist)}",
        f"repo_commit: {_report.repo_commit_field(git)}", "",
        f"pdk: {prov.get('pdk', {}).get('name', 'gf180mcuD')} @ "
        f"{str(prov.get('pdk', {}).get('version', 'unknown')).replace('open_pdks ', '')}",
        "pdk.models:",
        f"  - ~/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sha256:{env.get('models_lib_sha256')})",
        "", "tool:", f"  klt: {prov.get('klt_version', 'unknown')}",
        f"  ngspice: ngspice-{env.get('engine_version', 'unknown')}",
        f"  platform: {platform.platform()}", "",
        "corner:", f"  process: {row['process']}", f"  voltage: {_voltage_label(row['vdd'])}",
        f"  temperature: {row['temperature_c']}", "",
        "analysis:", "  type: tran (deterministic)", f"  tstop: {TSTOP_S * 1e9:g}n",
        f"  tstep: {TSTEP_S * 1e12:g}p (print step)", "  tmax: n/a", "  noise_params: n/a", "  runs: 1",
        "seeds: n/a (deterministic; no noise sources)", "",
        "raw:", f"  path: sim/records/raw/{stem}/", "  files:",
        *[f"    - {n}  sha256:{h}" for n, h in raw_files],
        f"wall_time: {corner.get('runtime_s', 'n/a')}s", "---", "",
        "## Result", "",
        f"Executed by {where}. Raw branch charges are read at the 2nd and 6th rising ring crossings "
        "(four ring periods); the derived terms below are `sim/tools/liveness_sampler_power.py`'s "
        "arithmetic on them.", "",
    ]
    for k in RECORD_FIELDS:
        lines.append(f"- `{k}`: {_fmt(row[k])}")
    lines += [
        "",
        f"At this corner the shipped liveness samplers cost {row['p_live_data_w'] * 1e6:.3f} uW of "
        "ring-data power (flops only, before the 2*f_clk*q_clk clock term, which the ledger adds from "
        "`sampler-dff-active-current`) and change the array's own supply power by "
        f"{row['dp_load_w'] * 1e6:+.3f} uW (tapped array minus the in-run control).",
        "", "Numbers only. No entropy-rate or spec-compliance claim is made by this record.", "",
        "## How to reproduce", "", "```sh",
        f"python3 sim/tools/liveness_sampler_power.py run --outdir DIR --backend local --only "
        f"{row['process']}/{row['temperature_c']}/{row['vdd']:.2f}",
        f"python3 sim/tools/liveness_sampler_power.py analyze DIR/probe-{row['process']}_{row['temperature_c']}_{row['vdd']:.2f}.report.json",
        "```", "",
        "## Caveats", "",
        "- The clock is a LOCAL 10 ns clock, not the ratified 1 MHz; the term is per-event charge and the "
        "ledger applies the declared rate (see the testbench header).",
        "- The clock charge is removed by in-run subtraction of `xsv` (D tied high); the output-node "
        "charge of `xsr` stays in the data term, which over-states a per-clock-cycle cost: a conservative "
        "direction.",
        "- Pre-layout, schematic-level; one window of four ring periods; no mismatch or noise.",
        "- The raw deck and log have this host's absolute paths replaced by `<repo>` and `~` before hashing.",
        "", "---", "",
        "Written by `sim/tools/liveness_sampler_power.py record`. Append-only: never edit or delete this file.",
        "",
    ]
    return "\n".join(lines)


def render_unmeasured(stem: str, corners: list[dict], rep: dict, raw_files: list[tuple[str, str]],
                      now: _dt.datetime, git: dict, note: str) -> str:
    env, prov = rep.get("environment", {}), rep.get("provenance", {})
    tb = TB_DIR / DECK
    netlist = REPO_ROOT / "design" / "sampler_core.spice"
    remote = env.get("remote") or {}
    codes = sorted({d.get("code", "?") for c in corners for d in c.get("diagnostics", [])})
    runner = sorted({d.get("runner_code") for c in corners for d in c.get("diagnostics", []) if d.get("runner_code")})
    lines = [
        "---", f"record: {stem}", f"date: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}", "status: valid", "",
        "testbench:", f"  path: {tb.relative_to(REPO_ROOT)}", f"  sha: {_report.blob_sha(REPO_ROOT, tb)}",
        "netlist:", f"  path: {netlist.relative_to(REPO_ROOT)}", f"  sha: {_report.blob_sha(REPO_ROOT, netlist)}",
        f"repo_commit: {_report.repo_commit_field(git)}", "",
        f"pdk: gf180mcuD @ {str(prov.get('pdk', {}).get('version', 'unknown')).replace('open_pdks ', '')}",
        "tool:", f"  klt: {prov.get('klt_version', 'unknown')} (client)",
        f"  platform: {platform.platform()}", "",
        "corner:", f"  process: {', '.join(PROCESSES)} -- NOT SIMULATED",
        f"  voltage: {' / '.join(f'{v:.2f}' for v in SUPPLIES_V)} V -- NOT SIMULATED",
        f"  temperature: {' / '.join(str(x) for x in TEMPS_C)} -- NOT SIMULATED", "",
        "analysis:", "  type: tran (deterministic)", f"  tstop: {TSTOP_S * 1e9:g}n",
        f"  tstep: {TSTEP_S * 1e12:g}p (print step)", "  runs: 0 (nothing executed)",
        "seeds: n/a (deterministic; no noise sources)", "",
        "raw:", f"  path: sim/records/raw/{stem}/", "  files:",
        *[f"    - {n}  sha256:{h}" for n, h in raw_files],
        "wall_time: n/a (batch submission failed)", "---", "",
        "## Result", "",
        f"**Outcome: UNMEASURED.** {len(corners)} of {n_units()} grid units were submitted to the batch "
        "fleet and none produced a measurement, so this record carries no measurement and no pass.", "",
        f"- fleet job: `{remote.get('job_id', 'n/a')}` ({remote.get('instance_type', 'n/a')}, "
        f"{remote.get('lifecycle', 'n/a')}), diagnostics `{', '.join(codes)}`"
        + (f", runner code `{', '.join(runner)}`" if runner else ""),
        f"- runner klt {remote.get('runner_klt_version', 'n/a')} vs client {remote.get('client_klt_version', 'n/a')} "
        f"(`runner_compatibility: {remote.get('runner_compatibility', 'n/a')}`)",
        "", note.strip(), "",
        "The grid was **not** run as a local loop (shared-worker rule). Every corner not covered by a "
        "`valid` measured record of this family is an explicit gap in `power_rollup.py`.", "",
        "## How to reproduce", "", "```sh",
        "python3 sim/tools/liveness_sampler_power.py emit --check",
        "python3 sim/tools/liveness_sampler_power.py run --outdir DIR --backend batch", "```", "",
        "---", "",
        "Written by `sim/tools/liveness_sampler_power.py record`. Append-only: never edit or delete this file.",
        "",
    ]
    return "\n".join(lines)


def cmd_record(paths: list[str], note: str, records_dir: Path | None = None) -> int:
    """Mint append-only records from klt reports: one measured record per usable
    corner, and one UNMEASURED record for the units that did not produce data."""
    records_dir = records_dir or REPO_ROOT / "sim" / "records"
    now = _dt.datetime.now(_dt.timezone.utc)
    date = now.strftime("%Y-%m-%d")
    git = _report.git_provenance(REPO_ROOT)
    for path in paths:
        rp = Path(path)
        rep = json.loads(rp.read_text())
        rows = analyse_report(rep)
        good = [(r, c) for r, c in zip(rows, rep.get("corners", [])) if r["verdict"] == "OK"]
        bad = [c for r, c in zip(rows, rep.get("corners", [])) if r["verdict"] != "OK"]
        stems = _report.reserve_record_stems(records_dir, date, SLUG, len(good)) if good else []
        for (row, corner), stem in zip(good, stems):
            raw = records_dir / _report.RAW_DIRNAME / stem
            files: list[tuple[str, str]] = []
            for name, key in (("corner.cir", "deck"), ("ngspice.log", "log")):
                src = (corner.get("artifacts") or {}).get(key)
                if src and Path(src).is_file():
                    (raw / name).write_text(_sanitize(Path(src).read_text(errors="replace")))
                    files.append((name, _report.sha256_file(raw / name)))
            sl = {"environment": rep.get("environment"), "provenance": rep.get("provenance"), "corner": corner}
            (raw / "report-unit.json").write_text(_sanitize(json.dumps(sl, indent=1)) + "\n")
            files.append(("report-unit.json", _report.sha256_file(raw / "report-unit.json")))
            (records_dir / f"{stem}.md").write_text(render_measured(stem, row, corner, rep, files, now, git))
            print(f"wrote {stem}.md  ({row['corner']})")
        if bad:
            stem = _report.reserve_record_stems(records_dir, date, SLUG_ATTEMPT, 1)[0]
            raw = records_dir / _report.RAW_DIRNAME / stem
            slim = dict(rep)
            slim["corners"] = [{k: v for k, v in c.items() if k != "measurements"} for c in bad]
            (raw / "report-errored.json").write_text(_sanitize(json.dumps(slim, indent=1)) + "\n")
            files = [("report-errored.json", _report.sha256_file(raw / "report-errored.json"))]
            (records_dir / f"{stem}.md").write_text(render_unmeasured(stem, bad, rep, files, now, git, note))
            print(f"wrote {stem}.md  (UNMEASURED, {len(bad)} units)")
    return 0


def cmd_analyze(paths: list[str], as_json: bool) -> int:
    rows: list[dict] = []
    for p in paths:
        rows += analyse_report(json.loads(Path(p).read_text()))
    if as_json:
        print(json.dumps(rows, indent=1))
    else:
        print(table(rows))
        bad = [r for r in rows if r["verdict"] != "OK"]
        print(f"\n{len(rows) - len(bad)}/{len(rows)} units usable"
              + ("" if not bad else "; not usable: " + ", ".join(f"{r['corner']} ({r['verdict']})" for r in bad)))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    e = sub.add_parser("emit")
    e.add_argument("--check", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("--outdir", required=True)
    r.add_argument("--only", help="ONE grid point PROCESS/TEMP_C/VDD (e.g. tt/27/3.30): a local debug probe")
    r.add_argument("--backend", default="batch", choices=("batch", "local"))
    r.add_argument("--klt", default="klt", dest="klt_cmd",
                   help="klt command; e.g. 'uvx --from klayout-tools==X.Y.Z klt'")
    rc_ = sub.add_parser("record", help="mint append-only records from klt reports")
    rc_.add_argument("reports", nargs="+")
    rc_.add_argument("--note", default="", help="prose appended to an UNMEASURED record")
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
        return cmd_run(args.outdir, args.backend, args.klt_cmd, args.only)
    if args.cmd == "record":
        return cmd_record(args.reports, args.note)
    return cmd_analyze(args.reports, args.json)


if __name__ == "__main__":
    sys.exit(main())
