#!/usr/bin/env python3
"""Q142(h2): the self-test of read_hc1b_i8pb.py, M11's HC1-B and I8P-B reader. Desk only: it reads committed files and writes only into
a temporary directory (removed at the end) and its --out and --txt files. No device, no ssh, no lab box.

  H0  the inputs: M11's three lists pass (58, 6, 9); the reader's M10 anchor list is fit_m10.ANCHORS; the seeds are 80,000 plus the
      character codes of 'M11-HC1-B' and 'M11-I8P-B'; the minimums are pool8-registration.json's M1 (10) and M1i (6).
  H1  E163's and E164's committed sessions as stand-ins (pool 7 on aifoundry3 and on card 1; their committed primary reductions and
      runs tables):
      (a) the reader's table (S, dT_win, run length) equals fit_m6.heat_rows' rows for both sessions, the rows M10's 4.5 s law was
          fitted on (reached through fit_m10's chain, unchanged);
      (b) h on E164 and on E163 with m10.json's coefficients and M10's anchor list equals heldout-m10.json's committed session heat
          scale (heat_c1 > session_heat_scales_all_rows) within 1e-4;
      (c) the int8 pair: each pool-7 int8 anchor's D ratio card 1 / aifoundry3 equals RK4's committed anchor_ratio
          (rank4-e163-e164.json) within 1e-9, and the three-anchor arm's median its arm_with_E78_anchors; k as section 9 forms it
          (each anchor's D over M10's Dhat at its own measured rate, paired) equals the same ratios, rate-adjusted, over the card term;
      (d) HC1-B's and I8P-B's computations on the stand-ins (pool 7's priority-1 tiles for N1 and I1): readings reported, labelled
          in-sample and post hoc (both sessions are in M10's training rows).
  H2  synthetic E171 and E172 sessions with known answers, each scored by the committed scorer (score_p8_600.py score, in this process,
      as the collectors call it), then read by the reader's command line:
      D1 h1 0.90 on anchors and tiles, k 0.97 on anchors and I1, launches after the registration: HC1-B BETTER, I8P-B BETTER, both
         blind, h1 and k to 1e-8, the control h3 = 1; the interval re-derived here from the registration's words, identical;
      D2 h1 0.90 on the anchors, tiles at 1.00; k 0.97, I1 at 1.00; launches before the registration: both WORSE, both post hoc, HC1's
         not-wanted clause met;
      D3 h1 and k exactly 1: both NOT RESOLVED (d = 0 in every draw);
      D4 h1 1.10 with tiles at 1.02; k 1.05 with I1 at 1.01: HC1-B WORSE and h1 over-corrects on N1; I8P-B WORSE and I1's bias
         over-corrects;
      D5 C FAILs: E172's int8.anchor8_full_a and E171's int8.full judged FAIL: k from the anchors left (still 0.97), both named; h1
         keeps every anchor, its C-clean arm drops the FAILed one;
      D6 small sets: 22 of E172's N1 tiles and 7 of its I1 tiles judged FAIL: HC1-B and I8P-B NOT SCORED (9 < 10, 5 < 6);
      D7 E172 kept one pass: the committed scorer's NOT SCORED session; both NOT SCORED;
      D8 no anchor: E172's heat anchors carry no dT_win, E171's three int8 anchors judged FAIL: both NOT SCORED;
      D9 the data-dir layout of the collectors (--e172-dir / --e171-dir) reads as D1 by name.
  H3  refusals, each by the reader's command line (nothing written): usage (2); E171's session given as E172's (6); the pair swapped
      (6); E171's scored file relabelled as E172's (6); E172 given twice (6); a scored file with no c_sessions (4); no check of C (4);
      another session's reduction (6); a runs table missing a run (6); another session's check of C (6); and, in this process, M11's
      list SHA256SUMS-a1 changed (9).

    /usr/bin/python3 -B tools/claims-v3/m11/selftest_read_hc1b_i8pb.py [--out <file.json>] [--txt <file.txt>]

Every line is masked (the repo and the temporary directory) before it is printed. Exit 0 when every part passes. Standard library and
numpy (through fit_m10's chain and the predictor). SPDX-License-Identifier: Apache-2.0
"""
import contextlib
import copy
import csv
import io
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
import read_hc1b_i8pb as R  # noqa: E402
SC, V2, V3 = R.SC, R.V2, R.V3
DD = os.path.join(TOP, "docs", "reports", "data")
M10D = R.M10D
E163D = os.path.join(DD, "2026-11-04-e163-blind7-aifoundry3")
E164D = os.path.join(DD, "2026-11-04-e164-blind7-card1")
B7 = os.path.join(TOP, "tools", "claims-v3", "kinds", "blind7")
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
    say(f"{name}: {'PASS' if ok else 'FAIL'}  {mask(json.dumps(detail, default=str))[:900]}")


