* sampler-array-digitize-extracted-routed -- issue #217's ROUTING-level re-run
* of sim/tb/sampler-array-digitize-extracted/. Each ring is now ONE instance of
* its whole physically-assembled, DRC-clean, LVS-matching, routing-level
* extraction (layout/pex/ro_ring11.routed.ntap.extracted.spice and its _ring2
* counterpart, behind the wrappers in
* layout/pex/ro_ring_pair.routed.ntap.extracted.spice) instead of eleven
* separately-extracted leaf cells -- so the hand-routed metal1 stage-to-stage
* chain and metal2/via1 vddr/vss straps drawn inside layout/rings/ are in these
* numbers. Node names, stimulus, rails, noise injection and every measurement
* expression are otherwise unchanged from the -extracted fragment.
*
* This deck closes the residual sim/characterization-post-layout-extracted.md
* §7.5 recorded on 2026-09-11 -- the one family of six that could not be
* re-run at routing level. That entry attributed the blocker to per-instance
* device addressability (filed as klayout-tools#1666: a flat extraction keeps
* no "this device belongs to stage N" tag). **That overstated what this deck
* actually needs.** A series noise source does not need to know which stage a
* device came from. It needs one NET broken between its driver side and its
* receiver side -- and `klt extract --parasitics` already discloses exactly
* that in the netlist it writes: every net's lumped resistance arrives as a
* star of per-terminal `R<name> <terminal> <hub> <ohms>` cards, and every
* device card names its own gate node, so each terminal is classifiable as
* receiver-side (a gate) or driver-side without any instance tag.
*
* layout/pex/build.py therefore emits a `_ntap` variant of each ring that
* re-points each tapped net's gate-side star resistors onto a new hub and
* promotes both hubs to ports. Tie a pair together and the tapped ring IS the
* untapped ring -- same cards, same star resistances, same grounded
* capacitance; a 0 V source is a short. That is not asserted here, it is held
* to BYTE equality by layout/tests/test_pex_noise_tap.py, which un-taps the
* committed netlist and compares it against the committed untapped one. The
* `vn1*`/`vn2*` sources below sit across those pairs, exactly as they sat
* between two leaf cells before. See layout/pex/build.py's module docstring,
* "Per-stage noise injection".
*
* One asymmetry is disclosed rather than hidden: each net's lumped grounded
* capacitance stays on the DRIVER side of the tap -- as it does in the
* leaf-level deck, where the wire capacitance lives inside the driving cell's
* own extraction, ahead of the source.
*
* What is NOT routing-level here, deliberately: `xor2` and the two
* `sampler_dff` instances are still leaf-level. This deck's pre-layout ancestor
* wires them up itself (no ro_buf, no ring-liveness samplers), so substituting
* the routed combiner_sampler block would have changed the TOPOLOGY as well as
* the parasitics and the leaf-vs-routed delta would no longer isolate the ring
* routing -- the only place this testbench's entropy comes from.
*
* Why a sibling family rather than repointing the -extracted one: its
* 2026-09-06 `level: extracted` records name that testbench's blob SHA and that
* netlist's blob SHA, and an in-place edit would leave them citing a fragment
* that no longer exists at HEAD. Same convention the five other
* `*-extracted-routed` families already follow.
*
* ONE manifest difference beyond the netlist: the transient window is
* tran 10p 200n, not 10p 132n. The routed rings are ~37% slower, so the 14th
* rising edge the period measurement addresses no longer lands inside 132 ns
* and ngspice returns `out of interval` instead of a number. Every sampled bit
* (39-129 ns) and swing window (30-130 ns) is where it was; tb.json's caveats
* record the measured size of the lengthening's own effect on the earlier part
* of the run.
*
* The two `.ic` lines below keep their role and their node names, but note what
* those names now mean: `n11`/`n21` are bound to each wrapper's first tapped
* net in `klt extract`'s own header ORDER, not to the NAND output the
* leaf-level deck's `n11`/`n21` happened to be. A flat extraction does not
* record which stage a net belonged to. That is immaterial to what the `.ic`
* is for -- kicking each ring off its unstable symmetric DC equilibrium, which
* any single ring node does equally well.
*
* See sim/characterization-post-layout-extracted.md §7 for scope/limits.
*
* sampler-array-digitize -- the entropy source, digitized. End to end.
*
* This is the testbench the original issue's acceptance criterion asks for:
* the shipped entropy source under transient noise, sampled by the shipped
* sampler, producing an actual raw bitstream at the DR-0001 raw tap.
*
* DUT: the sampler_dff cell of design/sampler_core.spice, exported from
* design/xschem/sampler_dff.sch by design/netlist.py, driven by the
* design's own leaf cells (ro_nand2 / ro_stage / xor2 from the same file).
*
* Why the ring array is wired here instead of instantiating sampler_core
* whole: ngspice cannot insert a series source into the interior of a
* subcircuit, and per-stage series noise injection is this repository's
* jitter method (sim/tb/ro-inv-05stage-jitter/, sim/tb/ro-array-sanity-jitter/).
* So this fragment restates ro_array_core's top-level wiring -- the SAME
* two ro_ring11 rings at the SAME wstv = 0.220u / 0.240u skew, the SAME
* lstv = 2u and cld = 0.5f, combined by the SAME xor2 -- around
* individually-injectable stages, and then instantiates the sampler cell
* itself unmodified. Only the array's top-level wiring is restated; every
* device, including all of the sampler's, still comes from the schematic.
* Compare with design/xschem/ro_array_core.sch and
* design/xschem/sampler_core.sch when reviewing. What is built here is
* sampler_core minus its two DR-0016 per-ring liveness digitizers (#65's
* xsr1/xsr2 on ro1/ro2): the raw-tap path -- ro_array_core + xsb + xsv --
* is instantiated below verbatim, and this deck is about the raw tap, not
* the liveness taps. The liveness taps' own loading on the ring nodes is
* measured separately, against the un-tapped baseline, by
* sim/tb/ring-liveness-tap-power/.
*
* Injected per-stage input-referred white PSD (harness params vn_rms /
* vn_dt, see tb.json):
*
*     S_inj = 2 * vn_rms^2 * vn_dt = 1e-16 V^2/Hz  (1e-08 V/sqrt(Hz))
*
* the same fixed level sim/tb/ro-array-sanity-jitter/ uses, so what varies
* corner to corner is the circuit's noise-to-jitter conversion, not the
* stimulus. This testbench does NOT convert that back to physical jitter
* and makes no min-entropy claim; it demonstrates digitization.
*
* ---- what this run answers -------------------------------------------
*   1. Does the sampler produce a settled, rail-to-rail logic level at
*      raw_bit on every clock edge, from a real analog xo swing at this
*      corner? (b0..b9, read 1 ns before each following edge)
*   2. Does raw_valid follow design/conditioner/README.md's contract --
*      low through reset, high from the first clock edge after rst_n
*      releases, and high thereafter? (rv_rst, rv0..rv9)
*   3. Do the two rings still hold their own distinct frequencies with the
*      sampler's load and switching activity on the XOR node?
*      (period_r1, period_r2, and the ratio between them)
*   4. Is the XOR node still rail-to-rail once the sampler's input
*      capacitance hangs on it? (xo_swing_v against the same quantity in
*      sim/tb/ro-array-core-power/'s records, which has no sampler load)
*
* ---- what this run does NOT answer -----------------------------------
* It is not a rate measurement and not an entropy measurement. The clock
* period here (param tclk, default 10 ns = 100 Mbps) is far above
* DR-0003's ratified 1 Mbps raw target, chosen so that ten raw bits fit
* inside a transient-noise window this array can afford: the deterministic
* 50 ns run of sim/tb/ro-array-core-power/ already costs ~15 minutes per
* PVT point, and adding 22 trnoise sources makes a microsecond-scale
* window impossible. Sampling FASTER than the target is the conservative
* direction for a functional demonstration (less jitter accumulated per
* sample, so a bitstream that looks alive here is not an artifact of a
* generous sample period) but it is the WRONG direction for an entropy
* claim, which is why none is made. The sampler's behavior at the real
* 1 Mbps clock period is sim/tb/sampler-dff-setup-hold/'s job, across the
* full PVT grid, where it is affordable because the rings are not present.
*
* Per DR-0012 the sample clock is a fixed external clock with no frequency
* relationship to either ring, so retargeting the rate is the `tclk` param
* and nothing else. That is the decision, not a limitation of this deck.
*
* ---- method notes ----------------------------------------------------
*   - Start-up: enable held HIGH from t = 0, each ring kicked out of its
*     unstable DC solution by a .ic on its NAND output. This is the method
*     sim/tb/ro-array-sanity-jitter/ documents: with trnoise sources active
*     ngspice fails to converge on an enable EDGE. Solver limitation, not a
*     circuit finding.
*   - rst_n releases at 20 ns, ~3 ring periods after the rings reach
*     steady state and 10 ns before the first clock edge, so no sample is
*     taken while the ring array is still settling.
*   - bx1/bx2 are measurement-only probes: they shift each ring output so
*     that a mid-supply crossing is a zero crossing `meas ... when v(..)=0`
*     finds at any supply.
*   - `abstol=1e-10` (tb.json "options"), 100x looser than ngspice's 1e-12
*     default. Without it this deck aborts with "Timestep too small ...
*     trouble with node vclk#branch" at whichever external edge (reset
*     release or first clock edge) arrives first. That was bisected rather
*     than guessed, and the finding is worth stating precisely because the
*     obvious reading of it is wrong:
*       * it is NOT a transient-noise artifact -- the abort reproduces
*         identically with vn_rms = 0, i.e. with every noise source silent;
*       * it is NOT the clock edge rate -- 100 ps, 1 ns and 5 ns edges all
*         abort the same way;
*       * it is NOT the sampler cell alone -- sim/tb/sampler-dff-setup-hold/
*         runs the same cell with 1 ps edges at ngspice's default tolerances
*         without complaint.
*     What it is: 22 series-starved ring stages hold their devices at
*     currents low enough that a 1 pA absolute current tolerance is a
*     meaningful fraction of the branch currents being solved, and an
*     abrupt external edge elsewhere in the same matrix then drives the
*     timestep control to zero. 100 pA is still ~5e-6 of the ~20 uA per-ring
*     supply current this array draws, and this testbench measures settled
*     node voltages and ring periods -- not currents -- so the relaxation is
*     recorded in every record's method notes rather than treated as free.
*     The other options tried and rejected: gmin, rshunt, chgtol, trtol,
*     method=gear, and tighter reltol all still abort; abstol=1e-11 still
*     aborts; abstol=1e-10 is the smallest relaxation that converges.
*   - Clock edge rate (param tclk_tr, default 1 ns) is deliberately soft --
*     a 1 ns edge on a 10 ns period is realistic for an off-chip clock
*     arriving through a pad, and it keeps the transmission gates' switching
*     window away from the noise sources' 10 ps breakpoint grid. It does
*     mean the effective sampling instant is defined only to within the
*     edge's own transit through the transmission gates' switching
*     threshold, which is one more reason no entropy claim is made from
*     this deck. The sharp-edge case (1 ps) is covered by
*     sim/tb/sampler-dff-setup-hold/.
*   - Each bit is read 1 ns BEFORE the next rising clock edge, i.e. 9 ns
*     after the edge that captured it -- far past this cell's clk-to-Q
*     delay (hundreds of ps; sim/tb/sampler-dff-setup-hold/ measures it) so
*     the reading is a settled level, not a transition caught in flight.
*     A reading that is not within a few hundred mV of a rail is itself the
*     finding, which is why the raw voltages are recorded rather than a
*     thresholded 0/1.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vtr vsup vdd dc 0

