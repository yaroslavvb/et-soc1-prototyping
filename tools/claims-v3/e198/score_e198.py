#!/usr/bin/env python3
"""E198's scorer: THE TRANSPORT RULES (E198.md 5), frozen before any card-1 X04 datum, with its self-tests.

It reads E198's frozen forecast (forecast-e198.json beside it, refused unless at its pinned sha256: E193's committed
prices on aifoundry3 card 0) and aifoundry1 card 1's outputs of the SAME registered reducer
(tools/claims-v3/e193/proposal/src/reduce_x04.py, unchanged; one file a sitting), and scores every registered price:

  price      sitting A: 16 arms' board W over idle (arms.<arm>.board_w, SE board_se) and 6 trains' board contrast
             (trains.<train>.contrast_board_w, SE board_se); sitting B: 14 arms' board W over idle. 36 in all.
  decided    card 1's arm or train is in its sitting's output with 4 or more measured passes and an SE (and the
             forecast's SE exists); otherwise NOT DECIDED, with the reason. The reducer's n counts measured passes for
             every price but the anchor spin2, whose n counts its runs (5 a pass in sitting A, 2 in B: 40 and 16 on
             aifoundry3), so spin2 needs n >= 20 in A and n >= 8 in B, four passes' worth of its runs (changed before the
             land and before any datum, Mon 16 Nov 2026, Q191 lane fix-e198: verify-e198's finding 1; the first form
             compared spin2's n of runs with 4).
  h          1.96 x sqrt(se1^2 + se3^2): the two values' combined 95 % interval (the registered reducer's own form for
             its nulls, reduce_x04.py lines 386-388).
  E198-T1    the price holds if |v1 - v3| <= h.
  E198-T2    the price holds if v1 lies in [min(s_lo v3, s_hi v3) - h, max(s_lo v3, s_hi v3) + h], [s_lo, s_hi] the
             forecast's scale band (0.952, 1.144: E189's and E191's six configurations, card 1 / aifoundry3).
  verdict    over the 36: FAIL if 8 or more decided prices miss; else PASS if 18 or more are decided and at least 80 %
             of the decided ones hold; FAIL if 18 or more are decided and fewer than 80 % hold; else NOT DECIDED.
             Per sitting, REPORTED: the same share, decided from half the sitting's prices, FAIL from the least number
             of misses that leaves under 80 % of the sitting's prices able to hold (A 5 of 22, B 3 of 14).

REPORTED, never scored (they decide nothing): the minion rail of every arm and train under the same arithmetic; the 7 fits'
slopes and intercepts with SEs propagated from each card's own points (x and point_se_w, the reducer's unweighted line);
the fitted scale (weighted least squares through the origin of card 1's decided board prices on aifoundry3's, weights
1/(se1^2 + se3^2)) with the share within h of it and the ratios' median; the anchor arms' ratios and the rail volts' ratio.

usage (from the repository's top; standard library only):
  python3 -I -B tools/claims-v3/e198/score_e198.py score --a card1-a.json [--b card1-b.json] --out scores-e198.json
  python3 -I -B tools/claims-v3/e198/score_e198.py --selftest-self OUT.json    # aifoundry3 against itself: PASS, PASS
  python3 -I -B tools/claims-v3/e198/score_e198.py --selftest-shift OUT.json   # stand-ins with stated verdicts
  python3 -I -B tools/claims-v3/e198/score_e198.py --selftest-mc OUT.json      # size and power (REPORTED)
A sitting card 1 did not run is simply not given (its prices NOT DECIDED). The scorer never refits a price and never
reads a sealed forecast.
"""
import copy
import hashlib
import json
import math
import os
import random
import statistics
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
FORECAST = os.path.join(HERE, "forecast-e198.json")
FORECAST_SHA256 = "524f49ad661a419f8372d2c443227b4e33fc9425a25f1bbcc8e2a70431cb2bf7"
# The registered measured passes a sitting (E198.md 4 and 5: "half the registered 8") and each price's runs a pass: the reducer's
# n counts passes for every arm and train but the anchor spin2, whose n counts its runs (E193's protocol: 5 a pass in sitting A,
# 2 in B). A price is decided at n >= n_min x its runs a pass, that is 4 measured passes for every price (fix-e198, Q191, before
# any datum: verify-e198's finding 1). load_forecast() refuses a forecast whose n_a3 is not 8 x this for every entry.
PASSES_REGISTERED = 8
RUNS_PER_PASS = {("A", "arm", "spin2"): 5, ("B", "arm", "spin2"): 2}


