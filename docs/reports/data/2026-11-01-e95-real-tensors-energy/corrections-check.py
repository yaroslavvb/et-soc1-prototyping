#!/usr/bin/env python3
"""E95: the desk check behind "Corrections after verification" (README.md): every number the corrections cite, from committed files.
Standard library only; run from anywhere. No card, nothing re-run; it reads scored.json, the arms, runs.csv, the frozen files and the tiles' bytes.

    python3 corrections-check.py > corrections-check.txt

Two inputs are not in this repository and are copied here, labelled: GPT-2 layer 11's largest activations (the verifier's own forward pass; its
largest value and zero-byte share match capture.json), and the names of the regressions compared before M4 (the bench lane's session record).
"""
import csv
import json
import math
import os
import statistics
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
K = os.path.join(ROOT, "tools/claims-v3/kinds")
P = json.load(open(os.path.join(HERE, "scored.json")))
N = json.load(open(os.path.join(HERE, "dips-arm/scored-nodips.json")))
E = json.load(open(os.path.join(HERE, "e95.json")))
F = json.load(open(os.path.join(K, "real2/predictions-real2.json")))
R2 = json.load(open(os.path.join(K, "real2/real2.json")))
RJ = json.load(open(os.path.join(K, "real/real.json")))
CAP = json.load(open(os.path.join(K, "real2/capture.json")))
M2 = json.load(open(os.path.join(HERE, "bench-prediction-2b7ece4a.json")))["models"]["vpu_map"]
M4 = json.load(open(os.path.join(HERE, "bench-prediction-m4-b995463e.json")))["e95_aifoundry3"]
DIPS = json.load(open(os.path.join(HERE, "dips-arm/dips.json")))
TL, TN = P["tiles"], N["tiles"]
GL = F["gate_law"]["per_type"]
T = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776}


def pm(m, d=3, sign=False):
    if not m or m.get("mean") is None:
        return "—"
    s = f"{m['mean']:+.{d}f}" if sign else f"{m['mean']:.{d}f}"
    return s + (f" ± {m['ci95']:.{d}f}" if m.get("ci95") is not None else "")


