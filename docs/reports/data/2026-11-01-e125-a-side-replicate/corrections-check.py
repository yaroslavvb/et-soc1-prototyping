#!/usr/bin/env python3
"""E125, corrections after verification (Sun 1 Nov 2026): print, from committed files only, every number that the
README's "Corrections after verification" section quotes and that no earlier file prints, beside the committed
numbers it rests on.

    python3 docs/reports/data/2026-11-01-e125-a-side-replicate/corrections-check.py > corrections-check.txt

Post hoc; it decides nothing and changes no file. Standard library only; it runs from any directory. The one paired
ratio it adds (spread A/B at k = 8) is formed per pass exactly as score_e125.py's N1 forms the low ones, through E113's
registered scorer's rules (tools/claims-v3/e113/score_e113.py: load_runs, pass_values, dw, mean_se, restated below
in a few lines, because that file needs Python 3.12; the low-layout r8 recomputed here must equal scored.json's, and
the output says whether it does). Every ± is one standard error over the kept passes, as in scored.json.
"""
import csv
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
REL = os.path.relpath(HERE, REPO)
E125 = os.path.join(REPO, "tools", "claims-v3", "e125")


def zero_of(item):  # score_e113.zero_of, for the items used here
    if item.startswith("alq_") or item.startswith("als_"):
        return "aq_h0"
    if item.startswith("lq_") or item.startswith("ls_"):
        return "lq_h0"
    return None


def mean_se(xs):  # score_e113.mean_se
    xs = [x for x in xs if x is not None]
    m = sum(xs) / len(xs)
    return m, math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1) / len(xs)), len(xs)


def load_runs(path):  # score_e113.load_runs, the fields used here
    out = []
    with open(path) as f:
        for r in csv.DictReader(f):
            try:
                r["pass"] = int(r["pass"])
                r["p80"] = float(r["p80"]) if r["p80"] not in ("", "None") else None
            except ValueError:
                continue
            r["failed"] = r["fail"] not in ("[]", "", None)
            out.append(r)
    return out


def pass_values(runs, kept):  # score_e113.pass_values: mean p80 per item per pass, failed runs out
    val = {}
    for p in kept:
        d = {}
        for r in runs:
            if r["pass"] == p and not r["failed"] and r["p80"] is not None:
                d.setdefault(r["item"], []).append(r["p80"])
        val[p] = {k: sum(v) / len(v) for k, v in d.items()}
    return val


def dw(val, p, item):  # score_e113.dw: the item over its zero, within one pass
    z = zero_of(item)
    if z is None or item not in val[p] or z not in val[p]:
        return None
    return val[p][item] - val[p][z]


def paired_ratio(val, kept, a_item, b_item):
    per = []
    for p in kept:
        a, b = dw(val, p, a_item), dw(val, p, b_item)
        if a is not None and b:
            per.append(a / b)
    return per


def load(*parts):
    with open(os.path.join(*parts)) as f:
        return json.load(f)


def text(*parts):
    with open(os.path.join(*parts)) as f:
        return f.read()


sc = load(HERE, "scored.json")
ph = load(HERE, "posthoc.json")
pr = load(E125, "predictions-e125.json")
nd = load(E125, "e113-nodips", "scored.json")
e113_dir = os.path.join(REPO, "docs", "reports", "data", "2026-11-01-e113-a-side-saturation")
e113 = load(e113_dir, "scored.json")
s_e82 = pr["card_scale"]["s_fp32_aifoundry3_over_card1"]

print("E125 corrections-check (post hoc, deciding nothing). Paths are relative to the repository's top level.")
print(f"Data: {REL}/ ; registration and frozen predictions: tools/claims-v3/e125/")
print()

# ---------------------------------------------------------------------------------------------------------------
print("C1  the mirror's c is fitted against E70's aifoundry3 B rungs, so card 1's c carries the card scale")
c, c_se = sc["D2_A"]["c_per_pass_mean_se"]
print(f"  card 1, c refitted over {sc['D2_A']['n_rungs']} rungs (scored.json > D2_A.c_per_pass_mean_se): "
      f"{c:.4f} ± {c_se:.4f} (n {len(sc['D2_A']['c_per_pass'])})")
