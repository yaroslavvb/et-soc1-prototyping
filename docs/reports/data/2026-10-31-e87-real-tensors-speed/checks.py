#!/usr/bin/env python3
"""E87: post-hoc checks, written after the data and LABELLED -- none is a registered rule or changes a verdict.
Every number is read from results.json (reduce_e87.py's output), E87's predictions.json and E83's/E80's results.json.

    python3 checks.py > checks.txt

K1  the like-with-like ratios pass by pass: each tile's ratio (c_tile - c_zeros) / (c_ref - c_zeros) from the pass-1
    bursts alone and from the pass-2 bursts alone (the two rounds run in the same order for every kind, so each round
    is a self-contained same-session comparison), its half-spread, and the format means with the between-tile spread.
K2  the anchors' switching term c in E80, E83 and E87 (how stable c is across sessions on this card).
K3  the idle resets: which runs carry one, and the burst cells with and without the reset samples (A1's view).
K4  the heat path: E87's die line against E80's and E83's, and the same-session int8 real-vs-full sustained clocks.
"""
import json
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
R = json.load(open(os.path.join(HERE, "results.json")))
P = json.load(open(os.path.join(ROOT, "tools/claims-v3/kspeed/e87/predictions.json")))
R83 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e83-kinds-speed-rest/results.json")))
C = R["cells"]
runs = R["runs"]


def by_pass(kind):
    out = {}
    for m in runs:
        if m["block"] == "BURST" and m["kind"] == kind:
            out[m["rep"] if "rep" in m else int(m["run"].rsplit("-r", 1)[1])] = m["c_w"]
    return out


print("K1  like-with-like ratios, pass by pass (c from each round's bursts alone)")
fmt_means = {}
for t in ("fp32", "fp16", "int8"):
    ref = "fp32/randn" if t == "fp32" else ("fp16/randn" if t == "fp16" else "int8/full")
    zp, rp = by_pass(f"{t}/zeros"), by_pass(ref)
    per_pass = {1: [], 2: []}
    for n in ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk"):
        k = f"{t}/{n}"
        tp = by_pass(k)
        rs = {}
        for p in (1, 2):
            if None not in (tp.get(p), rp.get(p), zp.get(p)):
                rs[p] = (tp[p] - zp[p]) / (rp[p] - zp[p])
                per_pass[p].append(rs[p])
        both = R["posthoc"]["like_with_like_ratios"].get(k)
        hs = abs(rs[1] - rs[2]) / 2 if len(rs) == 2 else None
        print(f"    {k:18s} pass1 {rs.get(1, float('nan')):.4f}  pass2 {rs.get(2, float('nan')):.4f}  "
              f"half-spread {hs:.4f}  cell {both}  predicted {P['tiles'][k]['like_with_like']['ratio_to_ref_measured']}")
    m1, m2 = st.mean(per_pass[1]), st.mean(per_pass[2])
    cell = [R["posthoc"]["like_with_like_ratios"][f"{t}/{n}"] for n in ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk")]
    sd = st.stdev(cell)
    fmt_means[t] = (st.mean(cell), sd)
    print(f"    {t} mean over the three tiles: {st.mean(cell):.4f} (pass-1 rounds {m1:.4f}, pass-2 rounds {m2:.4f}); "
          f"between-tile sd {sd:.4f}, so the mean's standard error {sd / math.sqrt(3):.4f}; "
          f"t against 1.000 = {(1 - st.mean(cell)) / (sd / math.sqrt(3)):.2f} on 2 df")
    print(f"      c per pass: ref {rp}  zeros {zp}")
print()
print("K2  the anchors' switching term c (W, E64's basis) in three sessions on aifoundry2")
for k, e in P["anchors"].items():
    e80 = (e.get("e80") or {}).get("e80_c_w")
    e83 = R83["cells"][k]["c_w"]
    print(f"    {k:12s} E80 {e80}  E83 {e83}  E87 {C[k]['c_w']}  (E87 passes {C[k]['c_w_runs']})")
print()
print("K3  idle resets (A1's detector, posthoc_idle.flags)")
for m in runs:
    a1 = m.get("a1") or {}
    if a1.get("n_dip"):
        print(f"    {m['run']:36s} dips {a1['n_dip']}  burst {m.get('burst_mhz')}  without {a1.get('burst_mhz_without')}  "
              f"sus {m.get('sus_mhz_mean')}  without {a1.get('sus_mhz_without')}")
print(f"    totals {R['posthoc']['idle_resets']}")
print()
print("K4  the heat path")
dl87, dl83 = R["posthoc"]["die_line_e87"], R83["posthoc"]["die_line_e83"]
print(f"    E87 die line {dl87['a_c']} + {dl87['k_c_per_w']} C/W (n {dl87['n']}, rms {dl87['rms_c']} C), "
      f"shift at E80's slope {dl87['shift_c_at_e80_slope']:+} C; E83's {dl83['shift_c_at_e80_slope']:+} C; "
      f"so E87 runs {dl87['shift_c_at_e80_slope'] - dl83['shift_c_at_e80_slope']:+.3f} C warmer than E83 at E80's slope")
print(f"    a-adj E87: W*_adj {R['posthoc']['a_adj_e87']['W_star_adj_w']} W (registered 49.75; E83's 49.724)")
i8 = [C[f"int8/{n}"] for n in ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk")]
print(f"    int8 sustained, same session: real {[c['sus_mhz'] for c in i8]} ({[c['sus_limit'] for c in i8]}), "
      f"board W {[c['sus_w'] for c in i8]}, die {[c['sus_die'] for c in i8]}; int8 full {C['int8/full']['sus_mhz']} "
      f"({C['int8/full']['sus_limit']}), {C['int8/full']['sus_w']} W, {C['int8/full']['sus_die']} C")
print(f"    int8 full sustained in three sessions: E80 {P['anchors']['int8/full']['e80']['e80_sus_mhz']} "
      f"{P['anchors']['int8/full']['e80']['e80_sus_mhz_runs']}, E83 {R83['cells']['int8/full']['sus_mhz']}, "
      f"E87 {C['int8/full']['sus_mhz']}")
