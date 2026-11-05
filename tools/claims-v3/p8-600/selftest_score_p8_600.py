#!/usr/bin/env python3
"""Q142(k6): the self-test of score_p8_600.py and ccsessions_p8.py (E171.md and E172.md, "The order of the freeze", step 2). Desk only:
it reads committed files and writes only into a temporary directory (removed at the end) and its --out file. No device, no ssh.

  S1  the lines at the planned n: the scorer's rule functions on each card's frozen sets give intervals-pool8.json's every bootstrap and
      coverage line exactly (P1-P3, B1, B2, H1-H3, C1, H4) and LG's F point (the same functions and seeds the verdicts read).
  S2  E163 (committed, aifoundry3): the scorer's measured, rms, bias, coverage and paired functions, configured as E163 registered them
      (seed base 16300, 20,000 draws, paired 5,000, M9's references in predictions-e163.json), on E163's committed reduction and M9's
      frozen predictions, reproduce E163's committed scored.json: P1-P3, B1, B2, C1, M1-M3, H1-H4, every reading, interval and verdict;
      c_status on E163's committed check of C and passes reproduces its committed c_status for every tile (KC PASS); ccsessions_p8 on
      E163's committed layout lists its 7 C-logged sessions and finds each checked to the end.
  S3  E164 (committed, card 1): the same with E164's registration (seed base 16400, paired 5,000, card-1 references) on e164.json; c_status
      and ccsessions on E164's committed layout.
  S4  end to end through the frozen predictor: pool 7's ten T9 tiles (predict_pool8_a2's own list) predicted for aifoundry3 and card 1,
      then the scorer's scale, its check and the frozen primary on M10's committed footing reductions of E163 and E164: every M10 primary
      equals rows-m10.json's in-sample prediction within 1e-9 W, the scale M10's committed session scale within 5e-6, and the scorer's
      per-format rms of (D - M10 primary) equals the rms computed from rows-m10.json alone.
  S5  a synthetic session with known answers on each card (rates at the stated rate; the scale anchors at s = 1.004 of M10's pass-1
      prediction; designed errors): every verdict and reading as designed; with all fp16 N1 tiles C-excluded the fp16 rules read NOT
      SCORED and the all-tiles block appears; one kept pass: every rule NOT SCORED; no scale anchor measured: s = 1 and KA NOT SCORED;
      a missing C log, a check that skipped a session's log, and a launched stop-path test: refused (exit 4) with nothing written; a
      check anchor or a zeros anchor in the scale: refused (exit 5); a predictions file whose hash is not the freeze's: refused (exit 9);
      ka-pooled over the two cards' synthetic sessions.
  S6  the paired form against an independent re-implementation, on S5's errors (identical intervals).

    /usr/bin/python3 -B tools/claims-v3/p8-600/selftest_score_p8_600.py [--out <file.json>] [--quick]

Exit 0 when every part passes. Standard library and numpy (through the predictor). SPDX-License-Identifier: Apache-2.0
"""
import copy
import gzip
import hashlib
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_p8_600 as SC  # noqa: E402
import ccsessions_p8 as CSN  # noqa: E402

DD = os.path.join(TOP, "docs", "reports", "data")
E163D = os.path.join(DD, "2026-11-04-e163-blind7-aifoundry3")
E164D = os.path.join(DD, "2026-11-04-e164-blind7-card1")
load = lambda p: json.load(gzip.open(p, "rt") if p.endswith(".gz") else open(p))  # noqa: E731
CLOSE = 1e-12


def near(a, b, tol=CLOSE):
    return a is not None and b is not None and abs(float(a) - float(b)) <= tol


# ------------------------------------------------------------------------------------------------- S1
def s1_lines():
    iv = load(os.path.join(SC.B8, "intervals-pool8.json"))
    out, ok = {}, True
    p = SC.P()
    mins = p.frozen()["reg"]["scoring"]["minimum_tiles"]
    for card in ("aifoundry3", "aifoundry1c1"):
        pred = load(os.path.join(SC.B8, f"predictions-pool8-{card}.json"))
        S, L = pred["sets"], iv["cards"][card]["rules"]
        refs = p.ref_errors(p.CARDS[card])
        href = {t: SC.A2().heat_ref(card, t) for t in SC.FORMATS}
        zero = {t: 0.0 for t in pred["tiles"]}
        got, bad = {}, []
        for rule, t in (("P8-P1", "fp32"), ("P8-P2", "fp16"), ("P8-P3", "int8")):
            got[rule] = SC.rms_rule(rule, zero, S["by_format"][t], refs, mins[rule[3:]], "W")["line"]
        got["P8-B1"] = SC.bias_rule("P8-B1", zero, S["F1"], refs, mins["B1"])["line"]
        got["P8-B2"] = SC.bias_rule("P8-B2", zero, S["I1"], refs, mins["B2"])["line"]
        for rule, t in (("P8-H1", "fp32"), ("P8-H2", "fp16"), ("P8-H3", "int8")):
            got[rule] = SC.rms_rule(rule, zero, S["by_format"][t], href, mins[rule[3:]], "C")["line"]
        for r, v in got.items():
            if v != L[r]["range_95"]:
                bad.append(f"{r}: {v} != {L[r]['range_95']}")
        cov = SC.coverage_rule({t: True for t in S["N1"]}, S["N1"], mins["C1"])
        if cov["inside_at_least"] != L["P8-C1"]["inside_at_least"] or cov["inside_at_least"] != L["P8-H4"]["inside_at_least"]:
            bad.append("C1 / H4 coverage line")
        D = SC.A2().DPG()
        F = D.f_ppf(0.95, L["P8-LG"]["k"], L["P8-LG"]["n"] - 2 * L["P8-LG"]["k"])
        if F != L["P8-LG"]["F_point_5pct"]:
            bad.append("LG F point")
        out[card] = {"lines_compared": len(got) + 3, "differences": bad, "pass": not bad}
        ok = ok and not bad
    out["pass"] = ok
    return out


