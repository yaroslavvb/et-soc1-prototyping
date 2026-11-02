// Q136(c): the VPU's register arrays, instrumented. Drop-in copies of core-et's three array modules with their behaviour
// unchanged (each body below is the original's, verbatim) and an accounting block added that only reads signals:
//   rf_latch_1r_1w               libs/rf_latches  - TenA (vpu_ctrl), TenB (two per lane, in each TIMA unit), TenTMP (vpu_ctrl)
//   vpu_tensorc_rf_buffer_array  libs/macros      - TenC (two per lane, in each TIMA unit): int8's accumulators
//   vpu_64x32_3r2w_vpurf         libs/macros      - the lane register file (one per lane): fp32's and fp16's accumulators
// Given on the Verilator command line, these definitions are used and the libraries' copies are never read (Verilator searches
// a -y directory only for a module nothing has defined).
//
// What each instance reports, once a cycle, sampled at the rising clock edge (pre-edge values: what the cycle settled to):
//   rf_latch_1r_1w (latches, no read enable: the read port is a mux on rd_addr_a)
//     writes        a write pulse this cycle (wr_en_a, which the entry's clock gate latched in the low phase)
//     bits_written  WIDTH per write: the latch bits of the written entry that are clocked
//     changed       storage bits that change at that write: rf[wr_addr_a] ^ wr_data_a_1p
//     dl_open       the write-data latch opened in the low phase before this edge (et_clk_gate_n's en_2p)
//     dl_changed    write-data latch bits that changed (wr_data_a_1p against its value one edge earlier)
//     raddr_tog     read-address bits that changed;  rdata_tog  read-data bits that changed (rd_data_a, combinational)
//   vpu_tensorc_rf_buffer_array, vpu_64x32_3r2w_vpurf (synchronous macros: a read enable, a registered output)
//     reads         read enables high this cycle (one per port);  reads_newaddr  of which at an address other than that port's last read
//     raddr_tog     read-address bits that changed (every cycle, enabled or not);  rdata_tog  output-register bits that change
//     writes, bits_written, changed   as above, per write port
// A negedge shadow of every rf_latch entry counts storage changes a second, independent way (shadow_changed), as a check.
// SPDX-License-Identifier: Apache-2.0 (the copied bodies are core-et's, Apache-2.0, (c) 2026 Ainekko)

package arr_pkg;
  // cls: 0 TenA, 1 TenB, 2 TenTMP, 3 TenC, 4 lane RF, 5 other (decided in C++ from the instance path)
  import "DPI-C" function int  arr_register(input string where, input int width, input int entries, input int kind);
  import "DPI-C" function void arr_cycle(input int id, input int writes, input int bits_written, input int changed, input int dl_open,
                                         input int dl_changed, input int reads, input int reads_newaddr, input int raddr_tog,
                                         input int rdata_tog, input int shadow_changed);
endpackage

`ifndef Q136C_NO_RF_LATCH
module rf_latch_1r_1w (/*AUTOARG*/
   // Outputs
   rd_data_a,
   // Inputs
   rd_addr_a,
   wr_data_a, wr_data_a_en_1p, wr_addr_a, wr_en_a,
   clk, test_en
   ) ;

   parameter WIDTH = 'd32, ENTRIES = 'd32;
   parameter LEVEL2_CLK_GATE = 0;
   localparam SIZE = $clog2(ENTRIES);

   output [WIDTH-1:0] rd_data_a; // Read Port A

   input [SIZE-1:0]   rd_addr_a; // Read Address for port A

   input [WIDTH-1:0]  wr_data_a; // Write Data - port A
   input              wr_data_a_en_1p; // Write Data Enable - port A (from Ph2 latch)
   input [SIZE-1:0]   wr_addr_a;  // Write Address - port A
   input              wr_en_a;    // Write Enable port A

   input              clk;
   input              test_en;

`ifdef ENABLE_VERILATOR_MODEL

   reg [WIDTH-1:0]           rf[ENTRIES-1:0];

   logic [WIDTH-1:0]         wr_data_a_del;
   always_ff@(negedge clk)
     if (wr_data_a_en_1p) wr_data_a_del <= wr_data_a;


   always_ff@(posedge clk) begin
      if (wr_en_a)
        rf[wr_addr_a] <= wr_data_a_del;
   end

