#!/usr/bin/env python3
"""E95: every derived number the README quotes that results.md does not print, from this directory's committed files. Standard library only.

    python3 readme-numbers.py > readme-numbers.txt
"""
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "scored.json")))
N = json.load(open(os.path.join(HERE, "dips-arm/scored-nodips.json")))
E = json.load(open(os.path.join(HERE, "e95.json")))
A = json.load(open(os.path.join(HERE, "e95-leak0.1994.json")))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
F = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/real2/predictions-real2.json")))
R = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/predictions-e95.json")))


def pm(m, d=3):
    return "—" if not m or m.get("mean") is None else (f"{m['mean']:.{d}f} ± {m['ci95']:.{d}f}" if m.get("ci95") is not None else f"{m['mean']:.{d}f}")


def t(name, rep=P):
    return rep["tiles"][name]


print("# E95: numbers the README quotes (readme-numbers.py)")
print("\n## Kept passes per reduction")
for lab, f in (("primary", "e95.json"), ("leak 0.1994", "e95-leak0.1994.json"), ("leak 0.3803", "e95-leak0.3803.json"), ("leak 0", "e95-leak0.json"),
               ("dips removed", "dips-arm/e95-nodips.json"), ("no A1", "no-a1-arm/e95-no-a1.json")):
    r = json.load(open(os.path.join(HERE, f)))
    print(f"{lab}: k {r['leak']['k_w_per_c']:.4f} W/C over {r['leak']['n_runs']} runs; kept {r['passes']}; runs kept {r['kept']}/{r['runs']}; set aside {[(x['pass'], x['why']) for x in r['passes_set_aside']]}")
print("\n## Runs per pass and the launch rule's skips")
for p in (9510, 9511, 9512, 9513, 9514):
    ms = [json.loads(x) for x in open(os.path.join(HERE, f"aifoundry3/kinds/p{p}/marks.jsonl"))]
    runs = [m for m in ms if m["kind"] == "run"]
    print(f"p{p}: {len(runs)} runs; skipped {[(m['item'], m['pos']) for m in ms if m['kind'] == 'skipped']}; block {json.load(open(os.path.join(HERE, f'aifoundry3/kinds/p{p}/block.json')))['t0_ms']}..{json.load(open(os.path.join(HERE, f'aifoundry3/kinds/p{p}/block.json')))['t1_ms']}")
    order = {m["pos"]: m["item"] for m in runs}
    for m in ms:
        if m["kind"] == "skipped":
            print(f"   before #{m['pos']} ran {order.get(m['pos'] - 1)}")
print("\n## Tiles with fewer than the kept passes, primary")
for n, v in P["tiles"].items():
    if v["D"]["n"] < len(P["passes"]):
        print(f"{n}: n {v['D']['n']}, values {v['D']['values']}")
print("\n## Primary against the 0.1994 arm (E78's slope), D in W")
print("| tile | primary | 0.1994 arm (three passes) | difference |\n|---|---|---|---|")
for n in ("fp32.randn", "fp16.randn", "int8.full", "fp32.r2_vit_l5_down", "fp32.r2_vit_l11_down", "fp32.r2_vgg16_fc2", "fp16.r2_vgg16_fc2", "int8.r2_vgg16_fc2", "fp32.r2_t5small_l0_up"):
    a = E["items"][n]["D"]["mean"]
    b = A["items"][n]["D"]["mean"]
    print(f"| {n} | {a:.3f} | {b:.3f} | {a - b:+.3f} |")
print("\n## Nested windows of one layer in three formats (r = D over the same pass's random kind of that format)")
print("| layer | format | gate closes | live share | r primary | r dips-removed | D W | r ÷ live share | a live lane's cost ÷ random's | pJ/MAC (D) | pJ/MAC (S) |\n|---|---|---|---|---|---|---|---|---|---|---|")
for lay, ty in (("vgg16_fc2", "fp32"), ("vgg16_fc2", "fp16"), ("vgg16_fc2", "int8"), ("resnet18_l3c1", "fp32"), ("resnet18_l3c1", "fp16"), ("resnet18_l3c1", "int8"),
                ("t5small_l0_down", "fp32"), ("t5small_l0_down", "fp16"), ("t5small_l0_down", "int8"), ("resnet18_l2c1", "fp32"), ("gpt2_l11_down_maxabs", "int8"), ("vit_l11_down", "int8")):
    n = f"{ty}.r2_{lay}"
    v = t(n)
    g = v["c"]["g"]
    print(f"| {lay} | {ty} | {g:.3f} | {1 - g:.3f} | {pm(v['r_D'], 4)} | {pm(t(n, N)['r_D'], 4)} | {pm(v['D'])} | {v['r_D']['mean'] / (1 - g):.3f} | {v['c']['live_lane_cost_over_random']:.3f} | {v['pj_mac_D']['mean']:.3f} | {v['pj_mac_S']['mean']:.3f} |")
