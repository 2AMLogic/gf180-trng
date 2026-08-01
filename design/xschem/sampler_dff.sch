v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sampler_dff -- static CMOS transmission-gate master-slave D flip-flop
with an asynchronous, active-low reset. This is #9's digitizer: it is the
ONLY cell in gf180-trng that turns an analog swing (the entropy source's
XOR node, design/xschem/ro_array_core.sch) into a logic-level bit, so its
own setup/hold/metastability behavior is part of the entropy story, not
just a timing hazard (the original issue's framing).

Positive-edge-triggered, built from two opposite-phase transmission-gate
latches (the standard static TGFF topology), all minimum-width gf180mcu
3.3 V core devices (same P=0.44u/N=0.22u sizing as xor2/ro_stage). Each
latch needs TWO series inversions in its hold loop, not one -- a single
inverter with a feedback TG creates q = NOT(q), which is not bistable and
settles at a metastable half-rail voltage in simulation (caught by a
functional check while building this cell; noted here so nobody
"simplifies" it back to the one-inverter form):

  master: TG_D (transparent clk=0) writes D into node m
          INVM: m -> mb            (drives the slave's TG_S)
          INVM2: mb -> mc          (second inversion, feedback only)
          TG_FBM (transparent clk=1) feeds mc back into m  -- hold
  slave:  TG_S (transparent clk=1) passes mb -> node s
          INVS: s -> q             (the cell's output)
          INVS2: q -> qb           (second inversion, feedback only)
          TG_FBS (transparent clk=0) feeds qb back into s  -- hold

D is captured into the master while clk=0; the master closes and the
slave opens as clk rises, so Q updates on the RISING clk edge -- ordinary
positive-edge D-FF behavior.

Reset is asynchronous and reset-dominant, not scan-style: Mrm pulls node m
to vss and Mrs pulls node s to vdd whenever rst_n=0, each sized 2x the
minimum-width devices in the loops they override (Mrs is a PMOS pull-up,
so it is gated directly by rst_n -- active LOW turns a PMOS ON -- not by
the internal active-high "rst" signal, which is the polarity Mrm needs
instead as an NMOS pull-down). That drives mb=1 and q=NOT(s)=0 regardless
of clk phase, and because both storage nodes are forced to the SAME
steady state the normal clk=1 hand-off would produce, releasing rst_n
never hands the slave a value the master disagrees with.

Sampler clock source (binding decision): clk is a FIXED EXTERNAL clock,
not divided down from either entropy-source ring -- see design/README.md
and spec/decision-records/DR-0012-sampler-fixed-external-clock.md for the
full argument. In short: deriving the sample clock from a ring that also
feeds the XOR node this cell digitizes risks a deterministic beat between
source and sampler (the very thing the original issue calls out to
avoid), and it collapses the corner metric DR-0007 SS4 depends on into an
unresolvable one. A clock with no frequency relationship to either ring
avoids both, at the cost of needing an external clock pin instead of an
on-chip divider -- which is why this schematic has no clock-generation
circuitry of its own.} -200 -900 0 0 0.2 0.2 {}
C {ipin.sym} -300 -500 0 0 {name=p1 lab=d}
C {ipin.sym} -300 -450 0 0 {name=p2 lab=clk}
C {ipin.sym} -300 -400 0 0 {name=p3 lab=rst_n}
C {opin.sym} -300 -350 0 0 {name=p4 lab=q}
C {iopin.sym} -300 -300 0 0 {name=p5 lab=vdd}
C {iopin.sym} -300 -250 0 0 {name=p6 lab=vss}
C {pfet_03v3.sym} 0 -300 0 0 {name=Mpc L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 0 -100 0 0 {name=Mnc L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 300 -300 0 0 {name=Mpr L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 300 -100 0 0 {name=Mnr L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 600 -300 0 0 {name=Mtdp L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 600 -100 0 0 {name=Mtdn L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 900 -300 0 0 {name=Mimp L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 900 -100 0 0 {name=Mimn L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 1200 -300 0 0 {name=Mim2p L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 1200 -100 0 0 {name=Mim2n L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 1500 -300 0 0 {name=Mfmp L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 1500 -100 0 0 {name=Mfmn L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 1800 -300 0 0 {name=Mtsp L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 1800 -100 0 0 {name=Mtsn L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 2100 -300 0 0 {name=Misp L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 2100 -100 0 0 {name=Misn L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 2400 -300 0 0 {name=Mis2p L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 2400 -100 0 0 {name=Mis2n L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 2700 -300 0 0 {name=Mfsp L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 2700 -100 0 0 {name=Mfsn L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 3000 -100 0 0 {name=Mrm L=0.28u W=0.44u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 3300 -300 0 0 {name=Mrs L=0.28u W=0.88u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {lab_pin.sym} 20 -270 0 0 {name=l1 lab=clkb}
C {lab_pin.sym} -20 -300 0 0 {name=l2 lab=clk}
C {lab_pin.sym} 20 -330 0 0 {name=l3 lab=vdd}
C {lab_pin.sym} 20 -300 0 0 {name=l4 lab=vdd}
C {lab_pin.sym} 20 -130 0 0 {name=l5 lab=clkb}
C {lab_pin.sym} -20 -100 0 0 {name=l6 lab=clk}
C {lab_pin.sym} 20 -70 0 0 {name=l7 lab=vss}
C {lab_pin.sym} 20 -100 0 0 {name=l8 lab=vss}
C {lab_pin.sym} 320 -270 0 0 {name=l9 lab=rst}
C {lab_pin.sym} 280 -300 0 0 {name=l10 lab=rst_n}
C {lab_pin.sym} 320 -330 0 0 {name=l11 lab=vdd}
C {lab_pin.sym} 320 -300 0 0 {name=l12 lab=vdd}
C {lab_pin.sym} 320 -130 0 0 {name=l13 lab=rst}
C {lab_pin.sym} 280 -100 0 0 {name=l14 lab=rst_n}
C {lab_pin.sym} 320 -70 0 0 {name=l15 lab=vss}
C {lab_pin.sym} 320 -100 0 0 {name=l16 lab=vss}
C {lab_pin.sym} 620 -270 0 0 {name=l17 lab=d}
C {lab_pin.sym} 580 -300 0 0 {name=l18 lab=clk}
C {lab_pin.sym} 620 -330 0 0 {name=l19 lab=m}
C {lab_pin.sym} 620 -300 0 0 {name=l20 lab=vdd}
C {lab_pin.sym} 620 -130 0 0 {name=l21 lab=d}
C {lab_pin.sym} 580 -100 0 0 {name=l22 lab=clkb}
C {lab_pin.sym} 620 -70 0 0 {name=l23 lab=m}
C {lab_pin.sym} 620 -100 0 0 {name=l24 lab=vss}
C {lab_pin.sym} 920 -270 0 0 {name=l25 lab=mb}
C {lab_pin.sym} 880 -300 0 0 {name=l26 lab=m}
C {lab_pin.sym} 920 -330 0 0 {name=l27 lab=vdd}
C {lab_pin.sym} 920 -300 0 0 {name=l28 lab=vdd}
C {lab_pin.sym} 920 -130 0 0 {name=l29 lab=mb}
C {lab_pin.sym} 880 -100 0 0 {name=l30 lab=m}
C {lab_pin.sym} 920 -70 0 0 {name=l31 lab=vss}
C {lab_pin.sym} 920 -100 0 0 {name=l32 lab=vss}
C {lab_pin.sym} 1220 -270 0 0 {name=l33 lab=mc}
C {lab_pin.sym} 1180 -300 0 0 {name=l34 lab=mb}
C {lab_pin.sym} 1220 -330 0 0 {name=l35 lab=vdd}
C {lab_pin.sym} 1220 -300 0 0 {name=l36 lab=vdd}
C {lab_pin.sym} 1220 -130 0 0 {name=l37 lab=mc}
C {lab_pin.sym} 1180 -100 0 0 {name=l38 lab=mb}
C {lab_pin.sym} 1220 -70 0 0 {name=l39 lab=vss}
C {lab_pin.sym} 1220 -100 0 0 {name=l40 lab=vss}
C {lab_pin.sym} 1520 -270 0 0 {name=l41 lab=mc}
C {lab_pin.sym} 1480 -300 0 0 {name=l42 lab=clkb}
C {lab_pin.sym} 1520 -330 0 0 {name=l43 lab=m}
C {lab_pin.sym} 1520 -300 0 0 {name=l44 lab=vdd}
C {lab_pin.sym} 1520 -130 0 0 {name=l45 lab=mc}
C {lab_pin.sym} 1480 -100 0 0 {name=l46 lab=clk}
C {lab_pin.sym} 1520 -70 0 0 {name=l47 lab=m}
C {lab_pin.sym} 1520 -100 0 0 {name=l48 lab=vss}
C {lab_pin.sym} 1820 -270 0 0 {name=l49 lab=mb}
C {lab_pin.sym} 1780 -300 0 0 {name=l50 lab=clkb}
C {lab_pin.sym} 1820 -330 0 0 {name=l51 lab=s}
C {lab_pin.sym} 1820 -300 0 0 {name=l52 lab=vdd}
C {lab_pin.sym} 1820 -130 0 0 {name=l53 lab=mb}
C {lab_pin.sym} 1780 -100 0 0 {name=l54 lab=clk}
C {lab_pin.sym} 1820 -70 0 0 {name=l55 lab=s}
C {lab_pin.sym} 1820 -100 0 0 {name=l56 lab=vss}
C {lab_pin.sym} 2120 -270 0 0 {name=l57 lab=q}
C {lab_pin.sym} 2080 -300 0 0 {name=l58 lab=s}
C {lab_pin.sym} 2120 -330 0 0 {name=l59 lab=vdd}
C {lab_pin.sym} 2120 -300 0 0 {name=l60 lab=vdd}
C {lab_pin.sym} 2120 -130 0 0 {name=l61 lab=q}
C {lab_pin.sym} 2080 -100 0 0 {name=l62 lab=s}
C {lab_pin.sym} 2120 -70 0 0 {name=l63 lab=vss}
C {lab_pin.sym} 2120 -100 0 0 {name=l64 lab=vss}
C {lab_pin.sym} 2420 -270 0 0 {name=l65 lab=qb}
C {lab_pin.sym} 2380 -300 0 0 {name=l66 lab=q}
C {lab_pin.sym} 2420 -330 0 0 {name=l67 lab=vdd}
C {lab_pin.sym} 2420 -300 0 0 {name=l68 lab=vdd}
C {lab_pin.sym} 2420 -130 0 0 {name=l69 lab=qb}
C {lab_pin.sym} 2380 -100 0 0 {name=l70 lab=q}
C {lab_pin.sym} 2420 -70 0 0 {name=l71 lab=vss}
C {lab_pin.sym} 2420 -100 0 0 {name=l72 lab=vss}
C {lab_pin.sym} 2720 -270 0 0 {name=l73 lab=qb}
C {lab_pin.sym} 2680 -300 0 0 {name=l74 lab=clk}
C {lab_pin.sym} 2720 -330 0 0 {name=l75 lab=s}
C {lab_pin.sym} 2720 -300 0 0 {name=l76 lab=vdd}
C {lab_pin.sym} 2720 -130 0 0 {name=l77 lab=qb}
C {lab_pin.sym} 2680 -100 0 0 {name=l78 lab=clkb}
C {lab_pin.sym} 2720 -70 0 0 {name=l79 lab=s}
C {lab_pin.sym} 2720 -100 0 0 {name=l80 lab=vss}
C {lab_pin.sym} 3020 -130 0 0 {name=l81 lab=m}
C {lab_pin.sym} 2980 -100 0 0 {name=l82 lab=rst}
C {lab_pin.sym} 3020 -70 0 0 {name=l83 lab=vss}
C {lab_pin.sym} 3020 -100 0 0 {name=l84 lab=vss}
C {lab_pin.sym} 3320 -270 0 0 {name=l85 lab=s}
C {lab_pin.sym} 3280 -300 0 0 {name=l86 lab=rst_n}
C {lab_pin.sym} 3320 -330 0 0 {name=l87 lab=vdd}
C {lab_pin.sym} 3320 -300 0 0 {name=l88 lab=vdd}