def runs_per_pass(sitting, kind, key):
    return RUNS_PER_PASS.get((sitting, kind, key), 1)


def passes_of(n, rpp):
    """the measured passes in a reducer n of runs at rpp runs a pass (0 for an n that is not a count)"""
    return n // rpp if isinstance(n, int) and not isinstance(n, bool) else 0


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_forecast():
    got = sha256(FORECAST)
    if got != FORECAST_SHA256:
        sys.exit("REFUSED: forecast-e198.json sha256 %s, pinned %s" % (got, FORECAST_SHA256))
    F = json.load(open(FORECAST))
    for p in F["prices"] + F["reported_rail"]:
        if p["n_a3"] != PASSES_REGISTERED * runs_per_pass(p["sitting"], p["kind"], p["key"]):
            sys.exit("REFUSED: %s n_a3 %s is not %d passes x its runs a pass (%d)" % (
                p["id"], p["n_a3"], PASSES_REGISTERED, runs_per_pass(p["sitting"], p["kind"], p["key"])))
    return F


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def lookup(c1, p, field=None, se_field=None):
    """card 1's (value, se, n, why) for forecast entry p from its sitting's reducer output (or None)"""
    if c1 is None:
        return None, None, None, "sitting %s: no card-1 output" % p["sitting"]
    group = c1.get("arms" if p["kind"] == "arm" else "trains") or {}
    rec = group.get(p["key"])
    if rec is None:
        return None, None, None, "%s %s absent from card 1's sitting %s output" % (p["kind"], p["key"], p["sitting"])
    v, s, n = rec.get(field or p["field"]), rec.get(se_field or p.get("se_field", "board_se")), rec.get("n")
    return v, s, n, ""


def judge(v1, s1, n_c1, v3, s3, rules, why="", rpp=1):
    """rpp: the price's runs a pass (runs_per_pass); n_c1 is the reducer's n, decided at n_min x rpp"""
    band = rules["scale_band"]
    out = {"v1": v1, "se1": s1, "n_c1": n_c1, "v3": v3, "se3": s3}
    if not why:
        if not (finite(v1) and finite(v3)):
            why = "a value missing or not a number"
        elif not isinstance(n_c1, int) or n_c1 < rules["n_min"] * rpp:
            why = ("card 1 has %s measured passes, fewer than %d" % (n_c1, rules["n_min"]) if rpp == 1 else
                   "card 1 has n %s of the anchor's runs (%d a pass), fewer than %d: under %d measured passes" % (
                       n_c1, rpp, rules["n_min"] * rpp, rules["n_min"]))
        elif not (finite(s1) and finite(s3)):
            why = "an SE missing"
    if why:
        out.update(decided=False, why=why, h=None, t1=None, t2=None)
        return out
    h = rules["z"] * math.hypot(s1, s3)
    lo, hi = sorted((band[0] * v3, band[1] * v3))
    out.update(decided=True, why="", h=h, t1=abs(v1 - v3) <= h, t2=(lo - h) <= v1 <= (hi + h),
               t2_band=[lo - h, hi + h], ratio=(v1 / v3 if abs(v3) >= 0.5 else None))
    return out


