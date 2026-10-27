#!/usr/bin/env python3
"""E67 (Q128): the results tables and the scored decision rules, out of the committed reductions.

    python3 tools/claims-v3/ha/report_e67.py --e67 hl.json --e65 <E65 hl.json> --closure closure.json
        --out results.md [--json scored.json]

Writes the markdown the data README's Results section uses, and scores P1-P8 against the bands registered in
tools/claims-v3/ha/README.md. Pure Python: no numpy, so it runs wherever the data is.
"""
import argparse
import json
import math

FIELD = {**{j: "mantissa" for j in range(23)}, **{j: "exponent" for j in range(23, 31)}, 31: "sign"}
GRID = [0, 8, 16, 22]


def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return num / (da * db) if da and db else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e67", required=True)
    ap.add_argument("--e65", required=True)
    ap.add_argument("--closure")
    ap.add_argument("--out", required=True)
    ap.add_argument("--json")
    a = ap.parse_args()
    C = json.load(open(a.e67))["cards"]["aifoundry3"]
    G = json.load(open(a.e67))["gates"]["aifoundry3"]
    B = json.load(open(a.e65))["cards"]["aifoundry3"]
    cl = json.load(open(a.closure)) if a.closure else {}
    A = {int(k): v for k, v in C.get("a_bits", {}).items()}
    AP = {int(k): v for k, v in C.get("a_bits_pi", {}).items()}
    BB = {int(k): v for k, v in B.get("bits", {}).items()}
    BP = {int(k): v for k, v in B.get("bits_pi", {}).items()}
    L, S = [], {}
    w = L.append
    fj = lambda x: x["J_per_alternating_bit"] * 1e15
    sefj = lambda x: (x["se"] or 0) / abs(x["dW"]) * fj(x) if x["dW"] else 0

    w(f"Card aifoundry3, {C['clock_mhz']} MHz, {C['v_mean']*1000:.1f} mV. Passes kept "
      f"{C['passes']}; runs kept {G['kept']} of {G['runs']}; leakage {G['leak_W_per_C']:.3f} W/°C "
      f"({G['leak_runs']} runs). Passes set aside: {G['passes_set_aside'] or 'none'}.\n")

    # ---- block 1
    w("### Block 1 — the A side at all 32 positions (B = 1.0)\n")
    w("| bit | field | ΔW above the constant-A zero | SE (W) | fJ per flipped A bit | E65's B side (fJ) | A / B |")
    w("|---|---|---|---|---|---|---|")
    ratios, pa, pb = {}, [], []
    for j in sorted(A):
        x = A[j]
        b = BB.get(j)
        r = (fj(x) / fj(b)) if b and fj(b) else None
        if b:
            ratios[j] = r
            if j <= 22:
                pa.append(fj(x))
                pb.append(fj(b))
        w(f"| {j} | {FIELD[j]} | {x['dW']:.3f} | {x['se'] or 0:.3f} | {fj(x):.0f} ± {sefj(x):.0f} | "
          f"{fj(b):.0f} | {r:.2f} |" if b else
          f"| {j} | {FIELD[j]} | {x['dW']:.3f} | {x['se'] or 0:.3f} | {fj(x):.0f} ± {sefj(x):.0f} | — | — |")
    mant = [fj(A[j]) for j in range(23) if j in A]
    allp = [fj(A[j]) for j in sorted(A)]
    rho_j = spearman(list(range(len(mant))), mant) if len(mant) > 2 else float("nan")
    span = (max(allp) / min(allp)) if allp and min(allp) > 0 else float("nan")
    cheap4 = sorted(A, key=lambda j: fj(A[j]))[:4]
    expo = [fj(A[j]) for j in range(23, 31) if j in A]
    low = [fj(A[j]) for j in range(16) if j in A]
    w(f"\nMantissa Spearman ρ(bit, price) = **{rho_j:.3f}**; span over all 32 positions "
      f"**{span:.1f}×** ({min(allp):.0f} fJ at bit {min(A, key=lambda j: fj(A[j]))}, "
      f"{max(allp):.0f} fJ at bit {max(A, key=lambda j: fj(A[j]))}). Exponent mean "
      f"{(sum(expo)/len(expo) if expo else float('nan')):.0f} fJ, "
      f"low-mantissa (0–15) mean {(sum(low)/len(low) if low else float('nan')):.0f} fJ, "
      f"sign bit {fj(A[31]):.0f} fJ. Four cheapest positions: {cheap4}.\n")
    rho_ab = spearman(pa, pb) if len(pa) > 2 else float("nan")
    rl = [r for r in ratios.values() if r]
    inband = sum(1 for r in rl if 1 / 3 <= r <= 3)
    w(f"A-side against E65's B side over the 23 mantissa positions: Spearman ρ = **{rho_ab:.3f}**; the A/B "
      f"ratio runs {min(rl):.2f}–{max(rl):.2f} over all {len(rl)} shared positions, median "
      f"{sorted(rl)[len(rl)//2]:.2f}, with **{inband} of {len(rl)}** inside [1/3, 3].\n")
    S["P1"] = {"rho_mantissa": rho_j, "span": span,
               "verdict": "PASS" if (rho_j > 0.5 and span > 5) else "FAIL"}
    S["P2"] = {"rho_A_vs_B": rho_ab, "n_in_band": inband, "n": len(rl),
               "ratio_min": min(rl), "ratio_max": max(rl), "ratio_median": sorted(rl)[len(rl) // 2],
               "verdict": "PASS" if (rho_ab > 0.5 and inband > len(rl) / 2) else "FAIL"}
    S["P3"] = {"sign_rank": sorted(A, key=lambda j: fj(A[j])).index(31) + 1, "cheapest_four": cheap4,
               "exponent_mean_fJ": sum(expo) / len(expo) if expo else None,
               "low_mantissa_mean_fJ": sum(low) / len(low) if low else None,
               "verdict": "PASS" if (31 in cheap4 and expo and low and min(expo) > max(low[:16]))
                          else ("PARTIAL" if 31 in cheap4 or (expo and low and sum(expo) / len(expo) > sum(low) / len(low))
                                else "FAIL")}

    # ---- block 2
    w("### Block 2 — the busy partner (B = π)\n")
    w("| A bit | ΔW above `ap_h0` | SE (W) | fJ per flipped A bit | quiet partner (fJ) | busy − quiet (W) | SE | E65's B side with A = π (fJ) |")
    w("|---|---|---|---|---|---|---|---|")
    nsig, npos = 0, 0
    for j in sorted(AP):
        x, q = AP[j], A.get(j)
        d = C.get("a_partner", {}).get(str(j)) or C.get("a_partner", {}).get(j) or {}
        bp = BP.get(j)
        if d.get("W") is not None:
            npos += 1 if d["W"] > 0 else 0
            nsig += 1 if (d["W"] > 0 and d.get("se") and d["W"] > 2 * d["se"]) else 0
        w(f"| {j} | {x['dW']:.3f} | {x['se'] or 0:.3f} | {fj(x):.0f} ± {sefj(x):.0f} | "
          f"{(fj(q) if q else float('nan')):.0f} | {(d.get('W') if d.get('W') is not None else float('nan')):.3f} | "
          f"{(d.get('se') or 0):.3f} | {(fj(bp) if bp else float('nan')):.0f} |")
    S["P4"] = {"n_positive": npos, "n_at_2se": nsig, "n": len(AP),
               "verdict": "PASS" if (npos == len(AP) and nsig >= 3) else ("PARTIAL" if nsig >= 3 else "FAIL")}
    if 11 in AP:
        r11 = fj(AP[11]) / 745.0
        S["P5"] = {"abp_11_fJ": fj(AP[11]), "e65_bpi_11_fJ": 745.0, "ratio": r11,
                   "verdict": "PASS" if 1 / 3 <= r11 <= 3 else "FAIL"}
        w(f"\n`abp_11`, the A-side mirror of the flow-M case: **{fj(AP[11]):.0f} ± {sefj(AP[11]):.0f} fJ** per "
          f"flipped A bit, against E65's `bpi_11` (B bit 11 with A = π) at 745 ± 56 fJ — a ratio of "
          f"**{r11:.2f}**.\n")

    # ---- block 3
    ix = C.get("ix")
    if ix:
        w("### Block 3 — the interaction grid: two flips at once against the sum of each alone\n")
        w(f"Base `ix_z` (both operands constant): {ix['base_W']:.2f} W. Margins, each against that base:\n")
        w("| margin | side | bit | ΔW | fJ per flipped bit |")
        w("|---|---|---|---|---|")
        for nm, m in sorted(ix["margins"].items(), key=lambda t: (t[1]["side"], t[1]["bit"])):
            w(f"| `{nm}` | {m['side'].upper()} | {m['bit']} | {m['dW']:.3f} | "
              f"{m['J_per_alternating_bit']*1e15:.0f} |")
        w("\n| A bit \\ B bit | " + " | ".join(str(j) for j in GRID) + " |")
        w("|---|" + "---|" * len(GRID))
        for i in GRID:
            row = [f"| **{i}** "]
            for j in GRID:
                c = ix["cells"].get(f"{i}_{j}")
                row.append(f"| {c['cell_dW']:.2f} / {c['sum_dW']:.2f} ({c['excess_W']:+.2f}) "
                           if c else "| — ")
            w("".join(row) + "|")
        w("\n*cell ΔW / sum of its two margins (excess).* Mean excess over the 16 cells "
          f"**{ix['excess_mean_W']:+.3f} ± {ix['excess_mean_se'] or 0:.3f} W**, largest |excess| "
          f"{ix['excess_abs_max_W']:.3f} W, mean excess as a fraction of the cell's sum "
          f"{ix['excess_frac_mean']*100:+.1f}%.\n")
        ok_cells = sum(1 for c in ix["cells"].values()
                       if c["excess_frac_of_sum"] is not None and abs(c["excess_frac_of_sum"]) < 0.20)
        allsmall = all(abs(c["excess_W"]) <= 0.5 for c in ix["cells"].values() if c["excess_W"] is not None)
        m_, se_ = ix["excess_mean_W"], ix["excess_mean_se"] or 0
        if allsmall and abs(m_) <= 0.3 and ok_cells >= 12:
            v = "PASS (additive)"
        elif m_ < -0.5 and abs(m_) > 3 * se_:
            v = "FAIL (sub-additive)"
        elif m_ > 0.5 and m_ > 3 * se_:
            v = "FAIL (super-additive)"
        else:
            v = "UNDECIDED"
        S["P6"] = {"mean_excess_W": m_, "se": se_, "max_abs_excess_W": ix["excess_abs_max_W"],
                   "cells_within_20pct": ok_cells, "n_cells": ix["n_cells"],
                   "all_within_0.5W": allsmall, "verdict": v}

    # ---- block 4
    anc = C.get("anchors", {})
    if anc:
        w("### Block 4 — the anchors on this card and pass set\n")
        w("| item | what it runs | board W | SE | ΔW above its zero | A bits/op | B bits/op |")
        w("|---|---|---|---|---|---|---|")
        WHAT = {"anchor_zeros": "both operands zero", "anchor_ones": "both operands 1.0",
                "anchor_pi": "both operands π", "anchor_randn": "both operands random fp32 (kernel-generated)",
                "nrd_a": "A random fp32, B = 1.0", "nrd_b": "A = 1.0, B random fp32",
                "lq_h0": "A = 1.0, B constant (E65's quiet zero)", "lb_h0": "A = π, B constant (E65's busy zero)",
                "aq_h0": "A constant, B = 1.0 (the A scan's zero)", "aq_e64": "A constant (exp 64), B = 1.0",
                "ap_h0": "A constant, B = π", "ix_z": "the grid's base, both constant"}
        for n in ("anchor_zeros", "anchor_ones", "anchor_pi", "anchor_randn", "nrd_a", "nrd_b",
                  "lq_h0", "lb_h0", "aq_h0", "aq_e64", "ap_h0", "ix_z"):
            x = anc.get(n)
            if not x or x.get("p80") is None:
                continue
            d = x.get("dW_vs_zero")
            w(f"| `{n}` | {WHAT.get(n,'')} | {x['p80']:.2f} | {x['se'] or 0:.2f} | "
              f"{(f'{d:+.2f}' if d is not None else '—')} | {x['A_bits_per_op'] or 0} | {x['B_bits_per_op'] or 0} |")
        za, zb = anc.get("nrd_a", {}), anc.get("nrd_b", {})
        if za.get("dW_vs_zero") and zb.get("dW_vs_zero"):
            r = za["dW_vs_zero"] / zb["dW_vs_zero"]
            S["P7"] = {"ratio": r, "designed_ratio": 27648 / 56784,
                       "verdict": "PASS" if 0.3 <= r <= 0.8 else "FAIL"}
            w(f"\nd(`nrd_a`) / d(`nrd_b`) = **{r:.3f}**, against the designed-bit ratio 27,648 / 56,784 = 0.487.\n")
        if anc.get("anchor_randn", {}).get("p80") and anc.get("anchor_zeros", {}).get("p80"):
            w(f"Random against zeros on this card at 600 MHz: "
              f"**{anc['anchor_randn']['p80'] - anc['anchor_zeros']['p80']:.2f} W** "
              f"({anc['anchor_zeros']['p80']:.2f} → {anc['anchor_randn']['p80']:.2f} W).\n")

    # ---- closure
    if cl.get("items"):
        w("### The closure test — do the summed per-position prices reproduce a random-data step?\n")
        w("| item | designed flips per multiply-add | predicted from the price lists | measured | measured / predicted | turn-on corrected | ratio |")
        w("|---|---|---|---|---|---|---|")
        rr, rc = [], []
        for n in ("nrd_a", "nrd_b"):
            d = cl["items"].get(n, {})
            if "predicted_W" not in d:
                continue
            rr.append(d["ratio_measured_over_predicted"])
            pc = d.get("predicted_W_turnon_corrected")
            if pc is not None:
                rc.append(d["ratio_measured_over_predicted_corrected"])
            w(f"| `{n}` | {d['A_bits']} A + {d['B_bits']} B | {d['predicted_W']:.2f} W | "
              f"{d['measured_W']:.2f} ± {d['measured_se'] or 0:.2f} W | **{d['ratio_measured_over_predicted']:.2f}** | "
              + (f"{pc:.2f} W | **{d['ratio_measured_over_predicted_corrected']:.2f}** |" if pc is not None else "— | — |"))
        if cl.get("turn_on_W") is not None:
            d0 = cl["items"].get("nrd_a", {})
            w(f"\n*Turn-on corrected* (post hoc, amendment A13, not a registered prediction): a price measured "
              f"against a constant-operand zero is `T + e·n·rate`, so summing it over a random workload charges "
              f"the fixed turn-on `T` once per flipped position — "
              f"{d0.get('turn_on_counted_times_in_raw_sum', float('nan')):.1f} times for `nrd_a`. Taking "
              f"**T = {cl['turn_on_W']:.3f} W** (minus the grid's mean interaction excess) out of every price and "
              f"adding it back once gives the right-hand columns.\n")
        if "randn_step" in cl:
            r = cl["randn_step"]
            w(f"\nThe both-sides anchor: `anchor_randn` − `anchor_zeros` = **{r['step_W']:.2f} W**. Its operands "
              f"are made by the kernel, not read from a file, so its flip histogram cannot be counted; the nearest "
              f"counted stimulus is `nrd_a` + `nrd_b` (one random side each), whose price-list prediction sums to "
              f"{r['counted_standin_W']:.2f} W — a stand-in, not the same workload, ratio "
              f"{r['ratio_step_over_standin']:.2f}.\n")
        if rr:
            S["P8"] = {"ratios": rr, "worst": max(rr + [1 / x for x in rr if x]),
                       "ratios_turnon_corrected": rc,
                       "verdict": "PASS" if all(0.5 <= x <= 2 for x in rr) else "FAIL"}

    w("### The registered rules, scored\n")
    w("| rule | what it asked | measured | verdict |")
    w("|---|---|---|---|")
    ASK = {"P1": "the A scan rises with the bit (mantissa ρ > 0.5) and spans > 5×",
           "P2": "A within a factor of 3 of E65's B at most shared positions, and ρ > 0.5",
           "P3": "the sign bit among the four cheapest; exponent dearer than mantissa 0–15",
           "P4": "busy − quiet > 0 everywhere, at ≥ 2 SE for ≥ 3 of 5",
           "P5": "`abp_11` within a factor of 3 of E65's `bpi_11` (745 fJ)",
           "P6": "every cell's excess within ±0.5 W, mean within ±0.3 W, ≥ 12 of 16 within 20%",
           "P7": "d(nrd_a)/d(nrd_b) in [0.3, 0.8]",
           "P8": "the summed price lists predict both one-sided steps within a factor of 2"}
    GOT = {"P1": lambda s: f"ρ = {s['rho_mantissa']:.3f}, span {s['span']:.1f}×",
           "P2": lambda s: f"ρ = {s['rho_A_vs_B']:.3f}, {s['n_in_band']}/{s['n']} in band, median ratio {s['ratio_median']:.2f}",
           "P3": lambda s: f"sign bit ranks {s['sign_rank']}/32; exponent mean {s['exponent_mean_fJ']:.0f} fJ vs low-mantissa {s['low_mantissa_mean_fJ']:.0f} fJ",
           "P4": lambda s: f"{s['n_positive']}/{s['n']} positive, {s['n_at_2se']}/{s['n']} at ≥ 2 SE",
           "P5": lambda s: f"{s['abp_11_fJ']:.0f} fJ, ratio {s['ratio']:.2f}",
           "P6": lambda s: f"mean excess {s['mean_excess_W']:+.3f} ± {s['se']:.3f} W, |max| {s['max_abs_excess_W']:.3f} W, {s['cells_within_20pct']}/{s['n_cells']} within 20%",
           "P7": lambda s: f"{s['ratio']:.3f}",
           "P8": lambda s: "ratios " + ", ".join(f"{x:.2f}" for x in s["ratios"])
                           + (" (turn-on corrected " + ", ".join(f"{x:.2f}" for x in s["ratios_turnon_corrected"]) + ")"
                              if s.get("ratios_turnon_corrected") else "")}
    for k in ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"):
        if k in S:
            w(f"| **{k}** | {ASK[k]} | {GOT[k](S[k])} | **{S[k]['verdict']}** |")
        else:
            w(f"| **{k}** | {ASK[k]} | not measured | — |")
    open(a.out, "w").write("\n".join(L) + "\n")
    if a.json:
        json.dump(S, open(a.json, "w"), indent=1)
    print("\n".join(L))


if __name__ == "__main__":
    main()
