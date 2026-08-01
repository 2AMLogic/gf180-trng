v {xschem version=3.4.4 file_version=1.2}
G {wstv=0.22u lstv=2u cld=0.5f}
K {}
V {}
S {}
E {}
T {ro_ring11 -- one ring of the entropy-source array: a starved NAND2 enable
stage followed by ten starved inverters, closed on itself.

Why eleven stages and not three. Under DR-0010's jitter-energy law the
entropy delivered per unit of ring power goes as the inverse SQUARE of the
energy switched per ring cycle, which is proportional to the stage count,
so three stages -- the minimum an inverting ring allows -- would be the
cheapest. The starved cell does not have the gain for it. ro_stage
measures a small-signal gain at its own trip point of 2.59 at 1 GHz at
nominal and 1.68 at ss/125 C/2.97 V (sim/records/2026-08-01-rostage-noise-
{01,04}.md), against the 2.0 per stage a three-stage ring needs to sustain
a rail-to-rail oscillation. Simulated directly, a three-stage ring of this
cell oscillates at ~45% of the supply and a five-stage one at ~79%; only
the eleven-stage ring reaches the rails (sim/records/2026-08-01-ro-array-
core-power-*.md, ring_swing_v). A ring that hands the XOR tree an analog
level is a sampler problem, and is not a trade this design makes for a
factor in the energy per cycle.

lstv = 2 um. The starve devices set the ring current, and therefore the
period, WITHOUT adding switched capacitance -- so they move the array's
power and its XOR-node transition density together at constant energy per
cycle. Longer is not better: at lstv = 6 um the four-ring array still
measures 939 uW against a < 500 uW row, worse per-transition tree energy
and a ring swing down to 3.19 V, because slower ring edges cost the
combining gates more short-circuit charge than the lower transition rate
saves (sim/records/2026-08-01-ro-array-core-power-{01,02,03}.md are the
2 um and 6 um measurements side by side). The array fits its power row by
ring COUNT, not by starve length; see ro_array_core.sch.

vddr is this ring's OWN supply pin (DR-0007's per-ring supply routing),
and doubles as the per-ring liveness observation point: a stopped ring's
supply current collapses by more than four orders of magnitude.} -700 -900 0 0 0.25 0.25 {}
C {ipin.sym} -700 -400 0 0 {name=p1 lab=en}
C {opin.sym} -600 -400 0 0 {name=p2 lab=ro}
C {iopin.sym} -700 -350 0 0 {name=p3 lab=vddr}
C {iopin.sym} -600 -350 0 0 {name=p4 lab=vss}
C {ro_nand2.sym} 0 0 0 0 {name=xg wstv=wstv lstv=lstv cld=cld}
C {ro_stage.sym} 300 0 0 0 {name=x1 wstv=wstv lstv=lstv cld=cld}
C {ro_stage.sym} 600 0 0 0 {name=x2 wstv=wstv lstv=lstv cld=cld}
C {ro_stage.sym} 900 0 0 0 {name=x3 wstv=wstv lstv=lstv cld=cld}
C {ro_stage.sym} 1200 0 0 0 {name=x4 wstv=wstv lstv=lstv cld=cld}
C {ro_stage.sym} 1500 0 0 0 {name=x5 wstv=wstv lstv=lstv cld=cld}
C {ro_stage.sym} 1800 0 0 0 {name=x6 wstv=wstv lstv=lstv cld=cld}
C {ro_stage.sym} 2100 0 0 0 {name=x7 wstv=wstv lstv=lstv cld=cld}
C {ro_stage.sym} 2400 0 0 0 {name=x8 wstv=wstv lstv=lstv cld=cld}
C {ro_stage.sym} 2700 0 0 0 {name=x9 wstv=wstv lstv=lstv cld=cld}
C {ro_stage.sym} 3000 0 0 0 {name=x10 wstv=wstv lstv=lstv cld=cld}
N 50 -10 250 -10 {lab=n1}
N 350 -10 550 -10 {lab=n2}
N 650 -10 850 -10 {lab=n3}
N 950 -10 1150 -10 {lab=n4}
N 1250 -10 1450 -10 {lab=n5}
N 1550 -10 1750 -10 {lab=n6}
N 1850 -10 2050 -10 {lab=n7}
N 2150 -10 2350 -10 {lab=n8}
N 2450 -10 2650 -10 {lab=n9}
N 2750 -10 2950 -10 {lab=n10}
N 3050 -10 3150 -10 {lab=ro}
N 3150 -10 3150 -140 {lab=ro}
N -150 -140 3150 -140 {lab=ro}
N -150 -140 -150 -30 {lab=ro}
N -150 -30 -50 -30 {lab=ro}
C {lab_pin.sym} 150 -10 0 0 {name=ln1 lab=n1}
C {lab_pin.sym} 450 -10 0 0 {name=ln2 lab=n2}
C {lab_pin.sym} 750 -10 0 0 {name=ln3 lab=n3}
C {lab_pin.sym} 1050 -10 0 0 {name=ln4 lab=n4}
C {lab_pin.sym} 1350 -10 0 0 {name=ln5 lab=n5}
C {lab_pin.sym} 1650 -10 0 0 {name=ln6 lab=n6}
C {lab_pin.sym} 1950 -10 0 0 {name=ln7 lab=n7}
C {lab_pin.sym} 2250 -10 0 0 {name=ln8 lab=n8}
C {lab_pin.sym} 2550 -10 0 0 {name=ln9 lab=n9}
C {lab_pin.sym} 2850 -10 0 0 {name=ln10 lab=n10}
C {lab_pin.sym} 1500 -140 0 0 {name=lro lab=ro}
C {lab_pin.sym} -50 10 0 1 {name=len lab=en}
C {lab_pin.sym} 0 -50 0 0 {name=lv0 lab=vddr}
C {lab_pin.sym} 300 -50 0 0 {name=lv1 lab=vddr}
C {lab_pin.sym} 600 -50 0 0 {name=lv2 lab=vddr}
C {lab_pin.sym} 900 -50 0 0 {name=lv3 lab=vddr}
C {lab_pin.sym} 1200 -50 0 0 {name=lv4 lab=vddr}
C {lab_pin.sym} 1500 -50 0 0 {name=lv5 lab=vddr}
C {lab_pin.sym} 1800 -50 0 0 {name=lv6 lab=vddr}
C {lab_pin.sym} 2100 -50 0 0 {name=lv7 lab=vddr}
C {lab_pin.sym} 2400 -50 0 0 {name=lv8 lab=vddr}
C {lab_pin.sym} 2700 -50 0 0 {name=lv9 lab=vddr}
C {lab_pin.sym} 3000 -50 0 0 {name=lv10 lab=vddr}
C {lab_pin.sym} 0 50 0 0 {name=ls0 lab=vss}
C {lab_pin.sym} 300 50 0 0 {name=ls1 lab=vss}
C {lab_pin.sym} 600 50 0 0 {name=ls2 lab=vss}
C {lab_pin.sym} 900 50 0 0 {name=ls3 lab=vss}
C {lab_pin.sym} 1200 50 0 0 {name=ls4 lab=vss}
C {lab_pin.sym} 1500 50 0 0 {name=ls5 lab=vss}
C {lab_pin.sym} 1800 50 0 0 {name=ls6 lab=vss}
C {lab_pin.sym} 2100 50 0 0 {name=ls7 lab=vss}
C {lab_pin.sym} 2400 50 0 0 {name=ls8 lab=vss}
C {lab_pin.sym} 2700 50 0 0 {name=ls9 lab=vss}
C {lab_pin.sym} 3000 50 0 0 {name=ls10 lab=vss}