* ---- ring 1 (wstv = 0.220u), ASSEMBLED + ROUTED, per-stage noise injection ----
* One instance, not eleven: ro_ring11_routed_ntap is the whole assembled ring
* as extracted from layout/rings/ro_ring11/ro_ring11.gds, so the metal1
* stage-to-stage chain and metal2/via1 vddr/vss straps between those eleven
* cells are INSIDE it. Its tapped ports expose both sides of every one of the
* eleven ring nets, in the order that wrapper's own banner publishes
* (layout/pex/ro_ring_pair.routed.ntap.extracted.spice) -- for THIS ring:
*   n1 n1__rx n2 n2__rx ... n10 n10__rx ro__rx
* Bound below to the same node names the leaf-level deck uses, so every
* `vn1*` source line and every measurement expression below is unchanged.
* NOTE the `n1`..`n10` labels are `klt extract`'s own header ORDER, not the
* logical stage order: a flat extraction does not record which stage a net
* belonged to. That is immaterial here -- all eleven sources are identical,
* and each sits between one net's driver side and that same net's receiver
* side whichever stage it turns out to be.
xr1 en ro1 vddr1 0 0 n11 g11 n12 g12 n13 g13 n14 g14 n15 g15 n16 g16 n17 g17 n18 g18 n19 g19 n1a g1a g10 ro_ring11_routed_ntap
vn10 ro1 g10 dc 0 trnoise( vn_rms vn_dt 0 0)
vn11 n11 g11 dc 0 trnoise( vn_rms vn_dt 0 0)
vn12 n12 g12 dc 0 trnoise( vn_rms vn_dt 0 0)
vn13 n13 g13 dc 0 trnoise( vn_rms vn_dt 0 0)
vn14 n14 g14 dc 0 trnoise( vn_rms vn_dt 0 0)
vn15 n15 g15 dc 0 trnoise( vn_rms vn_dt 0 0)
vn16 n16 g16 dc 0 trnoise( vn_rms vn_dt 0 0)
vn17 n17 g17 dc 0 trnoise( vn_rms vn_dt 0 0)
vn18 n18 g18 dc 0 trnoise( vn_rms vn_dt 0 0)
vn19 n19 g19 dc 0 trnoise( vn_rms vn_dt 0 0)
vn1a n1a g1a dc 0 trnoise( vn_rms vn_dt 0 0)

