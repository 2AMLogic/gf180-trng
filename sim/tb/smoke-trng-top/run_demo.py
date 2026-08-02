#!/usr/bin/env python3
"""Top-level smoke demonstration (#27): the assembled `trng_top` chain,
driven end to end at one nominal corner.

This is a **behavioural-level** testbench (DR-0009): it does not invoke
ngspice itself and has no device model of its own. What makes it a
*nominal-corner* smoke test rather than an ordinary behavioural
demonstration is its input -- ``raw_source.raw_bits()`` reads the ten raw
bits ``sim/tb/sampler-array-digitize/`` already captured, at the nominal
corner (``tt`` / 27 C / 3.30 V), from the shipped entropy source (#7) and
the shipped sampler (#9) under ngspice transient noise. Everything
downstream of that (#8's conditioner, #11's health tests, #26's interface)
runs through the real block models in ``design/trng_top/trng_top.py``.

Ten bits is deliberately far short of a DR-0002 start-up window (1024
samples) or an APT window (1024 samples): per this issue's own curation,
the smoke test's job is proving the assembled chain produces bits end to
end, not re-verifying entropy quality or completing a start-up window --
those stay the constituent blocks' own, PVT-swept, testbenches (see
design/trng_top/README.md).

Usage (from the repo root)::

    python3 sim/tb/smoke-trng-top/run_demo.py             # write a record
    python3 sim/tb/smoke-trng-top/run_demo.py --no-write  # print only
"""

from __future__ import annotations

import argparse
import hashlib
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
sys.path.insert(0, str(REPO_ROOT / "design" / "trng_top"))
sys.path.insert(0, str(REPO_ROOT / "design" / "interface"))

from harness import report  # noqa: E402
import raw_source  # noqa: E402
import regmap  # noqa: E402
import trng_top as top  # noqa: E402

SLUG = "smoke-trng-top"


def _field(word: int, name: str) -> int:
    f = next(f for f in regmap.STATUS.fields if f.name == name)
    return (word >> f.lsb) & ((1 << f.width) - 1)


def run() -> dict:
    started = time.time()
    bits = raw_source.raw_bits()

    chain = top.TopLevel()
    for bit in bits:
        chain.step(raw_bit=bit, raw_valid=True)

    # One register-bus cycle, to demonstrate the bus wiring works too --
    # not a scenario of its own, just the smoke test's second signal path
    # (the first being the raw tap).
    status_out = chain.step(
        raw_bit=0, raw_valid=False,
        reg_sel=True, reg_write=False, reg_addr=regmap.STATUS.index, reg_wdata=0,
    )
    status = status_out.reg_rdata

    return {
        "raw_bits_driven": bits,
        "raw_bits_str": "".join(str(b) for b in bits),
        "cycles": chain.cycles,
        "raw_samples": chain.raw_samples,
        "data_words_available": len(chain.iface.cond_fifo),
        "raw_words_available": len(chain.iface.raw_fifo),
        "cond_words_offered": chain.cond.words_out,
        "health_test_rct_failures": chain.health.rct_failures,
        "health_test_apt_failures": chain.health.apt_failures,
        "health_test_startup_passes": chain.health.startup_passes,
        "status_final": f"0x{status:08x}",
        "status_ht_alarm": _field(status, "HT_ALARM"),
        "status_startup": _field(status, "STARTUP"),
        "status_cond_ready": _field(status, "COND_READY"),
        "wall_time_s": time.time() - started,
    }


