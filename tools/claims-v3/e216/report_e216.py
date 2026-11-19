#!/usr/bin/env python3
"""E216 (Q227, lane fix-e216, Thu 19 Nov 2026, before any E216 datum): THE REPORTED READINGS OF E216-amendment-1.md A2 AND A4, made from the
frozen scorer's own output. Standard library only. Every figure it writes is REPORTED: never a registered verdict, never a rule.

    python3 -I -B tools/claims-v3/e216/report_e216.py <scored-e216.json> --out <reported-e216.json>
        THE INPUT is score_e216.py's own output on the day's data (runbook step 13 writes it as RB_OUT/score/scored-e216.json).
        A2 (verify-e216's F2): MM1-v3.1's per-point rules T1-T3 and E1-E4 over the 30 registered points OUTSIDE family G and over family G's 10
           alone, from the scorer's own cells (scored > points > <id> > cells_MM1-v3.1) by the scorer's own verdict() (PASS with at least 90% of
           the scored points within band, TOO FEW under 10, NO DATA with none), beside the registered verdicts over all 40, which are re-made from
           the same cells first and must equal the scorer's (else MISMATCH, and nothing else of A2 is written).
        A4 (verify-e216's F4): every head-to-head's tallies BY DISTINCT CONFIGURATION beside its point-level verdict. The cases are the scorer's
           own, re-made from scored > points > <id> > measured_route_c by the scorer's predicted() exactly as score() makes them, and their
           point-level tallies must equal the scorer's (else MISMATCH for that rule). A configuration is rules_e216.py's config_key(): the two
           forecasters' frozen per-op values at 799.0 MHz (wall cycles an op for 'wall'; W over idle at their own seconds for 'Wg' and 'Jf'),
           rounded to 6 decimals, with the quantity (and a case scored in watts apart). A configuration's d is the mean of its cases' d (the
           scorer's d: |ln(measured / second)| - |ln(measured / first)|, or the watts form), decided when |d| exceeds the cases' tie; the tallies
           (first closer, second closer, ties) and the exact two-sided sign test's p over the decided configurations are printed, never a verdict.
    python3 -I -B tools/claims-v3/e216/report_e216.py --selftest <out.json>
        stand-in days through the frozen scorer and this file: the scorer's own ten (its standin_days), and five of this amendment's (lnc_at_G:
        family G's W over idle at 'v3.1 + gemmLnc term', every other figure at MM1-v3.1; p1_4, p1_5, p1_5w and p1_ctrl: Y pairs moved 1% apart in
        ln each way). Checks: the re-made registered verdicts and point-level tallies equal the scorer's on every day; the distinct configurations
        counted on the full day equal rules-e216.json > power_shared_REPORTED's n_configurations; the words each day must read (A1's P1 at 4, 5,
        5 with one wrong, 6 with a control split; A2's reading with the gemmLnc term right at G). Writes the JSON (no time in it) and exits 0 on
        PASS, 1 otherwise.
It refuses (exit 4) when the scorer is not at its pin or the scorer's own pins fail. Interpreter: /usr/bin/python3 3.12.3 -I -B.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCORER = ("score_e216.py", "9c61d06cbb6d11ec00a6d7f26d25da48160857d0ddfefe5b403dd89fba3d3c4e")
QS = ("T1", "T2", "T3", "E1", "E2", "E3", "E4")
H2H_RULES = ("H1t", "H1w", "H1t-twins", "H1w-twins", "H2w", "H2f", "H3", "H4")
REST = 23.19   # the stand-in days' rest, the scorer's own


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def scorer():
    p = os.path.join(HERE, SCORER[0])
    if sha(p) != SCORER[1]:
        print("report_e216: REFUSED, score_e216.py is not at its pin")
        sys.exit(4)
    spec = importlib.util.spec_from_file_location("score_e216", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.check_pins()
    return m


def config_key(FC, pid, a, b, q, f="799.0"):
    """rules_e216.py's config_key(), the same definition (standard library here)"""
    def per_op(m):
        x = FC[pid][f]["forecasts"][m]
        v = x["cycles_per_op_wall"] if q == "wall" else x.get("W_over_idle")
        return None if v is None else round(v, 6)
    return (per_op(a), per_op(b), q)