`else
   //--------------------------------------------------------------------------
   // Write Data Clock Gaters & Latches
   //--------------------------------------------------------------------------
   reg [WIDTH-1:0]     wr_data_a_1p;    // Ph2 latched write data A

   wire               clk_wr_data_a_n; // Write data A Ph2 clock

   et_clk_gate_n cbuf_wr_data_a(.enclk_n(clk_wr_data_a_n), .en_1p(wr_data_a_en_1p), .clk(clk), .te(test_en));

   always @(clk_wr_data_a_n or wr_data_a)
     if (!clk_wr_data_a_n)
       wr_data_a_1p <= wr_data_a;

   //--------------------------------------------------------------------------
   // Register File
   //--------------------------------------------------------------------------
   reg [WIDTH-1:0]    rf[ENTRIES-1:0]; // Latch Array (RAM)


   // Write enables per ENTRIES
   wire [ENTRIES-1:0]   dec_wr_en;   // write from either port A or port B
   wire [ENTRIES-1:0]   clk_rf_wr;

   // second-level clock gate
   wire                 clk_wr;
   generate
     if (LEVEL2_CLK_GATE != 0) begin : clk_wr_gen
        et_clk_gate cbuf_wr(.enclk(clk_wr), .en(wr_en_a), .clk(clk), .te(1'b0));
     end else begin
        assign clk_wr = clk;
     end
   endgenerate

   // decode write enables
   assign dec_wr_en = ({{ENTRIES-1{1'b0}},1'b1} << wr_addr_a) & {ENTRIES{wr_en_a || test_en}};

   genvar             i;

   generate                     // the gated clocks for the write
      for (i = 0; i < ENTRIES; i = i + 1) begin : rf_c
         // disable test_en to avoid current spike
         et_clk_gate cbuf_rf_wr(.enclk(clk_rf_wr[i]), .en(dec_wr_en[i]), .clk(clk_wr), .te(1'b0));
      end
   endgenerate

   generate
      for (i = 0; i < ENTRIES; i=i+1) begin  : rf_
         always @(clk_rf_wr[i] or wr_data_a_1p)
           if (clk_rf_wr[i])
             rf[i] <= wr_data_a_1p;
      end
   endgenerate
`endif
   //--------------------------------------------------------------------------
   // Read Data Ports
   //--------------------------------------------------------------------------
   assign rd_data_a = rf[rd_addr_a];

   //--------------------------------------------------------------------------
   // Q136(c) accounting: reads only, no behavioural effect
   //--------------------------------------------------------------------------
`ifndef ENABLE_VERILATOR_MODEL
   int               acct_id;
   reg [SIZE-1:0]    acct_ra_prev = '0;
   reg [WIDTH-1:0]   acct_rd_prev = '0, acct_wd_prev = '0;
   reg [WIDTH-1:0]   acct_shadow [ENTRIES-1:0];
   int               acct_shadow_changed = 0;
   initial begin
      acct_id = arr_pkg::arr_register($sformatf("%m"), WIDTH, ENTRIES, 0);
      for (int k = 0; k < ENTRIES; k++) acct_shadow[k] = '0;
   end
   // every latch of the array is closed at the falling edge (an entry's gate is open only in the high phase)
   always @(negedge clk) begin
      for (int k = 0; k < ENTRIES; k++) begin
         acct_shadow_changed += $countones(rf[k] ^ acct_shadow[k]);
         acct_shadow[k] = rf[k];
      end
   end
   always @(posedge clk) begin
      automatic int w  = wr_en_a ? 1 : 0;
      automatic int ch = wr_en_a ? $countones(rf[wr_addr_a] ^ wr_data_a_1p) : 0;
      automatic int dl = cbuf_wr_data_a.en_2p ? 1 : 0;
      automatic int dc = $countones(wr_data_a_1p ^ acct_wd_prev);
      automatic int rt = $countones(rd_addr_a ^ acct_ra_prev);
      automatic int dt = $countones(rd_data_a ^ acct_rd_prev);
      if (w != 0 || dl != 0 || dc != 0 || rt != 0 || dt != 0 || acct_shadow_changed != 0)
        arr_pkg::arr_cycle(acct_id, w, w * WIDTH, ch, dl, dc, 0, 0, rt, dt, acct_shadow_changed);
      acct_shadow_changed = 0;
      acct_wd_prev = wr_data_a_1p;
      acct_ra_prev = rd_addr_a;
      acct_rd_prev = rd_data_a;
   end
`endif