def _frontmatter(stem: str, result: dict, git: dict, raw_files) -> str:
    tb_path = TB_DIR / "run_demo.py"
    model_path = REPO_ROOT / "design" / "trng_top" / "trng_top.py"
    xschem_path = REPO_ROOT / "design" / "xschem" / "trng_top.sch"
    netlist_path = REPO_ROOT / "design" / "trng_top.spice"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "---",
        f"record: {stem}",
        f"date: {now}",
        "status: valid",
        "",
        "level: behavioral (see spec/decision-records/"
        "DR-0009-behavioral-vs-transistor-verification-split.md) -- the "
        "raw-bit INPUT to this run is transistor-derived (see raw_input "
        "below); this run itself instantiates no device model",
        "",
        "testbench:",
        f"  path: sim/tb/{SLUG}/run_demo.py",
        f"  sha: {report.blob_sha(REPO_ROOT, tb_path)}",
        "netlist:",
        "  path: design/trng_top/trng_top.py",
        f"  sha: {report.blob_sha(REPO_ROOT, model_path)}",
        "  note: >-",
        "    Behavioral-level record: the DUT is the normative behavioural",
        "    top-level model (the three real digital block models, wired as",
        "    design/xschem/trng_top.sch's raw tap feeds them). The",
        "    synthesisable RTL design/trng_top/trng_top.v wires the same",
        "    three modules; sim/tests/test_trng_top.py checks both against",
        "    each other and against the analog side's pin names.",
        "",
        "analog_boundary:",
        "  schematic: design/xschem/trng_top.sch",
        f"  schematic_sha: {report.blob_sha(REPO_ROOT, xschem_path)}",
        "  netlist: design/trng_top.spice",
        f"  netlist_sha: {report.blob_sha(REPO_ROOT, netlist_path)}",
        "  note: >-",
        "    trng_top.sch instantiates sampler_core.sym (#7 entropy source +",
        "    #9 sampler) unmodified; design/netlist.py --check ties this",
        "    netlist to that schematic. Not re-simulated by this run -- see",
        "    raw_input below for the transistor-level evidence this run's",
        "    raw-bit stimulus comes from.",
        "",
        f"repo_commit: {report.repo_commit_field(git)}",
        "",
        "pdk: n/a (behavioral-level record -- no device models are instantiated "
        "by this run, per DR-0009)",
        "pdk.models:",
        "  - n/a (behavioral-level record)",
        "",
        "tool:",
        '  ngspice: "n/a (behavioral-level record -- ngspice is not invoked by '
        'this run; see raw_input for where it WAS invoked)"',
        f'  python: "{platform.python_version()} ({platform.python_implementation()})"',
        f"  platform: {platform.platform()}",
        "",
        "corner:",
        "  process: n/a (behavioral-level record -- no device models, so no "
        "process corner exists for THIS run; DR-0009 forbids citing this "
        "record for any P/V/T-dependent claim; see raw_input for the corner "
        "the cited transistor-level bits were captured at)",
        "  voltage: n/a (behavioral-level record)",
        "  temperature: n/a (behavioral-level record)",
        "",
        "analysis:",
        "  type: behavioral-top-level-smoke",
        f"  tstop: n/a (cycle-count driven: {result['cycles']} sampler clocks)",
        "  tstep: n/a",
        "  tmax: n/a",
        "  noise_params: n/a (no device noise in this run; the raw-bit input "
        "already carries whatever noise the cited transistor-level run injected)",
        "  runs: 1",
        "seeds: n/a (raw-bit input is a fixed, already-recorded capture, not "
        "re-seeded by this run; see raw_input.record for its own seeds)",
        "",
        "raw_input:",
        "  kind: transistor-derived (DR-0009 rule 4)",
        f"  record: sim/records/{raw_source.SOURCE_RECORD.name}",
        f"  record_sha: {report.blob_sha(REPO_ROOT, raw_source.SOURCE_RECORD)}",
        f"  corner.process: {raw_source.SOURCE_CORNER['process']}",
        f"  corner.temperature_c: {raw_source.SOURCE_CORNER['temperature_c']}",
        f"  corner.voltage_v: {raw_source.SOURCE_CORNER['voltage_v']}",
        f"  n_bits: {len(result['raw_bits_driven'])}",
        f"  bits: {result['raw_bits_str']}",
        "",
        "interface:",
        f"  registers: {', '.join(r.name for r in regmap.REGISTERS)}",
        f"  fifo_depth_words: {regmap.FIFO_DEPTH}",
        f"  raw_pack_bits: {regmap.RAW_PACK_BITS}",
        "",
        "raw:",
        f"  path: sim/records/raw/{stem}/",
        "  files:",
    ]
    for name, digest in raw_files:
        lines.append(f"    - {name}  sha256:{digest}")
    lines.append(f"wall_time: {result['wall_time_s']:.3f}s")
    lines.append("---")
    return "\n".join(lines)


