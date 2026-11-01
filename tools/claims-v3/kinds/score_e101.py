#!/usr/bin/env python3
"""E101 scorer (Q132): the power rules R1-R12 of tools/claims-v3/kinds/predictions-e101.json as frozen, on reduce_e101.py's output (E78's reduction, unchanged, with E101's items), and the
check records of the raw passes. Thresholds and predicted numbers are read from the frozen file, never retyped. Standard library only.

    python3 tools/claims-v3/kinds/score_e101.py --e101 e101.json [--arm leak0=e101-leak0.json ...] --raw <pass dir> [...] --json scored.json --md results.md

Intervals are t(0.975, n - 1) x SE over kept passes, a difference paired within the pass; fewer than the frozen minimum of kept passes: NOT SCORED. A verdict that moves between leakage arms is marked
slope-sensitive. It changes no rule.
"""
import argparse
import gzip
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e101_common as e101  # noqa: E402

T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
TYPES = ("fp32", "fp16", "int8")
FOUR = ("zeros", "ones", "random", "sparse50")
PASS, FAIL, INC, NOTSC = "PASS", "FAIL", "INCONCLUSIVE", "NOT SCORED"


def mc(v):
    v = [float(x) for x in v if x is not None]
    if not v:
        return {"mean": None, "se": None, "n": 0, "ci95": None, "lo": None, "hi": None}
    m = statistics.fmean(v)
    if len(v) < 2:
        return {"mean": m, "se": None, "n": 1, "ci95": None, "lo": None, "hi": None}
    se = statistics.stdev(v) / math.sqrt(len(v))
    h = se * T95.get(len(v) - 1, 1.96)
    return {"mean": m, "se": se, "n": len(v), "ci95": h, "lo": m - h, "hi": m + h}


def rnd(x, n=3):
    return None if x is None else round(x, n)


def name(arm, t, k):
    k2 = e101.kind_name(t, k)
    if arm == "res":
        return f"res.{t}.{k}" if k in ("e37", "real") else f"{t}.{k2}"
    return f"{arm}.{t}.{k2}"


def three_way(m, lo, hi, min_n):
    """R4's reading: PASS if the interval overlaps the range and the mean is inside it; FAIL if the interval lies outside it; else INCONCLUSIVE."""
    if m["n"] < min_n or m["ci95"] is None:
        return NOTSC
    if m["hi"] < lo or m["lo"] > hi:
        return FAIL
    return PASS if lo <= m["mean"] <= hi else INC


def combine(vs):
    vs = list(vs)
    if not vs or all(v == NOTSC for v in vs):
        return NOTSC
    if any(v == FAIL for v in vs):
        return FAIL
    if any(v == NOTSC for v in vs):
        return NOTSC
    return PASS if all(v == PASS for v in vs) else INC


def spearman(x, y):
    def ranks(a):
        o = sorted(range(len(a)), key=lambda i: a[i])
        r = [0.0] * len(a)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and a[o[j + 1]] == a[o[i]]:
                j += 1
            for q in range(i, j + 1):
                r[o[q]] = (i + j) / 2.0
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    a = sum((p - mx) * (q - my) for p, q in zip(rx, ry))
    b = math.sqrt(sum((p - mx) ** 2 for p in rx) * sum((q - my) ** 2 for q in ry))
    return a / b if b else None


