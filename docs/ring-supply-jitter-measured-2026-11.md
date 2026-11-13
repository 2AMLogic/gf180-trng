# Ring supply: measured starved-ring jitter at 3.30 V and 2.97 V

Evidence-only note for issue #831 (follow-up to #813, authorised by the settled
decision on #816, part of #700). It changes no spec row, bound, decision record,
design, testbench or Operating envelope row, and it does **not** answer the
ring-supply-domain question.

## Why

`docs/ring-supply-entropy-power-2026-11-09.md` (#813) models the entropy margin
*rising* as the ring supply falls. That result holds only because the model keeps
the jitter-energy constant `a = kappa^2 * P_ring / (k_B * T)` at the stated
10.932 across supply. No committed record measured ring jitter below 3.63 V at the
corners that matter. This note replaces that assumption with records.

## What was measured

The committed starved-ring jitter bench (`sim/tb/ro-ring5-starved-jitter-long-batch/`,
driven by `sim/tools/starved_hot_corner.py`) at five new PVT points x 8 units
(40 units), on the batch fleet through `klt sim` with `batch.capacity_wait_s: 600`.
Nothing was swept locally. Plus the cell's `.noise` density at four of the five
points (single-unit, local); `ss`/125/2.97 uses the existing
`2026-08-01-rostage-noise-04`.

| Point | Jitter record | Noise record |
|---|---|---|
| `ss`/125/3.30 | `2026-11-13-ro-ring5-starved-jitter-redsup-01` | `2026-11-13-rostage-noise-01` |
| `ss`/125/2.97 | `2026-11-13-ro-ring5-starved-jitter-redsup-02` | `2026-08-01-rostage-noise-04` |
| `ff`/-40/3.30 | `2026-11-13-ro-ring5-starved-jitter-redsup-03` | `2026-11-13-rostage-noise-02` |
| `ff`/-40/2.97 | `2026-11-13-ro-ring5-starved-jitter-redsup-04` | `2026-11-13-rostage-noise-03` |
| `tt`/27/2.97 | `2026-11-13-ro-ring5-starved-jitter-redsup-05` | `2026-11-13-rostage-noise-04` |

Each jitter record names its fleet job ids. Records 01-02 came from one two-supply
request, as did 03-04, so those pairs list the same jobs; `raw/report.json` in each
holds only that record's eight units.

Run length (`tstop`) was sized from a 120 ns period probe so the 770 rising edges
the window needs are reached with margin (4.2 us, 1.7 us, 2.8 us for the three
requests; the 3.63 V baseline used 3.1 us). A unit that ends short is refused by
`ingest`, not averaged; none was.

The records live in their own family, `ro-ring5-starved-jitter-redsup`, which the
corner-mean reader's glob does not match. The published four-corner constants are
unchanged (asymptotic 10.932, lag-1 23.255; sizing constant 7.322 at `ss`/-40/3.63),
held by `sim/tests/test_reduced_supply_jitter.py`.

## Result: `a` per point

Reproduce with `python3 sim/tools/starved_cell_jitter_energy.py --check --reduced-supply`.
`a_asym` is the asymptotic constant (the one DR-0007 section 2 extrapolates with);
`a_lag1` is the lag-1 figure. The comparator is the same-corner committed record.

| Point | `a_asym` | `a_lag1` | `a_asym` / 10.932 | Comparator (`a_asym`) | Ratio to comparator | Lag-1 seed spread | Window drift |
|---|---|---|---|---|---|---|---|
| `ss`/125/3.30 | 5.518 | 16.706 | 0.505 | `ss`/125/3.63 (8.421) | 0.655 | 4.95 % | 20 ppm |
| `ss`/125/2.97 | 6.972 | 15.467 | 0.638 | `ss`/125/3.63 (8.421) | 0.828 | 4.15 % | 13 ppm |
| `ff`/-40/3.30 | 15.872 | 19.742 | 1.452 | `ff`/-40/3.63 (17.109) | 0.928 | 3.08 % | 34 ppm |
| `ff`/-40/2.97 | 11.346 | 17.687 | 1.038 | `ff`/-40/3.63 (17.109) | 0.663 | 2.10 % | 20 ppm |
| `tt`/27/2.97 | 7.768 | 16.472 | 0.711 | `tt`/27/3.30 (10.874) | 0.714 | 3.55 % | 40 ppm |

`--check` passes on every new record: each lag-1 seed spread is within the 3x
tolerance of the 2.69 % a genuine 512-period estimate shows (2.10-4.95 %, ratios
0.78-1.84), and the pre-window drift is 7-41 ppm. Accumulation exponents are
0.39-0.49 (all-lag) and 0.40-0.50 (tail), as for the 3.63 V records. No check
failed, so nothing was relaxed.

## Effect on the modelled margin

`python3 sim/tools/worst_corner_entropy.py --supply-sweep --measured-a` (the
`--measured-a` report is new and read-only; default output is unchanged) rescales the
modelled `Q_array` with the measured `a` of the same corner and supply, at `ss`/125
and `ff`/-40 only. Rate 2000 bps, margin = `Q_array / (M * Q_H0)`.

| Point | `a` fixed | `a` measured | Margin, fixed `a` | Margin, measured `a` |
|---|---|---|---|---|
| `ss`/125/3.63 | 10.932 | 8.421 | 2.07x | 1.60x |
| `ss`/125/3.30 | 10.932 | 5.518 | 2.31x | 1.16x |
| `ss`/125/2.97 | 10.932 | 6.972 | 2.57x | 1.64x |
| `ff`/-40/3.63 | 10.932 | 17.109 | 2.84x | 4.44x |
| `ff`/-40/3.30 | 10.932 | 15.872 | 3.28x | 4.76x |
| `ff`/-40/2.97 | 10.932 | 11.346 | 3.80x | 3.94x |

These are **simulation-derived design estimates, not an SP 800-90B assessment**
(DR-0004), and not a measured min-entropy `H`.

## Gap statement

- The measured `a` **contradicts** "the margin does not fall at reduced supply" at
  `ss`/125: moving from 3.63 V to 3.30 V the measured-`a` margin falls from 1.60x to
  1.16x (the fixed-`a` model said it rises, 2.07x to 2.31x). The measured `a` at
  3.30 V is 0.66 of the 3.63 V value, which outweighs the power returned.
- At `ss`/125/2.97 V the margin recovers to 1.64x, about the 3.63 V value, so the
  dependence on supply is not monotonic at this corner and two points do not
  establish a trend.
- At `ff`/-40 the measured margin rises from 4.44x (3.63 V) to 4.76x (3.30 V) and
  then falls to 3.94x at 2.97 V, 11 % below the 3.63 V value; it stays above the
  fixed-`a` figure at 3.63 V and 3.30 V and is about equal to it at 2.97 V (3.80x).
- The measured margin at every point stays above 1x, but the 1.16x at `ss`/125/3.30 V
  is the smallest and sits on the corner that binds the entropy question (DR-0015).
- `fs`/`sf` are out of scope (DR-0006). Eight seeds per point: per the #628 ruling,
  no margin or rate ceiling is raised from these records. The stated constant and
  every published figure are untouched.

The ring-supply-domain question is not answered here. It can be re-asked with this
evidence in hand.
