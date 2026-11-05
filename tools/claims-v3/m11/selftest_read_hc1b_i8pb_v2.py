#!/usr/bin/env python3
"""Q142(h2) fix pass: the self-test of read_hc1b_i8pb_v2.py (README-h2-reader.md.dated-note-1.md). Desk only: it reads committed files
and writes only into a temporary directory (removed at the end) and its --out and --txt files. No device, no remote host, no card.
Every part of v1's self-test (selftest_read_hc1b_i8pb.py, 21666b23) is run again against v2, and the parts marked NEW test the four
changes:

  H0  the inputs: M11's three lists pass (58, 6, 9); v1's list SHA256SUMS-h2-reader (16) passes, so v1 and its self-test's output are
      unchanged; the C-session check's code is its committed code (change 2); the anchor list is fit_m10.ANCHORS; the seeds are
      80,000 plus the character codes of 'M11-HC1-B' and 'M11-I8P-B'; the minimums are pool8-registration.json's M1 (10) and M1i (6).
  H1  committed sessions:
      (a) E163's and E164's tables (S, dT_win, run length) equal fit_m6.heat_rows' rows (v1's H1a);
      (b) h on E164 and E163 equals heldout-m10.json's session heat scales within 1e-4, any anchor over 5.0 s named (v1's H1b);
      (c) the int8 pair E164 / E163 against RK4 (v1's H1c);
      (d) both readings on the stand-ins, in-sample and post hoc (v1's H1d);
      (e) NEW, change 1: every session M10's heat rows read (fit_m6.EXPDIR, E137, E140 and fit_m10.HEAT_EXTRA: 30): v2's table
          accepts each, and equals fit_m6.heat_rows' rows within 1e-9 in S, dT_win and run length on every row compared; E157,
          E141 and E82 named; v1's table refuses exactly the sessions that set a pass aside (exit 6) and accepts the others;
      (f) NEW, change 1: every committed reduction in reduce_e78's form (docs/reports/data/*/e<N>.json with 'runs' and 'kept' and a
          runs.csv beside it): v2's runs-table check accepts all of them; those that set a pass aside are counted and named;
      (g) NEW, change 4: the committed-files record on E163's committed files (all committed, the commit named) and on a copy
          outside the repository (not committed);
      (h) NEW, change 2: the C-session check as v2 calls it reads ok on E163's committed data dir (the collectors' layout, gzipped C
          logs).
  H2  synthetic E171 and E172 sessions with known answers, each written as reduce_e78 writes a reduction (every run in runs.csv, with
      its fail count and position), scored by the committed scorer (score_p8_600.py score, in this process, as the collectors call
      it), then read by v2's command line: D1-D9 as v1's; and NEW:
      V1  v1 and v2 read D1's pair to the same readings, every number and every tile's error equal;
      D10 change 1: E172 with five passes, the fourth set aside and the fifth configuration-flagged as reduce_e78 records them, and one
          failed run in a kept pass: the committed scorer scores it (exit 0); v2 reads it to exactly D1's readings; v1 refuses it (6);
      D11 change 2: a pass's C log removed after scoring, and the smoke's: v2 refuses 4 (v1 read both); a C log missing before
          scoring: the committed scorer exits 4 and writes no scored file, and v2 refuses 4 (v1: 2); the scored file missing with
          every C log in place: v2 refuses 2;
      D12 change 3: fp32.randn run 5.5 s long with its dT at half the law, and one N1 tile run 5.5 s long: the anchor is named and
          left out of h1 (h1 = the median of the other eight, computed here), h1 with it reported beside (the median of all nine);
          the tile is named and kept (n = 31); the C-clean arm leaves the anchor out too;
      D13 change 4: a reading from files outside the repository records the departure from REGISTRATION.md sections 8 and 11.
  H3  refusals, each by v2's command line (nothing written): v1's cases (usage 2; E171 given as E172 6; the pair swapped 6; E171's file
      relabelled 6; E172 twice 6; no c_sessions 4; no check of C 4; another reduction 6; a runs table short by one run 6; another
      session's check of C 6); NEW: a runs table with another pass's rows (d), a kept run marked failed (c, e), a kept pass relabelled
      (b, d), each 6; E157's committed runs table cut to its kept runs (v1's form) refused by v2's table (a); in this process, M11's
      list changed 9 and the C-session check's list changed 9.

    /usr/bin/python3 -B tools/claims-v3/m11/selftest_read_hc1b_i8pb_v2.py [--out <file.json>] [--txt <file.txt>]

Every line is masked (the repo and the temporary directory) before it is printed. Exit 0 when every part passes. Standard library and
numpy (through fit_m10's chain and the predictor). SPDX-License-Identifier: Apache-2.0
"""
import collections
import contextlib
import csv
import glob
import io
import json
import math
import os
import random
import shutil
import statistics
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import read_hc1b_i8pb_v2 as R  # noqa: E402
import read_hc1b_i8pb as R1  # noqa: E402  (v1, 21666b23, unchanged: H1e, V1 and D10 run it beside v2)
SC, V2, V3 = R.SC, R.V2, R.V3
DD = os.path.join(TOP, "docs", "reports", "data")
M10D = R.M10D
E163D = os.path.join(DD, "2026-11-04-e163-blind7-aifoundry3")
E164D = os.path.join(DD, "2026-11-04-e164-blind7-card1")
B7 = os.path.join(TOP, "tools", "claims-v3", "kinds", "blind7")
V2_READER = os.path.join(HERE, "read_hc1b_i8pb_v2.py")
V1_READER = os.path.join(HERE, "read_hc1b_i8pb.py")
load = lambda p: json.load(open(p))  # noqa: E731
LINES, RESULTS = [], {}
TMP = {"d": None}


def mask(t):
    t = str(t).replace(TOP + os.sep, "").replace(TOP, "<repo>")
    if TMP["d"]:
        t = t.replace(TMP["d"], "<tmp>")
    return t


def say(s):
    s = mask(s)
    LINES.append(s)
    print(s, flush=True)


def part(name, ok, detail):
    RESULTS[name] = {"pass": bool(ok), "detail": json.loads(mask(json.dumps(detail, default=str)))}
    say(f"{name}: {'PASS' if ok else 'FAIL'}  {mask(json.dumps(detail, default=str))[:1200]}")


def list_ok(path):
    bad = []
    lines = R.read_list(path)
    for h, p in lines:
        q = os.path.join(TOP, p)
        if not os.path.isfile(q) or R.sha(q) != h:
            bad.append(p)
    return len(lines), bad


# ------------------------------------------------------------------------------------------------- H0
def h0():
    g = R.frozen_code()
    lists = R.check_m11_lists()
    n1, bad1 = list_ok(os.path.join(HERE, "SHA256SUMS-h2-reader"))
    sys.path.insert(0, M10D)
    import fit_m10 as FM  # noqa: E402
    ok = (lists == {"SHA256SUMS": 58, "SHA256SUMS-m11": 6, "SHA256SUMS-a1": 9} and tuple(FM.ANCHORS) == R.M10_ANCHORS
          and R.seed_of("M11-HC1-B") == 80000 + sum(map(ord, "M11-HC1-B")) and g["min"] == {"N1": 10, "I1": 6}
          and n1 == 16 and not bad1 and len(g["c_session_code"]) == 3 and R.HEAT_TRUN_MAX == FM.M6.HEAT_TRUN_MAX)
    part("H0", ok, {"lists": lists, "v1_list": [n1, bad1], "anchors_equal_fit_m10": tuple(FM.ANCHORS) == R.M10_ANCHORS,
                    "min": g["min"], "seeds": {r: R.seed_of(r) for r in (R.RULE_HC1B, R.RULE_I8PB)}, "scorer": g["scorer"][:12],
                    "v2": g["v2"][:12], "v3": g["v3"][:12], "c_session_code": {k: v[:12] for k, v in g["c_session_code"].items()},
                    "heat_trun_max": [R.HEAT_TRUN_MAX, FM.M6.HEAT_TRUN_MAX]})
    return FM