# ------------------------------------------------------------------------------------------------- S2, S3: the parents
def parent_replay(prefix, red, regp, scored, refkey, href_key, seed_base, paired_draws, cov_set, p1set, models_cmp):
    """configure the scorer's functions as the parent registered them and compare with its committed scored.json"""
    reg = load(regp)
    sc = load(scored)
    res = load(red)
    spec = reg.get("spec") or {}
    names = sorted(reg["tiles"])
    mD, _ = SC.measured(res, names, "D", 2)
    mT, _ = SC.measured(res, names, "dT_win", 2)
    pri = sc["primary"]["primary"]["rules"] if "primary" in sc["primary"] else sc["primary"]["rules"]
    refP = reg["reference_errors"][refkey]
    refH = reg["reference_errors"][href_key]
    errs, inside, herr, hin = {}, {}, {}, {}
    for m in ("M9",) + tuple(o for _, o in models_cmp):
        errs[m] = {t: mD[t]["mean"] - reg["tiles"][t][m]["D_w"] for t in names if t in mD}
    for t in names:
        if t in mD:
            lo, hi = reg["tiles"][t]["M9"]["D_95"]
            inside[t] = lo <= mD[t]["mean"] <= hi
        m = reg["tiles"][t]["M9"]
        if t in mT and m.get("dT_win_c") is not None:
            herr[t] = mT[t]["mean"] - m["dT_win_c"]
            hin[t] = m["dT_win_95"][0] <= mT[t]["mean"] <= m["dT_win_95"][1]
    sd = lambda rid: seed_base + sum(map(ord, rid))  # noqa: E731
    bad, got = [], {}
    for rid, f in (("P1", "fp32"), ("P2", "fp16"), ("P3", "int8")):
        r = SC.rms_rule(f"{prefix}-{rid}", errs["M9"], p1set[f], refP, 1, "W", draws=20000, seed=sd(f"{prefix}-{rid}"))
        c = pri[f"{prefix}-{rid}"]
        got[rid] = r
        if not (near(r["rms"], c["rms"]) and near(r["line"][0], c["interval"]["lo95"]) and near(r["line"][1], c["interval"]["hi95"])
                and r["verdict"] == c["verdict"]):
            bad.append(f"{rid}: {r['rms']} {r['line']} {r['verdict']} vs {c['rms']} {c['interval']['lo95']} {c['interval']['hi95']} {c['verdict']}")
    for rid, fam in (("B1", ("fp32", "fp16")), ("B2", ("int8",))):
        sel = [t for f in fam for t in p1set[f]]
        r = SC.bias_rule(f"{prefix}-{rid}", errs["M9"], sel, refP, 1, draws=20000, seed=sd(f"{prefix}-{rid}"))
        c = pri[f"{prefix}-{rid}"]
        got[rid] = r
        if not (near(r["mean"], c["bias_meas_minus_pred_w"]) and near(r["line"][0], c["interval"]["lo95"]) and near(r["line"][1], c["interval"]["hi95"])
                and r["verdict"] == c["verdict"]):
            bad.append(f"{rid}: {r['mean']} {r['line']} {r['verdict']} vs {c['bias_meas_minus_pred_w']} {c['interval']} {c['verdict']}")
    r = SC.coverage_rule(inside, cov_set, 10)
    c = pri[f"{prefix}-C1"]
    got["C1"] = r
    if not (r["inside"] == c["inside"] and r["n"] == c["n"] and r["inside_at_least"] == c["binomial_low_2p5"] and r["verdict"] == c["verdict"]
            and r["outside"] == c["outside"]):
        bad.append(f"C1: {r} vs {c}")
    for rid, other in models_cmp:
        sel = [t for t in cov_set if t in errs["M9"]]
        r = SC.paired(errs["M9"], errs[other], sel, draws=paired_draws, seed=sd(f"{prefix}-{rid}"))
        c = pri[f"{prefix}-{rid}"]
        got[rid] = r
        if not (near(r["d_rms"], c["d_rms_w"]) and near(r["lo95"], c["lo95"]) and near(r["hi95"], c["hi95"]) and r["verdict"] == c["verdict"]):
            bad.append(f"{rid}: {r['d_rms']} [{r['lo95']}, {r['hi95']}] {r['verdict']} vs {c['d_rms_w']} [{c['lo95']}, {c['hi95']}] {c['verdict']}")
    for rid, f in (("H1", "fp32"), ("H2", "fp16"), ("H3", "int8")):
        r = SC.rms_rule(f"{prefix}-{rid}", herr, [t for t in p1set[f] if t in herr], refH, 1, "C", draws=20000, seed=sd(f"{prefix}-{rid}"))
        c = pri[f"{prefix}-{rid}"]
        got[rid] = r
        if not (near(r["rms"], c["rms"]) and near(r["line"][0], c["interval"]["lo95"]) and near(r["line"][1], c["interval"]["hi95"])
                and r["verdict"] == c["verdict"]):
            bad.append(f"{rid}: {r['rms']} {r['line']} {r['verdict']} vs {c['rms']} {c['interval']} {c['verdict']}")
    r = SC.coverage_rule(hin, cov_set, 10)
    c = pri[f"{prefix}-H4"]
    got["H4"] = r
    if not (r["inside"] == c["inside"] and r["n"] == c["n"] and r["verdict"] == c["verdict"]):
        bad.append(f"H4: {r} vs {c}")
    figs = {k: {x: v.get(x) for x in ("verdict", "rms", "mean", "line", "inside", "n", "d_rms", "lo95", "hi95")} for k, v in got.items()}
    return {"rules_compared": len(got), "differences": bad, "figures": figs, "pass": not bad}


