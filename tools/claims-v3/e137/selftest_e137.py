#!/usr/bin/env python3
"""E137 self-test, on the Intel, before the freeze; no card. Checks:
  A. the scorer on E128's committed primary reduction reproduces E128's per-pass shares exactly (fp16.share_het_m, share_walk_m, share_het_z,
     Bm_het, Bm_walk, Bz_rest), and with two passes every rule reads NOT SCORED (E137 needs four);
  B. synthetic worlds built from E128's per-pass D (five passes, each E128 pass plus a small offset): "located" (R1 MOST, R2 ALMOST NONE,
     R3 MOST, R4 ALIKE) and "other" (R1 ABOUT HALF, R2 SOME, R3 LITTLE, R4 MATCHED HIGHER);
  C. the set-aside rule: S1 with 4 kept; S2 restores a tie-only pass; S3 restores an fp32-anchor pass for fp16 items; a pass set aside by
     fp16.zeros or by failed runs is never restored; a quantity missing a tile in one pass uses the others (NOT SCORED below four);
  D. the stops: run_e137.guard_stops on a stub module ends with EXIT_HOT and writes STOP at board 68.0 W and at a shire 72.0 C, and passes 67.9 W /
     71.9 C;
  E. the desk reduction check's output file exists and reads max |diff| 0 (desk_reduce_check_e137.py, run before this).
Standard library only. Exit 0 if every check passes.

    python3 tools/claims-v3/e137/selftest_e137.py [<desk-reduce-check output>]
SPDX-License-Identifier: Apache-2.0
"""
import copy
import json
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_e137 as S  # noqa: E402

REG = json.load(open(S.REG))
E128 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-02-e128-fp16-signs/e128.json")))
SC128 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-02-e128-fp16-signs/scored.json")))
results = []


def check(name, cond, info=""):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (f"  [{info}]" if info else ""))


def red_from(pp, set_aside=(), cfg=()):
    return {"passes": sorted(int(p) for p in pp), "per_pass": {p: {it: {"D": d} for it, d in row.items()} for p, row in pp.items()},
            "passes_set_aside": list(set_aside), "passes_config_flags": list(cfg),
            "items": {c: {"D": {"mean": v["ref_w"]}} for c, v in REG["session_tie"]["cells"].items()}, "leak": {"mode": "0.2414"}}


