#!/usr/bin/env python3
"""E82, corrections after verification (Sat 31 Oct 2026): every number the README's section
"Corrections after verification" quotes, derived from committed files only.

    python3 docs/reports/data/2026-10-31-e82-kinds-aifoundry1/corrections-check.py > .../corrections-check.txt

It reads this directory's e82.json, its three leakage arms, scored.json and posthoc/dips.json; E78's committed
e78.json, its two arms and scored.json (docs/reports/data/2026-10-31-e78-kinds-energy-matrix/); predictions-e82.json
and predictions-e78.json (tools/claims-v3/kinds/); and September's cards-v3.json and abla.json. It changes nothing,
and it asserts first that it reads the registered numbers back (D of fp32 randn, the tallies, the cross-card
verdicts, the agreement count). Pure Python 3.9+, no numpy.
"""
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E78_DIR = os.path.join(REPO, "docs", "reports", "data", "2026-10-31-e78-kinds-energy-matrix")
KINDS_DIR = os.path.join(REPO, "tools", "claims-v3", "kinds")
SEPT_DIR = os.path.join(REPO, "docs", "reports", "data")
S_RESOLVED_W = 12.0  # C1: the die reading resolves a kind above this S (E78's C1 boundary, checked in [C1.3])
ARMS = (("leak0.545", "e82-leak0.545.json"), ("leak0.3803", "e82-leak0.3803.json"), ("leak0", "e82-leak0.json"))
TYPES = ("fp32", "fp16", "int8")


def load(*parts):
    with open(os.path.join(*parts)) as handle:
        return json.load(handle)


primary = load(HERE, "e82.json")
arm_docs = {name: load(HERE, fname) for name, fname in ARMS}
scored = load(HERE, "scored.json")
dips = load(HERE, "posthoc", "dips.json")
e78 = load(E78_DIR, "e78.json")
scored78 = load(E78_DIR, "scored.json")
reg82 = load(KINDS_DIR, "predictions-e82.json")
reg78 = load(KINDS_DIR, "predictions-e78.json")
cards_v3 = load(SEPT_DIR, "2026-09-21-horace-aifoundry2", "cards-v3.json")
abla = load(SEPT_DIR, "2026-09-25-claims-v3", "results", "abla.json")

items = {k: v for k, v in primary["items"].items() if k != "anchor_pi"}
tie = primary["items"]["anchor_pi"]


def m(item, key):
    return item[key]["mean"]


def ci(item, key):
    return item[key]["ci95"]


