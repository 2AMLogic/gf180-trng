* ro-array-core-pvt-q -- the shipped entropy-source array over the FULL
* covered PVT grid, deterministic.
*
* DUT: design/ro_array_core.spice, exported from design/xschem/ro_array_core.sch
* by design/netlist.py -- the same DUT sim/tb/ro-array-core-power/
* measures, with the same rails, the same enable/.ic start-up kick, the
* same per-branch charge integrators and the same mid-supply crossing
* probe. This fragment is that testbench's fragment verbatim except for
* this header; every method note in
* sim/tb/ro-array-core-power/tb_ro_array_core_power.sp applies here
* unchanged and is not repeated.
*
* Why a SECOND testbench rather than an edit to that one (issue #13).
* ro-array-core-power's transient window is `tran 1p 50n` and it reads the
* ring period between the 2nd and 6th rising edge. That fits comfortably
* at the three PVT points it was run at (T0 = 4.3-7.1 ns, so the 6th edge
* lands at ~26-43 ns) and does not fit at all in the slow half of the grid:
* at ss/125 C/2.97 V the starved ring's period is several times longer and
* the 6th rising edge falls outside a 50 ns window, so `meas` returns no
* value and the point cannot be measured at all with that manifest.
*
* Issue #13 needs the whole covered grid ({tt, ff, ss} x {-40, 27, 125} C x
* {2.97, 3.30, 3.63} V -- fs/sf stay out, per DR-0006), because the
* entropy-binding corner claim it has to confirm is a claim about a
* MINIMUM over that grid, and a minimum is only as trustworthy as the set
* it was taken over. So this manifest widens the window to `tran 5p 300n`:
*   - 300 ns is long enough for the 6th rising edge at the slowest measured
*     corner with margin to spare (the slowest point on this grid oscillates
*     at ~30 ns/period, so its 6th edge lands near 180 ns);
*   - the print/`tmax` step relaxes 1 ps -> 5 ps so the solver-step count,
*     and therefore the per-point cost, stays at the same ~60k steps a 50 ns
*     / 1 ps run already paid -- a 300 ns / 1 ps run would have been 6x the
*     cost per point on a 27-point grid.
*
* The 1 ps -> 5 ps relaxation is a methodology change, so it is CHECKED
* rather than asserted: three of this grid's points (tt/27/3.30,
* ff/-40/3.63, ss/-40/3.63) are exactly the points sim/tb/ro-array-core-power/
* already has committed records for, and sim/tools/worst_corner_entropy.py
* reports the per-quantity agreement between the two families at those
* points. A 5 ps ceiling still resolves this array's ~0.5 ns edges with
* ~100 solver steps, and both period and integrated charge are read from
* like-edged crossings an exact integer number of periods apart, which is
* the construction that makes them insensitive to where inside an edge a
* sample happens to land.
*
* What this testbench does NOT change: it measures exactly the quantities
* ro-array-core-power measures, by the same expressions, so a record from
* either family is usable in DR-0007 SS2's sizing inequality without
* conversion. It is a window/step change, not a new measurement.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vtr vsup vdd dc 0

xdut en en vddr1 vddr2 vdd 0 xo ro_array_core

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