endmodule
`endif

`timescale 1ns/1ps
module vpu_tensorc_rf_buffer_array #(
    parameter WIDTH     = 32,   // bits per word
    parameter DEPTH     = 16,  // number of words
    parameter ADDR_BITS = 4     // log2(DEPTH), 16 -> 4
)(
    input                  clk,        // clock
    input                  wr_enable,  // write enable (active-high)
    input                  rd_enable,  // read enable (active-high)
    input  [ADDR_BITS-1:0] wr_addr,    // write address
    input  [WIDTH-1:0]     wr_data,    // write data
    input  [ADDR_BITS-1:0] rd_addr,    // read address
    output reg [WIDTH-1:0] rd_data     // read data (synchronous)
);

    // Storage array
    reg [WIDTH-1:0] mem [0:DEPTH-1];

    // Temporary combinational value for match-or-x result
    reg [WIDTH-1:0] y;

    // Function: for each bit i, if a[i] === b[i], return that bit; else 'x'
    function [WIDTH-1:0] match_or_x_fn;
        input [WIDTH-1:0] a;
        input [WIDTH-1:0] b;
        integer i;
        begin
            for (i = 0; i < WIDTH; i = i + 1) begin
                match_or_x_fn[i] = (a[i] === b[i]) ? a[i] : 1'bx;
            end
        end
    endfunction

    // Synchronous read/write
    always @(posedge clk) begin
        // Simultaneous read & write to the same address
        if (wr_enable && rd_enable && (wr_addr == rd_addr)) begin
            // Compare against the OLD data (mem[rd_addr]) at this edge
            // Use case-inequality to treat X/Z explicitly if desired
            if (wr_data !== mem[rd_addr]) begin
                // Mismatch at some bits -> generate match-or-x vector
                y = match_or_x_fn(wr_data, mem[rd_addr]); // temporary combinational
                rd_data      <= y;        // return same vector on read
            end else begin
                // Perfect match; write is redundant but we can still commit
                rd_data      <= wr_data;  // read returns the (same) value
            end
            mem[wr_addr] <= wr_data;  // In case of decoupled read port the write should always be executed.
        end else begin
            // Normal independent write/read operations
            if (wr_enable) begin
                mem[wr_addr] <= wr_data;
            end
            if (rd_enable) begin
                rd_data <= mem[rd_addr];
            end
        end
    end

    // ---- Q136(c) accounting: reads only, no behavioural effect ----
    int                 acct_id;
    reg [ADDR_BITS-1:0] acct_ra_prev = '0, acct_last_read = '0;
    bit                 acct_read_before = 0;
    initial acct_id = arr_pkg::arr_register($sformatf("%m"), WIDTH, DEPTH, 1);
    always @(posedge clk) begin
        automatic int r  = rd_enable ? 1 : 0;
        automatic int rn = (rd_enable && (!acct_read_before || rd_addr != acct_last_read)) ? 1 : 0;
        automatic int w  = wr_enable ? 1 : 0;
        automatic int ch = wr_enable ? $countones(mem[wr_addr] ^ wr_data) : 0;
        automatic int rt = $countones(rd_addr ^ acct_ra_prev);
        automatic int dt = 0;
        if (rd_enable) begin
            automatic logic [WIDTH-1:0] nv = (wr_enable && (wr_addr == rd_addr)) ? match_or_x_fn(wr_data, mem[rd_addr]) : mem[rd_addr];
            dt = $countones(rd_data ^ nv);
            acct_last_read = rd_addr;
            acct_read_before = 1;
        end
        if (r != 0 || w != 0 || rt != 0)
            arr_pkg::arr_cycle(acct_id, w, w * WIDTH, ch, 0, 0, r, rn, rt, dt, 0);
        acct_ra_prev = rd_addr;
    end

