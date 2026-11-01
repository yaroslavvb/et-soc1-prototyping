#!/usr/bin/env python3
"""E94: the desk checks and the labelled post-hoc views behind the README. Standard library only; it reads committed files and
changes nothing. No registered number, band or verdict comes from here: sections A, F and G re-derive registered numbers from
the raw table; sections B, C, D, E, H and I are reported views, B and H from frozen rules, C, D, E and I POST HOC.

    python3 docs/reports/data/2026-11-01-e94-tile-spread/check_e94.py > docs/reports/data/2026-11-01-e94-tile-spread/check_e94.txt
"""
import csv
import json
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
reg = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/predictions-e94.json")))
sc = json.load(open(os.path.join(HERE, "scored.json")))
e94 = json.load(open(os.path.join(HERE, "e94.json")))
e78 = json.load(open(os.path.join(ROOT, reg["inputs_frozen"]["e78_reduction"]["path"])))
p88 = json.load(open(os.path.join(ROOT, "tools/claims-v3/rpath/predictions-e88.json")))
P = sc["primary"]
RN = reg["rules_of_number"]
T = reg["tiles"]
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 30: 2.042}


def t975(df):
    d = max(int(df), 1)
    return T975[max(x for x in T975 if x <= d)]


passes = e94["passes"]
print("# check_e94: desk checks and labelled post-hoc views; nothing here changes a registered number")
print(f"passes {passes}; predictions sha256 {sc['predictions_sha256'][:12]}...; scorer sha256 {sc['scorer_sha256'][:12]}...")

# ---------------------------------------------------------------- A: the table, from runs.csv with plain arithmetic
print("\n[A] per rule, re-derived from runs.csv by plain means (no two-way fit: every tile has every pass); against scored.json")
rows = list(csv.DictReader(open(os.path.join(HERE, "runs.csv"))))
cell = {}
for r in rows:
    if int(r["fail"]) == 0 and int(r["pass"]) in passes:
        cell.setdefault((r["item"], int(r["pass"])), []).append(float(r["D"]))
D = {k: sum(v) / len(v) for k, v in cell.items()}
worst = 0.0
for c, r in RN.items():
    draws = r["fresh"] + r["bridge"]
    tiles = [c] + draws
    y = {t: sum(D[(t, p)] for p in passes) / len(passes) for t in tiles}
    grand = sum(y.values()) / len(tiles)
    pm = {p: sum(D[(t, p)] for t in tiles) / len(tiles) for p in passes}
    sse = sum((D[(t, p)] - y[t] - pm[p] + grand) ** 2 for t in tiles for p in passes)
    df = (len(tiles) - 1) * (len(passes) - 1)
    ms = sse / df
    yd = [y[t] for t in draws]
    m, s = st.fmean(yd), st.stdev(yd)
    tau = math.sqrt(max(0.0, s ** 2 - ms / len(passes)))
    off = y[c] - m
    o = P["rules_of_number"][c]
    d = max(abs(m - o["spread"]["mean_w"]), abs(s - o["spread"]["s_w"]), abs(tau - o["spread"]["tau_w"]), abs(off - o["offset_w"]),
            abs(math.sqrt(ms) - o["one_tile_between_pass_sd_w"]))
    worst = max(worst, d)
    print(f"  {c:16s} k {len(draws)} kind {m:7.3f} s {s:.3f} tau {tau:.3f} one tile's between-pass sd {math.sqrt(ms):.3f} committed {y[c]:7.3f} offset {off:+.3f}; largest difference from scored.json {d:.1e}")
print(f"  largest difference over the eight rules: {worst:.1e} W")

