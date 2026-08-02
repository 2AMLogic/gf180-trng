// SPDX-License-Identifier: Apache-2.0
//
// Equivalence testbench: drives design/interface/trng_interface.v with a
// per-cycle stimulus vector and dumps *every* output the block drives, every
// cycle. The Python side (sim/tests/test_interface.py) generates the stimulus,
// runs the bit-exact behavioural model in design/interface/trng_interface.py
// over the same vector, and requires the two output streams to be identical
// cycle for cycle.
//
// This is what makes the behavioural model *normative* rather than merely
// illustrative (DR-0009 rule 5): if the RTL and the model disagree, one of
// them is wrong and the check fails.
//
// Sampling convention: the block's reg_rdata / str_data / str_valid /
// ht_alarm / cond_en / cond_flush / startup_req are combinational in the
// access cycle -- functions of the state *before* the rising edge and of the
// inputs applied in that cycle (DR-0013 §Decision, "Flush timing"). The loop
// below therefore applies inputs after the falling edge, samples the outputs
// before the rising edge, and only then lets the edge update the state. That
// is exactly the order the Python model's step() computes in.
//
// Plusargs:
//   +stim=<path>   stimulus file, one 76-bit hex vector per line (see the bit
//                  layout below; sim/tests/test_interface.py writes it)
//   +out=<path>    output file, one line per cycle:
//                    <reg_rdata:08h> <str_data:08h> <str_valid><ht_alarm>
//                    <cond_en><cond_flush><startup_req>
//   +nvec=<n>      number of stimulus vectors to apply

`timescale 1ns / 1ps
`default_nettype none

module tb_rtl_equivalence;

    localparam integer MAX_VEC = 1 << 16;

    // Stimulus bit layout, MSB first:
    //   [75] ht_fail_ring (DR-0016; appended ABOVE the pre-existing layout so
    //        adding a third failure source did not renumber any other field)
    //   [74:43] cond_word     [42:11] reg_wdata     [10:9] reg_addr
    //   [8] raw_bit  [7] raw_valid  [6] cond_valid  [5] ht_fail_rct
    //   [4] ht_fail_apt  [3] ht_startup_pass  [2] reg_sel  [1] reg_write
    //   [0] str_ready
    reg [75:0] stim [0:MAX_VEC-1];

    integer nvec;
    integer i;
    integer fout;
    reg [1023:0] stim_path;
    reg [1023:0] out_path;

    reg         clk = 1'b0;
    reg         rst_n = 1'b0;

    reg         raw_bit = 1'b0;
    reg         raw_valid = 1'b0;
    reg  [31:0] cond_word = 32'd0;
    reg         cond_valid = 1'b0;
    reg         ht_fail_rct = 1'b0;
    reg         ht_fail_apt = 1'b0;
    reg         ht_fail_ring = 1'b0;
    reg         ht_startup_pass = 1'b0;
    reg         reg_sel = 1'b0;
    reg         reg_write = 1'b0;
    reg  [1:0]  reg_addr = 2'd0;
    reg  [31:0] reg_wdata = 32'd0;
    reg         str_ready = 1'b0;

    wire        cond_en;
    wire        cond_flush;
    wire        startup_req;
    wire        ht_alarm;
    wire [31:0] reg_rdata;
    wire [31:0] str_data;
    wire        str_valid;

    always #5 clk = ~clk;

    trng_interface #(.FIFO_DEPTH(8)) dut (
        .clk             (clk),
        .rst_n           (rst_n),
        .raw_bit         (raw_bit),
        .raw_valid       (raw_valid),
        .cond_word       (cond_word),
        .cond_valid      (cond_valid),
        .cond_en         (cond_en),
        .cond_flush      (cond_flush),
        .ht_fail_rct     (ht_fail_rct),
        .ht_fail_apt     (ht_fail_apt),
        .ht_fail_ring    (ht_fail_ring),
        .ht_startup_pass (ht_startup_pass),
        .startup_req     (startup_req),
        .ht_alarm        (ht_alarm),
        .reg_sel         (reg_sel),
        .reg_write       (reg_write),
        .reg_addr        (reg_addr),
        .reg_wdata       (reg_wdata),
        .reg_rdata       (reg_rdata),
        .str_data        (str_data),
        .str_valid       (str_valid),
        .str_ready       (str_ready)
    );

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

        $readmemh(stim_path, stim);
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
            cond_word       = stim[i][74:43];
            reg_wdata       = stim[i][42:11];
            reg_addr        = stim[i][10:9];
            raw_bit         = stim[i][8];
            raw_valid       = stim[i][7];
            cond_valid      = stim[i][6];
            ht_fail_rct     = stim[i][5];
            ht_fail_apt     = stim[i][4];
            ht_fail_ring    = stim[i][75];
            ht_startup_pass = stim[i][3];
            reg_sel         = stim[i][2];
            reg_write       = stim[i][1];
            str_ready       = stim[i][0];

            // Settle the combinational outputs, then record them -- before the
            // rising edge that consumes them.
            #1;
            $fdisplay(fout, "%08h %08h %b%b%b%b%b",
                      reg_rdata, str_data,
                      str_valid, ht_alarm, cond_en, cond_flush, startup_req);

            @(posedge clk);
            @(negedge clk);
        end

        $fclose(fout);
        $finish;
    end

endmodule

`default_nettype wire
