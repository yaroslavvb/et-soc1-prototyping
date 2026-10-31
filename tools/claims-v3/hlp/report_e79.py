#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""E79: the results tables and the scored registered rules, from reduce_hlp.py's output.

    python3 tools/claims-v3/hlp/report_e79.py --hl hlp.json --pred predictions.json
        [--hl-leak hlp-leak0.3803.json] --md results.md --json scored.json

Every rule in predictions.json is scored exactly as it is written there. A rule whose inputs are unresolved
(fewer than 3 kept passes, or a price whose 95% interval contains zero where a positive floor is needed) is
reported as `not scored`, never as passed. A failed rule is printed as FAIL.
"""
import argparse
import json
import math

FIELDS = {"fp16": {**{j: "mantissa" for j in range(10)}, **{j: "exponent" for j in range(10, 15)}, 15: "sign"},
          "int8": {**{j: "magnitude" for j in range(7)}, 7: "MSB (sign)"},
          "fp32": {**{j: "mantissa" for j in range(23)}, **{j: "exponent" for j in range(23, 31)}, 31: "sign"}}
MANT = {"fp16": list(range(10)), "int8": list(range(7)), "fp32": list(range(23))}


def spearman(xs, ys):
    def rank(a):
        order = sorted(range(len(a)), key=lambda i: a[i])
        r = [0.0] * len(a)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and a[order[j + 1]] == a[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    if len(xs) < 3:
        return None
    rx, ry = rank(list(xs)), rank(list(ys))
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return None if den == 0 else num / den


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hl", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--hl-leak")
    ap.add_argument("--md")
    ap.add_argument("--json")
    ap.add_argument("--min-passes", type=int, default=3)
    a = ap.parse_args()
    hl = json.load(open(a.hl))
    pred = json.load(open(a.pred))
    card = sorted(hl["cards"])[0]
    C = hl["cards"][card]
    leak = json.load(open(a.hl_leak))["cards"][card] if a.hl_leak else None
    P = C["prices"]
    SW = C["switching"]

    def price(key, bit):
        x = P.get(key, {}).get(str(bit)) or P.get(key, {}).get(bit)
        return x

    def ok(x):
        return x and x.get("fJ") is not None and (x.get("n_passes") or 0) >= a.min_passes

    def resolved(x):
        """a coefficient, not a bound: the 95% interval excludes zero"""
        return ok(x) and (x.get("fJ_lo") or 0) > 0

    def dearest(key, bits):
        cand = [(price(key, b), b) for b in bits]
        cand = [(x, b) for x, b in cand if ok(x)]
        if not cand:
            return None, None
        x, b = max(cand, key=lambda t: t[0]["fJ"])
        return x, b

    rules, md, PRICE_KEYS = [], [], []

    def score(rid, got, test, verdict, note=""):
        r = next((x for x in pred["rules"] if x["id"] == rid), {"id": rid, "what": "", "leg": "primary"})
        rules.append({"id": rid, "leg": r.get("leg", "primary"), "what": r.get("what", ""),
                      "test": r.get("test", test), "measured": got, "verdict": verdict, "note": note})

    def band(rid, got, lo, hi, note=""):
        if got is None:
            return score(rid, None, f"in [{lo}, {hi}]", "not scored", note or "inputs unresolved")
        score(rid, got, f"in [{lo}, {hi}]", "PASS" if lo <= got <= hi else "FAIL", note)

    def atleast(rid, got, lo, note=""):
        if got is None:
            return score(rid, None, f">= {lo}", "not scored", note or "inputs unresolved")
        score(rid, got, f">= {lo}", "PASS" if got >= lo else "FAIL", note)

    def atmost(rid, got, hi, note=""):
        if got is None:
            return score(rid, None, f"<= {hi}", "not scored", note or "inputs unresolved")
        score(rid, got, f"<= {hi}", "PASS" if got <= hi else "FAIL", note)

    # ---------------------------------------------------------------- P1, the fp16 shape
    for rid, key in (("P1a", "fp16_b"), ("P1a_A", "fp16_a")):
        xs = [b for b in MANT["fp16"] if ok(price(key, b))]
        atleast(rid, spearman(xs, [price(key, b)["fJ"] for b in xs]), 0.60,
                f"{len(xs)} of 10 mantissa positions kept")
    d16b, d16b_bit = dearest("fp16_b", MANT["fp16"])
    floor = [(price("fp16_b", b), b) for b in MANT["fp16"] if resolved(price("fp16_b", b))]
    if d16b and floor:
        xmin, bmin = min(floor, key=lambda t: t[0]["fJ"])
        atleast("P1b", d16b["fJ"] / xmin["fJ"], 3.0, f"bit {d16b_bit} over bit {bmin}")
    else:
        atleast("P1b", None, 3.0)
    x5, x0 = price("fp16_b", 5), price("fp16_b", 0)
    if ok(x5) and ok(x0):
        got = x5["fJ_lo"] - x0["fJ_hi"]
        score("P1c", {"bit5_lo": x5["fJ_lo"], "bit0_hi": x0["fJ_hi"], "gap_fJ": got},
              "fJ(bit 5) 95% interval above fJ(bit 0)'s", "PASS" if got > 0 else "FAIL")
    else:
        score("P1c", None, "disjoint 95% intervals", "not scored", "inputs unresolved")

    # ---------------------------------------------------------------- P2, the width ratio
    tie = price("fp32_b", 22)
    band("P2b", (d16b["fJ"] / tie["fJ"]) if (d16b and resolved(tie)) else None, 0.25, 0.80,
         f"fp16 B bit {d16b_bit} over this run's b32_22" if d16b else "")
    band("P2b_e65", (d16b["fJ"] / pred["references"]["fp32_B_dearest_fJ"]["value"]) if d16b else None, 0.25, 0.80)
    d16a, d16a_bit = dearest("fp16_a", MANT["fp16"])
    band("P2a", (d16a["fJ"] / pred["references"]["fp32_A_dearest_fJ"]["value"]) if d16a else None, 0.25, 0.80,
         f"fp16 A bit {d16a_bit} over E67's 1440 fJ" if d16a else "")

    # ---------------------------------------------------------------- P3, int8
    for rid, key in (("P3a", "int8_b"), ("P3a_A", "int8_a")):
        xs = [b for b in MANT["int8"] if ok(price(key, b))]
        atleast(rid, spearman(xs, [price(key, b)["fJ"] for b in xs]), 0.60,
                f"{len(xs)} of 7 magnitude positions kept")
    x7, x6 = price("int8_b", 7), price("int8_b", 6)
    if ok(x7) and ok(x6):
        hw = math.hypot(x7.get("fJ_ci95") or 0, x6.get("fJ_ci95") or 0)
        score("P3b", {"bit7_fJ": x7["fJ"], "bit6_fJ": x6["fJ"], "allowance_fJ": hw},
              "fJ(7) >= fJ(6) - 95% half-width of the difference",
              "PASS" if x7["fJ"] >= x6["fJ"] - hw else "FAIL")
    else:
        score("P3b", None, "fJ(7) >= fJ(6) - allowance", "not scored", "inputs unresolved")

    # ---------------------------------------------------------------- P4, zeros
    for fmt in ("fp16", "int8"):
        s = SW.get(fmt, {})
        atmost(f"P4_{fmt}", s.get("zeros_over_h0"), 0.20,
               f"zeros {s.get('zeros_switching_W')} W, h0 {s.get('h0_switching_W')} W over idle "
               f"{s.get('idle_W')} W, {s.get('zeros_over_h0_n')} passes")

    # ---------------------------------------------------------------- P5, additivity
    add = C.get("additivity", {})
    for fmt, n2, n4 in (("fp16", "b16m2", "b16m4"), ("int8", "b8m2", "b8m4")):
        r2 = (add.get(n2) or {}).get("ratio")
        r4 = (add.get(n4) or {}).get("ratio")
        band(f"P5_{fmt}_2", r2, 0.55, 1.05, f"bits {(add.get(n2) or {}).get('bits')}")
        band(f"P5_{fmt}_4", r4, 0.35, 1.00, f"bits {(add.get(n4) or {}).get('bits')}")
        atmost(f"P5_{fmt}_mono", (r4 - r2) if (r2 is not None and r4 is not None) else None, 0.10,
               "r4 - r2")

    # ---------------------------------------------------------------- P6, the layout control
    lc = C.get("layout_control", {})
    for fmt, nm in (("fp16", "b16p_9"), ("int8", "b8p_6")):
        band(f"P6_{fmt}", (lc.get(nm) or {}).get("ratio"), 0.80, 1.25,
             f"control {(lc.get(nm) or {}).get('fJ_control')} fJ vs primary "
             f"{(lc.get(nm) or {}).get('fJ_primary')} fJ")

    # ---------------------------------------------------------------- P7, P8
    # amendment A4: the same three rules re-scored on the kg list, the only int8 B layout that alternates
    xs = [b for b in MANT["int8"] if ok(price("int8_b_kg", b))]
    atleast("P3a_kg", spearman(xs, [price("int8_b_kg", b)["fJ"] for b in xs]) if len(xs) >= 3 else None, 0.60,
            f"{len(xs)} of 7 magnitude positions kept, kg layout")
    y7, y6 = price("int8_b_kg", 7), price("int8_b_kg", 6)
    if ok(y7) and ok(y6):
        hw = math.hypot(y7.get("fJ_ci95") or 0, y6.get("fJ_ci95") or 0)
        score("P3b_kg", {"bit7_fJ": y7["fJ"], "bit6_fJ": y6["fJ"], "allowance_fJ": hw},
              "fJ(7) >= fJ(6) - allowance, kg layout", "PASS" if y7["fJ"] >= y6["fJ"] - hw else "FAIL")
    else:
        score("P3b_kg", None, "fJ(7) >= fJ(6) - allowance, kg layout", "not scored", "inputs unresolved")
    d8k, d8k_bit = dearest("int8_b_kg", list(range(8)))
    band("P8_kg", (d8k["fJ"] / tie["fJ"]) if (d8k and resolved(tie)) else None, 0.15, 0.60,
         f"int8 B kg bit {d8k_bit} over this run's b32_22" if d8k else "")
    band("P7", tie["fJ"] if ok(tie) else None, 756, 1260,
         f"95% [{(tie or {}).get('fJ_lo')}, {(tie or {}).get('fJ_hi')}]" if ok(tie) else "")
    d8b, d8b_bit = dearest("int8_b", list(range(8)))
    band("P8", (d8b["fJ"] / tie["fJ"]) if (d8b and resolved(tie)) else None, 0.15, 0.60,
         f"int8 B bit {d8b_bit} over this run's b32_22" if d8b else "")

    # ---------------------------------------------------------------- the tables
    md.append(f"## Results — card {card}, {C['clock_mhz']} MHz, {C['v_mean']*1000:.1f} mV\n")
    md.append(f"Passes kept {C['passes']} ({C['n_passes']}); runs kept {C['kept']} of {C['runs']}; leakage slope "
              f"{C['leak_W_per_C']:.4f} W/°C from {C['leak_runs']} runs; cycles per op {C['cycles_per_op']}.")
    if C["passes_set_aside"]:
        md.append(f"Passes set aside: {C['passes_set_aside']}.")
    md.append("")
    for key, title, bits in (("fp16_b", "fp16, B side (A = 1.0), jg layout", list(range(16))),
                             ("fp16_a", "fp16, A side (B = 1.0)", list(range(16))),
                             ("int8_b", "int8, B side (A = 1), jg layout - does not alternate (A4)", list(range(8))),
                             ("int8_b_kg", "int8, B side (A = 1), kg layout - the int8 B price list (A4)", list(range(8))),
                             ("int8_a", "int8, A side (B = 1)", list(range(8))),
                             ("fp32_b", "fp32 tie, B side (A = 1.0), jg layout", [22]),
                             ("fp32_b_jgp", "fp32, B side, jgp layout (A4 order probe)", [22]),
                             ("fp32_b_kg", "fp32, B side, kg layout (A4 order probe)", [22]),
                             ("fp16_b_jgp", "fp16, B side, jgp layout (the registered control)", [9]),
                             ("fp16_b_kg", "fp16, B side, kg layout (A4 order probe)", [9]),
                             ("int8_b_jgp", "int8, B side, jgp layout", [6])):
        if key not in P:
            continue
        fmt = key.split("_")[0]
        PRICE_KEYS.append(key)
        md.append(f"### {title}\n")
        md.append("| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |")
        md.append("|---|---|---|---|---|---|---|---|")
        for b in bits:
            x = price(key, b)
            if not x:
                continue
            md.append(f"| {b} | {FIELDS[fmt].get(b, '')} | {x['dW']:.3f} ± {(x['dW_ci95'] or 0):.3f} | "
                      f"**{x['fJ']:.0f}** | [{x['fJ_lo']:.0f}, {x['fJ_hi']:.0f}] | {(x['C_fF'] or 0):.2f} | "
                      f"{(x['electrons'] or 0):.3g} | {x['n_passes']} |")
        xs = [b for b in MANT[fmt] if ok(price(key, b))]
        if len(xs) >= 3:
            rho = spearman(xs, [price(key, b)["fJ"] for b in xs])
            lo = min(price(key, b)["fJ"] for b in xs)
            hi = max(price(key, b)["fJ"] for b in xs)
            md.append(f"\nSignificand Spearman ρ(bit, price) = "
                      f"**{('%.3f' % rho) if rho is not None else '—'}**; span over the kept significand "
                      f"positions **{(hi/lo if lo else float('nan')):.1f}×** ({lo:.0f}–{hi:.0f} fJ).\n")
    OP = C.get("order_probe", {})
    if OP:
        md.append("### The order probe: the same flip in three layouts (amendment A4)\n")
        md.append("The dW ratios divide by no designed count, so they are order-free.\n")
        md.append("| format | jg dW | jgp dW | kg dW | jgp/jg | kg/jg |")
        md.append("|---|---|---|---|---|---|")
        for fmt, e in OP.items():
            g = lambda k: (f"{e[k]['dW']:.3f}" if k in e and e[k].get("dW") is not None else "—")
            r = lambda k: (f"{e[k]:.3f}" if e.get(k) is not None else "—")
            md.append(f"| {fmt} | {g('jg')} | {g('jgp')} | {g('kg')} | {r('dW_jgp_over_jg')} | "
                      f"{r('dW_kg_over_jg')} |")
        md.append("")
    MG = C.get("marginal", {})
    if MG:
        md.append("### The marginal price of a further flipped bit (amendment A4)\n")
        md.append("| format | from | dW per extra flipped bit | marginal fJ per bit | 95% | passes |")
        md.append("|---|---|---|---|---|---|")
        for fmt, e in MG.items():
            md.append(f"| {fmt} | {' - '.join(e['from'])} | "
                      f"{('%.3f' % e['dW_per_extra_bit']) if e['dW_per_extra_bit'] is not None else '—'} | "
                      f"{('%.1f' % e['fJ']) if e['fJ'] is not None else '—'} | "
                      f"± {(e['fJ_ci95'] or 0):.1f} | {e['n_passes']} |")
        md.append("")
    md.append("### Switching over the idle bracket\n")
    md.append("A7: the **zeros − h0** column is paired per pass and needs no idle bracket, so it is the robust "
              "statement of what zeros buy. The idle-bracketed columns are kept because P4 is registered on them; "
              "the bracket is the second before each launch and in a dense pass it can still carry the previous "
              "run's tail, which is why its spread is wide.\n")
    md.append("| format | zeros − h0 (W, idle-free) | 95% | idle bracket W | h0 switching W | zeros switching W | zeros / h0 |")
    md.append("|---|---|---|---|---|---|---|")
    for fmt, s in SW.items():
        md.append(f"| {fmt} | "
                  f"**{('%.3f' % s['zeros_minus_h0_W']) if s.get('zeros_minus_h0_W') is not None else '—'}** | "
                  f"± {(s.get('zeros_minus_h0_ci95') or 0):.3f} | "
                  f"{(s.get('idle_bracket_W') or s.get('idle_W') or 0):.3f} ± {(s.get('idle_bracket_ci95') or 0):.3f} | "
                  f"{(s.get('h0_switching_W') or 0):.3f} ± {(s.get('ci95') or 0):.3f} | "
                  f"{('%.3f' % s['zeros_switching_W']) if s.get('zeros_switching_W') is not None else '—'} | "
                  f"{('%.4f' % s['zeros_over_h0']) if s.get('zeros_over_h0') is not None else '—'} |")
    if add:
        md.append("\n### Additivity (E70's law at low Hamming weight)\n")
        md.append("| rung | bits | ΔW | sum of its own single-bit ΔW ratio | 95% | fJ per bit |")
        md.append("|---|---|---|---|---|---|")
        for n, x in add.items():
            md.append(f"| {n} | {x['bits']} | {(x['dW'] or 0):.3f} | "
                      f"{('%.3f' % x['ratio']) if x['ratio'] is not None else '—'} | "
                      f"± {(x['ci95'] or 0):.3f} | {(x['fJ_per_bit'] or 0):.0f} |")
    if lc:
        md.append("\n### The layout control (the issue order)\n")
        md.append("| control | primary | bit | control fJ | primary fJ | ratio | 95% |")
        md.append("|---|---|---|---|---|---|---|")
        for n, x in lc.items():
            md.append(f"| {n} | {x['primary']} | {x['bit']} | {(x['fJ_control'] or 0):.0f} | "
                      f"{(x['fJ_primary'] or 0):.0f} | "
                      f"{('%.3f' % x['ratio']) if x['ratio'] is not None else '—'} | ± {(x['ci95'] or 0):.3f} |")
    md.append("\n### The registered rules, scored\n")
    md.append("| rule | leg | what | test | measured | verdict |")
    md.append("|---|---|---|---|---|---|")
    for r in rules:
        m = r["measured"]
        ms = ("—" if m is None else (f"{m:.4g}" if isinstance(m, (int, float))
                                     else ", ".join(f"{k} {v:.4g}" for k, v in m.items())))
        md.append(f"| **{r['id']}** | {r['leg']} | {r['what']} | {r['test']} | {ms} | **{r['verdict']}** |")
    n_pass = sum(1 for r in rules if r["verdict"] == "PASS")
    n_fail = sum(1 for r in rules if r["verdict"] == "FAIL")
    n_ns = sum(1 for r in rules if r["verdict"] == "not scored")
    md.append(f"\n{n_pass} passed, **{n_fail} failed**, {n_ns} not scored, of {len(rules)}.\n")
    if leak:
        md.append("### Sensitivity: every price at E71's measured idle slope 0.3803 W/°C\n")
        md.append("| list | bit | fitted-slope fJ | E71-slope fJ | change |")
        md.append("|---|---|---|---|---|")
        for key in sorted(P):
            for b in sorted(P[key], key=lambda s: int(s)):
                x, y = P[key][b], leak["prices"].get(key, {}).get(b)
                if not (x and y and x.get("fJ") and y.get("fJ")):
                    continue
                md.append(f"| {key} | {b} | {x['fJ']:.0f} | {y['fJ']:.0f} | "
                          f"{100*(y['fJ']/x['fJ'] - 1):+.1f}% |")
    out = "\n".join(md) + "\n"
    print(out, end="")
    if a.md:
        open(a.md, "w").write(out)
    if a.json:
        json.dump({"card": card, "rules": rules, "n_pass": n_pass, "n_fail": n_fail, "n_not_scored": n_ns,
                   "prices": P, "switching": SW, "additivity": add, "layout_control": lc, "order_probe": OP, "marginal": MG,
                   "passes": C["passes"], "kept": C["kept"], "runs": C["runs"],
                   "leak_W_per_C": C["leak_W_per_C"], "v_mean": C["v_mean"],
                   "cycles_per_op": C["cycles_per_op"]}, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