def verdict(rows, n_reg, rules):
    """the registered verdict over n_reg registered prices, from the per-price rows (each with decided, t)"""
    share = Fraction(str(rules["share"]))
    d = sum(1 for r in rows if r["decided"])
    h = sum(1 for r in rows if r["decided"] and r["t"])
    m = d - h
    fail_m = next(k for k in range(n_reg + 1) if (n_reg - k) < share * n_reg)
    d_min = math.ceil(n_reg / 2)
    if m >= fail_m:
        v = "FAIL"
    elif d >= d_min:
        v = "PASS" if h >= share * d else "FAIL"
    else:
        v = "NOT DECIDED"
    return {"verdict": v, "registered": n_reg, "decided": d, "hold": h, "miss": m, "not_decided": n_reg - d,
            "fail_at_misses": fail_m, "decided_min": d_min, "share": rules["share"]}


def fit_se(f):
    """slope and intercept SEs of the reducer's unweighted line through (x, y) with point SEs (independent points)"""
    x, s = f.get("x") or [], f.get("point_se_w") or []
    if len(x) < 2 or len(x) != len(s):
        return None, None
    xb = sum(x) / len(x)
    sxx = sum((xi - xb) ** 2 for xi in x)
    if sxx <= 0:
        return None, None
    c = [(xi - xb) / sxx for xi in x]
    se_b = math.sqrt(sum((ci * si) ** 2 for ci, si in zip(c, s)))
    se_a = math.sqrt(sum(((1.0 / len(x) - xb * ci) * si) ** 2 for ci, si in zip(c, s)))
    return se_b, se_a


