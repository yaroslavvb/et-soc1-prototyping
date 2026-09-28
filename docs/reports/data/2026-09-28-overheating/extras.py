#!/usr/bin/env python3
"""Descriptive numbers beside the registered OH verdicts (no verdicts here): written to reductions/extras.json.

  python3 docs/reports/data/2026-09-28-overheating/extras.py

1. near_65: every successful 1 s window of the OH blocks (OH-1 and OH-2, verdict blocks only) whose mean read 64, 65 or
   66 C (the governor's `mean > 65` point): the hottest sensor, per card and mean. OH-1's own descriptive set is empty
   (its preheat stops at 62 C), so this is where the governor's point is seen.
2. warm_vs_rest: OH2-b's statistic on the hottest band card 1 reached (die mean 70-80 C, it plateaued at 76) against its
   rest band B0, for every kernel metric (the registered OH2-b needs 80-85 C: INSUFFICIENT on card 1).
3. window_gap_by_load: dhot per whole-degree band of the mean for windows inside a whole-chip heater launch, inside a
   single-shire or 2x2 launch (OH-1), and with no launch within 3 s, per card.
4. totals: checked launches and wrong results across every OH block, aborted attempts included; card time per block.
Uses tools/claims-v3/oh/reduce.py's loaders, so a window, a launch's temperature and a check mean exactly what they mean
in the verdicts.
"""
import collections
import glob
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "oh"))
import ohlib  # noqa: E402
import reduce as R  # noqa: E402

dirs = sorted(d for d in glob.glob(os.path.join(HERE, "raw", "*", "oh", "p[0-9]*")) if os.path.isdir(d))
blocks = [R.Block(d) for d in dirs]
main = [b for b in blocks if (b.info or {}).get("status") == "ok"]
out = {"blocks": [os.path.relpath(b.d, HERE) + " (%s)" % (b.info or {}).get("status") for b in blocks]}


def dist(v):
    c = collections.Counter(v)
    return {str(k): c[k] for k in sorted(c)}


# 1. near 65
near = collections.defaultdict(list)
for B in main:
    for run in B.runs():
        for w in ohlib.windows(B.tel(run), 1000):
            if w["ok"] and w["max_mean"] in (64, 65, 66) and w["max_high"] is not None:
                near[(B.card, w["max_mean"])].append(w["max_high"])
out["near_65"] = {"%s mean %d" % k: {"n": len(v), "hottest_dist": dist(v), "hottest_median": st.median(v)}
                  for k, v in sorted(near.items())}

# 2. card 1's warm band against rest (descriptive OH2-b)
res = {}
for B in main:
    if B.kind != "OH2":
        continue
    tel = B.all_tel()
    warm, rest = collections.defaultdict(list), collections.defaultdict(list)
    for L in B.launches:
        if L["kind"] != "check" or L["tool"] == "MEMPROBE":
            continue
        s, n, why = B.status(L)
        if s == "BAD":
            continue
        T = R.hottest_mean(tel, L["t_start_ms"], L["t_end_ms"])
        x = {"name": L["name"], "tool": L["tool"], "recs": B.records(L)}
        for r in x["recs"]:
            k, v = None, None
            if L["tool"] == "SPARSITY" and r.get("test") == "fma":
                k, v = "%s sp=%.4f" % (L["name"], r.get("sparsity", 0)), r.get("cycles_per_op")
            elif L["tool"] == "SPARSITY" and r.get("test") == "gemv":
                k, v = "%s sp=%.4f" % (L["name"], r.get("sparsity", 0)), r.get("cycles_per_layer_max")
            elif L["tool"] in ("MMB",) or (L["tool"] == "ONCHIP" and r.get("test") == "relay"):
                k, v = L["name"], r.get("cycles_max")
            if k is None or v is None:
                continue
            if L.get("band") == "B0" and L.get("role") == "battery":
                rest[k].append(v)
            if T is not None and 70 <= T < 80:
                warm[k].append(v)
    items = {}
    for k in sorted(set(warm) & set(rest)):
        mh, mr = st.median(warm[k]), st.median(rest[k])
        items[k] = {"n_warm": len(warm[k]), "n_rest": len(rest[k]), "diff_pct": round((mh / mr - 1) * 100, 4),
                    "within_rest_range": min(rest[k]) <= mh <= max(rest[k])}
    diffs = [abs(v["diff_pct"]) for v in items.values()]
    res[B.card] = {"items": items, "max_abs_diff_pct": max(diffs) if diffs else None,
                   "n_metrics": len(items), "n_within_0p1pct": sum(1 for d in diffs if d <= 0.1)}
