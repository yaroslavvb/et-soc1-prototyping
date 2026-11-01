#!/usr/bin/env python3
"""E108's rules, on a reduction written by reduce_e108.py and the read-back written by readback_e108.py. Standard library only. A port of
tools/claims-v3/kinds/score_e106.py with E108's contrasts, ratios and rules.

    python3 tools/claims-v3/signloc/score_e108.py --e108 <e108.json from reduce_e108> --readback <readback.jsonl> [--arm name=<json> ...] [--md results.md] [--json scored.json]

Every threshold and prediction comes from predictions-e108.json; every expected accumulator from e108/e108.json. A contrast's, a ratio's and a difference's
interval is t(0.975, n - 1) over per-pass values, paired within a pass. Fewer than 2 kept passes: every power rule NOT SCORED. The read-back rule needs no pass.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e108.json")
SPEC = os.path.join(HERE, "e108", "e108.json")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447}
READINGS = ("rtl", "manual", "fl")


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def t975(df):
    return T975.get(df, 1.96 + 2.4 / max(df, 1))


def mci(v):
    v = list(v)
    if len(v) < 2:
        return {"mean": (v[0] if v else None), "ci95": None, "n": len(v)}
    return {"mean": sum(v) / len(v), "ci95": t975(len(v) - 1) * statistics.stdev(v) / math.sqrt(len(v)), "n": len(v)}


def lohi(s):
    return (None, None) if s["ci95"] is None or s["mean"] is None else (s["mean"] - s["ci95"], s["mean"] + s["ci95"])


def read_rows(path, spec):
    rows = []
    if not path or not os.path.exists(path):
        return rows
    seen = {}
    for line in open(path):
        r = json.loads(line)
        seen[(r["tile"], r["n"])] = r
    w = lambda b: [int.from_bytes(b[i:i + 4], "little") for i in range(0, 1024, 4)]
    for (tile, n), r in sorted(seen.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        e = spec["tiles"][tile]["read"][str(n)]
        groups = r.get("groups") or {}
        row = {"tile": tile, "n": n, "ok": bool(r.get("sparsity", {}).get("ok")), "cpo": r.get("sparsity", {}).get("cycles_per_op"), "iters": r.get("sparsity", {}).get("iters"), "distinct_c": r.get("distinct_c")}
        if not groups:
            row.update(matches=[], minions=0, unread=True)
            rows.append(row)
            continue
        big = max(groups.values(), key=lambda g: g["minions"])
        cw = w(bytes.fromhex(big["hex"]))
        row["minions"] = big["minions"]
        row["all_minions_agree"] = len(groups) == 1 and big["minions"] == 1024
        row["words_off"] = {q: sum(x != y for x, y in zip(cw, w(bytes.fromhex(e[q + "_hex"])))) for q in READINGS}
        row["matches"] = [q for q in READINGS if row["words_off"][q] == 0]
        row["card_c00"], row["card_c08"] = f"{cw[0]:08x}", f"{cw[8]:08x}"
        row["card_distinct_words"] = len(set(cw))
        row["c00"], row["c08"] = e["c00"], e["c08"]
        rows.append(row)
    return rows


def score_read(rows, reg):
    rr = reg["rules"]["E108-R1"]
    by = {}
    for r in rows:
        by.setdefault(r["tile"], []).append(r)
    off, unread = [], []
    for t, lens in rr["reads"].items():
        rs = {r["n"]: r for r in by.get(t, [])}
        for n in lens:
            r = rs.get(n)
            if r is None or r.get("unread") or not r.get("all_minions_agree"):
                unread.append((t, n))
            elif set(r["matches"]) != set(READINGS):
                off.append({"tile": t, "n": n, "words_off": r["words_off"], "card_c00": r["card_c00"], "card_c08": r["card_c08"]})
    v = "FAIL" if off else "UNREAD" if unread else "PASS"
    return ({"E108-R1": {"verdict": v, "reads": sum(len(x) for x in rr["reads"].values()), "off": off[:8], "n_off": len(off), "unread": unread[:8], "n_unread": len(unread)}},
            {t: sorted(set.intersection(*[set(r["matches"]) for r in rs])) if rs else None for t, rs in by.items()})


def pp(res, plus, minus):
    out = {}
    for p, it in sorted(res.get("per_pass", {}).items()):
        names = list(plus) + list(minus)
        if all(n in it and it[n].get("D") is not None for n in names):
            out[p] = sum(it[n]["D"] for n in plus) - sum(it[n]["D"] for n in minus)
    return out


def per_pass(res, reg, name):
    """A registered quantity, per pass: a contrast (plus, minus), a ratio of two contrasts, or a difference of two of those."""
    q = reg["quantities"][name]
    if q["form"] == "contrast":
        return pp(res, q["plus"], q["minus"])
    a, b = per_pass(res, reg, q["a"]), per_pass(res, reg, q["b"])
    if q["form"] == "ratio":
        return {p: a[p] / b[p] for p in a if p in b and b[p] != 0}
    if q["form"] == "diff":
        k = q.get("k", 1.0)
        return {p: a[p] - k * b[p] for p in a if p in b}
    raise ValueError(q["form"])


def verdict(rule, s):
    lo, hi = lohi(s)
    if lo is None:
        return "UNRESOLVED"
    f = rule["form"]
    if f == "bands":          # E106's share bands
        if rule["lo"] <= lo and hi <= rule["hi"]:
            return rule["names"]["inside"]
        if lo > rule["hi"]:
            return rule["names"]["above"]
        if hi < rule["lo"]:
            return rule["names"]["below"]
        return "INCONCLUSIVE"
    if f == "sign_then_band":  # a resolved sign first, then equivalence inside +-band
        if lo > 0:
            return rule["names"]["above"]
        if hi < 0:
            return rule["names"]["below"]
        if -rule["band"] <= lo and hi <= rule["band"]:
            return rule["names"]["inside"]
        return "INCONCLUSIVE"
    if f == "band_then_sign":  # equivalence inside +-band first, then a resolved sign
        if -rule["band"] <= lo and hi <= rule["band"]:
            return rule["names"]["inside"]
        if lo > 0:
            return rule["names"]["above"]
        if hi < 0:
            return rule["names"]["below"]
        return "INCONCLUSIVE"
    if f == "ratio_e104":      # E104-R5/R6's: HOLDS if the interval holds 1.552 and lies above 1.2; GOES if it lies below 1.552
        if lo <= rule["ratio"] <= hi and lo > rule["equal_above"]:
            return "1.55x HOLDS"
        if hi < rule["ratio"]:
            return "1.55x GOES"
        return "INCONCLUSIVE"
    raise ValueError(f)


def score_power(res, reg):
    rules = reg["rules"]
    out = {"passes": res.get("passes", []), "set_aside": res.get("passes_set_aside"), "leak": res.get("leak"), "rules": {}, "quantities": {}, "table": {}}
    power_rules = [r for r in rules if rules[r].get("kind") == "power"]
    if len(out["passes"]) < reg["plan"]["min_kept_passes_scored"]:
        for r in power_rules:
            out["rules"][r] = {"verdict": "NOT SCORED"}
        return out
    items = res["items"]
    for k, t in reg["tiles"].items():
        it = items.get(k)
        d = it.get("D") if it else None
        if d and d.get("mean") is not None and (d.get("n") or 0) >= reg["plan"]["min_tile_passes"]:
            out["table"][k] = {"D": d["mean"], "ci95": d.get("ci95"), "n": d.get("n"), **{q: t["pred"][q] for q in ("M", "lo95", "hi95")}, "group": t["group"]}
    Q = {}
    for name, q in reg["quantities"].items():
        v = per_pass(res, reg, name)
        Q[name] = {**mci(v.values()), "per_pass": v, "M": q.get("M"), "half95": q.get("half95"), "what": q.get("what"), "form": q["form"]}
    out["quantities"] = Q
    R = out["rules"]
    for rid, rule in rules.items():
        if rule.get("kind") != "power" or rule["form"] in ("step_band", "rms", "tie"):
            continue
        legs = rule["legs"]
        vs = {leg: verdict(rule, Q[leg]) for leg in legs}
        R[rid] = {"verdict": vs[legs[0]] if len(legs) == 1 else " / ".join(vs[x] for x in legs), "legs": {leg: {"verdict": vs[leg], "mean": Q[leg]["mean"], "ci95": Q[leg]["ci95"], "n": Q[leg]["n"], "M": Q[leg]["M"]} for leg in legs}}
    # R2: the step against E106's, one card, another session
    rr = rules["E108-R2"]
    cells, ok = {}, True
    for t, leg in (("fp32", "fp32.step"), ("fp16", "fp16.step")):
        c = Q[leg]
        good = c["mean"] is not None and abs(c["mean"] - rr["e106_w"][t]) <= rr["band_w"]
        ok = ok and good
        cells[t] = {"mean_w": c["mean"], "ci95_w": c["ci95"], "e106_w": rr["e106_w"][t], "M_w": c["M"], "ok": good}
    R["E108-R2"] = {"verdict": "PASS" if ok else "FAIL", "cells": cells}
    # R11: the bench's model
    rr = rules["E108-R11"]
    rows = list(out["table"].values())
    if len(rows) >= 3:
        e = rms([x["D"] - x["M"] for x in rows])
        R["E108-R11"] = {"verdict": "PASS" if e <= rr["pass_w"] else "FAIL" if e > rr["fail_w"] else "INCONCLUSIVE", "rms_w": e, "n": len(rows), "bias_w": sum(x["M"] - x["D"] for x in rows) / len(rows),
                         "worst": max((abs(k["D"] - k["M"]), n) for n, k in out["table"].items()), "inside_95": sum(x["lo95"] <= x["D"] <= x["hi95"] for x in rows)}
    else:
        R["E108-R11"] = {"verdict": "UNRESOLVED", "n": len(rows)}
    # S1: the session tie against E82, dips removed
    cells, ok = {}, True
    for c, v in reg["session_tie"]["cells"].items():
        it = items.get(c)
        dd = it["D"]["mean"] if it and it.get("D") else None
        good = dd is not None and abs(dd - v["ref_w"]) <= v["band_w"]
        ok = ok and good
        cells[c] = {"D": dd, "ref_w": v["ref_w"], "band_w": v["band_w"], "ok": good}
    R["E108-S1"] = {"verdict": "PASS" if ok else "FAIL", "cells": cells}
    return out


def fmt(c, d=3):
    if c["mean"] is None:
        return "unread"
    return f"{c['mean']:.{d}f}" + ("" if c["ci95"] is None else f" ± {c['ci95']:.{d}f}")


def write_md(prim, arms, rows, reg, path):
    L = ["# E108 results", "", f"Passes kept: {prim.get('passes')}; set aside: {prim.get('set_aside')}; leak {prim.get('leak')}", "",
         "| rule | verdict | " + " | ".join(arms) + " | numbers |", "|---|---|" + "---|" * len(arms) + "---|"]
    for r, v in prim["rules"].items():
        nums = {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k not in ("verdict", "cells", "arm_sensitive", "off", "unread", "legs")}
        if "legs" in v:
            nums = {leg: (None if x["mean"] is None else f"{x['mean']:.3f} ± {x['ci95'] if x['ci95'] is None else round(x['ci95'], 3)} (M4 {x['M'] if x['M'] is None else round(x['M'], 3)})") for leg, x in v["legs"].items()}
        L.append(f"| {r} | **{v['verdict']}** | " + " | ".join(arms[a]["rules"].get(r, {}).get("verdict", "") for a in arms) + f" | {nums} |")
    L += ["", "## The read-back", "", "| tile | n | minions agreeing | off rtl | off manual | off frozen | equals | card C00 / C08 | words on the card |", "|---|---:|---:|---:|---:|---:|---|---|---:|"]
    for r in rows:
        if r.get("unread"):
            L.append(f"| `{r['tile']}` | {r['n']} | - | - | - | - | unread | | |")
            continue
        o = r["words_off"]
        L.append(f"| `{r['tile']}` | {r['n']} | {r['minions']} | {o['rtl']} | {o['manual']} | {o['fl']} | {', '.join(r['matches']) or 'none'} | {r['card_c00']} / {r['card_c08']} | {r['card_distinct_words']} |")
    L += ["", "## Every registered quantity, per pass, t intervals", "", "| quantity | form | measured | n | M4 | what |", "|---|---|---:|---:|---:|---|"]
    for k, c in prim.get("quantities", {}).items():
        m4 = "" if c["M"] is None else (f"{c['M']:.3f}" + ("" if c.get("half95") is None else f" ± {c['half95']:.2f}"))
        L.append(f"| `{k}` | {c['form']} | {fmt(c)} | {c['n']} | {m4} | {c['what']} |")
    L += ["", "## The tiles", "", "| tile | group | D, W (95%) | M4 [95%] | D - M4 |", "|---|---|---:|---:|---:|"]
    for k, r in sorted(prim.get("table", {}).items()):
        L.append(f"| `{k}` | {r['group']} | {r['D']:.2f} ± {r['ci95'] or 0:.2f} | {r['M']:.2f} [{r['lo95']:.2f}, {r['hi95']:.2f}] | {r['D'] - r['M']:+.2f} |")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e108", required=True)
    ap.add_argument("--readback", default=None)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    spec = json.load(open(SPEC))
    rows = read_rows(a.readback, spec)
    read_rules, read_tiles = score_read(rows, reg)
    prim = score_power(json.load(open(a.e108)), reg)
    prim["rules"] = {**read_rules, **prim["rules"]}
    arms = {}
    for x in a.arm:
        n, p = x.split("=", 1)
        arms[n] = score_power(json.load(open(p)), reg)
    for r in prim["rules"]:
        v = prim["rules"][r]["verdict"]
        moved = {n: arms[n]["rules"].get(r, {}).get("verdict") for n in arms if r in arms[n]["rules"] and arms[n]["rules"][r].get("verdict") != v}
        if moved:
            prim["rules"][r]["arm_sensitive"] = moved
    t = {}
    for v in prim["rules"].values():
        t[v["verdict"]] = t.get(v["verdict"], 0) + 1
    prim["tally"] = t
    res = {"primary": prim, "arms": arms, "readback": {"rows": rows, "tiles": read_tiles}}
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1)
    if a.md:
        write_md(prim, arms, rows, reg, a.md)
    print(json.dumps({r: {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k not in ("cells", "off", "unread")} for r, v in prim["rules"].items()}, indent=0, default=str))
    print(prim.get("tally"))


if __name__ == "__main__":
    main()
