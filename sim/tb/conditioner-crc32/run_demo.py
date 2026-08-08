#!/usr/bin/env python3
"""Conditioner demonstration: simulated raw bitstream in, conditioned out.

This is a **behavioural-level** testbench (DR-0009). It does not invoke
ngspice and it has no P/V/T corner: it drives the conditioner model in
``design/conditioner/crc32_conditioner.py`` from the declared synthetic
source in ``source_model.py`` and writes one append-only evidence record per
scenario under ``sim/records/``, in the ``sim/README.md`` format, with the
device-model fields explicitly ``n/a`` and a reason.

Usage (from the repo root)::

    python3 sim/tb/conditioner-crc32/run_demo.py             # write records
    python3 sim/tb/conditioner-crc32/run_demo.py --no-write  # print only
    python3 sim/tb/conditioner-crc32/run_demo.py --scenario h050

Scenarios are fixed in :data:`SCENARIOS` rather than taken from the command
line so that "re-run the demonstration" means exactly one thing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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
sys.path.insert(0, str(REPO_ROOT / "design" / "conditioner"))

from harness import report  # noqa: E402
import crc32_conditioner as cond  # noqa: E402
import source_model  # noqa: E402
import sp800_90b  # noqa: E402

SLUG = "conditioner-crc32"

#: Per-scenario stimulus. ``h`` is the declared per-sample min-entropy of the
#: synthetic source; ``None`` means the scenario supplies its own bits.
SCENARIOS = {
    "h050": {
        "n_bits": 131072,
        "seed": 1,
        "h": "0.5",
        "why": (
            "the DR-0002 / DR-0007 design target H0 = 0.5 bit/sample -- the "
            "operating point the health-test cutoffs and the DR-0007 array "
            "sizing law are both written against"
        ),
    },
    "h0107": {
        "n_bits": 131072,
        "seed": 2,
        "h": "0.106456",
        "why": (
            "the break-even input min-entropy computed by sp800_90b.py for "
            "K = 8 -- the point at which the SP 800-90B non-vetted cap stops "
            "being the binding term on output entropy"
        ),
    },
    "h003": {
        "n_bits": 131072,
        "seed": 3,
        "h": "0.03",
        "why": (
            "DR-0002's hard floor: no valid APT cutoff exists at H <= 0.03, so "
            "this is the weakest source the health tests can still be "
            "parameterised for. Included to show what the conditioner does "
            "*not* fix"
        ),
    },
    "stuck0": {
        "n_bits": 8192,
        "seed": 0,
        "h": None,
        "why": (
            "a dead source (stuck at 0, min-entropy exactly 0). Included "
            "because the failure mode that matters for a linear conditioner is "
            "a plausible-looking output from a dead input"
        ),
    },
    "gate-flush": {
        "n_bits": 16384,
        "seed": 4,
        "h": "0.5",
        "flush_at": [1000, 4321, 9999],
        "why": (
            "the DR-0001 / DR-0002 flush rule: a health-test-failure gate or an "
            "OUT_MODE switch must clear the conditioner's internal state so no "
            "pre-flush raw bit can influence any later output word"
        ),
    },
}


def _monobit(bits) -> tuple[int, float]:
    ones = sum(bits)
    return ones, ones / len(bits) if bits else float("nan")


def _mcv_min_entropy(p_one: float) -> float:
    p_max = max(p_one, 1.0 - p_one)
    if p_max <= 0:
        return float("nan")
    return max(0.0, -math.log2(p_max))


def _words_to_bits(words):
    bits = []
    for word in words:
        bits.extend(cond.word_to_bits(word))
    return bits


def _bit_position_spread(words):
    """Ones count per output-bit position -- catches a stuck LFSR tap."""
    counts = [0] * cond.WORD_BITS
    for word in words:
        for i in range(cond.WORD_BITS):
            counts[i] += (word >> i) & 1
    return min(counts), max(counts)


def _run_stream(bits, flush_at=()):
    """Drive the conditioner cycle-accurately. Returns (words, dut, events)."""
    flush_set = set(flush_at)
    dut = cond.Conditioner()
    words: list[int] = []
    word_index_of_flush: list[dict] = []
    for i, bit in enumerate(bits):
        if i in flush_set:
            # One flush cycle: the register block asserts flush, no raw bit is
            # absorbed. Matches crc32_conditioner.v's flush-wins-over-absorb.
            dut.step(raw_valid=False, flush=True)
            word_index_of_flush.append({"sample_index": i, "words_before": len(words)})
        word, valid = dut.step(raw_bit=bit, raw_valid=True)
        if valid:
            words.append(word)
    return words, dut, word_index_of_flush


def _flush_independence_check(bits, flush_at):
    """Every post-flush word must equal a fresh conditioner's output.

    This is the property the DR-0002 flush rule actually asks for: after a
    gate, no bit absorbed before the gate can influence any word read after
    it. We verify it by construction -- re-running only the post-flush bits
    through a fresh conditioner must reproduce the tail of the word stream.
    """
    words, _, _ = _run_stream(bits, flush_at)
    last_flush = max(flush_at)
    tail_words = cond.condition_bits(bits[last_flush:])
    if not tail_words:
        return True, 0
    matched = words[-len(tail_words):] == tail_words
    return matched, len(tail_words)


def run_scenario(name: str) -> dict:
    spec = SCENARIOS[name]
    started = time.time()

    if spec["h"] is None:
        raw_bits = source_model.constant_bits(0, spec["n_bits"])
        declared_h = Decimal(0)
        p_one_target = Decimal(0)
        threshold = 0
    else:
        declared_h = Decimal(spec["h"])
        raw_bits, p_one_target, threshold = source_model.biased_bits(
            name, spec["seed"], spec["n_bits"], declared_h
        )

    flush_at = tuple(spec.get("flush_at", ()))
    words, dut, flush_events = _run_stream(raw_bits, flush_at)

    raw_ones, raw_p1 = _monobit(raw_bits)
    cond_bits = _words_to_bits(words)
    cond_ones, cond_p1 = _monobit(cond_bits) if cond_bits else (0, float("nan"))
    pos_min, pos_max = _bit_position_spread(words) if words else (0, 0)

    packed_raw = source_model.pack_lsb_first(raw_bits)
    cond_hex = "".join(f"{w:08x}\n" for w in words)
    cond_digest = hashlib.sha256(cond_hex.encode()).hexdigest()

    n_in = cond.BLOCK_BITS
    h_in_block = declared_h * n_in
    h_out_uncapped = sp800_90b.output_entropy(n_in, 32, 32, h_in_block)
    h_out = sp800_90b.non_vetted_output_entropy(n_in, 32, 32, h_in_block)

    result = {
        "scenario": name,
        "why": spec["why"],
        "seed": spec["seed"],
        "declared_h_per_bit": str(declared_h),
        "source_p_one_target": f"{Decimal(p_one_target):.12f}",
        "source_threshold_u32": threshold,
        "raw_bits": len(raw_bits),
        "raw_ones": raw_ones,
        "raw_p_one_measured": raw_p1,
        "raw_mcv_min_entropy_measured": _mcv_min_entropy(raw_p1),
        "cond_words": len(words),
        "cond_bits": len(cond_bits),
        "cond_ones": cond_ones,
        "cond_p_one_measured": cond_p1,
        "cond_distinct_words": len(set(words)),
        "cond_bit_position_ones_min": pos_min,
        "cond_bit_position_ones_max": pos_max,
        "cond_stream_sha256": cond_digest,
        "k_measured": (len(raw_bits) - dut.bits_discarded - dut.count) / len(cond_bits)
        if cond_bits
        else float("nan"),
        "flush_events": len(flush_events),
        "bits_discarded_by_flush": dut.bits_discarded,
        "block_bits": cond.BLOCK_BITS,
        "accounting_h_in_per_block": str(h_in_block),
        "accounting_h_out_uncapped": str(h_out_uncapped.quantize(Decimal("0.000001"))),
        "accounting_h_out_non_vetted": str(h_out.quantize(Decimal("0.000001"))),
        "wall_time_s": time.time() - started,
        "_raw_bytes": packed_raw,
        "_cond_hex": cond_hex,
    }

    if flush_at:
        ok, tail = _flush_independence_check(raw_bits, flush_at)
        result["flush_tail_independent_of_pre_flush_bits"] = ok
        result["flush_tail_words_checked"] = tail

    return result


def _frontmatter(stem: str, result: dict, git: dict, raw_files) -> str:
    tb_path = TB_DIR / "run_demo.py"
    model_path = REPO_ROOT / "design" / "conditioner" / "crc32_conditioner.py"
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
        "  path: design/conditioner/crc32_conditioner.py",
        f"  sha: {report.blob_sha(REPO_ROOT, model_path)}",
        "  note: >-",
        "    Behavioral-level record: the DUT is the normative behavioural model,",
        "    not a schematic-derived netlist. The synthesisable RTL",
        "    design/conditioner/crc32_conditioner.v is checked bit-for-bit against",
        "    this model by sim/tests/test_conditioner.py.",
        f"repo_commit: {report.repo_commit_field(git)}",
        "",
        "pdk: n/a (behavioral-level record -- no device models are instantiated, "
        "per DR-0009)",
        "pdk.models:",
        "  - n/a (behavioral-level record)",
        "",
        "tool:",
        f'  ngspice: "n/a (behavioral-level record -- ngspice is not invoked)"',
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
        f"  tstop: n/a (cycle-count driven: {result['raw_bits']} sampler clocks)",
        "  tstep: n/a",
        "  tmax: n/a",
        "  noise_params: n/a (no device noise -- the source is the declared synthetic "
        "model in sim/tb/conditioner-crc32/source_model.py)",
        "  runs: 1",
        f"seeds: [{result['seed']}]   # SHA-256 counter-mode source, "
        "bit-identical on any platform",
        "",
        "source_model:",
        f"  kind: {'stuck-at-0 (min-entropy 0)' if result['declared_h_per_bit'] == '0' else 'IID biased binary'}",
        f"  declared_min_entropy_per_sample: {result['declared_h_per_bit']}",
        f"  target_p_one: {result['source_p_one_target']}",
        f"  u32_threshold: {result['source_threshold_u32']}",
        "",
        "conditioner:",
        "  function: 32-bit Galois LFSR, CRC-32 (IEEE 802.3) reflected poly 0xEDB88320",
        "  vetted: false (SP 800-90B non-vetted conditioning component)",
        f"  K: {cond.K}",
        f"  block_bits: {cond.BLOCK_BITS}",
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
        ("raw bits in", f"{r['raw_bits']}"),
        ("raw ones", f"{r['raw_ones']}"),
        ("raw P(1) measured", f"{r['raw_p_one_measured']:.6f}"),
        (
            "raw most-common-value min-entropy measured",
            f"{r['raw_mcv_min_entropy_measured']:.6f} bit/sample",
        ),
        ("conditioned words out", f"{r['cond_words']}"),
        ("conditioned bits out", f"{r['cond_bits']}"),
        (
            "conditioned P(1) measured",
            "n/a (no whole block completed)"
            if r["cond_bits"] == 0
            else f"{r['cond_p_one_measured']:.6f}",
        ),
        ("conditioned distinct words", f"{r['cond_distinct_words']} of {r['cond_words']}"),
        (
            "conditioned ones per bit position (min-max)",
            f"{r['cond_bit_position_ones_min']}-{r['cond_bit_position_ones_max']}"
            f" of {r['cond_words']}",
        ),
        (
            "compression ratio K measured",
            "n/a" if r["cond_bits"] == 0 else f"{r['k_measured']:.4f}",
        ),
        ("flush events", f"{r['flush_events']}"),
        ("raw bits discarded by flush", f"{r['bits_discarded_by_flush']}"),
        ("conditioned stream sha256", f"`{r['cond_stream_sha256']}`"),
    ]
    if "flush_tail_independent_of_pre_flush_bits" in r:
        rows.append(
            (
                "post-flush words reproduced by a fresh conditioner",
                f"{r['flush_tail_independent_of_pre_flush_bits']} "
                f"({r['flush_tail_words_checked']} words checked)",
            )
        )

    table = "\n".join(f"| {k} | {v} |" for k, v in rows)

    return f"""
