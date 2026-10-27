// Q129: the fma_toggle stimulus driven into a GATE-LEVEL q129_scope_top.
//
// Same micro-op stream as tools/open-flow/txfma/tb_gate.sv and rtl-sim/fma_toggle/tb.sv
// (PRM 9.4, vpu_tensorfma.v): for each B row k, for each A row i, two micro-ops (C columns
// 0-7, then 8-15), each c = a*b + c. One lane. What differs from tb_gate.sv:
//
//   - the unit under test is the LANE'S TRANSPORT, not its arithmetic: the register files, the
//     operand bus, the result path, the per-lane control. The multiply-add itself is priced in
//     docs/reports/data/2026-10-26-open-netlist/, so this bench supplies the answer the
//     arithmetic would have produced (an fp32 multiply-add in the simulator's own arithmetic)
//     at the design's txfma_res_data port, delayed by the pipeline;
//   - the operands reach the lane the way the RTL routes them: A is written into TENA and read
//     back out of it, B into TENB, and the accumulator lives in the VPU register file at index
//     2*i + h, read on every micro-op and written back at F8.
//
//   +tiles=<hex>  768 words: A row-major, B row-major, the initial C
//   +ops=<n>      measured ops   +warm=<n> unmeasured ops before them
//   +lane=<l>     which of the 8 lanes this is (sets which B / C column it owns), default 0
//   +saif=<file>  where to write the activity file
//
// Two controls, each "everything else the same", so a term can be had by difference the way
// E60 and E61 had theirs on the card:
//   +accfix=1     the accumulator's register INDEX is held at 0 instead of sweeping 2*i+h.
//                 (measured run minus this one) / (index bits flipped) is the bottom-up
//                 counterpart of E61's 369-452 fJ per changed read-index bit.
//   +resfix=1     the word the arithmetic hands back at F8 is held constant. The difference is
//                 the result path's own data-dependent energy, against E60's 31.2 fJ per result
//                 bit.
`include "soc.vh"
module tb;
  localparam int LAT = 6;        // EX -> F8 in q129_lane_ctl's own pipeline

  logic clock = 0, reset = 1;
  always #1 clock = ~clock;

  logic [31:0] mem [0:767];
  logic [31:0] A [16][16];
  logic [31:0] B [16][16];
  logic [31:0] C [16][16];
  int unsigned lane = 0;
  int unsigned accfix = 0, resfix = 0;   // the two controls

  // --- the design's inputs ---------------------------------------------------
  logic        uop_valid = 0;
  logic [$clog2(`VPU_TENA_SIZE)-1:0] tena_raddr = 0, tena_waddr = 0;
  logic [$clog2(`VPU_TENB_SIZE)-1:0] tenb_raddr = 0, tenb_waddr = 0;
  logic [`FREG_ADDR_RANGE] acc_raddr = 0;
  logic        acc_thrid = 0;
  logic        tena_wen = 0, tenb_wen = 0, tentmp_wen = 0, tenc_wen = 0, tenc_ren = 0;
  logic [31:0] tena_wdata = 0, tenb_wdata = 0, tentmp_wdata = 0, tenc_wdata = 0;
  logic [`VPU_TENTMP_ADDR] tentmp_waddr = 0, tentmp_raddr = 0;
  logic [`VPU_TENC_ADDR]   tenc_waddr = 0, tenc_raddr = 0;
  logic [31:0] txfma_res_data = 0;
  logic [`VPU_FLAGS_SZ-1:0] txfma_res_exc = 0;
  logic [31:0] op_in1, op_in2, op_in3, wb_data, tentmp_rdata, tenc_rdata;

  q129_scope_top dut (
    .clock(clock), .reset(reset), .uop_valid(uop_valid),
    .tena_raddr(tena_raddr), .tenb_raddr(tenb_raddr),
    .acc_raddr(acc_raddr), .acc_thrid(acc_thrid),
    .tena_wen(tena_wen), .tena_waddr(tena_waddr), .tena_wdata(tena_wdata),
    .tenb_wen(tenb_wen), .tenb_waddr(tenb_waddr), .tenb_wdata(tenb_wdata),
    .tentmp_wen(tentmp_wen), .tentmp_waddr(tentmp_waddr), .tentmp_raddr(tentmp_raddr),
    .tentmp_wdata(tentmp_wdata),
    .tenc_wen(tenc_wen), .tenc_ren(tenc_ren), .tenc_waddr(tenc_waddr),
    .tenc_raddr(tenc_raddr), .tenc_wdata(tenc_wdata),
    .txfma_res_data(txfma_res_data), .txfma_res_exc(txfma_res_exc),
    .op_in1(op_in1), .op_in2(op_in2), .op_in3(op_in3), .wb_data(wb_data),
    .tentmp_rdata(tentmp_rdata), .tenc_rdata(tenc_rdata)
  );

  // --- the result queue: what the arithmetic answers, LAT cycles later -------
  logic [LAT:0][31:0] q_res = '0;
  logic [LAT:0]       q_val = '0;
  logic [LAT:0][4:0]  q_idx = '0;

  function automatic logic [31:0] fp32_fma(input logic [31:0] a, b, c);
    shortreal ra, rb, rc;
    ra = $bitstoshortreal(a); rb = $bitstoshortreal(b); rc = $bitstoshortreal(c);
    fp32_fma = $shortrealtobits(ra * rb + rc);
  endfunction

  // --- accounting, the same counters tb_gate.sv keeps ------------------------
  longint unsigned cycles = 0, uop_cycles = 0, bus_toggles = 0, idx_toggles = 0;
  longint unsigned res_toggles = 0, acc_rd_toggles = 0;
  logic [31:0] pa = 0, pb = 0, pc = 0, pres = 0, pacc = 0;
  logic [4:0]  pidx = 0;
  bit measuring = 0;
  int unsigned checks = 0;

  task automatic issue(input bit valid, input int k, input int i, input int h);
    @(negedge clock);
    uop_valid = valid;
    if (valid) begin
      // A reaches the lane through TENA, double-buffered (VPU_TENA_SIZE = 2)
      tena_wen   = (h == 0);
      tena_waddr = ($clog2(`VPU_TENA_SIZE))'(i & 1);
      tena_wdata = A[i][k];
      tena_raddr = ($clog2(`VPU_TENA_SIZE))'(i & 1);
      // B reaches the lane through TENB; raddr[0] picks which of the two TIMA files
      tenb_wen   = 1'b1;
      tenb_waddr = ($clog2(`VPU_TENB_SIZE))'({k[1:0], h[0:0]});
      tenb_wdata = B[k][8 * h + lane];
      tenb_raddr = ($clog2(`VPU_TENB_SIZE))'({k[1:0], h[0:0]});
      // the accumulator: one of this lane's 32 registers
      acc_raddr  = accfix ? (`FREG_ADDR_SIZE)'(0) : (`FREG_ADDR_SIZE)'(2 * i + h);
    end else begin
      tena_wen = 0; tenb_wen = 0;
    end
    q_val = {q_val[LAT-1:0], valid};
    q_res = {q_res[LAT-1:0], valid ? fp32_fma(A[i][k], B[k][8*h+lane], C[i][8*h+lane]) : 32'b0};
    q_idx = {q_idx[LAT-1:0], 5'(2 * i + h)};
    txfma_res_data = resfix ? 32'h3f800000 : q_res[LAT];
  endtask

  always @(posedge clock) begin
    if (q_val[LAT]) C[q_idx[LAT] >> 1][8 * (q_idx[LAT] & 1) + lane] <= q_res[LAT];
    if (measuring) begin
      cycles++;
      uop_cycles += longint'(uop_valid);
      // the operand words the lane is handed, counted exactly as tb_gate.sv counts them
      bus_toggles    += longint'($countones(op_in1 ^ pa)) + longint'($countones(op_in2 ^ pb))
                      + longint'($countones(op_in3 ^ pc));
      idx_toggles    += longint'($countones(acc_raddr ^ pidx));
      res_toggles    += longint'($countones(wb_data ^ pres));
      acc_rd_toggles += longint'($countones(op_in3 ^ pacc));
    end
    pa <= op_in1; pb <= op_in2; pc <= op_in3; pres <= wb_data; pacc <= op_in3; pidx <= acc_raddr;
  end

  task automatic one_op();
    for (int k = 0; k < 16; k++)
      for (int i = 0; i < 16; i++)
        for (int h = 0; h < 2; h++) issue(1, k, i, h);
  endtask

  string tiles, saif;
  int ops = 1, warm = 1;
  initial begin
    if (!$value$plusargs("tiles=%s", tiles)) begin $display("no +tiles"); $finish; end
    if (!$value$plusargs("saif=%s", saif))   saif = "activity.saif";
    void'($value$plusargs("ops=%d", ops));
    void'($value$plusargs("warm=%d", warm));
    void'($value$plusargs("lane=%d", lane));
    void'($value$plusargs("accfix=%d", accfix));
    void'($value$plusargs("resfix=%d", resfix));
    $readmemh(tiles, mem);
    for (int i = 0; i < 16; i++) for (int j = 0; j < 16; j++) begin
      A[i][j] = mem[16*i + j];
      B[i][j] = mem[256 + 16*i + j];
      C[i][j] = mem[512 + 16*i + j];
    end
    $dumpfile(saif);
    $dumpvars(0, tb);
    $dumpoff;
    repeat (8) @(posedge clock);
    @(negedge clock) reset = 0;
    repeat (4) issue(0, 0, 0, 0);
    for (int w = 0; w < warm; w++) one_op();
    repeat (16) issue(0, 0, 0, 0);
    @(negedge clock);
    measuring = 1;
    $dumpon;
    for (int o = 0; o < ops; o++) one_op();
    repeat (16) issue(0, 0, 0, 0);
    @(negedge clock);
    $dumpoff;
    measuring = 0;
    $display("ACCT {\"accfix\":%0d,\"resfix\":%0d,\"ops\":%0d,\"cycles\":%0d,\"uop_cycles\":%0d,\"bus_toggles\":%0d,\"idx_toggles\":%0d,\"res_toggles\":%0d,\"acc_rd_toggles\":%0d,\"muladds\":%0d}",
             accfix, resfix, ops, cycles, uop_cycles, bus_toggles, idx_toggles, res_toggles, acc_rd_toggles, 512 * ops);
    $finish;
  end
endmodule
