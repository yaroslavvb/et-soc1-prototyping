#!/usr/bin/env python3
"""E116 scorer (Q133): E88's split on a second card, aifoundry3 card 0. Standard library only. Every band, reference and
expectation is read from predictions-e116.json (frozen before the claim); nothing here is tuned to the data.

    python3 tools/claims-v3/e116/score_e116.py --red e116.json [--arm name=<json> ...] --e88rules scored-e88rules.json \
        --readback readback.jsonl --json scored.json --md results.md

--red is reduce_e88.py's output (reduce_e78.py unchanged inside it) on E116's passes; --e88rules is score_e88.py's
output, unchanged, on the same reduction (E88's 32 registered rules scored on this card); --readback is the read-back
pass's readback.jsonl. A part is E88's: (i) D(the constant, result frozen), (iii) D(the random operands, result frozen)
- (i), (ii) D(r_walk) - D(the same operands frozen); D is switching power over the type's zeros (E78's definition, the
board meter), paired within each kept pass; mean over passes, SE from the between-pass scatter, 95% half-width
t(0.975, n-1) x SE. A share is part / D(r_walk), per pass.
"""
import argparse
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
PARTS = ("i_clocked_lane", "iii_operand_multiplier", "ii_result_path")
DESIGN = {"fp32": ("fp32.c_abs", "fp32.r_abs", "fp32.r_walk"), "fp16": ("fp16.c_cancel", "fp16.r_cancel", "fp16.r_walk"),
          "int8": ("int8.c_cancel", "int8.r_cancel", "int8.r_walk")}
ANCHOR = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
H_RULES = ("H1-fp32", "H1-fp16", "H1-int8", "H2-fp32", "H2-fp16", "H2-int8", "H3-fp32", "H3-fp16", "H3-int8",
           "H4-signs-mult", "H4-signs-result", "H5-bus-share", "H6-two-freezes")


