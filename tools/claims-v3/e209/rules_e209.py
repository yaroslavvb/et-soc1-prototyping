#!/usr/bin/env python3
"""E209 (Q202): every band, tie, threshold and test of E209's scoring, computed from MM1-v2's committed held-out record and E208's committed
data on this card by the rules E209.md section 7 states, with each head-to-head test's power against the predicted gaps. Desk; numpy (the
predictors and the power simulation), Python otherwise. Nothing is measured.

    python3 -I -B tools/claims-v3/e209/rules_e209.py            writes rules-e209.json beside this file
    python3 -I -B tools/claims-v3/e209/rules_e209.py --check    re-makes it in memory and compares byte for byte (PASS / FAIL)

THE BANDS (MM1-v2's rules): twice the larger of MM1-v2's two held-out rms errors for the quantity - (i) the E208 fold (every constant refitted
  without E208, the experiment that taught MM1-v2 its 800 MHz terms) on E208's aifoundry2 card 0 points (this day's card and clock), and (ii)
  leave one experiment out over all points - rounded up to a whole percent (E207's rule, with E208 in E206's place). Read from
  tools/matmul/mm1/v2/out/holdout_v2.json; the counter's mean on E208's aifoundry2 points in the E208 fold is not recorded there, so it is
  computed here by summary_v2.py's own method (MM1-v2's held-out wall cycles over its rho, against the measured counter's mean) restricted
  to those points, and its all-cards value (summary_v2.json, 7.88%) taken in (ii)'s place (LOEO over all points is not recorded for it).
  Seconds given the measured clock are the wall cycles given the clock by the reducer's arithmetic: T3's band is T1's.
THE WATTS BAND (a point under about 3 W over idle): 2 x SD_rep, SD_rep the meter's replicate spread on this card: the pooled within-session
  sd of the W over idle of E208's anchor (4x8x8-int8-rnd, the one arm run more than once within a session there: 9 times in each of the
  sessions a2c0-S1, a2c0-S2 and a2c0-S1r), rounded up to 0.01 W. Beside it (REPORTED): the S1 / S1r per-run spread over every arm both read.
THE TIES of the head-to-head (in ln for cycles and joules, in watts at the watts points): at or above the replicate floor on this card (the
  same anchors' pooled within-session sd of ln of each reading), on the grid 0.001, 0.002, 0.005, 0.01, 0.02; the watts tie 0.05 W.
THE CLOCK BAND (K1): twice the governor model's chain rms of the burst's mean clock on E208's aifoundry2 runs (in sample: governor_v2.json),
  rounded up to a whole MHz.
THE HEAD-TO-HEAD TESTS and their power: each H rule's decision test is stated here (the exact two-sided sign test at alpha 0.05 on the untied
  cases, or the percentile bootstrap 95% interval of the mean d, B = 10,000); the power of both, simulated (seeded) on the frozen forecasts of
  E209's cases with the truth drawn as each model's forecast times exp(N(0, sigma)) (independent cases; sigma at MM1-v2's in-sample and
  held-out errors), is recorded, and the registered test is the one named in DECISION below, chosen by that power before any datum.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import hashlib
import json
import math
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V2 = "tools/matmul/mm1/v2"
S1R = "docs/reports/data/2026-11-17-e208-mmsweep-a2c0-S1r/data-e208-a2c0-S1r.json"
INPUTS = [f"{V2}/out/holdout_v2.json", f"{V2}/out/summary_v2.json", f"{V2}/out/governor_v2.json", f"{V2}/out/points_time_v2.csv",
          f"{V2}/data_e208.py", f"{V2}/inputs/e208/a2c0-S1__data-e208-a2c0-S1.json", f"{V2}/inputs/e208/a2c0-S2__data-e208-a2c0-S2.json", S1R]
GRID = (0.001, 0.002, 0.005, 0.01, 0.02)
DECISION = {"H1": "bootstrap", "H2": "bootstrap", "H3": "bootstrap", "H4": "bootstrap", "H5": "sign", "H6": "sign"}
NSIM, BSIM = 1000, 1000


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def up(x, step):
    return math.ceil(round(x / step, 9)) * step


def anchors_e208():
    """E208's aifoundry2 anchors, by session: (dP_w, ln cyc_op_max, ln cyc_op_mean, ln t_pass, ln J_pass_over) of each energy-read run"""
    src = {"a2c0-S1": f"{V2}/inputs/e208/a2c0-S1__data-e208-a2c0-S1.json", "a2c0-S2": f"{V2}/inputs/e208/a2c0-S2__data-e208-a2c0-S2.json",
           "a2c0-S1r": S1R}
    out, per_arm = {}, {}
    for sess, rel in src.items():
        D = json.load(open(os.path.join(REPO, rel)))
        rows = []
        for r in D["runs"]:
            v = (r.get("views") or {}).get(r.get("primary_view")) or {}
            ok = v.get("dP_w") is not None and v.get("p_mean_w") and not r.get("capped") and r["role"] != "time" and not v.get("thin")
            if r["role"] == "anchor" and ok:
                rows.append((v["dP_w"], math.log(v["cyc_op_max"]), math.log(v["cyc_op_mean"]), math.log(v["t_pass_s"]), math.log(v["J_pass_over"])))
            if r["role"] in ("arm", "anchor") and ok:
                per_arm.setdefault(sess, {}).setdefault(r["arm"], []).append(v["dP_w"])
        out[sess] = rows
    return out, per_arm


