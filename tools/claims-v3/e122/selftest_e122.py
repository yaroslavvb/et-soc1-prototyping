#!/usr/bin/env python3
"""E122 (Q134): self-test of score_e122.py on synthetic reductions and read-backs, before any E122 pass exists. Nothing it
prints is data.

    python3 tools/claims-v3/e122/selftest_e122.py > tools/claims-v3/e122/selftest_e122.txt

Each world is a reduction shaped like reduce_e78's (passes, per_pass > <pass> > <cell> > D, items > <cell> > D), built from
E108's own per-pass D on card 1 (docs/reports/data/2026-11-01-e108-sign-located/e108.json, sha-checked through
predictions-e122.json) times E82's per-type card scale, plus Gaussian noise (sd 0.03 W, seeded):
  replicate    every cell = scale x E108's: E108's verdicts come back (R1 with a synthetic read-back of the registered
               words), the cross-card aggregate PASSes, the tie to E78 PASSes;
  no_location  the same, but the two held tiles whose accumulators differ read as their equal-accumulator twins
               (c_mx_f as s_abs, b_B_z as z_s): R7 and R12 LITTLE, the cross-card aggregate FAILs;
  two / one    the replicate world with two passes (scored, E108's minimum) and one (every power rule NOT SCORED);
  read-back    one tile's words off: R1 FAIL; one read with a minion disagreeing: R1 UNREAD.
The reduction path is E108's reduce_e108.py, unchanged, which selftest_e108.py tested on E78's own generator.
"""
import copy
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_e122 as sc  # noqa: E402

REG = sc.REG
src = REG["inputs_frozen"]["e108_reduction"]
if sc.sha(os.path.join(ROOT, src["path"])) != src["sha256"]:
    raise SystemExit("e108.json differs from the one E122 froze")
E108 = json.load(open(os.path.join(ROOT, src["path"])))
SCALE = REG["card_scale"]["per_type"]


def ty(cell):
    return "fp32" if cell == "anchor_pi" else cell.split(".")[0]


def world(name, n_passes=4):
    rng = random.Random(f"E122|selftest|{name}|{n_passes}")
    src_passes = [str(p) for p in E108["passes"]]
    passes = [12210 + i for i in range(n_passes)]
    per = {}
    for i, p in enumerate(passes):
        sp = E108["per_pass"][src_passes[i % len(src_passes)]]
        cells = {}
        for cell, v in sp.items():
            d = v.get("D")
            if d is None:
                continue
            cells[cell] = {"D": SCALE.get(ty(cell), 1.0) * d + rng.gauss(0, 0.03)}
        if name == "no_location":
            cells["fp32.c_mx_f"]["D"] = cells["fp32.s_abs"]["D"] + rng.gauss(0, 0.03)
            cells["fp32.b_B_z"]["D"] = cells["fp32.z_s"]["D"] + rng.gauss(0, 0.03)
        per[str(p)] = cells
    items = {}
    for cell in per[str(passes[0])]:
        v = [per[str(p)][cell]["D"] for p in passes if cell in per[str(p)]]
        ci = None if len(v) < 2 else sc.s108.t975(len(v) - 1) * statistics.stdev(v) / math.sqrt(len(v))
        items[cell] = {"D": {"mean": sum(v) / len(v), "ci95": ci, "n": len(v)}}
    return {"passes": passes, "per_pass": per, "items": items, "passes_set_aside": [], "leak": {"mode": "0.1994"}}


def readback_rows(off_tile=None, split_tile=None):
    rows = []
    spec = sc.SPEC
    for t, lens in spec["readback"].items():
        for n in lens:
            e = spec["tiles"][t]["read"][str(n)]
            hx = e["rtl_hex"]
            if t == off_tile:
                b = bytearray(bytes.fromhex(hx))
                b[0] ^= 0x01
                hx = b.hex()
            groups = {"g": {"minions": 1024, "first_minion": 0, "hex": hx}}
            if t == split_tile and n == lens[0]:
                groups = {"g": {"minions": 1023, "first_minion": 0, "hex": hx}, "h": {"minions": 1, "first_minion": 7, "hex": hx[:-2] + "00"}}
            rows.append({"tile": t, "n": n, "rc": 0, "sparsity": {"ok": True, "cycles_per_op": 546.0, "iters": n},
                         "distinct_c": len(groups), "groups": groups})
    return rows


