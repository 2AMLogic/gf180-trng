---
record: 2026-10-28-power-switch-24
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
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-10-28-power-switch-24/
  files:
    - corner.cir  sha256:365bed44ef60185f164aee842b3d4e42931cca0e2ffe984f74bf995059a2970f
    - ngspice.log  sha256:1eef41d06fb052706ac2e29e572a0cf187bc5a5d8a30cf295b3174ab027c1a43
    - report-unit.json  sha256:a32feb912e8ee3806d7e507e193ff21fc420224d2e8ddef47f4d8c8b2358315f
wall_time: 1.869s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 5.765961e-03
- `droop_v_100um_b`: 1.165876e-01
- `droop_v_200um_a`: 2.880568e-03
- `droop_v_200um_b`: 5.728989e-02
- `droop_v_400um_a`: 1.439682e-03
- `droop_v_400um_b`: 2.840484e-02
- `droop_v_800um_a`: 7.196910e-04
- `droop_v_800um_b`: 1.414367e-02
- `ron_ohm_100um_a`: 5.962731e+01
- `ron_ohm_100um_b`: 6.158882e+01
- `ron_ohm_200um_a`: 2.978871e+01
- `ron_ohm_200um_b`: 3.026407e+01
- `ron_ohm_400um_a`: 1.488813e+01
- `ron_ohm_400um_b`: 1.500520e+01
- `ron_ohm_800um_a`: 7.442513e+00
- `ron_ohm_800um_b`: 7.471562e+00
- `p_loss_w_100um_a`: 5.575684e-07
- `p_loss_w_100um_b`: 2.207004e-04
- `p_loss_w_200um_a`: 2.785510e-07
- `p_loss_w_200um_b`: 1.084498e-04
- `p_loss_w_400um_a`: 1.392173e-07
- `p_loss_w_400um_b`: 5.377036e-05
- `p_loss_w_800um_a`: 6.959412e-08
- `p_loss_w_800um_b`: 2.677396e-05
- `ileak_a_100um`: 1.135157e-10
- `ileak_a_200um`: 2.270314e-10
- `ileak_a_400um`: 4.540627e-10
- `ileak_a_800um`: 9.081255e-10
- `i_stack_a`: 4.521826e-10
- `v_stack_v`: 8.690623e-03
- `i_ungated_a`: 1.858566e-08
- `stack_reduction_x`: 4.110211e+01
- `ipk_a_50pf_10ns`: 4.055326e-02
- `t_settle_s_50pf_10ns`: 1.003277e-08
- `vfin_v_50pf_10ns`: 3.300000e+00
- `ipk_a_200pf_10ns`: 6.938470e-02
- `t_settle_s_200pf_10ns`: 2.000521e-08
- `vfin_v_200pf_10ns`: 3.300000e+00
- `ipk_a_50pf_1000ns`: 2.610751e-03
- `t_settle_s_50pf_1000ns`: 3.395792e-07
- `vfin_v_50pf_1000ns`: 3.300000e+00
- `ipk_a_200pf_1000ns`: 6.491151e-03
- `t_settle_s_200pf_1000ns`: 4.239961e-07
- `vfin_v_200pf_1000ns`: 3.300000e+00

At this corner the 400 um switch has 15.01 ohm on-resistance at the 20 MHz bound load, leaks 0.454 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.452 nA (ungated reference 18.6 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ss/125/3.30   # single-point probe
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