def score(F, c1a, c1b, files=None):
    rules = F["rules"]
    C = {"A": c1a, "B": c1b}
    if rules["registered_prices"] != len(F["prices"]):
        sys.exit("REFUSED: the forecast's price count")
    rows = []
    for p in F["prices"]:
        v1, s1, n_c1, why = lookup(C[p["sitting"]], p)
        r = judge(v1, s1, n_c1, p["v3"], p["se3"], rules, why, runs_per_pass(p["sitting"], p["kind"], p["key"]))
        r.update(id=p["id"], sitting=p["sitting"], kind=p["kind"], key=p["key"], n_a3=p["n_a3"])
        rows.append(r)
    verdicts = {}
    for rule, key in (("E198-T1", "t1"), ("E198-T2", "t2")):
        rr = [dict(decided=r["decided"], t=r[key]) for r in rows]
        verdicts[rule] = verdict(rr, rules["registered_prices"], rules)
        for sit in ("A", "B"):
            sr = [dict(decided=r["decided"], t=r[key]) for r in rows if r["sitting"] == sit]
            verdicts[rule]["sitting_" + sit + "_REPORTED"] = verdict(sr, len(sr), rules)
    # REPORTED: the fitted scale over decided board prices
    dec = [r for r in rows if r["decided"]]
    fitted = {}
    if dec:
        w = [1.0 / (r["se1"] ** 2 + r["se3"] ** 2) for r in dec]
        sw = sum(wi * r["v3"] ** 2 for wi, r in zip(w, dec))
        if sw > 0:
            s_hat = sum(wi * r["v1"] * r["v3"] for wi, r in zip(w, dec)) / sw
            within = sum(1 for r in dec if abs(r["v1"] - s_hat * r["v3"]) <= r["h"])
            ratios = [r["ratio"] for r in dec if r["ratio"] is not None]
            fitted = {"s_hat": s_hat, "s_hat_se": 1.0 / math.sqrt(sw), "decided": len(dec), "within_h_of_s_hat": within,
                      "ratio_median_abs_v3_ge_0.5": statistics.median(ratios) if ratios else None,
                      "ratio_min": min(ratios) if ratios else None, "ratio_max": max(ratios) if ratios else None,
                      "ratios_n": len(ratios)}
    # REPORTED: the minion rail
    rail = []
    for p in F["reported_rail"]:
        v1, s1, n_c1, why = lookup(C[p["sitting"]], p)
        r = judge(v1, s1, n_c1, p["v3"], p["se3"], rules, why, runs_per_pass(p["sitting"], p["kind"], p["key"]))
        r.update(id=p["id"])
        rail.append(r)
    rail_v = {}
    for rule, key in (("T1", "t1"), ("T2", "t2")):
        rail_v[rule] = verdict([dict(decided=r["decided"], t=r[key]) for r in rail], len(rail), rules)
    # REPORTED: the fits, slopes and intercepts with propagated SEs
    fits = []
    for k, f3 in sorted(F["reported_fits"].items()):
        sit, _, name = k.split("/")
        f1 = ((C[sit] or {}).get("fits") or {}).get(name)
        b3, a3 = fit_se(f3)
        for part, v3, s3 in (("slope", f3["slope_w"], b3), ("intercept", f3["intercept_w"], a3)):
            if f1 is None:
                r = judge(None, None, None, v3, s3, rules, "fit %s absent from card 1's sitting %s output" % (name, sit))
            else:
                b1, a1 = fit_se(f1)
                # each arm's measured passes (the anchor's runs over its runs a pass), the fewest of the fit's arms
                n_c1 = min(passes_of((((C[sit] or {}).get("arms") or {}).get(a) or {}).get("n"), runs_per_pass(sit, "arm", a))
                           for a in f1.get("arms", [])) if f1.get("arms") else None
                r = judge(f1["slope_w"] if part == "slope" else f1["intercept_w"], b1 if part == "slope" else a1,
                          n_c1, v3, s3, rules)
            r.update(id="%s/%s" % (k, part))
            fits.append(r)
    # REPORTED: the anchor arms and the minion rail's volts
    anchors = {}
    for sit, arm in (("A", "spin2"), ("B", "spin2"), ("B", "faddps_p1"), ("B", "fsgnjs_p1")):
        r = next((x for x in rows if x["id"] == "%s/arm/%s" % (sit, arm)), None)
        if r and r["decided"]:
            anchors["%s/%s" % (sit, arm)] = {"ratio": r["v1"] / r["v3"], "v1": r["v1"], "v3": r["v3"]}
    volts = {}
    for sit in ("A", "B"):
        x = C[sit]
        if x and x.get("arms"):
            v1 = [a.get("minion_v") for a in x["arms"].values() if finite(a.get("minion_v"))]
            if v1:
                volts[sit] = {"card1_minion_v_mean": statistics.fmean(v1),
                              "aifoundry3_minion_v": 0.523,
                              "ratio_squared": (statistics.fmean(v1) / 0.523) ** 2}
    out = {"what": "E198 scored by score_e198.py: THE TRANSPORT RULES (E198.md 5) over E198's frozen forecast; every "
                   "per-price figure is the registered reducer's (card 1) or E193's committed (aifoundry3)",
           "forecast_sha256": FORECAST_SHA256, "card1_files": files or {}, "rules": rules,
           "verdicts": {k: v["verdict"] for k, v in verdicts.items()}, "rule_counts": verdicts, "prices": rows,
           "REPORTED": {"fitted_scale": fitted, "rail": {"verdicts_REPORTED": rail_v, "prices": rail},
                        "fits": fits, "anchors": anchors, "minion_volts": volts}}
    return out


