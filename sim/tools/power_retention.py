#!/usr/bin/env python3
"""Retained state and measured gated-domain idle: batch-fleet run, records, summary (issue #790).

    python3 sim/tools/power_retention.py plan
    python3 sim/tools/power_retention.py emit [--check]
    python3 sim/tools/power_retention.py run --outdir DIR [--backend batch] [--only PROCESS/TEMP/VDD]
    python3 sim/tools/power_retention.py record DIR/grid.report.json [--note TEXT]
    python3 sim/tools/power_retention.py analyze DIR/grid.report.json [--json]
    python3 sim/tools/power_retention.py summarize

``sim/tb/power-retention/tb_power_retention.sp`` builds the always-on set of ``design/power-intent.md``
from real gf180mcu cells (five retained flops, the retention clock gate, 66 isolation ANDs) beside the
#707 header switch and leakage-equivalent load, in one deterministic transient per PVT point: a power
cycle that checks the retained bits survive (with a free-running-clock control that must lose them), and
the idle current with the switch off and the pattern held. The 45-point grid is the one of
``power_switch.py`` and goes to the batch fleet through ``klt sim``; ``--only`` runs one point locally as a
debug probe. The arithmetic (pass/fail of the retained bits, idle sum with the analog block) is here so
it can be unit-tested.
"""

from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _power_cli as _pc  # noqa: E402
import power_switch as _ps  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
TB_DIR = REPO_ROOT / "sim" / "tb" / "power-retention"
DECK = "tb_power_retention.sp"
REQUEST_NAME = "request-grid.json"
SLUG = "power-retention"

PROCESSES, TEMPS_C, SUPPLIES_V = _ps.PROCESSES, _ps.TEMPS_C, _ps.SUPPLIES_V
PROCESS_SECTIONS = _ps.PROCESS_SECTIONS
BINDING = _ps.BINDING
IDLE_BUDGET_A = _ps.IDLE_BUDGET_A
ANALOG_IDLE_GLOB, ANALOG_IDLE_KEY = _ps.ANALOG_IDLE_GLOB, _ps.ANALOG_IDLE_KEY
TSTEP_S = 1e-9
TSTOP_S = 30e-6
HOSTS = 3

#: Retained flops in deck order and the pattern written into them (deck header).
RETAINED = ("ctrl_en", "ctrl_out_mode_raw", "fail_rct", "fail_apt", "fail_ring")
PATTERN = (1, 0, 1, 0, 1)
#: A node is read as 1 above half the supply, 0 below.
#: The clamp must hold the isolation output below this fraction of the supply while iso_n = 0.
CLAMP_FRACTION = 0.1
#: Quantities that need no arithmetic beyond the thresholds above.
STATIC_WINDOW = "10u to 14u"
CLOCK_WINDOW = "16u to 20u"


def measurements() -> list[dict]:
    m: list[dict] = []

    def add(name: str, spice: str, unit: str) -> None:
        m.append({"name": name, "spice": spice, "unit": unit})

    for k in range(1, len(RETAINED) + 1):
        add(f"qg_pre_{k}", f".meas tran qg_pre_{k} find v(qg{k}) at=4.5u", "V")
        add(f"qg_post_{k}", f".meas tran qg_post_{k} find v(qg{k}) at=29u", "V")
        add(f"qb_post_{k}", f".meas tran qb_post_{k} find v(qb{k}) at=29u", "V")
        add(f"qi_{k}", f".meas tran qi_{k} find v(qi{k}) at=13u", "V")
    add("z_off", ".meas tran z_off max v(zf) from=6.5u to=19.5u", "V")
    add("z_on", ".meas tran z_on find v(zf) at=29u", "V")
    add("i_ao_static", ".meas tran i_ao_static avg i(vwai) from=10u to=14u", "A")
    add("i_ao_clk", ".meas tran i_ao_clk avg i(vwai) from=16u to=20u", "A")
    add("i_sw", ".meas tran i_sw avg i(vwsi) from=10u to=14u", "A")
    add("v_rail", ".meas tran v_rail avg v(vsti) from=10u to=14u", "V")
    return m


