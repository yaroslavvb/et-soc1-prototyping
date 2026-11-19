#!/usr/bin/env python3
"""E216 (Q227): every band, tie, threshold and test of E216, computed before any datum from MM1-v3.1's held-out record as landed (2c971828; E215's
rules_e215.py functions heldout(), validate(), bases(), p_pass() and sign_test(), imported unchanged at their pin) and from E216's frozen
forecasts (forecast-e216.json). Desk; /usr/bin/python3 3.12.3 -I -B, numpy, single-threaded. Writes rules-e216.json and prints the tables.

THE BANDS (E216.md section 7; E215's form): band = 2 x the larger of B1 (MM1-v3.1's LOEO error without configuration twins over every point) and
B2 (the same over aifoundry2 card 0's points), rounded up to a whole percent; T3 (seconds) takes T1's bases; the watts band = 2 x the larger of the
LOEO watts rms without twins over every point under 3 W, over this card's, and the card's replicate spread SD_rep (0.173 W, E209.md's), rounded up
to 0.01 W.
THE TIES (stated now): cycles and seconds 0.005 in ln, W over idle and joules 0.01 in ln, watts points 0.10 W.
THE HEAD-TO-HEADS (each an exact two-sided sign test over the cases or points whose two errors differ by more than the tie; a winner when p < 0.05
with at least 10 decided; TOO FEW under 10; NO DATA with none):
  H1t MM1-v3.1 vs MM1-v3, wall cycles an op, every registered point (the twins apart: H1t-twins);
  H1w MM1-v3.1 vs MM1-v3, W over idle given the measured op time, every registered point with energy;
  H2w 'v3.1 + gemmLnc term' vs MM1-v3.1 on family G, W over idle given t (= J over idle given t: H2j is the same test by arithmetic);
  H2f 'v3.1 + gemmLnc term' vs MM1-v3.1 on family G, J over idle with the seconds forecast;
  H3  'v3.1 + contention' vs MM1-v3.1 on family Y, wall cycles an op;
  H4  'v3.1 + both terms' vs MM1-v3.1 over every registered point: wall cycles at Y, W over idle given t at G, every other point a tie by
      construction (the two forecasters are equal there);
  P1  THE PAIR RULE on family Y: of the Y pairs whose measured within-pair difference |ln(wall_a / wall_b)| exceeds the session-repeat noise
      threshold 0.0077 (2 x 0.383%, the cycles session-repeat rms on this card, E208 a2c0-S1 against a2c0-S1r, 5d99fe17), the share that
      'v3.1 + contention' orders right (the sign of its predicted difference equals the measured sign); MM1-v3.1 predicts every pair equal (a tie:
      it orders none). PASS when at least 5 pairs are decided, more than half are ordered right, and the one-sided exact binomial p (k of m at
      1/2) <= 0.05; FAIL when decided >= 5 and that does not hold; TOO FEW under 5 decided pairs; NO DATA with none.
      AMENDED BEFORE ANY E216 DATUM (fix-e216, Q227, Thu 19 Nov 2026; E216-amendment-1.md A1, verify-e216's F1): the minimum was 4, and 4 of 4
      ordered right gives p 1/16 = 0.0625 > 0.05, so at exactly 4 decided the rule could only read FAIL, the word of 0 of 4; at 5, 5 of 5 gives
      p 0.031. 4 or fewer decided pairs now read TOO FEW. Nothing else of the rule changed.
POWER (REPORTED): each head-to-head simulated 2,000 days with every case's truth = one forecaster x exp(N(0, sigma)), sigma MM1-v3.1's held-out
rms (B1 of the rule's quantity): P(first BETTER | truth first), P(second BETTER | truth second), P(a winner | the midpoint).
POWER WITH ERRORS SHARED BY CONFIGURATION (REPORTED; fix-e216, E216-amendment-1.md A4, verify-e216's F4; never a rule): the same simulation with
every case's ln error shared by its distinct configuration (one N(0, sigma) draw a configuration a day; a configuration = the two forecasters'
frozen per-op values at 799.0 MHz, wall cycles an op for 'wall' and W over idle at their own seconds for 'Wg' and 'Jf', rounded to 6 decimals,
with the quantity), from a generator of its own (seed 20261120), so every registered simulation above draws exactly as before.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
CARD = "aifoundry2 card 0"
F = "799.0"
R215 = ("tools/claims-v3/e215/rules_e215.py", "5a44879ca9c4f0c7d8c4084f4dca93886fe6b18bfb1cf1a81bb76cc29d6f2272")
TIES = {"cycles_ln": 0.005, "seconds_ln": 0.005, "joules_ln": 0.01, "watts_W": 0.10}
PAIR_THRESHOLD_LN = 0.0077
PAIR_MIN = 5      # fix-e216 (A1, verify-e216's F1), before any datum: was 4, where 4 of 4 (p 0.0625) could only read FAIL
SIM_SHARED_SEED = 20261120   # fix-e216 (A4, verify-e216's F4): the shared-error simulation's own generator
TOO_FEW = 10
MIN_DECIDED = {"H1t": 10, "H1w": 10, "H1t-twins": 10, "H1w-twins": 10, "H2w": 8, "H2f": 8, "H3": 10, "H4": 10}   # family G holds 10 points
LOW = 3.0
SD_REP_W = 0.173
SIM = 2000


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def r215():
    p = os.path.join(REPO, R215[0])
    if sha(p) != R215[1]:
        print("rules_e216: REFUSED, E215's rules code is not at its pin")
        sys.exit(4)
    spec = importlib.util.spec_from_file_location("rules_e215", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, sha(p)


def load():
    P = json.load(open(os.path.join(HERE, "points-e216.json")))["points"]
    FC = json.load(open(os.path.join(HERE, "forecast-e216.json")))["points"]
    return P, FC


def val(FC, pid, model, q, f=F):
    x = FC[pid][f]["forecasts"][model]
    if q == "wall":
        return x["cycles_per_op_wall"]
    if q == "mean":
        return x["cycles_per_op_mean"]
    if q == "seconds":
        return x["seconds_per_gemm"]
    if q == "Wg":
        # W over idle given ONE measured op time: stand in by MM1-v3.1's own op time for both forecasters
        t = FC[pid][f]["forecasts"]["MM1-v3.1"]["T_op_us"]
        return x["A_W"] + x["B_W_us"] / t if x.get("A_W") is not None else None
    if q == "Jf":
        return x.get("J_over_idle_per_gemm")
    raise KeyError(q)


def h2h_sets(P, FC):
    """each head-to-head's (first, second) frozen values per scored case or point, the quantity and the tie"""
    reg = [p for p in P if p["family"] != "F" or p.get("subfamily") != "card-transfer twin"]
    twins = [p for p in P if p.get("subfamily") == "card-transfer twin"]
    G = [p for p in P if p["family"] == "G"]
    Y = [p for p in P if p["family"] == "Y"]

    def arr(pts, a, b, q):
        out = []
        for p in pts:
            x, y = val(FC, p["id"], a, q), val(FC, p["id"], b, q)
            if x is None or y is None:
                continue
            watts = q in ("Wg",) and x < LOW
            out.append((p["id"], x, y, watts))
        return out
    H = {
        "H1t": ("MM1-v3.1", "MM1-v3", "wall", "cycles_ln", arr(reg, "MM1-v3.1", "MM1-v3", "wall")),
        "H1t-twins": ("MM1-v3.1", "MM1-v3", "wall", "cycles_ln", arr(twins, "MM1-v3.1", "MM1-v3", "wall")),
        "H1w": ("MM1-v3.1", "MM1-v3", "Wg", "joules_ln", arr(reg, "MM1-v3.1", "MM1-v3", "Wg")),
        "H1w-twins": ("MM1-v3.1", "MM1-v3", "Wg", "joules_ln", arr(twins, "MM1-v3.1", "MM1-v3", "Wg")),
        "H2w": ("v3.1+lnc", "MM1-v3.1", "Wg", "joules_ln", arr(G, "v3.1+lnc", "MM1-v3.1", "Wg")),
        "H2f": ("v3.1+lnc", "MM1-v3.1", "Jf", "joules_ln", arr(G, "v3.1+lnc", "MM1-v3.1", "Jf")),
        "H3": ("v3.1+contention", "MM1-v3.1", "wall", "cycles_ln", arr(Y, "v3.1+contention", "MM1-v3.1", "wall")),
    }
    h4 = []
    for p in reg:
        if p["family"] == "Y":
            q, tk = "wall", "cycles_ln"
        elif p["family"] == "G":
            q, tk = "Wg", "joules_ln"
        else:
            q, tk = "wall", "cycles_ln"
        x, y = val(FC, p["id"], "v3.1+both", q), val(FC, p["id"], "MM1-v3.1", q)
        if x is None or y is None:
            continue
        h4.append((p["id"], x, y, False, tk))
    H["H4"] = ("v3.1+both", "MM1-v3.1", "mixed", "mixed", h4)
    return H


