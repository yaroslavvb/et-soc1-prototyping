#!/usr/bin/env python3
"""E199's transport scorer (E199.md section 6), written and self-tested before any card-1 X01 datum. Standard library only.

    score_e199.py score <card-1 intbits.json> --out <scores-e199.json> [--checks <card-1 checks.json>]
        the day, after E199's data commit: the reducer's output for card 1 (E192's reduce_intbits.py at 715fddaa..., unchanged, run on
        the session's run directory after prefilter_e199.py) scored against forecast-e199.json; refuses unless every entry of
        SHA256SUMS-e199-registration matches from the top of the tree
    score_e199.py --selftest <selftest-e199.json>
        the self-tests of section 6.7: E192 against itself (must PASS), shifted stand-ins (must FAIL), the share's two edges, the three
        ways a price is NOT DECIDED, NO DATA, a scale at the allowance's edge; every expected verdict is written in CASES below

THE RULES (E199.md section 6; the constants are read from forecast-e199.json > rules and > allowance, never typed here):
  For each registered price of a family, m3 +- se3 is E192's (aifoundry3 card 0) and m1 +- se1 (over its measured passes) is card 1's.
  DECIDED: card 1 has the price with at least 4 measured passes (> rules > n_min) and an SE, and se1 <= 3 x se3; otherwise NOT DECIDED (the
      reason recorded). The first form admitted 2 passes; 4 since Mon 16 Nov 2026, before any datum (verify-e199 F3, lane fix-e199): with
      no card difference the family T1 rule failed about half the time at 2 passes (E199.md 6.2, 6.8).
  T1 (per price): |m1 - m3| <= 2 sqrt(se1^2 + se3^2) - card 1's value within the two values' combined 95% interval.
  T2 (per price): |m1 - s* m3| <= 2 sqrt(se1^2 + (s* se3)^2), where s* is the family's ONE card-to-card scale in the allowance
      [s_lo, s_hi] (which holds 1) under which the most of the family's decided prices hold (found exactly: the count is evaluated at
      the allowance's ends, at 1, at the clipped s_hat, at every solution of every price's boundary equation inside the allowance and at the
      midpoints between them; ties go to the value nearest the clipped s_hat, then nearest 1, then the smallest). So T2 never holds
      fewer prices than T1. THE SCALE: the weighted least-squares s_hat = sum(w m1 m3) / sum(w m3^2), w = 1 / (se1^2 + se3^2), over
      the family's decided prices; its SE is 1 / sqrt(sum(w m3^2)), times sqrt(chi2 / (D - 1)) when that is above 1 (chi2 = sum of
      w (m1 - s_hat m3)^2). THE SCALE HOLDS when s_hat's 95% interval (s_hat +- 2 SE) meets the allowance.
  A family of N prices (K = ceil(0.85 N), F = N - K + 1; D decided, H holding, M missing):
      T1: NO DATA if D = 0; PASS if H >= K; FAIL if M >= F; else NOT DECIDED.
      T2: NO DATA if D = 0; FAIL if M >= F, or if D >= K and the scale does not hold; PASS if H >= K and the scale holds; else NOT
          DECIDED.
  Verdicts: family A (board, per-arm contrasts: THE HEADLINE) E199-T1, E199-T2; family B (board ladders) E199-T1L, E199-T2L; family C
  (rail, per-arm contrasts) E199-T1R, E199-T2R; family D (rail ladders) E199-T1RL, E199-T2RL. R1 and R2 (energies over idle) are
  scored price by price and REPORTED with no verdict.

SPDX-License-Identifier: Apache-2.0
"""
import copy
import hashlib
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FORECAST = os.path.join(HERE, "forecast-e199.json")
LIST = os.path.join(HERE, "SHA256SUMS-e199-registration")
E192_IB = os.path.join(TOP, "docs/reports/data/2026-11-14-e192-intbits-aifoundry3/intbits-e192.json")
FAMILY_IDS = ("A", "B", "C", "D")
REPORTED_IDS = ("R1", "R2")
VERDICT_NAMES = {"A": ("E199-T1", "E199-T2"), "B": ("E199-T1L", "E199-T2L"), "C": ("E199-T1R", "E199-T2R"),
                 "D": ("E199-T1RL", "E199-T2RL")}


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def get(d, path):
    for k in path:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def decide(p, c, rules):
    if not isinstance(c, dict) or not num(c.get("mean")):
        return False, "NOT DECIDED: no card-1 value"
    n, se = c.get("n"), c.get("se")
    n_min = rules["n_min"]
    if not isinstance(n, int) or isinstance(n, bool) or n < n_min or not num(se):
        return False, "NOT DECIDED: fewer than %d measured passes, or no SE" % n_min
    if se > rules["se_ratio_max"] * p["se"]:
        return False, "NOT DECIDED: card 1's SE %.6g above %g x aifoundry3's %.6g" % (se, rules["se_ratio_max"], p["se"])
    return True, ""


