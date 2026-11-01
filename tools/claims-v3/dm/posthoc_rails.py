#!/usr/bin/env python3
"""E99 POST HOC, labelled: not registered and not scored. Written Sun 1 Nov 2026, after the data and after an independent verifier pointed
out that the committed telemetry records the NoC and SRAM rails, and the registered reducer read only the minion rail.

    python3 tools/claims-v3/dm/posthoc_rails.py <E99 data dir> [--out posthoc-rails.json] > posthoc-rails.txt

Every rail is read as reduce_hl.runs_of_pass reads the minion rail: sp.noc_w[0], sp.sram_w[0], sp.minion_w[0] over [t0+2 s, t0+4 s), never
past the run, from the registered primary arm's telemetry (the board meter's dip samples removed by dp/posthoc_dips.py's definition), raw, with
no leakage correction; within-pass differences; 95 % t over the headline passes. The board column is dm.json's own (p80 at the auto slope), and
the script stops unless it and the minion column reproduce dm.json's per_pass numbers. "off" is the board less the three rails, pass by pass.

What the columns are not. A rail is the PMIC's running average at the regulator's output (14-card-behaviour.md: tau about 1.05 s, E58), so a
window from t0+2 s reads about 7 % of the way back to what came before the launch. The board is the 12 V input. So "off every metered rail" holds the
regulators' own losses as well as the rails nothing meters (the DDR and I/O rails, the memory shires' logic, E30; the DRAM chips): it is an upper
bound on anything other than those losses, and it is not one place.
"""
import argparse
import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "hl"))
sys.path.insert(0, os.path.join(HERE, "..", "mf"))
sys.path.insert(0, os.path.join(HERE, "..", "dp"))
from reduce_dm import CONTRASTS  # noqa: E402
from reduce_dp import classify  # noqa: E402
from reduce_mf import ci  # noqa: E402

RAILS = (("noc", "noc_w"), ("sram", "sram_w"), ("minion", "minion_w"))
COLS = ("board", "noc", "sram", "minion", "off")
NO_TOGGLE = (("dm_w1", 1, 1), ("dm_u1", 64, 64), ("dm_u2", 128, 128), ("dm_u4", 256, 256), ("dm_u5", 320, 256), ("dm_u7", 448, 128),
             ("dm_u8", 512, 64), ("dm_l08", 256, 32))
LADDER = (1, 2, 3, 4, 8, 16, 17, 32, 256, 8192)
TAU = {"minion": 1.06, "sram": 1.01, "noc": 1.04}   # 14-card-behaviour.md, E58, aifoundry3
T975_4 = 2.7764


