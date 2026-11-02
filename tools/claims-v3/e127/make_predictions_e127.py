#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E127 (Q136): the freeze - M5's and M4's predictions for E127's thirteen tiles and its eleven contrasts, the plan, the rules
and their thresholds, E115's measured values, the session tie and every hash the run refuses to run without. Written before
E127's claim and before any card has run one of the ten new tiles.

    python3 tools/claims-v3/e127/make_predictions_e127.py      # writes predictions-e127.json and predictions-e127.md

The models are Q133(b)'s, frozen in 64b4124e: M5 (docs/reports/data/2026-11-01-q133b-power-model/m5.json) and M4 as frozen for
E103, refitted on E78's rows by predict_blind3.m4_reproduced. The features are fit_m5's (bench_feats on the bench's counts less
the type's zeros, fmt_feats; tile_feats from the bytes). The interval of one tile is predict_blind3's: t(0.975, n - 2) x
sqrt(pool^2 + x'Cx + m^2), pool = the rms of M5's nested errors for that format on aifoundry3 (M4: its frozen pool), C the
jackknife covariance by kind, m the standard error over the tile's three launch points; a contrast's interval is the two
tiles' half-widths in quadrature (Q133(b)'s contrasts_blind3.py rule). The model_pred function below is predict_blind3.py's
nested function, copied unchanged but for being lifted to module level; the script checks that it reproduces
predictions-blind3.json's frozen M5 and M4 points and half-widths for the three E115 tiles E127 reuses, from
counts-blind3.json, before it predicts anything new, and refuses on a difference above 1e-9 W.

The ten new tiles were counted on the Intel with Q133(b)'s bench binary and maps (rtl-sim/fma_toggle_v2, Verilator 5.052,
-fno-dfg, core-et b38a1a31), run_kinds.py unchanged, three launch points each, into counts-e127.json; that run also counted
E115's g_blanes_steady tile again as `repro_g_blanes_steady`, which must equal counts-blind3.json's row exactly.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
Q133B = os.path.join(ROOT, "docs", "reports", "data", "2026-11-01-q133b-power-model")
E115D = os.path.join(ROOT, "docs", "reports", "data", "2026-11-01-e115-blind-pool")
sys.path.insert(0, Q133B)
import predict_blind3 as PB  # noqa: E402  (fit_m5 comes with it, as PB.F)

F = PB.F
BLIND3 = os.path.join(ROOT, "tools", "claims-v3", "kinds", "blind3")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
rel = lambda p: os.path.relpath(p, ROOT)

FROZEN_EXPECT = {   # what E127 reuses, at the sha256 Q133(b) and E115 published
    "tools/claims-v3/kinds/blind3/blind3.json": "60dfbf12a10fc3f464eb1225261954b466a6209d746fa91d1c9218b146786f88",
    "tools/claims-v3/kinds/blind3/predictions-blind3.json": "5f28091a2878d5167aa4402286a1419cca2b78ebe4fbc0b3f34bda35a31f925a",
    "tools/claims-v3/kinds/blind3/contrasts-blind3.json": "399128b9ff83f1a357e6c20cdfd359f11eeb2a7d1d6415516e63cbae4a628578",
    "tools/claims-v3/kinds/blind3/counts-blind3.json": "428d0a3815ae66e7be84312e21a8763f276f2a1e8483dd5b17b27e823595684b",
    "docs/reports/data/2026-11-01-q133b-power-model/m5.json": "c19f2c7bc098b5a8969694b6563784d57bf88e7336fe97ac2afe769b0c63e2da",
    "docs/reports/data/2026-11-01-q133b-power-model/fit_m5.py": "e02116913042291bac41a4431bf880f00a4249bddf50c649c66feb267d77decb",
    "docs/reports/data/2026-11-01-q133b-power-model/predict_blind3.py": "a1877bac4e1ec7e501438504dac06a44762171790e6fe3757cd9095f71c41367",
}
REUSED_E78 = {   # E78's card code and reduction, as E115 froze them (predictions-e115.json > harness.reused_unchanged_sha256)
    "tools/claims-v3/lib.sh": "033d07762548c4abad0bb1721d338bb2333e58d6f07bc0d9a93bdcac0301eaaa",
    "tools/claims-v3/kinds/e78_common.py": "c58923a522849ea033a2d14b7981b0589bcd8a1d5c3129e608d3a418578a552e",
    "tools/claims-v3/kinds/run_e78.py": "f3efd7838686dbd158c8f45a82ab59f4beda68479d792d73a36265e48784bb73",
    "tools/claims-v3/kinds/reduce_e78.py": "6a158ceedc000fae884762d7e273231bfd4e4f42c09bf0b0723afc2da6c05d39",
    "tools/claims-v3/kinds/kinds.json": "9586568f23a97757e34b3cdacdffe5bee0122d236e28a9f76f06e8598b7b1337",
}
# aifoundry3's two binaries, read 2 Nov 2026 07:04 PST (sha256sum on the box): the device-command list (README.md) is
# classified for these; run_e127.sh setup refuses to call a different binary the one classified.
BINARIES = {
    "build/sparsity/host/sparsity_host": "20e760c20e9b99c789ef96f1e4e950d51f534410275bfb933c2aaf96d1090fd0",
    "build/ettelem/ettelem": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2",
}
CODE = ["e127_common.py", "make_e127.py", "run_e127.py", "block_e127.sh", "queue_e127.sh", "run_e127.sh", "reduce_e127.py",
        "score_e127.py", "collect_e127.sh", "selftest_e127.py", "make_predictions_e127.py"]
