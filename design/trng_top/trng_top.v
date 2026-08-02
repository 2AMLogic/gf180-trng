// SPDX-License-Identifier: Apache-2.0
//
// trng_top -- #27's top-level integration: the four digital blocks wired
// together exactly as trng_top.py wires their behavioural models, and as
// design/xschem/trng_top.sch's raw tap (clk/rst_n/raw_bit/raw_valid) and
// per-ring liveness taps (ring_bit1/ring_bit2) feed them. No logic lives in
// this file: every wire here is a straight connection between two of the
// four instantiated modules' own ports, so the registered-vs-combinational
// sequencing trng_top.py's module docstring works out by hand is exactly
// what plain Verilog signal flow already does -- rct_apt.v's
// ht_fail_rct/ht_fail_apt/ht_startup_pass and ring_liveness.v's
// ring_stuck/ring_stuck_any are `output reg` (registered, stable for the
// cycle after the edge that set them) and trng_interface.v's
// cond_en/cond_flush/startup_req are `output wire` (combinational on this
// cycle's inputs), so wiring the modules directly reproduces the one-cycle
// relationship trng_top.py's TopLevel.step imposes explicitly.
//
// The liveness monitor (DR-0016) is wired here and nowhere else: its
// ring_stuck_any is the interface's ht_fail_ring, i.e. a THIRD source of the
// DR-0002 latch beside ht_fail_rct/ht_fail_apt, with the same alarm, the
// same conditioned-path-only gate and the same explicit-clear-plus-retest
// recovery. It exists because RCT/APT observe the XOR-combined raw tap,
// where one dead ring out of the shipped N=2 array is invisible.
//
// What is upstream of here (the entropy source, #7, and the sampler, #9) is
// transistor-level and is NOT this file's job: design/xschem/trng_top.sch
// is the analog half, per
// spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md,
// and clk/rst_n/raw_bit/raw_valid are exactly its four raw-tap output pins.
//
// A register-bus clock-domain-crossing wrapper (if the integrator's bus
// runs outside the sampler clock domain) is out of scope here too --
// design/interface/README.md and design/interface/trng_interface.v both
// name it as "#27's wrapper" without baking it in, and nothing about CDC is
// decided by this file.

`default_nettype none

module trng_top #(
    // Entropy-source rings monitored for liveness. DR-0010 ships N = 2, and
    // design/xschem/sampler_core.sch instantiates exactly that many
    // digitizers, so this is a parameter for readability rather than an
    // invitation to change one side only.
    parameter integer N_RINGS = 2
) (
    input  wire        clk,        // sampler clock (DR-0012: fixed external)
    input  wire        rst_n,      // async power-on reset, active low

    // The DR-0001 raw tap -- design/xschem/trng_top.sch's sampler_core.sym.
    input  wire        raw_bit,
    input  wire        raw_valid,

    // The DR-0016 per-ring liveness taps, from the same sampler_core.sym:
    // ring_bit[0] is design/xschem/trng_top.sch's ring_bit1 (ring 1, the
    // ro1 node), ring_bit[1] is ring_bit2 (ring 2, ro2). Already digitized
    // by their own sampler_dff and already synchronous to clk, which is the
    // input contract ring_liveness.v states. sim/tests/test_trng_top.py
    // checks that index mapping by name, because a silent swap here is
    // invisible in every waveform.
    input  wire [N_RINGS-1:0] ring_bit,

    // Register bus, synchronous to clk (see the CDC note above).
    input  wire        reg_sel,
    input  wire        reg_write,
    input  wire [1:0]  reg_addr,
    input  wire [31:0] reg_wdata,
    output wire [31:0] reg_rdata,

    // Streaming port.
    output wire [31:0] str_data,
    output wire        str_valid,
    input  wire        str_ready,

    // Latched health-test alarm, mirrored out for an integrator that wants
    // it as a discrete pin rather than a STATUS.HT_ALARM register read.
    output wire         ht_alarm
);

    wire        cond_en, cond_flush;
    wire [31:0] cond_word;
    wire        cond_valid;

    wire ht_fail_rct, ht_fail_apt, ht_startup_pass;
    wire startup_req;

    wire [N_RINGS-1:0] ring_stuck;
    wire               ring_stuck_any;

    trng_conditioner_crc32 u_conditioner (
        .clk       (clk),
        .rst_n     (rst_n),
        .en        (cond_en),
        .flush     (cond_flush),
        .raw_bit   (raw_bit),
        .raw_valid (raw_valid),
        .cond_word (cond_word),
        .cond_valid(cond_valid)
    );

    trng_health_test u_health_test (
        .clk            (clk),
        .rst_n          (rst_n),
        .raw_bit        (raw_bit),
        .raw_valid      (raw_valid),
        .startup_req    (startup_req),
        .ht_fail_rct    (ht_fail_rct),
        .ht_fail_apt    (ht_fail_apt),
        .ht_startup_pass(ht_startup_pass)
    );

    trng_ring_liveness #(.N_RINGS(N_RINGS)) u_ring_liveness (
        .clk           (clk),
        .rst_n         (rst_n),
        .ring_bit      (ring_bit),
        .ring_stuck    (ring_stuck),
        .ring_stuck_any(ring_stuck_any)
    );

    // ring_stuck[] drives nothing downstream on purpose: STATUS.HT_FAIL_RING
    // says "a ring stopped", not "which ring", because a per-ring status bit
    // would make DR-0013's published register map depend on N_RINGS. The
    // per-ring pulses stay named and probeable at this net, which is where a
    // future per-ring report would take them from.

    trng_interface u_interface (
        .clk            (clk),
        .rst_n          (rst_n),
        .raw_bit        (raw_bit),
        .raw_valid      (raw_valid),
        .cond_word      (cond_word),
        .cond_valid     (cond_valid),
        .cond_en        (cond_en),
        .cond_flush     (cond_flush),
        .ht_fail_rct    (ht_fail_rct),
        .ht_fail_apt    (ht_fail_apt),
        .ht_fail_ring   (ring_stuck_any),
        .ht_startup_pass(ht_startup_pass),
        .startup_req    (startup_req),
        .ht_alarm       (ht_alarm),
        .reg_sel        (reg_sel),
        .reg_write      (reg_write),
        .reg_addr       (reg_addr),
        .reg_wdata      (reg_wdata),
        .reg_rdata      (reg_rdata),
        .str_data       (str_data),
        .str_valid      (str_valid),
        .str_ready      (str_ready)
    );

endmodule
