#!/usr/bin/env python3
"""E104: what the README quotes beyond scored.json. Standard library only; run it in this directory after collection. POST HOC where labelled: no rule of E104's depends on it.

    python3 posthoc-check.py > posthoc-check.txt

A: the runs a pass skipped. B: every contrast in the primary (two kept passes) and in the arm that keeps all three (E78's pass gates opened), per pass. C: the ratios fp16 over fp32 in three regimes, in the same two reductions.
D: per lane alternation, in fJ. E: how much of ±1 − +1 remains in a sum that truly holds, in both formats, against E92's values carried by the card scale. F: the read-back per tile. G: h_sub's walk in ulps per op against the RTL's −15. H: the same contrasts on the minion rail, which the board meter's dips do not touch. I: M4's misses, contrast by contrast. J: E88's fp16 r_abs: the store bits it writes against r_cancel's, priced. K: that lump per result bit in both formats, on the sums the card holds.
"""
import json
import math
import os
import statistics
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776}
P = json.load(open(os.path.join(HERE, "e104.json")))
G = json.load(open(os.path.join(HERE, "e104-gatesoff.json")))
K = json.load(open(os.path.join(HERE, "e104-dipskept.json")))
SC = json.load(open(os.path.join(HERE, "scored.json")))
SCALE = 0.9722


def pp(res, plus, minus):
    out = {}
    for p, it in sorted(res["per_pass"].items()):
        if all(n in it and it[n].get("D") is not None for n in list(plus) + list(minus)):
            out[p] = sum(it[n]["D"] for n in plus) - sum(it[n]["D"] for n in minus)
    return out


def mci(v):
    v = list(v)
    if len(v) < 2:
        return (v[0] if v else float("nan")), float("nan"), len(v)
    return sum(v) / len(v), T975[len(v) - 1] * statistics.stdev(v) / math.sqrt(len(v)), len(v)


def line(name, plus, minus):
    a, g = pp(P, plus, minus), pp(G, plus, minus)
    ma, ca, na = mci(a.values())
    mg, cg, ng = mci(g.values())
    print(f"  {name:36s} primary {ma:7.3f} ± {ca:6.3f} (n={na}) | all three {mg:7.3f} ± {cg:6.3f} (n={ng}) | per pass {' '.join(f'{p[-2:]}:{x:.3f}' for p, x in g.items())}")
    return a, g


print("A. Runs that did not run, from each pass's marks.jsonl (E78's runner: the launch reading not reached)")
for p in ("p10410", "p10411", "p10412"):
    for l in open(os.path.join(HERE, "aifoundry1-c1", "kinds", p, "marks.jsonl")):
        m = json.loads(l)
        if m.get("kind") == "skipped":
            print(f"  {p} {m['item']} pos {m['pos']}: start {m['start_c']} C, hot {m['start_hot_c']} C, heats {m['heats']}, wait {m['wait_s']} s")
print("  pass gates: set aside", P["passes_set_aside"], "kept", P["passes"], "dip samples removed", {k: v["samples_removed"] for k, v in P["reducer"]["dip_samples_removed"].items()})

print("B. The contrasts, paired within a pass, t(0.975, n-1)")
c = {}
for name, plus, minus in (("fp16 h_sub - h_add", ["fp16.h_sub"], ["fp16.h_add"]), ("fp16 u_sub - h_add", ["fp16.u_sub"], ["fp16.h_add"]), ("fp16 z_sub - z_add", ["fp16.z_sub"], ["fp16.z_add"]), ("fp16 h_sub - u_sub", ["fp16.h_sub"], ["fp16.u_sub"]),
                          ("fp16 m_h_sub - w_h_add", ["fp16.m_h_sub"], ["fp16.w_h_add"]), ("fp16 c_alt - c_abs", ["fp16.c_alt"], ["fp16.c_abs"]), ("fp16 s_abs - c_abs", ["fp16.s_abs"], ["fp16.c_abs"]), ("fp16 z_s - c_abs", ["fp16.z_s"], ["fp16.c_abs"]),
                          ("fp16 s_abs - z_s", ["fp16.s_abs"], ["fp16.z_s"]), ("fp16 h_add - c_abs", ["fp16.h_add"], ["fp16.c_abs"]), ("fp16 z_add - c_abs", ["fp16.z_add"], ["fp16.c_abs"]),
                          ("fp32 h_sub - h_add", ["fp32.h_sub"], ["fp32.h_add"]), ("fp32 u_sub - h_add", ["fp32.u_sub"], ["fp32.h_add"]), ("fp32 z_sub - z_add", ["fp32.z_sub"], ["fp32.z_add"]), ("fp32 h_sub - u_sub", ["fp32.h_sub"], ["fp32.u_sub"]),
                          ("fp32 u_sub - z_sub + z_add - h_add", ["fp32.u_sub", "fp32.z_add"], ["fp32.h_add", "fp32.z_sub"]), ("fp16 u_sub - z_sub + z_add - h_add", ["fp16.u_sub", "fp16.z_add"], ["fp16.h_add", "fp16.z_sub"]),
                          ("fp32 m_h_sub - w_h_add", ["fp32.m_h_sub"], ["fp32.w_h_add"]), ("fp32 z_s - c_abs", ["fp32.z_s"], ["fp32.c_abs"]), ("fp32 h_add - c_abs", ["fp32.h_add"], ["fp32.c_abs"]), ("fp32 z_add - c_abs", ["fp32.z_add"], ["fp32.c_abs"])):
    c[name] = line(name, plus, minus)

