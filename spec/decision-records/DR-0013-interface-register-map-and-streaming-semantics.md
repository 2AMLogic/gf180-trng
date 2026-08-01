---
dr: DR-0013-interface-register-map-and-streaming-semantics
title: Fix the interface as four registers plus a word-oriented mode-selected streaming port, with two flush scopes so a health-test gate never reaches the raw path
status: Accepted
date: 2026-08-01
deciders: Builder (issue #26). Delegated implementation of two ratified records — see Status.
supersedes: n/a
superseded_by: n/a
related: "#26 (origin), #8 (conditioner — the block on the other side of `cond_en`/`cond_flush`), #9 (sampler — the raw tap), #11 (health tests — `ht_fail_*`/`ht_startup_pass`), #16 (floorplan — top-level pinout), #27 (trng_top integration), #14; README §Target specification — Interface row; DR-0001 (raw/conditioned paths), DR-0002 (health-test failure behaviour), DR-0003 (raw rate), DR-0008 (conditioner, K = 8), DR-0009 (behavioural/transistor split), DR-0012 (fixed external sample clock)"
---

# DR-0013: Fix the interface as four registers plus a word-oriented mode-selected streaming port, with two flush scopes so a health-test gate never reaches the raw path

## Status

- 2026-08-01: **Accepted** by the Builder of #26.

This is a **delegated** decision of the same kind as DR-0008 and DR-0009, not
an operator ratification. It does not change the ratified spec: DR-0001 and
DR-0002 already fix the interface's externally visible contract — the two
paths, the `OUT_MODE` field and its flush rule, the `DATA`/`RAW_DATA` names,
the unconditional raw access, the latch-and-gate failure behaviour, and the
explicit-clear-plus-start-up-test recovery. What was missing was everything
below that line: addresses, bit positions, reset values, the streaming
handshake, and — the one place the two ratified records genuinely leave a
question open — **which flush event reaches which path**. This record fixes
those, and is correctable by a superseding DR rather than by editing.

DR-0001 §3 says so itself: "Bit positions, bus width, and the register map's
address layout are implementation choices left to #9/#8; the names, the tap
location, and the availability rules above are binding."

The **verification level** for this block is not decided here either.
DR-0009 §2 already lists "the output FIFO, `OUT_MODE` mux, and register file
(#26)" among the blocks verified behaviourally, and §4 explicitly refuses to
move the boundary into the middle of the digital path. #26's scope item
"record where this block's behavioural-vs-transistor boundary sits" is
therefore satisfied by *applying* DR-0009, not by re-deciding it — see
"Verification level" below.

## Context

The interface is the last block between the datapath and the outside world,
and the only one whose shape three other issues have to agree on:

- **#16** (floorplan) needs a top-level pinout to place pads against.
- **#27** (trng_top) needs a port list to instantiate.
- **#11** (health tests) needs to know what it must drive and what it will be
  driven by.

Two ratified records constrain it heavily, and one contract between blocks
already exists in the repository:

1. **DR-0001** fixes `OUT_MODE` (streaming source, `conditioned` at reset),
   the mode-switch flush ("no bit produced under the previous mode can be
   read after the switch"), the two read registers `DATA` and `RAW_DATA`, and
   two availability rules that are unusually strong: raw access carries **no
   fuse, lock bit or debug gate** (§4), and the raw path is **never gated by
   a health-test failure** (§5).
2. **DR-0002** fixes the failure behaviour: an RCT/APT failure sets a sticky
   `HT_FAIL_RCT`/`HT_FAIL_APT` flag and asserts a block-level `HT_ALARM`;
   the conditioned path gates immediately, valid deasserts, `DATA` returns no
   new bits, and the output FIFO is flushed; the flags are cleared only by a
   write-1-to-clear; and clearing restarts the noise source and the
   1024-sample start-up test, with the conditioned path staying gated until
   that test passes. The same start-up test runs at power-on.
3. **`design/conditioner/README.md`** (from #8) already states the half of
   the contract this block owes the conditioner, in the conditioner's own
   words: "#26 asserts `flush` for at least one sampler clock on a
   health-test-failure gate and on an `OUT_MODE` write in either direction,
   and holds `en` low for the whole start-up-test window."

There is no evidence record behind this decision because there was nothing
to measure: the register map is a contract, not a measurement. What *is*
recorded, after the fact, is that the contract behaves as specified — see
"Evidence" below.

### The one thing the ratified records leave genuinely open

DR-0001 §2 requires that an `OUT_MODE` switch "flushes the conditioner state
and **the output FIFO**", and DR-0001 §3 requires that `RAW_DATA` be readable
"independent of `OUT_MODE`". Read together with DR-0002's "the raw path is
not gated", those three clauses do not by themselves say what happens to
**buffered raw words** when the mode changes: flushing them looks like it
brushes against §3, and *not* flushing them looks like it brushes against §2
(the streaming port would be switched onto a FIFO still holding pre-switch
bits). Getting this wrong is exactly the kind of mistake #26's own curation
warned would "pass a narrow review and only surface once #27's top-level
integration or #16's floorplan tries to consume this block's pinout". It is
resolved explicitly below rather than left to the RTL to imply.

## Decision

We will implement the interface as **four 32-bit registers, a 32-bit
valid/ready streaming port whose source is selected by `CTRL.OUT_MODE`, and a
four-state gate machine**, with the register map held in one normative table
that generates both the RTL's constants and the documented pinout.

The full map is generated into
[`design/interface/REGMAP.md`](../../design/interface/REGMAP.md) from
`design/interface/regmap.py`; this record fixes the decisions behind it and
does not restate the tables.

### 1. Four registers, word-addressed

| Word | Register | Access | Purpose |
|---|---|---|---|
| 0 | `CTRL` | RW | `EN`, `OUT_MODE`, `SOFT_RESET` |
| 1 | `STATUS` | RO + W1C | `HT_FAIL_*`, `HT_ALARM`, `STARTUP`, `COND_READY`, `*_AVAIL`, `OVF_*`, FIFO levels |
| 2 | `DATA` | RO | conditioned FIFO; a read pops |
| 3 | `RAW_DATA` | RO | raw FIFO; a read pops; never gated |

Registers are addressed by **word index** (2 bits). Byte offsets are an
integrator's concern: a byte-addressed bus wrapper belongs in #27, not here.

`CTRL.EN` **resets to 1**. The block therefore acquires and runs its start-up
health test at power-on with no software write, which is what makes the
ratified time-to-first-valid row a property of the hardware rather than of
somebody's driver. `CTRL.OUT_MODE` resets to `conditioned`, per DR-0001 §2.

### 2. `STATUS` distinguishes "starting up" from "failed"

Both states gate the conditioned path, so `COND_READY` alone cannot tell them
apart. `STATUS.STARTUP` (start-up test in progress, nothing failed) and
`STATUS.HT_ALARM` (a latched failure) are separate bits, and a reader can
therefore tell "wait" from "intervene". This is a requirement DR-0002 implies
— its recovery path is meaningless if software cannot tell it is needed — and
did not spell out.

`STATUS` also carries two sticky **overflow** flags, `OVF_DATA` and
`OVF_RAW`. When a FIFO is full the **incoming** word is dropped, never a
buffered one, so what survives is always a contiguous run — and the flag is
how a reader learns the run ended. This is the direct answer to the hazard
DR-0001 named when it rejected register-only raw access: "risks
non-consecutive samples if the reader ever falls behind, **silently**
invalidating the dataset". With `OVF_RAW`, it is no longer silent.

### 3. One streaming port, 32 bits wide, valid/ready, mode-selected

The streaming port carries **32-bit words** in both modes. In `conditioned`
mode a word is one conditioner output block (DR-0008: 256 raw samples). In
`raw` mode a word is **32 consecutive raw samples, LSB first** — packing, not
decimation: every sample appears, in order, and `word_to_raw_bits()` in the
model is the exact inverse. DR-0001's "undecimated" requirement is met by
construction, and a captured word stream *is* a sample stream, which is what
DR-0004's sequential dataset needs.

Handshake: a transfer occurs on `str_valid && str_ready`. The port and the
register read draw from the **same** FIFO per path; a register read takes the
cycle it occurs in and the streaming port shows no valid word in that cycle,
so a word can never be delivered twice. Two access methods, one queue: a
consumer should use one or the other.

### 4. Two flush scopes — the resolution of the open question above

There are two flush signals, and the difference between them is the whole of
DR-0001 §5:

| Event | Flushes the conditioner + conditioned FIFO | Flushes the raw FIFO + partial raw word |
|---|---|---|
| `OUT_MODE` write that changes the mode | yes | **yes** |
| Health-test failure (`ht_fail_*`) | yes | **no** |
| Alarm cleared → start-up restart | yes | yes |
| `CTRL.SOFT_RESET` | yes | yes |
| `CTRL.EN` 1 → 0 | yes | yes |

- **A health-test failure never touches the raw path.** Gating or discarding
  raw on failure would remove exactly the observability needed to diagnose
  the failure and would corrupt #11's fault-injection measurements — DR-0001
  §5's stated reason. Raw acquisition continues while the alarm is latched.
- **An `OUT_MODE` change flushes both.** This is the ambiguity from Context,
  resolved in favour of DR-0001 §2's guarantee, on the following reasoning:
  the streaming port is switched onto the *other* FIFO, so flushing only the
  one being left would hand the port a queue full of pre-switch bits — the
  precise thing §2 forbids. §3's "independent of `OUT_MODE`" is a statement
  that `RAW_DATA` is not *muxed or gated* by the mode — it always reads raw
  bits, in every mode, in every health-test state — and a momentary empty
  queue after a **software-initiated** write is not a gate: acquisition never
  stops, and the next raw word is available 32 samples later.
- **A restart of the noise source flushes the raw path too**, for a reason
  that is about dataset integrity rather than about gating: a partial word
  straddling a restart would splice samples from before and after it into one
  word, and no reader could tell.

### 5. Flush timing: same cycle, and belt-and-braces

`cond_en`, `cond_flush` and `startup_req` are **combinational** on the cycle's
events, so the conditioner sees `flush` in the same cycle as the register
write or failure pulse that caused it. That matters: a registered (one cycle
later) flush would leave the conditioner free to complete a block in the
intervening cycle and push a pre-switch word into an already-flushed FIFO.
Independently, this block **discards any `cond_valid` presented in a flush
cycle**, so the guarantee holds even if a future conditioner implementation
reacts to `flush` a cycle late. `cond_en` is low in the flush cycle too, so
flush and enable are never asserted together.

### 6. Recovery has exactly one door

`STATUS.HT_FAIL_*` write-1-to-clear is the **only** way to clear a latched
alarm. `CTRL.SOFT_RESET` flushes both paths and restarts the start-up test
but deliberately does **not** clear the latches, so it cannot be used to
resume from a failure without acknowledging it — DR-0002 makes the
write-1-to-clear the recovery gesture, and a second door would make "which
one wins" a question. Clearing the *last* set `HT_FAIL_*` bit pulses
`startup_req` and re-enters the start-up state; clearing only one of two set
flags does neither. A failure pulse arriving in the same cycle as a clear
**wins** (set beats clear), so a clear can never swallow a failure.

### 7. Verification level: behavioural, per DR-0009 — stated, not re-decided

DR-0009 §2 already places this block on the behavioural side of the raw-tap
boundary, and §4 refuses to move that boundary into the middle of the digital
path. So:

- `design/interface/trng_interface.py` is the **normative** cycle-accurate
  model (DR-0009 rule 5).
- `design/interface/trng_interface.v` is synthesisable RTL, checked against
  the model **cycle for cycle, output for output** by
  `sim/tests/test_interface.py` under Icarus Verilog — skipped, never
  silently passed, when the tool is absent.
- Records from `sim/tb/interface-regfile/` carry `level: behavioral` and no
  P/V/T corner, and may not be cited for anything corner-dependent.
- **Digital timing closure at `ss` / −10 % / +125 °C remains owed**
  (DR-0009 rule 6). Nothing here shows this block closes timing; no issue
  owns that yet.

There is no transistor-level content in this block, and no schematic. The
deterministic-export discipline `design/netlist.py --check` applies to
schematics still applies here in the form the block actually has: the
register map is generated from one normative table into the RTL's included
header and the integrator-facing document, and
`python3 design/interface/regmap.py --check` fails when either is stale. The
guard runs inside the PR-blocking unit-test set, so drift fails the build
rather than being discovered at integration.

### 8. What this block does not do

- **No clock-domain crossing.** The register bus is synchronous to the
  sampler clock (DR-0012's fixed external clock). An integrator whose bus
  runs in another domain needs a CDC wrapper; that is #27's, and putting it
  here would bake one integrator's bus choice into the canary block.
- **No bus protocol.** `reg_sel`/`reg_write`/`reg_addr`/`reg_wdata`/
  `reg_rdata` is a bare synchronous register interface. APB/AHB/Wishbone
  adaptation is a wrapper, not a redesign.
- **No health tests.** RCT/APT and the start-up window are #11's; this block
  consumes `ht_fail_*`/`ht_startup_pass` and produces `startup_req`.
- **No raw-access lock.** DR-0001 §4 forbids one, and `CTRL.EN` is not a
  back door to one: it is ordinary read/write state that resets to 1, is not
  one-time-programmable, and leaves no configuration in which raw access is
  unavailable-by-default or unrecoverable.

## Alternatives considered

### Bit-serial streaming port instead of 32-bit words

- **What**: `str_bit`/`str_valid`/`str_ready`, one bit per transfer, so raw
  mode needs no packing at all.
- **Why plausible**: It is the most literal reading of "the raw tap,
  undecimated"; it removes the packing register and the partial-word flush
  case; and it makes the raw streaming rate equal the sample rate by
  construction, which is what DR-0003 measures.
- **Why rejected**: It makes the two modes structurally different — a
  conditioned word would have to be serialised anyway, so the port would
  carry 32 bits per block in one mode and 1 bit per sample in the other, and
  every consumer would need both. It also multiplies handshake overhead by 32
  for the conditioned path, and it does not remove the packing problem, only
  moves it into every consumer. Packing 32 samples LSB-first loses nothing
  (the model's `word_to_raw_bits` is an exact inverse) and lets `RAW_DATA`
  and raw streaming share one queue.

### Separate FIFOs for the register read and the streaming port

- **What**: Duplicate each path's queue so a register reader and a streaming
  consumer never contend.
- **Why plausible**: No arbitration, no "a read takes the cycle" rule, and
  the two access methods DR-0001 §3 describes become genuinely independent —
  #12 could correlate the same words through both.
- **Why rejected**: It doubles the FIFO area for a use case nobody has, and
  it introduces a worse question than the one it solves: with two queues fed
  from one source, a word must either be duplicated (so "which copy did I
  read" becomes ambiguous) or routed (so the two ports show different data
  and the "same gating behaviour" property is gone). One queue with a
  one-line priority rule is smaller and has one answer.

### Latch the health-test failure in the health-test block instead

- **What**: #11 owns the sticky flag and the alarm; this block only reads it.
- **Why plausible**: The failure is detected there, and a flag next to its
  detector is easier to reason about. It also keeps this block stateless with
  respect to health.
- **Why rejected**: DR-0002's clear path is a *register write*
  (write-1-to-clear), and its consequence is a *gate* on this block's
  conditioned path plus a restart request. Splitting the flag from the
  register that clears it and from the gate it drives would put the recovery
  sequence across a block boundary, with a three-signal handshake to keep the
  two halves consistent. #11 emits an event; this block owns the latch, the
  gate and the door.

### A single combined `HT_FAIL` bit

- **What**: One sticky failure flag, not one per test.
- **Why plausible**: DR-0002 explicitly does not mandate which ("RCT vs. APT
  distinguishable, or combined"), and one bit is one flop smaller.
- **Why rejected**: The two tests fail for different physical reasons — the
  RCT on a stuck source, the APT on a biased or injection-locked one — and
  DR-0002's own detection-latency acceptance targets for #11 are stated
  separately for each. A combined bit would make a fault-injection result
  ambiguous at the register a test reads, for one flop.

### `CTRL.EN` reset to 0 (software must start the block)

- **What**: The block powers up idle; software writes `EN = 1` to begin.
- **Why plausible**: Lower power at reset, no bits produced before anyone
  asked for them, and an explicit start is the conservative default for a
  security block.
- **Why rejected**: DR-0002 says "the same start-up test runs at power-on
  before the conditioned path is ever ungated", and the ratified
  time-to-first-valid row is stated *at power-on*. With `EN` reset to 0 that
  row would measure the driver, not the block. The power argument is also
  weak here: the entropy source's power is the ratified row, and it is not
  this register block's to gate.

## Consequences

- **Positive**:
  - #16 and #27 have a concrete, generated pinout to consume
    (`design/interface/REGMAP.md`, and `design/interface/regmap.py` as an
    importable table) instead of an English description.
  - The `en`/`flush` contract `design/conditioner/README.md` wrote down is
    now driven by something, and is checked: `sim/tests/test_interface.py`
    asserts each clause of it directly, and
    `sim/tb/interface-regfile/run_demo.py` runs the two real block models
    against each other with the conditioner's `en`/`flush` taken from this
    block's own outputs in the same cycle.
  - The ratified time-to-first-valid arithmetic is now demonstrated rather
    than asserted: the start-up scenario measures **1280 raw samples** to the
    first readable conditioned word — DR-0002's 1024-sample start-up window
    plus DR-0008's 256-sample conditioner fill, non-overlapping, exactly as
    the README row's arithmetic claims.
  - The register map cannot drift from the RTL: the RTL includes a generated
    header, and the staleness guard runs in the PR-blocking test set.
  - `OVF_RAW` converts DR-0001's named silent-dataset-corruption hazard into
    a bit a reader can check.

- **Negative / accepted cost**:
  - **An `OUT_MODE` write costs a reader up to `FIFO_DEPTH` buffered raw
    words plus a partial word.** That is a real cost of the §2/§3 resolution
    above, paid by characterization software, and the mitigation is
    procedural (drain before switching), not architectural.
  - **Two access methods share one queue**, so a consumer that uses both
    simultaneously will see each word exactly once, distributed between them
    in a way it must not depend on.
  - **A 32-bit register bus and a 32-bit streaming port is 11 external ports
    and 105 signal wires** before #27 makes any pin-multiplexing decision. An
    integrator that cannot afford them must narrow the bus in a wrapper.
  - **Timing closure remains unshown** (DR-0009 rule 6), and this block adds
    two 8×32-bit FIFOs plus a combinational flush path from the register bus
    to the conditioner to whatever a synthesis flow will eventually have to
    close.
  - **The health-test block does not exist yet**, so every run here uses a
    stand-in that pulses `ht_startup_pass` after 1024 samples and injects
    failures on a script. Nothing recorded here is evidence about a health
    test.

- **Follow-up required**:
  - **#16**: consume the "Top-level pinout contribution" table in
    `design/interface/REGMAP.md` — 11 ports, 105 wires — rather than
    inventing a pinout.
  - **#27**: instantiate `trng_interface` and `trng_conditioner_crc32` with
    `cond_en`/`cond_flush`/`cond_word`/`cond_valid` wired directly, and own
    the bus-protocol adapter and any clock-domain crossing. #27 also owes the
    byte-address decode if its bus is byte-addressed.
  - **#11**: drive `ht_fail_rct`/`ht_fail_apt` as one-cycle pulses and
    `ht_startup_pass` as a one-cycle pulse after 1024 consecutive raw
    samples; restart the start-up window on `startup_req` and never assert
    `ht_startup_pass` from a window that began before it.
  - **#14**: the hand-off DR-0009 assigned — check that these models consume
    the raw tap the way `sampler_core` presents it — now has a second
    consumer to check, not just the conditioner.
  - **New issue wanted** (nobody owns it): synthesis + static timing against
    the gf180mcu liberty files, which would close DR-0009 rule 6's gap for
    this block, the conditioner and the health tests at once.

- **Revisit if**: #27 finds the bare register bus needs a protocol this block
  should carry rather than wrap; **or** a consumer needs both access methods
  concurrently (which would make the shared-queue decision wrong); **or**
  DR-0001/DR-0002 are superseded in a way that changes the gating or flush
  rules; **or** #11's implementation cannot produce a single-cycle
  `ht_startup_pass` restartable by `startup_req`.

## Evidence

Behavioural-level records (DR-0009), written by
`sim/tb/interface-regfile/run_demo.py`:

| Scenario | What it shows |
|---|---|
| `startup` | conditioned path gated for the whole start-up window while the raw path runs from the first sample; 1280 raw samples to the first conditioned word |
| `ht-gate` | failure latches, gates and flushes the conditioned path; raw words continue to be acquired and read while the alarm is latched; recovery needs the explicit clear plus a fresh start-up pass |
| `mode-switch` | an `OUT_MODE` write in either direction leaves zero words in either FIFO |
| `overrun` | both `OVF_*` flags set, both FIFOs hold a full contiguous run, nothing buffered was overwritten |

These records have **no P/V/T corner** and may not be cited for any
corner-dependent claim (DR-0009 rule 3). Their raw source is the declared
synthetic model in `sim/tb/conditioner-crc32/source_model.py`; they are
evidence about this block, never about the entropy source.
