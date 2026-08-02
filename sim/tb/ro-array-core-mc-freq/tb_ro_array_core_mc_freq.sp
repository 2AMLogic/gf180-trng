* ro-array-core-mc-freq -- the shipped entropy-source array, Monte Carlo
* device mismatch: per-ring period spread across virtual chip samples.
*
* DUT: design/ro_array_core.spice (same subckt sim/tb/ro-array-core-power/
* characterizes deterministically). This fragment is that testbench's
* fragment unchanged -- only tb.json's analysis_type/extra_lib_sections/
* design_params differ, so a "virtual chip sample" here means "the same
* deterministic bias network, with device parameters redrawn from the
* PDK's mismatch distribution under a fresh ngspice ``.option seed``".
*
* Why this exists (issue #13). DR-0007 SS1 requires the array's two rings
* to stay at deliberately non-integer frequency ratios (injection-locking
* avoidance) and SS7/SS16 make per-ring independence/isolation a design
* obligation, not an assumption. Neither obligation has ever been checked
* against device MISMATCH specifically: the periods reported by
* sim/tb/ro-array-core-power/ are for ONE (mean, mismatch-free) device
* draw per corner. This testbench redraws devices ``default_runs`` times
* under gf180mcu's ``statistical`` library section (local, intra-die
* mismatch -- see design.ngspice's sw_stat_mismatch documentation) and
* reports the resulting period_r1/period_r2 spread, so a reader can see
* whether mismatch alone could plausibly pull the two rings' periods close
* enough to defeat the non-integer-ratio requirement on some fraction of
* fabricated parts.
*
* Scope (explicit, not silently narrowed): ONE PVT corner only (tt/27 C/
* 3.30 V nominal). gf180mcu's ``statistical`` section models intra-die
* mismatch on top of whichever corner's devices are loaded; running it at
* every PVT corner in addition to every mismatch seed multiplies an
* already re-drawn-per-seed cost by the corner count for a question (does
* mismatch alone move the ratio) that DR-0006's own reduced-grid precedent
* treats as a headline-corner question, not a full-grid one. If a later
* finding needs the other corners, re-run explicitly rather than silently
* assuming this record covers them.
*
* Reuses sim/tb/ro-array-core-power/tb_ro_array_core_power.sp's exact
* measurement method (hierarchical per-ring probes, integer-period charge
* integration, mid-supply crossing reference) -- see that testbench's
* header for the method notes, unchanged here.

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