def score(E, reg, E78):
    rules = reg["rules"]
    MIN = rules["min_passes"]
    per = E["per_pass"]
    passes = sorted(per)
    r_of = {t: {a: reg["inputs"]["cpo"]["res"][t] / reg["inputs"]["cpo"][a][t] for a in reg["inputs"]["cpo"]} for t in TYPES}
    item = E["items"]

    def vals(n, key="S"):
        return {p: per[p][n][key] for p in passes if n in per[p] and per[p][n].get(key) is not None}

    def stat(n, key="S"):
        return mc(list(vals(n, key).values()))

    def paired(fn, *names):
        """per pass fn(values of the names), over the passes that hold them all."""
        series = [vals(n) for n in names]
        out = []
        for p in passes:
            if all(p in s for s in series):
                out.append(fn(*[s[p] for s in series]))
        return mc(out)

    cpo = lambda n: item.get(n, {}).get("cycles_per_op")
    V = {}
    # R1
    c = {}
    for t in TYPES:
        m = stat(name("mm16", t, "e37"))
        T = reg["tie_e37"][t]
        ok = m["mean"] is not None and abs(m["mean"] - T["S_w"]) <= rules["R1_tie_e37"]["band_w"]
        cps = {k: cpo(name("mm16", t, k)) for k in FOUR + ("e37", "real")}
        ok2 = all(v is not None and abs(v / T["cpo"] - 1) <= rules["R1_tie_e37"]["cpo_rel"] for v in cps.values() if v is not None) and any(v is not None for v in cps.values())
        c[t] = {"S": m, "frozen": T, "cycles": cps, "watts_ok": ok, "cycles_ok": ok2, "verdict": (NOTSC if m["n"] < MIN else (PASS if ok and ok2 else FAIL))}
    V["R1_tie_e37"] = {"verdict": combine(x["verdict"] for x in c.values()), "cells": c}
    # R2
    c = {}
    for n in rules["R2_tie_e78"]["cells"]:
        m = stat(n)
        ref = E78[n]["S"]["mean"]
        c[n] = {"S": m, "e78": rnd(ref), "diff": rnd(None if m["mean"] is None else m["mean"] - ref), "verdict": NOTSC if m["n"] < MIN else (PASS if abs(m["mean"] - ref) <= rules["R2_tie_e78"]["band_w"] else FAIL)}
    V["R2_tie_e78"] = {"verdict": combine(x["verdict"] for x in c.values()), "cells": c}
    # R3 and R3b
    c, res2 = {}, {"mm16": [], "gemm1": []}
    for t in TYPES:
        for k in FOUR:
            r = r_of[t]["mm16"]
            m = paired(lambda a, b: a - r * b, name("mm16", t, k), name("res", t, k))
            c[f"{t}.{k}"] = {"premium": m, "verdict": NOTSC if m["n"] < MIN else (PASS if m["lo"] > rules["R3_premium"]["bar_w"] else FAIL)}
            for arm in res2:
                s = stat(name(arm, t, k))
                f = reg["cells"].get(name(arm, t, k))
                if s["mean"] is not None and f:
                    res2[arm].append((name(arm, t, k), s["mean"] - f["S_w"]))
    V["R3_premium"] = {"verdict": combine(x["verdict"] for x in c.values()), "cells": c}
    rm = {a: (math.sqrt(sum(d * d for _, d in v) / len(v)) if v else None) for a, v in res2.items()}
    V["R3b_model"] = {"rms_w": {a: rnd(x) for a, x in rm.items()}, "residuals_w": {a: {n: rnd(d) for n, d in v} for a, v in res2.items()},
                      "verdict": {"mm16": NOTSC if len(res2["mm16"]) < 12 or len(passes) < MIN else (PASS if rm["mm16"] <= rules["R3b_model"]["mm16_rms_w"] else FAIL),
                                  "gemm1": NOTSC if len(res2["gemm1"]) < 12 or len(passes) < MIN else (PASS if rm["gemm1"] <= rules["R3b_model"]["gemm1_rms_w"] else FAIL)}}
    # R4
    c = {}
    for t in TYPES:
        m = paired(lambda a, b: a - b, name("mm16", t, "e37"), name("res", t, "e37"))
        F = reg["kernel_clause"][t]
        c[t] = {"diff": m, "frozen": F, "verdict": three_way(m, F["lo"], F["hi"], MIN)}
    V["R4_clause"] = {"verdict": c["int8"]["verdict"], "cells": c}
    # R5, R5b
    c, d = {}, {}
    for t in TYPES:
        for arm in ("mm16", "gemm1"):
            r = r_of[t][arm]
            z, q = name("res", t, "zeros"), name("res", t, "random")
            m = paired(lambda a, b, x, y: (a - b) - r * (x - y), name(arm, t, "random"), name(arm, t, "zeros"), q, z)
            F = reg["memory_path"][f"{arm}.{t}"]
            c[f"{arm}.{t}"] = {"M": m, "frozen": F, "verdict": three_way(m, F["lo"], F["hi"], MIN)}
        r = r_of[t]["mm16"]
        m = paired(lambda a, b, x, y: (a - b) - r * (x - y), name("mm16", t, "ones"), name("mm16", t, "zeros"), name("res", t, "ones"), name("res", t, "zeros"))
        B = rules["R5b_memory_constant"]["band_w"]
        v = NOTSC if m["n"] < MIN or m["ci95"] is None else (PASS if m["lo"] >= -B and m["hi"] <= B else (FAIL if m["hi"] < -B or m["lo"] > B else INC))
        d[t] = {"C": m, "verdict": v}
    V["R5_memory_data"] = {"verdict": combine(c[f"mm16.{t}"]["verdict"] for t in TYPES), "cells": c}
    V["R5b_memory_constant"] = {"verdict": combine(x["verdict"] for x in d.values()), "cells": d}
    # R6
    c = {}
    for arm in ("mm16", "gemm1"):
        for t in TYPES:
            kinds = [k for k in rules["kinds_for_rank"] if stat(name(arm, t, k))["mean"] is not None and stat(name("res", t, k))["mean"] is not None]
            x = [stat(name("res", t, k))["mean"] for k in kinds]
            y = [stat(name(arm, t, k))["mean"] for k in kinds]
            rho = spearman(x, y) if len(kinds) >= 4 else None
            bar = rules["R6_rank"]["rho"] if len(kinds) == 5 else rules["R6_rank"]["rho_four_kinds"]
            c[f"{arm}.{t}"] = {"kinds": kinds, "res": [rnd(a) for a in x], "arm": [rnd(a) for a in y], "rho": rnd(rho), "bar": bar, "verdict": NOTSC if rho is None or len(passes) < MIN else (PASS if rho >= bar else FAIL)}
    V["R6_rank"] = {"verdict": combine(x["verdict"] for x in c.values()), "cells": c}
    # R7
    c = {}
    for t in TYPES:
        e78share = E78[f"{t}.zeros"]["S"]["mean"] / E78[f"{t}.{e101.RANDOM_KIND[t]}"]["S"]["mean"]
        for arm in ("mm16", "gemm1"):
            m = paired(lambda a, b: a / b, name(arm, t, "zeros"), name(arm, t, "random"))
            ok = m["n"] >= MIN and m["ci95"] is not None
            c[f"{arm}.{t}"] = {"share": m, "res_share_e78": rnd(e78share), "R7a": NOTSC if not ok else (PASS if m["lo"] > e78share else FAIL),
                               "R7b": NOTSC if not ok else (PASS if m["hi"] < rules["R7_gate"]["bar"] else (FAIL if m["lo"] > rules["R7_gate"]["bar"] else INC))}
    V["R7_gate"] = {"R7a": combine(x["R7a"] for x in c.values()), "R7b": combine(x["R7b"] for x in c.values()), "cells": c}
    # R8
    c = {}
    for t in TYPES:
        for lab, a in (("mm16_minus_gemm1", "mm16"), ("gemmnc1_minus_gemm1", "gemmnc1")):
            m = paired(lambda x, y: x - y, name(a, t, "random"), name("gemm1", t, "random"))
            c[f"{lab}.{t}"] = {"diff": m, "verdict": NOTSC if m["n"] < MIN or m["ci95"] is None else (PASS if m["lo"] > 0 else (FAIL if m["hi"] < 0 else INC))}
    V["R8_coop"] = {"verdict": combine(x["verdict"] for x in c.values()), "cells": c}
    # R9b
    c = {}
    for arm in ("tenb", "mm16", "gemm1", "gemm16", "gemmnc1", "mmp64"):
        for t in TYPES:
            ns = [it for it in item if it.startswith(f"{arm}.{t}.")]
            cp = {n: cpo(n) for n in ns if cpo(n)}
            if len(cp) >= 2:
                sp = max(cp.values()) / min(cp.values()) - 1
                c[f"{arm}.{t}"] = {"cycles": {n: rnd(v, 2) for n, v in cp.items()}, "spread": rnd(sp, 4), "verdict": PASS if sp <= rules["R9b_cycles"]["cpo_rel"] else FAIL}
    V["R9b_cycles"] = {"verdict": combine(x["verdict"] for x in c.values()) if len(passes) >= MIN else NOTSC, "cells": c}
    # R10
    xs, ys = [], []
    for n, e in item.items():
        s, dt = stat(n)["mean"], stat(n, "dT_win")["mean"]
        if s is not None and dt is not None and s >= rules["R10_heat"]["min_s_w"]:
            xs.append(s)
            ys.append(dt)
    slope = None
    if len(xs) >= 5:
        mx, my = statistics.fmean(xs), statistics.fmean(ys)
        slope = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / sum((a - mx) ** 2 for a in xs)
    lo, hi = rules["R10_heat"]["band_c_per_w"]
    V["R10_heat"] = {"slope_c_per_w": rnd(slope, 4), "ratio_mean_c_per_w": rnd(statistics.fmean(b / a for a, b in zip(xs, ys)), 4) if xs else None, "n_cells": len(xs), "verdict": NOTSC if slope is None or len(passes) < MIN else (PASS if lo <= slope <= hi else FAIL)}
    # R11
    m = paired(lambda a, b: a - b, name("mmp64", "fp32", "random"), name("mmp64", "fp32", "zeros"))
    F = reg["dram"]
    cp = {k: cpo(name("mmp64", "fp32", k)) for k in ("zeros", "random")}
    okc = all(v is not None and 0.9 * F["cpo_e37"][0] <= v <= 1.1 * F["cpo_e37"][1] for v in cp.values())
    V["R11_dram"] = {"diff": m, "frozen": F, "cycles": cp, "cycles_inside": okc, "S_zeros": stat(name("mmp64", "fp32", "zeros")), "S_random": stat(name("mmp64", "fp32", "random")), "verdict": three_way(m, F["lo"], F["hi"], MIN)}
    # R12
    c = {}
    for t in TYPES:
        m = paired(lambda a, b: a - b, name("gemm16", t, "random"), name("gemm16", t, "zeros"))
        cz, cr = cpo(name("gemm16", t, "zeros")), cpo(name("gemm16", t, "random"))
        g1 = cpo(name("gemm1", t, "random"))
        c[t] = {"diff": m, "cycles_zeros": rnd(cz, 1), "cycles_random": rnd(cr, 1), "ratio_to_gemm1": rnd(cr / g1, 3) if cr and g1 else None, "verdict": NOTSC if m["n"] < MIN or m["ci95"] is None else (PASS if m["lo"] > 0 else FAIL)}
    V["R12_gemm16"] = {"verdict": combine(x["verdict"] for x in c.values()), "cells": c}
    return V, passes


