// SPDX-License-Identifier: Apache-2.0
//
// On-die health tests: Repetition Count Test (RCT) + Adaptive Proportion
// Test (APT), plus the DR-0002 start-up test.
//
// Fixed by spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md.
// Verified against the bit-exact behavioural model in rct_apt.py
// (sim/tests/test_health_test.py runs both and requires identical pulse
// streams), at the level fixed by DR-0009.
//
// Structure
// ---------
//   raw_bit/raw_valid --> [ RCT: longest repeated run        ] --> ht_fail_rct
//   (DR-0001 raw tap)  --> [ APT: reference-value recurrence  ] --> ht_fail_apt
//                      --> [ start-up: 1024 clean samples     ] --> ht_startup_pass
//                                       ^
//                                 startup_req (restarts all three)
//
// RCT
// ---
// Counts the length of the current run of a repeated raw sample value.
// `ht_fail_rct` pulses for one cycle exactly when that run first reaches
// C_RCT; the counter then saturates (does not wrap) so a source stuck for
// far longer than C_RCT samples produces exactly one pulse, not a repeating
// one every C_RCT samples.
//
// APT
// ---
// Non-overlapping windows of W raw samples. The first sample of a window is
// its "reference"; `ht_fail_apt` pulses for one cycle exactly when the
// window completes (its Wth sample) with C_APT or more occurrences of the
// reference value, including the reference sample itself. A new window
// starts immediately, whether or not the previous one failed.
//
// Start-up test
// -------------
// A saturating counter of consecutive raw samples with neither test failing.
// `ht_startup_pass` pulses for one cycle exactly when it reaches
// STARTUP_SAMPLES (DR-0002: exactly 1024, i.e. == W by default). Any RCT/APT
// failure resets it to 0; so does `startup_req`.
//
// Reset / restart
// ---------------
//   rst_n         asynchronous power-on reset.
//   startup_req   synchronous restart: discards any in-flight RCT/APT window
//                 and the start-up counter (DR-0002 Sec.4 / DR-0013's
//                 interface contract). Takes priority over absorbing this
//                 cycle's raw sample -- the same priority `flush` has over
//                 absorption in crc32_conditioner.v.
//
// C_RCT, C_APT, W and STARTUP_SAMPLES are **parameters**, not hard-coded
// constants (DR-0002): the defaults below (81, 824, 1024, 1024) are the
// draft H0 = 0.5 cutoffs from rct_apt.py's formulas, mechanically checked
// against them by sim/tests/test_health_test.py -- not asserted here.
//
// C_APT must satisfy 1 <= C_APT <= W (DR-0002's APT degeneracy floor: no
// valid cutoff exists once the assumed H drops low enough). This is checked
// at elaboration time below; it is a simulation-time sanity check, not
// synthesizable logic.

