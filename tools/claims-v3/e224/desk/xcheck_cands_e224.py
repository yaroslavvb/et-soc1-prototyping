#!/usr/bin/env python3
"""E224 (Q237) desk check, run BEFORE the point rule and the forecasts (E222's xcheck_cands_e222.py line for line, through E224's callers, with
E217's switch-count inputs merged as E224 runs them, and two checks added: the four models against E220's own frozen forecasts at the same 306
rows, and the three pairs by compose_sub): the callers in desk/models_e224.py re-make each MM1-v3.3 candidate's
FROZEN E220 forecasts (their makers' own files, landed by land-cands: posimb/forecasts-e220-posimb.json, gemmlnc-af4/forecasts-e220-af4.json,
l3s/forecasts-e220-l3s.json) at E220's own points, cards and clocks (tools/claims-v3/e220/points-e220.json, sha256 2451ca9d...: arm A
aifoundry1 card 1 at 600.0 MHz, arm B aifoundry2 card 0 at 799.0, 700.0 and 600.0 MHz; 306 rows) - so the calls E224 makes at its two cards
(E220's own) are each candidate's frozen code, unchanged. Also: 'MM1-v3.2 + all three' (compose) re-makes each candidate where it alone acts.
Reads no E220 datum (points and forecasts only). /usr/bin/python3 3.12.3 -I -B, numpy, single-threaded.
    /usr/bin/python3 -I -B tools/claims-v3/e224/desk/xcheck_cands_e224.py      writes desk/xcheck-cands-e224.json; exit 0 = EQUAL
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import models_e224 as MZ  # noqa: E402

REPO = MZ.REPO
E220_POINTS = ("tools/claims-v3/e220/points-e220.json", "2451ca9d3763c17b2366a4c1b88e680a15a30a01a7a93e0cbf1c041d9f87bd28")
E220_FORECAST = ("tools/claims-v3/e220/forecast-e220.json", "dd31766796bc281ed47a56b8caf12465662e363eb2ec7dfaafd324a05fa78675")
FROZEN = {"posimb": ("tools/matmul/mm1/v3.3-cands/posimb/forecasts-e220-posimb.json", "3010f28c7e47e754a8bc4da5d0742e0d515c85da8d59e70a4ee3b798ccca1034"),
          "af4": ("tools/matmul/mm1/v3.3-cands/gemmlnc-af4/forecasts-e220-af4.json", "37ace71c028a707ef07e9658cfdb2a4b3743ec0498b20b3bae93f79ac6af93e4"),
          "l3s": ("tools/matmul/mm1/v3.3-cands/l3s/forecasts-e220-l3s.json", "ac65c9596f5611c95899b1c5105eee137602d5afbe00dfa316582ea651b753a8")}
CARD = {"A": "aifoundry1 card 1", "B": "aifoundry2 card 0"}
CLOCKS = {"A": (600.0,), "B": (799.0, 700.0, 600.0)}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rel(a, b):
    if a is None and b is None:
        return 0.0
    if a is None or b is None:
        return float("inf")
    if a == b:
        return 0.0
    return abs(a - b) / max(abs(a), abs(b), 1e-300)


def main():
    for k, (p, h) in list(FROZEN.items()) + [("points", E220_POINTS)]:
        if sha(os.path.join(REPO, p)) != h:
            print(f"xcheck_cands_e224: REFUSED, {p} is not at its pin")
            return 4
    P = json.load(open(os.path.join(REPO, E220_POINTS[0])))
    M = MZ.Models()
    mine = {}
    for arm in ("A", "B"):
        pts = [{"id": p["id"], "arm": p["token"], "fmt": p["format"], "kind": "random", "mask": p["shire_mask"]} for p in P["points"][arm]]
        for f in CLOCKS[arm]:
            got = M.forecast(pts, f=f, card=CARD[arm], models=MZ.MODELS)
            for pid, v in got.items():
                mine[(arm, f, pid)] = v
    res = {}
    # posimb
    F = json.load(open(os.path.join(REPO, FROZEN["posimb"][0])))
    lab = F["label"]
    w = {"n": 0, "worst_rel": 0.0, "worst": None, "exact_rows": 0}
    for r in F["rows"]:
        v = mine[(r["arm"], float(r["f_mhz"]), r["id"])][MZ.POSIMB]
        worst_row = 0.0
        for q in ("cycles_per_op_wall", "cycles_per_op_mean", "T_op_us", "seconds_per_gemm", "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm",
                  "J_at_rest_per_gemm"):
            d = rel(v.get(q), r.get(lab + "|" + q))
            worst_row = max(worst_row, d)
            if d > w["worst_rel"]:
                w["worst_rel"], w["worst"] = d, f"{r['arm']} {r['f_mhz']} {r['id']} {q}"
        for q in ("g_wall", "g_mean", "e", "Phi_hop", "Phi_lag"):
            d = rel(v["term"][q], r[q])
            worst_row = max(worst_row, d)
            if d > w["worst_rel"]:
                w["worst_rel"], w["worst"] = d, f"{r['arm']} {r['f_mhz']} {r['id']} {q}"
        w["n"] += 1
        w["exact_rows"] += int(worst_row == 0.0)
    res["posimb"] = w
    # AF4
    F = json.load(open(os.path.join(REPO, FROZEN["af4"][0])))
    w = {"n": 0, "worst_rel": 0.0, "worst": None, "exact_rows": 0}
    for r in F["rows"]:
        v = mine[(r["arm"], float(r["f_mhz"]), r["id"])][MZ.AF4]
        worst_row = 0.0
        for q, mq in (("W_over_idle", "W_over_idle"), ("A_W", "A_W"), ("B_W_us", "B_W_us"), ("J_over_idle_per_gemm_t_forecast", "J_over_idle_per_gemm"),
                      ("J_at_rest_per_gemm_t_forecast", "J_at_rest_per_gemm"), ("T_op_us", "T_op_us"), ("cycles_per_op_wall", "cycles_per_op_wall"),
                      ("seconds_per_gemm", "seconds_per_gemm")):
            d = rel(v.get(mq), r.get(q))
            worst_row = max(worst_row, d)
            if d > w["worst_rel"]:
                w["worst_rel"], w["worst"] = d, f"{r['arm']} {r['f_mhz']} {r['id']} {q}"
        d = rel(v["term"]["term_AF4_W"], r["term_AF4_W"])
        worst_row = max(worst_row, d)
        w["n"] += 1
        w["exact_rows"] += int(worst_row == 0.0)
    res["af4"] = w
    # L3S
    F = json.load(open(os.path.join(REPO, FROZEN["l3s"][0])))
    w = {"n": 0, "worst_rel": 0.0, "worst": None, "exact_rows": 0}
    for r in F["rows"]:
        v = mine[(r["arm"], float(r["f_mhz"]), r["id"])][MZ.L3S]
        x = r["models"][F["meta"]["what"].split("forecasts of ")[1].split(" (lam")[0]]
        worst_row = 0.0
        for q, mq in (("T_op_us", "T_op_us"), ("cycles_per_op_wall", "cycles_per_op_wall"), ("cycles_per_op_mean", "cycles_per_op_mean"),
                      ("seconds_per_gemm", "seconds_per_gemm"), ("W_over_idle", "W_over_idle"), ("A_W", "A_W"), ("B_W_us", "B_W_us"),
                      ("J_over_idle_per_gemm", "J_over_idle_per_gemm"), ("J_at_rest_per_gemm_REPORTED", "J_at_rest_per_gemm"),
                      ("P_rest_W_REPORTED", "rest_law_W")):
            d = rel(v.get(mq), x.get(q))
            worst_row = max(worst_row, d)
            if d > w["worst_rel"]:
                w["worst_rel"], w["worst"] = d, f"{r['arm']} {r['f_mhz']} {r['id']} {q}"
        if bool(v["in_scope"]) != bool(r["in_L3S_domain"]):
            worst_row = float("inf")
            w["worst"] = f"domain differs at {r['id']}"
        w["n"] += 1
        w["exact_rows"] += int(worst_row == 0.0)
    res["l3s"] = w
    # the combination equals each candidate where that candidate alone acts, and MM1-v3.2 where none acts
    w = {"n": 0, "by_acting": {}, "worst_rel": 0.0, "worst": None}
    for (arm, f, pid), v in mine.items():
        c = v[MZ.COMBO]
        a = tuple(c["acting"])
        w["by_acting"][" + ".join(a) or "none"] = w["by_acting"].get(" + ".join(a) or "none", 0) + 1
        ref = {(): v["MM1-v3.2"], (MZ.POSIMB,): v[MZ.POSIMB], (MZ.AF4,): v[MZ.AF4], (MZ.L3S,): v[MZ.L3S]}.get(a)
        if ref is None:
            continue
        for q in ("T_op_us", "cycles_per_op_wall", "W_over_idle", "B_W_us", "J_over_idle_per_gemm"):
            d = rel(c.get(q), ref.get(q))
            if d > w["worst_rel"]:
                w["worst_rel"], w["worst"] = d, f"{arm} {f} {pid} {q}"
        w["n"] += 1
    res["combination_single_term_rows"] = w
    # E224's added checks: (1) the four models against E220's own frozen forecasts (forecast-e220.json) at its 306 rows, with E217's counts merged
    if sha(os.path.join(REPO, E220_FORECAST[0])) != E220_FORECAST[1]:
        print(f"xcheck_cands_e224: REFUSED, {E220_FORECAST[0]} is not at its pin")
        return 4
    F220 = json.load(open(os.path.join(REPO, E220_FORECAST[0])))
    # equality read to 1e-9 relative (the batch a predictor is called with moves its last digits: E220 made its rows in one call per arm and
    # clock with its own point list); the worst per model and the exact rows are printed
    TOL4 = 1e-9
    w = {"n": 0, "worst_rel_by_model": {m: 0.0 for m in MZ.MODELS}, "worst": None, "exact_rows": 0, "e217_counts_merged": bool(M.e217),
         "tolerance_rel": TOL4}
    worst_all = 0.0
    for (arm, f, pid), v in mine.items():
        col = "%.1f" % f
        ref = F220["arms"][arm]["points"][pid]["clocks"][col]
        worst_row = 0.0
        for mdl in MZ.MODELS:
            x, y = v.get(mdl) or {}, ref.get(mdl) or {}
            for q in ("cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm", "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm"):
                d = rel(x.get(q), y.get(q))
                worst_row = max(worst_row, d)
                w["worst_rel_by_model"][mdl] = max(w["worst_rel_by_model"][mdl], d)
                if d > worst_all:
                    worst_all, w["worst"] = d, f"{arm} {f} {pid} {mdl} {q}"
        w["n"] += 1
        w["exact_rows"] += int(worst_row == 0.0)
    w["worst_rel"] = 0.0 if worst_all <= TOL4 else worst_all
    w["worst_rel_seen"] = worst_all
    res["four_models_vs_forecast_e220"] = w
    # (2) the pairs by compose_sub: each equals the single term that acts (or MM1-v3.2) where at most one of its two terms acts
    w = {"n": 0, "by_pair_acting": {}, "worst_rel": 0.0, "worst": None}
    for (arm, f, pid), v in mine.items():
        for terms, name in ((("posimb", "AF4"), "MM1-v3.2 + posimb + AF4"), (("posimb", "L3S"), "MM1-v3.2 + posimb + L3S"),
                            (("AF4", "L3S"), "MM1-v3.2 + AF4 + L3S")):
            c = v[name]
            a = tuple(c["acting"])
            w["by_pair_acting"][name + ": " + (" + ".join(a) or "none")] = w["by_pair_acting"].get(name + ": " + (" + ".join(a) or "none"), 0) + 1
            ref = {(): v["MM1-v3.2"], (MZ.POSIMB,): v[MZ.POSIMB], (MZ.AF4,): v[MZ.AF4], (MZ.L3S,): v[MZ.L3S], (MZ.AF4, MZ.L3S): v[MZ.COMBO]}.get(a)
            if ref is None:
                continue
            for q in ("T_op_us", "cycles_per_op_wall", "W_over_idle", "B_W_us", "J_over_idle_per_gemm"):
                d = rel(c.get(q), ref.get(q))
                if d > w["worst_rel"]:
                    w["worst_rel"], w["worst"] = d, f"{arm} {f} {pid} {name} {q}"
            w["n"] += 1
    res["pairs_by_compose_sub"] = w
    res["e217_counts"] = M.e217
    ok = all(res[k]["worst_rel"] == 0.0 for k in ("posimb", "af4", "l3s", "combination_single_term_rows", "four_models_vs_forecast_e220",
                                                  "pairs_by_compose_sub"))
    res["verdict"] = "EQUAL" if ok else "DIFFER"
    res["pins"] = {k: v[1] for k, v in FROZEN.items()}
    res["points"] = E220_POINTS[1]
    res["new_posimb_features_made"] = len(M.PS_made)
    res["new_l3s_records_made"] = len(M.l3s_extra)
    json.dump(res, open(os.path.join(HERE, "xcheck-cands-e224.json"), "w"), indent=1, sort_keys=True)
    for k in ("posimb", "af4", "l3s", "combination_single_term_rows", "four_models_vs_forecast_e220", "pairs_by_compose_sub"):
        print(k, res[k])
    print("XCHECK-CANDS-E224:", res["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
