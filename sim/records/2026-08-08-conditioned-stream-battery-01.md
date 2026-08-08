---
record: 2026-08-08-conditioned-stream-battery-01
date: 2026-08-08T14:58:22Z
status: valid

level: behavioral (see spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md)

testbench:
  path: sim/tb/conditioned-stream-battery/run_battery.py
  sha: a276edf489b25ffd1199135b23afaa8e084a4aae
netlist:
  path: design/conditioner/crc32_conditioner.py
  sha: 3da892d7ebcf65ba703cc8ef55088d3cd9149206
  note: >-
    Behavioral-level record: the DUT is the normative conditioner model
    (input) composed with sim/tools/statistical_battery.py (analysis),
    not a schematic-derived netlist.
repo_commit: dcd5085f281098a2af74461eeb63ca63833b80c3-dirty

pdk: n/a (behavioral-level record -- no device models are instantiated, per DR-0009)
pdk.models:
  - n/a (behavioral-level record)

tool:
  ngspice: "n/a (behavioral-level record -- ngspice is not invoked)"
  python: "3.12.3 (CPython)"
  statistical_battery_sha: 49b5815c77d00ce5724cfe7ebca0ac2a32d3cba8
  platform: Linux-7.0.0-1010-aws-x86_64-with-glibc2.39

corner:
  process: n/a (behavioral-level record -- no device models, so no process corner exists; DR-0009 forbids citing this record for any P/V/T-dependent claim)
  voltage: n/a (behavioral-level record)
  temperature: n/a (behavioral-level record)

analysis:
  type: behavioral-bitstream
  tstop: n/a (cycle-count driven: 32768 sampler clocks)
  tstep: n/a
  tmax: n/a
  noise_params: n/a (no device noise -- the source is the declared synthetic model in sim/tb/conditioner-crc32/source_model.py)
  runs: 1
seeds: [1]   # SHA-256 counter-mode source, bit-identical on any platform

source_model:
  kind: IID biased binary (declared synthetic -- NOT transistor-derived; see the module docstring for why)
  label: battery-h050
  declared_min_entropy_per_sample: 0.5
  target_p_one: 0.292893218813
  u32_threshold: 1257966796

conditioner:
  function: 32-bit Galois LFSR, CRC-32 (IEEE 802.3) reflected poly 0xEDB88320
  vetted: false (SP 800-90B non-vetted conditioning component)
  K: 8
  block_bits: 256

battery:
  kind: SP 800-22-style (NOT the SP 800-90B non-IID suite DR-0012 forbids)
  alpha: 0.01

raw:
  path: sim/records/raw/2026-08-08-conditioned-stream-battery-01/
  files:
    - raw_bits.bin  sha256:e9344cfaa9aeb015c1a5a504fe701fc43f84c6dd0a8f3eafa72bcfda048fb23f
    - cond_words.hex  sha256:767be8482eb91328fbe4726b3f1a9bfe90b89f73055c5b34d2997349243013ed
    - summary.json  sha256:d506ad7b52a61624d724d42394b0c251ae0df657d64da6957e9b028f5afe70bb
wall_time: 0.0s
---

## Result

| Quantity | Value |
|---|---|
| raw bits in | 32768 |
| raw ones | 9594 |
| raw P(1) measured | 0.292786 |
| conditioned words out | 128 |
| conditioned bits out | 4096 |
| conditioned P(1) measured | 0.501953 |
| conditioned stream sha256 | `767be8482eb91328fbe4726b3f1a9bfe90b89f73055c5b34d2997349243013ed` |

### Statistical battery on the CONDITIONED stream (`sim/tools/statistical_battery.py`)

| Test | n | statistic | p-value | alpha | Result |
|---|---|---|---|---|---|
| monobit (frequency) | 4096 | 0.2500 | 0.802587 | 0.01 | PASS |
| block frequency (M=128) | 4096 | 20.6250 | 0.939546 | 0.01 | PASS |
| runs | 4096 | 2068.0000 | 0.531324 | 0.01 | PASS |
| longest run of ones (M=8) | 4096 | 0.6882 | 0.875973 | 0.01 | PASS |

4 passed, 0 failed, 0 not applicable, 0 omitted (below
that test's minimum useful sample count), out of 4 implemented
tests, at alpha = 0.01.

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
python3 sim/tb/conditioned-stream-battery/run_battery.py --no-write
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
  seed, 1/3277 of the 32768 raw bits this run needs, and DR-0009's own
  cost table prices one *conditioner block* (256 raw bits) at ~1.9 days of
  ngspice, let alone 32768. See `sim/characterization-raw-min-entropy-
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

Written by `sim/tb/conditioned-stream-battery/run_battery.py`. Append-only: never edit or delete
this file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