def sign_p(npos, nneg):
    n = npos + nneg
    if n == 0:
        return 1.0
    k = min(npos, nneg)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n)


def binom_one_sided(k, m):
    return sum(math.comb(m, i) for i in range(k, m + 1)) / 2 ** m


def power(rows, sigma, tiefor, rng, mind=TOO_FEW):
    """P(first BETTER | truth first), P(second BETTER | truth second), P(a winner | midpoint), by the registered sign test"""
    if not rows:
        return None
    a = np.array([r[1] for r in rows], float)
    b = np.array([r[2] for r in rows], float)
    tl = np.array([tiefor(r) for r in rows], float)
    out = {}
    for truth in ("first", "second", "mid"):
        base = a if truth == "first" else (b if truth == "second" else np.sqrt(a * b))
        w = [0, 0, 0]
        for _ in range(SIM):
            tr = base * np.exp(rng.normal(0.0, sigma, len(a)))
            d = np.abs(np.log(tr / b)) - np.abs(np.log(tr / a))
            npos, nneg = int(np.sum(d > tl)), int(np.sum(d < -tl))
            if npos + nneg < mind:
                w[2] += 1
                continue
            pv = sign_p(npos, nneg)
            if pv < 0.05:
                w[0 if npos > nneg else 1] += 1
            else:
                w[2] += 1
        out[truth] = {"P_first_BETTER": round(w[0] / SIM, 3), "P_second_BETTER": round(w[1] / SIM, 3), "P_undecided": round(w[2] / SIM, 3)}
    return out


