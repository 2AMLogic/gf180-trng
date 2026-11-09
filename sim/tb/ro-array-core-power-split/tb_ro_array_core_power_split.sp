* ro-array-core-power-split -- the shipped array's `vdd` rail split into its
* three loads (issue #811, part of #700). Measurement only.
*
* Why. design/ro_array_core.spice hangs both ro_buf instances (xb1, xb2) and the
* xor2 (xa1) on the single `vdd` pin, and ro-array-core-pvt-q meters that pin with
* one zero-volt source (vtr). Its `i_tree_a` -- and so `p_total_w - p_rings_w`,
* the "ring buffers + XOR" row of sim/tools/active_power_breakdown.py -- is
* therefore buffers + XOR together. This deck keeps the shipped topology
* (ro_ring11 x2, ro_buf x2, xor2 x1, the same connectivity and ring `wstv`
* values) and changes ONE thing: the `vdd` rail is split into three zero-volt
* metered rails, vddb1 and vddb2 (the buffers) and vddx (the XOR).
*
* Everything else is sim/tb/ro-array-core-pvt-q/'s deck: the same rails, the same
* enable and .ic start-up kick, the same `tran 5p 300n` window, the same edge
* pairing (rise 2 to rise 6 on ro1) and the same per-branch charge integrators.
* The branch sources are zero-impedance taps off the same ideal vsup, so the
* split adds no electrical path. `vtr` is gone: the sum of the three branch
* currents is the pvt-q `i_tree_a`, and tb.json reports that sum under the same
* name so the reconcile compares like for like.
*
* The deck instantiates the subcircuits directly rather than ro_array_core
* because the composed subckt has one `vdd` pin and no splice point; a unit test
* (sim/tests/test_active_power_breakdown.py) pins this deck's instance set and
* connectivity to design/ro_array_core.spice so a copy cannot drift.
*
* The XOR inputs are the free-running rings' own buffered outputs (ro1, ro2),
* as in the shipped array.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vb1 vsup vddb1 dc 0
vb2 vsup vddb2 dc 0
vx vsup vddx dc 0

xr1 en rn1 vddr1 0 ro_ring11 wstv=0.220u lstv=2u cld=0.5f
xr2 en rn2 vddr2 0 ro_ring11 wstv=0.240u lstv=2u cld=0.5f
xb1 rn1 ro1 vddb1 0 ro_buf
xb2 rn2 ro2 vddb2 0 ro_buf
xa1 ro1 ro2 xo vddx 0 xor2

fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fq2 q2 0 vr2 1
cq2 q2 0 1n
rq2 q2 0 1e12
fqb1 qb1 0 vb1 1
cqb1 qb1 0 1n
rqb1 qb1 0 1e12
fqb2 qb2 0 vb2 1
cqb2 qb2 0 1n
rqb2 qb2 0 1e12
fqx qx 0 vx 1
cqx qx 0 1n
rqx qx 0 1e12

bvth vth 0 v = 0.5*vdd_val

.ic v(xr1.n1)=0
.ic v(xr2.n1)=0
.ic v(q1)=0
.ic v(q2)=0
.ic v(qb1)=0
.ic v(qb2)=0
.ic v(qx)=0
