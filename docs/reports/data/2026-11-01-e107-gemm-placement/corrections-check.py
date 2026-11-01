#!/usr/bin/env python3
"""E107, POST HOC (written Sun 1 Nov 2026 ~12:50 PST, after the verifier's review of the data commit 320dbd37; labelled, never a verdict): the numbers
the README's "Corrections after verification" cite. It reads committed files only and changes no registered number. Standard library.

    python3 docs/reports/data/2026-11-01-e107-gemm-placement/corrections-check.py      (writes corrections-check.json and .txt beside itself)

1. The minions: per arm and format, the mean minion's and the slowest minion's cycles per op (`cycles_mean` / `iters` and `cycles_max` / `iters` over
   every measurement launch, launch >= 0, of every kind and pass in aifoundry3/e107/p1071*/runs.jsonl).
2. The price of a missing L2 line three ways: from the launch's pace T (what posthoc.txt section 1 prints: it waits for the slowest minion), from the
   mean minion and from the slowest minion. Every one rests on the desk L2 model's 128 missing lines per shire-op of a cold pass by column
   (E105's desk/l2sim.txt), not on a count of misses. Cycles are priced at the pinned 600 MHz. Beside it, posthoc.txt section 4's vendor launch
   (64 x (T(c1) + 154 x price)) at the mean minion's price, as if the vendor's minions finished together.
3. DRAM's share: of the cold walk's extra time over a warm block (1 - f8) and of the cold walk's whole time per op ((T(c16) - T(c8s)) / T(c16)).
4. The two held board readings in c1's random cells (glitches.txt): fp32 in pass 10712, int8 in pass 10711. The run's window mean without the low
   samples is added to that pass's S one for one, an approximation (the reducer's S is the window's power at 80 C over idle).
5. R8 paired by pass: the ladder's random fp32 energy per op in each pass (e107.json per_pass, S / rate) and each step's mean and 95% interval over the
   three passes (t, 2 degrees of freedom). R8 was registered on means; this does not change its verdict.
6. The largest 95% interval of T over the 75 items (scored.json cells.*.T_ci95), and per arm and format.
7. Zeros' energy per op against the time per op: S, pJ per multiply-add and T from c1 to c16, per format.
8. E105's by-column cells on aifoundry3 (e105c.json gemm1.*, gemm16.*: two passes, 10520 and 10522), beside E107's c1.* and c16.* (three passes):
   the same designs, rgm105 against rgm107, the same card at the same clock.
"""
import argparse
import glob
import json
import math
import os
import statistics as st

TYPES = ("fp32", "fp16", "int8")
RK = {"fp32": "randn", "fp16": "randn", "int8": "full"}
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}
ARMS = ("c1", "c16r32", "c16r8", "c16r4", "c16r2", "c16", "c4s", "c8s", "c8", "c16s")
LADDER = ("c1", "c16r32", "c16r8", "c16r4", "c16r2", "c16")
MISS_COLD, F_HZ = 128, 600e6
T_Q = {1: 12.706, 2: 4.303, 3: 3.182}
PASSES = ("10710", "10711", "10712")


