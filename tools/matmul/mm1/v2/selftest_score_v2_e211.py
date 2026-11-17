#!/usr/bin/env python3
"""The self-test of score_v2_e211.py (Q206, lane score-v2-e211): stand-in days made from the frozen forecasts, each with what the scorer must
print stated before the run by arithmetic on the frozen files alone (never by the scorer's code), then the scorer run on each day as a
separate process and its output checked. Standard library only. The stand-in days are written under --tmp (outside the repository and
outside the round's lane folders, so no never-run search ever reads a stand-in record); nothing in the repository is written.

    /usr/bin/python3 -I -B tools/matmul/mm1/v2/selftest_score_v2_e211.py --base REPO_TOP --tmp EMPTY_DIR \
        [--registered tools/claims-v3/e211/score_e211.py]     (also: E211's registered scorer on the same days, for the cross-check)

Days: A every run at MM1-v2's forecast (family C at v2-C1); B at MM1-v1's (family C at v1-C1); C at F1's; D day A with a common -2% offset on
the wall cycles of every gemmLn run of families X and W (T4 FAIL, A1 applies: the control-corrected ratios equal MM1-v2's); E day A without
family C and with one run whose host record differs (set aside); G day A with every run's W over idle x 1.05; R a copy of forecasts-e211.json
with one number changed (REFUSED, exit 4). Exit 0 = PASS.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import hashlib
import json
import math
import os
import subprocess
import sys

V1 = "tools/claims-v3/e211/forecast-e211.json"
V2 = "tools/matmul/mm1/v2/forecasts-e211.json"
PTS = "tools/claims-v3/e211/points-e211.json"
RULES = "tools/claims-v3/e211/rules-e211.json"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def numbers(base):
    f1 = json.load(open(os.path.join(base, V1)))
    f2 = json.load(open(os.path.join(base, V2)))
    pts = json.load(open(os.path.join(base, PTS)))
    return f1, f2, pts


def col(f1, f2, pid, model):
    """(wall, mean, t, W over idle) of a model at a point; family C reads the C1 column for v2 and v1"""
    fam = f1["points"][pid]["family"]
    if model == "v2":
        x = f2["points"][pid]["C"]["C1"] if fam == "C" else f2["points"][pid]["v2"]
        return x["cycles_per_op_wall"], x["cycles_per_op_mean"], x["seconds_per_gemm"], x["W_over_idle"]
    if model == "v1":
        x = f1["points"][pid]["C"]["C1"] if fam == "C" else f1["points"][pid]["MM1"]
        return x["cycles_per_op_wall"], x["cycles_per_op_mean"], x["seconds_per_gemm"], x["W_over_idle"]
    if model == "F1":
        f = f1["points"][pid]["F"]
        return f["F1_cycles_per_op"], f["F1_cycles_per_op"], f["F1_seconds_per_gemm"], f["F1_W_over_idle"]
    raise ValueError(model)


def make_day(f1, f2, pts, model, wall_mult=None, w_mult=1.0, drop_block=None, bad_record_n=None):
    P = {p["id"]: p for p in pts["points"] + pts["smoke"]}
    runs, smoke = [], []
    for o in pts["order"]:
        pid, blk = o["point"], o["block"]
        if drop_block and blk == drop_block:
            continue
        p = P[pid]
        wall, mn, t, W = col(f1, f2, pid, model)
        if wall_mult and blk in ("X", "W") and p["arm_family"] == "gemmLn":
            wall *= wall_mult
        W *= w_mult
        rec = {"arm": p["arm"], "minions": 1024, "shire_mask": "0xffffffff"}
        rec["type"] = p["format"]
        if bad_record_n is not None and o["n"] == bad_record_n:
            rec["minions"] = 512
        walk = None
        if p["host"] == "rgm211":
            nm = "nm" if p["arm_family"] == "gemmLn" else "mn"
            walk = {"names": [nm] * 3, "ok": [True] * 3, "launches_bad": 0}
        run = {"point": pid, "block": blk, "pair": o["pair"], "n": o["n"], "t_gemm_s": t, "cycles_per_op": mn,
               "cycles_gemm": wall * p["ops_per_minion_per_gemm"], "p_work_w": 24.0 + W, "p_rest_w": 24.0, "die_start_c": 50.0,
               "mhz_min": 600.0, "mhz_max": 600.0, "checks": ["exact"], "record": rec, "walk": walk,
               "gate": f"GATE OK: {p['arm_family']}: {p['kernel']}"}
        if blk == "smoke":
            run["check_cycles_per_op"] = mn
            smoke.append(run)
        else:
            runs.append(run)
    return {"experiment": "E211", "arms": {"A": {"smoke": {"runs": smoke}, "runs": runs}}}


def write_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)   # one key a line: no line ever holds a host record whole
        f.write("\n")


def run_scorer(py, scorer, base, tmp, name, data_path, v2_path=None, regscore=None):
    cfg = {"base": ".", "files": {"data": [data_path, sha(data_path)], "points": [PTS, sha(os.path.join(base, PTS))],
                                  "rules": [RULES, sha(os.path.join(base, RULES))], "v1": [V1, sha(os.path.join(base, V1))],
                                  "v2": [v2_path or V2, sha(v2_path if v2_path else os.path.join(base, V2))]},
           "labels": {"v2": "stand-in day " + name}}
    if regscore:
        cfg["files"]["regscore"] = [regscore, sha(regscore)]
    cp = os.path.join(tmp, f"cfg-{name}.json")
    write_json(cp, cfg)
    out = os.path.join(tmp, f"out-{name}.json")
    r = subprocess.run([py, "-I", "-B", scorer, "--config", cp, "--out", out, "--base", base], capture_output=True, text=True)
    o = json.load(open(out)) if (r.returncode == 0 and os.path.exists(out)) else None
    return r.returncode, o, r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--tmp", required=True)
    ap.add_argument("--scorer", default=None)
    ap.add_argument("--registered", default=None)
    a = ap.parse_args()
    base, tmp = os.path.abspath(a.base), os.path.abspath(a.tmp)
    if os.listdir(tmp):
        print(f"selftest: REFUSED: {tmp} is not empty")
        return 4
    if base == tmp or tmp.startswith(base + os.sep):
        print("selftest: REFUSED: --tmp is inside --base")
        return 4
    scorer = os.path.abspath(a.scorer or os.path.join(os.path.dirname(os.path.abspath(__file__)), "score_v2_e211.py"))
    py = "/usr/bin/python3"
    f1, f2, pts = numbers(base)
    rules = json.load(open(os.path.join(base, RULES)))
    ids_n = [p["id"] for p in pts["points"] if p["arm_family"] == "gemmLn"]
    wp = [p["pair"] for p in pts["points"] if p["family"] == "W" and p["arm_family"] == "gemmLn"]
    tieT = rules["H"]["tie_ln_abs_cycles"]
    results = []

    def check(name, cond, what):
        what = what.replace(tmp, "<tmp>").replace(base, "<repo>")
        results.append((name, bool(cond), what))
        print(f"{'ok  ' if cond else 'FAIL'} {name}: {what}")

    def regrun(name, data_path):
        if not a.registered:
            return None
        out = os.path.join(tmp, f"reg-{name}.json")
        r = subprocess.run([py, "-I", "-B", os.path.join(base, a.registered), data_path, "--out", out], capture_output=True, text=True)
        return out if (r.returncode == 0 and os.path.exists(out)) else None

    # stated before any run: how many rgm211 points MM1-v2 and MM1-v1 part by more than the cycles tie
    differ = [pid for pid in ids_n if abs(math.log(col(f1, f2, pid, "v2")[0] / col(f1, f2, pid, "v1")[0])) > tieT]
    v2_wall_vs_v1 = math.sqrt(sum((col(f1, f2, pid, "v2")[0] / col(f1, f2, pid, "v1")[0] - 1) ** 2 for pid in ids_n) / len(ids_n))
    days = {}
    for name, kw in (("A", {"model": "v2"}), ("B", {"model": "v1"}), ("C", {"model": "F1"}), ("D", {"model": "v2", "wall_mult": 0.98}),
                     ("E", {"model": "v2", "drop_block": "C", "bad_record_n": 14}), ("G", {"model": "v2", "w_mult": 1.05})):
        d = make_day(f1, f2, pts, **kw)
        p = os.path.join(tmp, f"day-{name}.json")
        write_json(p, d)
        days[name] = p
    outs = {}
    for name, p in days.items():
        reg = regrun(name, p)
        rc, o, _ = run_scorer(py, scorer, base, tmp, name, p, regscore=reg)
        outs[name] = o
        check(f"{name} runs", rc == 0 and o is not None, f"the scorer exits 0 (rc {rc})")
    A, B, C, D, E, G = (outs[k] for k in "ABCDEG")
    if A:
        ag = A["aggregates"]["all_26_C1"]
        for q in ("wall", "mean", "t", "W_given", "W_fc", "J_given", "J_fc", "Jr_given", "Jr_fc"):
            check("A v2 zero", ag[q]["v2"]["rms"] < 1e-9, f"day A: MM1-v2's {q} rms {ag[q]['v2']['rms']:.2e} over 26 points (stated: 0)")
        x = A["aggregates"]["rgm211_12"]["wall"]["v1"]["rms"]
        check("A v1 wall", abs(x - math.sqrt(sum((col(f1, f2, pid, "v1")[0] / col(f1, f2, pid, "v2")[0] - 1) ** 2 for pid in ids_n) / 12)) < 1e-12,
              f"day A: MM1-v1's wall rms at rgm211's points {x:.6f} = rms(v1 / v2 - 1) from the frozen files")
        h = A["head_to_head_cases"]["rgm211_12"]["wall"]["v2_vs_v1"]
        check("A h2h", h["first_closer"] == len(differ) and h["second_closer"] == 0,
              f"day A: MM1-v2 closer at {h['first_closer']} of 12 rgm211 points, MM1-v1 at {h['second_closer']} (stated {len(differ)} and 0)")
        rb = A["ratio_wall"]["raw"]
        check("A ratio", rb["aggregates"]["v2"]["rms"] < 1e-12 and rb["inside_W1_tol"]["v2"]["inside"] == 10,
              f"day A: MM1-v2's wall ratio rms {rb['aggregates']['v2']['rms']:.2e}, inside 0.05 at {rb['inside_W1_tol']['v2']['inside']} of 10")
        check("A T4", A["controls"]["T4_reading"] == "PASS" and not A["controls"]["A1_applies"], f"day A: T4 {A['controls']['T4_reading']}, A1 {A['controls']['A1_applies']}")
        check("A coverage", A["coverage"]["points_with_data"] == 26 and A["coverage"]["runs_kept"] == 38 and not A["set_aside"],
              f"day A: {A['coverage']['points_with_data']} points, {A['coverage']['runs_kept']} runs, {len(A['set_aside'])} set aside (stated 26, 38, 0)")
        fc = A["family_C"]
        check("A family C", all(abs(fc[k]["ln_error"]["wall"]["v2-C1"]) < 1e-12 and abs(fc[k]["ln_error"]["J"]["v2-C1"]) < 1e-12 for k in fc),
              "day A: family C's measured ratios equal v2-C1's (wall and J)")
        check("A consistency", A["pairs_input_consistency_max_rel"] < 1e-9, f"the frozen pair ratios equal the frozen points' ratios ({A['pairs_input_consistency_max_rel']:.2e})")
        if a.registered:
            cc = A.get("crosscheck_registered") or {}
            check("A registered", cc and all(x["equal"] for x in cc["head_to_head"].values()) and cc["absolute_errors"]["max_abs_diff"] < 1e-12
                  and cc["pairs_measured"]["max_rel_diff"] < 1e-12, f"day A: against E211's registered scorer: {json.dumps(cc.get('head_to_head'))[:300]}")
    if B:
        ag = B["aggregates"]["all_26_C1"]
        check("B v1 zero", all(ag[q]["v1"]["rms"] < 1e-9 for q in ("wall", "mean", "t", "W_given", "J_given", "J_fc")), "day B: MM1-v1's errors 0")
        x = B["aggregates"]["rgm211_12"]["wall"]["v2"]["rms"]
        check("B v2 wall", abs(x - v2_wall_vs_v1) < 1e-12, f"day B: MM1-v2's wall rms at rgm211's points {x:.6f} = rms(v2 / v1 - 1) {v2_wall_vs_v1:.6f}")
        h = B["head_to_head_cases"]["rgm211_12"]["wall"]["v2_vs_v1"]
        check("B h2h", h["second_closer"] == len(differ) and h["first_closer"] == 0, f"day B: MM1-v1 closer at {h['second_closer']} (stated {len(differ)})")
        if a.registered:
            cc = B.get("crosscheck_registered") or {}
            check("B registered", cc and all(x["equal"] for x in cc["head_to_head"].values()) and cc["absolute_errors"]["max_abs_diff"] < 1e-12,
                  f"day B: against E211's registered scorer: T4 {cc.get('T4')}")
    if C:
        ag = C["aggregates"]["W_X_24"]
        check("C F1 zero", all(ag[q]["F1"]["rms"] < 1e-9 for q in ("wall", "mean", "t", "W_given", "W_fc", "J_given", "J_fc")), "day C: F1's errors 0")
        h = C["ratio_wall"]["raw"]["head_to_head"]["v2_vs_F1"]
        n_part = sum(1 for p in wp if abs(math.log(f2["pairs"][p]["ratio_wall"]["v2"] / f1["pairs"][p]["ratio_wall"]["F1"])) > rules["H"]["tie_ln_cycles"])
        check("C ratio h2h", h["second_closer"] == n_part and h["first_closer"] == 0, f"day C: F1 closer on the ratio at {h['second_closer']} pairs (stated {n_part})")
    if D:
        c = D["controls"]
        check("D T4/A1", c["T4_reading"] == "FAIL" and c["A1_applies"] and abs(c["c_hat_ln"] - math.log(0.98)) < 1e-12,
              f"day D: T4 {c['T4_reading']}, A1 {c['A1_applies']}, c_hat {c['c_hat_ln']:.6f} (stated FAIL, True, {math.log(0.98):.6f})")
        rc_, rr_ = D["ratio_wall"]["control_corrected"], D["ratio_wall"]["raw"]
        check("D corrected", rc_["aggregates"]["v2"]["rms"] < 1e-12, f"day D: corrected ratio rms for MM1-v2 {rc_['aggregates']['v2']['rms']:.2e} (stated 0)")
        check("D raw", abs(rr_["aggregates"]["v2"]["bias"] + math.log(0.98)) < 1e-12,
              f"day D: raw ratio bias for MM1-v2 {rr_['aggregates']['v2']['bias']:+.6f} (stated {-math.log(0.98):+.6f})")
        check("D basis", D["ratio_wall"]["E211_basis"] == "A1 control-corrected", f"day D: basis {D['ratio_wall']['E211_basis']}")
        if a.registered:
            cc = D.get("crosscheck_registered") or {}
            check("D registered", cc and all(x["equal"] for x in cc["head_to_head"].values()) and cc["T4"].get("A1_registered") is True,
                  f"day D: registered T4 {cc.get('T4')}")
    if E:
        cv = E["coverage"]
        check("E coverage", set(cv["no_data"]) == {"c01c", "c02c", "w03n"} and len(E["set_aside"]) == 1 and "w03" not in E["ratio_wall"]["raw"]["per_pair"]
              and E["R0_own_reading"]["reads"] == "FAIL",
              f"day E: NO DATA {cv['no_data']}, set aside {len(E['set_aside'])}, w03 not in the ratios, R0 own reading {E['R0_own_reading']['reads']}")
        check("E family C", all(v["measured"]["wall"] is None for v in E["family_C"].values()), "day E: family C has no measured ratio")
    if G:
        ag = G["aggregates"]["all_26_C1"]
        stated = 1.0 / 1.05 - 1.0
        check("G J", abs(ag["J_fc"]["v2"]["bias"] - stated) < 1e-12 and ag["J_fc"]["v2"]["rms"] - abs(stated) < 1e-12,
              f"day G: MM1-v2's J over idle error {ag['J_fc']['v2']['bias']:+.6f} at every point (stated {stated:+.6f})")
        check("G time", ag["wall"]["v2"]["rms"] < 1e-12, "day G: time untouched")
        check("G J ratio", G["ratio_other"]["J"]["aggregates"]["v2"]["rms"] < 1e-12, "day G: the J ratio unchanged (the same factor on both walks)")
    # R: a changed forecast file is refused
    bad = os.path.join(tmp, "forecasts-e211-changed.json")
    o2 = copy.deepcopy(f2)
    o2["points"]["w06n"]["v2"]["cycles_per_op_wall"] *= 1.001
    write_json(bad, o2)
    rc, o, outtxt = run_scorer(py, scorer, base, tmp, "R", days["A"], v2_path=bad)
    check("R refused", rc == 4 and "REFUSED" in outtxt, f"a changed copy of forecasts-e211.json: rc {rc} ({outtxt.strip()[:120]})")
    n_ok = sum(1 for _, ok, _ in results if ok)
    print(f"SELFTEST {'PASS' if n_ok == len(results) else 'FAIL'}: {n_ok} of {len(results)} checks as stated "
          f"(interpreter {sys.executable} {sys.version.split()[0]}; registered scorer {'run' if a.registered else 'NOT RUN'})")
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
