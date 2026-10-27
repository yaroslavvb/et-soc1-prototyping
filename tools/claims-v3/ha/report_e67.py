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
    # The span is a ratio, so it needs a positive floor: a position whose price is not at least 1 SE above zero
    # is excluded by name rather than allowed to make the ratio meaningless (one noisy position can read < 0).
    pos = {j: fj(A[j]) for j in A if fj(A[j]) > 0 and A[j]["dW"] > (A[j]["se"] or 0)}
    excluded = sorted(set(A) - set(pos))
    span = (max(pos.values()) / min(pos.values())) if pos else float("nan")
    cheap4 = sorted(A, key=lambda j: fj(A[j]))[:4]
    expo = [fj(A[j]) for j in range(23, 31) if j in A]
    low = [fj(A[j]) for j in range(16) if j in A]
    w(f"\nMantissa Spearman ρ(bit, price) = **{rho_j:.3f}**; span over the {len(pos)} positions whose price "
      f"clears its own SE **{span:.1f}×** ({min(pos.values()):.0f} fJ at bit {min(pos, key=pos.get)}, "
      f"{max(pos.values()):.0f} fJ at bit {max(pos, key=pos.get)})"
      + (f"; excluded as not above zero at 1 SE: {excluded}" if excluded else "") + ". Exponent mean "
      f"{(sum(expo)/len(expo) if expo else float('nan')):.0f} fJ, "
      f"low-mantissa (0–15) mean {(sum(low)/len(low) if low else float('nan')):.0f} fJ, "
      f"sign bit {fj(A[31]):.0f} fJ. Four cheapest positions: {cheap4}.\n")
    rho_ab = spearman(pa, pb) if len(pa) > 2 else float("nan")
    rl = [r for r in ratios.values() if r]
    rm = [r for j, r in ratios.items() if r and j <= 22]          # the 23 mantissa positions P2 registers
    inband = sum(1 for r in rm if 1 / 3 <= r <= 3)
    w(f"A-side against E65's B side over the 23 mantissa positions: Spearman ρ = **{rho_ab:.3f}**, with "
      f"**{inband} of {len(rm)}** inside the registered [1/3, 3] band. Over all {len(rl)} shared positions the "
      f"A/B ratio runs {min(rl):.2f}–{max(rl):.2f}, median {sorted(rl)[len(rl)//2]:.2f}.\n")
    S["P1"] = {"rho_mantissa": rho_j, "span": span, "positions_excluded_from_span": excluded,
               "verdict": "PASS" if (rho_j > 0.5 and span > 5) else "FAIL"}
    # ---- post hoc (amendment A14, written before the grid's data): the raw A/B ratio is not a ratio of
    # MARGINAL prices. Each per-position price is p = e + T/(n·rate), and the A side's n is 2,048 against the
    # B side's 4,096, so the same fixed turn-on T inflates an A-side price TWICE as much per bit as a B-side
    # one. With T from the grid (minus the mean interaction excess), e = p − T/(n·rate) on each side, and the
    # marginal ratio is reported beside the raw one. P2 keeps its registered scoring on the raw prices.
    ixg = C.get("ix") or {}
    T = -ixg["excess_mean_W"] if ixg.get("excess_mean_W") is not None else None
    rate0 = A[0]["rate"] if 0 in A else None
    if T is not None and rate0:
        eA = {j: fj(A[j]) - T / (2048 * rate0) * 1e15 for j in A}
        eB = {j: fj(BB[j]) - T / (4096 * rate0) * 1e15 for j in BB}
        mr = [eA[j] / eB[j] for j in sorted(eA) if j in eB and eB[j] > 0 and j <= 22]
        S["marginal_A_over_B"] = {"turn_on_W": T, "turn_on_fJ_per_A_bit": T / (2048 * rate0) * 1e15,
                                  "turn_on_fJ_per_B_bit": T / (4096 * rate0) * 1e15,
                                  "ratios": {j: eA[j] / eB[j] for j in sorted(eA) if j in eB and eB[j] > 0},
                                  "median_mantissa": sorted(mr)[len(mr) // 2] if mr else None,
                                  "n_negative_A": sum(1 for v in eA.values() if v < 0),
                                  "n_negative_B": sum(1 for v in eB.values() if v < 0)}
        w(f"**Marginal prices** (post hoc, amendment A14): every per-position price is `e + T/(n·rate)`, and the "
          f"A side's n is 2,048 against the B side's 4,096, so one fixed turn-on inflates an A-side price twice "
          f"as much per bit. With **T = {T:.3f} W** from the grid, that is "
          f"{T/(2048*rate0)*1e15:.0f} fJ on every A price and {T/(4096*rate0)*1e15:.0f} fJ on every B one. "
          f"Taking it out, the A/B ratio over the mantissa has median "
          f"**{(sorted(mr)[len(mr)//2] if mr else float('nan')):.2f}** against the raw "
          f"{sorted(rm)[len(rm)//2]:.2f}"
          + (f"; {S['marginal_A_over_B']['n_negative_A']} A and {S['marginal_A_over_B']['n_negative_B']} B "
             f"positions go negative once T is removed, which bounds T rather than pricing those positions."
             if (S["marginal_A_over_B"]["n_negative_A"] or S["marginal_A_over_B"]["n_negative_B"]) else ".") + "\n")
    S["P2"] = {"rho_A_vs_B": rho_ab, "n_in_band": inband, "n": len(rm),
               "ratio_min": min(rl), "ratio_max": max(rl), "ratio_median": sorted(rl)[len(rl) // 2],
               "verdict": "PASS" if (rho_ab > 0.5 and inband > len(rm) / 2) else "FAIL"}
    # P3 has two halves, scored as E65 scored its own A3: (a) the sign bit among the four cheapest; (b) EVERY
    # exponent bit dearer than EVERY mantissa bit below 16. The counterexample is named when (b) fails.
    half_a = 31 in cheap4
    ctr = [(je, jm) for je in range(23, 31) if je in A for jm in range(16) if jm in A
           and fj(A[jm]) >= fj(A[je])]
    half_b = expo and low and not ctr
    S["P3"] = {"sign_rank": sorted(A, key=lambda j: fj(A[j])).index(31) + 1, "cheapest_four": cheap4,
               "exponent_mean_fJ": sum(expo) / len(expo) if expo else None,
               "low_mantissa_mean_fJ": sum(low) / len(low) if low else None,
               "half_a_sign_cheap": bool(half_a), "half_b_exponent_over_low_mantissa": bool(half_b),
               "counterexamples": ctr[:6], "n_counterexamples": len(ctr),
               "verdict": "PASS" if (half_a and half_b) else ("PARTIAL" if (half_a or half_b) else "FAIL")}

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
        # The tie to E65: the items both experiments ran, four hours apart on the same card at the same clock
        # and rail. These are a comparison of two committed reductions, not a new analysis.
        tie = []
        for n in ("anchor_pi", "lq_h0", "lb_h0"):
            e67v = anc.get(n, {}).get("p80")
            e65v = (B.get("items", {}).get(n) or {}).get("p80")
            if e67v is not None and e65v is not None:
                tie.append((n, e65v, e67v, e67v - e65v))
        if tie:
            w("\n**The tie to E65**, the items both experiments ran on this card — this is what lets the two "
              "price lists be added without a conversion:\n")
            w("| item | E65 (W) | E67 (W) | difference |")
            w("|---|---|---|---|")
            for n, v5, v7, d_ in tie:
                w(f"| `{n}` | {v5:.2f} | {v7:.2f} | {d_:+.2f} |")
            S["tie_to_e65"] = {n: {"e65_W": v5, "e67_W": v7, "diff_W": d_} for n, v5, v7, d_ in tie}
            w(f"\nLargest disagreement {max(abs(d_) for _, _, _, d_ in tie):.2f} W over "
              f"{len(tie)} shared items.\n")
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
        # Additivity at the WHOLE-OPERAND level, beside the grid's per-bit additivity: one random side plus the
        # other, against both random at once. The four constant-operand items (anchor_pi, lq_h0, aq_h0, ix_z)
        # are the same state by four routes, so their spread is this comparison's own noise floor.
        base = [anc[n]["p80"] for n in ("anchor_pi", "lq_h0", "aq_h0", "aq_e64", "ap_h0", "ix_z")
                if anc.get(n, {}).get("p80") is not None]
        if anc.get("anchor_randn", {}).get("p80") and za.get("dW_vs_zero") and zb.get("dW_vs_zero") and base:
            both = anc["anchor_randn"]["p80"] - (sum(base) / len(base))
            summed = za["dW_vs_zero"] + zb["dW_vs_zero"]
            S["whole_operand_additivity"] = {"both_random_W": both, "sum_of_one_sided_W": summed,
                                             "ratio": both / summed if summed else None,
                                             "constant_operand_spread_W": max(base) - min(base), "n_bases": len(base)}
            w(f"**Additivity at the whole-operand level** (beside the grid's per-bit additivity): both operands "
              f"random is **{both:.2f} W** above the constant-operand level, where one random side plus the other "
              f"sums to **{summed:.2f} W** — a ratio of **{both/summed:.2f}**. The {len(base)} constant-operand "
              f"items (`anchor_pi`, `lq_h0`, `aq_h0`, `aq_e64`, `ap_h0`, `ix_z`: the same state by six routes) "
              f"span {max(base)-min(base):.2f} W, which is this comparison's own noise floor.\n")

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
           "P3": lambda s: (f"sign bit ranks {s['sign_rank']}/32 ({'in' if s['half_a_sign_cheap'] else 'not in'} the cheapest four); "
                            f"exponent mean {s['exponent_mean_fJ']:.0f} fJ vs low-mantissa {s['low_mantissa_mean_fJ']:.0f} fJ, "
                            f"{s['n_counterexamples']} mantissa-below-16 bits at or above an exponent bit"),
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
