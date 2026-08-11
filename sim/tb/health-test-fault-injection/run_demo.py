#!/usr/bin/env python3
"""Health-test fault-injection demonstration: simulated raw bitstream in,
RCT/APT/start-up verdicts out.

This is a **behavioural-level** testbench (DR-0009). It does not invoke
ngspice and it has no P/V/T corner: it drives the health-test model in
``design/health_test/rct_apt.py`` from the declared synthetic sources in
``fault_injection.py`` and writes one append-only evidence record per scenario
under ``sim/records/``, in the ``sim/README.md`` format, with the
device-model fields explicitly ``n/a`` and a reason. Follows
``sim/tb/conditioner-crc32/run_demo.py``'s pattern.

Usage (from the repo root)::

    python3 sim/tb/health-test-fault-injection/run_demo.py             # write records
    python3 sim/tb/health-test-fault-injection/run_demo.py --no-write  # print only
    python3 sim/tb/health-test-fault-injection/run_demo.py --scenario stuck-output

Scenarios are fixed in :data:`SCENARIOS` rather than taken from the command
line so that "re-run the demonstration" means exactly one thing.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

TB_DIR = Path(__file__).resolve().parent
SIM_DIR = TB_DIR.parents[1]
REPO_ROOT = SIM_DIR.parent

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(TB_DIR))
sys.path.insert(0, str(REPO_ROOT / "design" / "health_test"))

from harness import report  # noqa: E402
import rct_apt as ht  # noqa: E402
import fault_injection as source_model  # noqa: E402

SLUG = "health-test-fault-injection"

H0 = ht.H0  # DR-0002 draft H0 = 0.5, giving C_RCT=81, C_APT=824 at W=1024.

SCENARIOS = {
    "healthy": {
        "kind": "no-alarm",
        "n_bits": 4 * ht.W,  # 4 full APT windows
        "seed": 10,
        "h": str(H0),
        "why": (
            "the DR-0002 design target H0 = 0.5 bit/sample, run long enough to "
            "cover several full APT windows -- neither test should ever fire on "
            "a source whose declared min-entropy matches the assumption the "
            "cutoffs were derived from"
        ),
    },
    "false-positive-rate": {
        "kind": "false-positive",
        "n_windows": 4000,
        "seed": 11,
        "h": "0.5",
        "alpha": "0.05",
        "w": 64,
        "why": (
            "DR-0002 explicitly rules out observing a real alpha=2**-40 event "
            "in any feasible run, so this scenario recomputes C_APT at a "
            "deliberately inflated alpha (0.05, at a shortened W=64 window so "
            "thousands of windows are affordable) and checks the observed "
            "alarm rate against the binomial prediction"
        ),
    },
    "stuck-output": {
        "kind": "onset-fault",
        "lead_in_bits": 2000,
        "lead_in_seed": 20,
        "fault": {"generator": "constant_bits", "value": 1, "n_bits": 300},
        "latency_bound": "c_rct - 1",
        "why": (
            "DR-0002's first detection-latency target: a stuck raw output "
            "must be detected within C_RCT samples of onset"
        ),
    },
    "heavily-biased": {
        "kind": "onset-fault",
        "lead_in_bits": 2000,
        "lead_in_seed": 21,
        "fault": {"generator": "biased_bits", "seed": 210, "h": "0.05", "n_bits_multiple_of_w": 4},
        "latency_bound": "2*w - 1",
        "why": (
            "DR-0002's second detection-latency target: a heavily biased "
            "stream (declared H=0.05, near the APT degeneracy floor but still "
            "valid) must be detected within 2*W samples of onset, since the "
            "bias may begin mid-window"
        ),
    },
    "injection-locked": {
        "kind": "onset-fault",
        "lead_in_bits": 2000,
        "lead_in_seed": 22,
        "fault": {"generator": "oscillator_lockup_bits", "half_period": 2000, "n_bits_multiple_of_w": 4},
        "latency_bound": "2*w - 1",
        "why": (
            "DR-0002 groups 'heavily biased stream / injection-locked source' "
            "under the same 2*W latency target -- a locked pair of rings "
            "presents the combined node as a long deterministic run rather "
            "than a per-sample independent bit"
        ),
    },
    "startup-gate": {
        "kind": "startup-gate",
        "seed": 30,
        "h": "0.5",
        "why": (
            "DR-0002 Sec.4: an RCT/APT failure must reset the start-up "
            "counter, and startup_req must discard any in-flight window and "
            "re-arm it -- ht_startup_pass must only ever pulse after a full "
            "STARTUP_SAMPLES run with neither test failing"
        ),
    },
}


def _dut(**overrides) -> ht.HealthTest:
    kwargs = dict(c_rct=ht.c_rct(H0), c_apt=ht.c_apt(H0), w=ht.W, startup_samples=ht.W)
    kwargs.update(overrides)
    return ht.HealthTest(**kwargs)


def _run_no_alarm(spec: dict) -> dict:
    dut = _dut()
    bits, p_one, threshold = source_model.biased_bits(
        "healthy", spec["seed"], spec["n_bits"], spec["h"]
    )
    started = time.time()
    result = ht.run_stream(dut, bits)
    return {
        "kind": "no-alarm",
        "bits": bits,
        "n_bits": len(bits),
        "seed": spec["seed"],
        "declared_h": spec["h"],
        "p_one_target": p_one,
        "threshold_u32": threshold,
        "c_rct": dut.c_rct,
        "c_apt": dut.c_apt,
        "w": dut.w,
        "rct_events": result["rct_events"],
        "apt_events": result["apt_events"],
        "startup_events": result["startup_events"],
        "no_alarm": not result["rct_events"] and not result["apt_events"],
        "wall_time_s": time.time() - started,
    }


def _run_false_positive(spec: dict) -> dict:
    alpha = Decimal(spec["alpha"])
    w = spec["w"]
    h = Decimal(spec["h"])
    c_apt_loose = ht.c_apt(h, alpha=alpha, w=w)
    dut = ht.HealthTest(c_rct=w + 1, c_apt=c_apt_loose, w=w)  # RCT effectively disabled
    n_bits = spec["n_windows"] * w
    started = time.time()
    bits, p_one, threshold = source_model.biased_bits("false-positive", spec["seed"], n_bits, h)
    result = ht.run_stream(dut, bits)
    observed_rate = len(result["apt_events"]) / spec["n_windows"]
    tail_at_cutoff = ht.apt_tail_probability(c_apt_loose, h, w)
    return {
        "kind": "false-positive",
        "bits": bits,
        "n_bits": n_bits,
        "n_windows": spec["n_windows"],
        "seed": spec["seed"],
        "declared_h": str(h),
        "alpha": str(alpha),
        "w": w,
        "c_apt": c_apt_loose,
        "tail_probability_at_cutoff": tail_at_cutoff,
        "apt_events": result["apt_events"],
        "observed_alarm_rate": observed_rate,
        "wall_time_s": time.time() - started,
    }


def _make_fault_bits(fault: dict, w: int):
    gen = fault["generator"]
    if gen == "constant_bits":
        return source_model.constant_bits(fault["value"], fault["n_bits"])
    if gen == "biased_bits":
        n_bits = fault.get("n_bits") or fault["n_bits_multiple_of_w"] * w
        bits, _, _ = source_model.biased_bits(
            "fault", fault["seed"], n_bits, fault["h"]
        )
        return bits
    if gen == "oscillator_lockup_bits":
        n_bits = fault.get("n_bits") or fault["n_bits_multiple_of_w"] * w
        return source_model.oscillator_lockup_bits(n_bits, half_period=fault["half_period"])
    raise ValueError(f"unknown fault generator {gen!r}")


def _run_onset_fault(name: str, spec: dict) -> dict:
    dut = _dut()
    started = time.time()
    lead_in, _, _ = source_model.biased_bits(
        f"{name}-lead-in", spec["lead_in_seed"], spec["lead_in_bits"], H0
    )
    onset = len(lead_in)
    fault_bits = _make_fault_bits(spec["fault"], dut.w)
    bits = lead_in + fault_bits
    result = ht.run_stream(dut, bits)

    all_events = sorted(result["rct_events"] + result["apt_events"])
    first_after_onset = next((i for i in all_events if i >= onset), None)
    latency = None if first_after_onset is None else first_after_onset - onset
    bound = eval(spec["latency_bound"], {}, {"c_rct": dut.c_rct, "w": dut.w})  # noqa: S307

    return {
        "kind": "onset-fault",
        "bits": bits,
        "onset": onset,
        "n_bits": len(bits),
        "c_rct": dut.c_rct,
        "c_apt": dut.c_apt,
        "w": dut.w,
        "fault": spec["fault"],
        "rct_events": result["rct_events"],
        "apt_events": result["apt_events"],
        "first_event_after_onset": first_after_onset,
        "detection_latency": latency,
        "latency_bound_expr": spec["latency_bound"],
        "latency_bound": bound,
        "detected_within_bound": latency is not None and latency <= bound,
        "wall_time_s": time.time() - started,
    }


def _run_startup_gate(spec: dict) -> dict:
    started = time.time()
    dut = _dut()
    events = []

    # Phase 1: a clean start-up window of exactly W samples should pulse
    # ht_startup_pass exactly once, at the last sample.
    clean, _, _ = source_model.biased_bits("startup-clean", spec["seed"], dut.w, spec["h"])
    phase1 = ht.run_stream(dut, clean)
    events.append({"phase": "clean-startup-window", **phase1})
    startup_passed_cleanly = phase1["startup_events"] == [dut.w - 1]

    # Phase 2: an RCT failure mid-window must reset the start-up counter. The
    # trailing clean run after the failure is kept well short of
    # startup_samples so a pass here could only happen if the reset did not
    # take -- a direct check on the counter value itself (not just "no event
    # yet") follows immediately after the stuck run.
    dut2 = _dut()
    pre_fail, _, _ = source_model.biased_bits("startup-prefail", spec["seed"] + 1, 50, spec["h"])
    stuck = source_model.constant_bits(1, dut2.c_rct + 5)
    for bit in pre_fail + stuck:
        dut2.step(raw_bit=bit, raw_valid=True)
    startup_count_after_failure = dut2.startup_count
    rct_failures_in_stuck_run = dut2.rct_failures
    post_fail, _, _ = source_model.biased_bits(
        "startup-postfail", spec["seed"] + 2, 50, spec["h"]
    )
    phase2_tail_passes = [dut2.step(raw_bit=bit, raw_valid=True)[2] for bit in post_fail]
    phase2 = {
        "rct_failures": rct_failures_in_stuck_run,
        "startup_events": [i for i, passed in enumerate(phase2_tail_passes) if passed],
        "startup_count_after_failure": startup_count_after_failure,
    }
    events.append({"phase": "mid-window-failure", **phase2})
    startup_counter_was_reset_by_failure = (
        rct_failures_in_stuck_run > 0
        and startup_count_after_failure < dut2.w
        and phase2["startup_events"] == []
    )

    # Phase 3: startup_req discards an in-flight window; a fresh, full,
    # clean window after the restart must still pass.
    dut3 = _dut()
    partial, _, _ = source_model.biased_bits("startup-partial", spec["seed"] + 3, 100, spec["h"])
    for bit in partial:
        dut3.step(raw_bit=bit, raw_valid=True)
    pos_before_restart = dut3.apt_pos
    dut3.step(startup_req=True)
    pos_after_restart = dut3.apt_pos
    fresh, _, _ = source_model.biased_bits("startup-fresh", spec["seed"] + 4, dut3.w, spec["h"])
    phase3_passes = []
    for bit in fresh:
        _, _, startup_pass = dut3.step(raw_bit=bit, raw_valid=True)
        phase3_passes.append(startup_pass)
    restart_discarded_the_window = pos_before_restart > 0 and pos_after_restart == 0
    fresh_window_passed = phase3_passes.count(True) == 1 and phase3_passes[-1] is True

    n_bits = (
        len(clean)
        + len(pre_fail) + len(stuck) + len(post_fail)
        + len(partial) + 1 + len(fresh)  # +1 for the startup_req cycle itself
    )

    return {
        "kind": "startup-gate",
        "n_bits": n_bits,
        "declared_h": spec["h"],
        "seed": spec["seed"],
        "c_rct": dut.c_rct,
        "c_apt": dut.c_apt,
        "w": dut.w,
        "startup_passed_cleanly": startup_passed_cleanly,
        "startup_counter_was_reset_by_failure": startup_counter_was_reset_by_failure,
        "restart_discarded_the_window": restart_discarded_the_window,
        "fresh_window_passed_after_restart": fresh_window_passed,
        "phase1_startup_events": phase1["startup_events"],
        "phase2_startup_events": phase2["startup_events"],
        "phase2_rct_failures": phase2["rct_failures"],
        "wall_time_s": time.time() - started,
    }


def run_scenario(name: str) -> dict:
    spec = SCENARIOS[name]
    if spec["kind"] == "no-alarm":
        result = _run_no_alarm(spec)
    elif spec["kind"] == "false-positive":
        result = _run_false_positive(spec)
    elif spec["kind"] == "onset-fault":
        result = _run_onset_fault(name, spec)
    elif spec["kind"] == "startup-gate":
        result = _run_startup_gate(spec)
    else:  # pragma: no cover - defensive
        raise ValueError(f"unknown scenario kind {spec['kind']!r}")
    result["scenario"] = name
    result["why"] = spec["why"]
    return result


def _frontmatter(stem: str, result: dict, git: dict, raw_files) -> str:
    tb_path = TB_DIR / "run_demo.py"
    model_path = REPO_ROOT / "design" / "health_test" / "rct_apt.py"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "---",
        f"record: {stem}",
        f"date: {now}",
        "status: valid",
        "",
        "level: behavioral (see spec/decision-records/"
        "DR-0009-behavioral-vs-transistor-verification-split.md)",
        "",
        "testbench:",
        f"  path: sim/tb/{SLUG}/run_demo.py",
        f"  sha: {report.blob_sha(REPO_ROOT, tb_path)}",
        "netlist:",
        "  path: design/health_test/rct_apt.py",
        f"  sha: {report.blob_sha(REPO_ROOT, model_path)}",
        "  note: >-",
        "    Behavioral-level record: the DUT is the normative behavioural model,",
        "    not a schematic-derived netlist. The synthesisable RTL",
        "    design/health_test/rct_apt.v is checked cycle-for-cycle against this",
        "    model by sim/tests/test_health_test.py.",
        f"repo_commit: {report.repo_commit_field(git)}",
        "",
        "pdk: n/a (behavioral-level record -- no device models are instantiated, "
        "per DR-0009)",
        "pdk.models:",
        "  - n/a (behavioral-level record)",
        "",
        "tool:",
        '  ngspice: "n/a (behavioral-level record -- ngspice is not invoked)"',
        f'  python: "{platform.python_version()} ({platform.python_implementation()})"',
        f"  platform: {platform.platform()}",
        "",
        "corner:",
        "  process: n/a (behavioral-level record -- no device models, so no process "
        "corner exists; DR-0009 forbids citing this record for any P/V/T-dependent "
        "claim)",
        "  voltage: n/a (behavioral-level record)",
        "  temperature: n/a (behavioral-level record)",
        "",
        "analysis:",
        "  type: behavioral-bitstream",
        f"  tstop: n/a (cycle-count driven: {result.get('n_bits', 'n/a')} sampler clocks)",
        "  tstep: n/a",
        "  tmax: n/a",
        "  noise_params: n/a (no device noise -- the source is one of the declared "
        f"synthetic models in sim/tb/{SLUG}/fault_injection.py)",
        "  runs: 1",
        f"seeds: [{result.get('seed', 'n/a')}]   # SHA-256 counter-mode source, "
        "bit-identical on any platform",
        "",
        "health_test:",
        f"  c_rct: {result.get('c_rct', 'n/a')}",
        f"  c_apt: {result.get('c_apt', 'n/a')}",
        f"  w: {result.get('w', 'n/a')}",
        "  cutoff_source: DR-0002 formulas at H0 = 0.5 (design/health_test/rct_apt.py)",
        "",
        "input_source:",
        "  kind: declared synthetic (DR-0009 rule 4 -- no transistor-derived raw "
        "bitstream is committed yet)",
        f"  declared_min_entropy_per_sample: {result.get('declared_h', 'n/a')}",
        "",
        "raw:",
        f"  path: sim/records/raw/{stem}/",
        "  files:",
    ]
    for name, digest in raw_files:
        lines.append(f"    - {name}  sha256:{digest}")
    lines.append(f"wall_time: {result['wall_time_s']:.1f}s")
    lines.append("---")
    return "\n".join(lines)


def _body(result: dict) -> str:
    r = result
    rows: list[tuple[str, str]]

    if r["kind"] == "no-alarm":
        rows = [
            ("raw bits driven", f"{r['n_bits']}"),
            ("declared H", f"{r['declared_h']} bit/sample"),
            ("C_RCT / C_APT / W", f"{r['c_rct']} / {r['c_apt']} / {r['w']}"),
            ("RCT failures", f"{len(r['rct_events'])}"),
            ("APT failures", f"{len(r['apt_events'])}"),
            ("start-up passes", f"{len(r['startup_events'])}"),
            ("no alarm over the whole run", f"{r['no_alarm']}"),
        ]
    elif r["kind"] == "false-positive":
        rows = [
            ("windows driven", f"{r['n_windows']}"),
            ("declared H", f"{r['declared_h']} bit/sample"),
            ("inflated alpha", f"{r['alpha']}"),
            ("shortened window W", f"{r['w']}"),
            ("recomputed C_APT at this alpha/W/H", f"{r['c_apt']}"),
            ("exact tail probability at C_APT", f"{r['tail_probability_at_cutoff']:.6e}"),
            ("observed alarm rate", f"{r['observed_alarm_rate']:.6f}"),
            ("APT alarms observed", f"{len(r['apt_events'])} of {r['n_windows']} windows"),
        ]
    elif r["kind"] == "onset-fault":
        rows = [
            ("lead-in + fault bits total", f"{r['n_bits']}"),
            ("fault onset (sample index)", f"{r['onset']}"),
            ("fault generator", f"`{r['fault']['generator']}`"),
            ("C_RCT / C_APT / W", f"{r['c_rct']} / {r['c_apt']} / {r['w']}"),
            ("first event index after onset", f"{r['first_event_after_onset']}"),
            ("detection latency (samples after onset)", f"{r['detection_latency']}"),
            ("DR-0002 latency bound", f"{r['latency_bound_expr']} = {r['latency_bound']}"),
            ("detected within bound", f"{r['detected_within_bound']}"),
        ]
    else:  # startup-gate
        rows = [
            ("C_RCT / C_APT / W", f"{r['c_rct']} / {r['c_apt']} / {r['w']}"),
            ("clean W-sample window passes start-up", f"{r['startup_passed_cleanly']}"),
            ("mid-window RCT failure resets the start-up counter", f"{r['startup_counter_was_reset_by_failure']}"),
            ("startup_req discards the in-flight window", f"{r['restart_discarded_the_window']}"),
            ("a fresh full window after restart passes", f"{r['fresh_window_passed_after_restart']}"),
        ]

    table = "\n".join(f"| {k} | {v} |" for k, v in rows)

    return f"""