def build_request(only: str | None = None) -> dict:
    """The declared request; ``only`` restricts it to ONE grid point (the local debug probe)."""
    req = _pc.build_full_request(
        issue=790, title="power-retention", script="power_retention", deck=DECK,
        processes=PROCESSES, process_sections=PROCESS_SECTIONS, supply_param="vsup",
        supplies_v=SUPPLIES_V, temps_c=TEMPS_C,
        analysis_args=f"{TSTEP_S * 1e9:g}n {TSTOP_S * 1e6:g}u",
        measurements=measurements(), hosts=HOSTS, capacity_wait_s=600, timeout_s=300,
        ngspice_init=["set measureprec=12", "set num_threads=1"])
    if only is None:
        return req
    return _pc.restrict_to_point(req, only, parse_only=_ps.parse_only, supply_param="vsup",
                                 issue=790)


render = _pc.render


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


def bits(v: dict, prefix: str, vdd: float) -> list[int]:
    """The five retained bits read from ``{prefix}{k}`` node voltages (1 above vdd/2)."""
    return [1 if v[f"{prefix}{k}"] > vdd / 2 else 0 for k in range(1, len(RETAINED) + 1)]


def derive(v: dict, vdd: float) -> dict:
    names = [f"{p}{k}" for p in ("qg_pre_", "qg_post_", "qb_post_", "qi_") for k in range(1, len(RETAINED) + 1)]
    _need(v, *names, "z_off", "z_on", "i_ao_static", "i_ao_clk", "i_sw", "v_rail")
    out: dict = {"vdd_v": vdd}
    for tag in ("qg_pre_", "qg_post_", "qb_post_", "qi_"):
        out[f"bits_{tag.rstrip('_')}"] = "".join(str(b) for b in bits(v, tag, vdd))
    want = "".join(str(b) for b in PATTERN)
    out["retained_ok"] = int(out["bits_qg_pre"] == want and out["bits_qg_post"] == want)
    out["idle_hold_ok"] = int(out["bits_qi"] == want)
    out["control_lost"] = int(out["bits_qb_post"] != want)
    out["clamp_ok"] = int(v["z_off"] < CLAMP_FRACTION * vdd and v["z_on"] > vdd / 2)
    out["z_off_v"], out["z_on_v"] = v["z_off"], v["z_on"]
    out["i_ao_static_a"], out["i_ao_clk_a"] = v["i_ao_static"], v["i_ao_clk"]
    out["i_sw_a"], out["v_rail_v"] = v["i_sw"], v["v_rail"]
    out["i_digital_idle_a"] = v["i_ao_static"] + v["i_sw"]
    return out


def checks(row: dict) -> list[str]:
    bad = []
    for key in ("retained_ok", "idle_hold_ok", "control_lost", "clamp_ok"):
        if not row[key]:
            bad.append(f"{key} = 0")
    for key in ("i_ao_static_a", "i_sw_a"):
        if not row[key] > 0:
            bad.append(f"{key} = {row[key]:.4g} A is not positive")
    return bad


_vals = _pc.vals


def analyse_report(report: dict) -> list[dict]:
    return _pc.analyse_report(report, derive, checks, DerivationError)


