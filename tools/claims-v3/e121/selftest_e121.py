#!/usr/bin/env python3
"""E121 (Q134): self-test of score_e121.py on synthetic reductions, before any E121 pass exists. Nothing it prints is data.

    python3 tools/claims-v3/e121/selftest_e121.py > tools/claims-v3/e121/selftest_e121.txt

Each world is a reduction shaped like reduce_e78's (passes, per_pass > <pass> > <cell> > D, items), built from E93's own
per-pass D on card 1 (docs/reports/data/2026-11-01-e93-zero-gate-silicon/e93.json, sha-checked through predictions-e121.json),
times E82's per-type card scale, plus a little Gaussian noise (sd 0.05 W, seeded):
  replicate   every cell = scale x E93's: the 22 gate rules PASS, R5 FAILs as on card 1, pairing rtl, X PASS, tie PASS;
  value_gate  -0 and denormal tiles read as their +0 twins (gated), int8's pairing is (2l, 2l+1) and one A byte gates:
              R1, R3, R6b and R7 FAIL, the gate summary FAILs, the reading is alt, X FAILs;
  scale_off   every cell x 1.12 (a card 12% hotter than E82's scale): the gate rules still PASS, X FAILs;
  three       the replicate world with three passes: scored;
  two         the replicate world with two passes: every rule NOT SCORED.
The reduction path itself is E93's reduce_e93.py, unchanged, which selftest_e93.py tested on E78's own generator.
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_e121 as sc  # noqa: E402

REG = sc.REG
src = REG["inputs_frozen"]["e93_reduction"]
if sc.sha(os.path.join(ROOT, src["path"])) != src["sha256"]:
    raise SystemExit("e93.json differs from the one E121 froze")
E93 = json.load(open(os.path.join(ROOT, src["path"])))
SCALE = REG["card_scale"]["per_type"]


def ty(cell):
    return "fp32" if cell == "anchor_pi" else cell.split(".")[0]


def world(name, n_passes=4, mult=1.0):
    rng = random.Random(f"E121|selftest|{name}|{n_passes}")
    src_passes = [str(p) for p in E93["passes"]]
    passes = [12110 + i for i in range(n_passes)]
    per = {}
    for i, p in enumerate(passes):
        sp = E93["per_pass"][src_passes[i % len(src_passes)]]
        cells = {}
        for cell, v in sp.items():
            d = v.get("D")
            if d is None:
                continue
            cells[cell] = {"D": 0.0 if d == 0 else SCALE[ty(cell)] * mult * d + rng.gauss(0, 0.05)}
        if name == "value_gate":
            gated = {"fp32": cells["fp32.a_zeros_b_randn"]["D"], "fp16": 0.78, "int8": cells["int8.a_zeros_b_full"]["D"]}
            for c in ("fp32.nz_both", "fp32.dn1_both", "fp32.dnr_both", "fp16.nz_both", "fp16.dnr_both"):
                cells[c]["D"] = 0.0 + rng.gauss(0, 0.05)
            for c in ("fp32.a_nz_b_randn", "fp32.a_dnr_b_randn", "fp32.a_randn_b_nz", "fp32.a_randn_b_dnr"):
                cells[c]["D"] = gated["fp32"] + rng.gauss(0, 0.05)
            for c in ("fp16.a_nz_b_randn", "fp16.a_dnr_b_randn", "fp16.a_randn_b_nz"):
                cells[c]["D"] = gated["fp16"] + rng.gauss(0, 0.05)
            rtl, alt = cells["int8.b_pairs_rtl"]["D"], cells["int8.b_pairs_alt"]["D"]
            cells["int8.b_pairs_rtl"]["D"], cells["int8.b_pairs_alt"]["D"] = alt, rtl
            cells["int8.a_3of4_b_full"]["D"] = gated["int8"] + rng.gauss(0, 0.05)
            cells["fp32.sparse50_mask"]["D"] = cells["fp32.sparse50"]["D"] + rng.gauss(0, 0.05)
        per[str(p)] = cells
    items = {c: {"cycles_per_op": 318.0 if ty(c) == "int8" else 546.001} for c in per[str(passes[0])]}
    return {"passes": passes, "per_pass": per, "items": items, "passes_set_aside": [], "leak": {"mode": "0.1994"}}


def main():
    checks = []

    def check(what, ok):
        checks.append((what, bool(ok)))
        print(("ok   " if ok else "FAIL ") + what)

    for nm, kw in (("replicate", {}), ("value_gate", {}), ("scale_off", {"mult": 1.12}), ("three", {"n_passes": 3}),
                   ("two", {"n_passes": 2})):
        wname = "replicate" if nm in ("three", "two") else nm
        s = sc.score(world(wname, **kw), REG)
        print(f"-- {nm}: gate {s['gate_summary']}, tally {s['tally']}, X {s['cross_card']['aggregate']} {s['cross_card']['tally']}, "
              f"tie {s['tie_e78']['verdict']}, reading {s['pairing_reading'][:4]}")
        if nm == "replicate":
            check("replicate: the 22 gate rules PASS", s["gate_summary"] == "PASS")
            check("replicate: R5 FAILs as on card 1, R8 PASSes", s["rules"]["R5-fp32"]["verdict"] == "FAIL" and s["rules"]["R8"]["verdict"] == "PASS")
            check("replicate: every verdict equals E93's", s["same_verdict_as_e93"] == "24 of 24")
            check("replicate: pairing reading rtl", s["pairing_reading"].startswith("rtl"))
            check("replicate: cross-card aggregate PASS", s["cross_card"]["aggregate"] == "PASS")
            check("replicate: no X rule FAILs", s["cross_card"]["tally"].get("FAIL", 0) == 0)
            check("replicate: session tie to E78 PASS", s["tie_e78"]["verdict"] == "PASS")
        if nm == "value_gate":
            for rid in ("R1-fp32-both", "R1-fp32-a", "R1-fp16-both", "R3-fp32-one", "R3-fp32-both", "R6b", "R7", "R8"):
                check(f"value_gate: {rid} FAILs", s["rules"][rid]["verdict"] == "FAIL")
            check("value_gate: the gate summary FAILs", s["gate_summary"] == "FAIL")
            check("value_gate: pairing reading alt", s["pairing_reading"].startswith("alt"))
            check("value_gate: cross-card aggregate FAILs", s["cross_card"]["aggregate"] == "FAIL")
        if nm == "scale_off":
            others = [g for g in REG["gate_rules"] if g != "R2-fp16"]
            check("scale_off: every gate rule but R2-fp16 still PASSes (R2-fp16's fixed E78 constant does not move with "
                  "the session, so it alone sees a 12% hotter card)",
                  all(s["rules"][g]["verdict"] == "PASS" for g in others) and s["rules"]["R2-fp16"]["verdict"] != "PASS")
            check("scale_off: the session tie to E78 FAILs (the session moved)", s["tie_e78"]["verdict"] == "FAIL")
            check("scale_off: cross-card aggregate FAILs", s["cross_card"]["aggregate"] == "FAIL")
        if nm == "three":
            check("three passes: scored (gate PASS)", s["gate_summary"] == "PASS" and s["kept_passes"] == 3)
        if nm == "two":
            check("two passes: every rule NOT SCORED", set(v["verdict"] for v in s["rules"].values()) == {"NOT SCORED"}
                  and s["gate_summary"] == "NOT SCORED" and s["cross_card"]["aggregate"] == "NOT SCORED")

    n_ok = sum(1 for _, ok in checks if ok)
    print(f"\n{n_ok} of {len(checks)} checks")
    sys.exit(0 if n_ok == len(checks) else 1)


if __name__ == "__main__":
    main()
