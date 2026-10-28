#!/usr/bin/env python3
"""Check the digital power-gating intent in design/power-intent.md (#708).

    python3 sim/tools/power_intent_check.py --check            # static + gate level
    python3 sim/tools/power_intent_check.py --check --require-tools
    python3 sim/tools/power_intent_check.py --variant no_iso   # one broken fixture
    python3 sim/tools/power_intent_check.py --write-record     # mint an evidence record

``design/power-intent.md`` carries a machine-readable block (the fenced
``power-intent-json`` block). This tool holds the rest of the repository to it:

Static (stdlib only, always run)
  * every output port of ``trng_top`` -- from the RTL *and* from the synthesized
    netlist -- appears in the isolation table with the same width and a clamp
    value, and nothing else does;
  * every flip-flop in the synthesized netlist is classified as retained
    (always-on rail) or gated, and every retained name exists;
  * the declared power-down / wake sequence passes the ordering rules below, and
    the time-to-first-valid consequence is derived from it.

Gate level (needs ``iverilog``/``vvp`` and the gf180mcu cell models)
  * ``trng_top.synth.v`` is transformed into a power-aware netlist (flops swapped
    for ``sim/tb/power-intent/pi_cells.v``, retained flops re-pointed at the
    always-on reset and the gated retention clock) and run through a power-down
    / power-up testbench with an X-driving dead-rail model and AND-cell
    isolation. The control-edge trace it prints is then checked against the same
    ordering rules.

Ordering rules (the failure classes the check must catch)
  unisolated_output / x_on_visible_output   X or non-clamp value on an
                                             always-on-visible port while off
  iso_release_before_rail_good               isolation released before the rail
                                             is good
  reset_release_before_iso_release           gated reset released first
  rail_up_without_reset                      rail came up with reset released
  ret_clock_before_reset_release             retention clock restarted early
  power_off_before_isolation                 switch opened with isolation off
  power_off_with_retained_clock_running      retained flops still clocked
  wake_inside_decay                          switch re-closed before the rail
                                             decayed
  rail_settle_short                          rail "good" sooner than the settle
  missing_step                               a step never happened
  retained state reads X / wrong after wake  scenario ``PI_CHECK ... FAIL``

Exit 0 = every check passed; 1 = a check failed; 2 = a required tool is missing.
Gate level is skipped (loudly) without the tools unless ``--require-tools``.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SIM_DIR = REPO_ROOT / "sim"
INTENT_MD = REPO_ROOT / "design" / "power-intent.md"
TOP_V = REPO_ROOT / "design" / "trng_top" / "trng_top.v"
TB_DIR = SIM_DIR / "tb" / "power-intent"
SLUG = "power-intent"

CLK_NS = 10  # testbench clock period; PI_EVENT times are in ns

FLOP_TYPES = ("dffrnq_1", "dffsnq_1", "dffq_1")

#: broken fixtures -> (iverilog defines, transform kwargs, classes that MUST be reported)
VARIANTS = {
    "no_iso": (["VARIANT_NO_ISO"], {}, {"unisolated_output"}),
    "iso_early": (["VARIANT_ISO_EARLY"], {}, {"iso_release_before_rail_good", "x_on_visible_output"}),
    "reset_early": (["VARIANT_RESET_EARLY"], {}, {"reset_release_before_iso_release"}),
    "ret_lost": ([], {"ret_lost": True}, {"CHECK:ctrl_retained"}),
    "ret_clk_on": (["VARIANT_RET_CLK_ON"], {}, {"missing_step", "x_on_visible_output"}),
    "no_decay_wait": (["VARIANT_NO_DECAY_WAIT"], {}, {"wake_inside_decay"}),
}


# ------------------------------------------------------------------ intent

def load_intent(path: Path = INTENT_MD) -> dict:
    text = path.read_text()
    m = re.search(r"```power-intent-json\n(.*?)\n```", text, re.S)
    if not m:
        raise ValueError(f"{path}: no ```power-intent-json block")
    return json.loads(m.group(1))


# ------------------------------------------------------------------ ports

def netlist_modules(text: str) -> dict[str, str]:
    """Module name -> body text, for a Yosys-written structural netlist."""
    out = {}
    for m in re.finditer(r"^module\s+(\S+?)\s*\(.*?^endmodule", text, re.S | re.M):
        out[m.group(1)] = m.group(0)
    return out


def netlist_ports(text: str, top: str, direction: str) -> dict[str, int]:
    body = netlist_modules(text)[top]
    ports = {}
    for m in re.finditer(rf"^\s*{direction}\s*(?:\[(\d+):(\d+)\])?\s*(\w+);", body, re.M):
        hi, lo = m.group(1), m.group(2)
        ports[m.group(3)] = 1 if hi is None else abs(int(hi) - int(lo)) + 1
    return ports


def rtl_output_ports(text: str) -> dict[str, int]:
    text = re.sub(r"//[^\n]*", "", text)
    ports = {}
    for m in re.finditer(r"\boutput\s+(?:wire\s*)?(?:\[(\d+):(\d+)\])?\s*(\w+)", text):
        hi, lo = m.group(1), m.group(2)
        ports[m.group(3)] = 1 if hi is None else abs(int(hi) - int(lo)) + 1
    return ports


def check_isolation(intent: dict, rtl_text: str, netlist_text: str) -> list[str]:
    errs = []
    declared = {i["port"]: i["width"] for i in intent["isolation"]}
    for i in intent["isolation"]:
        if i.get("clamp") not in (0, 1):
            errs.append(f"isolation {i['port']}: clamp must be 0 or 1, got {i.get('clamp')!r}")
    for label, actual in (
        ("RTL trng_top.v", rtl_output_ports(rtl_text)),
        ("synthesized trng_top", netlist_ports(netlist_text, intent["top"], "output")),
    ):
        for p, w in actual.items():
            if p not in declared:
                errs.append(f"{label}: output {p}[{w}] crosses out of the gated domain with no isolation entry")
            elif declared[p] != w:
                errs.append(f"{label}: output {p} is {w} wide, isolation entry says {declared[p]}")
        for p in declared:
            if p not in actual:
                errs.append(f"isolation entry {p} is not an output of {label}")
    return errs


# ------------------------------------------------------------------ flops

_INST = re.compile(
    r"gf180mcu_fd_sc_mcu\w+?__(?P<cell>" + "|".join(FLOP_TYPES) + r")\s+(?P<name>\S+)\s*\((?P<pins>.*?)\n\s*\);",
    re.S,
)


def q_root(pins: str) -> str:
    m = re.search(r"\.Q\(\s*\\?([\w.$]+)", pins)
    return m.group(1) if m else ""


def classify_flops(netlist_text: str, intent: dict) -> dict:
    """Counts of retained and gated flops, and any retained name never found."""
    ret_mod = intent["retained"]["module"]
    ret_nets = set(intent["retained"]["q_nets"])
    counts = {"retained": 0, "gated": 0}
    found = set()
    for mod, body in netlist_modules(netlist_text).items():
        for m in _INST.finditer(body):
            root = q_root(m.group("pins"))
            if mod == ret_mod and root in ret_nets:
                counts["retained"] += 1
                found.add(root)
            else:
                counts["gated"] += 1
    counts["missing"] = sorted(ret_nets - found)
    return counts


def transform_netlist(text: str, intent: dict, ret_lost: bool = False) -> str:
    """Power-aware copy of the synthesized netlist (see pi_cells.v)."""
    ret_mod = intent["retained"]["module"]
    ret_nets = set(intent["retained"]["q_nets"])
    top = intent["top"]
    out = []
    pos = 0
    modules = netlist_modules(text)
    for mod, body in modules.items():
        start = text.index(body, pos)
        out.append(text[pos:start])
        pos = start + len(body)

        def swap(m, mod=mod):
            pins = m.group("pins")
            retained = mod == ret_mod and q_root(pins) in ret_nets
            if retained:
                pins = pins.replace(".CLK(clk)", ".CLK(clk_ret)")
                pins = re.sub(r"\.(RN|SETN)\(rst_n\)", r".\1(rst_ao_n)", pins)
            ret = 1 if retained and not ret_lost else 0
            return f"pi_{m.group('cell')} #(.RET({ret})) {m.group('name')} ({pins}\n  );"

        body = _INST.sub(swap, body)
        if mod == ret_mod or mod == top:
            body = re.sub(r"^(module\s+\S+?\s*\()(.*?)\);", r"\1\2, clk_ret, rst_ao_n);", body, count=1, flags=re.S | re.M)
            body = re.sub(r"(\);\n)", r"\1  input clk_ret;\n  input rst_ao_n;\n", body, count=1)
        if mod == top:
            body = body.replace(
                f"{ret_mod} u_interface (", f"{ret_mod} u_interface (\n    .clk_ret(clk_ret),\n    .rst_ao_n(rst_ao_n),"
            )
        out.append(body)
    out.append(text[pos:])
    return "".join(out)


# --------------------------------------------------------------- sequencing

def check_sequence(events: list[tuple[int, str]], settle_ns: int, decay_ns: int) -> list[str]:
    """Ordering rules over a (time_ns, event) trace; returns violation classes."""
    lvl = dict(pwr=0, rail=0, iso=0, rst=0, ret=0)
    t_on = t_off = None
    viol = []
    n_off = n_ret_off = n_on = n_iso_rel = n_rst_rel = n_ret_on = 0

    def bad(cls):
        if cls not in viol:
            viol.append(cls)

    for t, ev in events:
        if ev == "pwr_on":
            if t_off is not None and t - t_off < decay_ns:
                bad("wake_inside_decay")
            lvl["pwr"] = 1
            t_on = t
            n_on += 1
        elif ev == "pwr_off":
            if lvl["iso"] != 0:
                bad("power_off_before_isolation")
            if lvl["ret"] != 0:
                bad("power_off_with_retained_clock_running")
            lvl["pwr"] = 0
            t_off = t
            n_off += 1
        elif ev == "rail_good":
            if lvl["rst"] != 0:
                bad("rail_up_without_reset")
            if t_on is not None and t - t_on < settle_ns:
                bad("rail_settle_short")
            lvl["rail"] = 1
        elif ev == "rail_off":
            lvl["rail"] = 0
        elif ev == "iso_release":
            if lvl["rail"] != 1:
                bad("iso_release_before_rail_good")
            lvl["iso"] = 1
            n_iso_rel += 1
        elif ev == "iso_assert":
            lvl["iso"] = 0
        elif ev == "rst_release":
            if lvl["iso"] != 1:
                bad("reset_release_before_iso_release")
            lvl["rst"] = 1
            n_rst_rel += 1
        elif ev == "rst_assert":
            lvl["rst"] = 0
        elif ev == "ret_clk_on":
            if lvl["rst"] != 1 or lvl["iso"] != 1:
                bad("ret_clock_before_reset_release")
            lvl["ret"] = 1
            n_ret_on += 1
        elif ev == "ret_clk_off":
            lvl["ret"] = 0
            n_ret_off += 1
    # every power-on needs a full wake, every power-off a retained-clock stop
    if not (n_on == n_iso_rel == n_rst_rel == n_ret_on) or n_off != n_ret_off:
        bad("missing_step")
    return viol


def nominal_trace(intent: dict) -> list[tuple[int, str]]:
    """The declared sequence as a trace: one power-down then one wake."""
    t = 0
    trace = []
    seq = intent["sequence"]["power_down"]
    for step in seq:
        t += step["after_cycles"] * CLK_NS
        trace.append((t, step["event"]))
    t += intent["timing"]["t_rail_decay_cycles"]["value"] * CLK_NS
    trace.append((t, "rail_off"))
    for step in intent["sequence"]["wake"]:
        wait = step.get("after_cycles", 0) * CLK_NS
        if step.get("after_rail_settle"):
            wait += intent["timing"]["t_rail_settle_cycles"]["value"] * CLK_NS
        t += wait
        trace.append((t, step["event"]))
    return trace


def wake_budget(intent: dict) -> dict:
    """Wake latency from the declared sequence, plus the time-to-first-valid it implies."""
    sys.path.insert(0, str(SIM_DIR / "tools"))
    import time_to_first_valid as ttfv

    cycles = intent["timing"]["t_rail_settle_cycles"]["value"] + sum(
        s.get("after_cycles", 0) for s in intent["sequence"]["wake"]
    )
    period_s = 1.0 / ttfv.RATIFIED_RAW_RATE_BPS
    samples = ttfv.SAMPLER_SAMPLES + ttfv.STARTUP_SAMPLES + ttfv.CONDITIONER_SAMPLES
    return {
        "wake_cycles": cycles,
        "wake_overhead_s": cycles * period_s,
        "digital_floor_s": samples * period_s,
        "wake_time_to_first_valid_s": (samples + cycles) * period_s,
        "readme_floor_s": ttfv.README_FLOOR_S,
        "provisional": any(v["status"] == "placeholder" for v in intent["timing"].values()),
    }


# ------------------------------------------------------------- gate level

def find_cell_lib(netlist_text: str) -> Path | None:
    m = re.search(r"(gf180mcu_fd_sc_mcu\w+?)__", netlist_text)
    if not m:
        return None
    sys.path.insert(0, str(SIM_DIR))
    try:
        from harness import pdk
        root = pdk.find_pdk().path
    except Exception:
        return None
    lib = root / "libs.ref" / m.group(1) / "verilog" / f"{m.group(1)}.v"
    return lib if lib.is_file() else None


def tools_missing() -> list[str]:
    return [t for t in ("iverilog", "vvp") if not shutil.which(t)]


def run_gate_level(intent: dict, netlist_text: str, lib: Path, defines=(), ret_lost=False) -> dict:
    timing = intent["timing"]
    with tempfile.TemporaryDirectory(prefix="power-intent-") as tmp:
        tmp = Path(tmp)
        (tmp / "dut.v").write_text(transform_netlist(netlist_text, intent, ret_lost=ret_lost))
        vvp = tmp / "tb.vvp"
        cmd = [
            "iverilog", "-g2012", "-DFUNCTIONAL",
            f"-Ptb.T_SETTLE={timing['t_rail_settle_cycles']['value']}",
            f"-Ptb.T_DECAY={timing['t_rail_decay_cycles']['value']}",
            *[f"-D{d}" for d in defines],
            "-o", str(vvp),
            str(TB_DIR / "tb_power_intent.v"), str(TB_DIR / "pi_cells.v"), str(tmp / "dut.v"), str(lib.with_name("primitives.v")), str(lib),
        ]
        comp = subprocess.run(cmd, capture_output=True, text=True)
        if comp.returncode != 0:
            raise RuntimeError("iverilog failed:\n" + comp.stderr[-2000:])
        run = subprocess.run(["vvp", str(vvp)], capture_output=True, text=True, timeout=600)
    # keep protocol lines only: simulator chatter carries absolute host paths
    log = "".join(l + "\n" for l in run.stdout.splitlines() if l.startswith("PI_"))
    events = [(int(m.group(1)), m.group(2)) for m in re.finditer(r"^PI_EVENT (\d+) (\w+)", log, re.M)]
    viol = sorted(set(re.findall(r"^PI_VIOLATION (\w+)", log, re.M)))
    fails = sorted(m for m in re.findall(r"^PI_CHECK (\w+) FAIL", log, re.M))
    passes = sorted(m for m in re.findall(r"^PI_CHECK (\w+) PASS", log, re.M))
    done = "PI_DONE" in log
    seq = check_sequence(
        events,
        timing["t_rail_settle_cycles"]["value"] * CLK_NS,
        timing["t_rail_decay_cycles"]["value"] * CLK_NS,
    )
    return {
        "log": log, "events": events, "monitor_violations": viol, "sequence_violations": seq,
        "failed_checks": fails, "passed_checks": passes, "completed": done,
        "classes": set(viol) | set(seq) | {f"CHECK:{c}" for c in fails} | ({"INCOMPLETE"} if not done else set()),
    }


# ------------------------------------------------------------------- record

def write_record(intent: dict, netlist_text: str, lib: Path, good: dict, bad: dict) -> Path:
    import time
    from datetime import datetime, timezone

    sys.path.insert(0, str(SIM_DIR))
    from harness import report

    git = report.git_provenance(REPO_ROOT)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cls = classify_flops(netlist_text, intent)
    budget = wake_budget(intent)
    t0 = time.time()

    def render(stem: str, raw_dir: Path) -> str:
        (raw_dir / "gate_level.log").write_text(good["log"])
        summary = {
            "monitor_violations": good["monitor_violations"],
            "sequence_violations": good["sequence_violations"],
            "passed_checks": good["passed_checks"],
            "failed_checks": good["failed_checks"],
            "flops": cls,
            "wake_budget": budget,
            "broken_fixtures": {
                name: {"reported": sorted(r["classes"]), "required": sorted(VARIANTS[name][2])}
                for name, r in bad.items()
            },
        }
        (raw_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=list) + "\n")
        raw_files = [(n, report.sha256_file(raw_dir / n)) for n in ("gate_level.log", "summary.json")]
        fm = report.behavioral_frontmatter(
            stem=stem, git=git, raw_files=raw_files, repo_root=REPO_ROOT,
            testbench="sim/tb/power-intent/tb_power_intent.v",
            netlist="design/trng_top/trng_top.synth.v",
            netlist_note=[
                "Synthesized trng_top with its flip-flops swapped for the power-aware",
                "models in sim/tb/power-intent/pi_cells.v by sim/tools/power_intent_check.py;",
                "combinational cells are the PDK's own functional models",
                f"({lib.parent.parent.name}, -DFUNCTIONAL).",
            ],
            analysis_type="gate-level functional power-down/power-up (zero delay)",
            tstop=f"{len(good['events'])} control edges; see gate_level.log",
            noise_params="n/a (digital)",
            seeds="tb.seed = 0x1234abcd ($random)",
            wall_time=f"{time.time() - t0:.1f}s",
        )
        fm = fm.replace(
            "level: behavioral (see spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md)",
            "level: gate-simulation, functional and zero-delay (the netlist is the synthesized "
            "design/trng_top/trng_top.synth.v; power is a behavioural model, not a device model)",
        )
        return fm + "\n" + _record_body(intent, good, bad, cls, budget)

    return report.finalize_record(SIM_DIR / "records", date, SLUG, render)


def _record_body(intent, good, bad, cls, budget) -> str:
    rows = "\n".join(
        f"| `{n}` | {', '.join(sorted(r['classes'])) or 'none'} | {', '.join(sorted(VARIANTS[n][2]))} |"
        for n, r in bad.items()
    )
    return f"""
