#!/usr/bin/env python3
"""Interface/register-block demonstration: raw tap in, DATA/RAW_DATA out.

This is a **behavioural-level** testbench (DR-0009). It does not invoke
ngspice and it has no P/V/T corner. It wires the two digital blocks together
exactly as `trng_top` (#27) will:

    declared synthetic raw source  -->  trng_conditioner_crc32 (#8, DR-0008)
                 |                              |
                 +---------------> trng_interface (#26, DR-0013) --> DATA
                                    ^   |                        --> RAW_DATA
                          cond_en / cond_flush                   --> streaming

and drives the scenarios DR-0013 argues about: the start-up gate, a
health-test failure and its recovery, an `OUT_MODE` switch, and a FIFO
overrun. The conditioner's `en`/`flush` come from the interface's own outputs
in the same cycle (`Interface.peek_control`), so what runs here is the real
inter-block contract rather than a scripted approximation of it.

Usage (from the repo root)::

    python3 sim/tb/interface-regfile/run_demo.py             # write records
    python3 sim/tb/interface-regfile/run_demo.py --no-write  # print only
    python3 sim/tb/interface-regfile/run_demo.py --scenario ht-gate

Scenarios are fixed in :data:`SCENARIOS` rather than taken from the command
line so that "re-run the demonstration" means exactly one thing.
"""

from __future__ import annotations

import argparse
import hashlib
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
sys.path.insert(0, str(SIM_DIR / "tb" / "conditioner-crc32"))
sys.path.insert(0, str(REPO_ROOT / "design" / "conditioner"))
sys.path.insert(0, str(REPO_ROOT / "design" / "interface"))

from harness import report  # noqa: E402
import crc32_conditioner as cond  # noqa: E402
import regmap  # noqa: E402
import source_model  # noqa: E402
import trng_interface as iface  # noqa: E402

SLUG = "interface-regfile"

#: The DR-0002 start-up health test observes 1024 consecutive raw samples.
STARTUP_SAMPLES = 1024

#: Declared per-sample min-entropy of the synthetic raw source. The design
#: target of DR-0002 / DR-0007; it is an input parameter here, never a result.
DECLARED_H = "0.5"

SCENARIOS = {
    "startup": {
        "samples": 4096,
        "seed": 1,
        "why": (
            "power-on: DR-0002's start-up health test gates the conditioned "
            "path while the raw path runs from the first sample, and "
            "STATUS distinguishes 'starting up' from 'failed'"
        ),
    },
    "ht-gate": {
        "samples": 8192,
        "seed": 2,
        "fail_at": 3000,
        "clear_at": 3500,
        "why": (
            "DR-0002's latch-and-gate: a failure latches HT_FAIL_*, flushes "
            "the conditioned FIFO and deasserts streaming valid, while "
            "RAW_DATA keeps working; recovery needs an explicit "
            "write-1-to-clear plus a fresh start-up-test pass"
        ),
    },
    "mode-switch": {
        "samples": 8192,
        "seed": 3,
        "mode_switch_at": [3000, 5000],
        "why": (
            "DR-0001 §2's flush rule: switching OUT_MODE in either direction "
            "flushes the conditioner and both output FIFOs, so no bit "
            "produced before the switch is readable after it"
        ),
    },
    "overrun": {
        "samples": 8192,
        "seed": 4,
        "drain": False,
        "why": (
            "a consumer that stops reading: the FIFOs drop the *incoming* "
            "word rather than a buffered one, so what survives is a "
            "contiguous run, and OVF_* is what tells a reader the run ended "
            "-- the hazard DR-0001 named when it rejected register-only raw "
            "access for the SP 800-90B sequential dataset"
        ),
    },
}


