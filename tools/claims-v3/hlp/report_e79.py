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

Correction of Sat 31 Oct 2026 (after verification; desk only, no band moves): the resolution rule above was
applied to the price lists but never to the derived quantities P4, P5 and P6 are scored on. It now is: a derived
ratio resting on fewer than 3 passes, or dividing by a single-bit price or an h0 switching figure whose 95%
interval contains zero, is `not scored`. A PASS that compares a bound and would pass even if the price tested
were zero is flagged `vacuous`. The same scoring is applied to the registered E71-slope arm (--hl-leak) and the
verdicts that move between the two slopes are tabulated.
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


def score_rules(C, pred, min_passes):
    """Every registered rule scored on one reduction (the fitted-slope one or the E71-slope arm)."""
    P = C["prices"]
    SW = C["switching"]

    def price(key, bit):
        x = P.get(key, {}).get(str(bit)) or P.get(key, {}).get(bit)
        return x

    def ok(x):
        return x and x.get("fJ") is not None and (x.get("n_passes") or 0) >= min_passes

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

    rules = []

    def score(rid, got, test, verdict, note="", **extra):
        r = next((x for x in pred["rules"] if x["id"] == rid), {"id": rid, "what": "", "leg": "primary"})
        rules.append({"id": rid, "leg": r.get("leg", "primary"), "what": r.get("what", ""),
                      "test": r.get("test", test), "measured": got, "verdict": verdict, "note": note, **extra})

    def unscored(rid, test, value, why):
        """the registered resolution rule: the value is printed for information and takes no part in the tally"""
        score(rid, None, test, "not scored", "; ".join(why), unscored_value=value)

    def band(rid, got, lo, hi, note="", why=None):
        if why:
            return unscored(rid, f"in [{lo}, {hi}]", got, why)
        if got is None:
            return score(rid, None, f"in [{lo}, {hi}]", "not scored", note or "inputs unresolved")
        score(rid, got, f"in [{lo}, {hi}]", "PASS" if lo <= got <= hi else "FAIL", note)

    def atleast(rid, got, lo, note="", why=None):
        if why:
            return unscored(rid, f">= {lo}", got, why)
        if got is None:
            return score(rid, None, f">= {lo}", "not scored", note or "inputs unresolved")
        score(rid, got, f">= {lo}", "PASS" if got >= lo else "FAIL", note)

    def atmost(rid, got, hi, note="", why=None):
        if why:
            return unscored(rid, f"<= {hi}", got, why)
        if got is None:
            return score(rid, None, f"<= {hi}", "not scored", note or "inputs unresolved")
        score(rid, got, f"<= {hi}", "PASS" if got <= hi else "FAIL", note)

    def bounds_note(key, bits):
        b = [x for x in bits if ok(price(key, x)) and not resolved(price(key, x))]
        return f"; inputs that are bounds: bits {b}" if b else ""

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
                f"{len(xs)} of 7 magnitude positions kept" + bounds_note(key, xs))

    def sign_rule(rid, key, test):
        x7, x6 = price(key, 7), price(key, 6)
        if not (ok(x7) and ok(x6)):
            return score(rid, None, test, "not scored", "inputs unresolved")
        hw = math.hypot(x7.get("fJ_ci95") or 0, x6.get("fJ_ci95") or 0)
        verdict = "PASS" if x7["fJ"] >= x6["fJ"] - hw else "FAIL"
        # vacuous: bit 6's price minus the allowance is <= 0, so the test passes even if bit 7 cost nothing
        vac = verdict == "PASS" and x6["fJ"] - hw <= 0
        note = bounds_note(key, [6, 7]).lstrip("; ")
        if vac:
            note = (note + "; " if note else "") + ("vacuous: the allowance exceeds bit 6's price, so the test "
                                                    "passes even if bit 7 cost nothing")
        score(rid, {"bit7_fJ": x7["fJ"], "bit6_fJ": x6["fJ"], "allowance_fJ": hw}, test, verdict, note,
              vacuous=vac)

    sign_rule("P3b", "int8_b", "fJ(7) >= fJ(6) - 95% half-width of the difference")

    # ---------------------------------------------------------------- P4, zeros
    for fmt in ("fp16", "int8"):
        s = SW.get(fmt, {})
        n = s.get("zeros_over_h0_n") or 0
        why = []
        if n < min_passes:
            why.append(f"the ratio rests on {n} passes")
        h0, h0hw = s.get("h0_switching_W"), s.get("ci95")
        if h0 is None or h0hw is None or h0 - h0hw <= 0:
            why.append("the h0 switching in its denominator is a bound")
        atmost(f"P4_{fmt}", s.get("zeros_over_h0"), 0.20,
               f"zeros {s.get('zeros_switching_W')} W, h0 {s.get('h0_switching_W')} W over idle "
               f"{s.get('idle_W')} W, {n} passes", why=why)

    # ---------------------------------------------------------------- P5, additivity
    add = C.get("additivity", {})
    for fmt, n2, n4 in (("fp16", "b16m2", "b16m4"), ("int8", "b8m2", "b8m4")):
        got = {}
        for rung, lo, hi, rid in ((n2, 0.55, 1.05, f"P5_{fmt}_2"), (n4, 0.35, 1.00, f"P5_{fmt}_4")):
            x = add.get(rung) or {}
            why = []
            if (x.get("n_passes") or 0) < min_passes:
                why.append(f"the ratio rests on {x.get('n_passes') or 0} passes")
            bnd = [b for b in (x.get("bits") or []) if not resolved(price(f"{fmt}_b", b))]
            if bnd:
                why.append(f"its denominator sums single-bit prices that are bounds (bits {bnd})")
            band(rid, x.get("ratio"), lo, hi, f"bits {x.get('bits')}", why=why)
            got[rung] = None if why else x.get("ratio")
        r2, r4 = got.get(n2), got.get(n4)
        if r2 is None or r4 is None:
            raw2, raw4 = (add.get(n2) or {}).get("ratio"), (add.get(n4) or {}).get("ratio")
            unscored(f"P5_{fmt}_mono", "<= 0.1",
                     (raw4 - raw2) if (raw2 is not None and raw4 is not None) else None,
                     ["r2 or r4 is not scored"])
        else:
            atmost(f"P5_{fmt}_mono", r4 - r2, 0.10, "r4 - r2")

    # ---------------------------------------------------------------- P6, the layout control
    lc = C.get("layout_control", {})
    for fmt, nm, pkey, pbit in (("fp16", "b16p_9", "fp16_b", 9), ("int8", "b8p_6", "int8_b", 6)):
        x = lc.get(nm) or {}
        why = []
        if (x.get("n_passes") or 0) < min_passes:
            why.append(f"the ratio rests on {x.get('n_passes') or 0} passes")
        if not resolved(price(pkey, pbit)):
            why.append(f"its denominator, the primary {x.get('primary')}, is a bound")
        band(f"P6_{fmt}", x.get("ratio"), 0.80, 1.25,
             f"control {x.get('fJ_control')} fJ vs primary {x.get('fJ_primary')} fJ", why=why)

    # ---------------------------------------------------------------- P7, P8
    # amendment A4: the same three rules re-scored on the kg list, the only int8 B layout that alternates
    xs = [b for b in MANT["int8"] if ok(price("int8_b_kg", b))]
    atleast("P3a_kg", spearman(xs, [price("int8_b_kg", b)["fJ"] for b in xs]) if len(xs) >= 3 else None, 0.60,
            f"{len(xs)} of 7 magnitude positions kept, kg layout" + bounds_note("int8_b_kg", xs))
    sign_rule("P3b_kg", "int8_b_kg", "fJ(7) >= fJ(6) - allowance, kg layout")
    d8k, d8k_bit = dearest("int8_b_kg", list(range(8)))
    tie = price("fp32_b", 22)

    def num_note(x, b, key):
        if x and not resolved(x) and tie and tie.get("fJ"):
            return (f"; the numerator (bit {b}) is a bound, so the ratio lies in "
                    f"[{x['fJ_lo'] / tie['fJ']:.4f}, {x['fJ_hi'] / tie['fJ']:.4f}]")
        return ""

    band("P8_kg", (d8k["fJ"] / tie["fJ"]) if (d8k and resolved(tie)) else None, 0.15, 0.60,
         (f"int8 B kg bit {d8k_bit} over this run's b32_22" + num_note(d8k, d8k_bit, "int8_b_kg")) if d8k else "")
    band("P7", tie["fJ"] if ok(tie) else None, 756, 1260,
         f"95% [{(tie or {}).get('fJ_lo')}, {(tie or {}).get('fJ_hi')}]" if ok(tie) else "")
    d8b, d8b_bit = dearest("int8_b", list(range(8)))
    band("P8", (d8b["fJ"] / tie["fJ"]) if (d8b and resolved(tie)) else None, 0.15, 0.60,
         (f"int8 B bit {d8b_bit} over this run's b32_22" + num_note(d8b, d8b_bit, "int8_b")) if d8b else "")
    return rules


