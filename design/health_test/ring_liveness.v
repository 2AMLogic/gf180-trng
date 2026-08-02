// SPDX-License-Identifier: Apache-2.0
//
// Per-ring liveness monitor: N independent instances of DR-0002's Repetition
// Count Test (RCT), one per entropy-source ring, catching a stuck or dead
// ring that the block-level RCT/APT tests cannot see by construction (they
// observe the XOR-combined raw tap, where a dead ring contributes a constant
// and the surviving ring keeps the raw stream looking plausible -- see
// design/README.md "Per-ring liveness" and DR-0016).
//
// Fixed by spec/decision-records/DR-0016-per-ring-liveness-monitor.md.
// Verified against the bit-exact behavioural model in ring_liveness.py
// (sim/tests/test_ring_liveness.py runs both and requires identical pulse
// streams), at the level fixed by DR-0009.
//
// Mechanism
// ---------
// DR-0002's RCT already exists to catch exactly this failure signature -- a
// sampled bit repeating far more often than an effectively-random source
// would -- but it observes the *combined* raw tap, where with N=2 rings one
// dead ring still leaves a live ring driving the XOR node, so the combined
// stream keeps looking plausible. This module runs the IDENTICAL run-length
// test, with the IDENTICAL cutoff formula, independently on each ring's own
// already-digitized, already-clk-synchronized sample (`ring_bit[i]` --
// produced upstream by a per-ring digitizer structurally identical to the
// raw tap's own `sampler_dff`, per DR-0016). No new statistical assumption
// is introduced: C_LIVE defaults to 81, DR-0002's own C_RCT at the draft
// H0 = 0.5 (rct_apt.py's `c_rct(H0)`), so a future ratified worst-corner H
// (#13) updates both cutoffs from the same edit, not two.
//
// `ring_stuck[i]` pulses for one cycle exactly when ring i's own digitized
// bit first repeats C_LIVE times in a row; the run counter then SATURATES
// (does not wrap), so a ring stuck far longer than C_LIVE samples produces
// exactly one pulse per stall onset, not a periodic one -- the same
// saturating-run idiom rct_apt.v's own RCT counter uses (this is, in fact,
// the same counter, replicated per ring rather than run once on the
// combined tap).
//
// `ring_stuck_any` is the bitwise OR of `ring_stuck`, meant to be OR'd into
// the SAME latch-and-gate mechanism DR-0002 already defines for
// `ht_fail_rct`/`ht_fail_apt` (DR-0016 "Failure behavior": flag, not hard
// stop). This module never latches or gates anything itself -- exactly the
// boundary rct_apt.v draws for its own ht_fail_* pulses.
//
// Interface contract (DR-0016): `ring_bit` is assumed ALREADY digitized and
// ALREADY synchronized to `clk` by an upstream per-ring digitizer -- the same
// job description `sampler_dff` already performs for `xo` -> `raw_bit`.
// This module adds no synchronizer of its own and is ordinary digital logic,
// exactly as design/README.md's "Per-ring liveness" section anticipates.
// Nothing here creates a new externally-exposed per-ring pin (DR-0001):
// `ring_bit` and `ring_stuck`/`ring_stuck_any` are internal health-test-block
// signals, the same status as `raw_bit`/`ht_fail_rct` already are.
//
// Why RCT only, no per-ring APT: RCT alone already gives a deterministic,
// bounded detection of "ring frozen at a single value" -- this issue's
// stated failure mode (a stuck or dead ring). A per-ring APT would mostly
// re-detect the same failure at worse latency without covering a
// materially different, demonstrated fault mode; see DR-0016 "Revisit if".

`default_nettype none

module trng_ring_liveness #(
    // Number of rings monitored. DR-0010 ships N = 2.
    parameter integer N_RINGS = 2,
    // Consecutive repeated digitized samples of a ring's own bit before that
    // ring is declared stuck. Default 81 = rct_apt.c_rct(H0=0.5) -- DR-0002's
    // own draft C_RCT, reused rather than re-derived. Mechanically checked
    // against rct_apt.py by sim/tests/test_ring_liveness.py, the same
    // discipline RtlDefaultParameterTests already applies to rct_apt.v.
    parameter integer C_LIVE = 81
) (
    input  wire                  clk,          // sampler clock (DR-0012: fixed external)
    input  wire                  rst_n,        // async power-on reset, active low
    input  wire [N_RINGS-1:0]    ring_bit,     // already-digitized, clk-synchronized per-ring sample
    output reg  [N_RINGS-1:0]    ring_stuck,   // one-cycle pulse per ring: C_LIVE-th consecutive repeat
    output wire                  ring_stuck_any // OR of ring_stuck -- feeds DR-0002's alarm/gate path
);

    // synthesis translate_off
    initial begin
        if (N_RINGS < 1) begin
            $display("FATAL: N_RINGS=%0d must be >= 1", N_RINGS);
            $finish;
        end
        if (C_LIVE < 1) begin
            $display("FATAL: C_LIVE=%0d must be >= 1", C_LIVE);
            $finish;
        end
    end
    // synthesis translate_on

    localparam integer CNT_W = (C_LIVE <= 1) ? 1 : $clog2(C_LIVE + 1);
    localparam [CNT_W-1:0] C_LIVE_W = C_LIVE[CNT_W-1:0];

    reg [N_RINGS-1:0] ring_last_bit;
    reg [CNT_W-1:0]   ring_run [0:N_RINGS-1];  // 0 == no active run

    assign ring_stuck_any = |ring_stuck;

    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ring_last_bit <= {N_RINGS{1'b0}};
            ring_stuck    <= {N_RINGS{1'b0}};
            for (i = 0; i < N_RINGS; i = i + 1) begin
                ring_run[i] <= {CNT_W{1'b0}};
            end
        end else begin
            for (i = 0; i < N_RINGS; i = i + 1) begin
                if (ring_run[i] != {CNT_W{1'b0}} && ring_bit[i] == ring_last_bit[i]) begin
                    // Matching run continues; saturate at C_LIVE rather than wrap.
                    if (ring_run[i] < C_LIVE_W) begin
                        ring_run[i]   <= ring_run[i] + 1'b1;
                        ring_stuck[i] <= (ring_run[i] + 1'b1) == C_LIVE_W;
                    end else begin
                        ring_run[i]   <= ring_run[i];
                        ring_stuck[i] <= 1'b0;
                    end
                end else begin
                    // Value changed (or first sample after reset): run restarts at 1.
                    ring_run[i]   <= {{(CNT_W-1){1'b0}}, 1'b1};
                    ring_stuck[i] <= 1'b0;
                end
                ring_last_bit[i] <= ring_bit[i];
            end
        end
    end

endmodule

`default_nettype wire