def heading(title):
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def flat_verdicts(o, path=""):
    """(path, verdict) for every verdict leaf, as score_e82.py's flat_verdicts walks a rules block."""
    res = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("verdict", "X2a_verdict", "X2b_verdict", "verdict_R1_A1") and isinstance(v, str):
                res.append((f"{path}/{k}", v))
            elif k == "verdicts":
                continue
            else:
                res += flat_verdicts(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            key = v.get("cell", str(i)) if isinstance(v, dict) else str(i)
            res += flat_verdicts(v, f"{path}/{key}")
    return res


def scorer_tally(rules):
    """score_e78.py's tally(): R1 and R2 per type, R4 per cell, R3 rules with cells and no top verdict per cell."""
    vs = []
    for name, r in rules.items():
        if name in ("E78-R1", "E78-R2"):
            vs += list(r["verdict"].values())
        elif name == "E78-R4":
            vs += [x["verdict"] for x in r.values()]
        elif name == "E78-R5":
            continue
        elif "cells" in r and "verdict" not in r:
            vs += [c["verdict"] for c in r["cells"]]
        elif "verdict" in r:
            vs.append(r["verdict"])
    return vs


def registered_units(rules):
    """The same verdicts, with E78-R3c counted once as E78.md registers it ("both in [0.909, 1.10]")."""
    vs = []
    for name, r in rules.items():
        if name == "E78-R3c":
            cells = [c["verdict"] for c in r["cells"]]
            vs.append("PASS" if all(v == "PASS" for v in cells) else
                      ("FAIL" if any(v == "FAIL" for v in cells) else "INCONCLUSIVE"))
        elif name in ("E78-R1", "E78-R2"):
            vs += list(r["verdict"].values())
        elif name == "E78-R4":
            vs += [x["verdict"] for x in r.values()]
        elif name == "E78-R5":
            continue
        elif "cells" in r and "verdict" not in r:
            vs += [c["verdict"] for c in r["cells"]]
        elif "verdict" in r:
            vs.append(r["verdict"])
    return vs


def registered_leaves(rules):
    """{unit: verdict} in registered units: R1/R2 per type, R3a/R3b/R3i per cell, R3c once, R3d/R3e/R3f/R3g/R3h once
    (their top verdict; R3f's fp32 and fp16 cells are reported, not registered), R4 per cell."""
    out = {}
    for name, r in rules.items():
        if name in ("E78-R1", "E78-R2"):
            for fmt, v in r["verdict"].items():
                out[f"{name}/{fmt}"] = v
        elif name == "E78-R4":
            for cell, x in r.items():
                out[f"{name}/{cell}"] = x["verdict"]
        elif name == "E78-R5":
            continue
        elif name == "E78-R3c":
            cells = [c["verdict"] for c in r["cells"]]
            out[name] = "PASS" if all(v == "PASS" for v in cells) else "NOT PASS"
        elif "cells" in r and "verdict" not in r:
            for c in r["cells"]:
                out[f"{name}/{c['cell']}"] = c["verdict"]
        elif "verdict" in r:
            out[name] = r["verdict"]
    return out


def count(vs):
    return {k: sum(1 for v in vs if v == k) for k in ("PASS", "FAIL", "INCONCLUSIVE", "NOT SCORED")}


def gammaincc(a, x):
    """The regularized upper incomplete gamma Q(a, x) (series below a + 1, continued fraction above)."""
    if x <= 0:
        return 1.0
    log_gamma_a = math.lgamma(a)
    if x < a + 1.0:
        term = total = 1.0 / a
        a_next = a
        for _ in range(1000):
            a_next += 1.0
            term *= x / a_next
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        return 1.0 - total * math.exp(-x + a * math.log(x) - log_gamma_a)
    b = x + 1.0 - a
    c = 1.0 / 1e-300
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - log_gamma_a) * h


# ---------------------------------------------------------------------------------------------------- [0]
heading("[0] reading the registered numbers back (asserted)")
assert abs(m(items["fp32.randn"], "D") - 23.98694) < 1e-3, m(items["fp32.randn"], "D")
assert scored["tally"] == {"PASS": 23, "FAIL": 4, "INCONCLUSIVE": 0, "NOT SCORED": 0}, scored["tally"]
assert scored["arms"]["leak0.545"]["tally"] == {"PASS": 21, "FAIL": 5, "INCONCLUSIVE": 1, "NOT SCORED": 0}
assert scored["arms"]["leak0.3803"]["tally"] == {"PASS": 21, "FAIL": 5, "INCONCLUSIVE": 1, "NOT SCORED": 0}
assert scored["arms"]["leak0"]["tally"] == {"PASS": 23, "FAIL": 3, "INCONCLUSIVE": 1, "NOT SCORED": 0}
assert count(scorer_tally(scored["rules"])) == scored["tally"]
assert primary["leak"]["mode"] == "auto" and abs(primary["leak"]["k_w_per_c"] - 0.24143) < 1e-4
for (name, _), want in zip(ARMS, (0.545, 0.3803, 0.0)):
    assert abs(arm_docs[name]["leak"]["k_w_per_c"] - want) < 1e-9, name
cross = scored["cross_card"]
assert cross["verdicts"] == {"X1": "PASS", "X2a": "FAIL", "X2b": "FAIL", "X3": "FAIL"}, cross["verdicts"]
assert abs(cross["primary"]["x3"]["median_ratio"] - 1.0308) < 1e-3
assert cross["e78_rule_verdict_agreement"]["compared"] == 33 and cross["e78_rule_verdict_agreement"]["same"] == 31
assert scored78["tally"] == {"PASS": 28, "FAIL": 2, "INCONCLUSIVE": 0, "NOT SCORED": 0}
print(f"D(fp32 randn) = {m(items['fp32.randn'], 'D'):.3f} W; tally {scored['tally']}; arms "
      + "; ".join(f"{n} {scored['arms'][n]['tally']}" for n, _ in ARMS))
