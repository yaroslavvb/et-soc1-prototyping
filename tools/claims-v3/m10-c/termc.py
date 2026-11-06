#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q148(c): M10's constant-lane term, exactly as tools/claims-v3/m10-c/REGISTRATION.md (committed c71fbc7f before this file existed)
registers it: a level per float format and lane-word class (one word in every lane, or eight lane words) for the float tiles that pass
T_S as a zero, fitted leave one run out on committed rows only (M10's own T_S-zero rows and the built-in pi tie), with its uncertainty,
the frozen forecasts for E178's 27 float one-number kinds (a REPORTED arm, never one of E178's rules), the entry rule's power, the post
hoc readings, and the arm's scorer.

    python3 -B termc.py selftest [--txt <file>]          # registration section 9 step 2's checks; prints no residual
    python3 -B termc.py fit --out <dir>                  # the rows, the fit, the held-out errors, the forecasts, the power, post hoc
    python3 -B termc.py score --scored <E178 scored.json> --fit <dir>/termc-fit.json [--out <json>]
                                                         # registration sections 5-6, after E178's data

Standard library and numpy 1.26. One core. Nothing here writes outside --out / --txt.
SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import struct  # noqa: E402
import sys  # noqa: E402
from collections import defaultdict  # noqa: E402

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CV = os.path.join(TOP, "tools", "claims-v3")
DD = os.path.join(TOP, "docs", "reports", "data")
M10D = os.path.join(DD, "2026-11-04-q142m-m10")
E178D = os.path.join(CV, "e178")
B8 = os.path.join(CV, "kinds", "blind8")
for _p in (os.path.join(CV, "m10-s"), M10D):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import term_s as TS  # noqa: E402  (t_s, the byte test, unchanged; and through it fit_m10)
import predict_m10 as PM  # noqa: E402  (d600 and session_scale, unchanged)

FM = TS.FM
FLOATS = ("fp32", "fp16")
CARDS = ("a3", "c1")
CD = {"aifoundry3": "a3", "aifoundry1c1": "c1", "aifoundry1-c1": "c1"}
POOL8 = {"E171": ("a3", os.path.join(DD, "2026-11-05-e171-blind8-aifoundry3")),
         "E172": ("c1", os.path.join(DD, "2026-11-05-e172-blind8-card1"))}
SEED_BOOT, SEED_C1, SEED_POWER, NB = 1481, 1782, 1783, 2000
PI_WORD = 0x40490FDB
load = lambda p: json.load(open(p))  # noqa: E731
sha_b = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
fsha = lambda p: sha_b(open(p, "rb").read())  # noqa: E731
REL = lambda p: os.path.relpath(p, TOP)  # noqa: E731


def stop(msg):
    raise SystemExit("TERM C STOPPED: " + msg)


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def rms(v):
    v = [x for x in v if x is not None]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


# ------------------------------------------------------------------ Student t (exact, no scipy)
def _betacf(a, b, x):
    qab, qap, qam, c, d = a + b, a + 1.0, a - 1.0, 1.0, 1.0 - (a + b) * x / (a + 1.0)
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(c) > 1e-300 else 1e300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(c) > 1e-300 else 1e300
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-15:
            break
    return h


def _ibeta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_cdf(t, df):
    p = 0.5 * _ibeta(df / 2.0, 0.5, df / (df + t * t))
    return 1 - p if t > 0 else p


def t_ppf(q, df):
    lo, hi = 0.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_cdf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ------------------------------------------------------------------ the structure (registration section 2)
def classify(raw, fmt):
    """('zero', 'one'|'eight') for T_S zeros, ('bit', 'one'|'eight') for T_S single bits, ('zeros', None) for the all-zero tile,
    (None, None) otherwise"""
    s = TS.t_s(raw, fmt)
    if s is None:
        return None, None, None
    w = "one" if s["one_base"] else "eight"
    if s.get("zero"):
        if s["a_word"] == 0 and all(u == 0 for u in s["bases"]):
            return "zeros", None, s
        return "zero", w, s
    return "bit", w, s


# ------------------------------------------------------------------ the rows (registration section 3)
class Inputs:
    def __init__(self):
        self.m10 = PM.load_m10(os.path.join(M10D, "m10.json"))
        self.rows, _ = FM.assemble()
        self.by = {(r["exp"], r["key"]): r for r in self.rows}
        self.m10rows = load(os.path.join(M10D, "rows-m10.json"))
        zeros, zr = FM.M7.zeros_counts(), FM.M9.zeros_rows()
        self.anchors, _ = FM.assemble_anchors(self.rows, zeros, zr)
        self.c1 = self.m10["families"]["float"]["card1_scale"]
        self.sst = self.m10["families"]["float"]["session_scales_training"]
        self._s = {}

    def s_of(self, sess, card):
        """the session's float scale by M10's rule, exact (m10.json's session_scales_training holds it to 5 decimals)"""
        if sess not in self._s:
            self._s[sess] = PM.session_scale(self.anchors.get(sess, []), "float", card, self.m10)
        return self._s[sess]

    def cterm(self, card):
        return self.c1 if card == "c1" else 1.0


def m10_classed(I):
    """every float row of rows-m10.json with its T_S class, kind (sha256), e = err_w['B+a+b'], s, c, rate"""
    out = []
    for r in I.m10rows:
        a = I.by[(r["exp"], r["key"])]
        if a["type"] not in FLOATS:
            continue
        p = os.path.join(TOP, a["tile_path"]) if a.get("tile_path") else None
        raw = open(p, "rb").read() if p and os.path.exists(p) else None
        st, w, s = classify(raw, a["type"]) if raw else (None, None, None)
        if a.get("rate") is None:
            stop(f"{r['exp']}:{r['key']} has no measured rate")
        sess = f"{r['exp']}|{r['card']}"
        out.append({"src": "m10-row", "exp": r["exp"], "card": r["card"], "run": sess, "key": r["key"], "fmt": a["type"],
                    "struct": st, "cls": w, "kind": sha_b(raw) if raw else None, "tile": a.get("tile_path"),
                    "a_word": f"{s['a_word']:08x}" if s else None, "bit": (s or {}).get("bit"),
                    "D": r["D"], "e": r["err_w"]["B+a+b"], "e_insample": r["D"] - r["M10_insample_pred_w"],
                    "rate": float(a["rate"]), "s": I.s_of(sess, r["card"]), "c": I.cterm(r["card"])})
    return out


