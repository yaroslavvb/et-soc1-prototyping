#!/usr/bin/env python3
"""E104's rules, on a reduction written by reduce_e104.py and the read-back written by readback_e104.py. Standard library only.

    python3 tools/claims-v3/kinds/score_e104.py --e104 <e104.json from reduce_e104> --readback <readback.jsonl> [--arm name=<json> ...] [--md results.md] [--json scored.json]

Every threshold and prediction comes from predictions-e104.json; every expected accumulator from e104/e104.json (accum.c's real sums, make_e88's fl(n S)). A contrast's interval is t(0.975, n - 1) over its per-pass
values, as E92's. Fewer than 2 kept passes: every power rule NOT SCORED. The read-back rules need no pass.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e104.json")
SPEC = os.path.join(HERE, "e104", "e104.json")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def t975(df):
    return T975.get(df, 1.96 + 2.4 / max(df, 1))


READINGS = ("rtl", "manual", "fl")


def read_rows(path, spec):
    """One row per read: the words the card's minions hold against each reading. A read of the last attempt at a (tile, n) stands."""
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


def tile_readings(rows):
    """The readings every read of one tile equals, on every word and every minion. None if a read is missing or a minion disagrees."""
    if not rows or any(r.get("unread") or not r.get("all_minions_agree") for r in rows):
        return None
    out = set(READINGS)
    for r in rows:
        out &= set(r["matches"])
    return sorted(out)


def over_tiles(names, by):
    """(verdict, per-tile readings): RTL / MANUAL / FROZEN if exactly that reading is left over all the tiles, NONE if no reading is, UNREAD if a read is missing, TIED if more than one is left."""
    per = {t: tile_readings(by.get(t, [])) for t in names}
    if any(v is None for v in per.values()):
        return "UNREAD", per
    left = set(READINGS)
    for v in per.values():
        left &= set(v)
    if not left:
        return "NONE", per
    if len(left) > 1:
        return "TIED", per
    return {"rtl": "RTL", "manual": "MANUAL", "fl": "FROZEN"}[left.pop()], per


def first_miss(names, by, reading):
    for t in names:
        for r in by.get(t, []):
            if r.get("unread") or reading not in r["matches"]:
                return {"tile": t, "n": r["n"], "words_off": r.get("words_off"), "card_c00": r.get("card_c00"), "card_c08": r.get("card_c08"), reading: {"c00": r.get("c00", {}).get(reading), "c08": r.get("c08", {}).get(reading)}}
    return None


def contrast(res, plus, minus, want_ok=True):
    """Per-pass values of sum(plus) - sum(minus), their mean and t interval."""
    pp = res.get("per_pass", {})
    vals = {}
    for p, it in sorted(pp.items()):
        names = list(plus) + list(minus)
        if all(n in it and it[n].get("D") is not None for n in names):
            vals[p] = sum(it[n]["D"] for n in plus) - sum(it[n]["D"] for n in minus)
    v = list(vals.values())
    if len(v) < 2:
        return {"mean": None, "ci95": None, "n": len(v), "per_pass": vals}
    m = sum(v) / len(v)
    return {"mean": m, "ci95": t975(len(v) - 1) * statistics.stdev(v) / math.sqrt(len(v)), "n": len(v), "per_pass": vals}


def ratio(a, b):
    """Per-pass ratio of two contrasts: mean, t interval."""
    v = [a["per_pass"][p] / b["per_pass"][p] for p in a["per_pass"] if p in b["per_pass"] and b["per_pass"][p] != 0]
    if len(v) < 2:
        return {"mean": None, "ci95": None, "n": len(v)}
    m = sum(v) / len(v)
    return {"mean": m, "ci95": t975(len(v) - 1) * statistics.stdev(v) / math.sqrt(len(v)), "n": len(v), "of_means": a["mean"] / b["mean"] if b["mean"] else None}