def pair_power(P, FC, sigma, rng):
    """the pair rule simulated with truth = 'v3.1 + contention' and each run's ln error N(0, sigma) shared within a pair except a
    within-session part N(0, 0.0027) a run (the session-repeat rms 0.383% / sqrt 2): P(PASS), P(FAIL), P(TOO FEW)"""
    pairs = {}
    for p in P:
        if p["family"] == "Y":
            pairs.setdefault(p["pair"], []).append(p)
    rows = []
    for k, (a, b) in sorted(pairs.items()):
        ca, cb = val(FC, a["id"], "v3.1+contention", "wall"), val(FC, b["id"], "v3.1+contention", "wall")
        rows.append((k, math.log(ca / cb)))
    pred = np.array([r[1] for r in rows])
    out = {}
    for label, scale in (("truth = contention", 1.0), ("truth = contention x 3 (the layout effect E212 measured is larger)", 3.0),
                         ("truth = MM1-v3.1 (no layout effect)", 0.0)):
        w = {"PASS": 0, "FAIL": 0, "TOO FEW": 0}
        for _ in range(SIM):
            d = scale * pred + rng.normal(0.0, 0.0027 * math.sqrt(2), len(pred))
            dec = np.abs(d) > PAIR_THRESHOLD_LN
            m = int(dec.sum())
            k = int(np.sum(np.sign(d[dec]) == np.sign(pred[dec])))
            if m < PAIR_MIN:
                w["TOO FEW"] += 1
            elif k * 2 > m and binom_one_sided(k, m) <= 0.05:
                w["PASS"] += 1
            else:
                w["FAIL"] += 1
        out[label] = {k: round(v / SIM, 3) for k, v in w.items()}
    return {"pairs": [{"pair": k, "predicted_ln_a_over_b": round(v, 6), "over_threshold": abs(v) > PAIR_THRESHOLD_LN} for k, v in rows],
            "simulated": out}


def config_key(FC, pid, a, b, q, f=F):
    """fix-e216 (A4): a head-to-head case's DISTINCT CONFIGURATION: the two forecasters' frozen per-op values at 799.0 MHz (wall cycles an op for
    'wall'; W over idle at their own seconds for 'Wg' and 'Jf'), rounded to 6 decimals, with the quantity (verify-e216's F4 form)"""
    def per_op(m):
        x = FC[pid][f]["forecasts"][m]
        v = x["cycles_per_op_wall"] if q == "wall" else x.get("W_over_idle")
        return None if v is None else round(v, 6)
    return (per_op(a), per_op(b), q)


