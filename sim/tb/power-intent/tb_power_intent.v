// SPDX-License-Identifier: Apache-2.0
//
// Gate-level power-down / power-up testbench for the synthesized trng_top.
// Driven by sim/tools/power_intent_check.py, which derives the DUT netlist
// from design/trng_top/trng_top.synth.v (flip-flops swapped for the
// power-aware models in pi_cells.v, retained flops re-pointed at the
// always-on reset and the gated retention clock) and passes the timing
// parameters from design/power-intent.md.
//
// What is modelled
//   * the rail:      vdd_ok follows pwr_en after T_SETTLE (up) or T_DECAY
//                    (down) clock cycles; while it is low every gated flop is
//                    X and every output of the gated domain is X (the
//                    "dead rail" assigns below);
//   * isolation:     one PDK and2_1 per crossing output, on the always-on
//                    rail, clamp value 0;
//   * retention:     the retained flops sit on the always-on rail and are
//                    clocked by clk_ret, a PDK icgtp_1 gating of clk.
// What is checked here (X observation and architectural state); the ORDER of
// the control edges is checked by the tool from the PI_EVENT lines.
//
// Output protocol, one record per line:
//   PI_EVENT <time_ns> <event>        control-edge trace
//   PI_CHECK <name> PASS|FAIL         scenario assertions
//   PI_VIOLATION <class> t=<ns>       X / clamp monitor hits
//   PI_DONE violations=<n> failures=<n>
//
// VARIANT_* defines select the deliberately broken fixtures.

`timescale 1ns/1ps
`default_nettype none

module tb;
    parameter integer T_SETTLE = 20;   // rail settle, clock cycles (PLACEHOLDER, #707)
    parameter integer T_DECAY  = 8;    // rail decay, clock cycles (PLACEHOLDER, #707)
    localparam integer HALF = 5;       // 10 ns clock

    reg clk = 1'b0;
    always #HALF clk = ~clk;

    // ---- power-management controls (the sequencer's outputs)
    reg rst_ao_n = 1'b0;    // always-on power-on reset (retained flops only)
    reg rst_g_n  = 1'b0;    // gated-domain reset
    reg pwr_en   = 1'b0;    // switch control
    reg iso_n    = 1'b0;    // isolation, active low (clamp while low)
`ifdef VARIANT_RET_CLK_ON
    reg ret_clk_en = 1'b1;
`else
    reg ret_clk_en = 1'b0;