def ols(x, y):
    n = len(x)
    xm, ym = statistics.fmean(x), statistics.fmean(y)
    sxx = sum((a - xm) ** 2 for a in x)
    b = sum((a - xm) * (c - ym) for a, c in zip(x, y)) / sxx
    i = ym - b * xm
    sse = sum((c - i - b * a) ** 2 for a, c in zip(x, y))
    df = n - 2
    se = math.sqrt(sse / df / sxx) if df > 0 else None
    return {"slope": b, "intercept": i, "se": se, "df": df, "half95": None if se is None else T[df] * se}


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def slope_line(label, keys, ty):
    live = [1 - F["tiles"][k]["gated_lane_frac"] for k in keys]
    y = [TL[k.replace("/", ".r2_")]["D"]["mean"] for k in keys]
    o = ols(live, y)
    L = GL[ty]["L_w"]
    own = TL[{"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}[ty]]["D"]["mean"]
    print(f"{label}: slope {o['slope']:.3f} W = {o['slope'] / L:.3f} of E78's L ({L}); ± {(o['half95'] or 0) / L:.3f} over the tiles (df {o['df']}); over E95's own random D ({own:.3f} W) {o['slope'] / own:.3f}; intercept {o['intercept']:.3f} W, G {GL[ty]['G_w']} W")
    return o


print("# E95: corrections-check (corrections-check.py). Nothing here changes a number in e95*.json, runs*.csv, scored*.json, results*.md or the arms.")
print("\n## C1 int8: the five gated tiles")
I8 = ["int8/resnet18_l3c1", "int8/vgg16_fc2", "int8/t5small_l0_down", "int8/vit_l11_down", "int8/gpt2_l11_down_maxabs"]
print("| tile | ReLU | g | live | D W | r | r - live | (a) | (c) | (c') | D-(a) | D-(c) | D-(c') | between (a) and (c) | live lane / random, (D - gG) / ((1 - g)L) | M4 bus term W |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
G, L = GL["int8"]["G_w"], GL["int8"]["L_w"]
ea, ec, ep = [], [], []
for k in I8:
    n = k.replace("/", ".r2_")
    v, t = TL[n], F["tiles"][k]
    g, D, a, c, cp = t["gated_lane_frac"], v["D"]["mean"], t["a_aifoundry3_600mhz"]["D_w"], t["c_gate_law"]["D_w"], t["c_gate_law"]["D_w_with_L_from_e86_real_tiles"]
    ea.append(D - a); ec.append(D - c); ep.append(D - cp)
    print(f"| {n} | {'yes' if t['group'] == 'Z' else 'no'} | {g:.3f} | {1 - g:.3f} | {pm(v['D'])} | {v['r_D']['mean']:.4f} | {v['r_D']['mean'] - (1 - g):+.3f} | {a} | {c} | {cp} | {D - a:+.3f} | {D - c:+.3f} | {D - cp:+.3f} | {'yes' if a < D < c else 'no, above (c)'} | {(D - g * G) / ((1 - g) * L):.3f} | {M4[n]['terms_w'][1]:.2f} |")
print(f"rms: (a) {rms(ea):.3f}, (c) {rms(ec):.3f}, (c') {rms(ep):.3f} W")
o = slope_line("all five", I8, "int8")
slope_line("the three ReLU tiles alone", ["int8/resnet18_l3c1", "int8/vgg16_fc2", "int8/t5small_l0_down"], "int8")
loo = []
for k in I8:
    rest = [x for x in I8 if x != k]
    s = ols([1 - F["tiles"][x]["gated_lane_frac"] for x in rest], [TL[x.replace("/", ".r2_")]["D"]["mean"] for x in rest])["slope"] / L
    loo.append(s)
    print(f"  without {k}: {s:.3f}")
print(f"leave-one-out range {min(loo):.3f}..{max(loo):.3f}")
print(f"if a live lane cost (c')'s L, 5.86 W, the slope would be (5.86 - {G}) / {L} = {(5.86 - G) / L:.3f} of L; the line's intercept {o['intercept']:.2f} W against G {G} W")
print("ungated real int8 tiles, r and bus bits (bits move, gate 0):")
for n in ("int8.r2_gpt2_l11_down_asym", "int8.r2_vgg16_fc2_asym", "int8.r2_gpt2_l11_down_p999", "int8.real_l6_mlp_down", "int8.r2_gpt2_l6_down_per_token", "int8.r2_gpt2_l6_down_p9999", "int8.r2_gpt2_l6_down_p999"):
    print(f"  {n}: r {TL[n]['r_D']['mean']:.4f}, bus {TL[n]['bus_bits_per_op']}, M4 bus term {M4[n]['terms_w'][1]:.2f} W (a model, not a measurement)")
print("C5 stays INCONCLUSIVE:", P["claims"]["C5"]["verdict"])

print("\n## C2 C1's registered reading")
for lab, rep in (("primary", P), ("dips removed", N)):
    cells = rep["claims"]["C1"]["cells"]
    vs = [v["verdict"] for v in cells.values()]
    print(f"{lab}: PASS {vs.count('PASS')}, INCONCLUSIVE {vs.count('INCONCLUSIVE')}, FAIL {vs.count('FAIL')} of {len(vs)}:", "; ".join(f"{k} {pm(v['r'], 4)} [{v['r']['lo']:.4f}, {v['r']['hi']:.4f}] {v['verdict']}" for k, v in cells.items()))
for n in ("fp32.r2_gpt2_l3_mlp_down", "fp32.r2_gpt2_l9_attn_qk", "fp32.r2_bert_l6_up", "fp32.r2_vit_l5_down"):
    v = TN[n]["r_D"]
    print(f"{n}, dips removed: r {pm(v, 4)} [{v['lo']:.4f}, {v['hi']:.4f}]; primary {pm(TL[n]['r_D'], 4)}")
print("other fp32 tiles with no zero word, primary then dips removed:")
for n in ("fp32.r2_gpt2_l6_mlp_down_bf16fwd", "fp32.r2_vit_l11_down", "fp32.r2_t5small_l0_up"):
    print(f"  {n}: gate {TL[n]['gated_lane_frac']}, r {pm(TL[n]['r_D'], 4)}; {pm(TN[n]['r_D'], 4)}")

print("\n## C3 GPT-2's fp16 attention tiles: two windows, three tiles, one model")
w = lambda x: {k: x[k] for k in ("rows", "k", "cols")}
print("fp16.real_l6_attn_qk window", w(RJ["tiles"]["fp16"]["l6_attn_qk"]["window"]))
print("fp16.r2_gpt2_l6_attn_qk_fp16fwd window", w(R2["tiles"]["fp16"]["gpt2_l6_attn_qk_fp16fwd"]["window"]))
print("fp16.r2_gpt2_l9_attn_qk window", w(R2["tiles"]["fp16"]["gpt2_l9_attn_qk"]["window"]))
for n in ("fp16.r2_gpt2_l9_attn_qk", "fp16.real_l6_attn_qk", "fp16.r2_gpt2_l6_attn_qk_fp16fwd", "fp16.r2_bert_l6_up", "fp16.r2_vit_l5_down", "fp16.real_l6_mlp_down", "fp16.r2_gpt2_l6_mlp_down_fp16fwd"):
    print(f"  {n}: r {pm(TL[n]['r_D'], 4)}, dips removed {pm(TN[n]['r_D'], 4)}; M2's nets per op {M2['e95_aifoundry3'][n]['nets_per_op']:,.0f}")

print("\n## C4 the fp16 forward pass: a bound, not an equality")
dense = ["fp16.randn", "fp16.r2_bert_l6_up", "fp16.r2_gpt2_l6_attn_qk_fp16fwd", "fp16.r2_gpt2_l6_mlp_down_fp16fwd", "fp16.r2_gpt2_l9_attn_qk", "fp16.r2_vit_l5_down", "fp16.real_l6_attn_qk", "fp16.real_l6_mlp_down"]
pp = E["per_pass"]
sds = []
for i, a in enumerate(dense):
    for b in dense[i + 1:]:
        d = [pp[p][a]["D"] - pp[p][b]["D"] for p in pp if a in pp[p] and b in pp[p]]
        sds.append((statistics.stdev(d), a, b, len(d)))
sds.sort()
med = statistics.median(s[0] for s in sds)
print(f"{len(sds)} pairs of dense fp16 tiles; paired SD over kept passes: min {sds[0][0]:.3f} ({sds[0][1]} - {sds[0][2]}), median {med:.3f}, max {sds[-1][0]:.3f} W")
own = [s for s in sds if {s[1], s[2]} == {"fp16.r2_gpt2_l6_mlp_down_fp16fwd", "fp16.real_l6_mlp_down"}][0]
oth = [s for s in sds if {s[1], s[2]} == {"fp16.r2_gpt2_l6_attn_qk_fp16fwd", "fp16.real_l6_attn_qk"}][0]
print(f"C11's pair SD {own[0]:.3f} W, rank {[s[1:3] for s in sds].index(own[1:3]) + 1} of {len(sds)}; the attention pair's {oth[0]:.3f} W")
h = med * T[3] / 2
print(f"an interval on the median paired SD at n 4: ± {h:.3f} W, {100 * h / TL['fp16.real_l6_mlp_down']['D']['mean']:.2f}% of D; (a')'s {TL['fp16.r2_gpt2_l6_mlp_down_fp16fwd']['a_prime']['offset_w']} W lies inside it")
print("measured:", pm(P["claims"]["C11"]["diff_w"], 3, True), "W;", pm(TL["fp16.r2_gpt2_l6_attn_qk_fp16fwd"]["a_prime"]["measured_w"], 3, True), "W; dips removed", pm(N["claims"]["C11"]["diff_w"], 3, True), pm(TN["fp16.r2_gpt2_l6_attn_qk_fp16fwd"]["a_prime"]["measured_w"], 3, True))


def fp16_stats(pa, pb):
    a, b = open(os.path.join(K, pa), "rb").read(), open(os.path.join(K, pb), "rb").read()
    n = 512
    A = struct.unpack("<512H", a[:1024])
    B = struct.unpack("<512H", b[:1024])
    diffbits = sum(bin(x ^ y).count("1") for x, y in zip(A, B)) / n
    sign = sum(1 for x, y in zip(A, B) if (x ^ y) & 0x8000) / n
    exp = sum(1 for x, y in zip(A, B) if (x ^ y) & 0x7C00) / n
    same = sum(1 for x, y in zip(A, B) if x == y) / n
    return {"bits_differing_per_element": round(diffbits, 3), "sign_differs": sign, "exponent_differs": round(exp, 4), "identical": round(same, 3), "B_identical": a[1024:] == b[1024:]}


print("MLP tile, A rounded against A from the fp16 pass:", fp16_stats("real/tiles/fp16/l6_mlp_down.bin", "real2/tiles/fp16/gpt2_l6_mlp_down_fp16fwd.bin"))
print("attention tile:", fp16_stats("real/tiles/fp16/l6_attn_qk.bin", "real2/tiles/fp16/gpt2_l6_attn_qk_fp16fwd.bin"))
b1, b2 = TL["fp16.real_l6_mlp_down"]["bus_bits_per_op"], TL["fp16.r2_gpt2_l6_mlp_down_fp16fwd"]["bus_bits_per_op"]
print(f"bus bits {b1} -> {b2}, {100 * (b2 - b1) / b1:+.2f}%; M2 offset {[o['offset_w'] for o in M2['e95_offsets'] if o['tile'] == 'fp16.r2_gpt2_l6_mlp_down_fp16fwd'][0]:+.3f} W; M4 {M4['fp16.r2_gpt2_l6_mlp_down_fp16fwd']['D_w'] - M4['fp16.real_l6_mlp_down']['D_w']:+.3f} W")

print("\n## C5 the bench: which model, chosen how")
FORMS = ["M2 nets,clk", "M2u unit,clk", "bus", "bus+op", "clkt,clkr", "core,bus,exp+ctl,clk", "core,bus,op,clk", "core,bus,rest", "mult", "mult,add", "mult,add,bus", "mult,bus", "scp", "tog"]
print(f"{len(FORMS)} regressions compared in the bench lane's two runs (01:05:27 and 01:06:48 PST, between M2's commit and M4's; copied from its session record, not in this repository): {FORMS}; M4 is 'core,bus,rest'")
blind = [n for n, v in M2["e95_aifoundry3"].items() if v.get("blind")]
e2 = [TL[n]["D"]["mean"] - M2["e95_aifoundry3"][n]["D_w"] for n in blind]
e4 = [TL[n]["D"]["mean"] - M4[n]["D_w"] for n in blind]
ea = [TL[n]["D"]["mean"] - F["tiles"][n.replace(".r2_", "/")]["a_aifoundry3_600mhz"]["D_w"] for n in blind]
se = [TL[n]["D"]["se"] for n in blind]
print(f"30 blind tiles: M2 {rms(e2):.3f}, M4 {rms(e4):.3f}, (a) {rms(ea):.3f} W rms; each tile's D SE over passes: median {statistics.median(se):.3f}, rms {rms(se):.3f} W; M4 net of that {math.sqrt(rms(e4) ** 2 - rms(se) ** 2):.3f} W")
print("constants fitted on E78 alone: floats 4 on 33 kinds, int8 3 on 15 (bench-prediction-m4-b995463e.json families)")

print("\n## C6 'the same numbers' are nested windows, each ratio over its own format's random")


def zero_word_share(path, words_per_line):
    a = open(os.path.join(K, path), "rb").read()[:1024]
    z = n = 0
    for line in range(16):
        for w_ in range(words_per_line):
            word = a[line * 64 + 4 * w_:line * 64 + 4 * w_ + 4]
            n += 1
            z += word == b"\0\0\0\0"
    return z / n


for lay in ("vgg16_fc2", "resnet18_l3c1", "t5small_l0_down"):
    row = []
    for ty, wpl in (("fp32", 16), ("fp16", 8), ("int8", 4)):
        p = f"real2/tiles/{ty}/{lay}.bin"
        row.append(f"{ty}: tile {zero_word_share(p, 16):.3f}, on fp32's 16 k {zero_word_share(p, wpl):.3f}")
    print(f"{lay} zero-word share: " + "; ".join(row))
for lay in ("vgg16_fc2", "resnet18_l3c1", "t5small_l0_down"):
    print(f"{lay}: zero elements in A " + ", ".join(f"{ty} {F['tiles'][ty + '/' + lay]['a_zero_elem_frac']:.3f}" for ty in ("fp32", "fp16", "int8")))
for lay in ("vgg16_fc2", "resnet18_l3c1", "t5small_l0_down"):
    print(f"{lay}: " + "; ".join(f"{ty} D {TL[ty + '.r2_' + lay]['D']['mean']:.2f} W, r {TL[ty + '.r2_' + lay]['r_D']['mean']:.3f} over random {TL[{'fp32': 'fp32.randn', 'fp16': 'fp16.randn', 'int8': 'int8.full'}[ty]]['D']['mean']:.1f} W, live {1 - F['tiles'][ty + '/' + lay]['gated_lane_frac']:.3f}" for ty in ("fp32", "fp16", "int8")))

print("\n## C7 layer 11: a few huge activations, and the gate about half of the lever")
print("the verifier's own forward pass (copied; not in this repository): top |A| 44.08, 43.37, 28.46, 28.29, 13.72, 13.36, 13.07, 13.06; 4 above 20, 19 above 10, 96 above 5, of 393,216; p99.9 3.144")
print("capture.json products.gpt2_l11_mlp_down.stats.A: max_abs", CAP["products"]["gpt2_l11_mlp_down"]["stats"]["A"]["max_abs"], "shape", CAP["products"]["gpt2_l11_mlp_down"]["stats"]["A"]["shape"])
qa = R2["tiles"]["int8"]["gpt2_l11_down_asym"]["quantisation"]["A"]["scale"]
qm = R2["tiles"]["int8"]["gpt2_l11_down_maxabs"]["quantisation"]["A"]["scale"]
print(f"A's scale: max-abs {qm:.4f}, asymmetric {qa:.4f} (ratio {qm / qa:.2f}), p99.9 clip {R2['tiles']['int8']['gpt2_l11_down_p999']['quantisation']['A'].get('scale')}")
s1 = TL["int8.r2_gpt2_l11_down_asym"]["a_prime"]["measured_w"]
s0 = TL["int8.r2_gpt2_l11_down_p999"]["a_prime"]["measured_w"]
d = [pp[p]["int8.r2_gpt2_l11_down_p999"]["D"] - pp[p]["int8.r2_gpt2_l11_down_asym"]["D"] for p in pp]
print(f"max-abs -> asymmetric {pm(s1, 3, True)} W (gate 0.637 -> 0, scale halves); asymmetric -> p99.9 {statistics.fmean(d):+.3f} ± {statistics.stdev(d) / 2 * T[3]:.3f} W (gate 0 on both); max-abs -> p99.9 {pm(s0, 3, True)} W; the first step's share {s1['mean'] / s0['mean']:.2f}")

print("\n## C8 E86's window: the bound on C7's rank")
for lab, rep in (("primary", P), ("dips removed", N)):
    print(lab, "; ".join(f"{k.split('down_')[1]} {pm(v, 3, True)} (n {v['n']})" for k, v in rep["claims"]["C7"]["offsets_w"].items()), "; verdict", rep["claims"]["C7"]["verdict"])
ms = [TN[n]["D"]["mean"] for n in ("int8.real_l6_mlp_down", "int8.r2_gpt2_l6_down_p9999", "int8.r2_gpt2_l6_down_per_token", "int8.r2_gpt2_l6_down_p999")]
print(f"dips removed, the four means {[round(x, 3) for x in ms]}, spread {max(ms) - min(ms):.3f} W; 0.3 W is {100 * 0.3 / statistics.fmean(ms):.1f}% of D")

print("\n## C10 the float slopes, over the tiles")
o32 = slope_line("fp32, 4 tiles", ["fp32/resnet18_l2c1", "fp32/resnet18_l3c1", "fp32/vgg16_fc2", "fp32/t5small_l0_down"], "fp32")
o16 = slope_line("fp16, 3 tiles", ["fp16/resnet18_l3c1", "fp16/vgg16_fc2", "fp16/t5small_l0_down"], "fp16")
print("registered: C3b on the point, 0.955 and 0.933 of E78's L, band [0.85, 1.25], PASS. results.md's per-pass ±0.005, ±0.007, ±0.026 are measurement only: five or fewer fixed tiles re-measured")
print("r - live share, in points of random:", {k: round(TL[k.replace('/', '.r2_')]["r_D"]["mean"] - (1 - F["tiles"][k]["gated_lane_frac"]), 4) for k in ["fp32/resnet18_l2c1", "fp32/resnet18_l3c1", "fp32/vgg16_fc2", "fp32/t5small_l0_down", "fp16/resnet18_l3c1", "fp16/vgg16_fc2", "fp16/t5small_l0_down"]})
print(f"primary slope {E['leak']['k_w_per_c']:.4f} W/C, E78's 0.1994; L is E78's D at its slope, r is E95's D over E95's random")

print("\n## C11 C3a's and C12's intervals are wide")
for k in ("fp32/vgg16_fc2", "fp32/t5small_l0_down", "fp16/vgg16_fc2", "int8/vgg16_fc2"):
    print(k, "law", F["tiles"][k]["c_gate_law"]["scoring_interval_w"], "half", F["tiles"][k]["c_gate_law"]["halfwidth_w"], "(a)", F["tiles"][k]["a_aifoundry3_600mhz"]["scoring_interval_w"], "half", F["tiles"][k]["a_aifoundry3_600mhz"]["scoring_halfwidth_w"])
print("(a)'s half-widths by class:", {k: v["halfwidth_w"] for k, v in F["known_misses"]["classes"].items()})

print("\n## C12 -0.0's scope")
print("tile:", R2["tiles"]["fp32"]["vit_l11_down"]["zero"]["a"]["neg_zero_elem_frac"], "of A's words; the whole block:", CAP["products"]["vit_l11_ff_down"]["stats"]["A"]["neg_zero_frac"])
print("C9: D", pm(P["claims"]["C9"]["D"]), "W; dips removed", pm(N["claims"]["C9"]["D"]), "W; if the gate took it", P["claims"]["C9"]["gate_took_numeric_zero_prediction_w"], "W")

print("\n## C13 small things")
rows = [r for r in csv.DictReader(open(os.path.join(HERE, "runs.csv"))) if r["pass"] == "9510" and r["item"] == "fp32.randn"]


def span(k):
    p = [float(r["p_raw"]) - k * (float(r["t_win"]) - float(r["start_c"])) for r in rows]
    return max(p) - min(p)


for k in (0.2286, 0.25, 0.26, 0.27, 0.2959, 0.1994, 0.0):
    print(f"pass 9510, fp32.randn's span at {k} W/C: {span(k):.3f} W")
A3803 = json.load(open(os.path.join(HERE, "e95-leak0.3803.json")))
print("at 0.3803 the gates keep", A3803["passes"], "and set aside", [(x["pass"], x["why"]) for x in A3803["passes_set_aside"]])
dep = [min(r["neighbours_w"]) - r["board_w"] for v in DIPS["passes"].values() for r in v["rows"]]
print(f"dips: {len(dep)}, depth under the lower neighbour {min(dep):.1f}..{max(dep):.1f} W; definition: board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W (E95.md's '5-20 W' is a paraphrase)")
