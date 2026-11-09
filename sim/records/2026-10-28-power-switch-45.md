---
record: 2026-10-28-power-switch-45
date: 2026-10-28T07:25:25Z
status: valid

testbench:
  path: sim/tb/power-switch/tb_power_switch.sp
  sha: b23081dbb36fd553e491f76dd08dfc235286cc2d
netlist:
  path: design/power_switch.spice
  sha: f14b87ff4bb74a439a5eb3cd5a2f6ffe3f616d44
repo_commit: 18d24d110c54ae2309dcd6694ec581798a7e1c62-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - libs.tech/ngspice/sm141064.ngspice (sections: sf bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  klt: 0.8.1.dev511+gbbe05037064a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: sf
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 125

analysis:
  type: tran (deterministic)
  tstop: 3.5u
  tstep: 100p (print step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-10-28-power-switch-45/
  files:
    - corner.cir  sha256:5e4079a91c02a09f7db24464da0470d8b4571240b05db621f230e71d17793e87
    - ngspice.log  sha256:382dfe8a9da6d2a4e485fa963a4d214a16af8db584c0f525151035519ef8493e
    - report-unit.json  sha256:b66c7060abe14694beece6fae3fa464ebe7bd4abb666e6342058b956b0e64ea6
wall_time: 1.932s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.477168e-03
- `droop_v_100um_b`: 8.945428e-02
- `droop_v_200um_a`: 2.237384e-03
- `droop_v_200um_b`: 4.424263e-02
- `droop_v_400um_a`: 1.118392e-03
- `droop_v_400um_b`: 2.200350e-02
- `droop_v_800um_a`: 5.591212e-04
- `droop_v_800um_b`: 1.097269e-02
- `ron_ohm_100um_a`: 4.629956e+01
- `ron_ohm_100um_b`: 4.725530e+01
- `ron_ohm_200um_a`: 2.313737e+01
- `ron_ohm_200um_b`: 2.337170e+01
- `ron_ohm_400um_a`: 1.156559e+01
- `ron_ohm_400um_b`: 1.162361e+01
- `ron_ohm_800um_a`: 5.782019e+00
- `ron_ohm_800um_b`: 5.796458e+00
- `p_loss_w_100um_a`: 4.329421e-07
- `p_loss_w_100um_b`: 1.693370e-04
- `p_loss_w_200um_a`: 2.163550e-07
- `p_loss_w_200um_b`: 8.375131e-05
- `p_loss_w_400um_a`: 1.081485e-07
- `p_loss_w_400um_b`: 4.165263e-05
- `p_loss_w_800um_a`: 5.406702e-08
- `p_loss_w_800um_b`: 2.077131e-05
- `ileak_a_100um`: 5.673127e-09
- `ileak_a_200um`: 1.134625e-08
- `ileak_a_400um`: 2.269251e-08
- `ileak_a_800um`: 4.538502e-08
- `i_stack_a`: 1.223738e-08
- `v_stack_v`: 1.765787e+00
- `i_ungated_a`: 3.889400e-08
- `stack_reduction_x`: 3.178294e+00
- `ipk_a_50pf_10ns`: 2.935032e-02
- `t_settle_s_50pf_10ns`: 6.947561e-09
- `vfin_v_50pf_10ns`: 3.630000e+00
- `ipk_a_200pf_10ns`: 5.368707e-02
- `t_settle_s_200pf_10ns`: 1.256987e-08
- `vfin_v_200pf_10ns`: 3.630000e+00
- `ipk_a_50pf_1000ns`: 1.994879e-03
- `t_settle_s_50pf_1000ns`: 2.260826e-07
- `vfin_v_50pf_1000ns`: 3.630000e+00
- `ipk_a_200pf_1000ns`: 4.972496e-03
- `t_settle_s_200pf_1000ns`: 2.863463e-07
- `vfin_v_200pf_1000ns`: 3.630000e+00

At this corner the 400 um switch has 11.62 ohm on-resistance at the 20 MHz bound load, leaks 22.693 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 12.237 nA (ungated reference 38.9 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only sf/125/3.63   # single-point probe
python3 sim/tools/power_switch.py analyze DIR/grid.report.json
```

## Caveats

- Pre-layout, schematic-level: the switch is the netlist of `design/power_switch.spice`, with no extracted wiring, no well/tap resistance and no package or bond-wire inductance.
- The digital load is a leakage-equivalent off NFET (710 um = 71 x 10 um) and fixed DC currents, not the gate-level cells; the 50/200 pF rail capacitances are assumptions, not extractions. See the deck header.
- The static readings use the DC loads of the deck; instantaneous clock-edge current peaks are not modelled, so droop at a clock edge is bounded here only by the 20 MHz average load.
- Gate leakage of the digital cells and of the switch is not separated from channel leakage.
- The raw deck and log have this host's absolute paths replaced by `<repo>` and `~` before hashing.

---

Written by `sim/tools/power_switch.py record`. Append-only: never edit or delete this file.
