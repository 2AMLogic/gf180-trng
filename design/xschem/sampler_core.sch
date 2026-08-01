v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sampler_core -- #9's sampler/digitizer, wrapping the entropy source.

Instantiates the shipped ro_array_core (DR-0007's two-ring XOR-combined
array) and samples its xo node with two sampler_dff instances sharing one
external clock and one async reset:

  xsb  D = xo    -> raw_bit    the DR-0001 raw tap, at last
  xsv  D = vdd   -> raw_valid  registered "out of reset" indicator

xo never leaves this schematic as a pin -- design/README.md is explicit
that the raw tap sits at the SAMPLER's output, after digitisation, not at
the array's internal combining node. xsv's D is tied permanently to vdd
(logic 1), so raw_valid is low only during/immediately after reset and
goes high, and stays high, one clk edge after rst_n releases: a one-cycle
reset synchronizer built from the same cell as the data path, rather than
a second bespoke circuit.

clk / rst_n are the block's FIXED EXTERNAL sample clock and its async
active-low reset -- see sampler_dff.sch and
spec/decision-records/DR-0011-sampler-fixed-external-clock.md for why the
clock is external rather than divided down from either ring. This
schematic contains no divider and no clock-generation circuitry; that is
the point of the decision, not an omission.

en1/en2/vddr1/vddr2 are forwarded straight through to ro_array_core --
ring enable/start-up sequencing is not this cell's job (nothing here
assumes an enable policy). vdd/vss feed both the array's combining gate
and the two samplers; the rings keep their own separate vddr1/vddr2 per
DR-0007's independence requirement, untouched by this wrapper.

Port shape (raw_bit/raw_valid/clk/rst_n) matches
design/conditioner/README.md's already-fixed input contract exactly.} -1400 -700 0 0 0.2 0.2 {}
C {ipin.sym} -1000 -300 0 0 {name=pe1 lab=en1}
C {ipin.sym} -1000 -250 0 0 {name=pe2 lab=en2}
C {iopin.sym} -1000 -200 0 0 {name=pv1 lab=vddr1}
C {iopin.sym} -1000 -150 0 0 {name=pv2 lab=vddr2}
C {iopin.sym} -1000 -100 0 0 {name=pv lab=vdd}
C {iopin.sym} -1000 -50 0 0 {name=ps lab=vss}
C {ipin.sym} -1000 0 0 0 {name=pc lab=clk}
C {ipin.sym} -1000 50 0 0 {name=pr lab=rst_n}
C {opin.sym} -1000 100 0 0 {name=pb lab=raw_bit}
C {opin.sym} -1000 150 0 0 {name=pvv lab=raw_valid}
C {ro_array_core.sym} 0 0 0 0 {name=xdut}
C {sampler_dff.sym} 500 -200 0 0 {name=xsb}
C {sampler_dff.sym} 500 200 0 0 {name=xsv}
C {lab_pin.sym} -70 -40 0 1 {name=l1 lab=en1}
C {lab_pin.sym} -70 -10 0 1 {name=l2 lab=en2}
C {lab_pin.sym} -30 -70 0 0 {name=l3 lab=vddr1}
C {lab_pin.sym} 0 -70 0 0 {name=l4 lab=vddr2}
C {lab_pin.sym} 30 -70 0 0 {name=l5 lab=vdd}
C {lab_pin.sym} 0 70 0 0 {name=l6 lab=vss}
C {lab_pin.sym} 70 0 0 0 {name=l7 lab=xo}
C {lab_pin.sym} 450 -230 0 0 {name=l8 lab=xo}
C {lab_pin.sym} 450 -200 0 0 {name=l9 lab=clk}
C {lab_pin.sym} 450 -170 0 0 {name=l10 lab=rst_n}
C {lab_pin.sym} 550 -200 0 0 {name=l11 lab=raw_bit}
C {lab_pin.sym} 500 -250 0 0 {name=l12 lab=vdd}
C {lab_pin.sym} 500 -150 0 0 {name=l13 lab=vss}
C {lab_pin.sym} 450 170 0 0 {name=l14 lab=vdd}
C {lab_pin.sym} 450 200 0 0 {name=l15 lab=clk}
C {lab_pin.sym} 450 230 0 0 {name=l16 lab=rst_n}
C {lab_pin.sym} 550 200 0 0 {name=l17 lab=raw_valid}
C {lab_pin.sym} 500 150 0 0 {name=l18 lab=vdd}
C {lab_pin.sym} 500 250 0 0 {name=l19 lab=vss}
