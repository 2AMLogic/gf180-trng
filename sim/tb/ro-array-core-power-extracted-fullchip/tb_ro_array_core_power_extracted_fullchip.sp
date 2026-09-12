* ro-array-core-power-extracted-fullchip -- issue #232's full-chip
* (inter-region) delta post-layout re-run of
* sim/tb/ro-array-core-power-extracted-routed/ against
* layout/pex/sampler_core.fullchip.extracted.spice. See
* sim/tb/ro-array-core-pvt-q-extracted-fullchip/'s own header for the full
* rationale (sampler_core-based composition, xdut.xcs.<net> addressing,
* static clk/rst_n tie and its disclosed scope-broadening consequence on
* p_total_w) -- unchanged here beyond the corner/window below.
*
* ro-array-core-power -- active power at the array's fastest corner,
* deterministic.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val
vclk clk 0 dc 0
vrst rst_n 0 dc vdd_val

vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vtr vsup vdd dc 0

xdut en en vddr1 vddr2 vdd 0 clk rst_n rb rv rbit1 rbit2 0 sampler_core_fullchip_extracted

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
