#!/usr/bin/env python3
"""Q142(m): the README's tables, mechanically from heldout-m10.json (no fit, no new number).

    python3 -B tables_m10.py [<dir holding heldout-m10.json and m10.json>] > tables-m10.md
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1] if len(sys.argv) > 1 else HERE
h = json.load(open(os.path.join(D, "heldout-m10.json")))
m10 = json.load(open(os.path.join(D, "m10.json")))
P = print


def f(x, d=3):
    return "—" if x is None else f"{x:.{d}f}"


def rb(s):
    return f"{f(s['rms_w'])} ({s['bias_meas_minus_pred_w']:+.3f})" if s and s.get("n") else "—"


def ci(b):
    return "—" if not b else f"{b['d_rms_w']:+.4f} [{b['lo95']:+.4f}, {b['hi95']:+.4f}]"


P("## Power at 600 MHz, held out (leave one kind out): rms (bias, measured − predicted), W of D\n")
for fam in ("float", "int8"):
    pf = h["power"][fam]
    vs = list(pf["variants"])
    P(f"**{fam}** ({pf['n_rows']} rows, {pf['n_kinds']} kinds; frozen variant **{pf['frozen_variant']}**)\n")
    P("| rows | cell | " + " | ".join(vs) + " | M9 as frozen |")
    P("|---|---|" + "---:|" * (len(vs) + 1))
    for lab in pf["M9_as_frozen"]:
        for cell in pf["M9_as_frozen"][lab]:
            if cell != "all" and not cell.startswith("card") and "|" not in cell:
                continue
            P(f"| {lab} | {cell} | " + " | ".join(rb(pf["variants"][v][lab].get(cell)) for v in vs) + f" | {rb(pf['M9_as_frozen'][lab].get(cell))} |")
    P("")
    P("| test | pooled d rms [95%] | aifoundry3 | card 1 | S class | pool 7 against M9 as frozen |")
    P("|---|---|---|---|---|---|")
    for v, t in pf["paired_bootstrap"].items():
        if v == "B":
            P(f"| B (M9's form refitted) | — | — | — | — | {ci(t.get('pool7_vs_M9_as_frozen'))} |")
            continue
        P(f"| {v} − B | {ci(t['pooled'])} | {ci(t['per_card']['a3'])} | {ci(t['per_card']['c1'])} | {ci(t.get('S_class'))} | "
          f"{ci(t.get('pool7_vs_M9_as_frozen'))} |")
    P(f"\nentry: {pf['entry']}; band k {pf['band']['k']:.3f}, {pf['band']['coverage_all_rows'][0]} of {pf['band']['coverage_all_rows'][1]} rows inside\n")
P("## Session scales s (floats), all rows, the frozen variant's rule\n")
ss = h["power"]["float"]["session_scales_all_rows"]
P("| session | s | anchors |")
P("|---|---:|---:|")
for s, v in sorted(ss.items(), key=lambda kv: (kv[0].split("|")[1], int(kv[0].split("|")[0][1:]))):
    P(f"| {s} | {v:.5f} | {h['power']['float']['session_scale_anchor_counts'].get(s, 0)} |")
sa = h["power"]["int8"].get("session_scales_term_a_all_rows") or {}
P("\nint8, term a (not entered): " + ", ".join(f"{k} {v:.4f}" for k, v in sorted(sa.items())))
P("\n## Term b: the S class's counts\n")
P("| tile | counted to N | N used | e(N) W | met | 3pt − N W | source |")
P("|---|---:|---:|---:|---|---:|---|")
for n, r in h["S_recount"].items():
    eN = r["by_N"][str(r["N"])]["e_w"] if r["N"] else None
    P(f"| `{n}` | {r['N_counted']} | {r['N']} | {f(eN)} | {r['met']} | {r.get('three_point_minus_N_w', 0):+.3f} | {r['source']} |")
c1 = h["heat_c1"]
P("\n## Heat (c1): the 4.5 s window rise, held out, rms (bias), °C\n")
P("| rows | M7's law as frozen | base (M7's form refitted) | with the session heat scale |")
P("|---|---:|---:|---:|")
for cell in ("all", "aifoundry3", "aifoundry1-c1"):
    g = lambda k: c1[k][cell]  # noqa: E731
    P(f"| {cell} ({g('base_refit_loko')['n']}) | {f(g('M7_law_as_frozen')['rms_c'])} ({g('M7_law_as_frozen')['bias_c']:+.3f}) | "
      f"{f(g('base_refit_loko')['rms_c'])} ({g('base_refit_loko')['bias_c']:+.3f}) | {f(g('with_session_heat_scale_loko')['rms_c'])} "
      f"({g('with_session_heat_scale_loko')['bias_c']:+.3f}) |")
P(f"\npaired bootstrap (session scale − base): pooled {ci(c1['paired_bootstrap_sessscale_minus_base'])}; "
  + "; ".join(f"{c} {ci(v)}" for c, v in c1["per_card"].items()) + f"; enters {c1['enters']}")
P(f"\nrefitted coefficients {c1['refit_coef_all_rows']} against M7's {c1['M7_coef']}")
e2 = c1.get("end_to_end_base_law_at_M10_heldout_D")
if e2:
    P(f"\nend to end (the base law at M10's held-out D, the {e2['n']} heat rows that are power rows): rms {e2['rms_c']} °C "
      f"(bias {e2['bias_c']:+.3f}; by card {e2['by_card']}); the base law at the measured S on the same rows {e2['base_law_on_the_same_rows_rms_c']} °C")
P(f"\nsession heat scales (all rows): " + ", ".join(f"{k} {v:.3f}" for k, v in sorted(c1['session_heat_scales_all_rows'].items())))
c2, ee, d = h["heat_c2_card0_burst"], h["kappa_e_card0"], h["heat_d_chain_gain"]
P(f"\n## (c2) card 0's burst rise: frozen law k {c2['k_frozen_c_per_w']:.5f}: rms {c2['frozen_law']['rms_c']} (bias {c2['frozen_law']['bias_c']:+.3f}) °C; "
  f"leave one tile out k {c2['k_loto_range']}: rms {c2['loto']['rms_c']} ({c2['loto']['bias_c']:+.3f}); all tiles k {c2['k_all_tiles']}; "
  f"d {ci(c2['paired_bootstrap'])}; enters {c2['enters']}")
P(f"\n## (e) card 0's kappa: kappa0 {ee['kappa0']}: board rms {ee['kappa0_board']['rms_w']} ({ee['kappa0_board']['bias_w']:+.3f}) W; "
  f"leave one tile out {ee['kappa_loto_by_family']}: {ee['loto_kappa_board']['rms_w']} ({ee['loto_kappa_board']['bias_w']:+.3f}); "
  f"all tiles {ee['kappa_all_tiles_by_family']}; d {ci(ee['paired_bootstrap'])}; enters {ee['enters']}")
P("\n## (d) the chain's gain, leave one session out\n")
P("| variant | gamma (all holds) | large rises (n) without → with, rms °C | d [95%] | by card kind | all fitted holds | passes |")
P("|---|---|---|---|---|---|---|")
for v, r in d["variants"].items():
    P(f"| {v} | {r['gamma_all_holds']} | {r['large_rise_n']}: {r['large_rise_without_rms_c']} → {r['large_rise_with_rms_c']} | "
      f"{ci(r['paired_bootstrap_large_rise'])} | {r['d_rms_by_card_kind_c']} | {r['all_fitted_without_rms_c']} → {r['all_fitted_with_rms_c']} | {r['passes']} |")
P(f"\nenters: {d['enters']}\n")
P("| run | card kind | hold | R °C | arm A's e °C | fitted | e with common gamma |")
P("|---|---|---|---:|---:|---|---:|")
for r in d["holds"]:
    P(f"| {r['session']} | {r['card_kind']} | {r['hold']} | {f(r['R_C'], 2)} | {r['e_C']:+.3f} | {r['fitted']} | "
      f"{(format(r['e_common'], '+.3f')) if r.get('e_common') is not None else '—'} |")
P(f"\n## Entered\n\n{json.dumps(m10['entered'])}")
P("\n## Pool 7's 48 priority-1 kinds per card, all three formats (rows-m10.json): rms (bias), W\n")
rows = json.load(open(os.path.join(D, "rows-m10.json")))
fv = {"float": h["power"]["float"]["frozen_variant"], "int8": h["power"]["int8"]["frozen_variant"]}
P("| card | n | M10 held out | B (M9's form refitted, held out) | M9 as frozen (measured rates) |")
P("|---|---:|---:|---:|---:|")
for c in ("a3", "c1"):
    sel = [r for r in rows if r["exp"] in ("E163", "E164") and r["card"] == c and r["priority"] == 1]
    def rr(es):
        es = [e for e in es if e is not None]
        return f"{(sum(e * e for e in es) / len(es)) ** 0.5:.3f} ({sum(es) / len(es):+.3f})"
    m10e = [r["err_w"][fv["int8" if r["type"] == "int8" else "float"]] for r in sel]
    P(f"| {c} | {len(sel)} | {rr(m10e)} | {rr([r['err_w']['B'] for r in sel])} | {rr([r['M9_as_frozen_err_w'] for r in sel])} |")
