---
record: 2026-10-28-power-switch-32
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
  path: sim/records/raw/2026-10-28-power-switch-32/
  files:
    - corner.cir  sha256:a94cc5faca170e9eb32d1a30be9e086c908f844f1393c0789efa94c8780129b8
    - ngspice.log  sha256:e76bc711068b7f72bd45a70f6de2c802dcdd42a372942957171912059a7e5ad4
    - report-unit.json  sha256:bf81353dabb9017c9cb67b160d52bfdabdde2ca22fe3ce5c9b404518a72f95bf
wall_time: 2.058s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.622299e-03
- `droop_v_100um_b`: 9.297251e-02
- `droop_v_200um_a`: 2.309519e-03
- `droop_v_200um_b`: 4.581690e-02
- `droop_v_400um_a`: 1.154353e-03
- `droop_v_400um_b`: 2.274716e-02
- `droop_v_800um_a`: 5.770747e-04
- `droop_v_800um_b`: 1.133397e-02
- `ron_ohm_100um_a`: 4.780041e+01
- `ron_ohm_100um_b`: 4.911384e+01
- `ron_ohm_200um_a`: 2.388334e+01
- `ron_ohm_200um_b`: 2.420333e+01
- `ron_ohm_400um_a`: 1.193746e+01
- `ron_ohm_400um_b`: 1.201646e+01
- `ron_ohm_800um_a`: 5.967681e+00
- `ron_ohm_800um_b`: 5.987307e+00
- `p_loss_w_100um_a`: 4.469764e-07
- `p_loss_w_100um_b`: 1.759970e-04
- `p_loss_w_200um_a`: 2.233305e-07
- `p_loss_w_200um_b`: 8.673139e-05
- `p_loss_w_400um_a`: 1.116259e-07
- `p_loss_w_400um_b`: 4.306037e-05
- `p_loss_w_800um_a`: 5.580312e-08
- `p_loss_w_800um_b`: 2.145521e-05
- `ileak_a_100um`: 3.780551e-11
- `ileak_a_200um`: 7.561103e-11
- `ileak_a_400um`: 1.512221e-10
- `ileak_a_800um`: 3.024441e-10
- `i_stack_a`: 1.481915e-10
- `v_stack_v`: 2.584306e-02
- `i_ungated_a`: 6.267304e-09
- `stack_reduction_x`: 4.229193e+01
- `ipk_a_50pf_10ns`: 4.530982e-02
- `t_settle_s_50pf_10ns`: 9.403390e-09
- `vfin_v_50pf_10ns`: 3.300000e+00
- `ipk_a_200pf_10ns`: 8.169204e-02
- `t_settle_s_200pf_10ns`: 1.762206e-08
- `vfin_v_200pf_10ns`: 3.300000e+00
- `ipk_a_50pf_1000ns`: 2.897885e-03
- `t_settle_s_50pf_1000ns`: 3.529939e-07
- `vfin_v_50pf_1000ns`: 3.300000e+00
- `ipk_a_200pf_1000ns`: 7.180126e-03
- `t_settle_s_200pf_1000ns`: 4.279323e-07
- `vfin_v_200pf_1000ns`: 3.300000e+00

At this corner the 400 um switch has 12.02 ohm on-resistance at the 20 MHz bound load, leaks 0.151 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.148 nA (ungated reference 6.3 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only fs/27/3.30   # single-point probe
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