def stat(v):
    v = [float(x) for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return {"mean": None, "se": None, "ci95": None, "n": 0, "values": []}
    m = statistics.fmean(v)
    if len(v) < 2:
        return {"mean": m, "se": None, "ci95": None, "n": 1, "values": [round(x, 4) for x in v]}
    se = statistics.stdev(v) / math.sqrt(len(v))
    return {"mean": m, "se": se, "ci95": se * T95.get(len(v) - 1, 1.96), "n": len(v), "values": [round(x, 4) for x in v]}


def per_pass(red):
    return {p: {n: e.get("D") for n, e in items.items()} for p, items in red["per_pass"].items()}


def splits(red):
    pp = per_pass(red)
    out = {}
    for f, (c, r, w) in DESIGN.items():
        rows = [v for v in pp.values() if None not in (v.get(c), v.get(r), v.get(w))]
        parts = {"i_clocked_lane": [v[c] for v in rows], "iii_operand_multiplier": [v[r] - v[c] for v in rows],
                 "ii_result_path": [v[w] - v[r] for v in rows]}
        tot = [v[w] for v in rows]
        a = ANCHOR[f]
        anc = [v for v in pp.values() if None not in (v.get(c), v.get(r), v.get(w), v.get(a))]
        out[f] = {"total": stat(tot), "D": {p: stat(parts[p]) for p in PARTS},
                  "shares": {p: stat([x / t for x, t in zip(parts[p], tot)]) for p in PARTS},
                  "shares_of_anchor": {p: stat([(x[c] if p == PARTS[0] else (x[r] - x[c]) if p == PARTS[1] else x[w] - x[r]) / x[a]
                                                for x in anc]) for p in PARTS},
                  "unplaced_of_anchor": stat([(x[a] - x[w]) / x[a] for x in anc]),
                  "r_walk_over_anchor": stat([x[w] / x[a] for x in anc])}
    return out


def rule_s(sp, pred):
    band = pred["rules"]["E116-S"]["band"]
    ref = pred["reference_e88_card1"]["splits"]
    out = {}
    for f in DESIGN:
        rows, worst = [], "PASS"
        for p in PARTS:
            s = sp[f]["shares"][p]
            if s["mean"] is None or s["ci95"] is None:
                rows.append({"part": p, "verdict": "not scored"}); worst = "not scored"; continue
            d = s["mean"] - ref[f]["shares"][p]["mean"]
            v = "PASS" if abs(d) <= band[f] else ("FAIL" if abs(d) - s["ci95"] > band[f] else "INCONCLUSIVE")
            rows.append({"part": p, "share": s["mean"], "ci95": s["ci95"], "e88": ref[f]["shares"][p]["mean"], "diff": d,
                         "band": band[f], "verdict": v})
            worst = worst if worst == "not scored" else ("FAIL" if "FAIL" in (worst, v) else ("INCONCLUSIVE" if "INCONCLUSIVE" in (worst, v) else "PASS"))
        out[f] = {"verdict": worst, "parts": rows}
    return out


def rule_w(sp, pred):
    car = pred["carried_W"]
    out = {}
    for f in DESIGN:
        rows, worst = [], "PASS"
        for p in PARTS:
            s = sp[f]["D"][p]
            if s["mean"] is None or s["ci95"] is None:
                rows.append({"part": p, "verdict": "not scored"}); worst = "not scored"; continue
            c = car[f][p]
            b = max(0.6, 0.12 * abs(c))
            lo, hi = s["mean"] - s["ci95"], s["mean"] + s["ci95"]
            v = "PASS" if abs(s["mean"] - c) <= b else ("FAIL" if hi < c - b or lo > c + b else "INCONCLUSIVE")
            rows.append({"part": p, "W": s["mean"], "ci95": s["ci95"], "carried": c, "band": b, "ratio_to_e88": s["mean"] / (c / pred["card_scale_e82"]["value"][f]),
                         "verdict": v})
            worst = worst if worst == "not scored" else ("FAIL" if "FAIL" in (worst, v) else ("INCONCLUSIVE" if "INCONCLUSIVE" in (worst, v) else "PASS"))
        out[f] = {"verdict": worst, "parts": rows}
    return out


def rule_t(red, pred):
    pp = per_pass(red)
    rows, worst = [], "PASS"
    for k in ("fp32.randn", "fp16.randn", "int8.full"):
        s = stat([v.get(k) for v in pp.values()])
        ref = pred["tie_e78_aifoundry3"][k]["D"]
        b = max(0.4, 0.03 * ref)
        if s["mean"] is None or s["ci95"] is None:
            rows.append({"item": k, "verdict": "not scored"}); worst = "not scored"; continue
        lo, hi = s["mean"] - s["ci95"], s["mean"] + s["ci95"]
        v = "PASS" if abs(s["mean"] - ref) <= b else ("FAIL" if hi < ref - b or lo > ref + b else "INCONCLUSIVE")
        rows.append({"item": k, "D": s["mean"], "ci95": s["ci95"], "e78": ref, "band": b, "verdict": v})
        worst = worst if worst == "not scored" else ("FAIL" if "FAIL" in (worst, v) else ("INCONCLUSIVE" if "INCONCLUSIVE" in (worst, v) else "PASS"))
    return {"verdict": worst, "items": rows}


def rule_r0(path, expect):
    if not path or not os.path.exists(path):
        return {"verdict": "not scored", "why": "no read-back file"}
    recs = [json.loads(line) for line in open(path)]
    last = {}
    for r in recs:
        last[r["tile"]] = r
    rows = []
    for name, v in expect["tiles"].items():
        r = last.get(name)
        if r is None:
            rows.append({"tile": name, "read": False}); continue
        groups = r.get("groups") or {}
        row = {"tile": name, "read": True, "n": r["n"], "rc": r["rc"], "distinct_c": r.get("distinct_c"),
               "equal_accum": bool(r.get("equal_accum")), "c00_card": None, "c08_card": None, "c00_accum": v["c00"],
               "c08_accum": v["c08"], "does": v["does"], "sparsity_ok": (r.get("sparsity") or {}).get("ok"),
               "cycles_per_op": (r.get("sparsity") or {}).get("cycles_per_op"), "ghz": (r.get("sparsity") or {}).get("ghz")}
        if groups:
            big = max(groups.values(), key=lambda g: g["minions"])
            raw = bytes.fromhex(big["hex"])
            row["c00_card"] = raw[0:4][::-1].hex()
            row["c08_card"] = raw[32:36][::-1].hex()
            ref = bytes.fromhex(v["accum_hex"])
            row["words_differing_in_largest_group"] = sum(raw[i:i + 4] != ref[i:i + 4] for i in range(0, 1024, 4))
            row["minions_in_largest_group"] = big["minions"]
        if "e104_card1" in v:
            row["equal_card1_e104"] = row["equal_accum"] and v["e104_card1"]["rtl_hex_equal"]
        rows.append(row)
    n_read = sum(r["read"] for r in rows)
    n_eq = sum(r.get("equal_accum", False) for r in rows)
    if n_read < len(rows):
        verdict = "FAIL" if n_eq < n_read else "not scored"
    else:
        verdict = "PASS" if n_eq == len(rows) else "FAIL"
    return {"verdict": verdict, "reads": n_read, "equal": n_eq, "of": len(rows), "tiles": rows,
            "card1_cross": {"tiles": [r["tile"] for r in rows if "equal_card1_e104" in r],
                            "equal": sum(bool(r.get("equal_card1_e104")) for r in rows)}}


def score(red, pred, e88rules):
    kept = len(red["per_pass"])
    res = {"kept_passes": kept, "passes": sorted(red["per_pass"].keys()), "passes_set_aside": red.get("passes_set_aside")}
    sp = splits(red)
    res["splits"] = sp
    if kept < pred["rules"]["min_passes"]:
        res["note"] = f"{kept} kept passes < {pred['rules']['min_passes']}: S, W, H, P and T not scored (exploratory)"
        for k in ("E116-S", "E116-W", "E116-H", "E116-P", "E116-T"):
            res[k] = {"verdict": "not scored"}
        res["exploratory"] = {"E116-S": rule_s(sp, pred), "E116-W": rule_w(sp, pred), "E116-T": rule_t(red, pred)}
        return res
    res["E116-S"] = rule_s(sp, pred)
    res["E116-W"] = rule_w(sp, pred)
    res["E116-T"] = rule_t(red, pred)
    ref_v = pred["reference_e88_card1"]["verdicts"]
    if e88rules:
        have = {k: v["verdict"] for k, v in e88rules["primary"]["rules"].items()}
        diff = [k for k in H_RULES if have.get(k) != ref_v.get(k)]
        res["E116-H"] = {"verdict": "PASS" if not diff else ("INCONCLUSIVE" if len(diff) == 1 else "FAIL"),
                         "same": len(H_RULES) - len(diff), "of": len(H_RULES), "differ": {k: [ref_v.get(k), have.get(k)] for k in diff},
                         "verdicts": {k: have.get(k) for k in H_RULES}}
        prules = [k for k in ref_v if k.startswith("P-")]
        res["E116-P"] = {"reported": True, "pass": sum(have.get(k) == "PASS" for k in prules), "of": len(prules),
                         "verdicts": {k: [ref_v.get(k), have.get(k)] for k in prules},
                         "tally_e88rules": e88rules["primary"].get("tally")}
        res["contrasts"] = {k: {"a": v["a"], "b": v["b"], "D": v["D"]["mean"], "ci95": v["D"]["ci95"],
                                "e88": pred["reference_e88_card1"]["contrasts"].get(k, {}).get("D"),
                                "ratio_to_e88": (v["D"]["mean"] / pred["reference_e88_card1"]["contrasts"][k]["D"])
                                if pred["reference_e88_card1"]["contrasts"].get(k, {}).get("D") not in (None, 0) and v["D"]["mean"] is not None else None}
                            for k, v in e88rules["primary"]["contrasts"].items()}
    else:
        res["E116-H"] = res["E116-P"] = {"verdict": "not scored", "why": "no score_e88 output"}
    return res


def fmt(x, d=3):
    return "-" if x is None else f"{x:.{d}f}"


def write_md(out, path):
    L = ["# E116 results (score_e116.py; registered rules from predictions-e116.json)", ""]
    r0 = out["E116-R0"]
    L.append(f"**E116-R0 (read-back): {r0['verdict']}** — {r0.get('equal', 0)} of {r0.get('of', 22)} reads equal accum.c "
             f"on every word of all 1,024 minions; {r0.get('reads', 0)} reads ran. Card 1 (E104) cross-check: "
             f"{r0.get('card1_cross', {}).get('equal', 0)} of {len(r0.get('card1_cross', {}).get('tiles', []))} tiles the same words.")
    L += ["", "| tile | n | equal accum.c | distinct C | C[0][0] card / accum | C[0][8] card / accum | what it does |", "|---|---:|---|---:|---|---|---|"]
    for t in r0.get("tiles", []):
        L.append(f"| {t['tile']} | {t.get('n', '-')} | {t.get('equal_accum')} | {t.get('distinct_c')} | {t.get('c00_card')} / {t.get('c00_accum')} | "
                 f"{t.get('c08_card')} / {t.get('c08_accum')} | {t.get('does')} |")
    p = out["power"]
    L += ["", f"Kept passes: {p['kept_passes']} {p['passes']}; set aside: {p.get('passes_set_aside')}", ""]
    if "note" in p:
        L.append(p["note"])
    for f in DESIGN:
        sp = p["splits"][f]
        L.append(f"**{f}** total D(r_walk) {fmt(sp['total']['mean'])} ± {fmt(sp['total']['ci95'])} W")
        for q in PARTS:
            L.append(f"- {q}: {fmt(sp['D'][q]['mean'])} ± {fmt(sp['D'][q]['ci95'])} W, share {fmt(sp['shares'][q]['mean'])} ± {fmt(sp['shares'][q]['ci95'])}, "
                     f"of the anchor {fmt(sp['shares_of_anchor'][q]['mean'])} ± {fmt(sp['shares_of_anchor'][q]['ci95'])}")
        L.append(f"- unplaced of the anchor {fmt(sp['unplaced_of_anchor']['mean'])} ± {fmt(sp['unplaced_of_anchor']['ci95'])}")
    for k in ("E116-S", "E116-W"):
        L += ["", f"**{k}**"]
        for f, v in (p[k].items() if isinstance(p[k], dict) and "verdict" not in p[k] else []):
            L.append(f"- {f}: **{v['verdict']}** " + "; ".join(
                f"{r['part']} {fmt(r.get('share', r.get('W')))} vs {fmt(r.get('e88', r.get('carried')))} (band {fmt(r.get('band'))}) {r['verdict']}" for r in v["parts"]))
        if "verdict" in p[k]:
            L.append(f"- {p[k]['verdict']}")
    t = p["E116-T"]
    L += ["", f"**E116-T (session tie): {t.get('verdict')}** " + "; ".join(
        f"{r['item']} {fmt(r.get('D'))} ± {fmt(r.get('ci95'))} vs E78 {fmt(r.get('e78'))} {r['verdict']}" for r in t.get("items", []))]
    h = p["E116-H"]
    L += ["", f"**E116-H (E88's 13 mechanism rules): {h.get('verdict')}** — {h.get('same')} of {h.get('of')} the same; differ: {h.get('differ')}"]
    pr = p["E116-P"]
    L += ["", f"**E116-P (E88's 19 bands, reported):** {pr.get('pass')} of {pr.get('of')} PASS; tally of all 32: {pr.get('tally_e88rules')}"]
    for k, v in (pr.get("verdicts") or {}).items():
        L.append(f"- {k}: card 1 {v[0]}, aifoundry3 {v[1]}")
    if "contrasts" in p:
        L += ["", "| contrast | a − b | D (W) ±95% | E88 card 1 | ratio |", "|---|---|---|---|---|"]
        for k, v in p["contrasts"].items():
            L.append(f"| {k} | {v['a']} − {v['b']} | {fmt(v['D'])} ± {fmt(v['ci95'])} | {fmt(v['e88'])} | {fmt(v['ratio_to_e88'])} |")
    for name, a in out.get("arms", {}).items():
        L += ["", f"Arm {name}: kept {a['kept_passes']}; S " + ", ".join(f"{f} {a['E116-S'][f]['verdict']}" if 'verdict' not in a['E116-S'] else a['E116-S']['verdict'] for f in (DESIGN if 'verdict' not in a['E116-S'] else ['x'])) +
              "; W " + ", ".join(f"{f} {a['E116-W'][f]['verdict']}" if 'verdict' not in a['E116-W'] else a['E116-W']['verdict'] for f in (DESIGN if 'verdict' not in a['E116-W'] else ['x'])) +
              f"; T {a['E116-T'].get('verdict')}"]
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--red", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--e88rules")
    ap.add_argument("--readback")
    ap.add_argument("--json", required=True)
    ap.add_argument("--md")
    a = ap.parse_args()
    pred = json.load(open(os.path.join(HERE, "predictions-e116.json")))
    expect = json.load(open(os.path.join(HERE, "expect-e116.json")))
    red = json.load(open(a.red))
    e88rules = json.load(open(a.e88rules)) if a.e88rules and os.path.exists(a.e88rules) else None
    out = {"experiment": "E116", "E116-R0": rule_r0(a.readback, expect), "power": score(red, pred, e88rules), "arms": {}}
    for spec in a.arm:
        name, path = spec.split("=", 1)
        ar = json.load(open(path))
        out["arms"][name] = score(ar, pred, None)
        for k in ("splits",):
            out["arms"][name].pop(k, None)
    out["expected"] = pred["expected"]
    json.dump(out, open(a.json, "w"), indent=1)
    if a.md:
        write_md(out, a.md)
    print("R0", out["E116-R0"]["verdict"], "| S", {f: v["verdict"] for f, v in out["power"]["E116-S"].items()} if "verdict" not in out["power"]["E116-S"] else out["power"]["E116-S"]["verdict"],
          "| W", {f: v["verdict"] for f, v in out["power"]["E116-W"].items()} if "verdict" not in out["power"]["E116-W"] else out["power"]["E116-W"]["verdict"],
          "| H", out["power"]["E116-H"].get("verdict"), out["power"]["E116-H"].get("same"),
          "| P", out["power"]["E116-P"].get("pass"), "| T", out["power"]["E116-T"].get("verdict"), "| kept", out["power"]["kept_passes"])


if __name__ == "__main__":
    main()