def lines(res):
    L = []
    for r in res["prices"]:
        if r["decided"]:
            L.append("%-26s card1 %9.4f +- %.4f (n %2d)  a3 %9.4f +- %.4f  h %.4f  T1 %-4s T2 %-4s" % (
                r["id"], r["v1"], r["se1"], r["n_c1"], r["v3"], r["se3"], r["h"],
                "ok" if r["t1"] else "MISS", "ok" if r["t2"] else "MISS"))
        else:
            L.append("%-26s NOT DECIDED: %s" % (r["id"], r["why"]))
    for k in ("E198-T1", "E198-T2"):
        c = res["rule_counts"][k]
        L.append("%s: %s (decided %d of %d, hold %d, miss %d)" % (k, c["verdict"], c["decided"], c["registered"],
                                                                  c["hold"], c["miss"]))
        for sit in ("A", "B"):
            s = c["sitting_%s_REPORTED" % sit]
            L.append("  sitting %s (REPORTED): %s (decided %d of %d, hold %d, miss %d)" % (
                sit, s["verdict"], s["decided"], s["registered"], s["hold"], s["miss"]))
    f = res["REPORTED"]["fitted_scale"]
    if f:
        L.append("REPORTED fitted scale %.4f +- %.4f; %d of %d decided prices within h of it; ratio median %s" % (
            f["s_hat"], f["s_hat_se"], f["within_h_of_s_hat"], f["decided"],
            "%.4f" % f["ratio_median_abs_v3_ge_0.5"] if f["ratio_median_abs_v3_ge_0.5"] is not None else "-"))
    rv = res["REPORTED"]["rail"]["verdicts_REPORTED"]
    L.append("REPORTED minion rail: T1 %s (hold %d of %d decided), T2 %s (hold %d)" % (
        rv["T1"]["verdict"], rv["T1"]["hold"], rv["T1"]["decided"], rv["T2"]["verdict"], rv["T2"]["hold"]))
    L.append("VERDICTS: E198-T1 %s, E198-T2 %s" % (res["verdicts"]["E198-T1"], res["verdicts"]["E198-T2"]))
    return L


# ---------------------------------------------------------------------------------------------------------- self-tests
def e193_outputs(F):
    out = {}
    for p, h in F["inputs"].items():
        if p.endswith("/x04-e193-A.json") or p.endswith("/x04-e193-B.json"):
            if sha256(p) != h:
                sys.exit("REFUSED: %s not at its pin" % p)
            out["A" if p.endswith("A.json") else "B"] = json.load(open(p))
    return out["A"], out["B"]


def stand_in(x, scale=1.0, add=0.0, n=None, arms_scale=None):
    """a card-1 stand-in in the reducer's form from E193's output: board and minion values (and SEs) scaled, an offset
    added to the arms' board values only (a wrong idle level moves an arm's W over idle; a train's contrast has no idle
    subtraction), n set; arms_scale maps a key to its own factor"""
    y = copy.deepcopy(x)
    for grp, vf, mf in (("arms", "board_w", "minion_w"), ("trains", "contrast_board_w", "contrast_minion_w")):
        for k, r in y[grp].items():
            s = (arms_scale or {}).get(k, scale)
            r[vf] = r[vf] * s + (add if grp == "arms" else 0.0)
            r[mf] = r[mf] * s
            for se in ("board_se", "minion_se"):
                if r.get(se) is not None:
                    r[se] = r[se] * s
            if n is not None:
                r["n"] = n
    return y


def selftest_self(path):
    F = load_forecast()
    a, b = e193_outputs(F)
    res = score(F, a, b, {"A": "E193's committed x04-e193-A.json", "B": "E193's committed x04-e193-B.json"})
    want = {"E198-T1": "PASS", "E198-T2": "PASS"}
    c1, c2 = res["rule_counts"]["E198-T1"], res["rule_counts"]["E198-T2"]
    ok = res["verdicts"] == want and c1["hold"] == 36 and c2["hold"] == 36 and c1["decided"] == 36 \
        and abs(res["REPORTED"]["fitted_scale"]["s_hat"] - 1.0) < 1e-12
    out = {"what": "aifoundry3 against itself: E193's committed outputs given as card 1's (stated before the run: "
                   "E198-T1 PASS and E198-T2 PASS, 36 of 36 holding each, the fitted scale 1)",
           "expected": want, "got": res["verdicts"], "counts": {"T1": c1, "T2": c2},
           "fitted_scale": res["REPORTED"]["fitted_scale"], "verdict": "PASS" if ok else "FAIL"}
    json.dump(out, open(path, "w"), indent=1, sort_keys=True)
    open(path, "a").write("\n")
    for l in lines(res)[-8:]:
        print(l)
    print("SELFTEST-SELF %s" % out["verdict"])
    return 0 if ok else 1


