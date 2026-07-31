* corner-sanity-nfet-id -- NMOS Id(sat) vs process corner (harness bring-up)
*
* This is deliberately the harness's own correctness guardrail (see
* sim/README.md and this testbench's acceptance criteria): if a corner
* selection is ever silently ignored, this Id measurement stops moving
* across corners and sim/selftest.sh's corner-sanity check fails loudly
* instead of contaminating downstream evidence.
vdd vdd 0 dc vdd_val
vg  g   0 dc vdd_val
xn  d g 0 0 nfet_03v3 w=10u l=0.28u
rload d vdd 1k