def load(path):
    out = []
    op = gzip.open(path, "rt") if path.endswith(".gz") else open(path)
    with op as fh:
        for line in fh:
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def pass_rails(d, drop_w=4.0):
    """{item: {rail: W}} for one pass directory, the windows as reduce_hl.runs_of_pass's `wr`."""
    tel = load(os.path.join(d, "telemetry.jsonl.gz"))
    P = [s["board_w"] for s in tel]
    drop = {i for i in range(2, len(P) - 2) if P[i] < min(P[i - 2], P[i + 2]) - drop_w}
    tel = [s for i, s in enumerate(tel) if i not in drop]
    t = np.array([s["t_ms"] for s in tel], float)
    A = {f: np.array([s["sp"][k][0] for s in tel], float) for f, k in RAILS}
    recs = load(os.path.join(d, "runs.jsonl"))
    first, last = {}, {}
    for r in recs:
        key = (r["block"], r["item"], r.get("pos", 0), r.get("attempt", 1))
        first[key] = min(first.get(key, 1e30), r["t_start_ms"])
        last[key] = max(last.get(key, 0), r["t_end_ms"])
    out = {}
    for m in load(os.path.join(d, "marks.jsonl")):
        if m.get("kind") != "run":
            continue
        key = (m["block"], m["item"], m.get("pos", 0), m.get("attempt", 1))
        if key not in first:
            continue
        lo = first[key] + 1000
        wr = (t >= lo + 1000) & (t < min(lo + 3000, last[key]))
        out.setdefault(m["item"], []).append({f: float(A[f][wr].mean()) for f, _ in RAILS})
    return {it: {f: float(np.mean([x[f] for x in v])) for f, _ in RAILS} for it, v in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--out")
    a = ap.parse_args()
    d = json.load(open(os.path.join(a.data, "dm.json")))
    N = json.load(open(os.path.join(a.data, "gen", "counts.json")))
    passes = [str(p) for p in d["passes_headline"]]
    lr = d["headline"]["lines_per_s"]
    pj = lambda w: w / lr * 1e12

    # the per-pass table, every item, every column
    R = {}
    for p in passes:
        rails = pass_rails(os.path.join(a.data, "passes", "p" + p))
        R[p] = {}
        for it, b in d["per_pass"][p]["items_W"].items():
            r = rails[it]
            R[p][it] = dict(r, board=b, off=b - r["noc"] - r["sram"] - r["minion"])
    bad = 0
    for p in passes:
        for it, b in d["per_pass"][p]["rail_W"].items():
            if abs(R[p][it]["minion"] - b) > 1e-6:
                bad += 1
    print("E99 POST HOC, labelled: the three metered rails, headline passes %s, %.5e lines/s" % (passes, lr))
    print("check: the minion column against dm.json per_pass.rail_W, %d items x %d passes: %d differ" % (len(R[passes[0]]), len(passes), bad))
    print("every class below is E81's rule (pre: >= 0.25 W with the interval above 0; abs: the interval inside +-0.30 W), sized for the board: on one rail, read the interval")
    if bad:
        raise SystemExit("the windows do not reproduce the registered reducer's minion rail")

    def contrast(spec):
        out = {}
        for c in COLS:
            out[c] = ci([sum(q * R[p][it][c] for it, q in spec.items()) for p in passes])
        return out

    def line(name, s):
        txt = "%-14s" % name
        for c in COLS:
            x = s[c]
            txt += "  %s %+.3f [%+.3f, %+.3f] %s" % (c, x["mean"], x["lo"], x["hi"], classify(x, 0.25, 0.30)[:3])
        print(txt)

    res = {"note": "POST HOC, labelled", "passes": passes, "lines_per_s": lr, "contrasts_W": {}, "per_pass": R, "tent_fit": {}, "ladder_fits": {}}

    print("\n== A one: the same high pins, no toggle, more ones (W over the fewer-ones item; class by E81's rule)")
    for nm, ones in (("tie27", 320), ("tie18", 448), ("tie45", 64)):
        s = contrast(CONTRASTS[nm][0])
        res["contrasts_W"][nm] = s
        line(nm, s)
        print("    per one, pJ: " + "  ".join("%s %.2f [%.2f, %.2f]" % (c, pj(s[c]["mean"]) / ones, pj(s[c]["lo"]) / ones, pj(s[c]["hi"]) / ones) for c in COLS))

    print("\n== floor + one + high, fitted per pass over the eight no-toggle items (w1, u1, u2, u4, u5, u7, u8, l08): floor W, prices pJ, each +-95 %")
    X = np.array([[1.0, w, h] for _, w, h in NO_TOGGLE])
    for c in COLS:
        per = np.array([np.linalg.lstsq(X, np.array([R[p][n][c] - R[p]["dp_zeros"][c] for n, _, _ in NO_TOGGLE]), rcond=None)[0] for p in passes])
        m = per.mean(axis=0)
        h = T975_4 * per.std(axis=0, ddof=1) / math.sqrt(len(passes))
        print("%-8s floor %+.3f [%+.3f, %+.3f]   one %5.2f +-%.2f   high %5.2f +-%.2f"
              % (c, m[0], m[0] - h[0], m[0] + h[0], pj(m[1]), pj(h[1]), pj(m[2]), pj(h[2])))
        res["tent_fit"][c] = {"floor_W": float(m[0]), "floor_half_W": float(h[0]), "one_pJ": float(pj(m[1])), "one_half_pJ": float(pj(h[1])),
                              "high_pJ": float(pj(m[2])), "high_half_pJ": float(pj(h[2]))}
    tf = res["tent_fit"]
    print("one on the three rails together: %.2f pJ; off them: %.2f pJ of %.2f (the same fit on the off column: %.2f)"
          % (tf["noc"]["one_pJ"] + tf["sram"]["one_pJ"] + tf["minion"]["one_pJ"],
             tf["board"]["one_pJ"] - tf["noc"]["one_pJ"] - tf["sram"]["one_pJ"] - tf["minion"]["one_pJ"], tf["board"]["one_pJ"], tf["off"]["one_pJ"]))

    print("\n== the rails' lag: mean of 1 - exp(-t/tau) over t = 2..4 s after a step at t0")
    for f, tau in TAU.items():
        g = 1 - (tau / 2.0) * (math.exp(-2 / tau) - math.exp(-4 / tau))
        print("%-7s tau %.2f s: reads %.1f %% of a settled step; the one's price corrected for it, %.2f pJ" % (f, tau, 100 * g, tf[f]["one_pJ"] / g))
    print("E32's board-to-mesh-rail ratio, 192 / 129 fJ per one per hop (03-experiments.md, 05-claims.md), on the NoC rail's price: %.2f pJ at the board" % (tf["noc"]["one_pJ"] * 192 / 129))

    print("\n== The arrangement, the pins and the rest (W, class by E81's rule)")
    extra = {"c2_vs_c1": ({"dp_c2": 1, "dp_c1": -1}, ""), "c2_vs_l08": ({"dp_c2": 1, "dm_l08": -1}, ""), "L1_vs_l08": ({"dm_L1": 1, "dm_l08": -1}, ""),
             "arr_L1": ({"dm_L1": 1, "dp_c1": -1}, "")}
    for nm in ("hi_t0", "hi_ta", "hi_r", "t_enc", "t_both", "t_raw", "half", "arr_L2", "L2_vs_r08", "r08_vs_c2", "floor_w1", "ones_u8", "tie_total", "D",
               "c2_vs_c1", "c2_vs_l08", "L1_vs_l08", "arr_L1"):
        spec = CONTRASTS[nm][0] if nm in CONTRASTS else extra[nm][0]
        s = contrast(spec)
        res["contrasts_W"][nm] = s
        line(nm, s)

    print("\n== The ladder, over dm_L2 (W, class by E81's rule)")
    for n in LADDER:
        if n == 2:
            continue
        nm = "L%d_over_L2" % n
        s = contrast({"dm_L%d" % n: 1, "dm_L2": -1})
        res["contrasts_W"][nm] = s
        line(nm, s)
    print("\n== The ladder's steps")
    for x, y in ((8, 4), (16, 8), (16, 4), (32, 16), (256, 32), (8192, 256), (17, 3)):
        nm = "L%d_minus_L%d" % (x, y)
        s = contrast({"dm_L%d" % x: 1, "dm_L%d" % y: -1})
        res["contrasts_W"][nm] = s
        line(nm, s)
    D_ = res["contrasts_W"]["L8192_over_L2"]
    h16 = res["contrasts_W"]["L16_over_L2"]
    T_ = res["contrasts_W"]["tie_total"]
    share = lambda s: 100 * (s["noc"]["mean"] + s["sram"]["mean"]) / s["board"]["mean"]
    print("\nSRAM + NoC share of the board: top step D %.1f %%, h16 %.1f %%, tie_total %.1f %%" % (share(D_), share(h16), share(T_)))
    print("off: share of its own D at h3 %.0f %%, h32 %.0f %%" % (100 * res["contrasts_W"]["L3_over_L2"]["off"]["mean"] / D_["off"]["mean"],
                                                                100 * res["contrasts_W"]["L32_over_L2"]["off"]["mean"] / D_["off"]["mean"]))

    print("\n== Path counts on the ladder's ten rungs, floor + counts, the mean over the headline passes, per column: rms W, price pJ per bit [+-95 % over passes]")
    rungs = ["dm_L%d" % n for n in LADDER]
    for c in COLS:
        for terms in (("k_chan",), ("k_shire",), ("k_shire", "k_chan")):
            XX = np.array([[1.0] + [N[r][t] for t in terms] for r in rungs])
            per = np.array([np.linalg.lstsq(XX, np.array([R[p][r][c] - R[p]["dp_zeros"][c] for r in rungs]), rcond=None)[0] for p in passes])
            m = per.mean(axis=0)
            h = T975_4 * per.std(axis=0, ddof=1) / math.sqrt(len(passes))
            y = np.mean([[R[p][r][c] - R[p]["dp_zeros"][c] for r in rungs] for p in passes], axis=0)
            rms = float(np.sqrt(np.mean((y - XX @ m) ** 2)))
            print("%-8s %-16s rms %.3f W  %s" % (c, "+".join(terms), rms, "  ".join("%s %.2f [+-%.2f]" % (t, pj(v), pj(q)) for t, v, q in zip(terms, m[1:], h[1:]))))
            res["ladder_fits"].setdefault(c, {})["+".join(terms)] = {"rms_W": rms, "prices_pJ": {t: float(pj(v)) for t, v in zip(terms, m[1:])},
                                                                     "half_pJ": {t: float(pj(q)) for t, q in zip(terms, h[1:])}}

    print("\n== Every item over dp_zeros, the mean over the headline passes (W)")
    print("%-10s %7s %7s %7s %7s %7s" % ("item", *COLS))
    res["items_over_zeros_W"] = {}
    for it in sorted(R[passes[0]], key=lambda n: np.mean([R[p][n]["board"] - R[p]["dp_zeros"]["board"] for p in passes])):
        if it == "dp_zeros":
            continue
        v = {c: float(np.mean([R[p][it][c] - R[p]["dp_zeros"][c] for p in passes])) for c in COLS}
        res["items_over_zeros_W"][it] = v
        print("%-10s %+7.3f %+7.3f %+7.3f %+7.3f %+7.3f" % (it, v["board"], v["noc"], v["sram"], v["minion"], v["off"]))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, sort_keys=True, default=float)


if __name__ == "__main__":
    main()