def checks_of(dirs):
    """The host's check records: per item the verdicts, and every launch's ok."""
    out, bad_launches = {}, []
    for d in dirs:
        p = os.path.join(d, "runs.jsonl")
        if not os.path.exists(p):
            continue
        for line in open(p):
            r = json.loads(line)
            if r.get("test") == "check":
                out.setdefault(r["item"], {}).setdefault(r["result"], 0)
                out[r["item"]][r["result"]] += 1
            elif not r.get("ok", True):
                bad_launches.append((r.get("block"), r.get("item"), r.get("launch")))
    return out, bad_launches


def r9(checks, min_runs=1):
    if not checks:
        return {"verdict": NOTSC, "why": "no check records"}
    wrong = {n: v for n, v in checks.items() if v.get("wrong")}
    inexact = {}
    for n, v in checks.items():
        parts = n.split(".")
        k = parts[-1]
        if (k == "zeros" or ".int8." in n) and set(v) - {"exact"}:
            inexact[n] = v
    return {"verdict": PASS if not wrong and not inexact else FAIL, "wrong": wrong, "should_be_exact_but_not": inexact, "items_checked": len(checks),
            "exact_items": sorted(n for n, v in checks.items() if set(v) == {"exact"})}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e101", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--raw", nargs="*", default=[])
    ap.add_argument("--json", required=True)
    ap.add_argument("--md", required=True)
    a = ap.parse_args()
    reg = json.load(open(os.path.join(HERE, "predictions-e101.json")))
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    E78 = json.load(open(os.path.join(root, "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json")))["items"]
    E = json.load(open(a.e101))
    V, passes = score(E, reg, E78)
    checks, bad_launches = checks_of(a.raw)
    V["R9_correct"] = r9(checks)
    V["R9_correct"]["launches_not_ok"] = bad_launches[:40]
    arms = {}
    for spec in a.arm:
        lab, path = spec.split("=", 1)
        arms[lab] = score(json.load(open(path)), reg, E78)[0]
    verdict_keys = {"R1_tie_e37": "verdict", "R2_tie_e78": "verdict", "R3_premium": "verdict", "R4_clause": "verdict", "R5_memory_data": "verdict", "R5b_memory_constant": "verdict", "R6_rank": "verdict",
                    "R8_coop": "verdict", "R9b_cycles": "verdict", "R10_heat": "verdict", "R11_dram": "verdict", "R12_gemm16": "verdict"}
    sens = {}
    for r, key in verdict_keys.items():
        vs = {lab: arms[lab][r][key] for lab in arms}
        if any(v != V[r][key] for v in vs.values()):
            sens[r] = {"primary": V[r][key], **vs}
    out = {"experiment": "E101", "passes": passes, "kept_runs": E["kept"], "runs": E["runs"], "leak": E["leak"], "idle": E["idle_level"], "clock_mhz": E["clock_mhz"], "passes_set_aside": E["passes_set_aside"],
           "verdicts": {r: V[r].get(verdict_keys.get(r, "verdict")) for r in V}, "slope_sensitive": sens, "rules": V, "checks": checks}
    json.dump(out, open(a.json, "w"), indent=1)
    L = [f"# E101 scored, {len(passes)} passes, {E['kept']}/{E['runs']} runs kept, leak {E['leak']['k_w_per_c']:.4f} W/C, idle {E['idle_level']['mean']:.3f} W", ""]
    for r in sorted(V):
        v = V[r]
        L.append(f"- **{r}**: {v.get('verdict', {k: v[k] for k in ('R7a', 'R7b') if k in v})}" + (" (slope-sensitive)" if r in sens else ""))
    L += ["", "| cell | S, W | ±95% | frozen S [lo, hi] | inside | cycles/op | rate, Gop/s | pJ/op (S) | die rise, °C |", "|---|---|---|---|---|---|---|---|---|"]
    for n in sorted(E["items"]):
        e = E["items"][n]
        s = e["S"]
        f = reg["cells"].get(n)
        ins = "" if not f or s["mean"] is None else ("yes" if f["S_lo_w"] <= s["mean"] <= f["S_hi_w"] else "NO")
        fs = "" if not f else f"{f['S_w']} [{f['S_lo_w']}, {f['S_hi_w']}]"
        L.append(f"| {n} | {rnd(s['mean'], 3)} | {rnd(s['ci95'], 3)} | {fs} | {ins} | {rnd(e.get('cycles_per_op'), 2)} | {rnd((e['rate']['mean'] or 0) / 1e9, 4)} | {rnd(e['pj_op_S']['mean'], 0)} | {rnd(e['dT_win']['mean'], 2)} |")
    open(a.md, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:len(V) + 2]))


if __name__ == "__main__":
    main()
