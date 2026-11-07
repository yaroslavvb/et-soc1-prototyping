#!/usr/bin/env python3
"""Q153(m10acc), the fix pass: the figures that the data README's dated note 1
(docs/reports/data/2026-11-07-q153-m10acc/README.md.dated-note-1.md) quotes, computed from committed files only. Desk only, read only;
the Intel's /usr/bin/python3 (3.9.6, numpy 1.26.4, scipy 1.13.1).

    python3 -B tools/claims-v3/m10-acc/note1_m10acc.py run --out docs/reports/data/2026-11-07-q153-m10acc

It writes note1-m10acc.json and note1-m10acc.txt into --out and refuses to write over either. It imports the registered code unchanged:
fit_m10acc.py (ols0, loro, design, rule, boot_d_runs, boot_d_kinds, the seeds and draws) and P8-M1's paired form,
tools/claims-v3/p8-600/score_p8_600.py `paired()`, with pool8-registration.json's paired draws and seed rule. Its sections:

  anchors  the committed rows re-read: leave-one-run-out errors, frozen prices, the rule and F-P9 recomputed equal to the committed
           files, for the primary (M10-ACC) and A1 (M10-ACC-L), else it stops;
  N1       F-P9 (REGISTRATION.md section 6) read in P8-M1's verdict words, and P8-M1's own paired() on pool 8's rows (20,000 draws);
  N2       the entry rule's power: (a) the price that, added to the committed responses, makes R1 and then R1-R3 hold under the
           registered fit and bootstrap; (b) the chance R1-R3 hold at a true price, by an outer bootstrap over runs (1,000 resamples,
           each read by the registered 2,000-draw runs bootstrap); (c) the term's watts on the S class at the jackknife's upper end;
           (d) the chance P9-ACC reads BETTER / WORSE / NOT RESOLVED in P8-M1's form on a pool drawn like pool 8, at a true price;
  N3       the nesting: rows (a)'s responses equal M10's committed leave-one-kind-out errors (rows-m10.json err_w);
  N4       the frozen float term at E67's smallest, median and largest launch;
  N5       where term S's by-A-word table is (the registration's citation).

Every figure here is post hoc (computed after the registered fit, deciding nothing), except the anchors, which re-read committed
figures. SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse  # noqa: E402
import copy  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import platform  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
import scipy  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import fit_m10acc as FA  # noqa: E402

sys.path.insert(0, os.path.join(TOP, "tools", "claims-v3", "p8-600"))
import score_p8_600 as S8  # noqa: E402

DREL = "docs/reports/data/2026-11-07-q153-m10acc"
INPUTS = [
    f"{DREL}/rows-m10acc.json", f"{DREL}/rows-m10acc-a1.json", f"{DREL}/fit-m10acc.json", f"{DREL}/fit-m10acc-a1.json",
    f"{DREL}/m10acc.json", f"{DREL}/m10acc-a1.json", f"{DREL}/features-m10acc.json", f"{DREL}/features-m10acc-a1.json",
    f"{DREL}/README.md", "tools/claims-v3/m10-acc/REGISTRATION.md", "tools/claims-v3/m10-acc/REGISTRATION.md.dated-note-A1.md",
    "tools/claims-v3/m10-acc/fit_m10acc.py", "tools/claims-v3/p8-600/score_p8_600.py", "tools/claims-v3/m10/pool8-registration.json",
    "docs/reports/data/2026-11-04-q142m-m10/rows-m10.json", "docs/reports/data/2026-11-04-q142m-m10/README.md",
    "docs/reports/data/2026-11-06-q145b-m10-s/README.md.dated-note-1.md", "docs/reports/data/2026-11-06-q145b-m10-s/note2-checks.json",
    "tools/claims-v3/m10-s/REGISTRATION.md.dated-note-2.md", "tools/claims-v3/m10-c/REGISTRATION.md",
]
SEED_CHANCE, SEED_P9SIM = 1534, 1535       # this note's own seeds (the registration's are 1531-1533)
N_OUTER, N_POOLS, SIM_DRAWS = 1000, 1000, 2000
P8 = json.load(open(os.path.join(TOP, "tools", "claims-v3", "m10", "pool8-registration.json")))["scoring"]
P8_DRAWS = int(P8["paired_draws"])
P8_SEED = lambda rule: int(P8["seed_base"]) + sum(ord(ch) for ch in rule)  # noqa: E731
FORM_RULE = {"float": "P8-M1f", "int8": "P8-M1i"}   # the family's P8 paired rule, whose seed the one-off reading borrows
fsha = lambda p: hashlib.sha256(open(os.path.join(TOP, p), "rb").read()).hexdigest()  # noqa: E731
load = lambda p: json.load(open(os.path.join(TOP, p)))  # noqa: E731
rms = FA.rms
L = []


def say(s=""):
    L.append(s)
    print(s, flush=True)


def stop(msg):
    raise SystemExit("NOTE1 STOPPED: " + msg)


def word(lo, hi):
    """P8-M1's verdict words (predict_pool8_a2.paired_line; score_p8_600.paired)"""
    return "BETTER" if hi < 0 else ("WORSE" if lo > 0 else "NOT RESOLVED")


