---
record: 2026-10-28-power-switch-34
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
  - libs.tech/ngspice/sm141064.ngspice (sections: fs bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  klt: 0.8.1.dev511+gbbe05037064a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: fs
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
  path: sim/records/raw/2026-10-28-power-switch-34/
  files:
    - corner.cir  sha256:7a4717947283e2c2bfc801ee89919b646862b4f7b8fe9b95383f5b105de4f4ef
    - ngspice.log  sha256:63df3913abd29ee070c37127d234147ddea4c9b83b8d4031955af3c8632df501
    - report-unit.json  sha256:8067ebde22ad0e8a8139023e1772b0cb5db42468d5156709a419bda80db36ff5
wall_time: 2.001s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 3.659086e-03
- `droop_v_100um_b`: 7.312372e-02
- `droop_v_200um_a`: 1.828552e-03
- `droop_v_200um_b`: 3.616204e-02
- `droop_v_400um_a`: 9.140283e-04
- `droop_v_400um_b`: 1.798375e-02
- `droop_v_800um_a`: 4.569523e-04
- `droop_v_800um_b`: 8.967877e-03
- `ron_ohm_100um_a`: 3.783956e+01
- `ron_ohm_100um_b`: 3.862849e+01
- `ron_ohm_200um_a`: 1.890953e+01
- `ron_ohm_200um_b`: 1.910303e+01
- `ron_ohm_400um_a`: 9.452205e+00
- `ron_ohm_400um_b`: 9.500130e+00
- `ron_ohm_800um_a`: 4.725463e+00
- `ron_ohm_800um_b`: 4.737389e+00
- `p_loss_w_100um_a`: 3.538336e-07
- `p_loss_w_100um_b`: 1.384232e-04
- `p_loss_w_200um_a`: 1.768209e-07
- `p_loss_w_200um_b`: 6.845474e-05
- `p_loss_w_400um_a`: 8.838653e-08
- `p_loss_w_400um_b`: 3.404323e-05
- `p_loss_w_800um_a`: 4.418729e-08
- `p_loss_w_800um_b`: 1.697619e-05
- `ileak_a_100um`: 5.048181e-11
- `ileak_a_200um`: 1.009636e-10
- `ileak_a_400um`: 2.019272e-10
- `ileak_a_800um`: 4.038545e-10
- `i_stack_a`: 9.390841e-11
- `v_stack_v`: 1.289441e+00
- `i_ungated_a`: 2.838909e-10
- `stack_reduction_x`: 3.023062e+00
- `ipk_a_50pf_10ns`: 4.026777e-02
- `t_settle_s_50pf_10ns`: 7.747083e-09
- `vfin_v_50pf_10ns`: 3.630000e+00
- `ipk_a_200pf_10ns`: 7.510100e-02
- `t_settle_s_200pf_10ns`: 1.317507e-08
- `vfin_v_200pf_10ns`: 3.630000e+00
- `ipk_a_50pf_1000ns`: 2.704844e-03
- `t_settle_s_50pf_1000ns`: 3.284826e-07
- `vfin_v_50pf_1000ns`: 3.630000e+00
- `ipk_a_200pf_1000ns`: 6.592970e-03
- `t_settle_s_200pf_1000ns`: 3.856844e-07
- `vfin_v_200pf_1000ns`: 3.630000e+00

At this corner the 400 um switch has 9.50 ohm on-resistance at the 20 MHz bound load, leaks 0.202 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.094 nA (ungated reference 0.3 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only fs/-40/3.63   # single-point probe
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
