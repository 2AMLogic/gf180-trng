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
              at the sampler output, and no per-ring signal leaves the die.
              The sampler and its clock are #9's.
  ro1, ro2    per-ring outputs, OBSERVATION ONLY, added by #65 for the
              DR-0016 per-ring liveness monitor. They exist because a stuck
              ring is invisible at xo, and a monitor that cannot see a ring
              cannot report it. Nothing here digitizes them: the two
              sampler_dff taps live one level up in sampler_core.sch, the
              same cell and the same clock the raw tap already uses, so this
              cell stays a purely analog free-running source with no clock.
              They are per-ring signals INSIDE the block, not exposed
              pins -- DR-0001 constrains what the block publishes at the die
              boundary, not what it monitors internally, and DR-0016 says so.
              Since #78/DR-0018 this is the BUFFERED node (see below), not
              the ring's own raw node; adding the buffer changes what is on
              this pin without adding a device to the ring or changing any
              ring parameter, so the pre-#78 power and jitter records still
              describe the RING this cell contains -- they describe an array
              that shipped without the buffer on ro1/ro2, and #78's own
              record families are what describe the array as it ships now.

Per-ring output buffer (#78/DR-0018). Each ring's own last stage drives one
ro_buf instance -- a minimum-width, UNSTARVED inverter, identical device
sizing to xor2's own input stage -- and ro1/ro2 are re-driven from that
buffer's output, not from the ring directly, so every consumer downstream
of this cell (xa1 here, and one level up, the DR-0016 liveness digitizers
and the sampler) sees the buffered node. Two SEPARATE buffer instances,
one per ring: a single buffer feeding both combiner inputs would recreate
exactly the shared node the mitigation exists to remove.
sim/characterization-ring-buffer-mitigation.md measured why: a consumer's
own input-stage capacitance injects charge BACKWARDS into whatever drives
it, and driving that consumer from a low-impedance buffer output instead
of from the ring's own high-impedance oscillating node removes 92.8% of a
measured 27.10x coupling factor (a 2.87x residual survives and remains
inadmissible for DR-0007 SS2's per-ring sigma_acc measurement rule, which
this change does NOT relax). It also lightens each ring's own fanout from
xa1's 1.98 um of gate to the buffer's 0.66 um, which is why ring frequency
moves +6.7% and the block's active-power rollup moves -4.9% (the buffer's
fast edges cut the combiner's own crowbar current by more than the buffer
itself, or the ring running faster to spend the load saving, cost). Both
buffers run off vdd/vss -- the block/combiner supply -- not off either
ring's vddr, so each ring's own supply pin stays a pure per-ring current
signature; adding the buffer changes NEITHER ring's own vddr1/vddr2
branch.

Polarity: ro1/ro2 are now the COMPLEMENT of their ring's own internal
node. a XOR b == (NOT a) XOR (NOT b), so xa1's output is bit-identical;
the liveness digitizer counts transitions and is polarity-blind; sampler
entropy does not depend on polarity. Nothing downstream needs a matching
change, but a reader of ro1/ro2 should not assume it is the ring's own
sense.

Frequency skew is by starve-device width (wstv), not by stage count, so the
nominal ratio is set by a continuous parameter rather than by a ratio of
small integers -- integer-ratio rings are the ones that mutually injection
lock. The realized ratio is measured, not assumed; see
sim/records/*-ro-array-core-power-*.md -- records dated 2026-08-01 and
earlier describe the pre-#78 unbuffered array; records dated 2026-08-02 and
later describe the buffered one. Each record names the exact netlist sha it
ran against, so which array a record describes is checkable rather than
inferred from its date, and DR-0018 lists the re-run stems.} -1200 -700 0 0 0.25 0.25 {}
C {ipin.sym} -1200 -300 0 0 {name=pe1 lab=en1}
C {ipin.sym} -1200 -250 0 0 {name=pe2 lab=en2}
C {iopin.sym} -1000 -300 0 0 {name=pv1 lab=vddr1}
C {iopin.sym} -1000 -250 0 0 {name=pv2 lab=vddr2}
C {iopin.sym} -800 -300 0 0 {name=pv lab=vdd}
C {iopin.sym} -800 -250 0 0 {name=ps lab=vss}
C {opin.sym} -800 -200 0 0 {name=po lab=xo}
C {opin.sym} -800 -150 0 0 {name=po1 lab=ro1}
C {opin.sym} -800 -100 0 0 {name=po2 lab=ro2}
C {ro_ring11.sym} 0 0 0 0 {name=xr1 wstv=0.220u lstv=2u cld=0.5f}
C {ro_ring11.sym} 0 300 0 0 {name=xr2 wstv=0.240u lstv=2u cld=0.5f}
C {ro_buf.sym} 250 -10 0 0 {name=xb1}
C {ro_buf.sym} 250 290 0 0 {name=xb2}
C {xor2.sym} 400 150 0 0 {name=xa1}
C {lab_pin.sym} -70 -10 0 1 {name=le1 lab=en1}
C {lab_pin.sym} -70 290 0 1 {name=le2 lab=en2}
C {lab_pin.sym} 0 -70 0 0 {name=lw1 lab=vddr1}
C {lab_pin.sym} 0 230 0 0 {name=lw2 lab=vddr2}
C {lab_pin.sym} 0 70 0 0 {name=lg1 lab=vss}
C {lab_pin.sym} 0 370 0 0 {name=lg2 lab=vss}
C {lab_pin.sym} 70 -10 0 0 {name=lo1 lab=rn1}
C {lab_pin.sym} 70 290 0 0 {name=lo2 lab=rn2}
C {lab_pin.sym} 200 -20 0 0 {name=lb1a lab=rn1}
C {lab_pin.sym} 300 -20 0 0 {name=lb1y lab=ro1}
C {lab_pin.sym} 250 -60 0 0 {name=lb1v lab=vdd}
C {lab_pin.sym} 250 40 0 0 {name=lb1g lab=vss}
C {lab_pin.sym} 200 280 0 0 {name=lb2a lab=rn2}
C {lab_pin.sym} 300 280 0 0 {name=lb2y lab=ro2}
C {lab_pin.sym} 250 240 0 0 {name=lb2v lab=vdd}
C {lab_pin.sym} 250 340 0 0 {name=lb2g lab=vss}
C {lab_pin.sym} 360 130 0 1 {name=lxa1a lab=ro1}
C {lab_pin.sym} 360 170 0 1 {name=lxa1b lab=ro2}
C {lab_pin.sym} 440 150 0 0 {name=lxa1y lab=xo}
C {lab_pin.sym} 400 110 0 0 {name=lxa1v lab=vdd}
C {lab_pin.sym} 400 190 0 0 {name=lxa1g lab=vss}