def pooled(groups, k):
    num = sum((len(g) - 1) * statistics.variance([x[k] for x in g]) for g in groups if len(g) > 1)
    den = sum(len(g) - 1 for g in groups if len(g) > 1)
    return math.sqrt(num / den), den


def counter_mean_heldout():
    """summary_v2.py's method for the counter's mean, restricted to E208's aifoundry2 card 0 points (the E208 fold: column v2_loeo)"""
    sys.path.insert(0, os.path.join(REPO, V2))
    import data_e208 as D8  # noqa: E402
    import mm1_v2 as M2  # noqa: E402
    P = json.load(open(os.path.join(REPO, V2, "out", "mm1_v2_params.json")))
    M = M2.Model(P)
    pt = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, V2, "out", "points_time_v2.csv")))}
    T8 = {}
    for r in D8.runs():
        T8.setdefault(f"E208|{ {'a2c0': 'a2', 'a1c1': 'c1', 'a1c0': 'c0'}[r['card_key']] }|{r['case']}", []).append(r)
    res = {"all": {"v2_loeo": []}, "a2": {"v2_loeo": [], "v2_in": [], "v2_loco": []}}
    for pid, rs in T8.items():
        if pid not in pt or "T" not in rs[0]:
            continue
        p = pt[pid]
        o = M.predict(rs[0]["card"], rs[0]["arm"], rs[0]["fmt"], rs[0]["kind"], rs[0]["mask"], float(p["f_mhz"]), ops=rs[0]["ops"], minions=rs[0]["minions"])
        meas = float(np.mean([r["cyc_mean"] for r in rs]))
        e = float(p["v2_loeo"]) / o["rho_wall_over_mean"] / meas - 1
        res["all"]["v2_loeo"].append(e)
        if pid.startswith("E208|a2|"):
            for col in ("v2_loeo", "v2_in", "v2_loco"):
                res["a2"][col].append(float(p[col]) / o["rho_wall_over_mean"] / meas - 1)
    st = lambda v: {"n": len(v), "rms_pct": round(float(np.sqrt(np.mean(np.square(v)))) * 100, 2), "bias_pct": round(float(np.mean(v)) * 100, 2)}
    return {"all E208 (the E208 fold)": st(res["all"]["v2_loeo"]), "E208 aifoundry2 card 0, the E208 fold": st(res["a2"]["v2_loeo"]),
            "E208 aifoundry2 card 0, in sample": st(res["a2"]["v2_in"]), "E208 aifoundry2 card 0, LOCO": st(res["a2"]["v2_loco"])}


