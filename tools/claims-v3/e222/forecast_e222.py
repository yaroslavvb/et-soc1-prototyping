#!/usr/bin/env python3
"""E222 (Q236): THE FORECASTS, frozen by FROZEN.txt (OUT/reg-e222/FROZEN.txt, posted by the orchestrator) and by E222's registration commit:
every E222 point, the tie t01 and the two smoke rows, at aifoundry3 card 0's pinned 600.0 MHz, by every forecaster each from its frozen code
unchanged (desk/models_e222.py, the file the point rule's hash record names): MM1-v3.2 (the registered baseline), the three MM1-v3.3 candidates
'MM1-v3.2 + posimb', 'MM1-v3.2 + AF4' and 'MM1-v3.2 + L3S', MM1-v3.1, MM1-v3 and MM1-v2 beside, and 'MM1-v3.2 + all three' by construction
(desk/models_e222.compose, no refit; registered only if it composes at every row). numpy through the predictors; single-threaded.

    /usr/bin/python3 -I -B tools/claims-v3/e222/forecast_e222.py            writes forecast-e222.json, forecast-e222.csv, forecast-e222.txt
    /usr/bin/python3 -I -B tools/claims-v3/e222/forecast_e222.py --check    re-makes them in memory (by one combined call of every candidate, not
                                                                            the freeze's one call per candidate) and compares with the files

Per point and forecaster: the op time (us, the slowest minion), cycles an op on the wall and the counter's mean, seconds a GEMM, W over idle at
its own seconds, the affine form W = A + B / t_op (t_op in us: the scorer's given()), J over idle a GEMM, the rest law and the J at rest with t
forecast, and each candidate's term (REPORTED); the planning peaks (PP32, the drop rule's; PP_all, REPORTED); how each model and candidate prices
aifoundry3 card 0 (forecast-e222.json > per_card).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "desk"))
import models_e222 as MZ  # noqa: E402

POINTS = "points-e222.json"
RULE_HASH = "desk/point-rule-e222.sha256"
EXTRA = (("t01", "tie (E218's t01, a bridge; run and read, never in a rule)", "gemmL2x4x4", "fp32"),
         ("s01", "smoke (the session gate; never a point)", "gemmL2x2x2", "fp32"),
         ("s03", "smoke (the G block's gate; never a point)", "gemmLnc2x2x2", "fp32"))
QTY = ("T_op_us", "cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm", "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm",
       "rest_law_W", "J_at_rest_per_gemm")
WHICH = ("posimb", "af4", "l3s")
CNAME = {"posimb": MZ.POSIMB, "af4": MZ.AF4, "l3s": MZ.L3S}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def r12(x):
    return None if x is None else float("%.12g" % x)


def clean(v):
    if isinstance(v, float):
        return r12(v)
    if isinstance(v, dict):
        return {k: clean(x) for k, x in v.items() if k != "Q_mean"}
    if isinstance(v, list):
        return [clean(x) for x in v]
    return v


def check_rule_hash():
    """the forecasts are made through the files the point rule's hash record names, unchanged"""
    lines = [ln for ln in open(os.path.join(HERE, RULE_HASH)) if ln.strip() and not ln.startswith("#")]
    for ln in lines:
        h, f = ln.split(None, 1)
        f = f.strip()
        if f.startswith("desk/") and f.endswith(".py") and sha(os.path.join(HERE, f)) != h:
            print(f"forecast_e222: REFUSED, {f} differs from the point rule's hash record")
            sys.exit(4)