def _body(result: dict) -> str:
    r = result
    rows = [
        ("raw bits driven (transistor-derived, nominal corner)", f"`{r['raw_bits_str']}`"),
        ("sampler-clock cycles run", f"{r['cycles']}"),
        ("raw samples absorbed", f"{r['raw_samples']}"),
        ("conditioned words offered by the conditioner", f"{r['cond_words_offered']}"),
        ("DATA words available", f"{r['data_words_available']}"),
        ("RAW_DATA words available", f"{r['raw_words_available']}"),
        ("health-test RCT failures", f"{r['health_test_rct_failures']}"),
        ("health-test APT failures", f"{r['health_test_apt_failures']}"),
        ("health-test start-up passes", f"{r['health_test_startup_passes']}"),
        ("final STATUS (register-bus read)", f"`{r['status_final']}`"),
        ("final STATUS.HT_ALARM", f"{r['status_ht_alarm']}"),
        ("final STATUS.STARTUP", f"{r['status_startup']}"),
        ("final STATUS.COND_READY", f"{r['status_cond_ready']}"),
    ]
    table = "\n".join(f"| {k} | {v} |" for k, v in rows)

    return f"""
## Result

| Quantity | Value |
|---|---|
{table}

## What this record is evidence about

That the five-block assembly this issue's Scope names -- entropy source
(#7), sampler (#9), conditioner (#8), health tests (#11), interface (#26) --
is wired correctly enough to produce bits end to end at one nominal corner:
a real transistor-derived raw bitstream, captured at `tt` / 27 C / 3.30 V,
drives the real conditioner and the real health-test model, whose real
outputs drive the real interface, whose register bus is also exercised (the
final `STATUS` read above). `STATUS.STARTUP` reading `1` and both FIFOs
reading empty are the *expected* outcome of ten raw samples against a
1024-sample start-up window, not a defect -- see Caveats.

It is **not** an entropy, rate, power, or timing claim (DR-0009 rule 3: this
record's own corner fields are `n/a`), and it does not complete a DR-0002
start-up window or produce a first conditioned/raw word -- both need many
more raw samples than ten, and both are exactly what
`sim/tb/interface-regfile/` and `sim/tb/health-test-fault-injection/`
already cover on their own declared-synthetic sources, at the length each
needs.

## How to reproduce

```sh
python3 sim/tb/{SLUG}/run_demo.py --no-write
```

Add `--record` (the default) to mint a new record. Records are append-only:
a re-run mints a new stem, it never overwrites this one.

## Caveats

- **Behavioral level, no corner of its own.** This run instantiates no
  device model, so it has no P/V/T point and must not be cited for any
  claim that depends on one (DR-0009 rule 3). The *input* it consumes does
  have a corner (`tt` / 27 C / 3.30 V) -- see `raw_input` above -- but that
  corner belongs to the cited record, not to this one.
- **Ten bits, on purpose.** This is far too short to trip the health tests'
  RCT (`C_RCT` = 81 identical samples) or APT (`C_APT` of 824 within a
  1024-sample window), or to complete the DR-0002 start-up test (1024
  clean samples) or a single 256-sample conditioner block. Nothing here
  claims otherwise; `health_test_startup_passes` reading `0` and both FIFOs
  reading empty are the correct outcome of a run this short, not a bug.
- **Not a re-simulation.** The ten raw bits are read out of
  `sim/records/2026-08-01-sampler-array-digitize-03.md`'s own committed
  Result section (see `raw_source.py`), not re-run through ngspice by this
  script. That record's own caveats (declared synthetic per-stage noise,
  a 100 MHz sample clock rather than DR-0003's 1 Mbps target, ten bits
  being too short for any statistical claim) apply to the input here
  exactly as they did there.
- **No new claim about any constituent block.** The conditioner, health
  tests and interface each already have their own behavioural
  demonstrations (`sim/tb/conditioner-crc32/`, `sim/tb/health-test-fault-injection/`,
  `sim/tb/interface-regfile/`) and the entropy source and sampler their own
  transistor-level PVT sweeps. This record's only new claim is that they
  are wired together correctly, per this issue's own curation.

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

    summary = {k: v for k, v in result.items()}
    (raw_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")

    raw_files = [(name, report.sha256_file(raw_dir / name)) for name in ("summary.json",)]

    path = records_dir / f"{stem}.md"
    if path.exists():  # pragma: no cover - allocate_record_stem prevents this
        raise report.RecordExists(f"{path} already exists")
    path.write_text(_frontmatter(stem, result, git, raw_files) + "\n" + _body(result))
    return path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-write", action="store_true",
        help="print the results without minting an evidence record",
    )
    parser.add_argument("--record", action="store_true", help="mint a record (the default)")
    args = parser.parse_args(argv)

    git = report.git_provenance(REPO_ROOT)
    records_dir = SIM_DIR / "records"

    result = run()
    print(f"raw bits driven: {result['raw_bits_str']}")
    print(
        f"cycles={result['cycles']} raw_samples={result['raw_samples']} "
        f"data_words={result['data_words_available']} raw_words={result['raw_words_available']}"
    )
    print(
        f"final STATUS {result['status_final']}  "
        f"alarm={result['status_ht_alarm']} startup={result['status_startup']} "
        f"cond_ready={result['status_cond_ready']}"
    )
    if not args.no_write:
        path = write_record(result, records_dir, git)
        print(f"record: {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
