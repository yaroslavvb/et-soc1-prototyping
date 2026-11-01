#!/usr/bin/env python3
"""The README's tables, from analysis.json: make_tables.py analysis.json > tables.md"""
import json
import sys

a = json.load(open(sys.argv[1]))
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}
var = "vpu_map"
fit = a["fit_e78"]
print("## Tables generated from analysis.json\n")
print("### All 51 kinds\n")
print("Per multiply-add for the counts, watts over the type's own zeros for D. `fit` is the plain two-term fit (fp32 and fp16 pooled; int8 by itself), so `fit − D` is in-sample.")
print("nets = merged-net toggles of the whole VPU (`nets_map`); unit = the multiply-add unit alone, the first by this file's map, the second by the recount's per-run merge; clocked = register bits clocked; changed = register bits that change.\n")
print("| kind | D (W) | fit − D | nets | unit (map) | unit (recount) | clocked | changed | slots valid of 4,096 |")
print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
order = sorted(a["kinds"], key=lambda r: ({"fp32": 0, "fp16": 1, "int8": 2}[r["key"][:4]], -r["D"]))
res = {}
res.update(fit["fp32+fp16"][var]["resid"])
res.update(fit["int8"][var]["resid"])
ffc = {r["key"]: r for r in a["kinds"]}
for r in order:
    t = r["key"][:4]
    m = MACS[t]
    e = res.get(r["key"])
    print(f"| {r['key']} | {r['D']:.2f} | {(-e if e is not None else 0):+.2f} | {r['netsm_vpu'] / m:,.1f} | {r['netsm_unit'] / m:,.1f} | {r['nets_unit'] / m:,.1f} | {r['clk'] / m:,.1f} | {r['ff_tog'] / m:,.1f} | {r['valid']:,.0f} |")
print("\n### The fits on E78\n")
print("| scope | counted as | rms (W) | leave-one-out rms (W) | r | ρ | worst (W) | k (fJ per net toggle) | a (fJ per clocked bit) |")
print("|---|---|---:|---:|---:|---:|---:|---:|---:|")
for scope in ("fp32", "fp16", "fp32+fp16", "int8"):
    for v in ("vpu_map", "unit_map", "vpu_hier", "unit_hier", "vpu_hier2", "vpu_map_only", "clk_only", "ff_toggles_clk"):
        f = fit[scope][v]
        co = list(f["coef_fJ"].items())
        kk = next((x for c, x in co if c.startswith("dnets") or c == "dtog"), None)
        aa = next((x for c, x in co if c == "dclk"), None)
        print(f"| {scope} | {v} | {f['rms_w']:.3f} | {f['loo']['rms_w']:.3f} | {f['pearson_r']:.4f} | {f['spearman_rho']:.3f} | {f['worst_w']:.2f} | {kk if kk is None else round(kk, 3)} | {aa if aa is None else round(aa, 3)} |")
print("\n### Across formats, coefficients fitted on one and applied to the other\n")
print("| counted as | fp32 → fp16 rms (W), r | fp16 → fp32 rms (W), r | fp32+fp16 → int8 rms (W), bias (W), r |")
print("|---|---:|---:|---:|")
for v in ("vpu_map", "vpu_hier", "vpu_hier2"):
    x = a["across_formats"][v]
    print(f"| {v} | {x['fp32_to_fp16']['rms_w']:.3f}, {x['fp32_to_fp16']['pearson_r']:.4f} | {x['fp16_to_fp32']['rms_w']:.3f}, {x['fp16_to_fp32']['pearson_r']:.4f} | {x['float_to_int8']['rms_w']:.3f}, {x['float_to_int8']['bias_w']:+.3f}, {x['float_to_int8']['pearson_r']:.4f} |")
print("\n### Coefficients frozen on E78's fp32 and fp16 kinds, applied to other experiments\n")
print("| set | measured on | n | rms (W) | bias (W) | r | ρ | measured / predicted |")
print("|---|---|---:|---:|---:|---:|---:|---:|")
o = a["other_experiments"][var]
for name, where in (("e90", "aifoundry3, E90"), ("e86", "aifoundry3, E86")):
    x = o[name]["float"]
    print(f"| {name}, floats | {where} | {x['n']} | {x['rms_w']:.3f} | {x['bias_w']:+.3f} | {x['pearson_r']:.4f} | {x['spearman_rho']:.3f} | |")