def ppass(band, sigma, n, share=0.9):
    """P(at least share of n cases inside |ln err| <= ln(1 + band)), errors normal in ln with sd sigma (independent)"""
    from math import comb, erf, sqrt
    lo, hi = math.log(1 - band), math.log(1 + band)
    p = 0.5 * (erf(hi / (sigma * sqrt(2))) - erf(lo / (sigma * sqrt(2))))
    k0 = math.ceil(round(share * n, 9))
    return sum(comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(k0, n + 1))


def power(a, b, sigma, tie, alpha, min_n, seed):
    """a, b: ln forecasts of MM1-v2 and the other model per case; the truth = a, b or their midpoint plus N(0, sigma) in ln"""
    import score_e209 as S  # noqa: E402  (the scorer's own sign test)
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a), np.asarray(b)
    n = len(a)
    res = {}
    for truth, c in (("MM1-v2", a), ("other", b), ("midpoint", 0.5 * (a + b))):
        cnt = {"sign": {"MM1-v2 BETTER": 0, "OTHER BETTER": 0, "NOT DECIDED": 0, "TOO FEW": 0},
               "bootstrap": {"MM1-v2 BETTER": 0, "OTHER BETTER": 0, "NOT DECIDED": 0}}
        for _ in range(NSIM):
            m = c + rng.normal(0.0, sigma, n)
            d = np.abs(m - b) - np.abs(m - a)
            w, l = int(np.sum(d > tie)), int(np.sum(d < -tie))
            if w + l < min_n:
                cnt["sign"]["TOO FEW"] += 1
            else:
                p = S.sign_test_p(w, l)
                cnt["sign"]["MM1-v2 BETTER" if (p <= alpha and w > l) else ("OTHER BETTER" if (p <= alpha and l > w) else "NOT DECIDED")] += 1
            idx = rng.integers(0, n, size=(BSIM, n))
            mm = np.sort(d[idx].mean(axis=1))
            lo, hi = mm[int(0.025 * BSIM)], mm[int(0.975 * BSIM) - 1]
            cnt["bootstrap"]["MM1-v2 BETTER" if lo > 0 else ("OTHER BETTER" if hi < 0 else "NOT DECIDED")] += 1
        res[truth] = {t: {k: round(v / NSIM, 3) for k, v in cc.items()} for t, cc in cnt.items()}
    return res


