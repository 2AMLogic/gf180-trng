# Digital power switch: sizing, leakage and wake

Status: complete for issue [#707] (child of [#700]). This document sizes a PMOS header for the digital
section's supply and reports what it costs and what it saves at the `< 1 uA` idle row's binding corner. It
is an ordinary summary, not evidence: every number below comes from the 45 records
`sim/records/2026-10-28-power-switch-01..45.md`, through `python3 sim/tools/power_switch.py summarize`
(the tables are that command's output). It changes no spec row, no decision record and no signoff item.

## 1. Result

- **Switch.** One `pfet_03v3`, 40 fingers x 10 um = **400 um** at L = 0.28 um, between the always-on supply
  and the gated rail (`design/xschem/power_switch.sch`, netlist `design/power_switch.spice`). Layout
  `layout/cells/power_switch/`: DRC clean, LVS match, bounding box 41.5 x 14.2 um = 589 um^2 (0.0006 mm^2,
  1.2 % of the `< 0.05 mm^2` Area row's bound).
- **Droop.** At the 20 MHz implementation clock's largest digital current (1.893 mA, informational) the
  400 um switch drops at most **30.95 mV** (ss / +125 C / 2.97 V), inside the 33 mV yardstick used by
  `characterization-digital-supply-ir-drop.md`; 200 um does not (62.55 mV). At the ratified-rate bound (96.7 uA)
  every width in the sweep drops under 6.3 mV, so the 400 um choice is set by the informational 20 MHz bound,
  not by the ratified rate; 100 um would pass the ratified-rate load.
- **Off leakage.** The switch alone, with the full supply across it, leaks at most **41.91 nA** at ff / +10 % /
  +125 C (400 um): 4.2 % of the row.
- **Gated-domain idle, measured as modelled in section 3: 74.4 nA** at the binding corner (gated digital 41.7 nA
  + analog 32.8 nA), against 2212.5 nA with the digital section ungated. That is 7.4 % of the `< 1 uA` row. The
  verdict depends on the caveats in section 5, above all that this is the figure with the domain *off*: it is
  not the ratified idle, which keeps register state, and nothing here retains any (issue #708).
- **Wake.** Peak inrush through the 400 um switch is **104 mA** for a 200 pF rail and a 10 ns sleep edge,
  **8.6 mA** for a 1 us edge; the rail is at 95 % of vdd within 21 ns and 463 ns respectively (worst corners).
  These are inputs to #708's wake sequence.

## 2. Why a header, and what was chosen

See `sim/tb/power-switch/README.md`: the digital section has its own `vddd` pin while `vss` is the one shared
return, so a footer would sit in the analog taps' return path. The width was swept at 100, 200, 400 and 800 um
and 400 um is the smallest that meets the 33 mV yardstick at the 20 MHz bound at every corner. The leakage
cost of going from 100 to 400 um is 31 nA at the binding corner, and the area cost is below 0.001 mm^2.

## 3. What was measured and how

`sim/tb/power-switch/tb_power_switch.sp`, one transient per PVT point, 45 points = the five MOS corners
(tt, ff, ss, fs, sf) x -40 / 27 / 125 C x 2.97 / 3.30 / 3.63 V, on the batch fleet through `klt sim`
(fleet jobs in each record). Four instance groups:

- **Droop and on-resistance:** the four widths, each with a 96.7 uA and a 1.893 mA DC load (the largest
  currents in `characterization-digital-supply-ir-drop.md` at the ratified 1 MHz rate and at the 20 MHz
  implementation clock, ff / +125 C).
- **Off leakage:** the same four widths off with the virtual rail forced to 0 V, the worst case.
- **Gated idle:** the 400 um switch off with a leakage-equivalent load on its rail. The load is an off NFET
  of 710 um (71 x 10 um) at L = 0.28 um, sized so that on its own it draws 2.18 uA at ff / +125 C / 3.63 V,
  the digital leakage DR-0017 and DR-0023 report (the record shows 2179.7 nA there). It is a model of that
  leakage and not the cells: it follows the PDK's own corner, temperature and drain-bias dependence, not the
  Liberty library's. The switch off lets the rail float to 14.5 mV, at which the load leaks about as much as
  the switch does; that collapse of the load's drain bias is what removes 98 % of the digital leakage.
- **Wake:** a 400 um switch with 50 pF or 200 pF on the rail (an assumption: about 1655 cells at 30 fF, and
  a bracket for added well and decoupling capacitance; no extracted supply capacitance exists in this repo),
  the leakage-equivalent load, and a sleep fall of 10 ns or 1 us starting at 100 ns.

Source: 45 records `sim/records/*-power-switch-NN.md` (current, status valid).

**Sizing sweep** (worst case over all corners; loads a = 96.7 uA, b = 1.893 mA)

| width | droop a (mV) | droop b (mV, corner) | on-resistance b (ohm) | I^2R loss b (uW) | off leakage, full supply (nA, corner) |
|---|---|---|---|---|---|
| 100 um | 6.274 | 127.82 (ss/125C/2.97V) | 67.52 | 242.0 | 10.48 (ff/125C/3.63V) |
| 200 um | 3.134 | 62.55 (ss/125C/2.97V) | 33.04 | 118.4 | 20.95 (ff/125C/3.63V) |
| 400 um | 1.566 | 30.95 (ss/125C/2.97V) | 16.35 | 58.6 | 41.91 (ff/125C/3.63V) |
| 800 um | 0.783 | 15.40 (ss/125C/2.97V) | 8.13 | 29.1 | 83.82 (ff/125C/3.63V) |

**Binding idle corner ff / +10 % / +125 C** (`2026-10-28-power-switch-18`)

| quantity | value |
|---|---|
| switch off leakage, 100 um, full supply across it | 10.48 nA |
| switch off leakage, 200 um, full supply across it | 20.95 nA |
| switch off leakage, 400 um, full supply across it | 41.91 nA |
| switch off leakage, 800 um, full supply across it | 83.82 nA |
| digital leakage-equivalent load alone (ungated reference) | 2179.7 nA |
| 400 um switch off, load behind it (gated domain) | 41.67 nA |
| virtual rail level when off | 14.5 mV |
| analog block idle (`2026-08-02-sampler-core-idle-leakage-18`, `i_idle_clklo_a`) | 32.77 nA |
| **idle, gated digital + analog** | **74.44 nA** |
| idle, ungated digital + analog | 2212.5 nA |
| `< 1 uA` row, share used by the gated figure | 7.4 % |

Largest gated-domain leakage over all 45 corners: 41.67 nA (ff/125C/3.63V).

**Wake** (400 um switch; worst case over all corners)

| rail capacitance | sleep fall | peak inrush (mA, corner) | settle to 95 % (ns, corner) |
|---|---|---|---|
| 50 pF | 10 ns | 54.76 (ff/27C/3.63V) | 10.5 (ss/125C/2.97V) |
| 200 pF | 10 ns | 104.03 (ff/27C/3.63V) | 21.4 (ss/125C/2.97V) |
| 50 pF | 1000 ns | 3.44 (ff/27C/3.63V) | 400.5 (ss/-40C/2.97V) |
| 200 pF | 1000 ns | 8.60 (ff/27C/3.63V) | 462.6 (ss/-40C/2.97V) |

## 4. Layout and verification

`layout/cells/power_switch/build.py` draws one shared-diffusion strip (41 pads, 40 gates), Metal1 stripes
alternating `vdd` / `vvdd` into two buses and a poly bus for `sleep`. `layout/verify.py` runs `klt drc` (clean,
no rule counts) and `klt lvs` against a hand-written 40-device reference (match, 0 errors) under the pinned
`klayout-tools==0.6.0` / `klayout==0.30.10` of DR-0026; `layout/reports/power_switch.*` are the committed
reports. Not drawn, and so not verified: an n-well tap and implants (the curated deck's usual disclosure,
`device.body_unverified`), a guard ring, and any metal sized for electromigration.

## 5. What this does not establish

- **The idle figure is the domain-off figure.** The `< 1 uA` row defines idle as register state retained.
  Powering the domain off loses `CTRL`, `STATUS`, the FIFO contents, the health-test window position and the
  conditioner's in-flight block (DR-0017 option A), and the outputs crossing into the always-on domain float
  to an undefined level. Retention, isolation and the wake sequence are issue #708. This issue did not
  edit the README spec table or any decision record, and the figure above is reported as measured, not as a
  row verdict.
- **The digital load is a model**, a leakage-equivalent NFET plus DC currents; the cells' real leakage
  versus the supply is not simulated, and the 98 % reduction rests on the drain-bias dependence of that
  model. The wake capacitances are assumptions, so the inrush and settling figures bound a range, not a
  prediction.
- **Clock-edge current peaks are not modelled.** Droop is the DC drop at the average currents of the
  characterization above; a short peak above the average adds to it.
- **Pre-layout.** No extracted wiring, no well and tap resistance, no bond-wire inductance on the inrush.
- **Nothing is integrated.** The switch is not placed in `trng_top` or the floorplan, and no full-chip
  power or area signoff was re-run.
- **A failed first attempt** is recorded as `sim/records/2026-10-28-power-switch-attempt-01.md`: all 45 units
  hit their timeout on the fleet because its ngspice-46 workers did not finish this deck in 120 s, where a local
  ngspice-42 takes 1.5 s, until the request pinned `set num_threads=1` (a 1 us run went from 6.2 s to 0.37 s
  with it; the cause is probably thread oversubscription but was not isolated; reported on klayout-tools #3619).

[#707]: https://github.com/2AMLogic/gf180-trng/issues/707
[#700]: https://github.com/2AMLogic/gf180-trng/issues/700
