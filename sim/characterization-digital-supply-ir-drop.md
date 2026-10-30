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
    "record": "2026-10-30-digital-sta-power-12",
    "sha256": "852957e175b06e7deeadd04219548cb431a04ea7d11d0d7a6f54ae1b4047f1d5"
   },
   {
    "corner": "ff_125C_3v60/rc-min",
    "record": "2026-10-30-digital-sta-power-10",
    "sha256": "efecfe360bb69d4f2a35223b44e5156f930119c8d2fb9036067433e458441f67"
   },
   {
    "corner": "ff_125C_3v60/rc-nom",
    "record": "2026-10-30-digital-sta-power-11",
    "sha256": "ace1ce4c11db15162130d5dd5b240b2f13c32458c48af69050c414356fb221fe"
   },
   {
    "corner": "ff_n40C_3v60/rc-max",
    "record": "2026-10-30-digital-sta-power-15",
    "sha256": "59a5d0f9ab950b4a849439aba0f8bafef142800e3d3f7f22569c7a9ca2202137"
   },
   {
    "corner": "ff_n40C_3v60/rc-min",
    "record": "2026-10-30-digital-sta-power-13",
    "sha256": "19a33018e09846d6214254ac70a74463fc3a7ca7cf3016e27a457730af9d5e5c"
   },
   {
    "corner": "ff_n40C_3v60/rc-nom",
    "record": "2026-10-30-digital-sta-power-14",
    "sha256": "f3d209fb5cc9cbd582f960f7c85032b3ef84b70185d22a71a9e314db6c4f2aa2"
   },
   {
    "corner": "ss_125C_3v00/rc-max",
    "record": "2026-10-30-digital-sta-power-03",
    "sha256": "f1708a592d4437d0796183215230700a1ee94a0fbb6d14b5b67f12830d2bf4b6"
   },
   {
    "corner": "ss_125C_3v00/rc-min",
    "record": "2026-10-30-digital-sta-power-01",
    "sha256": "95afa856e18f1d63e045558449a3cd62d998ac0bd0bce5af69979b6db9c8962e"
   },
   {
    "corner": "ss_125C_3v00/rc-nom",
    "record": "2026-10-30-digital-sta-power-02",
    "sha256": "2338a676871021b16c07c7ad23da6a51c471926fb8067292663ddf57727ebb34"
   },
   {
    "corner": "ss_n40C_3v00/rc-max",
    "record": "2026-10-30-digital-sta-power-06",
    "sha256": "2a3394f43fa2e653b110595d76b8fbb78738bd461c30328f3744f65e7df2f032"
   },
   {
    "corner": "ss_n40C_3v00/rc-min",
    "record": "2026-10-30-digital-sta-power-04",
    "sha256": "862e1c05556d2afd47726eadd96417fe039e3aac77298046c215b0dfa6c649ca"
   },
   {
    "corner": "ss_n40C_3v00/rc-nom",
    "record": "2026-10-30-digital-sta-power-05",
    "sha256": "beaddf5d366d205ea905a1414e48e3fdb5692d56eb21736aa81fa363e29bb079"
   },
   {
    "corner": "tt_025C_3v30/rc-max",
    "record": "2026-10-30-digital-sta-power-09",
    "sha256": "eefece50cd37085d3970a5f3d85e9e58ea6ed356cb1b3c10e264a35fd7a4e95c"
   },
   {
    "corner": "tt_025C_3v30/rc-min",
    "record": "2026-10-30-digital-sta-power-07",
    "sha256": "1cbec18e37b2d2c2b8e277e5b503bbb8a723b45b94a837e5574939a0195276de"
   },
   {
    "corner": "tt_025C_3v30/rc-nom",
    "record": "2026-10-30-digital-sta-power-08",
    "sha256": "8fd27ac9bb5d187cbb284ba94032630846104f27ff6c602372c190b2dfff3f55"
   }
  ]
 },
 "geometry": {
  "layout/digital/trng_top.def": {
   "git_blob_sha": "d24d862fc3836f8f5514aa2fa32e319f1a96567c"
  },
  "layout/floorplan/reports/area.json": {
   "sha256": "dfa8af817716fa78cf15b484e4fffeb72ce53b53ff9d47d17834dc535d2e7b1d"
  },
  "layout/floorplan/reports/compose.json": {
   "sha256": "57f3ae3681b6acf10ad3663beb84513c2002f661f230c640a0fc543252c04a62"
  },
  "layout/floorplan/reports/interregion.json": {
   "sha256": "ec3fe16d5077298ed6a3ee41eb3fc4728e7f3288bb4c34b3d2c3c26c0840b035"
  },
  "layout/floorplan/trng_floorplan.gds": {
   "sha256": "2382d2c4d5a0784260d6c50fd57d53bb09c01e7b7bf6503be49afec5ee08717d"
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
| ff_125C_3v60/rc-max | 96.860 | 6.502 | 0.189 | 4.710 | 0.169 | 0.204 | 11.774 | 0.122 |
| ff_125C_3v60/rc-min | 94.160 | 6.321 | 0.184 | 4.579 | 0.165 | 0.204 | 11.452 | 0.119 |
| ff_125C_3v60/rc-nom | 95.364 | 6.402 | 0.186 | 4.637 | 0.167 | 0.204 | 11.596 | 0.120 |
| ff_n40C_3v60/rc-max | 88.632 | 4.250 | 0.124 | 3.078 | 0.111 | 0.146 | 7.708 | 0.080 |
| ff_n40C_3v60/rc-min | 86.102 | 4.129 | 0.120 | 2.991 | 0.107 | 0.146 | 7.492 | 0.077 |
| ff_n40C_3v60/rc-nom | 87.231 | 4.183 | 0.122 | 3.030 | 0.109 | 0.146 | 7.589 | 0.079 |
| ss_125C_3v00/rc-max | 73.623 | 4.942 | 0.144 | 3.580 | 0.129 | 0.204 | 8.999 | 0.093 |
| ss_125C_3v00/rc-min | 71.747 | 4.816 | 0.140 | 3.489 | 0.125 | 0.204 | 8.774 | 0.090 |
| ss_125C_3v00/rc-nom | 72.588 | 4.873 | 0.142 | 3.530 | 0.127 | 0.204 | 8.875 | 0.091 |
| ss_n40C_3v00/rc-max | 68.804 | 3.299 | 0.096 | 2.390 | 0.086 | 0.146 | 6.016 | 0.062 |
| ss_n40C_3v00/rc-min | 67.010 | 3.213 | 0.093 | 2.327 | 0.084 | 0.146 | 5.863 | 0.060 |
| ss_n40C_3v00/rc-nom | 67.814 | 3.252 | 0.095 | 2.355 | 0.085 | 0.146 | 5.932 | 0.061 |
| tt_025C_3v30/rc-max | 79.542 | 3.814 | 0.111 | 2.763 | 0.099 | 0.146 | 6.933 | 0.072 |
| tt_025C_3v30/rc-min | 77.379 | 3.710 | 0.108 | 2.688 | 0.097 | 0.146 | 6.748 | 0.070 |
| tt_025C_3v30/rc-nom | 78.347 | 3.757 | 0.109 | 2.721 | 0.098 | 0.146 | 6.831 | 0.071 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 96.860 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 11.501 + internal 1.372, vss external 9.430 + internal 1.337 + analog share 0.236 = **23.875 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 0.141 mV.

Worst per-corner estimate: 11.774 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.9461-3.6241 V. Against the 33.000 mV yardstick: **not material**.

### Scenario: idle, leakage only

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 2.288 | 0.154 | 0.004 | 0.111 | 0.004 | 0.000 | 0.274 | 0.003 |
| ff_125C_3v60/rc-min | 2.288 | 0.154 | 0.004 | 0.111 | 0.004 | 0.000 | 0.274 | 0.003 |
| ff_125C_3v60/rc-nom | 2.288 | 0.154 | 0.004 | 0.111 | 0.004 | 0.000 | 0.274 | 0.003 |
| ff_n40C_3v60/rc-max | 0.076 | 0.004 | 0.000 | 0.003 | 0.000 | 0.000 | 0.007 | 0.000 |
| ff_n40C_3v60/rc-min | 0.076 | 0.004 | 0.000 | 0.003 | 0.000 | 0.000 | 0.007 | 0.000 |
| ff_n40C_3v60/rc-nom | 0.076 | 0.004 | 0.000 | 0.003 | 0.000 | 0.000 | 0.007 | 0.000 |
| ss_125C_3v00/rc-max | 0.819 | 0.055 | 0.002 | 0.040 | 0.001 | 0.000 | 0.098 | 0.001 |
| ss_125C_3v00/rc-min | 0.819 | 0.055 | 0.002 | 0.040 | 0.001 | 0.000 | 0.098 | 0.001 |
| ss_125C_3v00/rc-nom | 0.819 | 0.055 | 0.002 | 0.040 | 0.001 | 0.000 | 0.098 | 0.001 |
| ss_n40C_3v00/rc-max | 0.062 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.005 | 0.000 |
| ss_n40C_3v00/rc-min | 0.062 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.005 | 0.000 |
| ss_n40C_3v00/rc-nom | 0.062 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.005 | 0.000 |
| tt_025C_3v30/rc-max | 0.071 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |
| tt_025C_3v30/rc-min | 0.071 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |
| tt_025C_3v30/rc-nom | 0.071 | 0.003 | 0.000 | 0.002 | 0.000 | 0.000 | 0.006 | 0.000 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 2.288 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 0.272 + internal 0.032, vss external 0.223 + internal 0.032 + analog share 0.000 = **0.559 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 0.003 mV.

Worst per-corner estimate: 0.274 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.9694-3.6300 V. Against the 33.000 mV yardstick: **not material**.

### Scenario: stress, 20 MHz (place-and-route clock constraint; informational)

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 1893.719 | 127.124 | 3.695 | 92.084 | 3.310 | 0.204 | 226.417 | 2.386 |
| ff_125C_3v60/rc-min | 1839.724 | 123.499 | 3.590 | 89.459 | 3.215 | 0.204 | 219.967 | 2.318 |
| ff_125C_3v60/rc-nom | 1863.793 | 125.115 | 3.637 | 90.629 | 3.257 | 0.204 | 222.842 | 2.348 |
| ff_n40C_3v60/rc-max | 1771.189 | 84.928 | 2.469 | 61.519 | 2.211 | 0.146 | 151.272 | 1.594 |
| ff_n40C_3v60/rc-min | 1720.579 | 82.501 | 2.398 | 59.761 | 2.148 | 0.146 | 146.953 | 1.549 |
| ff_n40C_3v60/rc-nom | 1743.177 | 83.585 | 2.430 | 60.546 | 2.176 | 0.146 | 148.882 | 1.569 |
| ss_125C_3v00/rc-max | 1456.909 | 97.801 | 2.843 | 70.844 | 2.546 | 0.204 | 174.238 | 1.836 |
| ss_125C_3v00/rc-min | 1419.373 | 95.282 | 2.770 | 69.019 | 2.481 | 0.204 | 169.754 | 1.788 |
| ss_125C_3v00/rc-nom | 1436.198 | 96.411 | 2.802 | 69.837 | 2.510 | 0.204 | 171.764 | 1.810 |
| ss_n40C_3v00/rc-max | 1374.903 | 65.926 | 1.916 | 47.754 | 1.716 | 0.146 | 117.459 | 1.237 |
| ss_n40C_3v00/rc-min | 1339.019 | 64.205 | 1.866 | 46.508 | 1.672 | 0.146 | 114.397 | 1.205 |
| ss_n40C_3v00/rc-nom | 1355.106 | 64.977 | 1.889 | 47.067 | 1.692 | 0.146 | 115.770 | 1.220 |
| tt_025C_3v30/rc-max | 1589.483 | 76.215 | 2.215 | 55.207 | 1.984 | 0.146 | 135.768 | 1.431 |
| tt_025C_3v30/rc-min | 1546.227 | 74.141 | 2.155 | 53.705 | 1.930 | 0.146 | 132.077 | 1.392 |
| tt_025C_3v30/rc-nom | 1565.580 | 75.069 | 2.182 | 54.377 | 1.954 | 0.146 | 133.728 | 1.409 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 1893.719 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 224.852 + internal 26.818, vss external 184.362 + internal 26.146 + analog share 0.236 = **462.414 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 2.757 mV.

Worst per-corner estimate: 226.417 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.5076-3.5156 V. Against the 33.000 mV yardstick: **MATERIAL (informational: not a ratified operating rate)**.

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
