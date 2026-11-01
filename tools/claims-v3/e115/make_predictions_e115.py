#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E115 (Q133): write predictions-e115.json, E115's freeze, from committed sources only - every number read from its
file, never retyped - before E115's claim and before any card has run a tile of blind pool 3.

    python3 tools/claims-v3/e115/make_predictions_e115.py

What it freezes:
  - Q133(b)'s files by sha256, each checked against the value Q133(b) published (the pool a9167033; M5, the counts and the
    predictions 64b4124e; the contrasts' intervals 0fae735f): E115 refuses to run, reduce or score on any difference;
  - E78's card code by sha256 (E78's freeze values, as E86-E103 ran it) and E115's own files;
  - every tile's frozen M5 and M4 prediction on aifoundry3's footing (a3), copied from predictions-blind3.json, and its
    ratio to its type's random anchor;
  - F0r, a comparator E115 adds: M4's own float form refitted on Q133(b)'s 283 rows, priced with the full-fit constants
    Q133(b) committed in loko.json (`coef_fJ_fit_on_all_by_form.F0_M4`) and the bench counts it committed, through
    Q133(b)'s own feature code (fit_m5.py); checked by reproducing M5's frozen a3 predictions with the same code. It
    isolates the per-format term (M5 against F0r) from the refit (F0r against M4). Reported, never a verdict;
  - the seven contrasts and their frozen 95% intervals, copied from contrasts-blind3.json;
  - the decision rules, their thresholds, and the reference errors behind R1 and R2 (M5's nested leave-one-kind-out
    errors, copied from loko.json), with the intervals for the planned tile sets computed now by score_e115.rms_interval;
  - the session tie's cells (E78's own D, from e78.json) and bands (E95's), the plan, the budget and the arms.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e115_common as e115  # noqa: E402
import score_e115 as S  # noqa: E402

Q = os.path.join(ROOT, "docs", "reports", "data", "2026-11-01-q133b-power-model")
sys.path.insert(0, Q)
import fit_m5 as F  # noqa: E402  (Q133(b)'s feature code, read only)

POOL = e115.POOL_DIR
A3_EXPS = ("E78", "E86", "E90", "E92", "E95")      # the float and int8 rows measured on aifoundry3 card 0 (their READMEs' titles)
ANCHOR = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rel(p):
    return os.path.relpath(p, ROOT)


# Q133(b)'s files with the sha256 it published (its README, its result, and the pool's README), checked here.
PUBLISHED = {
    "tools/claims-v3/kinds/blind3/blind3.json": "60dfbf12a10fc3f464eb1225261954b466a6209d746fa91d1c9218b146786f88",
    "tools/claims-v3/kinds/blind3/SHA256SUMS": "d100a9c7bd4d3fa5d4516377b8962da79cc54ad13a78bac4fa2efc67a654d1db",
    "tools/claims-v3/kinds/blind3/make_blind3.py": "e17a2c32310698f5571def8ddc68d0547b4e90e6a977cb57ccce280a7af34956",
    "tools/claims-v3/kinds/blind3/predictions-blind3.json": "5f28091a2878d5167aa4402286a1419cca2b78ebe4fbc0b3f34bda35a31f925a",
    "tools/claims-v3/kinds/blind3/counts-blind3.json": "428d0a3815ae66e7be84312e21a8763f276f2a1e8483dd5b17b27e823595684b",
    "tools/claims-v3/kinds/blind3/contrasts-blind3.json": "399128b9ff83f1a357e6c20cdfd359f11eeb2a7d1d6415516e63cbae4a628578",
    "docs/reports/data/2026-11-01-q133b-power-model/m5.json": "c19f2c7bc098b5a8969694b6563784d57bf88e7336fe97ac2afe769b0c63e2da",
    "docs/reports/data/2026-11-01-q133b-power-model/fit_m5.py": "e02116913042291bac41a4431bf880f00a4249bddf50c649c66feb267d77decb",
    "docs/reports/data/2026-11-01-q133b-power-model/predict_blind3.py": "a1877bac4e1ec7e501438504dac06a44762171790e6fe3757cd9095f71c41367",
    "docs/reports/data/2026-11-01-q133b-power-model/contrasts_blind3.py": "7f82fbbafb8daa2aff64aabb137c9a1ba8d9e48e496d1a3cc3f05fec928b8269",
}
# read and recorded by sha256 (Q133(b) committed them in 64b4124e / 0fae735f without publishing a hash)
RECORDED = ("docs/reports/data/2026-11-01-q133b-power-model/loko.json",
            "docs/reports/data/2026-11-01-q133b-power-model/corrections-check.txt",
            "docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json",
            "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json")
# E78's card code, unchanged since E78's freeze (the values E86, E90, E92, E95 and E103 checked)
REUSED = {
    "tools/claims-v3/lib.sh": "033d07762548c4abad0bb1721d338bb2333e58d6f07bc0d9a93bdcac0301eaaa",
    "tools/claims-v3/kinds/e78_common.py": "c58923a522849ea033a2d14b7981b0589bcd8a1d5c3129e608d3a418578a552e",
    "tools/claims-v3/kinds/run_e78.py": "f3efd7838686dbd158c8f45a82ab59f4beda68479d792d73a36265e48784bb73",
    "tools/claims-v3/kinds/reduce_e78.py": "6a158ceedc000fae884762d7e273231bfd4e4f42c09bf0b0723afc2da6c05d39",
    "tools/claims-v3/kinds/kinds.json": "9586568f23a97757e34b3cdacdffe5bee0122d236e28a9f76f06e8598b7b1337",
}
E115_FILES = ("e115_common.py", "run_e115.py", "block_e115.sh", "queue_e115.sh", "run_e115.sh", "reduce_e115.py",
              "score_e115.py", "collect_e115.sh", "selftest_e115.py", "make_predictions_e115.py")


def main():
    bad = []
    for r_, want in {**PUBLISHED, **REUSED}.items():
        have = sha(os.path.join(ROOT, r_))
        if have != want:
            bad.append(f"{r_}: {have} != {want}")
    if bad:
        raise SystemExit("a frozen input differs from its published sha256:\n  " + "\n  ".join(bad))
    pred = json.load(open(os.path.join(POOL, "predictions-blind3.json")))
    cont = json.load(open(os.path.join(POOL, "contrasts-blind3.json")))
    spec = json.load(open(e115.POOL_JSON))
    m5 = json.load(open(os.path.join(Q, "m5.json")))
    loko = json.load(open(os.path.join(Q, "loko.json")))

    # ---- F0r: M4's form refitted on all 283 float rows, through Q133(b)'s own feature code; M5 reproduced first
    zc = F.load(os.path.join(F.B, "counts-v2.json"))["rows"]
    zeros = {t: zc[f"{t}.zeros"]["mean"] for t in F.CPO}
    cb = F.load(os.path.join(POOL, "counts-blind3.json"))["rows"]
    bF0 = loko["families"]["float"]["coef_fJ_fit_on_all_by_form"]["F0_M4"]
    terms_F0 = F.FORMS["float"]["F0_M4"]
    b_F0 = np.array([bF0[q] for q in terms_F0]) * 1e-15
    M5f = m5["families"]["float"]
    b_M5, terms_M5 = np.array(M5f["coef_J"]), M5f["terms"]

    def point(name, t, b, terms):
        f = F.fmt_feats(F.bench_feats(cb[name]["mean"] if name in cb else zc[name]["mean"], zeros[t]), t)
        return float(np.array([F.RATE[t] * f[q] for q in terms]) @ b)

    repro = 0.0
    for name, v in pred["tiles"].items():
        if v["type"] != "int8":
            repro = max(repro, abs(point(name, v["type"], b_M5, terms_M5) - v["M5"]["a3"]["D_w"]))
    if repro > 1e-9:
        raise SystemExit(f"M5's frozen a3 predictions not reproduced through fit_m5's features: {repro}")
    f0r_anchor = {a: point(a, a.split(".")[0], b_F0, terms_F0) for t, a in ANCHOR.items() if t != "int8"}

    # ---- the tiles
    tiles = {}
    for name in e115.E115_NAMES:
        v = pred["tiles"][name]
        t = v["type"]
        rec = {"type": t, "kind": v["kind"], "open_case": v["open_case"], "priority": v["priority"], "group": v["group"],
               "sha256": v["sha256"], "anchor": ANCHOR[t], "gate_closes": v["gate_closes"]}
        for w in ("M5", "M4"):
            a3 = v[w]["a3"]
            rec[w] = {"D_w": a3["D_w"], "half95": a3["half95"], "lo95": a3["lo95"], "hi95": a3["hi95"],
                      "ratio_to_anchor": v[w]["ratio_to_anchor"], "terms": v[w]["terms"], "terms_w_a3": v[w]["terms_w_a3"]}
        if t != "int8":
            rec["F0r"] = {"D_w": point(name, t, b_F0, terms_F0), "what": "M4's form refitted on Q133(b)'s 283 rows (E115's comparator)"}
        else:
            rec["F0r"] = {"D_w": v["M5"]["a3"]["D_w"], "what": "int8: M5's own int8 (I3 refitted), which F0r's int8 would be"}
        mm = v.get("check_mismatch_words") or 0
        if mm:
            rec["flag"] = (f"its bench count carries fp16's window-model residue: {mm:g} of 256 accumulator words differ from "
                           "software at each launch point (predictions-blind3.json check_mismatch_words)")
        tiles[name] = rec

    # ---- the contrasts
    reads = {
        "fp32.m_blines_eq - fp32.m_bpair_eq": {
            "BELOW": "fits a cost for B lines that change (m_bpair_eq's B lines change 3,552 bits an op, m_blines_eq's 0), "
                     "or compute the bench misprices",
            "ABOVE": "fits a cost for B half-lines that change (m_blines_eq 3,680 bits an op against m_bpair_eq's 1,776), "
                     "or compute the bench misprices",
            "INSIDE": "no memory-path term beyond the bench's compute and bus, at this interval's resolution"},
    }
    contrasts = []
    for c in cont["contrasts"]:
        nm = c["contrast"]
        contrasts.append({
            "name": nm, "plus": c["plus"], "minus": c["minus"], "type": c["type"], "isolates": c["isolates"],
            "anchor": ANCHOR[c["type"]], "priorities": c["priorities"],
            "M5": {k: c["M5"]["a3"][k] for k in ("D_w", "half95", "lo95", "hi95")},
            "M4": {k: c["M4"]["a3"][k] for k in ("D_w", "half95", "lo95", "hi95")},
            "M5_terms_w_a3": c.get("M5_terms_w_a3"),
            "how_to_read": reads.get(nm, {"BELOW": "the plus tile costs less against the minus tile than M5 says",
                                          "ABOVE": "the plus tile costs more against the minus tile than M5 says",
                                          "INSIDE": "as M5 says, at this interval's resolution"}),
        })

    # ---- the reference errors (M5's nested leave-one-kind-out errors) and the planned sets' intervals
    fe = loko["families"]["float"]["row_errors"]
    ie = loko["families"]["int8"]["row_errors"]
    ref_f = {t: [round(r["nested_err_w"], 6) for r in fe if r["key"].startswith(t + ".")] for t in ("fp32", "fp16")}
    ref_f_a3 = {t: [round(r["nested_err_w"], 6) for r in fe if r["key"].startswith(t + ".") and r["exp"] in A3_EXPS] for t in ("fp32", "fp16")}
    ref_i = {"int8": [round(r["nested_err_w"], 6) for r in ie]}
    ref_i_a3 = {"int8": [round(r["nested_err_w"], 6) for r in ie if r["exp"] in A3_EXPS]}
    txt = open(os.path.join(Q, "corrections-check.txt")).read()

    def pop(label):
        m = re.search(label + r"\s*: nested rms ([0-9.]+) W, 95% bootstrap over \d+ kinds \(10,000, seed 7\) \[([0-9.]+), ([0-9.]+)\]", txt)
        return [float(m.group(2)), float(m.group(3))], float(m.group(1))

    pop_f, rms_f = pop("floats")
    pop_i, rms_i = pop("int8")
    DRAWS, SEED = 100000, 11500
    p1f = {t: sum(1 for n in e115.E115_NAMES if tiles[n]["type"] == t and tiles[n]["priority"] == 1) for t in ("fp32", "fp16")}
    alli = {"int8": sum(1 for n in e115.E115_NAMES if tiles[n]["type"] == "int8")}
    p1i = {"int8": sum(1 for n in e115.E115_NAMES if tiles[n]["type"] == "int8" and tiles[n]["priority"] == 1)}
    iv_r1 = S.rms_interval(ref_f, p1f, DRAWS, SEED)
    iv_r1_a3 = S.rms_interval(ref_f_a3, p1f, DRAWS, SEED)
    iv_r2 = S.rms_interval(ref_i, alli, DRAWS, SEED)
    iv_r2_p1 = S.rms_interval(ref_i, p1i, DRAWS, SEED)
    iv_r2_a3 = S.rms_interval(ref_i_a3, alli, DRAWS, SEED)

    e78 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json")))
    tie = {c: {"ref_w": e78["items"][c]["D"]["mean"], "ref_ci95_w": e78["items"][c]["D"]["ci95"], "band_w": b, "ref": "E78",
               "source": f"docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json items.{c}.D.mean"}
           for c, b in (("fp32.randn", 0.5), ("fp16.randn", 0.5), ("anchor_pi", 0.5), ("int8.full", 0.25))}

    out = {
        "experiment": "E115",
        "title": "E115: blind pool 3 on the card - the power model M5 (and M4) against 25 tiles written before the model was read (Q133, aifoundry3 card 0, 600 MHz)",
        "request": "Q133 (Sun 1 Nov 2026): kinds page section 11 item 6, a power model across kinds",
        "answers": "https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open item 6",
        "date": "2026-11-01",
        "registration": "tools/claims-v3/e115/README.md",
        "card": "aifoundry3 card 0 (no V3_DEVICE), 600 MHz pinned; TDP 0 W / threshold 65 C read, never set",
        "frozen_inputs": {
            **{r_: {"sha256": w, "checked_against": "the value Q133(b) published"} for r_, w in PUBLISHED.items()},
            **{r_: {"sha256": sha(os.path.join(ROOT, r_)), "checked_against": "recorded here"} for r_ in RECORDED},
        },
        "harness": {
            "reused_unchanged_sha256": REUSED,
            "frozen_pool_sha256": {**e115.FROZEN, **{f"tools/claims-v3/kinds/blind3/{spec['tiles'][n]['file']}": spec["tiles"][n]["sha256"]
                                                      for n in e115.E115_NAMES}},
            "e115_files_sha256": {f"tools/claims-v3/e115/{f}": sha(os.path.join(HERE, f)) for f in E115_FILES},
            "binary": "build/sparsity/host/sparsity_host in aifoundry3's ~/aifoundry (26 Sep 06:15), the one E67-E95 ran; no rebuild",
        },
        "plan": {
            "passes": [11510, 11511, 11512], "smoke": 11501, "smoke_items": list(e115.SMOKE_ITEMS),
            "runs_per_pass": 45, "burn_in_runs": 2, "min_kept_passes_scored": 2, "min_tile_passes": 2,
            "order": "Random('E115|aifoundry3|<pass>'): the 25 tiles dealt into three segments of 9, 8, 8, each with E78's six anchors, reshuffled; the tie first and last",
            "items_per_pass": "the tie twice, E78's six anchors three times, every one of the 25 pool tiles once (priority 1 and 2: the window holds all 25)",
            "bootstrap": {"draws": 10000, "seed": SEED},
            "data": "build/claims-v3/aifoundry3/kinds/p115<nn>/ on aifoundry3; results docs/reports/data/2026-11-01-e115-blind-pool/",
        },
        "card_budget": {
            "max_card_minutes": 30, "from": "the session-start config read (the smoke block's) to the session-end read",
            "queue_budget_s": 1590, "first_pass_estimate_s": 480, "pass_deadline": "2026-11-01 18:50 PST",
            "no_session_starts_after": "2026-11-01 18:00 PST", "every_run_ends_by": "2026-11-01 19:00 PST",
            "expected": "smoke ~1 min, then three passes of ~7.5 min (47 launches at E92's and E95's 9.3-10.2 s) with 15 s between: ~24 card-minutes",
        },
        "leakage": {"primary": "auto (E78's estimator on E115's own runs, as E86-E95 on this card)", "arms": [0.1994, 0.3803, 0]},
        "arms": {
            "dips_removed": "reduce_e115.py --drop-dips: E82 A2's dips removed; always reported; the reading reported if the primary keeps fewer than 2 passes",
            "gates_off": "reduce_e115.py --gates-off: E78's pass gates opened, every per-run gate kept; reported only",
            "leak": "0.1994 (E78's slope), 0.3803 (E71's idle slope), 0: reported; a verdict that moves is marked arm-sensitive",
            "anchor_footing": "every prediction times the session's measured anchor D over the model's predicted anchor D (predictions-blind3.json's ratio footing); reported; a verdict that differs is marked footing-sensitive",
        },
        "anchors_predicted_a3_w": pred["anchors_predicted_a3_w"],
        "F0r": {"coef_fJ": bF0, "terms": terms_F0, "source": "docs/reports/data/2026-11-01-q133b-power-model/loko.json families.float.coef_fJ_fit_on_all_by_form.F0_M4",
                "anchors_a3_w": f0r_anchor, "M5_reproduced_max_abs_w": repro,
                "what": "M4's float form (core, bus, rest, clk) refitted on Q133(b)'s 283 rows with no per-format term; computed here before any card ran a pool tile; a comparator, never a verdict"},
        "tiles": tiles,
        "contrasts": contrasts,
        "rules": {
            "E115-R1": {"what": "the float family: rms(D - M5) over the priority-1 float tiles, a3 footing",
                        "set": "type fp32 or fp16, priority 1 (16 tiles if all run)", "min_tiles": 5,
                        "verdict": "PASS if rms <= the interval's upper bound (inside, or below it: then better than the nested score says); FAIL if above",
                        "interval": "the 2.5-97.5% range of the rms of the set's format mix drawn with replacement from M5's nested leave-one-kind-out float errors of that format (both cards), 100,000 draws, seed 11500, recomputed for the tiles that ran",
                        "planned_interval": iv_r1, "reference_errors_w": ref_f, "reference_errors_a3_w": ref_f_a3,
                        "reported_a3_only_planned_interval": iv_r1_a3,
                        "population_interval_w": pop_f, "population_rms_w": rms_f,
                        "population_source": "docs/reports/data/2026-11-01-q133b-power-model/corrections-check.txt C7 (floats); for 283 rows, reported beside, never the verdict",
                        "draws": DRAWS, "seed": SEED,
                        "reported_without": [n for n in e115.E115_NAMES if tiles[n].get("flag")]},
            "E115-R2": {"what": "the int8 family: rms(D - M5) over the int8 tiles, a3 footing", "set": "type int8, priorities 1 and 2 (6 tiles if all run)",
                        "min_tiles": 3, "verdict": "PASS if rms <= the interval's upper bound; FAIL if above",
                        "interval": "as R1, from M5's 78 nested int8 errors", "planned_interval": iv_r2,
                        "planned_interval_priority1_only": iv_r2_p1, "reference_errors_w": ref_i, "reference_errors_a3_w": ref_i_a3,
                        "reported_a3_only_planned_interval": iv_r2_a3,
                        "population_interval_w": pop_i, "population_rms_w": rms_i, "draws": DRAWS, "seed": SEED},
            "E115-R3": {"what": "coverage: the share of every tile that ran whose D lies inside M5's frozen 95% interval (a3)",
                        "pass_at_least": 0.80, "fail_below": 0.60, "else": "INCONCLUSIVE"},
            "E115-R4": {"what": "the contrasts: the share of the seven whose measured value (D(plus) - D(minus) in each kept pass, averaged) lies inside contrasts-blind3.json's M5 a3 interval",
                        "pass_at_least": 0.85, "fail_below": 0.65, "min_contrasts": 5, "else": "INCONCLUSIVE; each contrast INSIDE, BELOW or ABOVE"},
            "E115-R5": {"what": "M5 against M4 as frozen: rms(D - M4) - rms(D - M5) over the priority-1 float tiles, paired bootstrap over tiles",
                        "min_tiles": 5, "verdict": "M5 BETTER if the 95% interval is above 0; M4 BETTER if below; else UNRESOLVED"},
            "E115-S1": {"what": "the session tie against E78 (E95's bands); reported, never a verdict on the model"},
        },
        "session_tie": {"cells": tie},
        "reported": [
            "per format (fp32, fp16 priority 1 and all; int8): rms and bias of M5, M4 and F0r",
            "per open case: n, mean D - M5 with its 95% interval over tiles, rms of M5 and M4, how many inside",
            "the per-format term: M5 against F0r (paired bootstrap over the priority-1 float tiles), and the refit: F0r against M4; on the fp16 tiles apart",
            "int8: M5 (I3 refitted) against M4 (I3 as frozen)",
            "R1 without the flagged tile (fp16.s_wpair0), R1 against the a3-only interval and against the 283-row population interval",
            "every tile: D with its 95% interval over passes, M5 [95%], D - M5, M4, D - M4, F0r",
            "the anchor footing; the leak, dips and gates arms",
        ],
        "expected": {
            "E115-R1": "PASS, near 0.27 W, the largest misses on the fp32 sign tiles and fp32.x_logu_s50, reading above M5 (as E103's c_near_rand, s_bhalf_alt and x_e_g did)",
            "E115-R2": "PASS", "E115-R3": "PASS, about 21 of 25", "E115-R4": "PASS or INCONCLUSIVE; s_bridge - s_pair0 the likeliest outside",
            "E115-R5": "UNRESOLVED (the two models differ by at most 0.20 W on any tile)", "E115-S1": "PASS",
            "memory path": "INSIDE: no memory-path term at +-0.56 W",
        },
        "not_scored_if": "fewer than 2 kept passes in the primary: every rule NOT SCORED; the dips-removed arm is then the reading reported, labelled as that arm",
    }
    p = os.path.join(HERE, "predictions-e115.json")
    json.dump(out, open(p, "w"), indent=1)
    print(json.dumps({"written": rel(p), "sha256": sha(p), "M5_reproduced_max_abs_w": repro,
                      "R1_planned": {k: round(v, 4) if isinstance(v, float) else v for k, v in iv_r1.items()},
                      "R1_a3_only": [round(iv_r1_a3["lo95"], 4), round(iv_r1_a3["hi95"], 4)],
                      "R2_planned": {k: round(v, 4) if isinstance(v, float) else v for k, v in iv_r2.items()},
                      "R2_a3_only": [round(iv_r2_a3["lo95"], 4), round(iv_r2_a3["hi95"], 4)],
                      "population": {"float": pop_f, "int8": pop_i},
                      "F0r_vs_M5_max_abs_w": max(abs(tiles[n]["F0r"]["D_w"] - tiles[n]["M5"]["D_w"]) for n in tiles),
                      "F0r_anchors": f0r_anchor}, indent=1))


if __name__ == "__main__":
    main()
