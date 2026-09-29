#!/usr/bin/env python3
"""Summarize the sparsity runs into the numbers and chart data used by the report.

    python3 workloads/sparsity/analyze.py docs/reports/data/2026-09-18-sparsity-aifoundry3 [--embed REPORT_HTML]

The data directory holds the SPARSITY lines of each run (*.jsonl from run_lab.sh; diverge/ for the divergence
sweep), clock.csv (minion clock and board power during those runs) and energy-*/ (run_energy.py). With --embed
the script replaces the JSON inside the report's <script type="application/json" id="sparsity-data"> tag.

"energy" is the page's first run of the power configurations (18 September, this card, no temperature control),
which the page keeps as one "first measured" note since 28 September; every power figure the page shows is the
three-card check's ("v3" below). The script ends by printing the values the page's text quotes (page_summary()).
Until 28 September --later HORACE3_JSON added the Horace experiment's 22 September runs of the same loop on this card
(zeros, ones, random normal); v3.operands, the three-card check's runs of those patterns, replaced them.

--claims-v3 DIR (default: docs/reports/data/2026-09-25-claims-v3, when it exists; "none" skips it) adds "v3": the
three-card check of 25-26 September on every card it holds (aifoundry2, aifoundry3, aifoundry1-c1), read in the
version-3 layout, which this script's own readers cannot take as a data directory:
  v3.tload.<card>: the same TensorLoad rows as "tload" ([lines, cycles per load, GB/s]) from each kept V3-LAT pass
      (raw/<card>/lat/p*/sp/, block.json "ok"), as the median over the passes, plus each pass's cycles per load;
  v3.energy.<card>: V3-ABL-B's runs of the same TensorFMA and layer configurations (results/ablb.runs.json, the
      reducer's per-run table; registered blocks 1-3, kept runs), in the shape of energy.configs: above-idle power
      ("dyn" = p80 - p_before, the reducer's metric) as mean, min and max over the blocks, the rate, pJ per unit
      above idle, J per unit above idle and on the board (p80 / rate), the idle just before the runs and the
      launch temperature; and c2_reads_high_w: how far its registered above-idle values read from the runs' launch
      temperature (the check's note C2, revised; W, positive = high), as the pair [die at the sensor's whole-degree
      launch reading, die V3_C2_STEP_C above it], with leak and reference from ablb.runs.json's params_by_card;
  v3.operands.<card>: V3-ABL-A's runs of the same TensorFMA fp32 loop on all 1,024 minions (A and B in the L1
      scratchpad, 546 cycles per op) with A and B all zeros, all ones and random normal data (results/abla.runs.json;
      kept runs of the passes the reducer used, the registered "switching" metric: p80 after the pre-registered
      dropout rule, minus p_before), as the energy manual's section 3.2 reduces them (tools/ettelem/
      build_energy_manual.py): per pattern the runs, above-idle power and pJ per multiply-add (each run's switching
      / rate) as mean, min and max, and the idle, rate and launch temperature; per card c2_reads_high_w over these
      runs, as for v3.energy, and at_die_w: each pattern's mean at the die temperature of its launches, at both ends.
"""
import argparse
import glob
import json
import math
import os
import re
import statistics

CLAIMS_V3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "reports", "data",
                         "2026-09-25-claims-v3")
V3_CARD_ORDER = ["aifoundry2", "aifoundry3", "aifoundry1-c1"]  # the chart kit's card registry order
V3_BLOCKS = [1, 2, 3]  # V3-ABL-B's registered blocks (tools/claims-v3/ablb/reduce.py REG)
# docs/reports/data/2026-09-25-claims-v3/AMENDMENTS.md, note C2 (revised 26 Sep): the registered leakage correction
# references a fixed launch temperature per card (params_by_card: 80.9 C and 0.81 W/C on aifoundry2 and aifoundry1-c1,
# 55.8 C and 0.55 W/C on aifoundry3), while each run launched at a whole-degree die reading; the die sat at the reading
# or up to V3_C2_STEP_C above it, which cannot be settled. A run's value at its launch temperature is its registered
# value + leak x (t_die - reference). The registered values are kept; c2_reads_high_w gives the mean offset, both ends.
V3_C2_STEP_C = 0.96
# V3-ABL-A's configurations of this page's TensorFMA fp32 loop on other operand values (tools/claims-v3/abla/abl_a.cfg)
V3_OPERANDS = [("fp32_zeros", "zeros"), ("fp32_ones", "ones"), ("fp32_randn", "randn")]
MAC_PER_FP32_OP = 16 * 16 * 16


