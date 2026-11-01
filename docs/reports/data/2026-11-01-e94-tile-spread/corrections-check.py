#!/usr/bin/env python3
"""E94: the desk check behind § Corrections after verification. It reads committed files and changes nothing; no card, no
re-run, and no registered number, band or verdict comes from here. Every number the corrections cite is printed under its
C-number. Standard library only; it reuses score_e94.py's own two_way, spread and interval code.

    python3 docs/reports/data/2026-11-01-e94-tile-spread/corrections-check.py > docs/reports/data/2026-11-01-e94-tile-spread/corrections-check.txt
"""
import csv
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools/claims-v3/kinds"))
import score_e94 as sm  # noqa: E402


def load(rel):
    return json.load(open(os.path.join(REPO, rel)))


reg = load("tools/claims-v3/kinds/predictions-e94.json")
kinds = load("tools/claims-v3/kinds/kinds.json")
sc = json.load(open(os.path.join(HERE, "scored.json")))
e94 = json.load(open(os.path.join(HERE, "e94.json")))
e78 = load(reg["inputs_frozen"]["e78_reduction"]["path"])
s90 = load(reg["inputs_frozen"]["e90_scored"]["path"])
P = sc["primary"]
RO, RR = P["rules_of_number"], P["rules"]
RN, T, DT = reg["rules_of_number"], reg["tiles"], reg["desk_table"]
passes = e94["passes"]
GATED = reg["rules"]["E94-R3"]["rules"]
FLOAT_GATED = reg["rules"]["E94-R7"]["rules"]
rand_of = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
zero_of = {"fp32": "fp32.zeros", "fp16": "fp16.zeros", "int8": "int8.zeros"}
rows = [r for r in csv.DictReader(open(os.path.join(HERE, "runs.csv"))) if int(r["fail"]) == 0]


def tm(c, res=e94, ps=passes, key="D"):
    return st.fmean(res["per_pass"][str(p)][c][key] for p in ps)


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def line(c):
    """OLS of the draws' mean D on their gate share, inside a rule: (slope, its 95% half-width, D at g=1, its half-width, residual sd, ḡ, Sxx)."""
    r = RN[c]
    draws = r["fresh"] + r["bridge"]
    y = [tm(t) for t in draws]
    g = [T[t]["gated_lane_frac"] for t in draws]
    gb, yb = st.fmean(g), st.fmean(y)
    sxx = sum((x - gb) ** 2 for x in g)
    b = sum((x - gb) * (v - yb) for x, v in zip(g, y)) / sxx
    res = [v - (yb + b * (x - gb)) for x, v in zip(g, y)]
    k = len(y)
    rs = math.sqrt(sum(x * x for x in res) / (k - 2))
    tq = sm.t975(k - 2)
    return b, tq * rs / math.sqrt(sxx), yb + b * (1 - gb), tq * rs * math.sqrt(1 / k + (1 - gb) ** 2 / sxx), rs, gb, sxx


print("# E94 corrections-check: every number § Corrections after verification cites, from committed files; it changes nothing")
print(f"passes {passes}; scored.json's predictions sha256 {sc['predictions_sha256'][:12]}...; scorer {sc['scorer_sha256'][:12]}...")

# ------------------------------------------------------------------------------------ C1
print("\n[C1] the page's † rows: every kind of kinds.json whose gate share moves with the draw (replicates' gate-share sd > 0)")
dag = []
for t in ("fp32", "fp16", "int8"):
    for kind, v in kinds["kinds"][t].items():
        rep = v.get("replicates") or {}
        g = rep.get("gated_lane_frac")
        if g and g["sd"] > 0:
            dag.append((f"{t}.{kind}", g["mean"], g["sd"]))