## Result

- Gate-level run of the synthesized `trng_top` across power-down and power-up
  (cold boot, a power cycle with a register read pending, a power cycle with a
  latched health-test alarm, and a back-to-back down/up):
  **{len(good['passed_checks'])} scenario checks passed, {len(good['failed_checks'])} failed;
  {len(good['monitor_violations'])} X/clamp violations; {len(good['sequence_violations'])} sequencing violations.**
- No X on any of the {sum(i['width'] for i in intent['isolation'])} always-on-visible output bits
  while off (all held at the clamp value 0), and no X on any of them after
  wake; sampled every clock.
- Flops: {cls['retained']} retained (always-on rail), {cls['gated']} gated.
- Wake latency {budget['wake_cycles']} sample-clock cycles
  ({budget['wake_overhead_s'] * 1e3:.2f} ms at the ratified raw rate) on top of the
  {budget['digital_floor_s'] * 1e3:.1f} ms digital start-up total:
  **{budget['wake_time_to_first_valid_s'] * 1e3:.1f} ms** wake-to-first-valid, **provisional**
  (rail settle and decay are placeholders until #707 lands).

Deliberately broken fixtures, each of which must be (and was) reported:

| Fixture | Reported | Required |
|---|---|---|
{rows}

## How to reproduce

```sh
python3 sim/tools/power_intent_check.py --check --require-tools
python3 sim/tools/power_intent_check.py --variant no_iso   # exits 1
```

## Caveats

- **No P/V/T corner.** This is a zero-delay functional simulation: it says
  nothing about leakage, switch resistance, rail settling, inrush, timing or
  any other PVT-dependent claim, and must not be cited for one. The rail model
  is two delays that are placeholders for #707's evidence.
- The power-down model is behavioural: gated flops go X and gated outputs go X
  when the rail is low. It does not model sneak paths, input-side protection
  or a partially collapsed rail.
- Only the output crossings are checked. Inputs driven into the unpowered
  domain are an open item recorded in `design/power-intent.md`.
- The retention scheme (clock-gated always-on flops) is not integrated into the
  shipped RTL, netlist or layout; the netlist here is a derived copy.

Written by `sim/tools/power_intent_check.py --write-record`. Append-only: never
edit or delete this file.
"""


# --------------------------------------------------------------------- main

def static_checks(intent: dict, netlist_text: str) -> list[str]:
    errs = check_isolation(intent, TOP_V.read_text(), netlist_text)
    cls = classify_flops(netlist_text, intent)
    for name in cls["missing"]:
        errs.append(f"retained net {name} has no flop in module {intent['retained']['module']}")
    if cls["retained"] == 0:
        errs.append("no retained flops found in the netlist")
    timing = intent["timing"]
    viol = check_sequence(
        nominal_trace(intent),
        timing["t_rail_settle_cycles"]["value"] * CLK_NS,
        timing["t_rail_decay_cycles"]["value"] * CLK_NS,
    )
    errs += [f"declared sequence violates {v}" for v in viol]
    for k, v in timing.items():
        if v["status"] not in ("placeholder", "measured"):
            errs.append(f"timing {k}: status must be placeholder or measured")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="static checks plus the gate-level run")
    ap.add_argument("--require-tools", action="store_true", help="fail (exit 2) instead of skipping the gate-level run")
    ap.add_argument("--variant", choices=sorted(VARIANTS), help="run one deliberately broken fixture")
    ap.add_argument("--write-record", action="store_true", help="run everything and mint an evidence record")
    args = ap.parse_args(argv)
    if not (args.check or args.variant or args.write_record):
        ap.error("one of --check, --variant, --write-record is required")

    intent = load_intent()
    netlist_text = (REPO_ROOT / intent["netlist"]).read_text()

    errs = static_checks(intent, netlist_text)
    for e in errs:
        print(f"FAIL static: {e}")
    if not errs:
        print("ok   static: isolation covers every output; flops classified; declared sequence ordered")
    b = wake_budget(intent)
    print(
        f"     wake budget: {b['wake_cycles']} cycles, wake-to-first-valid "
        f"{b['wake_time_to_first_valid_s'] * 1e3:.1f} ms"
        + (" (PROVISIONAL: placeholders from #707)" if b["provisional"] else "")
    )

    lib = find_cell_lib(netlist_text)
    missing = tools_missing()
    if missing or lib is None:
        why = f"{', '.join(missing)} not on PATH" if missing else "gf180mcu cell models not found"
        print(f"SKIP gate level: {why}")
        if args.require_tools or args.variant or args.write_record:
            return 2
        return 1 if errs else 0

    rc = 1 if errs else 0
    if args.variant:
        defines, kw, required = VARIANTS[args.variant]
        r = run_gate_level(intent, netlist_text, lib, defines, **kw)
        for c in sorted(r["classes"]):
            print(f"FAIL {args.variant}: {c}")
        return 1 if r["classes"] else 0

    good = run_gate_level(intent, netlist_text, lib)
    for c in good["failed_checks"]:
        print(f"FAIL gate level: scenario check {c}")
    for c in sorted(good["classes"] - {f"CHECK:{c}" for c in good["failed_checks"]}):
        print(f"FAIL gate level: {c}")
    if good["classes"]:
        rc = 1
    else:
        print(f"ok   gate level: {len(good['passed_checks'])} scenario checks, no X/clamp or ordering violation")

    bad = {}
    for name, (defines, kw, required) in VARIANTS.items():
        r = run_gate_level(intent, netlist_text, lib, defines, **kw)
        bad[name] = r
        if required <= r["classes"]:
            print(f"ok   broken fixture {name}: reported {', '.join(sorted(required))}")
        else:
            print(f"FAIL broken fixture {name}: expected {sorted(required)}, got {sorted(r['classes'])}")
            rc = 1
    if args.write_record and rc == 0:
        print("wrote", write_record(intent, netlist_text, lib, good, bad).relative_to(REPO_ROOT))
    return rc


if __name__ == "__main__":
    sys.exit(main())