def f_pi(I):
    pis = [r for r in I.rows if r["key"] == "fp32.pi"]
    if not pis or any(r["f"] != pis[0]["f"] for r in pis):
        stop("fp32.pi's committed rows do not share one feature set")
    return pis[0]["f"], pis[0]["tile_sha256"]


def tie_rows(I):
    """the built-in pi tie in every committed session on M10's footing (registration 3.1 (b))"""
    f, kind = f_pi(I)
    out, absent = [], []
    sessions = sorted({f"{r['exp']}|{r['card']}" for r in I.m10rows}, key=lambda x: int(x.split("|")[0][1:]))
    for sess in sessions:
        exp, card = sess.split("|")
        items = FM.footing_items(exp)
        tie = (items or {}).get("anchor_pi")
        if not tie or not isinstance(tie.get("D"), dict) or tie["D"].get("mean") is None:
            absent.append(sess)
            continue
        out.append(_tie(exp, card, sess, tie, I.s_of(sess, card), I, f, kind,
                        REL(os.path.join(DD, "2026-11-03-q139u-footing", "reduced", f"{exp.lower()}-footing.json"))
                        if exp not in FM.FOOTING else REL(FM.FOOTING[exp])))
    for exp, (card, d) in POOL8.items():
        red = load(os.path.join(d, f"{exp.lower()}.json"))
        sc = load(os.path.join(d, "scored.json"))["primary"]["scale"]["s_float"]
        out.append(_tie(exp, card, f"{exp}|{card}", red["items"]["anchor_pi"], float(sc), I, f, kind,
                        REL(os.path.join(d, f"{exp.lower()}.json"))))
    return out, absent


def _tie(exp, card, sess, tie, s, I, f, kind, src):
    rate = tie["rate"]["mean"] if isinstance(tie["rate"], dict) else tie["rate"]
    pred = PM.d600(f, "fp32", float(rate), card, I.m10, s)
    D = float(tie["D"]["mean"])
    return {"src": "tie", "exp": exp, "card": card, "run": sess, "key": "anchor_pi", "fmt": "fp32", "struct": "zero", "cls": "one",
            "kind": kind, "tile": "built-in --values pi (0x40490FDB)", "a_word": f"{PI_WORD:08x}", "bit": None, "D": D,
            "D_se": tie["D"].get("se"), "n_passes": tie["D"].get("n"), "e": D - pred, "rate": float(rate), "s": s, "c": I.cterm(card),
            "reduction": src}


def add_rho(rows):
    for r in rows:
        r["rho_J"] = r["e"] / (r["s"] * r["c"] * r["rate"])
    return rows


# ------------------------------------------------------------------ the estimator (registration section 4)
def level(rows, weighting="kind"):
    if not rows:
        return None
    if weighting == "row":
        return mean([r["rho_J"] for r in rows])
    by = defaultdict(list)
    for r in rows:
        by[r["kind"]].append(r["rho_J"])
    return mean([mean(v) for v in by.values()])


def levels(rows, weighting="kind"):
    out = {}
    for fmt in FLOATS:
        one = level([r for r in rows if r["fmt"] == fmt and r["cls"] == "one"], weighting)
        eight = level([r for r in rows if r["fmt"] == fmt and r["cls"] == "eight"], weighting)
        out[fmt] = {"one": one, "eight": eight if eight is not None else one, "eight_fitted": eight is not None}
    return out


def loro(rows, weighting="kind"):
    """each run held out in turn: lambda from the other runs' rows, e' for the run's rows; returns {run: levels}, rows get e_prime"""
    folds = {}
    for R in sorted({r["run"] for r in rows}):
        lv = levels([r for r in rows if r["run"] != R], weighting)
        folds[R] = lv
        for r in rows:
            if r["run"] == R:
                lam = lv[r["fmt"]][r["cls"]]
                r["lam_heldout_J"] = lam
                r["e_prime"] = None if lam is None else r["e"] - r["s"] * r["c"] * r["rate"] * lam
    return folds


def jackknife(rows, folds, full, fmt):
    runs = sorted({r["run"] for r in rows if r["fmt"] == fmt and r["cls"] == "one"})
    J = [folds[R][fmt]["one"] for R in runs if folds[R][fmt]["one"] is not None]
    n = len(J)
    if n < 2:
        return {"n_runs": n}
    mj = sum(J) / n
    se = math.sqrt((n - 1) / n * sum((x - mj) ** 2 for x in J))
    t = t_ppf(0.975, n - 1)
    lam = full[fmt]["one"]
    return {"n_runs": n, "se_J": se, "t": t, "lo95_J": lam - t * se, "hi95_J": lam + t * se, "loro_values_J": dict(zip(runs, J))}


def boot_runs(rows, fmt, weighting, seed=SEED_BOOT, nb=NB):
    rng = random.Random(seed)
    runs = sorted({r["run"] for r in rows if r["fmt"] == fmt and r["cls"] == "one"})
    byrun = defaultdict(list)
    for r in rows:
        if r["fmt"] == fmt and r["cls"] == "one":
            byrun[r["run"]].append(r)
    vals = []
    for _ in range(nb):
        pick = [rng.choice(runs) for _ in runs]
        vals.append(level([r for R in pick for r in byrun[R]], weighting))
    vals.sort()
    return {"lo95_J": vals[int(0.025 * nb)], "hi95_J": vals[int(0.975 * nb) - 1], "draws": nb, "seed": seed}


def sigma_c(rows, fmt):
    by = defaultdict(list)
    for r in rows:
        if r["fmt"] == fmt and r["cls"] == "one" and r.get("e_prime") is not None:
            by[r["kind"]].append(r["e_prime"] ** 2)
    return math.sqrt(mean([mean(v) for v in by.values()])) if by else None


def summary(rows, key="e_prime"):
    """rms and bias of e and of e' (W), row-weighted and kind-weighted"""
    if not rows:
        return {"n_rows": 0, "n_kinds": 0, "n_runs": 0}
    v0 = [r["e"] for r in rows]
    v1 = [r.get(key) for r in rows]
    by0, by1 = defaultdict(list), defaultdict(list)
    for r in rows:
        by0[r["kind"]].append(r["e"])
        by1[r["kind"]].append(r.get(key))
    kw = lambda by: (math.sqrt(mean([mean([x * x for x in v]) for v in by.values()])), mean([mean(v) for v in by.values()]))  # noqa: E731
    k0, k1 = kw(by0), kw(by1) if all(x is not None for x in v1) else (None, None)
    return {"n_rows": len(rows), "n_kinds": len(by0), "n_runs": len({r["run"] for r in rows}),
            "M10": {"rms_w": rms(v0), "bias_w": mean(v0), "kind_rms_w": k0[0], "kind_bias_w": k0[1]},
            "M10_C": {"rms_w": rms(v1), "bias_w": mean(v1), "kind_rms_w": k1[0], "kind_bias_w": k1[1]}}