print(f"  {len(dag)} rows; measured by E94: {sum(1 for n, _, _ in dag if n in RN)}")
for n, gm, gs in sorted(dag, key=lambda x: -x[1]):
    if n in RO:
        o = RO[n]
        s = o["spread"]
        b = line(n)[0]
        print(f"  {n:16s} gates {100 * gm:5.1f}%  MEASURED tau {s['tau_w']:.3f} [{s['tau_ci95_w'][0]:.3f}, {s['tau_ci95_w'][1]:.3f}] W; 1.96 tau {1.96 * s['tau_w']:.2f} W; registered PI +-{o['prediction_interval_w']:.2f} W; "
              f"post hoc slope x kinds.json's gate-share sd {abs(b) * gs:.3f} W; frozen SD gate law {RN[n]['law_gate']['sd_card1_w']:.2f}, Q130(n) {RN[n]['law_q130n']['sd_card1_w']:.2f}")
    else:
        d = DT[n]
        print(f"  {n:16s} gates {100 * gm:5.1f}%  predicted SD on aifoundry3's scale: gate law {d['gate_law_sd_a3_w']:.2f}, Q130(n) {d['q130n_sd_a3_w']:.2f} W; E78 D {d['D_e78_a3_w']:.2f} W")
others = [n for n, gm, _ in dag if n not in RO and not (n.startswith("fp") and 0.25 <= round(gm, 2) <= 0.75)]
print(f"  float rows gating 25-75%: measured {[n for n, gm, _ in dag if n in RO and n.startswith('fp') and 0.24 <= gm <= 0.76]}; predicted {[n for n, gm, _ in dag if n not in RO and n.startswith('fp') and 0.24 <= gm <= 0.76]}")
print(f"  the other unmeasured rows ({len(others)}): largest predicted SD {max(max(DT[n]['gate_law_sd_a3_w'], DT[n]['q130n_sd_a3_w']) for n in others):.2f} W, smallest {min(min(DT[n]['gate_law_sd_a3_w'], DT[n]['q130n_sd_a3_w']) for n in others):.2f} W")

# ------------------------------------------------------------------------------------ C2, C3
print("\n[C2] R2 by row: " + ", ".join(f"{c} {o['R2']}" for c, o in RO.items()))
print(f"  resolved {sum(1 for o in RO.values() if o['R2'] != 'UNRESOLVED')} of {len(RO)}; bridged and translated: {[c for c, v in P['corrections'].items() if v.get('translated_to_a3')]}")
o = RO["fp32.nn_like"]
print(f"\n[C3] fp32.nn_like on card 1: kind D {o['spread']['mean_w']:.3f} +- {o['spread']['kind_mean_halfwidth_w']:.3f} W, S {o['kind_S_w']['mean_w']:.3f} +- {o['kind_S_w']['halfwidth_w']:.3f} W; committed D {o['committed_D_w']:.3f}, S {o['committed_S_w']['mean']:.3f}; translated: {P['corrections']['fp32.nn_like'].get('translated_to_a3')}")

# ------------------------------------------------------------------------------------ C4
print("\n[C4] the two CORRECTION tiles are ordinary draws: R1's p, and the committed tile's z in kinds.json's 400 draws")
for c in ("fp32.sparse50", "fp16.nn_like"):
    rep = RN[c]["replicates"]["gated_lane_frac"]
    print(f"  {c:16s} R1 {RO[c]['R1']}, p {RO[c]['p_vs_one_more_draw']:.3f}; gate share {RN[c]['committed_gated_lane_frac']:.4f} against the rule's {rep['mean']:.4f} (sd {rep['sd']:.4f}): z {(RN[c]['committed_gated_lane_frac'] - rep['mean']) / rep['sd']:+.2f}, band [{rep['p2.5']:.3f}, {rep['p97.5']:.3f}]")
print(f"  rows: 2 CORRECTION, 5 NO CORRECTION, 1 UNRESOLVED of the 8 re-drawn, of E78's {len(e78['items']) - 1} kinds")

# ------------------------------------------------------------------------------------ C5
print("\n[C5] what the spread rests on")
print(f"  int8.sparse50 has random zeros and tau {RO['int8.sparse50']['spread']['tau_w']:.3f} W")
print("  R3 is a wide interval: " + "; ".join(f"{c} expected {RR['E94-R3:' + c]['expected_sd_w']:.2f} in [{RR['E94-R3:' + c]['tau_ci95_w'][0]:.2f}, {RR['E94-R3:' + c]['tau_ci95_w'][1]:.2f}]" for c in GATED))
g7 = RR["E94-R7:gate_law"]
print(f"  R7, gate law: centred residual {g7['residual_rms_w']:.3f} W of a centred SD {g7['centred_sd_w']:.3f} W over {g7['df']} df, 18 fresh draws")