# ------------------------------------------------------------------------------------------------- H1, committed sessions
def heat_rows_for(FM, sessions):
    old = dict(FM.M6.EXPDIR)
    FM.M6.EXPDIR.clear()
    FM.M6.EXPDIR.update(sessions)
    try:
        return FM.M6.heat_rows([])
    finally:
        FM.M6.EXPDIR.clear()
        FM.M6.EXPDIR.update(old)


def h1(FM):
    hr = heat_rows_for(FM, {"E163": os.path.basename(E163D), "E164": os.path.basename(E164D)})
    tabs, worst, n = {}, {"S": 0.0, "dT": 0.0, "T_run": 0.0}, 0
    for exp, d in (("E163", E163D), ("E164", E164D)):
        names = sorted(load(os.path.join(d, f"{exp.lower()}.json"))["items"])
        tabs[exp], _ = R.session_table(os.path.join(d, f"{exp.lower()}.json"), os.path.join(d, "runs.csv"), names)
    for r in hr:
        t = tabs[r["exp"]][r["key"]]
        for k_, kk in (("S", "S"), ("dT", "dT"), ("T_run", "T_run")):
            worst[k_] = max(worst[k_], abs(float(r[kk]) - float(t[k_])))
        n += 1
    part("H1a", n > 100 and max(worst.values()) <= 1e-9, {"rows_compared": n, "max_abs_diff": worst})
    held = load(os.path.join(M10D, "heldout-m10.json"))["heat_c1"]["session_heat_scales_all_rows"]
    hs = {}
    for exp, card, key in (("E164", "aifoundry1c1", "E164|aifoundry1-c1"), ("E163", "aifoundry3", "E163|aifoundry3")):
        h, rat = R.h_scale(tabs[exp], card, R.M10_ANCHORS)
        hs[exp] = {"h": h, "committed": held[key], "anchors": sorted(rat), "diff": abs(h - held[key]),
                   "long_anchors": R.long_anchors(tabs[exp], R.M10_ANCHORS)}
    part("H1b", all(v["diff"] <= 1e-4 for v in hs.values()), hs)
    rk = load(os.path.join(E164D, "rank4-e163-e164.json"))["families"]["int8"]
    p1 = load(os.path.join(TOP, "tools", "claims-v3", "kinds", "blind8", "predictions-pool8-aifoundry1c1.json"))
    p3 = load(os.path.join(TOP, "tools", "claims-v3", "kinds", "blind8", "predictions-pool8-aifoundry3.json"))
    an = ("int8.full", "int8.anchor7_full_a", "int8.anchor7_full_b")
    plain = {a: tabs["E164"][a]["D"] / tabs["E163"][a]["D"] for a in an}
    diffs = {a: abs(plain[a] - rk["anchor_ratio"][a]) for a in rk["anchor_ratio"]}
    arm = sorted(plain.values())[1]
    anch = {exp: {a: {"D": tabs[exp][a]["D"], "Dhat": tabs[exp][a]["rate"] * p["m10_anchors"][a]["k_J_per_op"]} for a in an}
            for exp, p in (("E164", p1), ("E163", p3))}
    k, q = R.i8p_k(anch["E164"], anch["E163"], an)
    c = p1["m10_anchors"]["int8.full"]["k_J_per_op"] / p3["m10_anchors"]["int8.full"]["k_J_per_op"]
    ind = sorted(plain[a] * tabs["E163"][a]["rate"] / tabs["E164"][a]["rate"] for a in an)[1] / c
    ok_c = max(diffs.values()) <= 1e-9 and abs(arm - rk["arm_with_E78_anchors"]["s_anchor"]) <= 1e-9 and abs(k - ind) <= 1e-12
    part("H1c", ok_c, {"plain_ratio_vs_RK4": diffs, "arm_median": arm, "RK4_arm": rk["arm_with_E78_anchors"]["s_anchor"],
                       "k": k, "k_independent": ind, "card_term_ratio": c, "q": q})
    man = load(os.path.join(B7, "blind7.json"))["tiles"]
    p1n = sorted(m["name"] for m in man if m.get("priority") == 1 and not m.get("anchor"))
    tiles = {t: tabs["E164"][t] for t in p1n if t in tabs["E164"]}
    hc = R.hc1b_core({t: {k_: tiles[t][k_] for k_ in ("dT", "S", "T_run")} for t in tiles}, tabs["E164"], "aifoundry1c1",
                     R.M10_ANCHORS, 10)
    rows = {(r["exp"], r["key"]): r for r in load(os.path.join(M10D, "rows-m10.json"))}
    i1 = {t: {"D": tabs["E164"][t]["D"], "M10": rows[("E164", t)]["M10_insample_pred_w"]} for t in p1n
          if t.startswith("int8.") and ("E164", t) in rows}
    ip = R.i8pb_core(anch["E164"], anch["E163"], i1, an, 6)
    keep = ("verdict", "h", "k", "n", "d_rms_c", "d_rms_w", "lo95", "hi95", "rms_without_c", "rms_with_c", "rms_without_w", "rms_with_w",
            "bias_without_c", "bias_with_c", "bias_without_w", "bias_with_w", "overcorrects", "I1_bias_overcorrects")
    part("H1d", hc.get("verdict") in ("BETTER", "WORSE", "NOT RESOLVED") and ip.get("verdict") in ("BETTER", "WORSE", "NOT RESOLVED"),
         {"label": "stand-in, in-sample, post hoc (E163 and E164 are in M10's training rows; pool 7's priority-1 tiles for N1 and I1)",
          "HC1-B_on_E164": {k_: hc.get(k_) for k_ in keep if k_ in hc}, "I8P-B_on_E164_E163": {k_: ip.get(k_) for k_ in keep if k_ in ip}})
    # H1e: every session M10's heat rows read
    S = dict(FM.M6.EXPDIR)
    S["E137"] = "2026-11-02-e137-fp16-sign-rest"
    S["E140"] = "2026-11-02-e140-blind4"
    S.update(FM.HEAT_EXTRA)
    hr = heat_rows_for(FM, S)
    per, refused2, setaside, v1_refused, v1_bad = {}, [], [], [], []
    for exp, d in sorted(S.items()):
        rp, cp = os.path.join(DD, d, f"{exp.lower()}.json"), os.path.join(DD, d, "runs.csv")
        res = load(rp)
        names = sorted(res.get("items", {}))
        try:
            tab, tchk = R.session_table(rp, cp, names)
        except R.Refuse as e:
            refused2.append(f"{exp}: {e}")
            continue
        sa = tchk["runs_table"]["passes_set_aside"]
        if sa:
            setaside.append(exp)
        try:
            R1.session_table(rp, cp, names)
            v1r = False
        except R1.Refuse as e:
            v1r = e.code == 6
            if e.code != 6:
                v1_bad.append(exp)
        if v1r:
            v1_refused.append(exp)
        w, n_ = {"S": 0.0, "dT": 0.0, "T_run": 0.0}, 0
        for r in (x for x in hr if x["exp"] == exp):
            t = tab.get(r["key"]) or {}
            if t.get("dT") is None or t.get("S") is None or t.get("T_run") is None:
                continue
            for k_ in ("S", "dT", "T_run"):
                w[k_] = max(w[k_], abs(float(r[k_]) - float(t[k_])))
            n_ += 1
        per[exp] = {"heat_rows": sum(1 for x in hr if x["exp"] == exp), "compared": n_, "max_abs_diff": max(w.values()),
                    "rows": tchk["runs_table"]["rows"], "kept": tchk["runs_table"]["reduction_kept"], "set_aside": sa}
    named = {e: per.get(e) for e in ("E157", "E141", "E82")}
    ok_e = (not refused2 and len(per) == 30 and all(v["max_abs_diff"] <= 1e-9 for v in per.values())
            and sum(v["compared"] for v in per.values()) > 800 and sorted(v1_refused) == sorted(setaside) and not v1_bad
            and all(named[e] and named[e]["set_aside"] and named[e]["compared"] == named[e]["heat_rows"] for e in named))
    part("H1e", ok_e, {"sessions": len(per), "refused_by_v2": refused2, "rows_compared": sum(v["compared"] for v in per.values()),
                       "max_abs_diff_any": max(v["max_abs_diff"] for v in per.values()), "named": named,
                       "set_aside_sessions": setaside, "v1_refused_exactly_those": sorted(v1_refused) == sorted(setaside)})
    # H1f: every committed reduction in reduce_e78's form
    acc, rej, sa_all = 0, [], []
    for p in sorted(glob.glob(os.path.join(DD, "*", "e*.json"))):
        b = os.path.basename(p)
        if not b[1:-5].isdigit():
            continue
        try:
            res = load(p)
        except ValueError:
            continue
        cp = os.path.join(os.path.dirname(p), "runs.csv")
        if not isinstance(res, dict) or "kept" not in res or "runs" not in res or not os.path.exists(cp):
            continue
        _, runs = R.run_lengths(cp)
        try:
            chk = R.runs_table_check(res, runs, cp)
            acc += 1
            if chk["passes_set_aside"] or chk["passes_config_flags"]:
                sa_all.append(b[:-5].upper())
        except R.Refuse as e:
            rej.append(f"{os.path.relpath(p, DD)}: {e}"[:200])
    part("H1f", acc >= 45 and not rej and len(sa_all) >= 14, {"accepted": acc, "refused": rej, "setting_a_pass_aside": len(sa_all),
                                                             "which": sa_all})
    # H1g: the committed-files record
    f = {"scored": os.path.join(E163D, "scored.json"), "reduction": os.path.join(E163D, "e163.json"),
         "runs": os.path.join(E163D, "runs.csv"), "ccheck": os.path.join(E163D, "ccheck", "ccheck-all.json"),
         "raw": os.path.join(E163D, "aifoundry3")}
    cs = R.committed_state(f)
    cp_ = os.path.join(TMP["d"], "e163-copy")
    os.makedirs(cp_, exist_ok=True)
    g = dict(f)
    for k_ in ("scored", "reduction", "runs"):
        g[k_] = os.path.join(cp_, os.path.basename(f[k_]))
        shutil.copy(f[k_], g[k_])
    cs2 = R.committed_state(g)
    ok_g = (cs["all_committed"] and cs["latest_commit"] and all(v.get("committed") for v in cs["files"].values())
            and not cs2["all_committed"] and all(cs2["files"][k_].get("why") == "outside this repository" for k_ in ("scored", "reduction", "runs")))
    part("H1g", ok_g, {"E163_committed": cs, "copy_outside": {k_: v.get("committed") for k_, v in cs2["files"].items()}})
    # H1h: the C-session check as v2 calls it, on E163's committed data dir
    o = {"c_sessions": {"sessions": []}}
    try:
        rec = R.c_sessions("E163", f, o)
        ok_h = rec["ok"] and rec["listed"] == 7 and rec["stoptest"] == "OK"
    except R.Refuse as e:
        rec, ok_h = {"refused": e.code, "msg": str(e)[:300]}, False
    part("H1h", ok_h, {"E163": rec})


