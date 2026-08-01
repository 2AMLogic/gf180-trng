# `design/health_test/` — on-die health tests (RCT + APT)

The continuous health-test block: the Repetition Count Test (RCT), the
Adaptive Proportion Test (APT), and the start-up test built from the same two
tests. Fixed by
[`DR-0002`](../../spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md);
verified at the level fixed by
[`DR-0009`](../../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md);
follows the `design/conditioner/` (#8) structural precedent.

```
                       ┌───────────────────────────────────────────┐
  raw_bit/raw_valid ──►│ RCT: longest run of a repeated value      │──► ht_fail_rct
  (DR-0001 raw tap,    │ APT: reference-value recurrence per window│──► ht_fail_apt
   undecimated)        │ start-up: STARTUP_SAMPLES clean samples   │──► ht_startup_pass
                       └───────────────────────────────────────────┘
                                          ▲
                                    startup_req (from design/interface/, #26)
```

**Both tests observe the raw tap directly, at the full raw sample rate,
undecimated** (DR-0002 "Test inputs and placement") — never the conditioned
stream, and this block never gates anything itself. Gating, latching, and the
FIFO flush live downstream in `design/interface/` (#26); see
[Interface contract](#interface-contract-with-designinterface-26) below.

## Files

| File | What it is |
|---|---|
| `rct_apt.py` | **Normative** bit-exact behavioural model: the cutoff formulas (`c_rct`, `c_apt`), the APT tail-probability check, and the cycle-accurate `HealthTest` state machine. DR-0009 makes this the definition of correct behaviour. |
| `rct_apt.v` | Synthesisable RTL. Checked against the model cycle-for-cycle under Icarus Verilog by `sim/tests/test_health_test.py`. |

## Cutoffs are parameters, not constants

DR-0002 is explicit: "the implementation should make both cutoffs
**parameters, not hard-coded constants**." `rct_apt.py` implements this as:

- `c_rct(h, alpha=ALPHA)` = `1 + ceil(-log2(alpha) / h)`.
- `c_apt(h, alpha=ALPHA, w=W)` = the smallest `C` with `Pr(X >= C) <= alpha`
  for `X ~ Binomial(w, 2**-h)`, computed by exact `Decimal` binomial-tail
  summation (120 digits of precision — the same budget
  `sim/tb/conditioner-crc32/sp800_90b.py` uses and for the same reason:
  `alpha = 2**-40 ~= 9.09e-13` and the tail terms at `w = 1024` span many
  orders of magnitude below that).
- `HealthTest(c_rct=..., c_apt=..., w=...)` takes the *resulting integer
  cutoffs* as constructor parameters (mirroring `crc32_conditioner.py`
  taking `K` as a parameter rather than baking in 256), or
  `HealthTest.from_h(h)` to go straight from an assumed `H`.
- `rct_apt.v`'s `C_RCT` / `C_APT` / `W` / `STARTUP_SAMPLES` are Verilog
  **parameters**. Their defaults (`81`, `824`, `1024`, `1024`) are the DR-0002
  draft `H0 = 0.5` cutoffs, and `sim/tests/test_health_test.py` mechanically
  checks the RTL's default parameter values against `rct_apt.py`'s formulas
  at `H0` — the same "generated artifact checked against its normative
  source" discipline `design/interface/regmap.py --check` uses, in the form
  this block actually has (no separate generated file, so the check lives in
  the test suite rather than a `--check` CLI flag).

Every one of DR-0002's cutoff-table rows (`H` = 0.1 .. 1.0) reproduces
exactly, along with the amendment A6 independent-verification tail
probabilities (`Pr(X >= 824) = 6.44e-13`, `Pr(X >= 823) = 1.10e-12` at
`H0 = 0.5`) — see `sim/tests/test_health_test.py::CutoffTableTests`.

**The ratified worst-corner `H` is #13's still-open deliverable.** Until it
lands, every construction in this repository uses the draft `H0 = 0.5`
default; recomputing for a ratified `H` is a one-argument change to
`HealthTest.from_h(h)`, not a redesign.

### APT degeneracy floor: refused, not silently accepted

DR-0002's amendment A2 states a hard structural limit: once the assumed `H`
falls low enough (around `H <= 0.03-0.05` at the ratified `alpha`/`W`), no
valid `C_APT <= W` exists and the APT becomes structurally incapable of
firing. `c_apt()` reports this by returning `APT_DEGENERATE` (`W + 1`, a value
outside the valid range) rather than a plausible-looking wrong number, and
`HealthTest`/`HealthTest.from_h` **raise `ValueError`** at construction time
if handed a `C_APT` outside `[1, W]` — a pathologically low `H` cannot
silently produce an unusable cutoff. `rct_apt.v` carries the same guard as a
simulation-time (`synthesis translate_off`) elaboration check, since Verilog
parameters have no exception mechanism.

## The two tests

- **RCT** — tracks the length of the current run of a repeated raw-sample
  value. `ht_fail_rct` pulses for one cycle exactly when that run first
  reaches `C_RCT`; the run counter then **saturates** at `C_RCT` (it does not
  wrap), so a source stuck far longer than `C_RCT` samples produces exactly
  one pulse, not a periodic one every `C_RCT` samples.
- **APT** — non-overlapping windows of `W` raw samples. The first sample of a
  window is its reference; `ht_fail_apt` pulses for one cycle exactly when
  the window completes (its `W`th sample) with `C_APT` or more occurrences of
  the reference value, including the reference sample itself. A new window
  starts immediately after every completed window, whether or not it failed.
- **Start-up test** — a saturating counter of consecutive raw samples with
  neither test failing. `ht_startup_pass` pulses for one cycle exactly when
  it reaches `STARTUP_SAMPLES` (DR-0002 fixes this at exactly 1024, i.e.
  `== W` by default, kept as its own parameter for clarity). Any RCT/APT
  failure resets the counter to 0, and so does `startup_req`.

## Interface contract with `design/interface/` (#26)

Port names/directions match `design/interface/regmap.py`'s port table exactly
(from *this* block's point of view — the regmap table is written from the
interface block's side, so the direction there is inverted):

| Port | Dir (this block) | Width | Meaning |
|---|---|---|---|
| `clk` | in | 1 | sampler clock (DR-0012: fixed external) |
| `rst_n` | in | 1 | asynchronous power-on reset, active low |
| `raw_bit` | in | 1 | the DR-0001 raw tap |
| `raw_valid` | in | 1 | `raw_bit` carries a new sample this cycle |
| `startup_req` | in | 1 | restart: discard any in-flight window, re-arm the start-up test |
| `ht_fail_rct` | out | 1 | one-cycle RCT failure pulse |
| `ht_fail_apt` | out | 1 | one-cycle APT failure pulse |
| `ht_startup_pass` | out | 1 | one-cycle pulse: `STARTUP_SAMPLES` consecutive clean raw samples |

`startup_req` **takes priority over absorbing that cycle's raw sample** — the
same priority `crc32_conditioner.v`'s `flush` has over absorption: a sample
presented in the same cycle as a restart belongs to the window being
discarded, not the fresh one.

## What is *not* here

- **Latching, gating, and the FIFO flush.** `design/interface/README.md`'s
  block diagram shows exactly where: `ht_fail_* ───► latch ──► ht_alarm, gate
  ──► startup_req`. This block only ever *reports*; it never decides what
  happens to the conditioned or raw output paths.
- **The raw tap itself.** That is #9's `sampler_core`; this block only
  consumes `raw_bit`/`raw_valid`.
- **A ratified worst-corner `H`.** #13's deliverable; this block ships with
  the DR-0002 draft `H0 = 0.5` default and the parameter hook to take a
  different value once #13 lands.

## Running things

```sh
# Contract tests, the DR-0002 cutoff-table and degeneracy-floor checks,
# fault-injection detection-latency checks, and RTL/model equivalence. The
# equivalence tests skip (they do not silently pass) without iverilog.
python3 -m unittest discover -s sim/tests -t sim/tests

# Demonstration run: fault injection against the real health-test model.
python3 sim/tb/health-test-fault-injection/run_demo.py --no-write
```

## Health warning

A clear `ht_alarm` at the interface means no RCT or APT window has tripped
its cutoff **since the last restart** — at cutoffs derived from an
**assumed** `H0 = 0.5` (DR-0002), which no measurement has yet replaced, and
against a false-positive target (`alpha = 2**-40`) that this repository has
never observed directly (see the `false-positive-rate` fault-injection
scenario). It does not mean the bits are good; it means neither test has
detected a problem yet.
