// SPDX-License-Identifier: Apache-2.0
//
// Equivalence testbench: drives design/conditioner/crc32_conditioner.v with a
// per-cycle stimulus vector and dumps every conditioned word it emits. The
// Python side (sim/tests/test_conditioner.py) generates the stimulus, runs the
// bit-exact behavioural model in design/conditioner/crc32_conditioner.py over
// the same vector, and requires the two word streams to be identical.
//
// This is what makes the behavioural model *normative* rather than merely
// illustrative (DR-0009): if the RTL and the model disagree, one of them is
// wrong and the check fails.
//
// Plusargs:
//   +stim=<path>   stimulus file, one 4-bit binary vector per line:
//                    bit3 raw_bit, bit2 raw_valid, bit1 en, bit0 flush
//   +out=<path>    output file, one %08h conditioned word per line
//   +nvec=<n>      number of stimulus vectors to apply
//   +k=<n>         compression ratio K (default 8)

`timescale 1ns / 1ps
`default_nettype none

module tb_rtl_equivalence;

    localparam integer MAX_VEC = 1 << 20;

    reg [3:0] stim [0:MAX_VEC-1];

    integer nvec;
    integer kparam;
    integer i;
    integer fout;
    reg [1023:0] stim_path;
    reg [1023:0] out_path;

    reg         clk = 1'b0;
    reg         rst_n = 1'b0;
    reg         raw_bit = 1'b0;
    reg         raw_valid = 1'b0;
    reg         en = 1'b1;
    reg         flush = 1'b0;
    wire [31:0] cond_word;
    wire        cond_valid;

    always #5 clk = ~clk;

    trng_conditioner_crc32 dut (
        .clk        (clk),
        .rst_n      (rst_n),
        .en         (en),
        .flush      (flush),
        .raw_bit    (raw_bit),
        .raw_valid  (raw_valid),
        .cond_word  (cond_word),
        .cond_valid (cond_valid)
    );

    initial begin
        if (!$value$plusargs("nvec=%d", nvec)) begin
            $display("FATAL: +nvec=<n> is required");
            $finish;
        end
        if (!$value$plusargs("k=%d", kparam)) kparam = 8;
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
            raw_bit   = stim[i][3];
            raw_valid = stim[i][2];
            en        = stim[i][1];
            flush     = stim[i][0];
            @(posedge clk);
            #1;
            if (cond_valid === 1'b1) $fdisplay(fout, "%08h", cond_word);
            @(negedge clk);
        end

        $fclose(fout);
        $finish;
    end

endmodule

`default_nettype wire
