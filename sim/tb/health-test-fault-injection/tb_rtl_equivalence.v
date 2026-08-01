// SPDX-License-Identifier: Apache-2.0
//
// Equivalence testbench: drives design/health_test/rct_apt.v with a per-cycle
// stimulus vector and dumps every (ht_fail_rct, ht_fail_apt, ht_startup_pass)
// pulse it emits. The Python side (sim/tests/test_health_test.py) generates
// the stimulus, runs the bit-exact behavioural model in
// design/health_test/rct_apt.py over the same vector, and requires the two
// pulse streams to be identical.
//
// This is what makes the behavioural model *normative* rather than merely
// illustrative (DR-0009): if the RTL and the model disagree, one of them is
// wrong and the check fails. Matches
// sim/tb/conditioner-crc32/tb_rtl_equivalence.v's pattern.
//
// The DUT is instantiated at its default parameters (C_RCT=81, C_APT=824,
// W=1024, STARTUP_SAMPLES=1024 -- the DR-0002 draft H0=0.5 cutoffs). Verilog
// module parameters are bound at elaboration, before any `+plusarg` is read
// in simulation, so they cannot be swept at run time through this file the
// way `HealthTest(c_rct=..., c_apt=...)` is swept on the Python side; the
// Python-side cutoff-table and degeneracy-floor checks in
// sim/tests/test_health_test.py exercise other H values against the pure
// Python cutoff functions instead (the same split
// sim/tb/conditioner-crc32/tb_rtl_equivalence.v's unused `+k=` already made).
//
// Plusargs:
//   +stim=<path>    stimulus file, one 3-bit binary vector per line:
//                     bit2 raw_bit, bit1 raw_valid, bit0 startup_req
//   +out=<path>     output file, one 3-bit binary vector per line:
//                     bit2 ht_fail_rct, bit1 ht_fail_apt, bit0 ht_startup_pass
//   +nvec=<n>       number of stimulus vectors to apply

`timescale 1ns / 1ps
`default_nettype none

module tb_rtl_equivalence;

    localparam integer MAX_VEC = 1 << 20;

    reg [2:0] stim [0:MAX_VEC-1];

    integer nvec;
    integer i;
    integer fout;
    reg [1023:0] stim_path;
    reg [1023:0] out_path;

    reg  clk = 1'b0;
    reg  rst_n = 1'b0;
    reg  raw_bit = 1'b0;
    reg  raw_valid = 1'b0;
    reg  startup_req = 1'b0;
    wire ht_fail_rct;
    wire ht_fail_apt;
    wire ht_startup_pass;

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
            raw_bit     = stim[i][2];
            raw_valid   = stim[i][1];
            startup_req = stim[i][0];
            @(posedge clk);
            #1;
            $fdisplay(fout, "%b%b%b", ht_fail_rct, ht_fail_apt, ht_startup_pass);
            @(negedge clk);
        end

        $fclose(fout);
        $finish;
    end

    trng_health_test dut (
        .clk            (clk),
        .rst_n          (rst_n),
        .raw_bit        (raw_bit),
        .raw_valid      (raw_valid),
        .startup_req    (startup_req),
        .ht_fail_rct    (ht_fail_rct),
        .ht_fail_apt    (ht_fail_apt),
        .ht_startup_pass(ht_startup_pass)
    );

endmodule

`default_nettype wire