print(f"k = {primary['leak']['k_w_per_c']:.4f} W/C (auto, {primary['leak']['n_runs']} runs) / 0.545 / 0.3803 / 0; "
      f"cross-card {cross['verdicts']}; median {cross['primary']['x3']['median_ratio']:.4f}; agreement "
      f"{cross['e78_rule_verdict_agreement']['same']} of {cross['e78_rule_verdict_agreement']['compared']}; "
      f"{len(items)} kinds + the tie; kept passes {primary['passes']}")
for name, _ in ARMS:
    a = arm_docs[name]
    print(f"   arm {name}: kept {a['passes']}; set aside "
          + "; ".join(f"{x['pass']} ({', '.join(x['why'])})" for x in a["passes_set_aside"]))

# ---------------------------------------------------------------------------------------------------- [C1]
heading("[C1] the heat column (dT_win) and the die reading's whole-degree steps")
print("[C1.1] dT_win cells whose 95% interval has zero width (every kept pass read the same window mean):")
zero_width = sorted(k for k, it in items.items() if abs(ci(it, "dT_win")) < 1e-9)
for k in zero_width:
    it = items[k]
    print(f"   {k:24s} dT {m(it, 'dT_win'):.2f} [+- 0.00]   S {m(it, 'S'):6.3f} W   n {it['dT_win']['n']}")
print(f"   {len(zero_width)} of {len(items)} kinds")

print()
print("[C1.2] dT / S for every kind, sorted by S (C per W of switching over idle); per-pass dT in pass order:")
print(f"   {'kind':26s}{'S W':>8s}{'dT C':>7s}{'+-95%':>7s}{'dT/S':>8s}  n  class           per-pass dT")
rows = sorted(list(items.items()) + [("anchor_pi (the tie)", tie)], key=lambda name_item: -m(name_item[1], "S"))
for k, it in rows:
    s, rise_c = m(it, "S"), m(it, "dT_win")
    key = "anchor_pi" if k.startswith("anchor_pi") else k
    per_pass_dt = [primary["per_pass"][str(p)][key]["dT_win"] for p in primary["passes"] if key in primary["per_pass"][str(p)]]
    category = "resolved" if s > S_RESOLVED_W else "STEP-LIMITED"
    print(f"   {k:26s}{s:8.3f}{rise_c:7.2f}{ci(it, 'dT_win'):7.2f}{rise_c / s:8.3f}  {it['dT_win']['n']}  {category:15s} "
          + " ".join(f"{x:.2f}" for x in per_pass_dt))

resolved = {k: it for k, it in items.items() if m(it, "S") > S_RESOLVED_W}
limited = {k: it for k, it in items.items() if m(it, "S") <= S_RESOLVED_W}
by_type = {fmt: sum(1 for k in resolved if k.startswith(fmt + ".")) for fmt in TYPES}
by_type_l = {fmt: sum(1 for k in limited if k.startswith(fmt + ".")) for fmt in TYPES}
ratios_r = [m(it, "dT_win") / m(it, "S") for it in resolved.values()]
ratios_l = [m(it, "dT_win") / m(it, "S") for it in limited.values()]
s_values = [m(it, "S") for it in resolved.values()]
dt_values = [m(it, "dT_win") for it in resolved.values()]
k_origin = sum(x * y for x, y in zip(s_values, dt_values)) / sum(x * x for x in s_values)
n = len(s_values)
xbar, ybar = sum(s_values) / n, sum(dt_values) / n
sxx = sum((x - xbar) ** 2 for x in s_values)
slope = sum((x - xbar) * (y - ybar) for x, y in zip(s_values, dt_values)) / sxx
offset = ybar - slope * xbar
resid = [y - (offset + slope * x) for x, y in zip(s_values, dt_values)]
resid_var = sum(r * r for r in resid) / (n - 2)
se_offset = math.sqrt(resid_var * (1.0 / n + xbar ** 2 / sxx))
se_slope = math.sqrt(resid_var / sxx)
print()
print(f"[C1.3] above {S_RESOLVED_W:.0f} W of S: {len(resolved)} kinds ({by_type['fp32']} fp32, {by_type['fp16']} fp16, "
      f"{by_type['int8']} int8); dT/S {min(ratios_r):.3f}-{max(ratios_r):.3f} C/W; through the origin "
      f"{k_origin:.4f} C/W; a straight line {slope:.4f} C/W (SE {se_slope:.4f}) + {offset:.3f} C (SE {se_offset:.3f})")
