#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q145(b): "M10 on the law", the exact one-footing test, as tools/claims-v3/m10-s/REGISTRATION.md section 6 (dfc005bf) registers it.

    python3 -B law_m10.py all --scratch <dir> --out <dir>

Stages, in order (each stops on a failed check):
 1. route: every M10 training session re-reduced at Q139(u)'s frozen slope through its registered route (reduce_footing.reduce for the
    26 experiments of Q139(u); the pool sessions' own wrappers with --drop-dips --leak k --no-refit), each output checked equal to the
    committed reduction (largest |D new - D committed| 0); its runs.csv gives T_mid (footing_law.py k_session).
 2. law: the same at FL3's k_s = k_c(T_mid) of each session (FL1's law of its card); E147's steps by M8's form with k_s.
 3. refit: fit_m10's Fit10 unchanged. First on the committed rows (it must reproduce m10.json's and m9.json's prices), then on the
    law rows: M10's frozen variant (floats B+a+b with term b's N-point features, int8 B) on the 959 rows; M9's forms on its 855.
 4. score (post hoc): E171's and E172's N1, F1 and I1 at FL7's committed law reductions (k_s 0.36007 / 0.49300); each model's
    prediction at the measured rate, M10's float scale read on the law-reduced pool-8 anchors by M10's rule; P8-M1, M1f, M1i and A1 by
    score_p8_600.paired with the pool-8 registration's draws and seeds. First the same code on the registered footing must reproduce
    the committed scored.json verdicts and figures.
Standard library and numpy 1.26. Writes only under --scratch and --out.
SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import statistics  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DD = os.path.join(TOP, "docs", "reports", "data")
CV = os.path.join(TOP, "tools", "claims-v3")
M10D = os.path.join(DD, "2026-11-04-q142m-m10")
M9D = os.path.join(DD, "2026-11-04-q140m-m9")
FOOT = os.path.join(DD, "2026-11-03-q139u-footing")
FLD = os.path.join(CV, "footing-law")
FL7 = os.path.join(DD, "2026-11-05-q145a-footing-law", "fl7")
B8 = os.path.join(CV, "kinds", "blind8")
P8 = os.path.join(CV, "p8-600")
for _p in (M10D, FOOT, FLD, P8):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import fit_m10 as FM  # noqa: E402
import reduce_footing as RF  # noqa: E402
import footing_law as FLAW  # noqa: E402

load = lambda p: json.load(open(p))  # noqa: E731
fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
REL = lambda p: os.path.relpath(p, TOP) if p.startswith(TOP) else os.path.basename(p)  # noqa: E731
LAW_CARD = {"a3": "aifoundry3", "c1": "aifoundry1c1"}
POOL = {"E153": ("2026-11-03-e153-blind6-aifoundry3", "a3", "e153"), "E157": ("2026-11-03-e157-blind6-card1", "c1", "e157"),
        "E163": ("2026-11-04-e163-blind7-aifoundry3", "a3", "e163"), "E164": ("2026-11-04-e164-blind7-card1", "c1", "e164")}
E147D = os.path.join(DD, "2026-11-02-e147-bit-prices-rest")
HEAT_A3 = 0.1186   # M8's E147_FOOTING_FACTOR's heat coefficient (fit_m8.py line 53), as M10's rows carry it
LOG = []


def log(s):
    print(s, flush=True)
    LOG.append(s)


def stop(msg):
    raise SystemExit("M10 ON THE LAW STOPPED: " + msg)


def rms(v):
    v = [x for x in v if x is not None]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else float("nan")