* ---- ring 2 (wstv = 0.240u), ASSEMBLED + ROUTED, per-stage noise injection ----
* As ring 1, from layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds. Its tapped
* port order DIFFERS from ring 1's, because `ro` lands at a different position
* in its own extracted header -- which is exactly the positional fact
* klayout-tools#1543 disclosed and layout/pex/build.py resolves. For THIS ring:
*   ro__rx n1 n1__rx n2 n2__rx ... n10 n10__rx
xr2 en ro2 vddr2 0 0 g20 n21 g21 n22 g22 n23 g23 n24 g24 n25 g25 n26 g26 n27 g27 n28 g28 n29 g29 n2a g2a ro_ring11_ring2_routed_ntap
vn20 ro2 g20 dc 0 trnoise( vn_rms vn_dt 0 0)
vn21 n21 g21 dc 0 trnoise( vn_rms vn_dt 0 0)
vn22 n22 g22 dc 0 trnoise( vn_rms vn_dt 0 0)
vn23 n23 g23 dc 0 trnoise( vn_rms vn_dt 0 0)
vn24 n24 g24 dc 0 trnoise( vn_rms vn_dt 0 0)
vn25 n25 g25 dc 0 trnoise( vn_rms vn_dt 0 0)
vn26 n26 g26 dc 0 trnoise( vn_rms vn_dt 0 0)
vn27 n27 g27 dc 0 trnoise( vn_rms vn_dt 0 0)
vn28 n28 g28 dc 0 trnoise( vn_rms vn_dt 0 0)
vn29 n29 g29 dc 0 trnoise( vn_rms vn_dt 0 0)
vn2a n2a g2a dc 0 trnoise( vn_rms vn_dt 0 0)

