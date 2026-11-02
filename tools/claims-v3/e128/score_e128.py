#!/usr/bin/env python3
"""E128's rules, on a reduction written by reduce_e128.py and the read-back written by readback_e128.py. Standard library only. A port of
tools/claims-v3/signloc/score_e108.py with E128's contrasts, ratios and rules, E122's cross-card rule form and a pooled ratio.

    python3 tools/claims-v3/e128/score_e128.py --e128 <e128.json from reduce_e128> --readback <readback.jsonl> [--arm name=<json> ...] [--md results.md] [--json scored.json]

Every threshold and prediction comes from predictions-e128.json; every expected accumulator from e128/e128.json; every earlier session's value from the
committed scored.json files predictions-e128.json froze (E108 on this card, E122 on aifoundry3). A contrast's, a ratio's and a difference's interval is
t(0.975, n - 1) over per-pass values, paired within a pass. Fewer than 2 kept passes: every power, cross and pooled rule NOT SCORED. The read-back rule
needs no pass.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e128.json")
SPEC = os.path.join(HERE, "e128", "e128.json")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145}
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
    rr = reg["rules"]["E128-R1"]
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
    return ({"E128-R1": {"verdict": v, "reads": sum(len(x) for x in rr["reads"].values()), "off": off[:8], "n_off": len(off), "unread": unread[:8], "n_unread": len(unread)}},
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
    if f == "bands":
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


def x_verdict(q, x):
    """E122's cross-card form: d = Q128 - s Qref, h = sqrt(h128^2 + (s href)^2); PASS if |d| + h <= w, FAIL if |d| - h > w, else INCONCLUSIVE."""
    if q is None or q.get("mean") is None or q.get("ci95") is None:
        return "UNRESOLVED", None, None
    s = x["scale"]
    d = q["mean"] - s * x["ref"]["mean"]
    h = math.sqrt(q["ci95"] ** 2 + (s * x["ref"]["ci95"]) ** 2)
    w = x["w"]
    return ("PASS" if abs(d) + h <= w else "FAIL" if abs(d) - h > w else "INCONCLUSIVE"), d, h


