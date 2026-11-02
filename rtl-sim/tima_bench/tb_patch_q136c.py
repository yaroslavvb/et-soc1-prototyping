#!/usr/bin/env python3
"""Q136(c): patch a copy of rtl-sim/fma_toggle_v2/tb_vpu.sv that E109's tb_patch_e109.py has already patched (+rows, +cols, +mask).

Adds, with nothing in the RTL changed:
  +pre=<n>       n int8 TensorFMA ops before the stream (the first with first_pass), so the stream starts the way a run does on the card
                 after an int8 run: the TIMA controls, clocked only while int8 works, keep the values that run left (vpu_tensorfma.v:841-929)
  +firstall=1    first_pass on every op of the stream (the kernel sets it only on a launch's first op): s1_tima_ren3 <= ~first_pass, so in
                 int8 TenC's read enable stays low
  counters over the measurement window, printed as `ACCTX {json}` after the ACCT lines, then the arrays' and the macro registers' dump:
    scp_rd32 / scp_rd64 / scp_rd256   the scratchpad reads the FSM issues, by size (dcache_ctrl.scp_req.size64 / size256 / neither)
    scp_data_tog        bits of the 256-bit read-data bus into the VPU that change (dcache_scp_data, as this bench's scratchpad drives it)
    scp_req_tog         bits of the request (way, addr, size64, size256, bid, read_en) that change
    tena_wd_tog, tentmp_wd_tog, tenb_wd_tog   bits of the TenA (32), TenTMP (32) and TenB (256) write-data buses that change
    tena_wen, tentmp_wen, tenb_wen            cycles each array's write enable is high (vpu_ctrl's f3_*_wen)
    tima_ren3           cycles TenC's read enable (f2_tima_ren3) is high;  tima_clk_en, working  cycles vpu_tensorfma's enables are high
    gate_tima, gate_txfma   lane clock-gate enables high, summed over the 8 lanes (one TIMA enable drives both units of a lane)
SPDX-License-Identifier: Apache-2.0"""
import os
import sys

d = sys.argv[1]
p = os.path.join(d, "tb_vpu.sv")
s = open(p).read()


def rep(old, new):
    global s
    assert s.count(old) == 1, (old, s.count(old))
    s = s.replace(old, new)


# the DPI dump
rep('  import "DPI-C" function longint acct_get(input int which);\n',
    '  import "DPI-C" function longint acct_get(input int which);\n  import "DPI-C" function void acct_dump();   // Q136(c)\n')
# plusargs and the stream's current format
rep("  int e109_rows = 16, e109_cols = 16, e109_mask = -1;   // E109: +rows +cols +mask",
    "  int e109_rows = 16, e109_cols = 16, e109_mask = -1;   // E109: +rows +cols +mask\n"
    "  int q_pre = 0, q_firstall = 0;   // Q136(c): +pre +firstall\n"
    "  string cur_fmt = \"fp32\";        // Q136(c): the format of the op being started (int8 during +pre ops)")
rep("    w.mode = fmt == \"fp32\" ? 3'b000 : fmt == \"fp16\" ? 3'b001 : 3'b011;",
    "    w.mode = cur_fmt == \"fp32\" ? 3'b000 : cur_fmt == \"fp16\" ? 3'b001 : 3'b011;   // Q136(c): cur_fmt, = fmt outside +pre")
rep('    void\'($value$plusargs("rows=%d", e109_rows));',
    '    void\'($value$plusargs("rows=%d", e109_rows));\n'
    '    void\'($value$plusargs("pre=%d", q_pre));\n'
    '    void\'($value$plusargs("firstall=%d", q_firstall));')
# the +pre ops, then the stream (its first op is a new launch's: first_pass, as before)
rep("      automatic int total = 0;\n",
    "      automatic int total = 0;\n"
    "      cur_fmt = \"int8\";\n"
    "      for (int n = 0; n < q_pre; n++) one_op(n == 0, 0);   // Q136(c): an int8 run before the stream\n"
    "      cur_fmt = fmt;\n")
rep("        one_op(first != 0 && total == 0, 0);\n        total++;\n        if (printc != 0) begin",
    "        one_op(q_firstall != 0 || (first != 0 && total == 0), 0);\n        total++;\n        if (printc != 0) begin")
rep("        one_op(first != 0 && total == 0, 0);\n        total++;\n        // hold the window open",
    "        one_op(q_firstall != 0 || (first != 0 && total == 0), 0);\n        total++;\n        // hold the window open")
