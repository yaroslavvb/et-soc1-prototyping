#!/usr/bin/env python3
"""E78, corrections after verification (Sat 31 Oct 2026): every number the README's section
"Corrections after verification" quotes, derived from this directory's committed files and kinds.json.

    python3 docs/reports/data/2026-10-31-e78-kinds-energy-matrix/corrections-check.py > .../corrections-check.txt

It reads only committed files (e78.json and its two leakage arms, scored.json, the raw marks of pass 7814,
tools/claims-v3/kinds/kinds.json and predictions-e78.json), changes nothing, and asserts first that it reads the
registered numbers back (D of fp32 randn and the three tallies). Pure Python 3.9+, no numpy.
"""
import datetime
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS_DIR = os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "kinds")
PDT = datetime.timezone(datetime.timedelta(hours=-7))  # 31 Oct 2026 is PDT (daylight time ends 1 Nov)
S_RESOLVED_W = 12.0  # C1: the die reading resolves a kind above this S (see [C1.2])


def load(*parts):
    with open(os.path.join(*parts)) as handle:
        return json.load(handle)


primary = load(HERE, "e78.json")
arm_zero = load(HERE, "e78-leak0.json")
arm_e71 = load(HERE, "e78-leak0.3803.json")
scored = load(HERE, "scored.json")
kinds_doc = load(KINDS_DIR, "kinds.json")
registration = load(KINDS_DIR, "predictions-e78.json")
items = {name: item for name, item in primary["items"].items() if name != "anchor_pi"}
tie = primary["items"]["anchor_pi"]


def mean_of(item, key):
    return item[key]["mean"]


def ci_of(item, key):
    return item[key]["ci95"]


def heading(title):
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


# ---------------------------------------------------------------------------------------------------- [0]
heading("[0] reading the registered numbers back (asserted)")
assert abs(mean_of(items["fp32.randn"], "D") - 24.7249) < 1e-3, mean_of(items["fp32.randn"], "D")
assert scored["tally"] == {"PASS": 28, "FAIL": 2, "INCONCLUSIVE": 0, "NOT SCORED": 0}, scored["tally"]
for arm_name in ("leak0.3803", "leak0"):
    assert scored["arms"][arm_name]["tally"] == scored["tally"], arm_name
assert abs(primary["leak"]["k_w_per_c"] - 0.19940) < 1e-4
assert abs(arm_zero["leak"]["k_w_per_c"]) < 1e-12 and abs(arm_e71["leak"]["k_w_per_c"] - 0.3803) < 1e-9
print(f"D(fp32 randn) = {mean_of(items['fp32.randn'], 'D'):.3f} W; tally {scored['tally']} at the primary and both "
      f"arms; k = {primary['leak']['k_w_per_c']:.4f} / {arm_zero['leak']['k_w_per_c']:.4f} / "
      f"{arm_e71['leak']['k_w_per_c']:.4f} W/C; {len(items)} kinds + the tie")

# ---------------------------------------------------------------------------------------------------- [C1]
heading("[C1] the heat column (dT_win) and the die reading's whole-degree steps")
print("[C1.1] dT_win cells whose 95% interval has zero width (every pass read the same window mean):")
zero_width = sorted(name for name, item in items.items() if ci_of(item, "dT_win") == 0)
for name in zero_width:
    print(f"   {name:24s} dT {mean_of(items[name], 'dT_win'):.2f} [+- {ci_of(items[name], 'dT_win'):.2f}]   "
          f"S {mean_of(items[name], 'S'):6.3f} W")
print(f"   {len(zero_width)} of {len(items)} kinds")

by_power = sorted(items.items(), key=lambda pair: -mean_of(pair[1], "S"))
print()
print("[C1.2] dT / S for every kind, sorted by S (C per W of switching over idle):")
print(f"   {'kind':24s} {'S W':>7s} {'dT C':>6s} {'+-95%':>6s} {'dT/S':>7s}  per-pass dT")
for name, item in by_power:
    per_pass = [primary["per_pass"][p][name]["dT_win"] for p in sorted(primary["per_pass"])
                if name in primary["per_pass"][p]]
    print(f"   {name:24s} {mean_of(item, 'S'):7.3f} {mean_of(item, 'dT_win'):6.2f} {ci_of(item, 'dT_win'):6.2f} "
          f"{mean_of(item, 'dT_win') / mean_of(item, 'S'):7.3f}  {' '.join(f'{v:.2f}' for v in per_pass)}")