# ---------------------------------------------------------------- B: E78's rows
print("\n[B] E78's rows on aifoundry3, by the registered statement: E78's cell minus (offset x E82's card scale), for the bridged rules, because E94-R8 passes")
print("    S and pJ take the same watts; the rate is E78's. +- is the offset's interval x scale, which leaves out E78's own +- (0.06-0.23 W)")
for c, r in RN.items():
    v = P["corrections"][c]
    it = e78["items"][c]
    tr = v.get("translated_to_a3")
    if tr:
        ds = tr["offset_w"]
        S = it["S"]["mean"] - ds
        rate = it["rate"]["mean"]
        macs = it["macs_per_op"]
        print(f"  {c:16s} {v['verdict']:13s} D {it['D']['mean']:7.3f} -> {it['D']['mean'] - ds:7.3f}  S {it['S']['mean']:7.3f} -> {S:7.3f}  +-{tr['halfwidth_w']:.3f}  "
              f"nJ/op {it['pj_op_S']['mean'] / 1000:6.2f} -> {1e9 * S / rate:6.2f}  pJ/MAC {it['pj_mac_S']['mean']:.3f} -> {1e12 * S / rate / macs:.3f}")
    else:
        print(f"  {c:16s} {v['verdict']:13s} D {it['D']['mean']:7.3f} (not translated: {v.get('translated_to_a3_why_not')}); card 1 offset {v['offset_w']:+.3f} +- {v['offset_halfwidth_w']:.3f}")

# ---------------------------------------------------------------- C: POST HOC, the gate share as a control variate
print("\n[C] POST HOC: the kind's mean with the gate law as a control variate: each draw moved to the rule's mean gate share (kinds.json, 400 draws)")
print("    by the frozen law, then averaged. Fitted: the same with each rule's own least-squares slope. Offset interval as R2's, same thresholds, labelled post hoc")
gated = reg["rules"]["E94-R3"]["rules"]
for c in gated:
    r = RN[c]
    draws = r["fresh"] + r["bridge"]
    tm = {t: st.fmean(D[(t, p)] for p in passes) for t in draws + [c]}
    g_c = r["committed_gated_lane_frac"]
    gm = r["replicates"]["gated_lane_frac"]["mean"]
    Dref = r["D_e82_nodips_card1_w"]
    pm = Dref * ((1 - gm) / (1 - g_c) - 1)
    adj = [tm[t] - T[t]["gate_law_delta_card1_w"] + pm for t in draws]
    k = len(adj)
    mean_cv, sd_cv = st.fmean(adj), st.stdev(adj)
    N2 = P["rules_of_number"][c]["ms_res"] / len(passes)
    off = tm[c] - mean_cv
    var = sd_cv ** 2 / k + N2
    dfs = var ** 2 / ((sd_cv ** 2 / k) ** 2 / (k - 1) + N2 ** 2 / P["rules_of_number"][c]["df_res"])
    hw = t975(dfs) * math.sqrt(var)
    b = r["band_w"]
    v = "NO CORRECTION" if abs(off) + hw <= b else ("CORRECTION" if (abs(off) - hw > 0 and abs(off) >= b) else "UNRESOLVED")
    gs = [T[t]["gated_lane_frac"] for t in draws]
    gb, yb = st.fmean(gs), st.fmean(tm[t] for t in draws)
    sxx = sum((x - gb) ** 2 for x in gs)
    slope = sum((x - gb) * (tm[t] - yb) for x, t in zip(gs, draws)) / sxx
    fit = yb + slope * (gm - gb)
    res = [tm[t] - (yb + slope * (x - gb)) for x, t in zip(gs, draws)]
    rs = math.sqrt(sum(x * x for x in res) / (k - 2))
    hwf = t975(k - 2) * rs * math.sqrt(1 / k + (gm - gb) ** 2 / sxx)
    print(f"  {c:16s} draws' mean gate share {gb:.4f}, rule's {gm:.4f}; registered kind {yb:7.3f} +- {P['rules_of_number'][c]['spread']['kind_mean_halfwidth_w']:.3f}; "
          f"law-adjusted {mean_cv:7.3f} +- {t975(k - 1) * sd_cv / math.sqrt(k):.3f}; fitted {fit:7.3f} +- {hwf:.3f}; committed {tm[c]:7.3f}; offset {off:+.3f} +- {hw:.3f} -> {v} (post hoc)")