def holds_at(r, s, z):
    return abs(r["m1"] - s * r["m3"]) <= z * math.sqrt(r["se1"] ** 2 + (s * r["se3"]) ** 2)


def best_scale(dec, z, s_lo, s_hi, s_clip):
    """The scale in [s_lo, s_hi] under which the most decided prices hold T2's test, found exactly (the count is piecewise constant
    in s and changes only at a solution of (m3^2 - z^2 se3^2) s^2 - 2 m1 m3 s + (m1^2 - z^2 se1^2) = 0). Returns (s*, candidates read)."""
    pts = {s_lo, s_hi, 1.0, s_clip}
    for r in dec:
        a = r["m3"] ** 2 - z * z * r["se3"] ** 2
        b = -2.0 * r["m1"] * r["m3"]
        c = r["m1"] ** 2 - z * z * r["se1"] ** 2
        roots = []
        if a != 0.0:
            disc = b * b - 4.0 * a * c
            if disc >= 0.0:
                q = math.sqrt(disc)
                roots = [(-b - q) / (2.0 * a), (-b + q) / (2.0 * a)]
        elif b != 0.0:
            roots = [-c / b]
        pts.update(x for x in roots if s_lo <= x <= s_hi)
    srt = sorted(pts)
    pts.update((u + v) / 2.0 for u, v in zip(srt, srt[1:]))
    best = None
    for s in sorted(pts):
        n = sum(1 for r in dec if holds_at(r, s, z))
        key = (-n, abs(s - s_clip), abs(s - 1.0), s)
        if best is None or key < best[0]:
            best = (key, s)
    return (best[1] if best else s_clip), len(pts)


