# DC voltage loss on the digital supply and return: docking path and power grid

Status: derivation complete for issue [#464]. This document quantifies how
much DC voltage the placed digital section loses between the chip pins and
its standard-cell rails, on both `vddd` and `vss`. It covers the external
docking path the composed floorplan draws into `digital` ([#224]) and the
parallel paths of the section's own power grid. It changes no spec row, no
decision record and no signoff item.

**Verdict at the ratified rate: not material.** At DR-0003's 1 MHz rate the
cross-corner upper bound on local supply collapse (the `vddd` drop plus the
`vss` rise that the cells see together) is **6.4 mV**. The worst per-corner
estimate is **2.8 mV** (`ff_125C_3v60/rc-max`). Both are below the 33 mV
yardstick the analog return analysis already uses. Idle (leakage only) is
about 0.14 mV. The digital load adds at most **0.14 mV** to the offset the
analog taps see on the shared `vss` trunk.

**Not covered at the 20 MHz implementation clock.** The place-and-route
clock constraint is not an operating rate this design ratifies. At 20 MHz
the same records give about 1.8 mA, a 51 mV estimate and a 120 mV bound.
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
  goes through a four-cut Via3 row, the 2 um wide Metal3 riser on the stack's
  east flank ([#803]), a 16-cut Via3 and a 16-cut Via4 array at the riser
  top, and the Metal5 dock onto the east end of the net's lowest strap.
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
is dominated by the Metal3 riser and the four-cut Via3 row at the trunk.
Together with the rest of the feed that is about 9 ohm nominal and 15 ohm in
the high-resistance variant for `vddd` (about 8 and 12 ohm for `vss`), against
a grid whose internal share is about 1-2 ohm under uniform allocation. The
plan tags each cut of one landing with a shared `_array` id, and the model
prices the cuts of one id as n parallel cuts at their centroid.

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
  "klt_version": "0.9.1",
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
    "record": "2026-11-09-digital-sta-power-12",
    "sha256": "efa092fc819b38b3246f65f16ed36e41aa408277fae9b4378aa2d2381b740dba"
   },
   {
    "corner": "ff_125C_3v60/rc-min",
    "record": "2026-11-09-digital-sta-power-10",
    "sha256": "0e467e40f8c0e217a905239fee0f094e826a518734a305ce26ed620c6fefbad3"
   },
   {
    "corner": "ff_125C_3v60/rc-nom",
    "record": "2026-11-09-digital-sta-power-11",
    "sha256": "9ffe22c76e8f45c0af0cd8a36d66e51e4f95035971e66bd89c42d6cd8711830f"
   },
   {
    "corner": "ff_n40C_3v60/rc-max",
    "record": "2026-11-09-digital-sta-power-15",
    "sha256": "d07126ec4c15dc118d7cfc15e7e0e14fdf9dda67f145b389b4e16012e0d71ca4"
   },
   {
    "corner": "ff_n40C_3v60/rc-min",
    "record": "2026-11-09-digital-sta-power-13",
    "sha256": "4f1ebdce2737dff432422db37ced0bb9e44c84c2a9a58a3eda28ae38cd79d688"
   },
   {
    "corner": "ff_n40C_3v60/rc-nom",
    "record": "2026-11-09-digital-sta-power-14",
    "sha256": "c573feb76b821db171ae6cd41de1cfa924bbc003f8745ce52b94884f3fad2a7f"
   },
   {
    "corner": "ss_125C_3v00/rc-max",
    "record": "2026-11-09-digital-sta-power-03",
    "sha256": "f539d580cb351bacc026b1e27a1598a042242bc0b3cafe99de202fff35c461a4"
   },
   {
    "corner": "ss_125C_3v00/rc-min",
    "record": "2026-11-09-digital-sta-power-01",
    "sha256": "5f32dfb5e0ac2d06e766f433228ec123ac8260c5ea35581bd19809b9f2b71d9f"
   },
   {
    "corner": "ss_125C_3v00/rc-nom",
    "record": "2026-11-09-digital-sta-power-02",
    "sha256": "682fc4f4393fd5165aaf89b5c3e113cd3189568a4fda39cb8b02a629597d5d38"
   },
   {
    "corner": "ss_n40C_3v00/rc-max",
    "record": "2026-11-09-digital-sta-power-06",
    "sha256": "b3050f79b04c959e3859adc0debc313f8a86f44bf8290cd96f24d56104d0aba1"
   },
   {
    "corner": "ss_n40C_3v00/rc-min",
    "record": "2026-11-09-digital-sta-power-04",
    "sha256": "84b39cf17bc48bf7657f06c67b8db62fe0d01a40f4e98c34c6b40152346d2901"
   },
   {
    "corner": "ss_n40C_3v00/rc-nom",
    "record": "2026-11-09-digital-sta-power-05",
    "sha256": "acacae3e1a7ea10eb35798b433606508745d83eef45d1ec35d3c40569ed5d7b5"
   },
   {
    "corner": "tt_025C_3v30/rc-max",
    "record": "2026-11-09-digital-sta-power-09",
    "sha256": "b14ae85db965bad3d5e66081977fba3afdad1cb0d20160baad4bb95540369b1a"
   },
   {
    "corner": "tt_025C_3v30/rc-min",
    "record": "2026-11-09-digital-sta-power-07",
    "sha256": "cf3cb0a0ba913d802a8aa41dff553291a8ab99b190eccc8f422481559fd6df1e"
   },
   {
    "corner": "tt_025C_3v30/rc-nom",
    "record": "2026-11-09-digital-sta-power-08",
    "sha256": "efcd6f1dd4dc10591926a52eedc8e9a5434b2e2218d83ae6f543a2d193690771"
   }
  ]
 },
 "geometry": {
  "layout/digital/trng_top.def": {
   "git_blob_sha": "87b3dedca82354ea1c6b17e7e2867c806f9625f5"
  },
  "layout/floorplan/reports/area.json": {
   "sha256": "70949c8e523db4f9a853fc2a27a399701e1d5a6d14062269d0d2237d35dcf6de"
  },
  "layout/floorplan/reports/compose.json": {
   "sha256": "9dd97d6ea0a26a65b5519bd236770e7aa8ad46f7fabad40ab2a579a3a758dd85"
  },
  "layout/floorplan/reports/interregion.json": {
   "sha256": "c3346ad9296624833514caf87841325a14855ea51e2c69ddf1cde39209d206b1"
  },
  "layout/floorplan/trng_floorplan.gds": {
   "sha256": "f2f080704ac245bb55534f474f8bf586c50a4ff054930f502215f9233cead025"
  },
  "wiring_plan(vddd, vss) shapes+routes": {
   "sha256": "dd6ca55ad02576bb30887230023a2ecb987eea87ba242b753eab0b2fad7a773a"
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
| `vddd` | nominal | 9.641 | 1.051 | 7.309 | 37 | 8 / 4 | 920 | 1255 |
| `vddd` | high | 14.819 | 1.426 | 9.688 | 37 | 8 / 4 | 920 | 1255 |
| `vss` | nominal | 7.617 | 1.439 | 7.303 | 38 | 8 / 4 | 944 | 1293 |
| `vss` | high | 12.479 | 1.871 | 9.661 | 38 | 8 / 4 | 944 | 1293 |

External feed, element by element, chip pin first (nominal / high, ohm):

| net | element | nominal | high |
|---|---|---:|---:|
| `vddd` | metal4 wiring-plan rect, 3.00 um x 0.30 um | 0.900 | 1.040 |
| `vddd` | via3 array x4 | 1.125 | 3.750 |
| `vddd` | metal3 wiring-plan rect, 150.18 um x 2.00 um | 6.758 | 7.809 |
| `vddd` | via3 array x16 | 0.281 | 0.938 |
| `vddd` | via4 array x16 | 0.281 | 0.938 |
| `vddd` | metal5 wiring-plan rect, 22.09 um x 4.48 um | 0.296 | 0.345 |
| `vss` | metal4 wiring-plan rect, 3.00 um x 0.30 um | 0.900 | 1.040 |
| `vss` | via3 array x4 | 1.125 | 3.750 |
| `vss` | metal3 wiring-plan rect, 106.08 um x 2.00 um | 4.774 | 5.516 |
| `vss` | via3 array x16 | 0.281 | 0.938 |
| `vss` | via4 array x16 | 0.281 | 0.938 |
| `vss` | metal5 wiring-plan rect, 19.09 um x 4.48 um | 0.256 | 0.298 |

Worst points (composed frame, um): `vddd` uniform at [146.51, 418.2], bound at [146.51, 418.2]; `vss` uniform at [146.51, 413.16], bound at [521.71, 423.24].

Analog return's own offset at the `digital` dock on the shared `vss` trunk: nominal active 0.146 mV, nominal idle 0.000 mV, high active 0.168 mV, high idle 0.000 mV.

### Scenario: active, 1 MHz (DR-0003 ratified rate), uniform 0.25 activity

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 94.264 | 1.272 | 0.139 | 1.005 | 0.190 | 0.204 | 2.810 | 0.119 |
| ff_125C_3v60/rc-min | 91.793 | 1.239 | 0.135 | 0.979 | 0.185 | 0.204 | 2.742 | 0.116 |
| ff_125C_3v60/rc-nom | 92.900 | 1.254 | 0.137 | 0.991 | 0.187 | 0.204 | 2.772 | 0.117 |
| ff_n40C_3v60/rc-max | 86.229 | 0.831 | 0.091 | 0.657 | 0.124 | 0.146 | 1.849 | 0.078 |
| ff_n40C_3v60/rc-min | 83.905 | 0.809 | 0.088 | 0.639 | 0.121 | 0.146 | 1.803 | 0.076 |
| ff_n40C_3v60/rc-nom | 84.944 | 0.819 | 0.089 | 0.647 | 0.122 | 0.146 | 1.823 | 0.076 |
| ss_125C_3v00/rc-max | 71.360 | 0.963 | 0.105 | 0.761 | 0.144 | 0.204 | 2.177 | 0.090 |
| ss_125C_3v00/rc-min | 69.645 | 0.940 | 0.102 | 0.743 | 0.140 | 0.204 | 2.129 | 0.088 |
| ss_125C_3v00/rc-nom | 70.414 | 0.950 | 0.104 | 0.751 | 0.142 | 0.204 | 2.151 | 0.089 |
| ss_n40C_3v00/rc-max | 66.684 | 0.643 | 0.070 | 0.508 | 0.096 | 0.146 | 1.463 | 0.060 |
| ss_n40C_3v00/rc-min | 65.052 | 0.627 | 0.068 | 0.495 | 0.094 | 0.146 | 1.430 | 0.059 |
| ss_n40C_3v00/rc-nom | 65.784 | 0.634 | 0.069 | 0.501 | 0.095 | 0.146 | 1.445 | 0.059 |
| tt_025C_3v30/rc-max | 77.254 | 0.745 | 0.081 | 0.588 | 0.111 | 0.146 | 1.671 | 0.070 |
| tt_025C_3v30/rc-min | 75.282 | 0.726 | 0.079 | 0.573 | 0.108 | 0.146 | 1.632 | 0.068 |
| tt_025C_3v30/rc-nom | 76.166 | 0.734 | 0.080 | 0.580 | 0.110 | 0.146 | 1.650 | 0.069 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 94.264 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 1.956 + internal 1.278, vss external 1.647 + internal 1.275 + analog share 0.236 = **6.392 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 0.137 mV.

Worst per-corner estimate: 2.810 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.9636-3.6286 V. Against the 33.000 mV yardstick: **not material**.

### Scenario: idle, leakage only

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 2.116 | 0.029 | 0.003 | 0.023 | 0.004 | 0.000 | 0.059 | 0.003 |
| ff_125C_3v60/rc-min | 2.116 | 0.029 | 0.003 | 0.023 | 0.004 | 0.000 | 0.059 | 0.003 |
| ff_125C_3v60/rc-nom | 2.116 | 0.029 | 0.003 | 0.023 | 0.004 | 0.000 | 0.059 | 0.003 |
| ff_n40C_3v60/rc-max | 0.070 | 0.001 | 0.000 | 0.001 | 0.000 | 0.000 | 0.001 | 0.000 |
| ff_n40C_3v60/rc-min | 0.070 | 0.001 | 0.000 | 0.001 | 0.000 | 0.000 | 0.001 | 0.000 |
| ff_n40C_3v60/rc-nom | 0.070 | 0.001 | 0.000 | 0.001 | 0.000 | 0.000 | 0.001 | 0.000 |
| ss_125C_3v00/rc-max | 0.713 | 0.010 | 0.001 | 0.008 | 0.001 | 0.000 | 0.020 | 0.001 |
| ss_125C_3v00/rc-min | 0.713 | 0.010 | 0.001 | 0.008 | 0.001 | 0.000 | 0.020 | 0.001 |
| ss_125C_3v00/rc-nom | 0.713 | 0.010 | 0.001 | 0.008 | 0.001 | 0.000 | 0.020 | 0.001 |
| ss_n40C_3v00/rc-max | 0.056 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 |
| ss_n40C_3v00/rc-min | 0.056 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 |
| ss_n40C_3v00/rc-nom | 0.056 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 |
| tt_025C_3v30/rc-max | 0.065 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 |
| tt_025C_3v30/rc-min | 0.065 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 |
| tt_025C_3v30/rc-nom | 0.065 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 2.116 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 0.044 + internal 0.029, vss external 0.037 + internal 0.029 + analog share 0.000 = **0.138 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 0.003 mV.

Worst per-corner estimate: 0.059 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.9699-3.6300 V. Against the 33.000 mV yardstick: **not material**.

### Scenario: stress, 20 MHz (place-and-route clock constraint; informational)

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 1845.090 | 24.905 | 2.714 | 19.675 | 3.717 | 0.204 | 51.215 | 2.325 |
| ff_125C_3v60/rc-min | 1795.669 | 24.238 | 2.641 | 19.148 | 3.618 | 0.204 | 49.849 | 2.263 |
| ff_125C_3v60/rc-nom | 1817.795 | 24.536 | 2.674 | 19.384 | 3.662 | 0.204 | 50.461 | 2.290 |
| ff_n40C_3v60/rc-max | 1723.263 | 16.615 | 1.810 | 13.126 | 2.480 | 0.146 | 34.176 | 1.551 |
| ff_n40C_3v60/rc-min | 1676.783 | 16.167 | 1.762 | 12.772 | 2.413 | 0.146 | 33.259 | 1.509 |
| ff_n40C_3v60/rc-nom | 1697.561 | 16.367 | 1.783 | 12.930 | 2.443 | 0.146 | 33.669 | 1.528 |
| ss_125C_3v00/rc-max | 1413.644 | 19.081 | 2.079 | 15.074 | 2.848 | 0.204 | 39.287 | 1.781 |
| ss_125C_3v00/rc-min | 1379.346 | 18.618 | 2.029 | 14.708 | 2.779 | 0.204 | 38.339 | 1.738 |
| ss_125C_3v00/rc-nom | 1394.722 | 18.826 | 2.051 | 14.872 | 2.810 | 0.204 | 38.764 | 1.757 |
| ss_n40C_3v00/rc-max | 1332.611 | 12.848 | 1.400 | 10.150 | 1.918 | 0.146 | 26.462 | 1.199 |
| ss_n40C_3v00/rc-min | 1299.974 | 12.534 | 1.366 | 9.902 | 1.871 | 0.146 | 25.817 | 1.170 |
| ss_n40C_3v00/rc-nom | 1314.613 | 12.675 | 1.381 | 10.013 | 1.892 | 0.146 | 26.106 | 1.183 |
| tt_025C_3v30/rc-max | 1543.852 | 14.885 | 1.622 | 11.759 | 2.222 | 0.146 | 30.633 | 1.389 |
| tt_025C_3v30/rc-min | 1504.407 | 14.505 | 1.581 | 11.459 | 2.165 | 0.146 | 29.855 | 1.354 |
| tt_025C_3v30/rc-nom | 1522.085 | 14.675 | 1.599 | 11.593 | 2.190 | 0.146 | 30.204 | 1.370 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 1845.090 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 38.280 + internal 25.024, vss external 32.236 + internal 24.955 + analog share 0.236 = **120.731 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 2.686 mV.

Worst per-corner estimate: 51.215 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.8493-3.6042 V. Against the 33.000 mV yardstick: **MATERIAL (informational: not a ratified operating rate)**.

### The shared `vss` return, analog side

`vss_trunk_ir_drop.py`'s own conservative bound (analog load only, nominal sheet): 23.305 mV. Adding the digital load's active-rate shift bound at the analog taps (0.137 mV): 23.443 mV against 33.000 mV.

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
[#803]: https://github.com/2AMLogic/gf180-trng/issues/803
