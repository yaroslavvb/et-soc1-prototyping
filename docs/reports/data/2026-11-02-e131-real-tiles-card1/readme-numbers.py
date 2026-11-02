#!/usr/bin/env python3
"""E131: the derived numbers the README quotes, each printed here from the committed files of this directory and E95's and E112's (written
after the registered reduction and scoring; decides nothing). Standard library only.

    python3 docs/reports/data/2026-11-02-e131-real-tiles-card1/readme-numbers.py > .../readme-numbers.txt
SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
D95 = os.path.join(HERE, "..", "2026-11-01-e95-real-tensors-energy")
D112 = os.path.join(HERE, "..", "2026-11-01-e112-real-replicates")
TYPES = ("fp32", "fp16", "int8")


def J(p):
    return json.load(open(p))


def f(x, d=4):
    return "—" if x is None else f"{x:+.{d}f}"


s = J(os.path.join(HERE, "scored.json"))
P = J(os.path.join(HERE, "e131.json"))
n95 = J(os.path.join(D95, "dips-arm", "scored-nodips.json"))
p95 = J(os.path.join(D95, "scored.json"))

print("== A. The session")
q = open(os.path.join(HERE, "logs", "queue.out")).read()
for m in re.finditer(r"^(\S+) (p131\d\d) (starts at .*|rc=.*)$", q, re.M):
    print("  ", m.group(1), m.group(2), m.group(3))
for m in re.finditer(r"^(\S+) (budget: .*|e131: done.*)$", q, re.M):
    print("  ", m.group(1), m.group(2))
for nm in ("config-session-start", "config-session-end"):
    print(f"   {nm}: {open(os.path.join(HERE, 'logs', nm + '.json')).read().strip()} at {open(os.path.join(HERE, 'logs', nm + '.json.time')).read().strip()}")
for d in sorted(glob.glob(os.path.join(HERE, "aifoundry1-c1", "e131", "p131*"))) + [os.path.join(HERE, "aifoundry1-c1", "e131-smoke-p13101")]:
    b = J(os.path.join(d, "block.json"))
    cs, ce = (open(os.path.join(d, x)).read().strip() for x in ("config_start.json", "config_end.json"))
    marks = [json.loads(x) for x in open(os.path.join(d, "marks.jsonl")) if x.strip()]
    heats = sum(1 for m in marks if m.get("kind") == "heater")
    burn = sum(1 for m in marks if m.get("kind") == "heater" and m.get("item") == "burnin")
    runs = sum(1 for m in marks if m.get("kind") == "run")
    print(f"   {os.path.basename(d)}: {b['status']}, {(b['t1_ms'] - b['t0_ms']) / 1000:.0f} s, die {b['die_c_start']} -> {b['die_c_end']} C; "
          f"{runs} runs, {heats} heater launches ({burn} before the burn-ins, {heats - burn} at the runs: {(heats - burn) / max(runs, 1):.2f} a run)")
    print(f"      config start {cs}")
    print(f"      config end   {ce}")
dips = P["reducer"]["dip_samples_removed"]
print("   dips removed per pass (primary):", {k: v["samples_removed"] for k, v in dips.items()})
print(f"   primary: passes {P['passes']}, runs kept {P['kept']} of {P['runs']}, set aside {P['passes_set_aside']}, leak {P['leak']}, "
      f"clock {P['clock_mhz']} MHz, mean minion voltage {P['v_mean'] * 1000:.1f} mV, idle {P['idle_level']['mean']:.3f} W")

print("\n== B. Each claim beside E95 on aifoundry3 (its dips-removed arm, five passes, and its registered primary, four)")
for k, v in s["claims"].items():
    print(f"   {k}: E131 {v['verdict']}; E95 dips-removed arm {n95['claims'][k]['verdict']}; E95 primary {p95['claims'][k]['verdict']}; "
          f"arm-sensitive {v.get('arm_sensitive')}; at the arms {v.get('at_arms')}")
C = s["claims"]
c95 = n95["claims"]
print("   C1 cells, E131 / E95 dips removed:")
for cell, v in C["C1"]["cells"].items():
    w = c95["C1"]["cells"][cell]
    print(f"      {cell}: {v['r']['mean']:.4f} ± {v['r']['ci95']:.4f} {v['verdict']} / {w['r']['mean']:.4f} ± {w['r']['ci95']:.4f} {w['verdict']}")
for ty, v in C["C2"]["formats"].items():
    w = c95["C2"]["formats"][ty]
    print(f"   C2 {ty}: {v['r']['mean']:.4f} ± {v['r']['ci95']:.4f} / {w['r']['mean']:.4f} ± {w['r']['ci95']:.4f}")
for k in ("C6", "C8", "C11"):
    v, w = C[k], c95[k]
    print(f"   {k}: {v['diff_w']['mean']:+.3f} ± {v['diff_w']['ci95']:.3f} W / {w['diff_w']['mean']:+.3f} ± {w['diff_w']['ci95']:.3f} W")
for name, v in C["C4"]["pairs"].items():
    w = c95["C4"]["pairs"][name]
    a, b = v["r_fp16_minus_r_fp32"], w["r_fp16_minus_r_fp32"]
    print(f"   C4 {name}: {a['mean']:+.4f} ± {a['ci95']:.4f} / {b['mean']:+.4f} ± {b['ci95']:.4f}")
for t, v in C["C5"]["tiles"].items():
    w = c95["C5"]["tiles"][t]
    print(f"   C5 {t}: D {v['D']['mean']:.3f} ± {v['D']['ci95']:.3f} W, (a) {v['a_w']}, (c) {v['c_w']}, nearer {v['nearer']} / E95 D {w['D']['mean']:.3f} "
          f"± {w['D']['ci95']:.3f} nearer {w['nearer']}")
for t, v in C["C7"]["offsets_w"].items():
    w = c95["C7"]["offsets_w"].get(t) or {}
    print(f"   C7 {t}: {v['mean']:+.3f} ± {v['ci95']:.3f} W / E95 {w.get('mean', float('nan')):+.3f} ± {w.get('ci95') or float('nan'):.3f}")
print(f"   C9 D {C['C9']['D']['mean']:.3f} ± {C['C9']['D']['ci95']:.3f} W / E95 {c95['C9']['D']['mean']:.3f} ± {c95['C9']['D']['ci95']:.3f}")
print(f"   C10 r {C['C10']['r']['mean']:.4f} ± {C['C10']['r']['ci95']:.4f} / E95 {c95['C10']['r']['mean']:.4f} ± {c95['C10']['r']['ci95']:.4f}")
print(f"   C12 {C['C12']['inside']} of {C['C12']['of']} / E95 {c95['C12']['inside']} of {c95['C12']['of']}")
for ty, v in C["C3b"]["formats"].items():
    print(f"   C3b {ty}: slope/L {v['slope_over_L']:.3f} (per pass {v['per_pass_interval_reported']['mean']:.3f} ± "
          f"{v['per_pass_interval_reported']['ci95']:.3f}) / E95 {c95['C3b']['formats'][ty]['slope_over_L']:.3f}")

print("\n== C. The cross-card rows (carrying reading against E95's dips-removed arm)")
rows = s["cross_card"]["carrying"]["rows"]
for ty in TYPES:
    dd = [v["r_diff"] for n, v in rows.items() if n.startswith(ty + ".") and v.get("r_diff") is not None]
    hw = [v["r_card1"]["ci95"] for n, v in rows.items() if n.startswith(ty + ".") and v.get("r_card1") and v["r_card1"].get("ci95")]
    rat = [v["ratio_a3_over_c1"] for n, v in rows.items() if n.startswith(ty + ".") and v.get("ratio_a3_over_c1")]
    print(f"   {ty}: {len(dd)} tiles; r(card 1) - r(aifoundry3): median {statistics.median(dd):+.4f}, max |diff| {max(abs(x) for x in dd):.4f}; "
          f"card 1's r half-widths median {statistics.median(hw):.4f}, max {max(hw):.4f}; D ratio a3/c1 median {statistics.median(rat):.4f} "
          f"({min(rat):.4f}-{max(rat):.4f}, every row incl. the random kind)")
x = s["cross_card"]["carrying"]
print(f"   X4 median {x['x4']['median_ratio']:.4f}, IQR {x['x4']['iqr']}, per type {x['x4']['per_type_median']}")
print(f"   X1 {[(t, round(v['rho'], 4)) for t, v in x['x1']['by_type'].items()]}; X5 {x['x5']['agree']} of {x['x5']['resolved']}")
print("   at the arms:", s["cross_card"]["at_arms"])
for nm in ("auto", "leak0.545", "leak0.1994"):
    sa = s["arms"][nm]
    print(f"   arm {nm}: leak {sa['leak']['k_w_per_c']:.4f}; cross {sa['cross_card']}")

print("\n== D. Beside E112(b)'s two kept passes on this card (reported)")
cs = s["cross_session_e112b_reported"]
for ty in TYPES:
    dd = [v["r_diff"] for n, v in cs.items() if n.startswith(ty + ".") and v.get("r_diff") is not None]
    dD = [v["D_diff_auto_vs_e112b"] for n, v in cs.items() if n.startswith(ty + ".") and v.get("D_diff_auto_vs_e112b") is not None]
    print(f"   {ty}: r(E131) - r(E112b): median {statistics.median(dd):+.4f}, max |diff| {max(abs(v) for v in dd):.4f} ({len(dd)} tiles); "
          f"D(E131 auto arm) - D(E112b): median {statistics.median(dD):+.3f} W, range {min(dD):+.3f} to {max(dD):+.3f} W ({len(dD)} rows)")

print("\n== E. The slope")
A = J(os.path.join(HERE, "e131-auto.json"))
for n in ("fp32.randn", "fp16.randn", "int8.full", "fp32.r2_vgg16_fc2", "int8.r2_vgg16_fc2"):
    a, b = P["items"][n]["D"]["mean"], A["items"][n]["D"]["mean"]
    print(f"   {n}: D at 0.2414 {a:.3f} W, at auto ({A['leak']['k_w_per_c']:.4f}) {b:.3f} W, difference {a - b:+.3f} W")
e112b = J(os.path.join(D112, "b-e95-card1", "e112b.json"))
print(f"   auto slopes on card 1: E131 {A['leak']['k_w_per_c']:.4f}, E112(b) {e112b['leak']['k_w_per_c']:.4f} W/C; E95 dips removed on aifoundry3 "
      f"{J(os.path.join(D95, 'dips-arm', 'e95-nodips.json'))['leak']['k_w_per_c']:.4f}")
L0 = J(os.path.join(HERE, "e131-leak0.json"))
print(f"   the leakage-0 arm keeps {L0['passes']}; set aside {L0['passes_set_aside']}")

print("\n== F. The session tie to E82's card-1 cells (reported)")
for n, v in s["session_tie_reported"]["rows"].items():
    print(f"   {n}: {v['D']['mean']:.3f} ± {v['D']['ci95']:.3f} W against {v['ref_D_w']:.3f}: {v['diff_w']:+.3f} W (band ±{v['band_w']}) {v['verdict']}")
c = s["checks"]
print(f"\n== G. Checks: idle consistency {c['idle_consistency_median_abs_w']:.3f} W; rail tau {c['rail_tau_median_s']} s; duty {c['duty_min']:.4f}-"
      f"{c['duty_max']:.4f}; carry-over {c['carryover']['slope_w_per_w']:.4f} W/W, SE {c['carryover']['se']:.4f}, n {c['carryover']['n']}")
