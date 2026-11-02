#!/usr/bin/env python3
"""E129 POST HOC (written after the data; decides nothing): arithmetic on E129's committed scored.json and Q136(c)'s committed priced.json.

    python3 docs/reports/data/2026-11-02-e129-int8-noissue/posthoc/posthoc_e129.py > posthoc.txt

1. What N - N1 (the part of int8's no-issue excess that one A row removes) would cost per event if it were all one event: per TenC read at a new address
   (the walk; 16-row int8 a second, Q136(c)), per 64-bit A read into TenTMP, per TenTMP write (both the A path). These are UPPER bounds on each one's
   price: N - N1 also holds the other per-row changes.
2. N1 beside the TIMA controls at the cards' issue price in the one-row arm (Q136(c) corrections-check.json, result 5b).
3. One row's fp32 level over the 16-row loop, S(m0r1) - S(m0), against what this session's own per-op price predicts for the op-rate change alone.
Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(D, "..", "..", "..", ".."))
Q = os.path.join(ROOT, "docs/reports/data/2026-11-02-q136c-tima-bench")
s = json.load(open(os.path.join(D, "scored.json")))
pr = json.load(open(os.path.join(Q, "priced.json")))
cc = json.load(open(os.path.join(Q, "corrections-check.json")))
E = "E124, aifoundry1 card 1 (registered, four passes)"
dn = pr["experiments"][E]["contrasts"]["N, from reset (the bench's own runs)"]["d_counts_per_s"]
o = s["one_row"]
dd = o["N_minus_N1"]
print("E129 POST HOC (decides nothing)")
print(f"N - N1 = {dd['mean']:+.3f} W, 95% [{dd['lo']:+.3f}, {dd['hi']:+.3f}] over {dd['n']} passes")
for lab, rate in (("a TenC read at a new address (the walk)", dn["tenc"]["reads_newaddr"]),
                  ("a 64-bit A read into TenTMP (int8's A path)", dn["scp"]["rd64"]),
                  ("a TenTMP write (int8's A path)", dn["scp"]["tentmp_writes"])):
    print(f"  if all of it were {lab}: {dd['mean'] / rate * 1e15:.0f} fJ each, 95% [{dd['lo'] / rate * 1e15:.0f}, {dd['hi'] / rate * 1e15:.0f}] "
          f"({rate:.3e} a second more in int8's 16-row loop than fp32's, Q136(c) priced.json, E124's rates)")
t = cc["experiments"][E]["per_pass"]["desk-only arm: one A row, fp32 after an int8 run|A|tima_ctrl"]
n1 = o["N1"]
print(f"N1 = {n1['mean']:+.3f} W [{n1['lo']:+.3f}, {n1['hi']:+.3f}]; the TIMA controls at the cards' issue price in this arm: {t['mean']:.3f} W "
      f"[{t['lo']:.3f}, {t['hi']:.3f}] (Q136(c) corrections-check.json); N1 / N = {n1['mean'] / o['N']['mean']:.2f}")
q = s["quantities"]
for f in ("fp32", "int8"):
    up = o[f"r1_over_m0_{f}"]
    e = q[f]["e_op_pj"]["mean"] * 1e-12
    dr = q[f]["rate_m0r1"]["mean"] - s["per_pass"][s["passes"][0]][f]["rates"]["m0"]
    print(f"{f}: S(m0r1) - S(m0) = {up['mean']:+.3f} W [{up['lo']:+.3f}, {up['hi']:+.3f}]; this session's e_op x the op-rate change "
          f"({q[f]['e_op_pj']['mean']:.0f} pJ x {dr:.3e}/s) = {e * dr:+.3f} W")