resolved = [(name, item) for name, item in by_power if mean_of(item, "S") > S_RESOLVED_W]
limited = [(name, item) for name, item in by_power if mean_of(item, "S") <= S_RESOLVED_W]
ratio_resolved = [mean_of(item, "dT_win") / mean_of(item, "S") for _, item in resolved]
ratio_limited = [mean_of(item, "dT_win") / mean_of(item, "S") for _, item in limited]
power_hi = [mean_of(item, "S") for _, item in resolved]
heat_hi = [mean_of(item, "dT_win") for _, item in resolved]
slope_origin = sum(a * b for a, b in zip(power_hi, heat_hi)) / sum(a * a for a in power_hi)
count_hi = len(power_hi)
power_mean, heat_mean = sum(power_hi) / count_hi, sum(heat_hi) / count_hi
power_ss = sum((a - power_mean) ** 2 for a in power_hi)
slope = sum((a - power_mean) * (b - heat_mean) for a, b in zip(power_hi, heat_hi)) / power_ss
offset = heat_mean - slope * power_mean
residuals = [b - (offset + slope * a) for a, b in zip(power_hi, heat_hi)]
resid_var = sum(r * r for r in residuals) / (count_hi - 2)
se_slope = math.sqrt(resid_var / power_ss)
se_offset = math.sqrt(resid_var * (1 / count_hi + power_mean * power_mean / power_ss))
print()
print(f"   S > {S_RESOLVED_W:.0f} W: {len(resolved)} kinds "
      f"(fp32 {sum(1 for name, _ in resolved if name.startswith('fp32'))}, "
      f"fp16 {sum(1 for name, _ in resolved if name.startswith('fp16'))}, "
      f"int8 {sum(1 for name, _ in resolved if name.startswith('int8'))}); "
      f"S {min(power_hi):.2f}-{max(power_hi):.2f} W; dT/S {min(ratio_resolved):.3f}-{max(ratio_resolved):.3f} C/W; "
      f"through the origin {slope_origin:.4f} C/W")
print(f"   least squares on the same {count_hi}: dT = {offset:.3f} (+- {se_offset:.3f} SE) + {slope:.4f} "
      f"(+- {se_slope:.4f} SE) x S; residual sd {math.sqrt(resid_var):.3f} C")
print(f"   S <= {S_RESOLVED_W:.0f} W: {len(limited)} kinds; dT/S {min(ratio_limited):.3f} to {max(ratio_limited):.3f} C/W")
print()
print("[C1.3] the same power, different readings; different power, the same reading:")
for first_name, second_name in (("fp32.pi", None), ("int8.ones", "int8.full"), ("fp32.sparse50", "fp16.wsparse50")):
    first = items[first_name]
    if second_name is None:
        print(f"   fp32.pi  S {mean_of(first, 'S'):.3f} W  dT {mean_of(first, 'dT_win'):.2f} +- "
              f"{ci_of(first, 'dT_win'):.2f}   |   anchor_pi (the built-in pi tie, the same values)  "
              f"S {mean_of(tie, 'S'):.3f} W  dT {mean_of(tie, 'dT_win'):.2f} +- {ci_of(tie, 'dT_win'):.2f}")
    else:
        second = items[second_name]
        print(f"   {first_name}  S {mean_of(first, 'S'):.3f} W  dT {mean_of(first, 'dT_win'):.2f} +- "
              f"{ci_of(first, 'dT_win'):.2f}   |   {second_name}  S {mean_of(second, 'S'):.3f} W  "
              f"dT {mean_of(second, 'dT_win'):.2f} +- {ci_of(second, 'dT_win'):.2f}")
print("   the zeros (each type's own zero-data level):")
for fmt_name in ("fp32", "fp16", "int8"):
    zeros = items[f"{fmt_name}.zeros"]
    print(f"   {fmt_name}.zeros  S {mean_of(zeros, 'S'):.3f} W  dT {mean_of(zeros, 'dT_win'):.2f} "
          f"[{mean_of(zeros, 'dT_win') - ci_of(zeros, 'dT_win'):.2f}, "
          f"{mean_of(zeros, 'dT_win') + ci_of(zeros, 'dT_win'):.2f}]")
print()
print(f"[C1.4] S x {slope_origin:.3f} C/W for the kinds at S <= {S_RESOLVED_W:.0f} W: an extrapolation of the resolved "
      f"kinds' ratio, NOT a measurement")
for name, item in limited:
    print(f"   {name:24s} S {mean_of(item, 'S'):6.3f} W -> {mean_of(item, 'S') * slope_origin:4.2f} C   "
          f"(window mean read {mean_of(item, 'dT_win'):.2f})")

