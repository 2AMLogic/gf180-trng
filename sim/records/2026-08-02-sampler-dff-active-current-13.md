---
record: 2026-08-02-sampler-dff-active-current-13
date: 2026-08-02T10:07:06Z
status: valid

testbench:
  path: sim/tb/sampler-dff-active-current/tb_sampler_dff_active_current.sp
  sha: 9b564038d61935a3e32fb39d5c3893c79b735fc0
netlist:
  path: design/sampler_core.spice
  sha: 50bc082dc2798c8b98e4ced8ebb70432549aa2ec
repo_commit: 599badd86cb8bb05c22c7691fe9a318477143989-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 27

analysis:
  type: tran
  tstop: 60n
  tstep: 20p (print step; ngspice's own LTE sets the actual solver step). 20p against a 2 ns D period is 100 samples per D cycle -- ample for a charge integrator read at fixed window boundaries, which depends on the solver's accuracy at those instants and not on the print grid.
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-02-sampler-dff-active-current-13/
  files:
    - ff_27c_2.97v.spice  sha256:76996e46c34f8329382d07b7c066b4db1dd0f4f38fc28e495f04dc97bcf75f97
    - ff_27c_2.97v.log  sha256:878d5b3eb536a678cf94cda99e8da2ccb2754ef098d522348e8fb4a35619c6a5
wall_time: 13.9s
---

## Result

- `q_d_shut_c`: 5.500000e-20
- `q_d_open_c`: 7.499417e-15
- `e_d_shut_j`: 1.633500e-19
- `e_d_open_j`: 2.227327e-14
- `q_clkcyc_xsv_c`: 6.907220e-15
- `e_clkcyc_xsv_j`: 2.051444e-14
- `q_clkcyc_xsb_resid_c`: 8.834667e-16
- `q_cyc_xsb_total_c`: 8.337760e-14
- `q_d_shut_xsv_c`: 6.833333e-20
- `q_d_open_xsv_c`: 8.000000e-20
- `vdd_mean_v`: 2.97
- `qv_pre_v`: 1.647818e-08
- `qv_post_v`: 2.97
- `qb_pre_v`: -1.912486e-07
- `qb_post_v`: 2.97

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-active-current --corners ff --temps 27 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 2.97 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- This record reports ENERGY AND CHARGE PER EVENT, not an average current or a power. It deliberately does not state a sampler power, because the rate that turns one into the other -- xo's transition rate -- is a property of the entropy array, is corner-dependent, and is measured per corner by sim/tb/ro-array-core-pvt-q/ (`xo_trans_per_s`, 3.1e8 to 9.6e8 /s across the 27-point grid). sim/tools/power_rollup.py combines the two; nothing here should be quoted as a power on its own.
- The clock runs at 50 MHz in simulation, 500x the ratified 1 MHz sample clock, so one whole clock period fits in a short transient. The recorded quantity is charge per CYCLE, which is a switching-energy quantity and is rate-independent once nodes settle between events -- the same argument sim/tb/ro-array-core-power/ relies on for `e_cycle_r1_j`. What that argument does NOT cover is any current that is genuinely rate-independent-per-second rather than per-event, i.e. static leakage: over a real 1 us clock period leakage contributes ~1000x more charge than over this deck's 20 ns one, and it is deliberately not in this record. Idle/static leakage is sim/tb/sampler-core-idle-leakage/'s measurement and enters the rollup from there.
- `q_clkcyc_xsv_c` is a direct measurement over exactly one clock period on the instance whose D is tied to vdd, so nothing is subtracted from it. `q_clkcyc_xsb_resid_c` IS a residual -- one whole-cycle charge minus 11 open-phase and 10 shut-phase per-transition charges -- and 21 transitions at roughly 8 fC each dwarf the ~8 fC clock term it is trying to expose, so a one-per-cent systematic in the per-transition figure moves the residual by its own magnitude. Treat it as an ORDER-OF-MAGNITUDE BOUND on xsb's clock-cycle charge (it establishes that xsb's is not far larger than xsv's), never as a measurement of it. Nothing depends on the distinction: at the ratified 1 MHz sample clock both flops' clock terms together are tens of nanowatts, five orders of magnitude below the per-D-transition term, which is why the rollup applies xsv's directly measured value to both.
- D on xsb is an idealised 1.0 GHz square wave (2 ns period, 1.0e9 transitions/s), chosen just above the grid maximum xo reaches so the per-event settling assumption is tested at a harder rate than the real one. It is not the real xo: xo's duty cycle, its rise/fall asymmetry, and the fact that its transitions are not uniformly spaced are not characterised by this testbench. The per-event decomposition is what makes the rate idealisation harmless for the rollup; it would not be harmless if this deck reported an average current.
- D on xsv is tied to its own branch's vdd, mirroring design/sampler_core.spice exactly (`xsv vdd clk rst_n raw_valid vdd vss sampler_dff` -- D and the supply pin are the same net). Its captured value therefore never changes, so `q_clkcyc_xsv_c` is the clock-cycle cost of a flop whose output does NOT toggle. A flop whose Q does toggle pays an additional output-node switching charge on those cycles; for xsb that is a per-CLOCK-cycle term at 1 MHz, i.e. six orders of magnitude below the per-D-transition term, which is why this deck does not separate it out.
- Reset is released once at 8 ns, between clock edges and 12 ns before the first rising edge, because this deck's job is the running state. It says nothing about reset-release phase against the clock -- that is sim/tb/sampler-dff-reset-clocked/'s measurement -- and nothing about the reset window's own current, which is sim/tb/sampler-dff-reset-current-{xsv,xsb}/'s.
- Characterises the two sampler_dff CELLS only, in isolation from ro_array_core, consistent with every other sampler-dff-* testbench. It is not a measurement of sampler_core's total supply current; the rings and the XOR tree are sim/tb/ro-array-core-power/ and sim/tb/ro-array-core-pvt-q/, and combining them is the rollup's job, not this deck's.
- The branch-splitting sense sources (vr1/vr2) report charge delivered INTO the branch as a negative quantity under ngspice's own branch-current sign convention -- the construction and sign behaviour design/README.md's 'Reading the recorded currents' documents. The measure expressions negate accordingly, so every recorded value here is a positive magnitude.
- `qv_pre_v`/`qv_post_v` and `qb_pre_v`/`qb_post_v` are functional witnesses, not power figures: they bracket the two real state changes in the run. `qv` must be at its reset value before the 20 ns edge and at the rail after it (xsv captures its tied-high D once and then holds), and `qb` must be low before the 41 ns edge and high after it (D is low at the 20 ns edge and high at the 41 ns one -- see the testbench header on why the clock period is 21 ns). A cell that 'passed' this deck by being stuck and never capturing would fail these four.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
