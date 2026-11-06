#!/usr/bin/env python3
"""E180's frozen forecasts: flips by register and bus class from the whole-minion bench, then watts above each mode's
zeros on the target card from the energy catalogue's own fadd rows (Q146(f); public tier).

    python3 forecast_e180.py --dir tools/claims-v3/e180            # writes forecast-e180.json and forecast-e180.txt
    python3 forecast_e180.py --dir tools/claims-v3/e180 --check    # re-makes both and compares byte for byte

Inputs (all in --dir): bench/counts-primary.jsonl (layout A, hart 1 started 50 cycles after hart 0), bench/counts-accpts.jsonl
(the accumulating kinds at three launch points), bench/counts-layouts.jsonl and bench/counts-lockstep.jsonl (the model-form
spread), noise/noise-e180.json (the catalogue's fadd rows per pass, from catalogue.json), kinds-e180.json.

Counts, per instruction (one fadd of eight lanes, both harts' results counted; the bench's lane-0 write enables are the
instruction count):
  N (named): bit flips between consecutive cycles, summed over 8 lanes, of the write-back path and the register file:
     wb_res (txfma's result, AND-ed with its valid), wr0 / wr1 (the RF's write data), byp (its three bypass registers),
     ram_rd and rd (the RF's read data before and after the bypass mux), opnd (txfma's in1-in3), rf_store (the 64 RF
     words), shsw (the short pipe's F4-F8 data). Above the mode's own zeros.
  I (all nets): Verilator's toggle coverage over the vector unit (tb.dut.vpu*), every bit and direction, clocks apart;
     hierarchical aliases of one net count once each, as in rtl-sim/fma_toggle_v2's `nets`. Above the mode's zeros.
Prices (fJ), each set by a rule fixed here, before any E180 datum:
  P  (primary) N priced by the catalogue's fadd.ps random - zeros on the target card, the same loop at the same operating
     point: p_N = (random - zeros) / N(random), an all-in price per named flip (E60's form: everything a designed flip
     drags with it). It does not use the const row, so that row is its check (the block says how it reads).
  C  N priced by the catalogue's fadd.ps const - zeros (a one-number result returning to zero at the write-back's gaps,
     the very mechanism), pooled over its three cards by inverse variance: p_N = (const - zeros) / N(const).
  F  N and I priced together, least squares on the target card's four catalogue rows above zeros (fadd.ps const and
     random, fadd.pi const and random).
  A  I alone, priced by fadd.ps random - zeros on the target card: one price per RTL toggle (M10's form).
  E  N priced by E60's measured result-path price, e_out = 30.00 +- 0.16 fJ per result bit that flips (fxor.pi, one
     hart, aifoundry3 at 600 MHz and 521.8 mV; docs/reports/data/2026-10-20-bitflip-ladder/reduce.txt line 32, commit
     dfee3d7a), shared over the five named nets one write-back bit's transition crosses here (wb_res, wr0, three byp):
     p_N = 30.00 / 5 fJ. The same price on card 1 (E60 did not run there).
Watts = price x count x the card's measured instruction rate for the mode (the catalogue's ops_per_s). The accumulating
modes use their plain mode's rate (the bench gives both the same rate). Uncertainty of P, in quadrature: the random row's
se on the card; the bench's spread of the write-back term over layouts and icache contention (B, o12, o16r, o28, icq8
against A); and the model-form term |C / P - 1| (P read on the const row, the one committed one-number point).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import filecmp
import json
import math
import os
import shutil
import statistics as st
import sys
import tempfile

TARGET = "aifoundry3"
FALLBACK = "aifoundry1-c1"
CARDS = (TARGET, FALLBACK)
NAMED = ("wb_res", "wr0", "wr1", "byp", "ram_rd", "rd", "opnd", "rf_store", "shsw")
E60_EOUT_FJ = 30.00          # E60 e_out_from_xio, aifoundry3, 600 MHz, 521.8 mV
NETS_PER_RZ_BIT = 5          # wb_res, wr0 and the three byp registers carry one write-back bit


def rnd(x):
    """Floats to 10 significant digits, so a --check does not depend on the interpreter's last-digit arithmetic."""
    if isinstance(x, float):
        return float(f"{x:.10g}") if x == x else None
    if isinstance(x, dict):
        return {k: rnd(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rnd(v) for v in x]
    return x


def jl(path):
    return [json.loads(l) for l in open(path)]


def per_instr(r):
    b = r["bench"]
    n = b["wb_any"]
    return {"n_instr": n, "named": {k: b["flips"][k] / n for k in NAMED}, "N": sum(b["flips"][k] for k in NAMED) / n,
            "I": r["cov"]["vpu"] / n, "I_lanes": r["cov"]["vpu_lanes"] / n, "core": r["cov"]["core"] / n,
            "rate": 64 * (b["iters"][0] + b["iters"][1]) / 2 / b["cycles"], "gaps_per_result": b["gap_runs"] / n,
            "gap_cycles_per_cycle": b["gap_cycles"] / b["cycles"]}


def above(x, z):
    return {"N": x["N"] - z["N"], "I": x["I"] - z["I"],
            "named": {k: x["named"][k] - z["named"][k] for k in NAMED}}


def lsq2(rows):
    """Least squares E = pN * N + pI * I through the origin (rows: (N, I, E))."""
    s11 = sum(n * n for n, i, e in rows)
    s12 = sum(n * i for n, i, e in rows)
    s22 = sum(i * i for n, i, e in rows)
    t1 = sum(n * e for n, i, e in rows)
    t2 = sum(i * e for n, i, e in rows)
    det = s11 * s22 - s12 * s12
    return (t1 * s22 - t2 * s12) / det, (s11 * t2 - s12 * t1) / det


def build(d):
    prim = {r["name"]: r for r in jl(os.path.join(d, "bench/counts-primary.jsonl"))}
    accp = jl(os.path.join(d, "bench/counts-accpts.jsonl"))
    lay = jl(os.path.join(d, "bench/counts-layouts.jsonl"))
    lock = {r["name"]: r for r in jl(os.path.join(d, "bench/counts-lockstep.jsonl"))}
    noise = json.load(open(os.path.join(d, "noise/noise-e180.json")))
    kinds = json.load(open(os.path.join(d, "kinds-e180.json")))["kinds"]
    pi = {k: per_instr(r) for k, r in prim.items()}
    # the accumulating kinds: the launch mean is the mean of the three launch points (E178's method)
    acc = {}
    for r in accp:
        acc.setdefault(r["name"], []).append(per_instr(r))
    zeros = {m: pi[f"{m}/zeros"] for m in ("fadd.ps", "fadd.pi", "fadd.ps.acc", "fadd.pi.acc")}
    counts = {}
    for k in kinds:
        name, mode = k["name"], k["mode"]
        if name.endswith("/zeros"):
            counts[name] = {"N": 0.0, "I": 0.0, "named": {c: 0.0 for c in NAMED}, "rate": pi[name]["rate"],
                            "gaps_per_result": pi[name]["gaps_per_result"]}
            continue
        a = above(pi[name], zeros[mode])
        a.update({"rate": pi[name]["rate"], "gaps_per_result": pi[name]["gaps_per_result"]})
        if name in acc:
            pts = [above(p, zeros[mode]) for p in acc[name]]
            a["window_from_zero"] = {"N": a["N"], "I": a["I"]}
            a["N"] = st.mean(p["N"] for p in pts)
            a["I"] = st.mean(p["I"] for p in pts)
            a["named"] = {c: st.mean(p["named"][c] for p in pts) for c in NAMED}
            a["launch_points"] = [{"N": p["N"], "I": p["I"]} for p in pts]
        counts[name] = a
    # the RZ term's spread over layouts and the alternative hart state, for his pair and const
    spread = {}
    for tag in sorted({r["tag"] for r in lay}):
        rows = {r["name"]: per_instr(r) for r in lay if r["tag"] == tag}
        z = rows["fadd.ps/zeros"]
        spread[tag] = {"N_const": rows["fadd.ps/const"]["N"] - z["N"], "N_f5_f4": rows["fadd.ps/f_5"]["N"] - rows["fadd.ps/f_4"]["N"],
                       "rate": rows["fadd.ps/zeros"]["rate"], "gaps_per_result": rows["fadd.ps/zeros"]["gaps_per_result"]}
    lz = per_instr(lock["fadd.ps/zeros"])
    spread["lockstep"] = {"N_const": per_instr(lock["fadd.ps/const"])["N"] - lz["N"],
                          "N_f5_f4": per_instr(lock["fadd.ps/f_5"])["N"] - per_instr(lock["fadd.ps/f_4"])["N"],
                          "rate": lz["rate"], "gaps_per_result": lz["gaps_per_result"]}
    nA = counts["fadd.ps/const"]["N"]
    rel = [spread[t]["N_const"] / nA for t in spread if t.startswith(("layout", "icq"))]
    lay_lo, lay_hi = min(rel + [1.0]), max(rel + [1.0])
    # prices
    cz = {c: noise["cards"][c]["above_zeros"]["fadd.ps/const-zeros"] for c in noise["cards"]}
    w = {c: 1.0 / cz[c]["se_pj"] ** 2 for c in cz}
    pooled = sum(w[c] * cz[c]["pj"] for c in cz) / sum(w.values())
    pooled_se = 1.0 / math.sqrt(sum(w.values()))
    prices = {"C": {"pN_fJ": 1000 * pooled / nA, "const_minus_zeros_pj": pooled, "se_pj": pooled_se,
                    "rel_se": pooled_se / pooled, "N_const": nA, "per_card": cz},
              "layout_rel_range": [lay_lo, lay_hi]}
    for c in CARDS:
        az = noise["cards"][c]["above_zeros"]
        rows4 = [(counts["fadd.ps/const"]["N"], counts["fadd.ps/const"]["I"], az["fadd.ps/const-zeros"]["pj"]),
                 (counts["fadd.ps/random"]["N"], counts["fadd.ps/random"]["I"], az["fadd.ps/random-zeros"]["pj"]),
                 (counts["fadd.pi/const"]["N"], counts["fadd.pi/const"]["I"], az["fadd.pi/const-zeros"]["pj"]),
                 (counts["fadd.pi/random"]["N"], counts["fadd.pi/random"]["I"], az["fadd.pi/random-zeros"]["pj"])]
        pN, pI = lsq2(rows4)
        prices[f"P@{c}"] = {"pN_fJ": 1000 * az["fadd.ps/random-zeros"]["pj"] / counts["fadd.ps/random"]["N"],
                            "random_minus_zeros_pj": az["fadd.ps/random-zeros"]["pj"],
                            "rel_se": az["fadd.ps/random-zeros"]["se_pj"] / az["fadd.ps/random-zeros"]["pj"]}
        prices[f"F@{c}"] = {"pN_fJ": 1000 * pN, "pI_fJ": 1000 * pI,
                            "fit": [{"N": n, "I": i, "measured_pj": e, "fitted_pj": pN * n + pI * i} for n, i, e in rows4]}
        prices[f"A@{c}"] = {"pI_fJ": 1000 * az["fadd.ps/random-zeros"]["pj"] / counts["fadd.ps/random"]["I"]}
    rates = {c: {m: st.mean(noise["cards"][c]["rows"][f"{m}/zeros/h2"]["ops_per_s"]) for m in ("fadd.ps", "fadd.pi")}
             for c in noise["cards"]}

    prices["E"] = {"pN_fJ": E60_EOUT_FJ / NETS_PER_RZ_BIT, "e_out_fJ": E60_EOUT_FJ, "nets_per_bit": NETS_PER_RZ_BIT,
                   "source": "docs/reports/data/2026-10-20-bitflip-ladder/reduce.txt line 32 (dfee3d7a)"}
    for c in CARDS:
        pc = prices[f"P@{c}"]
        pc["model_form_rel"] = abs(prices["C"]["pN_fJ"] / pc["pN_fJ"] - 1)
        pc["layout_rel"] = max(1 - lay_lo, lay_hi - 1)
        pc["total_rel"] = math.sqrt(pc["rel_se"] ** 2 + pc["layout_rel"] ** 2 + pc["model_form_rel"] ** 2)

    def watts(name, card):
        k = counts[name]
        mode = name.split("/")[0].replace(".acc", "")
        r = rates[card][mode]
        P = prices[f"P@{card}"]["pN_fJ"] * k["N"] * 1e-15 * r
        C = prices["C"]["pN_fJ"] * k["N"] * 1e-15 * r
        F = (prices[f"F@{card}"]["pN_fJ"] * k["N"] + prices[f"F@{card}"]["pI_fJ"] * k["I"]) * 1e-15 * r
        A = prices[f"A@{card}"]["pI_fJ"] * k["I"] * 1e-15 * r
        E = prices["E"]["pN_fJ"] * k["N"] * 1e-15 * r
        return {"P": P, "P_se": abs(P) * prices[f"P@{card}"]["total_rel"], "C": C, "F": F, "A": A, "E": E, "rate": r}

    fc = {}
    for k in kinds:
        name = k["name"]
        e = {"rule": k["rule"], "mode": k["mode"], "operands": k["operands"], "word": k.get("word"),
             "operand_popcount": k.get("operand_popcount"), "result_word": k.get("result_word"),
             "result_popcount": k.get("result_popcount"), "counts": counts[name],
             "per_lane_N": counts[name]["N"] / 8, "W": {c: watts(name, c) for c in CARDS}}
        fc[name] = e

    def pair(a, b, card=TARGET):
        x, y = fc[a]["W"][card], fc[b]["W"][card]
        out = {k: x[k] - y[k] for k in ("P", "C", "F", "A", "E")}
        out["dN"] = counts[a]["N"] - counts[b]["N"]
        out["dI"] = counts[a]["I"] - counts[b]["I"]
        return out

    pairs = {
        "his_pair_fadd.ps_5_minus_4": pair("fadd.ps/f_5", "fadd.ps/f_4"),
        "fadd.pi_f5_minus_f4": pair("fadd.pi/f_5", "fadd.pi/f_4"),
        "fadd.pi_i5_minus_i4": pair("fadd.pi/i_5", "fadd.pi/i_4"),
        "acc_5_minus_4": pair("fadd.ps.acc/f_5", "fadd.ps.acc/f_4"),
        "acc4_minus_plain4": {k: pair("fadd.ps.acc/f_4", "fadd.ps.acc/zeros")[k] - pair("fadd.ps/f_4", "fadd.ps/zeros")[k]
                              for k in ("P", "C", "F", "A", "E", "dN", "dI")},
        "X_ps_minus_pi_on_5": {k: pair("fadd.ps/f_5", "fadd.ps/zeros")[k] - pair("fadd.pi/f_5", "fadd.pi/zeros")[k]
                               for k in ("P", "C", "F", "A", "E", "dN", "dI")},
        "split_0p5_minus_1p5": pair("fadd.ps/f_0p5", "fadd.ps/f_1p5"),
        "split_const_minus_2": pair("fadd.ps/const", "fadd.ps/f_2"),
        "extreme_r3max_minus_zeros": pair("fadd.ps/r3_max", "fadd.ps/zeros"),
        "extreme_r3max_minus_const": pair("fadd.ps/r3_max", "fadd.ps/const"),
        "const_minus_zeros": pair("fadd.ps/const", "fadd.ps/zeros"),
    }
    # the result-popcount ladder over every fadd.ps one-number kind (anchors zeros and const included)
    ladder = [n for n in fc if fc[n]["mode"] == "fadd.ps" and fc[n]["operands"] in ("zeros", "const", "file")]
    xs = [fc[n]["result_popcount"] for n in ladder]
    slope = {}
    for arm in ("P", "C", "F", "A", "E"):
        ys = [fc[n]["W"][TARGET][arm] for n in ladder]
        mx, my = st.mean(xs), st.mean(ys)
        slope[arm] = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    groups = {}
    for n in ladder:
        groups.setdefault(fc[n]["result_popcount"], []).append(n)
    eq = {str(p): g for p, g in sorted(groups.items()) if len(g) >= 3}
    doc = {"what": "E180's frozen forecasts (forecast_e180.py)", "target": TARGET, "fallback": FALLBACK,
           "prices": prices, "rates": rates, "spread": spread, "kinds": fc, "pairs": pairs,
           "ladder": {"kinds": ladder, "result_popcount": xs, "slope_W_per_bit": slope},
           "equal_result_popcount_groups": eq}
    return doc


def text(doc):
    L = []
    p = doc["prices"]
    L.append("E180 forecasts (forecast_e180.py). Watts above each mode's zeros, aifoundry3 at 600 MHz; P primary, C F A E arms.")
    L.append(f"E: p_N = {p['E']['pN_fJ']:.3f} fJ per named flip (E60's e_out {p['E']['e_out_fJ']:.2f} fJ over {p['E']['nets_per_bit']} nets)")
    L.append(f"C: p_N = {p['C']['pN_fJ']:.3f} fJ per named flip (const - zeros pooled {p['C']['const_minus_zeros_pj']:.4f} "
             f"+- {p['C']['se_pj']:.4f} pJ over N(const) = {p['C']['N_const']:.3f}); the write-back term's range over bench "
             f"states x{p['layout_rel_range'][0]:.3f}-{p['layout_rel_range'][1]:.3f}")
    for c in CARDS:
        q = p['P@' + c]
        L.append(f"{c}: P p_N {q['pN_fJ']:.3f} fJ (random - zeros {q['random_minus_zeros_pj']:.4f} pJ, se {q['rel_se']:.4f}; "
                 f"model-form |C/P - 1| {q['model_form_rel']:.4f}; bench-state {q['layout_rel']:.4f}; total {q['total_rel']:.4f}); "
                 f"F p_N {p['F@' + c]['pN_fJ']:.3f} p_I {p['F@' + c]['pI_fJ']:.4f} fJ; A p_I {p['A@' + c]['pI_fJ']:.4f} fJ")
        for r in p["F@" + c]["fit"]:
            L.append(f"   F fit row N {r['N']:.2f} I {r['I']:.1f}: measured {r['measured_pj']:.4f} fitted {r['fitted_pj']:.4f} pJ")
    L.append("spread of the RZ term (N above zeros) by bench state: " + "; ".join(
        f"{t} const {v['N_const']:.3f} f5-f4 {v['N_f5_f4']:.3f} rate {v['rate']:.4f} gaps/result {v['gaps_per_result']:.4f}"
        for t, v in doc["spread"].items()))
    L.append("")
    L.append(f"{'kind':24s} {'op':>3s} {'res':>3s} {'N':>9s} {'I':>10s} {'P W':>8s} {'+-':>6s} {'C W':>8s} {'F W':>8s} {'A W':>8s} {'E W':>8s}")
    for n, k in doc["kinds"].items():
        w = k["W"][TARGET]
        L.append(f"{n:24s} {str(k['operand_popcount'] if k['operand_popcount'] is not None else '-'):>3s} "
                 f"{str(k['result_popcount'] if k['result_popcount'] is not None else '-'):>3s} {k['counts']['N']:9.3f} "
                 f"{k['counts']['I']:10.2f} {w['P']:8.4f} {w['P_se']:6.4f} {w['C']:8.4f} {w['F']:8.4f} {w['A']:8.4f} {w['E']:8.4f}")
    L.append("")
    for n, v in doc["pairs"].items():
        L.append(f"{n:32s} P {v['P']:+.4f} C {v['C']:+.4f} F {v['F']:+.4f} A {v['A']:+.4f} E {v['E']:+.4f} W  (dN {v['dN']:+.3f}, dI {v['dI']:+.2f})")
    L.append("ladder slope (W per result bit, fadd.ps one-number kinds): " +
             ", ".join(f"{a} {s:.5f}" for a, s in doc["ladder"]["slope_W_per_bit"].items()))
    L.append("equal-result-popcount groups: " + "; ".join(f"{k}: {', '.join(v)}" for k, v in doc["equal_result_popcount_groups"].items()))
    return "\n".join(L) + "\n"


def write(d, outdir):
    doc = build(d)
    json.dump(rnd(doc), open(os.path.join(outdir, "forecast-e180.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(outdir, "forecast-e180.txt"), "w").write(text(doc))
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not a.check:
        write(a.dir, a.dir)
        print(open(os.path.join(a.dir, "forecast-e180.txt")).read())
        return
    with tempfile.TemporaryDirectory() as t:
        write(a.dir, t)
        bad = [f for f in ("forecast-e180.json", "forecast-e180.txt")
               if not filecmp.cmp(os.path.join(t, f), os.path.join(a.dir, f), shallow=False)]
    print("CHECK FAIL: " + ", ".join(bad) if bad else "CHECK PASS: forecast-e180.json and forecast-e180.txt byte for byte")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