# ---------------------------------------------------------------------------------------------------- [C2]
heading("[C2] the derived price of a moving operand-bus bit in a gated lane (not registered)")
convention = kinds_doc["facts"]["hamming_convention"]
print("kinds.json facts.hamming_convention:")
print("   a_figure:", convention["a_figure"], "| bus_bits_per_op:", convention["bus_bits_per_op"])
print("   A_BROADCAST_IS_A_CONVENTION:", convention["A_BROADCAST_IS_A_CONVENTION"])
slots = {"fp32": 8, "fp16": 8, "int8": 16}
print()
print(f"   {'cell':26s} {'D W':>6s} {'+-95%':>6s} {'bits/op':>8s} {'R op/s':>11s} {'fJ/bit':>7s} {'[95%]':>15s}  "
      f"counting")
for name, side in (("fp32.a_randn_b_zeros", "A"), ("fp32.a_zeros_b_randn", "B"), ("fp16.a_randn_b_zeros", "A"),
                   ("fp16.a_zeros_b_randn", "B"), ("int8.a_full_b_zeros", "A"), ("int8.a_zeros_b_full", "B")):
    item = items[name]
    d_w, ci_w, rate, bits_op = mean_of(item, "D"), ci_of(item, "D"), mean_of(item, "rate"), item["bus_bits_per_op"]
    countings = [(bits_op, "lane-counted (kinds.json convention)" if side == "A"
                  else "per slot (each slot its own word)")]
    if side == "A":
        countings.append((bits_op / slots[item["type"]], f"per broadcast word (bits / {slots[item['type']]})"))
    for bits_used, counting in countings:
        fj_bit = d_w / (rate * bits_used) * 1e15
        print(f"   {name:26s} {d_w:6.3f} {ci_w:6.3f} {bits_used:8.0f} {rate:11.4e} {fj_bit:7.1f} "
              f"[{(d_w - ci_w) / (rate * bits_used) * 1e15:6.1f}, {(d_w + ci_w) / (rate * bits_used) * 1e15:6.1f}]  "
              f"{side} moves; {counting}" + ("; int8 bus counts provisional" if item["type"] == "int8" else ""))

# ---------------------------------------------------------------------------------------------------- [C3]
heading("[C3] Q130(b) r2 on int8: predicted / measured D32 (watts above fp32 zeros), both variants")
for variant in ("variant_A", "variant_B"):
    int8_rows = {key: row for key, row in scored["q130b"][variant]["rows"].items() if key.startswith("int8.")}
    order = sorted(int8_rows, key=lambda key: -int8_rows[key]["measured_D32"])
    ratio = {key: int8_rows[key]["predicted"] / int8_rows[key]["measured_D32"] for key in order}
    above = [key for key in order if int8_rows[key]["measured_D32"] > 1.5]
    mean_err = sum(int8_rows[key]["error_w"] for key in order) / len(order)
    print(f" {variant}: mean error {mean_err:+.3f} W over {len(order)} int8 kinds; ratio over the {len(above)} kinds "
          f"with measured D32 > 1.5 W: {min(ratio[key] for key in above):.2f}-{max(ratio[key] for key in above):.2f}; "
          f"below 1.5 W: " + ", ".join(f"{key.split('.')[1]} {ratio[key]:.2f}" for key in order if key not in above))
    for key in order:
        print(f"   {key:22s} measured {int8_rows[key]['measured_D32']:6.3f}  predicted "
              f"{int8_rows[key]['predicted']:7.3f}  ratio {ratio[key]:5.2f}  error {int8_rows[key]['error_w']:+7.3f}")

# ---------------------------------------------------------------------------------------------------- [C4]
heading("[C4] E78-R3f, static bits: neg_ones - ones, against the registered +-0.30 W")
for cell in scored["rules"]["E78-R3f"]["cells"]:
    diff = cell["diff"]
    inside = -0.30 < diff["lo"] and diff["hi"] < 0.30
    print(f"   {cell['cell']:26s} {diff['mean']:+.3f} W, 95% [{diff['lo']:+.3f}, {diff['hi']:+.3f}]  inside +-0.30: "
          f"{inside}  -> {cell['verdict']} ({'registered' if cell['registered'] else 'reported'}); "
          f"|bound| {max(-diff['lo'], diff['hi']):.3f}")