# ------------------------------------------------------------------ stages 1 and 2: reductions
def reduce_pool(exp, k, out_dir, scratch, tag):
    ddir, card, w = POOL[exp]
    prim = load(os.path.join(DD, ddir, f"{w}.json"))
    want = [os.path.basename(x.rstrip("/")) for x in prim["dirs"]]
    found = {}
    for dp, dn, fn in os.walk(os.path.join(DD, ddir)):
        if any(f.startswith("telemetry.jsonl") for f in fn) and os.path.basename(dp) in want:
            found.setdefault(os.path.basename(dp), dp)
    miss = [x for x in want if x not in found]
    if miss:
        stop(f"{exp}: pass dirs not committed: {miss}")
    dirs = [found[x] for x in want]
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{exp.lower()}-{tag}.json")
    csvp = os.path.join(scratch, "csv", f"runs-{exp.lower()}-{tag}.csv")
    txt = os.path.join(scratch, "txt", f"reduce-{exp.lower()}-{tag}.txt")
    os.makedirs(os.path.dirname(csvp), exist_ok=True)
    os.makedirs(os.path.dirname(txt), exist_ok=True)
    dips = ["--drop-dips"] if exp in ("E153", "E163") else []      # E157's and E164's wrappers remove A2's dips by default
    cmd = [sys.executable, os.path.join(CV, w, f"reduce_{w}.py"), *dirs, "--out", out, "--csv", csvp, "--txt", txt, *dips,
           "--leak", repr(float(k)), "--no-refit"]
    r = subprocess.run(cmd, cwd=TOP, capture_output=True, text=True)
    lg = os.path.join(scratch, "txt", f"reduce-{exp.lower()}-{tag}.log")
    open(lg, "w").write(" ".join(REL(c) for c in cmd) + "\n" + r.stdout[-3000:] + "\n" + r.stderr[-3000:])
    return {"exp": exp, "card": card, "k": k, "rc": r.returncode, "out": out, "csv": csvp, "log": lg}


def committed_items(exp):
    if exp in POOL:
        ddir, _, w = POOL[exp]
        return load(os.path.join(DD, ddir, f"{w}.json"))["items"]
    return load(os.path.join(FOOT, "reduced", f"{exp.lower()}-footing.json"))["items"]


def dmax(a, b):
    worst, n = 0.0, 0
    for nm, it in a.items():
        x = (it.get("D") or {}).get("mean") if isinstance(it.get("D"), dict) else None
        y = ((b.get(nm) or {}).get("D") or {}).get("mean") if isinstance((b.get(nm) or {}).get("D"), dict) else None
        if x is None and y is None:
            continue
        if (x is None) != (y is None):
            return float("inf"), n
        worst = max(worst, abs(x - y))
        n += 1
    return worst, n


def stage_reduce(scratch):
    sessions = list(RF.EXPS) + list(POOL)
    out = {}
    for exp in sessions:
        card = RF.EXPS[exp][1] if exp in RF.EXPS else POOL[exp][1]
        kf = RF.K_FROZEN[card]
        if exp in RF.EXPS:
            r0 = RF.reduce(exp, kf, os.path.join(scratch, "reg"), scratch, "reg")
        else:
            r0 = reduce_pool(exp, kf, os.path.join(scratch, "reg"), scratch, "reg")
        if r0["rc"] != 0:
            stop(f"{exp} at the frozen slope: rc {r0['rc']} ({open(r0['log']).read()[-600:]})")
        worst, n = dmax(committed_items(exp), load(r0["out"])["items"])
        if worst != 0.0:
            stop(f"{exp}: the route does not reproduce the committed reduction (largest |dD| {worst})")
        kk = FLAW.k_session(os.path.join(FLD, "footing-law.json"), LAW_CARD[card], r0["csv"])
        if exp in RF.EXPS:
            r1 = RF.reduce(exp, kk["k_w_per_c"], os.path.join(scratch, "law"), scratch, "law")
        else:
            r1 = reduce_pool(exp, kk["k_w_per_c"], os.path.join(scratch, "law"), scratch, "law")
        if r1["rc"] != 0:
            stop(f"{exp} at the law: rc {r1['rc']}")
        kk2 = FLAW.k_session(os.path.join(FLD, "footing-law.json"), LAW_CARD[card], r1["csv"])
        law = load(r1["out"])
        items = law["items"]
        out[exp] = {"card": card, "k_frozen": kf, "T_mid": kk["T_mid"], "runs_for_T_mid": kk["runs"], "k_s": kk["k_w_per_c"],
                    "T_mid_from_law_csv": kk2["T_mid"], "route_check": {"items_compared": n, "largest_abs_dD_w": worst},
                    "law_reduction": r1["out"], "law_sha256": fsha(r1["out"]), "kept_passes_reg": load(r0["out"]).get("passes"),
                    "kept_passes_law": law.get("passes"), "n_items_with_D_law": sum(1 for v in items.values()
                                                                                   if isinstance(v.get("D"), dict) and v["D"].get("mean") is not None)}
        log(f"  {exp} {card}: route 0 over {n} items; T_mid {kk['T_mid']:.3f} C, k_s {kk['k_w_per_c']:.5f} (frozen {kf:.4f}); "
            f"passes {out[exp]['kept_passes_reg']} -> {out[exp]['kept_passes_law']}")
    # E147: M8's form with its own k_s
    kk = FLAW.k_session(os.path.join(FLD, "footing-law.json"), "aifoundry3", os.path.join(E147D, "runs-dips4.csv"))
    out["E147"] = {"card": "a3", "k_frozen": RF.K_FROZEN["a3"], "T_mid": kk["T_mid"], "runs_for_T_mid": kk["runs"], "k_s": kk["k_w_per_c"],
                   "factor_reg": 1.0 - RF.K_FROZEN["a3"] * HEAT_A3, "factor_law": 1.0 - kk["k_w_per_c"] * HEAT_A3,
                   "route": "M8's step form (fit_m8.py E147_FOOTING_FACTOR) with k_s in place of the frozen slope"}
    log(f"  E147: T_mid {kk['T_mid']:.3f} C, k_s {kk['k_w_per_c']:.5f}; factor {out['E147']['factor_reg']:.5f} -> {out['E147']['factor_law']:.5f}")
    return out


