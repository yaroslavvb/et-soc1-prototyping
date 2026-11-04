#!/usr/bin/env python3
"""Q141(t): the reported arm M9_27pt of REGISTRATION.md (committed 0830f65b before any count), from the bench's 27-point counts
of pool 7's eight S tiles, mechanically, with the frozen code.

    /usr/bin/python3 -B make_arm_s7.py          # from anywhere; numpy is needed by the frozen predictor and fit_m9

Four checks run before anything is written, and a failure stops it (the predictions' own checks below stop before arm-s7.json):
  C    every counted point's check_mismatch is 0
  D1   each tile's three standard points equal its committed counts-blind7.json points exactly, and run_kinds.py's mean_rows
       over them gives the committed row's mean exactly
  D2   fp32.b_onebit_b20_pi's 27 points equal its byte twin fp32.cal_pi_b20's committed 27 (bench-check/counts-cal.json and
       recount-rule/counts-pilot27.json) exactly
  RR   this file's copy of recount_rule.py's per-tile block, run on the 16 calibration tiles' committed counts, reproduces
       recount-rule.json's by-N figures exactly
Then:
  counts-arm-s7.json   pool 7's 61 rows: the eight S rows' mean = run_kinds.py's mean_rows over their 27 points (their points: the
                       three standard ones, so fit_m9's lq1, in no kept form, is computed as frozen); the other 53 as committed
  arm/                 the frozen predict_blind7.py, unchanged, run as a script on counts-arm-s7.json for aifoundry3 and
                       aifoundry1c1 (check: the 53 other tiles' predictions equal the frozen files' exactly)
  arm/pool6-twins/     the same predictor on pool 6 (post hoc: M9 was fitted on pool 6's rows), with its committed three-point
                       counts (3pt/) and with fp32.b_onebit_b20_third and fp32.b_onebit_b12_third at their byte twins' committed
                       27 points (27pt/): REGISTRATION.md R6's pool-6 half and the scorer's self-test
  recount-s7.json/.txt e(9), e(27) per S tile by recount_rule.py's functions (points, prices, point_w, err), imported unchanged
  arm-s7.json          per card and tile: P3 (M9 as frozen), P27 (the arm), k = P3 - P27, u = s x e(27), the die rise's, and
                       M8's, M7's, M6's shifts beside (reported); arm-s7.txt, the same as a table
  arm/arm27-<card>.json  {tile: P27} on that card, the form tools/claims-v3/e163/score_e163.py --arm27 reads
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(TOP, "docs", "reports", "data")
M9D = os.path.join(DD, "2026-11-04-q140m-m9")
RRD = os.path.join(M9D, "recount-rule")
BC = os.path.join(M9D, "bench-check")
POOL7 = os.path.join(TOP, "tools", "claims-v3", "kinds", "blind7")
POOL6 = os.path.join(TOP, "tools", "claims-v3", "kinds", "blind6")
BENCH_SRC = os.path.join(TOP, "rtl-sim", "fma_toggle_v2")
sys.path.insert(0, RRD)
sys.path.insert(0, BENCH_SRC)
import recount_rule as RR  # noqa: E402  (imports fit_m9 unchanged; only its functions are used, never its main())
import run_kinds as RK  # noqa: E402  (the bench's own mean_rows)

fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
load = lambda p: json.load(open(p))  # noqa: E731
canon = lambda o: json.dumps(o, sort_keys=True)  # noqa: E731
S7 = ("fp32.b_onebit_b20_one", "fp32.b_onebit_b20_full", "fp32.b_onebit_b20_pi", "fp32.b_onebit_b20_seventh",
      "fp32.b_onebit_b22_third", "fp16.b_onebit_b9_one", "fp16.b_onebit_b8_pi")
A1P5 = "fp32.b_onebit_b20_third_a1p5"
TILES = S7 + (A1P5,)
TWINS6 = {"fp32.b_onebit_b20_third": "fp32.cal_third_b20", "fp32.b_onebit_b12_third": "fp32.cal_third_b12"}
CARDS = ("aifoundry3", "aifoundry1c1")
PY = "/usr/bin/python3"


def stop(msg):
    raise SystemExit("STOP: " + msg)


def diff_paths(a, b, path=""):
    """the leaf paths where two counted points differ (for a failed D1 or D2 report)"""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += diff_paths(a.get(k), b.get(k), f"{path}.{k}")
        return out
    return [] if canon(a) == canon(b) else [path or "."]


def rel(p):
    return os.path.relpath(p, TOP)


def per_tile_by_n(r, ns, pr, stop_at_first_met):
    """recount_rule.py main()'s per-tile block (its loop body, unchanged in substance): e(N) at each N whose points are counted"""
    typ = r["type"]
    std3 = RR.points(3)
    by_n, first = {}, None
    for n in ns:
        if not all(x in r["points"] for x in RR.points(n)):
            break
        ws = [RR.point_w(r["points"][x], typ, pr) for x in RR.points(n)]
        m3 = sum(RR.point_w(r["points"][x], typ, pr) for x in std3) / 3
        e = RR.err(ws)
        e["three_point_minus_N_w"] = m3 - e["mean_w"]
        e["met"] = e["e_w"] <= RR.BOUND_W
        by_n[str(n)] = e
        if e["met"] and first is None:
            first = n
            if stop_at_first_met:
                break
    return by_n, first