def build(combined=False):
    check_rule_hash()
    R = json.load(open(os.path.join(HERE, POINTS)))
    M = MZ.Models()
    pts = [{"id": p["id"], "arm": p["token"], "fmt": p["format"], "kind": p["kind"], "mask": p["shire_mask"]} for p in R["points"]]
    pts += [{"id": i, "arm": t, "fmt": f, "kind": "random", "mask": "0xffffffff"} for i, _, t, f in EXTRA]
    roles = {i: w for i, w, _, _ in EXTRA}
    base = M.forecast(pts, models=MZ.MODELS, cands=False)
    if combined:
        allc = M.forecast(pts, models=("MM1-v3.2",), cands=True, which=WHICH)
        for p in pts:
            for c in WHICH:
                base[p["id"]][CNAME[c]] = allc[p["id"]][CNAME[c]]
            base[p["id"]]["_combo_from_call"] = allc[p["id"]].get(MZ.COMBO)
    else:
        for c in WHICH:
            got = M.forecast(pts, models=("MM1-v3.2",), cands=True, which=(c,))
            for p in pts:
                assert got[p["id"]]["MM1-v3.2"] == base[p["id"]]["MM1-v3.2"], "MM1-v3.2 differs between calls"
                base[p["id"]][CNAME[c]] = got[p["id"]][CNAME[c]]
    # the combination, by construction (desk/models_e222.compose: exit 5 where it would not compose)
    fails = {}
    for p in pts:
        try:
            base[p["id"]][MZ.COMBO] = MZ.compose(p, base[p["id"]], M)
        except SystemExit as e:
            fails[p["id"]] = f"compose refused (exit {e.code})"
    combo_registered = not fails
    if combined:
        for p in pts:
            if base[p["id"]].pop("_combo_from_call", None) != base[p["id"]].get(MZ.COMBO):
                fails[p["id"]] = "the combined call's combination differs"
    names = MZ.MODELS + MZ.CANDS + ((MZ.COMBO,) if combo_registered else ())
    # the posimb features the freeze re-made must equal the point rule's (desk/posimb-features-e222.json)
    made_rule = json.load(open(os.path.join(HERE, "desk", "posimb-features-e222.json")))
    feat_check = {"rule_made": len(made_rule), "remade_here": len(M.PS_made),
                  "equal": set(M.PS_made) <= set(made_rule) and all(made_rule[k] == v for k, v in M.PS_made.items())}
    out = {"what": ("E222's frozen forecasts: every point, the tie and the smoke rows at aifoundry3 card 0, 600.0 MHz, by MM1-v3.2 (the registered "
                    "baseline), the three MM1-v3.3 candidates, MM1-v3.1, MM1-v3 and MM1-v2, each from its frozen code unchanged "
                    "(desk/models_e222.py), and 'MM1-v3.2 + all three' by construction"),
           "points_sha256": sha(os.path.join(HERE, POINTS)), "rule_hash_record_sha256": sha(os.path.join(HERE, RULE_HASH)), "pins": M.pins,
           "interpreter": "/usr/bin/python3 " + sys.version.split()[0], "card": MZ.A3, "f_mhz": MZ.F_REG,
           "calls": {
               "MM1-v3.2": "mm1_v32.Model(out/mm1_v32_params.json).predict_many([{card, arm: token, fmt, kind: 'random', mask, f, kernel: 'rgm136'}])",
               "MM1-v3.1": "mm1_v31.Model(out/mm1_v31_params.json).predict_many([{card, arm: token, fmt, kind: 'random', mask, f, kernel: 'rgm136'}])",
               "MM1-v3": "mm1_v3.Model(out/mm1_v3_params.json).predict(card, token, fmt, 'random', mask, f, kernel='rgm136', t0_c=None)",
               "MM1-v2": "e213_v3.v2_model().predict(card, token with gemmLnc read as gemmL, fmt, 'random', mask, f, V=None, t0_c=None)",
               MZ.POSIMB: ("MM1-v3.2's call, then posimb/scripts/h01_freeze.py's per-row form (its fields() and compose() imported from the file): "
                           "g_wall = clip(1 + a_hop Phi_hop + a_lag Phi_lag, 0.3, 3) at subset rgm136 gemmL points; features from posimb/out/"
                           "private_shared.json or f02_private.py's private_shared() and mesh_lat(); a_hop, a_lag from posimb/out/fit_results.json"),
               MZ.AF4: ("MM1-v3.2's call, then gemmlnc-af4/scripts/s03_freeze.py's per-row form: F3 removed, AF4's term added at MM1-v3.2's op time "
                        "(features by s02_fit.py's feats() taken from its text; c1, c2 from data/fit-record.json)"),
               MZ.L3S: "l3s/scripts/term_l3s.ModelL3S(MM1-v3.2's params, lam = out/fit/fit-l3s.json lam_all, the landed cache + desk/l3s-extra-e222.json).predict_many([...])",
               MZ.COMBO: "desk/models_e222.compose: per point the one term that acts, or L3S with F3's coefficient replaced by AF4's at a full-mask gemmLnc point",
               "given": ("card 'aifoundry3 card 0'; f 600.0 MHz; V, G, t0_c, minions and ops not given (each model's own volts and governed base at f for "
                         "the card; the energy at a 50 C die; 32 minions a shire of the mask; 64 MB NB KB ops a minion)")},
           "combination": {"registered": combo_registered, "refused_at": fails,
                           "acting_counts": {}, "construction": MZ.__doc__.split("THE COMBINATION")[1].split("THE PLANNING PEAK")[0].strip()},
           "posimb_features_check": feat_check, "l3s_records_made_by_the_freeze": sorted(set(M.l3s_extra) - set(json.load(open(MZ.L3S_EXTRA)))),
           "eps_G": M.eps_g, "rest_law_v32": M.rest, "points": {}}
    # how each model and candidate prices aifoundry3 card 0
    th32 = M.P32["energy"]["theta"]
    th31 = M.P31["energy"]["theta"]
    out["per_card"] = {
        "MM1-v3.2": {"Pa_W_awake_at_1024_minions": th32.get("Pa|aifoundry3 card 0"), "kc_energy_scale": "1 (the reference card: no kc term)",
                     "volts": M.P32["energy"].get("volts", {}).get("pinned", {}).get(MZ.A3), "rest_law": M.P32.get("rest_law", {}).get(MZ.A3),
                     "governed_base_W": 0.0, "time": "shared constants across cards; the clock f an input (no per-card time term)"},
        "MM1-v3.1": {"Pa_W_awake_at_1024_minions": th31.get("Pa|aifoundry3 card 0"), "kc_energy_scale": "1 (the reference card)",
                     "rest_law": M.P31.get("rest_law", {}).get(MZ.A3)},
        MZ.POSIMB: {"how": "MM1-v3.2's per-card terms for the card; posimb's two constants carry no card factor", "a_hop": M.a_hop, "a_lag": M.a_lag},
        MZ.AF4: {"how": "MM1-v3.2's per-card terms for the card (S_own = F3 / (c1 26 + c2 first) carries the card's volts through MM1-v3.2's sL); "
                        "AF4's two constants carry no card factor", "c1_c2_pJ": M.CONST_AF4},
        MZ.L3S: {"how": "MM1-v3.2's per-card terms for the card (its energy on L3S's map); L3S's one constant carries no card factor", "lam": M.lam}}
    acting = {}
    for p in pts:
        o = base[p["id"]]
        pp32, ppall, by = M.planning_peak({k: v for k, v in o.items() if k in names}, p["arm"])
        row = {"token": p["arm"], "fmt": p["fmt"], "kind": p["kind"], "mask": p["mask"], "role": roles.get(p["id"], "point"),
               "models": {m: clean(o.get(m) or {}) for m in names}, "PP32_W": r12(pp32), "PP_all_W": r12(ppall), "PP_all_by": by}
        if combo_registered:
            a = " + ".join(o[MZ.COMBO]["acting"]) or "none"
            acting[a] = acting.get(a, 0) + 1
        out["points"][p["id"]] = row
    out["combination"]["acting_counts"] = acting
    out["forecasters"] = list(names)
    return out