class Chain:
    """The conditioner and the interface, wired as `trng_top` will wire them."""

    def __init__(self) -> None:
        self.cond = cond.Conditioner()
        self.iface = iface.Interface()
        self.data_words: list[int] = []
        self.raw_words: list[int] = []
        self.startup_countdown = STARTUP_SAMPLES
        self.startups = 0
        self.first_data_cycle: int | None = None
        self.first_data_raw_samples: int | None = None
        self.cycle = 0
        self.raw_samples = 0

    def step(self, raw_bit: int, raw_valid: bool = True, **bus) -> iface.Outputs:
        """One sampler clock. ``bus`` carries the register-bus stimulus."""
        self.cycle += 1
        if raw_valid:
            self.raw_samples += 1

        # The health-test block (#11) is not built yet, so this stands in for
        # exactly the part of it this block contracts with: it counts 1024
        # consecutive raw samples after each `startup_req` and then pulses
        # `ht_startup_pass`. It runs no RCT/APT of its own -- failures are
        # injected by the scenario.
        startup_pass = False
        if self.startup_countdown > 0 and raw_valid:
            self.startup_countdown -= 1
            if self.startup_countdown == 0:
                startup_pass = True

        cond_en, cond_flush, _ = self.iface.peek_control(**bus)
        cond_word, cond_valid = self.cond.step(
            raw_bit=raw_bit, raw_valid=raw_valid, en=cond_en, flush=cond_flush
        )
        out = self.iface.step(
            raw_bit=raw_bit,
            raw_valid=raw_valid,
            cond_word=cond_word,
            cond_valid=cond_valid,
            ht_startup_pass=startup_pass,
            **bus,
        )
        if out.startup_req:
            self.startup_countdown = STARTUP_SAMPLES
            self.startups += 1
        if self.first_data_cycle is None and self.iface.cond_fifo:
            self.first_data_cycle = self.cycle
            self.first_data_raw_samples = self.raw_samples
        return out

    def drain(self) -> None:
        """Read one word from whichever FIFO has one.

        A bus cycle with no new raw sample: the whole chain is still clocked,
        because in hardware the conditioner and this block share the sampler
        clock whether or not a sample arrives.
        """
        if self.iface.cond_fifo and self.iface.cond_ready:
            register = regmap.DATA
            sink = self.data_words
        elif self.iface.raw_fifo:
            register = regmap.RAW_DATA
            sink = self.raw_words
        else:
            return
        out = self.step(
            0, raw_valid=False,
            reg_sel=True, reg_write=False, reg_addr=register.index, reg_wdata=0,
        )
        sink.append(out.reg_rdata)


def _status(chain: Chain) -> int:
    return chain.iface.status_value()


def _field(word: int, name: str) -> int:
    f = next(f for f in regmap.STATUS.fields if f.name == name)
    return (word >> f.lsb) & ((1 << f.width) - 1)


