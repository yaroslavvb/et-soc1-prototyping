#!/usr/bin/env python3
"""E198's forecast 1 (the transport forecast), frozen before any card-1 X04 datum: E193's committed reduced prices on
aifoundry3 card 0, taken as aifoundry1 card 1's prediction, with the card-to-card scale band of E198's rule T2.

E198 (tools/claims-v3/e198/E198.md) runs X04's two sittings, E193's arms, passes, smoke and order unchanged, on aifoundry1
card 1, and asks whether E193's measured prices hold there. Its forecast is not a model: it IS E193's measured result.

  - The prices. Every number is copied from E193's committed outputs, the registered reducer's x04-e193-A.json and
    x04-e193-B.json and the kit's checker's checks-e193-A.json and checks-e193-B.json (E193 data notes 2, 37d2b9fd), each
    read only after its sha256 matches the pin below. The floats are E193's own: json parses them and writes them back
    with Python's shortest round-trip repr, so every value here is bit for bit the committed one (`--check` re-reads the
    inputs and compares every number with ==).
  - The scored prices (36, E198.md 5): sitting A's 16 arms (board W over idle, `arms.<arm>.board_w`, SE `board_se`)
    and 6 trains (board contrast B - A, `trains.<train>.contrast_board_w`, SE `board_se`); sitting B's 14 arms.
  - REPORTED, never scored: the minion rail of every arm and train (`minion_w`, `contrast_minion_w`, SE `minion_se`);
    the 7 fits as E193's reducer wrote them (the scorer propagates their SEs from the points'); E193's nine checks.
  - The scale band of rule T2 [S_LO, S_HI]: the least and greatest card-1 / aifoundry3 ratio of measured J over idle a
    launch over the six configurations E189 ran on aifoundry3 card 0 (fa9098c4) and E191's second session ran on
    aifoundry1 card 1 (7156ac15): the mean of each configuration's four passes' energy.json > board.j_per_solve (every
    pass reduced ok), each energy.json checked against its data directory's SHA256SUMS, whose own sha256 is pinned. The
    least is rounded down and the greatest up at the third decimal, so the band holds all six.

usage (from the repository's top; standard library only; /usr/bin/python3 3.12.3 wrote the committed files):
  python3 -I -B tools/claims-v3/e198/forecast_e198.py           # write forecast-e198.json and forecast-e198.txt
  python3 -I -B tools/claims-v3/e198/forecast_e198.py --check   # FORECAST CHECK PASS when both equal the committed bytes
"""
import hashlib
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A_DIR = "docs/reports/data/2026-11-15-e193-x04-clock-sitting-a-aifoundry3"
B_DIR = "docs/reports/data/2026-11-15-e193-x04-clock-sitting-b-aifoundry3"
E189_DIR = "docs/reports/data/2026-11-14-e189-blind-day-aifoundry3"
E191_DIR = "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2"
PINS = {
    A_DIR + "/x04-e193-A.json": "e1e536e884f8b5dba2cc836b1bd648f7b5f5b8c7866ea5e1fbedd76b7818052e",
    A_DIR + "/checks-e193-A.json": "095f8a8ee59ecc26b318f6420cc953f163f060999f7691a26bf5c97b803fac73",
    B_DIR + "/x04-e193-B.json": "75c23d05ea20c198a83bd0a19fc7086aa9e1db0528e9884563a7c8f165a0a74f",
    B_DIR + "/checks-e193-B.json": "6fa307a9b04dcddeb69c0a0f53734db2ebfa72f33d4185ea935cc1c32c0752f3",
    E189_DIR + "/SHA256SUMS": "d3fb68b5bf0f7e937a803c3976cc75c6b725dc3e22314cb412b2f2d10358925f",
    E191_DIR + "/SHA256SUMS": "594f5ff613b85b20f82aee398cdd3c1e81d0ef13989fdcbae1bbd1e3ea80c0dc",
}
CONFIGS = ("copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity")
# The rules' registered constants (E198.md 5). They are written into the forecast so the scorer reads one frozen file.
RULES = {"z": 1.96, "n_min": 4, "share": 0.8, "registered_prices": 36, "decided_min": 18, "fail_misses": 8,
         "sitting_decided_min": {"A": 11, "B": 7}}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pinned(path):
    got = sha256(path)
    if got != PINS[path]:
        sys.exit("REFUSED: %s sha256 %s, pinned %s" % (path, got, PINS[path]))
    return path


def sums(dirpath):
    out = {}
    for line in open(pinned(dirpath + "/SHA256SUMS")):
        h, p = line.rstrip("\n").split("  ", 1)
        out[p] = h
    return out