# ------------------------------------------------------------------ E178's forecasts (registration section 5)
def e178_float_kinds():
    fc = load(os.path.join(E178D, "forecast-e178.json"))
    ke = {k["key"]: k for k in load(os.path.join(E178D, "kinds-e178.json"))["kinds"]}
    out = {}
    for k, v in sorted(fc["kinds"].items()):
        if v["type"] not in FLOATS:
            continue
        p = os.path.join(E178D, "tiles", v["type"], v["name"] + ".bin")
        raw = open(p, "rb").read()
        if sha_b(raw) != ke[k]["sha256"]:
            stop(f"{k}: the tile does not hash as kinds-e178.json says")
        st, w, s = classify(raw, v["type"])
        out[k] = {"fmt": v["type"], "P_w": v["P_w"], "a_word": v["a_word"], "b_word": v["b_word"], "role": v.get("role"),
                  "struct": st, "cls": w, "m10_features": v["m10_features"], "tile": REL(p), "sha256": ke[k]["sha256"]}
    return fc, out


def forecasts(fc, kinds, lv_primary, iv, sig, lv_card, lv_row):
    out = {}
    for k, v in kinds.items():
        fmt, rate = v["fmt"], fc["rate"][v["fmt"]]
        cards = {}
        for cd in CARDS:
            c = 1.0 if cd == "a3" else lv_primary["_c1"]
            L = c * rate * lv_primary[fmt]["one"]
            Lc = c * rate * lv_card[cd][fmt]["one"]
            Lr = c * rate * lv_row[fmt]["one"]
            P = v["P_w"][cd]
            cards[cd] = {"P_w": P, "L_w": L, "forecast_w": P + L,
                         "level_95_w": [c * rate * iv[fmt]["lo95_J"], c * rate * iv[fmt]["hi95_J"]],
                         "forecast_level_95_w": [P + c * rate * iv[fmt]["lo95_J"], P + c * rate * iv[fmt]["hi95_J"]],
                         "forecast_predictive_95_w": [P + L - 1.96 * sig[fmt], P + L + 1.96 * sig[fmt]],
                         "arm_K_card": {"L_w": Lc, "forecast_w": P + Lc}, "arm_R": {"L_w": Lr, "forecast_w": P + Lr}}
        out[k] = {"fmt": fmt, "a_word": v["a_word"], "b_word": v["b_word"], "role": v["role"], "class": f"{v['struct']}, {v['cls']} word",
                  "rate_per_s": rate, "cards": cards}
    return out


# ------------------------------------------------------------------ the entry rule (registration section 6)
def c1_rule(x, xp, seed=SEED_C1, nb=NB):
    n = len(x)
    d = rms(xp) - rms(x)
    rng = random.Random(seed)
    ds = []
    for _ in range(nb):
        idx = [rng.randrange(n) for _ in range(n)]
        ds.append(rms([xp[i] for i in idx]) - rms([x[i] for i in idx]))
    ds.sort()
    lo, hi = ds[int(0.025 * nb)], ds[int(0.975 * nb) - 1]
    v = "BETTER" if (d <= -0.010 and hi < 0) else ("WORSE" if lo > 0 else "NOT RESOLVED")
    return {"d_w": d, "lo95_w": lo, "hi95_w": hi, "verdict": v, "n_kinds": n, "rms_M10_w": rms(x), "rms_M10C_w": rms(xp)}


def t_interval(v):
    n = len(v)
    if n < 2:
        return {"n": n}
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    h = t_ppf(0.975, n - 1) * sd / math.sqrt(n)
    return {"n": n, "mean_w": m, "lo95_w": m - h, "hi95_w": m + h}


def score_session(scored, fitj):
    o = scored
    card = CD.get(o.get("card"), o.get("card"))
    if card not in CARDS:
        stop(f"unknown card {o.get('card')}")
    pr = o["primary"]
    if len(pr.get("kept_passes") or []) < 2:
        return {"verdict": "NOT SCORED", "why": "fewer than 2 kept passes (E178's rule)"}
    fcf = fitj["forecasts_e178"]
    kinds = pr["reported"]["kinds"]
    rows = []
    for k, v in sorted(kinds.items()):
        if k not in fcf:
            continue
        if not v.get("c_kept") or v.get("D_w") is None or (v.get("n") or 0) < 2:
            continue
        f = fcf[k]["cards"][card]
        fac = v["P_w"] / f["P_w"]
        x = v["D_w"] - v["P_w"]
        rows.append({"kind": k, "fmt": fcf[k]["fmt"], "x_w": x, "x_prime_w": x - fac * f["L_w"], "factor": fac,
                     "x_prime_K_card_w": x - fac * f["arm_K_card"]["L_w"], "x_prime_R_w": x - fac * f["arm_R"]["L_w"]})
    if not rows:
        return {"verdict": "NOT SCORED", "why": "no float kind kept"}
    X, XP = [r["x_w"] for r in rows], [r["x_prime_w"] for r in rows]
    C1 = c1_rule(X, XP)
    C2 = {}
    for fmt in FLOATS:
        a = [r for r in rows if r["fmt"] == fmt]
        C2[fmt] = (rms([r["x_prime_w"] for r in a]) - rms([r["x_w"] for r in a])) if a else None
    c2ok = all(C2[f] is not None and C2[f] < 0 for f in FLOATS)
    enters = C1["verdict"] == "BETTER" and c2ok
    m = {fmt: t_interval([r["x_w"] for r in rows if r["fmt"] == fmt]) for fmt in FLOATS}
    arms = {nm: rms([r[key] for r in rows]) - rms(X) for nm, key in (("K_card", "x_prime_K_card_w"), ("R", "x_prime_R_w"))}
    return {"run": "E178", "card": card, "arm": "REPORTED (never one of E178's rules)", "C1": C1, "C2_d_w": C2, "C2_holds": c2ok,
            "enters_M10_for_the_next_blind_pool": enters, "reported_m_level_w": m,
            "reported_L_w": {fmt: fitj["levels"]["primary_K"][fmt]["L_w"][card] for fmt in FLOATS},
            "reported_arms_d_w": arms, "kinds": rows}


