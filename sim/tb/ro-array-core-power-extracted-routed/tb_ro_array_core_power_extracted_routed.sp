* ro-array-core-power-extracted-routed -- issue #217's routing-level
* post-layout re-run of sim/tb/ro-array-core-power-extracted/ against
* layout/pex/ro_array_core.routed.extracted.spice. Byte-identical to that
* testbench's own fragment except this header and the `xdut` line naming
* `ro_array_core_routed_extracted`. No measurement expression changes --
* see sim/tb/ro-array-core-pvt-q-extracted-routed/'s own header for why
* `xdut.xr1.n1`/`xdut.xr2.n1` remain valid addresses under the routed
* composition. See sim/characterization-post-layout-extracted.md's
* 2026-09-11 delta section and layout/pex/build.py's own module docstring
* for scope/limits.
*
* ro-array-core-power -- the shipped entropy-source array, deterministic.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vtr vsup vdd dc 0

xdut en en vddr1 vddr2 vdd 0 xo ro1 ro2 0 ro_array_core_routed_extracted

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
