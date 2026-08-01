v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ro_array_sanity -- a reduced-cost stand-in for ro_array_core, used ONLY by
the array-level transient-noise sanity testbench.

Same leaf cells (ro_nand2 / ro_stage / xor2), same per-ring supplies, same
XOR tree, same wstv skew. Two things are deliberately different, and both
exist to make a transient-noise run finish:

  * FIVE stages per ring instead of eleven (ro_ring5, see that cell for why
    five and not three). Five also matches sim/tb/ro-inv-05stage-jitter/,
    the ratified per-ring characterization's flagship configuration, so the
    array's per-ring sigma_1 is comparable to it stage-for-stage.
  * lstv = 2 um instead of the shipped 6 um, so the ring period is ~3x
    shorter.

Together those make one accumulated ring period ~6.6x cheaper to simulate
than the shipped ring's. What connects this cell's numbers to the shipped
array's is DR-0008's jitter-energy law -- which is exactly what this cell's
run exists to TEST, by measuring sigma_1 and the ring's own supply current
in the same run and checking their product against the constant the
ratified plain-inverter grid gives.

The four ring outputs are brought out as observation pins HERE and only
here. They are absent from ro_array_core deliberately: DR-0001 puts the
raw tap at the sampler output, and a per-ring pin on the shipped cell
would be an entropy-source-internal node exposed at the block boundary.

What that buys and what it does not: the questions the sanity run asks --
do four rings on separate supplies stay at their own frequencies when
simulated together (no injection locking), does each ring's jitter in the
array match the same ring standing alone, does jitter still accumulate as
sqrt(t) inside the array, and is the XOR node alive -- are all questions
about the ARRAY, not about the stage count. The shipped operating point
(N = 4 x 11 stages) is sized from the deterministic ro-array-core-power
grid plus DR-0008's jitter-energy law, not from this cell. Do not cite
this cell's numbers as the core's.} -1200 -700 0 0 0.25 0.25 {}
C {ipin.sym} -1200 -300 0 0 {name=pe1 lab=en1}
C {ipin.sym} -1200 -250 0 0 {name=pe2 lab=en2}
C {ipin.sym} -1200 -200 0 0 {name=pe3 lab=en3}
C {ipin.sym} -1200 -150 0 0 {name=pe4 lab=en4}
C {iopin.sym} -1000 -300 0 0 {name=pv1 lab=vddr1}
C {iopin.sym} -1000 -250 0 0 {name=pv2 lab=vddr2}
C {iopin.sym} -1000 -200 0 0 {name=pv3 lab=vddr3}
C {iopin.sym} -1000 -150 0 0 {name=pv4 lab=vddr4}
C {iopin.sym} -800 -300 0 0 {name=pv lab=vdd}
C {iopin.sym} -800 -250 0 0 {name=ps lab=vss}
C {opin.sym} -800 -200 0 0 {name=po lab=xo}
C {opin.sym} -800 -150 0 0 {name=po1 lab=ro1}
C {opin.sym} -800 -100 0 0 {name=po2 lab=ro2}
C {opin.sym} -800 -50 0 0 {name=po3 lab=ro3}
C {opin.sym} -800 0 0 0 {name=po4 lab=ro4}
C {ro_ring5.sym} 0 0 0 0 {name=xr1 wstv=0.220u lstv=2u cld=0.5f}
C {ro_ring5.sym} 0 300 0 0 {name=xr2 wstv=0.240u lstv=2u cld=0.5f}
C {ro_ring5.sym} 0 600 0 0 {name=xr3 wstv=0.260u lstv=2u cld=0.5f}
C {ro_ring5.sym} 0 900 0 0 {name=xr4 wstv=0.285u lstv=2u cld=0.5f}
C {xor2.sym} 400 150 0 0 {name=xa1}
C {xor2.sym} 400 750 0 0 {name=xa2}
C {xor2.sym} 700 450 0 0 {name=xb1}
C {lab_pin.sym} -70 -10 0 1 {name=le1 lab=en1}
C {lab_pin.sym} -70 290 0 1 {name=le2 lab=en2}
C {lab_pin.sym} -70 590 0 1 {name=le3 lab=en3}
C {lab_pin.sym} -70 890 0 1 {name=le4 lab=en4}
C {lab_pin.sym} 0 -70 0 0 {name=lw1 lab=vddr1}
C {lab_pin.sym} 0 230 0 0 {name=lw2 lab=vddr2}
C {lab_pin.sym} 0 530 0 0 {name=lw3 lab=vddr3}
C {lab_pin.sym} 0 830 0 0 {name=lw4 lab=vddr4}
C {lab_pin.sym} 0 70 0 0 {name=lg1 lab=vss}
C {lab_pin.sym} 0 370 0 0 {name=lg2 lab=vss}
C {lab_pin.sym} 0 670 0 0 {name=lg3 lab=vss}
C {lab_pin.sym} 0 970 0 0 {name=lg4 lab=vss}
C {lab_pin.sym} 70 -10 0 0 {name=lo1 lab=ro1}
C {lab_pin.sym} 70 290 0 0 {name=lo2 lab=ro2}
C {lab_pin.sym} 70 590 0 0 {name=lo3 lab=ro3}
C {lab_pin.sym} 70 890 0 0 {name=lo4 lab=ro4}
C {lab_pin.sym} 360 130 0 1 {name=lxa1a lab=ro1}
C {lab_pin.sym} 360 170 0 1 {name=lxa1b lab=ro2}
C {lab_pin.sym} 440 150 0 0 {name=lxa1y lab=t1}
C {lab_pin.sym} 400 110 0 0 {name=lxa1v lab=vdd}
C {lab_pin.sym} 400 190 0 0 {name=lxa1g lab=vss}
C {lab_pin.sym} 360 730 0 1 {name=lxa2a lab=ro3}
C {lab_pin.sym} 360 770 0 1 {name=lxa2b lab=ro4}
C {lab_pin.sym} 440 750 0 0 {name=lxa2y lab=t2}
C {lab_pin.sym} 400 710 0 0 {name=lxa2v lab=vdd}
C {lab_pin.sym} 400 790 0 0 {name=lxa2g lab=vss}
C {lab_pin.sym} 660 430 0 1 {name=lxb1a lab=t1}
C {lab_pin.sym} 660 470 0 1 {name=lxb1b lab=t2}
C {lab_pin.sym} 740 450 0 0 {name=lxb1y lab=xo}
C {lab_pin.sym} 700 410 0 0 {name=lxb1v lab=vdd}
C {lab_pin.sym} 700 490 0 0 {name=lxb1g lab=vss}