def score_power(res, reg):
    rules = reg["rules"]
    out = {"passes": res.get("passes", []), "set_aside": res.get("passes_set_aside"), "leak": res.get("leak"), "rules": {}, "quantities": {}, "table": {}}
    kinds = ("power", "cross", "pooled")
    if len(out["passes"]) < reg["plan"]["min_kept_passes_scored"]:
        for r in rules:
            if rules[r].get("kind") in kinds:
                out["rules"][r] = {"verdict": "NOT SCORED"}
        return out
    items = res["items"]
    for k, t in reg["tiles"].items():
        it = items.get(k)
        d = it.get("D") if it else None
        if d and d.get("mean") is not None and (d.get("n") or 0) >= reg["plan"]["min_tile_passes"]:
            out["table"][k] = {"D": d["mean"], "ci95": d.get("ci95"), "n": d.get("n"), **{q: t["pred"][q] for q in ("M", "lo95", "hi95")}, "group": t["group"], "how": t.get("how")}
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
        R[rid] = {"verdict": vs[legs[0]] if len(legs) == 1 else " / ".join(vs[x] for x in legs),
                  "legs": {leg: {"verdict": vs[leg], "mean": Q[leg]["mean"], "ci95": Q[leg]["ci95"], "n": Q[leg]["n"], "M": Q[leg]["M"]} for leg in legs}}
    # R2: the step against E108's, this card, a third session
    rr = rules["E128-R2"]
    cells, ok = {}, True
    for t, leg in (("fp32", "fp32.step"), ("fp16", "fp16.step")):
        c = Q[leg]
        good = c["mean"] is not None and abs(c["mean"] - rr["e108_w"][t]) <= rr["band_w"]
        ok = ok and good
        cells[t] = {"mean_w": c["mean"], "ci95_w": c["ci95"], "e108_w": rr["e108_w"][t], "M_w": c["M"], "ok": good}
    R["E128-R2"] = {"verdict": "PASS" if ok else "FAIL", "cells": cells}
    # R11: the bench's model, every tile; the six new ones reported beside
    rr = rules["E128-R11"]
    rows = list(out["table"].values())
    new = [x for x in rows if x.get("how") == "new"]
    if len(rows) >= 3:
        e = rms([x["D"] - x["M"] for x in rows])
        R["E128-R11"] = {"verdict": "PASS" if e <= rr["pass_w"] else "FAIL" if e > rr["fail_w"] else "INCONCLUSIVE", "rms_w": e, "n": len(rows), "bias_w": sum(x["M"] - x["D"] for x in rows) / len(rows),
                         "worst": max((abs(k["D"] - k["M"]), n) for n, k in out["table"].items()), "inside_95": sum(x["lo95"] <= x["D"] <= x["hi95"] for x in rows),
                         "new_rms_w": rms([x["D"] - x["M"] for x in new]) if new else None, "new_n": len(new), "new_bias_w": (sum(x["M"] - x["D"] for x in new) / len(new)) if new else None,
                         "new_inside_95": sum(x["lo95"] <= x["D"] <= x["hi95"] for x in new)}
    else:
        R["E128-R11"] = {"verdict": "UNRESOLVED", "n": len(rows)}
    # S1: the session tie against E82, dips removed
    cells, ok = {}, True
    for c, v in reg["session_tie"]["cells"].items():
        it = items.get(c)
        dd = it["D"]["mean"] if it and it.get("D") else None
        good = dd is not None and abs(dd - v["ref_w"]) <= v["band_w"]
        ok = ok and good
        cells[c] = {"D": dd, "ref_w": v["ref_w"], "band_w": v["band_w"], "ok": good}
    R["E128-S1"] = {"verdict": "PASS" if ok else "FAIL", "cells": cells}
    # X: against E108 (this card) and E122 (aifoundry3), E122's form
    xs, tx = {}, {}
    for x in reg["cross_session"]["rules"]:
        q = Q.get(x["of"])
        v, d, h = x_verdict(q, x)
        xs[x["id"]] = {"verdict": v, "q128": None if q is None else q.get("mean"), "q128_ci95": None if q is None else q.get("ci95"), "ref": x["ref"]["mean"], "ref_ci95": x["ref"]["ci95"],
                       "scale": x["scale"], "predicted": x["scale"] * x["ref"]["mean"], "difference": d, "h": h, "w": x["w"], "unit": x["unit"], "against": x["against"]}
        tx[v] = tx.get(v, 0) + 1
    n_x = len(reg["cross_session"]["rules"])
    agg = "PASS" if tx.get("FAIL", 0) == 0 and tx.get("PASS", 0) >= n_x // 2 else "FAIL" if tx.get("FAIL", 0) >= 3 else "INCONCLUSIVE"
    R["E128-X"] = {"verdict": agg, "tally": tx, "rules": xs}
    # P: the moving-sum ratio pooled over the three sessions' kept passes
    pr = reg["pooled"]
    mine = Q[pr["of"]]["per_pass"]
    vals = list(pr["ref_per_pass"]["E108"].values()) + list(pr["ref_per_pass"]["E122"].values()) + list(mine.values())
    s = mci(vals)
    sess = []
    for nm, pv in (("E108", list(pr["ref_per_pass"]["E108"].values())), ("E122", list(pr["ref_per_pass"]["E122"].values())), ("E128", list(mine.values()))):
        c = mci(pv)
        if c["ci95"]:
            sess.append((nm, c["mean"], c["ci95"] / t975(c["n"] - 1)))
    wsum = sum(1 / se ** 2 for _, _, se in sess)
    ivw = {"mean": sum(m / se ** 2 for _, m, se in sess) / wsum, "ci95": 1.96 / math.sqrt(wsum), "n": len(sess)} if sess else {"mean": None, "ci95": None, "n": 0}
    R["E128-P"] = {"verdict": verdict(rules["E128-P"], s), "mean": s["mean"], "ci95": s["ci95"], "n": s["n"],
                   "sessions": {nm: {"mean": m, "se": se} for nm, m, se in sess},
                   "ivw_arm": {**ivw, "verdict": verdict(rules["E128-P"], ivw)}}
    return out