# ------------------------------------------------------------------ stage 3: the refits
def law_rows(rows, K):
    cache = {}
    out, dropped = [], []
    for r in rows:
        r2 = dict(r)
        if r["exp"] == "E147":
            r2["D_reg"] = r["D"]
            r2["D"] = float(r["step_W_dips4w"]) * K["E147"]["factor_law"]
        else:
            if r["exp"] not in cache:
                cache[r["exp"]] = load(K[r["exp"]]["law_reduction"])["items"]
            it = cache[r["exp"]].get(r["key"])
            d = (it or {}).get("D")
            if not isinstance(d, dict) or d.get("mean") is None:
                dropped.append(f"{r['exp']}:{r['key']}")
                continue
            r2["D_reg"] = r["D"]
            r2["D"] = float(d["mean"])
        out.append(r2)
    return out, dropped


def fit_family(rows, fam, terms, anchors, use_scale, over):
    fr = [r for r in rows if FM.fam_of(r["type"]) == fam]
    anc = {s: [x for x in v if FM.fam_of(x["type"]) == fam] for s, v in anchors.items()}
    ov = {}
    if over:
        for i, r in enumerate(fr):
            if r["S_class"] and r["key"] in over:
                ov[i] = over[r["key"]]
    ft = FM.Fit10(fr, terms, anc, use_scale, ov)
    f = ft.fit(None)
    return {"terms": terms, "coef_J": [float(v) for v in f["b"] / ft.sc], "pass1_coef_J": [float(v) for v in f["b0"] / ft.sc],
            "card1_scale": float(f["c"]), "session_scales_training": {s: float(v) for s, v in zip(ft.sessions, f["s"])},
            "n_rows": len(fr)}


def refit(rows, anchors, rc):
    m9 = load(os.path.join(M9D, "m9.json"))["families"]
    over = {k: v["fN"] for k, v in rc.items() if v.get("fN") is not None}
    m10 = {"float": fit_family(rows, "float", m9["float"]["terms"], anchors, True, over),
           "int8": fit_family(rows, "int8", m9["int8"]["terms"], anchors, False, None)}
    r9 = [r for r in rows if r.get("src") == "rows-m9.json"]
    m9r = {"float": fit_family(r9, "float", m9["float"]["terms"], {}, False, None),
           "int8": fit_family(r9, "int8", m9["int8"]["terms"], {}, False, None)}
    return m10, m9r


