# `sim/tb/health-test-fault-injection/` — health-test fault injection (behavioral)

Simulated raw bitstream in, RCT/APT/start-up verdicts out. This is the
fault-injection verification issue #11 asks for, produced at the level fixed
by
[`DR-0009`](../../../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md),
against the detection-latency and false-positive-rate targets fixed by
[`DR-0002`](../../../spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md).

**This testbench has no `tb.json` and is not an ngspice testbench.** Per
DR-0009 rule 7, a behavioral testbench is deliberately invisible to
`sim/run_corners.py` (which only discovers directories containing a
`tb.json`), so it cannot be swept across a PVT grid it has no meaning on. It
is run directly:

```sh
python3 sim/tb/health-test-fault-injection/run_demo.py --no-write   # print only
python3 sim/tb/health-test-fault-injection/run_demo.py              # mint records
python3 sim/tb/health-test-fault-injection/run_demo.py --scenario stuck-output
```

## Files

| File | What it is |
|---|---|
| `run_demo.py` | The testbench. Runs the fixed scenario set and writes one append-only evidence record per scenario. |
| `fault_injection.py` | The declared synthetic raw sources: an IID biased coin at a chosen min-entropy (`biased_bits`, also used for the "healthy" and "heavily biased" scenarios), a stuck-at source (`constant_bits`), and a deterministic low-frequency square wave standing in for an injection-locked ring pair (`oscillator_lockup_bits`). SHA-256 counter mode, so a stream is bit-identical on any platform. Named differently from `sim/tb/conditioner-crc32/source_model.py` (which it otherwise mirrors) so the two never collide on a shared module name when both are imported in one test process. |
| `tb_rtl_equivalence.v` | Icarus Verilog testbench driving `design/health_test/rct_apt.v` from a per-cycle stimulus file, for the RTL/model equivalence check in `sim/tests/test_health_test.py`. |

## Scenarios

| Scenario | Source | What it checks |
|---|---|---|
| `healthy` | IID, `H = 0.5` (H0) | no alarm over several full APT windows at the design target |
| `false-positive-rate` | IID, `H = 0.5`, recomputed at an inflated `alpha = 0.05` and a shortened `W = 64` | the observed alarm rate against the exact binomial prediction — DR-0002 rules out observing `alpha = 2**-40` directly |
| `stuck-output` | healthy lead-in, then stuck at 1 | detected within `C_RCT` samples of onset (DR-0002's first detection-latency target) |
| `heavily-biased` | healthy lead-in, then IID at `H = 0.05` | detected within `2*W` samples of onset (DR-0002's second target) |
| `injection-locked` | healthy lead-in, then a 2000-sample-half-period square wave | detected within `2*W` samples of onset — DR-0002 groups this with the heavily-biased target |
| `startup-gate` | scripted: clean window / mid-window RCT failure / `startup_req` restart | the start-up counter passes cleanly, resets on a failure, and `startup_req` discards an in-flight window before re-arming |

## What these runs do and do not show

They show the **block**: the cutoffs reproduce DR-0002's formulas exactly,
each fault type is detected inside its DR-0002 latency bound, a healthy
stream produces no alarm, the false-positive mechanism tracks the binomial
prediction at an observable (inflated) `alpha`, and the start-up/restart
state machine behaves as DR-0002 §4 specifies.

They show **nothing about the entropy source**. Every input here is a
declared synthetic model chosen because its properties (min-entropy, stuck
value, lock-up half-period) are known exactly — not a jitter-sampled ring
oscillator, which is neither IID nor stationary across corners. #9 owns the
real raw bitstream; #12/#13 own its min-entropy and the worst-corner `H` this
block's cutoffs should ultimately use instead of the DR-0002 draft `H0 = 0.5`.

They also have **no P/V/T corner**, so they may not be cited for rate, power,
or timing (DR-0009 rule 3).

The `false-positive-rate` scenario is the one worth reading twice: it does
**not** measure `alpha = 2**-40` (DR-0002 states plainly that no feasible run
could observe it). It recomputes `C_APT` at a deliberately loose `alpha` and
checks that the observed alarm rate tracks the binomial prediction — evidence
the *mechanism* implements the criterion correctly, not evidence about the
ratified `alpha`.
