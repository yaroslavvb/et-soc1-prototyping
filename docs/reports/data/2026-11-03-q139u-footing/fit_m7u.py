#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Q139(u), post hoc (FOOTING-RULE.md's analysis, fixed at d4c36bfe before any row was re-read):

  1. rows-m7u.json: M7's 637 rows (rows-m7.json: the same keys, tiles, features and rates) with D, D_se and dT_win from the
     footing's reduction (reduced/<exp>-footing.json); rows with no D at the footing are named.
  2. M7u: M7's frozen forms (floats G8_gtr_glive, int8 J8_b138) and frozen card term (C0) refitted on rows-m7u.json, with
     leave-one-kind-out errors of M7's, M6's and M5's forms on the same folds, on the old rows and on the new.
     M7's whole nested procedure (form and card term re-chosen inside every fold, fit_m7.run_family) is run on the new rows too.
  3. M7u's predictions for blind pool 5 on aifoundry3 and card 1 (each tile's committed features, M7's frozen band
     half-widths around them) and for pool 4 (M7u refitted without E140's rows).
  4. The registered scorers (tools/claims-v3/e141/score_e141.py, tools/claims-v3/e142/score_e142.py) run unchanged on the
     committed and the re-reduced measurements, with the frozen predictions and with M7u's in a copy of the registration.

    python3 fit_m7u.py <scratch dir>        (writes rows-m7u.json, m7u.json, scores-m7u.json, score/ here; ~3 min)
"""
import copy
import json
import math
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
M7D = os.path.join(DD, "2026-11-02-q138m-model")
sys.path.insert(0, M7D)
import fit_m7 as M7  # noqa: E402  (imports fit_m6, m6_rows and fit_m5, unchanged)

F = M7.F
RED = os.path.join(HERE, "reduced")
CV = os.path.join(ROOT, "tools", "claims-v3")
B5 = os.path.join(CV, "kinds", "blind5")
FAMS = {"float": ("fp32", "fp16"), "int8": ("int8",)}
load = lambda p: json.load(open(p))
rms = lambda v: float(np.sqrt(np.mean(np.square(v)))) if len(v) else None


def rows_u():
    rows = load(os.path.join(M7D, "rows-m7.json"))
    cache, out, lost = {}, [], []
    for r in rows:
        if r["exp"] not in cache:
            cache[r["exp"]] = load(os.path.join(RED, f"{r['exp'].lower()}-footing.json"))["items"]
        it = cache[r["exp"]].get(r["key"])
        if it is None or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
            lost.append(f"{r['exp']}:{r['key']}")
            continue
        q = dict(r)
        q["D_m7"], q["D"], q["D_se"] = r["D"], float(it["D"]["mean"]), it["D"].get("se")
        q["dT_win_m7"], q["dT_win"] = r.get("dT_win"), (it.get("dT_win") or {}).get("mean")
        out.append(q)
    return out, lost


def forms_of(famname, m7):
    return {"M7": m7["families"][famname]["terms"], "M6": M7.FORMS[famname][M7.M6_FORM[famname]],
            "M5": M7.FORMS[famname][M7.BASE_FORM[famname]]}


def loko_scores(rows, famname, m7):
    fam = M7.Fam(rows, forms_of(famname, m7), m7["families"][famname]["card_term"])
    errs = {lab: fam.loko(lab) for lab in fam.forms}
    exps = np.array([r["exp"] for r in rows])
    sc = {lab: M7.split(fam, e) for lab, e in errs.items()}
    for lab, e in errs.items():
        sc[lab]["by_exp"] = {x: rms(e[(exps == x) & ~np.isnan(e)]) for x in sorted(set(exps))}
        sc[lab]["bias_meas_minus_pred_by_card_w"] = {c: float(np.nanmean(e[np.array([r["card"] == c for r in rows])]))
                                                      for c in ("a3", "c1")}
    return fam, errs, sc


def fit_model(rows, famname, m7):
    fam = M7.Fam(rows, {"M7": m7["families"][famname]["terms"]}, m7["families"][famname]["card_term"])
    b, s = fam.fit_all("M7", [])
    C = fam.jackknife_cov("M7")
    return {"terms": m7["families"][famname]["terms"], "coef_J": [float(x) for x in fam.coef_J("M7", b)],
            "coef_fJ": dict(zip(m7["families"][famname]["terms"], [float(x) * 1e15 for x in fam.coef_J("M7", b)])),
            "coef_jackknife_se_fJ": dict(zip(m7["families"][famname]["terms"], [float(x) * 1e15 for x in np.sqrt(np.diag(C))])),
            "card1_scale_by_format": dict(zip(fam.fmts, [float(x) for x in s])), "n_rows": len(rows), "n_kinds": fam.K}


def predict(mod, t, f, card):
    x = np.array([F.RATE[t] * f[q] for q in mod["terms"]])
    d = float(x @ np.array(mod["coef_J"]))
    return d * (mod["card1_scale_by_format"][t] if card == "c1" else 1.0)


def run_scorer(script, flag, meas, reg, out, runs=None, e141=None):
    cmd = [sys.executable, os.path.join(CV, script), flag, meas, "--reg", reg, "--json", out]
    if runs:
        cmd += ["--runs", runs]
    if e141:
        cmd += ["--e141", e141]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return {"rc": r.returncode, "err": r.stderr[-600:]}


def digest(path, exp):
    s = load(path)
    s = s.get("primary", s)
    R = s.get("rules", {})
    g = lambda k, *f: None if k not in R else {x: R[k].get(x) for x in f}
    pfx = exp
    o = {"leak": (s.get("leak") or {}).get("k_w_per_c"), "passes": s.get("passes"),
         "P": {k: g(f"{pfx}-{k}", "verdict", "rms", "rms_w", "value", "lo95", "hi95") for k in ("P1", "P2", "P3")},
         "B1": g(f"{pfx}-B1", "verdict", "bias_meas_minus_pred_w", "interval"),
         "B2": g(f"{pfx}-B2", "verdict", "bias_meas_minus_pred_w", "interval"),
         "C1": g(f"{pfx}-C1", "verdict", "inside", "n"),
         "M1": g(f"{pfx}-M1", "verdict", "d_rms_w", "lo95", "hi95"), "M2": g(f"{pfx}-M2", "verdict", "d_rms_w", "lo95", "hi95"),
         "X1": g(f"{pfx}-X1", "verdict", "median_ratio", "lo95", "hi95", "card_term", "n"),
         "X2": g(f"{pfx}-X2", "verdict", "median_ratio", "lo95", "hi95", "card_term", "n"),
         "reported": {m: {"power": (s.get("reported") or {}).get(m, {}).get("power"),
                          "all": (s.get("reported") or {}).get(m, {}).get("power_all_nonanchor"),
                          "coverage": {k: (s.get("reported") or {}).get(m, {}).get("coverage_power", {}).get(k)
                                       for k in ("verdict", "inside", "n")}} for m in ("M7", "M6", "M5")}}
    return o


def main():
    scratch = os.path.abspath(sys.argv[1])
    m7, m6, m5 = load(os.path.join(M7D, "m7.json")), load(os.path.join(M7.M6D, "m6.json")), load(os.path.join(M7.M5D, "m5.json"))
    rows, lost = rows_u()
    old = load(os.path.join(M7D, "rows-m7.json"))
    json.dump(rows, open(os.path.join(HERE, "rows-m7u.json"), "w"), indent=0)
    res = {"n_rows": len(rows), "rows_lost": lost, "families": {}}
    shift = {}
    for r in rows:
        shift.setdefault(f"{r['card']}|{r['type']}", []).append(r["D"] - r["D_m7"])
    res["D_shift_footing_minus_m7_w"] = {k: {"mean": float(np.mean(v)), "min": float(np.min(v)), "max": float(np.max(v)), "n": len(v)}
                                         for k, v in sorted(shift.items())}
    model = {"_what": "M7u (post hoc): M7's frozen forms and card term refitted on rows-m7u.json (Q139(u)'s footing)",
             "families": {}, "k_w_per_c": {}}
    fp = load(os.path.join(HERE, "footing.json"))
    model["k_w_per_c"] = {c: v["k_w_per_c"] for c, v in fp["slopes"].items()}
    for famname, tys in FAMS.items():
        rn = [r for r in rows if r["type"] in tys]
        ro = [r for r in old if r["type"] in tys]
        _, eo, so = loko_scores(ro, famname, m7)
        _, en, sn = loko_scores(rn, famname, m7)
        mod = fit_model(rn, famname, m7)
        mod_noE140 = fit_model([r for r in rn if r["exp"] != "E140"], famname, m7)
        model["families"][famname] = {**mod, "card_term": m7["families"][famname]["card_term"],
                                      "form": m7["families"][famname]["form"],
                                      "band_k_m7": m7["families"][famname]["band_k"],
                                      "interval_pool_by_format_card_m7": m7["families"][famname]["interval_pool_by_format_card"]}
        # pool 4 out of sample: M7u without E140's rows, on E140's re-reduced rows
        p4 = []
        for r in rn:
            if r["exp"] != "E140":
                continue
            pr = predict(mod_noE140, r["type"], r["f"], "a3")
            pr_rate = pr * r["rate"] / F.RATE[r["type"]]
            pool = m7["families"][famname]["interval_pool_by_format_card"][f"{r['type']}|a3"]["rms_w"]
            hw = m7["families"][famname]["band_k"] * pool
            p4.append({"key": r["key"], "type": r["type"], "D_footing": r["D"], "D_m7rows": r["D_m7"], "pred": pr_rate,
                       "err": r["D"] - pr_rate, "inside": abs(r["D"] - pr_rate) <= hw, "hw": hw})
        res["families"][famname] = {"loko_old_rows": so, "loko_footing_rows": sn, "m7u": mod,
                                    "m7u_without_E140": mod_noE140, "pool4_out_of_sample": p4}
        print(f"== {famname}: rows {len(rn)} (old {len(ro)}); card term {m7['families'][famname]['card_term']}")
        for lab in ("M7", "M6", "M5"):
            print(f"   {lab} form LOKO old {so[lab]['all']:.4f} -> footing {sn[lab]['all']:.4f} W  "
                  + "  ".join(f"{k} {so[lab][k]['rms_w']:.3f}->{sn[lab][k]['rms_w']:.3f}" for k in sn[lab] if k in tys or k.startswith("card")))
        print(f"   M7u card-1 scale {mod['card1_scale_by_format']} (M7 {m7['families'][famname]['card1_scale_by_format']})")
        print(f"   M7u coef fJ {json.dumps({k: round(v, 2) for k, v in mod['coef_fJ'].items()})}")
        print(f"   M7  coef fJ {json.dumps({k: round(v, 2) for k, v in zip(m7['families'][famname]['terms'], m7['families'][famname]['coef_fJ'])})}")
        for ty in tys:
            e = [x["err"] for x in p4 if x["type"] == ty]
            if e:
                print(f"   pool 4 ({ty}, n {len(e)}), M7u without E140: rms {rms(e):.3f} bias(meas-pred) {np.mean(e):+.3f} inside {sum(x['inside'] for x in p4 if x['type'] == ty)}/{len(e)}")
    json.dump(model, open(os.path.join(HERE, "m7u.json"), "w"), indent=1, sort_keys=True)
    # ---- pool 5: M7u's predictions in a copy of each registration; the registered scorers on old and new measurements
    sdir = os.path.join(HERE, "score")
    os.makedirs(sdir, exist_ok=True)
    regs = {}
    for exp, card, regp, pfile in (("E141", "a3", os.path.join(CV, "e141", "predictions-e141.json"), "predictions-blind5-aifoundry3.json"),
                                   ("E142", "c1", os.path.join(CV, "e142", "predictions-e142.json"), "predictions-blind5-aifoundry1c1.json")):
        reg = load(regp)
        feats = load(os.path.join(B5, pfile))["tiles"]
        ru = copy.deepcopy(reg)
        for t, P in ru["tiles"].items():
            fam = "int8" if P["type"] == "int8" else "float"
            mod = model["families"][fam]
            lo, hi = P["M7"]["D_95"]
            hw = (hi - lo) / 2
            D = predict(mod, P["type"], feats[t]["features"], card)
            P["M7"] = dict(P["M7"], D_w=round(D, 4), D_95=[round(D - hw, 4), round(D + hw, 4)], m7_frozen_D_w=reg["tiles"][t]["M7"]["D_w"])
        if exp == "E142":
            ru["model"]["card1_scale"] = {"floats": model["families"]["float"]["card1_scale_by_format"]["fp32"],
                                          "int8": model["families"]["int8"]["card1_scale_by_format"]["int8"]}
        ru["_q139u"] = "post hoc copy: M7's power predictions replaced by M7u's (Q139(u)), M7's frozen half-widths kept; heat entries are M7's"
        rp = os.path.join(sdir, f"reg-{exp.lower()}-m7u.json")
        json.dump(ru, open(rp, "w"), indent=1)
        regs[exp] = (regp, rp)
    e141o = os.path.join(DD, "2026-11-02-e141-blind5-aifoundry3", "e141.json")
    e142o = os.path.join(DD, "2026-11-02-e142-blind5-card1", "e142.json")
    e141n, e142n = os.path.join(RED, "e141-footing.json"), os.path.join(RED, "e142-footing.json")
    runs = {"E141": os.path.join(scratch, "csv", "runs-e141-footing.csv"), "E142": os.path.join(scratch, "csv", "runs-e142-footing.csv")}
    arms = {
        "E141_committed_frozen": ("e141/score_e141.py", "--e141", e141o, regs["E141"][0], None),
        "E141_footing_frozen": ("e141/score_e141.py", "--e141", e141n, regs["E141"][0], None),
        "E141_footing_m7u": ("e141/score_e141.py", "--e141", e141n, regs["E141"][1], None),
        "E142_committed_frozen": ("e142/score_e142.py", "--e142", e142o, regs["E142"][0], e141o),
        "E142_footing_frozen": ("e142/score_e142.py", "--e142", e142n, regs["E142"][0], e141n),
        "E142_footing_m7u": ("e142/score_e142.py", "--e142", e142n, regs["E142"][1], e141n),
    }
    dig = {}
    for lab, (sc, flag, meas, reg, e141) in arms.items():
        out = os.path.join(sdir, f"scored-{lab}.json")
        st = run_scorer(sc, flag, meas, reg, out, None, e141)
        dig[lab] = {"run": st, **(digest(out, lab[:4]) if st["rc"] == 0 else {})}
        d = dig[lab]
        if st["rc"]:
            print(lab, "scorer failed", st["err"])
            continue
        b1, b2 = d["B1"] or {}, d["B2"] or {}
        print(f"{lab}: leak {d['leak']}, passes {d['passes']}; B1 {b1.get('verdict')} {b1.get('bias_meas_minus_pred_w')} "
              f"[{(b1.get('interval') or {}).get('lo95')}, {(b1.get('interval') or {}).get('hi95')}]; B2 {b2.get('verdict')} "
              f"{b2.get('bias_meas_minus_pred_w')}; C1 {d['C1']}; X1 {d['X1']}; X2 {d['X2']}")
        print("   M7 rms by format", {f: (v or {}).get("rms") for f, v in ((d["reported"]["M7"]["power"]) or {}).items()},
              "all", d["reported"]["M7"]["all"], "cov", d["reported"]["M7"]["coverage"])
    res["scores"] = dig
    # the whole nested procedure on the new rows (form and card term re-chosen inside every fold), beside M7's on the old
    nested = {}
    for famname, tys in FAMS.items():
        rn = [r for r in rows if r["type"] in tys]
        out, frozen, outer, e5, e6 = M7.run_family(rn, famname, m5, m6)
        nested[famname] = {"chosen_form": out["chosen_form"], "card_term_chosen": out["card_term_chosen"],
                           "nested": out["side_by_side_same_folds"]["M7_nested_loko"],
                           "M5_frozen_no_refit": out["side_by_side_same_folds"]["M5_frozen_no_refit"],
                           "M6_frozen_no_refit": out["side_by_side_same_folds"]["M6_frozen_no_refit"],
                           "card1_scale": frozen["card1_scale_by_format"]}
        print(f"nested procedure on footing rows, {famname}: picks {out['chosen_form']} / {out['card_term_chosen']}, nested "
              f"{out['side_by_side_same_folds']['M7_nested_loko']['all']:.4f} W (M7's own at freeze: see loko-m7.json)")
    res["nested_procedure_footing_rows"] = nested
    json.dump(res, open(os.path.join(HERE, "scores-m7u.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