def j_over(dirpath, cfg):
    s = sums(dirpath)
    vals = []
    for k in (1, 2, 3, 4):
        rel = "passes/%s/p%d/energy.json" % (cfg, k)
        p = dirpath + "/" + rel
        if s.get(rel) != sha256(p):
            sys.exit("REFUSED: %s not at its SHA256SUMS line" % p)
        e = json.load(open(p))
        if e.get("ok") is not True:
            sys.exit("REFUSED: %s not reduced ok" % p)
        vals.append(e["board"]["j_per_solve"])
    return vals


def scale_band():
    rows = {}
    for cfg in CONFIGS:
        a3, c1 = j_over(E189_DIR, cfg), j_over(E191_DIR, cfg)
        rows[cfg] = {"aifoundry3_j_over_passes": a3, "card1_j_over_passes": c1,
                     "aifoundry3_j_over_mean": statistics.fmean(a3), "card1_j_over_mean": statistics.fmean(c1)}
        rows[cfg]["ratio_card1_over_aifoundry3"] = rows[cfg]["card1_j_over_mean"] / rows[cfg]["aifoundry3_j_over_mean"]
    r = [rows[c]["ratio_card1_over_aifoundry3"] for c in CONFIGS]
    lo, hi = min(r), max(r)
    return rows, lo, hi, math.floor(lo * 1000) / 1000, math.ceil(hi * 1000) / 1000


def build():
    A = json.load(open(pinned(A_DIR + "/x04-e193-A.json")))
    B = json.load(open(pinned(B_DIR + "/x04-e193-B.json")))
    CA = json.load(open(pinned(A_DIR + "/checks-e193-A.json")))
    CB = json.load(open(pinned(B_DIR + "/checks-e193-B.json")))
    rows, lo, hi, s_lo, s_hi = scale_band()
    prices, reported = [], []
    for sit, x in (("A", A), ("B", B)):
        for name in sorted(x["arms"]):
            v = x["arms"][name]
            prices.append({"id": "%s/arm/%s" % (sit, name), "sitting": sit, "kind": "arm", "key": name,
                           "field": "board_w", "v3": v["board_w"], "se3": v["board_se"], "n_a3": v["n"]})
            reported.append({"id": "%s/arm/%s/minion" % (sit, name), "sitting": sit, "kind": "arm", "key": name,
                             "field": "minion_w", "se_field": "minion_se", "v3": v["minion_w"], "se3": v["minion_se"],
                             "n_a3": v["n"]})
        for name in sorted(x["trains"]):
            v = x["trains"][name]
            prices.append({"id": "%s/train/%s" % (sit, name), "sitting": sit, "kind": "train", "key": name,
                           "field": "contrast_board_w", "v3": v["contrast_board_w"], "se3": v["board_se"], "n_a3": v["n"]})
            reported.append({"id": "%s/train/%s/minion" % (sit, name), "sitting": sit, "kind": "train", "key": name,
                             "field": "contrast_minion_w", "se_field": "minion_se", "v3": v["contrast_minion_w"],
                             "se3": v["minion_se"], "n_a3": v["n"]})
    if len(prices) != RULES["registered_prices"]:
        sys.exit("REFUSED: %d scored prices, registered %d" % (len(prices), RULES["registered_prices"]))
    fits = {"%s/fit/%s" % (sit, k): v for sit, x in (("A", A), ("B", B)) for k, v in sorted(x["fits"].items())}
    out = {
        "what": "E198 forecast 1 (the transport forecast): E193's committed reduced prices on aifoundry3 card 0 "
                "(registered reducer reduce_x04.py, run unchanged on E193's data commits fe08ed67 and 96ef447c; outputs "
                "committed in 37d2b9fd), frozen as aifoundry1 card 1's prediction before any card-1 X04 datum. Not a "
                "model: E193's measured result. Not blind to E193's data: it is this forecast.",
        "inputs": {p: h for p, h in sorted(PINS.items())},
        "rules": dict(RULES, scale_band=[s_lo, s_hi]),
        "scale_source": {
            "what": "card-1 / aifoundry3 ratio of measured J over idle a launch (mean of each configuration's four passes' "
                    "energy.json > board.j_per_solve), E189 (aifoundry3 card 0, fa9098c4) against E191's second session "
                    "(aifoundry1 card 1, 7156ac15); the same six configurations, hosts, sizes and K, the same reducer",
            "configs": rows, "ratio_min": lo, "ratio_max": hi, "s_lo": s_lo, "s_hi": s_hi,
            "rounding": "the least ratio rounded down, the greatest rounded up, at the third decimal"},
        "prices": prices,
        "reported_rail": reported,
        "reported_fits": fits,
        "e193_checks": {"A": CA, "B": CB},
    }
    return out