def power_shared(rows, keys, sigma, tiefor, rng, mind=TOO_FEW):
    """fix-e216 (A4, REPORTED): power() with every case's ln error SHARED by its distinct configuration (one N(0, sigma) draw a configuration a
    simulated day), by the registered sign test: P(first BETTER | truth first), P(second BETTER | truth second), P(a winner | the midpoint)"""
    if not rows:
        return None
    a = np.array([r[1] for r in rows], float)
    b = np.array([r[2] for r in rows], float)
    tl = np.array([tiefor(r) for r in rows], float)
    uk = sorted(set(keys), key=str)
    idx = np.array([uk.index(k) for k in keys])
    out = {}
    for truth in ("first", "second", "mid"):
        base = a if truth == "first" else (b if truth == "second" else np.sqrt(a * b))
        w = [0, 0, 0]
        for _ in range(SIM):
            tr = base * np.exp(rng.normal(0.0, sigma, len(uk))[idx])
            d = np.abs(np.log(tr / b)) - np.abs(np.log(tr / a))
            npos, nneg = int(np.sum(d > tl)), int(np.sum(d < -tl))
            if npos + nneg < mind:
                w[2] += 1
                continue
            pv = sign_p(npos, nneg)
            if pv < 0.05:
                w[0 if npos > nneg else 1] += 1
            else:
                w[2] += 1
        out[truth] = {"P_first_BETTER": round(w[0] / SIM, 3), "P_second_BETTER": round(w[1] / SIM, 3), "P_undecided": round(w[2] / SIM, 3)}
    return {"n_cases": len(rows), "n_configurations": len(uk), "sim": out}


