---
record: 2026-10-28-power-switch-21
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
  - libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  klt: 0.8.1.dev511+gbbe05037064a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: ss
  voltage: 2.970 V (nominal 3.3 V, -10%)
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
  path: sim/records/raw/2026-10-28-power-switch-21/
  files:
    - corner.cir  sha256:825a2960516d04e97948f2ec66f566367341861d3ac5cc876c3af37afad784c5
    - ngspice.log  sha256:124b440fa8d1b88f9ba7691fc35217d8f607553d73fa1301c9f66482223cfc69
    - report-unit.json  sha256:b800dbf94d92693d5393d28ef49e57be8c139069a2f33ac81782ebb7e3dde224
wall_time: 1.878s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 6.274163e-03
- `droop_v_100um_b`: 1.278203e-01
- `droop_v_200um_a`: 3.133880e-03
- `droop_v_200um_b`: 6.255051e-02
- `droop_v_400um_a`: 1.566142e-03
- `droop_v_400um_b`: 3.095365e-02
- `droop_v_800um_a`: 7.828715e-04
- `droop_v_800um_b`: 1.539854e-02
- `ron_ohm_100um_a`: 6.488276e+01
- `ron_ohm_100um_b`: 6.752261e+01
- `ron_ohm_200um_a`: 3.240827e+01
- `ron_ohm_200um_b`: 3.304306e+01
- `ron_ohm_400um_a`: 1.619588e+01
- `ron_ohm_400um_b`: 1.635164e+01
- `ron_ohm_800um_a`: 8.095879e+00
- `ron_ohm_800um_b`: 8.134464e+00
- `p_loss_w_100um_a`: 6.067116e-07
- `p_loss_w_100um_b`: 2.419638e-04
- `p_loss_w_200um_a`: 3.030462e-07
- `p_loss_w_200um_b`: 1.184081e-04
- `p_loss_w_400um_a`: 1.514459e-07
- `p_loss_w_400um_b`: 5.859527e-05
- `p_loss_w_800um_a`: 7.570368e-08
- `p_loss_w_800um_b`: 2.914944e-05
- `ileak_a_100um`: 1.009289e-10
- `ileak_a_200um`: 2.018578e-10
- `ileak_a_400um`: 4.037156e-10
- `ileak_a_800um`: 8.074312e-10
- `i_stack_a`: 4.027574e-10
- `v_stack_v`: 7.665778e-03
- `i_ungated_a`: 1.518248e-08
- `stack_reduction_x`: 3.769633e+01
- `ipk_a_50pf_10ns`: 3.548500e-02
- `t_settle_s_50pf_10ns`: 1.053906e-08
- `vfin_v_50pf_10ns`: 2.970000e+00
- `ipk_a_200pf_10ns`: 5.726333e-02
- `t_settle_s_200pf_10ns`: 2.140767e-08
- `vfin_v_200pf_10ns`: 2.970000e+00
- `ipk_a_50pf_1000ns`: 2.264376e-03
- `t_settle_s_50pf_1000ns`: 3.680365e-07
- `vfin_v_50pf_1000ns`: 2.970000e+00
- `ipk_a_200pf_1000ns`: 5.660410e-03
- `t_settle_s_200pf_1000ns`: 4.556793e-07
- `vfin_v_200pf_1000ns`: 2.970000e+00

At this corner the 400 um switch has 16.35 ohm on-resistance at the 20 MHz bound load, leaks 0.404 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.403 nA (ungated reference 15.2 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ss/125/2.97   # single-point probe
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