# ------------------------------------------------------------------ the power (registration section 7)
def power(L, sig, n=(14, 13), seed=SEED_POWER, nd=2000, nbb=1000):
    rng = np.random.default_rng(seed)
    out = []
    Lv = np.array([L["fp32"]] * n[0] + [L["fp16"]] * n[1])
    for frac in (1.0, 0.5, 0.0):
        for scom in (0.0, 0.02, 0.04):
            ok = worse = 0
            for _ in range(nd):
                x = np.concatenate([frac * L["fp32"] + rng.normal(0, sig["fp32"], n[0]),
                                    frac * L["fp16"] + rng.normal(0, sig["fp16"], n[1])]) + rng.normal(0, scom)
                xp = x - Lv
                d = math.sqrt(np.mean(xp ** 2)) - math.sqrt(np.mean(x ** 2))
                idx = rng.integers(0, x.size, (nbb, x.size))
                ds = np.sqrt(np.mean(xp[idx] ** 2, axis=1)) - np.sqrt(np.mean(x[idx] ** 2, axis=1))
                lo, hi = np.quantile(ds, 0.025), np.quantile(ds, 0.975)
                c2 = all(math.sqrt(np.mean(xp[a:b] ** 2)) < math.sqrt(np.mean(x[a:b] ** 2)) for a, b in ((0, n[0]), (n[0], x.size)))
                ok += (d <= -0.010 and hi < 0 and c2)
                worse += lo > 0
            out.append({"L_true_fraction": frac, "sigma_common_w": scom, "P_enter": ok / nd, "P_C1_worse": worse / nd, "draws": nd})
    return out


# ------------------------------------------------------------------ checks (registration section 9 step 2)
def checks(I, quiet=False):
    log = []
    P = log.append
    rows = m10_classed(I)
    # (1) the classing reproduces posthoc-structure.json
    ph = load(os.path.join(DD, "2026-11-06-q145b-m10-s", "posthoc-structure.json"))["classes"]
    name = {("zero", "one"): "zero, one word in every lane", ("zero", "eight"): "zero, eight lane words",
            ("bit", "one"): "single B bit, one base word", ("bit", "eight"): "single B bit, eight base words"}
    mine = defaultdict(list)
    for r in rows:
        mine[name.get((r["struct"], r["cls"]), "other")].append(r)
    ok1 = True
    for c, v in ph.items():
        m = mine.get(c, [])
        b = mean([r["e"] for r in m]) if m else None
        good = len(m) == v["n_rows"] and b is not None and abs(b - v["bias_w"]) < 1e-12
        if v.get("rows"):
            good &= sorted((x["exp"], x["key"]) for x in v["rows"]) == sorted((r["exp"], r["key"]) for r in m)
        ok1 &= good
        P(f"[1] {c:34s} posthoc n {v['n_rows']:4d} bias {v['bias_w']:+.6f} | here n {len(m):4d} bias {b:+.6f}  {'OK' if good else 'FAIL'}")
    # (2) d600 reproduces the in-sample predictions of fp32.pi's committed rows
    f, kind = f_pi(I)
    ok2 = True
    for r in I.m10rows:
        if r["key"] != "fp32.pi":
            continue
        a = I.by[(r["exp"], r["key"])]
        sess = f"{r['exp']}|{r['card']}"
        s = I.s_of(sess, r["card"])
        d = PM.d600(f, "fp32", float(a["rate"]), r["card"], I.m10, s)
        dd = abs(d - r["M10_insample_pred_w"])
        s5 = round(s, 5) == round(I.sst[sess], 5)
        ok2 &= dd <= 1e-9 and s5
        P(f"[2] {sess} fp32.pi: d600 vs M10_insample_pred_w |diff| {dd:.2e} W; s {s:.8f} rounds to m10.json's {I.sst[sess]}  "
          f"{'OK' if dd <= 1e-9 and s5 else 'FAIL'}")
    # (3) d600 on E178's float kinds' features reproduces P_w for both cards
    fc, kinds = e178_float_kinds()
    worst = 0.0
    for k, v in kinds.items():
        for cd in CARDS:
            d = PM.d600(v["m10_features"], v["fmt"], fc["rate"][v["fmt"]], cd, I.m10, 1.0)
            worst = max(worst, abs(d - v["P_w"][cd]))
    ok3 = worst <= 1e-9 and len(kinds) == 27
    P(f"[3] E178's {len(kinds)} float kinds: d600 at s = 1 and E171's zeros rate vs forecast-e178.json P_w, both cards: max |diff| {worst:.2e} W  "
      f"{'OK' if ok3 else 'FAIL'}")
    # (4) E178's float tiles hash and pass as one-word zeros
    cls = defaultdict(int)
    for v in kinds.values():
        cls[(v["fmt"], v["struct"], v["cls"])] += 1
    ok4 = dict(cls) == {("fp32", "zero", "one"): 14, ("fp16", "zero", "one"): 13}
    P(f"[4] E178's float tiles by bytes (sha256 as kinds-e178.json): {dict(cls)}  {'OK' if ok4 else 'FAIL'}")
    # (5) the tie's bytes
    pib = open(os.path.join(TOP, "tools", "claims-v3", "kinds", "tiles", "fp32", "pi.bin"), "rb").read()
    words = set(struct.unpack("<512I", pib))
    host = struct.unpack("<I", struct.pack("<f", 3.14159274))[0]
    ok5 = words == {PI_WORD} and host == PI_WORD and sha_b(pib) == kind
    P(f"[5] pi.bin: {len(pib)} bytes, words {sorted(hex(w) for w in words)}; the host's 3.14159274f = {host:#010x}; "
      f"sha256 = fp32.pi's rows' {kind[:12]}  {'OK' if ok5 else 'FAIL'}")
    # (6) the arm's scorer on two synthetic sessions (a stand-in level of 0.07 W at aifoundry3, never the fit's)
    ok6 = True
    for truth, want in (("P + L", "BETTER"), ("P", "WORSE")):
        res = score_session(*_synthetic(fc, kinds, truth))
        good = res["C1"]["verdict"] == want and res["C2_holds"] == (want == "BETTER") and \
            res["enters_M10_for_the_next_blind_pool"] == (want == "BETTER")
        ok6 &= good
        P(f"[6] score on a synthetic session, truth {truth:5s}: C1 {res['C1']['verdict']} d {res['C1']['d_w']:+.4f} W, C2 {res['C2_holds']}, "
          f"enters {res['enters_M10_for_the_next_blind_pool']} (want {want})  {'OK' if good else 'FAIL'}")
    one = _synthetic(fc, kinds, "P", passes=["17810"])
    ns = score_session(*one)
    ok6 &= ns.get("verdict") == "NOT SCORED"
    P(f"[6] score with one kept pass: {ns.get('verdict')}  {'OK' if ns.get('verdict') == 'NOT SCORED' else 'FAIL'}")
    # (7) the t quantile
    ok7 = abs(t_ppf(0.975, 12) - 2.178813) < 1e-5 and abs(t_ppf(0.975, 31) - 2.039513) < 1e-5
    P(f"[7] t(0.975, 12) {t_ppf(0.975, 12):.6f} (2.178813), t(0.975, 31) {t_ppf(0.975, 31):.6f} (2.039513)  {'OK' if ok7 else 'FAIL'}")
    allok = ok1 and ok2 and ok3 and ok4 and ok5 and ok6 and ok7
    P(f"SELFTEST {'PASS' if allok else 'FAIL'}")
    if not quiet:
        print("\n".join(log))
    return allok, log, rows


