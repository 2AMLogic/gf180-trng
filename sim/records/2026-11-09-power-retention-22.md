---
record: 2026-11-09-power-retention-22
date: 2026-11-09T19:34:01Z
status: valid

testbench:
  path: sim/tb/power-retention/tb_power_retention.sp
  sha: ae15ce3bbf1c34b753dbcedd85030b852787e4d4
netlist:
  path: sim/tb/power-retention/retention_cells.spice
  sha: 3079699eca062b5df387b4abd66fdd17386633ff
  also: design/power_switch.spice sha f14b87ff4bb74a439a5eb3cd5a2f6ffe3f616d44
repo_commit: d225f324b198153ce302440a06093b16a4cb9843-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  klt: 0.9.2.dev385+gfafa69b5f3b6 (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: ss
  voltage: 3.300 V (nominal 3.3 V)
  temperature: -40

analysis:
  type: tran (deterministic)
  tstop: 30u
  tstep: 1n (print step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-11-09-power-retention-22/
  files:
    - corner.cir  sha256:45f54c9297222ce8b59344c871fe1bed843d3d99608fc169abefc7f4aa0387eb
    - ngspice.log  sha256:44a13b871e677c9b25c09552fb0a5608a53ad9ee45951d07aeb810dd4ccd3271
    - report-unit.json  sha256:8db48df4c15b29a50d72ea0dd86226a58f3d1e27a66921332263ea1dff2ce496
wall_time: 57.699s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-92142462ad47, klt-sim-834838d72625, klt-sim-55172570b9f0). Retained bits are read as 1 above half the supply, in the order ctrl_en, ctrl_out_mode_raw, fail_rct, fail_apt, fail_ring; the pattern written is 10101. The idle readings are averages over the windows in the deck header.

- `i_ao_static_a`: 9.341493e-10
- `i_ao_clk_a`: 7.599813e-08
- `i_sw_a`: 8.485444e-11
- `v_rail_v`: 1.183879e+00
- `i_digital_idle_a`: 1.019004e-09
- `z_off_v`: 6.596843e-09
- `z_on_v`: 3.300000e+00
- `retained_ok`: 1.000000e+00
- `idle_hold_ok`: 1.000000e+00
- `control_lost`: 1.000000e+00
- `clamp_ok`: 1.000000e+00
- bits_qg_pre: `10101`
- bits_qg_post: `10101`
- bits_qb_post: `00000`
- bits_qi: `10101`

At this corner the retained bits read `10101` after the forced power cycle (written `10101`), the free-running-clock control reads `00000`, and with the switch off the always-on set draws 0.934 nA beside 0.085 nA for the switch and its leakage-equivalent load.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_retention.py emit --check
python3 sim/tools/power_retention.py run --outdir DIR --backend batch   # via klt sim; the request sets batch.capacity_wait_s
python3 sim/tools/power_retention.py run --outdir DIR --backend local --only ss/-40/3.30   # single-point probe
python3 sim/tools/power_retention.py analyze DIR/grid.report.json
```

## Caveats

- Pre-layout, schematic-level: the cells and the switch are netlists, with no extracted wiring.
- The gated domain's logic is ideal sources (pattern, hold feedback, isolation inputs); the digital load behind the switch is the #707 leakage-equivalent NFET, not the cells.
- The rail is forced in the function group; rail decay is an open item (`design/power-intent.md`).
- The retained flops are plain `dffrnq_1` on the always-on rail: the library has no retention flop.
- The raw deck and log have this host's absolute paths replaced by `<repo>` and `~` before hashing.

---

Written by `sim/tools/power_retention.py record`. Append-only: never edit or delete this file.
