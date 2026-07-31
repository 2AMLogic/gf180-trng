---
dr: DR-0001-raw-and-conditioned-output-paths
title: Expose both a raw and a conditioned output path, with raw access always available
status: Accepted
date: 2026-07-31
deciders: Robb Walters (engineering) — ratified via #1 (operator decision, 2026-07-31), amendments landed by #29
supersedes: n/a
superseded_by: n/a
related: "#6 (origin), #1 (ratification), #29 (ratification amendment package), #8, #9, #11, #12; README §Target specification — Interface row; DR-0007 (entropy source feeding the sampler)"
---

# DR-0001: Expose both a raw and a conditioned output path, with raw access always available

## Status

- 2026-07-30: Proposed
- 2026-07-31: **Accepted**, as proposed and unamended, by Robb Walters
  (engineering) — ratification decision recorded on #1 and executed by the #29
  amendment package. The #29 spec review raised no amendment against this
  record (its interface findings were "comfortable as written"). One
  clarification that follows from DR-0007 rather than from any change here: the
  raw tap stays at the **sampler output**, so an N-way XOR-combined ring array
  presents exactly one raw tap — the XOR tree is part of the noise source, and
  no per-ring signal is a raw tap.

## Context

The draft spec table says only `Interface | streaming + register read`, and
`Raw rate | > 1 Mbps`. Neither row says what bits travel on which path. Three
downstream issues cannot start without that answer:

- **#9** (sampler/digitizer) is required to "include the raw-bit tap point
  required by the raw-vs-conditioned interface decision from #6" — it needs
  the tap's *location in the datapath*, not just its existence.
- **#8** (conditioner) needs to know whether it may sit unconditionally in the
  output path or must be bypassable.
- **#11** (health tests) needs to know which stream the tests observe.
- **#12** (min-entropy estimation) needs to know where a bitstream is drawn
  from before it can call the estimate "raw min-entropy per bit".

The binding external constraint is the quality row's SP 800-90B aspiration.
90B assesses the **noise source's digitized output** — the entropy assessment
is performed on raw samples, and the standard's datasets (a long sequential
raw dataset, plus the restart dataset) are raw-sample datasets. A part with no
raw observation path can never be assessed, only trusted. So a raw path is
effectively mandatory; the live decision is its *form* and its *availability*.

There is a real counter-pressure: a raw tap in a shipping product is an attack
surface — it exposes the unconditioned, potentially biased noise-source output
to anything that can read the bus. Production TRNGs commonly fuse or
lock raw access after characterization.

No simulation evidence exists in this repo yet (`sim/records/` is empty), and
none is needed: this is an architecture/observability decision, not a
measured one.

## Decision

We will build **two output paths from one noise source**, with the raw path
always observable:

