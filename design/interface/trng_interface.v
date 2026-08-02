// SPDX-License-Identifier: Apache-2.0
//
// TRNG interface / register block -- register file, output FIFOs, OUT_MODE
// mux and the gate/flush state machine.
//
// Fixed by
// spec/decision-records/DR-0013-interface-register-map-and-streaming-semantics.md,
// which derives the contract from DR-0001 (raw/conditioned paths, OUT_MODE,
// flush-on-switch) and DR-0002 (latch-and-gate failure behaviour), plus
// DR-0016 (the per-ring liveness monitor's ring_stuck_any is a THIRD source
// of that same latch -- ht_fail_ring below -- not a second mechanism).
// Verified
// against the bit-exact behavioural model in trng_interface.py
// (sim/tests/test_interface.py runs both cycle-for-cycle and compares every
// output), at the level fixed by DR-0009 §2.
//
//                      +--------------------------------------------+
//   raw_bit/raw_valid  |  pack 32 raw samples LSB-first --> raw FIFO |--> RAW_DATA
//   (DR-0001 raw tap)  |                                     |       |    (never gated)
//                      |                                     +--mux--|--> str_data
//   cond_word/valid    |  conditioned FIFO -------------------+       |    (OUT_MODE)
//   (from #8)          |         ^                                   |--> DATA
//                      |    cond_en / cond_flush                     |    (gated)
//   ht_fail_* (#11) ---|--> latch --> ht_alarm, gate                 |
//   (rct | apt | ring)  |                                            |
//                      +--------------------------------------------+
//
// Addresses, bit positions and reset values are NOT written here: they come
// from the generated header trng_regmap.vh, which design/interface/regmap.py
// emits from the one normative table. `python3 design/interface/regmap.py
// --check` fails if this file's header and that table disagree.