# ------------------------------------------------------------------------------------------------- H0
def h0():
    g = R.frozen_code()
    lists = R.check_m11_lists()
    sys.path.insert(0, M10D)
    import fit_m10 as FM  # noqa: E402
    ok = (lists == {"SHA256SUMS": 58, "SHA256SUMS-m11": 6, "SHA256SUMS-a1": 9} and tuple(FM.ANCHORS) == R.M10_ANCHORS
          and R.seed_of("M11-HC1-B") == 80000 + sum(map(ord, "M11-HC1-B")) and g["min"] == {"N1": 10, "I1": 6})
    part("H0", ok, {"lists": lists, "anchors_equal_fit_m10": tuple(FM.ANCHORS) == R.M10_ANCHORS, "min": g["min"],
                    "seeds": {r: R.seed_of(r) for r in (R.RULE_HC1B, R.RULE_I8PB)}, "scorer": g["scorer"][:12], "v2": g["v2"][:12],
                    "v3": g["v3"][:12]})
    return FM


# ------------------------------------------------------------------------------------------------- H1, the stand-ins
def h1(FM):
    old = dict(FM.M6.EXPDIR)
    FM.M6.EXPDIR.clear()
    FM.M6.EXPDIR.update({"E163": os.path.basename(E163D), "E164": os.path.basename(E164D)})
    try:
        hr = FM.M6.heat_rows([])
    finally:
        FM.M6.EXPDIR.clear()
        FM.M6.EXPDIR.update(old)
    tabs, worst, n = {}, {"S": 0.0, "dT": 0.0, "T_run": 0.0}, 0
    for exp, d in (("E163", E163D), ("E164", E164D)):
        names = sorted(load(os.path.join(d, f"{exp.lower()}.json"))["items"])
        tabs[exp], _ = R.session_table(os.path.join(d, f"{exp.lower()}.json"), os.path.join(d, "runs.csv"), names)
    for r in hr:
        t = tabs[r["exp"]][r["key"]]
        for k_, kk in (("S", "S"), ("dT", "dT"), ("T_run", "T_run")):
            worst[k_] = max(worst[k_], abs(float(r[kk]) - float(t[k_])))
        n += 1
    ok_a = n > 100 and max(worst.values()) <= 1e-9
    part("H1a", ok_a, {"rows_compared": n, "max_abs_diff": worst})
    held = load(os.path.join(M10D, "heldout-m10.json"))["heat_c1"]["session_heat_scales_all_rows"]
    hs = {}
    for exp, card, key in (("E164", "aifoundry1c1", "E164|aifoundry1-c1"), ("E163", "aifoundry3", "E163|aifoundry3")):
        h, rat = R.h_scale(tabs[exp], card, R.M10_ANCHORS)
        hs[exp] = {"h": h, "committed": held[key], "anchors": sorted(rat), "diff": abs(h - held[key])}
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


# ------------------------------------------------------------------------------------------------- H2, the synthetic sessions
S_TRUE = 1.004
R_RHO = 0.98
E78_SIX = ("fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full")
BLIND_BASE, POSTHOC_BASE = 1_800_000_000_000, 1_700_000_000_000


def t_run_of(n):
    """run lengths on a 0.125 s grid (4.25-4.75 s): whole milliseconds, exact in binary, so the reader's run length is the design's"""
    return 4.5 + 0.125 * ((sum(map(ord, n)) % 5) - 2)


