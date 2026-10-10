---
record: 2026-10-10-ro-ring11-ring2-pex-attempt-01
date: 2026-10-10T13:42:55Z
status: valid

testbench:
  path: sim/tb/ro-ring11-ring2-pex/tb_ro_ring11_ring2_pex.sp
  sha: 4ccd5aed8d7c43f7341ac09dbe6e9986755a8998
netlist:
  path: sim/tb/ro-ring11-ring2-pex/ro_ring11_ring2_schematic.spice (schematic side); layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds extracted by the run (extracted side)
  sha: 83cf3065dbf51cfe357b9cf4729f358b1b136f71 (schematic DUT); 857fb4d354a053ef6163615927d85a37b8cf273b (GDS)
request:
  path: sim/tb/ro-ring11-ring2-pex/request.json
  sha: 6cf91e5f2bd9f4692aeb94e0d8a04774f81bfb55
repo_commit: 75ae6ceb0e2a36bac7db5034104009f51bee8db7

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
tool:
  klt: 0.6.0 (client, DR-0026 producer pin; klayout 0.30.10), fleet runner klt 0.5.0
  platform: Linux-7.0.0-1014-aws-x86_64-with-glibc2.39

corner:
  process: tt, ff, ss -- NOT SIMULATED (27-point grid, both sides)
  voltage: 2.97 / 3.30 / 3.63 V -- NOT SIMULATED
  temperature: -40 / 27 / 125 -- NOT SIMULATED
  local debug probe: tt / 3.30 V / 27 C, extracted side only (see Result)

analysis:
  type: tran (deterministic)
  tstop: 1300n
  tstep: 10p
  runs: 0 of 54 grid units (27 corners x 2 sides) produced a measurement
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-10-10-ro-ring11-ring2-pex-attempt-01/
  files:
    - klt-pex-response-errored.json  sha256:e6b7d55c9a86289abcd8e2da23de1b9b35911069b03466940e3ee0020e1002ec
    - local-probe-tt-3v30-27c-report.json  sha256:cb5306806cee49109345b37612769c6720080fad427073915ef8e3cd72fa4112
    - local-probe-tt-3v30-27c-request.json  sha256:14fcf07b5b229a4edc6576b40d933afe55e88c87e6384f0cfb5c187b10ee31eb
    - pex-extracted-fleet-harness.log  sha256:a2212a0a956c2c54a2cc55c42d9b74c1011e59eab1901b5ba44f5b7669a9f554
    - pex-extracted-fleet-job.json  sha256:cd62f4536670eafc7417609b088757f3a333c7ef2e686c1bd411b2a580c069f2
    - pex-extracted-fleet-netlist.cir  sha256:282f9529fb8d29548157569b9d676b5c7019d6be40566ddc8a469ad99cfe882d
    - pex-extracted-fleet-report.json  sha256:e3e70e4aaf4fb1fd741ad89973573658e5847606233701365a29b22d7b6344b2
    - pex-extracted-fleet-status.json  sha256:9852d98099dafe90d398086618f1d752d587e8c593e2c06903089555dba9224c
    - pex-extracted-netlist.spice  sha256:4fc7769fb0429e7229bb43edab8447f5e7a002b0e4da629331895103e7e17bf0
    - pex-schematic-fleet-harness.log  sha256:21142ed39aaa3b2fbca5aa0520f64a080f732b703319321a3c12f65882c15a87
    - pex-schematic-fleet-job.json  sha256:cd62f4536670eafc7417609b088757f3a333c7ef2e686c1bd411b2a580c069f2
    - pex-schematic-fleet-netlist.cir  sha256:1a377116c2d3574590231aba6d617a5f4dee2202af5b03f99fa9315efebd5d6e
    - pex-schematic-fleet-report.json  sha256:c56f797405ba13c5d7f3772fbae3f1719a8fbfc9c8b4cfbc00c0a358118b5f24
    - pex-schematic-fleet-status.json  sha256:a36ec110af5f50d1a42294664fd253bba8aff4d992d6921e28fef1345cd8720b
    - probe-extracted-klt-sim-report.json  sha256:9527f9005f753f22dbdceeebd6e206696f97fa02ee78d47a3d2b92db56976602
    - probe-fleet-harness.log  sha256:c1ca7ea18d19826ce84ad189a3b2499a258b33f81ca54ed4419ee03d62e5f883
    - probe-fleet-inputs-netlist.cir  sha256:282f9529fb8d29548157569b9d676b5c7019d6be40566ddc8a469ad99cfe882d
    - probe-fleet-job.json  sha256:cd62f4536670eafc7417609b088757f3a333c7ef2e686c1bd411b2a580c069f2
    - probe-fleet-report.json  sha256:d568ac32a25cb9498c73f78355097187fc1984d94229e4b9b14ad896ce1e5598
    - probe-fleet-status.json  sha256:33b003ba5675928c4c47955c69995bb7a697e6c2e54d75aa7bc83a5ae8bca22a
    - publish-stderr.txt  sha256:215f8f176627a37010c2a4e852f6e3397aa0330fbaeb1583857aa5312f2c0069
