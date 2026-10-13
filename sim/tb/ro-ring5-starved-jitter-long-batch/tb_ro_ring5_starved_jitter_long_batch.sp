* ro-ring5-starved-jitter-long-batch -- the circuit body of
* sim/tb/ro-ring5-starved-jitter-long/ in the shape a `klt sim` request needs
* (issue #628).
*
* Why a second deck. sim/tb/ro-ring5-starved-jitter-long/ measures with an
* ngspice .control loop (769 edge times into a vector, then lag differences),
* which only the local harness can run. A request has no .control escape hatch,
* so this body carries the SAME circuit and the SAME stimulus, and the request
* (sim/tools/starved_hot_corner.py) asks only for the primitives -- the
* 769 mid-supply rising-edge times and the charge readings, as .meas cards. The
* jitter statistics (sigma at lags 1..128, per-block periods, energy per
* cycle) are computed from those primitives by the same tool, with the
* tb.json estimator definitions, so the record's Result lines are directly
* comparable to the local-harness records of the family.
*
* The circuit is unchanged: ring 1 of design/ro_array_sanity.spice (a ro_nand2
* enable stage plus four ro_stage, wstv = 0.220 um, lstv = 2 um, cld = 0.5 f),
* one trnoise() source in series with every stage input at the same fixed
* injected white density (vn_rms = 2.2361 mV, vn_dt = 10 ps -> 1e-16 V^2/Hz),
* a charge integrator on the ring's own supply pin, and a measurement-only
* probe x1 = v(ro1) - vsup/2. The enable is held high from t = 0 and the ring
* is kicked out of its unstable DC point by a .ic (an enable edge does not
* converge with trnoise active).
*
* Run length. The request stops at 3.1 us rather than the family's 2.4 us: at
* ss/+125 C the period is ~3.78 ns, so the window's last edge is near 2.92 us.
*
* Request axes. The supply is the source `vsup` (altered per unit by the
* request). `vseed` is an unconnected-in-effect marker source (a lone source
* to ground, no load): the request sweeps it 1..8 so the eight units are eight
* distinct units of one corner. It does not seed the noise; trnoise draws
* come from each ngspice process (DR-0031).

.include "../../../design/ro_array_sanity.spice"

* switches design.ngspice sets (its values, verbatim)
.param sw_stat_global=0 sw_stat_mismatch=0 mc_skew=3 res_mc_skew=3 cap_mc_skew=3 fnoicor=0
.param vn_rms=2.2361e-3 vn_dt=1e-11

vsup vsup 0 dc 3.63
vseed seedtag 0 dc 1
* enable tracks the supply (held high from t = 0)
een en2 0 vsup 0 1

* separate ring supply pin: the charge integrator sees the ring current alone
vr1 vsup vddr1 dc 0

xg1 g10 en2 n11 vddr1 0 ro_nand2 wstv=0.220u lstv=2u cld=0.5f
x11 g11 n12 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x12 g12 n13 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x13 g13 n14 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x14 g14 ro1 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
vn10 ro1 g10 dc 0 trnoise( vn_rms vn_dt 0 0)
vn11 n11 g11 dc 0 trnoise( vn_rms vn_dt 0 0)
vn12 n12 g12 dc 0 trnoise( vn_rms vn_dt 0 0)
vn13 n13 g13 dc 0 trnoise( vn_rms vn_dt 0 0)
vn14 n14 g14 dc 0 trnoise( vn_rms vn_dt 0 0)

* charge integrator: q1 is the ring's accumulated supply charge (cq = 1 nF)
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12

* measurement-only probe
bx1 x1 0 v = v(ro1) - 0.5*v(vsup)

.ic v(n11)=0
.ic v(q1)=0

* only the three probed vectors stay resident (1 ps print step over 2.4 us
* is ~1.5 GB for the full node set per unit)
.save v(x1) v(q1) v(vsup)
