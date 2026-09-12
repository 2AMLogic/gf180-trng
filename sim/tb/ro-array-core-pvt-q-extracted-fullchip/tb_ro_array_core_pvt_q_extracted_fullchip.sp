* ro-array-core-pvt-q-extracted-fullchip -- issue #232's full-chip
* (inter-region) delta post-layout re-run of
* sim/tb/ro-array-core-pvt-q-extracted-routed/ against
* layout/pex/sampler_core.fullchip.extracted.spice: DR-0025's ro1/ro2
* inter-region trunk delta inserted between each ring wrapper's own `ro`
* port and combiner_sampler_routed_extracted's `rn1`/`rn2` (see
* layout/pex/build.py's own module docstring, "Full-chip (inter-region)
* delta composition", and layout/pex/reports/fullchip_parasitics.json).
*
* Unlike the *_extracted_routed family, this DUT is composed from
* sampler_core's own topology (not ro_array_core's), because
* combiner_sampler -- not a leaf ro_buf -- is the physical block DR-0025's
* own delta is anchored to (its rn1/rn2 stub is what the trunk's own
* subtracted intra-region part is). `xo`/`ro1`/`ro2` (the buffered ring
* outputs this family's own measurement expressions reference) are
* therefore addressed one hierarchy hop deeper than the *_extracted_routed
* family, at `xdut.xcs.<net>` (combiner_sampler_routed_extracted's own
* internal, positively-identified net names -- layout/pex/build.py's own
* `_resolve_combiner_sampler_ports`), not at a top-level DUT pin.
*
* clk/rst_n are tied STATIC (clk=0, rst_n=vdd_val -- clock parked low,
* reset deasserted) rather than toggled: this family measures the ring
* array's own oscillation, unaffected by whether the samplers clock, and a
* static tie avoids adding unrelated switching activity. Disclosed
* consequence (tb.json's own caveats): the four sampler_dff instances' own
* static bias current is now included in vtr's measured current, because
* this DUT's vdd rail is the fully assembled combiner_sampler block (both
* buffers, the XOR and all four samplers), not ro_array_core's
* rings+XOR-only rail -- a disclosed SCOPE BROADENING relative to the
* *_extracted_routed family's own p_total_w, not a regression on it.
*
* ro-array-core-pvt-q -- the shipped entropy-source array over the worst
* (minimum-Q) corner, deterministic.

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