def score_power(res, reg):
    rules = reg["rules"]
    out = {"passes": res.get("passes", []), "set_aside": res.get("passes_set_aside"), "leak": res.get("leak"), "rules": {}, "contrasts": {}, "table": {}}
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
        C[name] = contrast(res, c["plus"], c["minus"])
        C[name].update({q: c.get(q) for q in ("M", "half95", "frozen_reading_w", "what")})
    out["contrasts"] = C
    R = out["rules"]

    # R4: where h_sub's premium goes on fp16: the two halves' swing on the result path
    d = C["fp16.h_sub - u_sub"]
    rr = rules["E104-R4"]
    if d["mean"] is None:
        R["E104-R4"] = {"verdict": "UNRESOLVED", **d}
    else:
        lo, hi = d["mean"] - d["ci95"], d["mean"] + d["ci95"]
        v = "FROZEN-READING" if (-rr["frozen_band_w"] <= lo and hi <= rr["frozen_band_w"]) else "RESULT-PATH" if lo > rr["frozen_band_w"] else "INCONCLUSIVE"
        c32 = C["fp32.h_sub - u_sub"]
        R["E104-R4"] = {"verdict": v, "mean_w": d["mean"], "ci95_w": d["ci95"], "M_w": d["M"], "n": d["n"], "control_fp32_w": c32["mean"], "control_fp32_ci95": c32["ci95"], "control_M_w": c32["M"]}

    # R5: 1.55x, the halves together
    a, b = C["fp16.u_premium"], C["fp32.u_premium"]
    rr = rules["E104-R5"]
    q = ratio(a, b) if a["mean"] is not None and b["mean"] is not None else {"mean": None}
    if q["mean"] is None:
        R["E104-R5"] = {"verdict": "UNRESOLVED"}
    else:
        lo, hi = q["mean"] - q["ci95"], q["mean"] + q["ci95"]
        R["E104-R5"] = {"verdict": "1.55x HOLDS" if lo <= rr["e92_ratio"] <= hi and lo > rr["equal_above"] else "1.55x GOES" if hi < rr["e92_ratio"] else "INCONCLUSIVE", "ratio": q["mean"], "ci95": q["ci95"], "of_means": q.get("of_means"), "fp16_w": a["mean"], "fp16_ci95": a["ci95"], "fp32_w": b["mean"], "fp32_ci95": b["ci95"], "n": q["n"]}

    # R6: 1.55x, moving regime: the missing pair
    a, b = C["fp16.m_premium"], C["fp32.m_premium"]
    rr = rules["E104-R6"]
    q = ratio(a, b) if a["mean"] is not None and b["mean"] is not None else {"mean": None}
    if q["mean"] is None:
        R["E104-R6"] = {"verdict": "UNRESOLVED"}
    else:
        lo, hi = q["mean"] - q["ci95"], q["mean"] + q["ci95"]
        R["E104-R6"] = {"verdict": "1.55x HOLDS" if lo <= rr["e92_ratio"] <= hi and lo > rr["equal_above"] else "1.55x GOES" if hi < rr["e92_ratio"] else "INCONCLUSIVE", "ratio": q["mean"], "ci95": q["ci95"], "of_means": q.get("of_means"), "fp16_w": a["mean"], "fp16_ci95": a["ci95"], "fp32_w": b["mean"], "fp32_ci95": b["ci95"], "n": q["n"]}

    # R7: the bench's model on E104's float tiles
    rows = [v for v in out["table"].values()]
    rr = rules["E104-R7"]
    if len(rows) >= 3:
        e = rms([v["D"] - v["M"] for v in rows])
        R["E104-R7"] = {"verdict": "PASS" if e <= rr["pass_w"] else "FAIL" if e > rr["fail_w"] else "INCONCLUSIVE", "rms_w": e, "n": len(rows), "bias_w": sum(v["M"] - v["D"] for v in rows) / len(rows),
                        "worst": max((abs(k["D"] - k["M"]), n) for n, k in out["table"].items()), "inside_95": sum(v["lo95"] <= v["D"] <= v["hi95"] for v in rows)}
    else:
        R["E104-R7"] = {"verdict": "UNRESOLVED", "n": len(rows)}

    # R8: E92's fp16 watts stand on this card
    rr = rules["E104-R8"]
    d = C["fp16.h_premium"]
    if d["mean"] is None:
        R["E104-R8"] = {"verdict": "UNRESOLVED"}
    else:
        want = rr["e92_dips_w"] * rr["scale"]
        R["E104-R8"] = {"verdict": "PASS" if abs(d["mean"] - want) <= rr["band_w"] else "FAIL", "mean_w": d["mean"], "ci95_w": d["ci95"], "e92_on_this_card_w": want}

    # S1: the session tie against E82, dips removed
    cells, ok = {}, True
    for c, v in reg["session_tie"]["cells"].items():
        it = items.get(c)
        dd = it["D"]["mean"] if it and it.get("D") else None
        good = dd is not None and abs(dd - v["ref_w"]) <= v["band_w"]
        ok = ok and good
        cells[c] = {"D": dd, "ref_w": v["ref_w"], "band_w": v["band_w"], "ok": good}
    R["E104-S1"] = {"verdict": "PASS" if ok else "FAIL", "cells": cells}
    return out


