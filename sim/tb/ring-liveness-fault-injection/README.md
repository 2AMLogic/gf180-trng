# `sim/tb/ring-liveness-fault-injection/` — per-ring liveness fault injection (behavioral)

Simulated per-ring bitstreams in, per-ring stuck verdicts out. This is the
fault-injection verification
[`DR-0016`](../../../spec/decision-records/DR-0016-per-ring-liveness-monitor.md)
asks for, produced at the level fixed by
[`DR-0009`](../../../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md).
Mirrors `sim/tb/health-test-fault-injection/`'s structure and conventions.

**This testbench has no `tb.json` and is not an ngspice testbench.** Per
DR-0009 rule 7, a behavioral testbench is deliberately invisible to
`sim/run_corners.py` (which only discovers directories containing a
`tb.json`), so it cannot be swept across a PVT grid it has no meaning on. It
is run directly:

```sh
python3 sim/tb/ring-liveness-fault-injection/run_demo.py --no-write   # print only
python3 sim/tb/ring-liveness-fault-injection/run_demo.py              # mint records
python3 sim/tb/ring-liveness-fault-injection/run_demo.py --scenario ring1-stuck
```

## Files

| File | What it is |
|---|---|
| `run_demo.py` | The testbench. Runs the fixed scenario set and writes one append-only evidence record per scenario. |
| `ring_source_model.py` | The declared synthetic per-ring sources: an IID (H = 1.0) source for a healthy ring (`healthy_ring_bits`) and a stuck-at source for a dead ring (`stuck_ring_bits`). SHA-256 counter mode, so a stream is bit-identical on any platform. Named differently from `sim/tb/health-test-fault-injection/fault_injection.py` (which it otherwise mirrors) so the two never collide on a shared module name when both are imported in one test process, per that module's own docstring. |
| `tb_rtl_equivalence.v` | Icarus Verilog testbench driving `design/health_test/ring_liveness.v` from a per-cycle stimulus file, for the RTL/model equivalence check in `sim/tests/test_ring_liveness.py`. |

## Scenarios

| Scenario | Source | What it checks |
|---|---|---|
| `healthy` | Both rings IID, `H = 1.0` | neither ring's `ring_stuck` ever fires over several multiples of `C_LIVE` |
| `ring1-stuck` | Ring 0 freezes at its last live value mid-stream; ring 1 keeps running | ring 0's `ring_stuck` fires within `C_LIVE - 1` samples of onset; ring 1's never fires |
| `ring2-stuck` | The same fault, on ring 1 instead | confirms the monitor is symmetric across `N_RINGS` |
| `both-stuck` | Both rings freeze at the same onset | `ring_stuck_any` (and each per-ring bit) still fires -- the monitor does not depend on a surviving ring |

## What these runs do and do not show

They show the **block**: a healthy pair of rings never trips the watchdog, a
stuck ring (either one, or both at once) is detected within DR-0016's stated
`C_LIVE - 1` sample bound, and the monitor's per-ring channels are
independent.

They show **nothing about a real ring oscillator**. Every input here is a
declared synthetic model (`ring_source_model.py`) chosen because its
properties (min-entropy, stuck value) are known exactly -- not a
jitter-sampled ring, and not the electrical tap that would produce a real
`ring_bit` from `ro1`/`ro2` (that tap's own cost is bounded, separately, in
`sim/tb/ring-liveness-tap-power/`, an ngspice testbench).

They also have **no P/V/T corner**, so they may not be cited for rate, power,
or timing (DR-0009 rule 3).