wall_time: ~2 min (submit to collect, both sides); every fleet job exited after ~5 s
---

## Result

**Outcome: UNMEASURED (blocked on execution).** The 27-corner ring2 paired
campaign (#476) was submitted to the batch fleet once through the existing
publisher (`signoff/publish_item7_analog.py --ring ring2 --backend batch`).
The fleet accepted and ran both jobs, but none of the 54 grid units (27
corners x 2 sides) produced a measurement. The publisher printed
`klt pex failed (exit 4); nothing published`. No envelope or `publication.json`
was written under `signoff/evidence/post-layout/ring2/`. This record carries
no comparison, no delta and no verdict.

This was not a capacity refusal. Both jobs started on spot m6i.4xlarge
instances:

| side | fleet job | state | job exit | corners errored |
|---|---|---|---|---|
| schematic | `klt-sim-dc936de81e20` | failed | 4 | 27 / 27 |
| extracted | `klt-sim-4ccd9e4d8532` | failed | 4 | 27 / 27 |
| extracted (re-staged `klt sim` probe) | `klt-sim-a44d58085f30` | failed | 4 | 27 / 27 |

Every corner reports only `measurement '<row>' produced no value`, in about
0.3 s. The cause comes from the uploaded inputs, not from any diagnostic:

1. **The DUT `.include` is not shipped.** The klt 0.6.0 batch client uploads
   just two files, `inputs/netlist.cir` (the testbench body) and
   `inputs/request.json`. The testbench reaches its DUT through `.include`.
   On the schematic side that is the relative
   `ro_ring11_ring2_schematic.spice`; on the extracted side it is the
   absolute path of the `klt pex` `-o` netlist on the submitting host. On the
   fleet instance neither include resolves, so ngspice has no `xdut`
   subcircuit and no `.meas` row can fire. Staging a netlist's
   `.include` closure for batch/remote jobs was fixed upstream after 0.6.0
   (2AMLogic/klayout-tools#2485).
2. **Runner/client skew.** The fleet's runner reports klt 0.5.0
   (`provenance.klt_version` in each collected `report.json`). A 0.7.0 client
   (which stages includes) is refused by that runner as
   `batch_runner_version_mismatch` (see 2026-10-10-sampler-core-liveness-active-attempt-01),
   and the publisher refuses any envelope that is not from the 0.6.0 pin. So
   no client/runner pair available today can run this `.include`-based
   fixture on the fleet and still publish under the pin. This is tracked
   upstream in 2AMLogic/klayout-tools#2882 (fleet include failure, runner
   skew) and #2872 (a `klt pex` report drops the per-corner cause).

**The fixture itself simulates.** One single-corner local debug probe was run
(tt / 3.30 V / 27 C, extracted side only, the re-staged extracted request
narrowed to that one corner, `--backend local`, 14 s). It measured all three
rows: `period_s` 1.13889e-08, `supply_current_avg_a` -1.8094e-05,
`ro_swing_v` 3.23672. This only shows that the failure is in job transport,
not in the testbench or the extracted netlist. It is one side at one corner,
with no schematic counterpart and no delta. It is not a ring2 comparison
result and it is not published.

Pre-run validation passed under the pin: `build_dut.py --ring ring2
--check-source` (source sha256:d98785fe…), `build_dut.py --ring ring2
--check` (re-extraction: sizing, generated schematic identity and port
mapping current) and `signoff/check.py` (verdict of record current).

The 27-corner grid was **not** run as a local loop (shared-worker rule).
No reduced grid and no `--allow-incomplete` publication was made. The
`klt pex` `-o` netlist the run wrote is kept here as
`pex-extracted-netlist.spice` (its hash matches the envelope's
`extraction.netlist_sha256`) instead of under `signoff/evidence/`, because
nothing was published.

## How to reproduce

```sh
export KLT="uvx --from klayout-tools==0.6.0 --with klayout==0.30.10 klt"
python3 sim/tb/ro-ring11-pex/build_dut.py --ring ring2 --check-source
python3 sim/tb/ro-ring11-pex/build_dut.py --ring ring2 --check
python3 signoff/publish_item7_analog.py --ring ring2 --backend batch
```

`build_dut.py --check` runs bare `klt`. To have it use the pin, put a
pinned environment first on `PATH`, not the host's klt.

---

Append-only: never edit or delete this file.