# ------------------------------------------------------------------ the two readings, as committed
def reading(name):
    if name == "primary":
        rows = load(f"{DREL}/rows-m10acc.json")
        fit, feats = load(f"{DREL}/fit-m10acc.json"), load(f"{DREL}/features-m10acc.json")
    else:
        rows = load(f"{DREL}/rows-m10acc-a1.json")["rows"]
        fit, feats = load(f"{DREL}/fit-m10acc-a1.json"), load(f"{DREL}/features-m10acc-a1.json")
    fam = {}
    for f, cols in (("float", ["acc", "bth"]), ("int8", ["acc"])):
        rr = [r for r in rows if r["fam"] == f]          # fit_m10acc.cmd_fit's order (assemble order, by family)
        Z = np.array([r["z"] for r in rr], float)
        e = np.array([r["e"] for r in rr], float)
        ep = np.array([r["e_prime"] for r in rr], float)
        if Z.shape[1] != len(cols):
            stop(f"{name} {f}: z has {Z.shape[1]} columns, not {len(cols)}")
        fam[f] = {"rr": rr, "Z": Z, "e": e, "ep": ep, "cols": cols, "src": np.array([r["src"] for r in rr]),
                  "card": np.array([r["card"] for r in rr]), "scl": np.array([bool(r.get("s_class")) for r in rr])}
    return {"rows": rows, "fit": fit, "feats": feats, "fam": fam}


def anchors(name, R):
    out = {}
    for f, q in R["fam"].items():
        rr, Z, e, ep = q["rr"], q["Z"], q["e"], q["ep"]
        com = R["fit"]["families"][f]
        tau = FA.ols0(Z, e)
        ep2, taus = FA.loro(rr, Z, e)
        ru = FA.rule(rr, e, ep, f)
        cr = com["rule"]
        dtau = max(abs(tau[j] - com["tau_J"][c]) for j, c in enumerate(q["cols"]))
        dep = float(np.max(np.abs(ep2 - ep)))
        drule = max(abs(ru["R1"][k] - cr["R1"][k]) for k in ("d_w", "lo95_w", "hi95_w"))
        fp9 = {}
        for c in ("a3", "c1"):
            for cls in ((False, True) if f == "float" else (False,)):
                m = (q["src"] == "b") & (q["card"] == c) & (q["scl"] if cls else True)
                key = f"pool8 class S {c}" if cls else f"pool8 {c}"
                lo, hi = FA.boot_d_kinds(e[m], ep[m], FA.SEED_FP9)
                cf = R["fit"]["forecasts_P9"][f][key]
                fp9[key] = max(abs(lo - cf["lo95_w"]), abs(hi - cf["hi95_w"]), abs((rms(ep[m]) - rms(e[m])) - cf["d_w"]))
        ok = dtau < 1e-27 and dep < 1e-12 and drule < 1e-12 and max(fp9.values()) < 1e-12 and ru["enters"] == cr["enters"]
        out[f] = {"n_rows": len(rr), "n_runs": len({r["run"] for r in rr}), "max_abs_diff_tau_J": float(dtau),
                  "max_abs_diff_loro_e_prime_w": dep, "max_abs_diff_rule_R1_w": float(drule), "max_abs_diff_fp9_w": fp9,
                  "enters": bool(ru["enters"]), "pass": bool(ok)}
        if not ok:
            stop(f"{name} {f}: the committed rows do not re-read as committed: {out[f]}")
    return out