def check_rr_replication(pr):
    rows = RR.merged([os.path.join(BC, "counts-cal.json"), os.path.join(RRD, "counts-pilot27.json")])
    ref = load(os.path.join(RRD, "recount-rule.json"))["tiles"]
    fields = ("mean_w", "se_sample_w", "se_interleaved_w", "e_w", "subrule_means_w", "three_point_minus_N_w", "met")
    n_cmp, bad = 0, []
    for name, rec in ref.items():
        mine, _ = per_tile_by_n(rows[name], (9, 27, 81, 243), pr, True)
        for n, e in rec["by_N"].items():
            for f in fields:
                n_cmp += 1
                if canon(mine.get(n, {}).get(f)) != canon(e[f]):
                    bad.append(f"{name} N={n} {f}")
    if bad:
        stop("the per-tile block does not reproduce recount-rule.json: " + ", ".join(bad[:5]))
    return {"tiles": len(ref), "fields_compared": n_cmp, "identical": True}


def run_predictor(pool, card, counts, out):
    os.makedirs(out, exist_ok=True)
    cmd = [PY, "-B", os.path.join(M9D, "predict_blind7.py"), pool, card, "--counts", counts, "--out", out]
    r = subprocess.run(cmd, cwd=TOP, capture_output=True, text=True)
    if r.returncode != 0:
        stop(f"predict_blind7.py failed for {card} on {rel(pool)}: {r.stderr[-400:]}")
    return load(os.path.join(out, f"predictions-{card}.json"))


