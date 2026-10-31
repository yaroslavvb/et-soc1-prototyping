// Q130(i): the same TensorFMA32 micro-op stream, driven into TWO copies of the structural
// register file -- one wired the way Q129's bench wires it, one wired the way the RTL wires it --
// so the difference can be counted.
//
// The stream is PRM 9.4 / `vpu_tensorfma.v`: for each B row k, for each A row i, two micro-ops
// (C columns 0-7, then 8-15), each c = a*b + c. One lane, 512 micro-ops per op. Same operand
// files as Q129 (`rtl-sim/fma_toggle/tiles.py <pattern> --seed 1 --iters-before 1000`).
//
// WHAT THE TWO WIRINGS ARE
//
// bench -- `tools/open-flow/scope/q129_scope_top.v` ll. 312-317:
//     rf_rd_en   = {uop_valid, uop_valid, uop_valid};
//     rf_rd_addr = {acc_raddr, acc_raddr, acc_raddr};
//     rf_wr_en / rf_wr_mask = f8_wmask, and `q129_lane_ctl` is given .ex_wmask(uop_valid)
//   so all three read ports sweep the accumulator index and the file is written on every
//   micro-op, in every pattern.
//
// rtl -- what `vpu_ctrl.v` and `vpu_tensorfma.v` actually present to `vpu_rf`:
//     id_regfile_ren[0] = ... & !id_tena_regfile_bypass_en   (l. 539)  -> 0 on a TensorFMA
//     id_regfile_ren[1] = ... & !id_tenb_regfile_bypass_en   (l. 541)  -> 0 on a TensorFMA
//     id_regfile_ren[2] = id_core_valid_int & sigs.ren3      (l. 543)  -> 1
//     id_regfile_raddr1 = id_ra1 = inst[REN1_RA_SEL] = fma_exec_mat_a_reg  (vpu_tensorfma l. 700)
//     id_regfile_raddr2 = id_ra2 = inst[REN2_RA_SEL] = fma_exec_mat_b_reg  (l. 701)
//     id_ra3            = inst[REN3_RA_SEL] = fma_exec_accum_reg           (l. 704)
//     fma_exec_accum_reg = {a_row, b_col}; mat_a_reg = {4'b0, a_rd_ptr};
//     mat_b_reg = {2'b01, b_rd_ptr, b_col}                                 (ll. 677-679)
//   and the write mask is gated off when the operand word is zero:
//     f3_zero_data_a/b   = (word == 0)                       (vpu_ctrl l. 1230-1233)
//     ex_tensor_zero_mask = A-zero | B-zero                  (l. 817)
//     ex_fma_gate_mask    = zero_mask & (cmd == MADD)        (l. 837)
//     ex_ml_mask_to_f2    = ~ex_fma_gate_mask & ex_ml_mask   (l. 844)
//     f2_regfile_wmask    = f2_ml_mask                       (l. 1002)  -> F3..F8 -> wr_mask
//
//   +tiles=<hex>   768 words: A row-major, B row-major, the initial C
//   +ops=<n>       measured ops (default 1)      +warm=<n> unmeasured ops first (default 1)
//   +lane=<l>      which of the 8 lanes (default 0)
//   +allmadd=1     every pass is an accumulate, so no micro-op escapes the zero gate
//                  (default: the k = 0 pass is the multiply pass and is not gated)
//
// SPDX-License-Identifier: Apache-2.0