# ------------------------------------------------------------------ N1: F-P9 in P8-M1's form
def n1(name, R):
    out = {}
    for f, q in R["fam"].items():
        e, ep = q["e"], q["ep"]
        for c in ("a3", "c1"):
            for cls in ((False, True) if f == "float" else (False,)):
                m = (q["src"] == "b") & (q["card"] == c) & (q["scl"] if cls else True)
                key = f"{f} pool8 class S {c}" if cls else f"{f} pool8 {c}"
                cf = R["fit"]["forecasts_P9"][f][key.split(" ", 1)[1]]
                ea = {i: float(v) for i, v in enumerate(ep[m])}
                eb = {i: float(v) for i, v in enumerate(e[m])}
                rule_id = FORM_RULE[f]
                p = S8.paired(ea, eb, list(range(int(m.sum()))), draws=P8_DRAWS, seed=P8_SEED(rule_id))
                out[key] = {"n": int(m.sum()), "d_w": cf["d_w"], "registered_interval_w": [cf["lo95_w"], cf["hi95_w"]],
                            "registered_interval": "fit_m10acc.boot_d_kinds, 2,000 draws, default_rng(1533) (REGISTRATION.md section 6)",
                            "verdict_in_P8M1_words": word(cf["lo95_w"], cf["hi95_w"]),
                            "P8M1_paired": {"verdict": p["verdict"], "d_w": p["d_rms"], "lo95_w": p["lo95"], "hi95_w": p["hi95"],
                                            "draws": p["draws"], "seed": p["seed"], "seed_of": rule_id},
                            "rms_M10_w": cf["rms_M10"], "rms_ACC_w": cf["rms_ACC"]}
        sb = R["fit"]["families"][f]["readings_heldout"].get("source b")
        out[f"{f} source b (both cards, held out by run)"] = {k: sb[k] for k in ("n", "rms_M10", "rms_ACC", "d", "bias_M10", "bias_ACC")}
    return out


# ------------------------------------------------------------------ N2: the rule's power
def d_of(e, ep):
    return rms(ep) - rms(e)


def detect(f, q, j, step_fj, tmax_fj):
    """the smallest injected price t (on a grid of step_fj) at which R1, and then R1-R3, hold; the leave-one-run-out errors e' do not
    change when t x z is added to e, since least squares is linear in the response (checked once in check_linear)"""
    rr, Z, e, ep = q["rr"], q["Z"], q["e"], q["ep"]
    cache = {}
    kmax = int(round(tmax_fj / step_fj))

    def ev(k):
        """the registered rule at the price k x step; None where d > -0.005 W (R1 cannot hold, so the rule does not enter)"""
        if k not in cache:
            t = k * step_fj * 1e-15
            ei = e + t * Z[:, j]
            if d_of(ei, ep) > -0.005:
                cache[k] = None
            else:
                ru = FA.rule(rr, ei, ep, f)
                row = {"t_fJ": round(k * step_fj, 6), "d_w": ru["R1"]["d_w"], "hi95_w": ru["R1"]["hi95_w"], "R1": ru["R1"]["holds"],
                       "R2": ru["R2"]["holds"], "d_a3_w": ru["R2"]["d_a3_w"], "d_c1_w": ru["R2"]["d_c1_w"], "enters": ru["enters"]}
                if "R3" in ru:
                    row.update({"R3": ru["R3"]["holds"], "d_S_w": ru["R3"]["d_S_w"]})
                cache[k] = row
        return cache[k]

    def first(sgn, key):
        """scan every 10th grid price, then the grid prices inside the first bracket where `key` turns true"""
        prev = 0
        for kc in range(10, kmax + 1, 10):
            r = ev(sgn * kc)
            if r and r[key]:
                for kk in range(prev + 1, kc + 1):
                    r2 = ev(sgn * kk)
                    if r2 and r2[key]:
                        return r2, kk
            prev = kc
        return None, None

    out = {}
    for sgn, lab in ((1, "positive"), (-1, "negative")):
        r1, _ = first(sgn, "R1")
        rin, kin = first(sgn, "enters")
        after = [ev(sgn * (kin + i)) for i in range(1, 6)] if kin else []
        mono = bool(rin) and all(x and x["enters"] for x in after)
        coarse_after = [cache[k] for k in sorted(cache, key=abs) if kin and k * sgn > kin and k % 10 == 0 and cache[k]]
        out[lab] = {"first_R1": r1, "first_enters": rin, "enters_at_the_5_grid_prices_after": mono,
                    "enters_at_every_coarse_price_read_after": bool(rin) and all(x["enters"] for x in coarse_after),
                    "grid_step_fJ": step_fj, "scanned_to_fJ": sgn * tmax_fj,
                    "read": [cache[k] for k in sorted(cache, key=lambda k: abs(k)) if k * sgn > 0 and cache[k]]}
    return out


