---
record: 2026-10-28-power-switch-18
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
  path: sim/records/raw/2026-10-28-power-switch-18/
  files:
    - corner.cir  sha256:21859fec55bc874e971702b5832f90fd909745d41eec392dcbff3b9e597c9471
    - ngspice.log  sha256:b90cdd0d9a60a548b376e792d4c976ab85905c396e5de3029494ebdd2e22a380
    - report-unit.json  sha256:79198ebfeedd39a0fc28c026465b86bd0efa1a8de8da9fbfd7afe71458e3a411
wall_time: 1.877s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.321049e-03
- `droop_v_100um_b`: 8.625549e-02
- `droop_v_200um_a`: 2.159417e-03
- `droop_v_200um_b`: 4.268176e-02
- `droop_v_400um_a`: 1.079432e-03
- `droop_v_400um_b`: 2.123229e-02
- `droop_v_800um_a`: 5.396469e-04
- `droop_v_800um_b`: 1.058935e-02
- `ron_ohm_100um_a`: 4.468510e+01
- `ron_ohm_100um_b`: 4.556550e+01
- `ron_ohm_200um_a`: 2.233110e+01
- `ron_ohm_200um_b`: 2.254715e+01
- `ron_ohm_400um_a`: 1.116269e+01
- `ron_ohm_400um_b`: 1.121621e+01
- `ron_ohm_800um_a`: 5.580630e+00
- `ron_ohm_800um_b`: 5.593951e+00
- `p_loss_w_100um_a`: 4.178454e-07
- `p_loss_w_100um_b`: 1.632816e-04
- `p_loss_w_200um_a`: 2.088156e-07
- `p_loss_w_200um_b`: 8.079657e-05
- `p_loss_w_400um_a`: 1.043811e-07
- `p_loss_w_400um_b`: 4.019273e-05
- `p_loss_w_800um_a`: 5.218386e-08
- `p_loss_w_800um_b`: 2.004564e-05
- `ileak_a_100um`: 1.047696e-08
- `ileak_a_200um`: 2.095391e-08
- `ileak_a_400um`: 4.190782e-08
- `ileak_a_800um`: 8.381564e-08
- `i_stack_a`: 4.166642e-08
- `v_stack_v`: 1.454575e-02
- `i_ungated_a`: 2.179693e-06
- `stack_reduction_x`: 5.231294e+01
- `ipk_a_50pf_10ns`: 5.004522e-02
- `t_settle_s_50pf_10ns`: 8.211888e-09
- `vfin_v_50pf_10ns`: 3.629976e+00
- `ipk_a_200pf_10ns`: 9.506162e-02
- `t_settle_s_200pf_10ns`: 1.573471e-08
- `vfin_v_200pf_10ns`: 3.629976e+00
- `ipk_a_50pf_1000ns`: 3.148461e-03
- `t_settle_s_50pf_1000ns`: 2.368116e-07
- `vfin_v_50pf_1000ns`: 3.629976e+00
- `ipk_a_200pf_1000ns`: 7.928969e-03
- `t_settle_s_200pf_1000ns`: 3.109473e-07
- `vfin_v_200pf_1000ns`: 3.629976e+00

At this corner the 400 um switch has 11.22 ohm on-resistance at the 20 MHz bound load, leaks 41.908 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 41.666 nA (ungated reference 2179.7 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ff/125/3.63   # single-point probe
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
