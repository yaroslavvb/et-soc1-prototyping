#!/usr/bin/env python3
"""The bench's frozen predictions against the experiments they were frozen for. Standard library only.

    score_frozen.py --counts <this dir> --data <docs/reports/data> --kinds <tools/claims-v3/kinds> --out scored-frozen.json

M2: e94-e95-bench-prediction.json, committed 2b7ece4a. M4 and I3: m4-bench-prediction.json, committed b995463e. E95's data commit ab23b1aa came after both. E94's data commit a3824bb8 came
before both, by the clock; it was not read before 2b7ece4a, and it was read before M4's form was chosen, so M4 on E94 is not a test at all and is marked so.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import glob
import json
import math
import os


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def stats(rows, q="pred"):
    if len(rows) < 2:
        return None
    ys = [r["D"] for r in rows]
    ps = [r[q] for r in rows]
    my, mp = sum(ys) / len(ys), sum(ps) / len(ps)
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    sp = math.sqrt(sum((p - mp) ** 2 for p in ps))
    return {"n": len(rows), "rms_w": rms([y - p for y, p in zip(ys, ps)]), "bias_w": sum(p - y for y, p in zip(ys, ps)) / len(rows), "worst_w": max(abs(y - p) for y, p in zip(ys, ps)),
            "r": (sum((y - my) * (p - mp) for y, p in zip(ys, ps)) / (sy * sp)) if sy * sp > 0 else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counts", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--kinds", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    load = lambda p: json.load(open(p))
    M2 = load(f"{a.counts}/e94-e95-bench-prediction.json")["models"]["vpu_map"]
    H2 = load(f"{a.counts}/e94-e95-bench-prediction.json")["models"]["vpu_hier2"]
    M4 = load(f"{a.counts}/m4-bench-prediction.json")
    e95 = load(glob.glob(f"{a.data}/2026-11-01-e95*/e95.json")[0])["items"]
    e94 = load(f"{a.data}/2026-11-01-e94-tile-spread/e94.json")["items"]
    real2 = load(f"{a.kinds}/predictions-e95.json") if os.path.exists(f"{a.kinds}/predictions-e95.json") else {}
    pr2 = load(f"{a.kinds}/real2/predictions-real2.json")["tiles"]
    out = {"_order": __doc__.split("M2:")[1].split("SPDX")[0].strip().replace("\n", " "), "e95": {}, "e94": {}}
    rows = []
    for k, r in M2["e95_aifoundry3"].items():
        it = e95.get(k)
        if not it or not it.get("D") or it["D"].get("mean") is None:
            continue
        m = M4["e95_aifoundry3"][k]
        p = pr2.get(k.replace(".r2_", "/"), {})
        pa = p.get("a_aifoundry3_600mhz", {}).get("D_w")
        row = {"key": k, "type": r["type"], "group": r["group"], "blind": r["blind"], "gate": r["gate_closes"], "D": it["D"]["mean"], "ci95": it["D"].get("ci95"), "M2": r["D_w"], "M2_lo": r["lo95"], "M2_hi": r["hi95"], "H2": H2["e95_aifoundry3"][k]["D_w"],
               "M4": m["D_w"], "M4_lo": m["lo95"], "M4_hi": m["hi95"], "q130n": pa}
        rows.append(row)
    out["e95"]["rows"] = rows
    def block(rs):
        o = {}
        for lab, sel in (("floats", [r for r in rs if r["type"] != "int8"]), ("fp32", [r for r in rs if r["type"] == "fp32"]), ("fp16", [r for r in rs if r["type"] == "fp16"]), ("int8", [r for r in rs if r["type"] == "int8"])):
            if len(sel) < 2:
                continue
            o[lab] = {"M2": stats(sel, "M2"), "M4": stats(sel, "M4"), "H2": stats(sel, "H2")}
            if all(r.get("q130n") is not None for r in sel):
                o[lab]["q130n"] = stats(sel, "q130n")
            o[lab]["M2_inside"] = sum(1 for r in sel if r["M2_lo"] <= r["D"] <= r["M2_hi"])
            o[lab]["M4_inside"] = sum(1 for r in sel if r["M4_lo"] <= r["D"] <= r["M4_hi"])
            o[lab]["n"] = len(sel)
        return o
    blind = [r for r in rows if r["blind"]]
    out["e95"]["blind"] = block(blind)
    out["e95"]["all33"] = block(rows)
    gated = [r for r in blind if r["gate"] >= 0.10]
    dense = [r for r in blind if r["gate"] < 0.10]
    out["e95"]["gated_floats"] = block([r for r in gated if r["type"] != "int8"]).get("floats")
    out["e95"]["dense_floats"] = block([r for r in dense if r["type"] != "int8"]).get("floats")
    r94 = []
    for k, r in M2["e94_card1"].items():
        it = e94[k]
        m = M4["e94_card1_not_blind"][k]
        r94.append({"key": k, "type": r["type"], "rule": r["rule"], "fresh": r["fresh"], "gate": r["gate_closes"], "D": it["D"]["mean"], "M2": r["D_w"], "M2_lo": r["lo95"], "M2_hi": r["hi95"], "H2": H2["e94_card1"][k]["D_w"], "M4": m["D_w"], "M4_lo": m["lo95"], "M4_hi": m["hi95"]})
    out["e94"]["rows"] = r94
    out["e94"]["all51"] = block(r94)
    out["e94"]["fresh42"] = block([r for r in r94 if r["fresh"]])
    by = {}
    for r in r94:
        by.setdefault(f"{r['type']}.{r['rule']}", []).append(r)
    out["e94"]["within_rule"] = {}
    for rk, v in by.items():
        if len(v) < 3:
            continue
        my, mp2, mp4 = sum(r["D"] for r in v) / len(v), sum(r["M2"] for r in v) / len(v), sum(r["M4"] for r in v) / len(v)
        sy = rms([r["D"] - my for r in v])
        out["e94"]["within_rule"][rk] = {"n": len(v), "sd_measured_w": sy, "sd_M2_w": rms([r["M2"] - mp2 for r in v]), "centred_rms_M2_w": rms([(r["D"] - my) - (r["M2"] - mp2) for r in v]), "centred_rms_M4_w": rms([(r["D"] - my) - (r["M4"] - mp4) for r in v]), "bias_M2_w": mp2 - my, "bias_M4_w": mp4 - my}
    json.dump(out, open(a.out, "w"), indent=1)
    def show(n, o):
        for lab, x in o.items():
            print(f"{n:14s} {lab:7s} n {x['n']:2d}  M2 rms {x['M2']['rms_w']:.3f} bias {x['M2']['bias_w']:+.3f} r {x['M2']['r']:.4f} in {x['M2_inside']:2d} | M4 rms {x['M4']['rms_w']:.3f} bias {x['M4']['bias_w']:+.3f} r {x['M4']['r']:.4f} in {x['M4_inside']:2d} | hier2 {x['H2']['rms_w']:.3f}" + (f" | Q130(n) {x['q130n']['rms_w']:.3f}" if 'q130n' in x else ''))
    show("E95 blind", out["e95"]["blind"])
    show("E95 all 33", out["e95"]["all33"])
    print("E95 gated floats", {k: (round(v["rms_w"], 3), round(v["bias_w"], 3)) for k, v in out["e95"]["gated_floats"].items() if isinstance(v, dict)})
    print("E95 dense floats", {k: (round(v["rms_w"], 3), round(v["bias_w"], 3)) for k, v in out["e95"]["dense_floats"].items() if isinstance(v, dict)})
    show("E94 (M2 post hoc by the clock; M4 not a test)", out["e94"]["all51"])
    for rk, v in out["e94"]["within_rule"].items():
        print(f"   within {rk:18s} n {v['n']} sd meas {v['sd_measured_w']:.3f} sd M2 {v['sd_M2_w']:.3f} centred rms M2 {v['centred_rms_M2_w']:.3f} M4 {v['centred_rms_M4_w']:.3f} bias M2 {v['bias_M2_w']:+.3f} M4 {v['bias_M4_w']:+.3f}")
    for r in sorted(rows, key=lambda r: r["D"] - r["M4"]):
        print(f"   {r['key']:40s} {r['group']:12s} g {r['gate']:.2f} D {r['D']:6.2f} ±{(r['ci95'] or 0):4.2f} M2 {r['M2']:6.2f} M4 {r['M4']:6.2f} [{r['M4_lo']:5.2f},{r['M4_hi']:5.2f}] D-M4 {r['D'] - r['M4']:+.2f} {'' if r['blind'] else '(E86 read)'}")


if __name__ == "__main__":
    main()
