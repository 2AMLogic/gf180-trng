---
record: 2026-10-28-power-switch-12
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
  path: sim/records/raw/2026-10-28-power-switch-12/
  files:
    - corner.cir  sha256:138375c75ecd38084bce4aa9586643a5f522cbd1806f7148be5e4a19d2f996fa
    - ngspice.log  sha256:0e3e8b9b39fb1eef9175effe5efa018f194b9483c730f0d1f3de5a034c67f6e4
    - report-unit.json  sha256:ecb2cf7508fb6743dcac6a75a2b62923d62a6de82c56d51915caa6fcd55314ca
wall_time: 1.924s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.887656e-03
- `droop_v_100um_b`: 9.832319e-02
- `droop_v_200um_a`: 2.442097e-03
- `droop_v_200um_b`: 4.844989e-02
- `droop_v_400um_a`: 1.220616e-03
- `droop_v_400um_b`: 2.405359e-02
- `droop_v_800um_a`: 6.102003e-04
- `droop_v_800um_b`: 1.198473e-02
- `ron_ohm_100um_a`: 5.054453e+01
- `ron_ohm_100um_b`: 5.194041e+01
- `ron_ohm_200um_a`: 2.525436e+01
- `ron_ohm_200um_b`: 2.559424e+01
- `ron_ohm_400um_a`: 1.262271e+01
- `ron_ohm_400um_b`: 1.270660e+01
- `ron_ohm_800um_a`: 6.310241e+00
- `ron_ohm_800um_b`: 6.331079e+00
- `p_loss_w_100um_a`: 4.726363e-07
- `p_loss_w_100um_b`: 1.861258e-04
- `p_loss_w_200um_a`: 2.361508e-07
- `p_loss_w_200um_b`: 9.171564e-05
- `p_loss_w_400um_a`: 1.180336e-07
- `p_loss_w_400um_b`: 4.553344e-05
- `p_loss_w_800um_a`: 5.900637e-08
- `p_loss_w_800um_b`: 2.268710e-05
- `ileak_a_100um`: 8.223546e-09
- `ileak_a_200um`: 1.644709e-08
- `ileak_a_400um`: 3.289419e-08
- `ileak_a_800um`: 6.578837e-08
- `i_stack_a`: 3.276727e-08
- `v_stack_v`: 1.110250e-02
- `i_ungated_a`: 1.302952e-06
- `stack_reduction_x`: 3.976382e+01
- `ipk_a_50pf_10ns`: 3.901941e-02
- `t_settle_s_50pf_10ns`: 8.921649e-09
- `vfin_v_50pf_10ns`: 2.969984e+00
- `ipk_a_200pf_10ns`: 7.403205e-02
- `t_settle_s_200pf_10ns`: 1.724035e-08
- `vfin_v_200pf_10ns`: 2.969984e+00
- `ipk_a_50pf_1000ns`: 2.405756e-03
- `t_settle_s_50pf_1000ns`: 2.732146e-07
- `vfin_v_50pf_1000ns`: 2.969984e+00
- `ipk_a_200pf_1000ns`: 6.126854e-03
- `t_settle_s_200pf_1000ns`: 3.528456e-07
- `vfin_v_200pf_1000ns`: 2.969984e+00

At this corner the 400 um switch has 12.71 ohm on-resistance at the 20 MHz bound load, leaks 32.894 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 32.767 nA (ungated reference 1303.0 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ff/125/2.97   # single-point probe
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
