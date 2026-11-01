#!/usr/bin/env python3
"""E107's scorer (registered with E107.md before the claim): the rules of predictions-e107.json on reduce_e107.py's e107.json and rails_e107.py's
rails-e107.json. Standard library only.

    python3 tools/claims-v3/e107/score_e107.py --e107 e107.json --rails rails-e107.json --out scored.json --md results.md

T, us per op of one minion, is the chip's 1,024 minions over the reducer's rate (the launch records inside its power window, [t0+1 s, t0+3 s)); an arm's T in a
format is the mean of its kinds' T. Its 95% interval comes from the rate's, over passes.
"""
import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TYPES = ("fp32", "fp16", "int8")
RK = {"fp32": "randn", "fp16": "randn", "int8": "full"}
FLOP_PER_OP = {"fp32": 8192, "fp16": 16384, "int8": 32768}   # 2 x 16 x 16 x K
NEW = ("c16r2", "c16r4", "c16r8", "c16r32", "c4s", "c8s", "c8", "c16s")
LADDER = (("c16", 1), ("c16r2", 2), ("c16r4", 4), ("c16r8", 8), ("c16r32", 32))
CLOCK_FOLLOW_BOUND_US = 529 * (1 / 600 - 1 / 800)            # 0.2204 us: the most an fp32 op's 529 FMA cycles can shed at x1.333 of clock


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def t_of(items, name):
    it = items.get(name)
    if not it or not it.get("rate") or it["rate"].get("mean") in (None, 0):
        return None, None
    r = it["rate"]
    T = 1024.0 / r["mean"] * 1e6
    ci = None if r.get("ci95") is None else T * r["ci95"] / r["mean"]
    return T, ci


def arm_T(items, arm, ty):
    ts = [t_of(items, n)[0] for n in items if n.startswith(f"{arm}.{ty}.")]
    return mean(ts)


def fit_inv(points):
    """Least squares T = a + b / R."""
    xs = [1.0 / R for R, _ in points]
    ys = [T for _, T in points]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    return a, b