def score_prices(prices, card1, rules, allowance):
    z = rules["z"]
    rows = []
    for p in prices:
        c = get(card1, p["path"])
        ok, why = decide(p, c, rules)
        r = {"key": p["key"], "m3": p["mean"], "se3": p["se"], "decided": ok}
        if isinstance(c, dict):
            r.update({"m1": c.get("mean"), "se1": c.get("se"), "n_card1": c.get("n")})
        if not ok:
            r["why"] = why
        rows.append(r)
    dec = [r for r in rows if r["decided"]]
    den = sum(r["m3"] ** 2 / (r["se1"] ** 2 + r["se3"] ** 2) for r in dec)
    nm = sum(r["m1"] * r["m3"] / (r["se1"] ** 2 + r["se3"] ** 2) for r in dec)
    s_hat = nm / den if den > 0 else 1.0
    s_lo, s_hi = allowance["s_lo"], allowance["s_hi"]
    s_clip = min(max(s_hat, s_lo), s_hi)
    s_star, s_cands = best_scale(dec, z, s_lo, s_hi, s_clip)
    chi2 = sum((r["m1"] - s_hat * r["m3"]) ** 2 / (r["se1"] ** 2 + r["se3"] ** 2) for r in dec)
    if den > 0 and len(dec) >= 2:
        birge = max(1.0, math.sqrt(chi2 / (len(dec) - 1)))
        s_se = birge / math.sqrt(den)
        scale_ok = (s_hat - z * s_se <= s_hi) and (s_hat + z * s_se >= s_lo)
    elif den > 0:
        birge, s_se, scale_ok = None, 1.0 / math.sqrt(den), None
    else:
        birge, s_se, scale_ok = None, None, (True if dec else None)
    for r in dec:
        sd1 = math.sqrt(r["se1"] ** 2 + r["se3"] ** 2)
        d = r["m1"] - r["m3"]
        sd2 = math.sqrt(r["se1"] ** 2 + (s_star * r["se3"]) ** 2)
        res2 = r["m1"] - s_star * r["m3"]
        r.update({"d": d, "sd": sd1, "z_d": d / sd1 if sd1 > 0 else None, "holds_T1": abs(d) <= z * sd1,
                  "ratio": (r["m1"] / r["m3"]) if r["m3"] != 0 else None,
                  "resid_T2": res2, "sd_T2": sd2, "holds_T2": abs(res2) <= z * sd2})
    scale = {"s_hat": s_hat, "s_hat_se": s_se, "birge_ratio": birge, "chi2": chi2, "s_hat_clipped": s_clip, "s_star": s_star,
             "s_star_candidates": s_cands, "allowance": [s_lo, s_hi], "scale_holds": scale_ok}
    return rows, scale


def verdict_t1(D, H, M, K, F):
    if D == 0:
        return "NO DATA"
    if H >= K:
        return "PASS"
    if M >= F:
        return "FAIL"
    return "NOT DECIDED"


def verdict_t2(D, H, M, K, F, scale_ok):
    if D == 0:
        return "NO DATA"
    if M >= F:
        return "FAIL"
    if D >= K and scale_ok is False:
        return "FAIL"
    if H >= K and scale_ok:
        return "PASS"
    return "NOT DECIDED"


