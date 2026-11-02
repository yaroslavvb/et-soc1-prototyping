#!/usr/bin/env python3
"""E121 (Q134): print every derived number the data README quotes beside scored.json and results.md, from this directory's
committed files (e121.json, the arms, scored.json) and E93's (docs/reports/data/2026-11-01-e93-zero-gate-silicon/). Post hoc
and labelled so in the README where it is not a registered quantity. Standard library only.
    python3 readme-numbers.py > readme-numbers.txt
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
E93D = os.path.join(HERE, "..", "2026-11-01-e93-zero-gate-silicon")
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}
e = json.load(open(os.path.join(HERE, "e121.json")))
s = json.load(open(os.path.join(HERE, "scored.json")))
e93 = json.load(open(os.path.join(E93D, "e93.json")))
s93 = json.load(open(os.path.join(E93D, "scored.json")))


def st(v):
    v = [x for x in v if x is not None]
    n = len(v)
    m = sum(v) / n
    if n < 2:
        return m, None, n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    return m, T95[n - 1] * sd / math.sqrt(n), n


def per(res, fn):
    out = []
    for p in res["passes"]:
        c = res["per_pass"][str(p)]
        try:
            out.append(fn(c))
        except (KeyError, TypeError):
            pass
    return st(out)


def f(x):
    m, h, n = x
    return f"{m:.3f} ± {h:.3f} (n {n})" if h is not None else f"{m:.3f} (n {n})"


print("== session: passes", e["passes"], "| leak", e["leak"], "| clock", e["clock_mhz"], "MHz | v_mean", round(e["v_mean"] * 1000, 1), "mV")
print("idle level (W, launch reading):", e["idle_level"])
print("runs", e["runs"], "kept", e["kept"], "failed", e["failed"])
print("dip samples removed per pass:", {k: v["samples_removed"] for k, v in e["reducer"]["dip_samples_removed"].items()})
print("cycles per op:", e["cycles_per_op"])
print("\n== the table: per tile, D over the type's zeros, S over idle, pJ/MAC from S, dT over the window, Drail (from e121.json > items)")
print("tile | gated | D | S | pJ/MAC (S) | dT | Drail | n")
for n, it in sorted(e["items"].items()):
    D, S = it["D"], it["S"]
    if D.get("n", 0) == 0:
        continue
    def g(x, k="mean"):
        return x.get(k) if isinstance(x, dict) else x
    pj = it.get("pj_mac_S")
    print(f"{n} | {it.get('gated_lane_frac')} | {D['mean']:.3f} ± {D['ci95'] or 0:.3f} | {S['mean']:.3f} ± {S['ci95'] or 0:.3f} | "
          f"{g(pj):.3f} ± {g(pj, 'ci95') or 0:.3f} | {g(it.get('dT_win')):.2f} | {g(it.get('Drail')):.2f} | {D['n']}")
print("\n== this session's card scale (D here over E93's D on card 1), post hoc")
for n in ("fp32.randn", "fp16.randn", "int8.full", "anchor_pi"):
    print(n, round(e["items"][n]["D"]["mean"] / e93["items"][n]["D"]["mean"], 4))
print("\n== reported (score_e93.reported's block on this session)")
rep = s["reported"]["e93_reported_block"]
def fs(x):
    return "—" if not x or x.get("mean") is None else (f"{x['mean']:.3f} ± {x['ci95']:.3f} (n {x['n']})" if x.get("ci95") is not None else f"{x['mean']:.3f}")
for k in ("minus_zero_premium_w", "denormal_vs_minus_zero_w", "booth_asymmetry_w", "int8_unit_costs_w"):
    for kk, v in rep[k].items():
        if isinstance(v, dict):
            print(f"{k} | {kk}: {fs(v)}")
print("constant_vs_minus_zero_w (anchor_pi - fp32.nz_both):", fs(rep["constant_vs_minus_zero_w"]))
print("sparse_mask_w:", fs(rep["sparse_mask_w"]))
print("\n== post hoc: the same numbers on card 1 (E93's scored.json > reported) beside")
r93 = s93["reported"]
for k in ("booth_asymmetry_w", "int8_unit_costs_w"):
    for kk, v in r93[k].items():
        if isinstance(v, dict):
            print(f"E93 {k} | {kk}: {fs(v)}")
print("\n== post hoc: int8's gate law on the half-gated tile, this session (E93 result 8's form)")
law = per(e, lambda c: c["int8.b_pairs_rtl"]["D"] - (0.5 * c["int8.full"]["D"] + 0.5 * c["int8.a_zeros_b_full"]["D"]))
print("b_pairs_rtl - (0.5 full + 0.5 a_zeros_b_full), same pass:", f(law))
law2 = per(e, lambda c: c["int8.b_pairs_rtl"]["D"] / c["int8.full"]["D"])
print("b_pairs_rtl / full, same pass:", f(law2))
print("b_pairs_rtl - E93's frozen point x int8 scale (3.61 x 1.027062 = %.3f):" % (3.6110 * 1.027062),
      f(per(e, lambda c: c["int8.b_pairs_rtl"]["D"] - 3.6110 * 1.027062)))
print("\n== post hoc: R5's pieces, fp32, this session")
print("a_randn_b_nz - a_nz_b_randn:", f(per(e, lambda c: c["fp32.a_randn_b_nz"]["D"] - c["fp32.a_nz_b_randn"]["D"])))
print("fp16 twin a_randn_b_nz - a_nz_b_randn:", f(per(e, lambda c: c["fp16.a_randn_b_nz"]["D"] - c["fp16.a_nz_b_randn"]["D"])))
print("\n== post hoc: denormal fraction per raw bit (fJ), fp32 both sides: (dnr_both - dn1_both) / (70,976 bits x 1.125e9 /s)")
x = per(e, lambda c: (c["fp32.dnr_both"]["D"] - c["fp32.dn1_both"]["D"]) / (70976 * 1.1252747e9) * 1e15)
print("fJ per raw denormal bit:", f(x))
print("\n== arms: passes kept and set aside (scored.json > arms)")
for nm, a in s["arms"].items():
    print(nm, "kept", a["passes"], "set aside", a["set_aside"], "| gate", a["gate_summary"], a["tally"], "| X", a["cross_card"]["aggregate"],
          a["cross_card"]["tally"], "| tie", a["tie_e78"]["verdict"], "| same as E93", a["same_verdict_as_e93"])
for nm in ("auto",):
    print("auto slope:", json.load(open(os.path.join(HERE, "e121-auto.json")))["leak"])
print("\n== skipped runs (E78's launch-reading rule), from the raw marks")
for p in e["passes"]:
    mk = os.path.join(HERE, "aifoundry3", "kinds", f"p{p}", "marks.jsonl")
    if os.path.exists(mk):
        sk = [json.loads(l) for l in open(mk) if '"skipped"' in l]
        print(p, [(m["item"], m["pos"], m["start_c"]) for m in sk])
print("\n== post hoc: D here over E93's D, every cell E93 read at 4 W or more (the session's own card scale, cell by cell)")
rs = sorted((e["items"][n]["D"]["mean"] / e93["items"][n]["D"]["mean"], n) for n in e["items"]
            if n in e93["items"] and (e93["items"][n]["D"]["mean"] or 0) >= 4.0)
vals = [r for r, _ in rs]
k = len(vals)
med = (vals[k // 2] if k % 2 else 0.5 * (vals[k // 2 - 1] + vals[k // 2]))
print(f"{k} cells: median {med:.4f}, range {vals[0]:.4f} ({rs[0][1]}) to {vals[-1]:.4f} ({rs[-1][1]}); "
      f"within 1.5% of E82's 1.031: {sum(1 for v in vals if abs(v / 1.0308 - 1) <= 0.015)} of {k}")
print("\n== post hoc: largest |difference| in the session tie against E78 (scored.json > primary > tie_e78)")
t = s["primary"]["tie_e78"]["cells"]
print(max((abs(v["difference_w"]), n) for n, v in t.items()))
