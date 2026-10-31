// Q130(i): a STRUCTURAL stand-in for the 64 x 32 3r2w VPU register file, built the way a
// synthesis tool builds `rf_latch_3r_2w`'s read path, so the nodes that switch can be counted.
//
// core-et `rtl/libs/rf_latches/rf_latch_3r_2w.v` ll. 167-169 read with three purely
// combinational expressions and NO read enable:
//
//     assign rd_data_a = vpu_rf[rd_addr_a];
//     assign rd_data_b = vpu_rf[rd_addr_b];
//     assign rd_data_c = vpu_rf[rd_addr_c];
//
// Each becomes a 64:1 select tree per bit: six levels of 2:1 muxes, 32 + 16 + 8 + 4 + 2 + 1 = 63
// muxes per bit per port, 2,016 per port, 6,048 in all. This module writes that tree out level by
// level so a simulation can count (a) how many mux OUTPUT bits change and (b) how many mux SELECT
// pins are driven by an address bit that changed. The write side is the module's own: a one-hot
// decode gated by `wr_en`, a second-level clock gate on `wr_en_a | wr_en_b`, 64 per-entry clock
// gates, and the Ph2 write-data latch behind its own gate.
//
// `rd_en_*` is carried only so the counters can be read two ways: the latch array ignores it (it
// has no such port), while the compiled macro `vpu_64x32_3r2w_vpurf` that the chip actually
// contains takes it as `rd_enable0/1/2` (`vpu_rf.v` ll. 60, 63, 66).
//
// CORRECTION, 31 Oct 2026 (same day, after review): `offs()` read
// `NODES - (ENTRIES >> L)`, which is -1 at L = 0 instead of 0, so the tree was built one index
// low, level 0's first node write was out of range and dropped, and the root node `node[NODES-1]`
// that `rd_data` reads was never assigned. `sel_pin_tr`, `addr_tr` and the whole write side never
// read the tree and were unaffected; `mux_out_tr` and `rd_data_tr` were. It is now
// `ENTRIES - (ENTRIES >> L)`, and `rd_chk_fail` asserts `rd_data[p] == rf[rd_addr[p]]` on every
// port every cycle so the same mistake cannot pass silently again.
//
// SPDX-License-Identifier: Apache-2.0

