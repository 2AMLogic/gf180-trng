---
record: 2026-10-28-power-switch-11
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
  voltage: 2.970 V (nominal 3.3 V, -10%)
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
  path: sim/records/raw/2026-10-28-power-switch-11/
  files:
    - corner.cir  sha256:a1fcff28d7d2df12161b35c9fe13ade0a3b800d4fae0a7a52e24405e797e5571
    - ngspice.log  sha256:e34dac74768b51e8e6c979f59621ae4b9c9610e243b84ed637411f909e991b30
    - report-unit.json  sha256:f436707d92af219b5ccd53fb1f8fbd633131abed64c8297681081e9ae490c3dd
wall_time: 1.918s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.068974e-03
- `droop_v_100um_b`: 8.164518e-02
- `droop_v_200um_a`: 2.033176e-03
- `droop_v_200um_b`: 4.028762e-02
- `droop_v_400um_a`: 1.016261e-03
- `droop_v_400um_b`: 2.001448e-02
- `droop_v_800um_a`: 5.080487e-04
- `droop_v_800um_b`: 9.975433e-03
- `ron_ohm_100um_a`: 4.207833e+01
- `ron_ohm_100um_b`: 4.313005e+01
- `ron_ohm_200um_a`: 2.102561e+01
- `ron_ohm_200um_b`: 2.128242e+01
- `ron_ohm_400um_a`: 1.050942e+01
- `ron_ohm_400um_b`: 1.057289e+01
- `ron_ohm_800um_a`: 5.253865e+00
- `ron_ohm_800um_b`: 5.269642e+00
- `p_loss_w_100um_a`: 3.934698e-07
- `p_loss_w_100um_b`: 1.545543e-04
- `p_loss_w_200um_a`: 1.966081e-07
- `p_loss_w_200um_b`: 7.626446e-05
- `p_loss_w_400um_a`: 9.827243e-08
- `p_loss_w_400um_b`: 3.788741e-05
- `p_loss_w_800um_a`: 4.912831e-08
- `p_loss_w_800um_b`: 1.888349e-05
- `ileak_a_100um`: 4.676578e-11
- `ileak_a_200um`: 9.353157e-11
- `ileak_a_400um`: 1.870631e-10
- `ileak_a_800um`: 3.741263e-10
- `i_stack_a`: 1.851413e-10
- `v_stack_v`: 1.492780e-02
- `i_ungated_a`: 9.309674e-09
- `stack_reduction_x`: 5.028416e+01
- `ipk_a_50pf_10ns`: 4.295838e-02
- `t_settle_s_50pf_10ns`: 8.612311e-09
- `vfin_v_50pf_10ns`: 2.970000e+00
- `ipk_a_200pf_10ns`: 8.209825e-02
- `t_settle_s_200pf_10ns`: 1.584274e-08
- `vfin_v_200pf_10ns`: 2.970000e+00
- `ipk_a_50pf_1000ns`: 2.651025e-03
- `t_settle_s_50pf_1000ns`: 3.033524e-07
- `vfin_v_50pf_1000ns`: 2.970000e+00
- `ipk_a_200pf_1000ns`: 6.685580e-03
- `t_settle_s_200pf_1000ns`: 3.751238e-07
- `vfin_v_200pf_1000ns`: 2.970000e+00

At this corner the 400 um switch has 10.57 ohm on-resistance at the 20 MHz bound load, leaks 0.187 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.185 nA (ungated reference 9.3 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ff/27/2.97   # single-point probe
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