def s2_e163():
    reg = load(os.path.join(TOP, "tools/claims-v3/e163/predictions-e163.json"))
    S = reg["spec"]["sets"]
    out = parent_replay("E163", os.path.join(E163D, "e163.json"), os.path.join(TOP, "tools/claims-v3/e163/predictions-e163.json"),
                        os.path.join(E163D, "scored.json"), "power_a3", "heat_normal_a3", 16300, 5000, S["coverage_tiles"],
                        S["priority1_by_format"], (("M1", "M6"), ("M2", "M8"), ("M3", "M7")))
    # KC through the copied c_status, on the committed check and passes
    sc = load(os.path.join(E163D, "scored.json"))
    res = load(os.path.join(E163D, "e163.json"))
    want = sorted(sc["c_status"])
    cs = SC.c_status(want, res, [os.path.join(E163D, "ccheck", "ccheck-all.json")], os.path.join(E163D, "aifoundry3", "e163"))
    same = cs == sc["c_status"]
    out["c_status_equals_committed"] = same
    out["c_status_launches"] = sum(v["launches"] for v in cs.values())
    out["c_status_all_pass"] = all(v["all_pass"] for v in cs.values())
    g = CSN.check("E163", os.path.join(E163D, "aifoundry3"), os.path.join(E163D, "ccheck", "ccheck-all.json"))
    out["ccsessions"] = {"ok": g["ok"], "listed": g["listed"], "lines": g["lines"]}
    out["pass"] = out["pass"] and same and out["c_status_all_pass"] and g["ok"] and g["listed"] == 7
    return out


def s3_e164(tmp):
    regp = os.path.join(TOP, "tools/claims-v3/e164/predictions-e164.json")
    reg = load(regp)
    S = reg["sets"]
    p1 = S["priority1_by_format"]
    cov = sorted(S["priority1_all"])
    out = parent_replay("E164", os.path.join(E164D, "e164.json"), regp, os.path.join(E164D, "scored.json"), "power_card1", "heat_normal_card1",
                        16400, 5000, cov, p1, (("M1", "M6"), ("M2", "M8")))
    # the committed layout is the collector's (e164-smoke-p16401, e164-stoptest-p16402): a raw view in the scratch, by links
    raw = os.path.join(tmp, "e164-raw-view")
    os.makedirs(os.path.join(raw, "e164-smoke"))
    os.makedirs(os.path.join(raw, "e164-stoptest"))
    base = os.path.join(E164D, "aifoundry1-c1")
    os.symlink(os.path.join(base, "e164"), os.path.join(raw, "e164"))
    os.symlink(os.path.join(base, "e164-smoke-p16401"), os.path.join(raw, "e164-smoke", "p16401"))
    os.symlink(os.path.join(base, "e164-stoptest-p16402"), os.path.join(raw, "e164-stoptest", "p16402"))
    g = CSN.check("E164", raw, os.path.join(E164D, "ccheck", "ccheck-session.json"))
    out["ccsessions"] = {"ok": g["ok"], "listed": g["listed"], "lines": g["lines"]}
    res = load(os.path.join(E164D, "e164.json"))
    want = [t for t in reg["tiles"]]
    cs = SC.c_status(want, res, [os.path.join(E164D, "ccheck", "ccheck-session.json.gz")], os.path.join(base, "e164"))
    out["c_status_launches"] = sum(v["launches"] for v in cs.values())
    out["c_status_all_pass"] = all(v["all_pass"] for v in cs.values())
    out["pass"] = out["pass"] and g["ok"] and g["listed"] == 5 and out["c_status_all_pass"]
    return out


