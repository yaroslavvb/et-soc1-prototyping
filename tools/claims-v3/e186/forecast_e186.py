#!/usr/bin/env python3
"""E186 (Q158): the registered forecast lines (E186.md section 4), from frozen files only. Nothing is fitted here.

    /usr/bin/python3 -B forecast_e186.py --root .            # writes forecast-e186.json and forecast-e186.txt beside this file
    /usr/bin/python3 -B forecast_e186.py --root . --check    # recomputes both and compares them byte for byte

Its inputs, each checked by sha256 before use: M12's frozen forecasts for E186's merged list (candidates-m12-e186.json, frozen Sun 8 Nov 2026
06:56:00 PST) and M12's own frozen candidates (candidates-m12.json, 05:07:07 PST), which the first carries unchanged; M12's parameters
(m12.json) for the derived quantities' se; M12's dated note 2 (note2-m12.json > f4_fp16) for the fp16-scaled arm, frozen HERE as E186's
own; E182's trains (trains-e182.json > T5) for S23's repeat of T5; the session's trains and the fallback's kinds from plan-e186.json. Every line is at aifoundry3, s = 1 and the candidates' rates; the scorer
applies the session's s and measured rates by `lines_at` (E186.md section 4.2), which this file defines and the scorer imports.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = {
    "tools/claims-v3/m12/candidates-m12-e186.json": "810423fa5d439dcc3f61fbe9bbbda411cada138f46f9cbe16a13e0c3adae4d1b",
    "tools/claims-v3/m12/candidates-m12.json": "e97a2ae4fb27d6d161d1fd209f13a7fad91c10c1455a86b984625862fb734907",
    "tools/claims-v3/m12/m12.json": "34118a60d338a33c0d4983f51f438156d9b9065a7ec1864f87b6b4da1ca05e56",
}
NOTE2 = "tools/claims-v3/m12/note2-m12.json"
E182_TRAINS = "docs/reports/data/2026-11-08-e182-one-number-r2-aifoundry3/trains-e182.json"
PLAN = "tools/claims-v3/e186/plan-e186.json"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def build(root):
    for p, h in FROZEN.items():
        got = sha(os.path.join(root, p))
        assert got == h, f"{p}: sha256 {got} is not the frozen {h}"
    cj = json.load(open(os.path.join(root, "tools/claims-v3/m12/candidates-m12-e186.json")))
    m = json.load(open(os.path.join(root, "tools/claims-v3/m12/m12.json")))
    n2 = json.load(open(os.path.join(root, NOTE2)))["f4_fp16"]
    t5 = json.load(open(os.path.join(root, E182_TRAINS)))["trains"]["T5"]["estimate"]
    T, K = cj["trains"], cj["kinds"]
    pl = json.load(open(os.path.join(root, PLAN)))
    SESSION, FALLBACK_KINDS = pl["session_trains"], pl["plans"]["PASSES"]["kinds"]
    assert all(t in T for t in SESSION) and len(set(SESSION)) == len(SESSION)
    out = {"_what": "E186's registered forecast lines (forecast_e186.py; E186.md section 4)", "card": "aifoundry3 card 0, 600 MHz pinned",
           "frozen_inputs_sha256": dict(FROZEN), "inputs_sha256": {p: sha(os.path.join(root, p)) for p in (NOTE2, E182_TRAINS, PLAN)},
           "at": "s = 1 and the candidates' rates (" + ", ".join(f"{k} {v:.6e}" for k, v in cj["rates_per_s"].items()) + " a second); the scorer "
                 "applies the session's s and measured rates by lines_at()", "rates_per_s": cj["rates_per_s"], "trains": {}, "derived": {}, "levels": {}}
    # 1. every train of the merged list: M12 (its se) and M10, from the frozen file
    for tid, v in T.items():
        r = {"first": v["first"], "second": v["second"], "type": v["type"], "M12_w": v["M12_w"], "M12_se_w": v["M12_se_w"], "M10_w": v["M10_w"],
             "M12_from": v["M12_from"], "d_pc_a": v["d_pc_a"], "d_pc_b": v["d_pc_b"], "in_session": tid in SESSION,
             "P10_difference_w": K[v["first"]]["P10_w"] - K[v["second"]]["P10_w"]}
        if v["type"] == "int8":
            r["M12_int8_flip_part_w"] = sum((K[v["first"]]["design_row"][i] - K[v["second"]]["design_row"][i]) * m["int8"]["b"][i] for i in (1, 2))
        out["trains"][tid] = r
    # 2. H16's fp16-scaled arm (M12's verifier's fault 4), frozen here as E186's own
    h = T["H16"]
    assert abs(n2["H16_M12_F16_SAME_w"] - h["M12_w"]) < 1e-15
    out["trains"]["H16"]["SCALED_w"] = n2["H16_at_fp16_slope_w"]
    out["trains"]["H16"]["SCALED_se_w"] = n2["H16_at_fp16_slope_se_w"]
    out["trains"]["H16"]["SCALED_rule"] = ("F16-SAME's H16 times fp16's held-bit level a bit as a fraction of F16-SAME's, "
                                           f"{n2['fp16_13_kinds']['slope']:.6f} (se {n2['fp16_13_kinds']['se']:.6f}), regressed through 0 on E178's 13 fp16 "
                                           "kinds (note2-m12.json > f4_fp16); post hoc in its making, frozen here before any E186 datum")
    # 3. the derived quantities
    b8, c8 = m["int8"]["b"], m["int8"]["cov"]
    bf, cf = m["float"]["b"], m["float"]["cov"]
    for name, sw, sg in (("SPLIT3", "Q3-swap", "Q3-sign"), ("SPLIT63", "Q63-swap", "Q63-sign")):
        dsw = (T[sw]["d_pc_a"] / 4, T[sw]["d_pc_b"] / 4)
        dsg = (T[sg]["d_pc_a"] / 4, T[sg]["d_pc_b"] / 4)
        (a1, b1), (a2, b2) = dsw, dsg
        det = a1 * b2 - b1 * a2
        m10a = (b2 * T[sw]["M10_w"] - b1 * T[sg]["M10_w"]) / det
        m10b = (-a2 * T[sw]["M10_w"] + a1 * T[sg]["M10_w"]) / det
        m12a = (b2 * T[sw]["M12_w"] - b1 * T[sg]["M12_w"]) / det
        m12b = (-a2 * T[sw]["M12_w"] + a1 * T[sg]["M12_w"]) / det
        assert abs(m12a - b8[3]) < 1e-12 and abs(m12b - b8[4]) < 1e-12, (name, m12a, m12b)
        out["derived"][name] = {"swap": sw, "sign": sg, "dh_swap_a_b_per_byte": dsw, "dh_sign_a_b_per_byte": dsg,
                                "M12_beta_A_w": b8[3], "M12_beta_A_se_w": math.sqrt(c8[3][3]), "M12_beta_B_w": b8[4],
                                "M12_beta_B_se_w": math.sqrt(c8[4][4]), "M10_beta_A_w": m10a, "M10_beta_B_w": m10b, "band_w_per_bit": 0.002}
    for name, x, y, idx in (("GB", "B23-B15", "B15-B7", 2), ("GA", "A23-A15", "A15-A7", 1)):
        nb = T[x]["d_pc_a"] + T[x]["d_pc_b"] + T[y]["d_pc_a"] + T[y]["d_pc_b"]
        offs = (out["trains"][x]["P10_difference_w"], out["trains"][y]["P10_difference_w"])
        m12 = ((T[x]["M12_w"] + T[y]["M12_w"]) - (offs[0] + offs[1])) / nb
        assert abs(m12 - bf[idx]) < 1e-12, (name, m12, bf[idx])
        out["derived"][name] = {"trains": [x, y], "bits": nb, "bits_each": [T[x]["d_pc_a"] + T[x]["d_pc_b"], T[y]["d_pc_a"] + T[y]["d_pc_b"]],
                                "P10_offsets_w": list(offs), "M12_gamma_w": bf[idx], "M12_gamma_se_w": math.sqrt(cf[idx][idx]),
                                "M10_gamma_w": 0.0, "side": "B" if name == "GB" else "A"}
    out["derived"]["S23R"] = {"train": "S23", "factor": 23 / 16, "T5": {k: t5[k] for k in ("mean", "lo", "hi", "se", "df", "n")},
                              "T5_source": "E182-F, blind, registered: trains-e182.json > T5 > estimate",
                              "M12_S23_times_factor_w": T["S23"]["M12_w"] * 23 / 16, "M10_S23_times_factor_w": T["S23"]["M10_w"] * 23 / 16}
    # 4. the fallback's levels (E186-LV): the 15 kinds, M12 (its se) and M10, and the int8 session anchor's E182 value
    for k in FALLBACK_KINDS:
        v = K[k]
        row = {"e186_id": v["e186_id"], "type": v["type"], "M12_w": v["M12_w"], "M12_se_w": v["M12_se_w"], "M10_w": v["M10_w"]}
        if v["type"] == "fp16":
            row["SCALED_w"] = v["P10_w"] + bf[0] + n2["fp16_13_kinds"]["slope"] * (v["M12_w"] - v["P10_w"] - bf[0])
        out["levels"][k] = row
    out["int8_session_anchor"] = {"form": "M12-S1's: every int8 kind's M12 level moves by D(int8.full, the session) - D(int8.full, E182)",
                                  "D_int8_full_E182_w": m["arm_S1"]["D_int8_full_e182_w"], "source": "m12.json > arm_S1 (E182's e182.json > items)"}
    return out


def lines_at(fc, tid, s_float, rate_meas, rate_frozen):
    """the train's lines at scoring (E186.md section 4.2): P10's difference takes the session's float scale s (floats; int8 s = 1) and the
    ratio of the pair's measured rate to the candidates' rate, as score_e182.py's scaled() does; M12's increment takes no scale, but its
    int8 flip part takes the rate ratio. Returns {'M12': (line, se), 'M10': (line, 0), and for H16 'SCALED': (line, se)}."""
    t = fc["trains"][tid]
    s = 1.0 if t["type"] == "int8" else s_float
    q = rate_meas / rate_frozen
    p10 = t["P10_difference_w"] * s * q
    if t["type"] == "int8":
        fl = t["M12_int8_flip_part_w"]
        m12 = fl * q + (t["M12_w"] - fl)
    else:
        m12 = p10 + (t["M12_w"] - t["P10_difference_w"])
    out = {"M12": (m12, t["M12_se_w"]), "M10": (p10, 0.0)}
    if "SCALED_w" in t:
        out["SCALED"] = (p10 + (t["SCALED_w"] - t["P10_difference_w"]), t["SCALED_se_w"])
    return out


def text(o):
    L = ["E186's registered forecast lines (forecast_e186.py), aifoundry3, s = 1, the candidates' rates; W, a train = D(first) - D(second)", "",
         f"{'train':9s} {'in E186':7s} {'M12':>9s} {'se':>7s} {'M10':>9s}  first - second"]
    for tid, v in sorted(o["trains"].items(), key=lambda kv: (not kv[1]["in_session"], kv[0])):
        L.append(f"{tid:9s} {'yes' if v['in_session'] else 'reserve':7s} {v['M12_w']:+9.4f} {v['M12_se_w']:7.4f} {v['M10_w']:+9.4f}  {v['first']} - {v['second']}")
    h = o["trains"]["H16"]
    L += ["", f"H16's fp16-scaled arm (frozen here): {h['SCALED_w']:+.4f} W (se {h['SCALED_se_w']:.4f}); F16-SAME {h['M12_w']:+.4f}; M10 {h['M10_w']:+.4f}", ""]
    for n in ("SPLIT3", "SPLIT63"):
        d = o["derived"][n]
        L.append(f"{n}: {d['swap']} and {d['sign']}; M12 beta_A {d['M12_beta_A_w']:+.5f} ({d['M12_beta_A_se_w']:.5f}), beta_B {d['M12_beta_B_w']:+.5f} "
                 f"({d['M12_beta_B_se_w']:.5f}); M10 beta_A {d['M10_beta_A_w']:+.5f}, beta_B {d['M10_beta_B_w']:+.5f} W a held 1-bit a byte")
    for n in ("GB", "GA"):
        d = o["derived"][n]
        L.append(f"{n}: {d['trains'][0]} + {d['trains'][1]}, {d['bits']} bits on {d['side']}; offsets {d['P10_offsets_w'][0]:+.5f}, {d['P10_offsets_w'][1]:+.5f}; "
                 f"M12 gamma {d['M12_gamma_w']:+.5f} ({d['M12_gamma_se_w']:.5f}) W a held bit; M10 0")
    d = o["derived"]["S23R"]
    L.append(f"S23R: S23 x 23/16 against E182's T5 {d['T5']['mean']:+.4f} [{d['T5']['lo']:+.4f}, {d['T5']['hi']:+.4f}]; M12's S23 x 23/16 "
             f"{d['M12_S23_times_factor_w']:+.4f}, M10's {d['M10_S23_times_factor_w']:+.4f}")
    L += ["", "The fallback's levels (E186-LV), W over each format's zeros at s = 1:"]
    for k, v in o["levels"].items():
        L.append(f"  {v['e186_id']} {k:24s} M12 {v['M12_w']:.4f} ({v['M12_se_w']:.4f})  M10 {v['M10_w']:.4f}" + (f"  SCALED {v['SCALED_w']:.4f}" if "SCALED_w" in v else ""))
    L.append(f"  int8 session anchor: D(int8.full, E182) = {o['int8_session_anchor']['D_int8_full_E182_w']:.6f} W")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    o = build(os.path.abspath(a.root))
    js, tx = json.dumps(o, indent=1, sort_keys=True) + "\n", text(o)
    fj, ft = os.path.join(HERE, "forecast-e186.json"), os.path.join(HERE, "forecast-e186.txt")
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