**1. Raw tap point (for #9).** The raw tap is taken at the **output of the
sampler/digitizer** — after digitization to one bit per sample, and before
*any* post-processing whatsoever: no XOR folding, no decimation, no von
Neumann corrector, no whitening, no health-test gating. This is the "noise
source output" in SP 800-90B terms. #9 owns bringing this signal out; it is
part of #9's deliverable, not an optional debug hook.

**2. Streaming interface: mode-selectable.** A control-register field
(working name `OUT_MODE`) selects what the streaming port carries:

| `OUT_MODE` | Streaming port carries | Notes |
|---|---|---|
| `conditioned` (reset default) | conditioner output | normal operation |
| `raw` | the raw tap, undecimated | characterization / entropy assessment |

Switching `OUT_MODE` in either direction **flushes the conditioner state and
the output FIFO**, so no bit produced under the previous mode can be read
after the switch. The mode is not changed implicitly by anything else.

**3. Register-read path: two distinct registers.** The register file exposes
both, so the two paths are never confused by a reader:

- `DATA` — reads from the conditioned output FIFO (the normal-use register).
- `RAW_DATA` — reads the raw tap directly, independent of `OUT_MODE` and
  independent of the conditioner.

**4. Raw access is unconditional in this block.** There is no fuse, lock bit,
or debug-mode gate on `RAW_DATA` or on `OUT_MODE = raw`. This is a canary
block whose product is verifiability; a locked raw path would make the block
unassessable by anyone but us.

**5. The raw path is never gated by a health-test failure.** Health-test
failure gates the *conditioned* path only (see DR-0002). Gating the raw path
on failure would remove exactly the observability needed to diagnose the
failure, and would corrupt #11's fault-injection measurements.

Bit positions, bus width, and the register map's address layout are
implementation choices left to #9/#8; the **names, the tap location, and the
availability rules above are binding.**

## Alternatives considered

### Conditioned-only streaming, raw exposed through the register file only

- **What**: Streaming port always carries conditioned bits; raw is reachable
  only by polling `RAW_DATA`.
- **Why plausible**: Smallest change to the datapath (no output mux), one
  fewer mode to verify, and a smaller "raw firehose" attack surface. It still
  satisfies the letter of the 90B raw-access requirement.
- **Why rejected**: The 90B sequential dataset is on the order of 10⁶
  consecutive raw samples. Collecting that through register polling makes the
  collection rate a property of the *bus and its driver*, not of the noise
  source — which (a) makes the raw-rate measurement in DR-0003 unmeasurable at
  the interface that matters, and (b) risks non-consecutive samples if the
  reader ever falls behind, silently invalidating the dataset. A raw streaming
  mode makes "10⁶ *consecutive* samples" a property the hardware can
  guarantee.

### Raw-only output; condition off-chip or in firmware

- **What**: The block ships raw bits and nothing else; the consumer conditions.
- **Why plausible**: Minimum hardware, minimum area (helps the < 0.05 mm²
  budget), maximum flexibility for the integrator, and no conditioner
  entropy-accounting argument to make.
- **Why rejected**: The spec table promises usable random output at the
  interface, and every integrator would then re-solve the same problem
  (differently, and some of them wrongly). It also makes health-test gating
  meaningless — there would be no conditioned path to gate — which removes
  the on-die failure containment the health-tests row exists to provide.

### Two simultaneous physical streaming ports (raw and conditioned)

- **What**: Separate always-live raw and conditioned streaming ports, no mode
  bit.
- **Why plausible**: No mode switch to verify, both streams observable at once,
  and #12 could correlate raw against conditioned from the same run
  bit-for-bit.
- **Why rejected**: Doubles the streaming port/pad count for a benefit used
  only during characterization. At the < 0.05 mm² area budget the I/O and its
  synchronization are not free, and the correlation use case is recoverable in
  simulation (where both nodes are probeable regardless of what is bonded out).

### Fuse/lock the raw path after characterization

- **What**: Raw available until a one-time-programmable lock is blown, then
  never again.
- **Why plausible**: Standard production practice; closes the raw attack
  surface in the field.
- **Why rejected for *this* block**: This is a canary block; its deliverable is
  an assessable, reproducible entropy claim. A lock adds an OTP dependency, a
  new fault mode ("locked in test"), and a verification burden, in exchange for
  a threat model this block does not have. Recorded as a follow-up for any
  production derivative rather than built here — see Consequences.

## Consequences

- **Positive**:
  - #9 has an unambiguous tap location (sampler output, pre-everything) and can
    proceed as soon as #7 lands.
  - #12 can state precisely which node an entropy estimate belongs to; a
    "raw min-entropy" number is now falsifiable rather than rhetorical.
  - #11's health tests have a defined input (the raw tap) and a defined
    non-interaction with the observation path.
  - The block satisfies 90B's structural raw-access precondition (see DR-0004)
    without further work.
  - The mode-switch flush rule makes "which bits came from which mode" a
    hardware guarantee rather than a software convention.

- **Negative / accepted cost**:
  - An output mux, a mode bit, and a flush mechanism in the streaming path —
    area and one more state element to verify.
  - Unconditional raw access is an exposure any integrator of this block must
    understand. It is a deliberate, recorded trade, not an oversight.
  - Two read registers is a small documentation burden; a careless integrator
    could read `RAW_DATA` believing it is usable output. Mitigated by naming,
    not by hardware.

- **Follow-up required**:
  - #9: bring out the raw tap; treat it as a deliverable, and exercise it in
    the transient-noise sim that produces the raw bitstream.
  - #8: the conditioner must be **bypassable** and must flush cleanly on mode
    switch. This is now a requirement on #8's implementation, not a preference.
  - #11: health tests take the raw tap as input, at the full raw sample rate,
    undecimated; and must not gate it.
  - #12: raw datasets are drawn from the raw tap; conditioned datasets from the
    conditioner output. State which, per evidence record.
  - New issue (not yet filed): raw-access lock strategy for a production
    derivative of this block. Explicitly out of scope here.
  - README Interface row updated to name the two paths (done alongside this DR).

- **Revisit if**: the block is retargeted from canary use to a
  production part with a hostile-integrator threat model (then the lock-bit
  alternative above becomes live), or if #8 finds the conditioner cannot be
  bypassed without an unacceptable area or timing cost.
