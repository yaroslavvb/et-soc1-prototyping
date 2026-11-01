#!/usr/bin/env python3
"""E109 desk: patch a copy of rtl-sim/fma_toggle_v2's tb_vpu.sv and acct.cpp in <dir> (bench_e109.sh calls it). Three plusargs feed the TensorFMA's
control word: +rows (A rows, AROWS), +cols (A columns, ACOLS), +mask (the row mask: sets is_conv and drives tensorfma_conv_bits, as the core does
after `csrw tensor_mask`). Defaults give the original word. acct.cpp loses its coverage hook (the lean build has no coverage)."""
import os, sys
d = sys.argv[1]
p = os.path.join(d, "tb_vpu.sv"); s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old, s.count(old))
    s = s.replace(old, new)
rep("  int n_ops = 4, n_warm = 1, first = 1, loadc = 0, period = 0, printc = 0;",
    "  int n_ops = 4, n_warm = 1, first = 1, loadc = 0, period = 0, printc = 0;\n  int e109_rows = 16, e109_cols = 16, e109_mask = -1;   // E109: +rows +cols +mask")
rep("    w.is_conv = 0;", "    w.is_conv = (e109_mask >= 0);   // E109: MSK bit when +mask is given")
rep("    w.rows_a  = 4'd15;       // (arows-1) << 51", "    w.rows_a  = 4'(e109_rows - 1);   // E109: (arows-1) << 51")
rep("    w.cols_a  = 4'd15;       // 15 << 47", "    w.cols_a  = 4'(e109_cols - 1);   // E109: (acols-1) << 47")
rep("    f0_core_ctrl.tensorfma_ctrl = make_ctrl(fp, last);\n",
    "    f0_core_ctrl.tensorfma_ctrl = make_ctrl(fp, last);\n    if (e109_mask >= 0) begin f0_core_ctrl.tensorfma_conv_bits = 16'(e109_mask); f0_core_ctrl.tensorfma_conv_bits_ready = 1; end   // E109\n")
rep('    void\'($value$plusargs("period=%d", period));',
    '    void\'($value$plusargs("period=%d", period));\n    void\'($value$plusargs("rows=%d", e109_rows));\n    void\'($value$plusargs("cols=%d", e109_cols));\n    void\'($value$plusargs("mask=%h", e109_mask));')
open(p, "w").write(s)
q = os.path.join(d, "acct.cpp"); a = open(q).read()
for old, new in (('  Verilated::threadContextp()->coveragep()->zero();\n', '  // E109 lean build: no coverage\n'), ('#include "verilated_cov.h"\n', '')):
    assert a.count(old) == 1, old
    a = a.replace(old, new)
open(q, "w").write(a)
print("patched", d)
