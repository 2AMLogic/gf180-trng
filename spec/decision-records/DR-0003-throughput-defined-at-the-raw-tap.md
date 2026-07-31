---
dr: DR-0003-throughput-defined-at-the-raw-tap
title: Define the > 1 Mbps target as sustained raw rate at the raw tap, binding at the slow/low-V/hot corner
status: Accepted
date: 2026-07-31
deciders: Robb Walters (engineering) — ratified via #1 (operator decision, 2026-07-31), amendments landed by #29
supersedes: n/a
superseded_by: n/a
related: "#6 (origin), #1 (ratification), #29 (ratification amendment package), #8, #9, #12, #13; README §Target specification — Raw rate row; DR-0001 (raw tap), DR-0002 (gating), DR-0007 (entropy source sized to hold H₀ at this rate)"
---

# DR-0003: Define the > 1 Mbps target as sustained raw rate at the raw tap, binding at the slow/low-V/hot corner

## Status

- 2026-07-30: Proposed
- 2026-07-31: **Accepted**, as proposed and unamended, by Robb Walters
  (engineering) — ratification decision recorded on #1 and executed by the #29
  amendment package. The #29 spec review found the rate row and its binding
  corner sound as written, and specifically endorsed the two-opposite-corners
  structure in §4. Two ratification notes, neither of which changes this
  record's decision:
  - **The rate target survived the review's rate × entropy finding by an
    architectural change elsewhere, not by moving this row.** Holding > 1 Mbps
    *while* holding H₀ = 0.5 is what forced DR-0007 (N-way XOR-combined RO
    array). If DR-0007's sizing proves unbuildable within the power/area rows,
    the superseding DR that results may have to reopen this row — see
    DR-0007 §Revisit if.
  - **§4's entropy-binding corner is refined, not corrected, by DR-0007 §4.**
    The direction stated here (entropy binds at the *least*-jitter, cold /
    +10 %-supply region, opposite the rate corner) is right; the process letter
    is not settled and the corner *metric* depends on the sampler clock source
    #9 has yet to pin. Read `ff`/+10 %/−40 °C in the table below as "cold /
    +10 % supply, process letter TBD by #13".

## Context

The draft spec row is `Raw rate | > 1 Mbps | > 4 Mbps`. The row is named "raw
rate" but the table never defines a measurement point or a corner, and #9's
acceptance criterion ("a raw bitstream at the draft target rate (> 1 Mbps
raw)") inherits the same ambiguity. Two distinct questions are open:

**Where is it measured?** If the target is a *post-conditioning* rate, it
cannot be evaluated until #8 fixes the conditioner's compression ratio K —
and #8 is itself downstream of the certification decision (DR-0004). Defining
the target at the raw interface makes it measurable at the earliest point in
the build order (#9), with no dependency on #8.

**At which corner?** #13 establishes that the *entropy*-worst corner for a
jitter TRNG is **fast process / high supply / cold** — less thermal noise,
faster edges, less accumulated jitter per sample. But that is the corner where
the ring oscillator runs **fastest**, i.e. where the raw *rate* is highest.
The rate-binding corner is the opposite one: **slow process / low supply /
hot**, where RO frequency and therefore the sample rate are lowest.

This is worth stating plainly because it is easy to get backwards: the spec
table has **two different binding corners** for two different rows, and
neither row is bound at nominal.

No evidence record is cited; `sim/records/` is empty and this is a definitional
decision. The corner *names* below use the #13 grid (−40/27/125 °C, ±10 %
supply, PDK process corners) rather than inventing a separate corner set.

## Decision

We will define the throughput row as follows.

**1. Measurement point: the raw tap.** "Raw rate" is the bit rate at the raw
tap defined in DR-0001 — the sampler/digitizer output, one bit per sample,
undecimated, before any conditioning. It is a property of the noise source and
sampler alone.