print("\n## D ÷ (c), range per format, primary")
for ty in ("fp32", "fp16", "int8"):
    xs = [v["c"]["measured_over_law"] for n, v in P["tiles"].items() if n.startswith(ty + ".") and v.get("c")]
    ms = [v["c"]["D_minus_c_w"] for n, v in P["tiles"].items() if n.startswith(ty + ".") and v.get("c")]
    aa = [v["a"]["D_minus_a_w"] for n, v in P["tiles"].items() if n.startswith(ty + ".") and v.get("c")]
    print(f"{ty}: D/(c) {min(xs):.3f}..{max(xs):.3f}; D-(c) {min(ms):+.3f}..{max(ms):+.3f} W, rms {math.sqrt(sum(x * x for x in ms) / len(ms)):.3f}; D-(a) {min(aa):+.3f}..{max(aa):+.3f} W, rms {math.sqrt(sum(x * x for x in aa) / len(aa)):.3f}; tiles {len(xs)}")
print("\n## Baselines of the no-zero and special tiles, D ÷, S ÷, whole board ÷ random (primary, then dips removed)")
print("| tile | D ÷ random | S ÷ random | board ÷ random | D ÷ random, dips removed |\n|---|---|---|---|---|")
for n in ("fp32.r2_gpt2_l3_mlp_down", "fp32.r2_gpt2_l9_attn_qk", "fp32.r2_bert_l6_up", "fp32.r2_vit_l5_down", "fp32.r2_t5small_l0_up", "fp32.r2_vit_l11_down", "fp32.r2_gpt2_l6_mlp_down_bf16fwd",
          "fp16.r2_gpt2_l9_attn_qk", "fp16.r2_bert_l6_up", "fp16.r2_vit_l5_down", "fp16.real_l6_attn_qk", "fp16.r2_gpt2_l6_attn_qk_fp16fwd", "fp16.real_l6_mlp_down", "fp16.r2_gpt2_l6_mlp_down_fp16fwd"):
    v = t(n)
    print(f"| {n} | {pm(v['r_D'], 4)} | {pm(v['r_S'], 4)} | {pm(v['r_p80'], 4)} | {pm(t(n, N)['r_D'], 4)} |")
print("\n## ΔT against the same pass's random kind (firmware's whole-degree reading, primary)")
for n in ("fp32.r2_vit_l5_down", "fp32.r2_vgg16_fc2", "fp32.r2_t5small_l0_down", "fp16.r2_vgg16_fc2", "fp16.r2_t5small_l0_down", "int8.r2_vgg16_fc2", "int8.r2_gpt2_l11_down_maxabs"):
    print(f"{n}: dT {t(n)['dT_win']['mean']:.2f} C, minus random {pm(t(n)['dT_minus_ref_c'], 2)} C")
print("\n## E78's cells beside (predictions-e95.json e78_beside)")
for k, v in R["e78_beside"].items():
    print(f"{k}: {v['D_w']} ± {v['ci95_w']}")
print("\n## Calibration tiles, primary and dips removed")
print("| layer | calibration | gate | bus bits/op | D W | r | S W | whole board ÷ random | D W, dips removed |\n|---|---|---|---|---|---|---|---|---|")
for lay, cal, n in (("GPT-2 l11", "max-abs", "int8.r2_gpt2_l11_down_maxabs"), ("GPT-2 l11", "asymmetric", "int8.r2_gpt2_l11_down_asym"), ("GPT-2 l11", "p99.9 clip", "int8.r2_gpt2_l11_down_p999"),
                    ("VGG fc2", "symmetric", "int8.r2_vgg16_fc2"), ("VGG fc2", "asymmetric", "int8.r2_vgg16_fc2_asym"),
                    ("GPT-2 l6", "committed (max-abs)", "int8.real_l6_mlp_down"), ("GPT-2 l6", "p99.99 clip", "int8.r2_gpt2_l6_down_p9999"), ("GPT-2 l6", "per token", "int8.r2_gpt2_l6_down_per_token"), ("GPT-2 l6", "p99.9 clip", "int8.r2_gpt2_l6_down_p999")):
    v = t(n)
    print(f"| {lay} | {cal} | {v['gated_lane_frac']:.3f} | {v['bus_bits_per_op']} | {pm(v['D'])} | {pm(v['r_D'], 4)} | {pm(v['S'])} | {pm(v['r_p80'], 4)} | {pm(t(n, N)['D'])} |")
print("\n## The E78 reference: S and pJ per MAC of random, primary")
for n in ("fp32.randn", "fp16.randn", "int8.full"):
    v = t(n)
    print(f"{n}: D {pm(v['D'])}, S {pm(v['S'])}, pJ/MAC (S) {v['pj_mac_S']['mean']:.3f}, (D) {v['pj_mac_D']['mean']:.3f}")
pp = E["per_pass"]
d = [pp[p]["int8.r2_gpt2_l11_down_p999"]["D"] - pp[p]["int8.r2_gpt2_l11_down_asym"]["D"] for p in pp]
print(f"\nGPT-2 layer 11, p99.9 - asymmetric, paired per pass (primary): {statistics.fmean(d):+.3f} +- {statistics.stdev(d) / math.sqrt(len(d)) * 3.182:.3f} W over {len(d)} passes")
print(f"\nidle level {pm(E['idle_level'])} W")