# ------------------------------------------------------------------------------------------------- S4: end to end on committed data
def s4_end_to_end(tmp):
    a2 = SC.A2()
    p = SC.P()
    g = p.frozen()
    pool = a2._pool(tmp, "pool-s4", a2.T9_NAMES)
    c7 = [os.path.join(p.B7, "counts-blind7.json")]
    ins = {(r["exp"], r["key"]): r for r in load(os.path.join(p.M10D, "rows-m10.json"))}
    sc_train = g["m10"]["families"]["float"]["session_scales_training"]
    out, ok = {}, True
    for card, exp in (("aifoundry3", "E163"), ("aifoundry1c1", "E164")):
        p.predict(pool, card, c7, reuse=True, out_dir=tmp)
        pp = os.path.join(tmp, f"predictions-pool8-{card}.json")
        pred = a2._as_all_new(load(pp))
        red = g["FM"].FOOTING[exp]
        r = SC.score_reduction(pp, pred, card, red)
        worst = max(abs(r["rows"][t]["M10_primary_w"] - ins[(exp, t)]["M10_insample_pred_w"]) for t in a2.T9_NAMES)
        s_ok = abs(r["scale"]["s_float"] - sc_train[f"{exp}|{p.CARDS[card]}"]) <= 5e-6
        by = {}
        for t in a2.T9_NAMES:
            if "e_primary" in r["rows"][t]:
                by.setdefault(t.split(".")[0], []).append(t)
        mine = {f: SC.rms([r["rows"][t]["e_primary"] for t in v]) for f, v in by.items()}
        theirs = {f: SC.rms([ins[(exp, t)]["D"] - ins[(exp, t)]["M10_insample_pred_w"] for t in v]) for f, v in by.items()}
        diff = max(abs(mine[f] - theirs[f]) for f in mine)
        dmeas = max(abs(r["rows"][t]["D_w"] - ins[(exp, t)]["D"]) for t in a2.T9_NAMES if "D_w" in r["rows"][t])
        out[card] = {"session": exp, "s_float": r["scale"]["s_float"], "m10_session_scale": sc_train[f"{exp}|{p.CARDS[card]}"],
                     "max_abs_primary_vs_insample_w": worst, "rms_by_format": mine, "rms_from_rows_m10": theirs, "max_rms_diff_w": diff,
                     "max_measured_D_vs_rows_m10_w": dmeas, "scale_check": r["scale_check"]["ok"], "verdicts": r["verdicts"]}
        ok = ok and worst <= 1e-9 and s_ok and diff <= 1e-9 and dmeas <= 1e-9 and r["scale_check"]["ok"]
    out["pass"] = bool(ok)
    return out


# ------------------------------------------------------------------------------------------------- S5: a synthetic session
DESIGN = {"fp32": 0.10, "fp16": 0.05, "int8": 0.30}       # N1 errors: fp32 all +0.10, fp16 alternate +-0.05, int8 all +0.30
HEAT = {"fp32": 0.05, "fp16": -0.05, "int8": 0.40}
S_TRUE = 1.004
GAIN = 0.006


