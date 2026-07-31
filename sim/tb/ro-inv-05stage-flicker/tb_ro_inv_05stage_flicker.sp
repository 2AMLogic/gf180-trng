* ro-inv-05stage-flicker -- 5-stage plain-inverter ring oscillator with injected 1/f noise
*
* 5 identical plain CMOS inverter delay cells in a ring, with one injected
* trnoise() voltage source in series with every stage input. ngspice does
* not simulate device noise during .tran, so the ONLY noise in this
* simulation is what these sources inject; their absolute PSD calibration
* is measured -- not assumed -- by sim/tb/trnoise-calibration/, and the
* device-noise density they stand in for is measured by
* sim/tb/inv-stage-noise/.
*
* Injected per-stage input-referred white PSD (harness params vn_rms /
* vn_dt, see tb.json):
*
*     S_inj = 2 * vn_rms^2 * vn_dt = 1e-16 V^2/Hz  (1e-08 V/sqrt(Hz))
*
* The injected level is deliberately FIXED across the whole PVT grid so
* that what varies from corner to corner is the CIRCUIT's noise-to-jitter
* conversion (slew rate and stage delay), not the stimulus. Jitter is
* linear in the injected amplitude -- verified by
* sim/tb/ro-inv-05stage-lownoise/ at 1/10 the amplitude -- so the physical
* per-corner jitter is recovered by scaling these figures with the
* per-corner device density from sim/tb/inv-stage-noise/. See
* sim/characterization-ro-delay-cell-jitter.md.
*
* bxing / bs40 / bs60 are pure measurement probes (behavioural, no
* loading): they shift v(n1) so that a threshold/slew crossing becomes a
* zero crossing that `meas ... when v(...)=0` can find at any supply,
* without hard-coding a supply-dependent trip voltage.
*
* .ic starts the ring from a defined state; the first rising crossing is
* discarded (the measurement loop starts at rise=2) so that start-up is
* not counted as jitter.

.subckt inv_cell a y vdd vss
xp y a vdd vdd pfet_03v3 w=2u l=0.28u
xn y a vss vss nfet_03v3 w=1u l=0.28u
cload y vss 5f
.ends

vdd vdd 0 dc vdd_val
x1 g1 n2 vdd 0 inv_cell
x2 g2 n3 vdd 0 inv_cell
x3 g3 n4 vdd 0 inv_cell
x4 g4 n5 vdd 0 inv_cell
x5 g5 n1 vdd 0 inv_cell
vn1 n1 g1 dc 0 trnoise( vn_rms vn_dt 1 5.4772e-5)
vn2 n2 g2 dc 0 trnoise( vn_rms vn_dt 1 5.4772e-5)
vn3 n3 g3 dc 0 trnoise( vn_rms vn_dt 1 5.4772e-5)
vn4 n4 g4 dc 0 trnoise( vn_rms vn_dt 1 5.4772e-5)
vn5 n5 g5 dc 0 trnoise( vn_rms vn_dt 1 5.4772e-5)
bxing xing 0 v = v(n1) - 0.5*vdd_val
bs40  xs40 0 v = v(n1) - 0.4*vdd_val
bs60  xs60 0 v = v(n1) - 0.6*vdd_val
.ic v(n1)=0