# ------------------------------------------------------------------------------------ C6
print("\n[C6] the law is local, and power is not proportional to the live share")
for c in GATED:
    b, hb, d1, h1, rs, gb, sxx = line(c)
    r = RN[c]
    draws = r["fresh"] + r["bridge"]
    ym = st.fmean(tm(t) for t in draws)
    gs = [T[t]["gated_lane_frac"] for t in draws]
    print(f"  {c:16s} kind D {ym:.3f} / live share {1 - gb:.4f} = {ym / (1 - gb):.2f} W; D(random) {tm(rand_of[r['type']]):.2f} W; the draws' line: slope {b:.2f} +- {hb:.2f} W per unit, D at g = 1 {d1:+.2f} +- {h1:.2f} W; "
          f"draws span g {min(gs):.3f}-{max(gs):.3f}, up to {max(abs(x - r['committed_gated_lane_frac']) for x in gs):.3f} from the committed tile")
c = "fp32.sparse50"
print(f"  with fp32.sparse50's intercept, slope from E82's D: ({RN[c]['D_e82_nodips_card1_w']:.2f} - {line(c)[2]:.2f}) / {1 - RN[c]['committed_gated_lane_frac']:.3f} = {(RN[c]['D_e82_nodips_card1_w'] - line(c)[2]) / (1 - RN[c]['committed_gated_lane_frac']):.1f} W per unit")
L = P["reported_laws_on_fresh_draws"]["gated"]
print(f"  24 fresh gated draws: gate law {L['gate_law_delta_w_rms_w']:.3f} W, no move against the committed tile {L['no_offset_rms_w']:.3f} W, the draws about their own kind (centred) {L['gate_law_delta_w_centred']['centred_sd_w']:.3f} W, gate law centred {L['gate_law_delta_w_centred']['residual_rms_w']:.3f} W, Q130(n) centred {L['q130n_delta_w_centred']['residual_rms_w']:.3f} W")
rb = {c: (RR["E94-R5"]["rms_by_rule"][c], RR["E94-R6"]["rms_by_rule"][c]) for c in GATED}
print("  Q130(n) against the gate law, rms by rule: " + "; ".join(f"{c} {a:.3f} / {b_:.3f}" for c, (a, b_) in rb.items()))

# ------------------------------------------------------------------------------------ C7
print("\n[C7] the gate law's two other readings")
e93 = load("docs/reports/data/2026-11-01-e93-zero-gate-silicon/e93.json")
p93 = load("tools/claims-v3/kinds/predictions-e93.json")
print(f"  E93 (registered before this lane began): int8.b_pairs_rtl predicted {p93['tiles']['int8.b_pairs_rtl']['point_w']:.2f} W by live share x cost, read {e93['items']['int8.b_pairs_rtl']['D']['mean']:.2f} W: +{e93['items']['int8.b_pairs_rtl']['D']['mean'] - p93['tiles']['int8.b_pairs_rtl']['point_w']:.2f} W")
br = [t for c in ("fp32.sparse50", "fp16.nn_like") for t in RN[c]["bridge"]]
print(f"  the gate law on E90's six gated draws read on card 1 (left out of R6, which takes fresh draws only): {rms([(tm(t) - tm(T[t]['rule_of'])) - T[t]['gate_law_delta_card1_w'] for t in br]):.3f} W; on the 24 fresh {L['gate_law_delta_w_rms_w']:.3f} W")
print(f"  R9 on fresh draws alone (it scores all draws): gate law {rms([(tm(c) - st.fmean(tm(t) for t in RN[c]['fresh'])) - RN[c]['law_gate']['committed_minus_mean_card1_w'] for c in GATED]):.3f} W")

