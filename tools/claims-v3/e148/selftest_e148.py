#!/usr/bin/env python3
"""E148 self-test (desk, before the freeze; no card, no device). Standard library only.

    python3 tools/claims-v3/e148/selftest_e148.py > tools/claims-v3/e148/selftest.txt      # from the repo root

A. the bench's counts for m0 and m0r1 are identical to Q136(c)'s committed counts.json (desk/bench-e148.json > check_against_q136c_counts);
B. the scorer on E129's committed reduction, with each m0r2 item set to its m0r1 item plus a shift on int8's S equal to a reading's point
   (W +0.296, T -0.425, C +0.044 W), returns that reading's verdict (WALK, A-PATH, PER-CYCLE) - a synthetic input, never a result;
C. the two-term solve at W's point gives E129's post hoc walk price (89 fJ a read at a new address).
SPDX-License-Identifier: Apache-2.0"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_e148 as sc  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e148.json")))
B = json.load(open(os.path.join(HERE, "desk", "bench-e148.json")))
E = json.load(open(os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e129-int8-noissue", "e129.json")))
ok = True
a = all(v == "identical" for v in B["check_against_q136c_counts"].values())
print(f"A bench m0/m0r1 identical to Q136(c)'s counts.json: {'PASS' if a else 'FAIL'} {B['check_against_q136c_counts']}")
ok &= a
want = {"W": "WALK", "T": "A-PATH", "C": "PER-CYCLE"}
for k, lab in want.items():
    o = copy.deepcopy(E)
    for p, e in o["per_pass"].items():
        for f in ("fp32", "int8"):
            x = copy.deepcopy(e[f"m0r1.{f}.zeros"])
            if f == "int8":
                x["S"] += P["readings"][k]["point"]
            e[f"m0r2.{f}.zeros"] = x
    o["cycles_per_op"]["m0r2:fp32"], o["cycles_per_op"]["m0r2:int8"] = 96.0, 94.0
    r = sc.score(o, P, E)
    v = r["rules"]["W1"]["verdict"]
    good = v == lab and all(x["verdict"] == "PASS" for x in r["rules"]["R6"].values())
    print(f"B reading {k} at its point {P['readings'][k]['point']:+.3f} W: W1 {v} (want {lab}); R6 all PASS: "
          f"{all(x['verdict'] == 'PASS' for x in r['rules']['R6'].values())}: {'PASS' if good else 'FAIL'}")
    ok &= good
    if k == "W":
        pw = r["reported"]["two_term"]["pw_fJ_per_newaddr_read"]["mean"]
        c = abs(pw - 89.0) < 2.0
        print(f"C two-term solve at W's point: pw {pw:.1f} fJ a new-address read (E129 post hoc 89): {'PASS' if c else 'FAIL'}")
        ok &= c
print("SELFTEST", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
