// SPDX-License-Identifier: Apache-2.0
//
// Equivalence testbench: drives the ASSEMBLED design/trng_top/trng_top.v
// (all four digital blocks wired together, exactly as #27 ships them) with a
// per-cycle stimulus vector and dumps every top-level output every cycle.
// The Python side (sim/tests/test_trng_top.py's AssembledCrossCheckTests)
// generates the stimulus, runs the same vector through the assembled
// behavioural model (design/trng_top/trng_top.TopLevel) and requires the two
// output streams to be identical cycle for cycle.
//
// Unlike design/conditioner/, design/health_test/ and design/interface/'s own
// per-block tb_rtl_equivalence.v testbenches (each of which drives one block
// in isolation against its own bit-exact model), this one exercises the
// CROSS-BLOCK handoffs that only exist once the blocks are wired together --
// exactly the class of bug #176 found: TopLevel.step handed
// ht_startup_pass and cond_word/cond_valid to the interface combinationally,
// in the same model cycle they were computed, when rct_apt.v and
// crc32_conditioner.v both register them (`output reg`) and trng_top.v wires
// them straight through with no extra delay. A per-block check cannot see
// that class of bug -- it never assembles a second block to hand a signal to.
//
// Sampling convention: the block's reg_rdata / str_data / str_valid /
// ht_alarm are combinational in the access cycle (DR-0013 Sec.Decision,
// "Flush timing"), the same convention
// sim/tb/interface-regfile/tb_rtl_equivalence.v uses. The loop below
// therefore applies inputs after the falling edge, samples the outputs
// before the rising edge, and only then lets the edge update every block's
// state -- exactly the order design/trng_top/trng_top.py's TopLevel.step
// computes in, one Python call per iteration of this loop.
//
// Plusargs:
//   +stim=<path>   stimulus file, one 41-bit hex vector per line (see the bit
//                  layout below; sim/tests/test_trng_top.py writes it)
//   +out=<path>    output file, one line per cycle:
//                    <reg_rdata:08h> <str_data:08h> <str_valid><ht_alarm>
//   +nvec=<n>      number of stimulus vectors to apply

`timescale 1ns / 1ps
`default_nettype none

module tb_rtl_equivalence;

    localparam integer MAX_VEC = 1 << 16;
    localparam integer N_RINGS = 2;

    // Stimulus bit layout, MSB first:
    //   [40] str_ready         [39:8] reg_wdata      [7:6] reg_addr
    //   [5] reg_write          [4] reg_sel           [3:2] ring_bit[1:0]
    //   [1] raw_valid          [0] raw_bit
    reg [40:0] stim [0:MAX_VEC-1];

    integer nvec;
    integer i;
    integer fout;
    reg [1023:0] stim_path;
    reg [1023:0] out_path;

    reg               clk = 1'b0;
    reg               rst_n = 1'b0;

    reg               raw_bit = 1'b0;
    reg               raw_valid = 1'b0;
    reg  [N_RINGS-1:0] ring_bit = {N_RINGS{1'b0}};
    reg               reg_sel = 1'b0;
    reg               reg_write = 1'b0;
    reg  [1:0]        reg_addr = 2'd0;
    reg  [31:0]       reg_wdata = 32'd0;
    reg               str_ready = 1'b0;

    wire [31:0] reg_rdata;
    wire [31:0] str_data;
    wire        str_valid;
    wire        ht_alarm;

    always #5 clk = ~clk;

    trng_top #(.N_RINGS(N_RINGS)) dut (
        .clk       (clk),
        .rst_n     (rst_n),
        .raw_bit   (raw_bit),
        .raw_valid (raw_valid),
        .ring_bit  (ring_bit),
        .reg_sel   (reg_sel),
        .reg_write (reg_write),
        .reg_addr  (reg_addr),
        .reg_wdata (reg_wdata),
        .reg_rdata (reg_rdata),
        .str_data  (str_data),
        .str_valid (str_valid),
        .str_ready (str_ready),
        .ht_alarm  (ht_alarm)
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
            raw_bit   = stim[i][0];
            raw_valid = stim[i][1];
            ring_bit  = stim[i][3:2];
            reg_sel   = stim[i][4];
            reg_write = stim[i][5];
            reg_addr  = stim[i][7:6];
            reg_wdata = stim[i][39:8];
            str_ready = stim[i][40];

            // Settle the combinational outputs, then record them -- before
            // the rising edge that consumes them.
            #1;
            $fdisplay(fout, "%08h %08h %b%b", reg_rdata, str_data, str_valid, ht_alarm);

            @(posedge clk);
            @(negedge clk);
        end

        $fclose(fout);
        $finish;
    end

endmodule

`default_nettype wire
