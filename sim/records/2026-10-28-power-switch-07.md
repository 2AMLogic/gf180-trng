---
record: 2026-10-28-power-switch-07
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
  path: sim/records/raw/2026-10-28-power-switch-07/
  files:
    - corner.cir  sha256:bcf85d3610c96d90cee871693431948ff23ed3f7419e3c632e969446803494c6
    - ngspice.log  sha256:ed5e240ab8aa3cb31792155e6b8de2b69bd0b074ad0881b75f657b54c8544b0a
    - report-unit.json  sha256:354df82e2d6facf7c6f9a0831f6788f94f3b0a5ac3fd9bd2b93b195d296b7f83
wall_time: 1.87s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 3.407628e-03
- `droop_v_100um_b`: 6.794874e-02
- `droop_v_200um_a`: 1.702987e-03
- `droop_v_200um_b`: 3.364269e-02
- `droop_v_400um_a`: 8.512872e-04
- `droop_v_400um_b`: 1.674042e-02
- `droop_v_800um_a`: 4.255920e-04
- `droop_v_800um_b`: 8.350217e-03
- `ron_ohm_100um_a`: 3.523918e+01
- `ron_ohm_100um_b`: 3.589474e+01
- `ron_ohm_200um_a`: 1.761104e+01
- `ron_ohm_200um_b`: 1.777216e+01
- `ron_ohm_400um_a`: 8.803383e+00
- `ron_ohm_400um_b`: 8.843327e+00
- `ron_ohm_800um_a`: 4.401158e+00
- `ron_ohm_800um_b`: 4.411103e+00
- `p_loss_w_100um_a`: 3.295177e-07
- `p_loss_w_100um_b`: 1.286270e-04
- `p_loss_w_200um_a`: 1.646789e-07
- `p_loss_w_200um_b`: 6.368561e-05
- `p_loss_w_400um_a`: 8.231947e-08
- `p_loss_w_400um_b`: 3.168961e-05
- `p_loss_w_800um_a`: 4.115475e-08
- `p_loss_w_800um_b`: 1.580696e-05
- `ileak_a_100um`: 5.464241e-11
- `ileak_a_200um`: 1.092848e-10
- `ileak_a_400um`: 2.185696e-10
- `ileak_a_800um`: 4.371393e-10
- `i_stack_a`: 9.378912e-11
- `v_stack_v`: 1.304859e+00
- `i_ungated_a`: 2.608900e-10
- `stack_reduction_x`: 2.781666e+00
- `ipk_a_50pf_10ns`: 4.140256e-02
- `t_settle_s_50pf_10ns`: 7.315116e-09
- `vfin_v_50pf_10ns`: 3.630000e+00
- `ipk_a_200pf_10ns`: 7.735000e-02
- `t_settle_s_200pf_10ns`: 1.244127e-08
- `vfin_v_200pf_10ns`: 3.630000e+00
- `ipk_a_50pf_1000ns`: 2.751222e-03
- `t_settle_s_50pf_1000ns`: 3.007834e-07
- `vfin_v_50pf_1000ns`: 3.630000e+00
- `ipk_a_200pf_1000ns`: 6.738005e-03
- `t_settle_s_200pf_1000ns`: 3.560829e-07
- `vfin_v_200pf_1000ns`: 3.630000e+00

At this corner the 400 um switch has 8.84 ohm on-resistance at the 20 MHz bound load, leaks 0.219 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.094 nA (ungated reference 0.3 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only tt/-40/3.63   # single-point probe
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
