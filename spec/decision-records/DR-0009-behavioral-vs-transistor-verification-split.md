---
dr: DR-0009-behavioral-vs-transistor-verification-split
title: Put the behavioral/transistor verification boundary exactly at the DR-0001 raw tap, and label every recorded result with the level that produced it
status: Accepted
date: 2026-08-01
deciders: Builder (issue #8), which owes this split per its own acceptance criteria. Not an operator ratification — see Status.
supersedes: n/a
superseded_by: n/a
related: "#8 (origin), #9, #11, #12, #13, #14, #26; CLAUDE.md (\"PVT corners on every recorded result\"); sim/README.md (record format); DR-0001 (the raw tap this boundary sits on), DR-0004 (Tier 2's ≥ 10⁶-sample sequential dataset), DR-0005 (per-point record granularity), DR-0006 (jitter-characterization PVT sampling), DR-0008 (the first block verified under this split)"
---

# DR-0009: Put the behavioral/transistor verification boundary exactly at the DR-0001 raw tap, and label every recorded result with the level that produced it

## Status

- 2026-08-01: **Accepted** by the Builder of #8. Issue #8's original text names
  this as its "key methodology decision to record up front"; it is recorded
  separately from DR-0008 because the DR template's "one decision per record"
  rule applies — the conditioning-function choice and the verification-level
  boundary are argued on entirely different grounds and either could change
  without the other. As with DR-0008 this is a delegated methodology decision,
  correctable by a superseding DR rather than by editing this one.

## Context

Every result this repository has recorded so far came out of ngspice at
transistor level, and `sim/`'s conventions were written on that assumption.
Two of them cannot be satisfied by a digital block:

- **CLAUDE.md**: "PVT corners on every recorded result."
- **`sim/README.md`**: the required frontmatter includes `pdk`, `pdk.models`,
  `tool.ngspice`, `corner.process`, `corner.voltage`, `corner.temperature`.

A conditioner (#8), a health-test block (#11), a register file (#26) and the
estimator pipeline (#12) have no device models in them. Running them through
ngspice is possible in principle and ruinous in practice, and pretending a
Python model has a process corner would be worse than admitting it has none.
The repository therefore has to say, once and in writing, **which parts are
simulated at transistor level and which are modelled behaviourally, where the
boundary is, and what a record produced on each side of it may be used for.**

### The cost argument, from this repository's own evidence

`sim/records/2026-07-31-ro-inv-05stage-jitter-01.md` records a transient-noise
run of a **5-stage inverter ring alone** — no array, no sampler, no digital:
`tstop: 170n`, `runs: 4`, `wall_time: 7.1m`. That is ~106 s of ngspice per
170 ns of simulated time, i.e. **~0.63 s of wall clock per nanosecond
simulated** (the record's own caveat notes this figure is inflated by `-j 4`
contention, so read it as an order of magnitude, not a benchmark).

Extrapolating at the DR-0003 raw rate of 1 Mbps, where one raw sample is 1 µs:

| Target | Simulated time | Extrapolated ngspice wall time |
|---|---|---|
| One 256-sample conditioner block (DR-0008, one 32-bit output word) | 256 µs | **~1.9 days** |
| One 1024-sample DR-0002 start-up health-test window | 1.024 ms | ~7.4 days |
| DR-0004 Tier 2's ≥ 10⁶-sample sequential dataset | 1 s | **~20 years** |

Even generously assuming an order of magnitude of headroom from a quiet
machine, a faster ring, or a coarser noise step, the conditioner's *first
output word* is a multi-hour transistor-level run and the entropy dataset is
never affordable. DR-0004 Tier 2 already anticipated this ("report the largest
achievable N together with what that N does and does not support"); this
record is the general form of that concession.

The converse is equally clear: the *entropy claim itself* is a physics claim.
Ring-oscillator phase jitter, its supply and temperature dependence, injection
locking between array members (DR-0007's named silent-failure mode), and the
sampler's metastability window are exactly the things a behavioural model
would have to *assume* rather than show. Simulating those behaviourally would
not be cheap verification; it would be no verification at all.

## Decision

We will place the verification-level boundary **exactly at the DR-0001 raw
tap** — the sampler/digitizer output, one bit per sample, before any
post-processing — and label every recorded result with the level that
produced it.

### 1. What is verified at transistor level (ngspice)

Everything **up to and including** the raw tap:

- the ring-oscillator delay cells and rings (#4, done: `sim/tb/ro-*`),
- the N-way array and its XOR combining tree (DR-0007, #7),
- bias/supply regulation feeding the rings,
- the sampler/digitizer and its metastability behaviour (#9),
- supply current and leakage (#32, done).

These carry the full `sim/README.md` frontmatter, a single P/V/T point per
record (DR-0005), and seeds for every stochastic run. **No entropy, rate, or
power claim may be made from anything other than a transistor-level record.**

### 2. What is verified behaviourally

Everything **strictly downstream** of the raw tap:

- the digital conditioner (#8 / DR-0008),
- the RCT/APT health tests and the start-up test (#11),
- the output FIFO, `OUT_MODE` mux, and register file (#26),
- the entropy-estimation pipeline (#10 / #12),
- top-level bitstream-level integration (#14).

These are modelled as **bit-exact executable models** — Python today, matching
the stdlib-only style of `sim/harness/` — driven by one of exactly two input
sources, which the record must name:

- **transistor-derived**: a raw bitstream captured from a transistor-level
  sampler run. Preferred whenever one exists and is long enough.
- **declared synthetic**: a source model whose parameters are stated in the
  record (e.g. `sim/tb/conditioner-crc32/source_model.py`, an IID biased coin
  with a declared per-sample min-entropy). Used when no transistor-derived
  stream of the required length exists, which today is always.

### 3. Rules that make the split safe

1. **Every record states its level.** `sim/README.md` frontmatter gains a
   `level:` field with value `transistor` or `behavioral`. Absence means
   `transistor` for records written before this DR; new records state it.
2. **A behavioural record has no corner and says so.** `corner.process`,
   `corner.voltage`, `corner.temperature`, `pdk`, `pdk.models` and
   `tool.ngspice` are written as `n/a` **with the reason**, per
   `sim/README.md`'s existing rule for inapplicable fields. This is the
   deliberate, bounded exception to CLAUDE.md's "PVT corners on every recorded
   result": the rule stands unchanged for every claim that *has* a corner.
3. **A behavioural record may not be cited for any P/V/T-dependent claim.**
   Rate, power, jitter, metastability, timing closure and min-entropy are
   corner-dependent. A behavioural record may establish functional behaviour,
   bit-exactness, block structure, and arithmetic — nothing that moves with
   process, voltage or temperature.
4. **A behavioural record must name its input source** and, for a declared
   synthetic source, its parameters and seed. A behavioural run driven by a
   synthetic source is evidence about the *block*, never about the *source*.
5. **The behavioural model is normative for the RTL.** Where a digital block
   also has an HDL implementation, the model defines the intended bit-level
   behaviour and the two are checked against each other by an automated
   equivalence test which fails the build when they diverge. See
   `sim/tests/test_conditioner.py` for the pattern (Icarus Verilog; skipped,
   not silently passed, when the tool is absent).
6. **Digital timing closure is not covered by either side and remains owed.**
   Nothing in this split shows that the digital blocks meet timing at
   `ss` / −10 % / +125 °C. That is a post-synthesis static-timing question
   against the gf180mcu liberty files, and no issue owns it yet — see
   Follow-up.
7. **Behavioural testbenches live under `sim/tb/<slug>/` like any other, but
   have no `tb.json`.** The harness's discovery (`sim/harness/testbench.py`)
   only picks up directories containing a `tb.json`, so a behavioural
   testbench is invisible to `run_corners.py` by construction and cannot be
   accidentally swept across a PVT grid it has no meaning on. Each such
   directory carries a `README.md` saying how it is run. This is the same kind
   of reconciliation DR-0005 made between this repo's record granularity and
   the upstream harness convention.

### 4. Where the boundary explicitly does *not* move

- **Not at the conditioner output.** Verifying the health tests behaviourally
  but the conditioner at transistor level (or vice versa) would put a level
  boundary in the middle of the digital path, where it buys nothing: the
  digital blocks are all equally corner-dependent for timing and equally
  corner-independent for function.
- **Not upstream of the sampler.** The sampler is where physics becomes bits.
  Modelling it behaviourally — as, say, "an unbiased coin with min-entropy H"
  — would assume the entire result that #12 and #13 exist to establish.

## Alternatives considered

### Everything at transistor level

- **What**: Simulate the whole block, digital included, in ngspice; no
  behavioural models anywhere.
- **Why plausible**: One level, one record format, no labelling rule to
  enforce, and no risk of a behavioural result being read as a physical one.
  It is also the only way to get a genuinely end-to-end result.
- **Why rejected**: The cost table above. One conditioner output word is a
  ~2-day run and DR-0004 Tier 2's entropy dataset is decades. The practical
  outcome would not be rigorous verification of the digital path; it would be
  *no* verification of the digital path, because nobody would run it.

### Everything behaviourally, including the entropy source

- **What**: Model the RO array and sampler as a parameterised stochastic bit
  source and verify the whole chain in Python.
- **Why plausible**: Fast, cheap, and it makes the estimator and health-test
  work trivially runnable at 10⁶+ samples.
- **Why rejected**: It assumes the claim. The min-entropy per raw bit is the
  one number this project exists to establish, and a behavioural source model
  hands it to you as an input parameter. It would also lose everything
  DR-0007 warns about — injection locking, supply coupling, the difference
  between N independent rings and N correlated ones — which is invisible to
  any model that starts from "assume an IID source with min-entropy H".

### Mixed-signal co-simulation (Verilog-A / ngspice-plus-HDL co-sim)

- **What**: Run the digital RTL and the analog core in one co-simulated
  session so the raw tap is a live signal rather than a captured file.
- **Why plausible**: It is what a commercial flow does, it removes the
  hand-off entirely, and it would catch interface-level mistakes (sampling
  the raw tap on the wrong edge, a valid-signal off-by-one) that a
  file-based hand-off can hide.
- **Why rejected**: It does not solve the cost problem — a co-simulation still
  advances at the analog solver's pace, so the 20-year figure is unchanged —
  and it adds a toolchain this repo does not have. The interface-level
  mistakes it would catch are real, and are instead assigned to #14 as an
  explicit obligation (see Follow-up) rather than bought with a co-simulator.

### Defer the split until a raw bitstream actually exists (#9)

- **What**: Write no methodology DR now; decide per block as each lands.
- **Why plausible**: The split is easier to argue against real data, and
  today's answer ("behavioural, synthetic source") is forced by circumstance
  rather than chosen.
- **Why rejected**: #8, #11, #12 and #26 all need to know *now* what a record
  from their block is allowed to claim, and the failure mode of deciding per
  block is that the first block sets an unwritten precedent the next one
  quietly widens. It is also exactly the situation DR-0004 Tier 2 anticipated
  and asked to be made explicit. Deferring would mean the first behavioural
  record lands with `corner: n/a` and no rule saying whether that is allowed.

## Consequences

- **Positive**:
  - #8, #11, #12, #14 and #26 can produce evidence today instead of blocking
    on #9's sampler and on transistor-level runs nobody can afford.
  - The rule "a behavioural record may not be cited for a P/V/T-dependent
    claim" is a structural guard, not an exhortation: the record physically
    lacks the corner fields such a claim would need to quote.
  - CLAUDE.md's PVT rule stops being something a digital block has to quietly
    ignore, and becomes a rule with one written, bounded exception.
  - Making the behavioural model normative for the RTL turns "the model and
    the hardware agree" into a test that fails, rather than a comment that
    goes stale (`sim/tests/test_conditioner.py`).
  - Behavioural testbenches are invisible to `run_corners.py` by construction,
    so no future contributor can sweep one across a PVT grid and mint records
    whose corner fields are meaningless but present.

- **Negative / accepted cost**:
  - **Two levels of evidence now coexist in one append-only directory**, and a
    reader who skips the `level:` field can mistake one for the other. The
    mitigation is the `n/a` corner fields and the mandatory caveat, both of
    which make a behavioural record look conspicuously unlike a transistor
    one — but it is a real added burden on the reader.
  - **The hand-off itself is unverified.** Nothing yet checks that the
    behavioural models consume the raw tap the way the sampler actually
    presents it. That is a genuine gap this split creates, and it is assigned
    below rather than waved at.
  - **Digital timing at the binding corners is not covered by anything.** A
    functionally-correct behavioural model says nothing about whether the
    conditioner closes timing at `ss` / −10 % / +125 °C, and this repo has no
    synthesis or STA flow.
  - Today's behavioural records are driven by declared synthetic sources, so
    they are evidence about blocks and arithmetic only. Nothing in
    `sim/records/` currently connects the digital path to a real sampled
    bitstream.

- **Follow-up required**:
  - **#9**: when the sampler lands, export a captured raw bitstream as a
    committed artifact so downstream behavioural runs can switch from
    `declared synthetic` to `transistor-derived` inputs. This is the single
    highest-value thing that would upgrade every behavioural record here.
  - **#14**: own the hand-off. Verify at least once, against a
    transistor-level sampler run, that the behavioural models sample the raw
    tap on the same edge and with the same valid semantics the hardware
    presents — the interface mistakes the rejected co-simulation option would
    have caught.
  - **#11, #12, #26**: adopt the `level:` field and the input-source rule in
    every record; state the level in every claim.
  - **New issue wanted**: stand up a synthesis + static-timing flow (yosys and
    the gf180mcu liberty files ship with the PDK) so rule 6's gap can be
    closed and DR-0008 §4's inventory can be replaced with a synthesised gate
    count. Nobody owns this today.
  - **`sim/README.md`**: the `level:` field and the behavioural-record rules
    are documented alongside this DR.

- **Revisit if**: a raw bitstream long enough to fill DR-0004 Tier 2's
  sequential dataset becomes affordable at transistor level (which would make
  the synthetic-source concession unnecessary); or a mixed-signal
  co-simulation flow lands in this repo's toolchain; or a behavioural record
  is ever found to have been cited for a corner-dependent claim, which would
  mean rule 3 needs mechanical enforcement rather than a written rule.