`default_nettype none

module trng_interface #(
    // Words in each of the two output FIFOs. Must be a power of two.
    parameter integer FIFO_DEPTH = 8
) (
    input  wire        clk,              // sampler clock (DR-0012: fixed external)
    input  wire        rst_n,            // async power-on reset, active low

    // Sampler (#9) -- the DR-0001 raw tap.
    input  wire        raw_bit,
    input  wire        raw_valid,

    // Conditioner (#8).
    input  wire [31:0] cond_word,
    input  wire        cond_valid,
    output wire        cond_en,
    output wire        cond_flush,

    // Health tests (#11).
    input  wire        ht_fail_rct,
    input  wire        ht_fail_apt,
    // trng_ring_liveness.ring_stuck_any (DR-0016): a per-ring liveness
    // failure, on each ring's own digitized sample rather than the
    // XOR-combined raw tap RCT/APT observe. Treated identically to the two
    // above in every respect except which STATUS bit records it.
    input  wire        ht_fail_ring,
    input  wire        ht_startup_pass,
    output wire        startup_req,
    output wire        ht_alarm,

    // Register bus (synchronous to clk; a CDC wrapper is #27's).
    input  wire        reg_sel,
    input  wire        reg_write,
    input  wire [1:0]  reg_addr,
    input  wire [31:0] reg_wdata,
    output reg  [31:0] reg_rdata,

    // Streaming port.
    output wire [31:0] str_data,
    output wire        str_valid,
    input  wire        str_ready
);

`include "trng_regmap.vh"

    localparam integer PTR_W = (FIFO_DEPTH <= 2) ? 1 : $clog2(FIFO_DEPTH);
    localparam integer CNT_W = TRNG_LEVEL_BITS;

    // Block states. COND_READY is exactly ST_RUN.
    localparam [1:0] ST_IDLE    = 2'd0;  // CTRL.EN = 0
    localparam [1:0] ST_STARTUP = 2'd1;  // DR-0002 start-up test in progress
    localparam [1:0] ST_RUN     = 2'd2;  // conditioned path ungated
    localparam [1:0] ST_FAILED  = 2'd3;  // a latched HT_FAIL_* gates it

    reg [1:0] state;
    reg       ctrl_en;
    reg       ctrl_out_mode_raw;
    reg       fail_rct;
    reg       fail_apt;
    reg       fail_ring;
    reg       ovf_data;
    reg       ovf_raw;

    reg [31:0] cond_mem [0:FIFO_DEPTH-1];
    reg [31:0] raw_mem  [0:FIFO_DEPTH-1];
    reg [PTR_W-1:0] cond_head, raw_head;
    reg [CNT_W-1:0] cond_count, raw_count_w;

    reg [31:0] raw_shift;
    reg [TRNG_LEVEL_BITS+1:0] raw_bit_count;  // 0..RAW_PACK_BITS-1

    // ---------------------------------------------------------------- decode
    wire reg_read_c  = reg_sel && !reg_write;
    wire write_ctrl  = reg_sel &&  reg_write && (reg_addr == TRNG_ADDR_CTRL);
    wire write_stat  = reg_sel &&  reg_write && (reg_addr == TRNG_ADDR_STATUS);

    wire en_next     = write_ctrl ? reg_wdata[TRNG_CTRL_EN_BIT]       : ctrl_en;
    wire mode_next   = write_ctrl ? reg_wdata[TRNG_CTRL_OUT_MODE_BIT] : ctrl_out_mode_raw;
    wire soft_reset  = write_ctrl && reg_wdata[TRNG_CTRL_SOFT_RESET_BIT];
    wire mode_switch = (mode_next != ctrl_out_mode_raw);
    wire enable_rise = en_next && !ctrl_en;
    wire disable_now = !en_next && ctrl_en;

    // A failure pulse beats a write-1-to-clear presented in the same cycle:
    // set wins over clear, so a clear can never lose a failure.
    wire w1c_rct  = write_stat && reg_wdata[TRNG_STATUS_HT_FAIL_RCT_BIT];
    wire w1c_apt  = write_stat && reg_wdata[TRNG_STATUS_HT_FAIL_APT_BIT];
    wire w1c_ring = write_stat && reg_wdata[TRNG_STATUS_HT_FAIL_RING_BIT];
    wire fail_event     = (ht_fail_rct || ht_fail_apt || ht_fail_ring) && ctrl_en;
    wire fail_rct_next  = (ht_fail_rct  && ctrl_en) || (fail_rct  && !w1c_rct);
    wire fail_apt_next  = (ht_fail_apt  && ctrl_en) || (fail_apt  && !w1c_apt);
    wire fail_ring_next = (ht_fail_ring && ctrl_en) || (fail_ring && !w1c_ring);
    wire alarm_next    = fail_rct_next || fail_apt_next || fail_ring_next;
    wire alarm_now     = fail_rct || fail_apt || fail_ring;
    wire alarm_cleared = alarm_now && !alarm_next;

    // DR-0002 §Failure behavior 4: clearing the latched flag restarts the
    // noise source and the start-up health test. So does a soft reset and a
    // 0->1 transition of CTRL.EN. None of them can ungate a still-latched
    // alarm: alarm_next is evaluated ahead of restart in the state update.
    wire restart = (alarm_cleared || soft_reset || enable_rise) && en_next && !alarm_next;

    // Two flush scopes, and the difference between them is DR-0001 §5: a
    // health-test failure never touches the raw path.
    wire flush_raw  = mode_switch || restart || disable_now;
    wire flush_cond = flush_raw || fail_event;

    // ----------------------------------------------------------- FIFO status
    wire cond_ready = (state == ST_RUN);
    wire cond_avail = (cond_count != {CNT_W{1'b0}}) && cond_ready;
    wire raw_avail  = (raw_count_w != {CNT_W{1'b0}});

    wire read_data = reg_read_c && (reg_addr == TRNG_ADDR_DATA);
    wire read_raw  = reg_read_c && (reg_addr == TRNG_ADDR_RAW_DATA);

    // The streaming port and the register read share one FIFO per path. A
    // register read takes the cycle; the streaming port shows no valid word in
    // it, so a word can never be popped twice.
    assign str_valid = ctrl_out_mode_raw ? (raw_avail  && !read_raw  && !flush_raw)
                                         : (cond_avail && !read_data && !flush_cond);
    assign str_data  = ctrl_out_mode_raw ? (raw_avail  ? raw_mem[raw_head]   : 32'd0)
                                         : (cond_avail ? cond_mem[cond_head] : 32'd0);

    wire pop_stream = str_valid && str_ready;
    wire pop_data   = (read_data && cond_avail && !flush_cond) || (pop_stream && !ctrl_out_mode_raw);
    wire pop_raw    = (read_raw  && raw_avail  && !flush_raw)  || (pop_stream &&  ctrl_out_mode_raw);

    assign ht_alarm    = alarm_now;
    assign cond_flush  = flush_cond;
    assign cond_en     = cond_ready && !flush_cond;
    assign startup_req = restart;

    // -------------------------------------------------------- register reads
    wire [31:0] ctrl_value;
    wire [31:0] status_value;

    // SOFT_RESET is write-1-self-clearing and always reads 0.
    assign ctrl_value = (32'd0
        | ({31'd0, ctrl_en}           << TRNG_CTRL_EN_BIT)
        | ({31'd0, ctrl_out_mode_raw} << TRNG_CTRL_OUT_MODE_BIT));

    assign status_value = (32'd0
        | ({31'd0, fail_rct}                     << TRNG_STATUS_HT_FAIL_RCT_BIT)
        | ({31'd0, fail_apt}                     << TRNG_STATUS_HT_FAIL_APT_BIT)
        | ({31'd0, fail_ring}                    << TRNG_STATUS_HT_FAIL_RING_BIT)
        | ({31'd0, alarm_now}                    << TRNG_STATUS_HT_ALARM_BIT)
        | ({31'd0, (state == ST_STARTUP)}        << TRNG_STATUS_STARTUP_BIT)
        | ({31'd0, cond_ready}                   << TRNG_STATUS_COND_READY_BIT)
        | ({31'd0, (cond_count != {CNT_W{1'b0}})} << TRNG_STATUS_DATA_AVAIL_BIT)
        | ({31'd0, raw_avail}                    << TRNG_STATUS_RAW_AVAIL_BIT)
        | ({31'd0, ovf_data}                     << TRNG_STATUS_OVF_DATA_BIT)
        | ({31'd0, ovf_raw}                      << TRNG_STATUS_OVF_RAW_BIT)
        | ({{(32-CNT_W){1'b0}}, cond_count}      << TRNG_STATUS_DATA_LEVEL_LSB)
        | ({{(32-CNT_W){1'b0}}, raw_count_w}     << TRNG_STATUS_RAW_LEVEL_LSB));

    always @* begin
        reg_rdata = 32'd0;
        if (reg_read_c) begin
            case (reg_addr)
                TRNG_ADDR_CTRL:     reg_rdata = ctrl_value;
                TRNG_ADDR_STATUS:   reg_rdata = status_value;
                TRNG_ADDR_DATA:     reg_rdata = cond_avail ? cond_mem[cond_head] : 32'd0;
                TRNG_ADDR_RAW_DATA: reg_rdata = raw_avail  ? raw_mem[raw_head]   : 32'd0;
                default:            reg_rdata = 32'd0;
            endcase
        end
    end

    // ------------------------------------------------------------- datapath
    // Raw acquisition is never gated by health-test state (DR-0001 §5): it
    // runs in STARTUP, in RUN and in FAILED alike. Only CTRL.EN = 0 stops it,
    // and only a flush_raw event discards what it has buffered.
    wire        raw_absorb   = ctrl_en && raw_valid && !flush_raw;
    wire [31:0] raw_shift_nx = {raw_bit, raw_shift[31:1]};
    wire        raw_word_done = raw_absorb && (raw_bit_count == TRNG_RAW_PACK_BITS - 1);

    wire cond_push = cond_valid && cond_ready && !flush_cond;

    // A push into a full FIFO drops the *incoming* word, never a buffered one,
    // so what remains is always a contiguous run -- and OVF_* is how a reader
    // learns the run ended. A pop in the same cycle makes room.
    wire cond_room = (cond_count < FIFO_DEPTH) || pop_data;
    wire raw_room  = (raw_count_w < FIFO_DEPTH) || pop_raw;

    // Sticky overflow flags: write-1-to-clear, with a set in the same cycle
    // winning -- the same rule the HT_FAIL_* latches use, so a clear can never
    // lose an event.
    wire ovf_data_nx = (ovf_data && !(write_stat && reg_wdata[TRNG_STATUS_OVF_DATA_BIT]))
                       || (cond_push && !cond_room);
    wire ovf_raw_nx  = (ovf_raw  && !(write_stat && reg_wdata[TRNG_STATUS_OVF_RAW_BIT]))
                       || (raw_word_done && !raw_room);

    wire [PTR_W-1:0] cond_tail = cond_head + cond_count[PTR_W-1:0];
    wire [PTR_W-1:0] raw_tail  = raw_head  + raw_count_w[PTR_W-1:0];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ctrl_en           <= TRNG_CTRL_RESET[TRNG_CTRL_EN_BIT];
            ctrl_out_mode_raw <= TRNG_CTRL_RESET[TRNG_CTRL_OUT_MODE_BIT];
            state             <= TRNG_CTRL_RESET[TRNG_CTRL_EN_BIT] ? ST_STARTUP : ST_IDLE;
            fail_rct          <= 1'b0;
            fail_apt          <= 1'b0;
            fail_ring         <= 1'b0;
            ovf_data          <= 1'b0;
            ovf_raw           <= 1'b0;
            cond_head         <= {PTR_W{1'b0}};
            raw_head          <= {PTR_W{1'b0}};
            cond_count        <= {CNT_W{1'b0}};
            raw_count_w       <= {CNT_W{1'b0}};
            raw_shift         <= 32'd0;
            raw_bit_count     <= {(TRNG_LEVEL_BITS+2){1'b0}};
        end else begin
            ovf_data <= ovf_data_nx;
            ovf_raw  <= ovf_raw_nx;

            // -- conditioned FIFO
            if (flush_cond) begin
                cond_head  <= {PTR_W{1'b0}};
                cond_count <= {CNT_W{1'b0}};
            end else begin
                if (cond_push && cond_room)
                    cond_mem[cond_tail] <= cond_word;
                if (pop_data)
                    cond_head <= cond_head + 1'b1;
                case ({cond_push && cond_room, pop_data})
                    2'b10:   cond_count <= cond_count + 1'b1;
                    2'b01:   cond_count <= cond_count - 1'b1;
                    default: cond_count <= cond_count;
                endcase
            end

            // -- raw packing and raw FIFO
            if (flush_raw) begin
                raw_head      <= {PTR_W{1'b0}};
                raw_count_w   <= {CNT_W{1'b0}};
                raw_shift     <= 32'd0;
                raw_bit_count <= {(TRNG_LEVEL_BITS+2){1'b0}};
            end else begin
                if (raw_absorb) begin
                    raw_shift     <= raw_shift_nx;
                    raw_bit_count <= raw_word_done ? {(TRNG_LEVEL_BITS+2){1'b0}}
                                                   : raw_bit_count + 1'b1;
                end
                if (raw_word_done) begin
                    raw_shift <= 32'd0;
                    if (raw_room)
                        raw_mem[raw_tail] <= raw_shift_nx;
                end
                if (pop_raw)
                    raw_head <= raw_head + 1'b1;
                case ({raw_word_done && raw_room, pop_raw})
                    2'b10:   raw_count_w <= raw_count_w + 1'b1;
                    2'b01:   raw_count_w <= raw_count_w - 1'b1;
                    default: raw_count_w <= raw_count_w;
                endcase
            end

            // -- control/status latches
            fail_rct          <= fail_rct_next;
            fail_apt          <= fail_apt_next;
            fail_ring         <= fail_ring_next;
            ctrl_en           <= en_next;
            ctrl_out_mode_raw <= mode_next;

            // -- state machine
            if (!en_next)
                state <= ST_IDLE;
            else if (alarm_next)
                state <= ST_FAILED;
            else if (restart)
                state <= ST_STARTUP;
            else if ((state == ST_STARTUP) && ht_startup_pass)
                state <= ST_RUN;
        end
    end

endmodule

`default_nettype wire
