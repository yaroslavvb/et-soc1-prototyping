#!/usr/bin/env python3
"""E178 (Q146, the kit): the self-test of score_e178.py, before any E178 datum. Desk only; it reads committed files and writes synthetic
sessions into a temporary directory (removed at the end). Three parts:

  A. THE REGISTRATION'S ARITHMETIC
     A1  the frozen-input check passes on the committed files and refuses (9) a copy whose forecast file differs by one byte;
     A2  the scored forecasts' route: for all 40 kinds on both cards, P = P_frozen x s x rate / E171's rate equals M10's own d600 on the
         kind's frozen features (predict_m10, unchanged) at three (s, rate) points, and F equals d600 plus the accumulator term rebuilt
         from forecast-e178.json's flips by forecast_e178.py's own formula (floats: c_end's price on c_store's launch mean less M10's c_end;
         int8: the bus price on the four lane_operand_bus classes' launch mean less their three-point mean), within 1e-9 W;
     A3  the scorer's interval, SIGN and SIZE functions, fed dated note A1's own draws (power_e178_a1.py's generators and seeds, rebuilt
         draw for draw), reproduce power-e178-a1.json's shares EXACTLY: E178-S-int8 under P, F, no difference and the three operand-bit
         truths (POSITIVE, NEGATIVE, dP inside, dF inside), and E178-U under P, F and no difference;
     A4  F's SIZE coverage (A1-5: "the scorer's self-test computes F's SIZE coverage on synthetic sessions"), from A3's E178-U draws:
         dF inside if F is right, if P is right and under no difference; and the same for E178-H-int8 at its own seed (power_e178's).
  B. COMMITTED ANCHOR DATA (E171, aifoundry3, 5 Nov 2026, lab 91f8ae40: E78's six anchors ran three times in every pass, as in E178)
     B1  the C-session route (ccsessions_e178, i.e. ccsessions_p8 unchanged) on E171's committed layout: every listed session checked;
     B2  the scale route: predict_pool8's scale on E171's committed e171.json gives E171's committed s and ratios exactly; on a copy
         with only E78's two random float anchors (what an E178 session holds), s is the median of their two ratios; score_e178's guard
         refuses (5) a reduction whose scale reads any other anchor;
     B3  the C status route (score_p8_600.c_status, unchanged) on E171's anchors and tie: every launch PASS, counts named;
     B4  the couple machinery on E171's committed runs.csv: for every kept pass and each format's (random, zeros) anchor pair, the
         segment-paired mean equals the reduction's per-pass difference wherever all three segments are kept (1e-9 W).
  C. SYNTHETIC E178 SESSIONS through score_session (the reduction, runs.csv, the raw copy's launch records and a check of C, all in
     E178's layout and order), each with a stated truth and its expected readings:
     C1 P true (s 1.01): E178-C PASS, H-int8 POSITIVE and SIZE PASS, S-int8 POSITIVE and SIZE PASS, R-int8 PASS, W-int8 PASS, U POSITIVE,
        the E groups PASS, the owner's sentence measured, s read back as 1.01;
     C2 the A and B words' 1-bits at P's spread (A1-1's alternative): S-int8 NEGATIVE, the owner's sentence not measured;
     C3 every int8 kind the same: S-int8 and H-int8 NOT RESOLVED, R-int8 FAIL, W-int8 FAIL HIGH (P's slope above the card's);
     C4 one launch of int8.e178_v85 judged FAIL by the check of C: E178-C FAIL leaving it out, S-int8 NOT SCORED, R-int8 and W-int8 on 12
        kinds (R's line the shuffle point at n 12);
     C5 one kept pass: every rule but E178-C NOT SCORED;
     C6 one run of int8.e178_v4 lost in a pass: that pass's H-int8 value is the mean of its two complete couples;
     C7 card 1 (aifoundry1c1): card 1's frozen forecasts (S-int8's dP +0.341 W), P true reads POSITIVE and SIZE PASS;
     C8 the C-session gate on the synthetic layout: all five listed sessions OK; the smoke's C log removed: refused (4).

    /usr/bin/python3 -B tools/claims-v3/e178/selftest_score_e178.py [--json <out>] [--txt <out>]
Exit 0 when every check passes. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import csv
import json
import math
import os
import random
import shutil
import statistics
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_e178 as S  # noqa: E402
import e178_common as E  # noqa: E402

E171 = os.path.join(TOP, "docs", "reports", "data", "2026-11-05-e171-blind8-aifoundry3")
M10D = os.path.join(TOP, "docs", "reports", "data", "2026-11-04-q142m-m10")
FC = json.load(open(os.path.join(HERE, "forecast-e178.json")))
A1J = json.load(open(os.path.join(HERE, "power-e178-a1.json")))
PJ = json.load(open(os.path.join(HERE, "power-e178.json")))
OUT = {}
LINES = []


def check(name, ok, detail):
    OUT[name] = {"pass": bool(ok), "detail": detail}
    LINES.append(f"{name}: {'PASS' if ok else 'FAIL'} - {detail}")


# ------------------------------------------------------------------------------------------------- A
def part_a():
    fz = S.frozen_check()
    tmp = tempfile.mkdtemp(prefix="e178-selftest-a1-")
    try:
        for rel in list(E.LISTS) + S.FROZEN_READ:
            os.makedirs(os.path.join(tmp, os.path.dirname(rel)), exist_ok=True)
            shutil.copyfile(os.path.join(TOP, rel), os.path.join(tmp, rel))
        p = os.path.join(tmp, "tools/claims-v3/e178/forecast-e178.json")
        b = bytearray(open(p, "rb").read())
        b[-2] = ord(" ") if b[-2] != ord(" ") else ord("\t")
        open(p, "wb").write(bytes(b))
        try:
            S.frozen_check(tmp)
            code = 0
        except S.Refuse as e:
            code = e.code
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    check("A1 frozen inputs", len(fz) == len(S.FROZEN_READ) and code == 9,
          f"{len(fz)} frozen inputs match the registration's lists; a one-byte change to forecast-e178.json refuses with exit {code}")
    sys.path.insert(0, M10D)
    import predict_m10 as PM  # noqa: E402
    m10 = PM.load_m10()
    worst = {"P": 0.0, "F": 0.0}
    for cd, card in (("a3", "aifoundry3"), ("c1", "aifoundry1c1")):
        for k, r in FC["kinds"].items():
            t = r["type"]
            fam = "int8" if t == "int8" else "float"
            fm = m10["families"][fam]
            f = r["m10_features"]
            lm, pm = r["flips_i"]["launch_mean"], r["flips_i"]["points_mean"]
            for s, rf in ((1.0, 1.0), (1.01, 0.99), (0.97, 1.02)):
                s_ = s if t in S.FLOATS else 1.0
                rate = FC["rate"][t] * rf
                res = {"items": {k: {"rate": {"mean": rate}}}}
                sf = S.scored_forecasts({"kinds": {k: r}, "rate": FC["rate"]}, card, s, res)[k]
                d = PM.d600(f, t, rate, cd, m10, s_)
                if fam == "float":
                    e = fm["coef_J"][fm["terms"].index("c_end")]
                    corr = rate * e * (lm["c_store"] - f["c_end"])
                else:
                    e = fm["coef_J"][fm["terms"].index("bus")]
                    cls = ("c_store", "c_in", "c_out", "tenb_rz")
                    corr = rate * e * (sum(lm[c] for c in cls) - sum(pm[c] for c in cls))
                fw = s_ * (d / s_ + corr * (fm["card1_scale"] if cd == "c1" else 1.0))
                worst["P"] = max(worst["P"], abs(sf["P_w"] - d))
                worst["F"] = max(worst["F"], abs(sf["F_w"] - fw))
    check("A2 scored forecasts", worst["P"] < 1e-9 and worst["F"] < 1e-9,
          f"40 kinds x 2 cards x 3 (s, rate) points: |P - d600| at most {worst['P']:.1e} W, |F - (d600 + the accumulator term)| at most "
          f"{worst['F']:.1e} W")

    # A3: A1's draws, rebuilt; the scorer's functions read them
    def shares(draw, rng, dP, dF, n_draws):
        pos = neg = inP = inF = 0
        for _ in range(n_draws):
            xs = draw(rng)
            m, lo, hi, hw = S.interval(xs)
            sg = S.sign_of(lo, hi)
            pos += sg == "POSITIVE"
            neg += sg == "NEGATIVE"
            inP += S.size_of(lo, hi, dP)[0] == "PASS"
            inF += S.size_of(lo, hi, dF)[0] == "PASS"
        return {"p_positive": pos / n_draws, "p_negative": neg / n_draws, "p_dP_inside": inP / n_draws, "p_dF_inside": inF / n_draws}

    def pair_draw(delta, n, s1):
        def f(rng):
            off = rng.gauss(0, 0.041) - rng.gauss(0, 0.041)
            return [delta + off + rng.gauss(0, s1) for _ in range(n)]
        return f

    def couple_draw(delta, n, s1, sys_sd):
        def f(rng):
            off = rng.gauss(0, sys_sd)
            return [delta + off + rng.gauss(0, s1 / math.sqrt(3)) for _ in range(n)]
        return f

    D = A1J["draws"]
    Sx = A1J["S"]["E178-S-int8"]
    dP, dF = Sx["dP_w"], Sx["dF_w"]
    a3 = {}
    allsame = True
    for c in Sx["cases"]:
        if (c["n"], c["sigma1"]) != (4, 0.125) or c["truth"].startswith("P plus"):
            continue
        rng = random.Random(f"E178-A1|E178-S-int8|{c['truth']}|4|0.125")
        got = shares(pair_draw(c["truth_w"], 4, 0.125), rng, dP, dF, D)
        same = all(got[k] == c[k] for k in got)
        allsame &= same
        a3[f"S | {c['truth']}"] = dict(got, equal_to_A1=same)
    U = A1J["U"]
    for c in U["cases"]:
        if (c["n"], c["sigma1"]) != (4, 0.125):
            continue
        tv = {"P true": U["dP_w"], "F true": U["dF_w"], "null": 0.0}[c["truth"]]
        got = shares(couple_draw(tv, 4, 0.125, 0.02), random.Random(17804), U["dP_w"], U["dF_w"], D)
        same = all(got[k] == c[k] for k in got)
        allsame &= same
        a3[f"U | {c['truth']}"] = dict(got, equal_to_A1=same)
    check("A3 the scorer's verdicts on A1's draws", allsame,
          "; ".join(f"{k}: POSITIVE {v['p_positive']:.4f}, NEGATIVE {v['p_negative']:.4f}, dP in {v['p_dP_inside']:.4f}, dF in "
                    f"{v['p_dF_inside']:.4f}{'' if v['equal_to_A1'] else ' (DIFFERS from power-e178-a1.json)'}" for k, v in a3.items()))
    OUT["A3_shares"] = a3
    # A4: F's SIZE coverage (from A3's E178-U draws) and H-int8's at power_e178's seed 17803
    cov = {k: v["p_dF_inside"] for k, v in a3.items() if k.startswith("U |")}
    k4, k5 = FC["kinds"]["int8.e178_v4"], FC["kinds"]["int8.e178_v5"]
    dPh, dFh = k5["P_w"]["a3"] - k4["P_w"]["a3"], k5["F_w"]["a3"] - k4["F_w"]["a3"]
    h = {}
    for tn, tv in (("P true", dPh), ("F true", dFh), ("null", 0.0)):
        h[tn] = shares(couple_draw(tv, 4, 0.125, 0.02), random.Random(17803), dPh, dFh, D)
    reg = {c["truth"]: c for c in PJ["rules"]["E178-H-int8"]["cases"] if c["n"] == 4 and c["sigma1"] == 0.125}
    hsame = all(h[t]["p_positive"] == reg[t]["p_resolved_positive"] and h[t]["p_dP_inside"] == reg[t]["p_dP_inside"] for t in h)
    OUT["A4_F_size_coverage"] = {"E178-U": cov, "E178-H-int8": {t: v["p_dF_inside"] for t, v in h.items()},
                                 "E178-H-int8_P_shares_equal_power-e178.json": hsame}
    check("A4 F's SIZE coverage", abs(cov["U | F true"] - 0.93115) < 1e-12 and hsame,
          f"E178-U dF inside {cov['U | F true']:.4f} if F is right, {cov['U | P true']:.4f} if P is right, {cov['U | null']:.4f} under no "
          f"difference (A1-5's 0.931 / 0.793 / 0.334); E178-H-int8 dF inside {h['F true']['p_dF_inside']:.4f} / {h['P true']['p_dF_inside']:.4f}"
          f" / {h['null']['p_dF_inside']:.4f}, and its POSITIVE and dP-inside shares equal power-e178.json's: {hsame}")


# ------------------------------------------------------------------------------------------------- B
def part_b():
    raw = os.path.join(E171, "aifoundry3")
    cc = os.path.join(E171, "ccheck", "ccheck-all.json")
    g = S.CS().check("E171", raw, cc)
    check("B1 the C-session route on E171", g["ok"] and g["listed"] == 5,
          f"ccsessions_e178 (ccsessions_p8 unchanged) on E171's committed layout: {g['listed']} listed sessions, all checked: {g['ok']}; "
          f"stop-path test {g['stoptest']}")
    red = os.path.join(E171, "e171.json")
    a2 = S.A2()
    a2.check_lists()
    p = a2.P()
    p.check_inputs()
    _, pred = S.pool8_pred("aifoundry3")
    sc = p.scale(pred, red)
    com = json.load(open(os.path.join(E171, "scored.json")))["primary"]["scale"]
    same = sc["s_float"] == com["s_float"] and sc["ratios"] == com["ratios"]
    tmp = tempfile.mkdtemp(prefix="e178-selftest-b2-")
    try:
        r = json.load(open(red))
        r["items"] = {k: v for k, v in r["items"].items() if not ("." in k and k.split(".", 1)[1].startswith("anchor8"))}
        q = os.path.join(tmp, "e171-e78-anchors-only.json")
        json.dump(r, open(q, "w"))
        sc2, _ = S.session_scale("aifoundry3", q)
        want2 = statistics.median([com["ratios"]["fp32.randn"], com["ratios"]["fp16.randn"]])
        try:
            S.session_scale("aifoundry3", red)
            code = 0
        except S.Refuse as e:
            code = e.code
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    check("B2 the scale route on E171", same and abs(sc2["s_float"] - want2) < 1e-15 and sorted(sc2["anchors_used"]) == ["fp16.randn", "fp32.randn"]
          and code == 5,
          f"predict_pool8.scale on E171's e171.json: s {sc['s_float']:.6f} and its 6 ratios equal E171's scored.json: {same}; with E78's two "
          f"anchors only, s {sc2['s_float']:.6f} = the median of fp32.randn's {com['ratios']['fp32.randn']:.6f} and fp16.randn's "
          f"{com['ratios']['fp16.randn']:.6f}; score_e178's guard on the full reduction (pool 8's anchors in s) exits {code}")
    res = json.load(open(red))
    cs = S.c_status_fn()(list(E.ANCHORS) + ["anchor_pi"], res, [cc], os.path.join(raw, "e171"))
    allp = all(v["all_pass"] for v in cs.values())
    check("B3 the C status route on E171's anchors", allp and len(cs) == 7,
          "; ".join(f"{k} {v['PASS']}/{v['launches']}" for k, v in sorted(cs.items())))
    rows = S.load_rows(os.path.join(E171, "runs.csv"))
    passes = [int(x) for x in res["passes"]]
    worst, n = 0.0, 0
    for a, b in (("fp32.randn", "fp32.zeros"), ("fp16.randn", "fp16.zeros"), ("int8.full", "int8.zeros")):
        xs = S.couple_xs(rows, passes, a, b)
        for pp, v in xs.items():
            if v["couples"] == 3:
                ref = res["per_pass"][str(pp)][a]["D"] - res["per_pass"][str(pp)][b]["D"]
                worst = max(worst, abs(v["x"] - ref))
                n += 1
    check("B4 the couple machinery on E171's runs.csv", n >= 10 and worst < 1e-9,
          f"{n} (pass, pair) values with three complete couples: the segment-paired mean equals e171.json's per-pass difference to "
          f"{worst:.1e} W")


# ------------------------------------------------------------------------------------------------- C
def dh_of(card, name, rate):
    p = S.A2().P()
    g = p.frozen()
    m10 = g["m10"]
    _, pred = S.pool8_pred(card)
    fm = m10["families"]["float"]
    c = fm["card1_scale"] if S.CD[card] == "c1" else 1.0
    return c * rate * p.dot(pred["m10_anchors"][name]["features"], fm["terms"], fm["pass1_coef_J"])


def make_session(d, card, truth, s_target=1.0, sd=0.004, seed=1, passes=(17810, 17811, 17812, 17813), fail_launch=None, drop=None,
                 c_logs=True):
    """a synthetic E178 session in E178's layout and registered order: per run D = truth + N(0, sd); every launch one record"""
    rng = random.Random(seed)
    key = E.PLAN_KEY[card]
    plan = json.load(open(E.PLAN_E178))["cards"][key]["passes"]
    plist = list(passes) if key == "aifoundry3" else [p + 10 for p in passes]
    raw = os.path.join(d, "raw")
    rate = dict(FC["rate"])
    anc = {}
    for n in ("fp32.randn", "fp16.randn"):
        anc[n] = s_target * dh_of(card, n, rate[n.split(".")[0]])
    rows, per_pass, launches, t_ms = [], {}, [], 1793900000000
    for p in plist:
        order = E.order_by_rule(key, p)
        assert [n for n, _ in order] == plan[str(p)]
        pd = os.path.join(raw, "e178", f"p{p}")
        os.makedirs(pd, exist_ok=True)
        open(os.path.join(pd, "block.json"), "w").write('{"status":"ok"}\n')
        rj = open(os.path.join(pd, "runs.jsonl"), "w")
        cl = open(os.path.join(pd, "c-log.jsonl"), "w")
        cl.write(json.dumps({"ccheck": 1, "kind": "host", "host_sha256": "h", "kernel_sha256": "k"}) + "\n")
        acc = {}
        for pos, (name, seg) in enumerate(order):
            t = name.split(".")[0] if name != "anchor_pi" else "fp32"
            if drop and (p, seg, name) == drop:
                continue
            if name in truth:
                Dv = truth[name] + rng.gauss(0, sd)
            elif name in anc:
                Dv = anc[name]                     # the scale anchors read s_target exactly (M10's term a)
            else:
                Dv = rng.gauss(0, sd)
            rows.append({"pass": p, "item": name, "segment": seg, "pos": pos, "D": Dv})
            acc.setdefault(name, []).append(Dv)
            t_ms += 10000
            rj.write(json.dumps({"item": name, "type": t, "launch": 0, "t_start_ms": t_ms, "t_end_ms": t_ms + 500, "pos": pos}) + "\n")
            cl.write(json.dumps({"ccheck": 1, "kind": "c", "type": t, "launch": 0, "iters": 1, "t_start_ms": t_ms, "t_end_ms": t_ms + 500,
                                 "ok": True, "groups": []}) + "\n")
            v = "FAIL" if fail_launch and (p, name) == fail_launch else "PASS"
            launches.append({"log": f"c-log-p{p}.jsonl", "t_start_ms": t_ms, "t_end_ms": t_ms + 500, "verdict": v})
        rj.close()
        cl.close()
        per_pass[str(p)] = {n: {"D": statistics.mean(v), "rate": rate.get(n.split(".")[0], rate["fp32"])} for n, v in acc.items()}
    for sub, nm in (("e178-smoke", "p17801"),):
        sd_ = os.path.join(raw, sub, nm)
        os.makedirs(sd_, exist_ok=True)
        t_ms += 10000
        open(os.path.join(sd_, "runs.jsonl"), "w").write(json.dumps({"item": "fp32.zeros", "launch": 0, "t_start_ms": t_ms,
                                                                       "t_end_ms": t_ms + 500}) + "\n")
        if c_logs:
            open(os.path.join(sd_, "c-log.jsonl"), "w").write(
                json.dumps({"ccheck": 1, "kind": "host", "host_sha256": "h", "kernel_sha256": "k"}) + "\n" +
                json.dumps({"ccheck": 1, "kind": "c", "type": "fp32", "launch": 0, "iters": 1, "t_start_ms": t_ms, "t_end_ms": t_ms + 500,
                            "ok": True, "groups": []}) + "\n")
        launches.append({"log": f"c-log-{nm}.jsonl", "t_start_ms": t_ms, "t_end_ms": t_ms + 500, "verdict": "PASS"})
    os.makedirs(os.path.join(raw, "e178-stoptest", "p17802"), exist_ok=True)
    cc = os.path.join(d, "ccheck-all.json")
    json.dump({"summary": {"launches": len(launches), "all_pass": all(x["verdict"] == "PASS" for x in launches),
                           "PASS": sum(x["verdict"] == "PASS" for x in launches)}, "launches": launches}, open(cc, "w"))
    items = {}
    for n in {n for pp in per_pass.values() for n in pp}:
        v = [per_pass[str(p)][n]["D"] for p in plist if n in per_pass[str(p)]]
        items[n] = {"D": {"mean": statistics.mean(v)}, "rate": {"mean": rate.get(n.split(".")[0], rate["fp32"])}}
    red = os.path.join(d, "e178.json")
    json.dump({"experiment": "E178 (synthetic)", "passes": plist, "passes_set_aside": [], "per_pass": per_pass, "items": items}, open(red, "w"))
    cpath = os.path.join(d, "runs.csv")
    with open(cpath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["pass", "item", "segment", "pos", "D"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return red, cpath, raw, cc


def truths(card):
    cd = S.CD[card]
    P = {k: r["P_w"][cd] for k, r in FC["kinds"].items()}
    i8 = sorted(k for k in P if FC["kinds"][k]["type"] == "int8")
    ob = A1J["operand_bits"]
    pc = ob["popcount_a_plus_b_words"]
    base = min(P[k] for k in i8)
    ones = dict(P)
    ones.update({k: base + ob["beta_w_per_bit"]["ones_span"] * (pc[k] - min(pc.values())) for k in i8})
    flat = dict(P)
    flat.update({k: 1.8 for k in i8})
    return P, ones, flat


def part_c():
    tmp = tempfile.mkdtemp(prefix="e178-selftest-c-")
    try:
        P3, ones3, flat3 = truths("aifoundry3")
        Ps = {k: (v * 1.01 if FC["kinds"][k]["type"] in S.FLOATS else v) for k, v in P3.items()}

        def run(name, truth, card="aifoundry3", skip_gate=True, **kw):
            d = os.path.join(tmp, name)
            os.makedirs(d)
            red, cpath, raw, cc = make_session(d, card, truth, **kw)
            return S.score_session(card, red, cpath, raw, cc, skip_c_gate=skip_gate)

        o = run("C1", Ps, s_target=1.01, seed=11)
        V, R = o["verdicts"], o["primary"]["rules"]
        want = {"E178-C": "PASS", "E178-H-int8": "POSITIVE", "E178-S-int8": "POSITIVE", "E178-R-int8": "PASS", "E178-W-int8": "PASS",
                "E178-U": "POSITIVE", "E178-E-int8": "PASS", "E178-E-fp32": "PASS", "E178-E-fp16": "PASS"}
        s1 = o["primary"]["scale"]["s_float"]
        ok = (all(V[k] == v for k, v in want.items()) and R["E178-H-int8"]["size"] == "PASS" and R["E178-S-int8"]["size"] == "PASS"
              and o["owner_sentence"]["measured"] and abs(s1 - 1.01) < 1e-9)
        check("C1 P true", ok, f"verdicts {V}; H-int8 SIZE {R['E178-H-int8']['size']}, S-int8 SIZE {R['E178-S-int8']['size']} (dP "
                               f"{R['E178-S-int8']['dP_w']:+.4f} W, read {R['E178-S-int8']['mean_w']:+.4f}); s {s1:.6f}; owner's sentence "
                               f"measured {o['owner_sentence']['measured']}")
        OUT["C1_scored"] = {"verdicts": V, "sizes": o["primary"]["verdicts_size"]}
        o = run("C2", dict(ones3), seed=12)
        V = o["verdicts"]
        check("C2 the operands' 1-bits at P's spread", V["E178-S-int8"] == "NEGATIVE" and not o["owner_sentence"]["measured"],
              f"S-int8 {V['E178-S-int8']} (read {o['primary']['rules']['E178-S-int8']['mean_w']:+.4f} W against dP "
              f"{o['primary']['rules']['E178-S-int8']['dP_w']:+.4f}); R-int8 {V['E178-R-int8']}, H-int8 {V['E178-H-int8']}, W-int8 "
              f"{V['E178-W-int8']}; owner's sentence measured {o['owner_sentence']['measured']}")
        o = run("C3", dict(flat3), seed=13)
        V, R = o["verdicts"], o["primary"]["rules"]
        check("C3 flat int8", V["E178-S-int8"] == "NOT RESOLVED" and V["E178-H-int8"] == "NOT RESOLVED" and V["E178-R-int8"] == "FAIL"
              and V["E178-W-int8"] == "FAIL HIGH" and "above" in R["E178-W-int8"]["reading"],
              f"S-int8 {V['E178-S-int8']}, H-int8 {V['E178-H-int8']}, R-int8 {V['E178-R-int8']} (rho {R['E178-R-int8']['rho']:+.3f}), "
              f"W-int8 {V['E178-W-int8']} ({R['E178-W-int8']['slope_fJ_per_flip']:+.2f} fJ against P's {R['E178-W-int8']['line_fJ']:.2f}: "
              f"{R['E178-W-int8']['reading']})")
        o = run("C4", dict(P3), seed=14, fail_launch=(17812, "int8.e178_v85"))
        V, R = o["verdicts"], o["primary"]["rules"]
        check("C4 a C FAIL on int8.e178_v85", V["E178-C"] == "FAIL" and R["E178-C"]["c_excluded"] == ["int8.e178_v85"]
              and V["E178-S-int8"] == "NOT SCORED" and R["E178-R-int8"]["n"] == 12 and R["E178-W-int8"]["n"] == 12
              and "shuffles at n = 12" in R["E178-R-int8"]["line_source"],
              f"E178-C {V['E178-C']} leaving out {R['E178-C']['c_excluded']}; S-int8 {V['E178-S-int8']}; R-int8 {V['E178-R-int8']} on "
              f"{R['E178-R-int8']['n']} kinds against {R['E178-R-int8']['line']:.3f} ({R['E178-R-int8']['line_source']}); W-int8 "
              f"{V['E178-W-int8']} on {R['E178-W-int8']['n']}")
        o = run("C5", dict(P3), seed=15, passes=(17810,))
        V = o["verdicts"]
        check("C5 one kept pass", all(v == "NOT SCORED" for k, v in V.items() if k != "E178-C") and V["E178-C"] == "PASS",
              f"verdicts {V}")
        o = run("C6", dict(P3), seed=16, drop=(17811, 1, "int8.e178_v4"))
        x = o["primary"]["rules"]["E178-H-int8"]["per_pass"][17811]
        check("C6 a lost run", x["couples"] == 2 and abs(x["x"] - statistics.mean(x["segment_diffs"])) < 1e-15 and x["adjacent"] == 2,
              f"pass 17811: {x['couples']} complete couples (both adjacent: {x['adjacent']}), x {x['x']:+.4f} W = their mean")
        P1, _, _ = truths("aifoundry1c1")
        o = run("C7", dict(P1), card="aifoundry1c1", seed=17)
        V, R = o["verdicts"], o["primary"]["rules"]
        check("C7 card 1", V["E178-S-int8"] == "POSITIVE" and R["E178-S-int8"]["size"] == "PASS" and abs(R["E178-S-int8"]["dP_w"] - 0.3413) < 0.0005,
              f"card 1's forecasts: S-int8 dP {R['E178-S-int8']['dP_w']:+.4f} W, read {R['E178-S-int8']['mean_w']:+.4f}: {V['E178-S-int8']}, SIZE "
              f"{R['E178-S-int8']['size']}; passes {o['primary']['kept_passes']}")
        o = run("C8a", dict(P3), seed=18, skip_gate=False)
        ok_a = o["c_sessions"]["ok"] and o["c_sessions"]["listed"] == 5
        try:
            run("C8b", dict(P3), seed=19, skip_gate=False, c_logs=False)
            code = 0
        except S.Refuse as e:
            code = e.code
        check("C8 the C-session gate on E178's layout", ok_a and code == 4,
              f"5 listed sessions (the smoke and four passes) all checked: {ok_a}; the smoke's C log missing: exit {code}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--txt")
    a = ap.parse_args()
    part_a()
    part_b()
    part_c()
    ok = all(v["pass"] for k, v in OUT.items() if isinstance(v, dict) and "pass" in v)
    OUT["PASS"] = ok
    LINES.append(f"SELFTEST-SCORE-E178 {'PASS' if ok else 'FAIL'}: {sum(1 for v in OUT.values() if isinstance(v, dict) and v.get('pass'))} of "
                 f"{sum(1 for v in OUT.values() if isinstance(v, dict) and 'pass' in v)} checks")
    txt = "\n".join(LINES) + "\n"
    print(txt, end="")
    if a.json:
        open(a.json, "w").write(json.dumps(OUT, indent=1, sort_keys=True, default=str) + "\n")
    if a.txt:
        open(a.txt, "w").write(txt)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
