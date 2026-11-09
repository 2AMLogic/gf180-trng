* power-switch -- PMOS header for the digital section (issue #707), deterministic.
*
* DUT: design/power_switch.spice, exported from design/xschem/power_switch.sch by
* design/netlist.py. Nothing about the DUT is redefined here; this fragment
* supplies the rail, the sleep drive, and the loads. One transient run per PVT point
* holds four independent groups of instances that share only the ideal supply.
*
* Group R (on-resistance, droop). sleep = 0, four total widths (100, 200, 400,
*   800 um = 10, 20, 40, 80 fingers of 10u) at each of two DC loads:
*     A  96.7 uA   the largest digital current at the ratified 1 MHz rate
*                  (sim/characterization-digital-supply-ir-drop.md, ff/+125 C)
*     B  1.893 mA  the largest at the 20 MHz implementation clock (informational)
*   Measured: v(vdd) - v(vvdd) at t = 2.9 us.
* Group L (off-state leakage). sleep = vdd. The same four widths with vvdd held
*   at 0 V through an ammeter, which is the worst case (the full supply across the
*   switch), plus the 400 um switch driving a leakage-equivalent digital load, which
*   is the gated-domain idle case (the virtual rail floats to where the two
*   leakages meet). The load is an off NFET of 710 um at L = 0.28 um, sized so
*   that, alone across the full supply, it draws about the 2.18 uA DR-0017 and
*   DR-0023 attribute to the digital section at ff / +125 C / 3.63 V. It is a MODEL
*   of that leakage, not the cells: it carries the PDK's own corner, temperature
*   and drain-bias dependence, not the Liberty library's. The load alone is also
*   measured, as the ungated reference.
* Group W (wake). sleep falls from vdd to 0 starting at 100 ns, over a fall time
*   trf, with the virtual rail loaded by the leakage-equivalent load and by a
*   decoupling-plus-gate capacitance cdig. Two cdig (50 pF, 200 pF) and two trf
*   (10 ns, 1 us), 400 um switch. The capacitances are ASSUMPTIONS, not extracted
*   (the digital section has no extracted supply capacitance in this repo): 50 pF
*   is about 1655 cells at 30 fF each, 200 pF brackets added well and decoupling
*   capacitance. Measured: peak supply current, and the time for vvdd to reach 95 %
*   of vdd, counted from the start of the sleep fall.
*
* Method notes:
*   - Every switch instance has its own 0 V ammeter in its supply lead (vwN), so
*     its current is read separately.
*   - The sleep drive is a behavioural source built from v(vdd), so it follows the
*     swept supply (sleep high = vdd = OFF, sleep low = 0 V = ON).
*   - All loads sit on vvdd; the switch bulk is vdd (design/xschem/power_switch.sch).

.include "../../../design/power_switch.spice"

.param sw_stat_global=0 sw_stat_mismatch=0 mc_skew=3 res_mc_skew=3 cap_mc_skew=3 fnoicor=0
.param iA=96.7u iB=1.893m wleak=71

vsup vdd 0 dc 3.63

* sleep levels: OFF = vdd, ON = 0
eoff soff 0 vdd 0 1
von son 0 dc 0

* ---------------- Group R: on-resistance and droop -----------------------
vwr1a vdd dr1a 0
xr1a son dr1a vr1a power_switch wf=10u nfing=10 lsw=0.28u
ir1a vr1a 0 dc iA
vwr1b vdd dr1b 0
xr1b son dr1b vr1b power_switch wf=10u nfing=10 lsw=0.28u
ir1b vr1b 0 dc iB
vwr2a vdd dr2a 0
xr2a son dr2a vr2a power_switch wf=10u nfing=20 lsw=0.28u
ir2a vr2a 0 dc iA
vwr2b vdd dr2b 0
xr2b son dr2b vr2b power_switch wf=10u nfing=20 lsw=0.28u
ir2b vr2b 0 dc iB
vwr4a vdd dr4a 0
xr4a son dr4a vr4a power_switch wf=10u nfing=40 lsw=0.28u
ir4a vr4a 0 dc iA
vwr4b vdd dr4b 0
xr4b son dr4b vr4b power_switch wf=10u nfing=40 lsw=0.28u
ir4b vr4b 0 dc iB
vwr8a vdd dr8a 0
xr8a son dr8a vr8a power_switch wf=10u nfing=80 lsw=0.28u
ir8a vr8a 0 dc iA
vwr8b vdd dr8b 0
xr8b son dr8b vr8b power_switch wf=10u nfing=80 lsw=0.28u
ir8b vr8b 0 dc iB

* ---------------- Group L: off-state leakage -----------------------------
* vvdd forced to 0 V: the worst case, the full supply across the switch.
xl1 soff vdd vl1 power_switch wf=10u nfing=10 lsw=0.28u
vl1 vl1 0 dc 0
xl2 soff vdd vl2 power_switch wf=10u nfing=20 lsw=0.28u
vl2 vl2 0 dc 0
xl4 soff vdd vl4 power_switch wf=10u nfing=40 lsw=0.28u
vl4 vl4 0 dc 0
xl8 soff vdd vl8 power_switch wf=10u nfing=80 lsw=0.28u
vl8 vl8 0 dc 0
* gated-domain idle: 400 um switch off, leakage-equivalent load on vvdd.
vwst vdd dst 0
xst soff dst vst power_switch wf=10u nfing=40 lsw=0.28u
xnst vst 0 0 0 nfet_03v3 w=10u l=0.28u m=wleak
* the same load with no switch (ungated reference).
vwun vdd dun 0
xnun dun 0 0 0 nfet_03v3 w=10u l=0.28u m=wleak

* ---------------- Group W: wake -------------------------------------------
* unit ramps (1 -> 0 starting at 100 ns, over 10 ns and over 1 us), scaled by the supply.
vrma rma 0 pwl(0 1 100n 1 110n 0 10u 0)
vrmb rmb 0 pwl(0 1 100n 1 1.1u 0 10u 0)
bsa sla 0 v = v(vdd)*v(rma)
bsb slb 0 v = v(vdd)*v(rmb)
vww1 vdd dw1 0
xw1 sla dw1 vw1 power_switch wf=10u nfing=40 lsw=0.28u
cw1 vw1 0 50p
xnw1 vw1 0 0 0 nfet_03v3 w=10u l=0.28u m=wleak
vww2 vdd dw2 0
xw2 sla dw2 vw2 power_switch wf=10u nfing=40 lsw=0.28u
cw2 vw2 0 200p
xnw2 vw2 0 0 0 nfet_03v3 w=10u l=0.28u m=wleak
vww3 vdd dw3 0
xw3 slb dw3 vw3 power_switch wf=10u nfing=40 lsw=0.28u
cw3 vw3 0 50p
xnw3 vw3 0 0 0 nfet_03v3 w=10u l=0.28u m=wleak
vww4 vdd dw4 0
xw4 slb dw4 vw4 power_switch wf=10u nfing=40 lsw=0.28u
cw4 vw4 0 200p
xnw4 vw4 0 0 0 nfet_03v3 w=10u l=0.28u m=wleak

* 95 % crossing detectors for the wake measurements (zero when v(vwN) = 0.95 vdd).
bc1 c1 0 v = v(vw1) - 0.95*v(vdd)
bc2 c2 0 v = v(vw2) - 0.95*v(vdd)
bc3 c3 0 v = v(vw3) - 0.95*v(vdd)
bc4 c4 0 v = v(vw4) - 0.95*v(vdd)
