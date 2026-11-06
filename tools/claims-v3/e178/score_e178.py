#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E178 (Q146, the kit): the scorer for E178.md section 5's rules and dated note A1's E178-S-int8, on one session's reduction. Nothing is
fitted or tuned here. The forecasts are forecast-e178.json's (frozen in 48171930), the registered numbers (P's watts per flip, the groups,
the seeds) power-e178.json's and power_e178.py's (imported unchanged: spearman, ranks, T975, RHO_CRIT, DRAWS); every frozen input is
checked against the registration's own hash lists first.

  score   python3 -B score_e178.py score --card aifoundry3 --reduction <primary e178.json> --runs-csv <primary runs.csv> --raw <raw copy>
              --ccheck <ccheck --out json> [--arm name=<reduction json>,<runs csv> ...] [--since <epoch s>] [--json scored.json]
              [--md results.md]

Order, enforced: (1) the frozen inputs (exit 9); (2) every session that must carry a C log has a finished check (ccsessions_e178, E171's
rule; exit 4 and nothing written); (3) E178-C: per kind, every launch in a kept pass judged PASS (E171's P8-KC form, score_p8_600.c_status
imported unchanged); a kind not all PASS leaves every scored set; (4) the session's float scale s, M10's term a, as E171's scorer reads it
(predict_pool8's scale over the reduction's items, pool 8's frozen anchor features; the anchors it may use here are E78's random float
anchors fp32.randn and fp16.randn, never a zeros anchor); (5) the scored forecasts at the session's s and each kind's measured rate
(E178.md section 4: "At scoring the session's own s (M10's term a) and measured rate apply, as E171's scorer does"): M10's D is linear in
s and the rate (predict_m10.d600), so P = P_frozen x s x rate / E171's rate, and F likewise (int8: s = 1); (6) the rules; (7) the readings
reported beside, never a verdict. Fewer than 2 kept passes: every rule NOT SCORED.