def _synthetic(fc, kinds, truth, passes=("17810", "17811", "17812", "17813")):
    """a stand-in E178 scored.json: s = 1.004, every float kind at P x s (+ a 0.07 W level at aifoundry3 when truth = 'P + L'),
    with a small deterministic scatter; and a stand-in fit carrying that level"""
    s, Lw = 1.004, 0.07
    rng = random.Random(9)
    kk = {}
    fcf = {}
    for k, v in kinds.items():
        P = v["P_w"]["a3"] * s
        D = P + (Lw * s if truth == "P + L" else 0.0) + rng.gauss(0, 0.02)
        kk[k] = {"D_w": D, "n": len(passes), "P_w": P, "c_kept": True}
        cards = {cd: {"P_w": v["P_w"][cd], "L_w": Lw * (1.0 if cd == "a3" else 0.9616),
                      "arm_K_card": {"L_w": Lw}, "arm_R": {"L_w": Lw}} for cd in CARDS}
        fcf[k] = {"fmt": v["fmt"], "cards": cards}
    scored = {"card": "aifoundry3", "primary": {"kept_passes": list(passes), "reported": {"kinds": kk}}}
    fitj = {"forecasts_e178": fcf, "levels": {"primary_K": {fmt: {"L_w": {"a3": Lw, "c1": Lw * 0.9616}} for fmt in FLOATS}}}
    return scored, fitj


