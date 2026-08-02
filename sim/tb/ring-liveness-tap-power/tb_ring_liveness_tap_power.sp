* ring-liveness-tap-power -- bounds the DR-0016 liveness monitor's own
* electrical cost against the shipped entropy-source array.
*
* DUT: design/sampler_core.spice (design/netlist.py output). That file
* contains .subckt ro_array_core, .subckt sampler_dff and the shipped
* sampler_core wrapper that now instantiates FOUR sampler_dff cells: the two
* raw-tap ones (xo -> raw_bit, raw_valid) and the two DR-0016 liveness
* digitizers (ro1/ro2 -> ring_bit1/ring_bit2). This deck deliberately does
* NOT instantiate that wrapper: xdut below is a bare ro_array_core, and
* xtap1/xtap2 restate only the two liveness taps, so every measurement here
* is directly comparable, expression for expression, to the un-tapped
* baseline sim/tb/ro-array-core-power/ -- which is the whole point of the
* deck. The raw tap's own two flip-flops are held out for the same reason
* the baseline holds them out: they load xo, not ro1/ro2, and this deck
* bounds what the LIVENESS taps cost the rings.
*
* Originally (#44) this deck reached ro1/ro2 through ngspice's hierarchical
* internal-node naming (`xdut.ro1`), because those nets had no pin. #65
* promoted the tap into the shipped design: ro_array_core.sym now carries
* ro1/ro2 as observation-only output pins and sampler_core.sch instantiates
* the two digitizers, so this deck names the same two nets at its own top
* level (`ro1`/`ro2`) instead. Same nets, same circuit, same numbers -- a
* subcircuit port is simply not addressable as an internal node. What this
* deck measures is now the cost of something the design actually contains
* rather than a bound on something it might one day contain.
*
* Still not an exposed tap (DR-0001): ro1/ro2 and ring_bit1/ring_bit2 are
* block-internal signals that stop at design/health_test/, exactly as
* raw_bit's predecessors do. No per-ring signal reaches a die pin.
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

xdut en en vddr1 vddr2 vdd 0 xo ro1 ro2 ro_array_core

* ---- the two liveness-monitor taps: sampler_dff, unmodified, digitizing
* ---- ro1/ro2 directly (the same cell that digitizes xo -> raw_bit today)
xtap1 ro1 mclk mrst_n ro1_bit vddtap 0 sampler_dff
xtap2 ro2 mclk mrst_n ro2_bit vddtap 0 sampler_dff

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
