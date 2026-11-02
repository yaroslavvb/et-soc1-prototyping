#!/usr/bin/env python3
"""E137's rules (E137.md, "Decision rules"), on reductions written by reduce_e137.py. Standard library only.

    python3 tools/claims-v3/e137/score_e137.py --primary <e137.json> --relaxed <e137-relaxed.json> [--arm name=<json> ...] \
        [--md results.md] [--json scored.json]

Every threshold and prediction comes from predictions-e137.json (M4's numbers copied there from E128's freeze; E128's per-pass values copied from
its committed reduction). The set-aside rule (predictions-e137.json > set_aside_rule) picks the reading: S1 the primary if it keeps >= 4 passes;
else S2 (passes set aside only by the pi tie restored whole, from the relaxed reduction); else S3 (passes set aside only by fp32 or int8 anchor
gates, or the tie, restored for fp16's items). A quantity is formed per pass, only in passes where every tile it reads has a value; its interval is
t(0.975, n - 1) over those passes; a rule whose quantity has fewer than 4 passes reads NOT SCORED. Arms are scored on their own kept passes (S1
only) and reported; a verdict that differs at an arm is marked arm-sensitive.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e137.json")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179}
FP16_ANCHORS = ("fp16.zeros", "fp16.randn")
OTHER_ANCHORS = ("fp32.zeros", "fp32.randn", "int8.zeros", "int8.full")
TIE = "anchor_pi"


def t975(df):
    return T975.get(df, 1.96 + 2.4 / max(df, 1))


def mci(vals):
    v = [x for x in vals if x is not None]
    if not v:
        return {"mean": None, "ci95": None, "n": 0}
    if len(v) < 2:
        return {"mean": v[0], "ci95": None, "n": 1}
    return {"mean": sum(v) / len(v), "ci95": t975(len(v) - 1) * statistics.stdev(v) / math.sqrt(len(v)), "n": len(v)}


def lohi(s):
    if s["mean"] is None or s["ci95"] is None:
        return None, None
    return s["mean"] - s["ci95"], s["mean"] + s["ci95"]


# ---- the set-aside rule ------------------------------------------------------------------------------------------------------------------
def classify_why(why):
    """'tie' if every reason is the pi tie's drift; 'other' if every reason is the tie or an fp32/int8 anchor gate; 'fp16' if any reason names an
    fp16 anchor; 'never' if any reason is failed runs (or anything not an anchor or the tie)."""
    kinds = set()
    for w in why:
        if w.startswith("anchor_pi drifts"):
            kinds.add("tie")
        elif any(w.startswith(a + " ") for a in OTHER_ANCHORS):
            kinds.add("other")
        elif any(w.startswith(a + " ") for a in FP16_ANCHORS):
            kinds.add("fp16")
        else:
            kinds.add("never")
    if "never" in kinds:
        return "never"
    if "fp16" in kinds:
        return "fp16"
    if kinds == {"tie"}:
        return "tie"
    return "other"


def reading(primary, relaxed, min_kept):
    """Returns (name, per_pass {pass: {item: D}}, notes) by the set-aside rule."""
    pp = {p: {it: v["D"] for it, v in primary["per_pass"][p].items() if isinstance(v, dict) and v.get("D") is not None}
          for p in primary.get("per_pass", {})}
    kept = sorted(pp)
    notes = {"S1_passes": kept, "set_aside": primary.get("passes_set_aside", []), "config_flags": primary.get("passes_config_flags", [])}
    if len(kept) >= min_kept or relaxed is None:
        return "S1", pp, notes
    cfg_bad = {str(x["pass"]) for x in primary.get("passes_config_flags", [])}
    rel = {p: {it: v["D"] for it, v in relaxed["per_pass"][p].items() if isinstance(v, dict) and v.get("D") is not None}
           for p in relaxed.get("per_pass", {})}
    cls = {str(x["pass"]): classify_why(x["why"]) for x in primary.get("passes_set_aside", []) if str(x["pass"]) not in cfg_bad}
    s2 = dict(pp)
    for p, c in cls.items():
        if c == "tie" and p in rel:
            s2[p] = rel[p]
    notes["S2_restored"] = sorted(p for p in s2 if p not in pp)
    if len(s2) >= min_kept:
        return "S2", s2, notes
    s3 = dict(s2)
    for p, c in cls.items():
        if c == "other" and p in rel and p not in s3:
            s3[p] = {it: d for it, d in rel[p].items() if it.startswith("fp16.")}
    notes["S3_restored_fp16_only"] = sorted(p for p in s3 if p not in s2)
    return "S3", s3, notes


# ---- quantities ----------------------------------------------------------------------------------------------------------------------------
def per_pass_q(reg, pp):
    Q = reg["quantities"]
    out = {}

    def one(q, row):
        d = Q[q]
        if d["form"] == "contrast":
            if any(t not in row for t in d["plus"] + d["minus"]):
                return None
            return sum(row[t] for t in d["plus"]) - sum(row[t] for t in d["minus"])
        a, b = one(d["a"], row), one(d["b"], row)
        if a is None or b is None:
            return None
        if d["form"] == "ratio":
            return None if b == 0 else a / b
        return a - b                                  # diff
    for q in Q:
        out[q] = {p: one(q, row) for p, row in pp.items()}
        out[q] = {p: v for p, v in out[q].items() if v is not None}
    return out


def verdict(rule, s):
    lo, hi = lohi(s)
    if lo is None:
        return "NOT SCORED"
    f, N = rule["form"], rule.get("names", {})
    if f == "bands":
        if lo > rule["hi"]:
            return N["above"]
        if hi < rule["lo"]:
            return N["below"]
        if lo >= rule["lo"] and hi <= rule["hi"]:
            return N["inside"]
        return "INCONCLUSIVE"
    if f == "band_then_sign":
        b = rule["band"]
        if -b <= lo and hi <= b:
            return N["inside"]
        if lo > 0:
            return N["above"]
        if hi < 0:
            return N["below"]
        return "INCONCLUSIVE"
    if f == "sign_then_band":
        b = rule["band"]
        if lo > 0:
            return N["above"]
        if hi < 0:
            return N["below"]
        if -b <= lo and hi <= b:
            return N["inside"]
        return "INCONCLUSIVE"
    raise ValueError(f)


def score(reg, name, pp, min_kept, e128_q=None):
    qv = per_pass_q(reg, pp)
    qs = {q: dict(mci(v.values()), per_pass={p: round(x, 5) for p, x in sorted(v.items())},
                  M=reg["quantities"][q].get("M"), half95=reg["quantities"][q].get("half95"), form=reg["quantities"][q]["form"],
                  what=reg["quantities"][q]["what"]) for q, v in qv.items()}
    R = reg["rules"]
    rules = {}
    for rn in ("E137-R1", "E137-R2", "E137-R3", "E137-R4"):
        q = R[rn]["legs"][0]
        s = qs[q]
        v = "NOT SCORED" if s["n"] < min_kept else verdict(R[rn], s)
        rules[rn] = {"verdict": v, "quantity": q, "mean": s["mean"], "ci95": s["ci95"], "n": s["n"], "M4": s["M"]}
    s = qs["fp16.step"]
    if s["n"] < min_kept:
        v = "NOT SCORED"
    else:
        v = "PASS" if abs(s["mean"] - R["E137-R5"]["e108_w"]) <= R["E137-R5"]["band_w"] else "FAIL"
    rules["E137-R5"] = {"verdict": v, "mean": s["mean"], "ci95": s["ci95"], "n": s["n"], "e108_w": R["E137-R5"]["e108_w"]}
    # R6: M4 on the eight items, item means over the reading's passes
    items = list(reg["tiles"])
    miss = []
    for t in items:
        vals = [row[t] for row in pp.values() if t in row]
        st = mci(vals)
        if st["mean"] is None:
            continue
        miss.append({"tile": t, "D": st["mean"], "ci95": st["ci95"], "n": st["n"], "M4": reg["tiles"][t]["pred"]["M"],
                     "lo95": reg["tiles"][t]["pred"]["lo95"], "hi95": reg["tiles"][t]["pred"]["hi95"],
                     "inside": reg["tiles"][t]["pred"]["lo95"] <= st["mean"] <= reg["tiles"][t]["pred"]["hi95"]})
    nmin = min((m["n"] for m in miss), default=0)
    if nmin < min_kept or len(miss) < len(items):
        v6, rmsw = "NOT SCORED", None
    else:
        rmsw = math.sqrt(sum((m["D"] - m["M4"]) ** 2 for m in miss) / len(miss))
        v6 = "PASS" if rmsw <= R["E137-R6"]["pass_w"] else ("FAIL" if rmsw > R["E137-R6"]["fail_w"] else "INCONCLUSIVE")
    rules["E137-R6"] = {"verdict": v6, "rms_w": rmsw, "n_tiles": len(miss),
                        "bias_w": (sum(m["D"] - m["M4"] for m in miss) / len(miss)) if miss else None, "tiles": miss}
    # R7: M4's seven fp16 sign contrasts out of sample
    r7 = R["E137-R7"]
    rows, ok = [], True
    for q in r7["legs"]:
        s = qs[q]
        if s["n"] < min_kept:
            ok = False
        rows.append({"q": q, "mean": s["mean"], "ci95": s["ci95"], "n": s["n"], "M4": s["M"], "half95": s["half95"],
                     "err": None if s["mean"] is None else s["mean"] - s["M"],
                     "inside": None if s["mean"] is None else abs(s["mean"] - s["M"]) <= s["half95"]})
    if not ok:
        v7, r7rms = "NOT SCORED", None
    else:
        r7rms = math.sqrt(sum(r["err"] ** 2 for r in rows) / len(rows))
        nout = sum(1 for r in rows if not r["inside"])
        if nout == 0 and r7rms <= r7["inside_all_rms_w"]:
            v7 = "PASS"
        elif nout >= r7["fail_outside_n"] or r7rms > r7["fail_rms_w"]:
            v7 = "FAIL"
        else:
            v7 = "INCONCLUSIVE"
    rules["E137-R7"] = {"verdict": v7, "rms_w": r7rms, "rows": rows, "outside": sum(1 for r in rows if r["inside"] is False)}
    # R8: against E128's two passes
    r8 = R["E137-R8"]
    sub = {}
    if e128_q is not None:
        for q in r8["legs"]:
            a, b = qs[q], e128_q.get(q) or {}
            if a["n"] < min_kept or a["ci95"] is None or b.get("ci95") is None:
                sub[q] = {"verdict": "NOT SCORED"}
                continue
            d = a["mean"] - b["mean"]
            h = math.sqrt(a["ci95"] ** 2 + b["ci95"] ** 2)
            vv = "PASS" if abs(d) + h <= r8["w"] else ("FAIL" if abs(d) - h > r8["w"] else "INCONCLUSIVE")
            sub[q] = {"verdict": vv, "d": d, "h": h, "e137": a["mean"], "e128": b["mean"]}
        vs = [x["verdict"] for x in sub.values()]
        v8 = "NOT SCORED" if "NOT SCORED" in vs else ("FAIL" if "FAIL" in vs else ("PASS" if all(x == "PASS" for x in vs) else "INCONCLUSIVE"))
    else:
        v8 = "NOT SCORED"
    rules["E137-R8"] = {"verdict": v8, "per_share": sub}
    return {"reading": name, "passes": sorted(pp), "quantities": qs, "rules": rules}


def session_tie(reg, red):
    out = {}
    for c, b in reg["session_tie"]["cells"].items():
        it = (red.get("items") or {}).get(c) or {}
        D = (it.get("D") or {}).get("mean")
        out[c] = {"D": D, "ref_w": b["ref_w"], "band_w": b["band_w"], "ok": None if D is None else abs(D - b["ref_w"]) <= b["band_w"]}
    oks = [x["ok"] for x in out.values()]
    v = "NOT SCORED" if None in oks or len(red.get("passes", [])) < reg["set_aside_rule"]["min_kept_passes"] else ("PASS" if all(oks) else "FAIL")
    return {"verdict": v, "cells": out}


def pooled(reg, pp137):
    """Reported arm, no verdict of its own: E128's two passes (its committed per-pass D) and E137's, each pass one replicate."""
    pp = {("e128:" + p): row for p, row in reg["e128_reference"]["per_pass_D"].items()}
    pp.update({("e137:" + p): row for p, row in pp137.items()})
    qv = per_pass_q(reg, pp)
    out = {}
    for q in ("fp16.share_het_m", "fp16.share_walk_m", "fp16.share_het_z", "fp16.design_m", "fp16.Bm_het", "fp16.Bm_walk", "fp16.Bm_rest",
              "fp16.Bz_rest", "fp16.step"):
        s = mci(qv[q].values())
        out[q] = dict(s, per_pass={p: round(x, 5) for p, x in sorted(qv[q].items())})
    for rn in ("E137-R1", "E137-R2", "E137-R3", "E137-R4"):
        q = reg["rules"][rn]["legs"][0]
        out[q]["bands_verdict"] = verdict(reg["rules"][rn], out[q]) if out[q]["ci95"] is not None else "NOT SCORED"
    return out


def fmt(s, k=3):
    if s is None or s.get("mean") is None:
        return "—"
    return f"{s['mean']:.{k}f}" + ("" if s.get("ci95") is None else f" ± {s['ci95']:.{k}f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", required=True)
    ap.add_argument("--relaxed")
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    mk = reg["set_aside_rule"]["min_kept_passes"]
    prim = json.load(open(a.primary))
    rel = json.load(open(a.relaxed)) if a.relaxed and os.path.exists(a.relaxed) else None
    name, pp, notes = reading(prim, rel, mk)
    e128_q = reg["e128_reference"]["quantities"]
    res = score(reg, name, pp, mk, e128_q)
    res["set_aside"] = notes
    res["rules"]["E137-S1"] = session_tie(reg, prim)
    res["leak"] = prim.get("leak")
    arms = {}
    for spec in a.arm:
        nm, path = spec.split("=", 1)
        if not os.path.exists(path):
            continue
        r = json.load(open(path))
        _, app, _ = reading(r, None, mk)
        sc = score(reg, "S1", app, mk, e128_q)
        sc["rules"]["E137-S1"] = session_tie(reg, r)
        arms[nm] = {"passes": sc["passes"], "rules": {k: v["verdict"] for k, v in sc["rules"].items()},
                    "shares": {q: {"mean": sc["quantities"][q]["mean"], "ci95": sc["quantities"][q]["ci95"], "n": sc["quantities"][q]["n"]}
                               for q in ("fp16.share_het_m", "fp16.share_walk_m", "fp16.share_het_z")}}
    for rn, rv in res["rules"].items():
        moved = sorted(nm for nm, ar in arms.items() if ar["rules"].get(rn) not in (rv["verdict"], "NOT SCORED"))
        rv["arm_sensitive"] = moved
    res["arms"] = arms
    res["pooled_e128_e137"] = pooled(reg, pp)
    out = {"experiment": "E137", "primary": res}
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, default=str)
    L = [f"# E137 results", "", f"Reading: **{name}** (set-aside rule); passes {res['passes']}; S1 kept {notes['S1_passes']}; "
         f"set aside {notes['set_aside']}; leak {prim.get('leak')}", "",
         "| rule | verdict | quantity | measured | n | M4 | arm-sensitive at |", "|---|---|---|---:|---:|---:|---|"]
    for rn in ("E137-R1", "E137-R2", "E137-R3", "E137-R4"):
        r = res["rules"][rn]
        L.append(f"| {rn} | **{r['verdict']}** | `{r['quantity']}` | {fmt(r)} | {r['n']} | {r['M4']:.3f} | {', '.join(r['arm_sensitive']) or '—'} |")
    r = res["rules"]["E137-R5"]
    L.append(f"| E137-R5 | **{r['verdict']}** | `fp16.step` | {fmt(r)} W | {r['n']} | E108 {r['e108_w']:.3f} | {', '.join(r['arm_sensitive']) or '—'} |")
    r = res["rules"]["E137-R6"]
    r6 = "—" if r["rms_w"] is None else f"{r['rms_w']:.3f} W, bias {r['bias_w']:+.3f} W"
    L.append(f"| E137-R6 | **{r['verdict']}** | rms(D − M4), {r['n_tiles']} items | {r6} | | | {', '.join(r['arm_sensitive']) or '—'} |")
    r = res["rules"]["E137-R7"]
    L.append(f"| E137-R7 | **{r['verdict']}** | M4's seven sign contrasts | rms {'—' if r['rms_w'] is None else round(r['rms_w'], 3)} W, {r['outside']} outside | | | {', '.join(r['arm_sensitive']) or '—'} |")
    r = res["rules"]["E137-R8"]
    L.append(f"| E137-R8 | **{r['verdict']}** | against E128's two passes | " + "; ".join(
        f"{q.split('.')[1]} {x['verdict']}" + (f" (d {x['d']:+.3f}, h {x['h']:.3f})" if 'd' in x else '') for q, x in r["per_share"].items()) + f" | | | {', '.join(r['arm_sensitive']) or '—'} |")
    r = res["rules"]["E137-S1"]
    L.append(f"| E137-S1 | **{r['verdict']}** | session tie | " + "; ".join(
        f"{c} {'—' if x['D'] is None else round(x['D'], 2)} ({x['ref_w']:.2f} ± {x['band_w']})" for c, x in r["cells"].items()) + f" | | | {', '.join(r['arm_sensitive']) or '—'} |")
    L += ["", "## Every quantity, per pass, t intervals", "", "| quantity | form | measured | n | M4 ± half95 | per pass |", "|---|---|---:|---:|---:|---|"]
    for q, s in res["quantities"].items():
        m4 = "—" if s["M"] is None else (f"{s['M']:.3f}" + ("" if s["half95"] is None else f" ± {s['half95']:.2f}"))
        L.append(f"| `{q}` | {s['form']} | {fmt(s)} | {s['n']} | {m4} | {', '.join(f'{v:.3f}' for v in s['per_pass'].values())} |")
    L += ["", "## The items against M4 (R6)", "", "| item | D, W | n | M4 [95%] | D − M4 |", "|---|---:|---:|---:|---:|"]
    for m in res["rules"]["E137-R6"]["tiles"]:
        L.append(f"| `{m['tile']}` | {m['D']:.3f}" + ("" if m["ci95"] is None else f" ± {m['ci95']:.3f}") +
                 f" | {m['n']} | {m['M4']:.2f} [{m['lo95']:.2f}, {m['hi95']:.2f}] | {m['D'] - m['M4']:+.3f} |")
    L += ["", "## M4's sign contrasts out of sample (R7)", "", "| contrast | measured, W | M4 ± half95 | error | inside |", "|---|---:|---:|---:|---|"]
    for x in res["rules"]["E137-R7"]["rows"]:
        L.append(f"| `{x['q']}` | {fmt(x)} | {x['M4']:.3f} ± {x['half95']:.2f} | " + ("—" if x["err"] is None else f"{x['err']:+.3f}") + f" | {x['inside']} |")
    L += ["", "## Arms (each on its own kept passes, S1 only)", "", "| arm | passes | " + " | ".join(res["rules"]) + " |",
          "|---|---|" + "---|" * len(res["rules"])]
    for nm, ar in arms.items():
        L.append(f"| {nm} | {len(ar['passes'])} | " + " | ".join(ar["rules"].get(k, "—") for k in res["rules"]) + " |")
    L += ["", "## Pooled with E128's two passes (reported arm, no verdict of its own)", "", "| quantity | pooled | n | bands, if scored |", "|---|---:|---:|---|"]
    for q, s in res["pooled_e128_e137"].items():
        L.append(f"| `{q}` | {fmt(s)} | {s['n']} | {s.get('bands_verdict', '')} |")
    if a.md:
        open(a.md, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:16]))


if __name__ == "__main__":
    main()
