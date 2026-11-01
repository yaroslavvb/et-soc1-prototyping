#!/usr/bin/env python3
"""E118, post hoc (not a registered rule; E72 published the same table): the exponent n that reproduces each measured
600/800 MHz price ratio as (V600/V800)^n, with the per-pass SEs of both sides propagated (the pass is the unit of
replication). n = 2 is the registered law; the clock-scaling alternative is n = 2 + ln(0.75)/ln(V600/V800).
Inputs: verdicts.json (this directory, from score_e118.py) and E60's hl.json (card aifoundry1-c0).
    python3 docs/reports/data/2026-11-01-e118-two-clock-card0/posthoc_exponents.py
"""
import json, math, os
H = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(H, "..", "..", "..", ".."))
v = json.load(open(os.path.join(H, "verdicts.json")))
pred = json.load(open(os.path.join(R, "tools/claims-v3/e118/predictions.json")))
e60 = pred["reference"]["e60_card0_800MHz"]
v600, v800 = v["measured_600"]["v_mean"], pred["voltages"]["v800_sp"]
lr = math.log(v600 / v800)
n_alt = 2 + math.log(0.75) / lr

def row(name, a, sa, b, sb):
    ratio = a / b
    rel = math.sqrt((sa / a) ** 2 + (sb / b) ** 2)
    n = math.log(ratio) / lr
    sn = rel / abs(lr)
    return {"row": name, "e118_600_fJ": a, "e118_se": sa, "e60_800_fJ": b, "e60_se": sb, "ratio": ratio, "ratio_se": ratio * rel,
            "n": n, "n_se": sn, "n2_in_sigma": (n - 2) / sn, "alt_in_sigma": (n_alt - n) / sn}

rows = [row("registered: each side at its own leak auto (E118 0.104, E60 0.327 W/C)", v["rules"]["V1"]["measured"], v["rules"]["V1"]["se"],
            e60["lq_fJ_per_designed_bit"], e60["lq_fJ_se"])]
for k, r in v["rules"]["V1m"]["rows"].items():
    m = pred["rules"]["V1m"]["e60_matched"][k]
    rows.append(row(f"matched at {k} W/C (E118 passes {v['rules']['V1m']['e118_fixed_passes']}, E60 passes {m['passes']})",
                    r["e118_secant"], r["e118_se"], m["secant_fJ"], m["designed_se_fJ"]))
rows.append(row("minion rail, uncorrected (E72's caveat: a later window, no leakage correction)", v["rules"]["V2"]["measured"],
                v["rules"]["V2"]["se"], e60["lq_rail_fJ"], 1.0599859041067768))
out = {"v600": v600, "v800": v800, "v2_ratio": (v600 / v800) ** 2, "n_alternative": n_alt, "rows": rows,
       "note": "E60's card-0 rail SE (1.0600 fJ) is hl.json cards.aifoundry1-c0.lq.designed.rail_se_J"}
json.dump(out, open(os.path.join(H, "posthoc_exponents.json"), "w"), indent=1)
print(f"V600 {v600:.5f} V800 {v800:.5f} (V600/V800)^2 {(v600/v800)**2:.4f}; alternative n = {n_alt:.3f}")
for r in rows:
    print(f"{r['row'][:60]:60s} ratio {r['ratio']:.4f} +- {r['ratio_se']:.4f}  n {r['n']:.2f} +- {r['n_se']:.2f}  (2 at {r['n2_in_sigma']:+.1f} SE; alt at {r['alt_in_sigma']:.1f} SE)")
