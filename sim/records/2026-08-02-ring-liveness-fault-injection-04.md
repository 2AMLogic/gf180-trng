---
record: 2026-08-02-ring-liveness-fault-injection-04
date: 2026-08-02T03:51:53Z
status: valid

level: behavioral (see spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md)

testbench:
  path: sim/tb/ring-liveness-fault-injection/run_demo.py
  sha: 278d5fdde7ce683bfd1054a321860c5aea0a2db7
netlist:
  path: design/health_test/ring_liveness.py
  sha: 139cdc55226afccce32ed62fac87969a7ec9ed66
  note: >-
    Behavioral-level record: the DUT is the normative behavioural model,
    not a schematic-derived netlist. The synthesisable RTL
    design/health_test/ring_liveness.v is checked cycle-for-cycle against
    this model by sim/tests/test_ring_liveness.py.
repo_commit: 06655e057214b551946169c95da32ffa51762971-dirty

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
  tstop: n/a (cycle-count driven: 2131 sampler clocks)
  tstep: n/a
  tmax: n/a
  noise_params: n/a (no device noise -- the source is one of the declared synthetic models in sim/tb/ring-liveness-fault-injection/ring_source_model.py)
  runs: 1
seeds: [n/a]   # SHA-256 counter-mode source, bit-identical on any platform

ring_liveness:
  c_live: 81
  n_rings: 2
  cutoff_source: DR-0002's c_rct(H0=0.5) formula, reused (DR-0016) -- design/health_test/rct_apt.py

input_source:
  kind: declared synthetic per-ring bitstream (DR-0009 rule 4 -- no transistor-derived per-ring digitized bitstream is committed yet)

raw:
  path: sim/records/raw/2026-08-02-ring-liveness-fault-injection-04/
  files:
    - summary.json  sha256:95099fd238e9de3596867651b13646d9127f7615818364108edca6117d7eb0e4
    - raw_rows.bin  sha256:9f52a69467ca92288911477b32d99862d2ec8c2e131df09dc5ade43f321cd959
wall_time: 0.1s
---

## Result

Scenario `both-stuck` -- both rings stop at the same onset -- ring_stuck_any must still fire (and each individual ring_stuck bit), demonstrating the monitor does not depend on a surviving ring to detect the shared failure mode.

| Quantity | Value |
|---|---|
| lead-in + fault cycles total | 2131 |
| fault onset (sample index) | 2000 |
| C_LIVE | 81 |
| per-ring first event after onset | [2078, 2079] |
| ring_stuck_any first event after onset | 2078 |
| DR-0016 latency bound (C_LIVE - 1) | 80 |
| all rings detected within bound | True |

Numbers only. **This record makes no entropy claim about any physical
ring.** It demonstrates the liveness-monitor block's behaviour against
declared synthetic per-ring streams, per DR-0009.

## How to reproduce

```sh
python3 sim/tb/ring-liveness-fault-injection/run_demo.py --scenario both-stuck --no-write
```

Add `--record` (the default) to mint a new record. Records are append-only:
a re-run mints a new stem, it never overwrites this one.

## Caveats

- **Behavioral level, no corner.** No device models are instantiated, so this
  record has no process/voltage/temperature point and must not be cited for
  any claim that depends on one (DR-0009).
- **Synthetic source, not a sampled ring oscillator.** The input is one of
  the declared source models in `sim/tb/ring-liveness-fault-injection/ring_source_model.py`. The
  healthy-ring model (IID, H = 1.0) is a declared, conservative modelling
  choice justified by phase aliasing (see `ring_source_model.py`'s docstring),
  not a measurement of any ring's real duty cycle -- none exists in this
  repository. The monitor's own C_LIVE cutoff does not depend on this choice:
  it is reused unchanged from DR-0002's C_RCT.
- **The "stuck ring" fault freezes at the ring's own last live value**, the
  physical signature of an oscillator that stops (design/README.md "Per-ring
  liveness": per-ring supply current collapses when this happens, per
  `sim/records/2026-08-01-ro-inv-05stage-stopped-leakage-*.md`), not an
  arbitrary constant.
- **The electrical tap that would produce `ring_bit` from a real ring's `ro1`/
  `ro2` node does not exist as shipped RTL/schematic yet.** DR-0016 bounds its
  cost in `sim/tb/ring-liveness-tap-power/` and records the remaining
  integration work as a follow-up (#65).

---

Written by `sim/tb/ring-liveness-fault-injection/run_demo.py`. Append-only: never edit or delete
this file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
