#!/usr/bin/env python3
"""Statistical battery on the CRC-32 conditioner's *output*, for issue #12.

This is a **behavioural-level** testbench (DR-0009): no ngspice, no P/V/T
corner. It drives the shipped conditioner model
(``design/conditioner/crc32_conditioner.py``) from the same declared
synthetic source ``sim/tb/conditioner-crc32/source_model.py`` uses, then runs
``sim/tools/statistical_battery.py``'s SP 800-22-style battery on the
*conditioned* stream and mints one append-only evidence record.

Why a new testbench rather than folding this into ``conditioner-crc32``
--------------------------------------------------------------------------
``sim/tb/conditioner-crc32`` demonstrates the conditioner's own contract
(compression ratio, per-block state clear, flush behaviour, SP 800-90B
output-entropy accounting). This testbench checks a different claim (does
the conditioned stream trip a classical statistical test) with a different
tolerance basis (p-values against NIST's own tables, not a compression-ratio
identity), so it gets its own single-purpose directory -- the same split
DR-0012's own "Alternatives considered" section argues for between
``trnoise-calibration`` and ``jitter-estimator-calibration``.

Why the source is still declared-synthetic, not the real sampler bits
--------------------------------------------------------------------------
``sim/tb/sampler-array-digitize`` (issue #9) is this repository's one
transistor-derived raw bitstream, and DR-0009 rule states a behavioural
record should prefer a transistor-derived source "whenever one exists and
is long enough". It exists; it is not long enough. Ten raw bits per seed is
1/25.6 of one conditioner block (``BLOCK_BITS = 256``), so it cannot even
fill a single conditioned word, let alone the thousands of conditioned bits
a statistical battery needs to say anything. ``sim/characterization-
raw-min-entropy-and-battery.md`` (the issue #12 summary this testbench
feeds) states why that gap is not a testbench oversight but a cost ceiling
this repository's own methodology (DR-0009's "~1.9 days per conditioner
block" table) already priced. So this run uses the declared-synthetic source
at the design's own H0 = 0.5 target, exactly as ``conditioner-crc32``'s
``h050`` scenario does, sized larger for the battery's own sample-count
floor -- and says so, plainly, in every place the result is quoted.

Usage (from the repo root)::

    python3 sim/tb/conditioned-stream-battery/run_battery.py             # write a record
    python3 sim/tb/conditioned-stream-battery/run_battery.py --no-write  # print only
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
TOOLS_DIR = SIM_DIR / "tools"
COND_TB_DIR = SIM_DIR / "tb" / "conditioner-crc32"

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(COND_TB_DIR))
sys.path.insert(0, str(REPO_ROOT / "design" / "conditioner"))

from harness import report  # noqa: E402
import crc32_conditioner as cond  # noqa: E402
import source_model  # noqa: E402
import statistical_battery as battery  # noqa: E402

SLUG = "conditioned-stream-battery"

#: Raw bit count chosen so the conditioned stream (raw_bits / K = raw_bits / 8)
#: lands inside SP 800-22's smallest tabulated "longest run of ones" regime,
#: 128 <= n < 6272 samples (sim/tools/statistical_battery.py), while still
#: giving the other three tests a comfortable multiple of their own (lower)
#: minimums.
RAW_BITS = 32768
SEED = 1
DECLARED_H = Decimal("0.5")
LABEL = "battery-h050"
ALPHA = battery.ALPHA


def _monobit(bits) -> tuple[int, float]:
    ones = sum(bits)
    return ones, (ones / len(bits) if bits else float("nan"))


def run() -> dict:
    started = time.time()

    raw_bits, p_one_target, threshold = source_model.biased_bits(
        LABEL, SEED, RAW_BITS, DECLARED_H
    )
    words = cond.condition_bits(raw_bits)
    cond_bits = [b for w in words for b in cond.word_to_bits(w)]

    raw_ones, raw_p1 = _monobit(raw_bits)
    cond_ones, cond_p1 = _monobit(cond_bits) if cond_bits else (0, float("nan"))

    results = battery.run_battery(cond_bits, alpha=ALPHA)

    packed_raw = source_model.pack_lsb_first(raw_bits)
    cond_hex = "".join(f"{w:08x}\n" for w in words)
    cond_digest = hashlib.sha256(cond_hex.encode()).hexdigest()

    return {
        "seed": SEED,
        "declared_h_per_bit": str(DECLARED_H),
        "source_p_one_target": f"{Decimal(p_one_target):.12f}",
        "source_threshold_u32": threshold,
        "raw_bits": len(raw_bits),
        "raw_ones": raw_ones,
        "raw_p_one_measured": raw_p1,
        "cond_words": len(words),
        "cond_bits": len(cond_bits),
        "cond_ones": cond_ones,
        "cond_p_one_measured": cond_p1,
        "cond_stream_sha256": cond_digest,
        "alpha": ALPHA,
        "battery": results,
        "wall_time_s": time.time() - started,
        "_raw_bytes": packed_raw,
        "_cond_hex": cond_hex,
    }


def _frontmatter(stem: str, result: dict, git: dict, raw_files) -> str:
    tb_path = TB_DIR / "run_battery.py"
    model_path = REPO_ROOT / "design" / "conditioner" / "crc32_conditioner.py"
    battery_path = TOOLS_DIR / "statistical_battery.py"
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
        f"  path: sim/tb/{SLUG}/run_battery.py",
        f"  sha: {report.blob_sha(REPO_ROOT, tb_path)}",
        "netlist:",
        "  path: design/conditioner/crc32_conditioner.py",
        f"  sha: {report.blob_sha(REPO_ROOT, model_path)}",
        "  note: >-",
        "    Behavioral-level record: the DUT is the normative conditioner model",
        "    (input) composed with sim/tools/statistical_battery.py (analysis),",
        "    not a schematic-derived netlist.",
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
        f"  statistical_battery_sha: {report.blob_sha(REPO_ROOT, battery_path)}",
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
        "  kind: IID biased binary (declared synthetic -- NOT transistor-derived; "
        "see the module docstring for why)",
        f"  label: {LABEL}",
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
        "battery:",
        f"  kind: SP 800-22-style (NOT the SP 800-90B non-IID suite DR-0012 forbids)",
        f"  alpha: {result['alpha']}",
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


def _battery_table(results: list[dict]) -> str:
    rows = ["| Test | n | statistic | p-value | alpha | Result |", "|---|---|---|---|---|---|"]
    for r in results:
        if r.get("omitted"):
            rows.append(f"| {r['name']} | {r['n']} | -- | -- | -- | OMITTED -- {r['reason']} |")
        elif r.get("p_value") is None:
            rows.append(f"| {r['name']} | {r['n']} | -- | -- | -- | NOT APPLICABLE -- {r['reason']} |")
        else:
            verdict = "PASS" if r["pass"] else "FAIL"
            rows.append(
                f"| {r['name']} | {r['n']} | {r['statistic']:.4f} | {r['p_value']:.6f} "
                f"| {r['alpha']:g} | {verdict} |"
            )
    return "\n".join(rows)


def _body(result: dict) -> str:
    r = result
    rows = [
        ("raw bits in", f"{r['raw_bits']}"),
        ("raw ones", f"{r['raw_ones']}"),
        ("raw P(1) measured", f"{r['raw_p_one_measured']:.6f}"),
        ("conditioned words out", f"{r['cond_words']}"),
        ("conditioned bits out", f"{r['cond_bits']}"),
        ("conditioned P(1) measured", f"{r['cond_p_one_measured']:.6f}"),
        ("conditioned stream sha256", f"`{r['cond_stream_sha256']}`"),
    ]
    table = "\n".join(f"| {k} | {v} |" for k, v in rows)
    battery_table = _battery_table(r["battery"])
    n_pass = sum(1 for x in r["battery"] if not x.get("omitted") and x.get("pass"))
    n_fail = sum(1 for x in r["battery"] if not x.get("omitted") and not x.get("pass") and x.get("p_value") is not None)
    n_omitted = sum(1 for x in r["battery"] if x.get("omitted"))
    n_na = sum(1 for x in r["battery"] if not x.get("omitted") and x.get("p_value") is None)

    return f"""
