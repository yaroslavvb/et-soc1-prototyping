#!/usr/bin/env python3
"""E106's rules, on a reduction written by reduce_e106.py and the read-back written by readback_e106.py. Standard library only.

    python3 tools/claims-v3/kinds/score_e106.py --e106 <e106.json from reduce_e106> --readback <readback.jsonl> [--arm name=<json> ...] [--md results.md] [--json scored.json]

Every threshold and prediction comes from predictions-e106.json; every expected accumulator from e106/e106.json. A contrast's and a share's interval is t(0.975, n - 1) over per-pass values, paired within a pass. Fewer than 2 kept passes: every power rule NOT SCORED. The read-back rule needs no pass.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e106.json")
SPEC = os.path.join(HERE, "e106", "e106.json")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}
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
    rr = reg["rules"]["E106-R1"]
    by = {}
    for r in rows:
        by.setdefault(r["tile"], []).append(r)
    want = {t: reg_lens for t, reg_lens in rr["reads"].items()}
    off, unread = [], []
    for t, lens in want.items():
        rs = {r["n"]: r for r in by.get(t, [])}
        for n in lens:
            r = rs.get(n)
            if r is None or r.get("unread") or not r.get("all_minions_agree"):
                unread.append((t, n))
            elif set(r["matches"]) != set(READINGS):
                off.append({"tile": t, "n": n, "words_off": r["words_off"], "card_c00": r["card_c00"], "card_c08": r["card_c08"]})
    v = "FAIL" if off else "UNREAD" if unread else "PASS"
    return {"E106-R1": {"verdict": v, "reads": sum(len(x) for x in want.values()), "off": off[:8], "n_off": len(off), "unread": unread[:8], "n_unread": len(unread)}}, {t: sorted(set.intersection(*[set(r["matches"]) for r in rs])) if rs else None for t, rs in by.items()}


def pp(res, plus, minus):
    out = {}
    for p, it in sorted(res.get("per_pass", {}).items()):
        names = list(plus) + list(minus)
        if all(n in it and it[n].get("D") is not None for n in names):
            out[p] = sum(it[n]["D"] for n in plus) - sum(it[n]["D"] for n in minus)
    return out


def share(res, held, step):
    a, b = pp(res, *held), pp(res, *step)
    return {p: a[p] / b[p] for p in a if p in b and b[p] != 0}


def band(s, lo, hi):
    if s["ci95"] is None:
        return "UNRESOLVED"
    a, b = s["mean"] - s["ci95"], s["mean"] + s["ci95"]
    if lo <= a and b <= hi:
        return "ABOUT HALF"
    if a > hi:
        return "MOST"
    if b < lo:
        return "LITTLE"
    return "INCONCLUSIVE"


def score_power(res, reg):
    rules = reg["rules"]
    out = {"passes": res.get("passes", []), "set_aside": res.get("passes_set_aside"), "leak": res.get("leak"), "rules": {}, "contrasts": {}, "table": {}, "shares": {}}
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
    C = {}
    for name, c in reg["contrasts"].items():
        v = pp(res, c["plus"], c["minus"])
        C[name] = {**mci(v.values()), "per_pass": v, **{q: c.get(q) for q in ("M", "half95", "what")}}
    out["contrasts"] = C
    S = {}
    for name, c in reg["shares"].items():
        v = share(res, (reg["contrasts"][c["held"]]["plus"], reg["contrasts"][c["held"]]["minus"]), (reg["contrasts"][c["step"]]["plus"], reg["contrasts"][c["step"]]["minus"]))
        S[name] = {**mci(v.values()), "per_pass": v, **{q: c.get(q) for q in ("M", "what")}}
    out["shares"] = S
    R = out["rules"]
    # R2: the step on one card, against E92's carried values
    rr = rules["E106-R2"]
    cells = {}
    ok = True
    for t in ("fp32", "fp16"):
        c = C[f"{t}.step"]
        good = c["mean"] is not None and abs(c["mean"] - rr["carried_w"][t]) <= rr["band_w"]
        ok = ok and good
        cells[t] = {"mean_w": c["mean"], "ci95_w": c["ci95"], "carried_w": rr["carried_w"][t], "M_w": c["M"], "ok": good}
    R["E106-R2"] = {"verdict": "PASS" if ok else "FAIL", "cells": cells}
    # R3, R4, R5: the held share
    for rid, key in (("E106-R3", "fp32.s_abs"), ("E106-R4", "fp16.z_ss"), ("E106-R5", "fp16.x_s")):
        rr = rules[rid]
        s = S[key]
        R[rid] = {"verdict": band(s, rr["lo"], rr["hi"]), "share": s["mean"], "ci95": s["ci95"], "n": s["n"], "M": s["M"], "held_w": C[reg["shares"][key]["held"]]["mean"], "held_ci95_w": C[reg["shares"][key]["held"]]["ci95"], "band": [rr["lo"], rr["hi"]]}
    # R6: the two formats' shares, the design with independent eff_subs against fp32's held tile
    rr = rules["E106-R6"]
    a, b = S["fp16.z_ss"]["per_pass"], S["fp32.s_abs"]["per_pass"]
    d = mci([a[p] - b[p] for p in a if p in b])
    if d["ci95"] is None:
        v = "UNRESOLVED"
    else:
        lo, hi = d["mean"] - d["ci95"], d["mean"] + d["ci95"]
        v = "ALIKE" if -rr["band"] <= lo and hi <= rr["band"] else "DIFFER" if lo > rr["band"] or hi < -rr["band"] else "INCONCLUSIVE"
    R["E106-R6"] = {"verdict": v, "difference": d["mean"], "ci95": d["ci95"], "n": d["n"], "band": rr["band"]}
    # R7: the bench's model
    rr = rules["E106-R7"]
    rows = list(out["table"].values())
    if len(rows) >= 3:
        e = rms([x["D"] - x["M"] for x in rows])
        R["E106-R7"] = {"verdict": "PASS" if e <= rr["pass_w"] else "FAIL" if e > rr["fail_w"] else "INCONCLUSIVE", "rms_w": e, "n": len(rows), "bias_w": sum(x["M"] - x["D"] for x in rows) / len(rows), "worst": max((abs(k["D"] - k["M"]), n) for n, k in out["table"].items()), "inside_95": sum(x["lo95"] <= x["D"] <= x["hi95"] for x in rows)}
    else:
        R["E106-R7"] = {"verdict": "UNRESOLVED", "n": len(rows)}
    # S1: the session tie against E82, dips removed
    cells, ok = {}, True
    for c, v in reg["session_tie"]["cells"].items():
        it = items.get(c)
        dd = it["D"]["mean"] if it and it.get("D") else None
        good = dd is not None and abs(dd - v["ref_w"]) <= v["band_w"]
        ok = ok and good
        cells[c] = {"D": dd, "ref_w": v["ref_w"], "band_w": v["band_w"], "ok": good}
    R["E106-S1"] = {"verdict": "PASS" if ok else "FAIL", "cells": cells}
    return out


def write_md(prim, arms, rows, path):
    L = ["# E106 results", "", f"Passes kept: {prim.get('passes')}; set aside: {prim.get('set_aside')}; leak {prim.get('leak')}", "", "| rule | verdict | " + " | ".join(arms) + " | numbers |", "|---|---|" + "---|" * len(arms) + "---|"]
    for r, v in prim["rules"].items():
        nums = {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k not in ("verdict", "cells", "arm_sensitive", "off", "unread")}
        L.append(f"| {r} | **{v['verdict']}** | " + " | ".join(arms[a]["rules"].get(r, {}).get("verdict", "") for a in arms) + f" | {nums} |")
    L += ["", "## The read-back", "", "| tile | n | minions agreeing | off rtl | off manual | off frozen | equals | card C00 / C08 | words on the card |", "|---|---:|---:|---:|---:|---:|---|---|---:|"]
    for r in rows:
        if r.get("unread"):
            L.append(f"| `{r['tile']}` | {r['n']} | - | - | - | - | unread | | |")
            continue
        o = r["words_off"]
        L.append(f"| `{r['tile']}` | {r['n']} | {r['minions']} | {o['rtl']} | {o['manual']} | {o['fl']} | {', '.join(r['matches']) or 'none'} | {r['card_c00']} / {r['card_c08']} | {r['card_distinct_words']} |")
    L += ["", "## The contrasts, per pass, t intervals", "", "| contrast | measured, W | n | M4 [95%] |", "|---|---:|---:|---:|"]
    for k, c in prim.get("contrasts", {}).items():
        m = "unread" if c["mean"] is None else (f"{c['mean']:.3f}" + ("" if c["ci95"] is None else f" ± {c['ci95']:.3f}"))
        L.append(f"| `{k}` | {m} | {c['n']} | {c['M']:.2f} ± {c['half95']:.2f} |")
    L += ["", "## The shares of the step, per pass", "", "| held tile | share | n | M4 |", "|---|---:|---:|---:|"]
    for k, c in prim.get("shares", {}).items():
        m = "unread" if c["mean"] is None else (f"{c['mean']:.3f}" + ("" if c["ci95"] is None else f" ± {c['ci95']:.3f}"))
        L.append(f"| `{k}` | {m} | {c['n']} | {c['M']:.3f} |")
    L += ["", "## The tiles", "", "| tile | group | D, W (95%) | M4 [95%] | D - M4 |", "|---|---|---:|---:|---:|"]
    for k, r in sorted(prim.get("table", {}).items()):
        L.append(f"| `{k}` | {r['group']} | {r['D']:.2f} ± {r['ci95'] or 0:.2f} | {r['M']:.2f} [{r['lo95']:.2f}, {r['hi95']:.2f}] | {r['D'] - r['M']:+.2f} |")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e106", required=True)
    ap.add_argument("--readback", default=None)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    spec = json.load(open(SPEC))
    rows = read_rows(a.readback, spec)
    read_rules, read_tiles = score_read(rows, reg)
    prim = score_power(json.load(open(a.e106)), reg)
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
        write_md(prim, arms, rows, a.md)
    print(json.dumps({r: {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k not in ("cells", "off", "unread")} for r, v in prim["rules"].items()}, indent=0))
    print(prim.get("tally"))


if __name__ == "__main__":
    main()