def synth(card, tmp, label, passes=(0, 1, 2), drop_scale=False, run=None):
    """a raw copy, a check of C and a reduction for a designed session; returns (raw, ccheck, reduction, pred, expected)"""
    run = run or ("E171" if card == "aifoundry3" else "E172")
    R = CSN.RUNS[run]
    pred = load(os.path.join(SC.B8, f"predictions-pool8-{card}.json"))
    T, S = pred["tiles"], pred["sets"]
    rate = {t: pred["rates"][t]["stated_per_s"] for t in SC.FORMATS}
    base = os.path.join(tmp, label)
    raw = os.path.join(base, "raw")
    num0 = int(R["smoke"][1:]) + 9          # 17110 / 17210
    pass_ids = [num0 + i for i in passes]
    # the measured values
    D, dT = {}, {}
    m10a = pred["m10_anchors"]
    scale_names = ["fp32.randn", "fp16.randn"] + list(S["scale_anchors_pool8"])
    for n in scale_names if not drop_scale else []:
        t = n.split(".")[0]
        k1 = m10a[n]["k1_J_per_op"] if n in m10a else T[n]["M10"]["k1_J_per_op"]
        D[n] = S_TRUE * rate[t] * k1
    s = 1.0 if drop_scale else S_TRUE
    prim = {n: (s if T[n]["type"] in SC.FLOATS else 1.0) * rate[T[n]["type"]] * T[n]["M10"]["k_J_per_op"] for n in T}
    exp_err = {}
    for t in SC.FORMATS:
        for i, n in enumerate(S["by_format"][t]):
            e = DESIGN[t] * (1 if t != "fp16" else (1 if i % 2 == 0 else -1))
            exp_err[n] = e
    # the re-runs: D = D_ref (1 + GAIN) + r, r orthogonal to [1, D_ref] in each reference group (so the full fit is a = 0, g = GAIN, the
    # gain model fits as well as the full one, and LG's registered test must read GAIN: a known answer, not a chance one)
    grp = {}
    for n in S["RR"]:
        ref = next((r for r in T[n]["lg_reference"] if r.get("tile") == n), T[n]["lg_reference"][0])
        grp.setdefault(ref["session"], []).append((n, float(ref["D_w"])))
    lg_noise = {}
    for g_, v in grp.items():
        xs = [d for _, d in v]
        u = [(-1) ** i * (1 + 0.1 * i) for i in range(len(v))]
        m = sum(xs) / len(xs)
        e1 = [1.0 / math.sqrt(len(xs))] * len(xs)
        c = [x - m for x in xs]
        nc = math.sqrt(sum(y * y for y in c))
        e2 = [y / nc for y in c]
        r = [ui - sum(a * b for a, b in zip(u, e1)) * e1[i] - sum(a * b for a, b in zip(u, e2)) * e2[i] for i, ui in enumerate(u)]
        mx = max(abs(y) for y in r)
        for (n, _), y in zip(v, r):
            lg_noise[n] = 0.005 * y / mx
    for n in T:
        if n in D or (drop_scale and n in S["scale_anchors_pool8"]):     # drop_scale: the pool's float scale anchors are not measured
            continue
        if n in S["RR"]:
            ref = next((r for r in T[n]["lg_reference"] if r.get("tile") == n), T[n]["lg_reference"][0])
            D[n] = ref["D_w"] * (1 + GAIN) + lg_noise[n]
        elif n in S["KA"]:
            D[n] = prim[n] + 0.01
        else:
            D[n] = prim[n] + exp_err.get(n, 0.0)
    for n in ("fp32.zeros", "fp16.zeros", "int8.zeros", "int8.full"):
        D.setdefault(n, 0.0 if "zeros" in n else 7.0)
    # heat: M10's rise at the primary D, plus the designed heat errors on N1
    p = SC.P()
    cd = p.CARDS[card]
    heat = {n: p.heat_m10(prim[n], T[n]["type"], cd)["dT_win_c"] for n in T}
    for t in SC.FORMATS:
        for n in S["by_format"][t]:
            dT[n] = heat[n] + HEAT[t]
    for n in T:
        dT.setdefault(n, heat[n])
    items, per = {}, {str(q): {} for q in pass_ids}
    jit = lambda n, q: 1e-9 * (((sum(map(ord, n)) + q) % 5) - 2)  # noqa: E731  (each pass differs by under a nanowatt)
    for n, v in D.items():
        t = n.split(".")[0]
        vals = [v + jit(n, q) for q in pass_ids]
        items[n] = {"type": t, "D": {"mean": sum(vals) / len(vals), "se": 1e-4, "n": len(vals)}, "rate": {"mean": rate[t]},
                    "dT_win": {"mean": dT.get(n, 1.0)}}
        for q, x in zip(pass_ids, vals):
            per[str(q)][n] = {"D": x, "dT_win": dT.get(n, 1.0), "rate": rate[t]}
    res = {"experiment": run, "passes": pass_ids, "items": items, "per_pass": per}
    os.makedirs(base, exist_ok=True)
    red = os.path.join(base, f"{run.lower()}.json")
    json.dump(res, open(red, "w"))
    # the raw copy: the smoke and each pass carry runs.jsonl and a C log; the stop-path test carries neither; the check of C judges all
    launches = []
    for d, names in [(os.path.join(raw, f"{R['dir']}-smoke", R["smoke"]), ["anchor_pi", "fp32.zeros"])] + \
                    [(os.path.join(raw, R["dir"], f"p{q}"), sorted(T)) for q in pass_ids]:
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "runs.jsonl"), "w") as rf, open(os.path.join(d, "c-log.jsonl"), "w") as cf:
            cf.write(json.dumps({"ccheck": 1, "kind": "host", "host_sha256": "x", "kernel_sha256": "y"}) + "\n")
            for j, n in enumerate(names):
                t0 = 10 ** 12 + len(launches) * 10
                rf.write(json.dumps({"item": n, "launch": 0, "t_start_ms": t0, "t_end_ms": t0 + 5}) + "\n")
                cf.write(json.dumps({"ccheck": 1, "kind": "c", "type": n.split(".")[0] if "." in n else "fp32", "launch": 0, "iters": 1,
                                     "t_start_ms": t0, "t_end_ms": t0 + 5, "ok": True, "groups": []}) + "\n")
                launches.append({"log": f"c-log-{os.path.basename(d)}.jsonl", "t_start_ms": t0, "t_end_ms": t0 + 5, "verdict": "PASS",
                                 "type": "fp32"})
        open(os.path.join(d, "block.json"), "w").write('{"status":"ok"}\n')
    os.makedirs(os.path.join(raw, f"{R['dir']}-stoptest", R["stoptest"]), exist_ok=True)
    cc = os.path.join(base, "ccheck-all.json")
    json.dump({"summary": {"launches": len(launches), "PASS": len(launches), "ROUNDING": 0, "UNMODELLED": 0, "FAIL": 0, "all_pass": True},
               "launches": launches}, open(cc, "w"))
    return raw, cc, red, pred, {"exp_err": exp_err, "s": s}


def expected_verdicts(card, pred, r):
    """the designed readings and the verdicts they must give against the frozen lines (computed here from the design, not the scorer)"""
    iv = load(os.path.join(SC.B8, "intervals-pool8.json"))["cards"][card]["rules"]
    S = pred["sets"]
    ex = {}
    rms_d = {"fp32": DESIGN["fp32"], "fp16": DESIGN["fp16"], "int8": DESIGN["int8"]}
    for rule, t in (("P8-P1", "fp32"), ("P8-P2", "fp16"), ("P8-P3", "int8")):
        ex[rule] = "PASS" if rms_d[t] <= iv[rule]["range_95"][1] else "FAIL"
    n32, n16 = len(S["by_format"]["fp32"]), len(S["by_format"]["fp16"])
    alt16 = sum(DESIGN["fp16"] * (1 if i % 2 == 0 else -1) for i in range(n16))
    b1 = (n32 * DESIGN["fp32"] + alt16) / (n32 + n16)
    lo, hi = iv["P8-B1"]["range_95"]
    ex["P8-B1"] = "PASS" if lo <= b1 <= hi else ("FAIL HIGH" if b1 < lo else "FAIL LOW")
    lo, hi = iv["P8-B2"]["range_95"]
    ex["P8-B2"] = "PASS" if lo <= DESIGN["int8"] <= hi else ("FAIL HIGH" if DESIGN["int8"] < lo else "FAIL LOW")
    for rule, t in (("P8-H1", "fp32"), ("P8-H2", "fp16"), ("P8-H3", "int8")):
        ex[rule] = "PASS" if abs(HEAT[t]) <= iv[rule]["range_95"][1] else "FAIL"
    ex["P8-KA"] = "PASS"
    ex["P8-LG"] = "GAIN"
    ex["P8-HM"] = "NOT SCORED"
    ex["P8-KC"] = "PASS"
    fail = any(ex[k].startswith("FAIL") for k in ("P8-P1", "P8-P2", "P8-P3", "P8-B1", "P8-B2"))
    ex["P8-G"] = "FAIL" if fail else None          # C1 and M1 read from the run (their readings are checked below)
    return ex, {"B1_mean": b1, "P1_rms": DESIGN["fp32"], "P3_rms": DESIGN["int8"]}