def check_linear(f, q, j, t_fj):
    rr, Z, e, ep = q["rr"], q["Z"], q["e"], q["ep"]
    ep2, _ = FA.loro(rr, Z, e + t_fj * 1e-15 * Z[:, j])
    return float(np.max(np.abs(ep2 - ep)))


def chance(f, q, j, prices_fj, seed):
    """the chance R1, R2, R3 and the whole rule hold at a true price t: runs resampled with replacement (the outer draw, N_OUTER),
    each resample read by the registered rule (its runs bootstrap of NB draws over the resample's runs), on the run sums"""
    rr, Z, e, ep = q["rr"], q["Z"], q["e"], q["ep"]
    runs = sorted({r["run"] for r in rr})
    K = len(runs)
    pos = {R: i for i, R in enumerate(runs)}
    ri = np.array([pos[r["run"]] for r in rr])
    z = Z[:, j]

    def sums(mask):
        w = mask.astype(float)
        return tuple(np.bincount(ri, w * v, K) for v in (np.ones_like(e), e * e, e * z, z * z, ep * ep))
    S_all = sums(np.ones(len(rr), bool))
    S_a3, S_c1 = sums(q["card"] == "a3"), sums(q["card"] == "c1")
    S_S = sums(q["scl"]) if f == "float" else None

    def dval(W, S, t):
        n, a, b, c, p = S
        nn = W @ n
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.sqrt((W @ p) / nn) - np.sqrt((W @ (a + 2 * t * b + t * t * c)) / nn)
    # check: on the data as they are, the run sums give the registered rule's d and interval
    rng0 = np.random.default_rng(FA.SEED_RULE)
    W0 = np.zeros((FA.NB, K))
    for b_ in range(FA.NB):
        W0[b_] = np.bincount(rng0.integers(0, K, K), minlength=K)
    ds0 = dval(W0, S_all, 0.0)
    lo0, hi0 = float(np.percentile(ds0, 2.5)), float(np.percentile(ds0, 97.5))
    lo_r, hi_r = FA.boot_d_runs(rr, e, ep, FA.SEED_RULE)
    chk = {"d_w": float(dval(np.ones(K), S_all, 0.0)), "d_w_registered": d_of(e, ep), "lo95_w": lo0, "hi95_w": hi0,
           "lo95_w_registered": lo_r, "hi95_w_registered": hi_r}
    if abs(chk["d_w"] - chk["d_w_registered"]) > 1e-12 or abs(lo0 - lo_r) > 1e-12 or abs(hi0 - hi_r) > 1e-12:
        stop(f"the run sums do not reproduce the registered rule: {chk}")
    rng = np.random.default_rng(seed)
    cnt = {p: {"R1": 0, "R2": 0, "R3": 0, "enters": 0, "R3_unreadable": 0} for p in prices_fj}
    for _ in range(N_OUTER):
        outer = rng.integers(0, K, K)
        wo = np.bincount(outer, minlength=K).astype(float)
        inner = outer[rng.integers(0, K, (FA.NB, K))]
        W = np.bincount((inner + K * np.arange(FA.NB)[:, None]).ravel(), minlength=FA.NB * K).reshape(FA.NB, K).astype(float)
        for p in prices_fj:
            t = p * 1e-15
            d = float(dval(wo, S_all, t))
            hi = float(np.percentile(dval(W, S_all, t), 97.5))
            r1 = d <= -0.005 and hi < 0
            da3, dc1 = float(dval(wo, S_a3, t)), float(dval(wo, S_c1, t))
            r2 = bool(da3 < 0 and dc1 < 0)
            ok = r1 and r2
            if f == "float":
                dS = float(dval(wo, S_S, t))
                if np.isnan(dS):
                    cnt[p]["R3_unreadable"] += 1
                    r3 = False
                else:
                    r3 = dS <= 0
                cnt[p]["R3"] += int(r3)
                ok = ok and r3
            cnt[p]["R1"] += int(r1)
            cnt[p]["R2"] += int(r2)
            cnt[p]["enters"] += int(ok)
    res = {f"{p:+.3f} fJ": {k: v / N_OUTER for k, v in c.items()} for p, c in cnt.items()}
    return {"check_against_registered_rule": chk, "outer_resamples": N_OUTER, "inner_draws": FA.NB, "seed": seed, "by_price": res}


