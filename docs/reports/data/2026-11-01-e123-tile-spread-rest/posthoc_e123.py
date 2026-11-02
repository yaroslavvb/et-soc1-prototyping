#!/usr/bin/env python3
"""E123 (Q134): desk views after the registered scoring, labelled post hoc. Standard library only; it changes nothing.

    python3 docs/reports/data/2026-11-01-e123-tile-spread-rest/posthoc_e123.py > docs/reports/data/2026-11-01-e123-tile-spread-rest/posthoc_e123.txt

A  each rule's offset and R2 at every arm (the range the arms span)
B  the page's frame: E78's S (the page's cell) less the measured offset, beside this session's kind's S
C  fp32 ReLU x small weights on two cards: E94's card-1 kind's mean (registered; post hoc) x E82's fp32 scale, against E123's
D  the dagger note's numbers: per-rule and pooled between-draw SD, E94's beside
E  fp16 50% zeros: E94's predicted page note against the measurement
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sc = json.load(open(os.path.join(HERE, "scored.json")))
reg = json.load(open(os.path.join(ROOT, "tools/claims-v3/e123/predictions-e123.json")))
e94 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-01-e94-tile-spread/scored.json")))
P = sc["primary"]
RN = reg["rules_of_number"]

print("[A] offset (W) and R2 at each arm")
arms = ["primary"] + list(sc["arms"])
for c in RN:
    row = []
    lo, hi = None, None
    for a in arms:
        o = P["rules_of_number"][c] if a == "primary" else sc["arms"][a]["rules_of_number"].get(c, {})
        off, v = o.get("offset_w"), o.get("R2")
        if off is not None:
            lo = off if lo is None else min(lo, off)
            hi = off if hi is None else max(hi, off)
        row.append(f"{a}={off:+.3f}:{v}" if off is not None else f"{a}=-")
    print(f"  {c:16s} range [{lo:+.3f}, {hi:+.3f}]  " + "  ".join(row))

print("\n[B] the page's frame (E78's S, the page's cell, less the measured offset) beside this session's kind's S")
for c, o in P["rules_of_number"].items():
    if "offset_w" not in o:
        continue
    s78 = RN[c]["e78_a3"]["S_w"]
    print(f"  {c:16s} page S {s78:6.2f}; page S - offset {s78 - o['offset_w']:6.2f} +- {o['offset_halfwidth_w']:.2f}; "
          f"this session: committed S {o['committed_S_w']['mean']:6.2f}, kind's S {o['kind_S_w']['mean_w']:6.2f}")

print("\n[C] fp32 ReLU x small weights (fp32.nn_like) on two cards, D over fp32 zeros")
r94 = e94["primary"]["rules_of_number"]["fp32.nn_like"]
scale = reg["bridge"]["card_scale_fp32"]
km, khw = r94["spread"]["mean_w"], r94["spread"]["kind_mean_halfwidth_w"]
o = P["rules_of_number"]["fp32.nn_like"]
print(f"  E94 card 1, registered plain mean: {km:.3f} +- {khw:.3f} W; x {scale:.4f} = {km * scale:.3f} +- {khw * scale:.3f} W")
print("  E94 card 1, post hoc law-adjusted (E94 README result 7): 12.933 +- 0.153 W; x scale = "
      f"{12.933 * scale:.3f} +- {0.153 * scale:.3f} W")
print(f"  E123 aifoundry3, primary (gate-share adjusted, frozen slope): {o['kind_mean_w']:.3f} +- {o['kind_mean_halfwidth_w']:.3f} W")
e = o["e94_form"]
print(f"  E123 aifoundry3, E94's form (plain mean, 7 draws): {e['kind_mean_w']:.3f} +- {e['kind_mean_halfwidth_w']:.3f} W")
print(f"  E123 minus E94's post hoc x scale: {o['kind_mean_w'] - 12.933 * scale:+.3f} W")

print("\n[D] between-draw SD (plain, the draw as the unit), W")
for c, o in P["rules_of_number"].items():
    ps = o.get("plain_spread", {})
    e = o.get("e94_form")
    ci = f" [{e['tau_ci95_w'][0]:.2f}, {e['tau_ci95_w'][1]:.2f}]" if e else ""
    print(f"  {c:16s} k {ps.get('k')}: tau {ps.get('tau_w', 0):.3f}{ci}; predicted (E94 desk table) gate law "
          f"{RN[c]['desk_table_e94']['gate_law_sd_w']:.2f}, Q130(n) {RN[c]['desk_table_e94']['q130n_sd_w']:.2f}")
for k in ("G", "LF", "LI"):
    v = P["rules"][f"E123-R4:{k}"]
    print(f"  pooled {k}: tau {v['tau_w']:.3f} [{v['tau_ci95_w'][0]:.3f}, {v['tau_ci95_w'][1]:.3f}] ({v['df']} df) {v['verdict']}")
for c in ("fp32.sparse50", "fp16.nn_like", "fp32.nn_like"):
    s = e94["primary"]["rules_of_number"][c]["spread"]
    print(f"  E94 card 1 {c:14s} tau {s['tau_w']:.3f} [{s['tau_ci95_w'][0]:.3f}, {s['tau_ci95_w'][1]:.3f}] (k {s['k']})")
print("  the gate share's residual (class-pooled s' of the adjusted draws): " +
      ", ".join(f"{k} {P['primary_by_class'][k]['s_w']:.3f} W" for k in ("G", "LF", "LI")))

print("\n[E] fp16 50% zeros (fp16.sparse50)")
o = P["rules_of_number"]["fp16.sparse50"]
r = RN["fp16.sparse50"]
print(f"  E94's desk table (frozen): committed - kind +{r['desk_table_e94']['gate_law_offset_w']:.3f} (gate law), "
      f"+{r['desk_table_e94']['q130n_offset_w']:.3f} (Q130(n)); the page: 'S about 14.7 W against 15.22, at the band'")
print(f"  measured: committed - kind {o['offset_w']:+.3f} +- {o['offset_halfwidth_w']:.3f} W, R2 {o['R2']}; kind's D {o['kind_mean_w']:.3f} "
      f"+- {o['kind_mean_halfwidth_w']:.3f}; this session's committed S {o['committed_S_w']['mean']:.2f}, kind's S {o['kind_S_w']['mean_w']:.2f} W; "
      f"the page's S less the offset {r['e78_a3']['S_w'] - o['offset_w']:.2f} W")
print(f"  this session's committed D {o['committed_D_w']:.3f} against E78's {r['e78_a3']['D_w']:.3f} +- "
      f"{r['e78_a3']['D_se_w'] * 2.571:.3f} (95%, 6 passes): {o['committed_D_w'] - r['e78_a3']['D_w']:+.3f} W (S1 band 0.50)")