# ---------------------------------------------------------------- D: POST HOC, the watts per share of lanes gated
print("\n[D] POST HOC: D against gate share inside a rule, all draws: slope +- 95%, against the gate law's frozen slope and D(random) in this session")
for c in gated:
    r = RN[c]
    draws = r["fresh"] + r["bridge"]
    tm = {t: st.fmean(D[(t, p)] for p in passes) for t in draws}
    gs = [T[t]["gated_lane_frac"] for t in draws]
    gb, yb = st.fmean(gs), st.fmean(tm[t] for t in draws)
    sxx = sum((x - gb) ** 2 for x in gs)
    slope = sum((x - gb) * (tm[t] - yb) for x, t in zip(gs, draws)) / sxx
    res = [tm[t] - (yb + slope * (x - gb)) for x, t in zip(gs, draws)]
    k = len(draws)
    se = math.sqrt(sum(x * x for x in res) / (k - 2) / sxx)
    rnd = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}[r["type"]]
    print(f"  {c:16s} k {k} slope {slope:7.2f} +- {t975(k - 2) * se:5.2f} W per unit gate share (residual sd {math.sqrt(sum(x * x for x in res) / (k - 2)):.3f} W); "
          f"gate law's -{r['law_gate']['slope_w_per_unit_live_share']:.2f}; D(random) {P['rules_of_number'][rnd]['committed_D_w']:.2f} W")

print("  the same 24 fresh draws against two one-line laws, D(draw) - D(committed): the frozen law, and POST HOC a gated share priced at D(random) per unit")
fr = []
for c in gated:
    r = RN[c]
    rnd = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}[r["type"]]
    Dr = P["rules_of_number"][rnd]["committed_D_w"]
    yc = st.fmean(D[(c, p)] for p in passes)
    for t in r["fresh"]:
        m = st.fmean(D[(t, p)] for p in passes) - yc
        fr.append((m, T[t]["gate_law_delta_card1_w"], -Dr * (T[t]["gated_lane_frac"] - r["committed_gated_lane_frac"])))
rms = lambda v: math.sqrt(sum(x * x for x in v) / len(v))  # noqa: E731
print(f"  no move {rms([a for a, _, _ in fr]):.3f} W; frozen gate law {rms([a - b for a, b, _ in fr]):.3f} W; D(random) per unit gate share {rms([a - c_ for a, _, c_ in fr]):.3f} W (post hoc: it has seen these draws)")

# ---------------------------------------------------------------- E: POST HOC, dense draws and the bus bits
print("\n[E] POST HOC: inside the dense rules, D against operand-bus bits (draws and the committed tile, centred per rule), against E88's frozen operand-bus price")
RATE = {"fp32": 1024 * 600e6 / 546, "fp16": 1024 * 600e6 / 546, "int8": 1024 * 600e6 / 318}
fit = p88["model"]["fit"]
for lab, group in (("fp32 and fp16", ("fp32.randn", "fp16.randn", "fp16.uniform01")), ("int8", ("int8.full",))):
    sxy = sxx = 0.0
    n = 0
    pts = []
    for c in group:
        r = RN[c]
        tiles = r["fresh"] + r["bridge"] + [c]
        y = [st.fmean(D[(t, p)] for p in passes) for t in tiles]
        x = [(T[t]["bus_bits_per_op"] if t in T else r["committed_bus_bits_per_op"]) for t in tiles]
        xb, yb = st.fmean(x), st.fmean(y)
        pts += [(a - xb, b - yb) for a, b in zip(x, y)]
        n += len(tiles) - 1
    sxx = sum(a * a for a, _ in pts)
    b = sum(a * c_ for a, c_ in pts) / sxx
    res = [c_ - b * a for a, c_ in pts]
    dfr = n - 1
    se = math.sqrt(sum(x * x for x in res) / dfr / sxx)
    print(f"  {lab}: slope {b * 1e6:.1f} +- {t975(dfr) * se * 1e6:.1f} uW per bit/op over {len(pts)} tiles, residual sd {math.sqrt(sum(x * x for x in res) / dfr):.3f} W; E88's frozen price {', '.join(f'{x} {fit[x]["a_fj_per_bus_bit"] * 1e-15 * RATE[x] * 1e6:.1f}' for x in sorted({g.split('.')[0] for g in group}))} uW per bit/op; "
          f"proportional law about {st.fmean(RN[c]['D_e82_nodips_card1_w'] / RN[c]['replicates']['bus_bits_per_op']['mean'] for c in group) * 1e6:.0f} uW per bit/op")
    for c in group:
        ty_ = c.split(".")[0]
        print(f"    {c:16s} kinds.json's bus sd {RN[c]['replicates']['bus_bits_per_op']['sd']:7.0f} x E88's price = {RN[c]['replicates']['bus_bits_per_op']['sd'] * fit[ty_]['a_fj_per_bus_bit'] * 1e-15 * RATE[ty_]:.3f} W; measured tau {P['rules_of_number'][c]['spread']['tau_w']:.3f} W")

