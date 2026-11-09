---
record: 2026-10-28-power-switch-33
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
  path: sim/records/raw/2026-10-28-power-switch-33/
  files:
    - corner.cir  sha256:a326e5b56c0e28d100e784c5313c5417e584d197dc7a4adfc9723e53567149fd
    - ngspice.log  sha256:331236cbce5835527f958272823a21ca13a5aa5f3e2829f5dbf1b735f5a706e9
    - report-unit.json  sha256:0163594eb7419b2f77adc9ea904cc4b34adca913759189368cf459127781d77b
wall_time: 2.073s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 5.555203e-03
- `droop_v_100um_b`: 1.120608e-01
- `droop_v_200um_a`: 2.775442e-03
- `droop_v_200um_b`: 5.513637e-02
- `droop_v_400um_a`: 1.387182e-03
- `droop_v_400um_b`: 2.735375e-02
- `droop_v_800um_a`: 6.934565e-04
- `droop_v_800um_b`: 1.362433e-02
- `ron_ohm_100um_a`: 5.744780e+01
- `ron_ohm_100um_b`: 5.919745e+01
- `ron_ohm_200um_a`: 2.870157e+01
- `ron_ohm_200um_b`: 2.912645e+01
- `ron_ohm_400um_a`: 1.434521e+01
- `ron_ohm_400um_b`: 1.444995e+01
- `ron_ohm_800um_a`: 7.171215e+00
- `ron_ohm_800um_b`: 7.197217e+00
- `p_loss_w_100um_a`: 5.371881e-07
- `p_loss_w_100um_b`: 2.121311e-04
- `p_loss_w_200um_a`: 2.683852e-07
- `p_loss_w_200um_b`: 1.043731e-04
- `p_loss_w_400um_a`: 1.341405e-07
- `p_loss_w_400um_b`: 5.178064e-05
- `p_loss_w_800um_a`: 6.705725e-08
- `p_loss_w_800um_b`: 2.579086e-05
- `ileak_a_100um`: 1.667350e-10
- `ileak_a_200um`: 3.334699e-10
- `ileak_a_400um`: 6.669398e-10
- `ileak_a_800um`: 1.333880e-09
- `i_stack_a`: 6.673040e-10
- `v_stack_v`: 3.437336e-04
- `i_ungated_a`: 9.493508e-07
- `stack_reduction_x`: 1.422666e+03
- `ipk_a_50pf_10ns`: 4.144707e-02
- `t_settle_s_50pf_10ns`: 9.800494e-09
- `vfin_v_50pf_10ns`: 3.299986e+00
- `ipk_a_200pf_10ns`: 7.301792e-02
- `t_settle_s_200pf_10ns`: 1.934323e-08
- `vfin_v_200pf_10ns`: 3.299986e+00
- `ipk_a_50pf_1000ns`: 2.653071e-03
- `t_settle_s_50pf_1000ns`: 3.281158e-07
- `vfin_v_50pf_1000ns`: 3.299986e+00
- `ipk_a_200pf_1000ns`: 6.613561e-03
- `t_settle_s_200pf_1000ns`: 4.111897e-07
- `vfin_v_200pf_1000ns`: 3.299986e+00

At this corner the 400 um switch has 14.45 ohm on-resistance at the 20 MHz bound load, leaks 0.667 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.667 nA (ungated reference 949.4 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only fs/125/3.30   # single-point probe
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
