---
record: 2026-10-28-power-switch-02
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
  path: sim/records/raw/2026-10-28-power-switch-02/
  files:
    - corner.cir  sha256:46e8d86efe06dd6dc90570b63b9e166ab820be63ffe84091ce2a7e67d93c4841
    - ngspice.log  sha256:f347ccbf56c64255921a7068e6fff55a3f285d4b21b3fa84685bb774a26aaeda
    - report-unit.json  sha256:01a5bd542ee480b07675b6b9feac9b30f9481335949726d171ae0a4d345aa128
wall_time: 1.921s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.597089e-03
- `droop_v_100um_b`: 9.265755e-02
- `droop_v_200um_a`: 2.296804e-03
- `droop_v_200um_b`: 4.561001e-02
- `droop_v_400um_a`: 1.147968e-03
- `droop_v_400um_b`: 2.263237e-02
- `droop_v_800um_a`: 5.738754e-04
- `droop_v_800um_b`: 1.127386e-02
- `ron_ohm_100um_a`: 4.753970e+01
- `ron_ohm_100um_b`: 4.894746e+01
- `ron_ohm_200um_a`: 2.375185e+01
- `ron_ohm_200um_b`: 2.409404e+01
- `ron_ohm_400um_a`: 1.187144e+01
- `ron_ohm_400um_b`: 1.195582e+01
- `ron_ohm_800um_a`: 5.934596e+00
- `ron_ohm_800um_b`: 5.955551e+00
- `p_loss_w_100um_a`: 4.445385e-07
- `p_loss_w_100um_b`: 1.754007e-04
- `p_loss_w_200um_a`: 2.221010e-07
- `p_loss_w_200um_b`: 8.633975e-05
- `p_loss_w_400um_a`: 1.110085e-07
- `p_loss_w_400um_b`: 4.284307e-05
- `p_loss_w_800um_a`: 5.549375e-08
- `p_loss_w_800um_b`: 2.134141e-05
- `ileak_a_100um`: 3.197930e-11
- `ileak_a_200um`: 6.395861e-11
- `ileak_a_400um`: 1.279172e-10
- `ileak_a_800um`: 2.558344e-10
- `i_stack_a`: 9.883618e-11
- `v_stack_v`: 5.559560e-01
- `i_ungated_a`: 6.867324e-10
- `stack_reduction_x`: 6.948189e+00
- `ipk_a_50pf_10ns`: 3.525856e-02
- `t_settle_s_50pf_10ns`: 8.891839e-09
- `vfin_v_50pf_10ns`: 2.970000e+00
- `ipk_a_200pf_10ns`: 6.661421e-02
- `t_settle_s_200pf_10ns`: 1.611952e-08
- `vfin_v_200pf_10ns`: 2.970000e+00
- `ipk_a_50pf_1000ns`: 2.261596e-03
- `t_settle_s_50pf_1000ns`: 3.433582e-07
- `vfin_v_50pf_1000ns`: 2.970000e+00
- `ipk_a_200pf_1000ns`: 5.632530e-03
- `t_settle_s_200pf_1000ns`: 4.136924e-07
- `vfin_v_200pf_1000ns`: 2.970000e+00

At this corner the 400 um switch has 11.96 ohm on-resistance at the 20 MHz bound load, leaks 0.128 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.099 nA (ungated reference 0.7 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only tt/27/2.97   # single-point probe
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
