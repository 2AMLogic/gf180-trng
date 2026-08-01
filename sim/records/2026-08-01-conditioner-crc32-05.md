---
record: 2026-08-01-conditioner-crc32-05
date: 2026-08-01T09:26:59Z
status: valid

level: behavioral (see spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md)

testbench:
  path: sim/tb/conditioner-crc32/run_demo.py
  sha: 82c5abab5e2b4631b5fd59eb93ac271c4b772e4f
netlist:
  path: design/conditioner/crc32_conditioner.py
  sha: 3da892d7ebcf65ba703cc8ef55088d3cd9149206
  note: >-
    Behavioral-level record: the DUT is the normative behavioural model,
    not a schematic-derived netlist. The synthesisable RTL
    design/conditioner/crc32_conditioner.v is checked bit-for-bit against
    this model by sim/tests/test_conditioner.py.
repo_commit: 418e5c7485e0945d9cc58158674bb12ada81874b

pdk: n/a (behavioral-level record -- no device models are instantiated, per DR-0009)
pdk.models:
  - n/a (behavioral-level record)

tool:
  ngspice: "n/a (behavioral-level record -- ngspice is not invoked)"
  python: "3.14.6 (CPython)"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: n/a (behavioral-level record -- no device models, so no process corner exists; DR-0009 forbids citing this record for any P/V/T-dependent claim)
  voltage: n/a (behavioral-level record)
  temperature: n/a (behavioral-level record)

analysis:
  type: behavioral-bitstream
  tstop: n/a (cycle-count driven: 16384 sampler clocks)
  tstep: n/a
  tmax: n/a
  noise_params: n/a (no device noise -- the source is the declared synthetic model in sim/tb/conditioner-crc32/source_model.py)
  runs: 1
seeds: [4]   # SHA-256 counter-mode source, bit-identical on any platform

source_model:
  kind: IID biased binary
  declared_min_entropy_per_sample: 0.5
  target_p_one: 0.292893218813
  u32_threshold: 1257966796

conditioner:
  function: 32-bit Galois LFSR, CRC-32 (IEEE 802.3) reflected poly 0xEDB88320
  vetted: false (SP 800-90B non-vetted conditioning component)
  K: 8
  block_bits: 256

raw:
  path: sim/records/raw/2026-08-01-conditioner-crc32-05/
  files:
    - raw_bits.bin  sha256:91974f05b63bdf872d1ee241527c937e5ae73e7ddf4dcbdb3eefa7329d94b0e3
    - cond_words.hex  sha256:01c3e0ff53df1f3a89765e908e2be6f252652ffde8d4a25e8a3eddc9a475ac2e
    - summary.json  sha256:a76e59a57ea8936cafa727f6e165ff97cba978abc031b09ee992974e1a975a89
wall_time: 0.2s
---

## Result

Scenario `gate-flush` -- the DR-0001 / DR-0002 flush rule: a health-test-failure gate or an OUT_MODE switch must clear the conditioner's internal state so no pre-flush raw bit can influence any later output word.

| Quantity | Value |
|---|---|
| raw bits in | 16384 |
| raw ones | 4888 |
| raw P(1) measured | 0.298340 |
| raw most-common-value min-entropy measured | 0.511156 bit/sample |
| conditioned words out | 61 |
| conditioned bits out | 1952 |
| conditioned P(1) measured | 0.494365 |
| conditioned distinct words | 61 of 61 |
| conditioned ones per bit position (min-max) | 21-39 of 61 |
| compression ratio K measured | 8.0000 |
| flush events | 3 |
| raw bits discarded by flush | 527 |
| conditioned stream sha256 | `01c3e0ff53df1f3a89765e908e2be6f252652ffde8d4a25e8a3eddc9a475ac2e` |
| post-flush words reproduced by a fresh conditioner | True (24 words checked) |

SP 800-90B conditioning arithmetic for this scenario's declared input
min-entropy, computed by `sim/tb/conditioner-crc32/sp800_90b.py` (n_in = 256,
n_out = nw = 32):

| Quantity | Value |
|---|---|
| declared input min-entropy per block | 128.0 bit |
| output entropy before the non-vetted cap | 32.000000 bit/word |
| output entropy credited to a non-vetted component | 27.200000 bit/word |

Numbers only. **This record makes no entropy claim about the conditioned
stream.** The rows above are the min-entropy the *declared source model*
carries and what SP 800-90B's conditioning arithmetic would credit for it --
not a measurement of the entropy of any physical source, and not an
SP 800-90B entropy assessment (DR-0004 Tier 3).

## How to reproduce

```sh
python3 sim/tb/conditioner-crc32/run_demo.py --scenario gate-flush --no-write
```

Add `--record` (the default) to mint a new record. Records are append-only:
a re-run mints a new stem, it never overwrites this one.

## Caveats

- **Behavioral level, no corner.** No device models are instantiated, so this
  record has no process/voltage/temperature point and must not be cited for
  any claim that depends on one (DR-0009). It says nothing about whether the
  conditioner closes timing at `ss` / -10 % / +125 C.
- **Synthetic source, not a sampled ring oscillator.** The input is the
  declared IID biased-coin model in `sim/tb/conditioner-crc32/source_model.py`, chosen
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
  `sim/tb/conditioner-crc32/sp800_90b.py` and DR-0008 -- inherited from DR-0004.

---

Written by `sim/tb/conditioner-crc32/run_demo.py`. Append-only: never edit or delete
this file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