`endif
    reg vdd_ok   = 1'b0;    // gated rail good

    always @(pwr_en) begin : rail
        if (pwr_en) begin
            #(T_SETTLE*2*HALF);
            if (pwr_en) vdd_ok = 1'b1;
        end else begin
            #(T_DECAY*2*HALF);
            if (!pwr_en) vdd_ok = 1'b0;
        end
    end

    // ---- control-edge trace
    always @(posedge pwr_en)    $display("PI_EVENT %0d pwr_on", $time);
    always @(negedge pwr_en)    $display("PI_EVENT %0d pwr_off", $time);
    always @(posedge vdd_ok)    $display("PI_EVENT %0d rail_good", $time);
    always @(negedge vdd_ok)    $display("PI_EVENT %0d rail_off", $time);
    always @(posedge iso_n)     $display("PI_EVENT %0d iso_release", $time);
    always @(negedge iso_n)     $display("PI_EVENT %0d iso_assert", $time);
    always @(posedge rst_g_n)   $display("PI_EVENT %0d rst_release", $time);
    always @(negedge rst_g_n)   $display("PI_EVENT %0d rst_assert", $time);
    always @(posedge ret_clk_en) $display("PI_EVENT %0d ret_clk_on", $time);
    always @(negedge ret_clk_en) $display("PI_EVENT %0d ret_clk_off", $time);

    // ---- environment (stays alive across the power cycle)
    reg        raw_bit = 1'b0, raw_valid = 1'b0;
    reg  [1:0] ring_bit = 2'b00;
    reg        reg_sel = 1'b0, reg_write = 1'b0;
    reg  [1:0] reg_addr = 2'd0;
    reg [31:0] reg_wdata = 32'd0;
    reg        str_ready = 1'b0;
    reg        raw_run = 1'b0, raw_stuck = 1'b0;
    integer    seed = 32'h1234abcd;

    always @(negedge clk) begin
        raw_valid <= raw_run;
        raw_bit   <= raw_stuck ? 1'b1 : ($random(seed) & 1);
        ring_bit  <= $random(seed);
    end

    // ---- DUT: gated domain (derived netlist) + retention clock gate
    wire        clk_ret;
    gf180mcu_fd_sc_mcu9t5v0__icgtp_1 u_ret_cg (.CLK(clk), .E(ret_clk_en), .TE(1'b0), .Q(clk_ret));

    wire [31:0] reg_rdata_d, str_data_d;
    wire        str_valid_d, ht_alarm_d;

    trng_top dut (
        .clk(clk), .rst_n(rst_g_n), .rst_ao_n(rst_ao_n), .clk_ret(clk_ret),
        .raw_bit(raw_bit), .raw_valid(raw_valid), .ring_bit(ring_bit),
        .reg_sel(reg_sel), .reg_write(reg_write), .reg_addr(reg_addr),
        .reg_wdata(reg_wdata), .reg_rdata(reg_rdata_d),
        .str_data(str_data_d), .str_valid(str_valid_d), .str_ready(str_ready),
        .ht_alarm(ht_alarm_d)
    );

    // ---- dead-rail model and isolation (the crossing set)
    wire [65:0] dut_o  = {reg_rdata_d, str_data_d, str_valid_d, ht_alarm_d};
    wire [65:0] rail_o = (vdd_ok === 1'b1) ? dut_o : {66{1'bx}};
    wire [65:0] pad_o;
`ifdef VARIANT_NO_ISO
    localparam integer BYPASS = 10;    // str_data[8] left without a clamp
`else
    localparam integer BYPASS = -1;
`endif
    genvar gi;
    generate for (gi = 0; gi < 66; gi = gi + 1) begin : iso
        if (gi == BYPASS) begin : bare
            assign pad_o[gi] = rail_o[gi];
        end else begin : clamp
            gf180mcu_fd_sc_mcu9t5v0__and2_1 u_iso (.A1(rail_o[gi]), .A2(iso_n), .Z(pad_o[gi]));
        end
    end endgenerate

    wire [31:0] reg_rdata = pad_o[65:34];
    wire        ht_alarm  = pad_o[0];

    // ---- monitors
    integer n_viol = 0, n_fail = 0;
    reg [8*40-1:0] last_class;
    task violate(input [8*40-1:0] cls);
        begin
            n_viol = n_viol + 1;
            $display("PI_VIOLATION %0s t=%0d", cls, $time);
        end
    endtask
    task check(input [8*40-1:0] name, input ok);
        begin
            if (ok) $display("PI_CHECK %0s PASS", name);
            else begin n_fail = n_fail + 1; $display("PI_CHECK %0s FAIL", name); end
        end
    endtask

    always @(negedge clk) begin
        if (iso_n === 1'b0 && pad_o !== 66'd0) violate("unisolated_output");
        if (iso_n === 1'b1 && (^pad_o) === 1'bx) violate("x_on_visible_output");
    end

    // ---- sequencer tasks
    task cycles(input integer n); begin repeat (n) @(negedge clk); end endtask

    task power_down;
        begin
            @(negedge clk);
`ifndef VARIANT_RET_CLK_ON
            ret_clk_en = 1'b0;
`endif
            cycles(2); iso_n = 1'b0;
            cycles(2); rst_g_n = 1'b0;
            cycles(1); pwr_en = 1'b0;
        end
    endtask

    task power_up;
        begin