# counters
rep("  always @(posedge clock) if (measuring) begin\n    cycles++;",
    "  // ---- Q136(c) counters ----------------------------------------------------------------------------------------------\n"
    "  longint unsigned q_rd32 = 0, q_rd64 = 0, q_rd256 = 0, q_scp_tog = 0, q_req_tog = 0, q_tena_tog = 0, q_tentmp_tog = 0, q_tenb_tog = 0;\n"
    "  longint unsigned q_tena_wen = 0, q_tentmp_wen = 0, q_tenb_wen = 0, q_ren3 = 0, q_tima_clk_en = 0, q_working = 0;\n"
    "  longint unsigned q_gate_tima = 0, q_gate_txfma = 0;\n"
    "  logic [`DCACHE_DATA_RANGE] q_scp_prev = '0, q_tenb_prev = '0;\n"
    "  logic [31:0] q_tena_prev = '0, q_tentmp_prev = '0;\n"
    "  logic [$bits(dcache_ctrl.scp_req)-1:0] q_req_prev = '0;\n"
    "  wire [7:0] q_lane_tima_en, q_lane_txfma_en;\n"
    "  for (genvar l = 0; l < 8; l++) begin : q_lanes\n"
    "    assign q_lane_tima_en[l]  = dut.VPU_LANES[l].lane.clock_en_tima;\n"
    "    assign q_lane_txfma_en[l] = dut.VPU_LANES[l].lane.clock_en_txfma;\n"
    "  end\n"
    "  always @(posedge clock) if (measuring) begin\n"
    "    if (dcache_ctrl.scp_req.read_en) begin\n"
    "      if (dcache_ctrl.scp_req.size256) q_rd256++;\n"
    "      else if (dcache_ctrl.scp_req.size64) q_rd64++;\n"
    "      else q_rd32++;\n"
    "    end\n"
    "    q_scp_tog    += longint'($countones(scp_data ^ q_scp_prev));\n"
    "    q_req_tog    += longint'($countones(dcache_ctrl.scp_req ^ q_req_prev));\n"
    "    q_tena_tog   += longint'($countones(dut.ctrl.f3_tena_regfile_wdata_l ^ q_tena_prev));\n"
    "    q_tentmp_tog += longint'($countones(dut.ctrl.f3_tentmp_msb_regfile_wdata_l ^ q_tentmp_prev));\n"
    "    q_tenb_tog   += longint'($countones(dut.ctrl.f3_tenb_regfile_wdata_l ^ q_tenb_prev));\n"
    "    q_tena_wen   += longint'(dut.ctrl.f3_tena_regfile_wen_l);\n"
    "    q_tentmp_wen += longint'(dut.ctrl.ml.tensorfma.f3_tentmp_wen);\n"
    "    q_tenb_wen   += longint'(dut.ctrl.f3_tenb_regfile_wen_l);\n"
    "    q_ren3       += longint'(dut.ctrl.ml.tensorfma.f2_tima_ren3);\n"
    "    q_tima_clk_en += longint'(dut.ctrl.ml.tensorfma.tima_clk_en);\n"
    "    q_working    += longint'(dut.ctrl.ml.tensorfma.working);\n"
    "    q_gate_tima  += longint'($countones(q_lane_tima_en));\n"
    "    q_gate_txfma += longint'($countones(q_lane_txfma_en));\n"
    "  end\n"
    "  always @(posedge clock) begin   // the previous cycle's values, kept outside the window too, so its first cycle compares right\n"
    "    q_scp_prev <= scp_data; q_req_prev <= dcache_ctrl.scp_req; q_tena_prev <= dut.ctrl.f3_tena_regfile_wdata_l;\n"
    "    q_tentmp_prev <= dut.ctrl.f3_tentmp_msb_regfile_wdata_l; q_tenb_prev <= dut.ctrl.f3_tenb_regfile_wdata_l;\n"
    "  end\n"
    "  always @(posedge clock) if (measuring) begin\n    cycles++;")
rep("      cycles = 0; busy_cycles = 0; txfma_valid = 0; tima_valid = 0; uops_any = 0; n_scp_reads = 0;\n",
    "      cycles = 0; busy_cycles = 0; txfma_valid = 0; tima_valid = 0; uops_any = 0; n_scp_reads = 0;\n"
    "      q_rd32 = 0; q_rd64 = 0; q_rd256 = 0; q_scp_tog = 0; q_req_tog = 0; q_tena_tog = 0; q_tentmp_tog = 0; q_tenb_tog = 0;\n"
    "      q_tena_wen = 0; q_tentmp_wen = 0; q_tenb_wen = 0; q_ren3 = 0; q_tima_clk_en = 0; q_working = 0; q_gate_tima = 0; q_gate_txfma = 0;\n")
rep('    $display("ACCTU %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d", acct_get(10), acct_get(11), acct_get(12), acct_get(20), acct_get(21), acct_get(22), acct_get(30), acct_get(31), acct_get(32), acct_get(40), acct_get(41), acct_get(42));\n',
    '    $display("ACCTU %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d %0d", acct_get(10), acct_get(11), acct_get(12), acct_get(20), acct_get(21), acct_get(22), acct_get(30), acct_get(31), acct_get(32), acct_get(40), acct_get(41), acct_get(42));\n'
    '    $display("ACCTX {\\"pre\\":%0d,\\"firstall\\":%0d,\\"scp_rd32\\":%0d,\\"scp_rd64\\":%0d,\\"scp_rd256\\":%0d,\\"scp_data_tog\\":%0d,\\"scp_req_tog\\":%0d,\\"tena_wd_tog\\":%0d,\\"tentmp_wd_tog\\":%0d,\\"tenb_wd_tog\\":%0d,\\"tena_wen\\":%0d,\\"tentmp_wen\\":%0d,\\"tenb_wen\\":%0d,\\"tima_ren3\\":%0d,\\"tima_clk_en\\":%0d,\\"working\\":%0d,\\"gate_tima\\":%0d,\\"gate_txfma\\":%0d}",\n'
    '             q_pre, q_firstall, q_rd32, q_rd64, q_rd256, q_scp_tog, q_req_tog, q_tena_tog, q_tentmp_tog, q_tenb_tog, q_tena_wen, q_tentmp_wen, q_tenb_wen, q_ren3, q_tima_clk_en, q_working, q_gate_tima, q_gate_txfma);\n'
    '    acct_dump();\n')
open(p, "w").write(s)
print("patched (Q136(c))", d)
