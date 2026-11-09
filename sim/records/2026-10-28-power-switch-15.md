---
record: 2026-10-28-power-switch-15
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
  path: sim/records/raw/2026-10-28-power-switch-15/
  files:
    - corner.cir  sha256:02dfc0826d870fac516831f7f784c316778d2b1763f473c02404d99318f97d8e
    - ngspice.log  sha256:5e3a73b687c7493d375125fc5de85f2c16eb7bcb1f36fb9d7eb833af8f1c9d78
    - report-unit.json  sha256:4567bb54d6fcf8351b10f4abea481f5f66fcc52986728b012c0ac09e5cc1e358
wall_time: 1.918s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.570648e-03
- `droop_v_100um_b`: 9.153659e-02
- `droop_v_200um_a`: 2.283963e-03
- `droop_v_200um_b`: 4.521512e-02
- `droop_v_400um_a`: 1.141641e-03
- `droop_v_400um_b`: 2.247350e-02
- `droop_v_800um_a`: 5.707358e-04
- `droop_v_800um_b`: 1.120374e-02
- `ron_ohm_100um_a`: 4.726627e+01
- `ron_ohm_100um_b`: 4.835531e+01
- `ron_ohm_200um_a`: 2.361905e+01
- `ron_ohm_200um_b`: 2.388543e+01
- `ron_ohm_400um_a`: 1.180601e+01
- `ron_ohm_400um_b`: 1.187190e+01
- `ron_ohm_800um_a`: 5.902128e+00
- `ron_ohm_800um_b`: 5.918513e+00
- `p_loss_w_100um_a`: 4.419817e-07
- `p_loss_w_100um_b`: 1.732788e-04
- `p_loss_w_200um_a`: 2.208592e-07
- `p_loss_w_200um_b`: 8.559222e-05
- `p_loss_w_400um_a`: 1.103967e-07
- `p_loss_w_400um_b`: 4.254234e-05
- `p_loss_w_800um_a`: 5.519015e-08
- `p_loss_w_800um_b`: 2.120869e-05
- `ileak_a_100um`: 9.244555e-09
- `ileak_a_200um`: 1.848911e-08
- `ileak_a_400um`: 3.697822e-08
- `ileak_a_800um`: 7.395644e-08
- `i_stack_a`: 3.680871e-08
- `v_stack_v`: 1.263827e-02
- `i_ungated_a`: 1.669241e-06
- `stack_reduction_x`: 4.534908e+01
- `ipk_a_50pf_10ns`: 4.451043e-02
- `t_settle_s_50pf_10ns`: 8.535750e-09
- `vfin_v_50pf_10ns`: 3.299980e+00
- `ipk_a_200pf_10ns`: 8.463027e-02
- `t_settle_s_200pf_10ns`: 1.640229e-08
- `vfin_v_200pf_10ns`: 3.299980e+00
- `ipk_a_50pf_1000ns`: 2.774061e-03
- `t_settle_s_50pf_1000ns`: 2.533682e-07
- `vfin_v_50pf_1000ns`: 3.299980e+00
- `ipk_a_200pf_1000ns`: 7.020802e-03
- `t_settle_s_200pf_1000ns`: 3.300202e-07
- `vfin_v_200pf_1000ns`: 3.299980e+00

At this corner the 400 um switch has 11.87 ohm on-resistance at the 20 MHz bound load, leaks 36.978 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 36.809 nA (ungated reference 1669.2 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ff/125/3.30   # single-point probe
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
