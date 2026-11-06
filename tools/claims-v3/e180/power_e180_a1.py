#!/usr/bin/env python3
"""E180's dated note A1 (E180.md.dated-note-A1.md section 2): the power of E180-H, -L and -O, and of the owner's sentence they make
together, at the noise levels the registration's own pairs support, and at 5 and 4 kept passes as well as 6.

    python3 -B tools/claims-v3/e180/power_e180_a1.py --dir tools/claims-v3/e180 --root .            # writes power-e180-a1.json and .txt
    python3 -B tools/claims-v3/e180/power_e180_a1.py --dir tools/claims-v3/e180 --root . --check    # re-makes both, byte for byte

The rules, their statistics and thresholds are the registration's, unchanged: power_e180.py's interval, sign, size, ols and ols2 are
imported, and the runs a pass are the plan's (fadd.ps/f_4 and f_5 three each, fadd.ps/zeros two, every other ladder kind one). What
changes is only the noise a run carries, which the registration took as N(0, sigma_d / sqrt 2) with sigma_d the median of 2-df pair sds
(0.1787 W on aifoundry3, which reads low by sqrt(ln 2) for Gaussian noise: the adversarial verifier's fault 3). The levels here, all from
noise/noise-e180-a1.json (noise_e180_a1.py), aifoundry3:
  registered  sigma_d 0.1787 (the registration's, for comparison: its figures are reproduced to the draw's error);
  debiased    the median / sqrt(ln 2), 0.2146;
  near_rms    the rms of the pairs whose two configurations sit within 1 W of each other, 0.2819;
  rms         the rms of all 7,021 pairs, 0.3443;
  mixture     a heavy-tailed run noise, N(0, s) with probability 1 - q and N(0, k s) with probability q, (s, q, k) chosen on a stated
              grid so that the simulated pair sds' quantiles (10, 25, 50, 75, 90, 95, 99%) match the 7,021 committed ones best in log
              (least squares), with the median matched exactly; reported as the noise that reproduces the committed pairs' heavy tail.
E180-R (Spearman of P against the 21 kinds' mean D, rho >= 0.433) is read on the joint draws too; E180-X, E180-A and E180-I on their own
draws (5,000 a case, random.Random(18200 + case index)), each with the plan's runs a pass, as power_e180.py simulates them.
The owner's sentence (E180.md section 5, score_e180.py's owners_sentence_measured): E180-H POSITIVE with SIZE PASS against P, P's slope
inside E180-L's interval, and E180-O NULL, read on one session's draws together. Truth P with a kind-level model error of 0 or 0.03 W
(the registration's two), n = 6, 5 and 4 kept passes; E180-H alone under every arm's truth and the null. Draws: 4,000 a joint case and
20,000 an E180-H case, from random.Random(18100 + case index); the mixture's fit uses random.Random(18190). Standard library only.
Nothing here is a new rule: it is the registered rules' power at noise levels read after the registration, before any E180 datum.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import power_e180 as pw          # noqa: E402  (the registration's statistics, unchanged)
import noise_e180_a1 as na1      # noqa: E402  (the pairs, as noise_e180.py reads them)

DRAWS_JOINT = 4000
DRAWS_H = 20000
NS = (6, 5, 4)
REPS = {"fadd.ps/f_4": 3, "fadd.ps/f_5": 3, "fadd.ps/zeros": 2}
ARMS = ("P", "C", "E", "F", "A")
QS = (0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99)
GRID_Q = (0.0, 0.02, 0.05, 0.08, 0.12, 0.16, 0.20, 0.25, 0.30)
GRID_K = (2.0, 3.0, 4.0, 5.0, 6.0, 8.0)
FIT_PAIRS = 20000


def r(x):
    return pw.rnd(x)


class Noise:
    """one run's noise: Gaussian (s) or a two-part mixture (s, q, k)"""

    def __init__(self, s, q=0.0, k=1.0):
        self.s, self.q, self.k = s, q, k

    def draw(self, rng):
        if self.q and rng.random() < self.q:
            return rng.gauss(0, self.s * self.k)
        return rng.gauss(0, self.s)