**2. Target: `R_raw > 1 Mbps`, sustained.** Sustained means the average over a
full transient-noise run (`N_bits / t_sim`, per the #10 methodology), not a
peak or an instantaneous rate, and with no throttling: the output FIFO must not
underflow when read continuously at the rated rate. Stretch target
`R_raw > 4 Mbps`, identical definition.

**3. Binding corner: slow / −10 % supply / +125 °C** (`ss`, 2.97 V nominal-3.3 V
supply, 125 °C) — the slowest-RO corner of the #13 grid. The target must hold
**there**; holding at nominal is not sufficient and is not the claim. Since RO
frequency is monotone in each of the three axes over this grid, meeting the
target at that corner implies meeting it everywhere on the grid, so no
per-corner rate sweep beyond #13's existing grid is required.

**4. Rate and quality are bound at opposite corners — both must be reported.**

| Row | Quantity | Binding corner |
|---|---|---|
| Raw rate (this DR) | `R_raw` | `ss` / −10 % / +125 °C (slowest RO) |
| Quality (DR-0004, #12) | min-entropy per raw bit `H` | `ff` / +10 % / −40 °C (least jitter) |

**5. Entropy throughput is a derived, reported figure — not yet a target.**
`R_H = R_raw × H` (bits of entropy per second) is the quantity an integrator
actually cares about, and it is *not* guaranteed by either row above, because
the two rows are bound at different corners. #12 shall report `R_H` per corner
alongside `R_raw` and `H`. This DR deliberately sets **no** `R_H` target — one
cannot be set honestly before #12 produces an H estimate. Setting it is
follow-up work for a later DR.

**6. No post-conditioning rate target is set here.** The conditioned rate is
`R_cond = R_raw / K`, where K is the conditioner's compression ratio, which
#8 owns. **#8 must publish K and the resulting `R_cond` at the same binding
corner.** If a conditioned-rate number is later needed for a datasheet, it
lands as a new DR once K is fixed — it is not silently inferred from this
row.

**7. The target applies to the healthy, ungated state.** While the conditioned
path is gated by a health-test failure (DR-0002), throughput on that path is
undefined; the rate claim is not made about a gated block. The raw path is
ungated under all conditions, so `R_raw` remains measurable during a health-test
failure — which is what makes it the right place to define the row.

## Alternatives considered

### Define the target post-conditioning

- **What**: "> 1 Mbps" means bits delivered at the conditioned output.
- **Why plausible**: It is the number an integrator consumes, and it is the
  number a datasheet normally quotes. Quoting a raw rate that a user never sees
  is arguably a vanity figure.
- **Why rejected**: It is unmeasurable until #8 fixes K, which blocks #9's
  acceptance criterion behind a decision two issues away. It also makes the
  row a *joint* claim about the source and the conditioner, so a change to the
  conditioner silently changes whether the entropy source meets spec. Keeping
  the row at the raw tap keeps one row testing one thing. The conditioned rate
  is recoverable at any time as `R_raw / K` once #8 publishes K, so nothing is
  lost.

### Define both a raw and a conditioned target now

- **What**: Two targets, e.g. "> 1 Mbps raw and > 250 kbps conditioned".
- **Why plausible**: Covers both audiences and forces the conditioner's cost to
  be visible in the spec.
- **Why rejected**: The conditioned number would have to be invented today,
  since K is unknown. Writing a number that no analysis supports into a spec
  table is exactly the failure mode CLAUDE.md's "no claim without a testbench"
  rule exists to prevent — and once it is in the table, #8 would be designing
  to a fabricated constraint.

### Bind the target at the nominal corner (`tt` / 3.3 V / 27 °C)

- **What**: Meet > 1 Mbps typical; report the corners for information.
- **Why plausible**: Standard datasheet practice for "typical" figures; easiest
  to hit; a single obvious corner to simulate first.
- **Why rejected**: The block's product is verification. A rate that holds only
  at nominal is a rate the integrator cannot design against, and #13 already
  requires the full grid anyway — so binding at the worst rate corner costs no
  additional simulation, only honesty.

### Bind rate at the same corner as entropy (`ff` / +10 % / −40 °C)

- **What**: One "worst corner" for the whole table, taken from #13's
  entropy analysis.
- **Why plausible**: A single named worst corner is much easier to communicate,
  and #13 already computes it.
- **Why rejected**: It is the *best* corner for rate, so the rate row would be
  trivially satisfied and would say nothing. The two-corner structure is not
  complexity for its own sake; it reflects that jitter accumulation per sample
  and sample rate move in opposite directions with process, voltage, and
  temperature.

## Consequences

- **Positive**:
  - #9's acceptance criterion becomes checkable the moment #9 has a sim: raw
    rate at `ss`/−10 %/+125 °C, sustained over the run.
  - The rate row is independent of #8, so the conditioner decision cannot
    invalidate an already-recorded rate result.
  - The opposite-corner structure is now explicit in the spec, which prevents
    the plausible error of reporting rate and entropy at the same "worst
    corner" and concluding the block passes both.
  - `R_H` is named as the honest composite figure and is deliberately left
    untargeted, so nobody has to pretend a number exists.

- **Negative / accepted cost**:
  - The headline table figure is one an end user does not directly consume;
    the datasheet will need `R_cond` added once #8 lands.
  - Two binding corners is more to explain than one, and a reader skimming the
    table can still conflate them. Mitigated by naming the corner inline in the
    README row.
  - No conditioned-rate commitment exists yet, so an integrator asking "how
    many usable bits per second?" gets "pending #8" until then.

- **Follow-up required**:
  - #9: report `R_raw` at the binding corner in its evidence record; the sim
    must run long enough for `N_bits / t_sim` to be a sustained average, not a
    startup transient.
  - #8: publish the compression ratio K and the derived `R_cond` at the same
    binding corner; a conditioned-rate spec row, if wanted, is a new DR.
  - #13: no new corners needed — the binding corner is already in the grid;
    #13 should call it out explicitly as the rate-binding corner alongside the
    entropy-binding one.
  - #12: report `R_raw`, `H`, and `R_H = R_raw × H` per corner.
  - README Raw rate row updated alongside this DR.

- **Revisit if**: #13 finds RO frequency is *not* monotone across the grid (so
  the slowest corner is not `ss`/−10 %/+125 °C), if the architecture changes to
  one where raw rate is not set by RO frequency (e.g. the metastability-hybrid
  stretch path), or once #8 fixes K and a conditioned-rate target becomes
  worth committing to.
