// SPDX-License-Identifier: Apache-2.0
//
// TRNG digital conditioner -- 32-bit CRC-32 LFSR compression, K:1.
//
// Fixed by spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md.
// Verified against the bit-exact behavioural model in crc32_conditioner.py
// (sim/tests/test_conditioner.py runs both and compares word-for-word), at
// the level fixed by DR-0009.
//
// Structure
// ---------
//   raw_bit --> [ 32-bit Galois LFSR, poly 0xEDB88320 ] --> cond_word[31:0]
//                        ^                                       ^
//                  clear per block                          cond_valid
//
// One conditioned word is a function of exactly BLOCK_BITS = 32*K raw
// samples and of no earlier sample: the LFSR is cleared at every block
// boundary. That is what makes the SP 800-90B conditioning-component
// accounting in DR-0008 apply per block with n_in = BLOCK_BITS,
// n_out = nw = 32.
//
// Reset / flush
// -------------
//   rst_n  asynchronous power-on reset.
//   flush  synchronous flush. Asserted by the register/streaming block (#26)
//          on a health-test-failure gate (DR-0002) and on an OUT_MODE switch
//          (DR-0001). Clears the LFSR and discards the partial block, so no
//          bit absorbed before the flush can influence any later output word.
//   en     conditioned path enabled. While low the conditioner is held
//          cleared, which is why the DR-0002 start-up test time and the
//          conditioner fill time add rather than overlap.
//
// The output FIFO, the OUT_MODE mux, the DATA/RAW_DATA registers and the
// generation of `en`/`flush` are NOT in this module -- they are #26's half
// of the interface. This module owns only the conditioner-internal state.

`default_nettype none

module trng_conditioner_crc32 #(
    // Compression ratio K: raw bits in per conditioned bit out.
    parameter integer K         = 8,
    // Output word width. DR-0008 fixes 32; the entropy accounting is stated
    // for 32 and does not carry over unchanged to another width.
    parameter integer WORD_BITS = 32,
    // CRC-32 (IEEE 802.3) feedback polynomial, LSB-first reflected form.
    parameter [31:0]  POLY      = 32'hEDB88320
) (
    input  wire                  clk,        // sampler clock
    input  wire                  rst_n,      // async power-on reset, active low
    input  wire                  en,         // conditioned path enabled
    input  wire                  flush,      // synchronous flush request
    input  wire                  raw_bit,    // DR-0001 raw tap
    input  wire                  raw_valid,  // raw_bit is a new sample this cycle
    output reg  [WORD_BITS-1:0]  cond_word,  // conditioned output word
    output reg                   cond_valid  // one-cycle strobe
);

    localparam integer BLOCK_BITS = WORD_BITS * K;
    localparam integer CNT_W      = (BLOCK_BITS <= 2) ? 1 : $clog2(BLOCK_BITS);

    reg [WORD_BITS-1:0] state;
    reg [CNT_W-1:0]     count;

    // Galois LFSR step: shift right, XOR the polynomial back in when the
    // feedback bit is set. 13 XOR2 for the taps (bit 31 needs none -- the
    // shifted-in bit is 0) plus one XOR2 for the feedback itself.
    wire                 fb         = state[0] ^ raw_bit;
    wire [WORD_BITS-1:0] shifted    = {1'b0, state[WORD_BITS-1:1]};
    wire [WORD_BITS-1:0] next_state = shifted ^ ({WORD_BITS{fb}} & POLY);

    wire block_done = (count == BLOCK_BITS[CNT_W-1:0] - 1'b1);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state      <= {WORD_BITS{1'b0}};
            count      <= {CNT_W{1'b0}};
            cond_word  <= {WORD_BITS{1'b0}};
            cond_valid <= 1'b0;
        end else begin
            cond_valid <= 1'b0;
            if (flush || !en) begin
                // Flush wins over absorption: a raw bit presented in the same
                // cycle as the gate belongs to the failing window (DR-0002).
                state <= {WORD_BITS{1'b0}};
                count <= {CNT_W{1'b0}};
            end else if (raw_valid) begin
                if (block_done) begin
                    cond_word  <= next_state;
                    cond_valid <= 1'b1;
                    state      <= {WORD_BITS{1'b0}};
                    count      <= {CNT_W{1'b0}};
                end else begin
                    state <= next_state;
                    count <= count + 1'b1;
                end
            end
        end
    end

endmodule

`default_nettype wire