def run_scenario(name: str) -> dict:
    spec = SCENARIOS[name]
    started = time.time()

    raw_bits, p_one_target, threshold = source_model.biased_bits(
        f"{SLUG}-{name}", spec["seed"], spec["samples"], Decimal(DECLARED_H)
    )

    chain = Chain()
    drain = spec.get("drain", True)
    fail_at = spec.get("fail_at")
    clear_at = spec.get("clear_at")
    switch_at = set(spec.get("mode_switch_at", ()))
    out_mode_raw = False

    events: list[dict] = []
    raw_words_read_while_alarmed = 0
    data_words_read_while_alarmed = 0
    raw_words_packed_while_alarmed = 0
    words_before_switch: list[int] = []
    words_after_switch: list[int] = []

    def _w1c(*names: str) -> dict:
        word = 0
        for name in names:
            f = next(f for f in regmap.STATUS.fields if f.name == name)
            word |= 1 << f.lsb
        return {
            "reg_sel": True, "reg_write": True,
            "reg_addr": regmap.STATUS.index, "reg_wdata": word,
        }

    for i, bit in enumerate(raw_bits):
        bus: dict = {}
        if fail_at is not None and i == fail_at:
            bus = {"ht_fail_rct": True}
            events.append({"sample": i, "event": "ht_fail_rct pulse"})
        elif clear_at is not None and i == clear_at:
            bus = _w1c("HT_FAIL_RCT")
            events.append({"sample": i, "event": "write-1-to-clear HT_FAIL_RCT"})
        elif i in switch_at:
            out_mode_raw = not out_mode_raw
            words_before_switch = list(chain.iface.cond_fifo) + list(chain.iface.raw_fifo)
            bus = {
                "reg_sel": True,
                "reg_write": True,
                "reg_addr": regmap.CTRL.index,
                "reg_wdata": (1 << 0) | (int(out_mode_raw) << 1),
            }
            events.append(
                {"sample": i, "event": f"OUT_MODE -> {'raw' if out_mode_raw else 'conditioned'}"}
            )

        raw_words_before = chain.iface.raw_words_in
        chain.step(bit, **bus)
        alarmed = chain.iface.alarm

        if i in switch_at:
            words_after_switch = list(chain.iface.cond_fifo) + list(chain.iface.raw_fifo)
        if alarmed:
            raw_words_packed_while_alarmed += chain.iface.raw_words_in - raw_words_before

        if drain:
            data_before, raw_before = len(chain.data_words), len(chain.raw_words)
            chain.drain()
            if alarmed:
                data_words_read_while_alarmed += len(chain.data_words) - data_before
                raw_words_read_while_alarmed += len(chain.raw_words) - raw_before

    status = _status(chain)
    data_hex = "".join(f"{w:08x}\n" for w in chain.data_words)
    raw_hex = "".join(f"{w:08x}\n" for w in chain.raw_words)

    result = {
        "scenario": name,
        "why": spec["why"],
        "seed": spec["seed"],
        "declared_h_per_bit": DECLARED_H,
        "source_p_one_target": f"{Decimal(p_one_target):.12f}",
        "source_threshold_u32": threshold,
        "raw_samples": len(raw_bits),
        "startup_samples": STARTUP_SAMPLES,
        "startup_windows_run": chain.startups + 1,
        "first_conditioned_word_at_cycle": chain.first_data_cycle,
        "raw_samples_before_first_conditioned_word": chain.first_data_raw_samples,
        "data_words_read": len(chain.data_words),
        "raw_words_read": len(chain.raw_words),
        "raw_words_packed": chain.iface.raw_words_in,
        "cond_words_offered": chain.cond.words_out,
        "flush_events": chain.iface.flushes,
        "words_dropped_by_flush": chain.iface.words_dropped_by_flush,
        "raw_bits_dropped_by_flush": chain.iface.raw_bits_dropped_by_flush,
        "status_final": f"0x{status:08x}",
        "status_ht_alarm": _field(status, "HT_ALARM"),
        "status_startup": _field(status, "STARTUP"),
        "status_cond_ready": _field(status, "COND_READY"),
        "status_ovf_data": _field(status, "OVF_DATA"),
        "status_ovf_raw": _field(status, "OVF_RAW"),
        "status_data_level": _field(status, "DATA_LEVEL"),
        "status_raw_level": _field(status, "RAW_LEVEL"),
        "data_stream_sha256": hashlib.sha256(data_hex.encode()).hexdigest(),
        "raw_stream_sha256": hashlib.sha256(raw_hex.encode()).hexdigest(),
        "events": events,
        "wall_time_s": time.time() - started,
        "_data_hex": data_hex,
        "_raw_hex": raw_hex,
    }

    if fail_at is not None:
        result["raw_words_packed_while_alarmed"] = raw_words_packed_while_alarmed
        result["raw_words_read_while_alarmed"] = raw_words_read_while_alarmed
        result["data_words_read_while_alarmed"] = data_words_read_while_alarmed
    if switch_at:
        result["fifo_words_held_at_last_switch"] = len(words_before_switch)
        result["fifo_words_surviving_last_switch"] = len(words_after_switch)

    # The raw words a reader collected must be the source's own bits, in
    # order, undecimated -- the property DR-0001 §3 promises and the SP 800-90B
    # sequential dataset depends on. Only meaningful when no flush intervened:
    # a flush deliberately discards buffered raw words, so a scenario that
    # switches OUT_MODE or restarts the source has a gap *by design*, and
    # OVF_RAW/STATUS is how a reader learns where.
    if chain.raw_words and drain and chain.iface.flushes == 0:
        recovered = [b for w in chain.raw_words for b in iface.word_to_raw_bits(w)]
        result["raw_words_are_a_prefix_of_the_source"] = (
            recovered == raw_bits[: len(recovered)]
        )

    return result