def fit_mixture(sds):
    """(s, q, k, loss): the grid point whose simulated 3-pass pair sds match the committed ones' quantiles best in log"""
    srt = sorted(sds)
    emp = [srt[min(len(srt) - 1, int(q * len(srt)))] for q in QS]
    best = None
    for q in GRID_Q:
        for k in (GRID_K if q else (1.0,)):
            rng = random.Random(18190)
            noise = Noise(1.0, q, k)
            sim = []
            for _ in range(FIT_PAIRS):
                d = [noise.draw(rng) - noise.draw(rng) for _ in range(3)]
                m = sum(d) / 3
                sim.append(math.sqrt(sum((x - m) ** 2 for x in d) / 2))
            sim.sort()
            qs = [sim[min(len(sim) - 1, int(qq * len(sim)))] for qq in QS]
            s = emp[2] / qs[2]                       # the median matched exactly
            loss = sum((math.log(s * a) - math.log(b)) ** 2 for a, b in zip(qs, emp))
            if best is None or loss < best[3]:
                best = (s, q, k, loss, [s * a for a in qs])
    return {"s_w": best[0], "q": best[1], "k": best[2], "loss": best[3], "sim_quantiles_w": best[4], "emp_quantiles_w": emp,
            "grid_q": list(GRID_Q), "grid_k": list(GRID_K), "pairs_simulated": FIT_PAIRS}


def joint(fc, noise, n, kerr, seed):
    K = fc["kinds"]
    lad = fc["ladder"]["kinds"]
    xr = [K[m]["result_popcount"] for m in lad]
    xo = [K[m]["operand_popcount"] for m in lad]
    W = {m: K[m]["W"]["aifoundry3"] for m in lad}
    fs = fc["ladder"]["slope_W_per_bit"]
    hP = W["fadd.ps/f_5"]["P"] - W["fadd.ps/f_4"]["P"]
    rng = random.Random(seed)
    c = {"H_POSITIVE": 0, "H_P_inside": 0, "L_P_inside": 0, "L_other_arm_inside": 0, "O_NULL": 0, "sentence": 0, "R_PASS": 0,
         "L_hw": 0.0, "O_hw": 0.0, "H_hw": 0.0}
    tP = [W[m]["P"] for m in lad]
    for _ in range(DRAWS_JOINT):
        err = {m: (rng.gauss(0, kerr) if kerr else 0.0) for m in lad}
        hx, lx, ox = [], [], []
        sums = [0.0] * len(lad)
        for _p in range(n):
            D = {}
            for m in lad:
                k = REPS.get(m, 1)
                D[m] = W[m]["P"] + err[m] + sum(noise.draw(rng) for _ in range(k)) / k
            ys = [D[m] - D["fadd.ps/zeros"] for m in lad]
            sums = [a + y for a, y in zip(sums, ys)]
            hx.append(D["fadd.ps/f_5"] - D["fadd.ps/f_4"])
            lx.append(pw.ols(xr, ys))
            ox.append(pw.ols2(xr, xo, ys))
        _, hlo, hhi = pw.interval(hx)
        _, llo, lhi = pw.interval(lx)
        _, olo, ohi = pw.interval(ox)
        hpos, hin = hlo > 0, hlo <= hP <= hhi
        lin = llo <= fs["P"] <= lhi
        onull = -pw.O_MARGIN <= olo and ohi <= pw.O_MARGIN
        c["H_POSITIVE"] += hpos
        c["H_P_inside"] += hin
        c["L_P_inside"] += lin
        c["L_other_arm_inside"] += any(llo <= fs[a] <= lhi for a in ARMS if a != "P")
        c["O_NULL"] += onull
        c["sentence"] += hpos and hin and lin and onull
        c["R_PASS"] += pw.spearman(tP, sums) >= pw.RHO_CRIT
        c["L_hw"] += (lhi - llo) / 2
        c["O_hw"] += (ohi - olo) / 2
        c["H_hw"] += (hhi - hlo) / 2
    return {k: v / DRAWS_JOINT for k, v in c.items()}


def h_alone(fc, noise, n, arm, seed):
    K = fc["kinds"]
    mu = 0.0 if arm == "null" else K["fadd.ps/f_5"]["W"]["aifoundry3"][arm] - K["fadd.ps/f_4"]["W"]["aifoundry3"][arm]
    hP = K["fadd.ps/f_5"]["W"]["aifoundry3"]["P"] - K["fadd.ps/f_4"]["W"]["aifoundry3"]["P"]
    rng = random.Random(seed)
    c = {"POSITIVE": 0, "NEGATIVE": 0, "P_inside": 0, "hw": 0.0}
    for _ in range(DRAWS_H):
        xs = [mu + sum(noise.draw(rng) for _ in range(3)) / 3 - sum(noise.draw(rng) for _ in range(3)) / 3 for _p in range(n)]
        _, lo, hi = pw.interval(xs)
        s = pw.sign(lo, hi)
        if s in c:
            c[s] += 1
        c["P_inside"] += lo <= hP <= hi
        c["hw"] += (hi - lo) / 2
    return {k: v / DRAWS_H for k, v in c.items()}