def score(items, rails, pred):
    R = pred["rules"]
    P = pred["predictions"]
    ends = pred["ends"]
    out = {"rules": {}, "T": {}, "cells": {}}
    T = {(a, ty): arm_T(items, a, ty) for a in pred["arms"] for ty in TYPES}
    out["T"] = {f"{a}.{ty}": v for (a, ty), v in T.items()}
    # R1
    chk = {}
    for ty in TYPES:
        c1, c16 = T[("c1", ty)], T[("c16", ty)]
        chk[ty] = {"c1": c1, "c1_e105": ends[ty]["T_c1"], "c16": c16, "c16_e105": ends[ty]["T_c16"],
                   "ok": c1 is not None and c16 is not None and abs(c1 / ends[ty]["T_c1"] - 1) <= R["R1_tie"]["c1_rel"]
                   and abs(c16 / ends[ty]["T_c16"] - 1) <= R["R1_tie"]["c16_rel"]}
    out["rules"]["R1_tie"] = {"per_format": chk, "verdict": "PASS" if all(v["ok"] for v in chk.values()) else "FAIL"}
    # R2
    bad, n = [], 0
    for name in items:
        a = name.split(".", 1)[0]
        if a not in pred["arms"]:
            continue
        _, ty, kind = name.split(".")
        if kind == "zeros":
            continue
        tz, tk = t_of(items, f"{a}.{ty}.zeros")[0], t_of(items, name)[0]
        if tz is None or tk is None:
            continue
        n += 1
        if abs(tk / tz - 1) > R["R2_kind"]["rel"]:
            bad.append({"item": name, "ratio": tk / tz})
    worst = max((abs(t_of(items, nm)[0] / t_of(items, f"{nm.split('.')[0]}.{nm.split('.')[1]}.zeros")[0] - 1)
                 for nm in items if nm.split(".", 1)[0] in pred["arms"] and not nm.endswith(".zeros")
                 and t_of(items, nm)[0] and t_of(items, f"{nm.split('.')[0]}.{nm.split('.')[1]}.zeros")[0]), default=None)
    out["rules"]["R2_kind"] = {"compared": n, "outside": bad, "worst_rel": worst, "verdict": "PASS" if n and not bad else ("FAIL" if bad else "NO DATA")}
    # R3
    r3 = {}
    for ty in TYPES:
        pts = [(Rr, T[(a, ty)]) for a, Rr in LADDER if T[(a, ty)] is not None]
        c1, c16 = T[("c1", ty)], T[("c16", ty)]
        if len(pts) < 4 or c1 is None or c16 is None:
            r3[ty] = {"verdict": "NO DATA", "points": pts}
            continue
        a_, b_ = fit_inv(pts)
        res = [abs(Tv - (a_ + b_ / Rr)) / Tv for Rr, Tv in pts]
        t32 = T[("c16r32", ty)]
        first = {str(Rr): Rr * Tv - (Rr - 1) * c1 for Rr, Tv in pts}
        if t32 is not None and t32 - c1 >= R["R3_reuse"]["not_frac"] * (c16 - c1):
            v = "NOT THE VARIABLE"
        elif abs(a_ - c1) <= R["R3_reuse"]["tinf_rel"] * c1 and max(res) <= R["R3_reuse"]["point_rel"]:
            v = "REUSE IS THE VARIABLE"
        else:
            v = "PARTIAL"
        r3[ty] = {"Tinf": a_, "D": b_, "T_c1": c1, "Tinf_over_c1": a_ / c1, "max_rel_resid": max(res), "points": pts,
                  "first_pass_us": first, "verdict": v}
    out["rules"]["R3_reuse"] = {"per_format": r3, "verdict": r3["fp32"]["verdict"]}
    # R4, R4b, R5, R6
    f = {}
    for a in ("c8s", "c4s", "c8", "c16s") + tuple(x for x, _ in LADDER):
        for ty in TYPES:
            c1, c16, ta = T[("c1", ty)], T[("c16", ty)], T[(a, ty)]
            f[f"{a}.{ty}"] = None if None in (c1, c16, ta) or c16 == c1 else (ta - c1) / (c16 - c1)
    out["f"] = f
    res4b = {ty: (None if None in (T[("c4s", ty)], T[("c8s", ty)]) else abs(T[("c4s", ty)] - T[("c8s", ty)]) / T[("c8s", ty)]) for ty in TYPES}
    resident = res4b["fp32"] is not None and res4b["fp32"] <= R["R4b_resident"]["rel"]
    out["rules"]["R4b_resident"] = {"rel_diff": res4b, "verdict": "PASS" if resident else ("NO DATA" if res4b["fp32"] is None else "FAIL")}

    def walk_verdict(x):
        if x is None:
            return "NO DATA"
        return "DRAM SETS MOST OF IT" if x <= R["R4_walk"]["dram_max"] else ("NOT DRAM" if x >= R["R4_walk"]["notdram_min"] else "SHARED")
    arm4 = "c8s" if resident or res4b["fp32"] is None else "c4s"
    out["rules"]["R4_walk"] = {"read_on": arm4, "f8": {ty: f[f"{arm4}.{ty}"] for ty in TYPES},
                               "frozen": R["R4_walk"]["frozen"], "per_format": {ty: walk_verdict(f[f"{arm4}.{ty}"]) for ty in TYPES},
                               "verdict": walk_verdict(f[f"{arm4}.fp32"]) + ("" if arm4 == "c8s" else " (read on c4s: the 26 MB walk did not behave as resident)")}
    # R4c
    def droop(name):
        r = rails.get(name, {}).get("ddr_droop_mv", {})
        return r.get("mean")
    r4c = {}
    for kind in ("zeros", "randn"):
        d1, d8, d16 = droop(f"c1.fp32.{kind}"), droop(f"c8s.fp32.{kind}"), droop(f"c16.fp32.{kind}")
        ok = None if None in (d1, d8, d16) else (d8 - d1) <= R["R4c_dram_check"]["frac"] * (d16 - d1)
        r4c[kind] = {"c1": d1, "c8s": d8, "c16": d16, "ok": ok}
    out["rules"]["R4c_dram_check"] = {"per_kind": r4c, "verdict": "NO DATA" if any(v["ok"] is None for v in r4c.values())
                                      else ("PASS" if all(v["ok"] for v in r4c.values()) else "FAIL")}
    f8, f8c, f16s = f[f"{arm4}.fp32"], f["c8.fp32"], f["c16s.fp32"]
    if None in (f8, f8c):
        v5 = "NO DATA"
    elif f8c >= f8 + 0.30:
        v5 = "C ALLOCATES"
    elif abs(f8c - f8) <= 0.10:
        v5 = "C DOES NOT DISPLACE"
    else:
        v5 = "PARTIAL"
    out["rules"]["R5_c_in_l3"] = {"f8c": f8c, "f8": f8, "frozen": R["R5_c_in_l3"]["frozen"], "verdict": v5}
    v6 = "NO DATA" if f16s is None else ("PART OF THE LIMIT" if f16s <= 0.85 else ("NOT THE LIMIT" if f16s >= 0.95 else "PARTIAL"))
    out["rules"]["R6_c_traffic"] = {"f16s": f16s, "frozen": R["R6_c_traffic"]["frozen"], "verdict": v6}
    # R7
    diffs = []
    for a in NEW:
        for ty in TYPES:
            for kind in ("zeros", RK[ty]):
                k = f"{a}.{ty}.{kind}"
                s = (items.get(k) or {}).get("S", {}).get("mean")
                if s is not None:
                    diffs.append({"cell": k, "S": s, "pred": P["S_w"][k], "diff": s - P["S_w"][k]})
    rms = math.sqrt(sum(d["diff"] ** 2 for d in diffs) / len(diffs)) if diffs else None
    out["rules"]["R7_power"] = {"cells": len(diffs), "rms_w": rms, "worst": max(diffs, key=lambda d: abs(d["diff"])) if diffs else None,
                                "verdict": "NO DATA" if rms is None else ("PASS" if rms <= R["R7_power"]["rms_w"] else "FAIL"), "diffs": diffs}
    # R8
    seq = ["c1", "c16r32", "c16r8", "c16r4", "c16r2", "c16"]
    e = [((items.get(f"{a}.fp32.randn") or {}).get("pj_op_S") or {}).get("mean") for a in seq]
    v8 = "NO DATA" if None in e else ("PASS" if all(x < y for x, y in zip(e, e[1:])) else "FAIL")
    out["rules"]["R8_energy_order"] = {"arms": seq, "pj_op": e, "verdict": v8}
    # cells and the speed-half bound
    for name, it in items.items():
        a = name.split(".", 1)[0]
        if a not in pred["arms"]:
            continue
        ty = name.split(".")[1]
        Tv, Tci = t_of(items, name)
        rl = rails.get(name, {})
        out["cells"][name] = {"T_us": Tv, "T_ci95": Tci, "rate_T": None if Tv is None else 1024 * FLOP_PER_OP[ty] / (Tv * 1e-6) / 1e12,
                              "S": it.get("S"), "pj_op_S": it.get("pj_op_S"), "pj_mac_S": it.get("pj_mac_S"), "cycles_per_op": it.get("cycles_per_op"),
                              "sram_nj_op": rl.get("sram_nj_op"), "noc_nj_op": rl.get("noc_nj_op"), "ddr_droop_mv": rl.get("ddr_droop_mv")}
    out["speed_half_bound_fp32"] = {a: (None if T[(a, "fp32")] is None else T[(a, "fp32")] / (T[(a, "fp32")] - CLOCK_FOLLOW_BOUND_US)) for a in pred["arms"]}
    return out