out["warm_vs_rest"] = res

# 3. the gap by load type
gap = collections.defaultdict(list)
for B in main:
    spans = []
    for L in B.launches:
        recs = B.records(L) if L["kind"] != "check" else []
        if recs:
            kind = "whole-chip heater" if L["kind"] == "heat" else ("one shire" if L["kind"] in ("cond-ONE-C", "cond-ONE-NE")
                                                                     else "2x2 block" if L["kind"] == "cond-B4C" else "other")
            spans.append((min(r["t_start_ms"] for r in recs), max(r["t_end_ms"] for r in recs), kind))
    allspans = sorted((L["t_start_ms"], L["t_end_ms"]) for L in B.launches)
    for run in B.runs():
        for w in ohlib.windows(B.tel(run), 1000):
            if not w["ok"] or w["max_high"] is None:
                continue
            k = next((kd for a, b, kd in spans if a <= w["t_start"] and w["t_end"] <= b), None)
            if k is None:
                if any(a - 3000 <= w["t_end"] and w["t_start"] <= b + 3000 for a, b in allspans):
                    continue
                k = "idle"
            band = "%d-%d" % (w["max_mean"] // 5 * 5, w["max_mean"] // 5 * 5 + 5)
            gap[(B.card, k, band)].append(w["max_high"] - w["max_mean"])
out["window_gap_by_load"] = {"%s | %s | %s" % k: {"n": len(v), "median": st.median(v), "max": max(v), "dist": dist(v)}
                             for k, v in sorted(gap.items())}

# 4. totals
tot = collections.defaultdict(collections.Counter)
card_time = []
for B in blocks:
    grp = "aborted" if (B.info or {}).get("status") == "aborted" else "verdict"
    for L in B.launches:
        if L["kind"] == "check" and L["tool"] != "MEMPROBE":
            s, n, why = B.status(L)
            c = tot[(B.card, grp)]
            c["checked_launches"] += s in ("OK", "PARTIAL", "BAD") and n > 0
            c["checked_records"] += n
            c["bad"] += s == "BAD"
            c["void"] += s == "NORESULT"
    if B.launches:
        t0 = min(L["t_start_ms"] for L in B.launches)
        t1 = max(L["t_end_ms"] for L in B.launches)
        xs = [ohlib.sample_fields(s) for s in B.all_tel()]
        card_time.append({"block": os.path.relpath(B.d, HERE), "status": (B.info or {}).get("status"),
                          "first_launch_ms": t0, "last_launch_end_ms": t1, "minutes": round((t1 - t0) / 60000.0, 1),
                          "launches": len(B.launches),
                          "mean_max": max((x[1] for x in xs if x[1] is not None), default=None),
                          "high_max": max((x[3] for x in xs if x[3] is not None), default=None),
                          "board_max_w": max((x[4] for x in xs if x[4] is not None), default=None)})
out["totals"] = {"%s %s" % k: dict(v) for k, v in sorted(tot.items())}
out["blocks_detail"] = card_time
g = []
for f in sorted(glob.glob(os.path.join(HERE, "raw", "aifoundry1-c1", "oh", "p*", "guard.jsonl.gz"))):
    for s in ohlib.load_jsonl(f):
        x = ohlib.sample_fields(s)
        if x[1] is not None:
            g.append(x[1])
out["card0_guard"] = {"samples": len(g), "mean_min": min(g) if g else None, "mean_max": max(g) if g else None}
json.dump(out, open(os.path.join(HERE, "reductions", "extras.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("near_65", "totals", "card0_guard")}, indent=1))
print(json.dumps({c: {k: v[k] for k in ("max_abs_diff_pct", "n_metrics", "n_within_0p1pct")} for c, v in out["warm_vs_rest"].items()}))
for k, v in out["window_gap_by_load"].items():
    print(k, v["n"], v["median"], v["max"], v["dist"])
for b in card_time:
    print(b)