# ------------------------------------------------------------------ the fit
def fit(out):
    I = Inputs()
    ok, log, mrows = checks(I, quiet=True)
    if not ok:
        print("\n".join(log))
        stop("a check failed: no fit")
    zrows = [r for r in mrows if r["struct"] == "zero"]
    ties, absent = tie_rows(I)
    pi_gap = [{"run": r["run"], "e_heldout_w": r["e"], "e_insample_w": r["e_insample"], "gap_w": r["e"] - r["e_insample"]}
              for r in mrows if r["key"] == "fp32.pi"]
    rows_K = add_rho([dict(r) for r in zrows] + ties)
    rows_R = add_rho([dict(r) for r in zrows])
    # primary K: kind-weighted, (a) + (b), cards pooled
    full = levels(rows_K, "kind")
    folds = loro(rows_K, "kind")
    iv = {}
    sig = {}
    for fmt in FLOATS:
        iv[fmt] = jackknife(rows_K, folds, full, fmt)
        iv[fmt]["boot_runs"] = boot_runs(rows_K, fmt, "kind")
        sig[fmt] = sigma_c(rows_K, fmt)
    # arm K-card
    lv_card, iv_card, fold_card = {}, {}, {}
    for cd in CARDS:
        rc = [dict(r) for r in rows_K if r["card"] == cd]
        lv_card[cd] = levels(rc, "kind")
        fold_card[cd] = loro(rc, "kind")
        iv_card[cd] = {fmt: jackknife(rc, fold_card[cd], lv_card[cd], fmt) for fmt in FLOATS}
        for r in rc:
            for q in rows_K:
                if q["run"] == r["run"] and q["key"] == r["key"] and q["src"] == r["src"]:
                    q["e_prime_K_card"] = r["e_prime"]
    # arm R: rows (a) only, row-weighted
    lv_row = levels(rows_R, "row")
    loro(rows_R, "row")
    rinsample = mean([r["e"] for r in rows_R if r["cls"] == "one"])
    fc, kinds = e178_float_kinds()
    c1 = I.c1
    lvp = {fmt: dict(full[fmt]) for fmt in FLOATS}
    lvp["_c1"] = c1
    fcs = forecasts(fc, kinds, lvp, iv, sig, lv_card, lv_row)
    Lw = {fmt: {cd: (1.0 if cd == "a3" else c1) * fc["rate"][fmt] * full[fmt]["one"] for cd in CARDS} for fmt in FLOATS}
    pw = power({fmt: Lw[fmt]["a3"] for fmt in FLOATS}, sig)
    # post hoc: the single-bit rows of M10 (not fit rows; E147's are steps over a constant-lane zero, where a level cancels)
    brows = add_rho([dict(r) for r in mrows if r["struct"] == "bit" and r["exp"] != "E147"])
    for r in brows:
        lv = folds.get(r["run"], full)
        lam = lv[r["fmt"]][r["cls"]]
        r["lam_heldout_J"] = lam
        r["e_prime"] = r["e"] - r["s"] * r["c"] * r["rate"] * lam
    # post hoc: pool 8's single-bit T_S tiles on E171 and E172
    man8 = {t["name"]: t for t in load(os.path.join(B8, "blind8.json"))["tiles"]}
    p8 = []
    for exp, (cd, d) in POOL8.items():
        sc = load(os.path.join(d, "scored.json"))
        red = load(os.path.join(d, f"{exp.lower()}.json"))["items"]
        s = float(sc["primary"]["scale"]["s_float"])
        for nm, v in sorted(sc["primary"]["rows"].items()):
            t = man8.get(nm)
            if not t or t["type"] not in FLOATS:
                continue
            st, w, _ = classify(open(os.path.join(B8, t["file"]), "rb").read(), t["type"])
            if st != "bit" or v.get("D_w") is None or v.get("M10_primary_w") is None:
                continue
            rate = float(red[nm]["rate"]["mean"])
            e = v["D_w"] - v["M10_primary_w"]
            add = s * I.cterm(cd) * rate * full[t["type"]][w]
            p8.append({"exp": exp, "card": cd, "key": nm, "fmt": t["type"], "cls": w, "kind": t["sha256"]["whole"] if isinstance(t.get("sha256"), dict) else nm,
                       "run": f"{exp}|{cd}", "e": e, "e_prime": e - add, "add_w": add})
    res = {
        "_what": "Q148(c), M10's constant-lane term (tools/claims-v3/m10-c/REGISTRATION.md, c71fbc7f): the fit, the held-out errors, "
                 "the uncertainty, the frozen forecasts for E178's float kinds (a REPORTED arm), the power, the post hoc readings",
        "labels": {"levels": "fitted on committed rows (the reading came from M10's part of them)",
                   "heldout": "leave one run out, POST HOC (these rows produced the reading)",
                   "forecasts_e178": "FROZEN before any E178 datum; a REPORTED arm, never one of E178's rules",
                   "power": "design arithmetic", "posthoc": "POST HOC"},
        "checks": log,
        "rows": {"n_m10_zero_rows": len(zrows), "n_tie_rows": len(ties), "tie_absent_sessions": absent,
                 "pi_insample_vs_heldout": pi_gap,
                 "by_class": {f"{fmt}|{cls}": {"rows": sum(1 for r in rows_K if r["fmt"] == fmt and r["cls"] == cls),
                                               "runs": len({r["run"] for r in rows_K if r["fmt"] == fmt and r["cls"] == cls}),
                                               "kinds": len({r["kind"] for r in rows_K if r["fmt"] == fmt and r["cls"] == cls})}
                              for fmt in FLOATS for cls in ("one", "eight")},
                 "fit_rows": [{q: r.get(q) for q in ("src", "run", "exp", "card", "key", "fmt", "cls", "kind", "tile", "a_word", "D", "e",
                                                     "rate", "s", "c", "rho_J", "lam_heldout_J", "e_prime", "e_prime_K_card",
                                                     "reduction", "n_passes")} for r in rows_K]},
        "kinds": _kinds_table(rows_K),
        "levels": {
            "primary_K": {fmt: {"lambda_J_per_op": full[fmt]["one"], "lambda_eight_J_per_op": full[fmt]["eight"] if full[fmt]["eight_fitted"] else None,
                                "eight_fitted_runs": sorted({r["run"] for r in rows_K if r["fmt"] == fmt and r["cls"] == "eight"}),
                                "L_w": Lw[fmt], "rate_per_s": fc["rate"][fmt],
                                "jackknife": {k: v for k, v in iv[fmt].items() if k != "boot_runs"}, "boot_runs": iv[fmt]["boot_runs"],
                                "L_95_w": {cd: [(1.0 if cd == "a3" else c1) * fc["rate"][fmt] * iv[fmt]["lo95_J"],
                                                (1.0 if cd == "a3" else c1) * fc["rate"][fmt] * iv[fmt]["hi95_J"]] for cd in CARDS},
                                "L_boot95_w": {cd: [(1.0 if cd == "a3" else c1) * fc["rate"][fmt] * iv[fmt]["boot_runs"]["lo95_J"],
                                                    (1.0 if cd == "a3" else c1) * fc["rate"][fmt] * iv[fmt]["boot_runs"]["hi95_J"]] for cd in CARDS},
                                "sigma_C_w": sig[fmt]} for fmt in FLOATS},
            "arm_K_card": {cd: {fmt: {"lambda_J_per_op": lv_card[cd][fmt]["one"],
                                      "L_w": (1.0 if cd == "a3" else c1) * fc["rate"][fmt] * lv_card[cd][fmt]["one"],
                                      "jackknife": {k: v for k, v in iv_card[cd][fmt].items() if k != "loro_values_J"},
                                      "L_95_w": [(1.0 if cd == "a3" else c1) * fc["rate"][fmt] * iv_card[cd][fmt]["lo95_J"],
                                                 (1.0 if cd == "a3" else c1) * fc["rate"][fmt] * iv_card[cd][fmt]["hi95_J"]]
                                      if "lo95_J" in iv_card[cd][fmt] else None} for fmt in FLOATS} for cd in CARDS},
            "arm_R": {fmt: {"lambda_J_per_op": lv_row[fmt]["one"], "L_w_a3": fc["rate"][fmt] * lv_row[fmt]["one"]} for fmt in FLOATS},
            "arm_R_check_insample_both_formats_w": rinsample},
        "heldout_posthoc": {
            "primary_K": {f"{fmt}|{cls}|{cd}": summary([r for r in rows_K if r["fmt"] == fmt and r["cls"] == cls and (cd == "all" or r["card"] == cd)])
                          for fmt in FLOATS for cls in ("one", "eight") for cd in ("all",) + CARDS
                          if any(r["fmt"] == fmt and r["cls"] == cls and (cd == "all" or r["card"] == cd) for r in rows_K)},
            "primary_K_without_tie": {f"{fmt}|one|{cd}": summary([r for r in rows_K if r["fmt"] == fmt and r["cls"] == "one" and r["src"] != "tie"
                                                                  and (cd == "all" or r["card"] == cd)]) for fmt in FLOATS for cd in ("all",) + CARDS},
            "tie_only": {cd: summary([r for r in rows_K if r["src"] == "tie" and (cd == "all" or r["card"] == cd)]) for cd in ("all",) + CARDS},
            "arm_K_card": {f"{fmt}|one|{cd}": summary([r for r in rows_K if r["fmt"] == fmt and r["cls"] == "one" and r["card"] == cd], "e_prime_K_card")
                           for fmt in FLOATS for cd in CARDS},
            "arm_R": {f"{fmt}|{cls}": summary([r for r in rows_R if r["fmt"] == fmt and r["cls"] == cls]) for fmt in FLOATS for cls in ("one", "eight")
                      if any(r["fmt"] == fmt and r["cls"] == cls for r in rows_R)},
            "by_run": {R: summary([r for r in rows_K if r["run"] == R]) for R in sorted({r["run"] for r in rows_K}, key=lambda x: int(x.split("|")[0][1:]))}},
        "posthoc_single_bit": {
            "m10_rows": {f"{fmt}|{cls}|{cd}": summary([r for r in brows if r["fmt"] == fmt and r["cls"] == cls and (cd == "all" or r["card"] == cd)])
                         for fmt in FLOATS for cls in ("one", "eight") for cd in ("all",) + CARDS
                         if any(r["fmt"] == fmt and r["cls"] == cls and (cd == "all" or r["card"] == cd) for r in brows)},
            "m10_rows_note": "E147's single-bit rows are left out: they are steps over a constant-lane zero, where a level cancels",
            "m10_rows_list": [{q: r.get(q) for q in ("run", "key", "fmt", "cls", "a_word", "bit", "e", "e_prime")} for r in brows],
            "pool8": {f"{cd}": summary([r for r in p8 if r["card"] == cd]) for cd in CARDS},
            "pool8_list": p8},
        "forecasts_e178": fcs,
        "power": pw,
        "inputs_sha256": {REL(p): fsha(p) for p in _inputs()},
    }
    os.makedirs(out, exist_ok=True)
    jp = os.path.join(out, "termc-fit.json")
    open(jp, "w").write(json.dumps(res, indent=1, sort_keys=True) + "\n")
    txt = report(res)
    open(os.path.join(out, "termc-fit.txt"), "w").write(txt)
    fj = {"_what": "Q148(c): M10's constant-lane term, FROZEN forecasts for E178's 27 float one-number kinds, a REPORTED arm "
                   "(never one of E178's rules), from termc-fit.json; P is E178's registered P_w (s = 1, E171's zeros rate)",
          "frozen_before_any_E178_datum": True, "registration": "tools/claims-v3/m10-c/REGISTRATION.md (c71fbc7f)",
          "scoring": "x = D_w - P_w (E178 scored.json primary.reported.kinds); x' = x - (P_w / P_frozen) x L_w; C1 and C2 by "
                     "REGISTRATION.md section 6; termc.py score",
          "levels_w": {fmt: {"L_w": Lw[fmt], "L_95_w": res["levels"]["primary_K"][fmt]["L_95_w"], "sigma_C_w": sig[fmt]} for fmt in FLOATS},
          "kinds": fcs}
    open(os.path.join(out, "forecast-m10c-e178.json"), "w").write(json.dumps(fj, indent=1, sort_keys=True) + "\n")
    open(os.path.join(out, "forecast-m10c-e178.txt"), "w").write(forecast_txt(fcs, Lw, res))
    print(txt)
    return 0