def fmt(c, d=3):
    if c["mean"] is None:
        return "unread"
    return f"{c['mean']:.{d}f}" + ("" if c["ci95"] is None else f" ± {c['ci95']:.{d}f}")


def write_md(prim, arms, rows, reg, path):
    L = ["# E128 results", "", f"Passes kept: {prim.get('passes')}; set aside: {prim.get('set_aside')}; leak {prim.get('leak')}", "",
         "| rule | verdict | " + " | ".join(arms) + " | numbers |", "|---|---|" + "---|" * len(arms) + "---|"]
    for r, v in prim["rules"].items():
        nums = {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k not in ("verdict", "cells", "arm_sensitive", "off", "unread", "legs", "rules", "sessions", "ivw_arm")}
        if "legs" in v:
            nums = {leg: (None if x["mean"] is None else f"{x['mean']:.3f} ± {x['ci95'] if x['ci95'] is None else round(x['ci95'], 3)} (M4 {x['M'] if x['M'] is None else round(x['M'], 3)})") for leg, x in v["legs"].items()}
        L.append(f"| {r} | **{v['verdict']}** | " + " | ".join(arms[a]["rules"].get(r, {}).get("verdict", "") for a in arms) + f" | {nums} |")
    x = prim["rules"].get("E128-X", {}).get("rules")
    if x:
        L += ["", "## The cross-session rules (E122's form)", "", "| X rule | against | E128 | ref × s | difference | ± h | w | verdict | " + " | ".join(arms) + " |",
              "|---|---|---|---|---|---|---|---|" + "---|" * len(arms)]
        for xid, v in x.items():
            q = "—" if v["q128"] is None else (f"{v['q128']:.3f}" + ("" if v["q128_ci95"] is None else f" ± {v['q128_ci95']:.3f}"))
            L.append(f"| {xid} | {v['against']} | {q} | {v['ref']:.3f} × {v['scale']:.4f} = {v['predicted']:.3f} | {'—' if v['difference'] is None else '%+.3f' % v['difference']} | "
                     f"{'—' if v['h'] is None else '%.3f' % v['h']} | {v['w']} | **{v['verdict']}** | " +
                     " | ".join(arms[a]["rules"].get("E128-X", {}).get("rules", {}).get(xid, {}).get("verdict", "") for a in arms) + " |")
    p = prim["rules"].get("E128-P")
    if p and "sessions" in p:
        L += ["", f"## The pooled moving-sum ratio: **{p['verdict']}**, {fmt(p)} over {p['n']} passes; inverse-variance arm {fmt(p['ivw_arm'])} ({p['ivw_arm']['verdict']})", "",
              "| session | mean | se |", "|---|---:|---:|"] + [f"| {nm} | {s['mean']:.3f} | {s['se']:.3f} |" for nm, s in p["sessions"].items()]
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
    ap.add_argument("--e128", required=True)
    ap.add_argument("--readback", default=None)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    spec = json.load(open(SPEC))
    rows = read_rows(a.readback, spec)
    read_rules, read_tiles = score_read(rows, reg)
    prim = score_power(json.load(open(a.e128)), reg)
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
    res = {"experiment": "E128", "primary": prim, "arms": arms, "readback": {"rows": rows, "tiles": read_tiles}}
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1)
    if a.md:
        write_md(prim, arms, rows, reg, a.md)
    print(json.dumps({r: {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k not in ("cells", "off", "unread", "rules", "legs")} for r, v in prim["rules"].items()}, indent=0, default=str))
    print(prim.get("tally"))


if __name__ == "__main__":
    main()