def p9_chances(f, q, prices_fj, rng):
    """the chance P9-ACC reads BETTER / WORSE / NOT RESOLVED in P8-M1's form on a pool drawn like pool 8: pools of pool 8's size
    drawn with replacement from its rows (M10's errors e + t x z_acc, M10-ACC's held-out errors e'), each read by the paired form
    (SIM_DRAWS draws, the form's order statistics)"""
    e, ep, Z = q["e"], q["ep"], q["Z"]
    lo_i, hi_i = int(0.025 * SIM_DRAWS), int(0.975 * SIM_DRAWS) - 1
    out = {}
    for c in ("a3", "c1"):
        for cls in ((False, True) if f == "float" else (False,)):
            m = (q["src"] == "b") & (q["card"] == c) & (q["scl"] if cls else True)
            key = f"{f} pool8 class S {c}" if cls else f"{f} pool8 {c}"
            n = int(m.sum())
            res = {}
            for p in prices_fj:
                a2 = ep[m] ** 2
                b2 = (e[m] + p * 1e-15 * Z[m, 0]) ** 2
                cnt = {"BETTER": 0, "WORSE": 0, "NOT RESOLVED": 0}
                for _ in range(N_POOLS):
                    pool = rng.integers(0, n, n)
                    inner = pool[rng.integers(0, n, (SIM_DRAWS, n))]
                    ds = np.sort(np.sqrt(a2[inner].mean(axis=1)) - np.sqrt(b2[inner].mean(axis=1)))
                    cnt[word(ds[lo_i], ds[hi_i])] += 1
                res[f"{p:+.3f} fJ"] = {k: v / N_POOLS for k, v in cnt.items()}
            out[key] = {"n": n, "by_price": res}
    return out


def s_shift(f, q, t_fj):
    """the term's watts at prices t (fJ, one per column) on the S class against the other whole tiles (rows with no zero tile)"""
    Z = q["Z"]
    w = Z @ (np.array(t_fj) * 1e-15)
    rr = q["rr"]
    whole = np.array([not r.get("zero_sha") for r in rr])
    b = q["src"] == "b"
    S = q["scl"]
    sets = {"S class (42)": S, "other whole float tiles": whole & ~S, "pool 8 class S (16)": S & b, "pool 8 other float tiles (34)": b & ~S}
    out = {k: {"n": int(v.sum()), "mean_w": float(w[v].mean()), "max_w": float(w[v].max())} for k, v in sets.items()}
    out["S class minus other whole tiles, mean_w"] = out["S class (42)"]["mean_w"] - out["other whole float tiles"]["mean_w"]
    out["pool 8 class S minus pool 8 other, mean_w"] = out["pool 8 class S (16)"]["mean_w"] - out["pool 8 other float tiles (34)"]["mean_w"]
    for c in ("a3", "c1"):
        mS, mO = S & b & (q["card"] == c), b & ~S & (q["card"] == c)
        out[f"pool 8 class S minus pool 8 other, {c}, mean_w"] = float(w[mS].mean() - w[mO].mean())
    return out


