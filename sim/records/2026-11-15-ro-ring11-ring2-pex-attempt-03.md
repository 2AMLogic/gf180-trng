---
record: 2026-11-15-ro-ring11-ring2-pex-attempt-03
date: 2026-11-15T08:15:30Z
status: valid

testbench:
  path: sim/tb/ro-ring11-ring2-pex/tb_ro_ring11_ring2_pex.sp
  sha: 9bc227b3ac5d1b24eade68628b04b16b56c94e01
netlist:
  path: sim/tb/ro-ring11-ring2-pex/ro_ring11_ring2_schematic.spice (schematic side); layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds extracted by the run (extracted side)
  sha: 0ac3e33ffe8ba38e7b9cb254ff03556ac9e9b3a0 (schematic DUT); a5ed6f8b59c086ab69a2f19ed3b2b1c314cf90de (GDS)
request:
  path: sim/tb/ro-ring11-ring2-pex/request.json
  sha: c35ba3811a70c5d5cc76034cd6e5e0f7ac273594
repo_commit: dd30f2df

pdk: gf180mcuD, open_pdks f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7 (search root ~/.ciel; a second install under ~/.volare was skipped by klt's first-match rule)
tool:
  klt: 0.9.2 client, tagged release (uvx throwaway, klayout 0.30.10; DR-0026's 2026-11-09 amendment — no producer pin, the record names its release), fleet runner klt 0.9.0 (runner_compatibility: match)
  platform: Linux aws x86_64 (client); fleet us-east-1, profile batch-runner-submit, ngspice on the runner's own install (client provenance records /usr/bin/ngspice, see below)

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
  path: sim/records/raw/2026-11-15-ro-ring11-ring2-pex-attempt-03/
  files:
    - klt-pex-response-0.9.2.json  sha256:d063592b52f1b384cbc908e4c52ea49930abbec2a35d1f6c18672444009423a8
    - pex-extracted-netlist.spice  sha256:14b1b82bb648e5fcb7b034a6caeafff9fba72e711d6aeb04a61240dfafc77606
    - publish-stderr.txt  sha256:9e0e424efb5e04ca250dee3416da79a48a9cdf0b2d55b743b91a8ac6aad5d928
    - publish-stdout.txt  sha256:b019fd12093ed0ad7c9e46ea8a2c7d88d1b4db3cc4e0a1fee6e18befb67144b7
    - batch-receipt-schematic.json  sha256:59646c2acd80587615fa603f2a94a170181137d2f6a35adae7c13bec7b9a3aa5
    - batch-receipt-extracted.json  sha256:f6157591a9131e60bb86d89ac9884d274a98a2d2dfd03f31520ff85caabe88e8
wall_time: ~95 s per side (launch to done)
---

## Result

**Outcome: MEASURED AND PUBLISHED.** On the current inputs (the four blob SHAs
above, identical to `origin/main` at the run's `dd30f2df`), the full 27-corner
paired ring2 campaign ran through the batch backend and measured every row on
both sides, and the result is published under
`signoff/evidence/post-layout/ring2/` — the first ring2 comparison committed
in this repository.

| side | fleet job | state | job exit | elapsed |
|---|---|---|---|---|
| schematic | `klt-sim-98ef631d6e7f` | done | 0 | 93 s |
| extracted | `klt-sim-9260f9fe9352` | done | 0 | 93 s |

Envelope: `status` pass, `corner_count` 27, `passed` 81, `failed` 0,
`errored` 0, `unfinished` [], `schematic_failed` 0, `backend_failure` null,
`pin_count_mismatch`, `flat_dut_mismatch` and `pin_order_mismatch` null.
`body_bias.status` is `biased` (`unbiased_device_count` 0; no unbiased PMOS
body nets). The committed extraction has 23 `pfet_03v3` devices; each bulk
sits on a per-tap `vddr__t<N>` net tied to `vddr` through that tap's
parasitic resistance (e.g. `Rvddr_t3 vddr__t3 vddr 33.4`), which is the
#705/PR #826 tapped layout — the floating-well condition attempt-02 measured
is gone, as the 2026-11-15 corrections on #476 predicted. `model_mismatch`
reports only the schematic's hierarchical subcircuits against the flat
extraction.

Extracted versus schematic, across the 27 corners (`delta_pct`; the rows
carry no limits, so a row's `pass` means "measured on both sides"):

| row | delta_pct range |
|---|---|
| `period_s` | 113.685 to 130.846 (extracted period roughly 2.3x the schematic's) |
| `supply_current_avg_a` | 12.227 to 14.806 |
| `ro_swing_v` | -6.102 to -4.864 |

At tt / 2.97 V / -40 C the periods are 5.318 ns (schematic) and 12.224 ns
(extracted). Compared with attempt-02's envelope (87.6 to 94.9 % period
delta, floating wells), the period shift moved materially, on the tapped
layout and the current inputs. This remains a diagnostic: no silicon,
entropy or timing claim, and no limit was tuned.

## Publication

Published by `signoff/publish_item7_analog.py --ring ring2 --backend batch`
in the same invocation as the run (no `--allow-incomplete`; the publisher
refuses an incomplete verdict). Files:

| file | sha256 |
|---|---|
| `signoff/evidence/post-layout/ring2/ro_ring11_ring2.pex.json` | d063592b52f1b384cbc908e4c52ea49930abbec2a35d1f6c18672444009423a8 (byte-identical to the raw response above) |
| `signoff/evidence/post-layout/ring2/ro_ring11_ring2.extracted.spice` | 14b1b82bb648e5fcb7b034a6caeafff9fba72e711d6aeb04a61240dfafc77606 |
| `signoff/evidence/post-layout/ring2/publication.json` | `producer_build` "0.9.2" (tagged), `klayout_build` "0.30.10", `body_bias_status` "biased", `backend_requested` "batch" |

Not a manifest citation: `7.analog` stays ring1's and the manifest is
untouched. The verdict recorded in `publication.json` is recomputed by
`signoff/check.py` (step 1c') on every run.

## The discarded first submission

The campaign was submitted twice on 2026-11-15. The first submission (fleet
jobs `klt-sim-0cb2e0a56c6a` schematic / `klt-sim-44b94b8379b1` extracted,
same commit, same inputs, same producer build) also completed with all 54
units measured and the same published verdict, but its envelope was discarded
before commit: its `client_ngspice_binary` provenance named
`/home/ubuntu/.local/bin/ngspice`, and `sim/tools/verify_report_host_paths.py`
refuses a `/home/<user>/` path in tracked JSON under `signoff/`. The item7
publisher does not redact that field (only the combiner/sampler publisher
calls `redact_client_paths`), and editing the publisher or the checker is out
of scope for #476. The response file was overwritten in the run's scratch
directory before the problem was noticed, so its bytes are not retained.
The committed run is the resubmission with the client resolving `ngspice`
from `/usr/bin`; that field is informational (the batch runner reads its own
install), so it does not make the two runs different measurements.

## Fixture validation and environment notes

`python3 sim/tb/ro-ring11-pex/build_dut.py --ring ring2 --check-source` and
`--check` both exited 0 before submission. Both submissions went to the batch
backend only; the grid was not run locally. klt warned that the job's
conservative bound (16320 s) exceeds the fleet's 3600 s whole-job ceiling —
advisory only; both jobs finished in ~95 s, as in attempts 01/02. The host's
own `klt` (a `.dev` build) was not used and not modified; the client ran from
`uvx --from klayout-tools==0.9.2 --with klayout==0.30.10`.

## How to reproduce

```sh
export KLT="uvx --from klayout-tools==0.9.2 --with klayout==0.30.10 klt"
python3 sim/tb/ro-ring11-pex/build_dut.py --ring ring2 --check-source
python3 sim/tb/ro-ring11-pex/build_dut.py --ring ring2 --check
python3 signoff/publish_item7_analog.py --ring ring2 --backend batch
python3 signoff/check.py   # in an environment whose `klt` is the 0.8.0 grader pin
```

---

Append-only: never edit or delete this file.
