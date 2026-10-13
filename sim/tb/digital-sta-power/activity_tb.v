// Switching-activity capture bench for the post-route netlist (#453).
//
// Drives layout/digital/trng_top.pnr.v (zero delay: run with -gno-specify)
// from a packed per-cycle stimulus file and dumps a VCD of the DUT scope
// only. Plusargs: +STIM=<hex file> +CYCLES=<n> +VCD=<out> +PERIOD_NS=<ns>.
//
// Row layout (48-bit word, mirrored by activity_workloads.pack_row):
//   [0] rst_n [1] raw_bit [2] raw_valid [4:3] ring_bit [5] reg_sel
//   [6] reg_write [8:7] reg_addr [40:9] reg_wdata [41] str_ready
//
// Rows change on the falling edge, half a period after the capturing rising
// edge, so cycle i occupies [i*PERIOD, (i+1)*PERIOD) and no input moves on
// a clock edge. The DUT instance is `tb.dut`: that scope name is part of
// the contract with activity.py's annotation validation.
`timescale 1ns/1ps
module tb;
  reg clk = 1'b0;
  reg [47:0] mem [0:65535];
  integer cycles, i;
  real period;
  reg [1023:0] stim_file, vcd_file;

  reg rst_n, raw_bit, raw_valid, reg_sel, reg_write, str_ready;
  reg [1:0] ring_bit, reg_addr;
  reg [31:0] reg_wdata;
  wire [31:0] reg_rdata, str_data;
  wire str_valid, ht_alarm;

  trng_top dut (
    .clk(clk), .rst_n(rst_n), .raw_bit(raw_bit), .raw_valid(raw_valid),
    .ring_bit(ring_bit), .reg_sel(reg_sel), .reg_write(reg_write),
    .reg_addr(reg_addr), .reg_wdata(reg_wdata), .reg_rdata(reg_rdata),
    .str_data(str_data), .str_valid(str_valid), .str_ready(str_ready),
    .ht_alarm(ht_alarm));

  task apply(input [47:0] w);
    begin
      rst_n = w[0]; raw_bit = w[1]; raw_valid = w[2]; ring_bit = w[4:3];
      reg_sel = w[5]; reg_write = w[6]; reg_addr = w[8:7];
      reg_wdata = w[40:9]; str_ready = w[41];
    end
  endtask

  initial begin
    if (!$value$plusargs("STIM=%s", stim_file)) begin $display("ERROR no +STIM"); $finish; end
    if (!$value$plusargs("CYCLES=%d", cycles)) begin $display("ERROR no +CYCLES"); $finish; end
    if (!$value$plusargs("VCD=%s", vcd_file)) begin $display("ERROR no +VCD"); $finish; end
    if (!$value$plusargs("PERIOD_NS=%f", period)) period = 1000.0;
    $readmemh(stim_file, mem, 0, cycles - 1);
    $dumpfile(vcd_file);
    $dumpvars(0, tb.dut);  // whole DUT hierarchy: OpenSTA binds activity to cell pins by path
    apply(mem[0]);
    for (i = 0; i < cycles; i = i + 1) begin
      apply(mem[i]);
      #(period/2.0) clk = 1'b1;
      #(period/2.0) clk = 1'b0;
    end
    $finish;
  end
endmodule
