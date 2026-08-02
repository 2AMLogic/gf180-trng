#!/usr/bin/env python3
"""Ring-liveness-monitor fault-injection demonstration: simulated per-ring
bitstreams in, per-ring stuck verdicts out.

This is a **behavioural-level** testbench (DR-0009), the fault-injection
verification DR-0016 asks for. It does not invoke ngspice and it has no P/V/T
corner: it drives the liveness-monitor model in
``design/health_test/ring_liveness.py`` from the declared synthetic sources
in ``ring_source_model.py`` and writes one append-only evidence record per
scenario under ``sim/records/``, in the ``sim/README.md`` format, with the
device-model fields explicitly ``n/a`` and a reason. Follows
``sim/tb/health-test-fault-injection/run_demo.py``'s pattern.

Usage (from the repo root)::

    python3 sim/tb/ring-liveness-fault-injection/run_demo.py             # write records
    python3 sim/tb/ring-liveness-fault-injection/run_demo.py --no-write  # print only
    python3 sim/tb/ring-liveness-fault-injection/run_demo.py --scenario ring1-stuck

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
from pathlib import Path

TB_DIR = Path(__file__).resolve().parent
SIM_DIR = TB_DIR.parents[1]
REPO_ROOT = SIM_DIR.parent

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(TB_DIR))
sys.path.insert(0, str(REPO_ROOT / "design" / "health_test"))

from harness import report  # noqa: E402
import ring_liveness as rl  # noqa: E402
import ring_source_model as source_model  # noqa: E402

SLUG = "ring-liveness-fault-injection"

N_RINGS = 2
LEAD_IN_BITS = 2000

SCENARIOS = {
    "healthy": {
        "kind": "no-alarm",
        "n_bits": 8 * rl.RingLivenessMonitor().c_live,  # several multiples of C_LIVE
        "seed": 40,
        "why": (
            "both rings healthy (declared IID, H = 1.0 bit/sample each) for "
            "several multiples of C_LIVE -- neither ring's watchdog should "
            "ever fire on a freely running source"
        ),
    },
    "ring1-stuck": {
        "kind": "onset-fault",
        "stuck_ring": 0,
        "lead_in_seed": 41,
        "fault_bits": None,  # filled at run time: c_live + 50
        "why": (
            "ring 1 (index 0) stops mid-stream while ring 2 keeps running -- "
            "the exact 'half the N=2 array silently dies' scenario DR-0010 "
            "raises the stakes on and design/README.md's 'Per-ring liveness' "
            "section names as invisible at the combined xo node"
        ),
    },
    "ring2-stuck": {
        "kind": "onset-fault",
        "stuck_ring": 1,
        "lead_in_seed": 42,
        "fault_bits": None,
        "why": (
            "the same fault as ring1-stuck, on the other ring -- confirms the "
            "monitor is symmetric across N_RINGS and not accidentally wired "
            "to only one channel"
        ),
    },
    "both-stuck": {
        "kind": "onset-fault-both",
        "lead_in_seed": 43,
        "fault_bits": None,
        "why": (
            "both rings stop at the same onset -- ring_stuck_any must still "
            "fire (and each individual ring_stuck bit), demonstrating the "
            "monitor does not depend on a surviving ring to detect the "
            "shared failure mode"
        ),
    },
}


def _dut() -> rl.RingLivenessMonitor:
    return rl.RingLivenessMonitor(n_rings=N_RINGS)


def _healthy_rows(seed_base: int, n_bits: int) -> list[list[int]]:
    ring_streams = [
        source_model.healthy_ring_bits(f"ring{r}", seed_base + r, n_bits)
        for r in range(N_RINGS)
    ]
    return [list(row) for row in zip(*ring_streams)]


def _run_no_alarm(spec: dict) -> dict:
    dut = _dut()
    n_bits = spec["n_bits"]
    rows = _healthy_rows(spec["seed"], n_bits)
    started = time.time()
    result = rl.run_stream(dut, rows)
    return {
        "kind": "no-alarm",
        "rows": rows,
        "n_bits": n_bits,
        "seed": spec["seed"],
        "c_live": dut.c_live,
        "n_rings": dut.n_rings,
        "per_ring_events": result["per_ring_events"],
        "any_events": result["any_events"],
        "no_alarm": not result["any_events"],
        "wall_time_s": time.time() - started,
    }


def _run_onset_fault(name: str, spec: dict) -> dict:
    dut = _dut()
    started = time.time()
    lead_in = _healthy_rows(spec["lead_in_seed"], LEAD_IN_BITS)
    onset = len(lead_in)
    stuck_ring = spec["stuck_ring"]
    fault_len = dut.c_live + 50
    # The stuck ring holds its last lead-in value forever (the physical
    # signature of a ring that stops oscillating: its digitized output
    # freezes at whatever level it last held); the other ring keeps running.
    frozen_value = lead_in[-1][stuck_ring]
    fault_stuck = source_model.stuck_ring_bits(frozen_value, fault_len)
    fault_other = source_model.healthy_ring_bits(f"{name}-other", spec["lead_in_seed"] + 100, fault_len)
    fault_rows = []
    for i in range(fault_len):
        row = [0] * N_RINGS
        for r in range(N_RINGS):
            row[r] = fault_stuck[i] if r == stuck_ring else fault_other[i]
        fault_rows.append(row)
    rows = lead_in + fault_rows
    result = rl.run_stream(dut, rows)

    stuck_events = result["per_ring_events"][stuck_ring]
    first_after_onset = next((i for i in stuck_events if i >= onset), None)
    latency = None if first_after_onset is None else first_after_onset - onset
    other_ring = 1 - stuck_ring if N_RINGS == 2 else None
    other_ring_ever_fired = bool(result["per_ring_events"][other_ring]) if other_ring is not None else None

    return {
        "kind": "onset-fault",
        "rows": rows,
        "onset": onset,
        "n_bits": len(rows),
        "c_live": dut.c_live,
        "n_rings": dut.n_rings,
        "stuck_ring": stuck_ring,
        "per_ring_events": result["per_ring_events"],
        "any_events": result["any_events"],
        "first_event_after_onset": first_after_onset,
        "detection_latency": latency,
        "latency_bound": dut.c_live - 1,
        "detected_within_bound": latency is not None and latency <= dut.c_live - 1,
        "other_ring_ever_fired": other_ring_ever_fired,
        "wall_time_s": time.time() - started,
    }


def _run_onset_fault_both(spec: dict) -> dict:
    dut = _dut()
    started = time.time()
    lead_in = _healthy_rows(spec["lead_in_seed"], LEAD_IN_BITS)
    onset = len(lead_in)
    fault_len = dut.c_live + 50
    frozen = lead_in[-1]
    fault_rows = [list(frozen) for _ in range(fault_len)]
    rows = lead_in + fault_rows
    result = rl.run_stream(dut, rows)

    per_ring_first = []
    for r in range(N_RINGS):
        events = result["per_ring_events"][r]
        first = next((i for i in events if i >= onset), None)
        per_ring_first.append(first)
    any_first = next((i for i in result["any_events"] if i >= onset), None)

    return {
        "kind": "onset-fault-both",
        "rows": rows,
        "onset": onset,
        "n_bits": len(rows),
        "c_live": dut.c_live,
        "n_rings": dut.n_rings,
        "per_ring_events": result["per_ring_events"],
        "any_events": result["any_events"],
        "per_ring_first_after_onset": per_ring_first,
        "any_first_after_onset": any_first,
        "latency_bound": dut.c_live - 1,
        "all_rings_detected_within_bound": all(
            f is not None and (f - onset) <= dut.c_live - 1 for f in per_ring_first
        ),
        "wall_time_s": time.time() - started,
    }


def run_scenario(name: str) -> dict:
    spec = SCENARIOS[name]
    if spec["kind"] == "no-alarm":
        result = _run_no_alarm(spec)
    elif spec["kind"] == "onset-fault":
        result = _run_onset_fault(name, spec)
    elif spec["kind"] == "onset-fault-both":
        result = _run_onset_fault_both(spec)
    else:  # pragma: no cover - defensive
        raise ValueError(f"unknown scenario kind {spec['kind']!r}")
    result["scenario"] = name
    result["why"] = spec["why"]
    return result


def _frontmatter(stem: str, result: dict, git: dict, raw_files) -> str:
    tb_path = TB_DIR / "run_demo.py"
    model_path = REPO_ROOT / "design" / "health_test" / "ring_liveness.py"
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
        "  path: design/health_test/ring_liveness.py",
        f"  sha: {report.blob_sha(REPO_ROOT, model_path)}",
        "  note: >-",
        "    Behavioral-level record: the DUT is the normative behavioural model,",
        "    not a schematic-derived netlist. The synthesisable RTL",
        "    design/health_test/ring_liveness.v is checked cycle-for-cycle against",
        "    this model by sim/tests/test_ring_liveness.py.",
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
        f"synthetic models in sim/tb/{SLUG}/ring_source_model.py)",
        "  runs: 1",
        f"seeds: [{result.get('seed', result.get('lead_in_seed', 'n/a'))}]   # SHA-256 "
        "counter-mode source, bit-identical on any platform",
        "",
        "ring_liveness:",
        f"  c_live: {result.get('c_live', 'n/a')}",
        f"  n_rings: {result.get('n_rings', 'n/a')}",
        "  cutoff_source: DR-0002's c_rct(H0=0.5) formula, reused (DR-0016) -- "
        "design/health_test/rct_apt.py",
        "",
        "input_source:",
        "  kind: declared synthetic per-ring bitstream (DR-0009 rule 4 -- no "
        "transistor-derived per-ring digitized bitstream is committed yet)",
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
            ("sampler-clock cycles driven", f"{r['n_bits']}"),
            ("rings monitored", f"{r['n_rings']}"),
            ("C_LIVE", f"{r['c_live']}"),
            ("per-ring stuck events", f"{[len(e) for e in r['per_ring_events']]}"),
            ("ring_stuck_any events", f"{len(r['any_events'])}"),
            ("no alarm over the whole run", f"{r['no_alarm']}"),
        ]
    elif r["kind"] == "onset-fault":
        rows = [
            ("lead-in + fault cycles total", f"{r['n_bits']}"),
            ("fault onset (sample index)", f"{r['onset']}"),
            ("stuck ring index", f"{r['stuck_ring']}"),
            ("C_LIVE", f"{r['c_live']}"),
            ("first ring_stuck event after onset (stuck ring)", f"{r['first_event_after_onset']}"),
            ("detection latency (samples after onset)", f"{r['detection_latency']}"),
            ("DR-0016 latency bound (C_LIVE - 1)", f"{r['latency_bound']}"),
            ("detected within bound", f"{r['detected_within_bound']}"),
            ("other (healthy) ring ever flagged stuck", f"{r['other_ring_ever_fired']}"),
        ]
    else:  # onset-fault-both
        rows = [
            ("lead-in + fault cycles total", f"{r['n_bits']}"),
            ("fault onset (sample index)", f"{r['onset']}"),
            ("C_LIVE", f"{r['c_live']}"),
            ("per-ring first event after onset", f"{r['per_ring_first_after_onset']}"),
            ("ring_stuck_any first event after onset", f"{r['any_first_after_onset']}"),
            ("DR-0016 latency bound (C_LIVE - 1)", f"{r['latency_bound']}"),
            ("all rings detected within bound", f"{r['all_rings_detected_within_bound']}"),
        ]

    table = "\n".join(f"| {k} | {v} |" for k, v in rows)

    return f"""
