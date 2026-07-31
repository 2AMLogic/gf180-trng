* nfet-mismatch-seed -- NMOS Id under device mismatch (harness seed-control demo)
*
* Demonstrates the harness's stochastic-run contract: analysis_type "mc"
* requires a seed for every run (sim/README.md: "no seed, no evidence"),
* the harness sets it via ".option seed=<N>" (see sim/harness/runner.py),
* and re-running with the same seed reproduces the same measurement exactly.
vdd vdd 0 dc vdd_val
vg  g   0 dc vdd_val
xn  d g 0 0 nfet_03v3 w=1u l=0.28u
rload d vdd 10k
