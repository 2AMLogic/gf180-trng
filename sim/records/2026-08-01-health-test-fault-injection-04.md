---
record: 2026-08-01-health-test-fault-injection-04
date: 2026-08-01T23:07:42Z
status: valid

level: behavioral (see spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md)

testbench:
  path: sim/tb/health-test-fault-injection/run_demo.py
  sha: b596ee4f758833c85df2016f0e7d542da15e4ba8
netlist:
  path: design/health_test/rct_apt.py
  sha: 7406d4f2195d3c46d9bc60c2014658043455e463
  note: >-
    Behavioral-level record: the DUT is the normative behavioural model,
    not a schematic-derived netlist. The synthesisable RTL
    design/health_test/rct_apt.v is checked cycle-for-cycle against this
    model by sim/tests/test_health_test.py.
repo_commit: dc8570a59d334bdeec04c2e284ed2dbe14a6e0de-dirty

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
  tstop: n/a (cycle-count driven: 6096 sampler clocks)
  tstep: n/a
  tmax: n/a
  noise_params: n/a (no device noise -- the source is one of the declared synthetic models in sim/tb/health-test-fault-injection/fault_injection.py)
  runs: 1
seeds: [n/a]   # SHA-256 counter-mode source, bit-identical on any platform

health_test:
  c_rct: 81
  c_apt: 824
  w: 1024
  cutoff_source: DR-0002 formulas at H0 = 0.5 (design/health_test/rct_apt.py)

input_source:
  kind: declared synthetic (DR-0009 rule 4 -- no transistor-derived raw bitstream is committed yet)
  declared_min_entropy_per_sample: n/a

raw:
  path: sim/records/raw/2026-08-01-health-test-fault-injection-04/
  files:
    - summary.json  sha256:4679663c60f9f913fd34d4ee4a13603f01c2f8f72f110bbbba32c2b1bf9c23da
    - raw_bits.bin  sha256:326ca1956f536fc0783dab5f64089d248f422e9367605434b4aa419df22d3d88
wall_time: 0.1s
---

## Result

Scenario `heavily-biased` -- DR-0002's second detection-latency target: a heavily biased stream (declared H=0.05, near the APT degeneracy floor but still valid) must be detected within 2*W samples of onset, since the bias may begin mid-window.

| Quantity | Value |
|---|---|
| lead-in + fault bits total | 6096 |
| fault onset (sample index) | 2000 |
| fault generator | `biased_bits` |
| C_RCT / C_APT / W | 81 / 824 / 1024 |
| first event index after onset | 2239 |
| detection latency (samples after onset) | 239 |
| DR-0002 latency bound | 2*w - 1 = 2047 |
| detected within bound | True |

Numbers only. **This record makes no entropy claim about any physical
source.** It demonstrates the health-test block's behaviour against a
declared synthetic stream, per DR-0009.

## How to reproduce

```sh
python3 sim/tb/health-test-fault-injection/run_demo.py --scenario heavily-biased --no-write
```

Add `--record` (the default) to mint a new record. Records are append-only:
a re-run mints a new stem, it never overwrites this one.

## Caveats

- **Behavioral level, no corner.** No device models are instantiated, so this
  record has no process/voltage/temperature point and must not be cited for
  any claim that depends on one (DR-0009).
- **Synthetic source, not a sampled ring oscillator.** The input is one of
  the declared source models in `sim/tb/health-test-fault-injection/fault_injection.py`, chosen
  because its properties (min-entropy, stuck value, lock-up half-period) are
  known exactly. A jitter-sampled RO array is neither IID nor stationary
  across corners, and #9/#12/#13 own the real raw stream and its min-entropy.
- **The cutoffs are the DR-0002 draft H0 = 0.5 values**, not a ratified
  worst-corner H (#13's still-open deliverable). `design/health_test/rct_apt.py`
  computes them from H as a parameter, not as hard-coded constants, so a
  ratified H is a one-argument change away.
- **The `false-positive-rate` scenario does not measure alpha=2**-40.**
  DR-0002 explicitly rules that out as infeasible; this scenario recomputes
  the cutoff at a deliberately inflated alpha where the predicted rate is
  observable in a feasible sample count, and checks the mechanism, not the
  ratified alpha.

---

Written by `sim/tb/health-test-fault-injection/run_demo.py`. Append-only: never edit or delete
this file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
