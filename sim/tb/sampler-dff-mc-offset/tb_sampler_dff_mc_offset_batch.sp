* sampler-dff-mc-offset batch body -- the circuit body of
* sim/tb/sampler-dff-mc-offset/tb_sampler_dff_mc_offset.sp for `klt sim`
* (issue #1025's sized mismatch campaign). Same DUT and same clk=0 open-loop
* master latch DC sweep as the harness fragment (see that file's header for
* the method); the differences are exactly the ones a klt request needs
* (same convention as sim/tb/ro-array-supply-ripple/'s netlist): no
* .control/.end (klt sim owns the control block and appends the corner's
* .lib/.temp cards, the request's .meas card, an `alter` for every key of
* the request's corners.supply_v and an `alterparam` for every key of
* corners.params, and the analysis), and no {vdd_val}/{vdd_half} format
* fields (the harness substitutes those in Python; here the supply source is
* the concrete nominal 3.3 V -- the ss/125C/3.63V request alters `vdd`, with
* rst_n tied to the vdd node through a zero-volt source so it tracks, and
* the request's .meas card carries the corner's own concrete mid-supply
* comparison value; the harness fragment's own meas never read the vth node
* either, so no bvth here).
*
* voff is the known-bad control's knob: a 0 V source in series with the d
* input (node di is the DUT's input; the swept node d rides voff away from
* it). The nominal requests never name it, so di sits at exactly d and the
* circuit is the harness fragment's, electrically. A control request
* `alter`s voff to a negative offset, which shifts the d voltage at which
* the master latch's mb crosses mid-supply UP by |voff| -- an input-referred
* threshold offset of the kind klt yield's negative-control discipline names
* ("a forced offset"), sized to push the crossing past the positive supply
* rail. The control requests widen the .dc sweep window (vd 2.5..5 V) so the
* shifted crossing stays measurable; the DR-0033 limit (0 < dtrip_v < VDD)
* is unchanged and is what must catch it.
*
* Mismatch stays OFF in this body: sw_stat_mismatch is 0 here, and the
* campaign's requests turn it on per sample with
* corners.params {"sw_stat_mismatch": [1]} (an alterparam after this
* include, so it wins) -- the same local (Pelgrom) mismatch mechanism the
* harness fragment's design_params switches on, driven instead by klt sim's
* seeded monte_carlo (.options seed= per sample). The known-bad offset
* requests carry the same params row, so the control population spreads
* under mismatch exactly like the nominal one.
*
* Nothing in this file is run by sim/selftest.sh or CI; the requests beside
* it (mc-*.request.json, emitted by sim/tools/mc_yield_campaign.py) are the
* run mechanism (batch fleet, monte_carlo per request).

.include "../../../design/sampler_core.spice"

* switches design.ngspice sets (its values, verbatim)
.param sw_stat_global=0 sw_stat_mismatch=0 mc_skew=3 res_mc_skew=3 cap_mc_skew=3 fnoicor=0

vdd vdd 0 dc 3.3
vrst rst_n vdd dc 0
vclk clk 0 dc 0
vd d 0 dc 0
voff di d dc 0

xdut di clk rst_n q vdd 0 sampler_dff