ANCHOR = PB.ANCHOR

# the contrasts: name -> (plus, minus, what it isolates)
CONTRASTS = {
    "B1": ("fp32.g_blanes_alt", "fp32.g_blanes_steady", "random data: every lane flipping each cycle against lanes 0-3 held off (E115's registered contrast, unequal bus)"),
    "B2": ("fp32.g_blanes_chk", "fp32.g_blanes_alt", "random data, equal operand bus and products: four live lanes in every micro-op against all-off / all-live micro-ops"),
    "B3": ("fp32.g_blanes_chk", "fp32.g_blanes_steady", "random data: every lane flipping each cycle with four live per micro-op, against lanes 0-3 held off"),
    "Q1": ("fp32.q_alt", "fp32.q_steady", "data held still, equal bus bits: every lane flipping each cycle (all-off / all-live micro-ops) against lanes 0-3 held off"),
    "Q2": ("fp32.q_chk", "fp32.q_steady", "data held still: every lane flipping each cycle with four live per micro-op, against lanes 0-3 held off"),
    "Q3": ("fp32.q_alt", "fp32.q_chk", "data held still, equal flipping: all-off / all-live micro-ops against four live in every micro-op"),
    "Q4": ("fp32.q_blk", "fp32.q_steady", "data held still: lanes off and on in 32-cycle stretches against lanes 0-3 held off"),
    "Q5": ("fp32.q_steady_hi", "fp32.q_steady", "data held still: lanes 4-7 held off against lanes 0-3 held off (lane position)"),
    "F1": ("fp16.g_blanes_alt", "fp16.g_blanes_steady", "fp16, random data: every lane flipping each cycle against lanes 0-3 held off"),
    "F2": ("fp16.q_alt", "fp16.q_steady", "fp16, data held still: every lane flipping each cycle (all-off / all-live) against lanes 0-3 held off"),
    "F3": ("fp16.q_chk", "fp16.q_steady", "fp16, data held still: every lane flipping each cycle, four live per micro-op, against lanes 0-3 held off"),
}


def cname(k):
    p, m, _ = CONTRASTS[k]
    return f"{k}: {p} - {m}"


