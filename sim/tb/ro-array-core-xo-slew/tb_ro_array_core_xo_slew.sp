* ro-array-core-xo-slew -- how fast the XOR node the sampler looks at
* actually crosses its decision band.
*
* DUT: design/ro_array_core.spice, exported from design/xschem/ro_array_core.sch
* by design/netlist.py. Rails, enable and start-up kick are
* sim/tb/ro-array-core-power/'s, verbatim; see that testbench's header for
* the method notes, which are not repeated here.
*
* Why this measurement exists (issue #13). A sampler decision-threshold
* offset -- the quantity sim/tb/sampler-dff-mc-offset/ measures in VOLTS --
* only becomes a raw-bit bias after division by the slew rate of the edge
* being sampled: an offset of dV displaces the captured crossing in TIME by
* dV/slew, and it is that time offset, compared against the ring's
* accumulated jitter, that biases the bit. Before this testbench existed,
* issue #13's own analysis had to stand in for the slew with a proxy
* computed from already-committed records -- the XOR node's total swing
* divided by one full ring period -- which is an average over an entire
* period rather than over an edge, and therefore understates the real slew
* by whatever fraction of a period the edge occupies. That proxy is
* conservative in the safe direction (it overstates the bias), but a
* conservative invented number is still an invented number, and the
* conclusion it feeds -- whether the offset matters at all -- turned out to
* be sensitive to it. So it is measured here instead.
*
* Two independent methods, deliberately:
*
*   1. `max(deriv(v(...)))` over the observation window: the steepest
*      dV/dt the node reaches. Needs no edge identification at all, which
*      matters on `xo`, whose transitions are the XOR of two independent
*      rings and are therefore NOT periodic and can include narrow runt
*      pulses that a `rise=N` edge count would mis-pair.
*   2. A 40 %-to-60 % band crossing time on the RING node (`ro1`),
*      which IS periodic and runt-free, giving an average slew across the
*      decision band rather than at the single steepest point.
*
* Method 2 exists to keep method 1 honest: a numerically differentiated
* transient can spike, and if the two methods agree on the ring node then
* method 1 is not being inflated by differentiation noise, which is what
* licenses reading method 1's answer on `xo` where method 2 cannot safely
* be applied. Both are reported; neither is discarded.
*
* Window: the transient runs from t = 0 (the ring has to start) but only
* saves from t = 40 ns, by which point a starved ring of this design is in
* steady state (sim/tb/ro-array-core-power/'s header measures that settling
* at ~20 ns). Everything measured here is therefore a steady-state figure,
* and the start-up transient cannot contaminate a max-of-derivative.
*
* bv40/bv60 are measurement-only supply-referred band edges, the same
* construction as ro-array-core-power's mid-supply `bvth` probe, so the
* band tracks the supply instead of being hardcoded at one corner's volts.
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

bvth vth 0 v = 0.5*vdd_val
bv40 v40 0 v = 0.4*vdd_val
bv60 v60 0 v = 0.6*vdd_val

.ic v(xdut.xr1.n1)=0
.ic v(xdut.xr2.n1)=0
