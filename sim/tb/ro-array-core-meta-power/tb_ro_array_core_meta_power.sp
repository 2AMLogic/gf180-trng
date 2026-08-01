* ro-array-core-meta-power -- the shipped array WITH the metastability tap.
*
* DUT: design/ro_array_core_meta.spice, exported from
* design/xschem/ro_array_core_meta.sch by design/netlist.py. That cell is
* ro_array_core -- unmodified, the same subcircuit this testbench's
* counterpart sim/tb/ro-array-core-power/ measures -- plus ro_meta_tap
* hanging off xo on its own supply pin.
*
* WHY THIS TESTBENCH IS A CLONE
*
* It is deliberately measurement-for-measurement identical to
* sim/tb/ro-array-core-power/, down to the measurement NAMES, the 50 ns
* window, the 1 ps print step and the charge-integrator construction. The
* claim it exists to test is "adding the tap does not change the core", and
* the only honest way to test that is to change exactly one thing -- the
* presence of the tap -- and read the same numbers back. Any difference in
* method between the two decks would be indistinguishable from a difference
* caused by the tap.
*
* Run the pair at the same PVT points and compare:
*
*   python3 sim/run_corners.py ro-array-core-power      --corners ff --temps -40 --supply 3.63 --supply-tol 0
*   python3 sim/run_corners.py ro-array-core-meta-power --corners ff --temps -40 --supply 3.63 --supply-tol 0
*
* WHAT IS EXPECTED TO MOVE, AND WHAT IS NOT
*
* The tap presents ONE minimum-width gate input on xo. xo is the XOR's
* output; the rings drive the XOR's inputs. So:
*
*   - period_r1/period_r2, i_r1_a/i_r2_a, p_rings_w, ring_swing_v should be
*     unchanged except through the combining gate's own Cgd, which is the
*     only path from xo back to a ring node. That residual is what this
*     testbench quantifies rather than assumes.
*   - i_tree_a is expected to RISE: the XOR now drives a load it did not
*     have. That is a real cost of the tap and it is charged to the tap, not
*     hidden -- see the tree/tap split in the measurements below.
*   - i_tap_a is new, on its own supply pin (vddm), which is why the tap has
*     one: the per-ring liveness argument in design/README.md depends on
*     vddr1/vddr2 seeing rings and nothing else.
*
* THE DELIBERATE DETUNE
*
* xdut is instantiated with ctb - cta = 0.5 fF rather than the shipped
* balanced default. A nominally balanced arbiter in a NOISELESS transient
* has no mechanism to leave the metastable point, so a balanced instance
* would either sit there for the whole 50 ns window or resolve at a time
* set by solver truncation error -- neither of which is a measurement of
* anything. Detuning by a stated amount makes the run convergent and makes
* the record's power figures meaningful. It is a simulation choice, not a
* design choice, and it is the reason DR-0011 claims no entropy from this
* cell. sim/tb/meta-arb-regeneration/ characterizes the balanced case
* head-on instead of stepping around it.
*
* METHOD NOTES (identical to sim/tb/ro-array-core-power/ unless stated)
*
*   - Per-branch 0 V sense sources (vr1, vr2, vtr, vtm) split one supply
*     into four separately-integrable branches; vtm is the one addition.
*   - fqN/cqN/rqN is the same ideal charge integrator: v(qN) is the charge
*     drawn on that branch since t = 0, scaled by 1/cq, differenced between
*     two like-edged crossings an exact integer number of ring periods
*     apart. Sign convention is unchanged from the counterpart testbench:
*     v(q) accumulates charge delivered INTO the branch, so the recorded
*     currents and powers are negative and the magnitudes are physical.
*   - Start-up: enable held HIGH from t = 0, each ring kicked out of its
*     unstable DC solution by a .ic on its NAND output. The tap's arbiter
*     gets the same treatment for the same reason.
*   - bvth is a measurement-only mid-supply reference.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vtr vsup vdd dc 0
vtm vsup vddm dc 0

xdut en en vddr1 vddr2 vdd vddm 0 xo mo ro_array_core_meta cta=2f ctb=2.5f cld=0.5f

fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fq2 q2 0 vr2 1
cq2 q2 0 1n
rq2 q2 0 1e12
fqt qt 0 vtr 1
cqt qt 0 1n
rqt qt 0 1e12
fqm qm 0 vtm 1
cqm qm 0 1n
rqm qm 0 1e12

bvth vth 0 v = 0.5*vdd_val

.ic v(xdut.xcore.xr1.n1)=0
.ic v(xdut.xcore.xr2.n1)=0
.ic v(xdut.xtap.mq)=0
.ic v(q1)=0
.ic v(q2)=0
.ic v(qt)=0
.ic v(qm)=0
