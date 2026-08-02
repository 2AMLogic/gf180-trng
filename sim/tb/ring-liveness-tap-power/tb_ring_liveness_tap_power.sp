* ring-liveness-tap-power -- bounds the DR-0016 liveness monitor's own
* electrical cost against the shipped entropy-source array.
*
* DUT: design/sampler_core.spice (design/netlist.py output). That file
* already contains BOTH .subckt ro_array_core AND .subckt sampler_dff (the
* already-verified, already-characterized cell that digitizes xo -> raw_bit
* in the shipped design), so this deck needs no schematic change and no new
* cell: xdut below is a bare ro_array_core instance (not the sampler_core
* wrapper), and xtap1/xtap2 are two MORE sampler_dff instances, tied
* directly to ro_array_core's own internal ro1/ro2 nodes.
*
* Why this does not require a new pin, and is not an exposed tap (DR-0001):
* xdut.ro1 / xdut.ro2 are addressed the same hierarchical way
* sim/tb/ro-array-core-power/'s own .measure lines already do
* (`v(xdut.ro1)`) -- ngspice flattens subcircuit instances into one global
* node namespace, so any element (not only a .measure probe) can reference
* an internal node of an already-instantiated subcircuit by its dotted name.
* This testbench goes one step further than a read-only probe and ties two
* sampler_dff D inputs to those nodes -- exactly the electrical shape the
* DR-0016 liveness monitor's per-ring digitizer needs -- without adding a
* pin to ro_array_core.sym and without any per-ring signal leaving the
* schematic. The digitized outputs (ro1_bit/ro2_bit) are new nodes of THIS
* testbench fragment, not of the design; DR-0016 records the corresponding
* shipped-design integration (promoting this tap into design/ RTL/schematic)
* as follow-up work, not something this record does.
*
* What this measures, per PVT point, directly comparable point for point to
* the un-tapped baseline sim/records/2026-08-01-ro-array-core-power-{04,05,06}.md
* (same DUT, same window, same measurement expressions):
*   - each ring's oscillation period, supply current and swing, exactly as
*     sim/tb/ro-array-core-power/ measures them -- so any perturbation the
*     two taps' input-gate capacitance introduces on ro1/ro2 shows up
*     directly as a period/power/swing delta against that baseline;
*   - the XOR node's swing (xo_swing_v), unaffected by this tap (it loads
*     ro1/ro2, not xo);
*   - the two taps' OWN average switching current/power, on their own supply
*     branch (vddtap), separate from p_rings_w/p_total_w -- the monitor's
*     digitizer lives in the block's digital domain, not on either ring's
*     own vddr, so its cost is reported separately rather than folded into
*     the ring numbers, the same accounting DR-0011 used for vddm/ro_meta_tap;
*   - a settling check on ro1_bit/ro2_bit (do the taps resolve to a rail
*     rather than a half-supply level), the same class of check
*     sim/tb/sampler-array-digitize/ makes for raw_bit.
*
* Method notes:
*   - Per-branch 0 V sense sources (vr1/vr2/vtr/vtap) split the supply into
*     four separately-integrable branches, same technique as
*     sim/tb/ro-array-core-power/.
*   - fqN/cqN/rqN is the same ideal charge integrator sim/tb/ro-inv-05stage-power/
*     and sim/tb/ro-array-core-power/ use.
*   - Start-up: enable held HIGH from t=0, each ring kicked out of its
*     unstable DC solution by a .ic on its own NAND output -- identical to
*     sim/tb/ro-array-core-power/'s method.
*   - mclk/mrst_n are a LOCAL, deliberately fast measurement clock (10 ns
*     period from t=5n) -- NOT DR-0012's real fixed external sample clock.
*     It exists only to exercise the taps' loading/switching behaviour
*     inside the same 50 ns window the baseline testbench uses; see
*     tb.json's caveats for why this does not touch DR-0016's detection-
*     latency claim (a cycle count, not a rate).
*   - bvth is a measurement-only probe: a mid-supply reference so
*     `meas ... when v(ring)=v(vth)` finds crossings at any supply without a
*     hard-coded trip voltage.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vtr vsup vdd dc 0
vtap vsup vddtap dc 0

xdut en en vddr1 vddr2 vdd 0 xo ro_array_core

* ---- the two liveness-monitor taps: sampler_dff, unmodified, digitizing
* ---- ro1/ro2 directly (the same cell that digitizes xo -> raw_bit today)
xtap1 xdut.ro1 mclk mrst_n ro1_bit vddtap 0 sampler_dff
xtap2 xdut.ro2 mclk mrst_n ro2_bit vddtap 0 sampler_dff

* ---- local measurement clock and reset for the taps (see method notes) --
vmclk mclk 0 dc 0 pulse(0 'vdd_val' 5n 200p 200p 4.6n 10n)
vmrst mrst_n 0 dc 0 pulse(0 'vdd_val' 2n 100p 100p 1 2)

fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fq2 q2 0 vr2 1
cq2 q2 0 1n
rq2 q2 0 1e12
fqt qt 0 vtr 1
cqt qt 0 1n
rqt qt 0 1e12
fqtap qtap 0 vtap 1
cqtap qtap 0 1n
rqtap qtap 0 1e12

bvth vth 0 v = 0.5*vdd_val

.ic v(xdut.xr1.n1)=0
.ic v(xdut.xr2.n1)=0
.ic v(q1)=0
.ic v(q2)=0
.ic v(qt)=0
.ic v(qtap)=0
