// SPDX-License-Identifier: Apache-2.0
//
// Power-aware stand-ins for the three flip-flop cells the synthesized
// trng_top uses (dffrnq_1, dffsnq_1, dffq_1). They are the behavioural
// power-down model for sim/tools/power_intent_check.py: a flop on a
// collapsed rail loses its state (Q goes X) and stays X until it is reset or
// clocked with defined data once the rail is back.
//
// RET = 1 marks a flop on the always-on rail (a retained element): it never
// sees the rail collapse. RET = 0 is a flop in the gated domain.
//
// The rail itself is the testbench's `tb.vdd_ok`; the models read it
// hierarchically rather than through a port so the netlist transform only has
// to rename cell types, not thread a supply net through every module. The
// rename is the whole of the "power-aware simulation" step: the combinational
// cells keep the PDK's own functional models.
//
// Reset is asynchronous and active low, as in the PDK cells. `clk_prev` is
// updated with a non-blocking assignment so that a rail event while CLK is
// high is not mistaken for a rising clock edge.

`default_nettype none

module pi_dffrnq_1 #(parameter RET = 0) (input wire CLK, input wire D, input wire RN, output reg Q);
    reg clk_prev;
    wire pwr = (RET != 0) ? 1'b1 : tb.vdd_ok;
    always @(CLK) clk_prev <= CLK;
    always @(CLK or RN or pwr) begin
        if (pwr !== 1'b1)       Q <= 1'bx;
        else if (RN === 1'b0)   Q <= 1'b0;
        else if (CLK === 1'b1 && clk_prev === 1'b0) Q <= D;
    end
endmodule

module pi_dffsnq_1 #(parameter RET = 0) (input wire CLK, input wire D, input wire SETN, output reg Q);
    reg clk_prev;
    wire pwr = (RET != 0) ? 1'b1 : tb.vdd_ok;
    always @(CLK) clk_prev <= CLK;
    always @(CLK or SETN or pwr) begin
        if (pwr !== 1'b1)         Q <= 1'bx;
        else if (SETN === 1'b0)   Q <= 1'b1;
        else if (CLK === 1'b1 && clk_prev === 1'b0) Q <= D;
    end
endmodule

module pi_dffq_1 #(parameter RET = 0) (input wire CLK, input wire D, output reg Q);
    reg clk_prev;
    wire pwr = (RET != 0) ? 1'b1 : tb.vdd_ok;
    always @(CLK) clk_prev <= CLK;
    always @(CLK or pwr) begin
        if (pwr !== 1'b1)       Q <= 1'bx;
        else if (CLK === 1'b1 && clk_prev === 1'b0) Q <= D;
    end
endmodule

`default_nettype wire
