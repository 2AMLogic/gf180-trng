---
record: 2026-11-05-ro-ring11-ring2-pex-attempt-02
date: 2026-11-05T08:15:00Z
status: valid

testbench:
  path: sim/tb/ro-ring11-ring2-pex/tb_ro_ring11_ring2_pex.sp
  sha: 1a1715579a17b123f26d41da2d1fb329a994e48b
netlist:
  path: sim/tb/ro-ring11-ring2-pex/ro_ring11_ring2_schematic.spice (schematic side); layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds extracted by the run (extracted side)
  sha: 8732ca7a2eaac5f236a61c57deeb09ee1eef1d47 (schematic DUT); 906ff2d7291ec1048ff720ac907f35f9487617db (GDS)
request:
  path: sim/tb/ro-ring11-ring2-pex/request.json
  sha: 6df21da2c702072b3cd9674bb3abd1535be894f8
repo_commit: e9f41e3d

pdk: gf180mcuD, open_pdks f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7 (search root ~/.ciel; a second install under ~/.volare was skipped by klt's first-match rule)
tool:
  klt: 0.9.0 client (probe, NOT the DR-0026 producer pin 0.6.0; klayout 0.30.10), fleet runner klt 0.9.0
  platform: Linux-7.0.0-1014-aws-x86_64 (client); fleet m7i.4xlarge spot, ami-04591566329422a44, ngspice 46

corner:
  process: tt, ff, ss
  voltage: 2.97 / 3.30 / 3.63 V
  temperature: -40 / 27 / 125
  grid: 27 corners, schematic and extracted sides (54 units), all measured

analysis:
  type: tran (deterministic)
  tstop: 1300n
  tstep: 10p
  runs: 54 of 54 grid units measured
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-11-05-ro-ring11-ring2-pex-attempt-02/
  files:
    - klt-pex-response-0.9.0.json  sha256:402c6e6a28f097c4a2adee5f5471e59b96fa2ac9cd4c109df50312f6e677af53
    - pex-extracted-netlist.spice  sha256:25835ccfb419970b26ce53280ea86562720cd33165ea4335095d64a389cffc6c
    - publish-stderr.txt  sha256:8d062857940c617c00c49e728822445039527db4a05cddfaacfbf119de93382c
wall_time: ~2 min per side (submit to collect)
---

## Result

**Outcome: MEASURED, NOT PUBLISHED (pin decision pending).** Under a klt 0.9.0
client against the klt 0.9.0 fleet runner, the full 27-corner paired ring2
campaign ran through the batch backend and measured every row on both sides.
The attempt-01 transport failure (DUT `.include` not staged, runner skew) did
not recur. The publisher then refused, as designed: `response is from klt
'0.9.0', not the producer pin 0.6.0`. Nothing was written under
`signoff/evidence/`. The result below is a probe, not published evidence.

| side | fleet job | state | job exit | elapsed |
|---|---|---|---|---|
| schematic | `klt-sim-e1ff14c3076d` | done | 0 | 83 s |
| extracted | `klt-sim-95ebbc6f1444` | done | 0 | 58 s |

Envelope: `status` pass, `corner_count` 27, `passed` 81, `failed` 0,
`errored` 0, `schematic_failed` 0, `backend_failure` null,
`pin_count_mismatch`, `flat_dut_mismatch` and `pin_order_mismatch` null.
`body_bias.status` is `unbiased` (23 devices; 11 anonymous floating PMOS
well nets, the known #339/#411 limitation). `model_mismatch` reports only the
schematic's hierarchical subcircuits against the flat extraction.

Extracted versus schematic, across the 27 corners (`delta_pct`; the rows
carry no limits, so a row's `pass` means "measured on both sides"):

| row | delta_pct range |
|---|---|
| `period_s` | 87.6 to 94.9 (extracted period roughly 1.9x the schematic's) |
| `supply_current_avg_a` | 3.4 to 15.9 |
| `ro_swing_v` | -5.6 to -4.9 |

At tt / 2.97 V / -40 C the periods are 5.318 ns (schematic) and 10.117 ns
(extracted). The large period shift is a measured diagnostic under the
floating-well limitation and extracted parasitics; this record makes no
silicon, entropy or timing claim and tunes no limit.

## Why it is not published

`signoff/check.py` `KLT_PIN` is 0.6.0, the publishers write and check
`producer_build` against it, and DR-0026 requires every restated pin site to
agree. Publishing this 0.9.0 envelope needs a ratified decision about which
pin covers it (a ring2-only producer build, or a global bump that would move
the producer of the older append-only reports). That choice is routed to the
operator, not made by the builder. The raw response is kept here, but a
published envelope should be produced under the ratified pin.

The `--check-source` and `--check` fixture validations passed before the run.
`python3 signoff/check.py` exits 1 on this host independent of this change: the
host `klt` is 0.9.1.dev17, not the 0.8.0 grader pin, so the T1 verdict of
record reads as stale.

## How to reproduce

```sh
export KLT="uvx --from klayout-tools==0.9.0 --with klayout==0.30.10 klt"
python3 sim/tb/ro-ring11-pex/build_dut.py --ring ring2 --check-source
python3 sim/tb/ro-ring11-pex/build_dut.py --ring ring2 --check
python3 signoff/publish_item7_analog.py --ring ring2 --backend batch   # refuses at the pin check
```

---

Append-only: never edit or delete this file.
