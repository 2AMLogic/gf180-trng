#!/usr/bin/env python3
"""Declare, emit, run and read the sized mismatch Monte Carlo campaign (issue #1025).

T1 item 6 (analog) graded the committed mismatch campaign
``signoff/evidence/mc-yield/klt_yield_response.json`` ``unmet`` /
``undersized_sample``: 8 seeds on ``period_r1`` and 30 on ``dtrip_v`` against
the 183 draws the ``klt yield`` default target needs at zero failures, and no
``klt yield``-sense negative control. This tool is the sized campaign's single
declaration -- the same two testbenches, the same two DR-0033 PVT points, the
same measurement method, at the sample count the report itself asks for, plus
one seeded known-bad variant per measurement:

``ro-array-core-mc-freq`` (``period_r1``)
    ``request-mc-tt|ss.request.json`` -- nominal mismatch population, seeded.
    ``request-mc-control-tt|ss.request.json`` -- same corner, same seeds
    machinery, with ring 1's per-stage channel length fabricated long
    (``ro_lstv``; see the batch body's header): a deterministic slow-device
    defect the DR-0033 period ceiling must catch, imposed on a seeded
    mismatch population so the control is a distribution, not a point.

``sampler-dff-mc-offset`` (``dtrip_v``)
    ``request-mc-tt|ss.request.json`` -- nominal mismatch population, seeded.
    ``request-mc-control-tt|ss.request.json`` -- same corner, a forced -2.2 V
    input-referred threshold offset (``voff``; see the batch body's header)
    that pushes the master latch's switching threshold past the positive
    supply rail: the DR-0033 rail window must catch it. The control requests
    widen the .dc sweep window so the shifted crossing stays measurable; the
    limit is unchanged.

Sample sizing is read from the committed report, never hard-coded:
``required_n`` is the max of the four ``sample_size.required_n`` values and
the nominal draw is ``ceil(required_n * HEADROOM)`` rounded up to a multiple
of 5. ``HEADROOM`` = 1.2 is not arbitrary: at zero failures the verdict needs
``n >= ln(alpha/2)/ln(1-2h)`` (183 at the default target), and with k
failures the normal-approximation form ``z^2 p(1-p)/h^2`` takes over -- one
failure out of 183 needs 199, two need 345. A 1.2x draw (220) keeps the
verdict ``sufficient`` through one stray failure (174 <= 220); two failures
are a design finding this campaign records with its seed, not a sample count
it absorbs (per the issue's own instruction).

Sharding: every request declares ``batch.max_units_per_job`` so each fleet
job's conservative bound (``options.timeout_s x units + 120 s``) stays inside
the fleet's 3600 s whole-job ceiling (issues #974/#976): 14 units/job for the
transient bench (240 s units), 29 for the DC bench (120 s units). The fleet
is vCPU-budgeted, so every request also carries ``batch.capacity_wait_s`` =
600 (the same wait the host rules mandate on the command line).

Nothing here is run by ``sim/selftest.sh`` or CI: ``emit --check`` and the
offline tests in ``sim/tests/test_mc_yield_campaign.py`` are the CI surface;
``run``/``run-set`` submit to the batch fleet and are opt-in, one set at a
time. ``analyze`` reads the collected reports and prints the counts the
record and ``signoff/publish_item6.py`` consume.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "sim"))

from harness import klt_request as _kreq  # noqa: E402
from harness.corners import CORNERS as _CORNER_REGISTRY  # noqa: E402

#: Where the required sample count is read from: the committed klt yield
#: response this campaign sizes itself against (read-only).
YIELD_RESPONSE = REPO_ROOT / "signoff/evidence/mc-yield/klt_yield_response.json"
LIMITS_FILE = REPO_ROOT / "signoff/evidence/mc-yield/limits.json"

TB_DIRS = {
    "ro": REPO_ROOT / "sim/tb/ro-array-core-mc-freq",
    "sampler": REPO_ROOT / "sim/tb/sampler-dff-mc-offset",
}

#: DR-0033's two PVT points (issue #146's justified subset, unchanged): the
#: nominal baseline and DR-0015's measured entropy-binding worst corner.
PVT = {
    "tt": {"process": "tt", "temperature_c": 27, "vsup": 3.30},
    "ss": {"process": "ss", "temperature_c": 125, "vsup": 3.63},
}

#: One base seed per request, all distinct, all recorded here and echoed by
#: the fleet reports' ``environment.monte_carlo``. Derived per-sample seeds
#: are klt's SHA-256 seed contract (docs/cli/sim.md), not ours.
SEEDS = {
    ("ro", "tt"): 10250101,
    ("ro", "ss"): 10250102,
    ("ro", "control-tt"): 10250181,
    ("ro", "control-ss"): 10250182,
    ("sampler", "tt"): 10250201,
    ("sampler", "ss"): 10250202,
    ("sampler", "control-tt"): 10250281,
    ("sampler", "control-ss"): 10250282,
}

#: Known-bad knobs. ``RO_CONTROL_LSTV_M`` lengthens ring 1's per-stage
#: channel (2e-6 m as shipped) far enough that the mismatch-free period sits
#: well past both corners' DR-0033 ceiling (calibrated by the fleet probes
#: quoted in the campaign record); stated in meters because a corners.params
#: alterparam value is a bare number. ``SAM_VOFF_V`` shifts the measured
#: threshold past the rail by ~0.29 V (tt) / ~0.11 V (ss) -- a forced
#: input-referred offset, the negative-control form klt yield's own
#: documentation names.
RO_CONTROL_LSTV_M = 3.4e-6
SAM_VOFF_V = -2.2

#: Draws per nominal measurement = ceil(required_n * HEADROOM) rounded to a
#: multiple of 5 (see the module docstring for the one-stray-failure
#: arithmetic). The control draw is sized for detection, not precision: the
#: defect is engineered so every draw fails, and 30 all-failing draws give a
#: Clopper-Pearson interval of [0, 0.116] against the nominal's [0.980, 1.0]
#: at n=183+ -- disjoint by a wide margin.
HEADROOM = 1.2
N_CONTROL = 30

#: Per-unit timeouts and the fleet whole-job ceiling they are sharded against
#: (issues #974/#976: bound = timeout_s x units + 120 s <= 3600 s). The
#: transient bench measures 17-25 s/unit on an idle 8-core host and runs on
#: dedicated fleet workers; 240 s is a >=10x margin. The DC bench measures
#: well under a second; 120 s is a >=100x margin.
FLEET_CEILING_S = 3600
FLEET_OVERHEAD_S = 120
RO_TIMEOUT_S = 240
SAM_TIMEOUT_S = 120
CAPACITY_WAIT_S = 600

REQUESTS = {
    "ro": ("mc-tt", "mc-ss", "mc-control-tt", "mc-control-ss"),
    "sampler": ("mc-tt", "mc-ss", "mc-control-tt", "mc-control-ss"),
}


def required_n() -> int:
    """The sample count the committed klt yield report asks for.

    Max over the four measurements' ``sample_size.required_n`` -- they are
    all 183 today (zero failures, default target), but the campaign sizes
    itself against whatever the report says, not against a memory of it.
    """
    doc = json.loads(YIELD_RESPONSE.read_text())
    values = [m["sample_size"]["required_n"] for m in doc["measurements"]]
    return max(values)


def n_nominal() -> int:
    n = required_n() * HEADROOM
    return math.ceil(n / 5.0) * 5


def limits() -> dict:
    return json.loads(LIMITS_FILE.read_text())["measurements"]


def max_units_per_job(timeout_s: int) -> int:
    return int((FLEET_CEILING_S - FLEET_OVERHEAD_S) // timeout_s)


def shards(units: int, timeout_s: int) -> int:
    return math.ceil(units / max_units_per_job(timeout_s))


def _process(name: str) -> dict:
    corner = _CORNER_REGISTRY[name]
    return {"name": corner.name, "sections": list(corner.sections)}


def ro_measurements(vth: float) -> list[dict]:
    """The period/frequency cards, concrete ``val=`` per request.

    TRIG/TARG plus ``param=`` (ngspice's own arithmetic over .meas results)
    reproduces the harness fragment's four-period averaging exactly; a
    ``measurements[].expr`` cannot do it (ngspice keeps no control-block
    vector for a file-scope .meas result -- probed locally against
    ngspice-47, quoted in the campaign record).
    """
    return [
        {"name": "m_t4_r1", "spice": f".meas tran m_t4_r1 trig v(ro1) val={vth} rise=2 targ v(ro1) val={vth} rise=6", "unit": "s"},
        {"name": "m_period_r1", "spice": ".meas tran m_period_r1 param='m_t4_r1/4'", "unit": "s"},
        {"name": "m_t4_r2", "spice": f".meas tran m_t4_r2 trig v(ro2) val={vth} rise=2 targ v(ro2) val={vth} rise=6", "unit": "s"},
        {"name": "m_period_r2", "spice": ".meas tran m_period_r2 param='m_t4_r2/4'", "unit": "s"},
        {"name": "m_f_r1", "spice": ".meas tran m_f_r1 param='4/m_t4_r1'", "unit": "Hz"},
        {"name": "m_f_r2", "spice": ".meas tran m_f_r2 param='4/m_t4_r2'", "unit": "Hz"},
    ]


def sam_measurements(vhalf: float) -> list[dict]:
    return [
        {"name": "m_dtrip_v", "spice": f".meas dc m_dtrip_v when v(xdut.mb)={vhalf} fall=1", "unit": "V"},
    ]


def build_request(tb: str, name: str) -> dict:
    """One request: one PVT point, one seeded mismatch population."""
    corner_key = "tt" if name.endswith("tt") else "ss"
    control = name.startswith("mc-control")
    pvt = PVT[corner_key]
    lim = limits()
    timeout_s = RO_TIMEOUT_S if tb == "ro" else SAM_TIMEOUT_S
    n = N_CONTROL if control else n_nominal()
    req = {
        "_comment": (
            f"issue #1025 sized mismatch campaign, {tb} {name}: {n} seeded draws at "
            f"{pvt['process']}/{pvt['temperature_c']}C/{pvt['vsup']:.2f}V"
            + (" plus the deterministic known-bad defect (see the batch body's header)"
               if control else "")
            + ". Generated by sim/tools/mc_yield_campaign.py; do not edit by hand"
              " (`emit --check` fails if this drifts)."
        ),
        "netlist": "tb_ro_array_core_mc_freq_batch.sp" if tb == "ro" else "tb_sampler_dff_mc_offset_batch.sp",
        "engine": "ngspice",
        "models": {"pdk": "gf180mcuD", "lib": "libs.tech/ngspice/sm141064.ngspice"},
        "corners": {
            "process": [_process(pvt["process"])],
            "temperature_c": [pvt["temperature_c"]],
        },
        "monte_carlo": {
            "n": n,
            "seed": SEEDS[(tb, name.replace("mc-", ""))],
            "vary": "mismatch",
        },
        "batch": {
            "capacity_wait_s": CAPACITY_WAIT_S,
            "max_units_per_job": max_units_per_job(timeout_s),
        },
        "options": {
            "timeout_s": timeout_s,
            "keep_artifacts": False,
            "waveforms": False,
            "ngspice_init": ["set measureprec=12", "set numdgt=12"],
        },
    }
    # The mismatch switch is the body's .param (off); each sample turns it on
    # through an alterparam, so the deck's own Pelgrom model spreads under
    # klt's per-sample .options seed.
    req["corners"]["params"] = {"sw_stat_mismatch": [1]}

    if tb == "ro":
        vth = pvt["vsup"] / 2.0
        req["corners"]["supply_v"] = ({"vsup": [pvt["vsup"]]} if corner_key == "ss" else {})
        req["analysis"] = {"kind": "tran", "args": "1p 100n"}
        meas = ro_measurements(vth)
        period_max = lim[f"period_r1@{corner_key}_{'27c_3.30v' if corner_key == 'tt' else '125c_3.63v'}"]["max"]
        for m in meas:
            if m["name"] == "m_period_r1":
                m["limits"] = {"max": period_max}
        req["measurements"] = meas
        if control:
            req["corners"]["params"]["ro_lstv"] = [RO_CONTROL_LSTV_M]
    else:
        vhalf = pvt["vsup"] / 2.0
        supply: dict = {}
        if corner_key == "ss":
            supply["vdd"] = [pvt["vsup"]]
        if control:
            supply["voff"] = [SAM_VOFF_V]
        req["corners"]["supply_v"] = supply
        # The known-bad crossing sits at ~3.59 V (tt) / ~3.74 V (ss); the
        # nominal requests sweep to the corner's own supply, the control
        # requests sweep 2.5..5 V so the shifted crossing stays measurable.
        sweep_hi = 5.0 if control else pvt["vsup"]
        sweep_lo = 2.5 if control else 0.0
        step = (sweep_hi - sweep_lo) / 500.0
        req["analysis"] = {"kind": "dc", "args": f"vd {sweep_lo:g} {sweep_hi:g} {step:.4g}"}
        meas = sam_measurements(vhalf)
        key = f"dtrip_v@{corner_key}_{'27c_3.30v' if corner_key == 'tt' else '125c_3.63v'}"
        m_lim = dict(lim[key])
        m_lim.pop("exclusive_min", None)
        m_lim.pop("exclusive_max", None)
        meas[0]["limits"] = m_lim
        req["measurements"] = meas
    return req


def request_path(tb: str, name: str) -> Path:
    return TB_DIRS[tb] / f"{name}.request.json"


def all_requests() -> dict[tuple[str, str], dict]:
    return {(tb, name): build_request(tb, name) for tb, names in REQUESTS.items() for name in names}


render = lambda req: json.dumps(req, indent=2) + "\n"  # noqa: E731 -- matches the sibling tools' render hook


def plan_text() -> str:
    nn, rn = n_nominal(), required_n()
    lines = [
        f"Sized mismatch Monte Carlo campaign (issue #1025): required_n {rn} (read from",
        f"{YIELD_RESPONSE.relative_to(REPO_ROOT)}), nominal draw {nn} (x{HEADROOM} headroom, one stray failure tolerated),",
        f"control draw {N_CONTROL} (all-fail engineered defect; detection needs ~3 failures at n={N_CONTROL})",
        "",
        f"{'request':26} {'tb':8} {'PVT':20} {'n':>4} {'seed':>9} {'defect':24} {'units':>5} {'t/o':>4} {'shards':>6}",
    ]
    for (tb, name), req in all_requests().items():
        pvt = PVT["tt" if name.endswith("tt") else "ss"]
        control = name.startswith("mc-control")
        timeout = req["options"]["timeout_s"]
        defect = ""
        if control and tb == "ro":
            defect = f"ro_lstv={RO_CONTROL_LSTV_M:g}m"
        elif control:
            defect = f"voff={SAM_VOFF_V}V, sweep 2.5-5V"
        lines.append(
            f"{name:26} {tb:8} {pvt['process']}/{pvt['temperature_c']}C/{pvt['vsup']:.2f}V "
            f"{req['monte_carlo']['n']:4d} {req['monte_carlo']['seed']:9d} {defect:24} "
            f"{req['monte_carlo']['n']:5d} {timeout:4d} {shards(req['monte_carlo']['n'], timeout):6d}"
        )
    total = sum(r["monte_carlo"]["n"] for r in all_requests().values())
    lines += [
        f"total simulation units: {total}",
        "",
        f"fleet ceiling: bound = timeout_s x units_per_job + {FLEET_OVERHEAD_S}s <= {FLEET_CEILING_S}s"
        f" -> {max_units_per_job(RO_TIMEOUT_S)} units/job (ro, {RO_TIMEOUT_S}s),"
        f" {max_units_per_job(SAM_TIMEOUT_S)} units/job (sampler, {SAM_TIMEOUT_S}s)",
        f"capacity wait: {CAPACITY_WAIT_S}s per request (batch.capacity_wait_s; also pass --wait-for-capacity)",
        "",
        "Not run by CI or selftest. Submit one testbench's set at a time:",
        "  python3 sim/tools/mc_yield_campaign.py run-set ro --outdir DIR",
        "  python3 sim/tools/mc_yield_campaign.py run-set sampler --outdir DIR",
    ]
    return "\n".join(lines)


def cmd_emit(check: bool) -> int:
    return _kreq.emit_requests(
        ((request_path(tb, name), render(req)) for (tb, name), req in all_requests().items()),
        check, repo_root=REPO_ROOT,
        ok=lambda: print(f"ok: {sum(len(v) for v in REQUESTS.values())} requests match the declared campaign"))


def cmd_run(name: str, outdir: str, backend: str, klt_cmd: str = "klt") -> int:
    for tb, names in REQUESTS.items():
        if name in names:
            return _kreq.run_klt_request(outdir, name, request_path(tb, name), backend, klt_cmd)
    choices = ", ".join(n for names in REQUESTS.values() for n in names)
    print(f"unknown request {name!r}; choices: {choices}", file=sys.stderr)
    return 2


def cmd_run_set(tb: str, outdir: str, klt_cmd: str = "klt") -> int:
    """Submit one testbench's four requests as one batch-set (issue #2869).

    A whole set is a grid, so this never runs on the local backend (the
    shared-host rule; see sim/harness/klt_request.py). Exit 3 from a control
    member is expected -- every control draw fails its limit by design -- so
    klt's per-member exit statuses are reported, not folded away.
    """
    if tb not in REQUESTS:
        print(f"unknown testbench {tb!r}; choices: {', '.join(REQUESTS)}", file=sys.stderr)
        return 2
    import shlex
    import subprocess

    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    argv = [
        *shlex.split(klt_cmd), "sim", "--batch-set",
        *[str(request_path(tb, n)) for n in REQUESTS[tb]],
        "--wait-for-capacity", str(CAPACITY_WAIT_S),
        "-o", str(out), "--format", "json",
    ]
    print(shlex.join(argv))
    done = subprocess.run(argv, cwd=REPO_ROOT, capture_output=True, text=True)
    (out / "set.report.json").write_text(done.stdout)
    (out / "set.stderr.txt").write_text(done.stderr)
    print(f"klt sim --batch-set exit {done.returncode}; envelope: {out / 'set.report.json'}", file=sys.stderr)
    if done.stdout.strip():
        try:
            env = json.loads(done.stdout)
            for member in env.get("requests", []):
                stem = Path(member.get("request", "?")).stem
                print(f"  member {stem}: exit {member.get('exit_code')}, report {member.get('report')}")
        except ValueError:
            pass
    return done.returncode


def cmd_analyze(reports: list[str], as_json: bool) -> int:
    """Per report: seeds, draw counts, per-measurement pass/fail and spread.

    The counts here are what the record quotes and what
    signoff/publish_item6.py pins; this command only reads files.
    """
    out: dict[str, dict] = {}
    for path in reports:
        doc = json.loads(Path(path).read_text())
        mc = (doc.get("environment") or {}).get("monte_carlo") or {}
        per_measure: dict[str, dict] = {}
        rollup = {m["name"]: m for m in doc.get("measurements", [])}
        samples = [c for c in doc.get("corners", []) if c.get("monte_carlo")]
        for name, roll in rollup.items():
            values = []
            fails = 0
            for c in samples:
                for m in c.get("measurements", []):
                    if m["name"] == name:
                        if m.get("value") is None:
                            values.append(None)
                        else:
                            values.append(m["value"])
                            if m.get("status") == "fail":
                                fails += 1
            numeric = [v for v in values if v is not None]
            entry = {
                "n": len(numeric),
                "errored": values.count(None),
                "failed_limit": fails,
            }
            if numeric:
                mean = sum(numeric) / len(numeric)
                var = sum((v - mean) ** 2 for v in numeric) / (len(numeric) - 1) if len(numeric) > 1 else 0.0
                entry.update(min=min(numeric), max=max(numeric), mean=mean, stddev=var ** 0.5)
            per_measure[name] = entry
        out[path] = {
            "seed": mc.get("seed"),
            "declared_n": mc.get("n"),
            "mismatch_scale": mc.get("mismatch_scale"),
            "samples_seen": len(samples),
            "measurements": per_measure,
        }
    if as_json:
        print(json.dumps(out, indent=2))
        return 0
    for path, info in out.items():
        print(f"== {path}")
        print(f"   seed {info['seed']} declared_n {info['declared_n']} samples {info['samples_seen']}")
        for name, e in info["measurements"].items():
            stats = ""
            if "mean" in e:
                stats = f" mean {e['mean']:.6g} stddev {e['stddev']:.3g} min {e['min']:.6g} max {e['max']:.6g}"
            print(f"   {name:14} n {e['n']:4} errored {e['errored']} failed_limit {e['failed_limit']}{stats}")
    return 0


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
    s = sub.add_parser("run-set")
    s.add_argument("tb", choices=tuple(REQUESTS))
    s.add_argument("--outdir", required=True)
    s.add_argument("--klt", default="klt", dest="klt_cmd")
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
    if args.cmd == "run-set":
        return cmd_run_set(args.tb, args.outdir, args.klt_cmd)
    return cmd_analyze(args.reports, args.json)


if __name__ == "__main__":
    sys.exit(main())