def cases(S, P, FC, R, scored, h):
    """the scorer's own cases of head-to-head h, re-made from its output's route-c figures (score_e216.score()'s loop, unchanged in meaning)"""
    a, b, q, g = S.H2H[h]
    T, LOW = R["ties"], R["low_W"]
    rows = []
    for pid in S.group_ids(P, g):
        m = (scored["points"].get(pid) or {}).get("measured_route_c")
        if not m:
            continue
        fa, fb = S.predicted(FC, pid, "799.0", a, m), S.predicted(FC, pid, "799.0", b, m)
        qq = ("Wg" if P[pid]["family"] == "G" else "wall") if q == "mixed" else q
        meas = {"wall": m["wall"], "Wg": m.get("W"), "Jf": m.get("J_over")}[qq]
        if meas is None or fa.get(qq) is None or fb.get(qq) is None:
            continue
        watts = qq == "Wg" and (meas < LOW or fa[qq] < LOW)
        if watts:
            d = abs(meas - fb[qq]) - abs(meas - fa[qq])
            tie = T["watts_W"]
        else:
            d = abs(math.log(meas / fb[qq])) - abs(math.log(meas / fa[qq]))
            tie = T["cycles_ln"] if qq == "wall" else T["joules_ln"]
        rows.append({"id": pid, "q": qq, "d": d, "tie": tie, "watts": watts, "config": config_key(FC, pid, a, b, qq)})
    return a, b, rows


def by_configuration(S, P, FC, R, scored):
    out = {}
    for h in H2H_RULES:
        a, b, rows = cases(S, P, FC, R, scored, h)
        npos = sum(1 for r in rows if r["d"] > r["tie"])
        nneg = sum(1 for r in rows if r["d"] < -r["tie"])
        nt = len(rows) - npos - nneg
        hs = scored["head_to_head"].get(h) or {}
        same = (npos, nneg, nt) == (hs.get("first_closer"), hs.get("second_closer"), hs.get("ties"))
        rec = {"first": a, "second": b, "registered_verdict": hs.get("verdict"), "point_level": {"first_closer": npos, "second_closer": nneg,
               "ties": nt, "equal_to_the_scorer": same}}
        if not same:
            rec["REPORTED"] = "MISMATCH: the re-made cases do not give the scorer's tallies; no configuration tally is written"
            out[h] = rec
            continue
        groups = {}
        for r in rows:
            groups.setdefault((r["config"], r["watts"]), []).append(r)
        cf = []
        for (k, watts), rs in sorted(groups.items(), key=lambda kv: (str(kv[0][0]), kv[0][1])):
            d = sum(r["d"] for r in rs) / len(rs)
            tie = max(r["tie"] for r in rs)
            word = "first closer" if d > tie else ("second closer" if d < -tie else "tie")
            cf.append({"configuration": [k[0], k[1], k[2]], "watts": watts, "points": [r["id"] for r in rs], "mean_d": d, "tie": tie,
                       "reads": word})
        fp = sum(1 for c in cf if c["reads"] == "first closer")
        sp = sum(1 for c in cf if c["reads"] == "second closer")
        rec["by_configuration_REPORTED"] = {"configurations": len(cf), "first_closer": fp, "second_closer": sp,
                                            "ties": len(cf) - fp - sp, "p_two_sided": (S.sign_p(fp, sp) if (fp + sp) else None),
                                            "note": "REPORTED (E216-amendment-1.md A4): never a verdict; the registered verdict is the point-level one",
                                            "each": cf}
        out[h] = rec
    return out


