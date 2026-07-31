# Ratification of the target specification — 2026-07-31

**Decision**: the target specification in [`README.md`](../README.md)
§Target specification is **ratified**, conditional on (and together with) the
amendment package tracked as issue #29. Ratified by Robb Walters
(engineering), the named human decision that issue #1 exists to capture; the
operator's ratification comment is on issue #1 (2026-07-31), and the
amendments it is conditional on are issue #29's.

This note is an index and a date-stamp. **The decisions themselves live in the
decision records below** — they are the single source of truth, and this note
does not restate or override any of them.

## What was ratified

| Record | Status | Ratification action |
|---|---|---|
| [DR-0001](decision-records/DR-0001-raw-and-conditioned-output-paths.md) — raw + conditioned output paths, raw always observable | Accepted 2026-07-31 | Accepted as proposed, unamended |
| [DR-0002](decision-records/DR-0002-health-test-parameters-and-failure-behavior.md) — RCT/APT cutoffs as formulas in H at α = 2⁻⁴⁰, latch-and-gate | Accepted 2026-07-31 | Accepted **with amendments**: APT degeneracy floor + revisit trigger (A2); independent verification of the formulas and all ten cutoff rows recorded (A6). No parameter, formula, or cutoff changed. |
| [DR-0003](decision-records/DR-0003-throughput-defined-at-the-raw-tap.md) — > 1 Mbps sustained at the raw tap, binding at the slowest-RO corner | Accepted 2026-07-31 | Accepted as proposed, unamended |
| [DR-0004](decision-records/DR-0004-sp-800-90b-path-pre-silicon.md) — designed-for-90B + bounded sim-stage min-entropy estimate; validation deferred to silicon | Accepted 2026-07-31 | Accepted as proposed, unamended |
| [DR-0007](decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md) — N-way XOR-combined ring-oscillator array with a stated jitter-budget sizing law | Accepted 2026-07-31 | **New at ratification** (A1) — closes the entropy-source gap #1 flagged |

[DR-0005](decision-records/DR-0005-sim-harness-record-granularity.md) and
[DR-0006](decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md)
were already `Accepted` on their own merits (sim-harness record granularity;
RO-jitter PVT/seed sampling strategy). They are unaffected by this
ratification and are listed only so the numbering is not mistaken for a gap.

## The amendment package (#29)

Ratification was conditional on six amendments from an external spec review
(the review is comment-of-record on #1; the work is #29):

- **A1 — entropy source.** The measured jitter and the draft's 1 Mbps × H₀ = 0.5
  operating point did not meet: a single 5-stage ring supports H ≈ 0.5 at
  ~3–5 kbps, ~220–370× short in `Q` at the target rate. Operator decision: close
  the gap **architecturally** — the rate target stands and the entropy source
  becomes an N-way XOR-combined RO array with a stated sizing law
  (**DR-0007**), rather than lowering the rate or re-labelling H₀.
- **A2 — APT degeneracy floor** added to DR-0002 (at α = 2⁻⁴⁰, W = 1024 the
  cutoff reaches W at H = 0.04 and no valid cutoff exists at H ≤ 0.03), with a
  revisit trigger and the structural (not parametric) fix named.
- **A3 — entropy-binding corner.** Stated as "measured minimum-`Q` corner,
  expected cold / +10 % supply; process letter TBD by #13", with the corner
  *metric*'s dependence on the sampler clock source (#9) recorded.
  `sim/characterization-ro-delay-cell-jitter.md` was corrected: its
  "Safe to size against" item 3 had sent entropy-per-bit margin sizing to the
  entropy-*best* corner, contradicting DR-0003 §4 / DR-0004. No measured number
  changed — only the interpretation, and the correction is marked in place.
- **A4 — Power row corner bindings** and a definition of "idle" added to the
  README. No power or leakage measurement exists anywhere in `sim/`; the
  characterization task is filed as **#32**, and the row is marked unevidenced
  until it lands.
- **A5 — four missing canonical rows** added to the README table (raw
  min-entropy per bit; conditioning and delivered rate; time-to-first-valid;
  operating envelope), plus the "entropy source only, no DRBG" scoping line.
- **A6 — verification on the record.** DR-0002's cutoff formulas and all ten
  table rows were independently reproduced by exact binomial computation
  against SP 800-90B §4.4.1/§4.4.2; recorded in DR-0002, no change required.

## What ratification does and does not mean

- **It makes the table binding.** Per [`CLAUDE.md`](../CLAUDE.md), agents do
  not relax the ratified spec to make results pass. A row that cannot be met
  is a superseding decision record, not an edit.
- **It does not turn placeholders into claims.** Three rows remain explicitly
  unmeasured and are labelled as such in the table: raw min-entropy per bit
  (H₀ = 0.5 is a design target, not a measurement — #12/#13), conditioning and
  delivered rate (TBD per #8), and Power (no supply-current or leakage evidence
  exists yet). Ratifying the table ratifies those *placeholders and their
  owners*, not numbers nobody has measured.
- **It does not weaken the maturity ladder.** No SP 800-90B conformance claim
  is made pre-silicon (DR-0004 Tier 3), and no simulated estimate may be
  reported as an entropy assessment.
- **It satisfies the layout-lock gate.** The 2026-07-28 delegation on #1 let
  design-phase work proceed on the draft while requiring ratification before
  layout locks to the spec; that gate is met as of this note.

## Known live tension, recorded rather than resolved

DR-0007's first-cut array size (N₀ = 560 rings against today's white-noise-only
jitter evidence) projects an order of magnitude more power than the `< 500 µW`
active row allows — roughly 250 mW by an order-of-magnitude estimate with no
evidence record behind it. Ratification does **not** paper over this. DR-0007
records it as an open conflict with named reduction levers (shorter rings, and
resolving the flicker contribution that today's √t extrapolation excludes),
binds #7 to close it, and requires a superseding DR — not a quiet under-sizing
of the array — if it cannot be closed. The measurement that will settle it is
**#32**.
