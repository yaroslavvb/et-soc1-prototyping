#!/usr/bin/env python3
"""Q132(b), corrections after verification: every number the corrections quote, recomputed from committed files. Standard library only.

    python3 corrections-check.py > corrections-check.txt         # from this directory

SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
load = lambda p: json.load(open(os.path.join(HERE, p)))
v2 = load("counts-v2.json")["rows"]
o0 = load("optimiser-sensitivity/counts-O0.json")["rows"]
o3 = load("optimiser-sensitivity/counts-O3.json")["rows"]
om = load("optimiser-sensitivity/counts-O0-map.json")["rows"]
MAC = {"fp32": 4096, "fp16": 8192, "int8": 16384}

print("# [A] how far the count moves with every Verilator optimisation off (counts-O0.json against counts-O3.json, one build each, the merges of that run)")
for k in o0:
    a, b = o0[k]["mean"], o3[k]["mean"]
    f = lambda q, s: f"{a[s][q] / max(b[s][q], 1) - 1:+.1%}"
    print(f"  {k:12s} unit nets_hier {f('nets_hier', 'unit')}, nets_hier2 {f('nets_hier2', 'unit')}; vpu nets_hier {f('nets_hier', 'vpu')}, nets_hier2 {f('nets_hier2', 'vpu')}; clocked {a['ff']['all']['clocked'] / b['ff']['all']['clocked'] - 1:+.1%}")
print("\n# [A2] nets_map, its merge learned again on the -O0 binary (train_maps.py), against this README's default build")
for k in om:
    a, b = om[k]["mean"], v2[k]["mean"]
    if b["vpu"]["nets_map"] == 0:
        continue
    t = om[k]["type"]
    st = {s: f"{a['vpu']['by_stage'][s] / MAC[t]:.1f} vs {b['vpu']['by_stage'][s] / MAC[t]:.1f}" for s in ("multiplier", "adder_norm", "lane_operand_bus", "operand", "exponent") if b["vpu"]["by_stage"][s] > 0.01 * b["vpu"]["nets_map"]}
    print(f"  {k:14s} unit map {a['unit']['nets_map'] / MAC[t]:8.1f} vs {b['unit']['nets_map'] / MAC[t]:8.1f} ({a['unit']['nets_map'] / max(b['unit']['nets_map'], 1) - 1:+.1%}); vpu map {a['vpu']['nets_map'] / MAC[t]:8.1f} vs {b['vpu']['nets_map'] / MAC[t]:8.1f} ({a['vpu']['nets_map'] / b['vpu']['nets_map'] - 1:+.1%}); clocked {a['ff']['all']['clocked'] / b['ff']['all']['clocked'] - 1:+.1%}; by stage, -O0 vs default, per MAC: {st}")

print("\n# [B] the merges: is nets_map at or above nets_hier in every kind, unit and VPU?")
bad = [k for k, v in v2.items() if v["mean"]["unit"]["nets_map"] < v["mean"]["unit"]["nets_hier"] - 1e-9]
badv = [k for k, v in v2.items() if v["mean"]["vpu"]["nets_map"] < v["mean"]["vpu"]["nets_hier"] - 1e-9]
print(f"  unit: {len(v2) - len(bad)} of {len(v2)} at or above; below: {bad[:8]}")
print(f"  VPU: {len(v2) - len(badv)} of {len(v2)} at or above; below: {badv[:8]}")
print(f"  fp32 randn per MAC: unit hier {v2['fp32.randn']['mean']['unit']['nets_hier'] / 4096:.1f}, hier2 {v2['fp32.randn']['mean']['unit']['nets_hier2'] / 4096:.1f}, map {v2['fp32.randn']['mean']['unit']['nets_map'] / 4096:.1f}")

print("\n# [C] what the functional check covers")
for f_ in ("fcheck/fcheck-unit-fp32.json", "fcheck/fcheck-unit-fp16.json"):
    u = load(f_)
    print(f"  {f_}: {u['tally']}; by class {u['by_kind']}; against exact RTZ {u.get('fp16_against_exact_rtz')}")
n = {t: sum(1 for v in v2.values() if v["type"] == t) for t in MAC}
zero = {t: [v["kind"] for v in v2.values() if v["type"] == t and v["mean"]["valid_slots"] == 0] for t in MAC}
print(f"  kinds {n}; 768 words a kind ({3} launch points x 256): {sum(n.values()) * 768} words; by format {[(t, n[t] * 768) for t in n]}")
print(f"  kinds with no valid slot, where C stays 0: {zero}; {sum(len(x) for x in zero.values()) * 768} words; leaving {(sum(n.values()) - sum(len(x) for x in zero.values())) * 768}, of which fp16 {(n['fp16'] - len(zero['fp16'])) * 768}")
print(f"  mismatches over all kinds: {sum(p['check_mismatch'] for v in v2.values() for p in v['points'])}")
print(f"  'result' on every card record: E103's runs.jsonl says {sorted(set(json.loads(l).get('result') for l in open(os.path.join(HERE, '..', '2026-11-01-e103-model-blind-test', 'aifoundry1-c1', 'kinds', 'p10310', 'runs.jsonl')))) }")

print("\n# [D] two terms on single B bits (E65), by the merge")
an = load("analysis.json")["other_experiments"]
for q in ("vpu_map", "vpu_hier2", "vpu_hier"):
    print(f"  {q}: rms {an[q]['ladder']['e65_bit']['rms_w']:.3f} W, measured/predicted {an[q]['ladder']['e65_bit']['slope_measured_over_pred']:.3f}; E70 spread {an[q]['ladder']['e70_ls']['rms_w']:.3f} W")
sa = load("../2026-11-01-e103-model-blind-test/score_all.json")
print(f"  M4: E65 {sa['post_hoc_ladders']['E65, one B bit, A = 1']['rms_w']:.3f} W, E70 spread {sa['post_hoc_ladders']['E70, spread bits']['rms_w']:.3f} W")

print("\n# [E] the reproducer's length, and accum.c's comment")
src = open(os.path.join(REPO, "rtl-sim/fma_toggle_v2/verilator_dfg_reproducer.sv")).read().splitlines()
code = [l for l in src if l.strip() and not l.strip().startswith("//")]
print(f"  verilator_dfg_reproducer.sv: {len(src)} lines, {len(code)} of code")
print("  accum.c:", [l.strip()[:120] for l in open(os.path.join(REPO, "rtl-sim/fma_toggle_v2/accum.c")) if re.search(r"of 40,?000|of 20,?000", l)])