# ------------------------------------------------------------------------------------------------- H2, the synthetic sessions
S_TRUE = 1.004
R_RHO = 0.98
E78_SIX = ("fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full")
BLIND_BASE, POSTHOC_BASE = 1_800_000_000_000, 1_700_000_000_000


def t_run_of(n):
    """run lengths on a 0.125 s grid (4.25-4.75 s): whole milliseconds, exact in binary, so the reader's run length is the design's"""
    return 4.5 + 0.125 * ((sum(map(ord, n)) % 5) - 2)


def build(run, label, H_TRUE=1.0, H_TILE=1.0, K_TRUE=1.0, K_TILE=1.0, base=BLIND_BASE, passes=3, fail=(), nan_heat=False,
          noise_c=0.02, noise_w=0.005, jitter=True, r_rho=R_RHO, set_aside=(), cfg_flag=(), failed_runs=(), trun=None, dT_ratio=None,
          clog_missing=None):
    """v1's design (selftest_read_hc1b_i8pb.build), written as reduce_e78 writes a reduction: runs.csv holds EVERY run of every pass
    with its position and fail count; the reduction counts 'runs', 'kept' (no failed run, no run of a set-aside or flagged pass) and
    lists 'failed', 'passes_set_aside' and 'passes_config_flags'; its per-pass values and item means are the kept passes'.
    set_aside / cfg_flag: pass indices (0-based); failed_runs: (pass index, item) whose LAST run in the pass failed a gate;
    trun: {name: run length s}; dT_ratio: {name: dT / law}; clog_missing: a session directory name whose C log is removed before
    scoring (the scorer then refuses with 4: returned, not raised)"""
    trun, dT_ratio = dict(trun or {}), dict(dT_ratio or {})
    card = R.RUN_CARD[run]
    Rr = SC.CS().RUNS[run]
    pred = load(os.path.join(SC.B8, f"predictions-pool8-{card}.json"))
    T, S = pred["tiles"], pred["sets"]
    rate = {t: pred["rates"][t]["stated_per_s"] for t in SC.FORMATS}
    zs = {t: pred["zeros_S_w"][t]["mean"] for t in SC.FORMATS}
    m10a = pred["m10_anchors"]
    b = os.path.join(TMP["d"], label)
    raw = os.path.join(b, "raw")
    num0 = int(Rr["smoke"][1:]) + 9
    pass_ids = [num0 + i for i in range(passes)]
    bad_p = {pass_ids[i] for i in set_aside} | {pass_ids[i] for i in cfg_flag}
    kept_ids = [q for q in pass_ids if q not in bad_p]
    D = {}
    for n in T:
        t = T[n]["type"]
        D[n] = (S_TRUE if t in SC.FLOATS else 1.0) * rate[t] * T[n]["M10"]["k_J_per_op"]
    for n in ("fp32.randn", "fp16.randn"):
        D[n] = S_TRUE * rate[n.split(".")[0]] * m10a[n]["k1_J_per_op"]
    for n in S["scale_anchors_pool8"]:
        D[n] = S_TRUE * rate[T[n]["type"]] * T[n]["M10"]["k1_J_per_op"]
    for n in ("fp32.zeros", "fp16.zeros", "int8.zeros"):
        D[n] = 0.0
    D["anchor_pi"] = 7.0
    k_i8 = {n: (m10a[n]["k_J_per_op"] if n in m10a else T[n]["M10"]["k_J_per_op"]) for n in R.I8P_ANCHORS}
    for n in R.I8P_ANCHORS:
        D[n] = (K_TRUE if run == "E172" else 1.0) * r_rho * rate["int8"] * k_i8[n]
    i1 = sorted(S["I1"])
    for i, n in enumerate(i1):
        u = (1 if i % 2 == 0 else -1) * (1.0 + 0.1 * (i // 2))
        D[n] = (K_TILE if run == "E172" else 1.0) * rate["int8"] * T[n]["M10"]["k_J_per_op"] + noise_w * u
    roles = pred["roles"]
    heat_anchors = sorted(["fp32.randn", "fp16.randn", "int8.full"] + [n for n, r in roles.items() if r.get("role") == "scale"])
    typ = lambda n: T[n]["type"] if n in T else ("fp32" if n == "anchor_pi" else n.split(".")[0])  # noqa: E731
    Sv = {n: D[n] + zs[typ(n)] for n in D}
    Tr = {n: trun.get(n, t_run_of(n)) for n in D}
    L = {n: R.law(Sv[n], Tr[n], card) for n in D}
    dT = {n: L[n] for n in D}
    n1 = sorted(S["N1"])
    for i, n in enumerate(n1):
        u = (1 if i % 2 == 0 else -1) * (1.0 + 0.1 * (i // 2))
        dT[n] = H_TILE * L[n] + noise_c * u
    for j, n in enumerate(heat_anchors):
        dT[n] = H_TRUE * (1 + 0.002 * (j - 4)) * L[n]
    for n in [n for n, r in roles.items() if r.get("role") == "check"]:
        dT[n] = H_TILE * L[n]
    for n, q in dT_ratio.items():
        dT[n] = q * L[n]
    items, per = {}, {str(q): {} for q in kept_ids}
    jit = (lambda n, q: 1e-9 * (((sum(map(ord, n)) + q) % 5) - 2)) if jitter else (lambda n, q: 0.0)  # noqa: E731
    for n in D:
        t = typ(n)
        vals = [D[n] + jit(n, q) for q in kept_ids]
        dv = float("nan") if (nan_heat and n in heat_anchors) else dT[n]
        items[n] = {"type": t, "D": {"mean": sum(vals) / len(vals), "se": 1e-4, "n": len(vals)}, "rate": {"mean": rate[t]},
                    "dT_win": {"mean": dv}, "S": {"mean": Sv[n]}}
        for q, x in zip(kept_ids, vals):
            per[str(q)][n] = {"D": x, "dT_win": dv, "S": Sv[n], "rate": rate[t]}
    tiles = sorted(T)
    launches, csvrows, k = [], [], [0]
    failed_list = []
    fail_last = {(pass_ids[i], n) for i, n in failed_runs}

    def seq_of(q):
        thirds = [tiles[0:22], tiles[22:43], tiles[43:]]
        out = ["anchor_pi"]
        for th in thirds:
            out += list(E78_SIX) + th
        return out + ["anchor_pi"]

    def write_session(d, names, q=None):
        os.makedirs(d, exist_ok=True)
        prev_end = None
        last_pos = {n: i for i, n in enumerate(names)}
        with open(os.path.join(d, "runs.jsonl"), "w") as rf, open(os.path.join(d, "c-log.jsonl"), "w") as cf:
            cf.write(json.dumps({"ccheck": 1, "kind": "host", "host_sha256": "x", "kernel_sha256": "y"}) + "\n")
            for pos, n in enumerate(names):
                t0 = base + k[0] * 20000
                k[0] += 1
                t1 = t0 + int(round(Tr.get(n, 4.5) * 1000))
                rf.write(json.dumps({"item": n, "launch": 0, "t_start_ms": t0, "t_end_ms": t1}) + "\n")
                cf.write(json.dumps({"ccheck": 1, "kind": "c", "type": typ(n), "launch": 0, "iters": 1, "t_start_ms": t0, "t_end_ms": t1,
                                     "ok": True, "groups": []}) + "\n")
                launches.append({"log": f"c-log-{os.path.basename(d)}.jsonl", "t_start_ms": t0, "t_end_ms": t1,
                                 "verdict": "FAIL" if n in fail else "PASS", "type": typ(n)})
                if q is not None:
                    fl = (q, n) in fail_last and last_pos[n] == pos
                    reasons = ["window 3 samples, gap 900 ms (a synthetic per-run gate)"] if fl else []
                    if fl:
                        failed_list.append([q, n, pos, reasons])
                    csvrows.append({"pass": str(q), "item": n, "pos": pos, "t0_ms": t0,
                                    "prev_end_ms": prev_end if prev_end is not None else t0 - 1000,
                                    "D": D.get(n), "dT_win": dT.get(n), "S": Sv.get(n), "type": typ(n), "fail": len(reasons),
                                    "fail_reasons": ";".join(reasons)})
                prev_end = t1
        open(os.path.join(d, "block.json"), "w").write('{"status":"ok"}\n')

    write_session(os.path.join(raw, f"{Rr['dir']}-smoke", Rr["smoke"]), ["anchor_pi", "fp32.zeros"])
    for q in pass_ids:
        write_session(os.path.join(raw, Rr["dir"], f"p{q}"), seq_of(q), q)
    os.makedirs(os.path.join(raw, f"{Rr['dir']}-stoptest", Rr["stoptest"]), exist_ok=True)
    cc = os.path.join(b, "ccheck.json")
    nf = sum(1 for v in launches if v["verdict"] == "FAIL")
    json.dump({"summary": {"launches": len(launches), "PASS": len(launches) - nf, "ROUNDING": 0, "UNMODELLED": 0, "FAIL": nf,
                           "all_pass": nf == 0}, "launches": launches}, open(cc, "w"))
    runs_csv = os.path.join(b, "runs.csv")
    with open(runs_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["pass", "item", "pos", "t0_ms", "prev_end_ms", "D", "dT_win", "S", "type", "fail",
                                           "fail_reasons"])
        w.writeheader()
        w.writerows(csvrows)
    kept_n = sum(1 for r in csvrows if int(r["pass"]) in kept_ids and r["fail"] == 0)
    red = os.path.join(b, f"{run.lower()}.json")
    json.dump({"experiment": run, "card": "aifoundry3" if card == "aifoundry3" else "aifoundry1-c1", "passes": kept_ids,
               "runs": len(csvrows), "kept": kept_n, "failed": failed_list,
               "passes_set_aside": [{"pass": pass_ids[i], "why": ["int8.zeros spans 0.700 W (a synthetic pass gate)"]} for i in set_aside],
               "passes_config_flags": [{"pass": pass_ids[i], "config_start": {"tdp_w": 5}, "config_end": {"tdp_w": 5}} for i in cfg_flag],
               "items": items, "per_pass": per}, open(red, "w"))
    if clog_missing:
        for walked, _, files in os.walk(raw):
            if os.path.basename(walked) == clog_missing and "c-log.jsonl" in files:
                os.remove(os.path.join(walked, "c-log.jsonl"))
    js = os.path.join(b, "scored.json")
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            rc = SC.main(["score", "--run", run, "--reduction", red, "--raw", raw, "--ccheck", cc, "--json", js])
        except SC.Refuse as e:
            rc = e.code
    out = {"run": run, "scored": js, "reduction": red, "runs": runs_csv, "raw": raw, "ccheck": cc, "base": b, "scorer_rc": rc,
           "pass_ids": pass_ids, "kept_ids": kept_ids, "design": {"H_TRUE": H_TRUE, "H_TILE": H_TILE, "K_TRUE": K_TRUE, "K_TILE": K_TILE}}
    if clog_missing is None and (rc != 0 or not os.path.exists(js)):
        raise RuntimeError(f"the committed scorer exited {rc} on {label}")
    return out


def args_of(s2, s1=None, out=None):
    a = []
    for s in ([s2] + ([s1] if s1 else [])):
        lc = s["run"].lower()
        a += [f"--{lc}-scored", s["scored"], f"--{lc}-reduction", s["reduction"], f"--{lc}-runs", s["runs"], f"--{lc}-raw", s["raw"],
              f"--{lc}-ccheck", s["ccheck"]]
    return a + ["--json", out or os.path.join(TMP["d"], "read.json")]


def cli(args, timeout=600, reader=V2_READER):
    r = subprocess.run([sys.executable, "-B", reader, "read", *args], capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout.strip().splitlines() or [""])[-1][:600]


def read_pair(tag, s2, s1, reader=V2_READER):
    out = os.path.join(TMP["d"], f"read-{tag}.json")
    if os.path.exists(out):
        os.remove(out)
    rc, line = cli(args_of(s2, s1, out), reader=reader)
    return rc, line, (load(out) if os.path.exists(out) else None)


def independent_paired(e1, e0, sel, rule):
    """the registration's words, re-implemented here: d = rms(with) - rms(without) over the tiles; 20,000 draws, each of as many tiles
    as the set holds, with replacement, from random.Random(80,000 + the rule's character codes); the 2.5% and 97.5% order statistics"""
    sel = sorted(sel)
    f = lambda e, s: math.sqrt(sum(e[t] ** 2 for t in s) / len(s))  # noqa: E731
    rng = random.Random(80000 + sum(map(ord, rule)))
    ds = []
    for _ in range(20000):
        s = [sel[rng.randrange(len(sel))] for _ in sel]
        ds.append(f(e1, s) - f(e0, s))
    ds.sort()
    return f(e1, sel) - f(e0, sel), ds[500], ds[19499]


KEYS_H = ("verdict", "h", "d_rms_c", "lo95", "hi95", "n", "rms_without_c", "rms_with_c", "bias_without_c", "bias_with_c", "overcorrects",
          "anchor_ratios", "h_c_clean", "tiles", "at_M10_primary_D", "check_anchors", "label")
KEYS_I = ("verdict", "k", "d_rms_w", "lo95", "hi95", "n", "rms_without_w", "rms_with_w", "bias_without_w", "bias_with_w",
          "I1_bias_overcorrects", "anchor_ratios", "tiles", "check_anchor", "label")


def same_readings(a, b):
    """every number of both readings equal (v1's keys), exactly"""
    da = [k for k in KEYS_H if a["HC1-B"].get(k) != b["HC1-B"].get(k)] + [k for k in KEYS_I if a["I8P-B"].get(k) != b["I8P-B"].get(k)]
    return not da, da


def h2():
    S = {}
    S["D1"] = (build("E172", "d1-e172", 0.90, 0.90, 0.97, 0.97), build("E171", "d1-e171"))
    rc, line, o = read_pair("d1", *S["D1"])
    h, i = o["HC1-B"], o["I8P-B"]
    t = h["tiles"]
    d0, lo, hi = independent_paired({k: v["e_with_c"] for k, v in t.items()}, {k: v["e_without_c"] for k, v in t.items()}, list(t),
                                    "M11-HC1-B")
    ti = i["tiles"]
    e0, lo2, hi2 = independent_paired({k: v["e_with_w"] for k, v in ti.items()}, {k: v["e_without_w"] for k, v in ti.items()}, list(ti),
                                      "M11-I8P-B")
    ok = (rc == 0 and h["verdict"] == "BETTER" and i["verdict"] == "BETTER" and abs(h["h"] - 0.90) <= 1e-8 and abs(i["k"] - 0.97) <= 1e-8
          and h["label"] == "blind" and i["label"] == "blind" and abs(h["control_h3_E171"]["h3"] - 1.0) <= 1e-8
          and (d0, lo, hi) == (h["d_rms_c"], h["lo95"], h["hi95"]) and (e0, lo2, hi2) == (i["d_rms_w"], i["lo95"], i["hi95"])
          and h["n"] == 31 and i["n"] == 12 and not h["not_wanted"]["met"] and h["at_M10_primary_D"]["reading"] in ("BETTER", "WORSE",
                                                                                                                     "NOT RESOLVED")
          and h["anchors_long_runs_left_out"] == [] and o["sessions"]["E172"]["c_sessions_rerun"]["ok"]
          and o["sessions"]["E172"]["c_sessions_rerun"]["differ_from_scored"] == [])
    part("H2-D1", ok, {"rc": rc, "line": line, "HC1-B": [h["verdict"], h["h"], h["d_rms_c"], h["lo95"], h["hi95"], h["n"], h["label"]],
                       "I8P-B": [i["verdict"], i["k"], i["d_rms_w"], i["lo95"], i["hi95"], i["n"], i["label"]],
                       "independent_interval_identical": [(d0, lo, hi) == (h["d_rms_c"], h["lo95"], h["hi95"]),
                                                          (e0, lo2, hi2) == (i["d_rms_w"], i["lo95"], i["hi95"])],
                       "h3": h["control_h3_E171"]["h3"], "at_M10_primary_D": h["at_M10_primary_D"]["reading"],
                       "c_sessions_rerun": o["sessions"]["E172"]["c_sessions_rerun"]})
    S["o1"] = o
    # V1: v1 reads D1's pair (no set-aside pass, no long run) to the same readings
    rc1, line1, ov1 = read_pair("d1-v1", *S["D1"], reader=V1_READER)
    same, diff = same_readings(o, ov1) if ov1 else (False, ["v1 wrote nothing"])
    part("H2-V1", rc1 == 0 and same, {"v1_rc": rc1, "v1_line": line1, "same": same, "differ": diff})
    S["D2"] = (build("E172", "d2-e172", 0.90, 1.00, 0.97, 1.00, base=POSTHOC_BASE), build("E171", "d2-e171", base=POSTHOC_BASE))
    rc, line, o = read_pair("d2", *S["D2"])
    h, i = o["HC1-B"], o["I8P-B"]
    ok = (rc == 0 and h["verdict"] == "WORSE" and i["verdict"] == "WORSE" and h["label"] == "post hoc" and i["label"] == "post hoc"
          and h["not_wanted"]["met"] and h["not_wanted"]["HC1-B reads WORSE"] and i["not_wanted"]["I8P-B reads WORSE"])
    part("H2-D2", ok, {"rc": rc, "HC1-B": [h["verdict"], h["label"], h["not_wanted"]], "I8P-B": [i["verdict"], i["label"]],
                       "why": h["precedence"]["why"]})
    S["D3"] = (build("E172", "d3-e172", 1.0, 1.0, 1.0, 1.0, passes=2, jitter=False, r_rho=1.0),
               build("E171", "d3-e171", passes=2, jitter=False, r_rho=1.0))
    rc, line, o = read_pair("d3", *S["D3"])
    h, i = o["HC1-B"], o["I8P-B"]
    ok = (rc == 0 and h["verdict"] == "NOT RESOLVED" and i["verdict"] == "NOT RESOLVED" and h["d_rms_c"] == 0.0 and i["d_rms_w"] == 0.0
          and h["h"] == 1.0 and i["k"] == 1.0 and h["lo95"] == h["hi95"] == 0.0 and i["lo95"] == i["hi95"] == 0.0)
    part("H2-D3", ok, {"rc": rc, "HC1-B": [h["verdict"], h["h"], h["d_rms_c"], h["lo95"], h["hi95"]],
                       "I8P-B": [i["verdict"], i["k"], i["d_rms_w"], i["lo95"], i["hi95"]]})
    S["D4"] = (build("E172", "d4-e172", 1.10, 1.02, 1.05, 1.01), build("E171", "d4-e171"))
    rc, line, o = read_pair("d4", *S["D4"])
    h, i = o["HC1-B"], o["I8P-B"]
    ok = (rc == 0 and h["verdict"] == "WORSE" and h["overcorrects"] and h["not_wanted"]["h1 over-corrects on E172's N1"]
          and i["verdict"] == "WORSE" and i["I1_bias_overcorrects"])
    part("H2-D4", ok, {"rc": rc, "HC1-B": [h["verdict"], h["bias_without_c"], h["bias_with_c"], h["overcorrects"]],
                       "I8P-B": [i["verdict"], i["bias_without_w"], i["bias_with_w"], i["I1_bias_overcorrects"]]})
    S["D5"] = (build("E172", "d5-e172", 0.90, 0.90, 0.97, 0.97, fail=("int8.anchor8_full_a_4aac84",)),
               build("E171", "d5-e171", fail=("int8.full",)))
    rc, line, o = read_pair("d5", *S["D5"])
    h, i = o["HC1-B"], o["I8P-B"]
    hc = sorted(h["anchor_ratios"].values())
    ok = (rc == 0 and abs(i["k"] - 0.97) <= 1e-8 and i["anchors_left_out"] == ["int8.anchor8_full_a_4aac84", "int8.full"]
          and i["anchors_used"] == ["int8.anchor8_full_b_935710"] and len(h["anchor_ratios"]) == 9 and abs(h["h"] - 0.90) <= 1e-8
          and h["anchors_not_C_clean"] == ["int8.anchor8_full_a_4aac84"] and len(h["c_clean_anchors"]) == 8
          and abs(h["h_c_clean"] - statistics.median([v for n, v in h["anchor_ratios"].items() if n != "int8.anchor8_full_a_4aac84"])) <= 1e-12
          and h["set"]["c_excluded"] == [])
    part("H2-D5", ok, {"rc": rc, "k": i["k"], "left_out": i["anchors_left_out"], "used": i["anchors_used"], "h": h["h"],
                       "h_c_clean": h["h_c_clean"], "not_clean": h["anchors_not_C_clean"], "ratios_range": [hc[0], hc[-1]],
                       "P8-KC_E172": o["sessions"]["E172"]["P8-KC"]["verdict"]})
    n1 = sorted(load(os.path.join(SC.B8, "predictions-pool8-aifoundry1c1.json"))["sets"]["N1"])
    i1 = sorted(load(os.path.join(SC.B8, "predictions-pool8-aifoundry1c1.json"))["sets"]["I1"])
    fl = [t for t in n1 if not t.startswith("int8.")][:15] + i1[:7]
    S["D6"] = (build("E172", "d6-e172", 0.90, 0.90, 0.97, 0.97, fail=tuple(fl)), S["D1"][1])
    rc, line, o = read_pair("d6", *S["D6"])
    h, i = o["HC1-B"], o["I8P-B"]
    ok = (rc == 0 and h["verdict"] == "NOT SCORED" and "fewer than 10" in h["why"] and i["verdict"] == "NOT SCORED" and
          "fewer than 6" in i["why"] and len(fl) == 22)
    part("H2-D6", ok, {"rc": rc, "failed": len(fl), "HC1-B": [h["verdict"], h.get("why")], "I8P-B": [i["verdict"], i.get("why")]})
    S["D7"] = (build("E172", "d7-e172", 0.90, 0.90, 0.97, 0.97, passes=1), S["D1"][1])
    rc, line, o = read_pair("d7", *S["D7"])
    h, i = o["HC1-B"], o["I8P-B"]
    ok = rc == 0 and h["verdict"] == "NOT SCORED" and i["verdict"] == "NOT SCORED" and "fewer than 2" in h["why"]
    part("H2-D7", ok, {"rc": rc, "HC1-B": [h["verdict"], h.get("why")], "I8P-B": [i["verdict"], i.get("why")]})
    S["D8"] = (build("E172", "d8-e172", 0.90, 0.90, 0.97, 0.97, nan_heat=True), build("E171", "d8-e171", fail=R.I8P_ANCHORS))
    rc, line, o = read_pair("d8", *S["D8"])
    h, i = o["HC1-B"], o["I8P-B"]
    ok = rc == 0 and h["verdict"] == "NOT SCORED" and "no random anchor" in h["why"] and i["verdict"] == "NOT SCORED" and \
        "no int8 random anchor" in i["why"]
    part("H2-D8", ok, {"rc": rc, "HC1-B": [h["verdict"], h.get("why")], "I8P-B": [i["verdict"], i.get("why")]})
    # D9: the collectors' data-dir layout
    dirs = {}
    for s in S["D1"]:
        run = s["run"]
        d = os.path.join(TMP["d"], f"datadir-{run.lower()}")
        os.makedirs(os.path.join(d, "ccheck"), exist_ok=True)
        shutil.copy(s["scored"], os.path.join(d, "scored.json"))
        shutil.copy(s["reduction"], os.path.join(d, f"{run.lower()}.json"))
        shutil.copy(s["runs"], os.path.join(d, "runs.csv"))
        shutil.copy(s["ccheck"], os.path.join(d, R.CCHECK_NAMES[run][0]))
        shutil.copytree(s["raw"], os.path.join(d, R.CARD_SUB[run]))
        dirs[run] = d
    out = os.path.join(TMP["d"], "read-d9.json")
    rc, line = cli(["--e172-dir", dirs["E172"], "--e171-dir", dirs["E171"], "--json", out])
    o9, o1 = load(out), load(os.path.join(TMP["d"], "read-d1.json"))
    same = all(o9[r][k] == o1[r][k] for r in ("HC1-B", "I8P-B") for k in ("verdict", "d_rms_" + ("c" if r == "HC1-B" else "w"), "lo95", "hi95"))
    part("H2-D9", rc == 0 and same, {"rc": rc, "line": line, "same_as_D1": same})
    # D10 (change 1): a set-aside pass, a configuration-flagged pass and a failed run, as reduce_e78 records them
    s10 = build("E172", "d10-e172", 0.90, 0.90, 0.97, 0.97, passes=5, set_aside=(3,), cfg_flag=(4,), failed_runs=((1, "anchor_pi"),))
    red = load(s10["reduction"])
    rc, line, o = read_pair("d10", s10, S["D1"][1])
    same, diff = same_readings(o, S["o1"]) if o else (False, ["v2 wrote nothing"])
    rt = (o or {}).get("sessions", {}).get("E172", {}).get("table_checks", {}).get("runs_table", {})
    rcv1, linev1, ov1 = read_pair("d10-v1", s10, S["D1"][1], reader=V1_READER)
    ok = (s10["scorer_rc"] == 0 and rc == 0 and same and rcv1 == 6 and ov1 is None and red["runs"] == 5 * 84 and red["kept"] == 3 * 84 - 1
          and rt.get("passes_set_aside") == [str(s10["pass_ids"][3])] and rt.get("passes_config_flags") == [str(s10["pass_ids"][4])]
          and rt.get("failed_runs") == 1 and rt.get("failed_list") == 1)
    part("H2-D10", ok, {"scorer_rc": s10["scorer_rc"], "reduction": {"runs": red["runs"], "kept": red["kept"], "passes": red["passes"],
                                                                     "set_aside": [x["pass"] for x in red["passes_set_aside"]],
                                                                     "config_flagged": [x["pass"] for x in red["passes_config_flags"]],
                                                                     "failed": red["failed"]},
                        "v2_rc": rc, "v2_line": line, "same_as_D1": same, "differ": diff, "runs_table": rt, "v1_rc": rcv1,
                        "v1_wrote": ov1 is not None, "v1_line": linev1[:300]})
    # D11 (change 2): the C logs
    cases = {}
    a = build("E172", "d11a-e172", 0.90, 0.90, 0.97, 0.97)
    pd = sorted(os.listdir(os.path.join(a["raw"], "e172")))[1]
    os.remove(os.path.join(a["raw"], "e172", pd, "c-log.jsonl"))
    for nm, rdr in (("v2", V2_READER), ("v1", V1_READER)):
        rc, line, o = read_pair(f"d11a-{nm}", a, S["D1"][1], reader=rdr)
        cases[f"pass_clog_removed_after_scoring_{nm}"] = {"rc": rc, "wrote": o is not None, "line": line[:260]}
    bsm = build("E172", "d11b-e172", 0.90, 0.90, 0.97, 0.97)
    os.remove(os.path.join(bsm["raw"], "e172-smoke", "p17201", "c-log.jsonl"))
    for nm, rdr in (("v2", V2_READER), ("v1", V1_READER)):
        rc, line, o = read_pair(f"d11b-{nm}", bsm, S["D1"][1], reader=rdr)
        cases[f"smoke_clog_removed_after_scoring_{nm}"] = {"rc": rc, "wrote": o is not None, "line": line[:260]}
    c = build("E172", "d11c-e172", 0.90, 0.90, 0.97, 0.97, clog_missing="p17211")
    cases["scorer_with_clog_missing"] = {"rc": c["scorer_rc"], "scored_written": os.path.exists(c["scored"])}
    for nm, rdr in (("v2", V2_READER), ("v1", V1_READER)):
        rc, line, o = read_pair(f"d11c-{nm}", c, S["D1"][1], reader=rdr)
        cases[f"no_scored_clog_missing_{nm}"] = {"rc": rc, "wrote": o is not None, "line": line[:260]}
    dd = build("E172", "d11d-e172", 0.90, 0.90, 0.97, 0.97)
    os.remove(dd["scored"])
    rc, line, o = read_pair("d11d", dd, S["D1"][1])
    cases["no_scored_clogs_fine_v2"] = {"rc": rc, "wrote": o is not None, "line": line[:260]}
    ok = (cases["pass_clog_removed_after_scoring_v2"]["rc"] == 4 and not cases["pass_clog_removed_after_scoring_v2"]["wrote"]
          and cases["pass_clog_removed_after_scoring_v1"]["rc"] == 0
          and cases["smoke_clog_removed_after_scoring_v2"]["rc"] == 4 and not cases["smoke_clog_removed_after_scoring_v2"]["wrote"]
          and cases["smoke_clog_removed_after_scoring_v1"]["rc"] == 0
          and cases["scorer_with_clog_missing"]["rc"] == 4 and not cases["scorer_with_clog_missing"]["scored_written"]
          and cases["no_scored_clog_missing_v2"]["rc"] == 4 and not cases["no_scored_clog_missing_v2"]["wrote"]
          and cases["no_scored_clog_missing_v1"]["rc"] == 2
          and cases["no_scored_clogs_fine_v2"]["rc"] == 2 and not cases["no_scored_clogs_fine_v2"]["wrote"]
          and "CCSESSION-MISSING" in cases["pass_clog_removed_after_scoring_v2"]["line"])
    part("H2-D11", ok, cases)
    # D12 (change 3): a long anchor and a long N1 tile
    tile_long = sorted(n1)[0]
    s12 = build("E172", "d12-e172", 0.90, 0.90, 0.97, 0.97, trun={"fp32.randn": 5.5, tile_long: 5.5}, dT_ratio={"fp32.randn": 0.5})
    rc, line, o = read_pair("d12", s12, S["D1"][1])
    h = o["HC1-B"]
    pred = load(os.path.join(SC.B8, "predictions-pool8-aifoundry1c1.json"))
    ha = sorted(["fp32.randn", "fp16.randn", "int8.full"] + [n for n, r in pred["roles"].items() if r.get("role") == "scale"])
    design = {n: 0.90 * (1 + 0.002 * (j - 4)) for j, n in enumerate(ha)}
    design["fp32.randn"] = 0.5
    want_h = statistics.median([v for n, v in design.items() if n != "fp32.randn"])
    want_all = statistics.median(design.values())
    ok = (rc == 0 and h["anchors_long_runs_left_out"] == ["fp32.randn"] and "fp32.randn" not in h["anchor_ratios"]
          and abs(h["h"] - want_h) <= 1e-9 and abs(h["h_with_long_anchors"] - want_all) <= 1e-9 and abs(want_h - want_all) > 1e-4
          and abs(h["long_anchor_ratios"]["fp32.randn"] - 0.5) <= 1e-9 and tile_long in h["long_runs_named"] and h["n"] == 31
          and "fp32.randn" not in h["c_clean_anchors"] and len(h["anchor_ratios"]) == 8)
    part("H2-D12", ok, {"rc": rc, "long_left_out": h["anchors_long_runs_left_out"], "h1": h["h"], "h1_want": want_h,
                        "h_with_long": h.get("h_with_long_anchors"), "h_with_long_want": want_all,
                        "long_tiles_named": h["long_runs_named"], "n": h["n"], "c_clean": len(h["c_clean_anchors"]), "verdict": h["verdict"]})
    # D13 (change 4): files outside the repository: the departure recorded
    o1 = S["o1"]
    ok = (o1["departure"] and "REGISTRATION.md sections 8 and 11" in o1["departure"] and not o1["committed_files"]["E172"]["all_committed"]
          and o1["HC1-B"]["departure"] and o1["I8P-B"]["departure"] and o1["HC1-B"]["label"] == "blind")
    part("H2-D13", ok, {"departure": o1["departure"], "E172_files": {k: v.get("why") for k, v in o1["committed_files"]["E172"]["files"].items()}})
    return S


# ------------------------------------------------------------------------------------------------- H3, refusals
def h3(S):
    e2, e1 = S["D1"]
    cases = {}

    def case(tag, args, want, must=None):
        out = os.path.join(TMP["d"], f"refuse-{tag}.json")
        if os.path.exists(out):
            os.remove(out)
        rc, line = cli(args + ["--json", out] if "--json" not in args else args)
        cases[tag] = {"rc": rc, "want": want, "wrote": os.path.exists(out), "line": mask(line)[:300]}
        if must:
            cases[tag]["names"] = must in line
        return out

    case("usage", ["--json", os.path.join(TMP["d"], "u.json")], 2)
    sw = dict(e1, run="E172")
    case("E171_as_E172", args_of(sw)[:-2], 6)
    a = args_of(e2, e1)[:-2]
    sw2 = [x.replace("--e172-", "--TMP-").replace("--e171-", "--e172-").replace("--TMP-", "--e171-") if x.startswith("--") else x for x in a]
    case("pair_swapped", sw2, 6)
    o = load(e1["scored"])
    o.update(run="E172", card="aifoundry1c1", predictions="tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry1c1.json",
             predictions_sha256=load(e2["scored"])["predictions_sha256"])
    rl = os.path.join(TMP["d"], "relabelled.json")
    json.dump(o, open(rl, "w"))
    case("relabelled", args_of(dict(e1, run="E172", scored=rl))[:-2], 6)
    case("E172_twice", args_of(e2, dict(e2, run="E171"))[:-2], 6)
    o = load(e2["scored"])
    o.pop("c_sessions", None)
    nc = os.path.join(TMP["d"], "no-c-sessions.json")
    json.dump(o, open(nc, "w"))
    case("no_c_sessions", args_of(dict(e2, scored=nc))[:-2], 4)
    case("no_ccheck", args_of(dict(e2, ccheck=os.path.join(TMP["d"], "absent.json")))[:-2], 4)
    case("other_reduction", args_of(dict(e2, reduction=S["D2"][0]["reduction"]))[:-2], 6)
    rows = list(csv.DictReader(open(e2["runs"])))
    fields = list(rows[0])

    def write_rows(tag, rr):
        p = os.path.join(TMP["d"], f"{tag}.csv")
        with open(p, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(rr)
        return p

    case("runs_table_short", args_of(dict(e2, runs=write_rows("short", rows[:-1])))[:-2], 6, "(a)")
    last = e2["kept_ids"][-1]
    extra = [dict(r, **{"pass": "17219"}) for r in rows if r["pass"] == str(last)]
    case("runs_table_other_pass", args_of(dict(e2, runs=write_rows("extra", rows + extra)))[:-2], 6, "(d)")
    flagged = [dict(r) for r in rows]
    flagged[5]["fail"] = "1"
    case("runs_table_kept_run_marked_failed", args_of(dict(e2, runs=write_rows("flag", flagged)))[:-2], 6, "(c)")
    relab = [dict(r, **{"pass": "17219"}) if r["pass"] == str(last) else r for r in rows]
    case("runs_table_kept_pass_relabelled", args_of(dict(e2, runs=write_rows("relab", relab)))[:-2], 6, "(b)")
    case("other_ccheck", args_of(dict(e2, ccheck=S["D5"][0]["ccheck"]))[:-2], 6)
    ok = all(v["rc"] == v["want"] and not v["wrote"] and v.get("names", True) for v in cases.values())
    # E157's committed runs table cut to its kept runs (the form v1 expected): v2's table refuses it at (a)
    e157 = os.path.join(DD, "2026-11-03-e157-blind6-card1")
    res = load(os.path.join(e157, "e157.json"))
    rr = list(csv.DictReader(open(os.path.join(e157, "runs.csv"))))
    keep = {str(p) for p in res["passes"]}
    cut = os.path.join(TMP["d"], "e157-kept-only.csv")
    with open(cut, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rr[0]))
        w.writeheader()
        w.writerows([r for r in rr if r["pass"] in keep])
    try:
        R.session_table(os.path.join(e157, "e157.json"), cut, sorted(res["items"]))
        cases["E157_kept_only_table"] = {"rc": 0, "want": 6}
    except R.Refuse as e:
        cases["E157_kept_only_table"] = {"rc": e.code, "want": 6, "names": "(a)" in str(e), "line": mask(str(e))[:240]}
    ok = ok and cases["E157_kept_only_table"]["rc"] == 6 and cases["E157_kept_only_table"].get("names")
    # M11's list changed: the reader's check, in this process, against a copy of the directory's lists
    t = os.path.join(TMP["d"], "m11-lists")
    os.makedirs(t, exist_ok=True)
    for nm, _ in R.M11_LISTS:
        shutil.copy(os.path.join(HERE, nm), os.path.join(t, nm))
    txt = open(os.path.join(t, "SHA256SUMS-a1")).read()
    open(os.path.join(t, "SHA256SUMS-a1"), "w").write(("0" * 64) + txt[64:])
    old = R.HERE
    R.HERE = t
    try:
        R.check_m11_lists()
        lists = {"rc": 0}
    except R.Refuse as e:
        lists = {"rc": e.code, "msg": mask(str(e))[:200]}
    finally:
        R.HERE = old
    cases["m11_list_changed"] = dict(lists, want=9)
    # the C-session check's list changed (in this process): a copy of p8-600/SHA256SUMS with ccsessions_p8.py's line altered
    lp = os.path.join(TMP["d"], "p8-SHA256SUMS")
    body = open(os.path.join(TOP, R.CS_LISTS[0][0])).read().splitlines()
    body = [("0" * 64 + ln[64:]) if ln.endswith("ccsessions_p8.py") else ln for ln in body]
    open(lp, "w").write("\n".join(body) + "\n")
    old_l, old_m = R.CS_LISTS, dict(R._M)
    R.CS_LISTS = ((lp, R.CS_LISTS[0][1]), R.CS_LISTS[1])
    R._M.clear()
    try:
        R.frozen_code()
        csl = {"rc": 0}
    except R.Refuse as e:
        csl = {"rc": e.code, "msg": mask(str(e))[:200]}
    finally:
        R.CS_LISTS = old_l
        R._M.clear()
        R._M.update(old_m)
    cases["c_session_list_changed"] = dict(csl, want=9)
    ok = ok and lists["rc"] == 9 and csl["rc"] == 9
    part("H3", ok, cases)


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--txt")
    a = ap.parse_args(argv)
    real = tempfile.mkdtemp(prefix="m11-h2v2-")
    TMP["d"] = real
    try:
        FM = h0()
        h1(FM)
        S = h2()
        h3(S)
    finally:
        shutil.rmtree(real, ignore_errors=True)
    ok = all(v["pass"] for v in RESULTS.values())
    say(f"SELFTEST read_hc1b_i8pb_v2.py: {sum(v['pass'] for v in RESULTS.values())} of {len(RESULTS)} parts PASS -> {'PASS' if ok else 'FAIL'}")
    o = {"_note": "Q142(h2) fix pass selftest_read_hc1b_i8pb_v2.py: the self-test of M11's HC1-B and I8P-B reader, v2 "
                  "(README-h2-reader.md.dated-note-1.md)", "reader_sha256": R.sha(R.__file__), "reader_v1_sha256": R.sha(R1.__file__),
         "selftest_sha256": R.sha(os.path.abspath(__file__)), "parts": RESULTS, "verdict": "PASS" if ok else "FAIL"}
    if a.out:
        open(a.out, "w").write(json.dumps(o, indent=1, sort_keys=True) + "\n")
    if a.txt:
        open(a.txt, "w").write("\n".join(LINES) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
