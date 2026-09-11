* ro-array-core-pvt-q-extracted-routed -- issue #217's routing-level
* post-layout re-run of sim/tb/ro-array-core-pvt-q-extracted/ against
* layout/pex/ro_array_core.routed.extracted.spice instead of
* layout/pex/ro_array_core.extracted.spice. Byte-identical to that
* testbench's own fragment except this header and the `xdut` line naming
* `ro_array_core_routed_extracted`. No measurement expression changes --
* `xdut.xr1.n1`/`xdut.xr2.n1` remain valid addresses: `ro_ring11_routed_
* extracted`/`ro_ring11_ring2_routed_extracted` (layout/pex/build.py) are
* thin wrapper subckts exposing the same five true ports (en, ro, vddr,
* vss, vsubs) and the same n1..n10 internal-node naming convention as the
* leaf-composed ro_ring11_extracted/ro_ring11_ring2_extracted did -- see
* layout/pex/build.py's own module docstring, "Routing-level composition".
* `n1`/`n2` here now name an arbitrary (klt-assigned) internal ring
* position rather than specifically "the node between stage 1 and stage 2"
* (unlike the leaf-composed netlist's chain-position-ordered n1..n10) --
* they are not measured by this deck's own `.ic` initial-condition kick,
* which only needs SOME internal node to break the ring's symmetric
* all-equal start.
*
* What "routing-level" means here, and its limits: see
* sim/characterization-post-layout-extracted.md's 2026-09-11 delta section
* and layout/pex/build.py's own module docstring. In short -- both rings'
* real hand-routed inter-stage metal1 chain and metal2/via1 vddr/vss straps
* are now captured (layout/rings/README.md); the buffer/XOR stage is not
* (still leaf-level); inter-region routing is not (still unrouted in the
* committed floorplan).
*
* ro-array-core-pvt-q -- the shipped entropy-source array over the FULL
* covered PVT grid, deterministic.
*
* Node-naming note (#65, carried through unchanged from the leaf-level
* family): ro_array_core now exposes its two per-ring nodes as
* observation-only output pins (ro1/ro2).

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
