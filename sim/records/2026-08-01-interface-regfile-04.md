---
record: 2026-08-01-interface-regfile-04
date: 2026-08-01T21:21:24Z
status: valid

level: behavioral (see spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md)

testbench:
  path: sim/tb/interface-regfile/run_demo.py
  sha: 3be7a3dd329a96d3295b320ea4791f26cf996eb6
netlist:
  path: design/interface/trng_interface.py
  sha: 6f94cf7c2a2e5e44e6ce8a753d67b9cf01626830
  note: >-
    Behavioral-level record: the DUT is the normative behavioural model,
    not a schematic-derived netlist. The synthesisable RTL
    design/interface/trng_interface.v is checked against this model
    cycle-for-cycle by sim/tests/test_interface.py.
repo_commit: 5f9a55b90d158ba3b9932984ad3e78864e4a4e26

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
  type: behavioral-register-interface
  tstop: n/a (cycle-count driven: 8192 sampler clocks)
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

interface:
  registers: CTRL, STATUS, DATA, RAW_DATA
  fifo_depth_words: 8
  raw_pack_bits: 32
  startup_samples: 1024

raw:
  path: sim/records/raw/2026-08-01-interface-regfile-04/
  files:
    - data_words.hex  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    - raw_words.hex  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    - summary.json  sha256:acc7855f8e78ac1b180ef7695740bb27aca5e21be36b8cbd91e7fd65102eef9a
wall_time: 0.8s
---

## Result

Scenario `overrun` — a consumer that stops reading: the FIFOs drop the *incoming* word rather than a buffered one, so what survives is a contiguous run, and OVF_* is what tells a reader the run ended -- the hazard DR-0001 named when it rejected register-only raw access for the SP 800-90B sequential dataset.

| Quantity | Value |
|---|---|
| raw samples driven | 8192 |
| start-up window (samples) | 1024 |
| start-up windows run | 1 |
| first conditioned word available at cycle | 1280 |
| raw samples before the first conditioned word | 1280 (DR-0002 start-up 1024 + DR-0008 conditioner 256, non-overlapping) |
| conditioned words offered by the conditioner | 28 |
| DATA words read | 0 |
| RAW_DATA words read | 0 |
| raw words packed | 256 |
| flush events | 0 |
| FIFO words discarded by flush | 0 |
| partial raw bits discarded by flush | 0 |
| final STATUS | `0x008801f0` |
| final STATUS.HT_ALARM | 0 |
| final STATUS.STARTUP | 0 |
| final STATUS.COND_READY | 1 |
| final STATUS.OVF_DATA / OVF_RAW | 1 / 1 |
| final DATA_LEVEL / RAW_LEVEL | 8 / 8 |
| DATA stream sha256 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| RAW_DATA stream sha256 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Scripted events:

| Raw sample | Event |
|---|---|
| — | none |

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
python3 sim/tb/interface-regfile/run_demo.py --scenario overrun --no-write
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
  `ht_startup_pass` after 1024 consecutive raw samples and
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

Written by `sim/tb/interface-regfile/run_demo.py`. Append-only: never edit or delete
this file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