def score_read(rows, reg):
    R = {}
    by = {}
    for r in rows:
        by.setdefault(r["tile"], []).append(r)
    rr = reg["rules"]
    # the controls first: if these miss, the read-back is broken and nothing is scored
    gate = {t: tile_readings(by.get(t, [])) for t in rr["E104-R2"]["gate_tiles"]}
    broken = [t for t, v in gate.items() if v is None or set(v) != set(READINGS)]
    cv = {t: tile_readings(by.get(t, [])) for t in rr["E104-R2"]["tiles"]}
    miss = [t for t, v in cv.items() if v is None or set(v) != set(READINGS)]
    unread = [t for t, v in cv.items() if v is None]
    R["E104-R2"] = {"verdict": "PASS" if not miss else "UNREAD" if len(unread) == len(miss) else "FAIL", "tiles_off": miss, "gate_off": broken, "tiles_read": len(cv), "first_off": first_miss(miss, by, "rtl") if miss else None}
    if broken:
        R["E104-R1"] = {"verdict": "NOT SCORED", "why": f"the controls miss: {broken}"}
        R["E104-R3"] = {"verdict": "NOT SCORED", "why": f"the controls miss: {broken}"}
    else:
        v, per = over_tiles(rr["E104-R1"]["tiles"], by)
        R["E104-R1"] = {"verdict": v, "tiles": per, "first_off_rtl": first_miss(rr["E104-R1"]["tiles"], by, "rtl")}
        v, per = over_tiles(rr["E104-R3"]["tiles"], by)
        R["E104-R3"] = {"verdict": v, "tiles": per, "first_off_rtl": first_miss(rr["E104-R3"]["tiles"], by, "rtl")}
    return R, {t: tile_readings(v) for t, v in by.items()}


def write_md(prim, arms, reg, rows, path):
    L = ["# E104 results", "", f"Passes kept: {prim.get('passes')}; set aside: {prim.get('set_aside')}; leak {prim.get('leak')}", "", "| rule | verdict | " + " | ".join(arms) + " | numbers |", "|---|---|" + "---|" * len(arms) + "---|"]
    for r, v in prim["rules"].items():
        nums = {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k not in ("verdict", "cells", "tiles", "arm_sensitive")}
        L.append(f"| {r} | **{v['verdict']}** | " + " | ".join(arms[a]["rules"].get(r, {}).get("verdict", "") for a in arms) + f" | {nums} |")
    L += ["", "## The read-back", "", "Words of 256 off each reading; C[0][0] and C[0][8] in hex, the card's and each reading's.", "", "| tile | n | minions agreeing | off rtl | off manual | off frozen | equals | card C00 / C08 | rtl | manual | frozen | words on the card |", "|---|---:|---:|---:|---:|---:|---|---|---|---|---|---:|"]
    for r in rows:
        if r.get("unread"):
            L.append(f"| `{r['tile']}` | {r['n']} | - | - | - | - | unread | | | | | |")
            continue
        o = r["words_off"]
        L.append(f"| `{r['tile']}` | {r['n']} | {r['minions']} | {o['rtl']} | {o['manual']} | {o['fl']} | {', '.join(r['matches']) or 'none'} | {r['card_c00']} / {r['card_c08']} | {r['c00']['rtl']} / {r['c08']['rtl']} | {r['c00']['manual']} / {r['c08']['manual']} | {r['c00']['fl']} / {r['c08']['fl']} | {r['card_distinct_words']} |")
    L += ["", "## The contrasts, per pass, t intervals", "", "| contrast | measured, W | n | bench M4 from real sums [95%] | E92's frozen reading |", "|---|---:|---:|---:|---:|"]
    for k, c in prim.get("contrasts", {}).items():
        m = "unread" if c["mean"] is None else f"{c['mean']:.3f} ± {c['ci95']:.3f}"
        f = "" if c.get("frozen_reading_w") is None else f"{c['frozen_reading_w']:.2f}"
        mm = "" if c.get("M") is None else f"{c['M']:.2f} ± {c['half95']:.2f}"
        L.append(f"| `{k}` | {m} | {c['n']} | {mm} | {f} |")
    L += ["", "## The tiles", "", "| tile | group | D, W (95%) | M4 [95%] | D - M4 |", "|---|---|---:|---:|---:|"]
    for k, r in sorted(prim.get("table", {}).items()):
        L.append(f"| `{k}` | {r['group']} | {r['D']:.2f} ± {r['ci95'] or 0:.2f} | {r['M']:.2f} [{r['lo95']:.2f}, {r['hi95']:.2f}] | {r['D'] - r['M']:+.2f} |")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e104", required=True)
    ap.add_argument("--readback", default=None)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    spec = json.load(open(SPEC))
    rows = read_rows(a.readback, spec)
    read_rules, read_tiles = score_read(rows, reg)
    prim = score_power(json.load(open(a.e104)), reg)
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
        write_md(prim, arms, reg, rows, a.md)
    print(json.dumps({r: {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items() if k not in ("cells", "tiles")} for r, v in prim["rules"].items()}, indent=0))
    print(prim.get("tally"))


if __name__ == "__main__":
    main()