print(f"   at or below {S_RESOLVED_W:.0f} W: {len(limited)} kinds ({by_type_l['fp32']} fp32, {by_type_l['fp16']} fp16, "
      f"{by_type_l['int8']} int8) plus the tie (S {m(tie, 'S'):.2f} W); dT/S {min(ratios_l):.3f}-{max(ratios_l):.3f} C/W")
lo_k = min(limited, key=lambda k: m(limited[k], "dT_win") / m(limited[k], "S"))
hi_k = max(limited, key=lambda k: m(limited[k], "dT_win") / m(limited[k], "S"))
print(f"   lowest  {lo_k}: dT {m(limited[lo_k], 'dT_win'):.2f} C at S {m(limited[lo_k], 'S'):.2f} W")
print(f"   highest {hi_k}: dT {m(limited[hi_k], 'dT_win'):.2f} C at S {m(limited[hi_k], 'S'):.2f} W")
for a, b in (("int8.neg_ones", "fp16.a_zeros_b_randn"), ("int8.neg_ones", "int8.full"), ("int8.ones", "int8.ternary"),
             ("fp32.pi", "fp32.neg_ones")):
    print(f"   {a}: S {m(items[a], 'S'):.2f} W, dT {m(items[a], 'dT_win'):.2f} C   |   "
          f"{b}: S {m(items[b], 'S'):.2f} W, dT {m(items[b], 'dT_win'):.2f} C")
print(f"   the tie: anchor_pi S {m(tie, 'S'):.2f} W, dT {m(tie, 'dT_win'):.2f} C against fp32.pi S "
      f"{m(items['fp32.pi'], 'S'):.2f} W, dT {m(items['fp32.pi'], 'dT_win'):.2f} C (the same bytes)")
print()
print(f"[C1.4] the step-limited kinds' heat as an extrapolation, S x {k_origin:.3f} C/W (not a measurement):")
for k in sorted(limited, key=lambda k: -m(limited[k], "S")):
    print(f"   {k:24s} S {m(limited[k], 'S'):6.3f} W -> {m(limited[k], 'S') * k_origin:4.2f} C (read {m(limited[k], 'dT_win'):.2f})")
print(f"   {'anchor_pi (the tie)':24s} S {m(tie, 'S'):6.3f} W -> {m(tie, 'S') * k_origin:4.2f} C (read {m(tie, 'dT_win'):.2f})")
e78_res = [m(it, "dT_win") / m(it, "S") for k, it in e78["items"].items() if k != "anchor_pi" and m(it, "S") > S_RESOLVED_W]
e78_x = [m(it, "S") for k, it in e78["items"].items() if k != "anchor_pi" and m(it, "S") > S_RESOLVED_W]
e78_y = [m(it, "dT_win") for k, it in e78["items"].items() if k != "anchor_pi" and m(it, "S") > S_RESOLVED_W]
k_origin_78 = sum(x * y for x, y in zip(e78_x, e78_y)) / sum(x * x for x in e78_x)
print(f"   beside: E78 (aifoundry3) on its {len(e78_res)} kinds above 12 W, dT/S {min(e78_res):.3f}-{max(e78_res):.3f}, "
      f"{k_origin_78:.4f} C/W through the origin")

