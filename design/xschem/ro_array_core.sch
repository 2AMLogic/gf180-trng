v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ro_array_core -- the gf180-trng entropy source.

Two independent, separately-supplied, free-running ring oscillators of a
common cell design with deliberately skewed frequencies, XOR-combined into
one node (xo) that a single sampler observes. Topology is DR-0007 section 1;
sizing (N = 2, 11 stages, minimum-width series-starved cell, lstv = 2u) is
DR-0010.

Why N = 2 and not more. Entropy is indifferent to N at fixed total ring
power (DR-0010's jitter-energy law), so N is chosen for independence and
for what the combiner costs -- and the combiner is what binds. A four-ring
array of these same rings measures 1.02 mW at the ff/+10%/-40 C power
corner, of which the two-level XOR tree alone is 444 uW
(sim/records/2026-08-01-ro-array-core-power-01.md), against a ratified
< 500 uW row. Slowing the rings does not fix it: at lstv = 6u the array
still measures 939 uW because the tree energy per transition rises as the
ring edges slow (record -02/-03). Halving the ring count halves the tree's
transition rate AND its depth, which is the only lever that moved the total
under the row. N = 2 is the floor of DR-0007's array concept, and DR-0010
says so and names the Power row as the next thing that gives if #16 finds
two rings insufficient.

  en1, en2    per-ring enable. en = 0 stops that ring in a static state.
  vddr1/2     per-ring supply. Separate routing is a DR-0007 requirement
              (independence), and is also the per-ring liveness observation
              point -- a stopped ring's supply current collapses by >4
              orders of magnitude, while a stuck ring is INVISIBLE at xo
              because it contributes a constant to the XOR.
  vdd/vss     block supply for the combining gate. Deliberately not either
              ring's vddr, so per-ring supply sensing sees rings only.
  xo          the combined node. The RAW TAP IS NOT HERE: DR-0001 puts it
              at the sampler output, and no per-ring signal leaves this
              cell. The sampler and its clock are #9's.

Frequency skew is by starve-device width (wstv), not by stage count, so the
nominal ratio is set by a continuous parameter rather than by a ratio of
small integers -- integer-ratio rings are the ones that mutually injection
lock. The realized ratio is measured, not assumed; see
sim/records/2026-08-01-ro-array-core-power-*.md.} -1200 -700 0 0 0.25 0.25 {}
C {ipin.sym} -1200 -300 0 0 {name=pe1 lab=en1}
C {ipin.sym} -1200 -250 0 0 {name=pe2 lab=en2}
C {iopin.sym} -1000 -300 0 0 {name=pv1 lab=vddr1}
C {iopin.sym} -1000 -250 0 0 {name=pv2 lab=vddr2}
C {iopin.sym} -800 -300 0 0 {name=pv lab=vdd}
C {iopin.sym} -800 -250 0 0 {name=ps lab=vss}
C {opin.sym} -800 -200 0 0 {name=po lab=xo}
C {ro_ring11.sym} 0 0 0 0 {name=xr1 wstv=0.220u lstv=2u cld=0.5f}
C {ro_ring11.sym} 0 300 0 0 {name=xr2 wstv=0.240u lstv=2u cld=0.5f}
C {xor2.sym} 400 150 0 0 {name=xa1}
C {lab_pin.sym} -70 -10 0 1 {name=le1 lab=en1}
C {lab_pin.sym} -70 290 0 1 {name=le2 lab=en2}
C {lab_pin.sym} 0 -70 0 0 {name=lw1 lab=vddr1}
C {lab_pin.sym} 0 230 0 0 {name=lw2 lab=vddr2}
C {lab_pin.sym} 0 70 0 0 {name=lg1 lab=vss}
C {lab_pin.sym} 0 370 0 0 {name=lg2 lab=vss}
C {lab_pin.sym} 70 -10 0 0 {name=lo1 lab=ro1}
C {lab_pin.sym} 70 290 0 0 {name=lo2 lab=ro2}
C {lab_pin.sym} 360 130 0 1 {name=lxa1a lab=ro1}
C {lab_pin.sym} 360 170 0 1 {name=lxa1b lab=ro2}
C {lab_pin.sym} 440 150 0 0 {name=lxa1y lab=xo}
C {lab_pin.sym} 400 110 0 0 {name=lxa1v lab=vdd}
C {lab_pin.sym} 400 190 0 0 {name=lxa1g lab=vss}