## Result

Scenario `{r['scenario']}` -- {r['why']}.

| Quantity | Value |
|---|---|
{table}

SP 800-90B conditioning arithmetic for this scenario's declared input
min-entropy, computed by `sim/tb/{SLUG}/sp800_90b.py` (n_in = {r['block_bits']},
n_out = nw = 32):

| Quantity | Value |
|---|---|
| declared input min-entropy per block | {r['accounting_h_in_per_block']} bit |
| output entropy before the non-vetted cap | {r['accounting_h_out_uncapped']} bit/word |
| output entropy credited to a non-vetted component | {r['accounting_h_out_non_vetted']} bit/word |

Numbers only. **This record makes no entropy claim about the conditioned
stream.** The rows above are the min-entropy the *declared source model*
carries and what SP 800-90B's conditioning arithmetic would credit for it --
not a measurement of the entropy of any physical source, and not an
SP 800-90B entropy assessment (DR-0004 Tier 3).

## How to reproduce

```sh
python3 sim/tb/{SLUG}/run_demo.py --scenario {r['scenario']} --no-write
```

Add `--record` (the default) to mint a new record. Records are append-only:
a re-run mints a new stem, it never overwrites this one.

## Caveats

- **Behavioral level, no corner.** No device models are instantiated, so this
  record has no process/voltage/temperature point and must not be cited for
  any claim that depends on one (DR-0009). It says nothing about whether the
  conditioner closes timing at `ss` / -10 % / +125 C.