# ---------------------------------------------------------------------------------------------------- [C2]
heading("[C2] card 1 against September (E38's anchors, R4): what the comparison does and does not show")
targets82 = reg82["replication_targets"]
for cell in ("fp32.randn", "fp32.ones"):
    t = targets82[cell]["target_w"]
    vals = [("auto 0.2414", items[cell])] + [(n, arm_docs[n]["items"][cell]) for n, _ in ARMS]
    print(f"   {cell}: E38 target {t:.3f} W (tol {targets82[cell]['tol_w']}); E82 D by leakage arm: "
          + "; ".join(f"{lab} {m(it, 'D'):.3f} W ({100 * (m(it, 'D') / t - 1):+.1f}%)" for lab, it in vals))
abla_t8 = [x for x in abla if isinstance(x, dict) and x.get("item") == "ABL-T8"]
subtests = None
if abla_t8:
    per_card_t8 = abla_t8[0].get("per_card") or {}
    subtests = (per_card_t8.get("aifoundry1-c1") or {}).get("vs_aifoundry2_values", {}).get("subtests")
if subtests:
    for subtest in subtests:
        ci_block = subtest["ci"]
        print(f"   E38 {subtest['test']}: {ci_block['point']} W = mean of {ci_block['n_x']} runs {ci_block['values_x']} minus mean of "
              f"{ci_block['n_y']} zeros runs {ci_block['values_y']} (a difference of run means; no within-run leakage term)")
L = cards_v3["launch"]
print(f"   cards-v3.json launch: card 1 reading {L['aifoundry1-c1']['reading']} C, leak "
      f"{L['aifoundry1-c1']['leak_w_per_c']} W/C; aifoundry3 reading {L['aifoundry3']['reading']:.1f} C, leak "
      f"{L['aifoundry3']['leak_w_per_c']} W/C")
patterns_v3 = {p["values"]: p["per_card"] for p in cards_v3["patterns"]}
sep_c1 = patterns_v3["randn"]["aifoundry1-c1"]["mean"] - patterns_v3["zeros"]["aifoundry1-c1"]["mean"]
sep_a3 = patterns_v3["randn"]["aifoundry3"]["mean"] - patterns_v3["zeros"]["aifoundry3"]["mean"]
d78 = m(e78["items"]["fp32.randn"], "D")
e67 = reg78["replication_targets"]["fp32.randn"]["target_w"]
print(f"   September randn - zeros (cards-v3.json patterns): card 1 {sep_c1:.3f} W, aifoundry3 {sep_a3:.3f} W")
print(f"   aifoundry3: E78 D(fp32 randn) {d78:.3f} W = {100 * (d78 / sep_a3 - 1):+.1f}% against its September "
      f"{sep_a3:.3f}, {100 * (d78 / e67 - 1):+.1f}% against E67's {e67:.3f} (27 Oct, E78's R4 target)")
d82 = m(items["fp32.randn"], "D")
print(f"   card 1:     E82 D(fp32 randn) {d82:.3f} W = {100 * (d82 / sep_c1 - 1):+.1f}% against its September {sep_c1:.3f}")
rise = m(items["fp32.randn"], "dT_win") - m(items["fp32.zeros"], "dT_win")
k = primary["leak"]["k_w_per_c"]
k_sept = L["aifoundry1-c1"]["leak_w_per_c"]
d_noleak = m(arm_docs["leak0"]["items"]["fp32.randn"], "D")
print(f"   E82's window rise, fp32 randn over fp32 zeros: {rise:.2f} C; x {k:.4f} (E82 auto) = {k * rise:.2f} W "
      f"(the leak0 arm reads {d_noleak - d82:.3f} W higher); x {k_sept} (card 1 at its September launch) = {k_sept * rise:.2f} W")
print(f"   the gap to E38's target: {sep_c1 - d82:.3f} W at E82's primary slope, {sep_c1 - d_noleak:.3f} W with no correction")

# ---------------------------------------------------------------------------------------------------- [C3]
heading("[C3] verdicts that move between the registered leakage arms (E78.md: reported as slope-sensitive)")
v_prim = dict(flat_verdicts(scored["rules"]))
v_arm = {n: dict(flat_verdicts(scored["arms"][n]["rules"])) for n, _ in ARMS}
moving = []
for leaf, v in v_prim.items():
    if "by_model/q130b" in leaf:
        continue
    row = [v] + [v_arm[n].get(leaf, "-") for n, _ in ARMS]
    if len(set(row)) > 1:
        moving.append(leaf)
        print(f"   {leaf}: primary {row[0]}; " + "; ".join(f"{n} {r}" for (n, _), r in zip(ARMS, row[1:])))


