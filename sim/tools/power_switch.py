#!/usr/bin/env python3
"""Batch-fleet run, record ingestion and arithmetic for the digital power switch (issue #707).

    python3 sim/tools/power_switch.py plan
    python3 sim/tools/power_switch.py emit [--check]
    python3 sim/tools/power_switch.py run --outdir DIR [--backend batch] [--only PROCESS/TEMP/VDD]
    python3 sim/tools/power_switch.py record DIR/grid.report.json [--note TEXT]
    python3 sim/tools/power_switch.py analyze DIR/grid.report.json [--json]
    python3 sim/tools/power_switch.py summarize

``sim/tb/power-switch/tb_power_switch.sp`` holds four groups of PMOS-header instances (design/
power_switch.spice) in one deterministic transient run per PVT point: on-resistance and
droop at four widths and two DC loads (group R), off-state leakage at four widths and in a
leakage-equivalent digital load (group L), and wake inrush and settling at two rail
capacitances and two sleep rise times (group W). The deck's header lists every load and why.

The declared grid is the harness's five MOS corners x three temperatures x three supplies
(45 units). It is submitted to the batch fleet through ``klt sim`` and never swept locally on
a shared worker (``sim/harness/klt_request.py``); ``--only`` runs one point locally as a debug
probe. This tool turns each unit's raw readings into the quantities the sizing report cites
(on-resistance, droop fraction, I^2 R loss, off leakage, inrush, settling), with the
arithmetic here rather than in ``.meas`` expressions so it can be unit-tested.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness import klt_request as _kreq  # noqa: E402
from harness import record_mint as _mint  # noqa: E402
from harness import report as _report  # noqa: E402
import _record_parsing as _rp  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
TB_DIR = REPO_ROOT / "sim" / "tb" / "power-switch"
DECK = "tb_power_switch.sp"
REQUEST_NAME = "request-grid.json"
SLUG = "power-switch"
SLUG_ATTEMPT = "power-switch-attempt"

# --------------------------------------------------------------------------
# Declared grid (chosen before any run)
# --------------------------------------------------------------------------

PROCESS_SECTIONS = {
    "tt": ["typical", "bjt_typical", "diode_typical", "res_typical", "moscap_typical", "mimcap_typical"],
    "ff": ["ff", "bjt_ff", "diode_ff", "res_ff", "moscap_ff", "mimcap_ff"],
    "ss": ["ss", "bjt_ss", "diode_ss", "res_ss", "moscap_ss", "mimcap_ss"],
    "fs": ["fs", "bjt_typical", "diode_typical", "res_typical", "moscap_typical", "mimcap_typical"],
    "sf": ["sf", "bjt_typical", "diode_typical", "res_typical", "moscap_typical", "mimcap_typical"],
}
PROCESSES = ("tt", "ff", "ss", "fs", "sf")
TEMPS_C = (-40, 27, 125)
SUPPLIES_V = (2.97, 3.30, 3.63)
TSTEP_S = 100e-12
TSTOP_S = 3.5e-6
T_STATIC_S = 2.9e-6
T_WAKE_S = 100e-9

#: Total switch widths in the sweep (um), keyed by the finger count of the 10 um finger.
WIDTH_UM = {1: 100, 2: 200, 4: 400, 8: 800}
#: DC loads of group R (A): label -> current. See the deck header for the sources.
LOADS_A = {"a": 96.7e-6, "b": 1.893e-3}
WAKE_CASES = {1: (50e-12, 10e-9), 2: (200e-12, 10e-9), 3: (50e-12, 1e-6), 4: (200e-12, 1e-6)}
SELECTED_WIDTH_UM = 400


def wake_tag(cap: float, trf: float) -> str:
    """Lower-case field suffix: record keys are matched by ``[a-z0-9_]+``."""
    return f"{cap * 1e12:g}pf_{trf * 1e9:g}ns"

#: Fleet shards for the 45 units (15 each).
HOSTS = 3
#: The off-state leakage the selected switch may show at any grid corner: a tenth of the
#: `< 1 uA` idle row, so the switch itself stays a small fraction of what it protects.
OFF_LEAKAGE_LIMIT_A = 100e-9
#: The 33 mV yardstick of sim/characterization-digital-supply-ir-drop.md (1 % of 3.3 V).
DROOP_BUDGET_V = 0.033


def measurements() -> list[dict]:
    m: list[dict] = []

    def add(name: str, spice: str, unit: str) -> None:
        m.append({"name": name, "spice": spice, "unit": unit})

    at = f"{T_STATIC_S * 1e6:g}u"
    for k in WIDTH_UM:
        for ld in LOADS_A:
            add(f"droop_{k}{ld}", f".meas tran droop_{k}{ld} find par('v(vdd)-v(vr{k}{ld})') at={at}", "V")
        add(f"ileak_{k}", f".meas tran ileak_{k} find i(vl{k}) at={at}", "A")
    add("i_stack", f".meas tran i_stack find i(vwst) at={at}", "A")
    add("v_stack", f".meas tran v_stack find v(vst) at={at}", "V")
    add("i_ungated", f".meas tran i_ungated find i(vwun) at={at}", "A")
    for k in WAKE_CASES:
        add(f"ipk_w{k}", f".meas tran ipk_w{k} max i(vww{k}) from=90n to={TSTOP_S * 1e6:g}u", "A")
        add(f"t95_w{k}", f".meas tran t95_w{k} when v(c{k})=0 rise=1", "s")
        add(f"vfin_w{k}", f".meas tran vfin_w{k} find v(vw{k}) at={TSTOP_S * 1e6 - 0.1:g}u", "V")
    return m


def parse_only(spec: str) -> tuple[str, int, float]:
    try:
        proc, temp, vdd = spec.split("/")
        key = (proc, int(temp), round(float(vdd), 2))
    except ValueError:
        raise ValueError(f"{spec!r} is not PROCESS/TEMP_C/VDD") from None
    if key[0] not in PROCESSES or key[1] not in TEMPS_C or key[2] not in SUPPLIES_V:
        raise ValueError(f"{spec!r} is not a point of the declared grid")
    return key


def _build_full_request() -> dict:
    return {
        "_comment": (
            f"issue #707 power-switch request: {n_units()} units. Generated by "
            "sim/tools/power_switch.py; do not edit by hand (`emit --check` fails if this drifts)."
        ),
        "netlist": DECK,
        "engine": "ngspice",
        "models": {"pdk": "gf180mcuD", "lib": "libs.tech/ngspice/sm141064.ngspice"},
        "corners": {
            "process": [{"name": p, "sections": PROCESS_SECTIONS[p]} for p in PROCESSES],
            "supply_v": {"vsup": list(SUPPLIES_V)},
            "temperature_c": list(TEMPS_C),
        },
        "analysis": {"kind": "tran", "args": f"{TSTEP_S * 1e12:g}p {TSTOP_S * 1e6:g}u"},
        "measurements": measurements(),
        # three shard jobs: the whole-job ceiling is checked against the serial sum of
        # the units' timeouts, and a unit here runs in about a second. `num_threads=1`
        # is load-bearing on the fleet: without it the units of this small circuit did not
        # finish in 120 s and every one timed out (issue #707; klayout-tools #3619).
        "remote": {"hosts": HOSTS},
        "options": {
            "timeout_s": 120,
            "keep_artifacts": True,
            "waveforms": False,
            "ngspice_init": ["set measureprec=12", "set num_threads=1"],
        },
    }


def build_request(only: str | None = None) -> dict:
    """The declared request; ``only`` restricts it to ONE grid point (a debug probe,
    the only thing allowed to run locally on a shared worker)."""
    req = _build_full_request()
    if only is None:
        return req
    proc, temp, vdd = parse_only(only)
    req["corners"]["process"] = [x for x in req["corners"]["process"] if x["name"] == proc]
    req["corners"]["temperature_c"] = [temp]
    req["corners"]["supply_v"] = {"vsup": [vdd]}
    req["_comment"] = f"issue #707 single-point probe {only}: 1 unit. Generated; not committed."
    return req


def render(req: dict) -> str:
    return json.dumps(req, indent=1) + "\n"


def request_path() -> Path:
    return TB_DIR / REQUEST_NAME


def n_units() -> int:
    return len(PROCESSES) * len(TEMPS_C) * len(SUPPLIES_V)


# --------------------------------------------------------------------------
# Arithmetic (pure; unit-tested)
# --------------------------------------------------------------------------


class DerivationError(ValueError):
    pass


def _need(v: dict, *names: str) -> None:
    missing = [n for n in names if n not in v]
    if missing:
        raise DerivationError("readings missing: " + ", ".join(missing))


def derive(v: dict, vdd: float) -> dict:
    """Sizing quantities from one unit's raw readings and its supply ``vdd``."""
    out: dict = {"vdd_v": vdd}
    for k, w in WIDTH_UM.items():
        for ld, i_a in LOADS_A.items():
            _need(v, f"droop_{k}{ld}")
            d = v[f"droop_{k}{ld}"]
            tag = f"{w}um_{ld}"
            out[f"droop_v_{tag}"] = d
            out[f"droop_pct_{tag}"] = d / vdd * 100.0
            out[f"ron_ohm_{tag}"] = d / i_a
            out[f"p_loss_w_{tag}"] = d * i_a
        _need(v, f"ileak_{k}")
        out[f"ileak_a_{w}um"] = v[f"ileak_{k}"]
    _need(v, "i_stack", "v_stack", "i_ungated")
    out["i_stack_a"] = v["i_stack"]
    out["v_stack_v"] = v["v_stack"]
    out["i_ungated_a"] = v["i_ungated"]
    out["stack_reduction_x"] = v["i_ungated"] / v["i_stack"] if v["i_stack"] > 0 else float("inf")
    for k, (cap, trf) in WAKE_CASES.items():
        _need(v, f"ipk_w{k}", f"t95_w{k}", f"vfin_w{k}")
        tag = wake_tag(cap, trf)
        out[f"ipk_a_{tag}"] = v[f"ipk_w{k}"]
        out[f"t_settle_s_{tag}"] = v[f"t95_w{k}"] - T_WAKE_S
        out[f"vfin_v_{tag}"] = v[f"vfin_w{k}"]
    return out


