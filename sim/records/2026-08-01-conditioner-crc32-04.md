---
record: 2026-08-01-conditioner-crc32-04
date: 2026-08-01T09:26:58Z
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
  tstop: n/a (cycle-count driven: 8192 sampler clocks)
  tstep: n/a
  tmax: n/a
  noise_params: n/a (no device noise -- the source is the declared synthetic model in sim/tb/conditioner-crc32/source_model.py)
  runs: 1
seeds: [0]   # SHA-256 counter-mode source, bit-identical on any platform

source_model:
  kind: stuck-at-0 (min-entropy 0)
  declared_min_entropy_per_sample: 0
  target_p_one: 0.000000000000
  u32_threshold: 0

conditioner:
  function: 32-bit Galois LFSR, CRC-32 (IEEE 802.3) reflected poly 0xEDB88320
  vetted: false (SP 800-90B non-vetted conditioning component)
  K: 8
  block_bits: 256

raw:
  path: sim/records/raw/2026-08-01-conditioner-crc32-04/
  files:
    - raw_bits.bin  sha256:5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef
    - cond_words.hex  sha256:0ab7c77e6cd264dd869454ae1c9fd842ce1c3cc88d5053cdc6344a1f10cc2f2a
    - summary.json  sha256:20577a5084609163fb4bdaac54d9aa0deb3bcf0544b26f269f13d95286ddae8e
wall_time: 0.0s
---

## Result

Scenario `stuck0` -- a dead source (stuck at 0, min-entropy exactly 0). Included because the failure mode that matters for a linear conditioner is a plausible-looking output from a dead input.

| Quantity | Value |
|---|---|
| raw bits in | 8192 |
| raw ones | 0 |
| raw P(1) measured | 0.000000 |
| raw most-common-value min-entropy measured | 0.000000 bit/sample |
| conditioned words out | 32 |
| conditioned bits out | 1024 |
| conditioned P(1) measured | 0.000000 |
| conditioned distinct words | 1 of 32 |
| conditioned ones per bit position (min-max) | 0-0 of 32 |
| compression ratio K measured | 8.0000 |
| flush events | 0 |
| raw bits discarded by flush | 0 |
| conditioned stream sha256 | `0ab7c77e6cd264dd869454ae1c9fd842ce1c3cc88d5053cdc6344a1f10cc2f2a` |

SP 800-90B conditioning arithmetic for this scenario's declared input
min-entropy, computed by `sim/tb/conditioner-crc32/sp800_90b.py` (n_in = 256,
n_out = nw = 32):

| Quantity | Value |
|---|---|
| declared input min-entropy per block | 0 bit |
| output entropy before the non-vetted cap | 0.000000 bit/word |
| output entropy credited to a non-vetted component | 0.000000 bit/word |

Numbers only. **This record makes no entropy claim about the conditioned
stream.** The rows above are the min-entropy the *declared source model*
carries and what SP 800-90B's conditioning arithmetic would credit for it --
not a measurement of the entropy of any physical source, and not an
SP 800-90B entropy assessment (DR-0004 Tier 3).

## How to reproduce

```sh
python3 sim/tb/conditioner-crc32/run_demo.py --scenario stuck0 --no-write
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