flip_bits = {"int8": ("0xFF", "0x01", 7), "fp16": ("0xBC00", "0x3C00", 1), "fp32": ("0xBF800000", "0x3F800000", 1)}
for fmt_name, (minus_one, plus_one, nbits) in flip_bits.items():
    print(f"   {fmt_name}: -1 is {minus_one}, +1 is {plus_one}: they differ in {nbits} bit(s) per element")

# ---------------------------------------------------------------------------------------------------- [C5]
heading("[C5] what the +-95% covers: one fixed tile, between passes, at one leakage slope")
print(" D, S and pJ/op(S) at the three leakage slopes (k = 0, auto 0.1994, 0.3803 W/C); span = |k=0 - k=0.3803|:")
spans = []
for name, item in by_power:
    arm_a, arm_b = arm_zero["items"][name], arm_e71["items"][name]
    span_d = abs(mean_of(arm_a, "D") - mean_of(arm_b, "D"))
    spans.append((span_d, name))
    print(f"   {name:24s} D {mean_of(arm_a, 'D'):7.3f} / {mean_of(item, 'D'):7.3f} / {mean_of(arm_b, 'D'):7.3f} "
          f"(span {span_d:5.3f}, +-95% {ci_of(item, 'D'):5.3f})   S {mean_of(arm_a, 'S'):7.3f} / "
          f"{mean_of(item, 'S'):7.3f} / {mean_of(arm_b, 'S'):7.3f}   pJ/op(S) {mean_of(arm_a, 'pj_op_S'):6.0f} / "
          f"{mean_of(item, 'pj_op_S'):6.0f} / {mean_of(arm_b, 'pj_op_S'):6.0f}")
spans.sort(reverse=True)
print(f"   largest D spans: " + ", ".join(f"{name} {span:.2f} W" for span, name in spans[:4]))
half = []
for name, item in by_power:
    arm_a, arm_b = arm_zero["items"][name], arm_e71["items"][name]
    half.append((abs(mean_of(arm_a, "pj_op_S") - mean_of(arm_b, "pj_op_S")) / 2 / mean_of(item, "pj_op_S") * 100,
                 name, abs(mean_of(arm_a, "S") - mean_of(arm_b, "S")) / 2, mean_of(item, "S")))
half.sort(reverse=True)
print("   pJ/op(S), half the arm span as % of the primary: random data "
      + ", ".join(f"{name} {pct:.2f}%" for pct, name, _, _ in half if name in ("fp32.randn", "fp16.randn", "int8.full"))
      + f"; on the {sum(1 for _, _, _, s in half if s > S_RESOLVED_W)} kinds with S > {S_RESOLVED_W:.0f} W at most "
      f"{max(pct for pct, _, _, s in half if s > S_RESOLVED_W):.2f}%; over all kinds at most {half[0][0]:.2f}% "
      f"({half[0][1]}, S {half[0][3]:.3f} W +- {half[0][2]:.3f} W)")
print("   the largest: " + ", ".join(f"{name} {pct:.1f}%" for pct, name, _, _ in half[:6]))
print()
print(" the spread between tile draws (kinds.json `replicates`: the same rule re-drawn with independent seeds; "
      "2.5-97.5% of the draws), against this tile:")
outside, checked = [], 0
for fmt_name in ("fp32", "fp16", "int8"):
    for kind, record in kinds_doc["kinds"][fmt_name].items():
        replicates = record.get("replicates")
        name = f"{fmt_name}.{kind}"
        if not replicates or name not in items:
            continue
        gated_band, bus_band = replicates.get("gated_lane_frac"), replicates.get("bus_bits_per_op")
        item = items[name]
        flags = []
        for label, value, band in (("gated", item["gated_lane_frac"], gated_band),
                                   ("bus bits", item["bus_bits_per_op"], bus_band)):
            checked += 1
            if not band["p2.5"] <= value <= band["p97.5"]:
                flags.append(label)
                outside.append(f"{name} {label} {value} (draws {band['p2.5']}-{band['p97.5']})")
        print(f"   {name:24s} n {gated_band['n']:3d}  gated {item['gated_lane_frac']:.3f} (draws "
              f"{gated_band['p2.5']:.3f}-{gated_band['p97.5']:.3f})   bus bits/op {item['bus_bits_per_op']:6d} (draws "
              f"{bus_band['p2.5']:.0f}-{bus_band['p97.5']:.0f}, sd {bus_band['sd'] / bus_band['mean'] * 100:.1f}% of the "
              f"mean {bus_band['mean']:.0f})" + (f"   <- this tile outside the band: {', '.join(flags)}" if flags else ""))
