# Shipped liveness samplers in the whole-block active-power ledger

Issue [#463](https://github.com/2AMLogic/gf180-trng/issues/463). Status:
**the ledger now accounts for the two shipped per-ring liveness samplers
(`xsr1`, `xsr2`) and the measurement is defined, committed and unit-tested, but
only one of its 27 PVT points was simulated** (`tt` / 27 °C / 3.30 V, a local
single-point probe). The other 26 points are explicit gaps because the batch
submit failed. See "Run status". Until they are filled, every active total the
ledger prints at an unmeasured corner **excludes** the liveness samplers and is
a lower bound.

**This document is an ordinary summary, not evidence.** The evidence is
`sim/records/2026-10-10-sampler-core-liveness-active-01.md` and the attempt
record `…-attempt-01.md`. It changes no specification row, no decision record
and no signoff verdict. In particular it does **not** ratify
[`DR-0016`](../spec/decision-records/DR-0016-per-ring-liveness-monitor.md), which
stays `Proposed`: the samplers are already in `design/sampler_core.spice`
(integration amendment, #65), and measuring circuitry that is already built does
not decide whether to keep it.

## The scope mismatch

`sim/tools/power_rollup.py` summed the array, the raw-bit/valid sampler pair
(`xsb`, `xsv`) and the digital section, and described the liveness digitizer as
uninstantiated and optional. `design/sampler_core.spice` instantiates four
`sampler_dff` cells: `xsb`, `xsv`, `xsr1`, `xsr2`. The last two digitize the
buffered ring outputs `ro1`/`ro2`. They were in no active-power term.

## Inventory

`power_rollup.py` now reads the instances out of the generated netlist and maps
each to exactly one required ledger term; `--check` fails on an unmapped
instance (a missing term) or an instance claimed twice.

| Instance | Cell | Ledger term | Evidence family |
|---|---|---|---|
| `xdut` | `ro_array_core` (two rings, two ring buffers, XOR) | `array` | `ro-array-core-pvt-q`, `ro-array-core-power` |
| `xsb`, `xsv` | `sampler_dff` | `sampler_raw` | `sampler-dff-active-current` × the corner's `xo` rate |
| `xsr1`, `xsr2` | `sampler_dff` | `liveness` | `sampler-core-liveness-active` (new) |
| digital section | `trng_top` logic | `P_digital` (outside `sampler_core`) | `digital-sta-power` |

The `liveness` term has two parts that are kept apart so nothing is counted
twice:

- **the flops themselves**, `V · (I_data + 2 · f_clk · q_clk)`: `I_data` is the
  ring-data charge per second from the new record; `q_clk` is the clock-cycle
  charge from `sampler-dff-active-current`, the same source and form
  `power_rollup.py` already uses for `xsb`/`xsv`;
- **the taps' loading of the array**, a signed delta. The array records the
  ledger reads were taken without the taps, so the extra load on `ro1`/`ro2`
  and the ring buffers is not in them. The new deck runs a control array
  (`xsb`/`xsv` only) beside the tapped one in the same simulation, so the delta
  is a like-for-like difference, not a comparison across records.

**Idle is reviewed separately, and no second idle term is added.**
`sampler-core-idle-leakage` instantiates the whole `sampler_core`, so `xsr1` and
`xsr2` leakage is already inside the 32.77 nA analog idle figure. A regression
test pins that scope.

## Method

`sim/tb/sampler-core-liveness-active/` puts `xsb`, `xsv`, `xsr1`, `xsr2`, each
ring, and the buffer/XOR tree on separate 0 V sense-source branches with ideal
charge integrators, next to the control array. Charge is read at the 2nd and
6th rising ring crossings (four ring periods), as `ro-array-core-pvt-q` does.
The clock charge is removed inside the run: `xsv`'s D is tied high, so its
window charge is a pure clock-cycle load over the same window and phases `xsr`
sees; `Q(xsr) − Q(xsv)` is the ring-data charge. The arithmetic lives in
`sim/tools/liveness_sampler_power.py`, not in `.meas` expressions.

Declared rates: the ledger evaluates the clock term at the ratified 1 MHz sample
clock and at 0.5 MHz. The deck itself uses a local 10 ns clock so a few whole
cycles fit in the window; the recorded quantities are per-event charges, and the
data term is set by the ring rates, which the clock does not move. The grid is
the 27-point PVT grid of `ro-array-core-pvt-q` (`tt`/`ff`/`ss` × −40/27/125 °C ×
2.97/3.30/3.63 V).

## What was measured

One point, `tt` / 27 °C / 3.30 V, pre-layout, local `ngspice` 42:

| Quantity | Value |
|---|---|
| ring frequencies, tapped (control) | 150.3 (149.8) MHz and 160.8 (160.2) MHz |
| data charge per ring transition | 9.71 fC (ring 1), 9.00 fC (ring 2) |
| `xsr1`/`xsr2` ring-data power | 19.19 µW |
| clock term at 1 MHz (`2 · f_clk · q_clk`, from `sampler-dff-active-current`) | 0.05 µW |
| loading change of the array (tapped − control) | +6.08 µW |
| liveness term total | **25.32 µW** |

Like-for-like effect on that corner's whole-block active total
(`power_rollup.py`): 540.8 µW without the samplers, **566.1 µW with them**
(113.2 % of the 500 µW row; the sum without them was already 108.2 %). The
samplers add 5.1 % of the row's budget at this corner. The ledger's binding
corner is `ff` / −40 °C / 3.63 V; that point is not measured, so its 758.2 µW
total remains a lower bound.

The loading delta is not small next to the flops themselves: roughly a quarter
of the liveness cost at this corner is the array's own supply power rising with the taps
attached (ring frequency within 0.4 % of the control, supply power +6 µW), which a flops-only
measurement would have missed.

**Why the historical 81.3 µW is not used.** `ring-liveness-tap-power` measured a
tap on the *unbuffered* array, at `ff` / −40 °C / 3.63 V, with a 10 ns clock
averaged over a 48 ns window. That is a different topology (no ring buffer
between the ring and the sampler), a different corner and a different rate, so it
is neither a drop-in correction nor comparable to the 25.32 µW above. The constant
is retained in `power_rollup.py` only as a named, never-added `HISTORICAL_…`
context value. `--with-taps` now adds only the unshipped metastability hybrid;
adding the historical liveness constant on top of the shipped term would have
counted the samplers twice, and a test pins that.

## Run status

| # | Date | What | Outcome |
|---|---|---|---|
| 1 | 2026-10-10 | Whole 27-unit grid, `--backend batch` (fleet job `klt-sim-36eae9fed238`) | Rejected by the runner before any simulation: runner `klt 0.5.0`, client `0.7.0` (`batch_runner_version_mismatch`); no measurement. Recorded in `2026-10-10-sampler-core-liveness-active-attempt-01`. The same skew blocked the `sampler-array-fs-sf` campaign; no compatible client/runner pair exists, and it is already tracked upstream, so no new tool issue was filed. |
| 2 | 2026-10-10 | Single-point probe `tt/27/3.30`, `--backend local` | Measured: `2026-10-10-sampler-core-liveness-active-01`. |

The grid was **not** run as a local loop. Remaining gaps, to be filled by one
`liveness_sampler_power.py run --backend batch` submit when a compatible fleet is
available, then `record`:

- 26 of 27 PVT points, including the ledger's binding `ff` / −40 °C / 3.63 V;
- the rate dependence is applied analytically (data term independent of
  `f_clk`), not re-simulated at 1 MHz;
- post-layout: the analog block is not laid out.

## Adoption

Nothing here is a verdict change, and no decision is needed yet: the active row
is already missed by the whole block (see
[`characterization-startup-and-power-budget.md`](characterization-startup-and-power-budget.md)
and DR-0023), and the liveness term moves that miss further, not across the line.
`sim/characterization-analog-summary.md` is pinned by a signoff evidence envelope
(its content hash is cited by `signoff/evidence/characterization-analog.generic.json`),
so it is deliberately not edited here; its whole-block figures at the binding
corner are the same lower bound this document describes, and it is refreshed
together with its envelope when the grid is complete.

Once the full grid is measured, the corrected default total at the binding corner
is presented from `power_rollup.py` for whatever decision follows; the ledger is
not silently re-baselined by this change. Historical records are unchanged.

## Reproduce

```sh
python3 sim/tools/liveness_sampler_power.py plan
python3 sim/tools/liveness_sampler_power.py emit --check
python3 sim/tools/liveness_sampler_power.py run --outdir DIR --backend batch        # the grid
python3 sim/tools/liveness_sampler_power.py run --outdir DIR --backend local --only tt/27/3.30   # one probe point
python3 sim/tools/liveness_sampler_power.py analyze DIR/*.report.json
python3 sim/tools/liveness_sampler_power.py record DIR/*.report.json
python3 sim/tools/power_rollup.py            # ledger, inventory, per-corner gaps
python3 -m unittest sim.tests.test_liveness_sampler_power
```
