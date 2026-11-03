#!/usr/bin/env python3
"""Q139(k): the 6 pool-5 tiles E153 and E157 re-run with C checked (critic rank 14), picked mechanically. Standard library.

    python3 tools/claims-v3/ccheck/pick6.py [--json]
    python3 tools/claims-v3/ccheck/pick6.py --same-card <E141|E142> <tile> <D mean> <D se> <passes>

Rule (written before any C-checked launch): pool 5's non-anchor tiles; per format the two whose D was measured most
tightly on both cards, smallest sqrt(ci95_E141^2 + ci95_E142^2), ties by name. The D comparison it sets up is per card
(E153 on aifoundry3 against E141, E157 on aifoundry1 card 1 against E142): each re-run is the same card's repeat.
Sources: docs/reports/data/2026-11-02-e141-blind5-aifoundry3/e141.json and 2026-11-02-e142-blind5-card1/e142.json,
items.<tile>.D {mean, se, n, ci95}; tools/claims-v3/kinds/blind5/blind5.json.

Corrected Tue 3 Nov 2026 (fix pass, after verification; the pick and its rule are unchanged): the docstring said the
comparison is per card "because the two cards' D differ by 0.3-0.5 W on most tiles". That is wrong: over pool 5's 30
kinds the cards' D differ by 0.004-0.466 W, median 0.233 W (10 kinds under 0.1 W, 10 in 0.1-0.3, 10 in 0.3-0.5), so
per card is the natural reading because each re-run repeats its own card, not because the cards could never agree.
The combined_ci95 below, sqrt(ci95_E141^2 + ci95_E142^2), is across the two cards: the key for picking the tiles, not
the interval of a same-card repeat. That interval is Welch's, `--same-card` (README, "The exact use", step 3):
  |D_new - D_old| <= t_0.975(nu) sqrt(se_new^2 + se_old^2),  nu = (se_new^2 + se_old^2)^2 /
                                                                  (se_new^4 / (n_new - 1) + se_old^4 / (n_old - 1)),
with se_old and n_old the same card's items.<tile>.D (its ci95 is t_0.975(n_old - 1) se_old). --json gives, per pick
and card, the half-width a repeat with the old session's own se and passes would get (repeat_band_W).
"""
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
E141 = os.path.join(ROOT, "docs/reports/data/2026-11-02-e141-blind5-aifoundry3/e141.json")
E142 = os.path.join(ROOT, "docs/reports/data/2026-11-02-e142-blind5-card1/e142.json")
POOL = os.path.join(ROOT, "tools/claims-v3/kinds/blind5/blind5.json")


def _betacf(a, b, x):
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 500):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c
        c = c if abs(c) > tiny else tiny
        de = d * c
        h *= de
        if abs(de - 1) < 3e-16:
            break
    return h


def _betainc(a, b, x):
    """The regularized incomplete beta function I_x(a, b) (continued fraction)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1 - bt * _betacf(b, a, 1 - x) / b


def t975(nu):
    """Student's t 0.975 quantile for nu > 0 degrees of freedom (nu need not be whole), by bisection."""
    lo, hi = 0.0, 1000.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1 - 0.5 * _betainc(nu / 2, 0.5, nu / (nu + mid * mid)) < 0.975:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def welch(mean_old, se_old, n_old, mean_new, se_new, n_new):
    """The same-card rule: is the new D inside Welch's 95% interval around the old one?"""
    v_old, v_new = se_old ** 2, se_new ** 2
    nu = (v_old + v_new) ** 2 / (v_old ** 2 / (n_old - 1) + v_new ** 2 / (n_new - 1))
    t = t975(nu)
    half = t * math.sqrt(v_old + v_new)
    diff = mean_new - mean_old
    return {"diff_W": round(diff, 4), "half_width_W": round(half, 4), "nu": round(nu, 3), "t975": round(t, 4),
            "inside": abs(diff) <= half}


def rows():
    a = json.load(open(E141))["items"]
    b = json.load(open(E142))["items"]
    pool = json.load(open(POOL))["tiles"]
    out = []
    for t in pool:
        if t.get("anchor"):
            continue
        nm = t["name"]
        k = nm if nm in a else nm.split(".", 1)[1]
        da, db = a[k]["D"], b[k]["D"]
        out.append({"tile": nm, "type": t["type"], "file": "tools/claims-v3/kinds/blind5/" + t["file"],
                    "sha256": t["sha256"]["whole"], "E141_D": round(da["mean"], 3), "E141_ci95": round(da["ci95"], 3),
                    "E141_n": da["n"], "E142_D": round(db["mean"], 3), "E142_ci95": round(db["ci95"], 3),
                    "E142_n": db["n"], "combined_ci95": round(math.hypot(da["ci95"], db["ci95"]), 3),
                    "E141_se": round(da["se"], 5), "E142_se": round(db["se"], 5),
                    "repeat_band_W": {"E141": round(welch(0, da["se"], da["n"], 0, da["se"], da["n"])["half_width_W"], 3),
                                      "E142": round(welch(0, db["se"], db["n"], 0, db["se"], db["n"])["half_width_W"], 3)},
                    "_D": {"E141": da, "E142": db}})
    return out


def main():
    rs = rows()
    if "--same-card" in sys.argv:
        i = sys.argv.index("--same-card")
        card, tile, mean, se, n = sys.argv[i + 1:i + 6]
        r = next(x for x in rs if x["tile"] == tile)
        old = r["_D"][card]
        v = welch(old["mean"], old["se"], old["n"], float(mean), float(se), int(n))
        v.update(tile=tile, card=card, old={"mean": round(old["mean"], 4), "se": round(old["se"], 5), "n": old["n"]},
                 new={"mean": float(mean), "se": float(se), "n": int(n)})
        print(json.dumps(v))
        return 0 if v["inside"] else 1
    pick = []
    for typ in ("fp32", "fp16", "int8"):
        pick += sorted((r for r in rs if r["type"] == typ), key=lambda r: (r["combined_ci95"], r["tile"]))[:2]
    narrow = min(min(r["E141_ci95"], r["E142_ci95"]) for r in rs)
    if "--json" in sys.argv:
        diffs = sorted(abs(r["E141_D"] - r["E142_D"]) for r in rs)
        print(json.dumps({"pick": [{k: v for k, v in r.items() if k != "_D"} for r in pick],
                          "narrowest_committed_ci95_W": narrow,
                          "card_difference_W": {"kinds": len(diffs), "min": diffs[0], "median": diffs[len(diffs) // 2]
                                                if len(diffs) % 2 else round((diffs[len(diffs) // 2 - 1] + diffs[len(diffs) // 2]) / 2, 3),
                                                "max": diffs[-1]}}, indent=1))
        return 0
    for r in pick:
        print("%-28s %s  E141 D %.3f +-%.3f (n=%d)  E142 D %.3f +-%.3f (n=%d)  combined +-%.3f  %s" % (
            r["tile"], r["type"], r["E141_D"], r["E141_ci95"], r["E141_n"], r["E142_D"], r["E142_ci95"], r["E142_n"],
            r["combined_ci95"], r["file"]))
    print("narrowest committed pool-5 D interval on either card: +-%.3f W (the critic's flat +-0.05 W is narrower than "
          "every other)" % narrow)
    return 0


if __name__ == "__main__":
    sys.exit(main())