print(f"   outside their rule's 2.5-97.5% band: {len(outside)} of {checked} checks "
      f"(about {0.05 * checked:.1f} expected by chance): {'; '.join(outside)}")
deterministic = sorted(name for name in items
                       if not (kinds_doc["kinds"][items[name]["type"]].get(items[name]["kind"], {}) or {})
                       .get("replicates"))
print(f"   no replicates (a deterministic tile): {', '.join(deterministic)}")

# ---------------------------------------------------------------------------------------------------- [C6]
heading("[C6] the in-flight peek: pass 7814's runs around 13:48:03 PDT, and that pass's value for the run it overlapped")


def pdt(ms):
    return datetime.datetime.fromtimestamp(ms / 1000, PDT).strftime("%H:%M:%S.%f")[:-3]


window_lo_ms = int(datetime.datetime(2026, 10, 31, 13, 47, 55, tzinfo=PDT).timestamp() * 1000)
window_hi_ms = int(datetime.datetime(2026, 10, 31, 13, 48, 12, tzinfo=PDT).timestamp() * 1000)
with open(os.path.join(HERE, "aifoundry3", "kinds", "p7814", "marks.jsonl")) as handle:
    for line in handle:
        mark = json.loads(line)
        if mark["t_end_ms"] >= window_lo_ms and mark["t_start_ms"] <= window_hi_ms:
            start = mark["t_start_ms"]
            print(f"   {mark['kind']:7s} #{mark.get('pos', '-')!s:3s} {mark['item']:22s} {pdt(start)} -> "
                  f"{pdt(mark['t_end_ms'])}   idle bracket {pdt(start - 1200)}-{pdt(start - 200)}, window "
                  f"{pdt(start + 1000)}-{pdt(start + 3000)}")
for name in ("fp16.pair_half_zero", "fp16.wsparse50"):
    per_pass = {p: primary["per_pass"][p][name] for p in sorted(primary["per_pass"]) if name in primary["per_pass"][p]}
    print(f"   {name}: D by pass " + ", ".join(f"{p} {v['D']:.3f}" for p, v in per_pass.items())
          + "; idle80 by pass " + ", ".join(f"{p} {v['idle80']:.3f}" for p, v in per_pass.items()))

# ---------------------------------------------------------------------------------------------------- [C7]
heading("[C7] wording")
print("(a) one operand all zero, D over the type's own zeros (E78-R3a):")
for cell in scored["rules"]["E78-R3a"]["cells"]:
    print(f"   {cell['cell']:28s} D {cell['D_w']['mean']:.3f} W, ratio {cell['ratio']['mean']:.3f}")
print("(b) replication targets (predictions-e78.json replication_targets) against E78:")
for name, target in registration["replication_targets"].items():
    measured = scored["rules"]["E78-R4"][name]["measured"]["mean"]
    print(f"   {name:12s} E78 {measured:7.3f}  target {target['target_w']:7.3f}  |diff| "
          f"{abs(measured - target['target_w']):.3f} W   source: {target['source']}")
print("(c) the tally, as the frozen scorer counts it and as E78.md registers R3c:")
rule_r3c = registration["rules"]["E78-R3c"]
print(f"   registered R3c pass_if: {rule_r3c['pass_if']!r}; scored.json emits "
      f"{len(scored['rules']['E78-R3c']['cells'])} cell verdicts: "
      f"{[cell['verdict'] for cell in scored['rules']['E78-R3c']['cells']]}")
verdicts = []
for name, rule in scored["rules"].items():
    if name in ("E78-R1", "E78-R2"):
        verdicts += list(rule["verdict"].values())
    elif name == "E78-R4":
        verdicts += [entry["verdict"] for entry in rule.values()]
    elif name == "E78-R5":
        continue
    elif name == "E78-R3c":
        cell_verdicts = [cell["verdict"] for cell in rule["cells"]]
        verdicts.append("PASS" if all(v == "PASS" for v in cell_verdicts)
                        else ("NOT SCORED" if "NOT SCORED" in cell_verdicts else "FAIL"))
    elif "cells" in rule and "verdict" not in rule:
        verdicts += [cell["verdict"] for cell in rule["cells"]]
    elif "verdict" in rule:
        verdicts.append(rule["verdict"])
counts = {key: sum(1 for v in verdicts if v == key) for key in ("PASS", "FAIL", "INCONCLUSIVE", "NOT SCORED")}
print(f"   as registered (R3c one verdict): {counts} of {len(verdicts)}; as the frozen scorer counts: "
      f"{scored['tally']} of {sum(scored['tally'].values())}")