module rf3r2w_struct #(
  parameter int WIDTH   = 32,
  parameter int ENTRIES = 64,
  parameter int SIZE    = 6
) (
  input  logic              clk,
  input  logic              measuring,
  // read ports
  input  logic [SIZE-1:0]   rd_addr [3],
  input  logic              rd_en   [3],
  // write port A (port B is tied off in q129_scope_top, as vpu_lane.v ties it for an fp32 TXFMA)
  input  logic              wr_en_a,
  input  logic [SIZE-1:0]   wr_addr_a,
  input  logic [WIDTH-1:0]  wr_data_a,
  output logic [WIDTH-1:0]  rd_data [3]
);

  // level L holds (32 >> L) nodes; node (L, n) is the mux that selects on rd_addr[L]
  localparam int NODES = 63;
  function automatic int offs(input int L);
    offs = ENTRIES - (ENTRIES >> L);   // L=0 -> 0, 1 -> 32, 2 -> 48, 3 -> 56, 4 -> 60, 5 -> 62
  endfunction
  function automatic int nlev(input int L);
    nlev = (ENTRIES / 2) >> L;         // 32, 16, 8, 4, 2, 1
  endfunction

  logic [WIDTH-1:0] rf [ENTRIES];
  logic [WIDTH-1:0] node [3][NODES];

  // ---- the three read trees -------------------------------------------------
  always_comb begin
    for (int p = 0; p < 3; p++) begin
      for (int n = 0; n < 32; n++)
        node[p][offs(0)+n] = rd_addr[p][0] ? rf[2*n+1] : rf[2*n];
      for (int L = 1; L < SIZE; L++)
        for (int n = 0; n < nlev(L); n++)
          node[p][offs(L)+n] = rd_addr[p][L] ? node[p][offs(L-1)+2*n+1]
                                             : node[p][offs(L-1)+2*n];
      rd_data[p] = node[p][NODES-1];
    end
  end

  // ---- the write side, as rf_latch_3r_2w builds it --------------------------
  logic [ENTRIES-1:0] dec_wr_en_a;
  logic               clk_wr_en;          // the second-level gate's enable
  logic               wrdata_gate_en;     // clk_wr_data_a_n's enable
  logic [WIDTH-1:0]   wr_data_a_1p;

  always_comb begin
    dec_wr_en_a    = wr_en_a ? (ENTRIES'(1) << wr_addr_a) : '0;
    clk_wr_en      = wr_en_a;             // wr_en_b is tied off
    wrdata_gate_en = wr_en_a;
  end

  always_ff @(posedge clk) begin
    if (wr_en_a) begin
      wr_data_a_1p <= wr_data_a;
      rf[wr_addr_a] <= wr_data_a;
    end
  end

  // ---- counters -------------------------------------------------------------
  // per port: mux output bit transitions, select-pin transitions, raw address bit flips
  longint unsigned mux_out_tr [3];
  longint unsigned sel_pin_tr [3];
  longint unsigned addr_tr    [3];
  longint unsigned rd_data_tr [3];
  // write side
  longint unsigned dec_tr, entry_clk_edges, wr_clk_edges, wrdata_clk_edges;
  longint unsigned wrdata_latch_tr, wr_addr_tr;
  longint unsigned cycles;
  // the read tree must deliver what the array holds. Checked every cycle on every port, because
  // a wrong offs() silently drops a level and leaves the root node unwritten: this counter was
  // zero in the first version of this file only because the counter did not exist. It must stay 0.
  longint unsigned rd_chk_fail;

  logic [WIDTH-1:0]   p_node [3][NODES];
  logic [SIZE-1:0]    p_addr [3];
  logic [WIDTH-1:0]   p_rd   [3];
  logic [ENTRIES-1:0] p_dec;
  logic [WIDTH-1:0]   p_wd1p;
  logic [SIZE-1:0]    p_waddr;

  initial begin
    for (int p = 0; p < 3; p++) begin
      mux_out_tr[p] = 0; sel_pin_tr[p] = 0; addr_tr[p] = 0; rd_data_tr[p] = 0;
    end
    dec_tr = 0; entry_clk_edges = 0; wr_clk_edges = 0; wrdata_clk_edges = 0;
    wrdata_latch_tr = 0; wr_addr_tr = 0; cycles = 0; rd_chk_fail = 0;
    for (int e = 0; e < ENTRIES; e++) rf[e] = '0;
    wr_data_a_1p = '0;
  end

  always @(posedge clk) begin
    // the read path is purely combinational and has no enable, so this holds every cycle
    for (int p = 0; p < 3; p++)
      if (rd_data[p] !== rf[rd_addr[p]]) begin
        rd_chk_fail++;
        if (rd_chk_fail < 4)
          $display("RD_CHK_FAIL port %0d: rd_data=%h rf[%0d]=%h", p, rd_data[p],
                   rd_addr[p], rf[rd_addr[p]]);
      end
    if (measuring) begin
      cycles++;
      for (int p = 0; p < 3; p++) begin
        for (int L = 0; L < SIZE; L++)
          if (rd_addr[p][L] !== p_addr[p][L]) sel_pin_tr[p] += longint'(nlev(L)) * WIDTH;
        addr_tr[p] += longint'($countones(rd_addr[p] ^ p_addr[p]));
        for (int n = 0; n < NODES; n++)
          mux_out_tr[p] += longint'($countones(node[p][n] ^ p_node[p][n]));
        rd_data_tr[p] += longint'($countones(rd_data[p] ^ p_rd[p]));
      end
      dec_tr     += longint'($countones(dec_wr_en_a ^ p_dec));
      wr_addr_tr += longint'($countones(wr_addr_a ^ p_waddr));
      // a gated clock that is enabled sees a rise and a fall in the cycle
      if (clk_wr_en)      wr_clk_edges     += 2;
      if (clk_wr_en)      entry_clk_edges  += 2;       // exactly one of the 64 per-entry gates
      if (wrdata_gate_en) wrdata_clk_edges += 2;
      if (wr_en_a) wrdata_latch_tr += longint'($countones(wr_data_a ^ p_wd1p));
    end
    for (int p = 0; p < 3; p++) begin
      p_addr[p] <= rd_addr[p];
      p_rd[p]   <= rd_data[p];
      for (int n = 0; n < NODES; n++) p_node[p][n] <= node[p][n];
    end
    p_dec   <= dec_wr_en_a;
    p_waddr <= wr_addr_a;
    p_wd1p  <= wr_en_a ? wr_data_a : p_wd1p;
  end
endmodule