def _frontmatter(stem: str, result: dict, git: dict, raw_files) -> str:
    tb_path = TB_DIR / "run_demo.py"
    model_path = REPO_ROOT / "design" / "interface" / "trng_interface.py"
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
        "  path: design/interface/trng_interface.py",
        f"  sha: {report.blob_sha(REPO_ROOT, model_path)}",
        "  note: >-",
        "    Behavioral-level record: the DUT is the normative behavioural model,",
        "    not a schematic-derived netlist. The synthesisable RTL",
        "    design/interface/trng_interface.v is checked against this model",
        "    cycle-for-cycle by sim/tests/test_interface.py.",
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
        "  type: behavioral-register-interface",
        f"  tstop: n/a (cycle-count driven: {result['raw_samples']} sampler clocks)",
        "  tstep: n/a",
        "  tmax: n/a",
        "  noise_params: n/a (no device noise -- the source is the declared synthetic "
        "model in sim/tb/conditioner-crc32/source_model.py)",
        "  runs: 1",
        f"seeds: [{result['seed']}]   # SHA-256 counter-mode source, "
        "bit-identical on any platform",
        "",
        "source_model:",
        "  kind: IID biased binary",
        f"  declared_min_entropy_per_sample: {result['declared_h_per_bit']}",
        f"  target_p_one: {result['source_p_one_target']}",
        f"  u32_threshold: {result['source_threshold_u32']}",
        "",
        "interface:",
        f"  registers: {', '.join(r.name for r in regmap.REGISTERS)}",
        f"  fifo_depth_words: {regmap.FIFO_DEPTH}",
        f"  raw_pack_bits: {regmap.RAW_PACK_BITS}",
        f"  startup_samples: {STARTUP_SAMPLES}",
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
    rows = [
        ("raw samples driven", f"{r['raw_samples']}"),
        ("start-up window (samples)", f"{r['startup_samples']}"),
        ("start-up windows run", f"{r['startup_windows_run']}"),
        ("first conditioned word available at cycle", f"{r['first_conditioned_word_at_cycle']}"),
        (
            "raw samples before the first conditioned word",
            f"{r['raw_samples_before_first_conditioned_word']} "
            f"(DR-0002 start-up {r['startup_samples']} + DR-0008 conditioner "
            f"{cond.BLOCK_BITS}, non-overlapping)",
        ),
        ("conditioned words offered by the conditioner", f"{r['cond_words_offered']}"),
        ("DATA words read", f"{r['data_words_read']}"),
        ("RAW_DATA words read", f"{r['raw_words_read']}"),
        ("raw words packed", f"{r['raw_words_packed']}"),
        ("flush events", f"{r['flush_events']}"),
        ("FIFO words discarded by flush", f"{r['words_dropped_by_flush']}"),
        ("partial raw bits discarded by flush", f"{r['raw_bits_dropped_by_flush']}"),
        ("final STATUS", f"`{r['status_final']}`"),
        ("final STATUS.HT_ALARM", f"{r['status_ht_alarm']}"),
        ("final STATUS.STARTUP", f"{r['status_startup']}"),
        ("final STATUS.COND_READY", f"{r['status_cond_ready']}"),
        ("final STATUS.OVF_DATA / OVF_RAW", f"{r['status_ovf_data']} / {r['status_ovf_raw']}"),
        ("final DATA_LEVEL / RAW_LEVEL", f"{r['status_data_level']} / {r['status_raw_level']}"),
        ("DATA stream sha256", f"`{r['data_stream_sha256']}`"),
        ("RAW_DATA stream sha256", f"`{r['raw_stream_sha256']}`"),
    ]
    for key, label in (
        ("raw_words_packed_while_alarmed", "raw words acquired while HT_ALARM latched (DR-0001 §5 requires > 0)"),
        ("raw_words_read_while_alarmed", "RAW_DATA words read while HT_ALARM latched (requires > 0)"),
        ("data_words_read_while_alarmed", "DATA words read while HT_ALARM latched (DR-0002 §2 requires 0)"),
        ("fifo_words_held_at_last_switch", "FIFO words held at the last OUT_MODE switch"),
        ("fifo_words_surviving_last_switch", "FIFO words surviving it (DR-0001 §2 requires 0)"),
        ("raw_words_are_a_prefix_of_the_source", "RAW_DATA words reproduce the source bits in order"),
    ):
        if key in r:
            rows.append((label, f"{r[key]}"))

    table = "\n".join(f"| {k} | {v} |" for k, v in rows)
    events = "\n".join(f"| {e['sample']} | {e['event']} |" for e in r["events"]) or "| — | none |"

    return f"""
## Result

Scenario `{r['scenario']}` — {r['why']}.

| Quantity | Value |
|---|---|
{table}

Scripted events:

| Raw sample | Event |
|---|---|
{events}

## What this record is evidence about

The **block**: the register map's gating, the flush rules, the FIFO
behaviour, and the `en`/`flush` contract between this block and the
conditioner. The conditioner in this run is the real model from
`design/conditioner/crc32_conditioner.py`, driven by this block's own
`cond_en`/`cond_flush` in the same cycle they are asserted — so what is
demonstrated is the inter-block contract, not a scripted stand-in for it.

It is evidence about **nothing else**. The raw source is the declared
synthetic model in `sim/tb/conditioner-crc32/source_model.py`, chosen because
its min-entropy is an input rather than a result.

## How to reproduce

```sh
python3 sim/tb/{SLUG}/run_demo.py --scenario {r['scenario']} --no-write
```

Add `--record` (the default) to mint a new record. Records are append-only:
a re-run mints a new stem, it never overwrites this one.

## Caveats

- **Behavioral level, no corner.** No device models are instantiated, so this
  record has no process/voltage/temperature point and must not be cited for
  any claim that depends on one (DR-0009 rule 3). In particular it says
  nothing about whether this block closes timing at `ss` / −10 % / +125 °C,
  which remains owed (DR-0009 rule 6).
- **The health-test block (#11) does not exist yet.** This run stands in for
  exactly the part of it this block contracts with: a counter that pulses
  `ht_startup_pass` after {r['startup_samples']} consecutive raw samples and
  restarts on `startup_req`. It runs no RCT or APT; failures are injected by
  the scenario. Nothing here validates a health test.
- **Synthetic source, not a sampled ring oscillator.** #9's sampler exists,
  but no committed raw bitstream of this length does; when one lands, these
  scenarios can be re-run with a `transistor-derived` input (DR-0009 §2).
- **The time-to-first-valid figure here is in sampler clocks, not seconds.**
  Converting it to a time requires the sampler clock frequency, which is a
  corner-dependent system choice this record cannot speak to (DR-0003,
  DR-0012).

---

Written by `sim/tb/{SLUG}/run_demo.py`. Append-only: never edit or delete
this file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
"""


