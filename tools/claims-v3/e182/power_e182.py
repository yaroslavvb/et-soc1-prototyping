#!/usr/bin/env python3
"""E182 (Q153): the power of every registered rule, by simulation from committed noise (E182.md section 6). Standard library only.

    /usr/bin/python3 -B power_e182.py --dir tools/claims-v3/e182            # writes power-e182.json and power-e182.txt
    /usr/bin/python3 -B power_e182.py --dir tools/claims-v3/e182 --check    # recomputes and compares both files byte for byte

THE TRAINS' NOISE (noise-e182.json, E178's committed runs read launch by launch): a quad's contrast is drawn N(x + o kappa, sigma_q^2)
with o = +1 in an SFFS process and -1 in an FSSF one, kappa = +0.009 W (the float quads' mean in E178's runs, a curvature inside a
process that the orientation pairs cancel), sigma_q = 0.03485 W (int8) or 0.03804 W (fp32) as BASE and twice that as DOUBLED (Q150's
allowance for switching transients); each quad is lost with chance 0.01 (a launch without two window samples). The plan's process
counts (plan-e182.json) and the statistics of e182_stats.py, exactly as the scorer reads them.
THE KINDS PASSES' NOISE (E178.md section 6, carried as registered; the critic's "couple-level noise, never the pass sd"): one read of a
kind in a pass has sd 0.125 / sqrt 2 W, a kind read three times in a pass 0.125 / sqrt 6; each kind carries a session term of 0.041 W,
the same in every pass. Three passes (FULL's floor) and four.
Seeds: random.Random(18200 + case index); 4,000 draws a case (2,000 for the slower kinds-pass cases).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import statistics
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e182_stats as S  # noqa: E402

KAPPA = 0.009
P_LOSS = 0.01
DRAWS = 4000
DRAWS_K = 2000
DELTA_AB = 0.002      # W per held 1-bit a byte: the NULL band of E182-A and E182-B
DELTA_F = 0.015       # W: the NULL band of E182-F (the float swap)
E178_INT8 = (0.021651298383282183, 0.08476234575729945)   # E178-H-int8's registered interval (scored.json)
E178_FP32 = (-0.0459, 0.1505)                            # E178-H-fp32 (data README)
SIG_K1 = 0.125 / math.sqrt(2)
SESSION = 0.041


def sim_train(rng, x, sig, nproc, first):
    procs = []
    for k in range(nproc):
        o = first if k % 2 == 0 else ("FSSF" if first == "SFFS" else "SFFS")
        sg = 1.0 if o == "SFFS" else -1.0
        q = [rng.gauss(x + sg * KAPPA, sig) for _ in range(3) if rng.random() >= P_LOSS]
        procs.append((o, q))
    return S.interval(S.train_units(procs)), procs


def resid_sd(procs_list):
    """the pooled residual sd of quads about their train's and orientation's mean (E182-TR-N's statistic)"""
    ss, dfn = 0.0, 0
    for procs in procs_list:
        for o in ("SFFS", "FSSF"):
            q = [c for oo, qq in procs if oo == o for c in qq]
            if len(q) > 1:
                m = statistics.mean(q)
                ss += sum((c - m) ** 2 for c in q)
                dfn += len(q) - 1
    return math.sqrt(ss / dfn)


def share(lst, word):
    return round(sum(1 for v in lst if v == word) / len(lst), 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=HERE)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    D = os.path.abspath(a.dir)
    F = json.load(open(os.path.join(D, "forecast-e182.json")))
    PL = json.load(open(os.path.join(D, "plan-e182.json")))
    NZ = json.load(open(os.path.join(D, "noise", "noise-e182.json")))
    tr = {t["train"]: t for t in PL["trains"]}
    pr = F["pairs"]
    sig = {"int8": NZ["sigma_q_w"]["int8"], "fp32": NZ["sigma_q_w"]["float"]}
    out = {"_what": "E182's power figures (power_e182.py), by simulation from committed noise", "kappa_w": KAPPA, "p_loss": P_LOSS,
           "draws": DRAWS, "draws_kinds": DRAWS_K, "delta_ab_w_per_bit": DELTA_AB, "delta_f_w": DELTA_F, "sigma_q_w": sig, "cases": {}}
    case = [0]

    def rng_next():
        case[0] += 1
        return random.Random(18200 + case[0])

    noise = {"BASE": 1.0, "DOUBLED": 2.0}
    lines = {arm: {pid: pr[pid][f"d{arm}_w_a3"] for pid in pr} for arm in ("P", "PACC", "E")}
    # 1. his pair (T1) and his fp32 pair (T6)
    for pid, ref in (("T1", E178_INT8), ("T6", E178_FP32)):
        t = tr[pid]
        ty = t["type"]
        truths = {"P": lines["P"][pid], "PACC": lines["PACC"][pid], "E": lines["E"][pid], "E178": (ref[0] + ref[1]) / 2, "zero": 0.0}
        for nk, f in noise.items():
            for tn, x in truths.items():
                rng = rng_next()
                sg, sp, se_, sa, hw = [], [], [], [], []
                for _ in range(DRAWS):
                    iv, _ = sim_train(rng, x, sig[ty] * f, t["processes"], t["orientations"][0])
                    sg.append(S.sign_of(iv))
                    sp.append(S.size_of(iv, lines["P"][pid]))
                    se_.append(S.size_of(iv, lines["E"][pid]))
                    sa.append(S.agrees(iv, *ref))
                    hw.append(iv["hw"])
                out["cases"][f"{pid}|{nk}|truth {tn}"] = {
                    "truth_w": x, "POSITIVE": share(sg, "POSITIVE"), "size_P_PASS": share(sp, "PASS"), "size_P_FAIL_HIGH": share(sp, "FAIL HIGH"),
                    "size_E_PASS": share(se_, "PASS"), "repeat_AGREES": share(sa, "AGREES"), "median_halfwidth_w": round(statistics.median(hw), 5)}
    # 2. the held-bit split (T3 x_sign, T2 x_swap), and the crossed pair's consistency (T4 against T2 / 7)
    bE = F["held_bit_split"]["E_a3"]["beta_B_w_per_bit"]
    bP = F["held_bit_split"]["P_a3"]["beta_B_w_per_bit"]
    hyps = {"B-ONLY at P": (0.0, bP), "B-ONLY at E": (0.0, bE), "A+B, equal": (bE / 2, bE / 2), "A-ONLY": (bE, 0.0),
            "NONE": (0.0, 0.0), "mixed: A 0.002, B at E": (0.002, bE)}
    for nk, f in noise.items():
        for hn, (ba, bb) in hyps.items():
            rng = rng_next()
            va, vb, vs, bsP, bsE, cons, x4s, hwa = [], [], [], [], [], [], [], []
            for _ in range(DRAWS):
                i3, _ = sim_train(rng, 7 * (ba + bb), sig["int8"] * f, tr["T3"]["processes"], tr["T3"]["orientations"][0])
                i2, _ = sim_train(rng, 7 * (bb - ba), sig["int8"] * f, tr["T2"]["processes"], tr["T2"]["orientations"][0])
                i4, _ = sim_train(rng, (bb - ba), sig["int8"] * f, tr["T4"]["processes"], tr["T4"]["orientations"][0])
                A = S.combine(i3, i2, 1, -1, 14)
                B = S.combine(i3, i2, 1, 1, 14)
                wa, wb = S.null_of(A, DELTA_AB), S.null_of(B, DELTA_AB)
                va.append(wa)
                vb.append(wb)
                vs.append(S.split_of(wa, wb))
                bsP.append(S.size_of(B, bP))
                bsE.append(S.size_of(B, bE))
                # consistency: x4 - x2 / 7, Welch
                cc = S.combine(i4, i2, 7, -1, 7)
                cons.append("CONSISTENT" if cc["lo"] <= 0 <= cc["hi"] else "INCONSISTENT")
                x4s.append(S.sign_of(i4))
                hwa.append(A["hw"])
            out["cases"][f"SPLIT|{nk}|{hn}"] = {
                "beta_A": ba, "beta_B": bb, "A": {w: share(va, w) for w in ("POSITIVE", "NULL", "NEGATIVE", "NOT RESOLVED")},
                "B": {w: share(vb, w) for w in ("POSITIVE", "NULL", "NEGATIVE", "NOT RESOLVED")},
                "SPLIT": {w: share(vs, w) for w in ("B-ONLY", "A+B", "A-ONLY", "NEITHER", "UNSETTLED")},
                "B_size_P_PASS": share(bsP, "PASS"), "B_size_E_PASS": share(bsE, "PASS"),
                "X_CONSISTENT": share(cons, "CONSISTENT"), "X_POSITIVE": share(x4s, "POSITIVE"),
                "median_halfwidth_beta_A_w": round(statistics.median(hwa), 6)}
    # 3. the float swap (T5)
    for nk, f in noise.items():
        for tn, x in (("zero (every arm)", 0.0), ("+0.010", 0.010), ("+0.030", 0.030)):
            rng = rng_next()
            v = []
            for _ in range(DRAWS):
                iv, _ = sim_train(rng, x, sig["fp32"] * f, tr["T5"]["processes"], tr["T5"]["orientations"][0])
                v.append(S.null_of(iv, DELTA_F))
            out["cases"][f"T5|{nk}|truth {tn}"] = {w: share(v, w) for w in ("POSITIVE", "NULL", "NEGATIVE", "NOT RESOLVED")}
    # 4. the train method: E182-TR-N (the quads' residual sd against the forecast) and E182-TR-H (the projection to 30 and 40 minutes)
    for nk, f in noise.items():
        rng = rng_next()
        wn, wh = [], []
        for _ in range(DRAWS // 4):
            ratios = []
            us = []
            for ty, ids in (("int8", ("T1", "T2", "T3", "T4")), ("fp32", ("T5", "T6"))):
                pl = []
                for pid in ids:
                    iv, procs = sim_train(rng, 0.05, sig[ty] * f, tr[pid]["processes"], tr[pid]["orientations"][0])
                    pl.append(procs)
                    if ty == "int8":
                        u = S.train_units(procs)
                        m = statistics.mean(u)
                        us.extend(x - m for x in u)
                ratios.append(resid_sd(pl) / sig[ty])
            r = max(ratios)
            wn.append("AS FORECAST" if r <= 1.25 else ("WORSE" if r <= 2.0 else "FAILS"))
            su = math.sqrt(sum(x * x for x in us) / (len(us) - 4))
            proc_s = PL["estimate"]["proc_s"]
            hw30 = S.t975(1800 / (2 * proc_s) - 1) * su / math.sqrt(1800 / (2 * proc_s))
            hw40 = S.t975(2400 / (2 * proc_s) - 1) * su / math.sqrt(2400 / (2 * proc_s))
            wh.append("BETTER" if hw40 < 0.003 and hw30 < 0.003 else ("HOLDS" if hw30 <= 0.006 else "FAILS"))
        out["cases"][f"TR|{nk}"] = {"TR-N": {w: share(wn, w) for w in ("AS FORECAST", "WORSE", "FAILS")},
                                     "TR-H": {w: share(wh, w) for w in ("BETTER", "HOLDS", "FAILS")}}
    # 5. the kinds passes: E182-W-int8 (slope against E's and P's lines), E182-R-int8 (rho), E182-Q (the quartet fit, reported)
    ks = F["kinds"]
    i8 = sorted(k for k in ks if ks[k]["type"] == "int8")
    core = {k for pid in ("T1", "T2", "T3", "T4") for k in (pr[pid]["first"], pr[pid]["second"])}
    flips = [ks[k]["flips_i"]["launch_mean"]["total"] for k in i8]
    R8 = F["rate"]["int8"]
    lineE = F["arm_E_lines"]["int8"]["price_fJ_per_flip"]
    lineP = F["slope_int8_fJ_per_flip"]["P"]
    rng = rng_next()
    null_r = []
    for _ in range(20000):
        v = list(range(len(i8)))
        rng.shuffle(v)
        null_r.append(S.spearman(list(range(len(i8))), v))
    null_r.sort()
    rho_crit = null_r[int(0.975 * len(null_r))]
    out["rho_crit_int8_n20"] = rho_crit
    held = {k: (ks[k]["popcount_a_word"] + ks[k]["popcount_b_word"]) / 4.0 for k in i8}
    truths = {"E": {k: ks[k]["E_w"]["a3"] for k in i8}, "P": {k: ks[k]["P_w"]["a3"] for k in i8},
              "E + A+B held bits": {k: ks[k]["E_w"]["a3"] + (bE / 2) * held[k] for k in i8}, "flat": {k: 1.70 for k in i8}}
    qkeys = F["quartet_keys"]
    sys.path.insert(0, D)
    import forecast_e182 as FE  # noqa: E402  (quartet_design and solve only)
    Xq, _ = FE.quartet_design([ks[k] for k in qkeys])
    for npass in (3, 4):
        for tn, tv in truths.items():
            rng = rng_next()
            wE, wP, rr, qa, qb = [], [], [], [], []
            for _ in range(DRAWS_K):
                g = {k: rng.gauss(0, SESSION) for k in i8}
                per = []
                for _p in range(npass):
                    per.append({k: tv[k] + g[k] + rng.gauss(0, SIG_K1 / (math.sqrt(3) if k in core else 1.0)) for k in i8})
                Dm = {k: statistics.mean(p[k] for p in per) for k in i8}
                b, se, _ = S.ols(flips, [Dm[k] for k in i8])
                hw = S.t975(len(i8) - 2) * se
                iv = {"lo": (b - hw) / R8 * 1e15, "hi": (b + hw) / R8 * 1e15}
                wE.append(S.size_of(iv, lineE))
                wP.append(S.size_of(iv, lineP))
                rr.append(S.spearman([ks[k]["P_w"]["a3"] for k in i8], [Dm[k] for k in i8]) >= rho_crit)
                fa, fb = [], []
                for p in per:
                    co = FE.solve(Xq, [p[k] for k in qkeys])
                    fa.append(co[-2])
                    fb.append(co[-1])
                qa.append(S.interval(fa)["hw"])
                qb.append(S.interval(fb)["hw"])
            out["cases"][f"KINDS|{npass} passes|truth {tn}"] = {
                "W_size_E_PASS": share(wE, "PASS"), "W_size_P_PASS": share(wP, "PASS"), "W_size_P_FAIL_HIGH": share(wP, "FAIL HIGH"),
                "R_PASS": round(sum(rr) / len(rr), 4), "Q_median_halfwidth_beta_A_w": round(statistics.median(qa), 5),
                "Q_median_halfwidth_beta_B_w": round(statistics.median(qb), 5)}
    js = json.dumps(out, indent=1, sort_keys=True) + "\n"
    L = ["E182 power (power_e182.py): shares of verdicts over simulated sessions; BASE = E178's per-launch noise, DOUBLED = twice it.",
         f"trains: sigma_q int8 {sig['int8']} W, fp32 {sig['fp32']} W; kappa {KAPPA} W; quad loss {P_LOSS}; {DRAWS} draws a case.",
         f"kinds passes: one read 0.125/sqrt2 W, three reads 0.125/sqrt6, session term {SESSION} W; {DRAWS_K} draws; rho line (n 20) {rho_crit:.4f}.", ""]
    for k, v in out["cases"].items():
        L.append(f"{k}: " + json.dumps(v, sort_keys=True))
    txt = "\n".join(L) + "\n"
    if a.check:
        ok = open(os.path.join(D, "power-e182.json")).read() == js and open(os.path.join(D, "power-e182.txt")).read() == txt
        print("CHECK PASS" if ok else "CHECK FAIL")
        return 0 if ok else 1
    open(os.path.join(D, "power-e182.json"), "w").write(js)
    open(os.path.join(D, "power-e182.txt"), "w").write(txt)
    print("wrote power-e182.json and power-e182.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