## Result

Scenario `{r['scenario']}` -- {r['why']}.

| Quantity | Value |
|---|---|
{table}

Numbers only. **This record makes no entropy claim about any physical
source.** It demonstrates the health-test block's behaviour against a
declared synthetic stream, per DR-0009.

## How to reproduce

```sh
python3 sim/tb/{SLUG}/run_demo.py --scenario {r['scenario']} --no-write
```

Add `--record` (the default) to mint a new record. Records are append-only:
a re-run mints a new stem, it never overwrites this one.

## Caveats

- **Behavioral level, no corner.** No device models are instantiated, so this
  record has no process/voltage/temperature point and must not be cited for
  any claim that depends on one (DR-0009).
- **Synthetic source, not a sampled ring oscillator.** The input is one of
  the declared source models in `sim/tb/{SLUG}/fault_injection.py`, chosen
  because its properties (min-entropy, stuck value, lock-up half-period) are
  known exactly. A jitter-sampled RO array is neither IID nor stationary
  across corners, and #9/#12/#13 own the real raw stream and its min-entropy.
- **The cutoffs are the DR-0002 draft H0 = 0.5 values**, not a ratified
  worst-corner H (#13's still-open deliverable). `design/health_test/rct_apt.py`
  computes them from H as a parameter, not as hard-coded constants, so a
  ratified H is a one-argument change away.
- **The `false-positive-rate` scenario does not measure alpha=2**-40.**
  DR-0002 explicitly rules that out as infeasible; this scenario recomputes
  the cutoff at a deliberately inflated alpha where the predicted rate is
  observable in a feasible sample count, and checks the mechanism, not the
  ratified alpha.

---

Written by `sim/tb/{SLUG}/run_demo.py`. Append-only: never edit or delete
this file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
"""


def write_record(result: dict, records_dir: Path, git: dict) -> Path:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def render(stem: str, raw_dir: Path) -> str:
        summary = {k: v for k, v in result.items() if k != "bits"}
        (raw_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")

        raw_files = [(name, report.sha256_file(raw_dir / name)) for name in ("summary.json",)]

        if "bits" in result:
            raw_bytes = source_model.pack_lsb_first(result["bits"])
            (raw_dir / "raw_bits.bin").write_bytes(raw_bytes)
            raw_files.append(("raw_bits.bin", report.sha256_file(raw_dir / "raw_bits.bin")))

        return _frontmatter(stem, result, git, raw_files) + "\n" + _body(result)

    return report.finalize_record(records_dir, date, SLUG, render)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        action="append",
        choices=sorted(SCENARIOS),
        help="run only this scenario (repeatable); default is all of them",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="print the results without minting evidence records",
    )
    parser.add_argument("--record", action="store_true", help="mint records (the default)")
    args = parser.parse_args(argv)

    names = args.scenario or list(SCENARIOS)
    git = report.git_provenance(REPO_ROOT)
    records_dir = SIM_DIR / "records"

    for name in names:
        result = run_scenario(name)
        print(f"== {name} ==")
        print(f"   {result['why']}")
        if result["kind"] == "no-alarm":
            print(
                f"   {result['n_bits']} bits, RCT failures={len(result['rct_events'])}, "
                f"APT failures={len(result['apt_events'])}, no_alarm={result['no_alarm']}"
            )
        elif result["kind"] == "false-positive":
            print(
                f"   C_APT={result['c_apt']} at alpha={result['alpha']}, "
                f"observed rate={result['observed_alarm_rate']:.6f}, "
                f"tail@cutoff={result['tail_probability_at_cutoff']:.3e}"
            )
        elif result["kind"] == "onset-fault":
            print(
                f"   onset={result['onset']}, detection_latency={result['detection_latency']}, "
                f"bound={result['latency_bound']}, within_bound={result['detected_within_bound']}"
            )
        else:
            print(
                f"   clean_pass={result['startup_passed_cleanly']}, "
                f"failure_resets={result['startup_counter_was_reset_by_failure']}, "
                f"restart_discards={result['restart_discarded_the_window']}, "
                f"fresh_after_restart={result['fresh_window_passed_after_restart']}"
            )
        if not args.no_write:
            path = write_record(result, records_dir, git)
            print(f"   record: {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