- **Synthetic source, not a sampled ring oscillator.** The input is the
  declared IID biased-coin model in `sim/tb/{SLUG}/source_model.py`, chosen
  because its min-entropy is known exactly. A jitter-sampled RO array is
  neither IID nor stationary across corners, and #9/#12 owe the real raw
  stream. Nothing here validates the source.
- **Monobit statistics on the conditioned stream are nearly uninformative.**
  A linear compression function spreads a low-entropy input over the whole
  2^32 output space, so a conditioned stream can pass a bias test while
  carrying almost no entropy. The `h003` scenario exists to make that
  visible. Entropy is credited from the *input* accounting, never from the
  appearance of the output.
- **The non-vetted cap constant is unverified against the published
  standard.** See the provenance warning at the top of
  `sim/tb/{SLUG}/sp800_90b.py` and DR-0008 -- inherited from DR-0004.

---

Written by `sim/tb/{SLUG}/run_demo.py`. Append-only: never edit or delete
this file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
"""


def write_record(result: dict, records_dir: Path, git: dict) -> Path:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def render(stem: str, raw_dir: Path) -> str:
        (raw_dir / "raw_bits.bin").write_bytes(result["_raw_bytes"])
        (raw_dir / "cond_words.hex").write_text(result["_cond_hex"])
        summary = {k: v for k, v in result.items() if not k.startswith("_")}
        (raw_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
        raw_files = [
            (name, report.sha256_file(raw_dir / name))
            for name in ("raw_bits.bin", "cond_words.hex", "summary.json")
        ]
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
        print(
            f"   raw {result['raw_bits']} bits, P(1)={result['raw_p_one_measured']:.6f}, "
            f"measured H_mcv={result['raw_mcv_min_entropy_measured']:.6f} bit/sample"
        )
        print(
            f"   conditioned {result['cond_words']} words "
            f"({result['cond_bits']} bits), P(1)={result['cond_p_one_measured']:.6f}, "
            f"K={result['k_measured']:.4f}"
        )
        print(
            f"   90B non-vetted credit: "
            f"{result['accounting_h_out_non_vetted']} bit per 32-bit word"
        )
        if "flush_tail_independent_of_pre_flush_bits" in result:
            print(
                f"   flush: {result['flush_events']} events, "
                f"{result['bits_discarded_by_flush']} raw bits discarded, "
                f"post-flush independence "
                f"{result['flush_tail_independent_of_pre_flush_bits']}"
            )
        if not args.no_write:
            path = write_record(result, records_dir, git)
            print(f"   record: {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