def rel_diff(a, b):
    return max(abs(x - y) / max(abs(y), 1e-300) for x, y in zip(a, b))


# ------------------------------------------------------------------ stage 4: pool 8 at 600 MHz
def predict_session(pred, red_items, card, fam_m10, fam_m9):
    """every tile's M10 primary and M9 prediction at its measured rate; M10's float scale on the session's pool-8 scale anchors"""
    c10 = {f: (fam_m10[f]["card1_scale"] if card == "c1" else 1.0) for f in ("float", "int8")}
    c9 = {f: (fam_m9[f]["card1_scale"] if card == "c1" else 1.0) for f in ("float", "int8")}

    def dot(f, fam, key):
        return sum(float(f[q]) * c for q, c in zip(fam["terms"], fam[key]))
    rat = []
    m10a = load(os.path.join(M10D, "m10.json"))["families"]["float"]["session_scale"]["anchors"]
    names = list(dict.fromkeys(list(m10a) + list(pred["sets"]["scale_anchors_pool8"])))   # predict_pool8.scale's list, in its order
    for a in names:
        it = red_items.get(a)
        if it is None or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
            continue
        if a in pred["m10_anchors"]:
            typ, f = a.split(".")[0], pred["m10_anchors"][a]["features"]
        else:
            typ, f = pred["tiles"][a]["type"], pred["tiles"][a]["features"]
        if FM.fam_of(typ) != "float":
            continue
        rate = float(it["rate"]["mean"]) if isinstance(it.get("rate"), dict) and it["rate"].get("mean") else FM.F.RATE[typ]
        dh = c10["float"] * rate * dot(f, fam_m10["float"], "pass1_coef_J")
        if dh > 0:
            rat.append(it["D"]["mean"] / dh)
    s = statistics.median(rat) if rat else 1.0
    out = {}
    for name, t in pred["tiles"].items():
        it = red_items.get(name)
        if it is None or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
            continue
        fam = FM.fam_of(t["type"])
        rate = it["rate"]["mean"]
        p10 = (s if fam == "float" else 1.0) * c10[fam] * rate * dot(t["features"], fam_m10[fam], "coef_J")
        p10a = c10[fam] * rate * dot(t["features"], fam_m10[fam], "coef_J")
        p9 = c9[fam] * rate * dot(t.get("features_3pt") or t["features"], fam_m9[fam], "coef_J")
        out[name] = {"D": it["D"]["mean"], "M10": p10, "M10_a_priori": p10a, "M9": p9, "rate": rate, "type": t["type"],
                     "case": t.get("case"), "s": (s if fam == "float" else 1.0), "c": c10[fam]}
    return out, s, len(rat)


def score_session(run, red_path, fam_m10, fam_m9, label):
    import score_p8_600 as SP  # noqa: E402
    d = {"E171": ("2026-11-05-e171-blind8-aifoundry3", "a3", "aifoundry3"), "E172": ("2026-11-05-e172-blind8-card1", "c1", "aifoundry1c1")}[run]
    pred = load(os.path.join(B8, f"predictions-pool8-{d[2]}.json"))
    sc = load(os.path.join(DD, d[0], "scored.json"))["primary"]
    rows, s, nanc = predict_session(pred, load(red_path)["items"], d[1], fam_m10, fam_m9)
    e10 = {t: v["D"] - v["M10"] for t, v in rows.items()}
    e9 = {t: v["D"] - v["M9"] for t, v in rows.items()}
    e0 = {t: v["D"] - v["M10_a_priori"] for t, v in rows.items()}
    res = {"label": label, "reduction": REL(red_path), "reduction_sha256": fsha(red_path), "s_float": s, "scale_anchors": nanc}
    for rule, pair, other in (("P8-M1", (e10, e9), "M9"), ("P8-M1f", (e10, e9), "M9"), ("P8-M1i", (e10, e9), "M9"), ("P8-A1", (e10, e0), "a priori")):
        tiles = [t for t in sc["rules"][rule].get("tiles", []) if t in e10]
        missing = [t for t in sc["rules"][rule].get("tiles", []) if t not in e10]
        r = SP.paired_rule(rule, pair[0], pair[1], tiles, 1)
        r.update(rms_M10=rms([pair[0][t] for t in tiles]), rms_other=rms([pair[1][t] for t in tiles]), other=other, missing_at_this_footing=missing)
        res[rule] = r
    res["tiles"] = rows
    return res