# ------------------------------------------------------------------------------------ C8
print("\n[C8] aifoundry3, S and the gate share of the two corrected rows")
for c in ("fp16.nn_like", "fp32.sparse50"):
    r = RN[c]
    it = e78["items"][c]
    tr = P["corrections"][c]["translated_to_a3"]
    gm, g_c = r["replicates"]["gated_lane_frac"]["mean"], r["committed_gated_lane_frac"]
    # post hoc 1: the control variate on card 1, translated
    draws = r["fresh"] + r["bridge"]
    pm = r["D_e82_nodips_card1_w"] * ((1 - gm) / (1 - g_c) - 1)
    cv = st.fmean(tm(t) - T[t]["gate_law_delta_card1_w"] + pm for t in draws)
    off_cv = (tm(c) - cv) * r["scale"]
    # post hoc 2: E90's own three draws on aifoundry3, moved to the rule's mean share by the law, anchored on E78's cell
    law = lambda g: it["D"]["mean"] * ((1 - g) / (1 - g_c) - 1)  # noqa: E731
    adj = st.fmean(reg["bridge"][t]["offset_a3_w"] - law(T[t]["gated_lane_frac"]) + law(gm) for t in r["bridge"])
    se = it["S"]["ci95"]
    print(f"  {c:16s} E78 S {it['S']['mean']:.2f}; kind's S: registered, translated {it['S']['mean'] - tr['offset_w']:.2f} +- {tr['halfwidth_w']:.2f} (with E78's own +-{se:.2f}: +-{math.hypot(tr['halfwidth_w'], se):.2f}); "
          f"E90's three draws law-adjusted {it['S']['mean'] + adj:.2f}; control variate translated {it['S']['mean'] - off_cv:.2f}. D the same way: {it['D']['mean'] - tr['offset_w']:.2f}, {it['D']['mean'] + adj:.2f}, {it['D']['mean'] - off_cv:.2f}")
    rate, macs = it["rate"]["mean"], it["macs_per_op"]
    print(f"    nJ/op {1e9 * (it['S']['mean'] - tr['offset_w']) / rate:.2f} to {1e9 * (it['S']['mean'] - off_cv) / rate:.2f}; pJ/MAC {1e12 * (it['S']['mean'] - tr['offset_w']) / rate / macs:.3f} to {1e12 * (it['S']['mean'] - off_cv) / rate / macs:.3f}; "
          f"gate closes: committed tile {100 * g_c:.1f}%, the kind {100 * gm:.1f}%")
print("  the bridge by rule, and the translation's scale:")
for c in reg["rules"]["E94-R8"].get("rules", ()) or ("fp32.sparse50", "fp16.nn_like", "fp16.uniform01"):
    ds = [v["difference_w"] for n, v in RR["E94-R8"]["draws"].items() if T[n]["rule_of"] == c]
    print(f"    {c:16s} rms {rms(ds):.3f} W, mean difference {st.fmean(ds):+.3f} W")
xs = [v["offset_card1_w"] for v in RR["E94-R8"]["draws"].values()]
ys = [v["offset_a3_w"] for v in RR["E94-R8"]["draws"].values()]
sxx = sum(x * x for x in xs)
b = sum(x * y for x, y in zip(xs, ys)) / sxx
se = math.sqrt(sum((y - b * x) ** 2 for x, y in zip(xs, ys)) / (len(xs) - 1) / sxx)
print(f"    aifoundry3's offsets on card 1's, through the origin: slope {b:.2f} +- {sm.t975(len(xs) - 1) * se:.2f} (95%), against E82's scale of about 1.03")

# ------------------------------------------------------------------------------------ C9
d = DT["fp16.sparse50"]
it = e78["items"]["fp16.sparse50"]
print(f"\n[C9] fp16 50% zeros, predicted: D {d['D_e78_a3_w']:.2f} -> {d['D_e78_a3_w'] - d['gate_law_committed_minus_mean_a3_w']:.2f} to {d['D_e78_a3_w'] - d['q130n_committed_minus_mean_a3_w']:.2f} W; "
      f"S {it['S']['mean']:.2f} -> {it['S']['mean'] - d['gate_law_committed_minus_mean_a3_w']:.2f} to {it['S']['mean'] - d['q130n_committed_minus_mean_a3_w']:.2f} W; offset {d['gate_law_committed_minus_mean_a3_w']:+.3f}, {d['q130n_committed_minus_mean_a3_w']:+.3f} against +-0.50 W; gate closes: committed {100 * d['gated_committed']:.1f}%, the rule {100 * d['gated_rule_mean']:.1f}%")

# ------------------------------------------------------------------------------------ C10
print("\n[C10] how firm is fp32.sparse50's CORRECTION; every view by score_e94's own arithmetic, none a registered verdict")


def view(c, draws=None, ps=passes, res=e94):
    r = dict(RN[c])
    o = sm.rule_stats(res, c, r, ps, draws if draws is not None else RN[c]["fresh"] + RN[c]["bridge"], 2)
    return o