def s5_synthetic(tmp):
    out, ok = {}, True
    for card in ("aifoundry3", "aifoundry1c1"):
        run = "E171" if card == "aifoundry3" else "E172"
        raw, cc, red, pred, des = synth(card, tmp, f"syn-{card}")
        o = SC.score_session(run, red, raw, cc)
        V = o["verdicts"]
        ex, reads = expected_verdicts(card, pred, o)
        R = o["primary"]["rules"]
        bad = [f"{k}: {V.get(k)} != {v}" for k, v in ex.items() if v is not None and V.get(k) != v]
        if not near(R["P8-P1"]["rms"], reads["P1_rms"], 1e-6) or not near(R["P8-P3"]["rms"], reads["P3_rms"], 1e-6):
            bad.append("P1/P3 readings")
        if not near(R["P8-B1"]["mean"], reads["B1_mean"], 1e-6):
            bad.append(f"B1 reading {R['P8-B1']['mean']} != {reads['B1_mean']}")
        if not near(o["primary"]["scale"]["s_float"], S_TRUE, 1e-9):
            bad.append(f"s {o['primary']['scale']['s_float']} != {S_TRUE}")
        # C1: every designed error against the frozen band's half-width
        S = pred["sets"]
        rows = o["primary"]["rows"]
        k_in = sum(1 for t in S["N1"] if abs(des["exp_err"][t]) <= 0.5 * (rows[t]["M10_primary_95"][1] - rows[t]["M10_primary_95"][0]) + 1e-6)
        if R["P8-C1"]["inside"] != k_in:
            bad.append(f"C1 inside {R['P8-C1']['inside']} != {k_in}")
        h_in = sum(1 for t in S["N1"] for f in [t.split(".")[0]]
                   if abs(HEAT[f]) <= 0.5 * (rows[t]["M10_heat_95"][1] - rows[t]["M10_heat_95"][0]) + 1e-9)
        exH4 = "PASS" if h_in >= SC.A2().binom_low(len(S["N1"])) else "FAIL"
        if R["P8-H4"]["inside"] != h_in or V["P8-H4"] != exH4:
            bad.append(f"H4 inside {R['P8-H4']['inside']} != {h_in} or {V['P8-H4']} != {exH4}")
        # G from its parts
        exG = "FAIL" if any(V[k].startswith("FAIL") for k in ("P8-P1", "P8-P2", "P8-P3", "P8-B1", "P8-B2", "P8-C1")) or V["P8-M1"] == "WORSE" else "PASS"
        if V["P8-G"] != exG:
            bad.append(f"G {V['P8-G']} != {exG}")
        # the command line on the same session: exit 0, scored.json and results.md written, the same verdicts
        js, md = os.path.join(tmp, f"cli-{card}.json"), os.path.join(tmp, f"cli-{card}.md")
        rr_ = subprocess.run([sys.executable, "-B", os.path.join(HERE, "score_p8_600.py"), "score", "--run", run, "--reduction", red, "--raw", raw,
                              "--ccheck", cc, "--json", js, "--md", md], capture_output=True, text=True, timeout=600)
        cli_same = rr_.returncode == 0 and os.path.exists(js) and os.path.exists(md) and load(js)["verdicts"] == V
        if not cli_same:
            bad.append(f"the command line: rc {rr_.returncode}, {rr_.stdout[-200:]} {rr_.stderr[-300:]}")
        res = {"cli": {"rc": rr_.returncode, "same_verdicts": cli_same},
               "verdicts": V, "s_float": o["primary"]["scale"]["s_float"], "c_sessions_listed": o["c_sessions"]["listed"],
               "readings": {r: {k: R[r].get(k) for k in ("rms", "mean", "inside", "d_rms", "lo95", "hi95", "F_slope", "F_level")} for r in R},
               "differences": bad}
        # (b) all fp16 N1 tiles C-excluded: their launches judged ROUNDING
        cc2 = os.path.join(tmp, f"syn-{card}", "ccheck-rounding.json")
        c = load(cc)
        f16 = set(S["by_format"]["fp16"])
        t_of = {}
        for q in load(red)["passes"]:
            for line in open(os.path.join(raw, CSN.RUNS[run]["dir"], f"p{q}", "runs.jsonl")):
                rr = json.loads(line)
                t_of[(rr["t_start_ms"], rr["t_end_ms"])] = rr["item"]
        for v in c["launches"]:
            if t_of.get((v["t_start_ms"], v["t_end_ms"])) in f16:
                v["verdict"] = "ROUNDING"
        c["summary"]["PASS"] = sum(v["verdict"] == "PASS" for v in c["launches"])
        c["summary"]["ROUNDING"] = len(c["launches"]) - c["summary"]["PASS"]
        c["summary"]["all_pass"] = False
        json.dump(c, open(cc2, "w"))
        o2 = SC.score_session(run, red, raw, cc2)
        V2 = o2["verdicts"]
        want2 = {"P8-KC": "FAIL", "P8-P2": "NOT SCORED", "P8-H2": "NOT SCORED"}
        bad2 = [f"{k}: {V2.get(k)} != {v}" for k, v in want2.items() if V2.get(k) != v]
        if sorted(o2["primary"]["rules"]["P8-KC"]["c_excluded"]) != sorted(f16):
            bad2.append("the C-excluded set is not the fp16 N1 tiles")
        if "rules_all_tiles_beside" not in o2["primary"] or o2["primary"]["rules_all_tiles_beside"]["P8-P2"]["verdict"] == "NOT SCORED":
            bad2.append("no all-tiles block, or P2 not scored there")
        if o2["primary"]["rules"]["P8-B1"]["mix"] != {"fp32": len(S["by_format"]["fp32"])}:
            bad2.append("B1's mix after the exclusion")
        res["c_excluded_case"] = {"verdicts": {k: V2[k] for k in ("P8-KC", "P8-P2", "P8-H2", "P8-B1", "P8-M1f", "P8-G")}, "differences": bad2}
        # (c) one kept pass: every rule NOT SCORED
        raw3, cc3, red3, _, _ = synth(card, tmp, f"syn1-{card}", passes=(0,))
        o3 = SC.score_session(run, red3, raw3, cc3)
        bad3 = [] if all(v == "NOT SCORED" for k, v in o3["verdicts"].items() if k != "P8-KC") else ["a rule scored on one pass"]
        res["one_pass_case"] = {"verdicts_not_scored": all(v == "NOT SCORED" for k, v in o3["verdicts"].items() if k != "P8-KC"), "differences": bad3}
        # (d) no scale anchor measured: s = 1, KA NOT SCORED
        raw4, cc4, red4, _, _ = synth(card, tmp, f"syn-s1-{card}", drop_scale=True)
        o4 = SC.score_session(run, red4, raw4, cc4)
        bad4 = []
        if o4["primary"]["scale"]["s_float"] != 1.0 or o4["verdicts"]["P8-KA"] != "NOT SCORED":
            bad4.append(f"s {o4['primary']['scale']['s_float']}, KA {o4['verdicts']['P8-KA']}")
        res["s1_case"] = {"s_float": o4["primary"]["scale"]["s_float"], "KA": o4["verdicts"]["P8-KA"], "A1": o4["verdicts"]["P8-A1"], "differences": bad4}
        # (e) refusals: a missing C log; a check that skipped one session's log; a launched stop-path test
        refusals = {}
        for lab in ("missing C log", "a log the check skipped", "stop-path test launched"):
            raw5, cc5, red5, _, _ = synth(card, tmp, f"syn-ref-{card}-{lab.replace(' ', '_')}")
            R5 = CSN.RUNS[run]
            if lab == "missing C log":
                os.remove(os.path.join(raw5, R5["dir"], f"p{int(R5['smoke'][1:]) + 10}", "c-log.jsonl"))
            elif lab == "a log the check skipped":
                c = load(cc5)
                skip = f"c-log-p{int(R5['smoke'][1:]) + 9}.jsonl"
                c["launches"] = [v for v in c["launches"] if v["log"] != skip]
                c["summary"]["launches"] = c["summary"]["PASS"] = len(c["launches"])
                json.dump(c, open(cc5, "w"))
            else:
                st = os.path.join(raw5, f"{R5['dir']}-stoptest", R5["stoptest"])
                open(os.path.join(st, "runs.jsonl"), "w").write(json.dumps({"item": "fp32.zeros", "launch": 0}) + "\n")
            js = os.path.join(tmp, f"refused-{card}-{len(refusals)}.json")
            r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "score_p8_600.py"), "score", "--run", run, "--reduction", red5,
                                "--raw", raw5, "--ccheck", cc5, "--json", js], capture_output=True, text=True, timeout=600)
            refusals[lab] = {"rc": r.returncode, "wrote": os.path.exists(js), "line": (r.stdout.strip().splitlines() or [""])[0][:200]}
        bad5 = [k for k, v in refusals.items() if v["rc"] != 4 or v["wrote"]]
        res["refusals_exit4"] = refusals
        # (f) a check anchor or a zeros anchor in the scale: exit 5
        sc_ok = {"anchors_used": ["fp32.randn", "fp16.randn"] + list(pred["sets"]["scale_anchors_pool8"])}
        f_res = {}
        for lab, extra in (("check anchor", pred["sets"]["KA"][0]), ("zeros anchor", pred["sets"]["zeros_anchors"][0]),
                           ("a non-anchor tile", pred["sets"]["N1"][0]), ("the true anchors", None)):
            scx = {"anchors_used": sc_ok["anchors_used"] + ([extra] if extra else [])}
            try:
                SC.check_scale(scx, pred)
                f_res[lab] = {"refused": False}
            except SC.Refuse as e:
                f_res[lab] = {"refused": True, "code": e.code}
        bad6 = [k for k, v in f_res.items() if (k == "the true anchors") == v["refused"] or (v["refused"] and v["code"] != 5)]
        res["scale_refusals"] = f_res
        # (g) a predictions file that is not the freeze's: exit 9
        keep = SC.freeze_sums
        try:
            SC.freeze_sums = lambda: {k: ("0" * 64 if "predictions-pool8" in k else v) for k, v in keep().items()}
            try:
                SC.load_pred(card)
                g_res = {"refused": False}
            except SC.Refuse as e:
                g_res = {"refused": True, "code": e.code}
        finally:
            SC.freeze_sums = keep
        bad7 = [] if g_res.get("code") == 9 else ["a changed predictions file was not refused with 9"]
        res["predictions_hash_refusal"] = g_res
        allbad = bad + bad2 + bad3 + bad4 + bad5 + bad6 + bad7
        res["pass"] = not allbad
        res["all_differences"] = allbad
        out[card] = res
        ok = ok and not allbad
        js = os.path.join(tmp, f"syn-scored-{card}.json")
        json.dump(o, open(js, "w"), default=str)
        out[card]["_scored"] = js
    # ka-pooled over the two synthetic sessions: 4 check anchors, PASS
    kp = SC.ka_pooled([out["aifoundry3"].pop("_scored"), out["aifoundry1c1"].pop("_scored")])
    out["ka_pooled"] = {k: kp[k] for k in ("verdict", "n") if k in kp}
    ok = ok and kp["verdict"] == "PASS" and kp["n"] == 4
    out["pass"] = bool(ok)
    return out