def stage_score(m10_law, m9_law):
    m10 = load(os.path.join(M10D, "m10.json"))["families"]
    m9 = load(os.path.join(M9D, "m9.json"))["families"]
    m9f = {f: {"terms": m9[f]["terms"], "coef_J": m9[f]["coef_J"], "card1_scale": list(m9[f]["card1_scale_by_format"].values())[0]}
           for f in m9}
    out = {}
    for run in ("E171", "E172"):
        d = {"E171": "2026-11-05-e171-blind8-aifoundry3", "E172": "2026-11-05-e172-blind8-card1"}[run]
        reg = score_session(run, os.path.join(DD, d, f"{run.lower()}.json"), m10, m9f, "registered footing, frozen M10 and M9 (reproduction)")
        sc = load(os.path.join(DD, d, "scored.json"))["primary"]
        chk = {}
        for rule in ("P8-M1", "P8-M1f", "P8-M1i", "P8-A1"):
            a, b = sc["rules"][rule], reg[rule]
            chk[rule] = {"committed": [a.get("verdict"), a.get("d_rms")], "here": [b.get("verdict"), b.get("d_rms")],
                         "pass": a.get("verdict") == b.get("verdict") and abs((a.get("d_rms") or 0) - (b.get("d_rms") or 0)) <= 1e-9}
        worst = max(abs(sc["rows"][t]["M10_primary_w"] - v["M10"]) for t, v in reg["tiles"].items() if t in sc["rows"] and "M10_primary_w" in sc["rows"][t])
        worst9 = max(abs(sc["rows"][t]["M9_w"] - v["M9"]) for t, v in reg["tiles"].items() if t in sc["rows"] and "M9_w" in sc["rows"][t])
        chk["tile_predictions_max_abs_w"] = {"M10": worst, "M9": worst9}
        chk["s_float"] = {"committed": sc["scale"]["s_float"], "here": reg["s_float"]}
        ok = all(v["pass"] for k, v in chk.items() if k.startswith("P8-")) and worst <= 1e-9 and worst9 <= 1e-9 \
            and abs(sc["scale"]["s_float"] - reg["s_float"]) <= 1e-12
        if not ok:
            stop(f"{run}: the scoring code does not reproduce the committed scored.json on the registered footing: {json.dumps(chk)[:800]}")
        law = score_session(run, os.path.join(FL7, f"{run.lower()}-law.json"), m10_law, m9_law,
                            "the law (FL3 k_s), M10 and M9 refitted on law rows (post hoc)")
        mixed = score_session(run, os.path.join(FL7, f"{run.lower()}-law.json"), m10, m9f,
                              "the law's test reduction with the frozen models (FL7's mixed arm, for comparison)")
        out[run] = {"reproduction_check": chk, "registered": {k: v for k, v in reg.items() if k != "tiles"},
                    "law": {k: v for k, v in law.items() if k != "tiles"}, "law_tiles": law["tiles"],
                    "mixed": {k: v for k, v in mixed.items() if k != "tiles"}}
        for lab in ("registered", "law", "mixed"):
            r = out[run][lab]["P8-M1"]
            log(f"  {run} {lab}: P8-M1 {r['verdict']} d {r['d_rms']:+.4f} [{r['lo95']:+.4f}, {r['hi95']:+.4f}] (M10 {r['rms_M10']:.4f}, M9 {r['rms_other']:.4f}); "
                f"s {out[run][lab]['s_float']:.5f}")
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["all"])
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    scratch, outd = os.path.abspath(a.scratch), os.path.abspath(a.out)
    os.makedirs(scratch, exist_ok=True)
    os.makedirs(outd, exist_ok=True)
    log("stage 1-2: reductions at the frozen slope (route check) and at the law")
    K = stage_reduce(scratch)
    json.dump({k: {kk: (REL(vv) if kk == "law_reduction" else vv) for kk, vv in v.items()} for k, v in K.items()},
              open(os.path.join(outd, "law-k.json"), "w"), indent=1)
    log("stage 3: the refits")
    rows, missing = FM.assemble()
    if len(rows) != 959:
        stop(f"{len(rows)} rows")
    zeros, zr = FM.M7.zeros_counts(), FM.M9.zeros_rows()
    anchors_reg, _ = FM.assemble_anchors(rows, zeros, zr)
    rc = FM.recount(os.path.join(M10D, "bench"), zeros, zr)
    m10_reg, m9_reg = refit(rows, anchors_reg, rc)
    m10j = load(os.path.join(M10D, "m10.json"))["families"]
    m9j = load(os.path.join(M9D, "m9.json"))["families"]
    chk = {"M10 float": rel_diff(m10_reg["float"]["coef_J"], m10j["float"]["coef_J"]),
           "M10 float pass 1": rel_diff(m10_reg["float"]["pass1_coef_J"], m10j["float"]["pass1_coef_J"]),
           "M10 int8": rel_diff(m10_reg["int8"]["coef_J"], m10j["int8"]["coef_J"]),
           "M9 float": rel_diff(m9_reg["float"]["coef_J"], m9j["float"]["coef_J"]),
           "M9 int8": rel_diff(m9_reg["int8"]["coef_J"], m9j["int8"]["coef_J"]),
           "M10 card term": abs(m10_reg["float"]["card1_scale"] - m10j["float"]["card1_scale"])}
    log(f"  refit on the committed rows against the frozen files (largest relative price difference): {chk}")
    if max(chk.values()) > 1e-9:
        stop(f"the refit machinery does not reproduce the frozen prices: {chk}")
    lrows, dropped = law_rows(rows, K)
    log(f"  law rows: {len(lrows)} ({len(dropped)} dropped: {dropped})")
    orig = FM.footing_items
    lawitems = {e: load(v["law_reduction"])["items"] for e, v in K.items() if "law_reduction" in v}
    FM.footing_items = lambda exp: lawitems.get(exp)
    try:
        anchors_law, _ = FM.assemble_anchors(lrows, zeros, zr)
    finally:
        FM.footing_items = orig
    m10_law, m9_law = refit(lrows, anchors_law, rc)
    shifts = {f: {q: (b / a - 1.0 if a else None) for q, a, b in zip(m10_reg[f]["terms"], m10_reg[f]["coef_J"], m10_law[f]["coef_J"])}
              for f in ("float", "int8")}
    log(f"  M10 on the law: card term {m10_law['float']['card1_scale']:.5f} (registered {m10_reg['float']['card1_scale']:.5f}); "
        f"float price shifts {json.dumps({q: round(v, 4) for q, v in shifts['float'].items()})}")
    json.dump({"what": "M10 and M9 refitted on M10's rows re-reduced by FL3 at each session's own T_mid (post hoc; REGISTRATION.md section 6)",
               "families": m10_law, "M9_on_the_law": m9_law, "price_shift_vs_registered": shifts, "refit_check_on_committed_rows": chk,
               "rows_dropped_at_the_law": dropped}, open(os.path.join(outd, "m10-law.json"), "w"), indent=1)
    json.dump([{"exp": r["exp"], "key": r["key"], "kind": r["kind"], "type": r["type"], "card": r["card"], "D_reg_w": r["D_reg"], "D_law_w": r["D"]}
               for r in lrows], open(os.path.join(outd, "rows-m10-law.json"), "w"))
    log("stage 4: pool 8 at 600 MHz (post hoc)")
    sc = stage_score(m10_law, m9_law)
    json.dump(sc, open(os.path.join(outd, "p8-law.json"), "w"), indent=1, default=str)
    open(os.path.join(outd, "law-m10-output.txt"), "w").write("\n".join(LOG) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