SCENARIOS = [
    # name, words, builder(a, b) -> (c1a, c1b), expected T1, expected T2
    ("S1 x1.10", "every price and SE x 1.10: a card scale inside T2's band",
     lambda a, b: (stand_in(a, 1.10), stand_in(b, 1.10)), "FAIL", "PASS"),
    ("S2 x1.30", "x 1.30: outside the band", lambda a, b: (stand_in(a, 1.30), stand_in(b, 1.30)), "FAIL", "FAIL"),
    ("S3 x0.90", "x 0.90: the voltage ratio's side, outside the band",
     lambda a, b: (stand_in(a, 0.90), stand_in(b, 0.90)), "FAIL", "FAIL"),
    ("S4 +0.20 W", "0.20 W added to every arm's board price (a wrong idle level), the trains and the SEs unchanged",
     lambda a, b: (stand_in(a, add=0.20), stand_in(b, add=0.20)), "FAIL", "FAIL"),
    ("S5 B absent", "sitting A exactly aifoundry3's, sitting B not run", lambda a, b: (stand_in(a), None), "PASS", "PASS"),
    ("S6 n 3", "every arm and train with 3 measured passes", lambda a, b: (stand_in(a, n=3), stand_in(b, n=3)),
     "NOT DECIDED", "NOT DECIDED"),
    ("S7 A short", "sitting A with 3 measured passes, B exact: 14 decided", lambda a, b: (stand_in(a, n=3), stand_in(b)),
     "NOT DECIDED", "NOT DECIDED"),
    ("S8 eight misses", "B absent; 8 of A's arms x 2 and A's other 14 prices with 3 passes: 8 decided, 8 missing",
     lambda a, b: (eight_misses(a), None), "FAIL", "FAIL"),
    ("S9 x1.02", "x 1.02: T1's resolution (30 of 36 hold, at the 80 % bar's 29)",
     lambda a, b: (stand_in(a, 1.02), stand_in(b, 1.02)), "PASS", "PASS"),
    ("S10 x0.952", "the band's lower edge", lambda a, b: (stand_in(a, 0.952), stand_in(b, 0.952)), "FAIL", "PASS"),
    ("S11 x1.144", "the band's upper edge", lambda a, b: (stand_in(a, 1.144), stand_in(b, 1.144)), "FAIL", "PASS"),
    ("S12 x0.94", "x 0.94 (the catalogue's no-op row's ratio): just outside the band, T2 still holds 32 of 36",
     lambda a, b: (stand_in(a, 0.94), stand_in(b, 0.94)), "FAIL", "PASS"),
    ("S13 one arm gone", "A's duty33k absent (its runs dropped by the reducer's gates), the rest exact",
     lambda a, b: (drop(a, "arms", "duty33k"), stand_in(b)), "PASS", "PASS"),
    # Added before the land (fix-e198, Q191): the anchor's decided rule in passes (verify-e198's finding 1), each with its decided
    # count stated before the run as well as its verdicts.
    ("S14 spin2 short", "verify-e198's case C14: A with 4 far misses, B cut at 2 passes (n 2; the anchor spin2 n 4, its runs) "
     "with spin2 far off: spin2 has 2 measured passes in B, NOT DECIDED; 22 decided, 18 hold (81.8 %); the first form decided "
     "spin2 and read FAIL, FAIL (18 of 23)", lambda a, b: spin2_short(a, b), "PASS", "PASS", 22),
    ("S15 spin2 at 4", "every arm and train with 4 measured passes, the anchor spin2 n 20 in A and 8 in B (4 passes of its "
     "runs), every value exact: 36 decided", lambda a, b: (anchor_n(a, 4, 20), anchor_n(b, 4, 8)), "PASS", "PASS", 36),
    ("S16 spin2 a run short", "as S15 but spin2 n 19 in A and 7 in B (a run dropped by a reducer gate): spin2 NOT DECIDED in "
     "both sittings, 34 decided", lambda a, b: (anchor_n(a, 4, 19), anchor_n(b, 4, 7)), "PASS", "PASS", 34),
]


