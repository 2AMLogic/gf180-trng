---
record: 2026-10-28-power-switch-43
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
  temperature: -40

analysis:
  type: tran (deterministic)
  tstop: 3.5u
  tstep: 100p (print step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-10-28-power-switch-43/
  files:
    - corner.cir  sha256:04506bbc2fa5149d5c0791c13e6d7bc715712f08e6321e2ee77cb2ae2c091f67
    - ngspice.log  sha256:e87959d9d452b2a20b96471042ddce2deb5d83e3f59c7c0f8080cc69c2466303
    - report-unit.json  sha256:058895152bb1dd5adaea71fe2fa85cd6c73372d0cf63811a03c06626826158a5
wall_time: 1.936s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 3.175109e-03
- `droop_v_100um_b`: 6.320905e-02
- `droop_v_200um_a`: 1.586851e-03
- `droop_v_200um_b`: 3.132344e-02
- `droop_v_400um_a`: 7.932498e-04
- `droop_v_400um_b`: 1.559298e-02
- `droop_v_800um_a`: 3.965810e-04
- `droop_v_800um_b`: 7.779491e-03
- `ron_ohm_100um_a`: 3.283464e+01
- `ron_ohm_100um_b`: 3.339094e+01
- `ron_ohm_200um_a`: 1.641004e+01
- `ron_ohm_200um_b`: 1.654699e+01
- `ron_ohm_400um_a`: 8.203203e+00
- `ron_ohm_400um_b`: 8.237180e+00
- `ron_ohm_800um_a`: 4.101148e+00
- `ron_ohm_800um_b`: 4.109610e+00
- `p_loss_w_100um_a`: 3.070331e-07
- `p_loss_w_100um_b`: 1.196547e-04
- `p_loss_w_200um_a`: 1.534485e-07
- `p_loss_w_200um_b`: 5.929528e-05
- `p_loss_w_400um_a`: 7.670725e-08
- `p_loss_w_400um_b`: 2.951752e-05
- `p_loss_w_800um_a`: 3.834938e-08
- `p_loss_w_800um_b`: 1.472658e-05
- `ileak_a_100um`: 6.006787e-11
- `ileak_a_200um`: 1.201357e-10
- `ileak_a_400um`: 2.402715e-10
- `ileak_a_800um`: 4.805429e-10
- `i_stack_a`: 9.359308e-11
- `v_stack_v`: 1.306571e+00
- `i_ungated_a`: 2.592621e-10
- `stack_reduction_x`: 2.770099e+00
- `ipk_a_50pf_10ns`: 4.262709e-02
- `t_settle_s_50pf_10ns`: 6.902094e-09
- `vfin_v_50pf_10ns`: 3.630000e+00
- `ipk_a_200pf_10ns`: 7.982166e-02
- `t_settle_s_200pf_10ns`: 1.179449e-08
- `vfin_v_200pf_10ns`: 3.630000e+00
- `ipk_a_50pf_1000ns`: 2.804369e-03
- `t_settle_s_50pf_1000ns`: 2.731747e-07
- `vfin_v_50pf_1000ns`: 3.630000e+00
- `ipk_a_200pf_1000ns`: 6.902104e-03
- `t_settle_s_200pf_1000ns`: 3.267522e-07
- `vfin_v_200pf_1000ns`: 3.630000e+00

At this corner the 400 um switch has 8.24 ohm on-resistance at the 20 MHz bound load, leaks 0.240 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.094 nA (ungated reference 0.3 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only sf/-40/3.63   # single-point probe
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