def md(sc, pred):
    L = ["# E107 scored (score_e107.py)", "", "| rule | measured | verdict |", "|---|---|---|"]
    r = sc["rules"]
    L.append(f"| R1 tie | " + "; ".join(f"{ty} c1 {v['c1']:.4f} (E105 {v['c1_e105']:.4f}), c16 {v['c16']:.4f} (E105 {v['c16_e105']:.4f})"
                                         for ty, v in r["R1_tie"]["per_format"].items() if v["c1"] and v["c16"]) + f" | {r['R1_tie']['verdict']} |")
    L.append(f"| R2 kind | {r['R2_kind']['compared']} compared, worst {100 * (r['R2_kind']['worst_rel'] or 0):.2f}% | {r['R2_kind']['verdict']} |")
    for ty, v in r["R3_reuse"]["per_format"].items():
        if "Tinf" in v:
            L.append(f"| R3 reuse {ty} | Tinf {v['Tinf']:.4f} against c1 {v['T_c1']:.4f} (x{v['Tinf_over_c1']:.3f}), worst point {100 * v['max_rel_resid']:.2f}% | {v['verdict']} |")
    L.append(f"| R4 walk ({r['R4_walk']['read_on']}) | f8 " + ", ".join(f"{ty} {x:.3f}" for ty, x in r["R4_walk"]["f8"].items() if x is not None)
             + f" (frozen fp32 {r['R4_walk']['frozen']['fp32']:.3f}) | {r['R4_walk']['verdict']} |")
    L.append(f"| R4b resident | |c4s - c8s| / c8s " + ", ".join(f"{ty} {100 * x:.2f}%" for ty, x in r["R4b_resident"]["rel_diff"].items() if x is not None)
             + f" | {r['R4b_resident']['verdict']} |")
    L.append(f"| R4c DRAM check | droop mV " + "; ".join(f"{k}: c1 {v['c1']:.2f}, c8s {v['c8s']:.2f}, c16 {v['c16']:.2f}" for k, v in r["R4c_dram_check"]["per_kind"].items()
                                                   if None not in (v["c1"], v["c8s"], v["c16"])) + f" | {r['R4c_dram_check']['verdict']} |")
    for k, lab, key in (("R5_c_in_l3", "R5 C in the L3", "f8c"), ("R6_c_traffic", "R6 C's traffic", "f16s")):
        x = r[k][key]
        L.append(f"| {lab} | {key} {'-' if x is None else f'{x:.3f}'} (frozen {r[k]['frozen']:.3f}) | {r[k]['verdict']} |")
    x = r["R7_power"]["rms_w"]
    L.append(f"| R7 power | rms {'-' if x is None else f'{x:.2f}'} W over {r['R7_power']['cells']} cells | {r['R7_power']['verdict']} |")
    L.append(f"| R8 energy order | " + ", ".join("-" if e is None else f"{e / 1000:.2f}" for e in r["R8_energy_order"]["pj_op"]) + f" nJ | {r['R8_energy_order']['verdict']} |")
    L += ["", "| arm | format | T us | T(FL)OP/s | S zeros W | S random W | S sparse50 W | pJ/MAC random | zeros / random |", "|---|---|---|---|---|---|---|---|---|"]
    for a in pred["arms"]:
        for ty in TYPES:
            c = sc["cells"]
            z, rr, sp = c.get(f"{a}.{ty}.zeros"), c.get(f"{a}.{ty}.{RK[ty]}"), c.get(f"{a}.{ty}.sparse50")
            if not z and not rr:
                continue
            g = lambda cell, k: None if not cell or not cell.get(k) or cell[k].get("mean") is None else cell[k]["mean"]
            T = sc["T"][f"{a}.{ty}"]
            fl = None if T is None else 1024 * FLOP_PER_OP[ty] / (T * 1e-6) / 1e12
            sz, sr, ss, pm = g(z, "S"), g(rr, "S"), g(sp, "S"), g(rr, "pj_mac_S")
            fm = lambda x, p=2: "" if x is None else f"{x:.{p}f}"
            L.append(f"| {a} | {ty} | {fm(T, 4)} | {fm(fl)} | {fm(sz)} | {fm(sr)} | {fm(ss)} | {fm(pm, 3)} | {fm(None if not sz or not sr else sz / sr, 3)} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e107", required=True)
    ap.add_argument("--rails", required=True)
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e107.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", required=True)
    a = ap.parse_args()
    pred = json.load(open(a.pred))
    items = json.load(open(a.e107))["items"]
    rails = json.load(open(a.rails))["items"]
    sc = score(items, rails, pred)
    json.dump(sc, open(a.out, "w"), indent=1)
    open(a.md, "w").write(md(sc, pred))
    print(open(a.md).read())


if __name__ == "__main__":
    main()