def table(F):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["card", "id", "role", "token", "format", "mask", "f_mhz", "model"] + list(QTY) + ["PP32_W"])
    for pid, r in F["points"].items():
        for m in F["forecasters"]:
            x = r["models"].get(m) or {}
            w.writerow([F["card"], pid, r["role"], r["token"], r["fmt"], r["mask"], "%.1f" % F["f_mhz"], m] +
                       [("" if x.get(q) is None else "%.9g" % x[q]) for q in QTY] + [("" if r["PP32_W"] is None else "%.6g" % r["PP32_W"])])
    return buf.getvalue()


def summary(F):
    S = ("MM1-v3.2", MZ.POSIMB, MZ.AF4, MZ.L3S, MZ.COMBO if MZ.COMBO in F["forecasters"] else None, "MM1-v3.1", "MM1-v3", "MM1-v2")
    S = [s for s in S if s]
    L = [f"E222's frozen forecasts (forecast-e222.json) at {F['card']}, {F['f_mhz']:.1f} MHz. Columns per forecaster in this order: "
         + ", ".join(S),
         "id | token fmt mask | wall cycles an op | W over idle at its own seconds | MM1-v3.2 ms a GEMM | PP32"]
    for pid, r in F["points"].items():
        ms = r["models"]

        def g(m, q, fmtx):
            x = (ms.get(m) or {}).get(q)
            return "-" if x is None else fmtx % x
        L.append(f"{pid:6s} | {r['token']:16s} {r['fmt']:5s} {r['mask']:10s} | " + " / ".join(g(m, 'cycles_per_op_wall', '%.1f') for m in S) +
                 " | " + " / ".join(g(m, 'W_over_idle', '%.2f') for m in S) + f" | {g('MM1-v3.2', 'seconds_per_gemm', '%.6f')} s | "
                 f"{('%.2f' % r['PP32_W']) if r['PP32_W'] else '-'}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    F = build(combined=a.check)
    js = json.dumps(F, indent=1, sort_keys=True) + "\n"
    files = {"forecast-e222.json": js, "forecast-e222.csv": table(F), "forecast-e222.txt": summary(F)}
    if a.check:
        bad = [k for k, v in files.items() if open(os.path.join(HERE, k)).read() != v]
        print("forecast_e222 --check (one combined candidate call):", "SAME" if not bad else f"DIFFER {bad}")
        sys.exit(0 if not bad else 1)
    for k, v in files.items():
        open(os.path.join(HERE, k), "w").write(v)
    print(datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"), {k: sha(os.path.join(HERE, k)) for k in files},
          "combination registered:", F["combination"]["registered"], F["combination"]["acting_counts"], "posimb features", F["posimb_features_check"],
          "l3s records made here", F["l3s_records_made_by_the_freeze"])


if __name__ == "__main__":
    main()