def mci(v):
    """mean, 95% half-interval (t), n"""
    n = len(v)
    m = st.mean(v)
    return m, (T_Q[n - 1] * st.stdev(v) / math.sqrt(n)) if n > 1 else None, n


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=here)
    ap.add_argument("--e105c", default=os.path.join(here, "..", "2026-11-01-e105-gemm-layout", "e105c.json"))
    ap.add_argument("--out", default=os.path.join(here, "corrections-check.json"))
    ap.add_argument("--txt", default=os.path.join(here, "corrections-check.txt"))
    a = ap.parse_args()
    e7 = json.load(open(os.path.join(a.data, "e107.json")))
    sc = json.load(open(os.path.join(a.data, "scored.json")))
    e5 = json.load(open(a.e105c))
    items, pp = e7["items"], e7["per_pass"]
    out = {"label": "POST HOC, written after the verifier's review, labelled, never a verdict"}
    L = ["E107 POST HOC (corrections-check.py), written after the verifier's review of 320dbd37; labelled, never a verdict. aifoundry3 card 0, 600 MHz pinned.", ""]

    # 1. minions
    cyc = {}
    for d in sorted(glob.glob(os.path.join(a.data, "aifoundry3", "e107", "p1071*"))):
        for ln in open(os.path.join(d, "runs.jsonl")):
            r = json.loads(ln)
            if r.get("test") != "fma" or r.get("launch", -1) < 0 or not r.get("ok") or "." not in r.get("item", ""):
                continue
            arm, ty = r["item"].split(".")[:2]
            if arm not in ARMS:
                continue
            c = cyc.setdefault(f"{arm}.{ty}", {"mean": [], "max": []})
            c["mean"].append(r["cycles_mean"] / r["iters"])
            c["max"].append(r["cycles_max"] / r["iters"])
    out["minions"] = {}
    L.append("1. The minions: cycles per op over every measurement launch (launch >= 0), all kinds and passes; T x 600 MHz is the launch's pace in cycles")
    L.append("   arm.format      launches  mean minion  slowest minion  slowest / mean  T x 600 MHz")
    for arm in ARMS:
        for ty in TYPES:
            k = f"{arm}.{ty}"
            if k not in cyc:
                continue
            mm, mx = st.mean(cyc[k]["mean"]), st.mean(cyc[k]["max"])
            tp = sc["T"][k] * 1e-6 * F_HZ
            out["minions"][k] = {"launches": len(cyc[k]["mean"]), "mean_cycles_per_op": mm, "slowest_cycles_per_op": mx, "slowest_over_mean": mx / mm,
                                 "T_cycles_at_600": tp}
            L.append(f"   {k:14s} {len(cyc[k]['mean']):8d}  {mm:11.1f}  {mx:14.1f}  {mx / mm:14.3f}  {tp:11.1f}")

    # 2. prices
    L.append("")
    L.append("2. The price of a missing L2 line, ns: (arm - c1) / 128 desk-model lines per shire-op, from the launch's pace T, the mean minion, the slowest minion")
    out["price_per_missing_line_ns"] = {}
    for ty in TYPES:
        row = {}
        for src in ("pace", "mean", "slowest"):
            if src == "pace":
                g = lambda arm: sc["T"][f"{arm}.{ty}"] * 1e-6 * F_HZ
            else:
                key = "mean_cycles_per_op" if src == "mean" else "slowest_cycles_per_op"
                g = lambda arm, key=key: out["minions"][f"{arm}.{ty}"][key]
            l3, l3_4, dr = ((g(x) - g("c1")) / MISS_COLD / F_HZ * 1e9 for x in ("c8s", "c4s", "c16"))
            f8 = (g("c8s") - g("c1")) / (g("c16") - g("c1"))
            row[src] = {"l3_ns": l3, "l3_ns_c4s": l3_4, "dram_walk_ns": dr, "dram_over_l3": dr / l3, "f8": f8}
        out["price_per_missing_line_ns"][ty] = row
        L.append(f"   {ty}: L3-served (c8s) pace {row['pace']['l3_ns']:.2f}, mean minion {row['mean']['l3_ns']:.2f}, slowest {row['slowest']['l3_ns']:.2f}; "
                 f"the DRAM walk (c16) pace {row['pace']['dram_walk_ns']:.2f}, mean {row['mean']['dram_walk_ns']:.2f}, slowest {row['slowest']['dram_walk_ns']:.2f}; "
                 f"DRAM / L3 x{row['pace']['dram_over_l3']:.2f} (pace), x{row['mean']['dram_over_l3']:.2f} (mean minion); "
                 f"f8 {row['pace']['f8']:.3f} (pace), {row['mean']['f8']:.3f} (mean minion)")
    v1, vm = sc["T"]["c1.fp32"], out["price_per_missing_line_ns"]["fp32"]["mean"]["l3_ns"] * 1e-3
    vm1 = out["minions"]["c1.fp32"]["mean_cycles_per_op"] / F_HZ * 1e6
    out["vendor_launch_us_mean_minion"] = {"T_c1_pace": 64 * (v1 + 154 * vm), "c1_mean_minion": 64 * (vm1 + 154 * vm)}
    L.append(f"   the vendor's launch, posthoc.txt section 4's form at the mean minion's L3 price ({vm * 1e3:.2f} ns): {64 * (v1 + 154 * vm):.1f} us with T(c1), "
             f"{64 * (vm1 + 154 * vm):.1f} us with c1's mean minion; posthoc.txt gives 93-98 us at the launch's pace")

    # 3. DRAM's share
    L.append("")
    L.append("3. DRAM's share of the cold walk, from T: of its extra time over a warm block, 1 - f8; of its whole time per op, (T(c16) - T(c8s)) / T(c16)")
    out["dram_share"] = {}
    for ty in TYPES:
        t1, t8, t16 = (sc["T"][f"{x}.{ty}"] for x in ("c1", "c8s", "c16"))
        ex = 1 - sc["f"][f"c8s.{ty}"]
        wh = (t16 - t8) / t16
        out["dram_share"][ty] = {"of_extra_time": ex, "of_whole_time": wh, "of_extra_time_mean_minion": 1 - out["price_per_missing_line_ns"][ty]["mean"]["f8"]}
        L.append(f"   {ty}: of the extra time {ex:.3f} (mean minion {1 - out['price_per_missing_line_ns'][ty]['mean']['f8']:.3f}); of the whole time {wh:.3f}")

    # 4. held readings
    L.append("")
    L.append("4. The two held board readings in c1's random cells (glitches.txt), S W and pJ per multiply-add, three passes, 95%")
    shifts = {}
    for ln in open(os.path.join(a.data, "glitches.txt")):
        f = ln.split()
        if len(f) > 3 and f[0].isdigit() and f[2] in ("c1.fp32.randn", "c1.int8.full"):
            shifts[f[2]] = (f[0], float(f[-1]))
    out["held_readings"] = {}
    for k, (ps, dw) in sorted(shifts.items()):
        ty = k.split(".")[1]
        s = [pp[p][k]["S"] for p in PASSES]
        s2 = [pp[p][k]["S"] + (dw if p == ps else 0.0) for p in PASSES]
        e = [pp[p][k]["S"] / pp[p][k]["rate"] / MACS[ty] * 1e12 for p in PASSES]
        e2 = [x / pp[p][k]["rate"] / MACS[ty] * 1e12 for x, p in zip(s2, PASSES)]
        (m, c, _), (m2, c2, _), (me, ce, _), (me2, ce2, _) = mci(s), mci(s2), mci(e), mci(e2)
        out["held_readings"][k] = {"pass": ps, "shift_w": dw, "S_per_pass": dict(zip(PASSES, s)), "S": [m, c], "S_without": [m2, c2],
                                   "pass_S_without": s2[PASSES.index(ps)], "pj_mac": [me, ce], "pj_mac_without": [me2, ce2]}
        L.append(f"   {k}: passes {', '.join(f'{x:.2f}' for x in s)} W; pass {ps}'s run reads {dw:+.2f} W without its low samples, so {s2[PASSES.index(ps)]:.2f} W; "
                 f"the cell {m:.2f} +- {c:.2f} W, without them {m2:.2f} +- {c2:.2f} W; pJ/MAC {me:.3f} +- {ce:.3f}, without them {me2:.3f} +- {ce2:.3f}")

    # 5. R8 paired
    L.append("")
    L.append("5. R8 paired by pass: random fp32 energy per op, nJ (S / rate), and each step's mean +- 95% over the three passes")
    epp = {arm: [pp[p][f"{arm}.fp32.randn"]["S"] / pp[p][f"{arm}.fp32.randn"]["rate"] * 1e9 for p in PASSES] for arm in LADDER}
    out["r8_paired"] = {"per_pass_nj": epp, "steps": []}
    for arm in LADDER:
        L.append(f"   {arm:7s} " + "  ".join(f"{p} {v:.3f}" for p, v in zip(PASSES, epp[arm])) + f"   mean {st.mean(epp[arm]):.3f}")
    for lo, hi in zip(LADDER, LADDER[1:]):
        dif = [b - x for x, b in zip(epp[lo], epp[hi])]
        m, c, _ = mci(dif)
        res = abs(m) > c
        out["r8_paired"]["steps"].append({"step": f"{lo} -> {hi}", "diff_nj": dif, "mean": m, "ci95": c, "resolved": res,
                                          "rises_in_every_pass": all(x > 0 for x in dif)})
        L.append(f"   {lo:7s} -> {hi:7s} {m:+.3f} +- {c:.3f} nJ  {'resolved' if res else 'NOT resolved'} at 95%; "
                 f"{'rises in every pass' if all(x > 0 for x in dif) else 'falls in pass ' + ', '.join(p for p, x in zip(PASSES, dif) if x <= 0)}")

    # 6. T intervals
    L.append("")
    L.append("6. T's 95% interval over the passes, us (scored.json cells.*.T_ci95)")
    ci = {k: v["T_ci95"] for k, v in sc["cells"].items() if v.get("T_ci95") is not None}
    kmax = max(ci, key=ci.get)
    per = {}
    for k, v in ci.items():
        arm, ty = k.split(".")[:2]
        per[f"{arm}.{ty}"] = max(per.get(f"{arm}.{ty}", 0.0), v)
    out["T_ci95"] = {"largest": [kmax, ci[kmax]], "items": len(ci), "per_arm_format_max": per}
    L.append(f"   largest {ci[kmax]:.5f} us ({kmax}) over {len(ci)} items; per arm and format, the largest of its kinds:")
    L.append("   " + ", ".join(f"{k} {v:.4f}" for k, v in per.items()))

    # 7. zeros against time
    L.append("")
    L.append("7. Zeros' energy per op against the time per op, c1 -> c16")
    out["zeros_vs_time"] = {}
    for ty in TYPES:
        z1, z16 = items[f"c1.{ty}.zeros"], items[f"c16.{ty}.zeros"]
        r1, r16 = items[f"c1.{ty}.{RK[ty]}"], items[f"c16.{ty}.{RK[ty]}"]
        t1, t16 = sc["T"][f"c1.{ty}"], sc["T"][f"c16.{ty}"]
        sz = {arm: items[f"{arm}.{ty}.zeros"]["S"]["mean"] for arm in ("c1", "c16r4", "c8s", "c16")}
        row = {"S_zeros": sz, "S_zeros_ratio": z16["S"]["mean"] / z1["S"]["mean"], "pj_mac_zeros": [z1["pj_mac_S"]["mean"], z16["pj_mac_S"]["mean"]],
               "pj_mac_zeros_ratio": z16["pj_mac_S"]["mean"] / z1["pj_mac_S"]["mean"], "T_ratio": t16 / t1,
               "S_random": [r1["S"]["mean"], r16["S"]["mean"]], "S_random_ratio": r16["S"]["mean"] / r1["S"]["mean"],
               "zeros_over_random_S": [z1["S"]["mean"] / r1["S"]["mean"], z16["S"]["mean"] / r16["S"]["mean"]]}
        out["zeros_vs_time"][ty] = row
        L.append(f"   {ty}: zeros S " + ", ".join(f"{a} {v:.2f}" for a, v in sz.items()) + f" W (c16 / c1 x{row['S_zeros_ratio']:.3f}); zeros pJ/MAC "
                 f"{row['pj_mac_zeros'][0]:.3f} -> {row['pj_mac_zeros'][1]:.3f} (x{row['pj_mac_zeros_ratio']:.3f}) while T x{row['T_ratio']:.3f}; random S "
                 f"{row['S_random'][0]:.2f} -> {row['S_random'][1]:.2f} W (x{row['S_random_ratio']:.3f}); zeros / random S {row['zeros_over_random_S'][0]:.3f} -> "
                 f"{row['zeros_over_random_S'][1]:.3f}")

    # 8. E105 replicate
    L.append("")
    L.append("8. E105's by-column cells on aifoundry3 (e105c.json, passes 10520 and 10522) beside E107's (three passes): S W, pJ per multiply-add, T us; 95%")
    out["e105_replicate"] = {}
    i5 = e5["items"]
    for e5arm, e7arm in (("gemm1", "c1"), ("gemm16", "c16")):
        for ty in TYPES:
            for kind in ("zeros", "sparse50", RK[ty]):
                k5, k7 = f"{e5arm}.{ty}.{kind}", f"{e7arm}.{ty}.{kind}"
                if k5 not in i5 or k7 not in items:
                    continue
                x5, x7 = i5[k5], items[k7]
                g = lambda x, q: (x[q]["mean"], x[q].get("ci95"), x[q].get("n"))
                t5, t7 = 1024 / x5["rate"]["mean"] * 1e6, 1024 / x7["rate"]["mean"] * 1e6
                row = {"e105": {"S": g(x5, "S"), "pj_mac": g(x5, "pj_mac_S"), "T_us": t5}, "e107": {"S": g(x7, "S"), "pj_mac": g(x7, "pj_mac_S"), "T_us": t7},
                       "S_diff_w": x7["S"]["mean"] - x5["S"]["mean"]}
                out["e105_replicate"][k7] = row
                L.append(f"   {k7:18s} E105 {x5['S']['mean']:6.2f} +- {x5['S']['ci95']:5.2f} W  {x5['pj_mac_S']['mean']:6.3f} pJ  T {t5:.4f}   |   "
                         f"E107 {x7['S']['mean']:6.2f} +- {x7['S']['ci95']:5.2f} W  {x7['pj_mac_S']['mean']:6.3f} pJ  T {t7:.4f}   |   S {row['S_diff_w']:+.2f} W")

    json.dump(out, open(a.out, "w"), indent=1)
    open(a.txt, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