# ---------------------------------------------------------------- F: how firm are the two corrections
print("\n[F] how firm are the two CORRECTION rows (registered R2 at the primary, then views of it)")
for c in ("fp32.sparse50", "fp16.nn_like"):
    o = P["rules_of_number"][c]
    print(f"  {c}: primary offset {o['offset_w']:+.3f} +- {o['offset_halfwidth_w']:.3f} -> {o['R2']}; fresh draws only {o['fresh_only']['offset_w']:+.3f} +- {o['fresh_only']['offset_halfwidth_w']:.3f} -> {o['fresh_only']['R2']}")
    print("    at the arms: " + "; ".join(f"{a} {v['rules_of_number'][c]['offset_w']:+.3f} +- {v['rules_of_number'][c]['offset_halfwidth_w']:.3f} {v['rules_of_number'][c]['R2']}" for a, v in sc["arms"].items()))
    r = RN[c]
    draws = r["fresh"] + r["bridge"]
    per = {p: D[(c, p)] - st.fmean(D[(t, p)] for t in draws) for p in passes}
    print("    offset, pass by pass: " + ", ".join(f"{p} {v:+.3f}" for p, v in per.items()) + "; committed tile's D by pass: " + ", ".join(f"{D[(c, p)]:.3f}" for p in passes))
    own = st.stdev(D[(c, p)] for p in passes)
    s2k = o["spread"]["s_w"] ** 2 / o["spread"]["k"]
    v2 = s2k + own ** 2 / len(passes)
    dfs = v2 ** 2 / (s2k ** 2 / (o["spread"]["k"] - 1) + (own ** 2 / len(passes)) ** 2 / (len(passes) - 1))
    print(f"    with the committed tile's own between-pass sd ({own:.3f} W) in place of the pooled one: +- {t975(dfs) * math.sqrt(v2):.3f} (df {dfs:.1f})")
e93p = os.path.join(ROOT, "docs/reports/data/2026-11-01-e93-zero-gate-silicon/e93.json")
if os.path.exists(e93p):
    e93 = json.load(open(e93p))
    v = e93["items"]["fp32.sparse50"]["D"]
    print(f"  the same committed fp32.sparse50 tile in E93's session on this card (read only after E94's data; not in any rule): {v['mean']:.3f} +- {v['ci95']:.3f} W, {v['n']} passes; E94 {st.fmean(D[('fp32.sparse50', p)] for p in passes):.3f}")
c = "fp16.nn_like"
r = RN[c]
draws = [t for t in r["fresh"] + r["bridge"] if t != "fp16.nn_like_e94d1"]
yd = [st.fmean(D[(t, p)] for p in passes) for t in draws]
print(f"  fp16.nn_like without the one draw outside the rule's band (e94d1): kind {st.fmean(yd):.3f}, offset {st.fmean(D[(c, p)] for p in passes) - st.fmean(yd):+.3f}, s {st.stdev(yd):.3f}, k {len(yd)}")

