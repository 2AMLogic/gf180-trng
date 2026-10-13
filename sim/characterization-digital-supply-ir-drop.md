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
    "record": "2026-10-10-digital-sta-power-12",
    "sha256": "4553ff32ae080c69b795b4288f72f95f98e93a719dd8dcbd162ef4a4be587885"
   },
   {
    "corner": "ff_125C_3v60/rc-min",
    "record": "2026-10-10-digital-sta-power-10",
    "sha256": "e5b6cd9e271b5e957e3bb04eae8714ce27c0335b7227c922267b9be0e93b6c84"
   },
   {
    "corner": "ff_125C_3v60/rc-nom",
    "record": "2026-10-10-digital-sta-power-11",
    "sha256": "7c7319e438fb07ccaf550f29a2d85419177cba3c80b7d834f18f5977519edd93"
   },
   {
    "corner": "ff_n40C_3v60/rc-max",
    "record": "2026-10-10-digital-sta-power-15",
    "sha256": "331e6bfb8ee153282af65018de445d7ad2197f937d3fe92b11ef59b6d5223523"
   },
   {
    "corner": "ff_n40C_3v60/rc-min",
    "record": "2026-10-10-digital-sta-power-13",
    "sha256": "3cf86d6b4484bdf1ca383c4fd31d7e9621cf11602b1306bca8fb72c548bfce0a"
   },
   {
    "corner": "ff_n40C_3v60/rc-nom",
    "record": "2026-10-10-digital-sta-power-14",
    "sha256": "c77ae77f7b31d0f5c30680606ab61fea824cdcbf619905824e9cd3a464ef54be"
   },
   {
    "corner": "ss_125C_3v00/rc-max",
    "record": "2026-10-10-digital-sta-power-03",
    "sha256": "24848148225624df83ed9c8a94623a74c8c87a1b6b8da184a131975f72c44249"
   },
   {
    "corner": "ss_125C_3v00/rc-min",
    "record": "2026-10-10-digital-sta-power-01",
    "sha256": "842e6280fe1d9648945e3fd6dded9c6f12cb03c0d1feadaf6c271843a1db0f3c"
   },
   {
    "corner": "ss_125C_3v00/rc-nom",
    "record": "2026-10-10-digital-sta-power-02",
    "sha256": "46cea5b05b6adc05576094259af6ccca7f49e8b592f8c84b0b722692102f96f0"
   },
   {
    "corner": "ss_n40C_3v00/rc-max",
    "record": "2026-10-10-digital-sta-power-06",
    "sha256": "57ff339408fbaea3810888ec41907f98b6a8b472c0e13849a4edc3446efe1e4c"
   },
   {
    "corner": "ss_n40C_3v00/rc-min",
    "record": "2026-10-10-digital-sta-power-04",
    "sha256": "216a0c5f3bb64b13ad0cb077c0fe1dd78fb244f06a8dd1f759662a386339a7b2"
   },
   {
    "corner": "ss_n40C_3v00/rc-nom",
    "record": "2026-10-10-digital-sta-power-05",
    "sha256": "662ab364aed8068d3705febd40258bd1a46f58f5d7e94bd2f51a80aa6ca497c7"
   },
   {
    "corner": "tt_025C_3v30/rc-max",
    "record": "2026-10-10-digital-sta-power-09",
    "sha256": "2d1a7a5b999f1ab2fd6c2486e4cf3938f55b6c7e540737f63950e4377dcb41cd"
   },
   {
    "corner": "tt_025C_3v30/rc-min",
    "record": "2026-10-10-digital-sta-power-07",
    "sha256": "f836b4b3e04212d2c76607c19ed118008881e66eff28f3590295ca21b44d9815"
   },
   {
    "corner": "tt_025C_3v30/rc-nom",
    "record": "2026-10-10-digital-sta-power-08",
    "sha256": "7c11c0d426927c6c054365f86f57a0bdcbb224e066d49c9f8eced8b9bec0f7f5"
   }
  ]
 },
 "geometry": {
  "layout/digital/trng_top.def": {
   "git_blob_sha": "8f13adca1f40260c48314a800b021eda212876f4"
  },
  "layout/floorplan/reports/area.json": {
   "sha256": "dfa8af817716fa78cf15b484e4fffeb72ce53b53ff9d47d17834dc535d2e7b1d"
  },
  "layout/floorplan/reports/compose.json": {
   "sha256": "66c65eb303cb05f68682f1848c02c4cf4ada310346ac4633d5e2c5d8820be65d"
  },
  "layout/floorplan/reports/interregion.json": {
   "sha256": "1444dd827c675b77ffc94dfcc7d181f53b1240257f697ae6f62fc3213e74a292"
  },
  "layout/floorplan/trng_floorplan.gds": {
   "sha256": "5d20e8808b5b7f59f27bc750128d5008899391b742a2f2bf902754b11428cc21"
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
| `vddd` | nominal | 47.950 | 1.394 | 7.649 | 38 | 8 / 4 | 944 | 1287 |
| `vddd` | high | 84.811 | 1.826 | 10.115 | 38 | 8 / 4 | 944 | 1287 |
| `vss` | nominal | 34.733 | 1.248 | 7.478 | 38 | 8 / 4 | 944 | 1293 |
| `vss` | high | 69.539 | 1.648 | 9.862 | 38 | 8 / 4 | 944 | 1293 |

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

Worst points (composed frame, um): `vddd` uniform at [909.22, 379.0], bound at [530.66, 389.08]; `vss` uniform at [909.22, 384.04], bound at [909.22, 384.04].

Analog return's own offset at the `digital` dock on the shared `vss` trunk: nominal active 0.146 mV, nominal idle 0.000 mV, high active 0.168 mV, high idle 0.000 mV.

### Scenario: active, 1 MHz (DR-0003 ratified rate), uniform 0.25 activity

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 96.718 | 6.493 | 0.189 | 4.703 | 0.169 | 0.204 | 11.757 | 0.122 |
| ff_125C_3v60/rc-min | 94.056 | 6.314 | 0.184 | 4.574 | 0.164 | 0.204 | 11.439 | 0.119 |
| ff_125C_3v60/rc-nom | 95.246 | 6.394 | 0.186 | 4.631 | 0.166 | 0.204 | 11.582 | 0.120 |
| ff_n40C_3v60/rc-max | 88.581 | 4.247 | 0.123 | 3.077 | 0.111 | 0.146 | 7.704 | 0.080 |
| ff_n40C_3v60/rc-min | 86.085 | 4.128 | 0.120 | 2.990 | 0.107 | 0.146 | 7.491 | 0.077 |
| ff_n40C_3v60/rc-nom | 87.201 | 4.181 | 0.122 | 3.029 | 0.109 | 0.146 | 7.586 | 0.078 |
| ss_125C_3v00/rc-max | 73.481 | 4.933 | 0.143 | 3.573 | 0.128 | 0.204 | 8.982 | 0.093 |
| ss_125C_3v00/rc-min | 71.632 | 4.809 | 0.140 | 3.483 | 0.125 | 0.204 | 8.761 | 0.090 |
| ss_125C_3v00/rc-nom | 72.461 | 4.864 | 0.141 | 3.523 | 0.127 | 0.204 | 8.860 | 0.091 |
| ss_n40C_3v00/rc-max | 68.725 | 3.295 | 0.096 | 2.387 | 0.086 | 0.146 | 6.010 | 0.062 |
| ss_n40C_3v00/rc-min | 66.957 | 3.211 | 0.093 | 2.326 | 0.084 | 0.146 | 5.859 | 0.060 |
| ss_n40C_3v00/rc-nom | 67.750 | 3.249 | 0.094 | 2.353 | 0.085 | 0.146 | 5.926 | 0.061 |
| tt_025C_3v30/rc-max | 79.475 | 3.811 | 0.111 | 2.760 | 0.099 | 0.146 | 6.927 | 0.072 |
| tt_025C_3v30/rc-min | 77.347 | 3.709 | 0.108 | 2.686 | 0.097 | 0.146 | 6.745 | 0.070 |
| tt_025C_3v30/rc-nom | 78.300 | 3.754 | 0.109 | 2.720 | 0.098 | 0.146 | 6.827 | 0.070 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 96.718 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 11.484 + internal 1.370, vss external 9.416 + internal 1.335 + analog share 0.236 = **23.841 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 0.141 mV.

Worst per-corner estimate: 11.757 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.9462-3.6241 V. Against the 33.000 mV yardstick: **not material**.

### Scenario: idle, leakage only

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 2.178 | 0.146 | 0.004 | 0.106 | 0.004 | 0.000 | 0.260 | 0.003 |
| ff_125C_3v60/rc-min | 2.178 | 0.146 | 0.004 | 0.106 | 0.004 | 0.000 | 0.260 | 0.003 |
| ff_125C_3v60/rc-nom | 2.178 | 0.146 | 0.004 | 0.106 | 0.004 | 0.000 | 0.260 | 0.003 |
| ff_n40C_3v60/rc-max | 0.071 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |
| ff_n40C_3v60/rc-min | 0.071 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |
| ff_n40C_3v60/rc-nom | 0.071 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |
| ss_125C_3v00/rc-max | 0.736 | 0.049 | 0.001 | 0.036 | 0.001 | 0.000 | 0.088 | 0.001 |
| ss_125C_3v00/rc-min | 0.736 | 0.049 | 0.001 | 0.036 | 0.001 | 0.000 | 0.088 | 0.001 |
| ss_125C_3v00/rc-nom | 0.736 | 0.049 | 0.001 | 0.036 | 0.001 | 0.000 | 0.088 | 0.001 |
| ss_n40C_3v00/rc-max | 0.058 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.005 | 0.000 |
| ss_n40C_3v00/rc-min | 0.058 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.005 | 0.000 |
| ss_n40C_3v00/rc-nom | 0.058 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.005 | 0.000 |
| tt_025C_3v30/rc-max | 0.066 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |
| tt_025C_3v30/rc-min | 0.066 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |
| tt_025C_3v30/rc-nom | 0.066 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 2.178 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 0.259 + internal 0.031, vss external 0.212 + internal 0.030 + analog share 0.000 = **0.532 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 0.003 mV.

Worst per-corner estimate: 0.260 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.9695-3.6300 V. Against the 33.000 mV yardstick: **not material**.

### Scenario: stress, 20 MHz (place-and-route clock constraint; informational)

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 1892.967 | 127.074 | 3.694 | 92.048 | 3.308 | 0.204 | 226.327 | 2.385 |
| ff_125C_3v60/rc-min | 1839.730 | 123.500 | 3.590 | 89.459 | 3.215 | 0.204 | 219.968 | 2.318 |
| ff_125C_3v60/rc-nom | 1863.541 | 125.098 | 3.636 | 90.617 | 3.257 | 0.204 | 222.812 | 2.348 |
| ff_n40C_3v60/rc-max | 1770.263 | 84.883 | 2.467 | 61.486 | 2.210 | 0.146 | 151.193 | 1.593 |
| ff_n40C_3v60/rc-min | 1720.349 | 82.490 | 2.398 | 59.753 | 2.148 | 0.146 | 146.934 | 1.548 |
| ff_n40C_3v60/rc-nom | 1742.658 | 83.560 | 2.429 | 60.528 | 2.176 | 0.146 | 148.837 | 1.568 |
| ss_125C_3v00/rc-max | 1455.624 | 97.715 | 2.840 | 70.781 | 2.544 | 0.204 | 174.085 | 1.834 |
| ss_125C_3v00/rc-min | 1418.641 | 95.232 | 2.768 | 68.983 | 2.479 | 0.204 | 169.667 | 1.787 |
| ss_125C_3v00/rc-nom | 1435.220 | 96.345 | 2.800 | 69.789 | 2.508 | 0.204 | 171.647 | 1.808 |
| ss_n40C_3v00/rc-max | 1373.412 | 65.854 | 1.914 | 47.703 | 1.715 | 0.146 | 117.332 | 1.236 |
| ss_n40C_3v00/rc-min | 1338.045 | 64.159 | 1.865 | 46.474 | 1.670 | 0.146 | 114.314 | 1.204 |
| ss_n40C_3v00/rc-nom | 1353.898 | 64.919 | 1.887 | 47.025 | 1.690 | 0.146 | 115.667 | 1.219 |
| tt_025C_3v30/rc-max | 1588.238 | 76.155 | 2.214 | 55.164 | 1.983 | 0.146 | 135.662 | 1.429 |
| tt_025C_3v30/rc-min | 1545.672 | 74.114 | 2.154 | 53.686 | 1.930 | 0.146 | 132.030 | 1.391 |
| tt_025C_3v30/rc-nom | 1564.745 | 75.029 | 2.181 | 54.348 | 1.953 | 0.146 | 133.657 | 1.408 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 1892.967 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 224.763 + internal 26.808, vss external 184.289 + internal 26.136 + analog share 0.236 = **462.231 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 2.756 mV.

Worst per-corner estimate: 226.327 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.5078-3.5157 V. Against the 33.000 mV yardstick: **MATERIAL (informational: not a ratified operating rate)**.

### The shared `vss` return, analog side

`vss_trunk_ir_drop.py`'s own conservative bound (analog load only, nominal sheet): 21.935 mV. Adding the digital load's active-rate shift bound at the analog taps (0.141 mV): 22.076 mV against 33.000 mV.

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