`ifndef VARIANT_NO_DECAY_WAIT
            if (vdd_ok !== 1'b0) wait (vdd_ok === 1'b0);
`endif
            @(negedge clk); pwr_en = 1'b1;
`ifdef VARIANT_ISO_EARLY
            cycles(2); iso_n = 1'b1;
`endif
            wait (vdd_ok === 1'b1);
            cycles(2);
`ifdef VARIANT_RESET_EARLY
            rst_g_n = 1'b1; cycles(2); iso_n = 1'b1;
`else
            iso_n = 1'b1; cycles(2); rst_g_n = 1'b1;
`endif
            cycles(2);
`ifndef VARIANT_RET_CLK_ON
            ret_clk_en = 1'b1;
`endif
            cycles(1);
        end
    endtask

    // ---- register bus
    localparam [1:0] A_CTRL = 2'd0, A_STATUS = 2'd1;
    reg [31:0] v;
    task bus_write(input [1:0] a, input [31:0] d);
        begin
            @(negedge clk); reg_sel = 1'b1; reg_write = 1'b1; reg_addr = a; reg_wdata = d;
            @(negedge clk); reg_sel = 1'b0; reg_write = 1'b0;
        end
    endtask
    task bus_read(input [1:0] a);
        begin
            @(negedge clk); reg_sel = 1'b1; reg_write = 1'b0; reg_addr = a;
            #2 v = reg_rdata;
            @(negedge clk); reg_sel = 1'b0;
        end
    endtask

    // ---- scenarios
    initial begin
        cycles(3); rst_ao_n = 1'b1;               // always-on power-on reset
        power_up;                                  // cold boot uses the wake sequence
        raw_run = 1'b1;
        bus_write(A_CTRL, 32'h3);                  // EN | OUT_MODE_RAW
        cycles(1400);                              // start-up test done, FIFOs filling, mid conditioner block
        bus_read(A_STATUS);
        check("pre_down_cond_ready", v[4] === 1'b1);
        bus_read(A_CTRL);
        check("pre_down_ctrl", v === 32'h3);

        // 1. power cycle with a register read pending across it
        @(negedge clk); reg_sel = 1'b1; reg_write = 1'b0; reg_addr = A_STATUS;
        power_down; cycles(30); power_up; cycles(2);
        reg_sel = 1'b0; cycles(1);
        bus_read(A_CTRL);
        check("ctrl_retained", v === 32'h3);
        bus_read(A_STATUS);
        check("state_reinitialised", (^v) !== 1'bx && v[3] === 1'b1 && v[4] === 1'b0 && v[19:16] === 4'd0);
        cycles(1400);
        bus_read(A_STATUS);
        check("startup_rerun", v[4] === 1'b1 && v[2] === 1'b0);

        // 2. alarm active at power-down
        raw_stuck = 1'b1; cycles(300); raw_stuck = 1'b0;
        bus_read(A_STATUS);
        check("alarm_set_pre_down", v[2] === 1'b1);
        power_down; cycles(20); power_up; cycles(2);
        bus_read(A_CTRL);
        check("ctrl_retained_with_alarm", v === 32'h3);
        bus_read(A_STATUS);
        check("alarm_survives_power_cycle", v[2] === 1'b1 && (v[0] === 1'b1 || v[1] === 1'b1 || v[9] === 1'b1));
        check("alarm_pin_survives", ht_alarm === 1'b1);

        // 3. back-to-back down/up (the sequencer waits out the decay)
        power_down; power_up; cycles(2);
        bus_read(A_CTRL);
        check("ctrl_retained_back_to_back", v === 32'h3);

        $display("PI_DONE violations=%0d failures=%0d", n_viol, n_fail);
        $finish;
    end

    initial begin
        #4000000;
        $display("PI_TIMEOUT");
        $finish;
    end
endmodule

`default_nettype wire
