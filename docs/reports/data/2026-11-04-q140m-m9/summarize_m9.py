#!/usr/bin/env python3
"""Q140(m): the README's tables from the frozen outputs (nested-m9.json, rows-m9.json), nothing refitted. Adds what the per-family
tables of nested-m9.json do not hold: pool 6's three formats together per card, M9's nested errors against M8's, M7's and M6's
registered blind errors (E153's and E157's power_rows, their predictions at the nominal rate) and against their errors at each row's
measured rate, with paired bootstraps over tiles (2,000 draws, seed 140), and pool 6 by case. Writes summary-m9.json and .txt.

    python3 summarize_m9.py
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SIX = ("fp32.b_onebit_b20_third", "int8.a_zeros_b_lineflip", "int8.b_line_zero_ff",
       "int8.bheld_bit1", "int8.bheld_bit4", "int8.bheld_bit7")
EXP = {"a3": "E153", "c1": "E157"}


def rms(v):
    v = np.asarray(v, float)
    return float(np.sqrt(np.mean(v ** 2))) if len(v) else None


def boot(ea, eb, seed=140, n=2000):
    ea, eb = np.asarray(ea, float), np.asarray(eb, float)
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(n):
        i = rng.integers(0, len(ea), len(ea))
        d.append(rms(ea[i]) - rms(eb[i]))
    lo, hi = np.quantile(d, [0.025, 0.975])
    return {"d_rms_w": rms(ea) - rms(eb), "lo95": float(lo), "hi95": float(hi), "resolved": bool(hi < 0 or lo > 0), "n_tiles": len(ea)}


def main():
    n = json.load(open(os.path.join(HERE, "nested-m9.json")))
    reg = n["check_frozen_pool6"]["registered_errors"]
    rows = []
    for fam in ("float", "int8"):
        rows += n["families"][fam]["pool6_rows"]
    out = {"_note": "Q140(m) summarize_m9.py: derived from nested-m9.json, nothing refitted", "combined": {}, "by_case": {}}
    L = ["Q140(m) summarize_m9.py (from nested-m9.json; nothing refitted)", ""]
    subsets = (("priority 1 (30 kinds)", lambda r: r["priority"] == 1), ("all 44 new kinds", lambda r: True),
               ("priority 1 without the six (24)", lambda r: r["priority"] == 1 and r["key"] not in SIX),
               ("all 44 without the six (38)", lambda r: r["key"] not in SIX))
    for cd in ("a3", "c1"):
        for lab, keep in subsets:
            rr = [r for r in rows if r["card"] == cd and keep(r)]
            e9 = [r["M9_nested"] for r in rr]
            res = {"n": len(rr), "M9_nested": {"rms_w": rms(e9), "bias_w": float(np.mean(e9))}}
            for m in ("M8", "M7", "M6"):
                er = [reg[m][EXP[cd]][r["key"]] for r in rr]
                em = [r[f"{m}_frozen"] for r in rr]
                res[f"{m}_registered_blind"] = {"rms_w": rms(er), "bias_w": float(np.mean(er))}
                res[f"{m}_frozen_measured_rate"] = {"rms_w": rms(em), "bias_w": float(np.mean(em))}
                res[f"M9_nested - {m}_registered_blind"] = boot(e9, er)
                res[f"M9_nested - {m}_frozen_measured_rate"] = boot(e9, em)
            for m in ("M8_form_loko", "M7_form_loko", "M6_form_loko"):
                ef = [r[m] for r in rr]
                res[m] = {"rms_w": rms(ef), "bias_w": float(np.mean(ef))}
                res[f"M9_nested - {m}"] = boot(e9, ef)
            for t in ("fp32", "fp16", "int8"):
                rt = [r for r in rr if r["key"].startswith(t + ".")]
                if rt:
                    res[f"by_format {t}"] = {"n": len(rt), "M9_nested": rms([r["M9_nested"] for r in rt]),
                                             **{f"{m}_registered_blind": rms([reg[m][EXP[cd]][r["key"]] for r in rt]) for m in ("M8", "M7", "M6")}}
            out["combined"][f"{cd} | {lab}"] = res
            L.append(f"{cd} | {lab}: n {len(rr)}; M9 nested {res['M9_nested']['rms_w']:.3f} (bias {res['M9_nested']['bias_w']:+.3f}); registered blind "
                     + ", ".join(f"{m} {res[f'{m}_registered_blind']['rms_w']:.3f}" for m in ("M8", "M7", "M6"))
                     + "; M9 - M6 reg " + "{d_rms_w:+.3f} [{lo95:+.3f}, {hi95:+.3f}]".format(**res["M9_nested - M6_registered_blind"])
                     + "; M9 - M8 reg " + "{d_rms_w:+.3f} [{lo95:+.3f}, {hi95:+.3f}]".format(**res["M9_nested - M8_registered_blind"])
                     + "; M9 - M7 reg " + "{d_rms_w:+.3f} [{lo95:+.3f}, {hi95:+.3f}]".format(**res["M9_nested - M7_registered_blind"]))
            for t in ("fp32", "fp16", "int8"):
                b = res.get(f"by_format {t}")
                if b:
                    L.append(f"     {t} ({b['n']}): M9 {b['M9_nested']:.3f}; M8 {b['M8_registered_blind']:.3f}, M7 {b['M7_registered_blind']:.3f}, M6 {b['M6_registered_blind']:.3f}")
    L.append("")
    L.append("pool 6 by case (both cards, all 44 new kinds): rms W, M9 nested / M8, M7, M6 registered blind")
    cases = sorted({r["case"] for r in rows})
    for c in cases:
        rr = [r for r in rows if r["case"] == c]
        res = {"n": len(rr), "M9_nested": rms([r["M9_nested"] for r in rr]), "M9_mean": float(np.mean([r["M9_nested"] for r in rr]))}
        for m in ("M8", "M7", "M6"):
            res[f"{m}_registered_blind"] = rms([reg[m][EXP[r["card"]]][r["key"]] for r in rr])
        out["by_case"][c] = res
        L.append(f"   {c} ({res['n']}): M9 {res['M9_nested']:.3f} (mean {res['M9_mean']:+.3f}); M8 {res['M8_registered_blind']:.3f}, M7 {res['M7_registered_blind']:.3f}, M6 {res['M6_registered_blind']:.3f}")
    L.append("")
    L.append("the six named-miss tiles (both cards): M9 nested / M8, M7, M6 registered blind, W")
    for k in SIX:
        for cd in ("a3", "c1"):
            r = next(x for x in rows if x["key"] == k and x["card"] == cd)
            L.append(f"   {k} {cd}: M9 {r['M9_nested']:+.3f}; M8 {reg['M8'][EXP[cd]][k]:+.3f}, M7 {reg['M7'][EXP[cd]][k]:+.3f}, M6 {reg['M6'][EXP[cd]][k]:+.3f}")
    json.dump(out, open(os.path.join(HERE, "summary-m9.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(HERE, "summary-m9.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
