# `sim/tb/conditioned-stream-battery/` — statistical battery on the conditioner's output (behavioral)

Issue #12's statistical-test-battery deliverable. Drives the shipped
conditioner model (`design/conditioner/crc32_conditioner.py`) from the same
declared synthetic source [`sim/tb/conditioner-crc32/source_model.py`](../conditioner-crc32/source_model.py)
uses, at the design's own `H0 = 0.5` target, and runs
[`sim/tools/statistical_battery.py`](../../tools/statistical_battery.py)'s
SP 800-22-style battery on the **conditioned** stream.

**This testbench has no `tb.json` and is not an ngspice testbench.** Per
[`DR-0009`](../../../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md)
rule 7, a behavioral testbench is deliberately invisible to
`sim/run_corners.py` (which only discovers directories containing a
`tb.json`), so it cannot be swept across a PVT grid it has no meaning on. It
is run directly:

```sh
python3 sim/tb/conditioned-stream-battery/run_battery.py --no-write   # print only
python3 sim/tb/conditioned-stream-battery/run_battery.py              # mint a record
```

## Why a declared synthetic source, not the real sampler bitstream

[`sim/tb/sampler-array-digitize/`](../sampler-array-digitize/) (issue #9) is
this repository's one transistor-derived raw bitstream, and DR-0009 prefers
it "whenever one exists and is long enough." It exists; it is nowhere near
long enough — ten raw bits per seed against the 32768 this run needs (a
factor of ~3277), because DR-0009's own cost table prices *one* 256-bit
conditioner block at ~1.9 days of ngspice. See
[`sim/characterization-raw-min-entropy-and-battery.md`](../../characterization-raw-min-entropy-and-battery.md)
for the full accounting and issue #12's transistor-level attempt on the
bitstream that does exist.

## What this battery is and is not

**Is**: an SP 800-22-style statistical battery (monobit, block frequency,
runs, longest run of ones) applied to the CRC-32 conditioner's output, at a
sample count each test's own NIST-tabulated minimum supports — a pipeline
sanity check that the conditioner's whitening behaves as expected on the
design's own `H0 = 0.5` operating point.

**Is not**: the SP 800-90B non-IID entropy-source suite
[`DR-0012`](../../../spec/decision-records/DR-0012-transient-noise-simulation-methodology.md)
§2 forbids running at an unsupported N — a different standard aimed at a
different question (raw min-entropy estimation, not post-conditioning
statistical sanity), with a much larger sample-size floor this repository
cannot afford transistor-level bits for. Not a measurement of the physical
entropy source: as `sim/tb/conditioner-crc32/README.md`'s own `h003`
scenario shows, a conditioned stream can pass every test here while the raw
source behind it carries almost no entropy — a linear conditioner spreads
even a weak input across the whole output space. Passing here says the
*conditioner* is not introducing a detectable statistical defect; it says
nothing about the entropy source #12's transistor-level section addresses
separately.

## Files

| File | What it is |
|---|---|
| `run_battery.py` | The testbench. Generates the synthetic raw stream, conditions it, runs the battery, and writes one append-only evidence record. |
| `README.md` | This file. |