def load(path):
    out = []
    if os.path.exists(path):
        for line in open(path):
            if line.startswith("SPARSITY "):
                out.append(json.loads(line.split(" ", 1)[1]))
    return out


def clock_mhz(d):
    vals = []
    for f in [os.path.join(d, "clock.csv"), os.path.join(d, "diverge", "clock.csv")]:
        if os.path.exists(f):
            for line in open(f):
                p = line.strip().split(",")
                if len(p) >= 2 and p[0].isdigit() and p[1]:
                    vals.append(float(p[1]))
    return statistics.median(vals) if vals else 600.0, sorted(set(vals))


def tload_rows(path, ns_per_cycle):
    """[lines, cycles per load, GB/s] per SPARSITY line of one tload-*.jsonl: the bytes the mask let through over the
    slowest minion's loop time. (The host's gbps_wall divides by the launch's wall time, which adds 0.2-0.4 ms to runs
    of about 1 ms.)"""
    return [[int(r["lines"]), round(r["cycles_per_load"], 1), round(r["bytes_requested"] / (r["cycles_max"] * ns_per_cycle), 2)]
            for r in load(path)]


def claims_v3(root):
    """The three-card check's TensorLoad sweeps and energy runs, per card (see --claims-v3 in the docstring)."""
    raw = os.path.join(root, "raw")
    cards = [c for c in V3_CARD_ORDER if os.path.isdir(os.path.join(raw, c, "lat"))]
    cards += sorted(c for c in os.listdir(raw) if os.path.isdir(os.path.join(raw, c, "lat")) and c not in cards
                    and c != "aifoundry1-c0")  # card 0 is outside the campaign (amendment A4)
    out = {"source": "docs/reports/data/2026-09-25-claims-v3: raw/<card>/lat/p*/sp (V3-LAT), results/ablb.runs.json (V3-ABL-B) "
                     "and results/abla.runs.json (V3-ABL-A)",
           "cards": cards, "tload": {}, "energy": {}, "operands": {}}

    def col(vals):
        vals = [x for x in vals if x is not None]
        return {"mean": statistics.mean(vals), "min": min(vals), "max": max(vals)} if vals else None

    def at_die(rs, metric, leak, ref):
        """The mean of a run's metric at the die temperature of its launch (note C2, revised), both ends: the die at the
        sensor's whole-degree reading, and V3_C2_STEP_C above it."""
        return [statistics.mean(r[metric] + leak * (r["t_launch"] + s - ref) for r in rs) for s in (0.0, V3_C2_STEP_C)]
    ns = 1000.0 / 600  # V3-LAT keeps only launches at 600 MHz (its clock rule)
    for c in cards:
        passes = []
        for d in sorted(glob.glob(os.path.join(raw, c, "lat", "p*"))):
            try:
                ok = json.load(open(os.path.join(d, "block.json"))).get("status") == "ok"
            except (OSError, ValueError):
                ok = False
            if ok and os.path.isdir(os.path.join(d, "sp")):
                passes.append(os.path.join(d, "sp"))
        tl = {}
        for w in ["dram", "l2", "scp"]:
            for scope in ["one", "all"]:
                per = [{r[0]: r for r in tload_rows(os.path.join(p, f"tload-{w}-{scope}.jsonl"), ns)} for p in passes]
                lines = sorted({l for q in per for l in q}, reverse=True)
                tl[f"{w}-{scope}"] = [[l, round(statistics.median(q[l][1] for q in per if l in q), 1),
                                       round(statistics.median(q[l][2] for q in per if l in q), 2),
                                       [q[l][1] for q in per if l in q]] for l in lines]
        out["tload"][c] = {"passes": len(passes), "rows": tl}
    runs_path = os.path.join(root, "results", "ablb.runs.json")
    if os.path.exists(runs_path):
        RJ = json.load(open(runs_path))
        R, C2P = RJ["runs"], RJ.get("params_by_card", {})
        for c in cards:
            rs = [r for r in R.get(c, []) if r.get("kept") and r.get("kept_busy", True) and r.get("pass") in V3_BLOCKS]
            if not rs:
                continue
            by = {}
            for r in rs:
                by.setdefault(r["config"], []).append(r)
            cf = {}
            for name, v in sorted(by.items()):
                rated = [r for r in v if r.get("per_s")]
                x = {"n": len(v), "unit": v[0].get("unit"), "above_idle_w": col([r["dyn"] for r in v]),
                     "per_s": col([r["per_s"] for r in rated]),
                     "j_per_unit_above_idle": col([r["dyn"] / r["per_s"] for r in rated]),
                     "j_per_unit": col([r["p80"] / r["per_s"] for r in rated]),
                     "cycles_per_op": col([r.get("cycles_per_op") for r in v])}
                if x["unit"] == "MAC":
                    x["pj_slot"] = col([r["dyn"] / r["per_s"] * 1e12 for r in rated])
                tiled = [r for r in v if r.get("nnz_a") is not None]
                if tiled:  # the A tile differs between blocks (each block draws with its own seed): keep every draw
                    rows_on = lambda r: bin(int(r.get("row_mask", "0xffff"), 16)).count("1")
                    x["nnz_a_runs"] = [r["nnz_a"] for r in tiled]
                    x["a_elems"], x["row_mask"] = tiled[0]["a_elems"], tiled[0].get("row_mask", "0xffff")
                    x["rows_on"] = rows_on(tiled[0])
                    # multiplies with a nonzero A element in an enabled row, the reducer's x (ABLB-3c)
                    x["frac"] = col([r["nnz_a"] / r["a_elems"] * rows_on(r) / 16 for r in tiled])
                if c in C2P:  # at the die temperature of the launches (note C2, revised), both ends
                    x["at_die_w"] = at_die(v, "dyn", C2P[c]["leak"], C2P[c]["launch"])
                cf[name] = x
            out["energy"][c] = {"blocks": sorted({r["pass"] for r in rs}), "idle_w": statistics.mean(r["p_before"] for r in rs),
                                "launch_c": statistics.mean(r["start_temp"] for r in rs), "configs": cf}
            if c in C2P:  # the check's note C2 (revised): how far the registered values read high, both ends
                leak, ref = C2P[c]["leak"], C2P[c]["launch"]
                off = statistics.mean(leak * (r["t_launch"] - ref) for r in rs)
                out["energy"][c]["c2_reads_high_w"] = [-off, -(off + leak * V3_C2_STEP_C)]
    # V3-ABL-A: the same loop on all zeros, all ones and random normal data, reduced as the energy manual's section 3.2
    abla_path = os.path.join(root, "results", "abla.runs.json")
    if os.path.exists(abla_path):
        AJ = json.load(open(abla_path))
        used, C2A = AJ.get("passes_used", {}), AJ.get("params_by_card", {})
        for c in cards:
            rs = [r for r in AJ["runs"].get(c, []) if r.get("kept") and r.get("pass") in used.get(c, [])
                  and r["config"] in dict(V3_OPERANDS)]
            if not rs:
                continue
            pats = {}
            for cfg, key in V3_OPERANDS:
                v = [r for r in rs if r["config"] == cfg]
                if not v:
                    continue
                pats[key] = {"config": cfg, "n": len(v), "above_idle_w": col([r["switching"] for r in v]),
                             "pj_mac": col([r["switching"] / r["per_s"] * 1e12 for r in v]),
                             "per_s": statistics.mean(r["per_s"] for r in v), "idle_w": statistics.mean(r["p_before"] for r in v),
                             "launch_c": statistics.mean(r["t_launch"] for r in v)}
                if c in C2A:
                    pats[key]["at_die_w"] = at_die(v, "switching", C2A[c]["leak"], C2A[c]["launch"])
            out["operands"][c] = {"passes": sorted({r["pass"] for r in rs}), "patterns": pats}
            if c in C2A:
                leak, ref = C2A[c]["leak"], C2A[c]["launch"]
                off = statistics.mean(leak * (r["t_launch"] - ref) for r in rs)
                out["operands"][c]["c2_reads_high_w"] = [-off, -(off + leak * V3_C2_STEP_C)]
    return out