def build(run, label, H_TRUE=1.0, H_TILE=1.0, K_TRUE=1.0, K_TILE=1.0, base=BLIND_BASE, passes=3, fail=(), nan_heat=False,
          noise_c=0.02, noise_w=0.005, jitter=True, r_rho=R_RHO):
    """a designed session in the collectors' raw layout, its check of C, its reduction and runs table; then the committed scorer"""
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
    Tr = {n: t_run_of(n) for n in D}
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
    items, per = {}, {str(q): {} for q in pass_ids}
    jit = (lambda n, q: 1e-9 * (((sum(map(ord, n)) + q) % 5) - 2)) if jitter else (lambda n, q: 0.0)  # noqa: E731
    for n in D:
        t = typ(n)
        vals = [D[n] + jit(n, q) for q in pass_ids]
        dv = float("nan") if (nan_heat and n in heat_anchors) else dT[n]
        items[n] = {"type": t, "D": {"mean": sum(vals) / len(vals), "se": 1e-4, "n": len(vals)}, "rate": {"mean": rate[t]},
                    "dT_win": {"mean": dv}, "S": {"mean": Sv[n]}}
        for q, x in zip(pass_ids, vals):
            per[str(q)][n] = {"D": x, "dT_win": dv, "S": Sv[n], "rate": rate[t]}
    tiles = sorted(T)
    launches, csvrows, k = [], [], [0]

    def seq_of(q):
        thirds = [tiles[0:22], tiles[22:43], tiles[43:]]
        out = ["anchor_pi"]
        for th in thirds:
            out += list(E78_SIX) + th
        return out + ["anchor_pi"]

    def write_session(d, names, q=None):
        os.makedirs(d, exist_ok=True)
        prev_end = None
        with open(os.path.join(d, "runs.jsonl"), "w") as rf, open(os.path.join(d, "c-log.jsonl"), "w") as cf:
            cf.write(json.dumps({"ccheck": 1, "kind": "host", "host_sha256": "x", "kernel_sha256": "y"}) + "\n")
            for n in names:
                t0 = base + k[0] * 20000
                k[0] += 1
                t1 = t0 + int(round(Tr.get(n, 4.5) * 1000))
                rf.write(json.dumps({"item": n, "launch": 0, "t_start_ms": t0, "t_end_ms": t1}) + "\n")
                cf.write(json.dumps({"ccheck": 1, "kind": "c", "type": typ(n), "launch": 0, "iters": 1, "t_start_ms": t0, "t_end_ms": t1,
                                     "ok": True, "groups": []}) + "\n")
                launches.append({"log": f"c-log-{os.path.basename(d)}.jsonl", "t_start_ms": t0, "t_end_ms": t1,
                                 "verdict": "FAIL" if n in fail else "PASS", "type": typ(n)})
                if q is not None:
                    csvrows.append({"pass": str(q), "item": n, "t0_ms": t0, "prev_end_ms": prev_end if prev_end is not None else t0 - 1000,
                                    "D": D.get(n), "dT_win": dT.get(n), "S": Sv.get(n), "type": typ(n)})
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
        w = csv.DictWriter(fh, fieldnames=["pass", "item", "t0_ms", "prev_end_ms", "D", "dT_win", "S", "type"])
        w.writeheader()
        w.writerows(csvrows)
    red = os.path.join(b, f"{run.lower()}.json")
    json.dump({"experiment": run, "card": "aifoundry3" if card == "aifoundry3" else "aifoundry1-c1", "passes": pass_ids,
               "kept": len(csvrows), "runs": len(csvrows), "items": items, "per_pass": per}, open(red, "w"))
    js = os.path.join(b, "scored.json")
    with contextlib.redirect_stdout(io.StringIO()):
        rc = SC.main(["score", "--run", run, "--reduction", red, "--raw", raw, "--ccheck", cc, "--json", js])
    if rc != 0 or not os.path.exists(js):
        raise RuntimeError(f"the committed scorer exited {rc} on {label}")
    return {"run": run, "scored": js, "reduction": red, "runs": runs_csv, "raw": raw, "ccheck": cc, "base": b,
            "design": {"H_TRUE": H_TRUE, "H_TILE": H_TILE, "K_TRUE": K_TRUE, "K_TILE": K_TILE}}


def args_of(s2, s1=None, out=None):
    a = []
    for s in ([s2] + ([s1] if s1 else [])):
        lc = s["run"].lower()
        a += [f"--{lc}-scored", s["scored"], f"--{lc}-reduction", s["reduction"], f"--{lc}-runs", s["runs"], f"--{lc}-raw", s["raw"],
              f"--{lc}-ccheck", s["ccheck"]]
    return a + ["--json", out or os.path.join(TMP["d"], "read.json")]


def cli(args, timeout=600):
    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "read_hc1b_i8pb.py"), "read", *args], capture_output=True, text=True,
                       timeout=timeout)
    return r.returncode, (r.stdout.strip().splitlines() or [""])[-1][:400]


