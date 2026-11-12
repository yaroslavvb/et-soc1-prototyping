#!/usr/bin/env python3
"""E188 (Q165, registration): the power of every registered rule, by simulation from committed noise (E188.md section 7). Standard
library only.

    /usr/bin/python3 -B tools/claims-v3/e188/power_e188.py --root .            # writes power-e188.json and power-e188.txt beside this file
    /usr/bin/python3 -B tools/claims-v3/e188/power_e188.py --root . --check    # recomputes both and compares them byte for byte

THE TRAINS (plan-e188.json's seven, each with its processes and first orientation): E182's simulator, power_e182.sim_train, imported
unchanged: a quad's contrast drawn N(x + o kappa, sigma_q^2), o = +1 in SFFS and -1 in FSSF, kappa 0.009 W, each quad lost with chance
0.01; then e182_stats', e186_stats' and e188_stats' statistics and words, exactly as the scorer reads them. Three noises:
  REGISTERED  E182's registered fp32 sigma_q, 0.03804 W (noise-e182.json);
  MEASURED    sigma_q set so that a train's se is E182's measured fp32 one (the mean of T5's and T6's): sigma_q = se x sqrt(3 x 76);
  DOUBLED     twice REGISTERED.
THE WORLDS (each train's true difference):
  M12         M12's lines (forecast-e188.json);
  M12-DRAWN   M12 with its own parameter uncertainty: each draw takes M12's float parameters from N(b, cov) (m12.json) and forms each train
              as M10's line plus its design-row difference times the draw;
  M10         M10's lines;
  POS-4, POS-6  M12's lines with the five one-bit B trains' held price moved linearly with the bit's place in id order (B04, B05, B10, B19,
              B22 by -1, -1/2, 0, +1/2, +1 times 0.004 or 0.006 W): stated alternatives for E188-BPOS, not forecasts.
THE FALLBACK'S LEVELS (E188-LV, kinds passes only): E182's kinds-pass noise as registered (E178.md section 6): a read 0.125 / sqrt 2 W, a
session term 0.041 W a kind; five passes; the rule's own bootstrap (2,000 draws, random.Random(18860)).
Seeds random.Random(18800 + case index): 1,000 sessions a train case (each of all seven trains), 400 a levels case.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e188_stats as E  # noqa: E402
R, S = E.R, E.S
sys.path.insert(0, os.path.join(HERE, "..", "e182"))
import power_e182 as PE  # noqa: E402  (sim_train and resid_sd only, unchanged)

DRAWS, DRAWS_LV = 1000, 400
SIG_REG = 0.03804
B_ONE_BIT = ("B04", "B05", "B10", "B19", "B22")
POS_SHAPE = {"B04": -1.0, "B05": -0.5, "B10": 0.0, "B19": 0.5, "B22": 1.0}
# E186's measured held-bit prices (blind; scored-e186.json > rules > E186-GB / E186-GA > gamma), the REPEAT words' references
E186_GB = (0.013453048323176146, 0.014288169478934068)
E186_GA = (0.0037342905425885296, 0.004692156878759674)


def chol(A):
    n = len(A)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = A[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            L[i][j] = math.sqrt(max(s, 0.0)) if i == j else (s / L[j][j] if L[j][j] > 0 else 0.0)
    return L


def mvn(rng, mu, L):
    z = [rng.gauss(0.0, 1.0) for _ in mu]
    return [m + sum(L[i][k] * z[k] for k in range(i + 1)) for i, m in enumerate(mu)]


def shares(lst):
    return {w: round(sum(1 for v in lst if v == w) / len(lst), 4) for w in sorted(set(lst))} if lst else {}


def build(root):
    fc = json.load(open(os.path.join(HERE, "forecast-e188.json")))
    pl = json.load(open(os.path.join(HERE, "plan-e188.json")))
    m = json.load(open(os.path.join(root, "tools/claims-v3/m12/m12.json")))
    nz = json.load(open(os.path.join(root, "tools/claims-v3/e182/noise/noise-e182.json")))
    assert nz["sigma_q_w"]["float"] == SIG_REG
    sc = json.load(open(os.path.join(root, "docs/reports/data/2026-11-09-e186-one-number-r3-aifoundry3/scored-e186.json")))["rules"]
    assert (sc["E186-GB"]["gamma"]["lo"], sc["E186-GB"]["gamma"]["hi"]) == E186_GB
    assert (sc["E186-GA"]["gamma"]["lo"], sc["E186-GA"]["gamma"]["hi"]) == E186_GA
    FT, K, D = fc["trains"], fc["kinds"], fc["derived"]
    trains = pl["trains"]
    ids = [t["train"] for t in trains]
    dr = {t: [x - y for x, y in zip(K[FT[t]["first"]]["design_row"], K[FT[t]["second"]]["design_row"])] for t in ids}
    Lf = chol(m["float"]["cov"])
    se_m = fc["train_noise"]["measured"]["se_w"]
    noises = {"REGISTERED": SIG_REG, "MEASURED": se_m * math.sqrt(3 * 76), "DOUBLED": 2 * SIG_REG}
    out = {"_what": "E188's power figures (power_e188.py), by simulation from committed noise", "draws": DRAWS, "draws_levels": DRAWS_LV,
           "kappa_w": PE.KAPPA, "p_loss": PE.P_LOSS, "sigma_q_w": noises, "pos_shape": POS_SHAPE, "e186_gb": E186_GB, "e186_ga": E186_GA,
           "cases": {}, "levels": {}}
    case = [0]

    def rng_next():
        case[0] += 1
        return random.Random(18800 + case[0])

    def truths(world, rng):
        if world == "M10":
            return {t: FT[t]["M10_w"] for t in ids}
        if world == "M12-DRAWN":
            pf = mvn(rng, m["float"]["b"], Lf)
            return {t: FT[t]["M10_w"] + sum(x * y for x, y in zip(dr[t], pf)) for t in ids}
        tt = {t: FT[t]["M12_w"] for t in ids}
        if world.startswith("POS-"):
            d = float(world.split("-")[1]) / 1000.0
            for t in B_ONE_BIT:
                tt[t] += POS_SHAPE[t] * d
        return tt

    for nk in ("REGISTERED", "MEASURED", "DOUBLED"):
        for world in ("M12", "M12-DRAWN", "M10", "POS-4", "POS-6"):
            rng = rng_next()
            rec = {t: {"sign": [], "size_M12": [], "size_M10": [], "which": [], "hw": []} for t in ids}
            der = {k: [] for k in ("GB1 sign", "GB1 size_M12", "GB1 repeat", "BPOS", "GA23 sign", "GA23 size_M12", "GA23 repeat", "JOINT_M12",
                                   "JOINT_M10", "E188-M", "TR-N")}
            for _ in range(DRAWS):
                x = truths(world, rng)
                iv, procs = {}, {}
                for t in trains:
                    tid = t["train"]
                    iv[tid], procs[tid] = PE.sim_train(rng, x[tid], noises[nk], t["processes"], t["orientations"][0])
                z12, z10 = [], []
                for tid in ids:
                    v, f = iv[tid], FT[tid]
                    w12 = R.size_band(v, f["M12_w"], f["M12_se_w"])
                    w10 = R.size_band(v, f["M10_w"], 0.0)
                    r = rec[tid]
                    r["sign"].append(S.sign_of(v))
                    r["size_M12"].append(w12)
                    r["size_M10"].append(w10)
                    r["which"].append(R.which(w12, w10))
                    r["hw"].append(v["hw"])
                    z12.append(R.zscore(v, f["M12_w"], f["M12_se_w"]))
                    z10.append(R.zscore(v, f["M10_w"], 0.0))
                held = [E.held_part(iv[t], FT[t]["M10_w"]) for t in B_ONE_BIT]
                g1 = E.mean_of(held)
                der["GB1 sign"].append(S.sign_of(g1))
                der["GB1 size_M12"].append(R.size_band(g1, D["gamma_B_w"], D["gamma_B_se_w"]))
                der["GB1 repeat"].append(E.repeat(g1, *E186_GB))
                der["BPOS"].append(E.flat_q(held)["word"])
                ga = E.per_bit(E.held_part(iv["AALL"], FT["AALL"]["M10_w"]), 23)
                der["GA23 sign"].append(S.sign_of(ga))
                der["GA23 size_M12"].append(R.size_band(ga, D["gamma_A_w"], D["gamma_A_se_w"]))
                der["GA23 repeat"].append(E.repeat(ga, *E186_GA))
                j12, j10 = R.joint(z12), R.joint(z10)
                der["JOINT_M12"].append(j12["word"])
                der["JOINT_M10"].append(j10["word"])
                der["E188-M"].append(R.models_word(j12["word"], j10["word"]))
                r_ = PE.resid_sd([procs[t] for t in ids]) / SIG_REG
                der["TR-N"].append("AS FORECAST" if r_ <= 1.25 else ("WORSE" if r_ <= 2.0 else "FAILS"))
            c = {"trains": {}, "derived": {k: shares(v) for k, v in der.items()}}
            xc = truths(world, None) if world != "M12-DRAWN" else truths("M12", None)
            for tid in ids:
                r = rec[tid]
                c["trains"][tid] = {"truth_central_w": round(xc[tid], 6), "sign": shares(r["sign"]), "size_M12": shares(r["size_M12"]),
                                    "size_M10": shares(r["size_M10"]), "which": shares(r["which"]),
                                    "median_halfwidth_w": round(statistics.median(r["hw"]), 5)}
            out["cases"][f"{nk}|{world}"] = c
    # the fallback's levels rule, E188-LV (the fifteen kinds' levels over fp32 zeros, five passes)
    keys = sorted(K)
    for world in ("M12", "M10"):
        rng = rng_next()
        words = []
        for _ in range(DRAWS_LV):
            e12, e10 = [], []
            for k in keys:
                truth = K[k]["M12_w"] if world == "M12" else K[k]["M10_w"]
                dmeas = truth + rng.gauss(0.0, 0.041) + statistics.mean(rng.gauss(0.0, 0.125 / math.sqrt(2)) for _ in range(5))
                e12.append(dmeas - K[k]["M12_w"])
                e10.append(dmeas - K[k]["M10_w"])
            b = R.boot_rms_diff(e12, e10, draws=2000, seed=18860)
            words.append("M12 BETTER" if b["hi95"] < 0 else ("M12 WORSE" if b["lo95"] > 0 else "NOT RESOLVED"))
        out["levels"][world] = shares(words)
    # the kinds passes in FULL (reported, never a verdict): a kind's level above fp32.ones read segment by segment, E178's noise
    seg_sd = 0.125
    out["kinds_pass_reported"] = {
        "rule": "a kind's per-segment contrast D(kind) - D(fp32.ones) on E182's registered footing, over the kept segments of the kept passes "
                "the mean with t(0.975, n - 1); E178.md section 6's registered noise: a read 0.125 / sqrt 2 W (so a contrast 0.125 W a "
                "segment) and a session term 0.041 W a kind that no segment averages away",
        "halfwidth_95_w_two_passes_six_segments": round(S.t975(5) * seg_sd / math.sqrt(6), 4),
        "halfwidth_95_w_one_pass_three_segments": round(S.t975(2) * seg_sd / math.sqrt(3), 4),
        "session_term_contrast_sd_w": round(0.041 * math.sqrt(2), 4)}
    return out


def text(o):
    L = ["E188's power (power_e188.py): shares of simulated sessions giving each word; sigma_q " + json.dumps(o["sigma_q_w"]), ""]
    for ck, c in o["cases"].items():
        L.append(f"== {ck}")
        for tid, v in c["trains"].items():
            L.append(f"  {tid:5s} truth {v['truth_central_w']:+.5f}  sign {v['sign']}  size_M12 {v['size_M12']}  size_M10 {v['size_M10']}  "
                     f"which {v['which']}  hw {v['median_halfwidth_w']}")
        for k, v in c["derived"].items():
            L.append(f"  {k:14s} {v}")
    L.append("== the fallback's levels, E188-LV")
    for w, v in o["levels"].items():
        L.append(f"  truth {w}: {v}")
    L.append("== the kinds passes in FULL, reported: " + json.dumps(o["kinds_pass_reported"], sort_keys=True))
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    o = build(os.path.abspath(a.root))
    js, tx = json.dumps(o, indent=1, sort_keys=True) + "\n", text(o)
    fj, ft = os.path.join(HERE, "power-e188.json"), os.path.join(HERE, "power-e188.txt")
    if a.check:
        ok = open(fj).read() == js and open(ft).read() == tx
        print("CHECK", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    open(fj, "w").write(js)
    open(ft, "w").write(tx)
    print(tx)
    return 0


if __name__ == "__main__":
    sys.exit(main())
