#!/usr/bin/env python3
"""E155 post hoc (deciding nothing; written while the passes ran, before any reduction was read): readings of E155's reduction that the registration
reports without a verdict or does not name, each printed with its inputs.

    python3 docs/reports/data/2026-11-03-e155-int8-floor-rows/posthoc/posthoc_e155.py      # from the repo root; standard library only

1. fp32's three arms solved per pass for its per-op energy e and its price per TenB write pB (S(m0r1) - S(m0r3) and S(m0r3k8) - S(m0r3) against
   the bench's rates and TenB writes a second), and the shared per-op term they imply at three rows, (e + 256 pB) x (r_int8 - r_fp32);
2. Q31k = S(m0r3k8.int8) - S(m0r1.int8), int8 at one row's schedule with the walk on, with B's halving added back at that pass's pB, against the
   walk parts of Wn and Wt (C and T put nothing there);
3. the per-row part's one-term prices at three rows (D31 less each shared term) against E148's sixteen-row prices (94.8 fJ a new-address read,
   50.5 fJ an address-bit toggle), and the residual of each count at E148's price;
4. N3 and D31 against each frozen reading and the null, as errors (this session's measured values minus the predictions);
5. the two sessions' rises side by side (E148's D21, E155's D31) with each count's prediction from each session's own N - N1 where measured.
SPDX-License-Identifier: Apache-2.0"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(D, "..", "..", "..", ".."))
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201}


def ci(v):
    n = len(v)
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1)) if n > 1 else float("nan")
    h = T95[n - 1] * sd / math.sqrt(n) if n > 1 else float("nan")
    return {"mean": m, "half": h, "lo": m - h, "hi": m + h, "n": n, "sd": sd}


def fm(c, k=3, s=1.0):
    return f"{c['mean'] * s:+.{k}f} ± {c['half'] * s:.{k}f}"


def main():
    P = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e155", "predictions-e155.json")))
    red = json.load(open(os.path.join(D, "e155.json")))
    sc = json.load(open(os.path.join(D, "scored.json")))
    e148 = json.load(open(os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e148-int8-excess", "scored.json")))
    pp = red["per_pass"]
    keys = sorted(pp, key=int)
    I8, FP, Q = P["bench_per_s_int8"], P["bench_per_s_fp32_card_order"], P["bench_per_s_card_order"]
    out = {"passes": [int(k) for k in keys]}
    L = [f"E155 post hoc (deciding nothing), {sc['which_reduction_scores']} reduction, {len(keys)} passes; per pass, then mean ± 95% t"]

    def S(k, it):
        return pp[k][it]["S"]

    def r(k, it):
        return pp[k][it]["rate"]
    # 1. fp32's three arms: e and pB per pass, with the bench's TenB writes an op (256 at K = 16, 128 at K = 8) times the measured rates
    e_l, pb_l, sh_l = [], [], []
    for k in keys:
        r1, r3, r3k = r(k, "m0r1.fp32.zeros"), r(k, "m0r3.fp32.zeros"), r(k, "m0r3k8.fp32.zeros")
        b1, b3, b3k = 256 * r1, 256 * r3, 128 * r3k
        y1 = S(k, "m0r1.fp32.zeros") - S(k, "m0r3.fp32.zeros")
        y2 = S(k, "m0r3k8.fp32.zeros") - S(k, "m0r3.fp32.zeros")
        a11, a12, a21, a22 = r1 - r3, b1 - b3, r3k - r3, b3k - b3
        det = a11 * a22 - a12 * a21
        e = (y1 * a22 - a12 * y2) / det
        pb = (a11 * y2 - a21 * y1) / det
        e_l.append(e * 1e12)
        pb_l.append(pb * 1e12)
        dri = r(k, "m0r3.int8.zeros") - r(k, "m0r3.fp32.zeros")
        sh_l.append((e + 256 * pb) * dri)
    out["fp32_solve"] = {"e_pJ": ci(e_l), "pB_pJ_per_TenB_write": ci(pb_l), "shared_w": ci(sh_l)}
    L.append(f"1. fp32's three arms: e {fm(ci(e_l), 1)} pJ an op, pB {fm(ci(pb_l), 3)} pJ a TenB write; shared term at three rows (e + 256 pB) x dr "
             f"{fm(ci(sh_l))} W (frozen: {P['shared_per_op_term']['point']:+.3f} W from E148's E_op; session E_op: {fm(sc['stats']['shared_session_w'])} W)")
    # 2. Q31k with B's halving added back
    q_raw, q_c = [], []
    for k, pb in zip(keys, pb_l):
        q = S(k, "m0r3k8.int8.zeros") - S(k, "m0r1.int8.zeros")
        db = 128 * r(k, "m0r3k8.int8.zeros") - 256 * r(k, "m0r1.int8.zeros")
        q_raw.append(q)
        q_c.append(q - pb * 1e-12 * db)
    qk = P["q31k_reported"]
    out["Q31k"] = {"raw": ci(q_raw), "B_added_back": ci(q_c), "walk_Wn": qk["walk_Wn"], "walk_Wt": qk["walk_Wt"]}
    L.append(f"2. Q31k = S(m0r3k8.int8) - S(m0r1.int8): raw {fm(ci(q_raw))} W; with B's halving added back at each pass's pB {fm(ci(q_c))} W; "
             f"walk parts frozen: Wn {qk['walk_Wn']['point']:+.3f} [{qk['walk_Wn']['lo']:+.3f}, {qk['walk_Wn']['hi']:+.3f}], Wt {qk['walk_Wt']['point']:+.3f} "
             f"[{qk['walk_Wt']['lo']:+.3f}, {qk['walk_Wt']['hi']:+.3f}]; C and T 0")
    # 3. one-term prices at three rows
    d31 = sc["stats"]["D31"]["per_pass"]
    shf = P["shared_per_op_term"]["point"]
    pr = {}
    for lab, sh in (("frozen shared", [shf] * len(keys)), ("fp32 three-arm shared", sh_l),
                    ("session E_op shared", [a - b for a, b in zip(d31, sc["stats"]["D31_less_session_shared"]["per_pass"])])):
        y = [a - b for a, b in zip(d31, sh)]
        pn = ci([v / Q["m0r3"]["newaddr"] * 1e15 for v in y])
        pt = ci([v / Q["m0r3"]["tog"] * 1e15 for v in y])
        pr[lab] = {"D31_less_shared": ci(y), "fJ_newaddr": pn, "fJ_toggle": pt}
        L.append(f"3. D31 less the {lab}: {fm(ci(y))} W -> {fm(pn, 1)} fJ a new-address read (E148 94.8), {fm(pt, 1)} fJ an address-bit toggle (E148 50.5)")
    out["one_term"] = pr
    # 4. errors against each frozen reading
    n3 = sc["stats"]["N3"]["mean"]
    dm = sc["stats"]["D31"]["mean"]
    errs = {}
    for k2, rd in list(P["readings"].items()) + list(P["readings_reported"].items()):
        errs[k2] = {"D31_error_w": dm - rd["point"], "N3_error_from_frozen_w": n3 - (P["e148_reference"]["N1"]["mean"] + rd["point"])}
        L.append(f"4. {k2:12s}: D31 predicted {rd['point']:+.3f}, error {dm - rd['point']:+.3f} W; N3 from E148's N1 {P['e148_reference']['N1']['mean'] + rd['point']:+.3f}, "
                 f"error {errs[k2]['N3_error_from_frozen_w']:+.3f} W")
    out["errors"] = errs
    # 5. the two sessions' rises
    d21 = e148["stats"]["D21"]
    L.append(f"5. E148 D21 (two rows) {fm(d21)} W; E155 D31 (three rows) {fm(sc['stats']['D31'])} W; ratio of means {dm / d21['mean']:.2f} "
             f"(Wn's count terms predict {P['readings']['Wn']['count_term']['point'] / (0.4225 * P['e148_reference']['N_minus_N1']['mean']):.2f} x, "
             f"Wt's {P['readings']['Wt']['count_term']['point'] / (0.2254 * P['e148_reference']['N_minus_N1']['mean']):.2f} x, before the shared terms)")
    json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)
    open(os.path.join(HERE, "posthoc.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