def text(f):
    s_lo, s_hi = f["rules"]["scale_band"]
    L = ["E198 forecast 1 (the transport forecast): E193's committed prices on aifoundry3 card 0, as aifoundry1 card 1's",
         "prediction, frozen before any card-1 X04 datum. Board W over idle (arms) and board contrast B - A (trains),",
         "mean +- SE over E193's measured passes; T2's scale band [%.3f, %.3f] times the price (before the combined" % (s_lo, s_hi),
         "95% interval widens it by 1.96 x sqrt(se1^2 + se3^2), which needs card 1's SE).", "",
         "%-26s %4s %10s %8s   %-22s" % ("price", "n", "W", "SE", "T2 band before widening")]
    for p in f["prices"]:
        a, b = sorted((s_lo * p["v3"], s_hi * p["v3"]))
        L.append("%-26s %4d %10.4f %8.4f   [%8.4f, %8.4f]" % (p["id"], p["n_a3"], p["v3"], p["se3"], a, b))
    L += ["", "scale band source (E189 on aifoundry3 card 0 against E191's second session on aifoundry1 card 1):",
          "%-15s %12s %12s %8s" % ("configuration", "aifoundry3 J", "card 1 J", "ratio")]
    for c, r in f["scale_source"]["configs"].items():
        L.append("%-15s %12.5f %12.5f %8.4f" % (c, r["aifoundry3_j_over_mean"], r["card1_j_over_mean"],
                                                r["ratio_card1_over_aifoundry3"]))
    L.append("ratios %.5f to %.5f -> band [%.3f, %.3f]" % (f["scale_source"]["ratio_min"], f["scale_source"]["ratio_max"],
                                                           s_lo, s_hi))
    L += ["", "REPORTED, never scored: the minion rail (W over idle; contrast B - A for trains)",
          "%-33s %4s %10s %8s" % ("price", "n", "W", "SE")]
    for p in f["reported_rail"]:
        L.append("%-33s %4d %10.4f %8.4f" % (p["id"], p["n_a3"], p["v3"], p["se3"]))
    L += ["", "REPORTED, never scored: the fits as E193's reducer wrote them (slope, intercept)"]
    for k, v in f["reported_fits"].items():
        L.append("%-26s slope %.6g  intercept %.6g W" % (k, v["slope_w"], v["intercept_w"]))
    L += ["", "rules: z %.2f, a price decided at n >= %d on card 1, PASS at >= %d decided of %d and >= %d%% of them holding,"
          % (f["rules"]["z"], f["rules"]["n_min"], f["rules"]["decided_min"], f["rules"]["registered_prices"],
             round(100 * f["rules"]["share"])),
          "FAIL at >= %d misses or (>= %d decided and < %d%% holding)" % (
              f["rules"]["fail_misses"], f["rules"]["decided_min"], round(100 * f["rules"]["share"])), ""]
    return "\n".join(L)


def render(f):
    return json.dumps(f, indent=1, sort_keys=True) + "\n", text(f)


def walk_equal(a, b, path=""):
    """every number, string and key equal (floats with ==); returns a list of differences"""
    bad = []
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            bad.append(path + " keys")
        for k in set(a) & set(b):
            bad += walk_equal(a[k], b[k], path + "/" + str(k))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            bad.append(path + " length")
        for i, (x, y) in enumerate(zip(a, b)):
            bad += walk_equal(x, y, "%s[%d]" % (path, i))
    elif a != b or type(a) is not type(b):
        bad.append(path)
    return bad


def main():
    f = build()
    js, tx = render(f)
    jp, tp = os.path.join(HERE, "forecast-e198.json"), os.path.join(HERE, "forecast-e198.txt")
    if "--check" in sys.argv[1:]:
        ok = open(jp).read() == js and open(tp).read() == tx
        # every scored and reported value bit for bit E193's committed field (a second reading of the inputs)
        A = json.load(open(A_DIR + "/x04-e193-A.json")); B = json.load(open(B_DIR + "/x04-e193-B.json"))
        X = {"A": A, "B": B}
        committed = json.load(open(jp))
        n = 0
        for p in committed["prices"] + committed["reported_rail"]:
            src = X[p["sitting"]]["arms" if p["kind"] == "arm" else "trains"][p["key"]]
            sef = p.get("se_field", "board_se")
            if not (src[p["field"]] == p["v3"] and src[sef] == p["se3"] and src["n"] == p["n_a3"]):
                ok = False
                print("DIFFERS:", p["id"])
            n += 1
        for k, v in committed["reported_fits"].items():
            sit, _, name = k.split("/")
            d = walk_equal(X[sit]["fits"][name], v)
            if d:
                ok = False
                print("DIFFERS:", k, d[:3])
            n += 1
        print("compared %d prices and fits with E193's committed fields (floats with ==)" % n)
        print("FORECAST CHECK PASS" if ok else "FORECAST CHECK FAIL")
        return 0 if ok else 1
    with open(jp, "w") as o:
        o.write(js)
    with open(tp, "w") as o:
        o.write(tx)
    print("wrote %s (%d prices scored, %d rail and %d fits reported); band [%.3f, %.3f]" % (
        jp, len(f["prices"]), len(f["reported_rail"]), len(f["reported_fits"]), *f["rules"]["scale_band"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
