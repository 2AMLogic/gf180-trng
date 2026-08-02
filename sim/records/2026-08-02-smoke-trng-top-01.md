---
record: 2026-08-02-smoke-trng-top-01
date: 2026-08-02T03:47:51Z
status: valid

level: behavioral (see spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md) -- the raw-bit INPUT to this run is transistor-derived (see raw_input below); this run itself instantiates no device model

testbench:
  path: sim/tb/smoke-trng-top/run_demo.py
  sha: e2cf61b265c833eb9901adff8d003227614c0574
netlist:
  path: design/trng_top/trng_top.py
  sha: e934bc888d525b9118072d96b79bd6d44834b55a
  note: >-
    Behavioral-level record: the DUT is the normative behavioural
    top-level model (the three real digital block models, wired as
    design/xschem/trng_top.sch's raw tap feeds them). The
    synthesisable RTL design/trng_top/trng_top.v wires the same
    three modules; sim/tests/test_trng_top.py checks both against
    each other and against the analog side's pin names.

analog_boundary:
  schematic: design/xschem/trng_top.sch
  schematic_sha: e58db9d51c2fb30b75196b168f70755d5e27f1c7
  netlist: design/trng_top.spice
  netlist_sha: 7d3dc07cdecd5117f4e00894b679d1557c5eebfc
  note: >-
    trng_top.sch instantiates sampler_core.sym (#7 entropy source +
    #9 sampler) unmodified; design/netlist.py --check ties this
    netlist to that schematic. Not re-simulated by this run -- see
    raw_input below for the transistor-level evidence this run's
    raw-bit stimulus comes from.

repo_commit: 06655e057214b551946169c95da32ffa51762971-dirty

pdk: n/a (behavioral-level record -- no device models are instantiated by this run, per DR-0009)
pdk.models:
  - n/a (behavioral-level record)

tool:
  ngspice: "n/a (behavioral-level record -- ngspice is not invoked by this run; see raw_input for where it WAS invoked)"
  python: "3.14.6 (CPython)"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: n/a (behavioral-level record -- no device models, so no process corner exists for THIS run; DR-0009 forbids citing this record for any P/V/T-dependent claim; see raw_input for the corner the cited transistor-level bits were captured at)
  voltage: n/a (behavioral-level record)
  temperature: n/a (behavioral-level record)

analysis:
  type: behavioral-top-level-smoke
  tstop: n/a (cycle-count driven: 11 sampler clocks)
  tstep: n/a
  tmax: n/a
  noise_params: n/a (no device noise in this run; the raw-bit input already carries whatever noise the cited transistor-level run injected)
  runs: 1
seeds: n/a (raw-bit input is a fixed, already-recorded capture, not re-seeded by this run; see raw_input.record for its own seeds)

raw_input:
  kind: transistor-derived (DR-0009 rule 4)
  record: sim/records/2026-08-01-sampler-array-digitize-03.md
  record_sha: 6a26574a68d11b408c260b11c8422204daa27c45
  corner.process: tt
  corner.temperature_c: 27
  corner.voltage_v: 3.3
  n_bits: 10
  bits: 0001111100

interface:
  registers: CTRL, STATUS, DATA, RAW_DATA
  fifo_depth_words: 8
  raw_pack_bits: 32

raw:
  path: sim/records/raw/2026-08-02-smoke-trng-top-01/
  files:
    - summary.json  sha256:b6167d2329cfeebf33a3da63265cbdc8c1ac7faabcd7d52405f9db695facfcbe
wall_time: 0.014s
---

## Result

| Quantity | Value |
|---|---|
| raw bits driven (transistor-derived, nominal corner) | `0001111100` |
| sampler-clock cycles run | 11 |
| raw samples absorbed | 10 |
| conditioned words offered by the conditioner | 0 |
| DATA words available | 0 |
| RAW_DATA words available | 0 |
| health-test RCT failures | 0 |
| health-test APT failures | 0 |
| health-test start-up passes | 0 |
| final STATUS (register-bus read) | `0x00000008` |
| final STATUS.HT_ALARM | 0 |
| final STATUS.STARTUP | 1 |
| final STATUS.COND_READY | 0 |

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
python3 sim/tb/smoke-trng-top/run_demo.py --no-write
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

Written by `sim/tb/smoke-trng-top/run_demo.py`. Append-only: never edit or delete
this file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