# ---------------------------------------------------------------- G: R1's tests
print("\n[G] R1: the committed tile's t against one more draw, its p, Holm over eight, and its rank among the rule's tiles")
ps = sorted((P["rules_of_number"][c]["p_vs_one_more_draw"], c) for c in RN)
for i, (p, c) in enumerate(ps):
    r = RN[c]
    draws = r["fresh"] + r["bridge"]
    yc = st.fmean(D[(c, q)] for q in passes)
    above = sum(1 for t in draws if st.fmean(D[(t, q)] for q in passes) > yc)
    print(f"  {c:16s} t {P['rules_of_number'][c]['t_vs_one_more_draw']:+.2f} p {p:.3f} Holm threshold {0.05 / (8 - i):.4f} {'resolved' if p < 0.05 / (8 - i) else 'not resolved'}; {above} of {len(draws)} draws read above the committed tile; R1 {P['rules_of_number'][c]['R1']}")

# ---------------------------------------------------------------- H: the desk table
print(f"\n[H] the frozen desk table (predictions-e94.json desk_table): may it speak? E94-R6 {P['rules']['E94-R6']['verdict']}, E94-R9 gate law {P['rules']['E94-R9:gate_law']['verdict']} -> {P['desk_table_may_speak']}")
print("    random rows no card ran here, on aifoundry3's scale, with an offset of at least half the band by either law; PREDICTED, never measured here")
for n, d in reg["desk_table"].items():
    if d["measured_by_e94"] or d["gated_committed"] >= 1.0 or d.get("gate_law_sd_a3_w") is None:
        continue
    b = 0.25 if n.startswith("int8") else 0.5
    og, oq = d["gate_law_committed_minus_mean_a3_w"], d["q130n_committed_minus_mean_a3_w"]
    if max(abs(og), abs(oq)) >= b / 2:
        print(f"  {n:20s} E78 D {d['D_e78_a3_w']:6.2f}; offset gate law {og:+.2f}, Q130(n) {oq:+.2f} (band +-{b}); SD gate law {d['gate_law_sd_a3_w']:.2f}, Q130(n) {d['q130n_sd_a3_w']:.2f}; {'at or past the band by both' if min(abs(og), abs(oq)) >= b else ('past the band by one' if max(abs(og), abs(oq)) >= b else 'inside the band')}")
print("    every other random row's SD, for the page's dagger: " + ", ".join(f"{n} {d.get('gate_law_sd_a3_w', 0):.2f}/{d['q130n_sd_a3_w']:.2f}" for n, d in reg["desk_table"].items() if not d["measured_by_e94"] and d["gated_rule_mean"] > 0 and d["gated_committed"] < 1.0))

# ---------------------------------------------------------------- I: the bridge
print("\n[I] the bridge, POST HOC views: R8 without its largest difference, and a kind's mean on aifoundry3 two ways")
rows8 = P["rules"]["E94-R8"]["draws"]
diffs = sorted((abs(v["difference_w"]), n) for n, v in rows8.items())
rest = [v["difference_w"] for n, v in rows8.items() if n != diffs[-1][1]]
print(f"  rms over nine {P['rules']['E94-R8']['rms_w']:.3f} W; largest {diffs[-1][1]} {rows8[diffs[-1][1]]['difference_w']:+.3f} W (its aifoundry3 SE {rows8[diffs[-1][1]]['offset_a3_se_w']:.3f}); without it {math.sqrt(sum(x * x for x in rest) / len(rest)):.3f} W")
for c in reg["rules"]["E94-R3"]["rules"] + ["fp16.uniform01"]:
    v = P["corrections"][c]
    if v.get("translated_to_a3"):
        print(f"  {c:16s} E78 {v['D_e78_a3_w']:.3f}; translated kind {v['translated_to_a3']['kind_D_w']:.3f} +- {v['translated_to_a3']['halfwidth_w']:.3f}; E90's own three draws' mean on aifoundry3 {v['e90_a3_draws_mean_w']:.3f}, E90's committed {v['e90_a3_committed_w']:.3f}")