def n2(name, R):
    out = {"detectable_price": {}, "linearity_check_max_abs_w": {}, "chance": {}, "class_S_shift_at_interval_end": {}, "P9_chances": {}}
    m10acc = R["fit"]["families"]
    steps = {("float", 0): (0.1, 40.0), ("float", 1): (0.01, 4.0), ("int8", 0): (0.1, 40.0)}
    for (f, j), (step, tmax) in steps.items():
        q = R["fam"][f]
        col = q["cols"][j]
        key = f"{f} tau_{col}"
        out["linearity_check_max_abs_w"][key] = check_linear(f, q, j, 6.0 if j == 0 else 0.5)
        out["detectable_price"][key] = detect(f, q, j, step, tmax)
        say(f"  {name} {key}: R1 first holds at +{(out['detectable_price'][key]['positive']['first_R1'] or {}).get('t_fJ')} / "
            f"{(out['detectable_price'][key]['negative']['first_R1'] or {}).get('t_fJ')} fJ; enters at "
            f"+{(out['detectable_price'][key]['positive']['first_enters'] or {}).get('t_fJ')} / "
            f"{(out['detectable_price'][key]['negative']['first_enters'] or {}).get('t_fJ')} fJ")
    # chance by the outer runs bootstrap, at prices around the detectable one and at the jackknife's upper end
    for (f, j) in steps:
        q = R["fam"][f]
        col = q["cols"][j]
        key = f"{f} tau_{col}"
        jk = m10acc[f]["jackknife"][col]
        dp = out["detectable_price"][key]
        det = (dp["positive"]["first_enters"] or dp["positive"]["first_R1"] or {}).get("t_fJ")
        neg = (dp["negative"]["first_enters"] or {}).get("t_fJ")
        prices = sorted({0.0, round(jk["lo95_J"] * 1e15, 3), round(jk["hi95_J"] * 1e15, 3)}
                        | ({round(det * x, 3) for x in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0)} if det else set()) | ({neg} if neg else set()))
        out["chance"][key] = chance(f, q, j, prices, SEED_CHANCE)
        out["chance"][key]["jackknife_95_fJ"] = [jk["lo95_J"] * 1e15, jk["hi95_J"] * 1e15]
    # the S class at the interval's upper end
    qf = R["fam"]["float"]
    jk = m10acc["float"]["jackknife"]
    hi_acc, hi_bth = jk["acc"]["hi95_J"] * 1e15, jk["bth"]["hi95_J"] * 1e15
    out["class_S_shift_at_interval_end"] = {
        "prices_fJ": {"acc_hi": hi_acc, "bth_hi": hi_bth},
        "acc at its upper end": s_shift("float", qf, [hi_acc, 0.0]),
        "bth at its upper end": s_shift("float", qf, [0.0, hi_bth]),
        "both at their upper ends": s_shift("float", qf, [hi_acc, hi_bth]),
        "M10 bias on the S class (42), held out": m10acc["float"]["readings_heldout"]["S class"]["bias_M10"],
        "M10 bias on pool 8's class S (posthoc.pool8_class_S)": {c: R["fit"]["posthoc"]["pool8_class_S"][c]["e_M10"]["bias"] for c in ("a3", "c1")}}
    # P9-ACC's chances at a true price
    rng = np.random.default_rng(SEED_P9SIM)
    for f in ("float", "int8"):
        q = R["fam"][f]
        jk = m10acc[f]["jackknife"]["acc"]
        det = (out["detectable_price"][f"{f} tau_acc"]["positive"]["first_enters"] or {}).get("t_fJ")
        prices = [0.0, round(jk["hi95_J"] * 1e15, 3)] + ([det] if det else [])
        out["P9_chances"][f] = p9_chances(f, q, prices, rng)
    out["P9_chances"]["_form"] = (f"pools of pool 8's size drawn with replacement from its rows ({N_POOLS} pools), each read by P8-M1's paired "
                                  f"form at {SIM_DRAWS} draws with its order statistics; M10's errors e + t x z_acc, M10-ACC's held-out errors e' "
                                  f"(unchanged by t); default_rng({SEED_P9SIM})")
    return out


# ------------------------------------------------------------------ N3: the nesting
def n3(R):
    r10 = load("docs/reports/data/2026-11-04-q142m-m10/rows-m10.json")
    m = {(x["exp"], x["card"], x["key"]): x for x in r10}
    n = eq = 0
    worst = 0.0
    for r in R["rows"]:
        if r["src"] != "a":
            continue
        x = m[(r["exp"], r["card"], r["key"])]
        v = x["err_w"]["B+a+b" if r["fam"] == "float" else "B"]
        n += 1
        eq += int(float(v) == r["e"])
        worst = max(worst, abs(float(v) - r["e"]))
    readme = open(os.path.join(TOP, "docs/reports/data/2026-11-04-q142m-m10/README.md"), encoding="utf-8").read().splitlines()
    line25 = next((i + 1 for i, s in enumerate(readme) if "leave one kind out" in s), None)
    return {"rows_a": n, "equal_to_rows_m10_err_w": eq, "max_abs_diff_w": worst,
            "m10_readme_line_saying_leave_one_kind_out": line25,
            "fit_m10acc_assemble_takes_err_w_as_given": True}


