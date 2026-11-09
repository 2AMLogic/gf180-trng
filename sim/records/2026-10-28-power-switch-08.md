---
record: 2026-10-28-power-switch-08
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
  - libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  klt: 0.8.1.dev511+gbbe05037064a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: tt
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
  path: sim/records/raw/2026-10-28-power-switch-08/
  files:
    - corner.cir  sha256:732bfa5210ffbb02aa6cf1bf871e8a9b432c3c797c3bf9b7871763e9cc815c4d
    - ngspice.log  sha256:c438d1c13cf8cf4da6ef8005c2cff60d0f237a9ec3b40ed0fed0659e58acab7a
    - report-unit.json  sha256:25e81baa12c53cca7da6c19f1288e6a4bdb07ef2019ba773847f9e2c1e56bb0a
wall_time: 1.872s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.030701e-03
- `droop_v_100um_b`: 8.052354e-02
- `droop_v_200um_a`: 2.014276e-03
- `droop_v_200um_b`: 3.982845e-02
- `droop_v_400um_a`: 1.006870e-03
- `droop_v_400um_b`: 1.980881e-02
- `droop_v_800um_a`: 5.033680e-04
- `droop_v_800um_b`: 9.878399e-03
- `ron_ohm_100um_a`: 4.168254e+01
- `ron_ohm_100um_b`: 4.253753e+01
- `ron_ohm_200um_a`: 2.083016e+01
- `ron_ohm_200um_b`: 2.103985e+01
- `ron_ohm_400um_a`: 1.041231e+01
- `ron_ohm_400um_b`: 1.046424e+01
- `ron_ohm_800um_a`: 5.205460e+00
- `ron_ohm_800um_b`: 5.218383e+00
- `p_loss_w_100um_a`: 3.897688e-07
- `p_loss_w_100um_b`: 1.524311e-04
- `p_loss_w_200um_a`: 1.947805e-07
- `p_loss_w_200um_b`: 7.539525e-05
- `p_loss_w_400um_a`: 9.736432e-08
- `p_loss_w_400um_b`: 3.749807e-05
- `p_loss_w_800um_a`: 4.867568e-08
- `p_loss_w_800um_b`: 1.869981e-05
- `ileak_a_100um`: 5.546928e-11
- `ileak_a_200um`: 1.109386e-10
- `ileak_a_400um`: 2.218771e-10
- `ileak_a_800um`: 4.437543e-10
- `i_stack_a`: 1.226354e-10
- `v_stack_v`: 7.365995e-01
- `i_ungated_a`: 1.108032e-09
- `stack_reduction_x`: 9.035177e+00
- `ipk_a_50pf_10ns`: 4.471360e-02
- `t_settle_s_50pf_10ns`: 8.036258e-09
- `vfin_v_50pf_10ns`: 3.630000e+00
- `ipk_a_200pf_10ns`: 8.395527e-02
- `t_settle_s_200pf_10ns`: 1.447091e-08
- `vfin_v_200pf_10ns`: 3.630000e+00
- `ipk_a_50pf_1000ns`: 2.918266e-03
- `t_settle_s_50pf_1000ns`: 2.922411e-07
- `vfin_v_50pf_1000ns`: 3.630000e+00
- `ipk_a_200pf_1000ns`: 7.209354e-03
- `t_settle_s_200pf_1000ns`: 3.574541e-07
- `vfin_v_200pf_1000ns`: 3.630000e+00

At this corner the 400 um switch has 10.46 ohm on-resistance at the 20 MHz bound load, leaks 0.222 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.123 nA (ungated reference 1.1 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only tt/27/3.63   # single-point probe
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
