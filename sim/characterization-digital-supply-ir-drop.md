# DC voltage loss on the digital supply and return: docking path and power grid

Status: derivation complete for issue [#464]. This document quantifies how
much DC voltage the placed digital section loses between the chip pins and
its standard-cell rails, on both `vddd` and `vss`. It covers the external
docking path the composed floorplan draws into `digital` ([#224]) and the
parallel paths of the section's own power grid. It changes no spec row, no
decision record and no signoff item.

**Verdict at the ratified rate: not material.** At DR-0003's 1 MHz rate the
cross-corner upper bound on local supply collapse (the `vddd` drop plus the
`vss` rise that the cells see together) is **23.8 mV**. The worst per-corner
estimate is **11.8 mV** (`ff_125C_3v60/rc-max`). Both are below the 33 mV
yardstick the analog return analysis already uses. Idle (leakage only) is
about 0.5 mV. The digital load adds at most **0.14 mV** to the offset the
analog taps see on the shared `vss` trunk.

**Not covered at the 20 MHz implementation clock.** The place-and-route
clock constraint is not an operating rate this design ratifies. At 20 MHz
the same records give about 1.9 mA, a 226 mV estimate and a 462 mV bound.
That result is kept below and labelled as failed. Any proposal to run the
digital section near its implementation clock would have to revisit the
docking path first.

The numbers come from the generated block below. `--check` fails if that
block no longer matches its inputs. If the block changes, re-read this prose
against it.

## 1. Why the digital section needs its own model

`sim/tools/vss_trunk_ir_drop.py` ([#234],
[`characterization-vss-trunk-ir-drop.md`](characterization-vss-trunk-ir-drop.md))
prices the shared `vss` return as a series chain: one trunk segment and one
riser per analog tap. It deliberately excludes `digital` because that
region's power grid is a mesh, and a chain would misstate it. This document
does not change that analysis or its coverage. It adds the model that the
analog tool declined to approximate: a nodal resistor-network solve
(`sim/tools/_resistor_network.py`) over the real mesh, joined to the real
docking path.

## 2. What the network contains

Each net is one network, built at run time from committed geometry. Nothing
in it is transcribed by hand.

- **External feed.** This is every Metal3/Metal4/Metal5 rectangle and every
  Via3/Via4 cut that `layout.floorplan.interregion.wiring_plan()` draws for
  the net. `vss_trunk_ir_drop.py` already evaluates the same function over
  the committed `reports/compose.json` and `area.json`. The path runs from
  the chip pin along the Metal4 trunk to the `digital` riser. From there it
  goes through one Via3, the Metal3 riser in the isolation channel, one Via3
  and one Via4 at the riser top, and the Metal5 dock onto the net's lowest
  strap.
- **Internal grid.** This is every `SPECIALNETS` wire and via of the net in
  `layout/digital/trng_top.def`. Per net that is 4 Metal5 straps, 8 Metal4
  straps and 38 Metal1 follow-pin rails. The vias are a 16-cut Via4 array at
  each of the 32 strap crossings, plus a 16-cut Via1/Via2/Via3 stack at each
  of the 304 rail-to-strap crossings. Each array is priced per cut from the
  DEF's own `VIAS ... ROWCOL`.
- **Joins** are geometric. A via joins the conductors of its two layers that
  contain its centre. Two same-layer conductors join where they overlap,
  which is how the Metal5 dock meets its strap. The network must be a single
  connected piece. A missing via, a missing dock or a rail without vias is
  rejected (section 6).

The block below lists the external feed element by element. On both nets it
is dominated by the Metal3 riser and by **three single-cut vias**. Together
these are about 13.5 ohm nominal and 45 ohm in the high-resistance variant,
against a grid whose internal share is about 1-2 ohm under uniform
allocation.

## 3. Resistance sources and assumptions

- **Sheet and via resistance** come from the gf180mcu magic technology
  file's extraction tables (`libs.tech/magic/gf180mcuD.tech`, at the PDK
  revision every digital record here pins; its sha256 is in the provenance
  block). Two variants are used. The nominal one is `variants ()`: 0.090
  ohm/sq for Metal1-4, 0.060 ohm/sq for Metal5 and 4.5 ohm per via cut. Its
  metal values are identical to the `klt` gf180mcu deck's curated
  `PARASITICS`. The high-resistance one is `variants (hrhc),(hrlc)`: 0.104
  and 0.070 ohm/sq, and 15 ohm per cut. The low-resistance variant prices
  vias at 0 ohm. It is not used: a zero-ohm via cannot be priced, and it is
  not the conservative direction in any case.
- **Temperature.** The tech file carries no temperature coefficient. The
  analysis therefore applies an *assumed* 0.004/K above 25 C (a typical
  aluminium-interconnect figure, not a PDK value). This gives a 1.40x factor
  at +125 C. No credit is taken below 25 C.
- The `klt` deck carries no via resistance or resistance corners. That gap
  is filed generically upstream as klayout-tools#3053, so these values are
  restated here with their source rather than read from the tool.

## 4. Current sources and allocations

- **Digital load.** The current-DEF `digital-sta-power` family supplies the
  digital load: 15 corners at gate level (DR-0021), selected through
  `digital_corner_characterization.load()`, which refuses records of any
  other DEF revision. *Active* is the record's 1 MHz total power at uniform
  0.25 activity, divided by that corner's deck voltage. *Idle* is the
  record's leakage current. *Stress* is the record's 20 MHz total. The
  measured workloads of [#453]
  ([`characterization-digital-activity-power.md`](characterization-digital-activity-power.md))
  stay at or below 0.72x the uniform baseline at every corner, so the
  uniform figure is the conservative one.
- **Where the current is drawn** inside the grid is not known at cell
  resolution, so two allocations are reported, and neither is a per-cell
  measurement:
  - *Uniform.* Every standard-cell row draws the same current, spread
    evenly along the row, from the rail on each of its edges. The
    distributed load along each rail segment is solved exactly, with no
    lumping error.
  - *Allocation-free bound.* The whole current is drawn at the one point on
    the rails with the highest effective resistance to the pin. In a
    resistor network no node's offset can exceed the total current times
    that resistance, so this bound holds for any allocation with the same
    total.
- **Analog load on the shared `vss` trunk.** This is
  `vss_trunk_ir_drop.py`'s own current profile, injected at the three analog
  taps. The profile and its corners are in the provenance block. The
  profile's own allocation assumptions are disclosed in that tool and are
  not repeated here.
- **Cross-corner bound.** The bound combines the high-resistance variant,
  the largest derating factor and the family's largest current. It is
  labelled as a bound because no single PVT corner produces it.

## 5. Results

<!-- digital-supply-ir-drop:begin (generated by sim/tools/digital_supply_ir_drop.py; do not edit) -->

### Provenance (pinned inputs; any change stales this block)

```json
{
 "connectivity": {
  "erc_status": "clean",
  "klt_version": "0.6.0",
  "nets_checked": [
   "vddd",
   "vss"
  ],
  "report": "layout/floorplan/reports/erc-supply.json"
 },
 "current": {
  "activity": "uniform 0.25 transitions/net/cycle, duty 0.5",
  "analog_profile": {
   "active_corner": {
    "process": "ff",
    "temperature_c": -40,
    "voltage_v": 3.63
   },
   "active_uw": {
    "liveness_taps_uw": 81.0,
    "ring_pair_uw": 489.9,
    "sampler_flops_uw": 16.88
   },
   "idle_corner": {
    "process": "ff",
    "temperature_c": 125,
    "voltage_v": 3.63
   },
   "idle_total_na": 136.8,
   "source": "sim/tools/vss_trunk_ir_drop.py"
  },
  "family": "digital-sta-power (gate level, DR-0021), current DEF only",
  "rates": {
   "active": "1 MHz",
   "idle": "leakage",
   "stress": "20 MHz"
  },
  "records": [
   {
    "corner": "ff_125C_3v60/rc-max",
    "record": "2026-10-29-digital-sta-power-12",
    "sha256": "3fc33dcaafbf44e9b9cfcc2f61f9ff41180709206e3c719c970d67153be233d0"
   },
   {
    "corner": "ff_125C_3v60/rc-min",
    "record": "2026-10-29-digital-sta-power-10",
    "sha256": "ec63f763a4186209ab5fa7a80d435044930a6b8500f937f13bf9418137f4bcdc"
   },
   {
    "corner": "ff_125C_3v60/rc-nom",
    "record": "2026-10-29-digital-sta-power-11",
    "sha256": "84c878425c3d4dcffc77ca593e5c06113ef7bb3d22a85bb430183f84a08cc462"
   },
   {
    "corner": "ff_n40C_3v60/rc-max",
    "record": "2026-10-29-digital-sta-power-15",
    "sha256": "d1bb966b7fa5c0bac08385f7337aa6a9a0a2ba76cde8dcd596ff9ad2aca3eba3"
   },
   {
    "corner": "ff_n40C_3v60/rc-min",
    "record": "2026-10-29-digital-sta-power-13",
    "sha256": "63f48193c747fff3897144b0067104a0f8fb8f72c9d9f7538f6b4a986dfbf5b3"
   },
   {
    "corner": "ff_n40C_3v60/rc-nom",
    "record": "2026-10-29-digital-sta-power-14",
    "sha256": "6bcc9719dc1dea6c039367e7f6e541edc54969685ff224cee0ae472b56ea4b22"
   },
   {
    "corner": "ss_125C_3v00/rc-max",
    "record": "2026-10-29-digital-sta-power-03",
    "sha256": "e25455ab8926489a9916bad311cc2f230c35648eb17337915e063633fbd30240"
   },
   {
    "corner": "ss_125C_3v00/rc-min",
    "record": "2026-10-29-digital-sta-power-01",
    "sha256": "f9bb625256c5ac26e83cc6bf0705a099f36edb25db0c0a3377cdebccc6a19c5b"
   },
   {
    "corner": "ss_125C_3v00/rc-nom",
    "record": "2026-10-29-digital-sta-power-02",
    "sha256": "f4008a286d12558d84b6594c1ab17e30d5450bd5237258e2f59df8a1416d730b"
   },
   {
    "corner": "ss_n40C_3v00/rc-max",
    "record": "2026-10-29-digital-sta-power-06",
    "sha256": "978dec9c30a5b12b0a96bc3bfc61cbbd645a206031bb268b7d4d5c2521c502aa"
   },
   {
    "corner": "ss_n40C_3v00/rc-min",
    "record": "2026-10-29-digital-sta-power-04",
    "sha256": "48b44ce0d81b0340b0e6df562f22eb91f4d89d9b6477ec59121d9e1c87fc30a2"
   },
   {
    "corner": "ss_n40C_3v00/rc-nom",
    "record": "2026-10-29-digital-sta-power-05",
    "sha256": "84b1a44f86a7583d605d2215cbccc718e9d8d572cf71977b082298c7776dff76"
   },
   {
    "corner": "tt_025C_3v30/rc-max",
    "record": "2026-10-29-digital-sta-power-09",
    "sha256": "c2cc64b1f98db797ab3dac815407edaba9a7a6810cbbfac9b6f7968140f34fd5"
   },
   {
    "corner": "tt_025C_3v30/rc-min",
    "record": "2026-10-29-digital-sta-power-07",
    "sha256": "193b43bede7a8a46ba810c10f042b6f83815acc69647b16bb36a2f6bc7f00dd6"
   },
   {
    "corner": "tt_025C_3v30/rc-nom",
    "record": "2026-10-29-digital-sta-power-08",
    "sha256": "41d9bc5e6c914e601135d6d84135da40755520de1575a26d68693ca7e1338491"
   }
  ]
 },
 "geometry": {
  "layout/digital/trng_top.def": {
   "git_blob_sha": "87b3dedca82354ea1c6b17e7e2867c806f9625f5"
  },
  "layout/floorplan/reports/area.json": {
   "sha256": "517a2b23f0e876fba93679d49690e6ccd57db9320fb48bfa645f78d3d7588dfc"
  },
  "layout/floorplan/reports/compose.json": {
   "sha256": "f306d901192ad4d9def9d8ed5ece0fb65252f79c22024c9e92ec1febbc4ee6c3"
  },
  "layout/floorplan/reports/interregion.json": {
   "sha256": "e2b98fa3494a1697d62cb7697fa2add363b00c9288ac54b3c6d63e0186ed81ea"
  },
  "layout/floorplan/trng_floorplan.gds": {
   "sha256": "a704c2dae86151203430b8fed70348b36cd8b24eef419758618ae85e3c1e79f0"
  },
  "wiring_plan(vddd, vss) shapes+routes": {
   "sha256": "4a545914c728fbe42b3ed1a63daf6bb6f6d23b3f9e16657f45057ef131b1df10"
  }
 },
 "resistance": {
  "assumed_tcr_per_k": 0.004,
  "source": {
   "file": "libs.tech/magic/gf180mcuD.tech",
   "pdk": "gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b",
   "sha256": "9340f8c2f97407281edc089363eda2ad369cdf5d2db8df6afcbf862162e4eafa"
  },
  "tcr_reference_c": 25.0,
  "variants": {
   "high": {
    "sheet_ohm_sq": {
     "Metal1": 0.104,
     "Metal2": 0.104,
     "Metal3": 0.104,
     "Metal4": 0.104,
     "Metal5": 0.07
    },
    "tech_block": "variants (hrhc),(hrlc)",
    "via_ohm_per_cut": {
     "Via1": 15.0,
     "Via2": 15.0,
     "Via3": 15.0,
     "Via4": 15.0
    }
   },
   "nominal": {
    "sheet_ohm_sq": {
     "Metal1": 0.09,
     "Metal2": 0.09,
     "Metal3": 0.09,
     "Metal4": 0.09,
     "Metal5": 0.06
    },
    "tech_block": "variants ()",
    "via_ohm_per_cut": {
     "Via1": 4.5,
     "Via2": 4.5,
     "Via3": 4.5,
     "Via4": 4.5
    }
   }
  }
 }
}
```

### Network and unit response (per ampere of digital current, 25 C)

| net | resistance variant | external feed (ohm) | internal, uniform (ohm) | internal, allocation-free bound (ohm) | rails | Metal4 / Metal5 straps | DEF via arrays | nodes |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `vddd` | nominal | 47.950 | 1.386 | 7.556 | 37 | 8 / 4 | 920 | 1255 |
| `vddd` | high | 84.811 | 1.818 | 10.033 | 37 | 8 / 4 | 920 | 1255 |
| `vss` | nominal | 34.733 | 1.239 | 7.142 | 38 | 8 / 4 | 944 | 1293 |
| `vss` | high | 69.539 | 1.637 | 9.474 | 38 | 8 / 4 | 944 | 1293 |

External feed, element by element, chip pin first (nominal / high, ohm):

| net | element | nominal | high |
|---|---|---:|---:|
| `vddd` | metal4 wiring-plan rect, 3.00 um x 0.30 um | 0.900 | 1.040 |
| `vddd` | via3 single cut | 4.500 | 15.000 |
| `vddd` | metal3 wiring-plan rect, 110.98 um x 0.30 um | 33.294 | 38.473 |
| `vddd` | via3 single cut | 4.500 | 15.000 |
| `vddd` | via4 single cut | 4.500 | 15.000 |
| `vddd` | metal5 wiring-plan rect, 19.08 um x 4.48 um | 0.256 | 0.298 |
| `vss` | metal4 wiring-plan rect, 3.00 um x 0.30 um | 0.900 | 1.040 |
| `vss` | via3 single cut | 4.500 | 15.000 |
| `vss` | metal3 wiring-plan rect, 66.88 um x 0.30 um | 20.064 | 23.185 |
| `vss` | via3 single cut | 4.500 | 15.000 |
| `vss` | via4 single cut | 4.500 | 15.000 |
| `vss` | metal5 wiring-plan rect, 20.08 um x 4.48 um | 0.269 | 0.314 |

Worst points (composed frame, um): `vddd` uniform at [866.66, 379.0], bound at [530.66, 379.0]; `vss` uniform at [905.86, 373.96], bound at [905.86, 384.04].

Analog return's own offset at the `digital` dock on the shared `vss` trunk: nominal active 0.146 mV, nominal idle 0.000 mV, high active 0.168 mV, high idle 0.000 mV.

### Scenario: active, 1 MHz (DR-0003 ratified rate), uniform 0.25 activity

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 94.264 | 6.328 | 0.183 | 4.584 | 0.163 | 0.204 | 11.462 | 0.119 |
| ff_125C_3v60/rc-min | 91.792 | 6.162 | 0.178 | 4.463 | 0.159 | 0.204 | 11.167 | 0.116 |
| ff_125C_3v60/rc-nom | 92.898 | 6.236 | 0.180 | 4.517 | 0.161 | 0.204 | 11.299 | 0.117 |
| ff_n40C_3v60/rc-max | 86.229 | 4.135 | 0.120 | 2.995 | 0.107 | 0.146 | 7.502 | 0.078 |
| ff_n40C_3v60/rc-min | 83.904 | 4.023 | 0.116 | 2.914 | 0.104 | 0.146 | 7.303 | 0.076 |
| ff_n40C_3v60/rc-nom | 84.943 | 4.073 | 0.118 | 2.950 | 0.105 | 0.146 | 7.392 | 0.076 |
| ss_125C_3v00/rc-max | 71.359 | 4.790 | 0.139 | 3.470 | 0.124 | 0.204 | 8.726 | 0.090 |
| ss_125C_3v00/rc-min | 69.644 | 4.675 | 0.135 | 3.387 | 0.121 | 0.204 | 8.522 | 0.088 |
| ss_125C_3v00/rc-nom | 70.413 | 4.727 | 0.137 | 3.424 | 0.122 | 0.204 | 8.613 | 0.089 |
| ss_n40C_3v00/rc-max | 66.683 | 3.197 | 0.092 | 2.316 | 0.083 | 0.146 | 5.834 | 0.060 |
| ss_n40C_3v00/rc-min | 65.051 | 3.119 | 0.090 | 2.259 | 0.081 | 0.146 | 5.695 | 0.059 |
| ss_n40C_3v00/rc-nom | 65.783 | 3.154 | 0.091 | 2.285 | 0.081 | 0.146 | 5.757 | 0.059 |
| tt_025C_3v30/rc-max | 77.253 | 3.704 | 0.107 | 2.683 | 0.096 | 0.146 | 6.736 | 0.070 |
| tt_025C_3v30/rc-min | 75.280 | 3.610 | 0.104 | 2.615 | 0.093 | 0.146 | 6.568 | 0.068 |
| tt_025C_3v30/rc-nom | 76.164 | 3.652 | 0.106 | 2.645 | 0.094 | 0.146 | 6.643 | 0.069 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 94.264 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 11.192 + internal 1.324, vss external 9.177 + internal 1.250 + analog share 0.236 = **23.180 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 0.137 mV.

Worst per-corner estimate: 11.462 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.9468-3.6243 V. Against the 33.000 mV yardstick: **not material**.

### Scenario: idle, leakage only

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 2.116 | 0.142 | 0.004 | 0.103 | 0.004 | 0.000 | 0.253 | 0.003 |
| ff_125C_3v60/rc-min | 2.116 | 0.142 | 0.004 | 0.103 | 0.004 | 0.000 | 0.253 | 0.003 |
| ff_125C_3v60/rc-nom | 2.116 | 0.142 | 0.004 | 0.103 | 0.004 | 0.000 | 0.253 | 0.003 |
| ff_n40C_3v60/rc-max | 0.070 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |
| ff_n40C_3v60/rc-min | 0.070 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |
| ff_n40C_3v60/rc-nom | 0.070 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |
| ss_125C_3v00/rc-max | 0.713 | 0.048 | 0.001 | 0.035 | 0.001 | 0.000 | 0.085 | 0.001 |
| ss_125C_3v00/rc-min | 0.713 | 0.048 | 0.001 | 0.035 | 0.001 | 0.000 | 0.085 | 0.001 |
| ss_125C_3v00/rc-nom | 0.713 | 0.048 | 0.001 | 0.035 | 0.001 | 0.000 | 0.085 | 0.001 |
| ss_n40C_3v00/rc-max | 0.056 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.005 | 0.000 |
| ss_n40C_3v00/rc-min | 0.056 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.005 | 0.000 |
| ss_n40C_3v00/rc-nom | 0.056 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.005 | 0.000 |
| tt_025C_3v30/rc-max | 0.065 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |
| tt_025C_3v30/rc-min | 0.065 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |
| tt_025C_3v30/rc-nom | 0.065 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 2.116 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 0.251 + internal 0.030, vss external 0.206 + internal 0.028 + analog share 0.000 = **0.515 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 0.003 mV.

Worst per-corner estimate: 0.253 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.9695-3.6300 V. Against the 33.000 mV yardstick: **not material**.

### Scenario: stress, 20 MHz (place-and-route clock constraint; informational)

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 1845.079 | 123.859 | 3.581 | 89.719 | 3.200 | 0.204 | 220.563 | 2.325 |
| ff_125C_3v60/rc-min | 1795.637 | 120.540 | 3.485 | 87.315 | 3.114 | 0.204 | 214.658 | 2.263 |
| ff_125C_3v60/rc-nom | 1817.771 | 122.026 | 3.528 | 88.391 | 3.152 | 0.204 | 217.302 | 2.290 |
| ff_n40C_3v60/rc-max | 1723.254 | 82.629 | 2.389 | 59.854 | 2.135 | 0.146 | 147.152 | 1.551 |
| ff_n40C_3v60/rc-min | 1676.753 | 80.400 | 2.325 | 58.239 | 2.077 | 0.146 | 143.185 | 1.509 |
| ff_n40C_3v60/rc-nom | 1697.544 | 81.396 | 2.353 | 58.961 | 2.103 | 0.146 | 144.959 | 1.528 |
| ss_125C_3v00/rc-max | 1413.625 | 94.896 | 2.744 | 68.739 | 2.452 | 0.204 | 169.034 | 1.781 |
| ss_125C_3v00/rc-min | 1379.328 | 92.593 | 2.677 | 67.071 | 2.392 | 0.204 | 164.938 | 1.738 |
| ss_125C_3v00/rc-nom | 1394.703 | 93.626 | 2.707 | 67.819 | 2.419 | 0.204 | 166.774 | 1.757 |
| ss_n40C_3v00/rc-max | 1332.588 | 63.897 | 1.847 | 46.285 | 1.651 | 0.146 | 113.826 | 1.199 |
| ss_n40C_3v00/rc-min | 1299.951 | 62.332 | 1.802 | 45.151 | 1.610 | 0.146 | 111.041 | 1.170 |
| ss_n40C_3v00/rc-nom | 1314.590 | 63.034 | 1.823 | 45.660 | 1.628 | 0.146 | 112.290 | 1.183 |
| tt_025C_3v30/rc-max | 1543.830 | 74.026 | 2.140 | 53.622 | 1.912 | 0.146 | 131.846 | 1.389 |
| tt_025C_3v30/rc-min | 1504.371 | 72.134 | 2.086 | 52.251 | 1.863 | 0.146 | 128.480 | 1.354 |
| tt_025C_3v30/rc-nom | 1522.053 | 72.982 | 2.110 | 52.865 | 1.885 | 0.146 | 129.988 | 1.370 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 1845.079 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 219.077 + internal 25.918, vss external 179.626 + internal 24.472 + analog share 0.236 = **449.328 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 2.686 mV.

Worst per-corner estimate: 220.563 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.5207-3.5190 V. Against the 33.000 mV yardstick: **MATERIAL (informational: not a ratified operating rate)**.

### The shared `vss` return, analog side

`vss_trunk_ir_drop.py`'s own conservative bound (analog load only, nominal sheet): 21.935 mV. Adding the digital load's active-rate shift bound at the analog taps (0.137 mV): 22.072 mV against 33.000 mV.

<!-- digital-supply-ir-drop:end -->

## 6. Refusals: what never becomes a zero-drop pass

- **No complete current-DEF record family, or a non-positive or non-finite
  current.** The derivation stops with "UNKNOWN (not a pass)" and
  `--check` exits 2.
- **A floating grid.** An omitted Via4, an omitted Metal5 dock, a rail with
  no vias or a broken via stack leaves part of the network unable to reach
  the pin, and the result is rejected (`ConnectivityError`). It is not
  solved with that part at 0 V.
- **Unproven structural connectivity.** The composed-floorplan `klt erc`
  supply report (`layout/floorplan/reports/erc-supply.json`) must describe
  the committed composed stream byte for byte. It must also report `vddd`
  and `vss` checked and finding-free. If not, the derivation stops.
- **A stale document.** Any change to the DEF, the composed stream, the
  floorplan reports, the drawn shapes of the two nets, a record of the
  family or the analog profile changes the provenance block. `--check` then
  fails until the block is regenerated and this prose is re-read.

`sim/tests/test_resistor_network.py` checks the solver against hand-computed
series, parallel and bridge networks and an independent dense solve.
`sim/tests/test_digital_supply_ir_drop.py` checks each refusal above, and
checks that raising a feed resistance raises the drop by exactly that amount.

## 7. What this is and is not

- **Not structural ERC.** The `klt erc` supply check answers whether each
  supply is one connected island. Here that is a precondition. This
  document answers how many millivolts the conductors cost on the way.
- **Not the analog return analysis.** `characterization-vss-trunk-ir-drop.md`
  remains the analysis of the analog taps. This document only adds the
  digital load's share of the trunk segment it shares with them.
- **Not supply-ripple characterization.** [#414]
  ([`characterization-array-supply-ripple.md`](characterization-array-supply-ripple.md))
  studies time-varying ripple at the analog array. This document is DC only:
  it covers no transient ground bounce, no di/dt and no decoupling.
- **No electromigration verdict, and no package or bond-wire resistance.**
  The chip pin is the reference node.
- **No signoff effect.** Nothing here promotes a T1 item or edits a README
  row. A verdict stated here is characterization only.

## 8. Explicit unknowns

- The per-cell current allocation is unknown. The uniform figure is an
  estimate, and the bound covers every allocation with the same total.
- The temperature coefficient is assumed.
- The high-resistance variant is a process interconnect corner. It is not
  jointly characterized with the liberty corners.
- Metal2/Metal3 signal routing and the well and substrate ties carry no
  supply current in this model. Leaving out these possible parallel paths
  can only overstate the drop.
- Currents are time-averaged, so the same caveat as `vss_trunk_ir_drop.py`
  applies: this is not an instantaneous peak.

## 9. Reproduce

```sh
python3 sim/tools/digital_supply_ir_drop.py            # the report
python3 sim/tools/digital_supply_ir_drop.py --json     # the full result
python3 sim/tools/digital_supply_ir_drop.py --check    # part of npm run check:spec
```

No PDK, no `klt` and no simulator are needed. The derivation reads committed
geometry, reports and records only.

[#224]: https://github.com/2AMLogic/gf180-trng/issues/224
[#234]: https://github.com/2AMLogic/gf180-trng/issues/234
[#414]: https://github.com/2AMLogic/gf180-trng/issues/414
[#453]: https://github.com/2AMLogic/gf180-trng/issues/453
[#464]: https://github.com/2AMLogic/gf180-trng/issues/464