print("C. fp16 over fp32, the per-pass ratio, the ratio of the two contrasts' means beside it")
for name, a, b in (("halves together: u_sub - h_add (R5)", "fp16 u_sub - h_add", "fp32 u_sub - h_add"), ("moving, alike: m_h_sub - w_h_add (R6)", "fp16 m_h_sub - w_h_add", "fp32 m_h_sub - w_h_add"), ("zero products: z_sub - z_add", "fp16 z_sub - z_add", "fp32 z_sub - z_add"), ("E92's: h_sub - h_add", "fp16 h_sub - h_add", "fp32 h_sub - h_add"), ("random signs held: z_s - c_abs", "fp16 z_s - c_abs", "fp32 z_s - c_abs")):
    for lab, i in (("primary", 0), ("all three", 1)):
        x, y = c[a][i], c[b][i]
        v = [x[p] / y[p] for p in x if p in y]
        m, h, n = mci(v)
        print(f"  {name:40s} {lab:9s} {m:6.3f} ± {h:6.3f} (n={n}); of means {sum(x[p] for p in x if p in y) / sum(y[p] for p in x if p in y):.3f}")

print("D. Per lane alternation, the contrast over (alternations an op x ops a second), in fJ. Rate: each type's own rate in the reduction. An alternation here is a lane-micro-op whose eff_sub differs from the lane's last one (fp16: eff_sub1 and eff_sub2 move together on h_, u_, z_).")
rate = {t: P["items"][f"{t}.randn"]["rate"]["mean"] for t in ("fp32", "fp16")}
print("  ops a second (all minions):", {k: round(v / 1e9, 4) for k, v in rate.items()}, "x 1e9")
for name, t, alts in (("fp32 h_sub - h_add", "fp32", 3840), ("fp32 u_sub - h_add", "fp32", 3472), ("fp32 z_sub - z_add", "fp32", 3840), ("fp32 m_h_sub - w_h_add", "fp32", 3840), ("fp16 h_sub - h_add", "fp16", 3840), ("fp16 u_sub - h_add", "fp16", 3472), ("fp16 z_sub - z_add", "fp16", 3840), ("fp16 m_h_sub - w_h_add", "fp16", 3840)):
    ma, _, _ = mci(c[name][0].values())
    mg, _, _ = mci(c[name][1].values())
    print(f"  {name:28s} {alts} a op: primary {ma / (alts * rate[t]) * 1e15:6.0f} fJ, all three {mg / (alts * rate[t]) * 1e15:6.0f} fJ")

print(f"E. POST HOC. How much of ±1 - +1 remains in a sum that truly holds. ±1 - +1 is E92's dips-removed value on aifoundry3 x {SCALE} (no ±1 tile ran here): fp32 5.016, fp16 4.965 W.")
for t, sv in (("fp32", 5.016), ("fp16", 4.965)):
    for lab, i in (("primary", 0), ("all three", 1)):
        v = [x / (sv * SCALE) for x in c[f"{t} z_s - c_abs"][i].values()]
        m, h, n = mci(v)
        print(f"  {t} z_s - c_abs over ±1 - +1, {lab:9s}: {m:.3f} ± {h:.3f} (n={n}); the step {sv * SCALE:.3f} W")
print(f"  beside it, E92's s_abs - c_abs on aifoundry3, dips removed, x {SCALE}: fp32 {2.520 * SCALE:.3f} W, {2.520 / 5.016:.3f} of the step (fp32.s_abs reads back held); fp16 {4.587 * SCALE:.3f} W, {4.587 / 4.965:.3f} of the step (fp16.s_abs reads back as 9 words: not a held sum)")

