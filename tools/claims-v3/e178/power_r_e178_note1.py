#!/usr/bin/env python3
"""E178 (Q146; the kit's dated note 1, KIT.md.dated-note-1.md section 2): E178-R-int8's power at the reading the scorer makes, stated before
any E178 datum. Design arithmetic on committed files; no E178 datum exists and nothing here is a forecast or a verdict.

E178.md section 5 registers E178-R-int8 as "Spearman rho (average ranks for ties) of the SCORED P against the measured D over the 13 int8
kinds", rho >= 0.56; score_e178.py reads it so: the scored P is the frozen P x (each kind's measured rate / E171's rate) (int8: s = 1).
P's frozen ties (int8 ones = 2 = 4 = 8; 3 = 6) do not survive the rate: each kind's measured rate differs from the next by a few parts
in 10^4, so the scored P orders a tied group by measured rate, and "average ranks for ties" never applies to P (the kit verifier's fault
2). power_e178.py's registered power (power-e178.json, E178-R-int8) and A1's (power-e178-a1.json, (A)) were computed on the frozen P,
ties exact. This computes both readings on the SAME draws of D: the registered generator and noise form, unchanged (power_e178.py
random.Random(17805) for the registered grid; power_e178_a1.py's seeds "E178-A1|A|R|<truth>|<n>" and its truths for A1's operand-bit
alternatives; meas_int8, power_e178_a1.py's copy of power_e178.py's draw order), so the frozen column must equal the committed figures
exactly (a check, CHECK lines), and the scored column differs only by the rate:
  scored P_k = frozen P_k x (1 + e_k), e_k ~ N(0, RATE_SD) a kind, drawn anew each session from a SEPARATE generator
  (random.Random("E178-note1|rate|<case>")), RATE_SD = the sd / mean of E171's measured int8 rates over its 21 int8 items (e171.json,
  lab 91f8ae40: 1.6419e-4; post hoc for E171, an input to the noise here). Only the order matters to rho; a tie breaks either way with
  equal chance, as measured-rate noise breaks it (a kind's rate moves its D by about 3e-4 W, far inside D's noise).

    python3 -B tools/claims-v3/e178/power_r_e178_note1.py --root .            # writes power-r-e178-note1.json and .txt (about 2 min)
    python3 -B tools/claims-v3/e178/power_r_e178_note1.py --root . --check    # re-makes both and compares byte for byte
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
E171 = "docs/reports/data/2026-11-05-e171-blind8-aifoundry3/e171.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    D = os.path.join(root, "tools", "claims-v3", "e178")
    sys.path.insert(0, D)
    import power_e178 as PW  # noqa: E402  (the registered noise model's functions, unchanged)
    import power_e178_a1 as A1  # noqa: E402  (A1's meas_int8 and SYS_KIND, unchanged)
    A1.PW = PW
    fc = json.load(open(os.path.join(D, "forecast-e178.json")))
    fz = json.load(open(os.path.join(D, "power-e178.json")))
    fa = json.load(open(os.path.join(D, "power-e178-a1.json")))
    ks = fc["kinds"]
    i8 = sorted(k for k in ks if ks[k]["type"] == "int8")
    P8 = [ks[k]["P_w"]["a3"] for k in i8]
    items = json.load(open(os.path.join(root, E171)))["items"]
    rates = [items[k]["rate"]["mean"] for k in sorted(items) if k.startswith("int8.") and items[k].get("rate")]
    rate_sd = statistics.stdev(rates) / statistics.mean(rates)
    ties = {}
    for k, p in zip(i8, P8):
        ties.setdefault(p, []).append(k)
    tied = [v for v in ties.values() if len(v) > 1]
    out = {"_what": "E178 dated note 1 (KIT.md.dated-note-1.md section 2): E178-R-int8's power on the frozen P (ties exact, as registered) "
                    "and on the scored P (ties broken by the measured rate, as score_e178.py reads it), on the same draws of D",
           "draws": PW.DRAWS, "rho_crit": PW.RHO_CRIT, "kinds": i8, "frozen_P_tied_groups": tied,
           "rate_sd_over_mean": rate_sd, "rate_sd_source": f"{E171} items[int8.*].rate.mean ({len(rates)} items), sd / mean",
           "registered_grid": [], "a1_alternatives": []}
    L = ["E178 dated note 1: E178-R-int8's power at the scorer's reading (power_r_e178_note1.py). 20,000 draws a case; E178.md section 6's",
         f"noise model, unchanged; aifoundry3's frozen P. The frozen P's tied groups: {tied}. The scored P breaks them by the measured rate",
         f"(each kind's rate x (1 + N(0, {rate_sd:.4e})), E171's int8 spread). Both readings on the same draws of D.", ""]

    def scored(rng):
        return [p * (1.0 + rng.gauss(0, rate_sd)) for p in P8]

    # (1) power_e178.py's registered grid: random.Random(17805), its own draw loop (meas_int8 is its copy: A1's (X) checks that)
    L.append("(1) The registered grid (power_e178.py: random.Random(17805) a case; truth P or flat; model error 0 or 0.03 W):")
    ok_all = True
    for n in (4, 3, 2):
        for s1 in (0.10, 0.125, 0.20):
            for msd in (0.0, 0.03):
                for truth in ("P", "flat"):
                    mu = {k: (ks[k]["P_w"]["a3"] if truth == "P" else 1.8) for k in i8}
                    rng = random.Random(17805)
                    rr = random.Random(f"E178-note1|rate|grid|{n}|{s1}|{msd}|{truth}")
                    hf = hs = 0
                    for _ in range(PW.DRAWS):
                        meas = A1.meas_int8(rng, mu, i8, n, s1, msd, lambda s: s / math.sqrt(3))
                        hf += PW.spearman(P8, meas) >= PW.RHO_CRIT
                        hs += PW.spearman(scored(rr), meas) >= PW.RHO_CRIT
                    reg = [c for c in fz["rules"]["E178-R-int8"]["cases"] if c["n"] == n and c["sigma1"] == s1 and c["model_sd"] == msd
                           and c["truth"] == truth][0]
                    same = reg["p_pass"] == hf / PW.DRAWS
                    ok_all &= same
                    out["registered_grid"].append({"n": n, "sigma1": s1, "model_sd": msd, "truth": truth, "p_pass_frozen_P": hf / PW.DRAWS,
                                                   "p_pass_scored_P": hs / PW.DRAWS, "registered_p_pass": reg["p_pass"],
                                                   "frozen_equals_registered": same})
                    if s1 == 0.125:
                        L.append(f"    n {n}, sigma1 {s1}, model {msd}, truth {truth}: PASS {hf / PW.DRAWS:.4f} on the frozen P "
                                 f"(registered {reg['p_pass']:.4f}, {'EQUAL' if same else 'DIFFER'}), {hs / PW.DRAWS:.4f} on the scored P")
    L.append(f"CHECK (1): the frozen-P column equals power-e178.json's E178-R-int8 p_pass in all {len(out['registered_grid'])} cases: "
             f"{'PASS' if ok_all else 'FAIL'}")
    L.append("")
    # (2) A1's (A): the operand-bit alternatives, power_e178_a1.py's seeds and truths, sigma1 0.125, model error 0
    L.append("(2) A1's alternatives (power_e178_a1.py (A): its truths and seeds; sigma1 0.125, model error 0):")
    pcAB = {k: ks[k]["popcount_a_word"] + ks[k]["popcount_b_word"] for k in i8}
    zcAB = {k: 64 - pcAB[k] for k in i8}
    span = max(P8) - min(P8)
    base = min(P8)
    Pa = {k: ks[k]["P_w"]["a3"] for k in i8}
    beta = {"ones_span": span / (max(pcAB.values()) - min(pcAB.values())),
            "ones_bridge": (Pa["int8.neg_ones"] - Pa["int8.ones"]) / (pcAB["int8.neg_ones"] - pcAB["int8.ones"]),
            "zeros_span": span / (max(zcAB.values()) - min(zcAB.values()))}
    truths = {"P": dict(Pa),
              "1-bits of the A and B words, at P's spread": {k: base + beta["ones_span"] * (pcAB[k] - min(pcAB.values())) for k in i8},
              "1-bits of the A and B words, at the bridge's size": {k: base + beta["ones_bridge"] * (pcAB[k] - min(pcAB.values())) for k in i8},
              "0-bits of the A and B words, at P's spread": {k: base + beta["zeros_span"] * (zcAB[k] - min(zcAB.values())) for k in i8},
              "flat": {k: 1.8 for k in i8}}
    ok_a = True
    for tn, tv in truths.items():
        for n in (4, 3):
            rng = random.Random(f"E178-A1|A|R|{tn}|{n}")
            rr = random.Random(f"E178-note1|rate|A|{tn}|{n}")
            hf = hs = 0
            for _ in range(PW.DRAWS):
                meas = A1.meas_int8(rng, tv, i8, n, 0.125, 0.0, lambda s: s / math.sqrt(3))
                hf += PW.spearman(P8, meas) >= PW.RHO_CRIT
                hs += PW.spearman(scored(rr), meas) >= PW.RHO_CRIT
            reg = [c for c in fa["A_rules_under_alternatives"]["cases"] if c["truth"] == tn and c["n"] == n][0]
            same = reg["R_int8_PASS"] == hf / PW.DRAWS
            ok_a &= same
            out["a1_alternatives"].append({"truth": tn, "n": n, "sigma1": 0.125, "p_pass_frozen_P": hf / PW.DRAWS,
                                           "p_pass_scored_P": hs / PW.DRAWS, "a1_R_int8_PASS": reg["R_int8_PASS"], "frozen_equals_a1": same})
            L.append(f"    {tn}, n {n}: PASS {hf / PW.DRAWS:.4f} on the frozen P (A1 {reg['R_int8_PASS']:.4f}, {'EQUAL' if same else 'DIFFER'}), "
                     f"{hs / PW.DRAWS:.4f} on the scored P")
    L.append(f"CHECK (2): the frozen-P column equals power-e178-a1.json's (A) R_int8_PASS in all {len(out['a1_alternatives'])} cases: "
             f"{'PASS' if ok_a else 'FAIL'}")
    out["checks"] = {"registered_grid_reproduced": ok_all, "a1_alternatives_reproduced": ok_a}
    js = json.dumps(out, indent=1, sort_keys=True) + "\n"
    txt = "\n".join(L) + "\n"
    pj, pt = os.path.join(D, "power-r-e178-note1.json"), os.path.join(D, "power-r-e178-note1.txt")
    if a.check:
        same = open(pj).read() == js and open(pt).read() == txt
        print(txt, end="")
        print(f"CHECK {'PASS' if same else 'FAIL'}: power-r-e178-note1.json and .txt re-made {'byte for byte' if same else 'with differences'}")
        return 0 if same and ok_all and ok_a else 1
    open(pj, "w").write(js)
    open(pt, "w").write(txt)
    print(txt, end="")
    return 0 if ok_all and ok_a else 1


if __name__ == "__main__":
    sys.exit(main())
