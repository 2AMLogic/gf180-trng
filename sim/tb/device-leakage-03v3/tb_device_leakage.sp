* device-leakage-03v3 -- off-state drain leakage per micron of gate width
*
* Purpose: give the block-level idle projection a MEASURED per-micron
* number instead of the textbook "0.1-1 nA/um at ff/125 C" range the
* Power row's idle figure has been argued from so far. Nothing in this
* repository had measured it.
*
* Two devices, each in its own off state at the full supply across it, each
* with a 0 V source in series with the drain acting as an ammeter:
*
*   nfet_03v3   Vgs = 0, Vds = vdd_val, bulk = source = 0
*   pfet_03v3   Vgs = 0 (gate at vdd), Vsd = vdd_val, bulk = source = vdd
*
* The measured drain current is total off-state drain leakage at that bias:
* subthreshold conduction plus junction/GIDL contributions, whatever the
* PDK's BSIM4 corner deck models. Gate leakage returns to the tied-off gate
* node and is therefore NOT in this number -- at 3.3 V devices with a thick
* gate oxide it is orders of magnitude below the subthreshold term, but the
* omission is stated rather than assumed away.
*
* w = 10u is chosen well above any numerical floor; l = 0.28u matches the
* channel length of every device in the candidate-A delay cell, so the
* per-micron figures below are the per-micron figures OF THAT CELL's
* devices, not of a generic transistor. Currents are divided by 10 in the
* measure expressions to report A per micron of gate width.

vdd vdd 0 dc vdd_val

* --- NMOS off: gate low, drain at vdd -------------------------------------
vdn vdd dn dc 0
xn dn 0 0 0 nfet_03v3 w=10u l=0.28u

* --- PMOS off: gate high, drain at 0 --------------------------------------
vdp dp 0 dc 0
xp dp vdd vdd vdd pfet_03v3 w=10u l=0.28u
