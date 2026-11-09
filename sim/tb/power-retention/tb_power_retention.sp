* power-retention -- retained state and measured gated-domain idle (issue #790), deterministic.
*
* Builds the always-on set of design/power-intent.md from real cells (three gf180mcu 9-track cells in
* sim/tb/power-retention/retention_cells.spice): five retained flops (dffrnq_1: ctrl_en, ctrl_out_mode_raw, fail_rct,
* fail_apt, fail_ring; written 1,0,1,0,1), the retention clock gate (icgtp_1) and 66 isolation ANDs
* (and2_1), all on the always-on rail vdd. The gated domain is design/power_switch.spice (400 um header)
* with the #707 leakage-equivalent load (710 um off NFET). Two independent groups share only the ideal supply.
*
* Group F (function, 30 us). The gated rail is FORCED (ideal source vvf, 1 -> 0 over 1 us at 8 us, back at
*   19 us): the real rail decays over ms..s (sim/characterization-power-switch.md section 6) and t_rail_decay is
*   an open item, so decay is not exercised here. Sequence (us), design/power-intent.md: write 0-3;
*   ret_clk_off 5; iso assert 6; pwr_off 8; pwr_on 19; iso release 20; ret_clk_on 22. The gated side drives each
*   flop's D: the pattern while wr=1, then Q (hold) while the rail is up, 0 while it is down. `good` takes the
*   gated clock; `bad` takes the free-running clock (the ret_clk_on fixture of power_intent_check.py) and is
*   the discriminating control: it must lose the ones. One isolation AND with its gated-side input held at
*   vdd (worst case) shows the clamp: it must read 0 while iso_n = 0.
* Group I (idle, 20 us). The 400 um switch is OFF from the DC operating point with the leakage-equivalent load on
*   its rail (which floats to where the two leakages meet, as in #707). The always-on set holds the pattern
*   (written while the gate is open, closed at 5 us); the gated side's D falls to 0 at 5.5 us, and the 66 isolation ANDs see
*   the rail on their gated-side input with iso_n = 0. The sample clock is parked low 8-14 us (static reading)
*   and toggles at 1 MHz 16-20 us with the gate closed (clock-input cost). Idle = always-on set (vwai) +
*   switch with its load (vwsi); the analog block's idle is added by sim/tools/power_retention.py from its
*   own record, as in #707.
*
* Every group has its own 0 V ammeter in its supply lead. Sources that stand for the gated domain's logic
* (pattern, hold feedback, isolation inputs) are ideal and draw from no rail. The 66-line isolation bank
* and the per-flop lines are uniform repeats of one line.

.include "../../../design/power_switch.spice"
.include "retention_cells.spice"

.param sw_stat_global=0 sw_stat_mismatch=0 mc_skew=3 res_mc_skew=3 cap_mc_skew=3 fnoicor=0
.param wleak=71

vsup vdd 0 dc 3.63
vss vss 0 0

* 1 MHz sample-clock shape (unit)
vck ck 0 pulse(0 1 0.25u 5n 5n 0.5u 1u)

* ---------------- Group F: function over a power cycle -----------------
vwr  wr  0 pwl(0 1 3u 1 3.01u 0)
vre  re  0 pwl(0 1 5u 1 5.01u 0 22u 0 22.01u 1)
vio  io  0 pwl(0 1 6u 1 6.01u 0 20u 0 20.01u 1)
vrf  rf  0 pwl(0 1 8u 1 9u 0 19u 0 19.1u 1)
bclk  clk    0 v = v(vdd)*v(ck)
bre   ret_en 0 v = v(vdd)*v(re)
bio   iso_nf 0 v = v(vdd)*v(io)
bvf   vvf    0 v = v(vdd)*v(rf)
vwf vdd daf 0
xicgf clk ret_en vss clkr daf daf vss vss gf180mcu_fd_sc_mcu9t5v0__icgtp_1
bdg1 dg1 0 v = v(vvf)*(v(wr)*1 + (1-v(wr))*(v(qg1) > v(vdd)/2 ? 1 : 0))
xfg1 dg1 daf clkr qg1 daf daf vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bdb1 db1 0 v = v(vvf)*(v(wr)*1 + (1-v(wr))*(v(qb1) > v(vdd)/2 ? 1 : 0))
xfb1 db1 daf clk qb1 daf daf vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bdg2 dg2 0 v = v(vvf)*(v(wr)*0 + (1-v(wr))*(v(qg2) > v(vdd)/2 ? 1 : 0))
xfg2 dg2 daf clkr qg2 daf daf vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bdb2 db2 0 v = v(vvf)*(v(wr)*0 + (1-v(wr))*(v(qb2) > v(vdd)/2 ? 1 : 0))
xfb2 db2 daf clk qb2 daf daf vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bdg3 dg3 0 v = v(vvf)*(v(wr)*1 + (1-v(wr))*(v(qg3) > v(vdd)/2 ? 1 : 0))
xfg3 dg3 daf clkr qg3 daf daf vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bdb3 db3 0 v = v(vvf)*(v(wr)*1 + (1-v(wr))*(v(qb3) > v(vdd)/2 ? 1 : 0))
xfb3 db3 daf clk qb3 daf daf vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bdg4 dg4 0 v = v(vvf)*(v(wr)*0 + (1-v(wr))*(v(qg4) > v(vdd)/2 ? 1 : 0))
xfg4 dg4 daf clkr qg4 daf daf vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bdb4 db4 0 v = v(vvf)*(v(wr)*0 + (1-v(wr))*(v(qb4) > v(vdd)/2 ? 1 : 0))
xfb4 db4 daf clk qb4 daf daf vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bdg5 dg5 0 v = v(vvf)*(v(wr)*1 + (1-v(wr))*(v(qg5) > v(vdd)/2 ? 1 : 0))
xfg5 dg5 daf clkr qg5 daf daf vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bdb5 db5 0 v = v(vvf)*(v(wr)*1 + (1-v(wr))*(v(qb5) > v(vdd)/2 ? 1 : 0))
xfb5 db5 daf clk qb5 daf daf vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bgf gf 0 v = v(vdd)
xisf gf iso_nf zf daf daf vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1

* ---------------- Group I: idle with the gated domain off ----------------
eoff soff 0 vdd 0 1
vwsi vdd dsi 0
xsti soff dsi vsti power_switch wf=10u nfing=40 lsw=0.28u
xnsti vsti 0 0 0 nfet_03v3 w=10u l=0.28u m=wleak
vld  ld   0 pwl(0 1 5.5u 1 5.51u 0)
vei  ei   0 pwl(0 1 5u 1 5.01u 0)
vcr  ckrun 0 pwl(0 1 8u 1 8.01u 0 14u 0 14.01u 1)
vio2 io2  0 pwl(0 1 6u 1 6.01u 0)
beI  ret_eni 0 v = v(vdd)*v(ei)
bcI  clki   0 v = v(vdd)*v(ck)*v(ckrun)
bioi iso_ni 0 v = v(vdd)*v(io2)
bgi  gin    0 v = v(vsti)
vwai vdd dai 0
xicgi clki ret_eni vss clkri dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__icgtp_1
bdi1 di1 0 v = v(vdd)*v(ld)*1
xfi1 di1 dai clkri qi1 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bdi2 di2 0 v = v(vdd)*v(ld)*0
xfi2 di2 dai clkri qi2 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bdi3 di3 0 v = v(vdd)*v(ld)*1
xfi3 di3 dai clkri qi3 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bdi4 di4 0 v = v(vdd)*v(ld)*0
xfi4 di4 dai clkri qi4 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
bdi5 di5 0 v = v(vdd)*v(ld)*1
xfi5 di5 dai clkri qi5 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__dffrnq_1
xiso1 gin iso_ni zi1 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso2 gin iso_ni zi2 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso3 gin iso_ni zi3 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso4 gin iso_ni zi4 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso5 gin iso_ni zi5 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso6 gin iso_ni zi6 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso7 gin iso_ni zi7 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso8 gin iso_ni zi8 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso9 gin iso_ni zi9 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso10 gin iso_ni zi10 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso11 gin iso_ni zi11 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso12 gin iso_ni zi12 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso13 gin iso_ni zi13 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso14 gin iso_ni zi14 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso15 gin iso_ni zi15 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso16 gin iso_ni zi16 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso17 gin iso_ni zi17 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso18 gin iso_ni zi18 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso19 gin iso_ni zi19 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso20 gin iso_ni zi20 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso21 gin iso_ni zi21 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso22 gin iso_ni zi22 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso23 gin iso_ni zi23 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso24 gin iso_ni zi24 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso25 gin iso_ni zi25 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso26 gin iso_ni zi26 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso27 gin iso_ni zi27 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso28 gin iso_ni zi28 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso29 gin iso_ni zi29 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso30 gin iso_ni zi30 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso31 gin iso_ni zi31 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso32 gin iso_ni zi32 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso33 gin iso_ni zi33 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso34 gin iso_ni zi34 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso35 gin iso_ni zi35 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso36 gin iso_ni zi36 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso37 gin iso_ni zi37 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso38 gin iso_ni zi38 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso39 gin iso_ni zi39 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso40 gin iso_ni zi40 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso41 gin iso_ni zi41 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso42 gin iso_ni zi42 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso43 gin iso_ni zi43 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso44 gin iso_ni zi44 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso45 gin iso_ni zi45 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso46 gin iso_ni zi46 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso47 gin iso_ni zi47 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso48 gin iso_ni zi48 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso49 gin iso_ni zi49 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso50 gin iso_ni zi50 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso51 gin iso_ni zi51 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso52 gin iso_ni zi52 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso53 gin iso_ni zi53 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso54 gin iso_ni zi54 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso55 gin iso_ni zi55 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso56 gin iso_ni zi56 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso57 gin iso_ni zi57 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso58 gin iso_ni zi58 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso59 gin iso_ni zi59 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso60 gin iso_ni zi60 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso61 gin iso_ni zi61 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso62 gin iso_ni zi62 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso63 gin iso_ni zi63 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso64 gin iso_ni zi64 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso65 gin iso_ni zi65 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
xiso66 gin iso_ni zi66 dai dai vss vss gf180mcu_fd_sc_mcu9t5v0__and2_1