def build():
    H = json.load(open(os.path.join(REPO, V2, "out", "holdout_v2.json")))
    Sm = json.load(open(os.path.join(REPO, V2, "out", "summary_v2.json")))
    G = json.load(open(os.path.join(REPO, V2, "out", "governor_v2.json")))
    tv2 = H["time v2"]["loeo"]
    ev2 = H["energy v2"]["stats"]
    cm = counter_mean_heldout()
    rec_cm = Sm["heldout"]["counter's mean, E208 (one point a card and case)"]["v2_loeo"]
    if abs(cm["all E208 (the E208 fold)"]["rms_pct"] - rec_cm["rms_pct"]) > 0.005:
        sys.exit(f"refused: the counter's-mean method does not reproduce summary_v2.json ({cm['all E208 (the E208 fold)']} vs {rec_cm})")
    basis = {
        "T1": {"what": "cycles an op, the wall, per time case", "i": tv2["E208 aifoundry2 card 0"]["rms_pct"], "ii": tv2["all"]["rms_pct"],
               "i_src": "holdout_v2.json > time v2 > loeo > E208 aifoundry2 card 0", "ii_src": "holdout_v2.json > time v2 > loeo > all"},
        "T2": {"what": "cycles an op, the counter's mean, per time case", "i": cm["E208 aifoundry2 card 0, the E208 fold"]["rms_pct"],
               "ii": rec_cm["rms_pct"], "i_src": "computed here (summary_v2.py's method, E208's aifoundry2 points, column v2_loeo)",
               "ii_src": "summary_v2.json > heldout > counter's mean, E208 > v2_loeo (all three cards; LOEO over all points not recorded)"},
        "E1": {"what": "J over idle given the measured seconds, per point", "i": ev2["LOEO | W = J over idle given t (>= 3 W) | E208 aifoundry2 card 0"]["rms_pct"],
               "ii": ev2["LOEO | W = J over idle given t (>= 3 W) | all"]["rms_pct"], "i_src": "holdout_v2.json > energy v2 > LOEO | W = J over idle given t (>= 3 W) | E208 aifoundry2 card 0",
               "ii_src": "... | all"},
        "E2": {"what": "J over idle with the seconds forecast, per point", "i": ev2["LOEO | J over idle t forecast (>= 3 W) | E208 aifoundry2 card 0"]["rms_pct"],
               "ii": ev2["LOEO | J over idle t forecast (>= 3 W) | all"]["rms_pct"], "i_src": "holdout_v2.json > energy v2 > LOEO | J over idle t forecast (>= 3 W) | E208 aifoundry2 card 0",
               "ii_src": "... | all"},
        "E3": {"what": "J with the card at rest given the measured seconds, per point", "i": ev2["LOEO | J at rest given t | E208 aifoundry2 card 0"]["rms_pct"],
               "ii": ev2["LOEO | J at rest given t | all"]["rms_pct"], "i_src": "holdout_v2.json > energy v2 > LOEO | J at rest given t | E208 aifoundry2 card 0",
               "ii_src": "... | all"},
        "E4": {"what": "J with the card at rest with the seconds forecast, per point", "i": ev2["LOEO | J at rest t forecast | E208 aifoundry2 card 0"]["rms_pct"],
               "ii": ev2["LOEO | J at rest t forecast | all"]["rms_pct"], "i_src": "holdout_v2.json > energy v2 > LOEO | J at rest t forecast | E208 aifoundry2 card 0",
               "ii_src": "... | all"},
    }
    bands = {}
    for k, b in basis.items():
        m = max(b["i"], b["ii"])
        bands[k] = dict(b, larger_pct=m, band_pct=int(up(2 * m, 1)), band_rel=int(up(2 * m, 1)) / 100.0,
                        arithmetic=f"2 x max({b['i']}, {b['ii']}) = {2 * m:.2f} -> {int(up(2 * m, 1))}%")
    bands["T3"] = dict(bands["T1"], what="seconds a GEMM, per time case (given the measured clock = the wall cycles given the clock; the same band)")
    A, per_arm = anchors_e208()
    groups = [g for g in A.values() if len(g) > 1]
    sdW, dfW = pooled(groups, 0)
    floors = {}
    for k, nm in ((1, "cycles wall"), (2, "cycles mean"), (3, "seconds"), (4, "J over idle")):
        floors[nm] = pooled(groups, k)[0]
    tie_cyc = min(g for g in GRID if g >= max(floors["cycles wall"], floors["cycles mean"], floors["seconds"]))
    tie_j = min(g for g in GRID if g >= floors["J over idle"])
    a, b = per_arm.get("a2c0-S1", {}), per_arm.get("a2c0-S1r", {})
    diffs = [statistics.mean(a[x]) - statistics.mean(b[x]) for x in a if x in b]
    s1r = {"arms": len(diffs), "mean_diff_W": round(statistics.mean(diffs), 4), "per_run_sd_W": round(statistics.stdev(diffs) / math.sqrt(2), 4)}
    watts = {"SD_rep_W": round(sdW, 4), "df": dfW, "band_w": round(up(2 * sdW, 0.01), 2),
             "how": "2 x the pooled within-session sd of E208's anchor's W over idle (a2c0-S1, a2c0-S2, a2c0-S1r: 9 runs each), rounded up to 0.01 W",
             "anchor_runs_by_session": {k: len(v) for k, v in A.items()}, "S1_vs_S1r_REPORTED": s1r,
             "threshold_w": 3.0, "which_points": "a point whose MM1-v2 W over idle at 799.0 MHz is under 3 W (none of E209's 45: its lowest is e39, "
                                               "7.51 W) or whose measured W over idle (the mean over its energy runs) is under 3 W"}
    clock = {"band_mhz": int(up(2 * G["chain"]["f_burst_mean_rms_mhz"], 1)), "basis_mhz": G["chain"]["f_burst_mean_rms_mhz"],
             "how": "2 x the chain's rms of the burst's mean clock on E208's 160 aifoundry2 runs (governor_v2.json > chain; in sample), rounded up to a MHz"}
    head = {"alpha": 0.05, "min_untied": 10, "tie_ln": {"cycles": tie_cyc, "joules": tie_j}, "tie_w": 0.05,
            "replicate_floors_ln": {k: round(v, 6) for k, v in floors.items()},
            "rules": {"H1": {"what": "cycles an op, the wall: MM1-v2 against MM1-v1, both at each run's measured clock, per time case", "decision": DECISION["H1"]},
                      "H2": {"what": "cycles an op, the counter's mean: MM1-v2 against MM1-v1 at the measured clock, per time case", "decision": DECISION["H2"]},
                      "H3": {"what": "seconds a GEMM given the measured clock: MM1-v2 against MM1-v1, per time case (equal to H1 by the reducer's arithmetic)",
                             "decision": DECISION["H3"]},
                      "H4": {"what": "J over idle given the measured seconds (and clock): MM1-v2 against MM1-v1, per point both price", "decision": DECISION["H4"]},
                      "H5": {"what": "cycles an op, the wall: MM1-v2 (measured clock) against F1@800, per time case", "decision": DECISION["H5"]},
                      "H6": {"what": "J over idle with the seconds forecast: MM1-v2 (measured clock) against F2@800, per point both price", "decision": DECISION["H6"]}}}
    # the power of both tests against the predicted gaps (frozen forecasts at 799 MHz; F1 / F2 at 800 MHz)
    pts = json.load(open(os.path.join(HERE, "points-e209.json")))
    v2 = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, V2, "out", "mm1_v2_e209.csv")))}
    v1 = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, V2, "out", "mm1_v1_e209.csv")))}
    f12 = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, V2, "out", "f1f2_e209.csv")))}
    fl = lambda x: float(x) if x not in ("", None) else None
    tcs = pts["time_cases"]
    def case_ln(col, src):
        out = []
        for tc, ms in sorted(tcs.items()):
            vals = [fl(src[m][col]) for m in ms]
            if all(v is not None for v in vals):
                out.append(math.log(sum(vals) / len(vals)))
        return out
    a_w, b1_w = case_ln("cyc_wall@799", v2), case_ln("cyc_wall@799", v1)
    a_m, b1_m = case_ln("cyc_mean@799", v2), case_ln("cyc_mean@799", v1)
    bF1 = [math.log(sum(fl(f12[m]["F1_cycles_per_op@800"]) for m in ms) / len(ms)) for tc, ms in sorted(tcs.items())]
    ej = [(math.log(fl(v2[p]["J_over@799"])), math.log(fl(v1[p]["J_over@799"]))) for p in v2 if fl(v1[p]["J_over@799"]) is not None]
    ef2 = [(math.log(fl(v2[p]["J_over@799"])), math.log(fl(f12[p]["F2_J_over@800"]))) for p in v2 if fl(f12[p].get("F2_J_over@800")) is not None]
    sig = {"cycles": (H["time v2"]["in_sample"]["E208 aifoundry2 card 0"]["rms_pct"] / 100.0, tv2["E208 aifoundry2 card 0"]["rms_pct"] / 100.0),
           "cycles_mean": (cm["E208 aifoundry2 card 0, in sample"]["rms_pct"] / 100.0, cm["E208 aifoundry2 card 0, the E208 fold"]["rms_pct"] / 100.0),
           "joules": (ev2["in | W = J over idle given t (>= 3 W) | E208 aifoundry2 card 0"]["rms_pct"] / 100.0,
                      ev2["LOEO | W = J over idle given t (>= 3 W) | all"]["rms_pct"] / 100.0)}
    sets = {"H1": (a_w, b1_w, "cycles", tie_cyc), "H2": (a_m, b1_m, "cycles_mean", tie_cyc), "H4": ([x for x, _ in ej], [y for _, y in ej], "joules", tie_j),
            "H5": (a_w, bF1, "cycles", tie_cyc), "H6": ([x for x, _ in ef2], [y for _, y in ef2], "joules", tie_j)}
    pw = {}
    for h, (aa, bb, sk, tie) in sets.items():
        gaps = [abs(x - y) for x, y in zip(aa, bb)]
        pw[h] = {"n": len(aa), "predicted_gap_rms_ln": round(math.sqrt(sum(g * g for g in gaps) / len(gaps)), 4),
                 "cases_gap_over_2pct": sum(1 for g in gaps if g > 0.02), "cases_gap_under_tie": sum(1 for g in gaps if g <= tie)}
        for lab, s in zip(("sigma_in_sample", "sigma_held_out"), sig[sk]):
            pw[h][lab] = {"sigma_ln": round(s, 4), "result": power(aa, bb, s, tie, head["alpha"], head["min_untied"], seed=abs(hash_seed(f"E209|power|{h}|{lab}")))}
    pw["H3"] = {"note": "H3 equals H1 (seconds given the measured clock are the wall cycles given the clock)"}
    n_t = len(tcs)
    n_e = len(pts["points"])
    pp = {}
    for k in ("T1", "T2", "T3", "E1", "E2", "E3", "E4"):
        s = bands[k]["larger_pct"] / 100.0
        n = n_t if k.startswith("T") else n_e
        pp[k] = {"n": n, "at_1x": round(ppass(bands[k]["band_rel"], s, n), 3), "at_1.25x": round(ppass(bands[k]["band_rel"], 1.25 * s, n), 3),
                 "at_1.5x": round(ppass(bands[k]["band_rel"], 1.5 * s, n), 3)}
    out = {"experiment": "E209", "what": "every band, tie, threshold and test of E209's scoring (E209.md section 7); desk, from committed files",
           "inputs_sha256": {p: sha(os.path.join(REPO, p)) for p in INPUTS}, "pins_local": {"points-e209.json": sha(os.path.join(HERE, "points-e209.json"))},
           "verdict": {"share": 0.9, "min_scored": 10, "how": "PASS if at least 90% of a rule's scored cases or points pass; FAIL otherwise; TOO FEW under 10; NO DATA with none"},
           "bands": bands, "counter_mean_heldout_desk": cm, "watts": watts, "clock": clock, "head_to_head": head, "power_REPORTED": pw,
           "p_pass_REPORTED": {"how": "desk: P(at least 90% of n inside the band) with independent normal errors in ln at 1, 1.25 and 1.5 x the band's basis", **pp},
           "python": sys.version.split()[0], "numpy": np.__version__, "simulations": {"days": NSIM, "bootstrap_resamples_in_simulation": BSIM}}
    return json.dumps(out, indent=1, sort_keys=True) + "\n"


def hash_seed(s):
    return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)


def main():
    sys.path.insert(0, HERE)
    txt = build()
    p = os.path.join(HERE, "rules-e209.json")
    if "--check" in sys.argv[1:]:
        ok = open(p, encoding="utf-8").read() == txt
        print("RULES CHECK " + ("PASS" if ok else "FAIL"))
        sys.exit(0 if ok else 1)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(txt)
    o = json.loads(txt)
    print({k: v["band_pct"] for k, v in o["bands"].items()}, "watts", o["watts"]["band_w"], "clock", o["clock"]["band_mhz"], "ties",
          o["head_to_head"]["tie_ln"], o["head_to_head"]["tie_w"])


if __name__ == "__main__":
    main()
