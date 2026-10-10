# Out-of-envelope health-test characterization: model-bound audit and plan

Status: **plan / feasibility assessment (issue #467). Not a measured report.**
No transistor simulation was run to produce it, it adds no evidence record, and
nothing here verifies the ratified operating-envelope row. That row's clause
"outside it, behavior is health-test-detected, not specified" (`README.md`,
"Operating envelope") **remains unverified** after this document.

Conclusion in one paragraph: the supported model range outside
-40 ... +125 degC and 2.97 ... 3.63 V is **not established** from the sources
checked, so **no supported simulation grid** exists today (section 3). Separately,
the one prior cost datum extrapolates to roughly 3,400 CPU-hours for a single
run of the required length, about 140 times the 24 CPU-hour planning cap
(section 6). Both limits are reported as limits; neither is a pass or a fail of
any health-test or entropy claim. Section 9 names the missing capabilities.

## Contents

1. Sources checked and revisions
2. Audit per envelope face
3. Eligible-point table: no supported simulation grid
4. Deck adaptation and cycle mapping
5. Capture length arithmetic
6. Budget against the 24 CPU-hour cap
7. Result fields
8. Replay-test plan for the eventual analysis
9. Handoff: feasibility-limit conclusion and conditional follow-up draft

## 1. Sources checked and revisions

Everything below was read from the repository or the locally installed PDK;
this session had no web-fetch capability, so **no upstream web documentation
(PDK datasheets, readthedocs pages, foundry reliability documents) was
consulted, and no claim here depends on one.** Where an authoritative bound
would normally come from such a source it is marked *not established*.

| Source | Revision / identity | Used for |
| --- | --- | --- |
| Installed PDK, variant selected by `sim/pdk.json` | `gf180mcuD`, `SOURCES` file: `open_pdks c6d73a35f524070e85faff4a6a9eef49553ebc2b` | which models are simulated |
| `libs.tech/ngspice/sm141064.ngspice` in that PDK | header: Document No. `YI-141-SM064`, Revision 9, "0.18um 3.3V/6V high voltage MCU process" | device-model text, `tnom`, geometry bins, temperature comments |
| `libs.tech/ngspice/design.ngspice` in that PDK | same install | global switch parameters (`sw_stat_global`, `sw_stat_mismatch`) |
| `design/sampler_core.spice` | repo `HEAD` `afe01cc05307cc2897005536abc8830e00786ae2` (generated from the schematic) | which devices are actually used |
| `sim/harness/corners.py`, `sim/harness/runner.py`, `sim/pdk.json` | same repo revision | default corner/section bundles, seed handling |
| `design/health_test/rct_apt.py`, `design/health_test/ring_liveness.py` | same repo revision | normative RCT/APT and per-ring behaviour |
| `sim/tb/array-liveness-tap-phase-clocked/tb.json` and `sim/records/2026-08-03-array-liveness-tap-phase-clocked-01.md` | same repo revision | candidate deck, clock, seeds, only cost datum |
| `spec/decision-records/DR-0012-transient-noise-simulation-methodology.md` | same repo revision | four-seed policy, long-capture limits |
| `sim/characterization-raw-min-entropy-and-battery.md`, section "Why the entropy-supporting rate cannot be simulated directly either" | same repo revision | prior cost reasoning |
| `sim/tb/ro-array-supply-ripple/README.md` | same repo revision | existing outside-envelope caveat (#414) |

Full DR filenames are used because two records share the number DR-0012
(tracked separately in #468); refresh the citations if that is resolved.

Circuit device models: the netlist `design/sampler_core.spice` instantiates
only `nfet_03v3` and `pfet_03v3` (23 instances of each; no resistors,
capacitors, diodes or BJTs, no 6 V devices). In the model file both are BSIM4
(`level = 54`) binned subcircuits, `tnom = 25` degC. The oscillator stages use
L = 0.28 um with W = 0.22 um (n) / 0.44 um (p) plus length 2 um starving
devices, so the geometry sits in the lowest bins (for example `nfet_03v3.0`:
`lmin 2.8e-7`, `wmin 2.2e-7`); that is a geometry-range fact, not a
voltage or temperature bound.

Bound searches performed on `sm141064.ngspice`: comment lines containing
"range", "valid", "limit", "recommend", "safe", "absolute", "maximum" or
"breakdown", and every line containing "Temperature"/"TEMPERATURE". Results:
geometry-range parameter blocks; the generic "extracted from test structures
with various dimensions ... take note of this limitation when extending design
& simulation beyond the test conditions" caveat (line 38254); the resistor
section's "Temperature: -40, 0, 25, 50, 75, 100 and 125C" characterization
note (line 38246); BSIM4 temperature-coefficient parameter blocks. **None of
these states a voltage or temperature validity range, recommended operating
range or absolute-maximum rating for `nfet_03v3` or `pfet_03v3`.** The only
temperature statement in the file is about resistors, which this circuit does
not contain.

## 2. Audit per envelope face

Three notions are kept apart: *model-characterization range* (where the
foundry says the fit was extracted), *recommended operation*, and *absolute
maximum* (damage/reliability, not model validity). Convergence of ngspice at a
point, or the device name saying "3v3", establishes none of them.

| Face | Envelope edge | Model-characterization range | Recommended operation | Absolute maximum | Disposition |
| --- | --- | --- | --- | --- | --- |
| Low supply | 2.97 V | not established (no stated range in model file; PDK docs not consulted) | not established | not established (a low supply is not a damage question, but that is not a model-validity statement) | **excluded** |
| High supply | 3.63 V | not established | not established | not established; the 6 V devices in the same process are not the ones instantiated, so their ratings do not transfer | **excluded** |
| Cold | -40 degC | not established for the MOS models (only the resistor note above mentions -40) | not established | not established | **excluded** |
| Hot | +125 degC | not established for the MOS models (only the resistor note above mentions 125) | not established | not established | **excluded** |

Terminal-bias constraints (gate-source, drain-source, bulk-source and
well/diode junction limits) for the 3.3 V devices were likewise not found in
any checked file: **not established**. No numeric limit is assumed anywhere in
this plan.

"Excluded" means: not simulated by this plan, with the reason recorded. It
does not mean the behaviour there is benign or unsafe.

Existing overlap, absorbed rather than duplicated: #414's
`sim/tb/ro-array-supply-ripple/` already drives rails above 3.63 V (its README
says positive excursions at the 3.63 V binding point leave the envelope and
labels each rail `in`/`OUT`). It measures deterministic ring-timing
sensitivity, not health-test detection, and itself does not claim model
validity there. The clause it touches is therefore also not established by
that experiment.

## 3. Eligible-point table: no supported simulation grid

The issue caps any grid at eight PVT points (outside-envelope points plus
matched boundary controls) and four fixed seeds per stochastic point, at most
32 baseline runs, with convergence checks budgeted separately.

Because every face is *excluded* in section 2, the table of eligible
outside-envelope points is empty:

| # | Corner sections | Temperature | Supply | Role | Seeds |
| --- | --- | --- | --- | --- | --- |
| (none) | | | | | |

**Result: no supported simulation grid.** Evidence: section 1 (sources and the
absence of any stated MOS validity range) and section 2 (per-face
disposition). Boundary controls (points on the envelope edge, which are
in-model) would be eligible but have no purpose without an outside point to
pair with, and in-envelope behaviour is covered by existing records.

Parameters that any future grid must fix once bounds exist, so a later
reviewer cannot widen them silently:

- Seeds: the four integers `1, 2, 3, 4` (the harness default,
  `sim/harness/cli.py`: `range(1, default_runs + 1)` with `default_runs = 4`,
  emitted as `.option seed=<n>` by `sim/harness/runner.py`). DR-0012 requires
  four seeds per reported stochastic point unless a justified departure is
  recorded.
- Model sections: the repository bundle names in `sim/harness/corners.py`
  (`typical`, `ff`, `ss`, `fs`, `sf` for MOS, with matching `bjt_`/`diode_`/
  `res_`/`moscap_`/`mimcap_` families), always preceded by `design.ngspice`.
  The outside-envelope sections would still be these in-envelope-extracted
  fits.
- Maximum total: 8 points x 4 seeds = 32 runs.

## 4. Deck adaptation and cycle mapping

Candidate deck: `sim/tb/array-liveness-tap-phase-clocked/`, which instantiates
the shipped `design/sampler_core.spice` topology (two `ro_ring11` rings,
per-ring `ro_buf`, `xor2`, four `sampler_dff`: `xsb` on the XOR node, `xsv` on
`vdd`, `xsr1`/`xsr2` on the ring buffer outputs). It runs a fixed external
clock `tclk_per = 1.0007 us`, `rst_n` tied high, both enables tied high, an
ideal supply, four noise seeds by default and `tstop = 3.000003 us`. It
measures phase cost, not a health-test window, so it **cannot be used as is**.
Required adaptations (to be made in the follow-up, not here):

1. **Observations.** Sample the shipped digitizer outputs `raw_bit` (xsb),
   `raw_valid` (xsv), `ring_bit1`, `ring_bit2` (xsr1/xsr2) once per clock
   cycle. Analog zero crossings of the ring nodes must not substitute for these
   digitizers.
2. **Clock.** Keep the fixed external period 1.0007 us, and keep the existing
   off-grid timing offsets (`tclk_del` 5.003 ns, `tclk_tr` 0.203 ns) that avoid
   landing on the 10 ps noise breakpoints (the deck's recorded solver
   limitation). Do not shorten windows or raise the clock to save time.
3. **Reset and enable timing.** Hold `rst_n` low and enables low through a
   declared settling interval, release reset, then enable; the first accepted
   sample is the first rising clock edge after both release. The interval is
   recorded and excluded from the 3072-sample count. `startup_req` is asserted
   to the health-test model for one cycle at that point (the model's
   `restart_window()`), mirroring a power-on restart.
4. **Supplies.** `vdd`, `vddr1`, `vddr2` set to the point's supply with the
   settling interval applied after the supply and temperature are set; the
   deck currently uses one ideal source, so supply-network effects are out of
   scope and stay so.
5. **Logic thresholds.** A digitized output is read at a fixed instant after
   each rising edge (declared in the deck, for example mid-period). Level above
   0.7 x supply is `1`, below 0.3 x supply is `0`, otherwise **unresolved**.
   These thresholds are declared assumptions, not measured values; an
   unresolved sample is never coerced to a bit.
6. **Raw-valid alignment.** `raw_valid` is itself a digitized output. A cycle
   is an accepted raw sample only if `raw_valid` resolves to `1` for it.
   Cycles with `raw_valid` `0` are passed to the model as `raw_valid = False`
   (they do not advance counters), and cycles with an unresolved level are
   counted as invalid and not passed as samples.
7. **Cycle mapping to the models.** One simulated clock rising edge equals one
   call per model:
   - `HealthTest.from_h(H0).step(raw_bit, raw_valid, startup_req)` with the
     digitized `raw_bit`/`raw_valid` of that cycle;
   - `RingLivenessMonitor.from_h(H0).step((ring_bit1, ring_bit2))` with the two
     digitized ring bits of that cycle. The monitor has no valid input, so
     cycles without a resolved ring bit must be handled by declaring that ring
     stream *incomplete* from that point rather than inventing a bit.
8. **Declared assumptions.** H0 = 0.5, W = 1024, `C_RCT` = 81, `C_APT` = 824,
   startup 1024 clean samples are the existing ratified draft values used as
   fixed assumptions. They are not measured entropy and are not tuned. The
   models report event pulses; latching and gating belong to the interface
   block and are out of scope. The models also do not represent digital-cell
   failure at abnormal supply or temperature, which is exactly what the
   analog digitizers in the deck would expose.
9. **Missing observations.** Never fill gaps with repeated or synthetic bits.
   A capture that ends early, fails to converge, or has unresolved cycles is
   reported as such (section 7).

## 5. Capture length arithmetic

- Start-up: 1024 accepted raw samples (`startup_samples = W`). The first APT
  window is the same 1024 samples (windows are non-overlapping and the first
  begins at restart).
- Two complete APT windows: 2 x 1024 = 2048.
- Requirement: startup + two windows = **3072 accepted raw samples**, of which
  at least **2048 follow any declared post-startup perturbation**, so the
  perturbation is followed by two complete windows.
- Per-ring monitoring needs at least `C_LIVE` = 81 consecutive resolved
  observations after the onset of a stall; the 2048 post-perturbation samples
  cover this.
- Duration at the fixed period: 3072 x 1.0007 us = **3.0741504 ms**
  (3072 x 1.0007 = 3074.1504 us). Reset, settling and any `raw_valid` gaps add
  to this; this is arithmetic, not a runtime measurement, and not a proof of
  the raw-rate target.

Relative to the existing deck's `tstop` of 3.000003 us, the requirement is
3074.1504 / 3.000003 = about 1024.7 times longer, and that deck's 3.000003 us
contains only about 3 clock periods.

## 6. Budget against the 24 CPU-hour cap

The 24 CPU-hour aggregate planning cap (including convergence checks) is a
scope choice, not a hardware or model limit. No simulation was run for this
estimate.

Only datum used: `sim/records/2026-08-03-array-liveness-tap-phase-clocked-01.md`
(the candidate deck): 4 runs, `tstop = 3.000003 us`, summed `wall_time` 799.8
minutes, which the record states is summed per-run ngspice cost inflated by
contention between concurrent runs.

| Quantity | Value | Basis |
| --- | --- | --- |
| Cost per run at 3.000003 us | 799.8 / 4 = 199.95 min = 3.3325 CPU-h | record above |
| Scale factor to 3.0741504 ms | 1024.72 | section 5 |
| Naive linear cost per run | about 3,415 CPU-h | 3.3325 x 1024.72 |
| One point, four seeds | about 13,660 CPU-h | x 4 |
| Cap | 24 CPU-h | issue scope |
| Runs the cap allows | about 0.007 | 24 / 3,415 |
| One point, four seeds vs cap | about 570x over | 13,660 / 24 |
| Full 8 points x 4 seeds | about 109,000 CPU-h, about 4,550x over | x 32 |

Uncertainty, stated plainly: the figure is a linear extrapolation from one
record whose cost is contention-inflated (the same caveat
`sim/characterization-raw-min-entropy-and-battery.md` makes for its own
13.6-19.3 minute figures), so it is an order-of-magnitude estimate. Take an
optimistic factor of 10 for contention and for a quieter machine and one run
is still about 340 CPU-h and one four-seed point about 57 times the cap.
Linear scaling is also not guaranteed (the deck's cost is dominated by the
10 ps noise breakpoints, a per-simulated-time cost that does scale with
duration, but long-run memory and storage growth could make it worse).

Step and storage bounds: the deck prints at `tstep = 1p`; 3.0741504 ms /
1 ps is about 3.07e9 points per saved vector if the print step is kept, which
is not a workable output size, and the solver step is bounded below by the
10 ps noise breakpoints (about 3.07e8 steps at minimum). The output would need
to be decimated to clock-edge samples inside the deck. Neither bound has been
measured here.

Convergence checks are budgeted separately from the 32 baseline runs and would
add to the figures above; no allowance is made for them because the baseline
already exceeds the cap.

Conclusion: **infeasible within the 24 CPU-hour budget by a gap of about
two to three orders of magnitude** for even one point at the required length.
The issue forbids closing the gap by shortening windows or raising the clock,
and this plan does not. Cheaper structures (a non-noisy deck, a reduced
digitizer-only model, partitioning into shorter chunks with state carried over)
are possible directions, but each is a methodology change with its own claim
limits and is not assumed here.

## 7. Result fields

Fields are separate; none implies another. The vocabulary replaces the
original proposal's "healthy/degenerate" labels and makes no first-failure
distance, monotonic-coverage or entropy-certification claim.

1. **Model admissibility** (per point): `admissible` / `not established` /
   `excluded`, with the section 2 citation. Nonconvergence is not recorded
   here.
2. **Run status** (per run): `converged` / `nonconverged` / `invalid
   digitization` (unresolved levels exceeded a declared count) / `truncated`.
   These are never reported as alarms or as passes.
3. **Observation sufficiency**: accepted raw samples observed (target 3072),
   accepted samples after the perturbation (target 2048), resolved
   consecutive observations per ring after onset (target at least 81);
   `sufficient` only if all three targets are met in a `converged` run,
   otherwise `insufficient observation`.
4. **Stream properties** (counts only): sample count, count of invalid
   (unresolved or `raw_valid` low) cycles, longest run of equal bits, APT
   reference-value counts per complete window, per ring longest run.
5. **Event flags** with first-event indices: `ht_fail_rct`, `ht_fail_apt`,
   `ring_stuck[0]`, `ring_stuck[1]` each as observed/not observed plus the
   index of the first pulse (the sample index at which the model fired).
   Alarms seen in an incomplete capture are **retained** with their index even
   if sufficiency is `insufficient`.

Reading rules:

- No alarm in a short or incomplete run: **insufficient observation**.
- No alarm in a complete, converged run: **no alarm observed at this sampled
  point**. It is not evidence of healthy entropy.
- Not-established or excluded model support, and over-budget duration, are
  reported as themselves and never converted into a passing verdict.
- Results hold only at the sampled points; intervals between and beyond them
  are untested.

## 8. Replay-test plan for the eventual analysis

When captures exist, the analysis that replays them through the models needs
its own offline tests (not added by this documentation change), at least:

- RCT and per-ring repeat boundaries: 80 repeated samples must not fire, 81
  must fire exactly once and saturate (cf. `test_does_not_fire_below_cutoff` and
  `test_fires_exactly_once_for_a_ring_stuck_far_beyond_the_cutoff` in
  `sim/tests/test_ring_liveness.py` and the RCT counterparts in
  `sim/tests/test_health_test.py`).
- APT window boundaries: a window with 1023 samples must not complete or fire;
  the 1024th sample completes the window; a window ending one match short of
  `C_APT` must not fire and one at `C_APT` must (cf. the non-overlapping-window
  and cutoff tests in `sim/tests/test_health_test.py`).
- `raw_valid` gaps: cycles with `raw_valid` low advance no counters and do not
  break a run.
- Per-ring-only stall: one ring stuck for at least 81 consecutive samples with a
  healthy combined stream raises only that ring's flag.
- Incomplete or invalid capture: truncated, nonconverged and
  unresolved-level inputs yield `insufficient observation` or `invalid
  digitization`, never a bit-filled completion and never a pass.
- Start-up accounting: 1024 clean samples pass start-up; an alarm resets the
  counter; `startup_req` discards the in-flight window.

## 9. Handoff: feasibility-limit conclusion and conditional follow-up draft

### Feasibility-limit conclusion

Within the 2026-10-10 sources, an out-of-envelope characterization campaign
cannot be executed meaningfully, for two independent reasons:

1. **Missing model capability.** No supported voltage or temperature range
   outside the envelope was established for `nfet_03v3`/`pfet_03v3` in
   `sm141064.ngspice` (Revision 9) of `gf180mcuD`
   (`open_pdks c6d73a35f524070e85faff4a6a9eef49553ebc2b`). All four faces are
   excluded. Needed: an authoritative foundry or PDK document stating the
   characterization range, recommended operation and absolute maximum with
   terminal-bias constraints for those two devices, or an explicit operator
   decision to proceed with unvalidated extrapolation and label results
   accordingly.
2. **Missing runtime capability.** At the required 3.0741504 ms of simulated
   time the shipped-array transient-noise deck extrapolates to about 3,400
   CPU-hours per run against a 24 CPU-hour cap (section 6). Needed: a
   substantially cheaper observation path that still uses the shipped
   digitizers, with its own validation and claim limits, or a larger approved
   budget.

The ratified envelope clause stays unverified. Any proposed amendment to the
row needs a separate decision record; this plan does not propose one.

### Conditional follow-up issue draft (do not file or approve automatically)

Title: Out-of-envelope health-test replay: obtain model bounds and a cheaper
observation path

Body outline:

- Prerequisite 1: record, with source and revision, the characterization
  range, recommended operation and absolute maximum, plus terminal-bias
  constraints, for `nfet_03v3` and `pfet_03v3` per envelope face; mark any
  face still unsupported as excluded.
- Prerequisite 2: demonstrate, on the candidate deck, a measured cost per
  simulated microsecond with an observation scheme that records the shipped
  digitized outputs once per clock edge, and show that 3072 samples
  (3.0741504 ms at 1.0007 us) fit a stated CPU budget without shortening
  windows or raising the clock.
- Scope when both hold: at most 8 points x 4 seeds (`1, 2, 3, 4`), the deck
  adaptation of section 4, result fields of section 7, replay tests of
  section 8.
- Out of scope: tuning cutoffs, hardware, editing the README row, entropy
  claims, post-layout netlists (see #339, #418).
- Acceptance: results reported only as sampled-point observations; no
  first-failure distance or monotonic-coverage claim.