def without_g(S, P, scored):
    pts = scored["points"]
    reg = S.group_ids(P, "registered")
    ids = {"registered_40_re_made": reg, "without_G_30": [i for i in reg if P[i]["family"] != "G"],
           "G_alone_10": [i for i in reg if P[i]["family"] == "G"]}
    res = {}
    for name, sel in ids.items():
        res[name] = {q: S.verdict([pts[i]["cells_MM1-v3.1"].get(q) for i in sel if "cells_MM1-v3.1" in (pts.get(i) or {})]) for q in QS}
    same = all((res["registered_40_re_made"][q].get("verdict"), res["registered_40_re_made"][q].get("pass"), res["registered_40_re_made"][q].get("n"))
               == ((scored["rules"].get(q) or {}).get("verdict"), (scored["rules"].get(q) or {}).get("pass"), (scored["rules"].get(q) or {}).get("n"))
               for q in QS)
    out = {"equal_to_the_scorer": same,
           "note": "REPORTED (E216-amendment-1.md A2): never a verdict; the registered verdicts are the scorer's over all 40 registered points"}
    if same:
        out.update(res)
    else:
        out["REPORTED"] = "MISMATCH: the re-made registered verdicts are not the scorer's; nothing else of A2 is written"
    return out


def report(S, P, FC, R, scored):
    return {"experiment": "E216", "what": "the REPORTED readings of E216-amendment-1.md A2 and A4 (never a registered verdict)",
            "scorer_sha256": SCORER[1], "A2_per_point_rules_REPORTED": without_g(S, P, scored),
            "A4_head_to_heads_by_configuration_REPORTED": by_configuration(S, P, FC, R, scored)}


# ------------------------------------------------------------------------------------------------ the self-test
def day(S, P, FC, wmodel=None, tk=None):
    """one stand-in day in the scorer's stand-in form (one run a point, every figure at MM1-v3.1's 799.0 MHz forecast): wmodel {id: forecaster}
    for W over idle; tk {id: factor} on the point's cycles and seconds"""
    wmodel, tk = wmodel or {}, tk or {}
    smoke = [{"arm": a, "rc": 0, "check": "exact", "good": True} for a in ("1x1x4-fp32-zeros", "1x1x4-fp16-ones", "1x1x4-int8-rnd")]
    runs = []
    for n, pid in enumerate(sorted(P), 1):
        p = P[pid]
        x = S.fcv(FC, pid, "799.0", "MM1-v3.1")
        y = S.fcv(FC, pid, "799.0", wmodel.get(pid, "MM1-v3.1"))
        k = tk.get(pid, 1.0)
        wall, mn, s = x["cycles_per_op_wall"] * k, x["cycles_per_op_mean"] * k, x["seconds_per_gemm"] * k
        T = s / p["ops_per_minion_per_gemm"] * 1e6
        W = y["A_W"] + y["B_W_us"] / T
        v = {"kclock_mhz": 799.0, "cyc_op_max": wall, "cyc_op_mean": mn, "T_op_us": T, "t_pass_s": s, "n_launch": 12, "mhz_min": 799.0,
             "mhz_mean": 799.0, "dP_w": W, "p_mean_w": REST + W, "J_pass_over": W * s, "J_pass_with": (REST + W) * s}
        runs.append({"arm": pid, "role": "arm", "form": "burst", "i": n, "ran": True, "shires": p["mask"], "type": p["fmt"], "minions": p["minions"],
                     "checks": ["exact"], "capped": False, "frac_800_after_step": 1.0, "no_step": False, "primary_view": "win", "views": {"win": v}})
    return [{"card": "a2c0", "smoke": smoke, "runs": runs}]


