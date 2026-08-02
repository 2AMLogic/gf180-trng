v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {trng_top -- #27's top-level integration.

This schematic is the ANALOG half of the top-level assembly, and it stops
exactly at the DR-0001 raw tap -- the same boundary
spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md
draws for the whole repository. It instantiates sampler_core.sym (#9's
entropy source, #7's ro_array_core, plus the sampler_dff instances that
digitize xo into raw_bit/raw_valid and ro1/ro2 into ring_bit1/ring_bit2)
UNMODIFIED: no device here differs from design/xschem/sampler_core.sch, so
this cell adds a name and a place in the hierarchy, not a new circuit.

The three digital blocks DR-0009 assigns to behavioural verification --
design/conditioner/ (#8), design/health_test/ (#11) and design/interface/
(#26) -- are deliberately NOT instantiated here. None of them has a
schematic or a device-level netlist (design/README.md is explicit about
this), so drawing them as SPICE subcircuits in this file would either
fabricate a netlist that contradicts DR-0009's ratified split, or paper
over three empty .subckt stubs that ngspice cannot simulate. Both are worse
than naming the boundary and crossing it in the tool DR-0009 already
assigns: design/trng_top/trng_top.py, which wires the SAME three blocks'
real behavioural models (crc32_conditioner.Conditioner, rct_apt.HealthTest,
trng_interface.Interface) together exactly as design/trng_top/trng_top.v
wires their RTL. sim/tests/test_trng_top.py cross-checks, mechanically,
that every signal named below actually exists with the same name on both
sides of the raw tap -- the pinout-mismatch class of bug a schematic
picture cannot catch by itself.

Pin-for-pin, this schematic's four raw-tap pins feed:

  clk        -> design/conditioner/crc32_conditioner.v      clk
             -> design/health_test/rct_apt.v                clk
  rst_n      -> design/conditioner/crc32_conditioner.v      rst_n
             -> design/health_test/rct_apt.v                rst_n
  raw_bit    -> design/conditioner/crc32_conditioner.v      raw_bit
             -> design/health_test/rct_apt.v                raw_bit
  raw_valid  -> design/conditioner/crc32_conditioner.v      raw_valid
             -> design/health_test/rct_apt.v                raw_valid

and the two per-ring liveness taps DR-0016 adds (#65) cross the same
boundary into the same file, one bit per ring:

  ring_bit1  -> design/health_test/ring_liveness.v          ring_bit[0]
  ring_bit2  -> design/health_test/ring_liveness.v          ring_bit[1]

design/trng_top/trng_top.v names that port ring_bit[1:0] -- one vector
rather than two scalars, because ring_liveness.v is parameterised in
N_RINGS -- and sim/tests/test_trng_top.py checks the index mapping above by
name so a silent swap cannot survive. The monitor's ring_stuck_any then
enters design/interface/'s ht_fail_ring, the third source of the DR-0002
latch, which is likewise digital and appears nowhere in this file.

en1/en2/vddr1/vddr2/vdd/vss are forwarded straight through to
sampler_core.sym, unchanged from what design/xschem/sampler_core.sch
already does; ring enable/start-up sequencing is not this cell's job
either, for the same reason design/README.md gives for sampler_core itself.

The conditioner's en/flush, the health tests' startup_req, and the
interface's cond_word/cond_valid/ht_fail_rct/ht_fail_apt/ht_startup_pass
wiring are entirely digital (register-bus and same-clock-domain
combinational signals, per design/interface/README.md's block diagram) and
have no analog representation -- they exist only in trng_top.py/trng_top.v,
not in this file.

One nominal-corner smoke record (bits produced end to end through both
halves) lives under sim/records/, per sim/tb/smoke-trng-top/README.md.} -1400 -900 0 0 0.2 0.2 {}
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
C {opin.sym} -1000 200 0 0 {name=pr1 lab=ring_bit1}
C {opin.sym} -1000 250 0 0 {name=pr2 lab=ring_bit2}
C {sampler_core.sym} 0 0 0 0 {name=xsc}
C {lab_pin.sym} -70 -60 0 1 {name=l1 lab=en1}
C {lab_pin.sym} -70 -20 0 1 {name=l2 lab=en2}
C {lab_pin.sym} -30 100 0 0 {name=l3 lab=vddr1}
C {lab_pin.sym} 0 100 0 0 {name=l4 lab=vddr2}
C {lab_pin.sym} 30 100 0 0 {name=l5 lab=vdd}
C {lab_pin.sym} 0 -100 0 0 {name=l6 lab=vss}
C {lab_pin.sym} -70 20 0 1 {name=l7 lab=clk}
C {lab_pin.sym} -70 60 0 1 {name=l8 lab=rst_n}
C {lab_pin.sym} 70 -20 0 0 {name=l9 lab=raw_bit}
C {lab_pin.sym} 70 20 0 0 {name=l10 lab=raw_valid}
C {lab_pin.sym} 70 -60 0 0 {name=l11 lab=ring_bit1}
C {lab_pin.sym} 70 60 0 0 {name=l12 lab=ring_bit2}