def read_pair(tag, s2, s1):
    out = os.path.join(TMP["d"], f"read-{tag}.json")
    if os.path.exists(out):
        os.remove(out)
    rc, line = cli(args_of(s2, s1, out))
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
                                                                                                                     "NOT RESOLVED"))
    part("H2-D1", ok, {"rc": rc, "line": line, "HC1-B": [h["verdict"], h["h"], h["d_rms_c"], h["lo95"], h["hi95"], h["n"], h["label"]],
                       "I8P-B": [i["verdict"], i["k"], i["d_rms_w"], i["lo95"], i["hi95"], i["n"], i["label"]],
                       "independent_interval_identical": [(d0, lo, hi) == (h["d_rms_c"], h["lo95"], h["hi95"]),
                                                          (e0, lo2, hi2) == (i["d_rms_w"], i["lo95"], i["hi95"])],
                       "h3": h["control_h3_E171"]["h3"], "at_M10_primary_D": h["at_M10_primary_D"]["reading"],
                       "check_anchors": sorted(h["check_anchors"]), "int8_check": i.get("check_anchor")})
    S["D2"] = (build("E172", "d2-e172", 0.90, 1.00, 0.97, 1.00, base=POSTHOC_BASE), build("E171", "d2-e171", base=POSTHOC_BASE))
    rc, line, o = read_pair("d2", *S["D2"])
    h, i = o["HC1-B"], o["I8P-B"]
    ok = (rc == 0 and h["verdict"] == "WORSE" and i["verdict"] == "WORSE" and h["label"] == "post hoc" and i["label"] == "post hoc"
          and h["not_wanted"]["met"] and h["not_wanted"]["HC1-B reads WORSE"] and i["not_wanted"]["I8P-B reads WORSE"])
    part("H2-D2", ok, {"rc": rc, "HC1-B": [h["verdict"], h["label"], h["not_wanted"]], "I8P-B": [i["verdict"], i["label"]],
                       "why": h["precedence"]["why"]})
    # exact in floating point: two passes (a mean of two equal values is the value), whole-millisecond run lengths, no jitter, r_rho 1
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
          and abs(h["h_c_clean"] - statistics_median([v for n, v in h["anchor_ratios"].items() if n != "int8.anchor8_full_a_4aac84"])) <= 1e-12
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
    return S


def statistics_median(v):
    import statistics
    return statistics.median(v)


# ------------------------------------------------------------------------------------------------- H3, refusals
def h3(S):
    e2, e1 = S["D1"]
    cases = {}

    def case(tag, args, want):
        out = os.path.join(TMP["d"], f"refuse-{tag}.json")
        if os.path.exists(out):
            os.remove(out)
        rc, line = cli(args + ["--json", out] if "--json" not in args else args)
        cases[tag] = {"rc": rc, "want": want, "wrote": os.path.exists(out), "line": mask(line)[:240]}
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
    short = os.path.join(TMP["d"], "short-runs.csv")
    with open(short, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows[:-1])
    case("runs_table_short", args_of(dict(e2, runs=short))[:-2], 6)
    case("other_ccheck", args_of(dict(e2, ccheck=S["D5"][0]["ccheck"]))[:-2], 6)
    ok = all(v["rc"] == v["want"] and not v["wrote"] for v in cases.values())
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
    ok = ok and lists["rc"] == 9
    part("H3", ok, cases)


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--txt")
    a = ap.parse_args(argv)
    real = tempfile.mkdtemp(prefix="m11-h2-")
    TMP["d"] = real
    try:
        FM = h0()
        h1(FM)
        S = h2()
        h3(S)
    finally:
        shutil.rmtree(real, ignore_errors=True)
    ok = all(v["pass"] for v in RESULTS.values())
    say(f"SELFTEST read_hc1b_i8pb.py: {sum(v['pass'] for v in RESULTS.values())} of {len(RESULTS)} parts PASS -> {'PASS' if ok else 'FAIL'}")
    o = {"_note": "Q142(h2) selftest_read_hc1b_i8pb.py: the self-test of M11's HC1-B and I8P-B reader", "reader_sha256": R.sha(R.__file__),
         "selftest_sha256": R.sha(os.path.abspath(__file__)), "parts": RESULTS, "verdict": "PASS" if ok else "FAIL"}
    if a.out:
        open(a.out, "w").write(json.dumps(o, indent=1, sort_keys=True) + "\n")
    if a.txt:
        open(a.txt, "w").write("\n".join(LINES) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