def write_record(result: dict, records_dir: Path, git: dict) -> Path:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def render(stem: str, raw_dir: Path) -> str:
        (raw_dir / "data_words.hex").write_text(result["_data_hex"])
        (raw_dir / "raw_words.hex").write_text(result["_raw_hex"])
        summary = {k: v for k, v in result.items() if not k.startswith("_")}
        (raw_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
        raw_files = [
            (name, report.sha256_file(raw_dir / name))
            for name in ("data_words.hex", "raw_words.hex", "summary.json")
        ]
        return _frontmatter(stem, result, git, raw_files) + "\n" + _body(result)

    return report.finalize_record(records_dir, date, SLUG, render)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario", action="append", choices=sorted(SCENARIOS),
        help="run only this scenario (repeatable); default is all of them",
    )
    parser.add_argument(
        "--no-write", action="store_true",
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
        print(
            f"   {result['raw_samples']} raw samples, "
            f"{result['data_words_read']} DATA words, "
            f"{result['raw_words_read']} RAW_DATA words, "
            f"{result['flush_events']} flush events"
        )
        print(
            f"   final STATUS {result['status_final']}  "
            f"alarm={result['status_ht_alarm']} startup={result['status_startup']} "
            f"cond_ready={result['status_cond_ready']} "
            f"ovf={result['status_ovf_data']}/{result['status_ovf_raw']}"
        )
        for key in (
            "raw_words_packed_while_alarmed",
            "raw_words_read_while_alarmed",
            "data_words_read_while_alarmed",
            "fifo_words_surviving_last_switch",
            "raw_words_are_a_prefix_of_the_source",
        ):
            if key in result:
                print(f"   {key}: {result[key]}")
        if not args.no_write:
            path = write_record(result, records_dir, git)
            print(f"   record: {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
