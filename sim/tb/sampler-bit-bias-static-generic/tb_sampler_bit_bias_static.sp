* sampler-bit-bias-static-generic -- issue #86.
*
* The CONTROL for sim/tb/sampler-bit-bias-clocked-generic/: the same
* circuit with the clk-locked modulation absent, sampled at the same
* instants by the same raw tap.
*
* The experiment, the circuit, the DUT provenance, the sample-reading method
* and every method note are documented ONCE, in the family's canonical deck
* sim/tb/sampler-bit-bias-clocked-generic/tb_sampler_bit_bias_clocked.sp.
* The circuit below is that deck's, with the one line noted below changed.
*
* What is different here: vclkm -- the source on the two liveness digitizers' clock pin -- is a DC
* rail at vdd instead of a running clock. One line.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

* ---- separate supply pins: per-ring (DR-0007 §1's own supply routing) ----
* ---- plus one for the buffers, combiner and samplers -------------------
vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vtr vsup vdd dc 0

* ---- ring 1 (wstv = 0.220u), per-stage series noise injection ----------
xg1 g10 en n11 vddr1 0 ro_nand2 wstv=0.220u lstv=2u cld=0.5f
x11 g11 n12 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x12 g12 n13 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x13 g13 n14 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x14 g14 rn1 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
vn10 rn1 g10 dc 0 trnoise( vn_rms vn_dt 0 0)
vn11 n11 g11 dc 0 trnoise( vn_rms vn_dt 0 0)
vn12 n12 g12 dc 0 trnoise( vn_rms vn_dt 0 0)
vn13 n13 g13 dc 0 trnoise( vn_rms vn_dt 0 0)
vn14 n14 g14 dc 0 trnoise( vn_rms vn_dt 0 0)

* ---- ring 2 (wstv = 0.240u), the skewed twin -------------------------
xg2 g20 en n21 vddr2 0 ro_nand2 wstv=0.240u lstv=2u cld=0.5f
x21 g21 n22 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x22 g22 n23 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x23 g23 n24 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x24 g24 rn2 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
vn20 rn2 g20 dc 0 trnoise( vn_rms vn_dt 0 0)
vn21 n21 g21 dc 0 trnoise( vn_rms vn_dt 0 0)
vn22 n22 g22 dc 0 trnoise( vn_rms vn_dt 0 0)
vn23 n23 g23 dc 0 trnoise( vn_rms vn_dt 0 0)
vn24 n24 g24 dc 0 trnoise( vn_rms vn_dt 0 0)

* ---- DR-0018 per-ring output buffers (sampler_core's xb1/xb2) ---------
xb1 rn1 ro1 vdd 0 ro_buf
xb2 rn2 ro2 vdd 0 ro_buf

* ---- DR-0007 §1 combiner (sampler_core's xa1) -------------------------
xa1 ro1 ro2 xo vdd 0 xor2

* ---- the DR-0001 raw tap (sampler_core's xsb) -------------------------
xsb xo clk rst_n raw_bit vdd 0 sampler_dff

* ---- the DR-0016 per-ring liveness digitizers (sampler_core's xsr1/xsr2)
xsr1 ro1 clkm rst_n ring_bit1 vdd 0 sampler_dff
xsr2 ro2 clkm rst_n ring_bit2 vdd 0 sampler_dff

* ---- DR-0012's fixed external sample clock, driving the raw tap -------
vclk clk 0 dc 0 pulse(0 'vdd_val' tclk_del tclk_tr tclk_tr 'tclk_per/2 - tclk_tr' tclk_per)

* ---- THE ONE CHANGE: the liveness digitizers' clock, PARKED HIGH ------
* This is the ONLY line that differs from
* sim/tb/sampler-bit-bias-clocked-generic/tb_sampler_bit_bias_clocked.sp.
* Both digitizers are still instantiated and still load ro1/ro2 exactly as
* they do in the shipped netlist; their master transmission gate is simply
* held OFF instead of being walked on and off once per clk period. clk
* itself keeps running and keeps driving the raw tap xsb, so the bit is
* still sampled at the same instants -- what is absent is the clk-locked
* modulation of the rings, and nothing else.
vclkm clkm 0 dc vdd_val

vrst rst_n 0 dc vdd_val

* ---- measurement probes (measurement-only; no device is added) --------
* bx1/bx2 shift each RING node so a mid-supply crossing is a zero crossing;
* bxc does the same for clk, which is what indexes the samples; bvth is the
* decision threshold the recorded sample voltages are read against; btclk
* exposes the clk period to the control block, which cannot read a .param.
bx1 x1 0 v = v(rn1) - 0.5*vdd_val
bx2 x2 0 v = v(rn2) - 0.5*vdd_val
bxc xc 0 v = v(clk) - 0.5*vdd_val
bvth vth 0 v = 0.5*vdd_val
btclk tclkv 0 v = tclk_per

.ic v(n11)=0
.ic v(n21)=0