def pairs_moved(S, P, FC, right=(), wrong=()):
    """the named Y pairs moved 1% apart in ln each way (0.02 in ln between the two): in the contention term's predicted order for 'right', against
    it for 'wrong' (a control, predicted equal, moved with its first point the slower)"""
    tk = {}
    for k in list(right) + list(wrong):
        a, b = sorted(i for i in P if P[i].get("pair") == k)
        dp = math.log(S.fcv(FC, a, "799.0", "v3.1+contention")["cycles_per_op_wall"] / S.fcv(FC, b, "799.0", "v3.1+contention")["cycles_per_op_wall"])
        sg = (1.0 if dp >= 0 else -1.0) * (1.0 if k in right else -1.0)
        tk[a], tk[b] = math.exp(0.01 * sg), math.exp(-0.01 * sg)
    return tk


def selftest(S, P, FC, R, outp):
    res, ok = {}, True

    def run(name, datas, want):
        nonlocal ok
        sc = S.score(datas, P, FC, R)
        sc = json.loads(json.dumps(sc, default=float))         # through JSON, as step 13 hands it over
        rp = report(S, P, FC, R, sc)
        a2, a4 = rp["A2_per_point_rules_REPORTED"], rp["A4_head_to_heads_by_configuration_REPORTED"]
        got = {"A2 equal to the scorer": a2["equal_to_the_scorer"],
               "A4 equal to the scorer": all(v["point_level"]["equal_to_the_scorer"] for v in a4.values())}
        for k, w in want.items():
            kind, key = k.split(" ", 1)
            if kind == "rule":
                got[k] = (sc["rules"].get(key) or sc["head_to_head"].get(key) or {}).get("verdict")
                if isinstance(w, list):
                    r_ = sc["rules"].get(key) or {}
                    got[k] = [r_.get("verdict"), r_.get("pass"), r_.get("n")] if key in QS else [r_.get("verdict"), r_.get("decided"), r_.get("ordered_right")]
            elif kind == "noG":
                v = a2.get("without_G_30", {}).get(key, {})
                got[k] = [v.get("verdict"), v.get("pass"), v.get("n")]
            elif kind == "Galone":
                v = a2.get("G_alone_10", {}).get(key, {})
                got[k] = [v.get("verdict"), v.get("pass"), v.get("n")]
            elif kind == "config":
                v = (a4.get(key) or {}).get("by_configuration_REPORTED") or {}
                got[k] = [v.get("configurations"), v.get("first_closer"), v.get("second_closer"), v.get("ties")]
        good = got["A2 equal to the scorer"] and got["A4 equal to the scorer"] and all(got[k] == w for k, w in want.items())
        ok &= bool(good)
        res[name] = {"want": want, "got": got, "ok": bool(good)}
        print(f"{name:14s} {'OK ' if good else 'BAD'} " + "; ".join(f"{k} {got[k]}" for k in got))
        return sc, rp

    # the scorer's own ten stand-in days: the re-made verdicts and tallies equal the scorer's on each
    for case in S.expected(R):
        sc, rp = run("scorer:" + case, S.standin_days(P, FC, case), {})
    # the configurations counted on the full day equal rules-e216.json's power_shared_REPORTED
    sc, rp = run("v31_full", day(S, P, FC), {"noG T1": ["PASS", 30, 30], "noG E1": ["PASS", 30, 30], "Galone E1": ["PASS", 10, 10],
                                              "config H2w": [3, 0, 3, 0]})
    a4 = rp["A4_head_to_heads_by_configuration_REPORTED"]
    ncfg = {h: len({(tuple(c["configuration"]), c["watts"]) for c in a4[h]["by_configuration_REPORTED"]["each"]}) for h in ("H1t", "H2w", "H2f", "H3", "H4")}
    want_cfg = {h: R["power_shared_REPORTED"][h]["n_configurations"] for h in ncfg}
    good = ncfg == want_cfg
    ok &= good
    res["configurations"] = {"want": want_cfg, "got": ncfg, "ok": good}
    print(f"{'configurations':14s} {'OK ' if good else 'BAD'} counted {ncfg}; rules-e216.json {want_cfg}")
    # A2: the gemmLnc term right at family G, MM1-v3.1 everywhere else
    run("lnc_at_G", day(S, P, FC, wmodel={i: "v3.1+lnc" for i in P if P[i]["family"] == "G"}),
        {"rule E1": ["FAIL", 30, 40], "rule E2": ["FAIL", 30, 40], "rule E3": ["FAIL", 30, 40], "rule E4": ["FAIL", 34, 40],
         "rule T1": ["PASS", 40, 40], "noG E1": ["PASS", 30, 30], "noG E2": ["PASS", 30, 30], "noG E3": ["PASS", 30, 30],
         "noG E4": ["PASS", 30, 30], "Galone E1": ["FAIL", 0, 10], "Galone E4": ["FAIL", 4, 10], "rule H2w": "v3.1+lnc BETTER",
         "config H2w": [3, 3, 0, 0]})
    # A1: the pair rule's minimum, 5 decided pairs
    run("p1_4", day(S, P, FC, tk=pairs_moved(S, P, FC, right=("y01", "y02", "y03", "y04"))), {"rule P1": ["TOO FEW", 4, 4]})
    run("p1_5", day(S, P, FC, tk=pairs_moved(S, P, FC, right=("y01", "y02", "y03", "y04", "y05"))), {"rule P1": ["PASS", 5, 5]})
    run("p1_5w", day(S, P, FC, tk=pairs_moved(S, P, FC, right=("y01", "y02", "y03", "y04"), wrong=("y05",))), {"rule P1": ["FAIL", 5, 4]})
    run("p1_ctrl", day(S, P, FC, tk=pairs_moved(S, P, FC, right=("y01", "y02", "y03", "y04", "y05"), wrong=("y07",))), {"rule P1": ["FAIL", 6, 5]})
    json.dump({"ok": bool(ok), "what": "report_e216.py's self-test (E216-amendment-1.md A1, A2, A4), desk, stand-ins only", "scorer_sha256": SCORER[1],
               "cases": res}, open(outp, "w"), indent=1, sort_keys=True)
    print("SELFTEST-REPORT-E216", "PASS" if ok else "FAIL")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scored", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--selftest")
    a = ap.parse_args()
    S = scorer()
    P, FC, R = S.load()
    if a.selftest:
        sys.exit(0 if selftest(S, P, FC, R, a.selftest) else 1)
    if not a.scored or not a.out:
        print("usage: report_e216.py <scored-e216.json> --out <reported-e216.json> | --selftest <out.json>")
        sys.exit(10)
    sc = json.load(open(a.scored))
    rp = report(S, P, FC, R, sc)
    rp["inputs_sha256"] = {os.path.basename(a.scored): sha(a.scored)}
    json.dump(rp, open(a.out, "w"), indent=1, default=float)
    a2 = rp["A2_per_point_rules_REPORTED"]
    print("A2 (REPORTED): the re-made registered verdicts equal the scorer's:", a2["equal_to_the_scorer"])
    if a2["equal_to_the_scorer"]:
        for q in QS:
            r40, r30, r10 = a2["registered_40_re_made"][q], a2["without_G_30"][q], a2["G_alone_10"][q]
            print(f"  {q}: registered {r40['verdict']} ({r40['pass']}/{r40['n']}); without G {r30['verdict']} ({r30['pass']}/{r30['n']}); "
                  f"G alone {r10['verdict']} ({r10['pass']}/{r10['n']})")
    for h, v in rp["A4_head_to_heads_by_configuration_REPORTED"].items():
        c = v.get("by_configuration_REPORTED")
        pl = v["point_level"]
        line = f"A4 (REPORTED) {h}: registered {v['registered_verdict']} (points {pl['first_closer']}/{pl['second_closer']}/{pl['ties']})"
        print(line + (f"; by configuration {c['first_closer']}/{c['second_closer']}/{c['ties']} of {c['configurations']}, p {c['p_two_sided']}"
                      if c else f"; {v.get('REPORTED')}"))


if __name__ == "__main__":
    main()
