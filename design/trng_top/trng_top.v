// SPDX-License-Identifier: Apache-2.0
//
// trng_top -- #27's top-level integration: the three digital blocks wired
// together exactly as trng_top.py wires their behavioural models, and as
// design/xschem/trng_top.sch's raw tap (clk/rst_n/raw_bit/raw_valid) feeds
// them. No logic lives in this file: every wire here is a straight
// connection between two of the three instantiated modules' own ports, so
// the registered-vs-combinational sequencing trng_top.py's module docstring
// works out by hand is exactly what plain Verilog signal flow already does
// -- rct_apt.v's ht_fail_rct/ht_fail_apt/ht_startup_pass are `output reg`
// (registered, stable for the cycle after the edge that set them) and
// trng_interface.v's cond_en/cond_flush/startup_req are `output wire`
// (combinational on this cycle's inputs), so wiring the three modules
// directly reproduces the one-cycle relationship trng_top.py's TopLevel.step
// imposes explicitly.
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

module trng_top (
    input  wire        clk,        // sampler clock (DR-0012: fixed external)
    input  wire        rst_n,      // async power-on reset, active low

    // The DR-0001 raw tap -- design/xschem/trng_top.sch's sampler_core.sym.
    input  wire        raw_bit,
    input  wire        raw_valid,

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