def stat(rules, which):
    if which == "R2.fp16":
        return f"rms {rules['E78-R2']['by_model']['q130c']['fp16']['rms_w']:.3f} W (bound 2.0)"
    if which == "R3f.int8":
        d = rules["E78-R3f"]["cells"][0]["diff"]
        return f"{d['mean']:.3f} [{d['lo']:.3f}, {d['hi']:.3f}] W (pass if inside +-0.30)"
    if which == "R4.ones":
        x = rules["E78-R4"]["fp32.ones"]["measured"]
        return f"{x['mean']:.3f} +- {x['ci95']:.3f} W against 8.996 +- 1.0"


for which in ("R2.fp16", "R3f.int8", "R4.ones"):
    print(f"   {which}: primary {stat(scored['rules'], which)}; "
          + "; ".join(f"{n} {stat(scored['arms'][n]['rules'], which)}" for n, _ in ARMS))
v78 = dict(flat_verdicts(scored78["rules"]))
moves78 = []
for leaf, v in v78.items():
    if "by_model/q130b" in leaf:
        continue
    row = [v] + [dict(flat_verdicts(scored78["arms"][n]["rules"])).get(leaf, "-") for n in scored78["arms"]]
    if len(set(row)) > 1:
        moves78.append(leaf)
print(f"   E78 (aifoundry3), arms {list(scored78['arms'])}: {len(moves78)} verdict leaves move {moves78}")
print(f"   cross-card slope_sensitive (scored.json): {cross['slope_sensitive']}; arm medians "
      + ", ".join(f"{lab} {o['x3']['median_ratio']:.3f}" for lab, o in cross["arms"].items()))

# ---------------------------------------------------------------------------------------------------- [C4]
heading("[C4] counting the verdicts: as the frozen scorer counts them, and as E78.md registers them")
for lab, rules in [("primary", scored["rules"])] + [(n, scored["arms"][n]["rules"]) for n, _ in ARMS]:
    a, b = scorer_tally(rules), registered_units(rules)
    print(f"   {lab:10s} scorer {count(a)} of {len(a)}; R3c once {count(b)} of {len(b)}")
r3 = [v for name, r in scored["rules"].items() if name.startswith("E78-R3")
      for v in ([c["verdict"] for c in r["cells"]] if ("cells" in r and "verdict" not in r) else [r["verdict"]])]
print(f"   R3 verdicts: {len(r3)} as the scorer counts ({count(r3)['PASS']} PASS); "
      f"{len(r3) - 1} with R3c counted once")
a78, units_reg78 = scorer_tally(scored78["rules"]), registered_units(scored78["rules"])
print(f"   E78 (aifoundry3): scorer {count(a78)} of {len(a78)}; R3c once {count(units_reg78)} of {len(units_reg78)}")
g = cross["e78_rule_verdict_agreement"]
leaves82 = dict(flat_verdicts(scored["rules"]))
cells_on_top = [k for k in leaves82 if any(k.startswith(f"/{r}/cells/") for r in ("E78-R3e", "E78-R3f"))]
print(f"   the scorer's agreement walk: {g['same']} of {g['compared']} leaves the same; it counts R3e's and R3f's "
      f"top verdicts and their {len(cells_on_top)} cells, among them R3f's reported fp32 and fp16 cells")
units82, units78 = registered_leaves(scored["rules"]), registered_leaves(scored78["rules"])
both = [u for u in units82 if u in units78]
diff = [u for u in both if units82[u] != units78[u]]
print(f"   in registered units: {len(both) - len(diff)} of {len(both)} the same; differing: "
      + ", ".join(f"{u} (E82 {units82[u]}, E78 {units78[u]})" for u in diff))

