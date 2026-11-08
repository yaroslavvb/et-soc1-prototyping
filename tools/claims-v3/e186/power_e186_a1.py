#!/usr/bin/env python3
"""E186 dated amendment A1 (Q158, fix-e186; verify-e186's fault 2): the power of E186-M in the branch where the session's float scale s is
not read (E186.md section 4.2's fail-closed clause), with power_e186.py's simulator unchanged. Standard library only.

    /usr/bin/python3 -B power_e186_a1.py --root .            # writes power-e186-a1.json and power-e186-a1.txt beside this file
    /usr/bin/python3 -B power_e186_a1.py --root . --check    # recomputes both and compares them byte for byte

THE SESSIONS ARE power_e186.py's OWN. Its build() is not called; its loop is re-run here draw for draw: the same twelve cases in its order
(REGISTERED, MEASURED, DOUBLED x M12, M12-DRAWN, M12-H16S, M10), the same seeds (random.Random(18600 + case index), 1,000 sessions a case),
the same truths (power_e186's mvn and chol on m12.json's covariances for M12-DRAWN) and the same ten trains drawn by power_e182.sim_train in
plan order, which is every draw power_e186's loop takes from its generator; nothing after the trains draws from it. So each simulated
session is the registered power's session, and THE CHECK comes first: E186-M over the nine trains other than H16, read here on these
sessions with e186_stats' words, must give power-e186.json's committed shares in every case, else this script refuses (exit 3).
THE BRANCH (A1-1): when s is not read the four ladder trains (B15-B7, B23-B15, A15-A7, A23-A15) carry no line, so E186-M reads over the
other five: S23, Q63-sign, Q63-swap, Q3-sign and Q3-swap (Q = sum z^2 against chi-square at 5 degrees of freedom, e186_stats.joint).
Reported beside: the same over all six non-ladder trains (H16 in), the branch's form of the reported all-ten joint word.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e186_stats as R  # noqa: E402
import power_e186 as P  # noqa: E402  (chol, mvn, shares, DRAWS, TRN_SIG and its noises' rule; build() is not called)
PE = P.PE                # power_e182, as power_e186 imports it (sim_train)

LADDERS = ("B15-B7", "B23-B15", "A15-A7", "A23-A15")
BRANCH = ("S23", "Q63-sign", "Q63-swap", "Q3-sign", "Q3-swap")
CASES = [(nk, w) for nk in ("REGISTERED", "MEASURED", "DOUBLED") for w in ("M12", "M12-DRAWN", "M12-H16S", "M10")]


def build(root):
    fc = json.load(open(os.path.join(HERE, "forecast-e186.json")))
    pl = json.load(open(os.path.join(HERE, "plan-e186.json")))
    cj = json.load(open(os.path.join(root, "tools/claims-v3/m12/candidates-m12-e186.json")))
    m = json.load(open(os.path.join(root, "tools/claims-v3/m12/m12.json")))
    nz = json.load(open(os.path.join(root, "tools/claims-v3/e182/noise/noise-e182.json")))
    reg = json.load(open(os.path.join(HERE, "power-e186.json")))
    assert nz["sigma_q_w"] == P.TRN_SIG, nz["sigma_q_w"]
    se_m = cj["train_noise"]["measured"]["se_w"]
    trains = pl["trains"]
    ids = [t["train"] for t in trains]
    assert tuple(i for i in ids if i not in LADDERS and i != "H16") == BRANCH, ids
    FT = fc["trains"]
    K = cj["kinds"]
    dr = {t: [x - y for x, y in zip(K[FT[t]["first"]]["design_row"], K[FT[t]["second"]]["design_row"])] for t in ids}
    L8, Lf = P.chol(m["int8"]["cov"]), P.chol(m["float"]["cov"])
    noises = {}
    for t in trains:
        fam = "int8" if t["type"] == "int8" else "float"
        sm = se_m["int8"] if t["type"] == "int8" else se_m["fp32"]
        noises.setdefault("REGISTERED", {})[t["train"]] = P.TRN_SIG[fam]
        noises.setdefault("MEASURED", {})[t["train"]] = sm * (3 * t["processes"]) ** 0.5
        noises.setdefault("DOUBLED", {})[t["train"]] = 2 * P.TRN_SIG[fam]
    if noises != reg["sigma_q_w"]:
        raise SystemExit("the noises differ from power-e186.json's sigma_q_w: refusing")

    def truths(world, rng):
        if world == "M10":
            return {t: FT[t]["M10_w"] for t in ids}
        if world == "M12-DRAWN":
            p8, pf = P.mvn(rng, m["int8"]["b"], L8), P.mvn(rng, m["float"]["b"], Lf)
            return {t: (sum(x * y for x, y in zip(dr[t], p8)) if FT[t]["type"] == "int8"
                        else FT[t]["P10_difference_w"] + sum(x * y for x, y in zip(dr[t], pf))) for t in ids}
        tt = {t: FT[t]["M12_w"] for t in ids}
        if world == "M12-H16S":
            tt["H16"] = FT["H16"]["SCALED_w"]
        return tt

    out = {"_what": "E186.md.dated-amendment-A1.md: E186-M's power when s is not read (power_e186_a1.py), on power_e186.py's own sessions",
           "draws": P.DRAWS, "branch_trains": list(BRANCH), "check_nine_trains_equal_power_e186": {}, "cases": {}}
    bad = []
    for i, (nk, world) in enumerate(CASES, start=1):
        rng = random.Random(18600 + i)
        nine, five, six = [], [], []
        q12, q10 = [], []
        for _ in range(P.DRAWS):
            x = truths(world, rng)
            iv = {}
            for t in trains:
                iv[t["train"]], _p = PE.sim_train(rng, x[t["train"]], noises[nk][t["train"]], t["processes"], t["orientations"][0])
            z12 = {t: R.zscore(iv[t], FT[t]["M12_w"], FT[t]["M12_se_w"]) for t in ids}
            z10 = {t: R.zscore(iv[t], FT[t]["M10_w"], 0.0) for t in ids}
            j = lambda ts: R.models_word(R.joint([z12[t] for t in ts])["word"], R.joint([z10[t] for t in ts])["word"])  # noqa: E731
            nine.append(j([t for t in ids if t != "H16"]))
            a12, a10 = R.joint([z12[t] for t in BRANCH]), R.joint([z10[t] for t in BRANCH])
            five.append(R.models_word(a12["word"], a10["word"]))
            q12.append(a12["Q"])
            q10.append(a10["Q"])
            six.append(j(["H16"] + list(BRANCH)))
        key = f"{nk}|{world}"
        mine, theirs = P.shares(nine), reg["cases"][key]["derived"]["E186-M"]
        out["check_nine_trains_equal_power_e186"][key] = mine == theirs
        if mine != theirs:
            bad.append(f"{key}: {mine} against {theirs}")
        q12.sort()
        q10.sort()
        out["cases"][key] = {"E186-M_nine_trains_registered": mine, "E186-M_s_not_read_five_trains": P.shares(five),
                             "joint_six_trains_with_H16_reported": P.shares(six),
                             "median_Q_five": {"M12": round(q12[len(q12) // 2], 3), "M10": round(q10[len(q10) // 2], 3)}}
    if bad:
        raise SystemExit("REFUSED: these sessions are not power_e186.py's (E186-M over nine differs): " + "; ".join(bad))
    out["check_all_equal"] = True
    return out


def text(o):
    L = ["E186.md.dated-amendment-A1.md: E186-M's power when s is not read (power_e186_a1.py), shares of 1,000 sessions a case,",
         "the sessions power_e186.py's own (its nine-train E186-M shares re-read here equal power-e186.json's in every case: "
         f"{o['check_all_equal']})", "",
         f"{'case':24s} {'E186-M over nine (registered)':40s} {'over the five, s not read (A1-1)':40s} median Q five (M12, M10)"]
    for k, c in o["cases"].items():
        L.append(f"{k:24s} {json.dumps(c['E186-M_nine_trains_registered'], sort_keys=True):40s} "
                 f"{json.dumps(c['E186-M_s_not_read_five_trains'], sort_keys=True):40s} {c['median_Q_five']['M12']}, {c['median_Q_five']['M10']}")
    L += ["", "reported beside (never a verdict): the joint word over the six non-ladder trains, H16 in"]
    for k, c in o["cases"].items():
        L.append(f"  {k:24s} {json.dumps(c['joint_six_trains_with_H16_reported'], sort_keys=True)}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    try:
        o = build(os.path.abspath(a.root))
    except SystemExit as e:
        print(str(e))
        return 3
    js, tx = json.dumps(o, indent=1, sort_keys=True) + "\n", text(o)
    fj, ft = os.path.join(HERE, "power-e186-a1.json"), os.path.join(HERE, "power-e186-a1.txt")
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
