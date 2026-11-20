# Roadmap

gf180-trng is a true random number generator on gf180mcu, built with an open-source flow, whose
second job is to expose gaps in [klayout-tools](https://github.com/2AMLogic/klayout-tools).

Status as of 2026-11-16, `main` @ `d4a01163`.

[`WORK_PLAN.md`](../WORK_PLAN.md) is the generated snapshot of issue labels;
[`spec-row-status.md`](spec-row-status.md) is the per-row evidence history. This file orders the work.

## Where it stands

**Maturity ladder** (README): simulation-complete → layout DRC/LVS-clean → shuttle seat → measured
silicon over temperature. The block is on the first rung. Nothing has been fabricated or measured.

**Specification.** Ratified 2026-07-31
([`spec/ratification-2026-07-31-target-spec.md`](../spec/ratification-2026-07-31-target-spec.md)),
amended only through [`spec/decision-records/`](../spec/decision-records/). README row tags today:

- `missed`: **Power** (active 748.2 µW against < 500 µW; idle 2.138 µA against < 1 µA) and **Area**
  (172 828.6 µm² against < 0.05 mm²). Tracker: #700.
- `unmeasured`: **Raw rate** (a derived target) and **Raw min-entropy per bit** (owed to measured
  silicon, DR-0004). Every other row is `specified` or `derived from target`.

**Design-evidence ladder.** The verdict of record,
[`signoff/records/t1-tier-report.json`](../signoff/records/t1-tier-report.json), reads **T1 17 of
22 met** (a `mixed-signal` block is graded per partition). Tracker: #698. The five unmet rows:

| Row | Reason in the report | What moves it |
|---|---|---|
| 3.digital DRC clean | `check_failed`: 2737 violations, all `comp.tap_distance.{nwell,psub}.mv.1` | #717, then #718 |
| 5.analog corner verification | `no_evidence` | no ratified analog row has a measured quantity with a bound ([`signoff/README.md`](../signoff/README.md), "Item 5 analog") |
| 6.analog Monte Carlo | `undersized_sample` | size the mismatch campaign (Next) |
| 6.digital Monte Carlo | `not_applicable_statistical_row` | the statement is committed and refused as-is (mixed-signal scoping gap, [klayout-tools#6938](https://github.com/2AMLogic/klayout-tools/issues/6938)); see [`signoff/README.md`](../signoff/README.md), "Item 6" |
| 11.analog power delivery | `supply_spec_disclosed_unexpressible` | #701 |

Since #698 was written, 5.digital became `met` and 3.digital `unmet`: same count, different rows.

**Where `main` and its documents disagree.** Each was checked against the tree at the sha above.

1. *The 30 µm tapcell re-placement is in history but not in the tree.* Commit `8939b542` (PR #720)
   added a configurable pitch to `layout/digital/build.py` and re-placed the digital block. Merge
   `a395d6e1` resolved its conflicts to the other side, so `build.py` has no pitch setting and
   `layout/digital/reports/tap-distance.json` still reads `verdict: fail` at 49.7 µm. Merging
   PR #720 now would change no file; the work has to be redone on `main`.
2. *The ERC supply specs' tie disclosures predate the drawn ties.* The specs under
   `layout/analog/` declare no `ties[]` and disclose the omission as `unexpressible` because
   their streams drew no Nplus, Pplus or LVPWELL — but the streams now draw the Nplus and Pplus
   ties (#705, PR #826), so the disclosure's stated reason no longer matches its artifacts, as
   `layout/analog/README.md` itself records. #701 tracks the refresh.
3. *README and `layout/digital/README.md` call the digital section and the composed floorplan
   DRC-clean*; the committed reports read 2737 and 2721 violations (#879).

## Now

Startable today, one pull request each.

- **Re-place the digital block at a tighter tapcell pitch (#717).** Done when `build.py` passes
  `request.power.tapcell.distance_um`, `tap-distance.json` no longer reads `fail` against the
  retained 15 µm MV limit, and `layout/digital/reports/drc.json` reports no `comp.tap_distance.*`
  violation. `8939b542` is a starting point (14.857 µm at a 30 µm pitch, per PR #720). Base it on
  the chain PR #878 regenerated (#866): the same digital chain, re-run under the nightly's
  Yosys 0.69 / klt 0.9.1 toolchain.

In flight, not to be duplicated: #879 (correct the DRC-clean statements so the three sentences
match `drc.json` and `floorplan.drc.json` and `check.py` passes on the re-hashed README; in
review as PR #898), #866 (PR #878 merged the re-run chain on 2026-11-14; the issue stays open on
a Champion AC hold until the first scheduled nightly run shows the synthesis staleness guard
green), #520 (import convention, PR #581 held).

## Next

- **Refresh the evidence that depends on the placement (#718)**, per the DR-0029 inventory, once
  #717 lands. Done when each listed artifact is re-minted as a new append-only record on the
  re-placed geometry and the tier report shows 3.digital `met`. #487 closes with it.
- **Declare `ties[]` in the analog ERC supply specs (#701).** Its recorded blocker (#411, whether
  to draw ring well ties) is overtaken: the ties are drawn. Needs a re-read to release
  `loom:blocked`. Done when the three region reports compute `erc.missing_tie` and the tier
  report grades 11.analog on it.
- **Size the mismatch Monte Carlo campaign for 6.analog.** The citation is restored (#885, PR
  #911); `signoff/README.md` names the gap: 8 and 30 seeds against the 183 the default target
  needs, and no seeded known-bad variant. Done when a `klt yield` report over the larger sample
  set has a `sample_size` verdict other than `insufficient`.
- **Publish the ring2 paired PEX comparison (#476).** In review as PR #923. The 27-corner grid
  measured under klt 0.9.0 (`sim/records/2026-11-05-ro-ring11-ring2-pex-attempt-02.md`); its
  parked question, which producer pin covers it, predates #705 removing the single producer pin.
  Done when `signoff/evidence/post-layout/ring2/` holds the published response and `check.py`
  accepts it.
- **Record the liveness-sampler current in the power rollup (#810)**, once the scope question on
  that issue is answered. Done when the breakdown and `power_rollup.py` agree and
  `sim/characterization-analog-summary.md` quotes the same totals.
- **Refresh the bodies of trackers #698 and #700** against the tier report (an issue edit, no PR).

## Later

- **5.analog.** Question first: which analog quantity gets a ratified bound that a `klt sim`
  envelope can report pass or fail on? That is a decision record, not a simulation.
- **Power and Area rows.** The standing rulings on #700 keep both bounds and ask for analysis
  before another design round. Question first: do the levers ranked in `spec-row-status.md` and
  the `docs/area-*-2026-11-09.md` studies reach the bounds, or is there evidence of physical
  unreachability to bring back as a new decision?
- **Asymmetric fs/sf corners on the integrated sampler path (#472).** Question first: does a batch
  submission of its grid now obtain capacity and a compatible runner? (In flight: PR #932 is
  running that campaign on the batch fleet.)
- **Out-of-envelope health-test behavior.** [The plan](out-of-envelope-characterization-plan.md)
  found no supported simulation grid. Question first: what model range holds outside the envelope?

## Blocked and waiting

- **#486** needs a controlled GF180MCU DRM revision, or written confirmation of the device-class
  column, for LU.3/LU.4. It gates the final acceptance of #449 and #487 only.
- **#810** carries an open decision block; #476's is being resolved by its in-review PR #923
  (DR-0026's 2026-11-09 amendment covers the producer pin).
- **PR #413** (#339) is parked on whether its branch history may be rewritten. #339, #411 and #412
  describe floating wells that `main` no longer has, and need a re-read, not a build.
- **6.digital** waits on klayout-tools#6938 (scoping an item-6 `not_applicable`
  to one partition of a mixed-signal block), as `signoff/README.md` records;
  the statement itself is committed and its refusal is the recorded verdict.

## Not planned

- A DRBG, seeding or reseeding semantics, or bulk-rate operation (README, "Scope").
- A simulated min-entropy figure or an SP 800-90B validation claim before silicon (DR-0004).
- Relaxing a ratified row to make a result pass; an unmeetable row gets a superseding decision record.