def checks(row: dict) -> list[str]:
    """Plausibility failures. A unit with any is SUSPECT and never read as a measurement."""
    bad = []
    vdd = row["vdd_v"]
    for key, val in row.items():
        if key.startswith("droop_v_") and not 0.0 < val < 0.5 * vdd:
            bad.append(f"{key} = {val:.4g} V outside (0, vdd/2)")
        if key.startswith("ileak_a_") and not val > 0:
            bad.append(f"{key} = {val:.4g} A is not positive")
        if key.startswith("vfin_v_") and val < 0.95 * vdd:
            bad.append(f"{key} = {val:.4g} V: rail did not wake")
        if key.startswith("t_settle_s_") and not val > 0:
            bad.append(f"{key} = {val:.4g} s is not positive")
    if not row["i_stack_a"] > 0:
        bad.append("i_stack_a is not positive")
    return bad


def _vals(corner: dict) -> dict[str, float]:
    return {x["name"]: x["value"] for x in corner.get("measurements", []) if x.get("value") is not None}


def analyse_report(report: dict) -> list[dict]:
    rows = []
    for c in report.get("corners", []):
        v = _vals(c)
        vdd = float(c.get("supply_v", {}).get("vsup", 3.3))
        key = f"{c.get('process')}/{c.get('temperature_c')}/{vdd:.2f}"
        row = {"corner": key, "process": c.get("process"), "temperature_c": c.get("temperature_c"),
               "vdd": vdd, "status": c.get("status")}
        try:
            row.update(derive(v, vdd))
            row["problems"] = checks(row)
            row["verdict"] = "OK" if not row["problems"] else "SUSPECT"
        except DerivationError as exc:
            row["problems"] = [str(exc)]
            row["verdict"] = "UNMEASURED"
        rows.append(row)
    return rows