print("F. The read-back, per tile: which readings every read equals")
rows = SC["readback"]["rows"]
by = {}
for r in rows:
    by.setdefault(r["tile"], []).append(r)
for t, rs in by.items():
    print(f"  {t:14s} n {','.join(str(r['n']) for r in rs):38s} minions {min(r['minions'] for r in rs):4d} equals {','.join(SC['readback']['tiles'][t])} | words on the card at the last n: {rs[-1]['card_distinct_words']} | C00 {rs[-1]['card_c00']} C08 {rs[-1]['card_c08']}")
print(f"  {len(rows)} reads; all 1,024 minions on one C in {sum(1 for r in rows if r.get('all_minions_agree'))}; equal rtl {sum('rtl' in r['matches'] for r in rows)}; equal manual {sum('manual' in r['matches'] for r in rows)}; equal frozen {sum('fl' in r['matches'] for r in rows)}")


def ulp(w):
    return 2.0 ** (((w >> 23) & 255) - 150)


def val(h):
    return struct.unpack(">f", bytes.fromhex(h))[0]


print("G. POST HOC. fp16.h_sub on the card: C[0][0] and C[0][8], and the deficit of C[0][8] in units of its own last place")
for r in by["fp16.h_sub"]:
    a, b = val(r["card_c00"]), val(r["card_c08"])
    w = int(r["card_c08"], 16)
    print(f"  n {r['n']:7d} C00 {a:.6e} C08 {b:.6e} C08/C00 {b / a:.5f} deficit {(a - b) / ulp(w):12.0f} ulps of C08's binade")


print("H. The same contrasts on the minion rail: Drail in each reduction, per pass (Drail carries E78's rail term, 0.81 k, so it moves with the leakage slope)")


def pr(res, plus, minus):
    out = {}
    for p, it in sorted(res["per_pass"].items()):
        if all(n in it and it[n].get("Drail") is not None for n in list(plus) + list(minus)):
            out[p] = sum(it[n]["Drail"] for n in plus) - sum(it[n]["Drail"] for n in minus)
    return out


rr = {}
for name, plus, minus in (("fp16 h_sub - h_add", ["fp16.h_sub"], ["fp16.h_add"]), ("fp16 u_sub - h_add", ["fp16.u_sub"], ["fp16.h_add"]), ("fp16 h_sub - u_sub", ["fp16.h_sub"], ["fp16.u_sub"]), ("fp16 z_sub - z_add", ["fp16.z_sub"], ["fp16.z_add"]), ("fp16 m_h_sub - w_h_add", ["fp16.m_h_sub"], ["fp16.w_h_add"]), ("fp16 z_s - c_abs", ["fp16.z_s"], ["fp16.c_abs"]), ("fp16 s_abs - c_abs", ["fp16.s_abs"], ["fp16.c_abs"]),
                          ("fp32 h_sub - h_add", ["fp32.h_sub"], ["fp32.h_add"]), ("fp32 u_sub - h_add", ["fp32.u_sub"], ["fp32.h_add"]), ("fp32 h_sub - u_sub", ["fp32.h_sub"], ["fp32.u_sub"]), ("fp32 z_sub - z_add", ["fp32.z_sub"], ["fp32.z_add"]), ("fp32 m_h_sub - w_h_add", ["fp32.m_h_sub"], ["fp32.w_h_add"]), ("fp32 z_s - c_abs", ["fp32.z_s"], ["fp32.c_abs"])):
    a, g = pr(P, plus, minus), pr(G, plus, minus)
    ma, ca, na = mci(a.values())
    mg, cg, ng = mci(g.values())
    rr[name] = (a, g)
    print(f"  {name:28s} primary {ma:7.3f} ± {ca:6.3f} (n={na}) | all three {mg:7.3f} ± {cg:6.3f} (n={ng})")
for name, a, b in (("u_sub - h_add", "fp16 u_sub - h_add", "fp32 u_sub - h_add"), ("m_h_sub - w_h_add", "fp16 m_h_sub - w_h_add", "fp32 m_h_sub - w_h_add"), ("h_sub - h_add", "fp16 h_sub - h_add", "fp32 h_sub - h_add"), ("z_s - c_abs", "fp16 z_s - c_abs", "fp32 z_s - c_abs")):
    for lab, i in (("primary", 0), ("all three", 1)):
        x, y = rr[a][i], rr[b][i]
        m, h, n = mci([x[p] / y[p] for p in x if p in y])
        print(f"  ratio fp16/fp32 {name:20s} {lab:9s} {m:6.3f} ± {h:6.3f} (n={n})")