# ------------------------------------------------------------------ N4: E67's launch size
def n4(name, R):
    q = R["fam"]["float"]
    rr, e = q["rr"], q["e"]
    ls = R["feats"]["launch_sizes"]
    b = ls["E67"]["by_type"]["fp32"]
    out = {"E67_fp32_launch": {"min": b["min"], "median_N": b["N"], "max": b["max"]}}
    for lab, n in (("min", b["min"]), ("median", b["N"]), ("max", b["max"])):
        ls2 = copy.deepcopy(ls)
        ls2["E67"]["by_type"]["fp32"]["N"] = n
        Zn, _ = FA.design(rr, R["feats"]["tiles"], ls2, q["cols"])
        if lab == "median" and float(np.max(np.abs(Zn - q["Z"]) / np.maximum(np.abs(q["Z"]), 1.0))) > 1e-12:
            stop(f"{name}: the design at E67's median N is not the committed z")
        tau = FA.ols0(Zn, e)
        epn, _ = FA.loro(rr, Zn, e)
        ru = FA.rule(rr, e, epn, "float")
        out[lab] = {"N": n, "tau_acc_fJ": float(tau[0]) * 1e15, "tau_bth_fJ": float(tau[1]) * 1e15, "d_w": ru["R1"]["d_w"],
                    "hi95_w": ru["R1"]["hi95_w"], "d_S_w": ru["R3"]["d_S_w"], "enters": ru["enters"]}
    return out


# ------------------------------------------------------------------ N5: the citation
def n5():
    a = "docs/reports/data/2026-11-06-q145b-m10-s/README.md.dated-note-1.md"
    b = "tools/claims-v3/m10-s/REGISTRATION.md.dated-note-2.md"
    ta = open(os.path.join(TOP, a), encoding="utf-8").read()
    tb = open(os.path.join(TOP, b), encoding="utf-8").read()
    sec_a = next((s for s in ta.split("\n## ") if s.startswith("2. ")), "")
    sec_b = next((s for s in tb.split("\n## ") if s.startswith("2. ")), "")
    nc = load("docs/reports/data/2026-11-06-q145b-m10-s/note2-checks.json")["by_list_and_A_99"]["by_A"]
    return {"table_file": a, "table_file_section_2_heading": sec_a.splitlines()[0] if sec_a else None,
            "table_file_section_2_holds_0438_0066": bool("0.438" in sec_a and "0.066" in sec_a and "by_list_and_A_99" in sec_a),
            "note2_checks_by_list_and_A_99_by_A": {k: {"n": v["n"], "bias_w": v["bias_w"]} for k, v in nc.items()},
            "cited_file": b, "cited_file_section_2_heading": sec_b.splitlines()[0] if sec_b else None,
            "cited_file_holds_0438": bool("0.438" in tb)}