# ---------------------------------------------------------------------------------------------------- [C5]
heading("[C5] one card scale? the 32 per-kind ratios D(aifoundry3) / D(card 1) against one weighted mean")
K = [k for k, v in cross["primary"]["kinds"].items() if v.get("status") == "ok"]
rows5 = []
for kind_name in K:
    a, b = e78["items"][kind_name]["D"], items[kind_name]["D"]
    r = a["mean"] / b["mean"]
    se = r * math.sqrt((a["se"] / a["mean"]) ** 2 + (b["se"] / b["mean"]) ** 2)
    rows5.append((kind_name, r, se))
w = [1.0 / se ** 2 for _, _, se in rows5]
wmean = sum(weight * r for weight, (_, r, _) in zip(w, rows5)) / sum(w)
chi2 = sum(((r - wmean) / se) ** 2 for _, r, se in rows5)
dof = len(rows5) - 1
p = gammaincc(dof / 2.0, chi2 / 2.0)
ratios_sorted = sorted(r for _, r, _ in rows5)
med = statistics.median(ratios_sorted)
q = sorted(ratios_sorted)
print(f"   {len(rows5)} kinds; inverse-variance weighted mean {wmean:.4f}; chi2 {chi2:.1f} with {dof} degrees of freedom (p {p:.4f}); "
      "SEs from each card's between-pass scatter (4-5 degrees of freedom), so p is approximate")
for z, kind_name, r in sorted(((abs(r - wmean) / se, kind_name, r) for kind_name, r, se in rows5), reverse=True)[:4]:
    print(f"   largest |z|: {kind_name:22s} ratio {r:.3f}  z {z:.1f}")
print(f"   median {med:.4f}; range {ratios_sorted[0]:.3f}-{ratios_sorted[-1]:.3f}; sd {100 * statistics.pstdev(ratios_sorted) / med:.2f}% "
      f"(population) / {100 * statistics.stdev(ratios_sorted) / med:.2f}% (sample) of the median; within +-1.5% of the median: "
      f"{sum(abs(r - med) <= 0.015 * med for r in ratios_sorted)} of {len(ratios_sorted)}")
print(f"   scored.json x3: median {cross['primary']['x3']['median_ratio']:.4f}, IQR {cross['primary']['x3'].get('iqr')}")

# ---------------------------------------------------------------------------------------------------- [C6]
heading("[C6] what the table cells' intervals cover: between-pass scatter at the primary slope only")
moved = 0
nonzero_kinds = 0
for kind_name, it in sorted(items.items()):
    vals = [m(arm_docs[n]["items"][kind_name], "D") for n, _ in ARMS]
    dmax = max(abs(v - m(it, "D")) for v in vals)
    if m(it, "D") != 0.0:
        nonzero_kinds += 1
    if dmax > ci(it, "D") + 1e-12:
        moved += 1
print(f"   kinds whose D moves across the three arms by more than its 95% half-width: {moved} of {len(items)} "
      f"({nonzero_kinds} non-zero; each type's zeros is 0 by construction at every arm)")
largest_moves = sorted(((max(abs(m(arm_docs[n]['items'][kind_name], 'D') - m(it, 'D')) for n, _ in ARMS), kind_name)
              for kind_name, it in items.items()), reverse=True)[:3]
print("   largest arm moves: " + "; ".join(f"{kind_name} {move_w:.3f} W" for move_w, kind_name in largest_moves))
for key, unit in (("D", "W"), ("pj_mac_S", "pJ/MAC")):
    it = items["fp32.randn"]
    print(f"   fp32 randn {key}: primary {m(it, key):.4f} +- {ci(it, key):.4f} {unit}; arms "
          + "; ".join(f"{n} {m(arm_docs[n]['items']['fp32.randn'], key):.4f} "
                      f"({m(arm_docs[n]['items']['fp32.randn'], key) - m(it, key):+.4f})" for n, _ in ARMS))
pj_moves = [(kind_name, max(abs(m(arm_docs[n]["items"][kind_name], "pj_mac_S") / m(items[kind_name], "pj_mac_S") - 1) for n, _ in ARMS))
       for kind_name in ("fp32.zeros", "fp16.zeros", "int8.zeros", "fp32.randn", "fp16.randn", "int8.full")]