print("I. M4's frozen contrasts against the primary and the all-three arm: the miss, measured - M4, and whether the measured mean lies inside M4's frozen interval")
reg = json.load(open(os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "kinds", "predictions-e104.json"))) if os.path.exists(os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "kinds", "predictions-e104.json")) else None
if reg is None:
    import glob
    reg = json.load(open(glob.glob(os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "kinds", "predictions-e104.json"))[0]))
for n, x in reg["contrasts"].items():
    a, g = pp(P, x["plus"], x["minus"]), pp(G, x["plus"], x["minus"])
    ma, ca, na = mci(a.values())
    mg, cg, ng = mci(g.values())
    f = x["frozen_reading_w"]
    print(f"  {n:34s} M4 {x['M']:6.2f} ± {x['half95']:4.2f} | primary {ma:6.3f} miss {ma - x['M']:+6.3f} | all three {mg:6.3f} miss {mg - x['M']:+6.3f} inside {abs(mg - x['M']) <= x['half95']}" + ("" if f is None else f" | frozen reading {f:5.2f}, the all-three mean off it by {mg - f:+6.3f}"))

print("J. E88's fp16.r_abs against r_cancel: result-path bits an op on the RTL's arithmetic (e104.json counts_real, at two op indices over a launch), priced at 30 fJ (E92's fp32 moving part) and 51.75 fJ (E88's fp16 price)")
spec = json.load(open(os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "kinds", "e104", "e104.json")))
for t in ("fp16.r_abs", "fp16.r_cancel"):
    k = spec["tiles"][t]["counts_real"]
    print(f"  {t}: cbus {k['cbus']:.0f} rbus {k['rbus']:.0f} store {k['store']:.0f} total {k['cbus'] + k['rbus'] + k['store']:.0f}")
k = spec["tiles"]["fp16.r_abs"]["counts_real"]
b = k["cbus"] + k["rbus"] + k["store"]
print(f"  at {rate['fp16'] / 1e9:.3f}e9 ops a second: {b * rate['fp16'] * 30e-15:.3f} W at 30 fJ, {b * rate['fp16'] * 51.75e-15:.3f} W at 51.75 fJ; E88's A16 is 0.388 ± 0.111 W")


print("K. POST HOC. A lump: everything that moves when the halves part, over the result bits, nothing taken off. Result bits are e104.json's counts_real (C read + result bus + store, RTL's arithmetic, two op indices over a launch; a count on a tile with two words moves with n, so these are rough)")


def bits(t):
    k = spec["tiles"][t]["counts_real"]
    return k["cbus"] + k["rbus"] + k["store"]


for name, plus, minus, ty in (("fp16 h_sub - u_sub", "fp16.h_sub", "fp16.u_sub", "fp16"), ("fp32 h_sub - u_sub", "fp32.h_sub", "fp32.u_sub", "fp32"), ("fp16 w_h_add - h_add", "fp16.w_h_add", "fp16.h_add", "fp16"), ("fp32 w_h_add - h_add", "fp32.w_h_add", "fp32.h_add", "fp32")):
    a, g = pp(P, [plus], [minus]), pp(G, [plus], [minus])
    ma, ca, na = mci(a.values())
    mg, cg, ng = mci(g.values())
    db = bits(plus) - bits(minus)
    print(f"  {name:24s} primary {ma:6.3f} ± {ca:5.3f} (n={na}) | all three {mg:6.3f} ± {cg:5.3f} (n={ng}) | result bits {bits(plus):8.0f} - {bits(minus):7.0f} = {db:8.0f} | {(ma / (db * rate[ty]) * 1e15) if db else float('nan'):6.1f} fJ a bit, all three {(mg / (db * rate[ty]) * 1e15) if db else float('nan'):6.1f}")
a = pp(P, ["fp16.h_sub", "fp32.u_sub"], ["fp16.u_sub", "fp32.h_sub"])
g = pp(G, ["fp16.h_sub", "fp32.u_sub"], ["fp16.u_sub", "fp32.h_sub"])
ma, ca, na = mci(a.values())
mg, cg, ng = mci(g.values())
db = bits("fp16.h_sub") - bits("fp16.u_sub")
print(f"  fp16's h_sub - u_sub less fp32's, the 1/15 of the alternations taken out: primary {ma:.3f} ± {ca:.3f} (n={na}) | all three {mg:.3f} ± {cg:.3f} (n={ng}) | over {db:.0f} bits: {ma / (db * rate['fp16']) * 1e15:.1f} fJ a bit, all three {mg / (db * rate['fp16']) * 1e15:.1f}; E92's fp32 moving part read 29.7-30.0 fJ")
