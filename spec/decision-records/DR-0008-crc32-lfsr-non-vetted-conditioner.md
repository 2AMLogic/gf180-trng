---
dr: DR-0008-crc32-lfsr-non-vetted-conditioner
title: Condition the raw stream with a non-vetted 32-bit CRC-32 LFSR compression at K = 8
status: Accepted
date: 2026-08-01
deciders: Builder (issue #8), under the explicit delegation in DR-0004 §"Constraint on #8" and DR-0003 §6. Not an operator ratification — see Status.
supersedes: n/a
superseded_by: n/a
related: "#8 (origin), #6, #26, #11, #12, #14; README §Target specification — Conditioning row, Delivered (post-conditioning) rate row, Time-to-first-valid row; DR-0001 (bypass + flush on OUT_MODE switch), DR-0002 (gate + flush on health-test failure), DR-0003 §6 (publish K and R_cond at the rate-binding corner), DR-0004 §Constraint on #8 (function, vetted status, K, area, entropy accounting), DR-0007 (H₀ = 0.5 is an architectural target), DR-0009 (the level this record's evidence was produced at)"
---

# DR-0008: Condition the raw stream with a non-vetted 32-bit CRC-32 LFSR compression at K = 8

## Status

- 2026-08-01: **Accepted** by the Builder of #8, filling in the blanks that
  the 2026-07-31 ratification deliberately left to this issue. This is a
  delegated decision, not an operator ratification: DR-0004's Follow-up says
  "#8: record conditioning function, vetted/non-vetted status, K, area
  estimate, and non-vetted output-entropy accounting in its own DR", and
  DR-0003 §6 says "#8 must publish K and the resulting `R_cond` at the same
  binding corner". No ratified row is relaxed here — two rows that read
  "TBD per #8" are filled in, and one arithmetic floor that read "plus
  conditioner latency" is completed. If engineering disagrees with any of it,
  the correction path is a superseding DR, not an edit to this one.

## Context

The README `Conditioning` and `Delivered (post-conditioning) rate` rows both
read "TBD per #8". Three ratified records constrain what may go in them, and
between them they leave exactly five open parameters:

**DR-0004 §"Constraint on #8"**, verbatim:

> - A **vetted** 90B conditioning function is **not mandated**. Tier 3 is
>   deferred, so nothing pre-silicon depends on having one, and the area cost
>   is plausibly prohibitive.
> - The **default assumption is a lightweight non-vetted conditioner** (von
>   Neumann, XOR/parity compression, LFSR/CRC-based compression, or similar).
> - **#8 must record, in its own DR**: which conditioning function it chose,
>   whether it is vetted or non-vetted, the compression ratio K (feeding
>   DR-0003), an **area estimate**, and — for a non-vetted function — the
>   output-entropy accounting including 90B's non-vetted penalty.
> - If #8's area estimate shows a vetted function *does* fit, that is a live
>   option and a superseding DR to this one; it is not foreclosed, merely not
>   required.

**DR-0003 §6**, verbatim:

> **6. No post-conditioning rate target is set here.** The conditioned rate is
> `R_cond = R_raw / K`, where K is the conditioner's compression ratio, which
> #8 owns. **#8 must publish K and the resulting `R_cond` at the same binding
> corner.** If a conditioned-rate number is later needed for a datasheet, it
> lands as a new DR once K is fixed — it is not silently inferred from this
> row.

**DR-0001 and DR-0002** constrain the *implementation* rather than the
choice. DR-0001 §2: switching `OUT_MODE` in either direction "**flushes the
conditioner state and the output FIFO**, so no bit produced under the previous
mode can be read after the switch", and its Follow-up makes bypassability and
clean flush "a requirement on #8's implementation, not a preference".
DR-0002's failure behavior gates the conditioned path immediately on an RCT or
APT failure and flushes the output FIFO "so no bit produced under the failing
window can be read afterward", with recovery only via an explicit clear
followed by a 1024-sample start-up test.

Two further pieces of context bear on the choice:

- **`H₀ = 0.5` is a target the source is *sized* to hit, not a measurement**
  (DR-0007, README Raw min-entropy row). DR-0007 additionally records an
  unresolved conflict between its own sizing law and the ratified Power row,
  which #7 owes a superseding DR for. A conditioner sized with no margin
  against `H₀` would therefore be sized against a number that may move.
- **The area budget is small and mostly spoken for.** DR-0004 estimates that
  a vetted (cryptographic) conditioner could consume the majority of the
  < 0.05 mm² budget by itself, and explicitly calls that an
  order-of-magnitude estimate rather than evidence. This record replaces the
  estimate for the *chosen* function with a PDK-derived inventory, and leaves
  the AES comparison labelled as the literature value it is.

### Evidence and provenance

- **Behavioural evidence** for the function's input/output behaviour:
  `sim/records/2026-08-01-conditioner-crc32-01.md` … `-05.md` (scenarios
  `h050`, `h0107`, `h003`, `stuck0`, `gate-flush`). These are
  **behavioural-level** records with no P/V/T corner, produced under the split
  ratified in DR-0009; they may not be cited for any corner-dependent claim.
- **Area** is derived from the installed PDK's own standard-cell LEF —
  `<pdk>/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lef/gf180mcu_fd_sc_mcu7t5v0.lef`,
  gf180mcuD @ open_pdks `c6d73a35f524070e85faff4a6a9eef49553ebc2b` — by
  `design/conditioner/area_estimate.py`. It is a **gate-level inventory, not a
  synthesis result**: no synthesiser, floorplanner or router has been run on
  this block, and yosys is not part of this repo's toolchain today.
- **The SP 800-90B arithmetic** is computed by
  `sim/tb/conditioner-crc32/sp800_90b.py` and unit-tested in
  `sim/tests/test_conditioner.py`, so the numbers below are re-derivable.
  **The provenance caveat DR-0004 attached to that arithmetic is inherited
  unchanged**: this repository holds no offline copy of SP 800-90B, and the
  clause numbering and the `0.85` non-vetted cap were written from the
  published expression as recalled rather than transcribed from the document.
  DR-0004 relies on the vetted/non-vetted *distinction*, not on the constant;
  so does this record's *choice*. Its *numbers* do depend on the constant, and
  are arranged so that changing one symbol (`sp800_90b.NON_VETTED_CAP`)
  re-derives them all. Before any of these numbers is used in a datasheet or a
  90B submission, both must be checked against the published standard.

## Decision

We will condition the raw stream with a **32-bit Galois LFSR compression
function**, clocked by the sampler clock, cleared at every block boundary,
absorbing **K = 8** raw bits per conditioned bit.

### 1. The function

- **Structure**: a 32-bit Galois LFSR. Each raw sample is absorbed as
  `fb = state[0] XOR raw_bit; state = (state >> 1) XOR (fb ? POLY : 0)`.
- **Polynomial**: CRC-32 (IEEE 802.3) in its LSB-first reflected form,
  `POLY = 0xEDB88320`. Chosen because it is a primitive degree-32 polynomial
  whose properties are widely published and whose 14-tap weight is cheap; no
  cryptographic property is claimed for it, and none is needed.
- **Block structure**: the LFSR is cleared to zero at the start of each
  block, `BLOCK_BITS = 32 × K = 256` raw samples are absorbed, and the state
  is then emitted as one 32-bit word. **One output word is a function of
  exactly 256 raw samples and of no earlier sample.** This is the property
  that makes the SP 800-90B conditioning-component accounting in §5 apply
  per block with `n_in = 256`, `n_out = nw = 32`.
- **Init value zero, deliberately.** With a zero state and an all-zero input,
  the LFSR stays at zero, so a stuck-at-0 raw source produces all-zero output
  words rather than a statistically flawless maximal-length LFSR sequence.
  See Consequences for the half of this that does *not* work.

### 2. Vetted status

**Non-vetted.** This is a linear compression function, not one of SP 800-90B's
vetted conditioning components (the keyed/cryptographic set — CMAC, CBC-MAC,
HMAC, the hash and block-cipher derivation functions). Its output entropy is
therefore credited with the non-vetted cap, per §5. DR-0004 does not mandate a
vetted function and the area comparison in §4 is why we do not volunteer for
one.

### 3. Compression ratio K and the conditioned rate

**`K = 8`** — 256 raw bits in, 32 conditioned bits out.

Per DR-0003 §6, at the **rate-binding corner `ss` / −10 % / +125 °C**:

| Quantity | Value at the rate-binding corner |
|---|---|
| `R_raw` (DR-0003 target) | > 1 Mbps sustained |
| `K` (this DR) | 8 |
| **`R_cond = R_raw / K`** | **> 125 kbps** |
| `R_cond` at the DR-0003 stretch rate (`R_raw` > 4 Mbps) | > 500 kbps |
| Creditable output entropy rate, `0.85 × R_cond` | > 106.25 kbit/s |

**This is a derived target, not a measurement.** `R_raw` has never been
measured — #9 owes the sampler and DR-0003's row is itself a target. `R_cond`
inherits exactly the status of the row it is derived from, and it will become
a measured figure only when `R_raw` does. DR-0003 §6 says a conditioned-rate
*spec row* is a separate DR if one is later wanted; this record publishes the
figure without asking for the row.

### 4. Area estimate

Gate-level inventory of `design/conditioner/crc32_conditioner.v` mapped onto
`gf180mcu_fd_sc_mcu7t5v0` cells, with each area read from the PDK LEF by
`design/conditioner/area_estimate.py`:

| Section | Cells | Area (µm²) |
|---|---|---|
| LFSR state register | 32 × dffrnq_1 | 2388.4 |
| LFSR feedback network | 14 × xor2_1 | 368.8 |
| block counter | 8 × dffrnq_1 | 597.1 |
| block counter increment | 7 × and2_1 + 7 × xor2_1 | 307.3 |
| terminal-count decode | 1 × inv_1 + 5 × nand2_1 + 2 × nor2_1 | 90.0 |
| clock-enable gate | 1 × icgtp_1 | 61.5 |
| flush / enable control | 2 × and2_1 + 1 × inv_1 + 2 × nor2_1 | 70.2 |
| cond_valid output strobe | 1 × dffrnq_1 | 74.6 |
| **TOTAL cell area** | **361 GE** | **3957.9** |

(1 GE = `nand2_1` = 10.976 µm² in this library.)

| Placement utilisation | Placed area | Share of the < 0.05 mm² budget |
|---|---|---|
| 80 % (aggressive) | 0.00495 mm² | 9.9 % |
| 60 % (conservative) | 0.00660 mm² | 13.2 % |
| 60 %, mux-feedback enable instead of a clock gate | 0.00844 mm² | 16.9 % |

**The conditioner's contribution to the README `Area` row is therefore
~0.005–0.008 mm², i.e. 10–17 % of the whole-block budget.** It is one
contributor among several (RO array, bias, sampler, health tests, register
file, pads); this record does not speak for the others and the README `Area`
row is not rewritten from this number alone.

For contrast, the vetted option DR-0004 left open: a compact serialised
AES-128 core at 2400–3400 GE (**literature value, unconfirmed — no AES
synthesis has been run in this repository**) is 26–37 × 10³ µm² of cell area,
i.e. **0.044–0.062 mm² placed at 60 % utilisation, or 88–124 % of the entire
block budget for the conditioner alone**. That is a quantified version of
DR-0004's "plausibly prohibitive", and it is why §2 does not take the vetted
path.

### 5. Output-entropy accounting (non-vetted)

Using SP 800-90B's conditioning-component output entropy with `n_in = 256`,
`n_out = nw = 32`, and the non-vetted cap `0.85 × min(n_out, nw)`
(`sim/tb/conditioner-crc32/sp800_90b.py`; see the provenance caveat above):

| Input min-entropy `H` (bit/raw sample) | `h_in` per block | Credited `h_out` per 32-bit word | Per output bit |
|---|---|---|---|
| 0.5 (the DR-0002 / DR-0007 design target) | 128 bit | **27.2 bit** | 0.85 |
| 0.106456 (break-even, see below) | 27.25 bit | 27.2 bit | 0.85 |
| 0.03 (DR-0002's hard floor) | 7.68 bit | 7.68 bit | 0.24 |
| 0 (dead source) | 0 bit | 0 bit | 0 |

**Break-even.** The cap is the binding term — i.e. the conditioner delivers
all the entropy a non-vetted component may be credited with — for every input
at or above

> **`H ≥ 0.106456` bit per raw sample**, equivalently `h_in ≥ 27.25` bit per
> 256-sample block.

At the `H₀ = 0.5` design target that is a **4.70× margin**. Below break-even
the conditioner, not the penalty, is the limit and output entropy falls
linearly with `H` — the conditioner does not manufacture entropy, and the
table above deliberately shows it failing to.

Three things this accounting is **not**:

- It is **not an entropy assessment**. Per DR-0004 Tier 3, no SP 800-90B
  validation or "pass" claim is made pre-silicon. `h_out` above is what the
  standard's arithmetic *would* credit for a *declared* input entropy; the
  input entropy itself is unmeasured (#12/#13 own it) and the labelling rule
  of DR-0004 Tier 2 applies to every number derived from it.
- It **assumes `h_in = n_in × H`**, i.e. that raw samples contribute
  independently. A jitter-sampled RO array's samples are not IID, and #12's
  estimate must supply the block min-entropy directly rather than by
  multiplication if the estimator finds dependence.
- It says **nothing about how the output looks**. See Consequences.

### 6. Implementation, interface, and flush

The block is implemented at the level DR-0009 fixes:

| Artifact | Role |
|---|---|
| `design/conditioner/crc32_conditioner.py` | **Normative** bit-exact behavioural model |
| `design/conditioner/crc32_conditioner.v` | Synthesisable RTL, checked against the model word-for-word |
| `design/conditioner/area_estimate.py` | The §4 inventory, re-derivable from the PDK |
| `sim/tb/conditioner-crc32/` | Demonstration testbench + the 90B arithmetic |
| `sim/tests/test_conditioner.py` | The contract below, as executable tests |

Ports (`crc32_conditioner.v`):

| Port | Direction | Meaning |
|---|---|---|
| `clk` | in | sampler clock |
| `rst_n` | in | asynchronous power-on reset |
| `en` | in | conditioned path enabled |
| `flush` | in | synchronous flush request |
| `raw_bit` | in | the DR-0001 raw tap |
| `raw_valid` | in | `raw_bit` is a new sample this cycle |
| `cond_word[31:0]` | out | conditioned output word |
| `cond_valid` | out | one-cycle strobe |

**Flush behaviour — this record's half of the DR-0001 / DR-0002 rule.** The
conditioner-internal state (LFSR + block counter) is cleared, and the partial
block discarded, whenever `flush` is asserted or `en` is deasserted. `flush`
takes priority over absorption, so a raw bit presented in the same cycle as
the gate is not absorbed: it belongs to the failing window. The consequence
that DR-0002 actually asks for — *no bit absorbed before the gate can
influence any word read after it* — holds by construction, because the state
is cleared and each word depends on nothing before its own block; it is
checked directly in `sim/tests/test_conditioner.py`
(`test_no_pre_flush_bit_influences_a_later_word`) and recorded in
`sim/records/2026-08-01-conditioner-crc32-05.md`.

**Scope boundary with #26.** This record owns only the conditioner-internal
half. The output FIFO, the `OUT_MODE` mux and its bypass path, the
`DATA` / `RAW_DATA` registers, the latched `HT_FAIL_*` flags, and the
generation of `en` / `flush` from the health-test gate and the `OUT_MODE`
write are **#26's**. The contract between them is exactly the port list
above: #26 must assert `flush` for at least one sampler clock on a
health-test-failure gate and on an `OUT_MODE` write in either direction, and
must hold `en` low for the whole start-up-test window.

**Bypass** (DR-0001's other requirement on #8) is satisfied structurally: the
conditioner is not in the raw path at all. `RAW_DATA` and `OUT_MODE = raw`
read the raw tap directly, so bypassing costs a mux in #26's streaming path
and nothing in this block.

### 7. Time-to-first-valid

The README row reads "≥ ~1.05 ms at 1 Mbps … 1024 consecutive raw samples for
the start-up health test (1.024 ms) **plus conditioner latency**". This record
supplies the missing term. Because the conditioner is held cleared while
`en` is low, the start-up window and the block fill do **not** overlap:

> 1024 start-up samples + 256 block samples = **1280 samples = 1.28 ms at
> 1 Mbps**, at the same binding corner (`ss` / −10 % / +125 °C, slowest
> sampling).

This is arithmetic on two already-ratified numbers, not a new target.

## Alternatives considered

### Von Neumann corrector

- **What**: The classic debiaser — consume raw bits in pairs, emit `0` for
  `01`, `1` for `10`, nothing for `00`/`11`. Named explicitly in DR-0004's
  default-assumption list.
- **Why plausible**: Trivially small (a 2-bit shift register and a comparator,
  well under 100 GE), needs no polynomial, and produces exactly unbiased
  output from an IID biased source with no distributional assumption beyond
  independence.
- **Why rejected**: Its output rate is **data-dependent**, so `R_cond` is a
  random variable rather than a number, and DR-0003 §6 asks this record for a
  number. Worse, the rate collapses precisely where it matters: at
  `H = 0.5` (`p ≈ 0.293`) the yield is `p(1−p) ≈ 0.207` bit out per bit in,
  and at DR-0002's `H = 0.03` floor it is `≈ 0.02` — a > 10× swing in
  delivered rate driven by exactly the parameter that is unmeasured. It also
  requires independence to debias at all, and a jitter-sampled RO stream's
  dependence is the failure mode most likely to be present. Finally, being
  unbiased is not the same as carrying entropy, so von Neumann would still
  need the same 90B accounting on top.

### XOR / parity compression (XOR of K consecutive raw bits)

- **What**: Emit one bit per K raw bits, the parity of the block. Also on
  DR-0004's list.
- **Why plausible**: The smallest possible conditioner — one XOR, one flop,
  one counter, perhaps 60 GE — and its bias-reduction behaviour is the
  textbook piling-up result.
- **Why rejected**: It discards the block's structure entirely, mapping 256
  bits onto 1. To reach the same 32-bit output word it needs 8× the raw bits
  this record's function needs for equal `n_out`, i.e. `K = 64` and
  `R_cond > 15.6 kbps`, an eightfold worse rate for no accounting benefit
  (the non-vetted cap is the binding term either way). It is also the option
  with the weakest response to *correlated* input: the piling-up argument
  DR-0007 §Alternatives already rejected for the XOR-of-rings case is the
  same argument here, and it is invalid for the same reason.

### `K = 2` or `K = 4`

- **What**: Same function, shorter block (64 or 128 raw bits per word), for
  `R_cond > 500 kbps` or `> 250 kbps`.
- **Why plausible**: Rate is the scarcest quantity in this spec — DR-0003's
  target already forced an architectural change (DR-0007), and giving 8× of
  it back to the conditioner is a real cost.
- **Why rejected**: The break-even input entropy scales inversely with the
  block length: `K = 2` needs `H ≥ 0.4258` and `K = 4` needs `H ≥ 0.2129`
  bit/sample to reach the cap, i.e. margins of only 1.17× and 2.35× against a
  target that DR-0007 records as architecturally strained and that #7 may yet
  move. `K = 8`'s 4.70× margin means the conditioner still delivers full
  credit even if the measured `H` comes in at a fifth of the target. `K` is a
  counter terminal-count parameter, so a superseding DR can trade margin back
  for rate cheaply once #12 has a measured `H` — the reverse trade, discovering
  after tape-out that `K` was too small, cannot be made at all.

### `K = 16` or larger

- **What**: A 512-bit block, break-even `H ≥ 0.0532`, `R_cond > 62.5 kbps`.
- **Why plausible**: Even more margin, and it would still clear DR-0002's
  `H = 0.03` hard floor by a factor of ~1.8 if the source ever ran that badly.
- **Why rejected**: The extra margin is bought below the point where it is
  useful. DR-0002 already refuses to parameterise health tests at
  `H ≤ 0.03`, so a source weak enough to need `K = 16` is a source the block
  is required to gate rather than condition. Halving an already-scarce
  delivered rate to buy margin in a region the health tests declare
  out-of-bounds is the wrong trade.

### A vetted 90B conditioning function (AES-CMAC or HMAC-SHA-256)

- **What**: Take the vetted path DR-0004 left open, removing the 0.85 cap and
  making the block submission-shaped on day one of silicon.
- **Why plausible**: It is what a production TRNG normally does; it removes
  the non-vetted penalty entirely; and DR-0004 explicitly invited this record
  to reopen it if the area worked out.
- **Why rejected**: The area does not work out. §4 puts a compact serialised
  AES-128 at **88–124 % of the entire block's < 0.05 mm² budget for the
  conditioner alone**, before the RO array, bias, sampler, health tests and
  register file take their share. And it buys nothing this project can cash
  in: DR-0004 Tier 3 defers validation to measured silicon, so the pre-silicon
  value of removing a penalty on a claim that is not being made is zero.
  Deliberately left live: if the block is ever retargeted with a bigger area
  budget, this is a superseding DR, not a re-derivation.

### No conditioner — ship raw only

- **What**: Expose the raw tap and let the integrator condition.
- **Why plausible**: Zero area, zero rate loss, no non-vetted penalty to
  account for, and DR-0001 already guarantees unconditional raw access — an
  integrator with a DRBG conditions the seed anyway.
- **Why rejected**: The README `Interface` row, DR-0001 and DR-0002 all
  assume a conditioned path exists — `DATA`, `OUT_MODE = conditioned` (the
  reset default), the output FIFO, and the entire health-test gating
  behaviour are defined in terms of it. Removing it is not a smaller version
  of this record; it is a superseding DR against three ratified ones. It also
  removes the only thing that makes a health-test failure *actionable* at the
  interface: with no gated path, "failure" would mean nothing but a status
  bit.

## Consequences

- **Positive**:
  - The two README rows that read "TBD per #8" can be filled in, and the
    time-to-first-valid floor stops carrying an open term.
  - #26 gets a concrete port-level contract for the conditioner-internal half
    of the flush rule, so the two halves cannot drift.
  - #12 gets a concrete conditioned-dataset definition: 32-bit words, each a
    function of exactly 256 consecutive raw samples, with the state cleared
    between them — which is what makes conditioned-stream datasets meaningful
    to analyse block-by-block.
  - The area question DR-0004 flagged as an order-of-magnitude guess now has
    a PDK-derived number behind it for the chosen function, and a quantified
    (if literature-sourced) comparison for the rejected one.
  - `K` and the polynomial are parameters, and the RTL is checked against a
    normative model, so a superseding DR that moves `K` is a one-line change
    plus a re-run, not a redesign.

- **Negative / accepted cost**:
  - **The conditioner destroys entropy, by construction.** At the design
    target it takes a raw stream carrying 500 kbit/s of (targeted) entropy and
    delivers a conditioned stream creditable with 106.25 kbit/s. That ratio is
    the non-vetted penalty and `K` together, and it is the price of a
    fixed-rate output with a stated accounting.
  - **A linear conditioner makes a dead source look alive.** Feed a stuck-at-1
    or otherwise deterministic stream into a CRC and the output is a
    maximal-length LFSR sequence: it will pass a monobit test, a runs test,
    and most of what a casual reader would try. The `h003` scenario in
    `sim/records/2026-08-01-conditioner-crc32-03.md` shows a stream with a
    measured raw min-entropy of 0.0296 bit/sample producing a conditioned
    stream with `P(1) = 0.4927`. **The output's appearance is not evidence
    about the source**, ever. This is precisely why DR-0002 puts the health
    tests on the *raw* stream and gates the conditioned path, and why DR-0001
    keeps raw access unconditional. The zero-init choice in §1 buys visibility
    for the stuck-at-**0** case only; stuck-at-1 remains invisible at the
    output, and this record does not pretend otherwise.
  - Being non-vetted caps creditable output entropy at 0.85 bit/bit no matter
    how good the source is, so the last 15 % is unreachable without an AES or
    hash core.
  - Time-to-first-valid grows from 1.024 ms to 1.28 ms at 1 Mbps because the
    flush rule forbids overlapping the start-up window with the block fill.
    That is a deliberate trade of latency for the guarantee that no bit
    absorbed before a passing start-up test is readable after it.
  - The area number is an inventory, not a synthesis run. A real synthesis
    will add buffering and may implement the counter differently; treat
    ~360 GE as a floor and the 60 %-utilisation figure as the planning number.

- **Follow-up required**:
  - **#26**: implement the register/streaming half — output FIFO, `OUT_MODE`
    mux and bypass, `DATA` / `RAW_DATA`, and the `en` / `flush` generation
    described in §6. The FIFO flush DR-0002 requires is #26's; the internal
    flush is done here.
  - **#12**: report conditioned-stream datasets as 32-bit words with the block
    structure above, and supply block min-entropy directly rather than as
    `n_in × H` if the estimators find dependence between raw samples.
  - **#7**: if the superseding DR that #7 owes moves `H₀` or the raw-rate row,
    re-check §3 and §5 against the new numbers. The *choice* here does not
    depend on them; the margin figure (4.70×) and `R_cond` do.
  - **#11 / #14**: the RTL in `design/conditioner/crc32_conditioner.v` is
    intended to be instantiated as-is; verify it against
    `crc32_conditioner.py` after any edit (the check already exists).
  - **New issue wanted**: run a real synthesis (yosys + the gf180mcu
    liberty files) over the conditioner RTL to replace §4's inventory with a
    synthesised gate count and a timing check at `ss` / −10 % / +125 °C. No
    issue currently owns that, and no synthesis toolchain is set up in this
    repo.
  - **README**: `Conditioning`, `Delivered (post-conditioning) rate` and
    `Time-to-first-valid` rows updated alongside this DR. The `Area` row is
    **not** rewritten — this block is one contributor to it.

- **Revisit if**: #12's measured `H` at the entropy-binding corner lands below
  ~0.11 bit/sample (the break-even, at which point `K` must grow or the rate
  claim must move); or #7's superseding DR moves `H₀` or `R_raw` enough to
  change the margin argument in the `K = 2`/`K = 4` alternative; or the area
  budget grows enough that a vetted conditioning function fits, in which case
  DR-0004's invitation applies and this record is superseded; or the recalled
  non-vetted cap turns out, on checking the published standard, not to be
  `0.85 × min(n_out, nw)`.