def main():
    bad = [f"{p}: {sha(os.path.join(ROOT, p))[:12]} != {w[:12]}" for p, w in {**FROZEN_EXPECT, **REUSED_E78}.items()
           if sha(os.path.join(ROOT, p)) != w]
    if bad:
        raise SystemExit("refusing: a reused file differs from its freeze: " + "; ".join(bad))
    spec = json.load(open(os.path.join(HERE, "e127-tiles.json")))
    rows, _ = F.assemble()
    m5 = F.load(os.path.join(Q133B, "m5.json"))
    m4 = PB.m4_reproduced(rows)
    zc = F.load(os.path.join(F.B, "counts-v2.json"))["rows"]
    zeros = {t: zc[f"{t}.zeros"]["mean"] for t in F.CPO}
    cb = F.load(os.path.join(BLIND3, "counts-blind3.json"))["rows"]
    pb = json.load(open(os.path.join(BLIND3, "predictions-blind3.json")))
    ce_path = os.path.join(HERE, "counts-e127.json")
    ce = F.load(ce_path)["rows"]

    def feats_for(crow, t, path):     # predict_blind3.main's, unchanged
        f = F.fmt_feats(F.bench_feats(crow["mean"], zeros[t]), t)
        if path:
            f.update({k: v for k, v in F.tile_feats(path, t).items() if k != "sha256"})
        pts = [F.fmt_feats(F.bench_feats(q, zeros[t]), t) for q in crow["points"]]
        if path:
            tf = {k: v for k, v in F.tile_feats(path, t).items() if k != "sha256"}
            for p in pts:
                p.update(tf)
        return f, pts

    def model_pred(fam, f, pts, t, which):     # predict_blind3.main's, unchanged
        if which == "M5":
            M = m5["families"][fam]
            b, C, terms, s1 = np.array(M["coef_J"]), np.array(M["cov_J2"]), M["terms"], M["card1_scale"]
            pools = M["interval_pool_by_format_card"]
            pa3, pc1 = pools[f"{t}|a3"], pools[f"{t}|c1"]
            se_s = M.get("card1_scale_se", 0.0)
        else:
            M = m4[fam]
            b, C, terms, s1 = M["b"], M["C"], M["terms"], M["scale"]
            pa3 = pc1 = M["pool"]
            se_s = M["scale_se"]
        rate = F.RATE[t]
        x = np.array([rate * f[q] for q in terms])
        d = float(x @ b)
        lp = [float(np.array([rate * p[q] for q in terms]) @ b) for p in pts]
        m = float(np.std(lp, ddof=1) / math.sqrt(len(lp))) if len(lp) > 1 else 0.0
        xcx = float(x @ C @ x)
        out = {}
        for foot, sc, pool, extra in (("a3", 1.0, pa3, 0.0), ("c1", s1, pc1, (d * se_s) ** 2), ("new", 1.0, pa3, (abs(1 - s1) * d) ** 2)):
            half = F.t975(pool["n"] - 2) * math.sqrt(pool["rms_w"] ** 2 + sc * sc * xcx + (sc * m) ** 2 + extra)
            D = d * sc
            out[foot] = {"D_w": D, "lo95": D - half, "hi95": D + half, "half95": half}
        out["launch_points_w_a3"] = lp
        out["terms_w_a3"] = [float(v) for v in x * b]
        out["terms"] = terms
        return out

    # 1. the code reproduces predictions-blind3.json for the three reused tiles
    repro = {}
    for name in ("fp32.g_blanes_steady", "fp32.g_blanes_alt", "fp16.g_blanes_alt"):
        v = spec["tiles"][name]
        f, pts = feats_for(cb[name], v["type"], os.path.join(ROOT, v["file"]))
        for w in ("M5", "M4"):
            p = model_pred("float", f, pts, v["type"], w)["a3"]
            q = pb["tiles"][name][w]["a3"]
            repro[f"{name} {w}"] = max(abs(p["D_w"] - q["D_w"]), abs(p["half95"] - q["half95"]))
    worst = max(repro.values())
    if worst > 1e-9:
        raise SystemExit(f"refusing: model_pred does not reproduce predictions-blind3.json ({worst} W)")
    # 2. the bench's repeat count of g_blanes_steady equals Q133(b)'s row exactly
    a, b_ = ce["fp32.repro_g_blanes_steady"], cb["fp32.g_blanes_steady"]
    strip = lambda r: {k: v for k, v in r.items() if k != "kind"}     # the label differs by design (repro_...), nothing else may
    same = json.dumps(strip(a), sort_keys=True) == json.dumps(strip(b_), sort_keys=True)
    if not same:
        diffs = [k for k in a["mean"] if json.dumps(a["mean"].get(k), sort_keys=True) != json.dumps(b_["mean"].get(k), sort_keys=True)]
        raise SystemExit(f"refusing: the bench's repeat count of g_blanes_steady differs from counts-blind3.json in {diffs[:8]}")
    # 3. every new count passed the bench's functional check
    mism = {n: ce[n]["mean"].get("check_mismatch") for n in ce}
    # 4. the anchors on the a3 footing (in-sample kinds; for the anchor footing only), as predict_blind3 computed them
    anchors = {a_: {w: pb["anchors_predicted_a3_w"][a_][w] for w in ("M5", "M4")} for a_ in ANCHOR.values()}
    tiles, terms_names = {}, None
    for name, v in sorted(spec["tiles"].items()):
        t = v["type"]
        if v["family"] == "bridge":
            src, crow = "predictions-blind3.json (frozen in 64b4124e), reproduced above", cb[name]
        else:
            src, crow = "this script, on counts-e127.json", ce[name]
            if crow["mean"].get("check_mismatch"):
                raise SystemExit(f"refusing: {name} failed the bench's functional check ({crow['mean'].get('check_mismatch')} words)")
        f, pts = feats_for(crow, t, os.path.join(ROOT, v["file"]))
        rec = {"type": t, "kind": v["kind"], "family": v["family"], "file": v["file"], "sha256": v["sha256"],
               "anchor": ANCHOR[t], "source": src, "stats": v["stats"],
               "bench": {"check_mismatch_words": crow["mean"].get("check_mismatch"), "valid_slots": crow["mean"].get("valid_slots"),
                         "cycles": crow["mean"].get("cycles"), "clocked_bits_less_zeros": f["clk"], "bus_nets_less_zeros": f["bus"],
                         "gtr": f.get("gtr"), "bbits": f.get("bbits"), "abits": f.get("abits")}}
        for w in ("M5", "M4"):
            p = model_pred("float", f, pts, t, w)
            rec[w] = {"D_w": p["a3"]["D_w"], "lo95": p["a3"]["lo95"], "hi95": p["a3"]["hi95"], "half95": p["a3"]["half95"],
                      "terms_w_a3": dict(zip(p["terms"], p["terms_w_a3"])), "launch_points_w_a3": p["launch_points_w_a3"],
                      "ratio_to_anchor": p["a3"]["D_w"] / anchors[ANCHOR[t]][w]}
            if v["family"] == "bridge":
                q = pb["tiles"][name][w]["a3"]
                rec[w].update({"D_w": q["D_w"], "lo95": q["lo95"], "hi95": q["hi95"], "half95": q["half95"]})
        tiles[name] = rec
    cons = {}
    for k, (p, m, iso) in CONTRASTS.items():
        tp, tm = tiles[p], tiles[m]
        c = {"plus": p, "minus": m, "isolates": iso, "anchor": tp["anchor"]}
        for w in ("M5", "M4"):
            d = tp[w]["D_w"] - tm[w]["D_w"]
            h = math.sqrt(tp[w]["half95"] ** 2 + tm[w]["half95"] ** 2)
            c[w] = {"D_w": d, "half95": h, "lo95": d - h, "hi95": d + h,
                    "terms_w_a3": {q: tp[w]["terms_w_a3"][q] - tm[w]["terms_w_a3"][q] for q in tp[w]["terms_w_a3"]}}
        cons[cname(k)] = c
    # E115's measured values (its reported reading: the dips-removed arm, e115-nodips.json), for R1 and the tie
    e115 = json.load(open(os.path.join(E115D, "e115-nodips.json")))
    per = e115["per_pass"]
    b1_vals = [per[p]["fp32.g_blanes_alt"]["D"] - per[p]["fp32.g_blanes_steady"]["D"] for p in sorted(per)]
    b1_mean = sum(b1_vals) / len(b1_vals)
    e115_tiles = {n: e115["items"][n]["D"] for n in ("fp32.g_blanes_steady", "fp32.g_blanes_alt", "fp16.g_blanes_alt")}
    tie = {}
    for cell, band in (("fp32.randn", 0.5), ("fp16.randn", 0.5), ("anchor_pi", 0.5), ("int8.full", 0.25)):
        d = e115["items"][cell]["D"]
        tie[cell] = {"ref_w": d["mean"], "ref_ci95_w": d.get("ci95"), "band_w": band, "ref": "E115 (dips removed)",
                     "source": "docs/reports/data/2026-11-01-e115-blind-pool/e115-nodips.json items.<cell>.D.mean"}
    rules = {
        "E127-R1": {"what": "the replicate: B1 lies above M5's frozen 95% interval again", "contrast": cname("B1"),
                    "pass": "B1's low end > M5's upper bound", "fail": "B1's mean <= M5's upper bound",
                    "E115_measured_w": b1_mean, "E115_per_pass_w": b1_vals},
        "E127-R2": {"what": "the primary: does the miss stay with the data held still? (fp32)", "test": cname("Q1"), "reference": cname("B1"),
                    "line": "0.5 x e(B1), this session", "GATE": "e(Q1) low end >= line", "DATA": "e(Q1) high end <= line",
                    "OPPOSITE": "e(Q1) high end < -line", "needs": "E127-R1 PASS"},
        "E127-R3": {"what": "the same in fp16", "test": cname("F2"), "reference": cname("F1"), "line": "0.5 x e(F1), this session",
                    "needs": "e(F1)'s low end > 0"},
        "E127-R4": {"what": "per-lane flipping or all lanes off together (fp32, random data)", "test": cname("B3"), "reference": cname("B1"),
                    "line": "0.5 x e(B1)", "PER-LANE": "e(B3) low end >= line", "ALL-OFF": "e(B3) high end <= line", "needs": "E127-R1 PASS"},
        "E127-R4q": {"what": "the same at quiet data", "test": cname("Q2"), "reference": cname("Q1"), "line": "0.5 x e(Q1)",
                     "needs": "E127-R2 GATE"},
        "E127-R5": {"what": "the time scale (fp32, quiet)", "test": cname("Q4"), "reference": cname("Q1"), "line": "0.5 x e(Q1)",
                    "SHORT": "e(Q4) high end <= line (a lane off 32 cycles at a time prices like a steady one)",
                    "LONG": "e(Q4) low end >= line", "needs": "E127-R2 GATE"},
        "E127-R6": {"what": "lane position (fp32, quiet)", "contrast": cname("Q5"), "tolerance_w": 0.30,
                    "pass": "|Q5| + half-width <= 0.30 W", "fail": "|Q5| - half-width > 0.30 W"},
        "E127-S1": {"what": "the session tie against E115 on this card (a failure means the session moved, never a verdict)"},
    }
    plan = {"card": "aifoundry3 card 0", "clock": "600 MHz as read (TDP 0 latched at boot), never set", "first_pass": 12710,
            "passes_planned": 5, "smoke_pass": 12701, "min_kept_passes_scored": 3, "min_tile_passes": 3,
            "runs_per_pass": 33, "launches_per_pass": 35, "budget_s_from_session_start": 1890, "card_minutes_max": 35,
            "deadline": "2026-11-02 15:50 PST (every run ends by 16:00 PST; no session starts after 15:00 PST)",
            "first_pass_estimate_s": 380, "gap_s": 15, "board_power_stop_w": 65.0, "die_stop_c": 70.0,
            "primary_reduction": "reduce_e78.py unchanged via reduce_e127.py --drop-dips (E82 A2), leakage auto",
            "arms": ["dips kept", "leakage 0.1994 (dips removed)", "leakage 0.3803 (dips removed)", "leakage 0 (dips removed)",
                     "gates off (dips removed)"],
            "fewer_than_min_kept": "every rule NOT SCORED on the primary; the gates-off arm is then the reading reported, labelled"}
    expected = {"E127-R1": "PASS, B1 near +2.0 W",
                "E127-R2": "GATE: the miss stays with the data still, because the bench puts its whole 0.86 W clocked-bit "
                           "difference between E115's pair on the micro-ops with all eight lanes off (M5's clk term: q_alt and q_blk "
                           "-0.86 and -0.84 W against q_steady, q_chk 0.00), and no data value moves that",
                "E127-R3": "GATE",
                "E127-R4": "ALL-OFF: the miss goes with micro-ops whose eight lanes are all off, where the bench prices a clocking "
                           "saving the card may not take, not with each lane's own gate flipping (g_blanes_chk keeps g_blanes_steady's "
                           "clk term)",
                "E127-R4q": "ALL-OFF", "E127-R5": "LONG (q_blk has all-off micro-ops, as q_alt does)", "E127-R6": "PASS",
                "E127-S1": "PASS",
                "written": "after the bench's counts and before any card data; the first draft of this registration expected "
                           "PER-LANE and SHORT, before the counts showed where the bench's clocked bits differ"}
    harness = {"reused_unchanged_sha256": REUSED_E78,
               "e127_files_sha256": {rel(os.path.join(HERE, f)): sha(os.path.join(HERE, f)) for f in CODE if os.path.exists(os.path.join(HERE, f))},
               "e127_tiles_sha256": {**{v["file"]: v["sha256"] for v in spec["tiles"].values()},
                                     "tools/claims-v3/e127/e127-tiles.json": sha(os.path.join(HERE, "e127-tiles.json")),
                                     "tools/claims-v3/e127/SHA256SUMS": sha(os.path.join(HERE, "SHA256SUMS")),
                                     "tools/claims-v3/e127/counts-e127.json": sha(ce_path)},
               "frozen_reused_sha256": FROZEN_EXPECT, "binaries_sha256": BINARIES,
               "card_frozen_sha256": {"tools/claims-v3/kinds/blind3/blind3.json": FROZEN_EXPECT["tools/claims-v3/kinds/blind3/blind3.json"]}}
    out = {"experiment": "E127", "request": "Q136 (critic 3 of Q134's final critic)", "date": "2026-11-02",
           "answers": "https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open item 6",
           "units": "D, W over the type's own zeros at 600 MHz on aifoundry3 card 0 (the a3 footing, no scale), E78's reduction",
           "harness": harness, "plan": plan, "tiles": tiles, "contrasts": cons, "rules": rules, "expected": expected,
           "session_tie": {"cells": tie, "beside": "E78's cells (e78.json) are printed beside, no verdict"},
           "anchors_predicted_a3_w": anchors,
           "e115_measured": {"tiles_D": e115_tiles, "B1_per_pass_w": b1_vals, "B1_mean_w": b1_mean,
                             "source": "docs/reports/data/2026-11-01-e115-blind-pool/e115-nodips.json"},
           "checks": {"model_pred_reproduces_predictions_blind3_max_abs_w": worst,
                      "bench_repeat_of_g_blanes_steady_identical": same, "bench_check_mismatch_words": mism}}
    jp = os.path.join(HERE, "predictions-e127.json")
    json.dump(out, open(jp, "w"), indent=1, sort_keys=True)
    with open(os.path.join(HERE, "predictions-e127.md"), "w") as fo:
        w = fo.write
        w("# E127: frozen predictions (M5 and M4, aifoundry3 card 0, a3 footing)\n\nWritten by `make_predictions_e127.py`. D in W over "
          "the type's own zeros at 600 MHz. The commit holding this file is the freeze; no card had run a new E127 tile.\n\n")
        w("| tile | family | b-bus bits/op | gate flips/op | live lanes/micro-op | **M5 [95%]** | M4 [95%] | M5 clk term | M5 bus term |\n"
          "|---|---|---:|---:|---|---:|---:|---:|---:|\n")
        for n, r in sorted(tiles.items()):
            s = r["stats"]
            w(f"| `{n}` | {r['family']} | {s['b_bus_bits_per_op']:,} | {s['gate_flips_per_op']:,} | {s['live_lanes_per_microop']} | "
              f"**{r['M5']['D_w']:.2f}** [{r['M5']['lo95']:.2f}, {r['M5']['hi95']:.2f}] | {r['M4']['D_w']:.2f} [{r['M4']['lo95']:.2f}, "
              f"{r['M4']['hi95']:.2f}] | {r['M5']['terms_w_a3']['clk']:.2f} | {r['M5']['terms_w_a3']['bus']:.2f} |\n")
        w("\n| contrast | isolates | **M5 [95%]** | M4 | M5 terms (W) |\n|---|---|---:|---:|---|\n")
        for n, c in cons.items():
            t5 = ", ".join(f"{q} {v:+.2f}" for q, v in c["M5"]["terms_w_a3"].items() if abs(v) > 0.005)
            w(f"| `{n}` | {c['isolates']} | **{c['M5']['D_w']:+.2f}** [{c['M5']['lo95']:+.2f}, {c['M5']['hi95']:+.2f}] | "
              f"{c['M4']['D_w']:+.2f} | {t5} |\n")
    print(json.dumps({"tiles": len(tiles), "contrasts": len(cons), "sha256": sha(jp), "repro_max_w": worst, "bench_repeat_same": same,
                      "mismatch": mism}))


if __name__ == "__main__":
    main()