endmodule

`timescale 1ns/1ps
module vpu_64x32_3r2w_vpurf #(
    parameter WIDTH     = 32,  // bits per word
    parameter DEPTH     = 64,  // number of words
    parameter ADDR_BITS = 6    // log2(DEPTH) = 6 for 64 words
)(
    input                       clk,

    // ------------------- Write Port 0 -------------------
    input                       wr_enable0,
    input      [ADDR_BITS-1:0]  wr_addr0,
    input      [WIDTH-1:0]      wr_data0,

    // ------------------- Write Port 1 -------------------
    input                       wr_enable1,
    input      [ADDR_BITS-1:0]  wr_addr1,
    input      [WIDTH-1:0]      wr_data1,

    // ------------------- Read Port A --------------------
    input                       rd_enable0,
    input      [ADDR_BITS-1:0]  rd_addr0,
    output reg [WIDTH-1:0]      rd_data0,

    // ------------------- Read Port B --------------------
    input                       rd_enable1,
    input      [ADDR_BITS-1:0]  rd_addr1,
    output reg [WIDTH-1:0]      rd_data1,

    // ------------------- Read Port C --------------------
    input                       rd_enable2,
    input      [ADDR_BITS-1:0]  rd_addr2,
    output reg [WIDTH-1:0]      rd_data2
);

    // ----------------------------------------------------------------
    // Storage array
    // ----------------------------------------------------------------
    reg [WIDTH-1:0] mem [0:DEPTH-1];

    // ----------------------------------------------------------------
    // Utility function: bitwise "match-or-X"
    // For each bit i:
    //   - if a[i] === b[i], return that bit
    //   - else return 1'bx
    // ----------------------------------------------------------------
    function [WIDTH-1:0] match_or_x_fn;
        input [WIDTH-1:0] a;
        input [WIDTH-1:0] b;
        integer i;
        begin
            match_or_x_fn = {WIDTH{1'bx}}; // default to X
            for (i = 0; i < WIDTH; i = i + 1) begin
                match_or_x_fn[i] = (a[i] === b[i]) ? a[i] : 1'bx;
            end
        end
    endfunction

    // ----------------------------------------------------------------
    // Precompute combined-write conditions/data
    // ----------------------------------------------------------------
    wire both_wr_same_addr = wr_enable0 && wr_enable1 && (wr_addr0 == wr_addr1);

    // If both write same address, this is the value actually written:
    // - matching bits take that bit value
    // - mismatching bits become X
    wire [WIDTH-1:0] merged_wr_data = match_or_x_fn(wr_data0, wr_data1);

    // ----------------------------------------------------------------
    // Synchronous read + write behavior
    // - Reads are registered (1-cycle latency)
    // - Read hazards produce match(write_data, old_mem) per spec
    // - Memory writes occur after read RHS have sampled old mem values
    // ----------------------------------------------------------------
    always @(posedge clk) begin
        // =========================
        // READ PORT A (registered)
        // =========================
        if (rd_enable0) begin
            // Old memory content sampled at this edge (RHS is old value)
            // Use local wire to emphasize read-before-write in this cycle
            // (nonblocking assignment ensures RHS is old mem)
            reg [WIDTH-1:0] old_a;
            old_a = mem[rd_addr0];

            if (both_wr_same_addr && (rd_addr0 == wr_addr0)) begin
                // Both writes to same address and read hits that address:
                // - memory will get merged_wr_data
                // - read returns match(merged_wr_data, old_a)
                rd_data0 <= match_or_x_fn(merged_wr_data, old_a);
            end else if (wr_enable0 && (rd_addr0 == wr_addr0)) begin
                // Single write port 0 hazard
                rd_data0 <= match_or_x_fn(wr_data0, old_a);
            end else if (wr_enable1 && (rd_addr0 == wr_addr1)) begin
                // Single write port 1 hazard
                rd_data0 <= match_or_x_fn(wr_data1, old_a);
            end else begin
                // No hazard: return old memory data
                rd_data0 <= old_a;
            end
        end

        // =========================
        // READ PORT B (registered)
        // =========================
        if (rd_enable1) begin
            reg [WIDTH-1:0] old_b;
            old_b = mem[rd_addr1];

            if (both_wr_same_addr && (rd_addr1 == wr_addr0)) begin
                rd_data1 <= match_or_x_fn(merged_wr_data, old_b);
            end else if (wr_enable0 && (rd_addr1 == wr_addr0)) begin
                rd_data1 <= match_or_x_fn(wr_data0, old_b);
            end else if (wr_enable1 && (rd_addr1 == wr_addr1)) begin
                rd_data1 <= match_or_x_fn(wr_data1, old_b);
            end else begin
                rd_data1 <= old_b;
            end
        end

        // =========================
        // READ PORT C (registered)
        // =========================
        if (rd_enable2) begin
            reg [WIDTH-1:0] old_c;
            old_c = mem[rd_addr2];

            if (both_wr_same_addr && (rd_addr2 == wr_addr0)) begin
                rd_data2 <= match_or_x_fn(merged_wr_data, old_c);
            end else if (wr_enable0 && (rd_addr2 == wr_addr0)) begin
                rd_data2 <= match_or_x_fn(wr_data0, old_c);
            end else if (wr_enable1 && (rd_addr2 == wr_addr1)) begin
                rd_data2 <= match_or_x_fn(wr_data1, old_c);
            end else begin
                rd_data2 <= old_c;
            end
        end

        // =========================
        // WRITES
        // =========================
        if (both_wr_same_addr) begin
            // One write to the common address with merged data
            mem[wr_addr0] <= merged_wr_data;
        end else begin
            // Independent writes to potentially different addresses
            if (wr_enable0) mem[wr_addr0] <= wr_data0;
            if (wr_enable1) mem[wr_addr1] <= wr_data1;
        end
    end

    // ---- Q136(c) accounting: reads only, no behavioural effect (hazard cases count as the plain read they replace) ----
    int                 acct_id;
    reg [ADDR_BITS-1:0] acct_ra_prev [3];
    reg [ADDR_BITS-1:0] acct_last_read [3];
    bit                 acct_read_before [3];
    initial begin
        acct_id = arr_pkg::arr_register($sformatf("%m"), WIDTH, DEPTH, 2);
        for (int p = 0; p < 3; p++) begin acct_ra_prev[p] = '0; acct_last_read[p] = '0; acct_read_before[p] = 0; end
    end
    always @(posedge clk) begin
        automatic logic [2:0] en = {rd_enable2, rd_enable1, rd_enable0};
        automatic logic [ADDR_BITS-1:0] ra [3] = '{rd_addr0, rd_addr1, rd_addr2};
        automatic logic [WIDTH-1:0] rd [3] = '{rd_data0, rd_data1, rd_data2};
        automatic int r = 0, rn = 0, rt = 0, dt = 0, w = 0, ch = 0;
        for (int p = 0; p < 3; p++) begin
            rt += $countones(ra[p] ^ acct_ra_prev[p]);
            if (en[p]) begin
                r++;
                if (!acct_read_before[p] || ra[p] != acct_last_read[p]) rn++;
                dt += $countones(rd[p] ^ mem[ra[p]]);
                acct_last_read[p] = ra[p];
                acct_read_before[p] = 1;
            end
            acct_ra_prev[p] = ra[p];
        end
        if (both_wr_same_addr) begin
            w = 1; ch = $countones(mem[wr_addr0] ^ merged_wr_data);
        end else begin
            if (wr_enable0) begin w++; ch += $countones(mem[wr_addr0] ^ wr_data0); end
            if (wr_enable1) begin w++; ch += $countones(mem[wr_addr1] ^ wr_data1); end
        end
        if (r != 0 || w != 0 || rt != 0)
            arr_pkg::arr_cycle(acct_id, w, w * WIDTH, ch, 0, 0, r, rn, rt, dt, 0);
    end

endmodule