## Result

Scenario `{r['scenario']}` -- {r['why']}.

| Quantity | Value |
|---|---|
{table}

Numbers only. **This record makes no entropy claim about any physical
ring.** It demonstrates the liveness-monitor block's behaviour against
declared synthetic per-ring streams, per DR-0009.

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
  the declared source models in `sim/tb/{SLUG}/ring_source_model.py`. The
  healthy-ring model (IID, H = 1.0) is a declared, conservative modelling
  choice justified by phase aliasing (see `ring_source_model.py`'s docstring),
  not a measurement of any ring's real duty cycle -- none exists in this
  repository. The monitor's own C_LIVE cutoff does not depend on this choice:
  it is reused unchanged from DR-0002's C_RCT.
- **The "stuck ring" fault freezes at the ring's own last live value**, the
  physical signature of an oscillator that stops (design/README.md "Per-ring
  liveness": per-ring supply current collapses when this happens, per
  `sim/records/2026-08-01-ro-inv-05stage-stopped-leakage-*.md`), not an
  arbitrary constant.
- **The electrical tap that would produce `ring_bit` from a real ring's `ro1`/
  `ro2` node does not exist as shipped RTL/schematic yet.** DR-0016 bounds its
  cost in `sim/tb/ring-liveness-tap-power/` and records the remaining
  integration work as a follow-up (#65).

---

Written by `sim/tb/{SLUG}/run_demo.py`. Append-only: never edit or delete
this file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
"""


def write_record(result: dict, records_dir: Path, git: dict) -> Path:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stem = report.allocate_record_stem(records_dir, date, SLUG)
    raw_dir = records_dir / "raw" / stem
    raw_dir.mkdir(parents=True, exist_ok=True)

    summary = {k: v for k, v in result.items() if k != "rows"}
    (raw_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")

    raw_files = [(name, report.sha256_file(raw_dir / name)) for name in ("summary.json",)]

    if "rows" in result:
        packed = source_model.pack_lsb_first([bit for row in result["rows"] for bit in row])
        (raw_dir / "raw_rows.bin").write_bytes(packed)
        raw_files.append(("raw_rows.bin", report.sha256_file(raw_dir / "raw_rows.bin")))

    path = records_dir / f"{stem}.md"
    if path.exists():  # pragma: no cover - allocate_record_stem prevents this
        raise report.RecordExists(f"{path} already exists")
    path.write_text(_frontmatter(stem, result, git, raw_files) + "\n" + _body(result))
    return path


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
                f"   {result['n_bits']} cycles, per-ring events="
                f"{[len(e) for e in result['per_ring_events']]}, no_alarm={result['no_alarm']}"
            )
        elif result["kind"] == "onset-fault":
            print(
                f"   onset={result['onset']}, detection_latency={result['detection_latency']}, "
                f"bound={result['latency_bound']}, within_bound={result['detected_within_bound']}, "
                f"other_ring_ever_fired={result['other_ring_ever_fired']}"
            )
        else:
            print(
                f"   onset={result['onset']}, per_ring_first={result['per_ring_first_after_onset']}, "
                f"all_within_bound={result['all_rings_detected_within_bound']}"
            )
        if not args.no_write:
            path = write_record(result, records_dir, git)
            print(f"   record: {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
