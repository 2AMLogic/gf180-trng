---
record: 2026-10-28-power-switch-17
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
  - libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  klt: 0.8.1.dev511+gbbe05037064a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: ff
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 27

analysis:
  type: tran (deterministic)
  tstop: 3.5u
  tstep: 100p (print step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-10-28-power-switch-17/
  files:
    - corner.cir  sha256:89c58a633c5b6c7cda7c9fc82b4345de92bc74c08013a9997973b52da6efd960
    - ngspice.log  sha256:41669238f6e95edb7873a033bcffabc0c31353e3eba18564493941a9a96d0b42
    - report-unit.json  sha256:cbc680c7229b0249566d7fa1f8909d671e329733396d5a1072c584128ad7779f
wall_time: 1.881s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 3.628272e-03
- `droop_v_100um_b`: 7.229325e-02
- `droop_v_200um_a`: 1.813292e-03
- `droop_v_200um_b`: 3.580836e-02
- `droop_v_400um_a`: 9.064350e-04
- `droop_v_400um_b`: 1.782159e-02
- `droop_v_800um_a`: 4.531648e-04
- `droop_v_800um_b`: 8.890382e-03
- `ron_ohm_100um_a`: 3.752091e+01
- `ron_ohm_100um_b`: 3.818978e+01
- `ron_ohm_200um_a`: 1.875172e+01
- `ron_ohm_200um_b`: 1.891620e+01
- `ron_ohm_400um_a`: 9.373681e+00
- `ron_ohm_400um_b`: 9.414467e+00
- `ron_ohm_800um_a`: 4.686296e+00
- `ron_ohm_800um_b`: 4.696451e+00
- `p_loss_w_100um_a`: 3.508539e-07
- `p_loss_w_100um_b`: 1.368511e-04
- `p_loss_w_200um_a`: 1.753453e-07
- `p_loss_w_200um_b`: 6.778523e-05
- `p_loss_w_400um_a`: 8.765226e-08
- `p_loss_w_400um_b`: 3.373626e-05
- `p_loss_w_800um_a`: 4.382104e-08
- `p_loss_w_800um_b`: 1.682949e-05
- `ileak_a_100um`: 8.619996e-11
- `ileak_a_200um`: 1.723999e-10
- `ileak_a_400um`: 3.447998e-10
- `ileak_a_800um`: 6.895997e-10
- `i_stack_a`: 3.303709e-10
- `v_stack_v`: 3.301138e-02
- `i_ungated_a`: 1.759963e-08
- `stack_reduction_x`: 5.327234e+01
- `ipk_a_50pf_10ns`: 5.476480e-02
- `t_settle_s_50pf_10ns`: 7.874114e-09
- `vfin_v_50pf_10ns`: 3.630000e+00
- `ipk_a_200pf_10ns`: 1.040341e-01
- `t_settle_s_200pf_10ns`: 1.447850e-08
- `vfin_v_200pf_10ns`: 3.630000e+00
- `ipk_a_50pf_1000ns`: 3.436232e-03
- `t_settle_s_50pf_1000ns`: 2.598683e-07
- `vfin_v_50pf_1000ns`: 3.630000e+00
- `ipk_a_200pf_1000ns`: 8.603865e-03
- `t_settle_s_200pf_1000ns`: 3.268946e-07
- `vfin_v_200pf_1000ns`: 3.630000e+00

At this corner the 400 um switch has 9.41 ohm on-resistance at the 20 MHz bound load, leaks 0.345 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.330 nA (ungated reference 17.6 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ff/27/3.63   # single-point probe
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