def others(fc, noise, n, seed):
    """E180-X, E180-A and E180-I under truth P, each simulated on its own draws (the registration's way), with the plan's runs a pass"""
    K = fc["kinds"]
    W = {m: K[m]["W"]["aifoundry3"]["P"] for m in K}
    pi8 = [m for m in K if K[m]["mode"] == "fadd.pi" and K[m]["rule"] == "R4"]
    fX = (W["fadd.ps/f_5"] - W["fadd.ps/zeros"]) - (W["fadd.pi/f_5"] - W["fadd.pi/zeros"])
    fA = (W["fadd.ps.acc/f_4"] - W["fadd.ps.acc/zeros"]) - (W["fadd.ps/f_4"] - W["fadd.ps/zeros"])
    rng = random.Random(seed)

    def run(m, k):
        return W[m] + sum(noise.draw(rng) for _ in range(k)) / k

    c = {"X_POSITIVE": 0, "X_P_inside": 0, "A_POSITIVE": 0, "A_P_inside": 0, "I_NULL": 0, "X_hw": 0.0, "A_hw": 0.0, "I_hw": 0.0}
    for _ in range(DRAWS_H // 4):
        xs, as_, is_ = [], [], []
        for _p in range(n):
            z2, pz2 = run("fadd.ps/zeros", 2), run("fadd.pi/zeros", 2)
            xs.append((run("fadd.ps/f_5", 3) - z2) - (run("fadd.pi/f_5", 1) - pz2))
            as_.append((run("fadd.ps.acc/f_4", 1) - run("fadd.ps.acc/zeros", 1)) - (run("fadd.ps/f_4", 3) - run("fadd.ps/zeros", 2)))
            is_.append(sum(run(m, 1) for m in pi8) / len(pi8) - run("fadd.pi/zeros", 2))
        _, lo, hi = pw.interval(xs)
        c["X_POSITIVE"] += lo > 0
        c["X_P_inside"] += lo <= fX <= hi
        c["X_hw"] += (hi - lo) / 2
        _, lo, hi = pw.interval(as_)
        c["A_POSITIVE"] += lo > 0
        c["A_P_inside"] += lo <= fA <= hi
        c["A_hw"] += (hi - lo) / 2
        _, lo, hi = pw.interval(is_)
        c["I_NULL"] += -pw.I_MARGIN <= lo and hi <= pw.I_MARGIN
        c["I_hw"] += (hi - lo) / 2
    return {k: v / (DRAWS_H // 4) for k, v in c.items()}


def build(d, root):
    fc = json.load(open(os.path.join(d, "forecast-e180.json")))
    nz = json.load(open(os.path.join(d, "noise", "noise-e180-a1.json")))["cards"]["aifoundry3"]
    cat = json.load(open(os.path.join(root, "docs/reports/data/2026-09-23-energy-manual/catalogue.json")))
    sds = [s for s, _ in na1.pair_sds(cat, "aifoundry3")]
    mix = fit_mixture(sds)
    levels = {"registered": nz["median_w_full"], "debiased": nz["debiased_median_w"], "near_rms": nz["near_rms_w"], "rms": nz["rms_w"]}
    models = {k: Noise(v / math.sqrt(2)) for k, v in levels.items()}
    models["mixture"] = Noise(mix["s_w"], mix["q"], mix["k"])
    out = {"what": "E180 dated note A1: the registered rules' power at the re-read noise levels (power_e180_a1.py)",
           "sigma_d_w": levels, "sigma_ind_w": {k: v / math.sqrt(2) for k, v in levels.items()}, "mixture": mix,
           "mixture_run_sd_w": math.sqrt((1 - mix["q"]) * mix["s_w"] ** 2 + mix["q"] * (mix["k"] * mix["s_w"]) ** 2),
           "draws_joint": DRAWS_JOINT, "draws_h": DRAWS_H, "draws_others": DRAWS_H // 4, "joint": {}, "h_alone": {}, "others": {}}
    idx = 0
    for name, noise in models.items():
        for n in NS:
            for kerr in (0.0, 0.03):
                out["joint"][f"{name}|n{n}|kerr{kerr}"] = joint(fc, noise, n, kerr, 18100 + idx)
                idx += 1
    for name, noise in models.items():
        for n in (6, 5):
            for arm in ARMS + ("null",):
                out["h_alone"][f"{name}|n{n}|{arm}"] = h_alone(fc, noise, n, arm, 18100 + idx)
                idx += 1
    j = 0
    for name, noise in models.items():
        for n in (6, 5):
            out["others"][f"{name}|n{n}"] = others(fc, noise, n, 18200 + j)
            j += 1
    return out


def text(p):
    L = [f"E180 dated note A1, power (power_e180_a1.py): {p['draws_joint']} draws a joint case, {p['draws_h']} an E180-H case; aifoundry3."]
    L.append("sigma_d (W): " + ", ".join(f"{k} {v:.4f}" for k, v in p["sigma_d_w"].items()))
    m = p["mixture"]
    L.append(f"mixture: run noise N(0, {m['s_w']:.4f}) w.p. {1 - m['q']:.2f}, N(0, {m['k'] * m['s_w']:.4f}) w.p. {m['q']:.2f} "
             f"(run sd {p['mixture_run_sd_w']:.4f}; log-quantile loss {m['loss']:.4f})")
    L.append("   pair-sd quantiles 10/25/50/75/90/95/99%: committed " + " ".join(f"{x:.3f}" for x in m["emp_quantiles_w"]) +
             "; mixture " + " ".join(f"{x:.3f}" for x in m["sim_quantiles_w"]))
    L.append("Truth P. H POS = E180-H POSITIVE; H in = P inside H's interval (SIZE PASS); L in = P inside L; L other = any other arm inside L;")
    L.append("O NULL = E180-O NULL; sentence = all four together (score_e180.py's owners_sentence_measured).")
    for key, c in p["joint"].items():
        name, n, kerr = key.split("|")
        L.append(f"   {name:10s} {n:3s} {kerr:9s}: H POS {c['H_POSITIVE']:.3f}  H in {c['H_P_inside']:.3f}  L in {c['L_P_inside']:.3f}"
                 f"  L other {c['L_other_arm_inside']:.3f}  O NULL {c['O_NULL']:.3f}  R PASS {c['R_PASS']:.3f}  sentence {c['sentence']:.3f}"
                 f"  (half-widths H {c['H_hw']:.4f} W, L {c['L_hw']:.5f}, O {c['O_hw']:.5f} W a bit)")
    L.append("E180-H alone, POSITIVE (NEGATIVE) by truth:")
    for key, c in p["h_alone"].items():
        name, n, arm = key.split("|")
        L.append(f"   {name:10s} {n:3s} truth {arm:4s}: POSITIVE {c['POSITIVE']:.3f} NEGATIVE {c['NEGATIVE']:.3f} P inside {c['P_inside']:.3f}"
                 f" half-width {c['hw']:.4f}")
    L.append(f"E180-X, E180-A and E180-I, truth P ({p['draws_others']} draws a case):")
    for key, c in p["others"].items():
        name, n = key.split("|")
        L.append(f"   {name:10s} {n:3s}: X POSITIVE {c['X_POSITIVE']:.3f} (P inside {c['X_P_inside']:.3f}, half-width {c['X_hw']:.3f} W);"
                 f" A POSITIVE {c['A_POSITIVE']:.3f} (P inside {c['A_P_inside']:.3f}, half-width {c['A_hw']:.3f} W);"
                 f" I NULL {c['I_NULL']:.3f} (half-width {c['I_hw']:.3f} W)")
    return "\n".join(L) + "\n"


def write(d, root, outdir):
    p = build(d, root)
    json.dump(r(p), open(os.path.join(outdir, "power-e180-a1.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(outdir, "power-e180-a1.txt"), "w").write(text(p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not a.check:
        write(a.dir, a.root, a.dir)
        print(open(os.path.join(a.dir, "power-e180-a1.txt")).read())
        return
    with tempfile.TemporaryDirectory() as t:
        write(a.dir, a.root, t)
        bad = [f for f in ("power-e180-a1.json", "power-e180-a1.txt")
               if open(os.path.join(t, f)).read() != open(os.path.join(a.dir, f)).read()]
    print("CHECK FAIL: " + ", ".join(bad) if bad else "CHECK PASS: power-e180-a1.json and power-e180-a1.txt byte for byte")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