def anchor_n(x, n, n_anchor):
    y = stand_in(x, n=n)
    y["arms"]["spin2"]["n"] = n_anchor
    return y


def spin2_short(a, b):
    y = stand_in(a)
    for k in sorted(y["arms"])[:4]:
        y["arms"][k]["board_w"] = a["arms"][k]["board_w"] * 2.0 + 1.0
    z = anchor_n(b, 2, 4)
    z["arms"]["spin2"]["board_w"] = b["arms"]["spin2"]["board_w"] * 2.0 + 1.0
    return y, z


def eight_misses(a):
    y = stand_in(a, n=3)
    for k in sorted(y["arms"])[:8]:
        r = y["arms"][k]
        r["n"] = a["arms"][k]["n"]
        r["board_w"] = a["arms"][k]["board_w"] * 2.0 + 1.0
    return y


def drop(a, grp, key):
    y = stand_in(a)
    del y[grp][key]
    return y


def selftest_shift(path):
    F = load_forecast()
    a, b = e193_outputs(F)
    out = {"what": "stand-ins in the reducer's form made from E193's committed outputs, each verdict stated before the run",
           "scenarios": []}
    ok = True
    for name, words, mk, w1, w2, *want_d in SCENARIOS:
        c1a, c1b = mk(a, b)
        res = score(F, c1a, c1b)
        got = (res["verdicts"]["E198-T1"], res["verdicts"]["E198-T2"])
        c1, c2 = res["rule_counts"]["E198-T1"], res["rule_counts"]["E198-T2"]
        good = got == (w1, w2) and (not want_d or c1["decided"] == c2["decided"] == want_d[0])
        ok &= good
        row = {"name": name, "words": words, "expected": [w1, w2], "got": list(got), "pass": good,
               "T1": {k: c1[k] for k in ("decided", "hold", "miss")},
               "T2": {k: c2[k] for k in ("decided", "hold", "miss")}}
        if want_d:
            row["expected_decided"] = want_d[0]
        out["scenarios"].append(row)
        print("%-16s expected T1 %-11s T2 %-11s got %-11s %-11s (T1 hold %2d/%2d, T2 hold %2d/%2d) %s" % (
            name, w1, w2, got[0], got[1], c1["hold"], c1["decided"], c2["hold"], c2["decided"],
            "ok" if good else "WRONG"))
    out["verdict"] = "PASS" if ok else "FAIL"
    json.dump(out, open(path, "w"), indent=1, sort_keys=True)
    open(path, "a").write("\n")
    print("SELFTEST-SHIFT %s (%d scenarios)" % (out["verdict"], len(SCENARIOS)))
    return 0 if ok else 1


def halves(x, sel):
    out = {}
    for r in x["runs"]:
        if r["pass"] > 0 and r["ok"] and sel(r["pass"]):
            out.setdefault(("arm", r["arm"]), []).append(r["over_idle_w"])
    for r in x["trains_runs"]:
        if r["pass"] > 0 and r["ok"] and sel(r["pass"]):
            out.setdefault(("train", r["train"]), []).append(r["contrast_board_w"])
    return {k: (statistics.fmean(v), statistics.stdev(v) / math.sqrt(len(v)), len(v)) for k, v in out.items()}