print("   pJ/MAC (S), largest relative arm move: " + "; ".join(f"{kind_name} {100 * v:.1f}%" for kind_name, v in pj_moves))
print(f"   board against rail, fp32 randn: D {m(items['fp32.randn'], 'D'):.2f} W (board), Drail "
      f"{m(items['fp32.randn'], 'Drail'):.2f} W (the minion rail, deconvolved)")
n4 = sorted(kind_name for kind_name, it in items.items() if it["D"]["n"] != 5)
print(f"   kinds with fewer than five passes: " + ", ".join(f"{kind_name} (n {items[kind_name]['D']['n']})" for kind_name in n4)
      + f" -> {3 * len(n4)} table cells (D, pJ/MAC, dT)")

# ---------------------------------------------------------------------------------------------------- [C7]
heading("[C7] wording")
x1 = cross["primary"]["x1"]
print("   X1 ranks " + " / ".join(f"{x1[fmt]['n_kinds']} {fmt}" for fmt in TYPES)
      + f" = {sum(x1[fmt]['n_kinds'] for fmt in TYPES)} non-zero kinds")
widths = sorted(((v["ratio_ci95_halfwidth"], kind_name, v["ratio"]) for kind_name, v in cross["primary"]["kinds"].items()
                 if v.get("status") == "ok"), reverse=True)
print("   ratio intervals, widest first: " + "; ".join(f"{kind_name} {r:.3f} +-{half_width:.3f}" for half_width, kind_name, r in widths[:6]))
print("   fp16.sparse50 rank among the 32 by width: "
      + str(1 + [kind_name for _, kind_name, _ in widths].index("fp16.sparse50")))
for kind_name in ("fp32.randn", "fp16.randn", "int8.full", "fp32.zeros", "fp16.zeros", "int8.zeros"):
    a, b = m(e78["items"][kind_name], "pj_mac_S"), m(items[kind_name], "pj_mac_S")
    print(f"   pJ/MAC (S) {kind_name:12s} aifoundry3 {a:.4f}, card 1 {b:.4f}: a3/c1 {a / b:.3f}")


def events(rows_, gap_ms=200):
    """Group dip samples into events: consecutive samples no more than gap_ms apart."""
    evs = []
    for r in sorted(rows_, key=lambda r: r["t_ms"]):
        if evs and r["t_ms"] - evs[-1][-1]["t_ms"] <= gap_ms:
            evs[-1].append(r)
        else:
            evs.append([r])
    return evs


tot_s = tot_e = run_s = run_e = 0
for pname, pass_doc in dips["passes"].items():
    evs = events(pass_doc["rows"])
    inrun = [e for e in evs if e[0]["where"].startswith("run")]
    tot_s += len(pass_doc["rows"])
    tot_e += len(evs)
    run_s += sum(1 for r in pass_doc["rows"] if r["where"].startswith("run"))
    run_e += len(inrun)
    if pname == "p8210":
        print(f"   p8210: {len(pass_doc['rows'])} dip samples in {len(evs)} events; inside runs "
              f"{sum(1 for r in pass_doc['rows'] if r['where'].startswith('run'))} samples in {len(inrun)} events "
              f"({', '.join(e[0]['where'][4:] for e in inrun)}); the first sample of each in-run event "
              + ", ".join(str(e[0]["ms_after_launch_boundary"]) for e in inrun) + " ms after a launch boundary")
all_ms = [r["ms_after_launch_boundary"] for pass_doc in dips["passes"].values() for r in pass_doc["rows"]
          if r["where"].startswith("run")]
first_ms = [e[0]["ms_after_launch_boundary"] for pass_doc in dips["passes"].values() for e in events(pass_doc["rows"])
            if e[0]["where"].startswith("run")]
print(f"   all seven passes: {tot_s} dip samples in {tot_e} events; inside runs {run_s} samples in {run_e} events; "
      f"in-run samples {min(all_ms)}-{max(all_ms)} ms after a launch boundary (median {statistics.median(all_ms):g}); "
      f"first samples of in-run events {min(first_ms)}-{max(first_ms)} ms")
print(f"   dips.json totals: {dips['totals']}")