def main():
    counts27 = os.path.join(HERE, "counts-s7-27.json")
    new = load(counts27)["rows"]
    c7 = load(os.path.join(POOL7, "counts-blind7.json"))
    for line in open(os.path.join(BC, "bench-sha256.txt")):
        if line.strip().endswith("run_kinds.py") and fsha(os.path.join(BENCH_SRC, "run_kinds.py")) != line.split()[0]:
            stop("the repo's run_kinds.py differs from the bench build's")
    checks = {}
    # C
    miss = {k: [p["n0"] for p in r["points"] if p.get("check_mismatch")] for k, r in new.items()}
    if any(miss.values()) or set(new) != set(TILES):
        stop(f"C or tile set: {miss} {sorted(new)}")
    p27 = RR.points(27)
    for k, r in new.items():
        if sorted(p["n0"] for p in r["points"]) != p27:
            stop(f"{k}: not the 27 points of RECOUNT-RULE.md section 1")
    checks["C"] = {"points": sum(len(r["points"]) for r in new.values()), "check_mismatch_points": 0}
    # D1
    std3 = RR.points(3)
    d1 = {}
    for k in TILES:
        old = c7["rows"][k]
        mine = {p["n0"]: p for p in new[k]["points"]}
        same = all(canon(mine[p["n0"]]) == canon(p) for p in old["points"]) and sorted(p["n0"] for p in old["points"]) == std3
        mean_same = canon(RK.mean_rows(sorted(old["points"], key=lambda p: p["n0"]))) == canon(old["mean"])
        own_mean = canon(RK.mean_rows(sorted(new[k]["points"], key=lambda p: p["n0"]))) == canon(new[k]["mean"])
        if not (same and mean_same and own_mean):
            where = sorted({d for p in old["points"] for d in diff_paths(mine.get(p["n0"]), p)})
            stop(f"D1 fails on {k}: points identical {same} (differing fields {where[:8]}), mean_rows reproduces the committed "
                 f"mean {mean_same}, the run's own 27-point mean {own_mean}")
        d1[k] = {"three_points_identical": True, "mean_rows_reproduces_committed_mean": True,
                 "mean_rows_reproduces_the_runs_own_27_point_mean": True}
    checks["D1"] = d1
    # D2
    cal = RR.merged([os.path.join(BC, "counts-cal.json"), os.path.join(RRD, "counts-pilot27.json")])
    twin = cal["fp32.cal_pi_b20"]["points"]
    mine = {p["n0"]: p for p in new["fp32.b_onebit_b20_pi"]["points"]}
    if sorted(twin) != p27 or any(canon(mine[n]) != canon(twin[n]) for n in p27):
        where = sorted({d for n in p27 if n in twin for d in diff_paths(mine[n], twin[n])})
        stop(f"D2 fails: fp32.b_onebit_b20_pi's 27 points differ from fp32.cal_pi_b20's committed 27 (fields {where[:8]})")
    man7 = {m["name"]: m for m in load(os.path.join(POOL7, "blind7.json"))["tiles"]}
    calm = {m["name"]: m for m in load(os.path.join(BC, "cal-tiles.json"))["tiles"]}
    checks["D2"] = {"tile": "fp32.b_onebit_b20_pi", "twin": "fp32.cal_pi_b20", "points_identical": 27,
                    "bytes_identical": man7["fp32.b_onebit_b20_pi"]["sha256"]["whole"] == calm["fp32.cal_pi_b20"]["sha256"]}
    pr = RR.prices()
    checks["RR"] = check_rr_replication(pr)
    # the arm's counts file
    rows = {}
    for k, r in c7["rows"].items():
        if k in TILES:
            pts = sorted(new[k]["points"], key=lambda p: p["n0"])
            rows[k] = dict(r)
            rows[k]["points"] = [p for p in pts if p["n0"] in std3]
            rows[k]["mean"] = RK.mean_rows(pts)
            rows[k]["arm_note"] = "Q141(t) M9_27pt: mean over the 27 points of RECOUNT-RULE.md section 1 (counts-s7-27.json); points: the three standard ones"
        else:
            rows[k] = r
    arm_counts = os.path.join(HERE, "counts-arm-s7.json")
    json.dump({"_bench": c7["_bench"], "_units": c7["_units"],
               "_points": "Q141(t) arm M9_27pt: the eight S rows' mean is over the 27 points of RECOUNT-RULE.md section 1 (their "
                          "points: the three standard ones); every other row is counts-blind7.json's, unchanged", "rows": rows},
              open(arm_counts, "w"), indent=1)
    armd = os.path.join(HERE, "arm")
    pred = {}
    for card in CARDS:
        a = run_predictor(POOL7, card, arm_counts, armd)
        f = load(os.path.join(POOL7, f"predictions-blind7-{card}.json"))
        diff = [k for k in f["tiles"] if k not in TILES and canon(a["tiles"][k]) != canon(f["tiles"][k])]
        if diff or set(a["tiles"]) != set(f["tiles"]):
            stop(f"{card}: the 53 other tiles' predictions differ from the frozen file: {diff[:5]}")
        for hk in ("m9_sha256", "m8_sha256", "m7_sha256", "m6_sha256", "manifest_sha256", "predict_blind7_sha256", "fit_m9_sha256"):
            if a[hk] != f[hk]:
                stop(f"{card}: {hk} differs from the frozen file's")
        pred[card] = (f, a)
        checks[f"others_identical|{card}"] = {"tiles": len(f["tiles"]) - len(TILES), "identical": True}
    # pool 6's two byte twins (post hoc: M9 was fitted on pool 6's rows)
    c6 = load(os.path.join(POOL6, "counts-blind6.json"))
    man6 = {m["name"]: m for m in load(os.path.join(POOL6, "blind6.json"))["tiles"]}
    rows6, twin_check = {}, {}
    for k, r in c6["rows"].items():
        if k in TWINS6:
            ct = TWINS6[k]
            if man6[k]["sha256"]["whole"] != calm[ct]["sha256"]:
                stop(f"{k} and {ct} are not byte twins")
            pts = [cal[ct]["points"][n] for n in p27]
            twin_check[k] = {"twin": ct, "bytes_identical": True,
                             "three_points_identical": all(canon(cal[ct]["points"][p["n0"]]) == canon(p) for p in r["points"]),
                             "three_points_nets_map_identical": all(cal[ct]["points"][p["n0"]]["vpu"]["nets_map"] == p["vpu"]["nets_map"]
                                                                    for p in r["points"])}
            rows6[k] = dict(r)
            rows6[k]["points"] = [p for p in pts if p["n0"] in std3]
            rows6[k]["mean"] = RK.mean_rows(pts)
            rows6[k]["arm_note"] = f"Q141(t): mean over the 27 committed points of its byte twin {ct}"
        else:
            rows6[k] = r
    tw = os.path.join(armd, "pool6-twins")
    os.makedirs(tw, exist_ok=True)
    c6_27 = os.path.join(tw, "counts-pool6-twins-27.json")
    json.dump({"_bench": c6["_bench"], "_units": c6["_units"],
               "_points": "Q141(t), post hoc: pool 6's counts-blind6.json with fp32.b_onebit_b20_third and fp32.b_onebit_b12_third at "
                          "the mean of their byte twins' committed 27 points (cal_third_b20, cal_third_b12)", "rows": rows6},
              open(c6_27, "w"), indent=1)
    checks["pool6_twins_posthoc"] = twin_check
    p6 = {}
    for card in CARDS:
        p6[card] = (run_predictor(POOL6, card, os.path.join(POOL6, "counts-blind6.json"), os.path.join(tw, "3pt")),
                    run_predictor(POOL6, card, c6_27, os.path.join(tw, "27pt")))
    # e(N) per S tile
    rr = RR.merged([counts27])
    rec7 = {"_note": "Q141(t): e(N) per pool-7 S tile at M9's frozen float prices by recount_rule.py's functions (RECOUNT-RULE.md "
                     "section 2), bound 0.10 W; the arm is fixed at N = 27 (REGISTRATION.md section 2)", "bound_w": RR.BOUND_W,
            "input": "counts-s7-27.json", "tiles": {}}
    L = ["Q141(t): e(N) per pool-7 S tile by RECOUNT-RULE.md's rule (recount_rule.py's functions), at M9's frozen prices; bound "
         f"e(N) <= {RR.BOUND_W:.2f} W", "",
         f"{'tile':32s} {'N':>3s} {'mean W':>7s} {'3pt-N W':>8s} {'se_samp':>8s} {'se_intl':>8s} {'e(N)':>6s}  met"]
    for k in TILES:
        by_n, first = per_tile_by_n(rr[k], (9, 27), pr, False)
        e27 = by_n["27"]["e_w"]
        t = {"type": rr[k]["type"], "by_N": by_n, "first_N_meeting_bound": first, "e9_over_e27": by_n["9"]["e_w"] / e27,
             "projected_N_by_inverse_sqrt_law": None if by_n["27"]["met"] else int(math.ceil(27 * (e27 / RR.BOUND_W) ** 2)),
             "in_S7": k in S7}
        rec7["tiles"][k] = t
        for n in ("9", "27"):
            e = by_n[n]
            L.append(f"{k:32s} {n:>3s} {e['mean_w']:7.3f} {e['three_point_minus_N_w']:+8.3f} {e['se_sample_w']:8.3f} "
                     f"{e['se_interleaved_w']:8.3f} {e['e_w']:6.3f}  {'yes' if e['met'] else 'no'}")
    met27 = [k for k in TILES if rec7["tiles"][k]["by_N"]["27"]["met"]]
    rec7["met_at_27"] = met27
    rec7["above_bound_at_27"] = [k for k in TILES if k not in met27]
    L += ["", f"meeting the bound at 27: {len(met27)} of {len(TILES)} ({', '.join(met27) if met27 else 'none'})",
          "projected N by the 1/sqrt(N) law for the others (planning only): " + ", ".join(
              f"{k.split('.', 1)[1]} {rec7['tiles'][k]['projected_N_by_inverse_sqrt_law']}" for k in rec7["above_bound_at_27"])]
    json.dump(rec7, open(os.path.join(HERE, "recount-s7.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(HERE, "recount-s7.txt"), "w").write("\n".join(L) + "\n")
    # arm-s7.json
    m9 = load(os.path.join(M9D, "m9.json"))
    s1 = m9["families"]["float"]["card1_scale_by_format"]
    out = {"_note": "Q141(t): the reported arm M9_27pt of REGISTRATION.md (0830f65b), frozen before any pool-7 data. P3 = M9's frozen "
                    "primary D (tools/claims-v3/kinds/blind7/predictions-blind7-<card>.json, 75802201); P27 = M9's D on the 27-point "
                    "launch averages (arm/predictions-<card>.json); k = P3 - P27, the three-point count's error at M9's prices; "
                    "u = s x e(27), its 1-s.e. counting error (s = 1 on aifoundry3, M9's card1_scale_by_format on card 1). "
                    "Reported only: M9's frozen predictions stay primary.",
           "registration": "0830f65b", "parents": {"pool7": "75802201", "pool7_notes": "3c9bb2ba", "m9": "1f244140",
                                                    "m9_registration": "8dfafae3", "recount_rule": "b4444dd4", "pilot27": "b85ca0f9"},
           "s7": list(S7), "beside": [A1P5], "checks": checks, "cards": {}, "pool6_twins_posthoc": {}, "files": {}}
    for card in CARDS:
        f, a = pred[card]
        cs = {}
        for k in TILES:
            t = k.split(".", 1)[0]
            s = 1.0 if card == "aifoundry3" else s1[t]
            fr, ar = f["tiles"][k], a["tiles"][k]
            e27 = rec7["tiles"][k]["by_N"]["27"]["e_w"]
            cs[k] = {"type": t, "priority": fr["priority"], "in_S7": k in S7,
                     "P3_w": fr["M9"]["D_w"], "P3_95": fr["M9"]["D_95"], "P27_w": ar["M9"]["D_w"], "P27_95": ar["M9"]["D_95"],
                     "k_w": round(fr["M9"]["D_w"] - ar["M9"]["D_w"], 4), "u_w": round(s * e27, 4), "card_scale": s,
                     "e27_w": round(e27, 4), "e9_w": round(rec7["tiles"][k]["by_N"]["9"]["e_w"], 4),
                     "rule_three_point_minus_27_w": round(s * rec7["tiles"][k]["by_N"]["27"]["three_point_minus_N_w"], 4),
                     "dT3_c": fr["M9"]["dT_win_c"], "dT27_c": ar["M9"]["dT_win_c"], "dT3_95": fr["M9"]["dT_win_95"],
                     "dT27_95": ar["M9"]["dT_win_95"], "k_dT_c": round(fr["M9"]["dT_win_c"] - ar["M9"]["dT_win_c"], 3),
                     "S3_w": fr["M9"]["S_w"], "S27_w": ar["M9"]["S_w"],
                     "beside_k_w": {m: round(fr[m]["D_w"] - ar[m]["D_w"], 4) for m in ("M8", "M7", "M6")}}
        out["cards"][card] = cs
        q3, q27 = p6[card]
        tw6 = {}
        for k, ct in TWINS6.items():
            t = "fp32"
            s = 1.0 if card == "aifoundry3" else s1[t]
            calrec = load(os.path.join(RRD, "recount-rule.json"))["tiles"][ct]["by_N"]["27"]
            tw6[k] = {"twin": ct, "P3_w": q3["tiles"][k]["M9"]["D_w"], "P27_w": q27["tiles"][k]["M9"]["D_w"],
                      "k_w": round(q3["tiles"][k]["M9"]["D_w"] - q27["tiles"][k]["M9"]["D_w"], 4), "u_w": round(s * calrec["e_w"], 4),
                      "rule_three_point_minus_27_w": round(s * calrec["three_point_minus_N_w"], 4),
                      "dT3_c": q3["tiles"][k]["M9"]["dT_win_c"], "dT27_c": q27["tiles"][k]["M9"]["dT_win_c"],
                      "note": "post hoc: M9 was fitted on pool 6's rows (E153, E157)"}
        out["pool6_twins_posthoc"][card] = tw6
    # the hand-off form tools/claims-v3/e163/score_e163.py --arm27 reads: {tile: the arm's D on that card}
    for card in CARDS:
        json.dump({k: out["cards"][card][k]["P27_w"] for k in TILES}, open(os.path.join(armd, f"arm27-{card}.json"), "w"),
                  indent=1, sort_keys=True)
    for p in [counts27, arm_counts, c6_27, os.path.join(HERE, "recount-s7.json")] + [
            os.path.join(armd, f"arm27-{c}.json") for c in CARDS] + [
            os.path.join(armd, f"predictions-{c}.json") for c in CARDS] + [
            os.path.join(tw, d, f"predictions-{c}.json") for d in ("3pt", "27pt") for c in CARDS]:
        out["files"][os.path.relpath(p, HERE)] = fsha(p)
    for p in (os.path.join(M9D, "predict_blind7.py"), os.path.join(M9D, "m9.json"), os.path.join(RRD, "recount_rule.py"),
              os.path.join(BENCH_SRC, "run_kinds.py"), os.path.join(POOL7, "counts-blind7.json")):
        out["files"][rel(p)] = fsha(p)
    json.dump(out, open(os.path.join(HERE, "arm-s7.json"), "w"), indent=1, sort_keys=True)
    # a readable table
    T = ["Q141(t): the arm M9_27pt, frozen before any pool-7 data (REGISTRATION.md, 0830f65b). W of D over the type's zeros at 600 MHz.",
         "P3 = M9 as frozen (primary); P27 = M9 on 27-point counts; k = P3 - P27 +- u (1 s.e., the counting error left at 27 points).", ""]
    for card in CARDS:
        T.append(f"{card}:")
        T.append(f"  {'tile':32s} {'P3':>8s} {'P27':>8s} {'k':>7s} {'u':>6s}  {'dT3':>6s} {'dT27':>6s}  M8/M7/M6 k")
        for k in TILES:
            r = out["cards"][card][k]
            T.append(f"  {k:32s} {r['P3_w']:8.3f} {r['P27_w']:8.3f} {r['k_w']:+7.3f} {r['u_w']:6.3f}  {r['dT3_c']:6.3f} {r['dT27_c']:6.3f}  "
                     + " / ".join(f"{r['beside_k_w'][m]:+.3f}" for m in ("M8", "M7", "M6")))
        ks = [out["cards"][card][k]["k_w"] for k in S7]
        T.append(f"  S7: mean k {sum(ks) / len(ks):+.3f} W, rms k {math.sqrt(sum(x * x for x in ks) / len(ks)):.3f} W, range "
                 f"{min(ks):+.3f} to {max(ks):+.3f} W")
        for k, r in out["pool6_twins_posthoc"][card].items():
            T.append(f"  post hoc, pool 6's {k} (twin {r['twin']}): P3 {r['P3_w']:.3f}, P27 {r['P27_w']:.3f}, k {r['k_w']:+.3f} +- "
                     f"{r['u_w']:.3f} W (the rule's stage-price 3pt-27: {r['rule_three_point_minus_27_w']:+.3f})")
        T.append("")
    T.append("checks: C (every point's check_mismatch 0), D1 (three standard points and mean reproduced, 8 of 8), D2 (b20_pi's 27 points = "
             "cal_pi_b20's committed 27), RR (the per-tile block reproduces recount-rule.json: "
             f"{checks['RR']['fields_compared']} fields), the 53 other tiles' predictions identical on both cards")
    open(os.path.join(HERE, "arm-s7.txt"), "w").write("\n".join(T) + "\n")
    print("\n".join(L))
    print()
    print("\n".join(T))


if __name__ == "__main__":
    main()