def selftest_mc(path):
    F = load_forecast()
    rules = F["rules"]
    a, b = e193_outputs(F)
    rep = {"what": "REPORTED desk arithmetic (decides nothing): the rules' size and power on the forecast's own SEs, "
                   "and aifoundry3 against itself by halves of each sitting", "rules": rules}
    split = {}
    for name, s1, s3 in (("passes 1-4 against 5-8", lambda p: p <= 4, lambda p: p >= 5),
                         ("odd against even passes", lambda p: p % 2 == 1, lambda p: p % 2 == 0)):
        rows = []
        for x in (a, b):
            h1, h3 = halves(x, s1), halves(x, s3)
            for k in sorted(h1):
                rows.append(judge(h1[k][0], h1[k][1], h1[k][2], h3[k][0], h3[k][1], rules))
        split[name] = {"T1": verdict([dict(decided=r["decided"], t=r["t1"]) for r in rows], len(rows), rules),
                       "T2": verdict([dict(decided=r["decided"], t=r["t2"]) for r in rows], len(rows), rules)}
        print("split %-24s T1 %s (hold %d of %d)  T2 %s (hold %d)" % (
            name, split[name]["T1"]["verdict"], split[name]["T1"]["hold"], split[name]["T1"]["decided"],
            split[name]["T2"]["verdict"], split[name]["T2"]["hold"]))
    rep["split_halves_aifoundry3"] = split
    rng = random.Random(198)
    N = 2000
    mc = []
    P = F["prices"]
    for s in (0.90, 0.92, 0.94, 0.96, 0.98, 1.00, 1.02, 1.04, 1.06, 1.10, 1.144, 1.16, 1.20):
        pass1 = pass2 = 0
        h1s, h2s = [], []
        for _ in range(N):
            rows = []
            for p in P:
                se1 = s * p["se3"]
                v1 = s * p["v3"] + rng.gauss(0.0, math.hypot(se1, s * p["se3"]))
                rows.append(judge(v1, se1, 8, p["v3"], p["se3"], rules))
            c1 = verdict([dict(decided=r["decided"], t=r["t1"]) for r in rows], len(rows), rules)
            c2 = verdict([dict(decided=r["decided"], t=r["t2"]) for r in rows], len(rows), rules)
            pass1 += c1["verdict"] == "PASS"; pass2 += c2["verdict"] == "PASS"
            h1s.append(c1["hold"]); h2s.append(c2["hold"])
        mc.append({"scale": s, "T1_pass_rate": pass1 / N, "T2_pass_rate": pass2 / N,
                   "T1_hold_median": statistics.median(h1s), "T2_hold_median": statistics.median(h2s)})
        print("MC s %.3f: T1 PASS rate %.3f (median hold %.0f)  T2 PASS rate %.3f (median hold %.0f)" % (
            s, pass1 / N, statistics.median(h1s), pass2 / N, statistics.median(h2s)))
    rep["monte_carlo"] = {"draws": N, "seed": 198,
                          "model": "card 1 = s x v3 + N(0, sqrt(se1^2 + (s se3)^2)), se1 = s x se3, card 1 with 8 passes",
                          "rows": mc}
    json.dump(rep, open(path, "w"), indent=1, sort_keys=True)
    open(path, "a").write("\n")
    print("SELFTEST-MC DONE (REPORTED)")
    return 0


def main(argv):
    if len(argv) == 2 and argv[0] == "--selftest-self":
        return selftest_self(argv[1])
    if len(argv) == 2 and argv[0] == "--selftest-shift":
        return selftest_shift(argv[1])
    if len(argv) == 2 and argv[0] == "--selftest-mc":
        return selftest_mc(argv[1])
    if argv and argv[0] == "score":
        args = dict(zip(argv[1::2], argv[2::2]))
        if "--a" not in args and "--b" not in args or "--out" not in args or len(argv) % 2 != 1:
            sys.exit(__doc__)
        F = load_forecast()
        c1 = {}
        files = {}
        for sit in ("A", "B"):
            p = args.get("--" + sit.lower())
            if p:
                c1[sit] = json.load(open(p))
                files[sit] = {"path": p, "sha256": sha256(p)}
        res = score(F, c1.get("A"), c1.get("B"), files)
        json.dump(res, open(args["--out"], "w"), indent=1, sort_keys=True)
        open(args["--out"], "a").write("\n")
        for l in lines(res):
            print(l)
        return 0
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
