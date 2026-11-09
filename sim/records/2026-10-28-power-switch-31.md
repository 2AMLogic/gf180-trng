---
record: 2026-10-28-power-switch-31
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
  path: sim/records/raw/2026-10-28-power-switch-31/
  files:
    - corner.cir  sha256:f297da0fde7a1848f0410a4ba28853fbb426bb436b6e70bb5372b2bf20eedad0
    - ngspice.log  sha256:1f35352d8fbb313de43d65846367291f73c44ad645163d16cfa6043266ef54a9
    - report-unit.json  sha256:b2acf8a54336d68fe429820fc78f5a1605e7309237bb71705486ff485e2c577d
wall_time: 2.022s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 3.891146e-03
- `droop_v_100um_b`: 7.806917e-02
- `droop_v_200um_a`: 1.944323e-03
- `droop_v_200um_b`: 3.852533e-02
- `droop_v_400um_a`: 9.718497e-04
- `droop_v_400um_b`: 1.913945e-02
- `droop_v_800um_a`: 4.858469e-04
- `droop_v_800um_b`: 9.539414e-03
- `ron_ohm_100um_a`: 4.023936e+01
- `ron_ohm_100um_b`: 4.124098e+01
- `ron_ohm_200um_a`: 2.010676e+01
- `ron_ohm_200um_b`: 2.035147e+01
- `ron_ohm_400um_a`: 1.005015e+01
- `ron_ohm_400um_b`: 1.011065e+01
- `ron_ohm_800um_a`: 5.024270e+00
- `ron_ohm_800um_b`: 5.039310e+00
- `p_loss_w_100um_a`: 3.762739e-07
- `p_loss_w_100um_b`: 1.477849e-04
- `p_loss_w_200um_a`: 1.880161e-07
- `p_loss_w_200um_b`: 7.292845e-05
- `p_loss_w_400um_a`: 9.397787e-08
- `p_loss_w_400um_b`: 3.623099e-05
- `p_loss_w_800um_a`: 4.698140e-08
- `p_loss_w_800um_b`: 1.805811e-05
- `ileak_a_100um`: 3.769026e-11
- `ileak_a_200um`: 7.538053e-11
- `ileak_a_400um`: 1.507611e-10
- `ileak_a_800um`: 3.015221e-10
- `i_stack_a`: 8.492988e-11
- `v_stack_v`: 1.172036e+00
- `i_ungated_a`: 2.512246e-10
- `stack_reduction_x`: 2.958024e+00
- `ipk_a_50pf_10ns`: 3.570635e-02
- `t_settle_s_50pf_10ns`: 8.143895e-09
- `vfin_v_50pf_10ns`: 3.300000e+00
- `ipk_a_200pf_10ns`: 6.678493e-02
- `t_settle_s_200pf_10ns`: 1.381568e-08
- `vfin_v_200pf_10ns`: 3.300000e+00
- `ipk_a_50pf_1000ns`: 2.384477e-03
- `t_settle_s_50pf_1000ns`: 3.556746e-07
- `vfin_v_50pf_1000ns`: 3.300000e+00
- `ipk_a_200pf_1000ns`: 5.826208e-03
- `t_settle_s_200pf_1000ns`: 4.147159e-07
- `vfin_v_200pf_1000ns`: 3.300000e+00

At this corner the 400 um switch has 10.11 ohm on-resistance at the 20 MHz bound load, leaks 0.151 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.085 nA (ungated reference 0.3 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only fs/-40/3.30   # single-point probe
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
