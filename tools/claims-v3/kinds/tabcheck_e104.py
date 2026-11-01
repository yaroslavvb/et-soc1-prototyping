#!/usr/bin/env python3
"""E104: my three readings against E102's verifier's table, word for word, before any card time. Standard library only.

    python3 tools/claims-v3/kinds/tabcheck_e104.py <verifier's table> > <out>

The verifier wrote its table from its own emulator of the manual's sentence (walk.c) and from accum.c; make_e104.py wrote e104.json from manual_e104.c, written separately, and from accum.c. Each row compares C[0][0], C[0][8] and the count of
distinct words. Exit 1 if any row differs.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = json.load(open(os.path.join(HERE, "e104", "e104.json")))
pat = re.compile(r"e(92|88)/(\S+)\s+n\s+(\d+) window C00 (\w+) C08 (\w+)\s+(\d+) words \| exact-RTZ C00 (\w+) C08 (\w+)\s+(\d+) words")
n_ok = n_bad = n_absent = 0
for line in open(sys.argv[1]):
    m = pat.match(line)
    if not m:
        continue
    _, kind, n, w0, w8, wn, x0, x8, xn = m.groups()
    t = spec["tiles"].get("fp16." + kind)
    r = t["read"].get(n) if t else None
    if r is None:
        n_absent += 1
        print(f"not in e104.json: fp16.{kind} n {n}")
        continue
    want = ((r["c00"]["rtl"], r["c08"]["rtl"], r["distinct"]["rtl"]), (r["c00"]["manual"], r["c08"]["manual"], r["distinct"]["manual"]))
    have = ((w0, w8, int(wn)), (x0, x8, int(xn)))
    ok = want == have
    n_ok += ok
    n_bad += not ok
    print(f"{'same' if ok else 'DIFF'} fp16.{kind:9s} n {n:>6s} rtl {r['c00']['rtl']} {r['c08']['rtl']} {r['distinct']['rtl']:3d} words | manual {r['c00']['manual']} {r['c08']['manual']} {r['distinct']['manual']:3d} words | frozen {r['c00']['fl']} {r['c08']['fl']} {r['distinct']['fl']:3d} words" + ("" if ok else f"  verifier {have}"))
print(f"{n_ok} rows the same, {n_bad} differ, {n_absent} not read")
sys.exit(1 if n_bad else 0)