module tb;
  localparam int LAT = 6;          // EX -> F8, as q129_lane_ctl pipelines it

  logic clock = 0;
  always #1 clock = ~clock;

  logic [31:0] mem [0:767];
  logic [31:0] A [16][16];
  logic [31:0] B [16][16];
  logic [31:0] Cb [16][16];        // the bench wiring's accumulators
  logic [31:0] Cr [16][16];        // the rtl wiring's accumulators
  int unsigned lane = 0, allmadd = 0;

  logic measuring = 0;

  // ---- what the two wirings present ---------------------------------------
  logic [5:0] b_addr [3];
  logic [5:0] r_addr [3];
  logic       b_en   [3];
  logic       r_en   [3];
  logic        b_wen = 0, r_wen = 0;
  logic [5:0]  b_waddr = 0, r_waddr = 0;
  logic [31:0] b_wdata = 0, r_wdata = 0;
  logic [31:0] b_rdata [3];
  logic [31:0] r_rdata [3];

  initial begin
    for (int p = 0; p < 3; p++) begin
      b_addr[p] = '0; r_addr[p] = '0; b_en[p] = 1'b0; r_en[p] = 1'b0;
    end
  end

  rf3r2w_struct bench (.clk(clock), .measuring(measuring), .rd_addr(b_addr), .rd_en(b_en),
                       .wr_en_a(b_wen), .wr_addr_a(b_waddr), .wr_data_a(b_wdata),
                       .rd_data(b_rdata));
  rf3r2w_struct rtl   (.clk(clock), .measuring(measuring), .rd_addr(r_addr), .rd_en(r_en),
                       .wr_en_a(r_wen), .wr_addr_a(r_waddr), .wr_data_a(r_wdata),
                       .rd_data(r_rdata));

  function automatic logic [31:0] fp32_fma(input logic [31:0] a, b, c);
    shortreal ra, rb, rc;
    ra = $bitstoshortreal(a); rb = $bitstoshortreal(b); rc = $bitstoshortreal(c);
    fp32_fma = $shortrealtobits(ra * rb + rc);
  endfunction

  // ---- the writeback queues ------------------------------------------------
  logic [LAT:0][31:0] qb_res = '0, qr_res = '0;
  logic [LAT:0]       qb_val = '0, qr_val = '0;
  logic [LAT:0][4:0]  q_idx  = '0;

  longint unsigned uops = 0, gated = 0, first_pass_uops = 0;

  task automatic issue(input bit valid, input int k, input int i, input int h);
    logic [4:0] accum_reg, mat_a_reg, mat_b_reg;
    logic       a_zero, b_zero, is_madd, gate;
    @(negedge clock);
    accum_reg = 5'(2 * i + h);                                 // {a_row, b_col}
    mat_a_reg = {4'b0, 1'(i & 1)};                             // {4'b0, a_rd_ptr}
    mat_b_reg = {2'b01, 2'(k & 2'b11), 1'(h)};                 // {2'b01, b_rd_ptr, b_col}

    a_zero  = (A[i][k] == 32'b0);
    b_zero  = (B[k][8*h + lane] == 32'b0);
    is_madd = allmadd ? 1'b1 : (k != 0);                       // the k = 0 pass is the multiply
    gate    = valid & is_madd & (a_zero | b_zero);

    if (valid && measuring) begin
      uops++;
      if (gate) gated++;
      if (!is_madd) first_pass_uops++;
    end

    // --- the bench's wiring: three swept read ports, a write on every micro-op
    b_addr[0] = {1'b0, accum_reg};
    b_addr[1] = {1'b0, accum_reg};
    b_addr[2] = {1'b0, accum_reg};
    b_en[0] = valid; b_en[1] = valid; b_en[2] = valid;

    // --- the RTL's wiring: port 2 only, ports 0/1 on their own static indices
    r_addr[0] = {1'b0, mat_a_reg};
    r_addr[1] = {1'b0, mat_b_reg};
    r_addr[2] = {1'b0, accum_reg};
    r_en[0] = 1'b0; r_en[1] = 1'b0; r_en[2] = valid;

    qb_val = {qb_val[LAT-1:0], valid};
    qr_val = {qr_val[LAT-1:0], valid & ~gate};
    q_idx  = {q_idx [LAT-1:0], accum_reg};
    qb_res = {qb_res[LAT-1:0], valid ? fp32_fma(A[i][k], B[k][8*h+lane], Cb[i][8*h+lane]) : 32'b0};
    qr_res = {qr_res[LAT-1:0], valid ? fp32_fma(A[i][k], B[k][8*h+lane], Cr[i][8*h+lane]) : 32'b0};

    b_wen   = qb_val[LAT];
    b_waddr = {1'b0, q_idx[LAT]};
    b_wdata = qb_res[LAT];
    r_wen   = qr_val[LAT];
    r_waddr = {1'b0, q_idx[LAT]};
    r_wdata = qr_res[LAT];
  endtask

  always @(posedge clock) begin
    if (qb_val[LAT]) Cb[q_idx[LAT] >> 1][8 * (q_idx[LAT] & 1) + lane] <= qb_res[LAT];
    if (qr_val[LAT]) Cr[q_idx[LAT] >> 1][8 * (q_idx[LAT] & 1) + lane] <= qr_res[LAT];
  end

  task automatic one_op();
    for (int k = 0; k < 16; k++)
      for (int i = 0; i < 16; i++)
        for (int h = 0; h < 2; h++) issue(1, k, i, h);
  endtask

  function automatic longint unsigned sum3(input longint unsigned v [3]);
    sum3 = v[0] + v[1] + v[2];
  endfunction

  string tiles;
  int ops = 1, warm = 1;
  initial begin
    if (!$value$plusargs("tiles=%s", tiles)) begin $display("no +tiles"); $finish; end
    void'($value$plusargs("ops=%d", ops));
    void'($value$plusargs("warm=%d", warm));
    void'($value$plusargs("lane=%d", lane));
    void'($value$plusargs("allmadd=%d", allmadd));
    $readmemh(tiles, mem);
    for (int i = 0; i < 16; i++) for (int j = 0; j < 16; j++) begin
      A[i][j]  = mem[16*i + j];
      B[i][j]  = mem[256 + 16*i + j];
      Cb[i][j] = mem[512 + 16*i + j];
      Cr[i][j] = mem[512 + 16*i + j];
    end
    repeat (4) issue(0, 0, 0, 0);
    for (int w = 0; w < warm; w++) one_op();
    repeat (16) issue(0, 0, 0, 0);
    @(negedge clock);
    measuring = 1;
    for (int o = 0; o < ops; o++) one_op();
    repeat (16) issue(0, 0, 0, 0);
    @(negedge clock);
    measuring = 0;

    $display("CNT {\"tiles\":\"%s\",\"allmadd\":%0d,\"muladds\":%0d,\"uops\":%0d,\"gated\":%0d,\"first_pass_uops\":%0d,\"cycles\":%0d,%s%s}",
             tiles, allmadd, 512*ops, uops, gated, first_pass_uops, bench.cycles,
             $sformatf("\"bench\":{\"sel_pin_tr\":%0d,\"sel_pin_tr_p\":[%0d,%0d,%0d],\"mux_out_tr\":%0d,\"mux_out_tr_p\":[%0d,%0d,%0d],\"addr_tr\":%0d,\"rd_data_tr\":%0d,\"dec_tr\":%0d,\"wr_clk_edges\":%0d,\"entry_clk_edges\":%0d,\"wrdata_clk_edges\":%0d,\"wrdata_latch_tr\":%0d,\"wr_addr_tr\":%0d},",
                      sum3(bench.sel_pin_tr), bench.sel_pin_tr[0], bench.sel_pin_tr[1], bench.sel_pin_tr[2],
                      sum3(bench.mux_out_tr), bench.mux_out_tr[0], bench.mux_out_tr[1], bench.mux_out_tr[2],
                      sum3(bench.addr_tr), sum3(bench.rd_data_tr),
                      bench.dec_tr, bench.wr_clk_edges, bench.entry_clk_edges, bench.wrdata_clk_edges,
                      bench.wrdata_latch_tr, bench.wr_addr_tr),
             $sformatf("\"rtl\":{\"sel_pin_tr\":%0d,\"sel_pin_tr_p\":[%0d,%0d,%0d],\"mux_out_tr\":%0d,\"mux_out_tr_p\":[%0d,%0d,%0d],\"addr_tr\":%0d,\"rd_data_tr\":%0d,\"dec_tr\":%0d,\"wr_clk_edges\":%0d,\"entry_clk_edges\":%0d,\"wrdata_clk_edges\":%0d,\"wrdata_latch_tr\":%0d,\"wr_addr_tr\":%0d}",
                      sum3(rtl.sel_pin_tr), rtl.sel_pin_tr[0], rtl.sel_pin_tr[1], rtl.sel_pin_tr[2],
                      sum3(rtl.mux_out_tr), rtl.mux_out_tr[0], rtl.mux_out_tr[1], rtl.mux_out_tr[2],
                      sum3(rtl.addr_tr), sum3(rtl.rd_data_tr),
                      rtl.dec_tr, rtl.wr_clk_edges, rtl.entry_clk_edges, rtl.wrdata_clk_edges,
                      rtl.wrdata_latch_tr, rtl.wr_addr_tr));
    $finish;
  end
endmodule
