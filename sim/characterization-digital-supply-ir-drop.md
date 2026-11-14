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
    "record": "2026-11-13-digital-sta-power-12",
    "sha256": "ef834e747c5f37c94560be864343f612f7782334bee18cf393ed681c0f2ae52c"
   },
   {
    "corner": "ff_125C_3v60/rc-min",
    "record": "2026-11-13-digital-sta-power-10",
    "sha256": "27030c06df93b006354d9a39da36b05eca525fe00ff6653cc0132f7b2cd3d055"
   },
   {
    "corner": "ff_125C_3v60/rc-nom",
    "record": "2026-11-13-digital-sta-power-11",
    "sha256": "85795e4f818fb8ba0fedfb99f3744071c5df4376758dc8859bb2e87a2e4e7c5b"
   },
   {
    "corner": "ff_n40C_3v60/rc-max",
    "record": "2026-11-13-digital-sta-power-15",
    "sha256": "d2159a3feb41a24917aed18a1bfbde38f76be93ef45e67b1e188e871000b9728"
   },
   {
    "corner": "ff_n40C_3v60/rc-min",
    "record": "2026-11-13-digital-sta-power-13",
    "sha256": "73765575705712ab64415cc9746d47ff9551591100bb5950ab47a0433e51b3c5"
   },
   {
    "corner": "ff_n40C_3v60/rc-nom",
    "record": "2026-11-13-digital-sta-power-14",
    "sha256": "52636bf05976a5118f1471d21ecbd7834ecfcdd9dc0398b0bce64406e35aaa22"
   },
   {
    "corner": "ss_125C_3v00/rc-max",
    "record": "2026-11-13-digital-sta-power-03",
    "sha256": "26fddedfa19970e277dce57ae1a84d435ba7a111a8e0161a6b3279e58963ccd9"
   },
   {
    "corner": "ss_125C_3v00/rc-min",
    "record": "2026-11-13-digital-sta-power-01",
    "sha256": "61570688cb6ece59b6771e24714d6d53c9ea96bca23292a29005e455200a8c80"
   },
   {
    "corner": "ss_125C_3v00/rc-nom",
    "record": "2026-11-13-digital-sta-power-02",
    "sha256": "0aecd237595163f2aa7cb9759d74e56f1219d9a88d6f2e9f2eb0aff5d622c983"
   },
   {
    "corner": "ss_n40C_3v00/rc-max",
    "record": "2026-11-13-digital-sta-power-06",
    "sha256": "f19c374ba3549a0982aaef3e089fac0cda10d2894a8029d5fca4d8c6909f979e"
   },
   {
    "corner": "ss_n40C_3v00/rc-min",
    "record": "2026-11-13-digital-sta-power-04",
    "sha256": "e5bb1e4625bd97a1c7e3bf0a19fb1438c74d267081574bfdd76a732c2f8bb41c"
   },
   {
    "corner": "ss_n40C_3v00/rc-nom",
    "record": "2026-11-13-digital-sta-power-05",
    "sha256": "4a2ea2545e81154224d6ed5b9de79e421a8425b787aff43af3f382f1d4eeb3cd"
   },
   {
    "corner": "tt_025C_3v30/rc-max",
    "record": "2026-11-13-digital-sta-power-09",
    "sha256": "f22cbb8c356d7ca4817c9b2a02cfc49435bd99500a0a85be27f208ed8ffab47b"
   },
   {
    "corner": "tt_025C_3v30/rc-min",
    "record": "2026-11-13-digital-sta-power-07",
    "sha256": "7e13fe56c010d4f8116461a8156230833c6cbc897ca8410e7fbb5df9fb1167f9"
   },
   {
    "corner": "tt_025C_3v30/rc-nom",
    "record": "2026-11-13-digital-sta-power-08",
    "sha256": "423917d7ea88356d6e0fdb3f797de40ef587656cda30f7f7288e0b9a4622441f"
   }
  ]
 },
 "geometry": {
  "layout/digital/trng_top.def": {
   "git_blob_sha": "89e8f60a83222b44213d3c89a059db389405b475"
  },
  "layout/floorplan/reports/area.json": {
   "sha256": "ce595d39ddbe154a66d704c1253c78882a89f51917028ec93b1d3bfd320524c8"
  },
  "layout/floorplan/reports/compose.json": {
   "sha256": "0a245017499223852498cdd6b1d31f4f1f5cc24d5ba7b6df6b7e6cb26c90e553"
  },
  "layout/floorplan/reports/interregion.json": {
   "sha256": "0895fc227155b66342207ff0d9548e2b341cebcf749c01aa1c578cd80c7ba37d"
  },
  "layout/floorplan/trng_floorplan.gds": {
   "sha256": "faa782a8ec4f8c17c04cb2f32cf2bf19c7ec89cddcc1bb1ca29da8c71a991ff3"
  },
  "wiring_plan(vddd, vss) shapes+routes": {
   "sha256": "f09b5218335bf2ee8c8a95660f61e7b388e94a33c7645a4cef01324d3e4984e5"
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
| `vddd` | nominal | 9.590 | 1.036 | 7.294 | 37 | 8 / 4 | 920 | 1255 |
| `vddd` | high | 14.759 | 1.409 | 9.670 | 37 | 8 / 4 | 920 | 1255 |
| `vss` | nominal | 7.565 | 1.425 | 7.176 | 38 | 8 / 4 | 944 | 1293 |
| `vss` | high | 12.419 | 1.854 | 9.514 | 38 | 8 / 4 | 944 | 1293 |

External feed, element by element, chip pin first (nominal / high, ohm):

| net | element | nominal | high |
|---|---|---:|---:|
| `vddd` | metal4 wiring-plan rect, 3.00 um x 0.30 um | 0.900 | 1.040 |
| `vddd` | via3 array x4 | 1.125 | 3.750 |
| `vddd` | metal3 wiring-plan rect, 150.18 um x 2.00 um | 6.758 | 7.809 |
| `vddd` | via3 array x16 | 0.281 | 0.938 |
| `vddd` | via4 array x16 | 0.281 | 0.938 |
| `vddd` | metal5 wiring-plan rect, 18.23 um x 4.48 um | 0.244 | 0.285 |
| `vss` | metal4 wiring-plan rect, 3.00 um x 0.30 um | 0.900 | 1.040 |
| `vss` | via3 array x4 | 1.125 | 3.750 |
| `vss` | metal3 wiring-plan rect, 106.08 um x 2.00 um | 4.774 | 5.516 |
| `vss` | via3 array x16 | 0.281 | 0.938 |
| `vss` | via4 array x16 | 0.281 | 0.938 |
| `vss` | metal5 wiring-plan rect, 15.23 um x 4.48 um | 0.204 | 0.238 |

Worst points (composed frame, um): `vddd` uniform at [147.99, 418.2], bound at [147.99, 418.2]; `vss` uniform at [147.99, 413.16], bound at [522.07, 423.24].

Analog return's own offset at the `digital` dock on the shared `vss` trunk: nominal active 0.146 mV, nominal idle 0.000 mV, high active 0.168 mV, high idle 0.000 mV.

### Scenario: active, 1 MHz (DR-0003 ratified rate), uniform 0.25 activity

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 93.921 | 1.261 | 0.136 | 0.995 | 0.187 | 0.204 | 2.783 | 0.118 |
| ff_125C_3v60/rc-min | 91.377 | 1.227 | 0.133 | 0.968 | 0.182 | 0.204 | 2.713 | 0.115 |
| ff_125C_3v60/rc-nom | 92.517 | 1.242 | 0.134 | 0.980 | 0.185 | 0.204 | 2.745 | 0.117 |
| ff_n40C_3v60/rc-max | 86.000 | 0.825 | 0.089 | 0.651 | 0.123 | 0.146 | 1.833 | 0.077 |
| ff_n40C_3v60/rc-min | 83.616 | 0.802 | 0.087 | 0.633 | 0.119 | 0.146 | 1.786 | 0.075 |
| ff_n40C_3v60/rc-nom | 84.685 | 0.812 | 0.088 | 0.641 | 0.121 | 0.146 | 1.807 | 0.076 |
| ss_125C_3v00/rc-max | 71.270 | 0.957 | 0.103 | 0.755 | 0.142 | 0.204 | 2.161 | 0.090 |
| ss_125C_3v00/rc-min | 69.509 | 0.933 | 0.101 | 0.736 | 0.139 | 0.204 | 2.113 | 0.088 |
| ss_125C_3v00/rc-nom | 70.299 | 0.944 | 0.102 | 0.745 | 0.140 | 0.204 | 2.135 | 0.089 |
| ss_n40C_3v00/rc-max | 66.650 | 0.639 | 0.069 | 0.504 | 0.095 | 0.146 | 1.453 | 0.060 |
| ss_n40C_3v00/rc-min | 64.969 | 0.623 | 0.067 | 0.491 | 0.093 | 0.146 | 1.420 | 0.058 |
| ss_n40C_3v00/rc-nom | 65.724 | 0.630 | 0.068 | 0.497 | 0.094 | 0.146 | 1.435 | 0.059 |
| tt_025C_3v30/rc-max | 77.115 | 0.740 | 0.080 | 0.583 | 0.110 | 0.146 | 1.658 | 0.069 |
| tt_025C_3v30/rc-min | 75.087 | 0.720 | 0.078 | 0.568 | 0.107 | 0.146 | 1.619 | 0.068 |
| tt_025C_3v30/rc-nom | 75.998 | 0.729 | 0.079 | 0.575 | 0.108 | 0.146 | 1.636 | 0.068 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 93.921 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 1.941 + internal 1.272, vss external 1.633 + internal 1.251 + analog share 0.236 = **6.332 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 0.137 mV.

Worst per-corner estimate: 2.783 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.9637-3.6286 V. Against the 33.000 mV yardstick: **not material**.

### Scenario: idle, leakage only

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 2.105 | 0.028 | 0.003 | 0.022 | 0.004 | 0.000 | 0.058 | 0.003 |
| ff_125C_3v60/rc-min | 2.105 | 0.028 | 0.003 | 0.022 | 0.004 | 0.000 | 0.058 | 0.003 |
| ff_125C_3v60/rc-nom | 2.105 | 0.028 | 0.003 | 0.022 | 0.004 | 0.000 | 0.058 | 0.003 |
| ff_n40C_3v60/rc-max | 0.070 | 0.001 | 0.000 | 0.001 | 0.000 | 0.000 | 0.001 | 0.000 |
| ff_n40C_3v60/rc-min | 0.070 | 0.001 | 0.000 | 0.001 | 0.000 | 0.000 | 0.001 | 0.000 |
| ff_n40C_3v60/rc-nom | 0.070 | 0.001 | 0.000 | 0.001 | 0.000 | 0.000 | 0.001 | 0.000 |
| ss_125C_3v00/rc-max | 0.716 | 0.010 | 0.001 | 0.008 | 0.001 | 0.000 | 0.020 | 0.001 |
| ss_125C_3v00/rc-min | 0.716 | 0.010 | 0.001 | 0.008 | 0.001 | 0.000 | 0.020 | 0.001 |
| ss_125C_3v00/rc-nom | 0.716 | 0.010 | 0.001 | 0.008 | 0.001 | 0.000 | 0.020 | 0.001 |
| ss_n40C_3v00/rc-max | 0.056 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 |
| ss_n40C_3v00/rc-min | 0.056 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 |
| ss_n40C_3v00/rc-nom | 0.056 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 |
| tt_025C_3v30/rc-max | 0.065 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 |
| tt_025C_3v30/rc-min | 0.065 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 |
| tt_025C_3v30/rc-nom | 0.065 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 2.105 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 0.044 + internal 0.029, vss external 0.037 + internal 0.028 + analog share 0.000 = **0.137 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 0.003 mV.

Worst per-corner estimate: 0.058 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.9699-3.6300 V. Against the 33.000 mV yardstick: **not material**.

### Scenario: stress, 20 MHz (place-and-route clock constraint; informational)

Estimate per corner -- nominal resistance, uniform allocation, derated to the corner's own temperature (mV):

| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int | vss analog share | local collapse | shift at analog taps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff_125C_3v60/rc-max | 1838.416 | 24.682 | 2.667 | 19.471 | 3.667 | 0.204 | 50.691 | 2.316 |
| ff_125C_3v60/rc-min | 1787.547 | 23.999 | 2.593 | 18.932 | 3.566 | 0.204 | 49.294 | 2.252 |
| ff_125C_3v60/rc-nom | 1810.330 | 24.305 | 2.627 | 19.173 | 3.611 | 0.204 | 49.920 | 2.281 |
| ff_n40C_3v60/rc-max | 1718.686 | 16.482 | 1.781 | 13.002 | 2.449 | 0.146 | 33.859 | 1.547 |
| ff_n40C_3v60/rc-min | 1670.996 | 16.024 | 1.732 | 12.641 | 2.381 | 0.146 | 32.924 | 1.504 |
| ff_n40C_3v60/rc-nom | 1692.378 | 16.229 | 1.754 | 12.803 | 2.411 | 0.146 | 33.343 | 1.523 |
| ss_125C_3v00/rc-max | 1411.798 | 18.954 | 2.048 | 14.953 | 2.816 | 0.204 | 38.975 | 1.779 |
| ss_125C_3v00/rc-min | 1376.575 | 18.481 | 1.997 | 14.579 | 2.746 | 0.204 | 38.008 | 1.734 |
| ss_125C_3v00/rc-nom | 1392.383 | 18.694 | 2.020 | 14.747 | 2.777 | 0.204 | 38.442 | 1.754 |
| ss_n40C_3v00/rc-max | 1331.926 | 12.773 | 1.380 | 10.076 | 1.898 | 0.146 | 26.273 | 1.199 |
| ss_n40C_3v00/rc-min | 1298.314 | 12.451 | 1.345 | 9.822 | 1.850 | 0.146 | 25.613 | 1.168 |
| ss_n40C_3v00/rc-nom | 1313.407 | 12.595 | 1.361 | 9.936 | 1.871 | 0.146 | 25.909 | 1.182 |
| tt_025C_3v30/rc-max | 1541.062 | 14.778 | 1.597 | 11.658 | 2.196 | 0.146 | 30.375 | 1.387 |
| tt_025C_3v30/rc-min | 1500.515 | 14.390 | 1.555 | 11.352 | 2.138 | 0.146 | 29.580 | 1.350 |
| tt_025C_3v30/rc-nom | 1518.716 | 14.564 | 1.574 | 11.489 | 2.164 | 0.146 | 29.937 | 1.367 |

**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x 1.40 temperature derating x the family's largest current, 1838.416 uA at ff_125C_3v60/rc-max, allocation-free): vddd external 37.987 + internal 24.889, vss external 31.964 + internal 24.486 + analog share 0.236 = **119.562 mV** local supply collapse; shift the digital load adds at the analog `vss` taps <= 2.677 mV.

Worst per-corner estimate: 50.691 mV at ff_125C_3v60/rc-max. Effective local supply over the 2.97-3.63 V pin envelope: 2.8504-3.6044 V. Against the 33.000 mV yardstick: **MATERIAL (informational: not a ratified operating rate)**.

### The shared `vss` return, analog side

`vss_trunk_ir_drop.py`'s own conservative bound (analog load only, nominal sheet): 23.136 mV. Adding the digital load's active-rate shift bound at the analog taps (0.137 mV): 23.272 mV against 33.000 mV.

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