def tally(rules):
    t = {"pass": sum(1 for r in rules if r["verdict"] == "PASS"),
         "fail": sum(1 for r in rules if r["verdict"] == "FAIL"),
         "not_scored": sum(1 for r in rules if r["verdict"] == "not scored"),
         "vacuous": [r["id"] for r in rules if r.get("vacuous")], "of": len(rules)}
    reg = [r for r in rules if r["leg"] != "A4 re-score"]
    t["registered"] = {"pass": sum(1 for r in reg if r["verdict"] == "PASS"),
                       "fail": sum(1 for r in reg if r["verdict"] == "FAIL"),
                       "not_scored": sum(1 for r in reg if r["verdict"] == "not scored"), "of": len(reg)}
    return t


def tally_line(t):
    vac = (f" ({len(t['vacuous'])} of them vacuous: {', '.join(t['vacuous'])})" if t["vacuous"] else "")
    g = t["registered"]
    return (f"{t['pass']} passed{vac}, **{t['fail']} failed**, {t['not_scored']} not scored, of {t['of']}; "
            f"of the {g['of']} registered before the data (A4's three re-scores left out): {g['pass']} passed, "
            f"{g['fail']} failed, {g['not_scored']} not scored.")


def measured_cell(r):
    m = r["measured"]
    if m is None:
        u = r.get("unscored_value")
        if u is None:
            return "—"
        return f"— (would read {u:.4g})" if isinstance(u, (int, float)) else "—"
    return (f"{m:.4g}" if isinstance(m, (int, float)) else ", ".join(f"{k} {v:.4g}" for k, v in m.items()))


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
    add = C.get("additivity", {})
    lc = C.get("layout_control", {})

    def price(key, bit):
        x = P.get(key, {}).get(str(bit)) or P.get(key, {}).get(bit)
        return x

    def ok(x):
        return x and x.get("fJ") is not None and (x.get("n_passes") or 0) >= a.min_passes

    rules = score_rules(C, pred, a.min_passes)
    rules_leak = score_rules(leak, pred, a.min_passes) if leak else None
    md, PRICE_KEYS = [], []

    # ---------------------------------------------------------------- the tables
    md.append(f"## The tables — card {card}, {C['clock_mhz']} MHz, {C['v_mean']*1000:.1f} mV\n")
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
    md.append("A rule is `not scored` when a derived ratio it tests rests on fewer than 3 passes or divides by a "
              "price (or an h0 switching figure) whose 95% interval contains zero — the registered resolution rule, "
              "applied to the derived quantities since the correction of 31 Oct (the first scoring applied it to "
              "the price lists only). A `vacuous` PASS compares a bound and would pass even if the price tested "
              "were zero.\n")
    md.append("| rule | leg | what | test | measured | verdict | note |")
    md.append("|---|---|---|---|---|---|---|")
    for r in rules:
        v = r["verdict"] + (" (vacuous)" if r.get("vacuous") else "")
        md.append(f"| **{r['id']}** | {r['leg']} | {r['what']} | {r['test']} | {measured_cell(r)} | **{v}** | "
                  f"{r.get('note', '')} |")
    T = tally(rules)
    n_pass, n_fail, n_ns = T["pass"], T["fail"], T["not_scored"]
    md.append(f"\n{tally_line(T)}\n")
    TL = None
    if rules_leak:
        TL = tally(rules_leak)
        byid = {r["id"]: r for r in rules_leak}
        moved = [(r, byid.get(r["id"])) for r in rules
                 if byid.get(r["id"]) and (r["verdict"], bool(r.get("vacuous")))
                 != (byid[r["id"]]["verdict"], bool(byid[r["id"]].get("vacuous")))]
        md.append("### The registered rules at E71's slope (the registered sensitivity arm)\n")
        md.append(f"At 0.3803 W/°C: {tally_line(TL)}\n")
        if moved:
            md.append("| rule | fitted slope | E71 slope | measured at E71's slope | note at E71's slope |")
            md.append("|---|---|---|---|---|")
            for r, y in moved:
                v0 = r["verdict"] + (" (vacuous)" if r.get("vacuous") else "")
                v1 = y["verdict"] + (" (vacuous)" if y.get("vacuous") else "")
                md.append(f"| **{r['id']}** | {v0} | **{v1}** | {measured_cell(y)} | {y.get('note', '')} |")
        else:
            md.append("No verdict moves between the two slopes.")
        md.append("")
    if leak:
        md.append("### Sensitivity: every price at E71's measured idle slope 0.3803 W/°C\n")
        md.append("A **bound** is a price whose 95% interval contains zero. The change is quoted only for a price "
                  "that is a coefficient at the fitted slope; a change in a bound means nothing.\n")
        md.append("| list | bit | fitted-slope fJ [95%] | E71-slope fJ [95%] | change |")
        md.append("|---|---|---|---|---|")
        span = {}
        for key in sorted(P):
            for b in sorted(P[key], key=lambda s: int(s)):
                x, y = P[key][b], leak["prices"].get(key, {}).get(b)
                if not (x and y and x.get("fJ") and y.get("fJ")):
                    continue
                bx, by = (x.get("fJ_lo") or 0) <= 0, (y.get("fJ_lo") or 0) <= 0
                ch = 100 * (y["fJ"] / x["fJ"] - 1)
                if not bx:
                    span.setdefault(key, []).append((ch, by))
                md.append(f"| {key} | {b} | {x['fJ']:.0f} [{x['fJ_lo']:.0f}, {x['fJ_hi']:.0f}]"
                          f"{' bound' if bx else ''} | {y['fJ']:.0f} [{y['fJ_lo']:.0f}, {y['fJ_hi']:.0f}]"
                          f"{' **bound**' if by and not bx else (' bound' if by else '')} | "
                          f"{'—' if bx else f'{ch:+.1f}%'} |")
        md.append("\nPer list, over the positions that are coefficients at the fitted slope:\n")
        md.append("| list | positions | change at E71's slope | of them bounds at E71's slope |")
        md.append("|---|---|---|---|")
        for key, v in span.items():
            md.append(f"| {key} | {len(v)} | {min(c for c, _ in v):+.1f}% to {max(c for c, _ in v):+.1f}% | "
                      f"{sum(1 for _, bb in v if bb)} |")
    out = "\n".join(md) + "\n"
    print(out, end="")
    if a.md:
        open(a.md, "w").write(out)
    if a.json:
        json.dump({"card": card, "rules": rules, "n_pass": n_pass, "n_fail": n_fail, "n_not_scored": n_ns,
                   "n_vacuous": len(T["vacuous"]), "tally": T,
                   "rules_leak0.3803": rules_leak, "tally_leak0.3803": TL,
                   "prices": P, "switching": SW, "additivity": add, "layout_control": lc, "order_probe": OP, "marginal": MG,
                   "passes": C["passes"], "kept": C["kept"], "runs": C["runs"],
                   "leak_W_per_C": C["leak_W_per_C"], "v_mean": C["v_mean"],
                   "cycles_per_op": C["cycles_per_op"]}, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