THE STATISTICS (E178.md section 5, A1-1; the kit's readings where the text leaves a choice, stated in KIT.md before any datum):
  a kind's per-pass D       the reduction's per_pass[p][kind]["D"] (the mean of its kept runs in the pass, E78's reduction);
  a couple's per-pass x_p   E178-H-*, E178-U: the mean, over the pass's segments in which both runs of the couple were kept, of
                            D(the first named) - D(the second) in that segment, from the reduction's runs.csv; a pass with no complete
                            couple gives none;
  E178-S-int8               x_p = D(int8.e178_v85) - D(int8.neg_ones) per kept pass (each one run a pass); 127 - neg_ones beside;
  the interval              m +- t(0.975, n - 1) sd / sqrt(n) over the passes that give an x_p (power_e178's T975);
  SIGN                      POSITIVE (lower end > 0), NEGATIVE (upper end < 0), NOT RESOLVED;
  SIZE                      PASS if the scored forecast is inside; FAIL HIGH if the forecast is above the interval (the model prices more
                            than the card reads: E178.md section 5's own definition, "FAIL HIGH (M10 prices the flips higher than the
                            card)", and E171's P8 scorer's); FAIL LOW if below. Every SIZE verdict prints its direction in words. A1-1's
                            sentence "With SIZE FAIL LOW, the flips' sign holds and something takes part of it back" names, in the
                            measurement's words, the case printed here as FAIL HIGH (forecast above the interval): KIT.md says so;
  E178-R-int8               Spearman rho (average ranks) of the scored P against the measured D over the int8 kinds scored; >= 0.56 at
                            13 kinds (the registered line); at fewer, the 97.5% point of rho under random order (20,000 shuffles of the
                            measured D, random.Random(17805), power_e178's seed for the rule); 4 or fewer kinds NOT SCORED;
  E178-W-int8               the OLS slope of the measured D on (i)'s launch-mean flips over the int8 kinds scored, divided by the mean of
                            their measured rates, in fJ a flip, 95% by t(0.975, n - 2); PASS if P's registered 7.48 fJ
                            (power-e178.json slope_P_fJ_per_flip) is inside, FAIL HIGH if above, FAIL LOW if below;
  E178-E-*                  the spread (max - min) of the group's measured D against its 95% point under equality: 20,000 draws, each
                            member N(0, se^2 + 0.041^2) with se its sd over passes / sqrt(n), random.Random(17807) (power_e178's);
                            PASS (read equal) if the spread is at or below it, FAIL (read unequal) if above; fewer than 2 members NOT SCORED.
A kind needs D in 2 kept passes for the single-kind rules (E163's minimum); a shorter one leaves them and is named.

Exit 0 when scored.json is written, 4 (no finished check of C), 5 (the scale read a wrong anchor), 9 (a frozen input differs).
Python 3.9 with numpy (the frozen predictor's chain needs it): the Intel's /usr/bin/python3. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import math
import os
import random
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PRED_DIR = os.path.join(TOP, "docs", "reports", "data", "2026-11-05-q142p-pool8-predictor")
FREEZE_SUMS = os.path.join(TOP, "docs", "reports", "data", "2026-11-05-q142x-pool8-freeze", "SHA256SUMS")
P8DIR = os.path.join(TOP, "tools", "claims-v3", "p8-600")
CD = {"aifoundry3": "a3", "aifoundry1c1": "c1"}
FLOATS = ("fp32", "fp16")
RULES = ["E178-C", "E178-H-int8", "E178-H-fp32", "E178-H-fp16", "E178-U", "E178-S-int8", "E178-R-int8", "E178-W-int8", "E178-E-int8",
         "E178-E-fp32", "E178-E-fp16"]
COUPLE_RULES = {"E178-H-int8": ("int8.e178_v5", "int8.e178_v4"), "E178-H-fp32": ("fp32.e178_v5", "fp32.e178_v4"),
                "E178-H-fp16": ("fp16.e178_v5", "fp16.e178_v4"), "E178-U": ("fp32.ones", "fp32.e178_uf")}
S_RULE = ("int8.e178_v85", "int8.neg_ones")
S_BESIDE = ("int8.e178_v127", "int8.neg_ones")
SCALE_ANCHORS_OK = ("fp32.randn", "fp16.randn")
SYS_KIND = 0.041                     # E178.md section 6: the per-kind session term
MIN_KIND_PASSES = 2
EXIT_FROZEN, EXIT_NO_C, EXIT_SCALE = 9, 4, 5
# the registration's files this scorer reads, each checked against the registration's own hash lists
FROZEN_READ = ["tools/claims-v3/e178/forecast-e178.json", "tools/claims-v3/e178/power-e178.json", "tools/claims-v3/e178/power_e178.py",
               "tools/claims-v3/e178/kinds-e178.json", "tools/claims-v3/e178/plan-e178.json", "tools/claims-v3/e178/E178.md",
               "tools/claims-v3/e178/E178.md.dated-note-A1.md", "tools/claims-v3/e178/power-e178-a1.json"]
_M = {}


class Refuse(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ------------------------------------------------------------------------------------------------- inputs
def frozen_check(top=TOP):
    """every file this scorer reads against SHA256SUMS-e178-registration / SHA256SUMS-e178-a1, whose own sha256 are e178_common.LISTS"""
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import e178_common as E  # noqa: E402
    bad, want = [], {}
    for rel, lit in E.LISTS.items():
        p = os.path.join(top, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != lit:
            bad.append(f"{rel}: sha256 {have[:12]} is not the pinned {lit[:12]}")
            continue
        for line in open(p):
            if line.strip():
                h, q = line.split(None, 1)
                want[q.strip().lstrip("*")] = h
    for rel in FROZEN_READ:
        p = os.path.join(top, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if want.get(rel) is None:
            bad.append(f"{rel}: in neither registration hash list")
        elif have != want[rel]:
            bad.append(f"{rel}: sha256 {have[:12]} is not the registered {want[rel][:12]}")
    if bad:
        raise Refuse(EXIT_FROZEN, "a frozen input differs from the registration's hash lists: " + "; ".join(bad))
    return {rel: want[rel] for rel in FROZEN_READ}


def PW():
    if "PW" not in _M:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import power_e178 as pw  # noqa: E402  (the registered rule functions, unchanged)
        _M["PW"] = pw
    return _M["PW"]


def T(df):
    """t(0.975, df): power_e178.T975, with the standard values it does not hold"""
    t = dict(PW().T975)
    t.update({k: v for k, v in {7: 2.365, 8: 2.306, 9: 2.262, 12: 2.179}.items() if k not in t})
    return t[df]


def CS():
    if "CS" not in _M:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import ccsessions_e178 as c  # noqa: E402
        _M["CS"] = c
    return _M["CS"]


def c_status_fn():
    if "CST" not in _M:
        if P8DIR not in sys.path:
            sys.path.insert(0, P8DIR)
        import score_p8_600 as s8  # noqa: E402  (E163's c_status, copied there; imported unchanged)
        _M["CST"] = s8.c_status
    return _M["CST"]


def A2():
    if "A2" not in _M:
        if PRED_DIR not in sys.path:
            sys.path.insert(0, PRED_DIR)
        import predict_pool8_a2 as a2  # noqa: E402  (its own check_lists runs before predict_pool8 is imported, in A2.P())
        _M["A2"] = a2
    return _M["A2"]


def freeze_sums():
    out = {}
    for line in open(FREEZE_SUMS):
        if line.strip():
            h, p = line.split(None, 1)
            out[p.strip().lstrip("*")] = h
    return out


def pool8_pred(card):
    """pool 8's frozen predictions file for this card: the source of M10's float anchors' features (E171's scorer's route)"""
    rel = f"tools/claims-v3/kinds/blind8/predictions-pool8-{card}.json"
    path = os.path.join(TOP, rel)
    want = freeze_sums().get(rel)
    have = sha(path) if os.path.exists(path) else "missing"
    if not want or have != want:
        raise Refuse(EXIT_FROZEN, f"{rel}: sha256 {have[:12]} is not the freeze's {str(want)[:12]} (Q142(x) SHA256SUMS)")
    return path, json.load(open(path))


def session_scale(card, red_path):
    """M10's term a for this session: predict_pool8.scale (the frozen predictor's, unchanged) over the reduction's anchor items, with pool
    8's frozen m10_anchors features. Only fp32.randn and fp16.randn can be present in an E178 session; any other anchor used refuses (5)."""
    a2 = A2()
    lists = a2.check_lists()
    p = a2.P()
    p.check_inputs()
    _, pred = pool8_pred(card)
    sc = p.scale(pred, red_path)
    bad = [n for n in sc.get("anchors_used", []) if n not in SCALE_ANCHORS_OK]
    if bad:
        raise Refuse(EXIT_SCALE, f"the scale read anchors other than E78's random float anchors: {bad}")
    return {k: sc[k] for k in ("s_float", "anchors_used", "anchors_at_nominal_rate", "ratios", "reduction_sha256")}, lists


# ------------------------------------------------------------------------------------------------- statistics
def interval(xs):
    """mean and the t interval, in power_e178_a1's arithmetic order (m - hw, m + hw)"""
    n = len(xs)
    m = statistics.mean(xs)
    hw = T(n - 1) * statistics.stdev(xs) / math.sqrt(n)
    return m, m - hw, m + hw, hw


def sign_of(lo, hi):
    return "POSITIVE" if lo > 0 else ("NEGATIVE" if hi < 0 else "NOT RESOLVED")


def size_of(lo, hi, fc):
    if lo <= fc <= hi:
        return "PASS", "the forecast is inside the measured interval"
    if fc > hi:
        return "FAIL HIGH", "the forecast is above the measured interval: the model prices more than the card reads"
    return "FAIL LOW", "the forecast is below the measured interval: the model prices less than the card reads"


def couple_xs(rows, passes, a, b):
    """per kept pass: the mean over segments with both runs kept of D(a) - D(b) in that segment; the couples' count and adjacency"""
    out = {}
    for p in passes:
        diffs, adj = [], 0
        for s in (0, 1, 2):
            ra = [r for r in rows if r["pass"] == p and r["segment"] == s and r["item"] == a and r["D"] is not None]
            rb = [r for r in rows if r["pass"] == p and r["segment"] == s and r["item"] == b and r["D"] is not None]
            if ra and rb:
                diffs.append(statistics.mean(r["D"] for r in ra) - statistics.mean(r["D"] for r in rb))
                adj += int(any(abs(x["pos"] - y["pos"]) == 1 for x in ra for y in rb))
        if diffs:
            out[p] = {"x": statistics.mean(diffs), "couples": len(diffs), "adjacent": adj, "segment_diffs": diffs}
    return out


def pair_xs(res, passes, a, b):
    out = {}
    for p in passes:
        pp = res.get("per_pass", {}).get(str(p), {})
        da, db = (pp.get(a) or {}).get("D"), (pp.get(b) or {}).get("D")
        if da is not None and db is not None:
            out[p] = {"x": float(da) - float(db)}
    return out


def diff_rule(xs, dP, dF):
    """SIGN, SIZE against P, and F's SIZE beside, over the per-pass values"""
    v = [xs[p]["x"] for p in sorted(xs)]
    if len(v) < 2:
        return {"verdict": "NOT SCORED", "why": f"{len(v)} kept passes give a value, fewer than 2", "n": len(v), "per_pass": xs}
    m, lo, hi, hw = interval(v)
    sz, why = size_of(lo, hi, dP)
    fz, fwhy = size_of(lo, hi, dF)
    return {"verdict": sign_of(lo, hi), "sign": sign_of(lo, hi), "size": sz, "size_reading": why, "size_F": fz, "size_F_reading": fwhy,
            "mean_w": m, "lo95_w": lo, "hi95_w": hi, "halfwidth_w": hw, "n": len(v), "dP_w": dP, "dF_w": dF, "per_pass": xs}


def measured(res, kinds, passes):
    """E163's form: a kind's mean over the kept passes it has a D in, its sd and n; kinds short of MIN_KIND_PASSES named"""
    out, short = {}, []
    for k in kinds:
        vals = []
        for p in passes:
            r = res.get("per_pass", {}).get(str(p), {}).get(k)
            if r and r.get("D") is not None and not (isinstance(r["D"], float) and math.isnan(r["D"])):
                vals.append(float(r["D"]))
        if len(vals) >= MIN_KIND_PASSES:
            out[k] = {"mean": statistics.mean(vals), "sd": statistics.stdev(vals), "n": len(vals), "per_pass": vals}
        else:
            short.append(k)
    return out, short


def spearman_rule(P, D, kinds):
    pw = PW()
    n = len(kinds)
    if n <= 4:
        return {"verdict": "NOT SCORED", "why": f"{n} int8 kinds scored: rho's 2.5% point cannot be reached", "n": n}
    x, y = [P[k] for k in kinds], [D[k] for k in kinds]
    rho = pw.spearman(x, y)
    if n == 13:
        crit, src = pw.RHO_CRIT, "registered: 0.56, one-sided 2.5% for n = 13"
    else:
        rng = random.Random(17805)
        null = []
        for _ in range(pw.DRAWS):
            yy = list(y)
            rng.shuffle(yy)
            null.append(pw.spearman(x, yy))
        null.sort()
        crit, src = null[int(0.975 * pw.DRAWS)], f"the 97.5% point of {pw.DRAWS} shuffles at n = {n} (random.Random(17805))"
    return {"verdict": "PASS" if rho >= crit else "FAIL", "rho": rho, "line": crit, "line_source": src, "n": n, "kinds": kinds}


def ols(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((a - mx) ** 2 for a in xs)
    b = sum((a - mx) * (c - my) for a, c in zip(xs, ys)) / sxx
    resid = [c - (my + b * (a - mx)) for a, c in zip(xs, ys)]
    se = math.sqrt(sum(r * r for r in resid) / (len(xs) - 2) / sxx)
    return b, se


def slope_rule(D, P, flips, rates, kinds, thr_fj):
    n = len(kinds)
    if n < 4:
        return {"verdict": "NOT SCORED", "why": f"{n} int8 kinds, fewer than 4", "n": n}
    x = [flips[k] for k in kinds]
    b, se = ols(x, [D[k] for k in kinds])
    bp, _ = ols(x, [P[k] for k in kinds])
    R = statistics.mean(rates[k] for k in kinds)
    hw = T(n - 2) * se
    w, lo, hi = b / R * 1e15, (b - hw) / R * 1e15, (b + hw) / R * 1e15
    sz, why = size_of(lo, hi, thr_fj)
    return {"verdict": sz, "reading": why, "slope_fJ_per_flip": w, "lo95_fJ": lo, "hi95_fJ": hi, "line_fJ": thr_fj,
            "scored_P_slope_fJ_per_flip": bp / R * 1e15, "mean_rate_per_s": R, "n": n, "t": T(n - 2), "kinds": kinds}


def equal_rule(meas, members):
    pw = PW()
    have = [m for m in members if m in meas]
    if len(have) < 2:
        return {"verdict": "NOT SCORED", "why": f"{len(have)} members scored, fewer than 2", "members": have}
    v = [meas[m]["mean"] for m in have]
    ses = [meas[m]["sd"] / math.sqrt(meas[m]["n"]) for m in have]
    spread = max(v) - min(v)
    rng = random.Random(17807)
    null = sorted(max(z) - min(z) for z in ([rng.gauss(0, math.sqrt(s * s + SYS_KIND ** 2)) for s in ses] for _ in range(pw.DRAWS)))
    crit = null[int(0.95 * pw.DRAWS)]
    return {"verdict": "PASS" if spread <= crit else "FAIL", "reading": "read equal" if spread <= crit else "read unequal",
            "spread_w": spread, "line_w": crit, "n": len(have), "members": have, "se_w": dict(zip(have, ses)), "D_w": dict(zip(have, v)),
            "left_out": [m for m in members if m not in have]}


# ------------------------------------------------------------------------------------------------- one reduction
def load_rows(csv_path):
    rows = []
    with open(csv_path, newline="") as f:
        for r in csv.DictReader(f):
            def num(k, cast=float):
                x = r.get(k)
                try:
                    return cast(x) if x not in (None, "", "None") else None
                except ValueError:
                    return None
            rows.append({"pass": num("pass", int), "item": r.get("item"), "segment": num("segment", int), "pos": num("pos", int),
                         "D": num("D")})
    return rows


def scored_forecasts(fc, card, s_float, res):
    cd = CD[card]
    items = res.get("items", {})
    out = {}
    for k, r in fc["kinds"].items():
        t = r["type"]
        s = float(s_float) if t in FLOATS else 1.0
        rate = ((items.get(k) or {}).get("rate") or {}).get("mean")
        src = "measured"
        if rate is None:
            rate, src = fc["rate"][t], "E171's zeros rate (no measured rate)"
        f = s * float(rate) / fc["rate"][t]
        out[k] = {"type": t, "P_w": r["P_w"][cd] * f, "F_w": r["F_w"][cd] * f, "P_frozen_w": r["P_w"][cd], "F_frozen_w": r["F_w"][cd],
                  "rate_per_s": float(rate), "rate_source": src, "s": s, "flips_launch_mean": r["flips_i"]["launch_mean"]["total"],
                  "flips_run_mean": (r["flips_i"].get("run_mean") or {}).get("total")}
    return out


def score_reduction(card, red_path, csv_path, kinds_ok, scale=None):
    """every rule on one reduction; kinds_ok is the set of kinds E178-C keeps (None: all)"""
    import e178_common as E  # noqa: E402
    pw = PW()
    fc = json.load(open(os.path.join(HERE, "forecast-e178.json")))
    pj = json.load(open(os.path.join(HERE, "power-e178.json")))
    res = json.load(open(red_path))
    passes = [int(p) for p in res.get("passes", [])]
    out = {"reduction": os.path.relpath(red_path, TOP) if red_path.startswith(TOP + os.sep) else os.path.basename(red_path),
           "reduction_sha256": sha(red_path), "runs_csv_sha256": sha(csv_path) if csv_path else None,
           "kept_passes": passes, "set_aside": res.get("passes_set_aside")}
    if scale is None:
        scale, _ = session_scale(card, red_path)
    out["scale"] = scale
    sf = scored_forecasts(fc, card, scale["s_float"], res)
    out["forecasts_scored"] = sf
    kinds = list(E.E178_NAMES)
    ok = set(kinds) if kinds_ok is None else set(kinds_ok)
    if len(passes) < 2:
        out["verdicts"] = {r: "NOT SCORED" for r in RULES if r != "E178-C"}
        out["NOT SCORED"] = f"{len(passes)} kept passes, fewer than 2"
        out["rules"] = {r: {"verdict": "NOT SCORED", "why": out["NOT SCORED"]} for r in RULES if r != "E178-C"}
        return out
    meas, short = measured(res, kinds, passes)
    out["short_kinds"] = short
    meas_ok = {k: v for k, v in meas.items() if k in ok}
    rows = load_rows(csv_path)
    R = {}
    for rule, (a, b) in COUPLE_RULES.items():
        if a not in ok or b not in ok:
            R[rule] = {"verdict": "NOT SCORED", "why": f"E178-C left out {[x for x in (a, b) if x not in ok]}"}
            continue
        R[rule] = dict(diff_rule(couple_xs(rows, passes, a, b), sf[a]["P_w"] - sf[b]["P_w"], sf[a]["F_w"] - sf[b]["F_w"]),
                       a=a, b=b, form="three adjacent couples a pass")
    for rule, (a, b), beside in (("E178-S-int8", S_RULE, False), ("beside: 127 - neg_ones", S_BESIDE, True)):
        if a not in ok or b not in ok:
            R[rule] = {"verdict": "NOT SCORED", "why": f"E178-C left out {[x for x in (a, b) if x not in ok]}"}
        else:
            R[rule] = dict(diff_rule(pair_xs(res, passes, a, b), sf[a]["P_w"] - sf[b]["P_w"], sf[a]["F_w"] - sf[b]["F_w"]),
                           a=a, b=b, form="one run each a pass")
        if beside:
            R[rule]["reported_only"] = "never a verdict (A1-1)"
    i8 = sorted(k for k in kinds if fc["kinds"][k]["type"] == "int8" and k in meas_ok)
    Dm = {k: meas_ok[k]["mean"] for k in meas_ok}
    Pm = {k: sf[k]["P_w"] for k in sf}
    R["E178-R-int8"] = spearman_rule(Pm, Dm, i8)
    R["E178-W-int8"] = slope_rule(Dm, Pm, {k: sf[k]["flips_launch_mean"] for k in sf}, {k: sf[k]["rate_per_s"] for k in sf}, i8,
                                  pj["rules"]["E178-W-int8"]["slope_P_fJ_per_flip"])
    for g, mem in pj["rules"]["E178-E"]["groups"].items():
        R[f"E178-E-{g}"] = equal_rule(meas_ok, mem)
    out["rules"] = R
    out["verdicts"] = {r: R[r]["verdict"] for r in RULES if r in R}
    out["verdicts_size"] = {r: {"P": R[r].get("size"), "F": R[r].get("size_F")} for r in list(COUPLE_RULES) + ["E178-S-int8"]
                            if "size" in R[r]}
    out["reported"] = reported(fc, sf, meas, rows, passes, res, ok)
    return out


def reported(fc, sf, meas, rows, passes, res, ok):
    """beside, never a verdict: every pair of section 4 against P and F, each kind's D against P and F, the floats' ranking and slope"""
    pw = PW()
    kinds = {}
    for k, s in sf.items():
        m = meas.get(k)
        kinds[k] = {"D_w": m["mean"] if m else None, "n": m["n"] if m else 0, "sd_w": m["sd"] if m else None, "P_w": s["P_w"],
                    "F_w": s["F_w"], "D_minus_P_w": (m["mean"] - s["P_w"]) if m else None, "D_minus_F_w": (m["mean"] - s["F_w"]) if m else None,
                    "flips_launch_mean": s["flips_launch_mean"], "flips_run_mean": s["flips_run_mean"], "rate_per_s": s["rate_per_s"],
                    "c_kept": k in ok}
    pairs = {}
    for grp, lst in list(fc["pairs"].items()) + [("extremes", [v for t in ("fp32", "fp16", "int8") for v in fc["extremes"][t].values()])]:
        pairs[grp] = []
        for p in lst:
            a, b = p["a"], p["b"]
            xs = pair_xs(res, passes, a, b)
            v = [xs[q]["x"] for q in sorted(xs)]
            e = {"a": a, "b": b, "why": p.get("why"), "dP_w": sf[a]["P_w"] - sf[b]["P_w"], "dF_w": sf[a]["F_w"] - sf[b]["F_w"], "n": len(v)}
            if len(v) >= 2:
                m, lo, hi, _ = interval(v)
                e.update(mean_w=m, lo95_w=lo, hi95_w=hi, sign=sign_of(lo, hi), P_inside=lo <= e["dP_w"] <= hi, F_inside=lo <= e["dF_w"] <= hi)
            e["c_kept"] = a in ok and b in ok
            pairs[grp].append(e)
    rank = {}
    for t in FLOATS:
        kk = sorted(k for k in sf if sf[k]["type"] == t and k in meas and k in ok)
        if len(kk) >= 5:
            rank[t] = {"spearman_P": pw.spearman([sf[k]["P_w"] for k in kk], [meas[k]["mean"] for k in kk]),
                       "spearman_F": pw.spearman([sf[k]["F_w"] for k in kk], [meas[k]["mean"] for k in kk]), "n": len(kk)}
            if len(kk) >= 4:
                b, se = ols([sf[k]["flips_launch_mean"] for k in kk], [meas[k]["mean"] for k in kk])
                R = statistics.mean(sf[k]["rate_per_s"] for k in kk)
                rank[t].update(slope_fJ_per_flip=b / R * 1e15, se_fJ=se / R * 1e15)
    bridge_note = ("E78 +0.069 +- 0.045 W and E82 +0.116 +- 0.049 W (int8 neg_ones - ones, post hoc; E178.md section 5)")
    return {"kinds": kinds, "pairs": pairs, "floats_ranking_and_slope": rank, "bridge_earlier": bridge_note,
            "rates": {k: sf[k]["rate_per_s"] for k in sf}}


# ------------------------------------------------------------------------------------------------- the session
def score_session(card, red_path, csv_path, raw, ccheck, arms=(), since=None, skip_c_gate=False):
    if card not in CD:
        raise Refuse(2, f"--card is aifoundry3 or aifoundry1c1, not {card}")
    import e178_common as E  # noqa: E402
    out = {"_note": f"Q146 score_e178.py: E178 on {card}, E178.md section 5's rules with dated note A1's E178-S-int8",
           "run": "E178", "card": card, "scorer_sha256": sha(os.path.abspath(__file__)), "frozen_inputs": frozen_check()}
    run = CS().RUN_OF_CARD[card]
    if not skip_c_gate:
        g = CS().check(run, raw, ccheck, since)
        g = json.loads(json.dumps(g).replace(TOP + os.sep, ""))
        out["c_sessions"] = {k: g[k] for k in ("sessions", "stoptest", "ccdone", "ok", "listed")}
        if not g["ok"]:
            raise Refuse(EXIT_NO_C, "a session that must carry a C log has no finished check of C (E178.md section 7); every rule reads NOT "
                                    "SCORED and nothing is written:\n  " + "\n  ".join(g["lines"]))
    res = json.load(open(red_path))
    want = list(E.E178_NAMES)
    passes_dir = os.path.join(raw, "e178")
    cst = c_status_fn()([*want, *E.ANCHORS, "anchor_pi"], res, [ccheck] if os.path.exists(ccheck) else [ccheck + ".gz"], passes_dir)
    unmeasured = sorted(t for t in want if not (cst.get(t) or {}).get("passes_without_log") and (cst.get(t) or {}).get("launches", 0) == 0)
    cfail = sorted(t for t in want if t not in unmeasured and not (cst.get(t) or {}).get("all_pass"))
    ok = [t for t in want if t not in cfail]
    kc = {"verdict": "FAIL" if cfail else ("PASS" if any((cst.get(t) or {}).get("launches") for t in want) else "NOT SCORED"),
          "c_excluded": cfail, "not_measured": unmeasured,
          "launches": sum((cst.get(t) or {}).get("launches", 0) for t in want), "PASS": sum((cst.get(t) or {}).get("PASS", 0) for t in want),
          "per_kind": {t: cst.get(t) for t in want}, "anchors_and_tie_beside": {t: cst.get(t) for t in [*E.ANCHORS, "anchor_pi"]}}
    prim = score_reduction(card, red_path, csv_path, ok)
    prim["rules"] = dict({"E178-C": kc}, **prim.get("rules", {}))
    prim["verdicts"] = dict({"E178-C": kc["verdict"]}, **prim.get("verdicts", {}))
    out["primary"] = prim
    out["verdicts"] = {r: prim["verdicts"].get(r, "NOT SCORED") for r in RULES}
    # reported, never a verdict: the smoke's C per item (E178.md section 7: fp32.e178_uf's C must read +0 throughout, int8.e178_v85's and
    # int8.e178_v127's accumulator wraps; the check of C judges each against its reference), and each kept pass's order as run
    sm = os.path.join(raw, "e178-smoke")
    out["smoke_c"] = c_status_fn()(list(E.SMOKE_ITEMS), {"passes": [E.SMOKE_PASS]}, [ccheck] if os.path.exists(ccheck) else [ccheck + ".gz"], sm) \
        if os.path.isdir(sm) else {"why": "no e178-smoke directory in the raw copy"}
    plan = json.load(open(E.PLAN_E178))["cards"][E.PLAN_KEY[card]]["passes"]
    oc = {}
    for p in res.get("passes", []):
        pj = os.path.join(passes_dir, f"p{p}", "plan.json")
        if not os.path.exists(pj):
            oc[str(p)] = "no plan.json in the pass directory"
            continue
        ran = [r["item"] for r in json.load(open(pj))]
        oc[str(p)] = ran == plan.get(str(p))
    out["order_as_registered"] = oc
    sa = [cst.get(a) or {} for a in SCALE_ANCHORS_OK]
    out["scale_anchors_c"] = {a: (cst.get(a) or {}).get("all_pass") for a in SCALE_ANCHORS_OK}
    if not all(x.get("all_pass") for x in sa):
        out["scale_c_note"] = "a scale anchor is not C all PASS: reported, the scale is read as registered"
    out["owner_sentence"] = owner_sentence(out["verdicts"], prim)
    out["arms"] = {}
    for nm, path, cpath in arms:
        try:
            a = score_reduction(card, path, cpath, ok)
            out["arms"][nm] = {"reduction_sha256": a["reduction_sha256"], "kept_passes": a["kept_passes"], "s_float": a["scale"]["s_float"],
                               "verdicts": a["verdicts"], "sizes": a.get("verdicts_size"),
                               "rules": {r: {k: v.get(k) for k in ("verdict", "size", "size_F", "mean_w", "lo95_w", "hi95_w", "rho", "line",
                                                                   "slope_fJ_per_flip", "spread_w", "line_w", "n")}
                                         for r, v in a.get("rules", {}).items()}}
        except Refuse:
            raise
        except Exception as e:  # noqa: BLE001  (an arm that cannot be scored is reported, never the verdict)
            out["arms"][nm] = {"error": f"{type(e).__name__}: {e}"[:400]}
    return out


def owner_sentence(V, prim):
    """A1-1: the owner's sentence is measured only when H-int8 POSITIVE with SIZE PASS, S-int8 POSITIVE, R-int8 PASS and W-int8 PASS"""
    R = prim.get("rules", {})
    parts = {"E178-H-int8": f"{V.get('E178-H-int8')} / SIZE {R.get('E178-H-int8', {}).get('size')}",
             "E178-S-int8": V.get("E178-S-int8"), "E178-R-int8": V.get("E178-R-int8"), "E178-W-int8": V.get("E178-W-int8")}
    met = (V.get("E178-H-int8") == "POSITIVE" and R.get("E178-H-int8", {}).get("size") == "PASS" and V.get("E178-S-int8") == "POSITIVE"
           and V.get("E178-R-int8") == "PASS" and V.get("E178-W-int8") == "PASS")
    return {"measured": met, "parts": parts,
            "reading": ("a matrix of 5s costs more than a matrix of 4s by what the flips and M10's price say, and int8 power follows the "
                        "flips, not the held 1-bits (A1-1)") if met else "not measured: the four rules do not read together (A1-1)"}


def markdown(o):
    pr = o["primary"]
    sc = pr["scale"]
    L = [f"# E178 on {o['card']}: one-number matrices, E178.md section 5's rules and A1's E178-S-int8 (score_e178.py)", "",
         f"Reduction `{pr['reduction']}` ({pr['reduction_sha256'][:12]}); kept passes {pr.get('kept_passes')}; the session's float scale "
         f"s = {float(sc['s_float']):.5f} from {sc['anchors_used']}.", ""]
    if "c_sessions" in o:
        L += [f"Sessions that must carry a C log: {o['c_sessions']['listed']}, all checked to the end: {o['c_sessions']['ok']}; the "
              f"stop-path test {o['c_sessions']['stoptest']}.", ""]
    if o.get("order_as_registered"):
        L += [f"Each kept pass ran plan-e178.json's order: {o['order_as_registered']}.", ""]
    sc_ = o.get("smoke_c") or {}
    if sc_ and "why" not in sc_:
        L += ["The smoke's C, reported (fp32.e178_uf must read +0 throughout; int8.e178_v85 and int8.e178_v127 wrap): " +
              "; ".join(f"{k} {v.get('PASS')}/{v.get('launches')}" for k, v in sorted(sc_.items())) + ".", ""]
    L += ["| rule | verdict | SIZE (P / F) | reading | interval or line | n |", "|---|---|---|---|---|---|"]
    for r in RULES:
        v = pr.get("rules", {}).get(r, {})
        size = f"{v.get('size')} / {v.get('size_F')}" if "size" in v else ""
        if "mean_w" in v:
            rd, ln = f"{v['mean_w']:+.4f} W (dP {v['dP_w']:+.4f}, dF {v['dF_w']:+.4f})", f"[{v['lo95_w']:+.4f}, {v['hi95_w']:+.4f}]"
        elif "rho" in v:
            rd, ln = f"rho {v['rho']:+.3f}", f">= {v['line']:.3f}"
        elif "slope_fJ_per_flip" in v:
            rd, ln = f"{v['slope_fJ_per_flip']:.2f} fJ/flip (P {v['line_fJ']:.2f})", f"[{v['lo95_fJ']:.2f}, {v['hi95_fJ']:.2f}]"
        elif "spread_w" in v:
            rd, ln = f"spread {v['spread_w']:.4f} W", f"<= {v['line_w']:.4f}"
        elif r == "E178-C":
            rd, ln = f"{v.get('PASS')} of {v.get('launches')} launches PASS; left out {v.get('c_excluded')}", ""
        else:
            rd, ln = v.get("why", ""), ""
        L.append(f"| {r} | {o['verdicts'].get(r)} | {size} | {rd} | {ln} | {v.get('n', '')} |")
    b = pr.get("rules", {}).get("beside: 127 - neg_ones", {})
    if "mean_w" in b:
        L += ["", f"Beside, never a verdict: 127 - neg_ones {b['mean_w']:+.4f} W [{b['lo95_w']:+.4f}, {b['hi95_w']:+.4f}] (dP {b['dP_w']:+.4f})."]
    L += ["", f"The owner's sentence (A1-1): {o['owner_sentence']['reading']}."]
    L += ["", "SIZE: FAIL HIGH = the forecast above the measured interval (the model prices more than the card reads); FAIL LOW = below."]
    if o.get("arms"):
        L += ["", "Arms (reported beside, never the verdict):", ""]
        for nm, a in o["arms"].items():
            L.append(f"- {nm}: " + (a.get("error") or ", ".join(f"{r} {v}" for r, v in a["verdicts"].items())))
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("--card", required=True, choices=sorted(CD))
    s.add_argument("--reduction", required=True)
    s.add_argument("--runs-csv", required=True)
    s.add_argument("--raw", required=True)
    s.add_argument("--ccheck", required=True)
    s.add_argument("--arm", action="append", default=[])
    s.add_argument("--since", type=float)
    s.add_argument("--json")
    s.add_argument("--md")
    a = ap.parse_args(argv)
    try:
        arms = []
        for x in a.arm:
            nm, rest = x.split("=", 1)
            j, c = rest.split(",", 1)
            arms.append((nm, os.path.abspath(j), os.path.abspath(c)))
        o = score_session(a.card, os.path.abspath(a.reduction), os.path.abspath(a.runs_csv), os.path.abspath(a.raw), os.path.abspath(a.ccheck),
                          arms, a.since)
    except Refuse as e:
        print(f"REFUSED (exit {e.code}): {e}")
        return e.code
    if a.json:
        open(a.json, "w").write(json.dumps(o, indent=1, sort_keys=True, default=str) + "\n")
    if a.md:
        open(a.md, "w").write(markdown(o))
        print("results.md written")
    print(json.dumps(o["verdicts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