def _kinds_table(rows):
    by = defaultdict(list)
    for r in rows:
        by[(r["fmt"], r["cls"], r["kind"])].append(r)
    out = []
    for (fmt, cls, kind), v in sorted(by.items()):
        out.append({"fmt": fmt, "cls": cls, "kind_sha256": kind, "labels": sorted({r["key"] for r in v}), "a_word": v[0]["a_word"],
                    "n_rows": len(v), "runs": sorted({r["run"] for r in v}), "mean_e_w": mean([r["e"] for r in v]),
                    "mean_rho_J": mean([r["rho_J"] for r in v]),
                    "mean_e_prime_w": mean([r.get("e_prime") for r in v]) if all(r.get("e_prime") is not None for r in v) else None,
                    "by_card": {cd: {"n": sum(1 for r in v if r["card"] == cd), "mean_e_w": mean([r["e"] for r in v if r["card"] == cd])}
                                for cd in CARDS}})
    return out


def _inputs():
    ps = [os.path.join(HERE, "REGISTRATION.md"), os.path.abspath(__file__), os.path.join(CV, "m10-s", "term_s.py"),
          os.path.join(M10D, "m10.json"), os.path.join(M10D, "rows-m10.json"), os.path.join(M10D, "predict_m10.py"),
          os.path.join(M10D, "fit_m10.py"), os.path.join(DD, "2026-11-06-q145b-m10-s", "posthoc-structure.json"),
          os.path.join(E178D, "forecast-e178.json"), os.path.join(E178D, "kinds-e178.json"),
          os.path.join(TOP, "tools", "claims-v3", "kinds", "tiles", "fp32", "pi.bin"), os.path.join(B8, "blind8.json")]
    for exp, (cd, d) in POOL8.items():
        ps += [os.path.join(d, f"{exp.lower()}.json"), os.path.join(d, "scored.json")]
    return ps


