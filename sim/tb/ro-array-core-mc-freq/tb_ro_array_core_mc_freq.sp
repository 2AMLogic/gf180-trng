* ro-array-core-mc-freq -- the shipped entropy-source array, Monte Carlo
* device mismatch: per-ring period spread across virtual chip samples.
*
* DUT: design/ro_array_core.spice (same subckt sim/tb/ro-array-core-power/
* characterizes deterministically). This fragment is that testbench's
* fragment unchanged -- only tb.json's analysis_type/design_params/corners/
* temperatures_c differ, so a "virtual chip sample" here means "the same
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
* under gf180mcu's per-corner ``sw_stat_mismatch``-gated local (Pelgrom)
* mismatch model (see design.ngspice's sw_stat_mismatch documentation) and
* reports the resulting period_r1/period_r2 spread, so a reader can see
* whether mismatch alone could plausibly pull the two rings' periods close
* enough to defeat the non-integer-ratio requirement on some fraction of
* fabricated parts.
*
* Scope (explicit, not silently narrowed; issue #146). TWO PVT points, not
* a full corner sweep: tt/27 C/3.30 V (nominal) and ss/125 C/3.63 V
* (DR-0015's own measured entropy-binding worst corner over this array's
* full covered PVT grid). Running every mismatch seed at every point of the
* harness's full `mos` corner set (tt/ff/ss/fs/sf) x 3 temperatures x 3
* supplies (45 points) would be affordable in wall-clock terms at this
* testbench's per-seed cost, but was not run -- DR-0006's own reduced-grid
* precedent treats "does mismatch alone move the ratio" as a headline-corner
* question, not a full-grid one, and these two points are the ones a reader
* most needs: the pre-existing baseline and the corner DR-0015 already flags
* as worst. If a later finding needs the other corners, re-run explicitly
* rather than silently assuming this record covers them. Until #146,
* `corners` in the nominal-only version of this manifest was bookkeeping
* only -- `extra_lib_sections: ["statistical"]` unconditionally overrode
* whichever corner's own per-family sections would otherwise load, so any
* non-`tt` corner would have silently simulated the same devices as `tt`
* under the old mechanism (see tb.json's caveats for the fix).
*
* Reuses sim/tb/ro-array-core-power/tb_ro_array_core_power.sp's exact
* measurement method (per-ring node probes, integer-period charge
* integration, mid-supply crossing reference) -- see that testbench's
* header for the method notes, unchanged here.
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