def page_summary(data):
    """Print the power and energy values the page's text quotes, as it rounds them: the three-card check's
    (v3.energy, V3-ABL-B, E39; v3.operands, V3-ABL-A, E38) and the first run's, which the page keeps as one note."""
    v3, en = data.get("v3") or {}, data.get("energy") or {}
    E, O = v3.get("energy") or {}, v3.get("operands") or {}
    cards = [c for c in v3.get("cards", []) if c in E]
    span = lambda xs, dp, pct=False: (lambda a, b: a if a == b else f"{a}-{b}")(
        *(f"{(100 * x if pct else x):.{dp}f}" for x in (min(xs), max(xs))))
    save = lambda z, d: 1 - z / d
    reads = lambda r: ("from " if (r[0] >= 0) != (r[1] >= 0) else "") + f"{r[0]:+.2f} to {r[1]:+.2f} W (+ = high)"
    print("\nthe values the page's text quotes (registered values; 'at the die' = at the die temperature of the launches,"
          " note C2's two readings):")
    if cards:
        print("  this page's TensorFMA loop, operands -3..3 (V3-ABL-B, E39):")
        rate, sv, svd = [], [], []
        for c in cards:
            cf = E[c]["configs"]
            d, z = cf["fma-dense"], cf["fma-zero"]
            s = save(z["above_idle_w"]["mean"], d["above_idle_w"]["mean"])
            sd = [save(zz, dd) for zz, dd in zip(z.get("at_die_w", [0, 0]), d.get("at_die_w", [1, 1]))]
            sv.append(s)
            svd += sd
            rate += [cf[k]["per_s"][m] / MAC_PER_FP32_OP for k in cf if k.startswith("fma-") and cf[k].get("per_s")
                     for m in ("min", "max")]
            print(f"    {c}: dense +{d['above_idle_w']['mean']:.1f} -> all-zero A +{z['above_idle_w']['mean']:.1f} W, "
                  f"{100 * s:.0f}% saved ({span(sd, 0, True)}% at the die); rows masked +{cf['fma-rowmask']['above_idle_w']['mean']:.1f} W, "
                  f"half zeros +{cf['fma-50']['above_idle_w']['mean']:.1f} W; the integer loop +{cf['spin']['above_idle_w']['mean']:.1f} "
                  f"of the zeros' {z['above_idle_w']['mean']:.1f} W; pJ per multiply slot dense {d['pj_slot']['mean']:.1f}, "
                  f"all-zero A {z['pj_slot']['mean']:.1f}; idle {E[c]['idle_w']:.1f} W; the values read {reads(E[c]['c2_reads_high_w'])}")
        print(f"    across the cards: {span(sv, 0, True)}% saved ({span(svd, 0, True)}% at the die); dense "
              f"{span([E[c]['configs']['fma-dense']['above_idle_w']['mean'] for c in cards], 1)} W, all-zero A "
              f"{span([E[c]['configs']['fma-zero']['above_idle_w']['mean'] for c in cards], 1)} W; pJ per slot dense "
              f"{span([E[c]['configs']['fma-dense']['pj_slot']['mean'] for c in cards], 1)}, all-zero A "
              f"{span([E[c]['configs']['fma-zero']['pj_slot']['mean'] for c in cards], 1)}; every run "
              f"{min(rate) / 1e9:.2f}-{max(rate) / 1e9:.2f} x 10^9 ops/s")
        for c in cards:
            cf = E[c]["configs"]
            d0, d9 = cf["gemv-dense-0"]["above_idle_w"]["mean"], cf["gemv-dense-90"]["above_idle_w"]["mean"]
            uj = lambda k, f: cf[k][f]["mean"] * 1e6
            print(f"    {c} layer: above idle {uj('gemv-skip-0', 'j_per_unit_above_idle'):.1f} / {uj('gemv-skip-90', 'j_per_unit_above_idle'):.1f} / "
                  f"{uj('gemv-skip-99', 'j_per_unit_above_idle'):.1f} uJ, board {uj('gemv-skip-0', 'j_per_unit'):.0f} / "
                  f"{uj('gemv-skip-90', 'j_per_unit'):.0f} / {uj('gemv-skip-99', 'j_per_unit'):.0f} uJ at 0 / 90 / 99% zeros; every row "
                  f"loaded, 0 -> 90% zeros {d0:.1f} -> {d9:.1f} W ({100 * save(d9, d0):.0f}% less)")
    oc = [c for c in v3.get("cards", []) if c in O]
    if oc:
        print("  the same loop on other operand values, A and B alike (V3-ABL-A, E38):")
        P = lambda c, k, f="above_idle_w": O[c]["patterns"][k][f]["mean"]
        for c in oc:
            pt = O[c]["patterns"]
            at = {k: pt[k]["at_die_w"] for k in pt if "at_die_w" in pt[k]}
            print(f"    {c}: zeros +{P(c, 'zeros'):.1f} W ({P(c, 'zeros', 'pj_mac'):.2f} pJ per multiply-add), ones +{P(c, 'ones'):.1f} "
                  f"({P(c, 'ones', 'pj_mac'):.2f}), random normal +{P(c, 'randn'):.1f} ({P(c, 'randn', 'pj_mac'):.2f}); "
                  f"{pt['zeros']['n']}, {pt['ones']['n']}, {pt['randn']['n']} runs, launched at {pt['zeros']['launch_c']:.0f} C; zeros save "
                  f"{100 * save(P(c, 'zeros'), P(c, 'ones')):.1f}% against ones, {100 * save(P(c, 'zeros'), P(c, 'randn')):.1f}% against "
                  f"random normal" + (f" ({span([save(a, b) for a, b in zip(at['zeros'], at['ones'])], 1, True)}% and "
                                      f"{span([save(a, b) for a, b in zip(at['zeros'], at['randn'])], 1, True)}% at the die)" if at else "")
                  + (f"; the values read {reads(O[c]['c2_reads_high_w'])}" if "c2_reads_high_w" in O[c] else ""))
        rng = lambda k, f="above_idle_w", dp=1: span([P(c, k, f) for c in oc], dp)
        atd = lambda k: [save(a, b) for c in oc for a, b in zip(O[c]["patterns"]["zeros"].get("at_die_w", []),
                                                                  O[c]["patterns"][k].get("at_die_w", []))]
        print(f"    across the cards: zeros {rng('zeros')} W ({rng('zeros', 'pj_mac', 2)} pJ), ones {rng('ones')} W "
              f"({rng('ones', 'pj_mac', 2)}), random normal {rng('randn')} W ({rng('randn', 'pj_mac', 2)}); zeros save "
              f"{span([save(P(c, 'zeros'), P(c, 'ones')) for c in oc], 0, True)}% against ones and "
              f"{span([save(P(c, 'zeros'), P(c, 'randn')) for c in oc], 0, True)}% against random normal "
              f"({span(atd('ones'), 0, True)}% and {span(atd('randn'), 0, True)}% at the die)")
    C = en.get("configs") or {}
    if C:
        a = lambda k: C[k]["above_idle_w"]["mean"]
        uj = lambda k: C[k]["j_per_unit_above_idle"]["mean"] * 1e6
        print(f"  first run (18 Sep, this card, runs {', '.join(en['runs'])}; idle {min(en['idle_w']):.1f}-{max(en['idle_w']):.1f} W): "
              f"dense +{a('fma-dense'):.1f} -> all-zero A +{a('fma-zero'):.1f} W ({100 * save(a('fma-zero'), a('fma-dense')):.0f}% saved), "
              f"{C['fma-dense']['pj_slot']['mean']:.1f} pJ per multiply slot dense; rows masked +{a('fma-rowmask'):.1f} W; the integer loop "
              f"+{a('spin'):.1f} W; layer above idle {uj('gemv-skip-0'):.0f} / {uj('gemv-skip-90'):.0f} / {uj('gemv-skip-99'):.1f} uJ at "
              f"0 / 90 / 99% zeros; gating with the masked kernel at 0%: {a('gemv-skip-0'):.1f} -> {a('gemv-dense-90'):.1f} W "
              f"({100 * save(a('gemv-dense-90'), a('gemv-skip-0')):.0f}% less)")


