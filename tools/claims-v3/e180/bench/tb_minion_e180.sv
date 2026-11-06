// E180 (Q146(f)): the energy catalogue's vector-add loop on core-et's WHOLE minion, both harts, under Verilator 5.052.
// Thu 5 / Fri 6 Nov 2026. It counts what switches in a one-number fadd.ps / fadd.pi loop, by register and bus class, and
// the loop's own gaps between results, from the RTL's front end, integer pipe, CSR replay and vector unit together.
//
// It instantiates core-et's minion_top whole (b38a1a3, rtl/shire/minion/minion_top.v): frontend_top (thread buffers,
// thread scheduler, RVC expander, VPU decoder), intpipe_top (decode, scoreboards, CSRs with the PMU-read replay), the
// dcache, and vpu_top (vpu_ctrl, all eight vpu_lanes with their register files, bypass and txfma). WHAT REMAINS
// TESTBENCH CODE, all of it below and nothing else:
//   1. The shared instruction cache of the neighbourhood (rtl/shire/neigh/neigh_shared_icache.v, not instantiated): a
//      request accepted in the minion's F1 is answered in its F5, four cycles later, always a hit, with the 32 B block
//      at the request's address; icache_req_ready every +icq cycles (1: never contended, the registered primary).
//   2. The neighbourhood's PMU read path, as rtl/shire/neigh/neigh_pmu.v writes it: pmu_read_sel flopped, then the
//      selected counter flopped into pmu_read_data (two cycles); the counter is this bench's cycle count.
//   3. Ties: no data-cache traffic is made (the program needs none), PTW, interrupts, debug, DFT, APB and ESRs idle.
//   4. Read-only back doors: the RF words, and each thread's ++iters register (x9) in the integer latch array.
// Clock: one free-running clock, zero delay, no glitches; the chip's PLL, clock tree and wires are not modelled.
//
//   +prog=<hex>    the program (asm_e180.py), one 32-bit word per line from 0x1000
//   +enabled=<n>   thread mask: 3 both harts (the catalogue's h2), 1 hart 0 alone (h1)
//   +warm=<n>      cycles before the window (reset, prologue, the first iterations)
//   +win=<n>       cycles in the window
//   +icq=<k>       the icache answers a request only on every k-th cycle (1 = always)
//   +trace=<n>     print the first n cycles of the window: issue, write-back and gap per cycle
//   +t1_delay=<d>  hart 1 starts d cycles after hart 0 (default 0: both from reset)
`include "soc.vh"
module tb;
  import "DPI-C" function void acct_reset();
  import "DPI-C" function longint acct_get(input int which);

  logic clock = 0, reset = 1;
  always #1 clock = ~clock;

  localparam int unsigned BASE = 32'h1000;
  logic [31:0] imem [0:4095];
  int unsigned cyc = 0;
  always @(posedge clock) cyc <= cyc + 1;

  // ---- the instruction cache (testbench item 1) -------------------------------------------------------------------
  logic icache_req_valid;
  logic [$bits(frontend_icache_req)-1:0] icache_req_v;
  frontend_icache_req icache_req_s;
  assign icache_req_s = frontend_icache_req'(icache_req_v);
  int icq = 1;
  wire icache_req_ready = (icq <= 1) ? 1'b1 : ((cyc % icq) == 0);
  logic [4:1] pv = '0;
  logic [63:0] pa [4:1];
  always @(posedge clock) begin
    if (reset) pv <= '0;
    else begin
      pv[1] <= icache_req_valid && icache_req_ready;
      pa[1] <= 64'(icache_req_s.addr);
      pv[2] <= pv[1]; pa[2] <= pa[1];
      pv[3] <= pv[2]; pa[3] <= pa[2];
      pv[4] <= pv[3]; pa[4] <= pa[3];
    end
  end
  icache_frontend_resp resp_s;
  always_comb begin
    automatic int unsigned blk = (32'(pa[4]) - BASE) / 32;
    resp_s = '0;
    for (int w = 0; w < 8; w++) resp_s.data[32 * w +: 32] = imem[(blk * 8 + w) % 4096];
    resp_s.cacheable = 1'b1;
  end
  wire icache_resp_valid = pv[4];
  int n_fetch = 0;

  // ---- the PMU read path (testbench item 2) -----------------------------------------------------------------------
  logic [`CORE_NR_THREADS-1:0][`PMU_COUNTERS_SELECT_RANGE] pmu_read_sel, pmu_read_sel_reg;
  logic [`CORE_NR_THREADS-1:0][`XREG_RANGE] pmu_read_data = '0;
  always @(posedge clock) begin
    pmu_read_sel_reg <= pmu_read_sel;
    for (int t = 0; t < `CORE_NR_THREADS; t++)
      if (pmu_read_sel_reg[t] < `PMU_TOTAL_COUNTERS_NUM) pmu_read_data[t] <= 64'(cyc);
  end

  logic [`CORE_NR_THREADS-1:0] enabled = 2'b11;

  minion_top dut (
    .clock(clock), .reset(reset), .reset_debug(reset), .reset_non_debug(reset),
    .dft__scanin('0), .dft__scanout(), .dft__scan_mode(1'b0), .dft__reset_byp(1'b0), .dft__scan_enable(1'b0),
    .dft__test_mode('0), .dft__reset(1'b0), .dft__clock_gate_en(1'b0), .dft__cntl('0), .dft__occ_scanin(1'b0),
    .dft__occ_scanout(), .dft__occ_reset(1'b0), .dft__occ_testmode(1'b0), .dft__scan_ate_clk(1'b0), .dft__occ_bypass(1'b0),
    .eco_i('0), .eco_o(), .ioshire(1'b0), .nsleepin(1'b1), .iso_enable(1'b0), .nsleepout(), .chicken_bits('0),
    .l2_dcache_evict_req_ready('1), .l2_dcache_evict_req_valid(), .l2_dcache_evict_req(),
    .l2_dcache_miss_req_ready('1), .l2_dcache_miss_req_valid(), .l2_dcache_miss_req(),
    .l2_dcache_resp_ready(), .l2_dcache_resp_valid(1'b0), .l2_dcache_resp('0),
    .icache_req_ready(icache_req_ready), .icache_req_valid(icache_req_valid), .icache_req(icache_req_v),
    .icache_resp_valid(icache_resp_valid), .icache_resp_miss(1'b0), .icache_resp(resp_s), .icache_fill_done(1'b0),
    .icache_flush_data(), .satp_info(), .matp_info(), .tlb_invalidate(),
    .dc_ptw_req_data(), .dc_ptw_req_valid(), .dc_ptw_req_ready(1'b1), .ptw_dc_resp_data('0), .ptw_dc_resp_valid(1'b0),
    .interrupts('0), .shire_id('0), .shire_min_id('0), .enabled(enabled), .reset_vector(BASE),
    .mprot('0), .vmspagesize('0),
    .flb_neigh_req_valid(), .flb_neigh_req_data(), .flb_neigh_resp_valid(1'b0), .flb_neigh_resp_data(1'b0),
    .te_thread_sel(1'b0), .traceEncoder(), .te_enable(1'b0),
    .apb_paddr('0), .apb_penable(1'b0), .apb_prdata(), .apb_pready(), .apb_psel(1'b0), .apb_pslverr(), .apb_pwdata('0),
    .apb_pwrite(1'b0), .debug_in('0), .debug_out(), .minion_dbg_signals(), .minion_dbg_signals_mux('0),
    .minion_dbg_sig_enable(1'b0), .esr_features('0), .esr_bypass_dcache(1'b0), .esr_shire_coop_mode(1'b0),
    .esr_minion_mem_override('0), .pmu_count_up(), .pmu_read_data(pmu_read_data), .pmu_read_sel(pmu_read_sel),
    .pmu_write_en(), .pmu_write_data(), .pmu_neigh_event_sel());

  // ---- the counts, by class (lane-summed bit flips between consecutive cycles) -------------------------------------
  bit measuring = 0;
  int trace_n = 0, traced = 0;
  // classes: 0 wb_res (txfma result, AND-ed with its valid), 1 wr0 (RF write port 0 data = f8_wdata), 2 wr1, 3 byp (the
  // three bypass registers), 4 ram_rd (the RF macro's registered read data, 3 ports), 5 rd (read data after the bypass
  // mux), 6 opnd (txfma's in1/in2/in3), 7 rf_store (the 64 RF words), 8 shsw (the short pipe's F4..F8 stage data)
  localparam int NC = 9;
  longint unsigned flips [NC];
  longint unsigned wb_cycles [2];          // lane-0 RF port-0 writes, by thread
  longint unsigned wb_any = 0, gap_runs = 0, gap_cycles = 0, vpu_id_valid [2];
  longint unsigned gap_hist [17];
  logic [31:0] p_wb_res [8], p_wr0 [8], p_wr1 [8], p_byp [8][3], p_ram [8][3], p_rd [8][3], p_op [8][3], p_sh [8][5];
  logic [31:0] p_mem [8][64];
  bit prev_wb = 0;
  int run_len = 0;
  string fdesc;

  for (genvar l = 0; l < 8; l++) begin : MON
    wire [31:0] wb_res = dut.vpu.VPU_LANES[l].lane.f8_txfma_res.data;
    wire [31:0] wr0 = dut.vpu.VPU_LANES[l].lane.rf.wr_data[0];
    wire [31:0] wr1 = dut.vpu.VPU_LANES[l].lane.rf.wr_data[1];
    wire [31:0] byp0 = dut.vpu.VPU_LANES[l].lane.rf.bypass_data[0];
    wire [31:0] byp1 = dut.vpu.VPU_LANES[l].lane.rf.bypass_data[1];
    wire [31:0] byp2 = dut.vpu.VPU_LANES[l].lane.rf.bypass_data[2];
    wire [31:0] ram0 = dut.vpu.VPU_LANES[l].lane.rf.ram_rd_data[0];
    wire [31:0] ram1 = dut.vpu.VPU_LANES[l].lane.rf.ram_rd_data[1];
    wire [31:0] ram2 = dut.vpu.VPU_LANES[l].lane.rf.ram_rd_data[2];
    wire [31:0] rd0 = dut.vpu.VPU_LANES[l].lane.rf.rd_data[0];
    wire [31:0] rd1 = dut.vpu.VPU_LANES[l].lane.rf.rd_data[1];
    wire [31:0] rd2 = dut.vpu.VPU_LANES[l].lane.rf.rd_data[2];
    wire [31:0] op0 = dut.vpu.VPU_LANES[l].lane.ex_req.in1;
    wire [31:0] op1 = dut.vpu.VPU_LANES[l].lane.ex_req.in2;
    wire [31:0] op2 = dut.vpu.VPU_LANES[l].lane.ex_req.in3;
    wire [31:0] sh4 = dut.vpu.VPU_LANES[l].lane.bypass.f4_bits.data;
    wire [31:0] sh5 = dut.vpu.VPU_LANES[l].lane.bypass.f5_bits.data;
    wire [31:0] sh6 = dut.vpu.VPU_LANES[l].lane.bypass.f6_bits.data;
    wire [31:0] sh7 = dut.vpu.VPU_LANES[l].lane.bypass.f7_bits.data;
    wire [31:0] sh8 = dut.vpu.VPU_LANES[l].lane.bypass.f8_bits.data;
    always @(negedge clock) begin
      if (measuring) begin
        flips[0] += $countones(wb_res ^ p_wb_res[l]);
        flips[1] += $countones(wr0 ^ p_wr0[l]);
        flips[2] += $countones(wr1 ^ p_wr1[l]);
        flips[3] += $countones(byp0 ^ p_byp[l][0]) + $countones(byp1 ^ p_byp[l][1]) + $countones(byp2 ^ p_byp[l][2]);
        flips[4] += $countones(ram0 ^ p_ram[l][0]) + $countones(ram1 ^ p_ram[l][1]) + $countones(ram2 ^ p_ram[l][2]);
        flips[5] += $countones(rd0 ^ p_rd[l][0]) + $countones(rd1 ^ p_rd[l][1]) + $countones(rd2 ^ p_rd[l][2]);
        flips[6] += $countones(op0 ^ p_op[l][0]) + $countones(op1 ^ p_op[l][1]) + $countones(op2 ^ p_op[l][2]);
        flips[8] += $countones(sh4 ^ p_sh[l][0]) + $countones(sh5 ^ p_sh[l][1]) + $countones(sh6 ^ p_sh[l][2]) +
                    $countones(sh7 ^ p_sh[l][3]) + $countones(sh8 ^ p_sh[l][4]);
        for (int r = 0; r < 64; r++) begin
          flips[7] += $countones(dut.vpu.VPU_LANES[l].lane.rf.vpu_64x32_3r2w_vpurf.mem[r] ^ p_mem[l][r]);
        end
      end
      p_wb_res[l] = wb_res; p_wr0[l] = wr0; p_wr1[l] = wr1;
      p_byp[l][0] = byp0; p_byp[l][1] = byp1; p_byp[l][2] = byp2;
      p_ram[l][0] = ram0; p_ram[l][1] = ram1; p_ram[l][2] = ram2;
      p_rd[l][0] = rd0; p_rd[l][1] = rd1; p_rd[l][2] = rd2;
      p_op[l][0] = op0; p_op[l][1] = op1; p_op[l][2] = op2;
      p_sh[l][0] = sh4; p_sh[l][1] = sh5; p_sh[l][2] = sh6; p_sh[l][3] = sh7; p_sh[l][4] = sh8;
      for (int r = 0; r < 64; r++) p_mem[l][r] = dut.vpu.VPU_LANES[l].lane.rf.vpu_64x32_3r2w_vpurf.mem[r];
    end
  end

  // lane 0's RF write port 0: a result is written this cycle (its thread), or not (a gap in the write-back)
  wire       wb_en0  = dut.vpu.VPU_LANES[0].lane.rf.wr_en[0] & dut.vpu.VPU_LANES[0].lane.rf.wr_mask[0];
  wire       wb_th0  = dut.vpu.VPU_LANES[0].lane.rf.wr_thrid[0];
  wire       id_v    = dut.vpu.id_core_req.valid;
  wire       id_t    = dut.vpu.id_core_req.thread_id;
  always @(negedge clock) if (measuring) begin
    if (id_v) vpu_id_valid[id_t]++;
    if (wb_en0) begin
      wb_cycles[wb_th0]++;
      wb_any++;
      if (!prev_wb && run_len > 0) begin gap_hist[run_len > 16 ? 16 : run_len]++; end
      run_len = 0;
    end else begin
      gap_cycles++;
      if (prev_wb) gap_runs++;
      run_len++;
    end
    prev_wb = wb_en0;
    if (icache_resp_valid) n_fetch++;
    if (traced < trace_n) begin
      $display("T %0d id=%0d.%0d wb=%0d.%0d res0=%08x wr0=%08x byp0=%08x ram0=%08x fetch=%0d", cyc, id_v, id_t, wb_en0, wb_th0,
               MON[0].wb_res, MON[0].wr0, MON[0].byp0, MON[0].ram0, icache_resp_valid);
      traced++;
    end
  end

  // ++iters of each thread (x9), read from the integer latch array (testbench item 4: read only)
  function automatic longint unsigned iters_of(input int t);
    return longint'(dut.core.intpipe.rf.rf_latches.rf[t * 32 + 9]);
  endfunction

  string prog;
  int warm = 4000, win = 20000, en = 3, t1_delay = 0;
  longint unsigned it0 [2], it1 [2];
  initial begin
    for (int c = 0; c < NC; c++) flips[c] = 0;
    for (int i = 0; i < 17; i++) gap_hist[i] = 0;
    wb_cycles[0] = 0; wb_cycles[1] = 0; vpu_id_valid[0] = 0; vpu_id_valid[1] = 0;
    for (int i = 0; i < 4096; i++) imem[i] = 32'h00000013;
    if (!$value$plusargs("prog=%s", prog)) $fatal(1, "need +prog");
    void'($value$plusargs("enabled=%d", en));
    void'($value$plusargs("warm=%d", warm));
    void'($value$plusargs("win=%d", win));
    void'($value$plusargs("icq=%d", icq));
    void'($value$plusargs("trace=%d", trace_n));
    void'($value$plusargs("t1_delay=%d", t1_delay));
    $readmemh(prog, imem);
    // +t1_delay=<d>: hart 1 is enabled d cycles after hart 0 (a launch's two harts need not start on one cycle)
    enabled = (t1_delay > 0 && en == 3) ? 2'b01 : en[1:0];
    repeat (16) @(posedge clock);
    @(negedge clock) reset = 0;
    if (t1_delay > 0 && en == 3) begin
      repeat (t1_delay) @(negedge clock);
      enabled = 2'b11;
      repeat (warm - t1_delay) @(negedge clock);
    end else repeat (warm) @(negedge clock);
    for (int t = 0; t < 2; t++) it0[t] = iters_of(t);
    acct_reset();
    measuring = 1;
    repeat (win) @(negedge clock);
    measuring = 0;
    for (int t = 0; t < 2; t++) it1[t] = iters_of(t);
    $display("E180 {\"cycles\":%0d,\"iters\":[%0d,%0d],\"wb\":[%0d,%0d],\"wb_any\":%0d,\"id_vpu\":[%0d,%0d],\"gap_cycles\":%0d,\"gap_runs\":%0d,\"fetches\":%0d,\"flips\":{\"wb_res\":%0d,\"wr0\":%0d,\"wr1\":%0d,\"byp\":%0d,\"ram_rd\":%0d,\"rd\":%0d,\"opnd\":%0d,\"rf_store\":%0d,\"shsw\":%0d},\"ff\":{\"clocked\":%0d,\"toggles\":%0d,\"present\":%0d,\"txfma_toggles\":%0d,\"rest_toggles\":%0d}}",
             win, it1[0] - it0[0], it1[1] - it0[1], wb_cycles[0], wb_cycles[1], wb_any, vpu_id_valid[0], vpu_id_valid[1],
             gap_cycles, gap_runs, n_fetch, flips[0], flips[1], flips[2], flips[3], flips[4], flips[5], flips[6], flips[7],
             flips[8], acct_get(0), acct_get(1), acct_get(2), acct_get(11), acct_get(31));
    fdesc = "";
    for (int i = 1; i < 17; i++) fdesc = {fdesc, $sformatf("%s%0d", i > 1 ? "," : "", gap_hist[i])};
    $display("E180GAPS [%s]", fdesc);
    $finish;
  end
endmodule
