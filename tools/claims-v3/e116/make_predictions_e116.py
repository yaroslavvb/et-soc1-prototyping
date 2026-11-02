#!/usr/bin/env python3
"""E116 (Q133): freeze the predictions and the read-back's expected words before the claim. Desk compute, standard
library only. It writes predictions-e116.json and expect-e116.json beside itself.

    python3 tools/claims-v3/e116/make_predictions_e116.py <accum dir>

<accum dir> holds <tile>/accum_199874.bin for each of E88's 22 tiles: what accum.c (rtl-sim/fma_toggle_v2/accum.c, the
RTL's arithmetic: E104's reading, which equalled all 110 of E104's reads on aifoundry1 card 1) holds after n = 199,874
ops, written by `build/e102-accum/accum <type> <tile> 199874`. n is E104's length, so the seven tiles E104 read at
199,874 on card 1 can be compared word for word across the two cards.

What it freezes (every number is read from a committed file, named in `sources`):
  - E88's reference (aifoundry1 card 1, 31 Oct): the three parts per format in watts and as shares, the 19 contrasts
    and the 32 registered verdicts, from docs/reports/data/2026-10-31-e88-result-path/scored.json;
  - E82's per-format card scale D(aifoundry3) / D(card 1): fp32 1.030, fp16 1.033, int8 1.027 (scored.json
    cross_card.primary.x3.per_type_median), which carries E88's watts to this card;
  - E78's anchors on aifoundry3 (31 Oct), for the session tie;
  - the rules, the bands and what I expect.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
N = 199874
E88_SCORED = "docs/reports/data/2026-10-31-e88-result-path/scored.json"
E82_SCORED = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/scored.json"
E78_RED = "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json"
E104_SPEC = "tools/claims-v3/kinds/e104/e104.json"
E88_SPEC = "tools/claims-v3/rpath/e88.json"
PARTS = ("i_clocked_lane", "iii_operand_multiplier", "ii_result_path")
# What each design does with its result, as E88 designed it (make_e88.py --check, e88.json checks) and as E104 read
# fp16's r_abs on card 1 (it walks one unit a micro-op). For the record only: the read-back rule tests the words.
DOES = {
    "fp32.c_abs": "holds: a 2^100 product at k = 0 absorbs every later product (C = n x 2^100)",
    "fp32.r_abs": "holds: absorbed, random positive operands (C = n x 2^100)",
    "fp32.r_het": "holds per accumulator, the accumulators differ (k = 0 B row 2^50 m_j)",
    "fp32.s_abs": "holds: absorbed, +-1 operands (C = n x 2^100)",
    "fp32.r_walk": "walks: the same operands as r_abs, k = 0 slice 1.0",
    "fp32.s_walk": "walks: +-1 operands",
    "fp16.c_cancel": "holds at 0: each micro-op's dot product cancels exactly",
    "fp16.r_cancel": "holds at 0: paired values cancel exactly",
    "fp16.r_abs": "walks one unit a micro-op (E104 on card 1: fp16 truncates each aligned product separately)",
    "fp16.r_walk": "walks",
    "int8.c_cancel": "holds at 0: each micro-op's dot product cancels exactly",
    "int8.r_cancel": "holds at 0: paired bytes cancel exactly",
    "int8.r_walk": "walks (int32, wraps)",
}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    acc = sys.argv[1]
    e88 = json.load(open(os.path.join(ROOT, E88_SPEC)))
    e104 = json.load(open(os.path.join(ROOT, E104_SPEC)))
    tiles = {}
    for name, v in e88["items"].items():
        raw = open(os.path.join(acc, name, f"accum_{N}.bin"), "rb").read()
        assert len(raw) == 1024, name
        words = [raw[i:i + 4][::-1].hex() for i in range(0, 1024, 4)]
        t = {"type": v["type"], "kind": v["kind"], "file": v["file"], "sha256": v["sha256"], "n": N,
             "accum_sha256": hashlib.sha256(raw).hexdigest(), "accum_hex": raw.hex(),
             "distinct_words": len(set(words)), "c00": words[0], "c08": words[8],
             "does": DOES.get(name, {"zeros": "holds at 0 (every lane gated)"}.get(v["kind"], "walks (anchor)"))}
        e = e104["tiles"].get(name)
        if e and e["sha256"] == v["sha256"] and str(N) in e.get("read", {}):
            t["e104_card1"] = {"read_at": N, "rtl_hex_equal": e["read"][str(N)].get("rtl_hex", "") == raw.hex(),
                               "note": "E104 read this tile at this n on aifoundry1 card 1, and every read equalled accum.c"}
        tiles[name] = t
    expect = {"experiment": "E116", "what": "accum.c's C after n ops for each of E88's 22 tiles, frozen before the claim",
              "accum": "rtl-sim/fma_toggle_v2/accum.c via build/e102-accum/accum (E102/E104's)", "n": N, "tiles": tiles}
    json.dump(expect, open(os.path.join(HERE, "expect-e116.json"), "w"), indent=1)

    s88 = json.load(open(os.path.join(ROOT, E88_SCORED)))["primary"]
    x3 = json.load(open(os.path.join(ROOT, E82_SCORED)))["cross_card"]["primary"]["x3"]["per_type_median"]
    e78 = json.load(open(os.path.join(ROOT, E78_RED)))["items"]
    ref = {"splits": {}, "contrasts": {}, "verdicts": {k: v["verdict"] for k, v in s88["rules"].items()}}
    for f, sp in s88["splits"].items():
        ref["splits"][f] = {"total": {"mean": sp["total"]["mean"], "ci95": sp["total"]["ci95"]},
                            "D": {p: {"mean": sp["parts"][p]["D"]["mean"], "ci95": sp["parts"][p]["D"]["ci95"]} for p in PARTS},
                            "shares": {p: {"mean": sp["shares"][p]["mean"], "ci95": sp["shares"][p]["ci95"]} for p in PARTS}}
    for c, v in s88["contrasts"].items():
        ref["contrasts"][c] = {"a": v["a"], "b": v["b"], "D": v["D"]["mean"], "ci95": v["D"]["ci95"]}
    scale = {f: round(x3[f], 4) for f in ("fp32", "fp16", "int8")}
    carried = {f: {p: round(ref["splits"][f]["D"][p]["mean"] * scale[f], 4) for p in PARTS} for f in scale}
    tie = {k: {"D": round(e78[k]["D"]["mean"], 4), "ci95": round(e78[k]["D"]["ci95"], 4)}
           for k in ("fp32.randn", "fp16.randn", "int8.full", "fp32.ones", "fp16.ones", "int8.ones", "anchor_pi")}
    pred = {
        "experiment": "E116",
        "registered": "Sun 1 Nov 2026, before the claim (the commit time is the registration time)",
        "registration": "tools/claims-v3/e116/E116.md",
        "card": {"name": "aifoundry3", "clock_mhz": 600, "config_expected": {"tdp_w": 0, "temp_threshold_c": 65},
                 "note": "E78's own aifoundry3 gate in reduce_e78.py; reduce_e88.py's card-1 substitution never fires here"},
        "sources": {E88_SCORED: sha(os.path.join(ROOT, E88_SCORED)), E82_SCORED: sha(os.path.join(ROOT, E82_SCORED)),
                    E78_RED: sha(os.path.join(ROOT, E78_RED)), E104_SPEC: sha(os.path.join(ROOT, E104_SPEC)),
                    E88_SPEC: sha(os.path.join(ROOT, E88_SPEC))},
        "reference_e88_card1": ref,
        "card_scale_e82": {"value": scale, "what": "D(aifoundry3) / D(aifoundry1 card 1), median over kinds >= 5 W, per format"},
        "carried_W": carried,
        "tie_e78_aifoundry3": tie,
        "rules": {
            "E116-R0": {"what": "every read equals accum.c's 256 words on all 1,024 minions (22 tiles, n = 199,874)",
                        "PASS": "22 of 22 reads equal", "FAIL": "any read differs on any word of any minion",
                        "not scored": "fewer than 22 reads ran: the reads that ran are reported"},
            "E116-S": {"what": "per format, the three parts' shares of the r_walk total, per pass, against E88's (card 1)",
                       "band": {"fp32": 0.04, "fp16": 0.04, "int8": 0.08},
                       "PASS": "all three |share - E88's share| <= band",
                       "FAIL": "any part's |difference| exceeds the band by more than its 95% half-width",
                       "INCONCLUSIVE": "otherwise"},
            "E116-W": {"what": "per format, the three parts' watts against E88's x E82's card scale",
                       "band": "max(0.6 W, 12% of the carried value)",
                       "PASS": "all three inside", "FAIL": "any part's 95% interval lies wholly outside its band",
                       "INCONCLUSIVE": "otherwise"},
            "E116-H": {"what": "E88's 13 mechanism rules (H1-H6), scored by score_e88.py unchanged on E116's reduction",
                       "PASS": "13 of 13 give E88's card-1 verdict", "FAIL": "2 or more differ", "INCONCLUSIVE": "one differs"},
            "E116-P": {"what": "E88's 19 frozen model bands, scored by score_e88.py unchanged (card 1's bands, no scale)",
                       "reported": "the tally and each verdict against E88's; no pass/fail of its own"},
            "E116-T": {"what": "the session tie: fp32.randn, fp16.randn, int8.full against E78 on aifoundry3 (31 Oct)",
                       "PASS": "each within max(0.4 W, 3%)", "FAIL": "any 95% interval wholly outside that band",
                       "INCONCLUSIVE": "otherwise"},
            "min_passes": 4,
            "fewer_passes": "fewer than 4 kept passes: E116-S, -W, -H, -P and -T are not scored (reported as exploratory)",
        },
        "expected": {"E116-R0": "PASS", "E116-S": {"fp32": "PASS", "fp16": "PASS", "int8": "PASS"},
                     "E116-W": {"fp32": "PASS", "fp16": "PASS", "int8": "PASS"},
                     "E116-H": "PASS (13 of 13; H4-signs-mult FAILS again, as on card 1)",
                     "E116-P": "18 of 19 PASS: P-M32s FAILS as on card 1; P-R32s, which missed its band by 0.003 W on card 1, passes once the 3% scale lifts it",
                     "E116-T": "PASS"},
        "primary": {"reduction": "reduce_e88.py unchanged (reduce_e78.py unchanged inside it), dips removed, leakage slope auto",
                    "arms": ["dips kept", "leak 0.545", "leak 0.3803", "leak 0"], "min_passes": 4},
        "budget": {"card_minutes_max": 40, "queue_budget_min": 34, "passes_planned": "11610.. (up to 6; the queue's budget rule stops it)",
                   "deadline_local": "18:55 PST"},
    }
    files = {}
    for rel in ("tools/claims-v3/lib.sh", "tools/claims-v3/kinds/run_e78.py", "tools/claims-v3/kinds/reduce_e78.py",
                "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/kinds.json",
                "tools/claims-v3/kinds/patch_host_e104.py", "rtl-sim/fma_toggle_v2/accum.c"):
        files[rel] = sha(os.path.join(ROOT, rel))
    for d in ("tools/claims-v3/rpath",):
        for dp, _, fs in os.walk(os.path.join(ROOT, d)):
            if "__pycache__" in dp:
                continue
            for f in sorted(fs):
                p = os.path.join(dp, f)
                files[os.path.relpath(p, ROOT)] = sha(p)
    pred["harness"] = {"reused_unchanged_sha256": files}
    json.dump(pred, open(os.path.join(HERE, "predictions-e116.json"), "w"), indent=1)
    print("wrote predictions-e116.json and expect-e116.json;", len(tiles), "tiles;", "scale", scale)
    for f in carried:
        print(" carried", f, carried[f])


if __name__ == "__main__":
    main()