b70 = {k: v.get("B_same_mask_E70_W") for k, v in sc["items"].items() if v.get("B_same_mask_E70_W") is not None}
print(f"  its B side, per rung (scored.json > items.*.B_same_mask_E70_W, E70's aifoundry3 rungs): {len(b70)} rungs, "
      f"e.g. als_h8 {b70.get('als_h8', float('nan')):.3f} W against card 1's own ls_h8 {sc['items']['ls_h8']['dW']:.3f} W")
print(f"  E82's fp32 card scale s, aifoundry3 over card 1 (predictions-e125.json > card_scale): {s_e82:.6f}")
print(f"  card 1's c at its own scale, c x s: {c * s_e82:.4f}")
xc = [r for r in pr["x_rules"] if r["id"] == "X-c"][0]
print(f"  X-c as frozen (predictions-e125.json > x_rules X-c): E113 {xc['E113']:.4f} / s = predicted {xc['pred']:.4f}; "
      f"card 1 read {c:.4f}")
c13, c13_se = e113["D2_A"]["c_per_pass_mean_se"]
cnd, cnd_se = nd["D2_A"]["c_per_pass_mean_se"]
print(f"  E113 on aifoundry3, registered (docs/reports/data/2026-11-01-e113-a-side-saturation/scored.json > "
      f"D2_A.c_per_pass_mean_se): {c13:.4f} ± {c13_se:.4f}")
print(f"  E113 on aifoundry3, dip-free frame (tools/claims-v3/e125/e113-nodips/scored.json > D2_A.c_per_pass_mean_se): "
      f"{cnd:.4f} ± {cnd_se:.4f}")
r8 = sc["e125"]["N1"]["r"]["8"]
print("  within card 1's own passes, B run in the same passes, A/B of the same mask at k = 8:")
print(f"    low,    alq_h8 / lq_h8 (scored.json > e125.N1.r.8): {r8['mean']:.4f} ± {r8['se']:.4f} (n {r8['n']})")
runs = load_runs(os.path.join(HERE, "runs.csv"))
kept = sc["passes_kept"]
val = pass_values(runs, kept)
lo = paired_ratio(val, kept, "alq_h8", "lq_h8")
lo_m, lo_se, _ = mean_se(lo)
same = abs(lo_m - r8["mean"]) < 1e-9 and abs(lo_se - r8["se"]) < 1e-9 and len(lo) == r8["n"]
print(f"    self-check, low r8 recomputed here from runs.csv: {lo_m:.6f} ± {lo_se:.6f} (n {len(lo)}); "
      f"equals scored.json's: {same}")
per = paired_ratio(val, kept, "als_h8", "ls_h8")
m, se, _ = mean_se(per)
print(f"    spread, als_h8 / ls_h8 per pass, paired as N1 pairs the low ones (runs.csv, passes {kept[0]}-{kept[-1]}): "
      f"{m:.4f} ± {se:.4f} (n {len(per)}); per pass {', '.join(f'{x:.3f}' for x in per)}")
print(f"    spread, ratio of the means (scored.json > items.als_h8.dW / items.ls_h8.dW): "
      f"{sc['items']['als_h8']['dW']:.3f} / {sc['items']['ls_h8']['dW']:.3f} = "
      f"{sc['items']['als_h8']['dW'] / sc['items']['ls_h8']['dW']:.4f}")
print()

# ---------------------------------------------------------------------------------------------------------------
print("C2  blog wording: rho per designed bit depends on k; one fitted card scale, not the same 3% on every rung")
rk = ph["rho_k"]
r_n1 = sc["e125"]["N1"]["r"]
print("  rho_k, low layout, per designed bit (posthoc.json > rho_k; = 2 x scored.json > e125.N1.r, A's designed flips "
      "being half of B's):")
for k in ("2", "4", "8"):
    print(f"    k = {k}: rho {rk[k]['rho']:.3f} ± {rk[k]['se']:.3f}; 2 x r_{k} = {2 * r_n1[k]['mean']:.3f}")
