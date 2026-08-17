* ro-array-core-mc-freq-control -- deterministic negative control for
* sim/tb/ro-array-core-mc-freq/: same DUT, same measurement, mismatch
* disabled (tb.json's design_params sets sw_stat_mismatch=0).
*
* Why this exists (issue #146). #146's acceptance criteria requires a
* deterministic negative control next to the mismatch-enabled MC spread --
* the thing that distinguishes a real MC result from a noisy one: if the
* mismatch draw were NOT actually doing anything (a wiring mistake, a
* switch that silently defaults off, ...), the "spread" the MC record
* reports would be an artifact and this control run would look identical
* to it instead of collapsing to zero. gf180mcu's per-corner device
* libraries compute their local (Pelgrom) mismatch offset unconditionally
* (``mis_vth=agauss(...)``) and only gate its effect on the device model by
* multiplying it by ``sw_stat_mismatch`` (see design.ngspice's
* documentation) -- with that switch at 0, the offset is always multiplied
* to exactly zero regardless of which ``.option seed`` is active, so this
* testbench's measurement is bit-for-bit identical across every seed. This
* deck is otherwise IDENTICAL to
* sim/tb/ro-array-core-mc-freq/tb_ro_array_core_mc_freq.sp -- see that
* file's header for the DUT, the measurement method, and the corner scope
* (the two same PVT points: tt/27 C/3.30 V and ss/125 C/3.63 V,
* DR-0015's binding corner).

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