def table(rows: list[dict]) -> str:
    w = SELECTED_WIDTH_UM
    head = (f"{'corner':<14} {'ron@' + str(w) + 'um':>11} {'droop B mV':>11} {'leak ' + str(w) + 'um nA':>13} "
            f"{'idle stack nA':>14} {'ipk 200p/10n mA':>16} {'settle ns':>10} verdict")
    lines = [head]
    for r in rows:
        if r["verdict"] == "UNMEASURED":
            lines.append(f"{r['corner']:<14} UNMEASURED: {'; '.join(r['problems'])}")
            continue
        lines.append(
            f"{r['corner']:<14} {r[f'ron_ohm_{w}um_b']:>9.2f} O {r[f'droop_v_{w}um_b'] * 1e3:>11.2f} "
            f"{r[f'ileak_a_{w}um'] * 1e9:>13.3f} {r['i_stack_a'] * 1e9:>14.3f} "
            f"{r['ipk_a_200pf_10ns'] * 1e3:>16.3f} {r['t_settle_s_200pf_10ns'] * 1e9:>10.2f} {r['verdict']}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Summary of the committed records (the tables sim/characterization-power-switch.md quotes)
# --------------------------------------------------------------------------

#: The row's binding corner for idle: ff / +10 % / +125 C.
BINDING = ("ff", 125.0, 3.63)
IDLE_BUDGET_A = 1e-6
ANALOG_IDLE_GLOB = "*-sampler-core-idle-leakage-[0-9]*.md"
ANALOG_IDLE_KEY = "i_idle_clklo_a"


def load_records(records_dir: Path) -> list[dict]:
    """The current power-switch measurement records: corner plus Result bullets."""
    out = []
    for path in _rp.current_records(records_dir, f"*-{SLUG}-[0-9]*.md"):
        text = path.read_text()
        proc, temp, vdd = _rp.parse_corner(text, label=path.stem)
        out.append({"stem": path.stem, "corner": (proc, temp, vdd),
                    "values": _rp.parse_values(_rp.result_section(text, label=path.stem), label=path.stem)})
    return out


def _label(rec: dict) -> str:
    proc, temp, vdd = rec["corner"]
    return f"{proc}/{temp:g}C/{vdd:.2f}V"


def _worst(recs: list[dict], key: str, largest: bool = True) -> tuple[float, str]:
    pick = max if largest else min
    best = pick(recs, key=lambda r: r["values"][key])
    return best["values"][key], _label(best)


def analog_idle_a(records_dir: Path) -> tuple[float, str]:
    """The shipped analog block's idle current at the binding corner (clock parked low)."""
    for path in _rp.current_records(records_dir, ANALOG_IDLE_GLOB):
        text = path.read_text()
        proc, temp, vdd = _rp.parse_corner(text, label=path.stem)
        if (proc, float(temp), round(float(vdd), 2)) == BINDING:
            vals = _rp.parse_values(_rp.result_section(text, label=path.stem), label=path.stem)
            return vals[ANALOG_IDLE_KEY], path.stem
    raise RuntimeError("no analog idle record at the binding corner")


def summary_text(recs: list[dict], analog_a: float, analog_stem: str) -> str:
    n = len(recs)
    lines = [f"Source: {n} records `sim/records/*-{SLUG}-NN.md` (current, status valid).", ""]
    lines += ["**Sizing sweep** (worst case over all corners; loads a = 96.7 uA, b = 1.893 mA)", "",
              "| width | droop a (mV) | droop b (mV, corner) | on-resistance b (ohm) | I^2R loss b (uW) | off leakage, full supply (nA, corner) |",
              "|---|---|---|---|---|---|"]
    for w in WIDTH_UM.values():
        da, _ = _worst(recs, f"droop_v_{w}um_a")
        db, cb = _worst(recs, f"droop_v_{w}um_b")
        rb, _ = _worst(recs, f"ron_ohm_{w}um_b")
        pb, _ = _worst(recs, f"p_loss_w_{w}um_b")
        lk, cl = _worst(recs, f"ileak_a_{w}um")
        lines.append(f"| {w} um | {da * 1e3:.3f} | {db * 1e3:.2f} ({cb}) | {rb:.2f} | {pb * 1e6:.1f} | {lk * 1e9:.2f} ({cl}) |")
    bind = [r for r in recs if (r["corner"][0], float(r["corner"][1]), round(float(r["corner"][2]), 2)) == BINDING]
    if len(bind) != 1:
        raise RuntimeError(f"expected one record at the binding corner, found {len(bind)}")
    b = bind[0]["values"]
    lines += ["", f"**Binding idle corner ff / +10 % / +125 C** (`{bind[0]['stem']}`)", "",
              "| quantity | value |", "|---|---|"]
    for w in WIDTH_UM.values():
        lines.append(f"| switch off leakage, {w} um, full supply across it | {b[f'ileak_a_{w}um'] * 1e9:.2f} nA |")
    lines += [f"| digital leakage-equivalent load alone (ungated reference) | {b['i_ungated_a'] * 1e9:.1f} nA |",
              f"| {SELECTED_WIDTH_UM} um switch off, load behind it (gated domain) | {b['i_stack_a'] * 1e9:.2f} nA |",
              f"| virtual rail level when off | {b['v_stack_v'] * 1e3:.1f} mV |",
              f"| analog block idle (`{analog_stem}`, `{ANALOG_IDLE_KEY}`) | {analog_a * 1e9:.2f} nA |",
              f"| **idle, gated digital + analog** | **{(b['i_stack_a'] + analog_a) * 1e9:.2f} nA** |",
              f"| idle, ungated digital + analog | {(b['i_ungated_a'] + analog_a) * 1e9:.1f} nA |",
              f"| `< 1 uA` row, share used by the gated figure | {(b['i_stack_a'] + analog_a) / IDLE_BUDGET_A * 100:.1f} % |"]
    wi, wc = _worst(recs, "i_stack_a")
    lines += ["", f"Largest gated-domain leakage over all {n} corners: {wi * 1e9:.2f} nA ({wc}).", "",
              f"**Wake** ({SELECTED_WIDTH_UM} um switch; worst case over all corners)", "",
              "| rail capacitance | sleep fall | peak inrush (mA, corner) | settle to 95 % (ns, corner) |", "|---|---|---|---|"]
    for cap, trf in WAKE_CASES.values():
        tag = wake_tag(cap, trf)
        ip, ic = _worst(recs, f"ipk_a_{tag}")
        ts, tc = _worst(recs, f"t_settle_s_{tag}")
        lines.append(f"| {cap * 1e12:g} pF | {trf * 1e9:g} ns | {ip * 1e3:.2f} ({ic}) | {ts * 1e9:.1f} ({tc}) |")
    return "\n".join(lines)


def cmd_summarize(records_dir: Path | None = None) -> int:
    records_dir = records_dir or REPO_ROOT / "sim" / "records"
    recs = load_records(records_dir)
    if not recs:
        print("no power-switch measurement records", file=sys.stderr)
        return 2
    analog, stem = analog_idle_a(records_dir)
    print(summary_text(recs, analog, stem))
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def plan_text() -> str:
    return "\n".join([
        "digital power switch (issue #707)",
        f"  deck        : sim/tb/power-switch/{DECK}",
        f"  units       : {n_units()} = {len(PROCESSES)} MOS corners {PROCESSES} x {len(TEMPS_C)} temps {TEMPS_C} C"
        f" x {len(SUPPLIES_V)} supplies {SUPPLIES_V} V",
        f"  widths (um) : {', '.join(str(w) for w in WIDTH_UM.values())}; DC loads {LOADS_A}",
        f"  tstop       : {TSTOP_S * 1e6:g} us; static readings at {T_STATIC_S * 1e6:g} us; wake edge at {T_WAKE_S * 1e9:g} ns",
        "  backend     : batch via klt sim (KLT_SIM_BACKEND=batch); never a local loop",
    ])


def cmd_emit(check: bool) -> int:
    path, text = request_path(), render(build_request())
    return _kreq.emit_requests(
        [(path, text)], check, repo_root=REPO_ROOT,
        ok=lambda: print(f"ok: {path.relative_to(REPO_ROOT)} matches the declared grid ({n_units()} units)"))


def cmd_run(outdir: str, backend: str, klt_cmd: str, only: str | None = None) -> int:
    return _kreq.run_probe_or_grid(
        outdir, backend, klt_cmd, only, request=request_path(), tb_dir=TB_DIR,
        render_probe=lambda point: render(build_request(point)), probe_hint="--only PROCESS/TEMP/VDD")


def _fmt(x: float) -> str:
    return f"{x:.6e}"


RECORD_FIELDS = (
    [f"droop_v_{w}um_{ld}" for w in WIDTH_UM.values() for ld in LOADS_A]
    + [f"ron_ohm_{w}um_{ld}" for w in WIDTH_UM.values() for ld in LOADS_A]
    + [f"p_loss_w_{w}um_{ld}" for w in WIDTH_UM.values() for ld in LOADS_A]
    + [f"ileak_a_{w}um" for w in WIDTH_UM.values()]
    + ["i_stack_a", "v_stack_v", "i_ungated_a", "stack_reduction_x"]
    + [f"{q}_{wake_tag(cap, trf)}" for cap, trf in WAKE_CASES.values()
       for q in ("ipk_a", "t_settle_s", "vfin_v")]
)


def render_measured(stem: str, row: dict, corner: dict, rep: dict, raw_files: list[tuple[str, str]],
                    now: _dt.datetime, git: dict) -> str:
    env, prov = rep.get("environment", {}), rep.get("provenance", {})
    tb = TB_DIR / DECK
    netlist = REPO_ROOT / "design" / "power_switch.spice"
    remote = env.get("remote")
    fleet = (remote or {}).get("fleet", [])
    # The simulating PDK and ngspice are the fleet worker's, not the submitting host's.
    worker = [(f.get("worker_environment") or {}) for f in fleet]
    stamps = sorted({(w.get("pdk") or {}).get("stamp_text", "") for w in worker} - {""})
    pdk_ver = (stamps[0].replace("open_pdks ", "") if len(stamps) == 1
               else ("; ".join(stamps) or str((prov.get("pdk") or {}).get("version", "unknown"))))
    banners = sorted({((w.get("simulator") or {}).get("version_banner", "").split("\n")[1:2] or [""])[0].strip("* ").strip()
                      for w in worker} - {""})
    ngspice = banners[0] if len(banners) == 1 else f"ngspice-{env.get('engine_version', 'unknown')}"
    jobs = ", ".join(f["job_id"] for f in (remote or {}).get("fleet", []) if f.get("job_id"))
    where = f"batch fleet through klt sim (jobs {jobs})" if jobs else "local ngspice (single-point debug probe)"
    lines = [
        "---", f"record: {stem}", f"date: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}", "status: valid", "",
        "testbench:", f"  path: {tb.relative_to(REPO_ROOT)}", f"  sha: {_report.blob_sha(REPO_ROOT, tb)}",
        "netlist:", f"  path: {netlist.relative_to(REPO_ROOT)}", f"  sha: {_report.blob_sha(REPO_ROOT, netlist)}",
        f"repo_commit: {_report.repo_commit_field(git)}", "",
        f"pdk: gf180mcuD @ {pdk_ver}",
        "pdk.models:",
        f"  - libs.tech/ngspice/sm141064.ngspice (sections: {' '.join(PROCESS_SECTIONS[row['process']])})",
        "", "tool:", f"  klt: {prov.get('klt_version', 'unknown')} (client; batch backend)",
        f"  ngspice: \"{ngspice} (batch fleet)\"",
        f"  platform: \"{platform.platform()} (submitting host)\"", "",
        "corner:", f"  process: {row['process']}", f"  voltage: {_report._voltage_label(row['vdd'], 3.3)}",
        f"  temperature: {row['temperature_c']}", "",
        "analysis:", "  type: tran (deterministic)", f"  tstop: {TSTOP_S * 1e6:g}u",
        f"  tstep: {TSTEP_S * 1e12:g}p (print step)", "  tmax: n/a", "  noise_params: n/a", "  runs: 1",
        "seeds: n/a (deterministic; no noise sources)", "",
        "raw:", f"  path: sim/records/raw/{stem}/", "  files:",
        *[f"    - {n}  sha256:{h}" for n, h in raw_files],
        f"wall_time: {corner.get('runtime_s', 'n/a')}s", "---", "",
        "## Result", "",
        f"Executed by {where}. Raw readings are taken at {T_STATIC_S * 1e6:g} us (static groups) and over "
        "the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. "
        f"Loads: a = {LOADS_A['a'] * 1e6:g} uA, b = {LOADS_A['b'] * 1e3:g} mA (deck header). "
        "Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.", "",
    ]
    for k in RECORD_FIELDS:
        lines.append(f"- `{k}`: {_fmt(row[k])}")
    w = SELECTED_WIDTH_UM
    lines += [
        "",
        f"At this corner the {w} um switch has {row[f'ron_ohm_{w}um_b']:.2f} ohm on-resistance at the 20 MHz bound "
        f"load, leaks {row[f'ileak_a_{w}um'] * 1e9:.3f} nA off with the full supply across it, and with the "
        f"leakage-equivalent digital load behind it the gated domain draws {row['i_stack_a'] * 1e9:.3f} nA "
        f"(ungated reference {row['i_ungated_a'] * 1e9:.1f} nA).",
        "", "Numbers only. No entropy-rate or spec-compliance claim is made by this record.", "",
        "## How to reproduce", "", "```sh",
        "python3 sim/tools/power_switch.py emit --check",
        "python3 sim/tools/power_switch.py run --outdir DIR --backend batch",
        f"python3 sim/tools/power_switch.py run --outdir DIR --backend local --only "
        f"{row['process']}/{row['temperature_c']}/{row['vdd']:.2f}   # single-point probe",
        "python3 sim/tools/power_switch.py analyze DIR/grid.report.json",
        "```", "",
        "## Caveats", "",
        "- Pre-layout, schematic-level: the switch is the netlist of `design/power_switch.spice`, with no "
        "extracted wiring, no well/tap resistance and no package or bond-wire inductance.",
        "- The digital load is a leakage-equivalent off NFET (710 um = 71 x 10 um) and fixed DC currents, not the gate-level "
        "cells; the 50/200 pF rail capacitances are assumptions, not extractions. See the deck header.",
        "- The static readings use the DC loads of the deck; instantaneous clock-edge current peaks are not "
        "modelled, so droop at a clock edge is bounded here only by the 20 MHz average load.",
        "- Gate leakage of the digital cells and of the switch is not separated from channel leakage.",
        "- The raw deck and log have this host's absolute paths replaced by `<repo>` and `~` before hashing.",
        "", "---", "",
        "Written by `sim/tools/power_switch.py record`. Append-only: never edit or delete this file.",
        "",
    ]
    return "\n".join(lines)


def render_unmeasured(stem: str, corners: list[dict], rep: dict, raw_files: list[tuple[str, str]],
                      now: _dt.datetime, git: dict, note: str) -> str:
    prov = rep.get("provenance", {})
    tb = TB_DIR / DECK
    lines = [
        "---", f"record: {stem}", f"date: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}", "status: valid", "",
        "testbench:", f"  path: {tb.relative_to(REPO_ROOT)}", f"  sha: {_report.blob_sha(REPO_ROOT, tb)}",
        "netlist:", "  path: design/power_switch.spice",
        f"  sha: {_report.blob_sha(REPO_ROOT, REPO_ROOT / 'design' / 'power_switch.spice')}",
        f"repo_commit: {_report.repo_commit_field(git)}", "",
        "tool:", f"  klt: {prov.get('klt_version', 'unknown')}", "",
        "raw:", f"  path: sim/records/raw/{stem}/", "  files:",
        *[f"    - {n}  sha256:{h}" for n, h in raw_files],
        "---", "", "## Result", "",
        f"UNMEASURED: {len(corners)} unit(s) produced no usable readings; no number is claimed.", "",
    ]
    if note:
        lines += [note, ""]
    lines += ["---", "", "Written by `sim/tools/power_switch.py record`. Append-only.", ""]
    return "\n".join(lines)


def cmd_record(paths: list[str], note: str, records_dir: Path | None = None) -> int:
    return _mint.mint_records(
        paths, note, records_dir, repo_root=REPO_ROOT, slug=SLUG, slug_attempt=SLUG_ATTEMPT,
        analyse_report=analyse_report, render_measured=render_measured, render_unmeasured=render_unmeasured)


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
    r.add_argument("--klt", default="klt", dest="klt_cmd")
    rc_ = sub.add_parser("record", help="mint append-only records from klt reports")
    rc_.add_argument("reports", nargs="+")
    rc_.add_argument("--note", default="", help="prose appended to an UNMEASURED record")
    sub.add_parser("summarize", help="tables over the committed records, for the characterization report")
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
    if args.cmd == "summarize":
        return cmd_summarize()
    return cmd_analyze(args.reports, args.json)


if __name__ == "__main__":
    sys.exit(main())