# ------------------------------------------------------------------ run
def cmd_run(a):
    out_dir = os.path.abspath(a.out)
    pj, pt = os.path.join(out_dir, "note1-m10acc.json"), os.path.join(out_dir, "note1-m10acc.txt")
    for p in (pj, pt):
        if os.path.exists(p):
            stop(f"{os.path.relpath(p, TOP)} exists; this program never writes over a file")
    t0 = time.time()
    res = {"_what": ("Q153(m10acc) fix: the figures of docs/reports/data/2026-11-07-q153-m10acc/README.md.dated-note-1.md, from committed "
                     "files (tools/claims-v3/m10-acc/note1_m10acc.py). Post hoc, deciding nothing; the anchors re-read committed figures."),
           "interpreter": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
           "inputs_sha256": {p: fsha(p) for p in INPUTS},
           "P8M1_form": {"paired_draws": P8_DRAWS, "seed_rule": P8["seed_rule"], "verdict_form": "BETTER if its upper end < 0, WORSE if its lower "
                         "end > 0, else NOT RESOLVED (predict_pool8_a2.paired_line; score_p8_600.paired)"},
           "anchors": {}, "N1": {}, "N2": {}, "N4": {}}
    say("Q153(m10acc) fix, dated note 1's figures (note1_m10acc.py). Post hoc unless marked; W are measured - predicted.")
    for name in ("primary", "A1"):
        R = reading(name)
        res["anchors"][name] = anchors(name, R)
        say(f"anchors {name}: " + "; ".join(f"{f} {v['n_rows']} rows in {v['n_runs']} runs, re-read equal" for f, v in res["anchors"][name].items()))
        res["N1"][name] = n1(name, R)
        say(f"N1 {name}: F-P9 in P8-M1's words (registered interval) | P8-M1's paired(), {P8_DRAWS} draws")
        for k, v in res["N1"][name].items():
            if "registered_interval_w" in v:
                p = v["P8M1_paired"]
                say(f"  {k:26s} n {v['n']:2d}  d {v['d_w']:+.4f} [{v['registered_interval_w'][0]:+.4f}, {v['registered_interval_w'][1]:+.4f}] "
                    f"{v['verdict_in_P8M1_words']:12s} | [{p['lo95_w']:+.4f}, {p['hi95_w']:+.4f}] {p['verdict']} (seed {p['seed']})")
            else:
                say(f"  {k}: n {v['n']}, M10 {v['rms_M10']:.4f} -> {v['rms_ACC']:.4f}, d {v['d']:+.4f}")
        say(f"N2 {name}: the rule's power")
        res["N2"][name] = n2(name, R)
        for key, v in res["N2"][name]["chance"].items():
            say(f"  {name} {key}: chance by an outer runs bootstrap (jackknife 95% [{v['jackknife_95_fJ'][0]:+.3f}, {v['jackknife_95_fJ'][1]:+.3f}] fJ):")
            for p, c in v["by_price"].items():
                say(f"    t {p}: R1 {c['R1']:.3f}, R2 {c['R2']:.3f}" + (f", R3 {c['R3']:.3f}" if key.startswith("float") else "")
                    + f", enters {c['enters']:.3f}")
        cs = res["N2"][name]["class_S_shift_at_interval_end"]
        for lab in ("acc at its upper end", "bth at its upper end", "both at their upper ends"):
            v = cs[lab]
            say(f"  {name} S-class shift, {lab}: S {v['S class (42)']['mean_w']:+.4f} W (max {v['S class (42)']['max_w']:+.4f}), other whole "
                f"{v['other whole float tiles']['mean_w']:+.4f} W, difference {v['S class minus other whole tiles, mean_w']:+.4f} W; pool 8 S minus "
                f"other {v['pool 8 class S minus pool 8 other, mean_w']:+.4f} W")
        for f in ("float", "int8"):
            for k, v in res["N2"][name]["P9_chances"][f].items():
                say(f"  {name} P9 {k:24s} n {v['n']:2d}: " + "; ".join(
                    f"t {p}: B {c['BETTER']:.3f} W {c['WORSE']:.3f} NR {c['NOT RESOLVED']:.3f}" for p, c in v["by_price"].items()))
        res["N4"][name] = n4(name, R)
        say(f"N4 {name}: E67 at " + "; ".join(f"{lab} N {v['N']}: tau_acc {v['tau_acc_fJ']:+.4f} fJ, tau_bth {v['tau_bth_fJ']:+.4f} fJ, d {v['d_w']:+.4f}, "
                                            f"enters {v['enters']}" for lab, v in res["N4"][name].items() if lab != "E67_fp32_launch"))
        if name == "primary":
            res["N3"] = n3(R)
            say(f"N3: rows (a) {res['N3']['rows_a']}, equal to rows-m10.json err_w {res['N3']['equal_to_rows_m10_err_w']} "
                f"(max diff {res['N3']['max_abs_diff_w']:.1e} W); M10 README line {res['N3']['m10_readme_line_saying_leave_one_kind_out']}")
    res["N5"] = n5()
    v5 = res["N5"]
    say(f"N5: the by-A-word table is in {v5['table_file']}, {v5['table_file_section_2_heading'][:60]}... (holds it: "
        f"{v5['table_file_section_2_holds_0438_0066']}); the cited {v5['cited_file']} section 2 is "
        f"{v5['cited_file_section_2_heading'][:50]}... (holds -0.438: {v5['cited_file_holds_0438']})")
    os.makedirs(out_dir, exist_ok=True)
    json.dump(res, open(pj, "w"), indent=1, sort_keys=True, default=float)
    open(pt, "w").write("\n".join(L) + "\n")
    print(f"wrote {os.path.relpath(pj, TOP)} and {os.path.relpath(pt, TOP)} in {time.time() - t0:.1f} s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run",))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cmd_run(a)


if __name__ == "__main__":
    main()
