// SPDX-License-Identifier: Apache-2.0
//
// Equivalence testbench: drives design/health_test/ring_liveness.v with a
// per-cycle stimulus vector (one N_RINGS-wide row per sampler clock) and
// dumps every ring_stuck/ring_stuck_any pulse it emits. The Python side
// (sim/tests/test_ring_liveness.py) generates the stimulus, runs the
// bit-exact behavioural model in design/health_test/ring_liveness.py over
// the same vector, and requires the two pulse streams to be identical.
//
// This is what makes the behavioural model *normative* rather than merely
// illustrative (DR-0009), matching
// sim/tb/health-test-fault-injection/tb_rtl_equivalence.v's pattern.
//
// The DUT is instantiated at N_RINGS=2 (DR-0010's shipped array) and
// C_LIVE=81 (DR-0016's default -- DR-0002's own draft C_RCT at H0 = 0.5).
//
// Plusargs:
//   +stim=<path>    stimulus file, one 2-bit binary vector per line:
//                     bit1 ring_bit[1], bit0 ring_bit[0]
//   +out=<path>     output file, one 3-bit binary vector per line:
//                     bit2 ring_stuck[1], bit1 ring_stuck[0], bit0 ring_stuck_any
//   +nvec=<n>       number of stimulus vectors to apply

`timescale 1ns / 1ps
`default_nettype none

module tb_rtl_equivalence;

    localparam integer N_RINGS = 2;
    localparam integer C_LIVE = 81;
    localparam integer MAX_VEC = 1 << 20;

    reg [1:0] stim [0:MAX_VEC-1];

    integer nvec;
    integer i;
    integer fout;
    reg [1023:0] stim_path;
    reg [1023:0] out_path;

    reg  clk = 1'b0;
    reg  rst_n = 1'b0;
    reg  [N_RINGS-1:0] ring_bit = {N_RINGS{1'b0}};
    wire [N_RINGS-1:0] ring_stuck;
    wire ring_stuck_any;

    always #5 clk = ~clk;

    initial begin
        if (!$value$plusargs("nvec=%d", nvec)) begin
            $display("FATAL: +nvec=<n> is required");
            $finish;
        end
        if (!$value$plusargs("stim=%s", stim_path)) begin
            $display("FATAL: +stim=<path> is required");
            $finish;
        end
        if (!$value$plusargs("out=%s", out_path)) begin
            $display("FATAL: +out=<path> is required");
            $finish;
        end
        if (nvec > MAX_VEC) begin
            $display("FATAL: nvec %0d exceeds MAX_VEC %0d", nvec, MAX_VEC);
            $finish;
        end

        $readmemb(stim_path, stim);
        fout = $fopen(out_path, "w");
        if (fout == 0) begin
            $display("FATAL: cannot open output file");
            $finish;
        end

        // Two clocks of asynchronous reset, then release.
        @(negedge clk);
        @(negedge clk);
        rst_n = 1'b1;

        for (i = 0; i < nvec; i = i + 1) begin
            ring_bit = stim[i];
            @(posedge clk);
            #1;
            $fdisplay(fout, "%b%b", ring_stuck, ring_stuck_any);
            @(negedge clk);
        end

        $fclose(fout);
        $finish;
    end

    trng_ring_liveness #(
        .N_RINGS(N_RINGS),
        .C_LIVE (C_LIVE)
    ) dut (
        .clk           (clk),
        .rst_n         (rst_n),
        .ring_bit      (ring_bit),
        .ring_stuck    (ring_stuck),
        .ring_stuck_any(ring_stuck_any)
    );

endmodule

`default_nettype wire