def table(rows: list[dict]) -> str:
    lines = [f"{'corner':<14} {'retained':>8} {'ctrl lost':>9} {'clamp':>5} {'AO static nA':>13} "
             f"{'switch nA':>10} {'digital idle nA':>16} {'rail mV':>8} verdict"]
    for r in rows:
        if r["verdict"] == "UNMEASURED":
            lines.append(f"{r['corner']:<14} UNMEASURED: {'; '.join(r['problems'])}")
            continue
        lines.append(f"{r['corner']:<14} {r['bits_qg_post']:>8} {r['bits_qb_post']:>9} {r['clamp_ok']:>5} "
                     f"{r['i_ao_static_a'] * 1e9:>13.3f} {r['i_sw_a'] * 1e9:>10.3f} "
                     f"{r['i_digital_idle_a'] * 1e9:>16.3f} {r['v_rail_v'] * 1e3:>8.1f} {r['verdict']}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Summary of the committed records
# --------------------------------------------------------------------------

#: Whole-record fields that are numbers (the string bit fields are written as text bullets).
NUM_FIELDS = ("i_ao_static_a", "i_ao_clk_a", "i_sw_a", "v_rail_v", "i_digital_idle_a", "z_off_v", "z_on_v",
              "retained_ok", "idle_hold_ok", "control_lost", "clamp_ok")
MODEL_IDLE_A = 74.44e-9  # sim/characterization-power-switch.md section 3 (modelled, no retention)


def load_records(records_dir: Path) -> list[dict]:
    """The current measurement records for this tool's slug: corner plus Result bullets."""
    return _pc.load_records(records_dir, SLUG)


_label = _pc.label


def summary_text(recs: list[dict], analog_a: float, analog_stem: str) -> str:
    n = len(recs)
    lines = [f"Source: {n} records `sim/records/*-{SLUG}-NN.md` (current, status valid).", ""]
    failed = [r for r in recs if not all(r["values"][k] == 1 for k in ("retained_ok", "idle_hold_ok", "control_lost", "clamp_ok"))]
    lines += [f"Retained bits survive the power cycle, the idle hold, and the clamp holds at "
              f"{n - len(failed)} of {n} corners; the free-running-clock control loses state at "
              f"{sum(1 for r in recs if r['values']['control_lost'] == 1)} of {n}."
              + ("" if not failed else " Failing: " + ", ".join(_label(r) for r in failed) + "."), ""]
    bind = [r for r in recs if (r["corner"][0], float(r["corner"][1]), round(float(r["corner"][2]), 2)) == BINDING]
    if len(bind) != 1:
        raise RuntimeError(f"expected one record at the binding corner, found {len(bind)}")
    b = bind[0]["values"]
    idle = b["i_digital_idle_a"] + analog_a
    lines += [f"**Binding idle corner ff / +10 % / +125 C** (`{bind[0]['stem']}`)", "",
              "| quantity | value |", "|---|---|",
              f"| always-on set (5 retained flops, clock gate, 66 isolation ANDs), clock parked | {b['i_ao_static_a'] * 1e9:.2f} nA |",
              f"| 400 um switch off with the leakage-equivalent load behind it | {b['i_sw_a'] * 1e9:.2f} nA |",
              f"| virtual rail level when off | {b['v_rail_v'] * 1e3:.1f} mV |",
              f"| analog block idle (`{analog_stem}`, `{ANALOG_IDLE_KEY}`) | {analog_a * 1e9:.2f} nA |",
              f"| **idle, gated digital + retained set + analog (measured)** | **{idle * 1e9:.2f} nA** |",
              f"| modelled figure without retention (`sim/characterization-power-switch.md`) | {MODEL_IDLE_A * 1e9:.2f} nA |",
              f"| cost of retention over the model | {(idle - MODEL_IDLE_A) * 1e9:.2f} nA |",
              f"| `< 1 uA` row, share used | {idle / IDLE_BUDGET_A * 100:.1f} % |",
              f"| always-on set with the 1 MHz clock toggling into the closed gate | {b['i_ao_clk_a'] * 1e9:.2f} nA |"]
    worst = max(recs, key=lambda r: r["values"]["i_digital_idle_a"])
    lines += ["", f"Largest digital idle (retained set + switch + load) over all {n} corners: "
              f"{worst['values']['i_digital_idle_a'] * 1e9:.2f} nA ({_label(worst)}), before the analog block."]
    return "\n".join(lines)


def cmd_summarize(records_dir: Path | None = None) -> int:
    records_dir = records_dir or REPO_ROOT / "sim" / "records"
    recs = load_records(records_dir)
    if not recs:
        print("no power-retention measurement records", file=sys.stderr)
        return 2
    analog, stem = _ps.analog_idle_a(records_dir)
    print(summary_text(recs, analog, stem))
    return 0


# --------------------------------------------------------------------------
# Records and CLI
# --------------------------------------------------------------------------


def plan_text() -> str:
    return "\n".join([
        "retained state and measured gated-domain idle (issue #790)",
        f"  deck        : sim/tb/power-retention/{DECK}",
        f"  units       : {n_units()} = {len(PROCESSES)} MOS corners {PROCESSES} x {len(TEMPS_C)} temps {TEMPS_C} C"
        f" x {len(SUPPLIES_V)} supplies {SUPPLIES_V} V",
        f"  static idle : {STATIC_WINDOW}; clock-toggling reading {CLOCK_WINDOW}; tstop {TSTOP_S * 1e6:g} us",
        "  backend     : batch via klt sim (KLT_SIM_BACKEND=batch); never a local loop",
    ])


def cmd_emit(check: bool) -> int:
    return _pc.cmd_emit(check, path=request_path(), text=render(build_request()), repo_root=REPO_ROOT, n_units=n_units())


def cmd_run(outdir: str, backend: str, klt_cmd: str, only: str | None = None) -> int:
    return _pc.cmd_run(outdir, backend, klt_cmd, only, request=request_path(), tb_dir=TB_DIR, build_request=build_request)


_fmt = _pc.fmt


def render_measured(stem: str, row: dict, corner: dict, rep: dict, raw_files: list[tuple[str, str]],
                    now: _dt.datetime, git: dict) -> str:
    where = _pc.fleet_where(rep)
    lines = _pc.fleet_header(
        stem=stem, row=row, unit=corner, rep=rep, raw_files=raw_files, now=now, git=git,
        repo_root=REPO_ROOT, testbench=TB_DIR / DECK, netlist=TB_DIR / "retention_cells.spice",
        netlist_also=REPO_ROOT / "design" / "power_switch.spice",
        sections=PROCESS_SECTIONS[row["process"]],
        analysis=["  type: tran (deterministic)", f"  tstop: {TSTOP_S * 1e6:g}u",
                  f"  tstep: {TSTEP_S * 1e9:g}n (print step)", "  tmax: n/a", "  noise_params: n/a",
                  "  runs: 1"])
    lines += [
        "## Result", "",
        f"Executed by {where}. Retained bits are read as 1 above half the supply, in the order "
        f"{', '.join(RETAINED)}; the pattern written is {''.join(str(b) for b in PATTERN)}. "
        "The idle readings are averages over the windows in the deck header.", "",
    ]
    for k in NUM_FIELDS:
        lines.append(f"- `{k}`: {_fmt(float(row[k]))}")
    for k in ("bits_qg_pre", "bits_qg_post", "bits_qb_post", "bits_qi"):
        lines.append(f"- {k}: `{row[k]}`")
    lines += [
        "",
        f"At this corner the retained bits read `{row['bits_qg_post']}` after the forced power cycle "
        f"(written `{''.join(str(b) for b in PATTERN)}`), the free-running-clock control reads "
        f"`{row['bits_qb_post']}`, and with the switch off the always-on set draws "
        f"{row['i_ao_static_a'] * 1e9:.3f} nA beside {row['i_sw_a'] * 1e9:.3f} nA for the switch and its "
        "leakage-equivalent load.",
        "", "Numbers only. No entropy-rate or spec-compliance claim is made by this record.", "",
        "## How to reproduce", "", "```sh",
        "python3 sim/tools/power_retention.py emit --check",
        "python3 sim/tools/power_retention.py run --outdir DIR --backend batch   # via klt sim; the request sets batch.capacity_wait_s",
        f"python3 sim/tools/power_retention.py run --outdir DIR --backend local --only "
        f"{row['process']}/{row['temperature_c']}/{row['vdd']:.2f}   # single-point probe",
        "python3 sim/tools/power_retention.py analyze DIR/grid.report.json",
        "```", "",
        "## Caveats", "",
        "- Pre-layout, schematic-level: the cells and the switch are netlists, with no extracted wiring.",
        "- The gated domain's logic is ideal sources (pattern, hold feedback, isolation inputs); the digital load "
        "behind the switch is the #707 leakage-equivalent NFET, not the cells.",
        "- The rail is forced in the function group; rail decay is an open item (`design/power-intent.md`).",
        "- The retained flops are plain `dffrnq_1` on the always-on rail: the library has no retention flop.",
        "- The raw deck and log have this host's absolute paths replaced by `<repo>` and `~` before hashing.",
        "",
        *_pc.record_footer("power_retention"),
    ]
    return "\n".join(lines)


def render_unmeasured(stem: str, corners: list[dict], rep: dict, raw_files: list[tuple[str, str]],
                      now: _dt.datetime, git: dict, note: str) -> str:
    return _pc.render_attempt(
        stem=stem, corners=corners, rep=rep, raw_files=raw_files, now=now, git=git, note=note,
        repo_root=REPO_ROOT, testbench=TB_DIR / DECK,
        netlist=TB_DIR / "retention_cells.spice", tool_name="power_retention")


def cmd_record(paths: list[str], note: str, records_dir: Path | None = None) -> int:
    return _pc.cmd_record(
        paths, note, records_dir, repo_root=REPO_ROOT, slug=SLUG, analyse_report=analyse_report,
        render_measured=render_measured, render_unmeasured=render_unmeasured)


def cmd_analyze(paths: list[str], as_json: bool) -> int:
    return _pc.cmd_analyze(paths, as_json, analyse_report=analyse_report, table=table)


def main(argv: list[str] | None = None) -> int:
    return _pc.main(argv, doc=__doc__, only_example="ff/125/3.63", plan_text=plan_text,
                    cmd_emit=cmd_emit, cmd_run=cmd_run, cmd_record=cmd_record,
                    cmd_analyze=cmd_analyze, cmd_summarize=cmd_summarize)


if __name__ == "__main__":
    sys.exit(main())