* ---- combining node (ro_array_core's xa1, verbatim) ------------------
xa1 ro1 ro2 vdd 0 0 xo xor2

* ---- the sampler (sampler_core's xsb / xsv, verbatim) ----------------
* xsb registers the entropy source; xsv registers a constant 1, so
* raw_valid rises one clock edge after reset releases and stays high.
xsb clk xo raw_bit rst_n vdd 0 0 sampler_dff
xsv clk vdd raw_valid rst_n vdd 0 0 sampler_dff

* ---- stimulus: the FIXED EXTERNAL sample clock and async reset -------
vrst rst_n 0 dc 0 pulse(0 'vdd_val' 20n 100p 100p 1 2)
vclk clk 0 dc 0 pulse(0 'vdd_val' 'tclk0' 'tclk_tr' 'tclk_tr' 'tclk/2-tclk_tr' 'tclk')

* ---- measurement probes ----------------------------------------------
bx1 x1 0 v = v(ro1) - 0.5*vdd_val
bx2 x2 0 v = v(ro2) - 0.5*vdd_val
bvth vth 0 v = 0.5*vdd_val
* the clock period as a vector, so the control block can use it: ngspice's
* control language cannot read a .param directly (a bare `tclk` there is a
* parse error, exactly as `0.5*vdd_val` is)
btclk tclkv 0 v = tclk

.ic v(n11)=0
.ic v(n21)=0
