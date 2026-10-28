---
record: 2026-10-28-power-switch-09
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
  path: sim/records/raw/2026-10-28-power-switch-09/
  files:
    - corner.cir  sha256:8fda9af90212adc746ac0360bc6698d9110a8ffa44de32484ba5dc6dc404fcda
    - ngspice.log  sha256:53ef731f7f8fdf9ca1e546cdd9d60755fa974d621158c01739d705c0c1bbeb27
    - report-unit.json  sha256:712ddd9aa4f7301e9ed620d62f0af7f5bc9fc9119dc7c9ffe78b774537bcbc5e
wall_time: 1.923s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.820033e-03
- `droop_v_100um_b`: 9.650207e-02
- `droop_v_200um_a`: 2.408599e-03
- `droop_v_200um_b`: 4.767559e-02
- `droop_v_400um_a`: 1.203946e-03
- `droop_v_400um_b`: 2.369828e-02
- `droop_v_800um_a`: 6.018844e-04
- `droop_v_800um_b`: 1.181478e-02
- `ron_ohm_100um_a`: 4.984522e+01
- `ron_ohm_100um_b`: 5.097838e+01
- `ron_ohm_200um_a`: 2.490795e+01
- `ron_ohm_200um_b`: 2.518520e+01
- `ron_ohm_400um_a`: 1.245032e+01
- `ron_ohm_400um_b`: 1.251890e+01
- `ron_ohm_800um_a`: 6.224244e+00
- `ron_ohm_800um_b`: 6.241302e+00
- `p_loss_w_100um_a`: 4.660972e-07
- `p_loss_w_100um_b`: 1.826784e-04
- `p_loss_w_200um_a`: 2.329115e-07
- `p_loss_w_200um_b`: 9.024990e-05
- `p_loss_w_400um_a`: 1.164215e-07
- `p_loss_w_400um_b`: 4.486085e-05
- `p_loss_w_800um_a`: 5.820222e-08
- `p_loss_w_800um_b`: 2.236539e-05
- `ileak_a_100um`: 9.153203e-10
- `ileak_a_200um`: 1.830641e-09
- `ileak_a_400um`: 3.661281e-09
- `ileak_a_800um`: 7.322562e-09
- `i_stack_a`: 3.646936e-09
- `v_stack_v`: 9.519402e-03
- `i_ungated_a`: 2.148227e-07
- `stack_reduction_x`: 5.890498e+01
- `ipk_a_50pf_10ns`: 4.803128e-02
- `t_settle_s_50pf_10ns`: 8.902200e-09
- `vfin_v_50pf_10ns`: 3.629997e+00
- `ipk_a_200pf_10ns`: 9.063034e-02
- `t_settle_s_200pf_10ns`: 1.719379e-08
- `vfin_v_200pf_10ns`: 3.629997e+00
- `ipk_a_50pf_1000ns`: 3.063001e-03
- `t_settle_s_50pf_1000ns`: 2.765413e-07
- `vfin_v_50pf_1000ns`: 3.629997e+00
- `ipk_a_200pf_1000ns`: 7.647598e-03
- `t_settle_s_200pf_1000ns`: 3.543826e-07
- `vfin_v_200pf_1000ns`: 3.629997e+00

At this corner the 400 um switch has 12.52 ohm on-resistance at the 20 MHz bound load, leaks 3.661 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 3.647 nA (ungated reference 214.8 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only tt/125/3.63   # single-point probe
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