`default_nettype none

module trng_health_test #(
    // Repetition Count Test cutoff. 1 + ceil(-log2(alpha) / H) (DR-0002).
    parameter integer C_RCT = 81,
    // Adaptive Proportion Test cutoff. Smallest C with Pr(X >= C) <= alpha
    // for X ~ Binomial(W, 2**-H) (DR-0002). Must satisfy 1 <= C_APT <= W.
    parameter integer C_APT = 824,
    // APT window size, binary source (DR-0002).
    parameter integer W = 1024,
    // Consecutive clean raw samples required for ht_startup_pass. DR-0002
    // fixes this at exactly W; kept as its own parameter for clarity.
    parameter integer STARTUP_SAMPLES = W
) (
    input  wire clk,          // sampler clock (DR-0012: fixed external)
    input  wire rst_n,        // async power-on reset, active low
    input  wire raw_bit,      // DR-0001 raw tap
    input  wire raw_valid,    // raw_bit carries a new sample this cycle
    input  wire startup_req,  // restart: discard in-flight window, re-arm start-up test
    output reg  ht_fail_rct,      // one-cycle RCT failure pulse
    output reg  ht_fail_apt,      // one-cycle APT failure pulse
    output reg  ht_startup_pass   // one-cycle pulse: STARTUP_SAMPLES clean samples
);

    localparam integer RCT_CNT_W = (C_RCT <= 1)   ? 1 : $clog2(C_RCT + 1);
    localparam integer APT_CNT_W = (W <= 1)       ? 1 : $clog2(W + 1);
    localparam integer SU_CNT_W  = (STARTUP_SAMPLES <= 1) ? 1 : $clog2(STARTUP_SAMPLES + 1);

    localparam [RCT_CNT_W-1:0] C_RCT_W = C_RCT[RCT_CNT_W-1:0];
    localparam [APT_CNT_W-1:0] C_APT_W = C_APT[APT_CNT_W-1:0];
    localparam [APT_CNT_W-1:0] W_W     = W[APT_CNT_W-1:0];
    localparam [SU_CNT_W-1:0]  SU_W    = STARTUP_SAMPLES[SU_CNT_W-1:0];

    // synthesis translate_off
    initial begin
        if (C_APT < 1 || C_APT > W) begin
            $display(
                "FATAL: C_APT=%0d is outside [1, W=%0d] -- DR-0002's APT degeneracy ",
                C_APT, W
            );
            $display(
                "floor: no valid cutoff exists at this H/alpha/W (H too low). ",
                "Recompute C_APT from a valid H via design/health_test/rct_apt.py."
            );
            $finish;
        end
        if (C_RCT < 1) begin
            $display("FATAL: C_RCT=%0d must be >= 1", C_RCT);
            $finish;
        end
        if (STARTUP_SAMPLES < 1) begin
            $display("FATAL: STARTUP_SAMPLES=%0d must be >= 1", STARTUP_SAMPLES);
            $finish;
        end
    end
    // synthesis translate_on

    // --- RCT state ---------------------------------------------------------
    reg [RCT_CNT_W-1:0] rct_run;       // 0 == no active run
    reg                 rct_last_bit;

    wire                 rct_match    = (rct_run != {RCT_CNT_W{1'b0}}) && (raw_bit == rct_last_bit);
    wire [RCT_CNT_W-1:0] rct_run_next = rct_match
        ? ((rct_run < C_RCT_W) ? rct_run + 1'b1 : rct_run)
        : {{(RCT_CNT_W-1){1'b0}}, 1'b1};
    wire rct_fires = (rct_run_next == C_RCT_W) && (rct_run != C_RCT_W);

    // --- APT state -----------------------------------------------------------
    reg [APT_CNT_W-1:0] apt_pos;       // 0 == window not yet started
    reg [APT_CNT_W-1:0] apt_match;
    reg                 apt_ref_bit;

    wire                 apt_window_starting = (apt_pos == {APT_CNT_W{1'b0}});
    wire [APT_CNT_W-1:0] apt_pos_next        = apt_pos + 1'b1;
    wire [APT_CNT_W-1:0] apt_match_next      = apt_window_starting
        ? {{(APT_CNT_W-1){1'b0}}, 1'b1}
        : (apt_match + ((raw_bit == apt_ref_bit) ? {{(APT_CNT_W-1){1'b0}}, 1'b1}
                                                  : {APT_CNT_W{1'b0}}));
    wire apt_window_done = (apt_pos_next == W_W);
    wire apt_fires       = apt_window_done && (apt_match_next >= C_APT_W);

    // --- start-up counter ------------------------------------------------
    reg [SU_CNT_W-1:0] startup_count;  // saturates at STARTUP_SAMPLES

    wire [SU_CNT_W-1:0] startup_count_next =
        (startup_count < SU_W) ? startup_count + 1'b1 : startup_count;
    wire startup_pass_fires = (startup_count < SU_W) && (startup_count_next == SU_W);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rct_run         <= {RCT_CNT_W{1'b0}};
            rct_last_bit    <= 1'b0;
            apt_pos         <= {APT_CNT_W{1'b0}};
            apt_match       <= {APT_CNT_W{1'b0}};
            apt_ref_bit     <= 1'b0;
            startup_count   <= {SU_CNT_W{1'b0}};
            ht_fail_rct     <= 1'b0;
            ht_fail_apt     <= 1'b0;
            ht_startup_pass <= 1'b0;
        end else begin
            ht_fail_rct     <= 1'b0;
            ht_fail_apt     <= 1'b0;
            ht_startup_pass <= 1'b0;

            if (startup_req) begin
                // Restart wins over absorption: a sample presented in the
                // same cycle as a restart belongs to the window being
                // discarded (mirrors crc32_conditioner.v's flush-over-absorb
                // priority).
                rct_run       <= {RCT_CNT_W{1'b0}};
                apt_pos       <= {APT_CNT_W{1'b0}};
                apt_match     <= {APT_CNT_W{1'b0}};
                startup_count <= {SU_CNT_W{1'b0}};
            end else if (raw_valid) begin
                rct_run      <= rct_run_next;
                rct_last_bit <= raw_bit;
                ht_fail_rct  <= rct_fires;

                apt_ref_bit  <= apt_window_starting ? raw_bit : apt_ref_bit;
                apt_pos      <= apt_window_done ? {APT_CNT_W{1'b0}} : apt_pos_next;
                apt_match    <= apt_window_done ? {APT_CNT_W{1'b0}} : apt_match_next;
                ht_fail_apt  <= apt_fires;

                if (rct_fires || apt_fires) begin
                    startup_count <= {SU_CNT_W{1'b0}};
                end else begin
                    startup_count   <= startup_count_next;
                    ht_startup_pass <= startup_pass_fires;
                end
            end
        end
    end

endmodule

`default_nettype wire
