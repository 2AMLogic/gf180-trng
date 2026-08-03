v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ro_buf -- minimum-width, unstarved 3.3 V inverter (issue #78 / DR-0018).

The per-ring output buffer ro_array_core.sch instantiates once per ring,
between that ring's own last stage and every consumer (the XOR combiner
and, through ro_array_core's ro1/ro2 pins, the DR-0016 liveness
digitizers and the sampler). Device sizing is IDENTICAL to xor2's own
input-stage inverter (Mp W=0.44u, Mn W=0.22u, both L=0.28u) -- the same
minimum-width 3.3 V devices used everywhere else in this design, carrying
the same ad/as/pd/ps/nrd/nrs diffusion-geometry expressions every device
in the committed netlists uses, so this cell's own drain junction
capacitance is modelled rather than omitted.

Unlike ro_stage, this inverter has NO series starve devices: it is not
part of a ring's frequency-setting delay chain, and its whole job is to
present a fast, low-impedance, actively-driven node to whatever it
drives, so a coupling path landing on that node cannot inject charge back
through it onto the ring's own oscillating node the way it could through
the ring node itself. sim/characterization-ring-buffer-mitigation.md
measured this: 92.8% of a 27.10x coupling factor removed, and the block's
own active-power rollup improves rather than worsens, because this
buffer's fast edges cut the combiner's own crowbar current more than the
buffer itself, or the ring running faster to spend the load-capacitance
saving, cost.

This cell runs off vdd/vss -- the BLOCK supply, the same one the XOR
combiner uses -- not off either ring's vddr. That keeps each ring's own
vddr1/vddr2 pin a pure per-ring current signature (DR-0007's independence
requirement, and the per-ring liveness observation point DR-0016 relies
on): this buffer adds no switching current to either ring's own supply
branch, whether or not the ring driving it is enabled.

Polarity: y = NOT a. Every consumer of this cell's output sees the
COMPLEMENT of the node driving `a`. a XOR b == (NOT a) XOR (NOT b), so a
combiner fed from two buffered rings is bit-identical to one fed
directly; the DR-0016 liveness digitizer counts transitions and is
polarity-blind; sampler entropy does not depend on polarity. Nothing
downstream needs a matching change, but a reader of a buffered node's
level should not assume it is the ring's own sense.} -700 -650 0 0 0.25 0.25 {}
C {ipin.sym} -560 -150 0 0 {name=p1 lab=a}
C {opin.sym} -480 -150 0 0 {name=p2 lab=y}
C {iopin.sym} -560 -100 0 0 {name=p3 lab=vdd}
C {iopin.sym} -480 -100 0 0 {name=p4 lab=vss}
C {pfet_03v3.sym} 0 -200 0 0 {name=Mp L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 0 -100 0 0 {name=Mn L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
N 20 -170 20 -130 {lab=y}
N 20 -150 200 -150 {lab=y}
N -20 -200 -20 -100 {lab=a}
C {lab_pin.sym} -20 -150 0 1 {name=la lab=a}
C {lab_pin.sym} 100 -150 0 0 {name=ly lab=y}
C {lab_pin.sym} 20 -230 0 0 {name=lv1 lab=vdd}
C {lab_pin.sym} 20 -200 0 0 {name=lvb lab=vdd}
C {lab_pin.sym} 20 -70 0 0 {name=ls1 lab=vss}
C {lab_pin.sym} 20 -100 0 0 {name=lsb lab=vss}