# ------------------------------------------------------------------------------------------------- S6
def s6_paired_independent(tmp):
    """the paired interval against a second implementation written from the registration's words alone"""
    card = "aifoundry3"
    raw, cc, red, pred, _ = synth(card, tmp, "s6")
    o = SC.score_session("E171", red, raw, cc)
    rows = o["primary"]["rows"]
    S = pred["sets"]
    out, ok = {}, True
    for rule, setn, b in (("P8-M1", "N1", "e_M9"), ("P8-M1f", "F1", "e_M9"), ("P8-M1i", "I1", "e_M9"), ("P8-A1", "F1", "e_a_priori")):
        sel = sorted(S[setn])
        a = [rows[t]["e_primary"] for t in sel]
        bb = [rows[t][b] for t in sel]
        rng = random.Random(80000 + sum(ord(c) for c in rule))
        vals = []
        for _ in range(20000):
            idx = [rng.randrange(len(sel)) for _ in sel]
            ra = math.sqrt(sum(a[i] ** 2 for i in idx) / len(idx))
            rb = math.sqrt(sum(bb[i] ** 2 for i in idx) / len(idx))
            vals.append(ra - rb)
        vals.sort()
        lo, hi = vals[500], vals[19499]
        mine = o["primary"]["rules"][rule]
        same = near(lo, mine["lo95"], 1e-12) and near(hi, mine["hi95"], 1e-12)
        out[rule] = {"independent": [lo, hi], "scorer": [mine["lo95"], mine["hi95"]], "same": same, "verdict": mine["verdict"]}
        ok = ok and same
    out["pass"] = bool(ok)
    return out