cs = a["card_scale"][var]
print(f"| e82, floats, card scale {cs['scale_from_e82']:.4f} fitted here | aifoundry1 card 1 | {cs['e82_after_scale']['n']} | {cs['e82_after_scale']['rms_w']:.3f} | {cs['e82_after_scale']['bias_w']:+.3f} | {cs['e82_after_scale']['pearson_r']:.4f} | {cs['e82_after_scale']['spearman_rho']:.3f} | |")
print(f"| e88, floats, E82's card scale | aifoundry1 card 1 | {cs['e88_after_scale']['n']} | {cs['e88_after_scale']['rms_w']:.3f} | {cs['e88_after_scale']['bias_w']:+.3f} | {cs['e88_after_scale']['pearson_r']:.4f} | {cs['e88_after_scale']['spearman_rho']:.3f} | |")
L = {"e65_bit": "E65, fp32 B, one bit, A = 1.0", "e65_bpi": "E65, B, A = π", "e67_abit": "E67, fp32 A, one bit, B = 1.0", "e67_abp": "E67, A, B = π", "e67_ix": "E67, the interaction grid", "e70_lq": "E70, low bits together", "e70_ls": "E70, spread bits", "e70_alq": "E70, A, low bits", "e60_lb": "E60, low bits, A = π", "e60_ord": "E60, A's order"}
for k, nm in L.items():
    st = o["ladder"].get(k)
    if st and "bias_w" in st:
        print(f"| {nm} | aifoundry3 | {st['n']} | {st['rms_w']:.3f} | {st['bias_w']:+.3f} | {st['pearson_r']:.4f} | {st['spearman_rho']:.3f} | {st['slope_measured_over_pred']:.3f} |")
for fam, st in sorted(o.get("e79", {}).items()):
    if "bias_w" in st:
        print(f"| E79, {fam} | aifoundry3 | {st['n']} | {st['rms_w']:.3f} | {st['bias_w']:+.3f} | {st['pearson_r']:.4f} | {st['spearman_rho']:.3f} | {st['slope_measured_over_pred']:.3f} |")
print("\n### What the coefficients do under other readings\n")
for v, x in a["coef_spread"].items():
    print(f"- {v}: k {x['coef_fJ'][0]:.3f} ± {x['jackknife_se_fJ'][0]:.3f} fJ, a {x['coef_fJ'][1]:.3f} ± {x['jackknife_se_fJ'][1]:.3f} fJ (jackknife over kinds); leakage arm 0: {x['arms']['leak0']['coef_fJ'][0]:.3f}, {x['arms']['leak0']['coef_fJ'][1]:.3f}, rms {x['arms']['leak0']['rms_w']:.3f} W; arm 0.3803: {x['arms']['leak0.3803']['coef_fJ'][0]:.3f}, {x['arms']['leak0.3803']['coef_fJ'][1]:.3f}, rms {x['arms']['leak0.3803']['rms_w']:.3f} W")
print("\n### Random data's watts, split by the model\n")
print("| kind | D | clocked register bits | data nets | multiplier | adder and normaliser | result path (f6 + C register file) | operand bus (f0 + lane) | exponent | control | sequencer |")
print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for k in ("fp32.randn", "fp16.randn", "int8.full", "fp32.ones"):
    s = a["split"][k]
    w = s["stages_W"]
    g = lambda n: w.get(n, 0)
    print(f"| {k} | {s['D']:.2f} | {s['clocked_W']:.2f} | {s['nets_W']:.2f} | {g('multiplier'):.2f} | {g('adder_norm'):.2f} | {g('result') + g('c_regfile'):.2f} | {g('operand') + g('lane_operand_bus'):.2f} | {g('exponent'):.2f} | {g('control'):.2f} | {g('vpu_sequencer'):.2f} |")
print("\n(The split is of the fit, not a measurement, and it is over the type's zeros only in total: the stage columns are absolute nets at the fit's k.)")
print("\n### Merged-net toggles per multiply-add, by stage (the whole VPU, `nets_map`)\n")
print("| kind | clocked | changed | operand bus | multiplier | adder and normaliser | result path | exponent | control | sequencer | total |")
print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for k in ("fp32.randn", "fp32.uniform01", "fp32.smallint", "fp32.ones", "fp32.nn_like", "fp16.randn", "fp16.uniform01", "fp16.ones", "int8.full", "int8.ones"):
    r = ffc[k]
    m = MACS[k[:4]]
    w = r["by_stage_vpu"]
    print(f"| {k} | {r['clk'] / m:,.0f} | {r['ff_tog'] / m:,.0f} | {(w['operand'] + w['lane_operand_bus']) / m:,.1f} | {w['multiplier'] / m:,.1f} | {w['adder_norm'] / m:,.1f} | {(w['result'] + w['c_regfile']) / m:,.1f} | {w['exponent'] / m:,.1f} | {w['control'] / m:,.1f} | {w['vpu_sequencer'] / m:,.1f} | {r['netsm_vpu'] / m:,.1f} |")
print("\n### E65's list: a flip of one B bit, A = 1.0, by stage, per multiply-add over `lq_h0`\n")
print("| bit | D (W) | predicted (W) | nets | operand bus | multiplier | adder and normaliser | result path | exponent | control |")
print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
it = o["ladder"]["e65_bit"]["items"]
for j in (0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 21, 22, 23, 25, 27, 29, 30, 31):
    v = it.get(f"bit_{j}")
    if not v:
        continue
    w = v["stage"]
    print(f"| {j} | {v['D']:.2f} | {v['pred']:.2f} | {v['dnets_per_mac']:.1f} | {w['operand'] + w['lane_operand_bus']:.1f} | {w['multiplier']:.1f} | {w['adder_norm']:.1f} | {w['result'] + w['c_regfile']:.1f} | {w['exponent']:.1f} | {w['control']:.1f} |")