def report(res):
    L = []
    P = L.append
    lv = res["levels"]["primary_K"]
    P("Q148(c): M10's constant-lane term (REGISTRATION.md, c71fbc7f). Labels: levels fitted on committed rows; held-out figures POST HOC;")
    P("E178 forecasts FROZEN, a REPORTED arm; power = design arithmetic.")
    P("")
    P(f"rows: M10's T_S zeros {res['rows']['n_m10_zero_rows']}, the tie {res['rows']['n_tie_rows']} (absent: {', '.join(res['rows']['tie_absent_sessions']) or 'none'})")
    for k, v in res["rows"]["by_class"].items():
        P(f"  {k:12s} rows {v['rows']:3d} runs {v['runs']:3d} kinds {v['kinds']:2d}")
    P("  fp32.pi held out vs in sample: " + "; ".join(f"{x['run']} {x['e_heldout_w']:+.4f} / {x['e_insample_w']:+.4f} (gap {x['gap_w']:+.4f})"
                                              for x in res["rows"]["pi_insample_vs_heldout"]))
    P("")
    P("THE TERM (primary K: kind-weighted, the tie included, cards pooled), one word in every lane:")
    for fmt in FLOATS:
        v = lv[fmt]
        j = v["jackknife"]
        P(f"  {fmt}: lambda {v['lambda_J_per_op'] * 1e12:+.3f} pJ/op; L aifoundry3 {v['L_w']['a3']:+.4f} W [{v['L_95_w']['a3'][0]:+.4f}, "
          f"{v['L_95_w']['a3'][1]:+.4f}] (jackknife over {j['n_runs']} runs, t {j['t']:.3f}); boot [{v['L_boot95_w']['a3'][0]:+.4f}, "
          f"{v['L_boot95_w']['a3'][1]:+.4f}]; card 1 {v['L_w']['c1']:+.4f} W; sigma_C {v['sigma_C_w']:.4f} W")
        P(f"        eight lane words: {('%+.3f pJ/op, fitted on ' % (v['lambda_eight_J_per_op'] * 1e12) + ', '.join(v['eight_fitted_runs'])) if v['lambda_eight_J_per_op'] is not None else 'none'} (in sample; one run)")
    P("ARMS (reported):")
    for cd in CARDS:
        for fmt in FLOATS:
            a = res["levels"]["arm_K_card"][cd][fmt]
            ci = a["L_95_w"]
            P(f"  K-card {cd} {fmt}: L {a['L_w']:+.4f} W" + (f" [{ci[0]:+.4f}, {ci[1]:+.4f}] ({a['jackknife']['n_runs']} runs)" if ci else ""))
    for fmt in FLOATS:
        P(f"  R {fmt}: L aifoundry3 {res['levels']['arm_R'][fmt]['L_w_a3']:+.4f} W")
    P(f"  R check: rows (a) one word, both formats, row mean of e {res['levels']['arm_R_check_insample_both_formats_w']:+.6f} W (posthoc-structure +0.069)")
    P("")
    P("KINDS (mean held-out e of M10, W):")
    for k in res["kinds"]:
        P(f"  {k['fmt']} {k['cls']:5s} {','.join(k['labels'])[:44]:44s} A {k['a_word']} rows {k['n_rows']:3d} runs {len(k['runs']):2d} "
          f"e {k['mean_e_w']:+.4f}  a3 {k['by_card']['a3']['n']:2d} {(k['by_card']['a3']['mean_e_w'] or 0):+.4f}  c1 {k['by_card']['c1']['n']:2d} "
          f"{(k['by_card']['c1']['mean_e_w'] or 0):+.4f}  e' {(k['mean_e_prime_w'] if k['mean_e_prime_w'] is not None else float('nan')):+.4f}")
    P("")
    P("HELD OUT BY RUN, POST HOC (M10 -> M10-C; rms (bias), W; kind-weighted beside):")
    for name in ("primary_K", "primary_K_without_tie", "arm_K_card", "arm_R"):
        for k, s in res["heldout_posthoc"][name].items():
            if not s["n_rows"]:
                continue
            a, b = s["M10"], s["M10_C"]
            P(f"  {name:22s} {k:14s} n {s['n_rows']:3d} kinds {s['n_kinds']:2d}: {a['rms_w']:.4f} ({a['bias_w']:+.4f}) -> {b['rms_w']:.4f} "
              f"({b['bias_w']:+.4f}); kind-weighted {a['kind_rms_w']:.4f} ({a['kind_bias_w']:+.4f}) -> {b['kind_rms_w']:.4f} ({b['kind_bias_w']:+.4f})")
    for cd, s in res["heldout_posthoc"]["tie_only"].items():
        if not s["n_rows"]:
            continue
        a, b = s["M10"], s["M10_C"]
        P(f"  {'tie only':22s} {cd:14s} n {s['n_rows']:3d}: {a['rms_w']:.4f} ({a['bias_w']:+.4f}) -> {b['rms_w']:.4f} ({b['bias_w']:+.4f})")
    P("")
    P("POST HOC, NOT FIT ROWS: single-bit T_S tiles with their class's level added")
    for k, s in res["posthoc_single_bit"]["m10_rows"].items():
        if not s["n_rows"]:
            continue
        a, b = s["M10"], s["M10_C"]
        P(f"  M10 rows {k:16s} n {s['n_rows']:3d}: {a['rms_w']:.4f} ({a['bias_w']:+.4f}) -> {b['rms_w']:.4f} ({b['bias_w']:+.4f})")
    for k, s in res["posthoc_single_bit"]["pool8"].items():
        if s["n_rows"]:
            a, b = s["M10"], s["M10_C"]
            P(f"  pool 8 {k:18s} n {s['n_rows']:3d}: {a['rms_w']:.4f} ({a['bias_w']:+.4f}) -> {b['rms_w']:.4f} ({b['bias_w']:+.4f})")
    P("")
    P("POWER of the entry rule (design arithmetic; aifoundry3's L; 14 fp32 + 13 fp16 kinds):")
    for p in res["power"]:
        P(f"  L_true {p['L_true_fraction']:.1f} x L, sigma_common {p['sigma_common_w']:.2f} W: enters {p['P_enter']:.3f}, C1 WORSE {p['P_C1_worse']:.3f}")
    P("")
    P("CHECKS:")
    L += ["  " + x for x in res["checks"]]
    return "\n".join(L) + "\n"


def forecast_txt(fcs, Lw, res):
    L = ["Q148(c): FROZEN forecasts for E178's 27 float one-number kinds, a REPORTED arm (never one of E178's rules).",
         "P = E178's registered P_w (s = 1, E171's zeros rate); L = c x rate x lambda (primary K); intervals 95%.",
         "At scoring: x = D_w - P_w (E178's scored P), x' = x - (P_w / P) x L.", ""]
    for fmt in FLOATS:
        v = res["levels"]["primary_K"][fmt]
        L.append(f"{fmt}: L aifoundry3 {Lw[fmt]['a3']:+.4f} W [{v['L_95_w']['a3'][0]:+.4f}, {v['L_95_w']['a3'][1]:+.4f}], card 1 "
                 f"{Lw[fmt]['c1']:+.4f} W [{v['L_95_w']['c1'][0]:+.4f}, {v['L_95_w']['c1'][1]:+.4f}]; sigma_C {v['sigma_C_w']:.4f} W")
    L.append("")
    L.append(f"{'kind':20s} {'card':4s} {'P':>8s} {'L':>8s} {'P + L':>8s} {'level 95%':>19s} {'predictive 95%':>19s} {'K-card':>8s} {'R':>8s}")
    for k, v in fcs.items():
        for cd in CARDS:
            c = v["cards"][cd]
            L.append(f"{k:20s} {cd:4s} {c['P_w']:8.4f} {c['L_w']:+8.4f} {c['forecast_w']:8.4f} [{c['forecast_level_95_w'][0]:8.4f}, "
                     f"{c['forecast_level_95_w'][1]:8.4f}] [{c['forecast_predictive_95_w'][0]:8.4f}, {c['forecast_predictive_95_w'][1]:8.4f}] "
                     f"{c['arm_K_card']['forecast_w']:8.4f} {c['arm_R']['forecast_w']:8.4f}")
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("selftest", "fit", "score"))
    ap.add_argument("--out")
    ap.add_argument("--txt")
    ap.add_argument("--scored")
    ap.add_argument("--fit")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        ok, log, _ = checks(Inputs(), quiet=True)
        txt = "\n".join(log) + "\n"
        print(txt, end="")
        if a.txt:
            open(a.txt, "w").write(txt)
        return 0 if ok else 1
    if a.cmd == "fit":
        if not a.out:
            stop("fit needs --out")
        return fit(a.out)
    if not (a.scored and a.fit):
        stop("score needs --scored and --fit")
    res = score_session(load(a.scored), load(a.fit))
    s = json.dumps(res, indent=1, sort_keys=True) + "\n"
    if a.out:
        open(a.out, "w").write(s)
    print(json.dumps({k: res.get(k) for k in ("verdict", "C1", "C2_holds", "enters_M10_for_the_next_blind_pool") if k in res}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