for c in ("fp32.sparse50", "fp16.nn_like"):
    print(f"  {c}: leave one draw out:")
    draws = RN[c]["fresh"] + RN[c]["bridge"]
    for t in draws:
        o = view(c, [x for x in draws if x != t])
        print(f"    without {t:24s} (g {T[t]['gated_lane_frac']:.4f}): kind {o['spread']['mean_w']:.3f}, offset {o['offset_w']:+.3f} +- {o['offset_halfwidth_w']:.3f} {o['R2']}")
    for q in passes:
        o = view(c, ps=[p for p in passes if p != q])
        print(f"    without pass {q}: offset {o['offset_w']:+.3f} +- {o['offset_halfwidth_w']:.3f} {o['R2']}")
    o = view(c)
    print(f"    primary {o['offset_w']:+.3f} +- {o['offset_halfwidth_w']:.3f}; offset / its SE {o['offset_w'] / (o['offset_halfwidth_w'] / sm.t975(o['offset_df'])):+.2f} on {o['offset_df']:.1f} df, p {sm.two_sided_t_p(o['offset_w'] / (o['offset_halfwidth_w'] / sm.t975(o['offset_df'])), o['offset_df']):.4f}")
    # other frames: S, the rail, and the pass's mean zeros instead of E78's interpolated zeros
    fS = {"per_pass": {str(p): {t: {"D": e94["per_pass"][str(p)][t]["S"]} for t in e94["per_pass"][str(p)]} for p in passes}}
    fR = {"per_pass": {str(p): {t: {"D": (e94["per_pass"][str(p)][t]["Drail"] or 0.0) / 0.81} for t in e94["per_pass"][str(p)]} for p in passes}}
    ty = RN[c]["type"]
    zm = {p: st.fmean(float(r["p80"]) for r in rows if r["item"] == zero_of[ty] and int(r["pass"]) == p) for p in passes}
    pm_ = {}
    for r in rows:
        if r["type"] == ty:
            pm_.setdefault(int(r["pass"]), {}).setdefault(r["item"], []).append(float(r["p80"]) - zm[int(r["pass"])])
    fZ = {"per_pass": {str(p): {t: {"D": st.fmean(v)} for t, v in pm_[p].items()} for p in passes}}
    for lab, f_ in (("S", fS), ("minion rail / 0.81", fR), ("the pass's mean zeros", fZ)):
        o = view(c, res=f_)
        print(f"    frame {lab}: offset {o['offset_w']:+.3f} +- {o['offset_halfwidth_w']:.3f}")
print("  position in the pass: E78's interpolation is flat before a pass's first zeros anchor, so items ahead of it inherit that anchor's reading")
ty = "fp32"
for p in passes:
    rp = [r for r in rows if int(r["pass"]) == p and r["type"] == ty]
    z = sorted((int(r["pos"]), float(r["p80"])) for r in rp if r["item"] == "fp32.zeros")
    first = z[0][0]
    before = [r for r in rp if int(r["pos"]) < first and r["item"] not in ("fp32.zeros",)]
    deltas, tiles_only = [], []
    for r in before:
        oth = [e94["per_pass"][str(q)][r["item"]]["D"] for q in passes if q != p and r["item"] in e94["per_pass"][str(q)]]
        deltas.append(float(r["D"]) - st.fmean(oth))
        if r["item"] not in ("anchor_pi", "fp32.randn"):
            tiles_only.append(deltas[-1])
    ps = [int(r["pos"]) for r in rp if r["item"] == "fp32.sparse50"]
    print(f"    pass {p}: fp32.zeros at #{[x for x, _ in z]} read {[round(v, 2) for _, v in z]} W; {len(before)} fp32 runs ahead of it read {st.fmean(deltas) if deltas else 0:+.3f} W against their other passes ({len(tiles_only)} without the tie and the random anchor: {st.fmean(tiles_only) if tiles_only else 0:+.3f} W); the committed fp32.sparse50 ran at #{ps}, D {e94['per_pass'][str(p)]['fp32.sparse50']['D']:.3f}")

