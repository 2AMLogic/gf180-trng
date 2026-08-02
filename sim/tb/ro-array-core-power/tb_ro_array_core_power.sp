* ro-array-core-power -- the shipped entropy-source array, deterministic.
*
* DUT: design/ro_array_core.spice, exported from design/xschem/ro_array_core.sch
* by design/netlist.py. Nothing about the DUT is redefined here; this
* fragment supplies rails, an enable ramp, and measurement-only elements.
*
* What it measures, per PVT point:
*   - each ring's oscillation period, from that ring's own output node
*     (ro1/ro2 -- an observation-only pin of the core since #65, and still
*     not an exposed tap: DR-0001 constrains what leaves the die, and no
*     per-ring signal does; see the node-naming note below);
*   - each ring's supply current, integrated over an exact integer number
*     of that ring's periods;
*   - the XOR tree's supply current, over the same window;
*   - the ring node's high/low levels, because a series-starved stage can
*     lose output swing before it loses oscillation, and a degraded swing
*     is a sampler problem, not a ring problem.
*
* Together with DR-0010's jitter law those numbers are the array's sizing
* evidence: energy per ring cycle sets the entropy cost per raw bit, and
* the sum of ring frequencies sets the transition density the sampler has
* to resolve.
*
* Method notes:
*   - Per-branch 0 V sense sources (vr1..vr4, vtr) split one supply into
*     three separately-integrable branches. This is the per-ring supply
*     routing DR-0007 requires, wired the way the design intends it.
*   - fqN/cqN/rqN is the same ideal charge integrator sim/tb/ro-inv-05stage-power/
*     uses: v(qN) is the charge drawn on that branch since t = 0, scaled by
*     1/cq. Taking its difference between two like-edged crossings an exact
*     integer number of periods apart removes the partial-cycle bias a
*     fixed-window average would carry. rq gives the integrator node a DC
*     path (tau = 1000 s, i.e. ~2e-8 of the window).
*   - Start-up: the enable is held HIGH from t = 0 and each ring is kicked
*     out of its unstable DC solution by a .ic on its NAND output -- the
*     method sim/tb/ro-inv-05stage-jitter/ uses. Starting instead from an
*     enable EDGE also works here, and is more faithful to the block's real
*     start-up path, but a starved ring takes ~20 ns to reach steady state
*     from the NAND-latched condition, which would be simulated dead time
*     ahead of every measurement window. Start-up time itself is worth
*     measuring; it is not what THIS testbench measures.
*   - bvth is a measurement-only probe: a mid-supply reference so
*     `meas ... when v(ring)=v(vth)` finds crossings at any supply without
*     a hard-coded trip voltage.
*
* Node-naming note (#65): ro_array_core now exposes its two per-ring nodes as
* observation-only output pins (ro1/ro2), so the shipped DR-0016 liveness
* digitizers in design/xschem/sampler_core.sch can reach them. That change
* adds no device and changes no ring. The two extra nodes on the xdut line
* below, and the v(ro1)/v(ro2) measurement expressions in tb.json, name the
* SAME nets this deck already measured hierarchically as v(xdut.ro1) before
* the pins existed -- a subcircuit port is not addressable as an internal
* node, so the reference moved from dotted to top-level. The circuit
* simulated here is identical to the one the pre-#65 records describe.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vtr vsup vdd dc 0

xdut en en vddr1 vddr2 vdd 0 xo ro1 ro2 ro_array_core

fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fq2 q2 0 vr2 1
cq2 q2 0 1n
rq2 q2 0 1e12
fqt qt 0 vtr 1
cqt qt 0 1n
rqt qt 0 1e12

bvth vth 0 v = 0.5*vdd_val

.ic v(xdut.xr1.n1)=0
.ic v(xdut.xr2.n1)=0
.ic v(q1)=0
.ic v(q2)=0
.ic v(qt)=0