## Result

| Quantity | Value |
|---|---|
{table}

### Statistical battery on the CONDITIONED stream (`sim/tools/statistical_battery.py`)

{battery_table}

{n_pass} passed, {n_fail} failed, {n_na} not applicable, {n_omitted} omitted (below
that test's minimum useful sample count), out of {len(r['battery'])} implemented
tests, at alpha = {r['alpha']:g}.

**What this battery is not.** This is an SP 800-22-style statistical
battery (monobit, block frequency, runs, longest run of ones), aimed at the
*conditioned* (whitened) stream. It is **not** the SP 800-90B non-IID
entropy-source suite DR-0012 Section 2 forbids running at an unsupported N
-- different standard, different question, different (much smaller and
achievable) sample-size floor. A PASS above says the conditioned bits did
not trip a classical bias/pattern detector; it says **nothing** about the
min-entropy of whatever feeds the conditioner (see Caveats).

## How to reproduce

```sh
python3 sim/tb/{SLUG}/run_battery.py --no-write
```

Add `--record` (the default) to mint a new record. Records are append-only:
a re-run mints a new stem, it never overwrites this one.

## Caveats

- **Behavioral level, no corner.** No device models are instantiated, so this
  record has no process/voltage/temperature point and must not be cited for
  any claim that depends on one (DR-0009).
- **Declared synthetic source, not the real sampler bitstream.** The input is
  the same IID biased-coin model `sim/tb/conditioner-crc32/source_model.py`
  uses, at the design's own H0 = 0.5 target, chosen because a transistor-
  derived stream long enough to matter does not exist and is not affordable
  -- `sim/tb/sampler-array-digitize` (issue #9) yields ten raw bits per
  seed, 1/3277 of the {RAW_BITS} raw bits this run needs, and DR-0009's own
  cost table prices one *conditioner block* (256 raw bits) at ~1.9 days of
  ngspice, let alone {RAW_BITS}. See `sim/characterization-raw-min-entropy-
  and-battery.md` for the full accounting. Nothing here is a measurement of
  the physical entropy source.
- **A PASS on a conditioned stream is close to uninformative about the raw
  source's entropy, by construction.** `sim/tb/conditioner-crc32/README.md`'s
  own `h003` scenario demonstrates a raw stream with ~0.03 bit/sample of
  measured min-entropy still yields a conditioned `P(1)` within a fraction
  of a percent of 0.5 -- a linear conditioner spreads even a weak input
  across the whole output space. This battery is a **pipeline sanity check**
  (does the conditioner's whitening behave as expected on the design's own
  H0 target), not evidence of the raw entropy source's quality.
- **The `longest run of ones` test is implemented for one NIST-tabulated
  regime only** (128 <= n < 6272 samples, M = 8) -- see
  `sim/tools/statistical_battery.py`'s module docstring for why the larger-N
  tables (M = 128, M = 10^4) are not implemented here.
- **Single realization, one seed.** This is one run of one declared source at
  one target H; it is not a PVT- or seed-swept characterization (there is no
  PVT axis at the behavioral level, and the source is a deterministic
  function of its stated seed).

---

Written by `sim/tb/{SLUG}/run_battery.py`. Append-only: never edit or delete
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
        "--no-write", action="store_true", help="print the results without minting an evidence record"
    )
    parser.add_argument("--record", action="store_true", help="mint a record (the default)")
    args = parser.parse_args(argv)

    result = run()
    print(
        f"raw {result['raw_bits']} bits, P(1)={result['raw_p_one_measured']:.6f} "
        f"(target H0={result['declared_h_per_bit']})"
    )
    print(
        f"conditioned {result['cond_words']} words ({result['cond_bits']} bits), "
        f"P(1)={result['cond_p_one_measured']:.6f}"
    )
    for r in result["battery"]:
        if r.get("omitted"):
            print(f"  {r['name']}: OMITTED ({r['reason']})")
        elif r.get("p_value") is None:
            print(f"  {r['name']}: NOT APPLICABLE ({r['reason']})")
        else:
            verdict = "PASS" if r["pass"] else "FAIL"
            print(f"  {r['name']}: {verdict} (p={r['p_value']:.6f}, alpha={r['alpha']:g})")

    if not args.no_write:
        git = report.git_provenance(REPO_ROOT)
        records_dir = SIM_DIR / "records"
        path = write_record(result, records_dir, git)
        print(f"record: {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