def as_rows(raw):
    path = os.path.join(HERE, ".selftest-readback.jsonl")
    with open(path, "w") as f:
        for r in raw:
            f.write(json.dumps(r) + "\n")
    rows = sc.s108.read_rows(path, sc.SPEC)
    os.remove(path)
    return rows


def main():
    checks = []

    def check(what, ok):
        checks.append((what, bool(ok)))
        print(("ok   " if ok else "FAIL ") + what)

    good = as_rows(readback_rows())
    for nm, kw in (("replicate", {}), ("no_location", {}), ("two", {"n_passes": 2}), ("one", {"n_passes": 1})):
        wname = "replicate" if nm in ("two", "one") else nm
        s = sc.score(world(wname, **kw), good)
        v = {r: x["verdict"] for r, x in s["rules"].items()}
        print(f"-- {nm}: {v}; same as E108 {s['same_verdict_as_e108']}; X {s['cross_card']['aggregate']} {s['cross_card']['tally']}")
        if nm == "replicate":
            check("replicate: R1 PASS on the registered words", v["E108-R1"] == "PASS")
            check("replicate: R7 and R12 MOST", v["E108-R7"] == "MOST" and v["E108-R12"] == "MOST")
            check("replicate: R3 ALIKE, R4 ABSORBED HIGHER", v["E108-R3"] == "ALIKE" and v["E108-R4"] == "ABSORBED HIGHER")
            check("replicate: R8 RISES / RISES, R9 FALLS", v["E108-R8"] == "RISES / RISES" and v["E108-R9"] == "FALLS")
            check("replicate: R2, R11 and S1 PASS (the tie against E78's cells on aifoundry3)",
                  v["E108-R2"] == "PASS" and v["E108-R11"] == "PASS" and v["E108-S1"] == "PASS")
            check("replicate: at least 11 of E108's 13 verdicts come back", int(s["same_verdict_as_e108"].split()[0]) >= 11)
            check("replicate: cross-card aggregate PASS, no X rule FAILs",
                  s["cross_card"]["aggregate"] == "PASS" and s["cross_card"]["tally"].get("FAIL", 0) == 0)
        if nm == "no_location":
            check("no_location: R7 LITTLE", v["E108-R7"] == "LITTLE")
            check("no_location: R12 LITTLE", v["E108-R12"] == "LITTLE")
            check("no_location: X-fp32.share_het and X-fp32.share_het_z FAIL",
                  s["cross_card"]["rules"]["X-fp32.share_het"]["verdict"] == "FAIL"
                  and s["cross_card"]["rules"]["X-fp32.share_het_z"]["verdict"] == "FAIL")
            check("no_location: cross-card aggregate FAILs", s["cross_card"]["aggregate"] == "FAIL")
        if nm == "two":
            check("two passes: scored (R12 MOST)", v["E108-R12"] == "MOST" and s["cross_card"]["aggregate"] != "NOT SCORED")
        if nm == "one":
            pw = [r for r in v if r != "E108-R1"]
            check("one pass: every power rule NOT SCORED, R1 still scored",
                  all(v[r] == "NOT SCORED" for r in pw) and v["E108-R1"] == "PASS")
            check("one pass: cross-card NOT SCORED", s["cross_card"]["aggregate"] == "NOT SCORED")
    w = world("replicate")
    s = sc.score(w, as_rows(readback_rows(off_tile="fp32.c_mx_f")))
    check("read-back: one tile's words off reads R1 FAIL", s["rules"]["E108-R1"]["verdict"] == "FAIL")
    s = sc.score(w, as_rows(readback_rows(split_tile="fp32.b_B_z")))
    check("read-back: one minion disagreeing reads R1 UNREAD", s["rules"]["E108-R1"]["verdict"] == "UNREAD")
    s = sc.score(w, [])
    check("read-back: no reads at all reads R1 UNREAD", s["rules"]["E108-R1"]["verdict"] == "UNREAD")
    n_ok = sum(1 for _, ok in checks if ok)
    print(f"\n{n_ok} of {len(checks)} checks")
    sys.exit(0 if n_ok == len(checks) else 1)


if __name__ == "__main__":
    main()