def pareto_eff(alpha, n):
    """Lane efficiency E[k] / E[max of n] for continuous Pareto(alpha, xmin = 1) (research note, verified by MC)."""
    if alpha <= 1:
        return 0.0
    return (alpha / (alpha - 1)) / (math.gamma(n + 1) * math.gamma(1 - 1 / alpha) / math.gamma(n + 1 - 1 / alpha))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("data_dir")
    p.add_argument("--embed", metavar="REPORT_HTML")
    p.add_argument("--claims-v3", metavar="DIR", default=CLAIMS_V3,
                   help="the three-card check's data directory (adds v3; default %(default)s when it exists; 'none' skips it)")
    args = p.parse_args()
    d = args.data_dir
    mhz, mhz_values = clock_mhz(d)
    ns_per_cycle = 1000.0 / mhz
    data = {"clock_mhz": mhz, "clock_values": mhz_values}
    bad = []
    for f in glob.glob(os.path.join(d, "*.jsonl")) + glob.glob(os.path.join(d, "diverge", "*.jsonl")):
        bad += [os.path.basename(f) for r in load(f) if r.get("ok") is False]
    if bad:
        print("WARNING: failed lines in", sorted(set(bad)))
    print(f"minion clock: median {mhz:.0f} MHz, values seen {mhz_values}")

    # ---- TensorFMA: cycles per op against the fraction of zeros
    fma = {}
    for name in ["fp32-elem", "fp32-col", "fp32-row", "fp32-elem-tenb", "fp16-elem", "fp16-pair", "int8-elem",
                 "fp32-elem-all"]:
        rows = load(os.path.join(d, f"fma-{name}.jsonl"))
        fma[name] = [[r["sparsity"], round(r["cycles_per_op"], 2), r["result"], r["nnz_a"], r["a_elems"]] for r in rows]
    fma["b-sparse"] = [[r["b_sparsity"], round(r["cycles_per_op"], 2), r["result"]]
                       for n in ["fp32-bsparse", "fp32-bsparse90"] for r in load(os.path.join(d, f"fma-{n}.jsonl"))]
    fma["rowmask"] = []
    for m in ["0xFFFF", "0x00FF", "0x000F", "0x0001", "0x0000"]:
        for r in load(os.path.join(d, f"fma-fp32-rowmask-{m}.jsonl")):
            fma["rowmask"].append([bin(int(m, 16)).count("1"), round(r["cycles_per_op"], 2), r["result"]])
    data["fma"] = fma
    print("\nTensorFMA cycles per op (A tile 16x16, B 16x16):")
    for name, rows in fma.items():
        if rows:
            cyc = [r[1] for r in rows]
            print(f"  {name:15s} {min(cyc):7.1f}-{max(cyc):7.1f}  over {len(rows)} points  results {sorted(set(r[2] for r in rows))}")

    # ---- TensorLoad under a mask
    tload = {}
    for w in ["dram", "l2", "scp"]:
        for scope in ["one", "all"]:
            # Bytes the mask let through over the slowest minion's loop time at the logged clock.
            tload[f"{w}-{scope}"] = tload_rows(os.path.join(d, f"tload-{w}-{scope}.jsonl"), ns_per_cycle)
    data["tload"] = tload
    print("\nTensorLoad (16 lines max) cycles per load and GB/s on chip by lines requested:")
    for k, rows in tload.items():
        print(f"  {k:9s} " + "  ".join(f"{l}:{c:.1f}c/{g:.1f}GB/s" for l, c, g in rows))

    # ---- The batch-1 layer (time of each 16-row block's slowest minion, mean over the 64 blocks)
    gemv = {}
    for name in ["dense", "masked", "skip", "skip-oneshire", "tree-dense", "tree-masked", "tree-skip",
                 "tree-oneshire"]:
        rows = load(os.path.join(d, f"gemv-{name}.jsonl"))
        gemv[name] = [[r["sparsity"], round(r["cycles_per_layer_mean"], 1), round(r["cycles_per_layer_mean"] * ns_per_cycle / 1000, 3),
                       round(r["slices_per_minion"], 2), round(r["lines_per_minion"], 1), r["ok"]] for r in rows]
    data["gemv"] = gemv
    print(f"\nlayer y = W x, 1024 x 4096 fp32 (cycles, us at {mhz:.0f} MHz):")
    for k, rows in gemv.items():
        if rows:
            print(f"  {k:14s} " + "  ".join(f"{s:.2f}:{c:.0f}c/{u:.2f}us" for s, c, u, *_ in rows))

    # ---- Divergence
    div = {"alpha": [], "static": [], "refill": [], "scalar": [], "simt8": [], "simt32": [], "model8": [], "model32": []}
    for a in ["0", "3", "2", "1.5", "1.2"]:
        rs = {v: load(os.path.join(d, "diverge", f"diverge-{v}-a{a}.jsonl")) for v in ["static", "refill", "scalar"]}
        if not all(rs.values()):
            continue
        alpha = float(a)
        div["alpha"].append(alpha)
        for v, rows in rs.items():
            r = rows[0]
            fma_mean = 8 * r["useful_lane_iters"] / r["minions"] / r["cycles_mean"]
            fma_max = 8 * r["useful_lane_iters"] / r["minions"] / r["cycles_max"]
            div[v].append({"lane_eff": round(r["lane_efficiency"], 4), "fma_per_cycle_mean": round(fma_mean, 3),
                           "fma_per_cycle_makespan": round(fma_max, 3), "mean_k": r["mean_k"], "max_k": r["max_k"],
                           "tfma_chip_mean": round(fma_mean * r["minions"] * mhz / 1e6, 3),
                           "cycles_mean": r["cycles_mean"], "cycles_max": r["cycles_max"], "items": r["items"],
                           "harts": r["harts"], "chunk": r["chunk"]})
        div["simt8"].append(rs["static"][0]["simt8_efficiency"])
        div["simt32"].append(rs["static"][0]["simt32_efficiency"])
        div["model8"].append(round(pareto_eff(alpha, 8), 4) if alpha > 0 else 1.0)
        div["model32"].append(round(pareto_eff(alpha, 32), 4) if alpha > 0 else 1.0)
    data["diverge"] = div
    if div["alpha"]:
        print("\ndivergence (mean k 64, capped at 16384; lane efficiency, FMA/cycle/minion in steady state):")
        for i, a in enumerate(div["alpha"]):
            print(f"  alpha {a:>4}: static {div['static'][i]['lane_eff']:.3f} ({div['static'][i]['fma_per_cycle_mean']:.2f})"
                  f"  refill {div['refill'][i]['lane_eff']:.3f} ({div['refill'][i]['fma_per_cycle_mean']:.2f})"
                  f"  scalar ({div['scalar'][i]['fma_per_cycle_mean']:.2f})  simt8 {div['simt8'][i]:.3f}"
                  f"  simt32 {div['simt32'][i]:.3f}  [continuous model 8/32: {div['model8'][i]:.3f}/{div['model32'][i]:.3f}]")

    # ---- Energy
    energy = []
    for ef in sorted(glob.glob(os.path.join(d, "energy-*", "results.json"))):
        energy.append({"run": os.path.basename(os.path.dirname(ef)), **json.load(open(ef))})
    summary = {}
    for e in energy:
        for name, r in e["results"].items():
            summary.setdefault(name, []).append(r)
    en = {"runs": [e["run"] for e in energy], "idle_w": [e["idle_w"] for e in energy], "configs": {}}
    # The TensorFMA configurations' A tile as drawn (nonzero elements, size) and tensor_mask, from the host's records.
    tile = {}
    for rf in sorted(glob.glob(os.path.join(d, "energy-*", "runs.jsonl"))):
        for line in open(rf):
            r = json.loads(line)
            if r.get("nnz_a") is not None:
                t = (r["nnz_a"], r["a_elems"], r.get("row_mask", "0xffff"))
                if tile.setdefault(r["config"], t) != t:
                    raise SystemExit(f"{rf}: {r['config']} has A tiles of different sparsity: {tile[r['config']]} and {t}")
    for name, rs in summary.items():
        def col(key):
            vals = [r[key] for r in rs if r.get(key) is not None]
            return {"mean": statistics.mean(vals), "min": min(vals), "max": max(vals)} if vals else None
        en["configs"][name] = {"what": rs[0]["what"], "unit": rs[0]["unit"], "mean_w": col("mean_w"),
                               "above_idle_w": col("above_idle_w"), "above_spin_w": col("above_spin_w"),
                               "per_s": col("per_s"), "mean_mhz": col("mean_mhz"),
                               "j_per_unit_above_idle": col("j_per_unit_above_idle"), "j_per_unit": col("j_per_unit"),
                               "pj_slot": col("pj_per_fma_slot_above_idle"),
                               "pj_useful": col("pj_per_useful_fma_above_idle"),
                               "cycles_per_op": col("cycles_per_op"), "cycles_per_layer": col("cycles_per_layer")}
        if name in tile:
            c = en["configs"][name]
            c["nnz_a"], c["a_elems"], c["row_mask"] = tile[name]
            c["rows_on"] = bin(int(c["row_mask"], 16)).count("1")  # of 16 rows of C
    data["energy"] = en
    if energy:
        print(f"\nenergy: runs {en['runs']}, idle {[round(w, 2) for w in en['idle_w']]} W")
        for name, c in en["configs"].items():
            extra = ""
            if c["pj_slot"]:
                extra = f"  {c['pj_slot']['mean']:.3f} pJ/FMA slot"
                if c["pj_useful"]:
                    extra += f", {c['pj_useful']['mean']:.3f} pJ/useful FMA"
            elif c["j_per_unit_above_idle"]:
                extra = f"  {c['j_per_unit_above_idle']['mean'] * 1e6:.3f} uJ/{c['unit']} above idle"
            print(f"  {name:14s} {c['mean_w']['mean']:6.2f} W (+{c['above_idle_w']['mean']:5.2f}, "
                  f"{c['above_idle_w']['min']:.2f}-{c['above_idle_w']['max']:.2f}){extra}")

    if args.claims_v3 != "none" and os.path.isdir(args.claims_v3):
        v3 = claims_v3(args.claims_v3)
        data["v3"] = v3
        print(f"\nthree-card check ({v3['source']}):")
        for c in v3["cards"]:
            t = v3["tload"][c]["rows"]
            print(f"  {c}: {v3['tload'][c]['passes']} TensorLoad passes; one minion L2 " +
                  "  ".join(f"{l}:{cy:.1f}c" for l, cy, g, _ in t["l2-one"]) + "; DRAM " +
                  "  ".join(f"{l}:{cy:.1f}c {pp}" for l, cy, g, pp in t["dram-one"] if l in (16, 1)))
            e = v3["energy"].get(c)
            if e:
                cf = e["configs"]
                print(f"    energy blocks {e['blocks']}, idle {e['idle_w']:.2f} W, launch {e['launch_c']:.1f} C; dense "
                      f"+{cf['fma-dense']['above_idle_w']['mean']:.2f} W, zeros +{cf['fma-zero']['above_idle_w']['mean']:.2f} W, "
                      f"layer board uJ " + ", ".join(f"{k[10:]}% {cf[k]['j_per_unit']['mean'] * 1e6:.0f}" for k in
                                                   ("gemv-skip-0", "gemv-skip-90", "gemv-skip-99")))
    page_summary(data)
    if args.embed:
        html = open(args.embed).read()
        pat = re.compile(r'(<script type="application/json" id="sparsity-data">)(.*?)(</script>)', re.S)
        if len(pat.findall(html)) != 1:
            raise SystemExit(f"{args.embed}: expected exactly one sparsity-data script tag")
        html = pat.sub(lambda m: m.group(1) + json.dumps(data, separators=(",", ":")) + m.group(3), html)
        open(args.embed, "w").write(html)
        print(f"embedded report data into {args.embed}")


if __name__ == "__main__":
    main()