def main():
    outp = None
    if "--out" in sys.argv:
        outp = sys.argv[sys.argv.index("--out") + 1]
    tmp = tempfile.mkdtemp(prefix="p8-600-selftest-")
    res = {}
    try:
        res["S0"] = {"predictor_lists": SC.A2().check_lists(), "pool8_inputs": SC.P().check_inputs(),
                     "scorer_sha256": hashlib.sha256(open(os.path.join(HERE, "score_p8_600.py"), "rb").read()).hexdigest(),
                     "ccsessions_sha256": hashlib.sha256(open(os.path.join(HERE, "ccsessions_p8.py"), "rb").read()).hexdigest(), "pass": True}
        for k, f in (("S1", s1_lines), ("S2", s2_e163), ("S3", lambda: s3_e164(tmp)), ("S4", lambda: s4_end_to_end(tmp)),
                     ("S5", lambda: s5_synthetic(tmp)), ("S6", lambda: s6_paired_independent(tmp))):
            try:
                res[k] = f()
            except Exception as e:  # noqa: BLE001
                import traceback
                res[k] = {"pass": False, "error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()[-1500:]}
            print(k, "PASS" if res[k].get("pass") else "FAIL", flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    res["PASS"] = all(v.get("pass") for k, v in res.items() if k.startswith("S"))
    if outp:
        # the record names the tree and the temporary directory, never spells them out (the lab repo is public)
        txt = json.dumps(res, indent=1, sort_keys=True, default=str)
        txt = txt.replace(TOP + os.sep, "").replace(TOP, "<repo>").replace(tmp, "<tmp>")
        open(outp, "w").write(txt + "\n")
    print(json.dumps({k: (v.get("pass") if isinstance(v, dict) else v) for k, v in res.items()}, sort_keys=True))
    return 0 if res["PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