ls = sc["e125"]["ladder_scale"]
print(f"  this ladder's card scale (scored.json > e125.ladder_scale; least squares through the origin, E113's 16 A rungs "
      f"on card 1's): s {ls['s_ladder']:.4f}, rms {ls['rms_W']:.3f} W over {ls['n_rungs']} rungs; E82's s {ls['s_E82']:.4f}")
rows = []
for r in pr["x_rules"]:
    if r["group"] != "A_rungs":
        continue
    item = r["id"][2:]
    d1 = sc["items"].get(item, {}).get("dW")
    if d1:
        rows.append((d1, item, r["E113"], r["E113"] / d1))
rows.sort()
print("  per rung, E113 in the same frame (predictions-e125.json > x_rules.E113) over card 1 (scored.json > items.dW):")
for d1, item, e, q in rows:
    print(f"    {item:8s} card 1 {d1:6.3f} W  E113 {e:6.3f} W  ratio {q:.3f}")
qs = [q for _, _, _, q in rows]
qh = [q for d1, _, _, q in rows if d1 > 1.5]
print(f"  ratio range over all {len(qs)} rungs: {min(qs):.3f}-{max(qs):.3f}; over the {len(qh)} rungs above 1.5 W: "
      f"{min(qh):.3f}-{max(qh):.3f}")
print()

# ---------------------------------------------------------------------------------------------------------------
print("C3  rho(8)'s layout difference is a reading beside P5, not a registered rule")
d = sc["rho8"]["spread_minus_low"]
print(f"  card 1, spread minus low (scored.json > rho8.spread_minus_low): {d['d']:+.3f} ± {d['se']:.3f} "
      f"({d['d'] / d['se']:.1f} SE)")
p5 = sc["rules"]["P5"]
print(f"  P5 as registered (scored.json > rules.P5.asked): \"{p5['asked']}\" -> {p5['verdict']}")
xids = [r["id"] for r in pr["x_rules"]]
print(f"  the registered rules (predictions-e125.json): Z over E113's {sorted(pr['e113_verdicts'])}; "
      f"{len(xids)} X rules ({', '.join(x for x in xids if not x.startswith('X-al'))}, and the 16 A rungs); N1")
diff_rules = [x for x in xids if "minus" in x.lower() or "diff" in x.lower() or x.endswith("-d")]
print(f"  X rules on the difference between the layouts' rho(8): {diff_rules if diff_rules else 'none'} "
      f"(X-rho8-low and X-rho8-spread each test one layout against E113's value / s)")
dn = nd["rho8"]["spread_minus_low"]
print(f"  the desk finding, E113's passes dip-free (tools/claims-v3/e125/e113-nodips/scored.json > rho8.spread_minus_low): "
      f"{dn['d']:+.3f} ± {dn['se']:.3f} ({dn['d'] / dn['se']:.1f} SE), committed with the registration (105f4601)")
print()

# ---------------------------------------------------------------------------------------------------------------
print("C4  fJ per designed A bit is E70's within-experiment currency (in the lane's result only)")
fl = sorted(v["fJ_per_designed_bit"] for k, v in sc["items"].items() if k.startswith("alq_") and v.get("fJ_per_designed_bit"))
fs = sorted(v["fJ_per_designed_bit"] for k, v in sc["items"].items() if k.startswith("als_") and v.get("fJ_per_designed_bit"))
print(f"  scored.json > items.*.fJ_per_designed_bit: low alq {fl[0]:.0f}-{fl[-1]:.0f} fJ ({len(fl)} rungs), "
      f"spread als {fs[0]:.0f}-{fs[-1]:.0f} fJ ({len(fs)} rungs)")
readme = text(HERE, "README.md")
flat = " ".join(readme.split())
i = flat.find("within-experiment currency")
print(f"  README's caveat: \"...{flat[max(0, i - 40):i + 80]}...\"" if i >= 0 else "  README's caveat: NOT FOUND")
print()

# ---------------------------------------------------------------------------------------------------------------
print("C5  the README's header sentence (the text above its first '## ' heading)")
head = " ".join(readme.split("\n## ", 1)[0].split())
print(f"  'committed and **committed' present: {'committed and **committed' in head}; "
      f"'**committed as `105f4601`' present: {'**committed as `105f4601`' in head}")