def main():
    # A
    name, pp, _ = S.reading(E128, None, 4)
    res = S.score(REG, name, pp, 4, REG["e128_reference"]["quantities"])
    worst = 0.0
    for q in ("fp16.share_het_m", "fp16.share_walk_m", "fp16.share_het_z", "fp16.Bm_het", "fp16.Bm_walk", "fp16.Bz_rest"):
        for p, v in SC128["primary"]["quantities"][q]["per_pass"].items():
            worst = max(worst, abs(res["quantities"][q]["per_pass"][p] - v))
    check("A1 E128's per-pass shares reproduced", worst < 1e-4, f"max diff {worst:.2e}")
    check("A2 two passes: R1-R7 NOT SCORED", all(res["rules"][r]["verdict"] == "NOT SCORED" for r in
                                                 ("E137-R1", "E137-R2", "E137-R3", "E137-R4", "E137-R5", "E137-R6", "E137-R7")))
    base = {p: {it: v["D"] for it, v in row.items() if isinstance(v, dict) and v.get("D") is not None} for p, row in E128["per_pass"].items()}
    b0 = base["12810"]

    def world(f):
        out = {}
        for i in range(5):
            row = dict(b0)
            f(row, i)
            out[str(13710 + i)] = row
        return out

    # B located: matched held = walk (sums changing ~0), E108's design held ~ walk
    def located(row, i):
        e = (i - 2) * 0.02
        row["fp16.z_s"] = 10.2 + e
        row["fp16.b_B_zm"] = 13.4 + e
        row["fp16.b_B_wm"] = 13.42 + e + (i % 2) * 0.02
        row["fp16.b_B_z"] = 13.6 + e
        row["fp16.b_B_w"] = 13.62 + e
        row["fp16.signs"] = 12.9 + e
        row["fp16.ones"] = 8.1
    r = S.score(REG, "S1", world(located), 4, REG["e128_reference"]["quantities"])
    v = {k: r["rules"][k]["verdict"] for k in r["rules"]}
    check("B1 located world", v["E137-R1"] == "MOST" and v["E137-R2"] == "ALMOST NONE" and v["E137-R3"] == "MOST" and v["E137-R4"] == "ALIKE"
          and v["E137-R5"] == "PASS", v)

    def other(row, i):
        e = (i - 2) * 0.02
        row["fp16.z_s"] = 10.2 + e
        row["fp16.b_B_zm"] = 11.7 + e
        row["fp16.b_B_wm"] = 13.2 + e
        row["fp16.b_B_z"] = 10.4 + e
        row["fp16.b_B_w"] = 13.2 + e
        row["fp16.signs"] = 15.5 + e
    r = S.score(REG, "S1", world(other), 4, REG["e128_reference"]["quantities"])
    v = {k: r["rules"][k]["verdict"] for k in r["rules"]}
    check("B2 other world", v["E137-R1"] == "ABOUT HALF" and v["E137-R2"] == "SOME" and v["E137-R3"] == "LITTLE" and v["E137-R4"] == "MATCHED HIGHER"
          and v["E137-R5"] == "FAIL", v)
    # C set-aside
    w = world(located)
    four = {p: w[p] for p in list(w)[:4]}
    nm, _, _ = S.reading(red_from(four), None, 4)
    check("C1 S1 with four kept", nm == "S1")
    three = {p: w[p] for p in list(w)[:3]}
    rel = red_from(w)
    prim = red_from(three, set_aside=[{"pass": 13713, "why": ["anchor_pi drifts +0.700 W"]},
                                      {"pass": 13714, "why": ["fp16.zeros departs +0.300 W from its straight line"]}])
    nm, pp, notes = S.reading(prim, rel, 4)
    check("C2 S2 restores the tie-only pass, never the fp16-anchor pass", nm == "S2" and "13713" in pp and "13714" not in pp, notes)
    prim = red_from(three, set_aside=[{"pass": 13713, "why": ["fp32.randn spans 1.102 W"]},
                                      {"pass": 13714, "why": ["3 runs failed a gate"]}])
    nm, pp, notes = S.reading(prim, rel, 4)
    check("C3 S3 restores an fp32-anchor pass for fp16 items only; failed runs never", nm == "S3" and "13713" in pp and "13714" not in pp
          and all(k.startswith("fp16.") for k in pp["13713"]), notes)
    prim = red_from(three, set_aside=[{"pass": 13713, "why": ["anchor_pi drifts +0.700 W"]}],
                    cfg=[{"pass": 13713}])
    nm, pp, notes = S.reading(prim, rel, 4)
    check("C4 a config-flagged pass is never restored", "13713" not in pp, notes)
    w5 = copy.deepcopy(w)
    del w5["13711"]["fp16.signs"]
    r = S.score(REG, "S1", w5, 4, None)
    check("C5 a skipped tile leaves its pass out of that quantity only", r["quantities"]["fp16.step"]["n"] == 4
          and r["quantities"]["fp16.share_het_m"]["n"] == 5 and r["rules"]["E137-R5"]["verdict"] != "NOT SCORED")
    del w5["13712"]["fp16.signs"]
    r = S.score(REG, "S1", w5, 4, None)
    check("C6 below four passes for a quantity: its rule NOT SCORED", r["rules"]["E137-R5"]["verdict"] == "NOT SCORED"
          and r["rules"]["E137-R1"]["verdict"] != "NOT SCORED")
    # D stops
    import run_e137 as R
    for line, hot in (({"board_w": 68.0, "temp_c": {"minshire": [60, 61]}}, True), ({"board_w": 60.0, "temp_c": {"minshire": [60, 72.0]}}, True),
                      ({"board_w": 67.9, "temp_c": {"minshire": [71.9, 70]}}, False)):
        stub = types.SimpleNamespace(EXIT_HOT=6, last_sample=lambda path, line=line: line)
        td = tempfile.mkdtemp()
        g = R.guard_stops(stub, REG["stops"]["board_w"], REG["stops"]["die_hottest_shire_c"], td)
        try:
            g("x")
            code = None
        except SystemExit as e:
            code = e.code
        stopped = os.path.exists(os.path.join(td, "STOP"))
        check(f"D stop at {line}", (code == 6 and stopped) if hot else (code is None and not stopped), f"exit {code}, STOP {stopped}")
    # E
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        t = open(sys.argv[1]).read()
        check("E desk reduction check: max |diff| 0", "DESK-REDUCE-CHECK: 19 fp16 per-pass D values compared, max |diff| 0.000e+00 W" in t)
    n_ok = sum(1 for _, ok in results if ok)
    print(f"SELFTEST {n_ok} of {len(results)} checks pass")
    sys.exit(0 if n_ok == len(results) else 1)


if __name__ == "__main__":
    main()
