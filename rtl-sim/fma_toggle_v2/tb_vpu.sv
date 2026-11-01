// The real vector unit executing real TensorFMA instructions. Q132(b), Sat 31 Oct / Sun 1 Nov 2026.
//
// This instantiates core-et's vpu_top whole: vpu_ctrl, vpu_ml, vpu_tensorfma, all eight vpu_lanes with their register
// files, bypass, txfma_top and tima_top. The micro-op stream, the zero gate, use_prev_sigs, the clock gates and the
// write-back are therefore the RTL's own. WHAT REMAINS TESTBENCH CODE, all of it below and nothing else:
//   1. The scratchpad: an array that answers the VPU's read port 2 cycles later, always (the bid is never refused).
//   2. The core: one tensorfma_start pulse with a control word, the bit layout of workloads/sparsity/kernel/sparsity.c
//      fma_word, then idle. The gap between the end of one op and the next start stands for the core's loop.
//   3. Back-door writes of the accumulators into the RF / TenC memories, to start an op at a chosen point of a launch,
//      and back-door reads of them after each op, to check them.
// Clock: one free-running clock; the chip's PLL, clock tree and dcache are not modelled.
//
//   +tiles=<hex>   768 words: A[row][col], B[row][col], initial C[row][col], row-major
//   +fmt=fp32|fp16|int8
//   +ops=<n>       measured ops, after +warm=<n> unmeasured ops
//   +first=<0|1>   1: the first op has first_pass set (a launch's first op; its first A column is a MUL pass)
//   +loadc=<0|1>   1: write C from the hex file into the RF/TenC before the first op
//   +period=<n>    cycles from one start to the next, if the FSM allows it (card: 546 fp32/fp16, 318 int8; default)
//   +printc=<0|1>  print C after every op, "C <op> <row> <col> <word>"
//   +dump=<file>   open a VCD window for +dump_ops measured ops and stop at its end
`include "soc.vh"
module tb;
  import "DPI-C" function void acct_reset();
  import "DPI-C" function longint acct_get(input int which);

  logic clock = 0, reset = 1;
  always #1 clock = ~clock;

  // ---- what the core drives -------------------------------------------------------------------------------------
  core_vpu_ctrl f0_core_ctrl;
  minion_vpu_id_req id_core_req;
  minion_vpu_ex_req ex_core_req;
  vpu_ctrl_sigs_t id_sigs;
  dcache_vpu_resp wb_resp;
  dcache_vpu_reduce_ctrl reduce_ctrl;
  dcache_vpu_scp_resp scp_resp;
  vpu_dcache_ctrl dcache_ctrl;
  logic [`DCACHE_DATA_RANGE] scp_data = '0, tenb_data = '0;
  vpu_minion_id_ctrl id_core_ctrl;
  vpu_minion_ex_ctrl ex_core_ctrl;
  vpu_minion_tag_ctrl f2_core_ctrl;
  vpu_minion_mem_ctrl f3_core_ctrl;
  vpu_minion_wb_ctrl wb_core_ctrl;

  vpu_top dut (
    .clock(clock), .reset(reset),
    .id_core_req(id_core_req), .id_vpu_decoder_sigs(id_sigs), .ex_core_req(ex_core_req),
    .f2_core_kill(1'b0), .f3_core_kill(1'b0), .f4_core_kill(1'b0), .f0_core_ctrl(f0_core_ctrl),
    .chicken_bit_vpulane(1'b0), .chicken_bit_vputima(1'b0), .chicken_bit_vputrans(1'b0),
    .mem_ctrl_override('0),
    .wb_dcache_resp_valid(1'b0), .wb_dcache_resp(wb_resp),
    .dcache_ctrl(dcache_ctrl), .dcache_scp_resp(scp_resp), .dcache_scp_data(scp_data), .dcache_tenb_data(tenb_data),
    .dcache_reduce_ctrl(reduce_ctrl),
    .id_core_ctrl(id_core_ctrl), .ex_core_ctrl(ex_core_ctrl), .f2_core_ctrl(f2_core_ctrl), .f3_core_ctrl(f3_core_ctrl),
    .wb_core_ctrl(wb_core_ctrl), .io_events(), .vpu_dbg_match(), .vpu_dbg_filter(), .vpu_dbg_data());

  // ---- the scratchpad: lines 0-15 hold A, lines 16-31 hold B --------------------------------------------------------
  logic [31:0] mem [0:767];
  logic [31:0] scp [0:32*16-1];       // 32 lines of 16 words
  logic        rd1 = 0;
  logic [`DCACHE_DATA_RANGE] data1 = '0, data2 = '0;
  // the flat byte address the FSM computes (vpu_tensorfma.v:329), before its way/set hash
  wire [31:0] rd_flat = 32'(dut.ctrl.ml.tensorfma.dc_read_addr_flat);
  function automatic logic [`DCACHE_DATA_RANGE] chunk(input int unsigned byteaddr);
    int unsigned base = (byteaddr / 32) * 8;         // a 256-bit chunk holds 8 words
    for (int w = 0; w < 8; w++) chunk[32 * w +: 32] = scp[(base + w) % (32 * 16)];
  endfunction
  always @(posedge clock) begin
    if (dcache_ctrl.scp_req.read_en) begin
      data1 <= chunk(rd_flat);
      n_scp_reads++;
    end
    scp_data <= data1;
  end

  // ---- back doors ---------------------------------------------------------------------------------------------------
  logic [31:0] cshadow [8][64];
  logic [31:0] timashadow [8][2][16];
  for (genvar l = 0; l < 8; l++) begin : gl
    always @(negedge clock) if (peek_now) for (int r = 0; r < 64; r++) cshadow[l][r] = dut.VPU_LANES[l].lane.rf.vpu_64x32_3r2w_vpurf.mem[r];
    always @(negedge clock) if (poke_now) begin
      for (int i = 0; i < 16; i++) for (int h = 0; h < 2; h++)
        dut.VPU_LANES[l].lane.rf.vpu_64x32_3r2w_vpurf.mem[2 * i + h] = mem[512 + 16 * i + 8 * h + l];
    end
    for (genvar t = 0; t < 2; t++) begin : gt
      always @(negedge clock) if (peek_now) for (int r = 0; r < 16; r++)
        timashadow[l][t][r] = dut.VPU_LANES[l].lane.LANE_TIMA[t].lane_tima.tenc_rf.rf_buffer_array.mem[r];
      always @(negedge clock) if (poke_now) for (int r = 0; r < 16; r++)
        dut.VPU_LANES[l].lane.LANE_TIMA[t].lane_tima.tenc_rf.rf_buffer_array.mem[r] = mem[512 + 16 * r + 8 * t + l];
    end
  end
  bit peek_now = 0, poke_now = 0;

  // ---- accounting ---------------------------------------------------------------------------------------------------
  string fmt = "fp32";
  bit is_int8 = 0;
  int n_ops = 4, n_warm = 1, first = 1, loadc = 0, period = 0, printc = 0;
  longint unsigned cycles = 0, starts = 0, n_scp_reads = 0;
  longint unsigned txfma_valid = 0, tima_valid = 0, uops_any = 0, clk_txfma = 0, clk_tima = 0, gated = 0;
  longint unsigned busy_cycles = 0;
  bit measuring = 0;
  wire tfma_on = dut.ctrl.ml.tensorfma.enabled;
  // the lane valids the RTL itself forms (vpu_ctrl.v:839, :830)
  wire [7:0]      w_txfma_valid = dut.ctrl.ex_txfma_valid;
  wire [7:0][1:0] w_tima_valid  = dut.ctrl.ex_tima_valid;
  wire            w_tima_unqual = dut.ctrl.ex_tima_valid_unqual;
  wire            w_txfma_all   = dut.ctrl.ex_txfma_valid_all;
  always @(posedge clock) if (measuring) begin
    cycles++;
    busy_cycles += longint'(tfma_on);
    txfma_valid += longint'($countones(w_txfma_valid));
    tima_valid  += longint'($countones(w_tima_valid));
    uops_any    += longint'(w_txfma_all | w_tima_unqual);
  end

  task automatic report(input int n);
    $display("ACCT {\"fmt\":\"%s\",\"ops\":%0d,\"cycles\":%0d,\"busy\":%0d,\"uops\":%0d,\"txfma_valid\":%0d,\"tima_valid\":%0d,\"ff_clocked_bits\":%0d,\"ff_toggles\":%0d,\"ff_present_bits\":%0d,\"scp_reads\":%0d}",
             fmt, n, cycles, busy_cycles, uops_any, txfma_valid, tima_valid, acct_get(0), acct_get(1), acct_get(2), n_scp_reads);
    $display("ACCTU %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d", acct_get(10), acct_get(11), acct_get(12), acct_get(20), acct_get(21), acct_get(22), acct_get(30), acct_get(31), acct_get(32), acct_get(40), acct_get(41), acct_get(42));
  endtask

  task automatic dump_c(input int op);
    peek_now = 1;
    @(negedge clock);
    peek_now = 0;
    for (int i = 0; i < 16; i++)
      for (int j = 0; j < 16; j++) begin
        automatic logic [31:0] v;
        if (is_int8) v = timashadow[j % 8][j / 8][i];
        else         v = cshadow[j % 8][2 * i + j / 8];
        $display("C %0d %0d %0d %08x", op, i, j, v);
      end
  endtask

  // ---- one TensorFMA ------------------------------------------------------------------------------------------------
  tensorfma_control ctrl_word;
  function automatic tensorfma_control make_ctrl(input bit fp, input bit last);
    tensorfma_control w = '0;
    w.is_conv = 0;
    w.cols_b  = 2'd3;        // fma_word: 3 << 55
    w.rows_a  = 4'd15;       // (arows-1) << 51
    w.cols_a  = 4'd15;       // 15 << 47
    w.start_a = 4'd0;
    w.to_vrf  = is_int8 && last;   // the kernel sets it only on a launch's last op (1 << 23)
    w.u_b = 0; w.u_a = 0; w.ten_b = 0;
    w.scp_b = 6'd16; w.scp_a = 6'd0;
    w.mode = fmt == "fp32" ? 3'b000 : fmt == "fp16" ? 3'b001 : 3'b011;
    w.first_pass = fp;
    return w;
  endfunction

  int last_start_cycle = 0, cyc = 0;
  always @(posedge clock) cyc++;
  task automatic one_op(input bit fp, input bit last);
    // wait for the FSM to be free, and for the period since the previous start
    while (tfma_on || (cyc - last_start_cycle) < period) @(negedge clock);
    f0_core_ctrl.tensorfma_ctrl = make_ctrl(fp, last);
    f0_core_ctrl.tensorfma_start = 1;
    last_start_cycle = cyc;
    starts++;
    @(negedge clock);
    f0_core_ctrl.tensorfma_start = 0;
    @(negedge clock);
    while (tfma_on) @(negedge clock);
  endtask

  // ---- VCD window ---------------------------------------------------------------------------------------------------
  string dump_file; int dump_ops = 1; bit do_dump = 0;

  string tiles;
  initial begin
    f0_core_ctrl = '0; id_core_req = '0; ex_core_req = '0; id_sigs = '0; wb_resp = '0; reduce_ctrl = '0; scp_resp = '0;
    if (!$value$plusargs("tiles=%s", tiles)) $fatal(1, "need +tiles");
    void'($value$plusargs("fmt=%s", fmt));
    is_int8 = (fmt == "int8");
    period = is_int8 ? 318 : 546;
    void'($value$plusargs("ops=%d", n_ops));
    void'($value$plusargs("warm=%d", n_warm));
    void'($value$plusargs("first=%d", first));
    void'($value$plusargs("loadc=%d", loadc));
    void'($value$plusargs("period=%d", period));
    void'($value$plusargs("printc=%d", printc));
    do_dump = $value$plusargs("dump=%s", dump_file);
    void'($value$plusargs("dump_ops=%d", dump_ops));
    $readmemh(tiles, mem);
    for (int i = 0; i < 16; i++)
      for (int j = 0; j < 16; j++) begin
        scp[16 * i + j]      = mem[16 * i + j];
        scp[16 * (16 + i) + j] = mem[256 + 16 * i + j];
      end
    repeat (8) @(posedge clock);
    @(negedge clock) reset = 0;
    repeat (6) @(negedge clock);
    if (loadc != 0) begin
      poke_now = 1;
      @(negedge clock);
      poke_now = 0;
      @(negedge clock);
    end
    begin
      automatic int total = 0;
      for (int n = 0; n < n_warm; n++) begin
        one_op(first != 0 && total == 0, 0);
        total++;
        if (printc != 0) begin
          repeat (12) @(negedge clock);
          dump_c(total);
        end
      end
      // leave the core idle till the next start is due, then open the window exactly at it
      while ((cyc - last_start_cycle) < period - 2) @(negedge clock);
      acct_reset();
      cycles = 0; busy_cycles = 0; txfma_valid = 0; tima_valid = 0; uops_any = 0; n_scp_reads = 0;
      if (do_dump) begin
        $dumpfile(dump_file);
        $dumpvars();
      end
      measuring = 1;
      for (int n = 0; n < (do_dump ? dump_ops : n_ops); n++) begin
        one_op(first != 0 && total == 0, 0);
        total++;
        // hold the window open to the next start, so a window is a whole period
        while ((cyc - last_start_cycle) < period - 2) @(negedge clock);
        if (printc != 0 && !do_dump) begin
          measuring = 0;
          dump_c(total);
          measuring = 1;
        end
      end
      @(negedge clock);
      measuring = 0;
      report(do_dump ? dump_ops : n_ops);
      repeat (12) @(negedge clock);
      if (printc != 0) dump_c(total);
    end
    $finish;
  end
endmodule
