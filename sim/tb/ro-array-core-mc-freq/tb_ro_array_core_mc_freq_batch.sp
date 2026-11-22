* ro-array-core-mc-freq batch body -- the circuit body of
* sim/tb/ro-array-core-mc-freq/tb_ro_array_core_mc_freq.sp for `klt sim`
* (issue #1025's sized mismatch campaign). Same DUT, same stimulus, same
* measurement method as the harness fragment; the differences are exactly the
* ones a klt request needs (see sim/tb/ro-array-supply-ripple/'s netlist for
* the convention): no .control/.end (klt sim owns the control block and
* appends the corner's .lib/.temp cards, the request's .meas cards, an
* `alter` for every key of the request's corners.supply_v and an
* `alterparam` for every key of corners.params, and the analysis), and no
* {vdd_val}-style format fields (the harness substitutes those in Python
* before ngspice ever sees them; here the supply source is the concrete
* nominal 3.3 V -- the ss/125C/3.63V request alters `vsup`, with every other
* rail tied to vsup through zero-volt sources so the whole bench tracks the
* altered rail).
*
* DUT note: design/ro_array_core.spice's top wrapper is re-expressed here --
* its five instance lines verbatim, except xr1's stage length is hoisted to
* the .param ro_lstv so a request can alterparam it (the generated design
* netlist cannot carry a body-level knob, and it is not edited here). Every
* subcircuit (ro_ring11, ro_buf, xor2) still comes from the include, and a
* mismatch-free nominal run reproduces the committed campaign's mismatch-free
* ring-1 period exactly (6.6774e-9 s at tt/27C/3.30V, DR-0033's T0_r1) --
* the campaign's record under sim/records/ quotes the probe.
*
* ro_lstv is the known-bad control's knob: ring 1's per-stage channel length,
* 2u as shipped. A control request sets ro_lstv to a longer length -- a
* deterministic, corner-independent slow-device defect (the ring's defining
* dimension fabricated long), the kind of degradation the DR-0033 period
* ceiling exists to catch. Ring 2, the buffers and the XOR are untouched: the
* limit is on ring 1's period, so the defect is put where the limit looks.
*
* The charge-integration network (fq*/cq*/rq*, fqt/cqt/rqt) is the harness
* fragment's, verbatim: it only senses i(vr1)/i(vr2)/i(vtr) into dangling
* nodes (no feedback into the DUT), kept so this body is the same circuit
* the committed 2026-08-17 records describe. The ring-current measurements
* that network fed in the harness campaign (i_r1_a/i_r2_a) are not part of
* this campaign's requests; the campaign's record under sim/records/ says so.
*
* Mismatch stays OFF in this body: sw_stat_mismatch is 0 here, and the
* campaign's requests turn it on per sample with
* corners.params {"sw_stat_mismatch": [1]} (an alterparam after this include,
* so it wins) -- the same local (Pelgrom) mismatch mechanism the harness
* fragment's design_params switches on, driven instead by klt sim's seeded
* monte_carlo (.options seed= per sample). The known-bad requests carry the
* same params row, so the control population spreads under mismatch exactly
* like the nominal one.
*
* bvth is kept (the harness fragment's mid-supply probe) for circuit
* identity only; the requests' .meas cards do not read it. The period cards
* use ngspice's TRIG/TARG form with a concrete val= literal (the corner's
* own altered vsup/2, emitted per request by sim/tools/mc_yield_campaign.py)
* plus a param= card for the /4 averaging, because a measurements[].expr
* cannot reference a file-scope .meas result (ngspice keeps no vector for
* it; verified against ngspice-47 locally -- the campaign's record quotes
* the probe).
*
* Nothing in this file is run by sim/selftest.sh or CI; the requests beside
* it (mc-*.request.json, emitted by sim/tools/mc_yield_campaign.py) are the
* run mechanism (batch fleet, monte_carlo per request).

.include "../../../design/ro_array_core.spice"

* switches design.ngspice sets (its values, verbatim); ro_lstv is ring 1's
* stage length in meters (see the header) -- 2e-6 is the shipped 2u, stated
* unitless because a corners.params alterparam value is a bare number
.param sw_stat_global=0 sw_stat_mismatch=0 mc_skew=3 res_mc_skew=3 cap_mc_skew=3 fnoicor=0
.param ro_lstv=2e-6

vsup vsup 0 dc 3.3
ven en vsup dc 0

vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vtr vsup vdd dc 0

* design/ro_array_core.spice's wrapper, re-expressed (see the header): xr1's
* lstv reads the hoisted param, everything else verbatim
xr1 en rn1 vddr1 0 ro_ring11 wstv=0.220u lstv='ro_lstv' cld=0.5f
xr2 en rn2 vddr2 0 ro_ring11 wstv=0.240u lstv=2u cld=0.5f
xb1 rn1 ro1 vdd 0 ro_buf
xb2 rn2 ro2 vdd 0 ro_buf
xa1 ro1 ro2 xo vdd 0 xor2

fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fq2 q2 0 vr2 1
cq2 q2 0 1n
rq2 q2 0 1e12
fqt qt 0 vtr 1
cqt qt 0 1n
rqt qt 0 1e12

bvth vth 0 v = 0.5*v(vsup)

.ic v(xr1.n1)=0
.ic v(xr2.n1)=0
.ic v(q1)=0
.ic v(q2)=0
.ic v(qt)=0