# ------------------------------------------------------------------------------------ C11
print("\n[C11] the post-hoc intervals with the rule's mean gate share's own error (its SE over 400 draws, at the frozen slope)")
for c in ("fp32.sparse50", "fp16.nn_like", "fp32.nn_like", "int8.sparse50"):
    r = RN[c]
    gsd = r["replicates"]["gated_lane_frac"]["sd"]
    slope = r["law_gate"]["slope_w_per_unit_live_share"]
    extra = 1.96 * slope * gsd / math.sqrt(400)
    draws = r["fresh"] + r["bridge"]
    gm, g_c = r["replicates"]["gated_lane_frac"]["mean"], r["committed_gated_lane_frac"]
    pm = r["D_e82_nodips_card1_w"] * ((1 - gm) / (1 - g_c) - 1)
    adj = [tm(t) - T[t]["gate_law_delta_card1_w"] + pm for t in draws]
    hw = sm.t975(len(adj) - 1) * st.stdev(adj) / math.sqrt(len(adj))
    tot = math.hypot(hw, extra)
    N2 = RO[c]["ms_res"] / len(passes)
    off = tm(c) - st.fmean(adj)
    k = len(adj)
    var = st.variance(adj) / k + N2
    dfs = var ** 2 / ((st.variance(adj) / k) ** 2 / (k - 1) + N2 ** 2 / RO[c]["df_res"])
    hw_off = sm.t975(dfs) * math.sqrt(var)
    tot_off = math.hypot(hw_off, extra)
    b = RN[c]["band_w"]
    v = "NO CORRECTION" if abs(off) + tot_off <= b else ("CORRECTION" if (abs(off) - tot_off > 0 and abs(off) >= b) else "UNRESOLVED")
    print(f"  {c:16s} law-adjusted kind {st.fmean(adj):.3f} +- {hw:.3f} W; SE of the rule's mean share {gsd / 20:.5f} -> +-{extra:.3f} W; together +-{tot:.3f} W; committed - kind {off:+.3f} +- {hw_off:.3f}, with it +-{tot_off:.3f} W -> {v}; tightening of the registered interval {RO[c]['spread']['kind_mean_halfwidth_w'] / tot:.1f}x")

# ------------------------------------------------------------------------------------ C12
print("\n[C12] the small ones")
print("  the offset against zero, all eight rows: " + "; ".join(f"{c} p {sm.two_sided_t_p(o_['offset_w'] / (o_['offset_halfwidth_w'] / sm.t975(o_['offset_df'])), o_['offset_df']):.4f}" for c, o_ in RO.items()))
for k_ in (9, 6, 4):
    print(f"  chi-squared factor on an SD, k = {k_}: {math.sqrt((k_ - 1) / sm.chi2_ppf(k_ - 1, 0.975)):.2f} to {math.sqrt((k_ - 1) / sm.chi2_ppf(k_ - 1, 0.025)):.2f}")
nod = load(reg["inputs_frozen"]["e82_nodips"]["path"])
kd = nod["leak"]["k_w_per_c"]
print(f"  E82's dips-removed reference was reduced at {kd:.4f} W/C, E94's primary at 0.2414: on the tie's cells " + ", ".join(f"{c} {(kd - 0.2414) * ((nod['items'][c]['dT_win']['mean'] or 0) - (nod['items'][zero_of[nod['items'][c]['type']]]['dT_win']['mean'] or 0)):.3f} W" for c in reg["session_tie"]["cells"]))
pts = {}
for lab, drop in (("all 20 tiles", None), ("without the committed fp16.uniform01", "fp16.uniform01")):
    xy = []
    n = 0
    for c in ("fp32.randn", "fp16.randn", "fp16.uniform01"):
        r = RN[c]
        tiles = r["fresh"] + r["bridge"] + ([c] if c != drop else [])
        y = [tm(t) for t in tiles]
        x = [T[t]["bus_bits_per_op"] if t in T else r["committed_bus_bits_per_op"] for t in tiles]
        xb, yb = st.fmean(x), st.fmean(y)
        xy += [(a - xb, b_ - yb) for a, b_ in zip(x, y)]
        n += len(tiles) - 1
    sxx = sum(a * a for a, _ in xy)
    b = sum(a * c_ for a, c_ in xy) / sxx
    res = [c_ - b * a for a, c_ in xy]
    se = math.sqrt(sum(x * x for x in res) / (n - 1) / sxx)
    print(f"  dense float slope on bus bits, {lab}: {b * 1e6:.1f} +- {sm.t975(n - 1) * se * 1e6:.1f} uW per bit/op")