def main():
    M, msha = r215()
    Trec, Erec, meta = M.heldout()
    valid = M.validate(Trec, Erec)
    B = M.bases(Trec, Erec, CARD)
    P, FC = load()
    reg = [p for p in P if p.get("subfamily") != "card-transfer twin"]
    ns = {"T": len(reg), "E": len(reg)}
    bands = {}
    for q in ("T1", "T2", "E1", "E2", "E3", "E4"):
        x1, x2 = B[q]["B1_LOEO_no_twin_all"]["rms_pct"], B[q]["B2_LOEO_no_twin_card"]["rms_pct"]
        basis = max(x1, x2) / 100.0
        band = M.ceil_pct(2 * basis)
        n = ns["T"] if q.startswith("T") else ns["E"]
        bands[q] = {"band": band, "basis": round(basis, 6), "B1": x1, "B2": x2, "n_B1": B[q]["B1_LOEO_no_twin_all"]["n"],
                    "n_B2": B[q]["B2_LOEO_no_twin_card"]["n"],
                    "arithmetic": f"2 x max({x1:.3f}, {x2:.3f}) = {2 * max(x1, x2):.2f} -> {round(100 * band)}%",
                    "P_PASS_at_1_1.25_1.5_x_basis": [M.p_pass(band, k * basis, n) for k in (1.0, 1.25, 1.5)], "n_scored": n,
                    "REPORTED": {k: v for k, v in B[q].items() if k.startswith("REPORTED")}}
    bands["T3"] = dict(bands["T1"], note="seconds: T1's bases (seconds = ops x the wall op time; MM1-v3.1's held-out record is on it)")
    wb = B["W"]
    wbasis = max(wb["all_under_3W_no_twin"]["rms_W"] or 0, wb["card_under_3W_no_twin"]["rms_W"] or 0, SD_REP_W)
    band_w = math.ceil(round(2 * wbasis * 100, 6)) / 100.0
    H = h2h_sets(P, FC)
    rng = np.random.default_rng(20261119)
    sig = {"wall": bands["T1"]["basis"], "Wg": bands["E1"]["basis"], "Jf": bands["E2"]["basis"]}
    gaps, pw = {}, {}
    for h, (a, b, q, tk, rows) in H.items():
        if h == "H4":
            tiefor = (lambda r: TIES[r[4]])
            d = [math.log(r[1] / r[2]) for r in rows]
            sigma = bands["T1"]["basis"]
        else:
            tiefor = (lambda r, tk=tk: TIES["watts_W"] if r[3] else TIES[tk])
            d = [math.log(r[1] / r[2]) for r in rows]
            sigma = sig[q]
        dec = sum(1 for r, x in zip(rows, d) if abs(x) > tiefor(r))
        gaps[h] = {"first": a, "second": b, "quantity": q, "n": len(rows), "rms_ln_first_over_second": round(float(np.sqrt(np.mean(np.square(d)))), 5) if d else None,
                   "max_abs_ln": round(max(abs(x) for x in d), 5) if d else None, "decidable_gap_over_tie": dec,
                   "over_2pct": sum(1 for x in d if abs(x) > 0.02)}
        if dec < MIN_DECIDED[h]:
            pw[h] = {"note": f"fewer than {MIN_DECIDED[h]} cases whose predicted gap exceeds the tie: the rule reads TOO FEW on every possible measurement",
                     "decidable": dec}
        else:
            pw[h] = {"sigma": sigma, "sim": power(rows, sigma, tiefor, rng, MIN_DECIDED[h]), "decidable": dec}
    pr = pair_power(P, FC, bands["T1"]["basis"], rng)
    # fix-e216 (A4, REPORTED): the same head-to-heads with errors shared by each distinct configuration, from a generator of its own
    rs = np.random.default_rng(SIM_SHARED_SEED)
    fam = {p["id"]: p["family"] for p in P}
    pws = {}
    for h, (a, b, q, tk, rows) in H.items():
        if "sim" not in pw[h]:
            pws[h] = {"note": pw[h]["note"], "decidable": pw[h]["decidable"]}
            continue
        if h == "H4":
            tiefor = (lambda r: TIES[r[4]])
            keys = [config_key(FC, r[0], a, b, "Wg" if fam[r[0]] == "G" else "wall") for r in rows]
        else:
            tiefor = (lambda r, tk=tk: TIES["watts_W"] if r[3] else TIES[tk])
            keys = [config_key(FC, r[0], a, b, q) for r in rows]
        pws[h] = dict(power_shared(rows, keys, pw[h]["sigma"], tiefor, rs, MIN_DECIDED[h]), sigma=pw[h]["sigma"], decidable=pw[h]["decidable"],
                      note="REPORTED (fix-e216, E216-amendment-1.md A4): errors shared by configuration; never a rule")
    out = {"experiment": "E216", "request": "Q227", "what": "every band, tie, threshold and test of E216, before any datum",
           "interpreter": "/usr/bin/python3 " + sys.version.split()[0], "numpy": np.__version__, "card": CARD, "forecast_clock_mhz": 799.0,
           "rules_e215_sha256": msha, "heldout_validation": valid, "bases": B, "bands": bands,
           "band_w": {"band_W": band_w, "basis_W": round(wbasis, 4), "all_under_3W_no_twin": wb["all_under_3W_no_twin"],
                      "card_under_3W_no_twin": wb["card_under_3W_no_twin"], "SD_rep_W": SD_REP_W,
                      "arithmetic": f"2 x max({wb['all_under_3W_no_twin']['rms_W']}, {wb['card_under_3W_no_twin']['rms_W']}, SD_rep {SD_REP_W}) = {2 * wbasis:.3f} -> {band_w:.2f} W"},
           "ties": TIES, "pass_fraction": 0.9, "too_few": TOO_FEW, "h2h_min_decided": MIN_DECIDED, "low_W": LOW, "test": "exact two-sided sign test, alpha 0.05",
           "pair_rule": {"threshold_ln": PAIR_THRESHOLD_LN, "min_decided": PAIR_MIN, "test": "one-sided exact binomial at 1/2, alpha 0.05",
                         "source": "2 x 0.383%: E208 a2c0-S1 vs its repeat a2c0-S1r on this card, cycles repeat-first rms (Q205, 5d99fe17)"},
           "predicted_gaps": gaps, "power_REPORTED": pw, "pair_power_REPORTED": pr, "power_shared_REPORTED": pws,
           "inputs_sha256": {"forecast-e216.json": sha(os.path.join(HERE, "forecast-e216.json")), "points-e216.json": sha(os.path.join(HERE, "points-e216.json")),
                             "tools/matmul/mm1/v3.1/out/holdout_v31.json": sha(os.path.join(REPO, "tools/matmul/mm1/v3.1/out/holdout_v31.json"))}}
    json.dump(out, open(os.path.join(HERE, "rules-e216.json"), "w"), indent=1, sort_keys=True, default=float)
    for q, bd in bands.items():
        print(f"{q}: band {round(100 * bd['band'])}% ({bd['arithmetic']}; n {bd['n_B1']}/{bd['n_B2']}); P(PASS) {bd['P_PASS_at_1_1.25_1.5_x_basis']}")
    print("watts:", out["band_w"]["arithmetic"])
    for h, g_ in gaps.items():
        print(h, json.dumps(g_), json.dumps(pw[h])[:400])
    print("pair rule:", json.dumps(pr)[:1500])
    for h, v in pws.items():
        print("shared by configuration (REPORTED):", h, json.dumps(v)[:400])


if __name__ == "__main__":
    main()
