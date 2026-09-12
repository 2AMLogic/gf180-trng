* ro-array-core-startup-extracted-fullchip -- issue #232's full-chip
* (inter-region) delta post-layout re-run of
* sim/tb/ro-array-core-startup-extracted-routed/ against
* layout/pex/sampler_core.fullchip.extracted.spice. See
* sim/tb/ro-array-core-pvt-q-extracted-fullchip/'s own header for the full
* rationale (sampler_core-based composition, one-hierarchy-hop-deeper
* xdut.xcs.<net> addressing, static clk/rst_n tie and its disclosed
* consequence) -- unchanged here beyond the DUT/measurement-window
* differences below.
*
* Node-naming note, carried through from the *_extracted_routed family:
* the ring's own pre-delta output is `xdut.xr1.n1`-adjacent internally, but
* the signal this family measures (the buffer's own input, i.e. the ring's
* output AFTER the DR-0025 delta but BEFORE the buffer) is this
* composition's own top-level internal net `rn1`/`rn2` (between the delta
* and combiner_sampler_routed_extracted's own `xb1`/`xb2` instances) --
* addressed at `xdut.rn1`/`xdut.rn2`, the same single-hop convention the
* routing-level family already uses for that same conceptual node.
*
* ro-array-core-startup -- time-to-first-valid oscillator start-up,
* deterministic.

vsup vsup 0 dc vdd_val
ven en 0 dc 0 pulse(0 vdd_val 5n 1p 1p 10u 20u)
vclk clk 0 dc 0
vrst rst_n 0 dc vdd_val

xdut en en vsup vsup vsup 0 clk rst_n rb rv rbit1 rbit2 0 sampler_core_fullchip_extracted

bvth vth 0 v = 0.5*vdd_val