def score(forecast, card1):
    rules, allowance = forecast["rules"], forecast["allowance"]
    nm = rules.get("n_min")
    if not isinstance(nm, int) or isinstance(nm, bool) or nm < 2:
        raise SystemExit("REFUSED: the forecast's rules give no n_min (an integer of at least 2)")
    out = {"families": {}, "reported": {}, "verdicts": {}}
    for fid in FAMILY_IDS:
        fam = forecast["families"][fid]
        rows, scale = score_prices(fam["prices"], card1, rules, allowance)
        N, K, F = fam["N"], fam["K"], fam["F"]
        if not (N == len(fam["prices"]) and K == (rules["share_pct"] * N + 99) // 100 and F == N - K + 1):
            raise SystemExit("REFUSED: family %s's N, K, F do not follow the rule" % fid)
        D = sum(1 for r in rows if r["decided"])
        H1 = sum(1 for r in rows if r["decided"] and r["holds_T1"])
        H2 = sum(1 for r in rows if r["decided"] and r["holds_T2"])
        v1 = verdict_t1(D, H1, D - H1, K, F)
        v2 = verdict_t2(D, H2, D - H2, K, F, scale["scale_holds"])
        name1, name2 = VERDICT_NAMES[fid]
        out["verdicts"][name1], out["verdicts"][name2] = v1, v2
        ns = [r["n_card1"] for r in rows if r["decided"]]
        out["families"][fid] = {"meter": fam["meter"], "N": N, "K": K, "F": F, "decided": D,
                                "card1_passes": [min(ns), max(ns)] if ns else None,
                                "T1": {"verdict": v1, "hold": H1, "miss": D - H1},
                                "T2": {"verdict": v2, "hold": H2, "miss": D - H2},
                                "scale": scale, "prices": rows}
    for rid in REPORTED_IDS:
        fam = forecast["reported"][rid]
        rows, scale = score_prices(fam["prices"], card1, rules, allowance)
        D = sum(1 for r in rows if r["decided"])
        out["reported"][rid] = {"meter": fam["meter"], "N": fam["N"], "decided": D, "label": "REPORTED, no verdict",
                                "T1_hold": sum(1 for r in rows if r["decided"] and r["holds_T1"]),
                                "T2_hold": sum(1 for r in rows if r["decided"] and r["holds_T2"]),
                                "scale": scale, "prices": rows}
    return out


def summary_lines(res):
    L = []
    words = {"A": "board, per-arm contrasts (THE HEADLINE)", "B": "board ladders", "C": "core rail, per-arm contrasts",
             "D": "core rail ladders"}
    for fid in FAMILY_IDS:
        f = res["families"][fid]
        sc = f["scale"]
        name1, name2 = VERDICT_NAMES[fid]
        L.append("%s (family %s, %s): %s - %d of %d decided, %d hold, %d miss (PASS at %d, FAIL at %d misses)" % (
            name1, fid, words[fid], f["T1"]["verdict"], f["decided"], f["N"], f["T1"]["hold"], f["T1"]["miss"], f["K"], f["F"]))
        L.append("%s (family %s): %s - %d hold, %d miss at the best scale s* %.6g; s_hat %.6g +- %s, the scale %s [%g, %g]" % (
            name2, fid, f["T2"]["verdict"], f["T2"]["hold"], f["T2"]["miss"], sc["s_star"], sc["s_hat"],
            ("%.4g" % sc["s_hat_se"]) if sc["s_hat_se"] is not None else "-",
            {True: "meets", False: "misses", None: "not read against"}[sc["scale_holds"]], sc["allowance"][0], sc["allowance"][1]))
    for rid in REPORTED_IDS:
        f = res["reported"][rid]
        L.append("%s (REPORTED, %s energies over idle): %d of %d decided, T1 %d hold, T2 %d hold, s_hat %.6g" % (
            rid, f["meter"], f["decided"], f["N"], f["T1_hold"], f["T2_hold"], f["scale"]["s_hat"]))
    v = res["verdicts"]
    L.append("SCORES-E199: " + "; ".join("%s %s" % (k, v[k]) for k in
                                         ("E199-T1", "E199-T2", "E199-T1L", "E199-T2L", "E199-T1R", "E199-T2R", "E199-T1RL",
                                          "E199-T2RL")))
    return L


def verify_list():
    bad = []
    if not os.path.exists(LIST):
        return ["no SHA256SUMS-e199-registration"]
    for line in open(LIST):
        parts = line.split()
        if len(parts) != 2:
            continue
        want, rel = parts
        p = os.path.join(TOP, rel.lstrip("*"))
        got = sha(p) if os.path.exists(p) else "missing"
        if got != want:
            bad.append("%s: %s, not %s" % (rel, got, want))
    return bad


def forecast_matches_builder():
    spec = importlib.util.spec_from_file_location("forecast_e199_here", os.path.join(HERE, "forecast_e199.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return open(FORECAST).read() == mod.dumps(mod.build())


# ---------------------------------------------------------------- the self-tests (section 6.7)
def paths_of(forecast, fids):
    out = []
    for fid in fids:
        grp = forecast["families"] if fid in FAMILY_IDS else forecast["reported"]
        out += [p["path"] for p in grp[fid]["prices"]]
    return out


ALL = FAMILY_IDS + REPORTED_IDS


def stand_in(ib, forecast, how):
    """A card-1 stand-in made from E192's own reducer output: E192's values, transformed. se1 = se3 and 8 passes unless changed."""
    c = copy.deepcopy(ib)
    kind = how[0]
    if kind == "self":
        return c
    if kind == "empty":
        return {}
    if kind == "scale":
        for path in paths_of(forecast, ALL):
            get(c, path)["mean"] *= how[1]
        return c
    if kind == "shift_sigma":            # m1 = m3 + k sqrt(2) se3: k combined SEs when se1 = se3
        for path in paths_of(forecast, ALL):
            r = get(c, path)
            r["mean"] += how[1] * math.sqrt(2.0) * r["se"]
        return c
    if kind == "add_A":
        for path in paths_of(forecast, ("A",)):
            get(c, path)["mean"] += how[1]
        return c
    keysA = [p["key"] for p in forecast["families"]["A"]["prices"]]
    if kind == "move_A":                 # the first n keys of family A (sorted) moved by k combined SEs
        n, k = how[1], how[2]
        for path in paths_of(forecast, ("A",))[:n]:
            r = get(c, path)
            r["mean"] += k * math.sqrt(2.0) * r["se"]
        return c
    if kind == "drop_arms":              # the first n arms of family A absent from card 1's file
        for arm in keysA[:how[1]]:
            del c["arms"][arm]
        return c
    if kind == "se_A":                   # card 1's SE x f on the first n prices of family A
        for path in paths_of(forecast, ("A",))[:how[1]]:
            get(c, path)["se"] *= how[2]
        return c
    if kind == "passes_A":               # n = k measured passes (the SE kept) on the first n prices of family A
        for path in paths_of(forecast, ("A",))[:how[1]]:
            get(c, path)["n"] = how[2]
        return c
    if kind == "passes_all":             # n = k measured passes (the SE kept) on every price: a session cut short
        for path in paths_of(forecast, ALL):
            get(c, path)["n"] = how[1]
        return c
    if kind == "one_pass_A":             # n = 1 and no SE on the first n prices of family A
        for path in paths_of(forecast, ("A",))[:how[1]]:
            r = get(c, path)
            r["n"], r["se"] = 1, None
        return c
    raise SystemExit("unknown stand-in %r" % (how,))


ALL8 = ("E199-T1", "E199-T2", "E199-T1L", "E199-T2L", "E199-T1R", "E199-T2R", "E199-T1RL", "E199-T2RL")
T1S = ("E199-T1", "E199-T1L", "E199-T1R", "E199-T1RL")
T2S = ("E199-T2", "E199-T2L", "E199-T2R", "E199-T2RL")
# Each case: its name, the stand-in, and the verdicts it must give, written before the self-test first ran. The expectations for the
# scaled stand-ins follow from E192's own |mean| / SE (forecast-e199.txt): at x1.25, s* = s_hi and a price misses T2 when
# |m3| / se3 > 13.5 (T1: > 11.3); at least 14 of family A's, 9 of B's and more of C's and D's are; at x0.80 (s* = s_lo, misses
# above 19.2; T1 above 14.1) at least 10, 7, 5 and 4 are, each at or above its family's F (5, 4, 5, 4). At +3 combined SEs every price
# misses T1 (|d| = 3 sd). At +0.30 pJ every family-A price misses T1 (every se3 there is below 0.106 pJ). Moving 4 family-A prices by 5
# combined SEs leaves 27 = K holding (PASS); moving 5 makes 5 = F misses (FAIL). Dropping 8 arms, an SE x4 on 10 prices, or one pass on
# 6 leaves 23, 21 or 25 decided, all holding: under K = 27 with no miss, NOT DECIDED. At x1.10 the fitted scale (about 1.10, SE about
# 0.01 in every family) misses the allowance, so T2 FAILS in every family.
# One expectation was added after the first run, with the one change made to the rules then (E199.md section 6.7): the first form of T2
# took s* as the clipped s_hat, and on EDGE-4 it held 26 prices where T1 held 27 (the four moved prices pulled s_hat to 1.049); s* is
# now the allowed scale under which the most prices hold, so T2 never holds fewer than T1, and EDGE-4's T2 must PASS (27 hold at s = 1;
# s_hat 1.049 +- 0.027 meets the allowance). Every other expectation is as first written.
# Three cases were added on Mon 16 Nov 2026, before any datum (Q191, lane fix-e199), with the second change to the rules (verify-e199
# F3: a price is decided at n >= 4 measured passes, rules > n_min), their expectations written here before they first ran: three
# measured passes on 6 family-A prices leave 25 decided, all holding (under K = 27, no miss): NOT DECIDED; four on the same 6 decide
# all 31: every verdict PASS, as SELF; every price at three passes decides none: all eight NO DATA. The case of one measured pass keeps
# its expectations (its reason now reads 'fewer than 4 measured passes').
CASES = [
    ("SELF: E192 against itself (aifoundry3 card 0 as card 1)", ("self",), {k: "PASS" for k in ALL8}),
    ("SHIFTED x1.25: every price 25% higher", ("scale", 1.25), {k: "FAIL" for k in ALL8}),
    ("SHIFTED x0.80: every price 20% lower", ("scale", 0.80), {k: "FAIL" for k in ALL8}),
    ("SHIFTED +3 combined SEs on every price", ("shift_sigma", 3.0), {k: "FAIL" for k in T1S}),
    ("SHIFTED +0.30 pJ on every family-A contrast", ("add_A", 0.30), {"E199-T1": "FAIL", "E199-T2": "FAIL"}),
    ("SHIFTED x1.10: every price 10% higher (beyond the allowance)", ("scale", 1.10), {k: "FAIL" for k in T2S}),
    ("EDGE: 4 family-A prices moved by 5 combined SEs (27 = K hold)", ("move_A", 4, 5.0),
     {"E199-T1": "PASS", "E199-T1L": "PASS", "E199-T1R": "PASS", "E199-T1RL": "PASS", "E199-T2": "PASS"}),
    ("EDGE: 5 family-A prices moved by 5 combined SEs (5 = F miss)", ("move_A", 5, 5.0),
     {"E199-T1": "FAIL", "E199-T1L": "PASS", "E199-T1R": "PASS", "E199-T1RL": "PASS"}),
    ("NOT DECIDED: 8 arms absent from card 1's file", ("drop_arms", 8),
     {"E199-T1": "NOT DECIDED", "E199-T2": "NOT DECIDED", "E199-T1R": "NOT DECIDED", "E199-T2R": "NOT DECIDED",
      "E199-T1L": "PASS", "E199-T2L": "PASS", "E199-T1RL": "PASS", "E199-T2RL": "PASS"}),
    ("NOT DECIDED: card 1's SE 4 x aifoundry3's on 10 family-A prices", ("se_A", 10, 4.0),
     {"E199-T1": "NOT DECIDED", "E199-T2": "NOT DECIDED", "E199-T1L": "PASS", "E199-T1R": "PASS", "E199-T1RL": "PASS"}),
    ("NOT DECIDED: one measured pass (no SE) on 6 family-A prices", ("one_pass_A", 6),
     {"E199-T1": "NOT DECIDED", "E199-T2": "NOT DECIDED"}),
    ("NOT DECIDED: three measured passes (an SE) on 6 family-A prices (decided at 4)", ("passes_A", 6, 3),
     {"E199-T1": "NOT DECIDED", "E199-T2": "NOT DECIDED", "E199-T1L": "PASS", "E199-T1R": "PASS", "E199-T1RL": "PASS"}),
    ("DECIDED AT 4: four measured passes on the same 6 family-A prices", ("passes_A", 6, 4), {k: "PASS" for k in ALL8}),
    ("NO DATA: every price with three measured passes (a session cut short before its fourth)", ("passes_all", 3),
     {k: "NO DATA" for k in ALL8}),
    ("NO DATA: an empty card-1 file", ("empty",), {k: "NO DATA" for k in ALL8}),
    ("ALLOWANCE EDGE: every price x s_hi", ("scale", "s_hi"), {k: "PASS" for k in T2S}),
    ("ALLOWANCE EDGE: every price x s_lo", ("scale", "s_lo"), {k: "PASS" for k in T2S}),
]


def selftest(out_path):
    forecast = json.load(open(FORECAST))
    ib = json.load(open(E192_IB))
    if sha(E192_IB) != forecast["sources"]["docs/reports/data/2026-11-14-e192-intbits-aifoundry3/intbits-e192.json"]["sha256"]:
        raise SystemExit("REFUSED: intbits-e192.json is not at the forecast's pin")
    same_builder = forecast_matches_builder()
    results, all_ok = [], same_builder
    for name, how, want in CASES:
        how2 = tuple(forecast["allowance"][x] if isinstance(x, str) and x in ("s_lo", "s_hi") else x for x in how)
        res = score(forecast, stand_in(ib, forecast, how2))
        got = res["verdicts"]
        diff = {k: (v, got[k]) for k, v in want.items() if got[k] != v}
        ok = not diff
        all_ok = all_ok and ok
        results.append({"case": name, "stand_in": list(how2), "expected": want, "got": got, "ok": ok,
                        "mismatches": {k: {"expected": a, "got": b} for k, (a, b) in diff.items()},
                        "counts": {fid: {"decided": res["families"][fid]["decided"], "T1": res["families"][fid]["T1"],
                                         "T2": res["families"][fid]["T2"],
                                         "s_hat": res["families"][fid]["scale"]["s_hat"],
                                         "s_hat_se": res["families"][fid]["scale"]["s_hat_se"],
                                         "scale_holds": res["families"][fid]["scale"]["scale_holds"]} for fid in FAMILY_IDS}})
    rep = {"what": "E199's scorer self-tests on E192's own reducer output and stand-ins made from it (desk check of code; nothing "
                   "measured)", "forecast_sha256": sha(FORECAST), "intbits_e192_sha256": sha(E192_IB),
           "forecast_equals_its_builder": same_builder, "cases": results, "interpreter": sys.version.split()[0],
           "verdict": "PASS" if all_ok else "FAIL"}
    with open(out_path, "w") as f:
        f.write(json.dumps(rep, indent=1) + "\n")
    for r in results:
        print("%-4s %s: %s" % ("ok" if r["ok"] else "BAD", r["case"],
                               "; ".join("%s %s" % (k, r["got"][k]) for k in ALL8)))
    print("forecast-e199.json equals forecast_e199.py's output: %s" % same_builder)
    print("SELFTEST-E199 %s (%d of %d cases as expected)" % ("PASS" if all_ok else "FAIL", sum(r["ok"] for r in results),
                                                            len(results)))
    return 0 if all_ok else 1


def main():
    a = sys.argv[1:]
    if a[:1] == ["--selftest"] and len(a) == 2:
        sys.exit(selftest(a[1]))
    if a[:1] == ["score"] and len(a) >= 4 and "--out" in a:
        card1_path = a[1]
        out_path = a[a.index("--out") + 1]
        bad = verify_list()
        if bad:
            raise SystemExit("REFUSED: the registration list does not match: " + "; ".join(bad))
        forecast = json.load(open(FORECAST))
        card1 = json.load(open(card1_path))
        res = score(forecast, card1)
        res.update({"experiment": "E199", "what": "E199 scored by its registered transport scorer (score_e199.py): card 1's "
                    "measured prices (aifoundry1 card 1) against E192's (aifoundry3 card 0)",
                    "forecast": {"path": os.path.relpath(FORECAST, TOP), "sha256": sha(FORECAST)},
                    "card1_file": {"path": card1_path, "sha256": sha(card1_path)},
                    "headline": {k: res["verdicts"][k] for k in ("E199-T1", "E199-T2")},
                    "interpreter": sys.version.split()[0]})
        if "--checks" in a:
            ck = json.load(open(a[a.index("--checks") + 1]))
            res["checks_beside"] = {k: {"aifoundry3": v, "card1": (ck.get("checks", {}).get(k) or {}).get("verdict"),
                                        "same": v == (ck.get("checks", {}).get(k) or {}).get("verdict")}
                                    for k, v in forecast["e192_checks"].items()}
            res["checks_beside_label"] = "REPORTED, never a transport verdict"
        with open(out_path, "w") as f:
            f.write(json.dumps(res, indent=1) + "\n")
        for line in summary_lines(res):
            print(line)
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
