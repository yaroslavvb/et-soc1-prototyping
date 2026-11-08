#!/usr/bin/env python3
"""E186 (Q158): the power of every registered rule, by simulation from committed noise (E186.md section 6). Standard library only.

    /usr/bin/python3 -B power_e186.py --root .            # writes power-e186.json and power-e186.txt beside this file
    /usr/bin/python3 -B power_e186.py --root . --check    # recomputes both and compares them byte for byte

THE TRAINS (plan-e186.json's ten, each with its processes and first orientation): E182's simulator, power_e182.sim_train, imported
unchanged: a quad's contrast drawn N(x + o kappa, sigma_q^2), o = +1 in SFFS and -1 in FSSF, kappa 0.009 W, each quad lost with chance
0.01; then e182_stats' statistics and e186_stats' words, exactly as the scorer reads them. Three noises:
  REGISTERED  E182's registered sigma_q (noise-e182.json: int8 0.03485, float 0.03804 W; fp16 takes the float figure, as E182's sizing did);
  MEASURED    sigma_q set so that a train's se is E182's measured one (int8 the median of T1-T4, fp32 the mean of T5 and T6; fp16 none was
              measured, fp32's stands in): sigma_q = se x sqrt(3 x processes);
  DOUBLED     twice REGISTERED (E182's DOUBLED, Q150's allowance for switching transients).
THE WORLDS (each train's true difference):
  M12         M12's central lines (candidates-m12-e186.json; H16 at F16-SAME);
  M12-DRAWN   M12 with its own parameter uncertainty: each draw takes M12's int8 and float parameters from N(b, cov) (m12.json) and forms each
              train from its design-row difference (a float train adds P10's difference);
  M12-H16S    M12's central lines with H16 at the fp16-scaled arm (forecast-e186.json);
  M10         M10's lines.
THE FALLBACK'S LEVELS (E186-LV, kinds passes only): E182's kinds-pass noise as registered (E178.md section 6): a read 0.125 / sqrt 2 W, a
session term 0.041 W a kind; five passes; the int8 anchor int8.full read the same way; the rule's own bootstrap (2,000 draws).
Seeds random.Random(18600 + case index): 1,000 draws a train case (a session of ten trains each), 400 a levels case.
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
import e186_stats as R  # noqa: E402
S = R.S
sys.path.insert(0, os.path.join(HERE, "..", "e182"))
import power_e182 as PE  # noqa: E402  (sim_train and resid_sd only, unchanged)

DRAWS, DRAWS_LV = 1000, 400
TRN_SIG = {"int8": 0.03485, "float": 0.03804}   # E182-TR-N's forecast sigma_q (noise-e182.json), asserted below


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


def share(lst, word):
    return round(sum(1 for v in lst if v == word) / len(lst), 4) if lst else None


def shares(lst):
    out = {}
    for w in sorted(set(lst)):
        out[w] = share(lst, w)
    return out


def build(root):
    fc = json.load(open(os.path.join(HERE, "forecast-e186.json")))
    pl = json.load(open(os.path.join(HERE, "plan-e186.json")))
    cj = json.load(open(os.path.join(root, "tools/claims-v3/m12/candidates-m12-e186.json")))
    m = json.load(open(os.path.join(root, "tools/claims-v3/m12/m12.json")))
    nz = json.load(open(os.path.join(root, "tools/claims-v3/e182/noise/noise-e182.json")))
    assert nz["sigma_q_w"] == TRN_SIG, nz["sigma_q_w"]
    se_m = cj["train_noise"]["measured"]["se_w"]
    trains = pl["trains"]
    ids = [t["train"] for t in trains]
    FT, D = fc["trains"], fc["derived"]
    K = cj["kinds"]
    dr = {}
    for t in ids:
        a, b = FT[t]["first"], FT[t]["second"]
        dr[t] = [x - y for x, y in zip(K[a]["design_row"], K[b]["design_row"])]
    L8, Lf = chol(m["int8"]["cov"]), chol(m["float"]["cov"])
    noises = {}
    for t in trains:
        fam = "int8" if t["type"] == "int8" else "float"
        sm = se_m["int8"] if t["type"] == "int8" else se_m["fp32"]
        noises.setdefault("REGISTERED", {})[t["train"]] = TRN_SIG[fam]
        noises.setdefault("MEASURED", {})[t["train"]] = sm * math.sqrt(3 * t["processes"])
        noises.setdefault("DOUBLED", {})[t["train"]] = 2 * TRN_SIG[fam]
    out = {"_what": "E186's power figures (power_e186.py), by simulation from committed noise", "draws": DRAWS, "draws_levels": DRAWS_LV,
           "kappa_w": PE.KAPPA, "p_loss": PE.P_LOSS, "sigma_q_w": noises, "cases": {}, "levels": {}}
    case = [0]

    def rng_next():
        case[0] += 1
        return random.Random(18600 + case[0])

    def truths(world, rng):
        if world == "M10":
            return {t: FT[t]["M10_w"] for t in ids}
        if world == "M12-DRAWN":
            p8, pf = mvn(rng, m["int8"]["b"], L8), mvn(rng, m["float"]["b"], Lf)
            out_t = {}
            for t in ids:
                if FT[t]["type"] == "int8":
                    out_t[t] = sum(x * y for x, y in zip(dr[t], p8))
                else:
                    out_t[t] = FT[t]["P10_difference_w"] + sum(x * y for x, y in zip(dr[t], pf))
            return out_t
        tt = {t: FT[t]["M12_w"] for t in ids}
        if world == "M12-H16S":
            tt["H16"] = FT["H16"]["SCALED_w"]
        return tt

    for nk in ("REGISTERED", "MEASURED", "DOUBLED"):
        for world in ("M12", "M12-DRAWN", "M12-H16S", "M10"):
            rng = rng_next()
            central = truths("M12" if world == "M12-DRAWN" else world, None)
            rec = {t: {"sign": [], "size_M12": [], "size_M10": [], "which": [], "hw": []} for t in ids}
            rec["H16"].update({"size_SCALED": [], "word": []})
            der = {k: [] for k in ("SPLIT3", "SPLIT63", "GB", "GA", "S23R", "JOINT_M12", "JOINT_M10", "E186-M", "JOINT_M12_all10",
                                   "JOINT_M10_all10", "E186-M_all10", "TR-N")}
            der_size = {k: [] for k in ("SPLIT3 beta_A", "SPLIT3 beta_B", "SPLIT63 beta_A", "SPLIT63 beta_B", "GB", "GA")}
            for _ in range(DRAWS):
                x = truths(world, rng)
                iv, procs = {}, {}
                for t in trains:
                    tid = t["train"]
                    iv[tid], procs[tid] = PE.sim_train(rng, x[tid], noises[nk][tid], t["processes"], t["orientations"][0])
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
                    z12.append((tid, R.zscore(v, f["M12_w"], f["M12_se_w"])))
                    z10.append((tid, R.zscore(v, f["M10_w"], 0.0)))
                    if tid == "H16":
                        ws = R.size_band(v, f["SCALED_w"], f["SCALED_se_w"])
                        r["size_SCALED"].append(ws)
                        r["word"].append(R.h16_word({"F16-SAME": w12, "SCALED": ws, "M10": w10}))
                for nm in ("SPLIT3", "SPLIT63"):
                    d = D[nm]
                    bA, bB = R.split_from(iv[d["swap"]], iv[d["sign"]], tuple(d["dh_swap_a_b_per_byte"]), tuple(d["dh_sign_a_b_per_byte"]))
                    wa, wb = S.null_of(bA, d["band_w_per_bit"]), S.null_of(bB, d["band_w_per_bit"])
                    der[nm].append(S.split_of(wa, wb))
                    der_size[nm + " beta_A"].append(R.size_band(bA, d["M12_beta_A_w"], d["M12_beta_A_se_w"]))
                    der_size[nm + " beta_B"].append(R.size_band(bB, d["M12_beta_B_w"], d["M12_beta_B_se_w"]))
                for nm in ("GB", "GA"):
                    d = D[nm]
                    g = R.slope_from(iv[d["trains"][0]], iv[d["trains"][1]], d["P10_offsets_w"], d["bits_each"])
                    der[nm].append(S.sign_of(g))
                    der_size[nm].append(R.size_band(g, d["M12_gamma_w"], d["M12_gamma_se_w"]))
                d = D["S23R"]
                der["S23R"].append(S.agrees(R.scaled(iv["S23"], d["factor"]), d["T5"]["lo"], d["T5"]["hi"]))
                j12, j10 = R.joint([z for t_, z in z12 if t_ != "H16"]), R.joint([z for t_, z in z10 if t_ != "H16"])
                der["JOINT_M12"].append(j12["word"])
                der["JOINT_M10"].append(j10["word"])
                der["E186-M"].append(R.models_word(j12["word"], j10["word"]))
                a12, a10 = R.joint([z for _, z in z12]), R.joint([z for _, z in z10])
                der["JOINT_M12_all10"].append(a12["word"])
                der["JOINT_M10_all10"].append(a10["word"])
                der["E186-M_all10"].append(R.models_word(a12["word"], a10["word"]))
                ratios = []
                for fam, members in (("int8", [t for t in ids if FT[t]["type"] == "int8"]), ("float", [t for t in ids if FT[t]["type"] != "int8"])):
                    if members:
                        ratios.append(PE.resid_sd([procs[t] for t in members]) / TRN_SIG[fam])
                r_ = max(ratios)
                der["TR-N"].append("AS FORECAST" if r_ <= 1.25 else ("WORSE" if r_ <= 2.0 else "FAILS"))
            c = {"trains": {}, "derived": {k: shares(v) for k, v in der.items()}, "derived_size_M12": {k: shares(v) for k, v in der_size.items()}}
            for tid in ids:
                r = rec[tid]
                c["trains"][tid] = {"truth_central_w": central[tid],
                                    "sign": shares(r["sign"]), "size_M12": shares(r["size_M12"]), "size_M10": shares(r["size_M10"]),
                                    "which": shares(r["which"]), "median_halfwidth_w": round(statistics.median(r["hw"]), 5)}
                if tid == "H16":
                    c["trains"][tid]["size_SCALED"] = shares(r["size_SCALED"])
                    c["trains"][tid]["word"] = shares(r["word"])
            out["cases"][f"{nk}|{world}"] = c
    # the fallback's levels rule, E186-LV
    lv = fc["levels"]
    keys = list(lv)
    anchor_noise = math.sqrt(0.041 ** 2 + (0.125 / math.sqrt(2)) ** 2 / 5)
    for world in ("M12", "M10"):
        rng = rng_next()
        words = []
        for _ in range(DRAWS_LV):
            shift = rng.gauss(0.0, anchor_noise)      # the session's int8.full against E182's: no true shift, its read noise only
            e12, e10 = [], []
            for k in keys:
                v = lv[k]
                truth = v["M12_w"] if world == "M12" else v["M10_w"]
                dmeas = truth + rng.gauss(0.0, 0.041) + statistics.mean(rng.gauss(0.0, 0.125 / math.sqrt(2)) for _ in range(5))
                l12 = v["M12_w"] + (shift if v["type"] == "int8" else 0.0)
                e12.append(dmeas - l12)
                e10.append(dmeas - v["M10_w"])
            b = R.boot_rms_diff(e12, e10, draws=2000, seed=18660)
            words.append("M12 BETTER" if b["hi95"] < 0 else ("M12 WORSE" if b["lo95"] > 0 else "NOT RESOLVED"))
        out["levels"][world] = shares(words)
    return out


def text(o):
    L = ["E186's power (power_e186.py): shares of simulated sessions giving each word", ""]
    for ck, c in o["cases"].items():
        L.append(f"== {ck}")
        for tid, v in c["trains"].items():
            L.append(f"  {tid:9s} sign {v['sign']}  size_M12 {v['size_M12']}  size_M10 {v['size_M10']}  which {v['which']}  hw {v['median_halfwidth_w']}")
            if "word" in v:
                L.append(f"            size_SCALED {v['size_SCALED']}  H16 word {v['word']}")
        for k, v in c["derived"].items():
            L.append(f"  {k:10s} {v}")
        for k, v in c["derived_size_M12"].items():
            L.append(f"  size against M12, {k}: {v}")
    L.append("== the fallback's levels, E186-LV")
    for w, v in o["levels"].items():
        L.append(f"  truth {w}: {v}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    o = build(os.path.abspath(a.root))
    js, tx = json.dumps(o, indent=1, sort_keys=True) + "\n", text(o)
    fj, ft = os.path.join(HERE, "power-e186.json"), os.path.join(HERE, "power-e186.txt")
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
