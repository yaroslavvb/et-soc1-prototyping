#!/usr/bin/env python3
"""E160 (Q139): POST HOC, never a verdict. Written at the desk on Tue 3 Nov 2026, about 16:20 PST, after the registered reduction (results.json), by
the lane that collected the data. Nothing here was registered; nothing frozen is changed or refitted. It reads results.json, the frozen predictions,
the collected sessions and E143's committed data dir.

    python3 docs/reports/data/2026-11-03-e160-blind6-aifoundry2/posthoc_more_e160.py > docs/reports/data/2026-11-03-e160-blind6-aifoundry2/posthoc-more.txt

  (M1) the governor's mid-burst idle status: how many bursts carry a service-processor POWER_IDLE status (power-status record, throttle state 0) before
       the work's end, E160 against E143 (E80's host, no C log), and the launch gaps inside those bursts
  (M2) this session against E143's (Mon 2 Nov, evening): the rest reading, the die at each burst's start, the byte-identical zeros anchors and E80's
       two replicate tiles
  (M3) what M8 leaves on this card: the board error on the tiles M8 puts at the cap, against the cap it was refitted to (65.20 W) and M7's (65.58 W);
       the pinned tiles' board error with the zeros level E143's corrections measured (-1.20 W, committed 2 Nov, before E160) added, and with this
       session's own zeros anchors as the level (an in-session anchor); the error against M8's predicted board W (offset or scale)
  (M4) F2 as registered, and with the two pinned passes that carry a mid-burst idle status set aside
  (M5) the one tile over M8's 95% peak: when its highest samples came
  (M6) int8's 32-bit wrap on silicon: how many int8 launches had a C word with |n x S| >= 2^31 at the launch's own n (S a word's exact sum over
       one op, ccheck.py's exact_terms), and their verdicts
  (M7) the die at the burst's start inside a session: the within-tile slope of the board W and of the burst clock on die_start (each tile's
       passes about its own mean, pooled; 95% from 4,000 draws over tiles, seeded), on the governed tiles (mean below 790 MHz) and on the tiles
       pinned at 800 MHz above 40 W, E160 and E143

SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "hpl"))
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "dv2"))
import sptrace_full as spf  # noqa: E402  (the trace ring's reader, read-only)

A2 = os.path.join(HERE, "aifoundry2")
E143 = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e143-blind5-aifoundry2")
R = json.load(open(os.path.join(HERE, "results.json")))
P = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e160", "predictions-e160.json")))
R143 = json.load(open(os.path.join(E143, "results.json")))
T = R["score"]["reported"]["tiles"]
out = {}


def jl(p):
    if not os.path.exists(p) and os.path.exists(p + ".gz"):
        p += ".gz"
    if not os.path.exists(p):
        return []
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as f:
        return [json.loads(x) for x in f if x.startswith("{")]


def rms(xs):
    xs = [x for x in xs if x is not None]
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else None


def r(x, n=3):
    return None if x is None else round(x, n)


# ---------------------------------------------------------------- (M1)
print("(M1) mid-burst idle statuses (the service processor's POWER_IDLE power-status record before the work's end)")


def idle_bursts(s1):
    rr = jl(os.path.join(s1, "runs.jsonl"))
    L = {x["run"]: x for x in jl(os.path.join(s1, "launches.jsonl")) if x.get("role") == "work"}
    prev = spf.scan(open(os.path.join(s1, "sp", "start.bin"), "rb").read())
    rows = []
    for x in rr:
        p = os.path.join(s1, "sp", x["run"] + ".bin")
        if not os.path.exists(p):
            continue
        cur = spf.scan(open(p, "rb").read())
        new = spf.since(prev, cur)
        prev = cur
        idle = [e for e in new if e["kind"] == "pstat" and e["throttle_state"] == 0]
        downs = sum(1 for e in new if e["kind"] == "power_down")
        sp = (L.get(x["run"]) or {}).get("sparsity") or []
        gaps = [b["t_start_ms"] - a["t_end_ms"] for a, b in zip(sp, sp[1:])]
        low = [s["launch"] for s in sp if s.get("launch", 0) >= 1 and s.get("ghz", 1) < 0.75]
        rows.append({"run": x["run"], "idle_statuses": len(idle), "power_downs": downs, "launch_gap_ms_max": max(gaps) if gaps else None,
                     "launches_below_750mhz": low})
    return rows


m1 = {}
for lab, s1 in (("E160", os.path.join(A2, "s1")), ("E143", os.path.join(E143, "aifoundry2", "s1"))):
    rows = idle_bursts(s1)
    multi = [x for x in rows if x["idle_statuses"] >= 2]
    m1[lab] = {"bursts": len(rows), "with_a_mid_burst_idle": len(multi), "which": multi}
    print(f"  {lab}: {len(rows)} bursts, {len(multi)} with a mid-burst idle status")
    for x in multi:
        print("    ", json.dumps(x))
out["M1_mid_burst_idle"] = m1

# ---------------------------------------------------------------- (M2)
print("\n(M2) this session against E143's (the evening before)")
ph143 = json.load(open(os.path.join(E143, "posthoc.json")))
ph160 = json.load(open(os.path.join(HERE, "posthoc.json")))


def die_starts(res):
    rows = [x for x in res["run_rows"] if x.get("die_start") is not None]
    gov = [x for x in rows if x["burst_mhz"] < 795]
    return {"all_mean_c": r(st.mean(x["die_start"] for x in rows), 2), "n": len(rows), "measured_governed_mean_c": r(st.mean(x["die_start"] for x in gov), 2),
            "measured_governed_die_max_mean_c": r(st.mean(x["die_max"] for x in gov), 2), "n_governed": len(gov)}


m2 = {"rest_reading": {"E160": ph160.get("rest"), "E143": ph143.get("rest")}, "die_at_burst_start": {"E160": die_starts(R), "E143": die_starts(R143)}}
T143 = R143["score"]["reported"]["tiles"]
z = {}
for ty in ("fp32", "fp16", "int8"):
    a, b = T[f"{ty}.anchor6_zeros"], T143[f"{ty}.anchor_zeros"]
    at800 = [w for w, f in zip(a["burst_w_runs"], a["burst_mhz_runs"]) if f >= 795]
    z[ty] = {"E160_w": a["burst_w"], "E160_w_runs": a["burst_w_runs"], "E160_mhz_runs": a["burst_mhz_runs"], "E160_w_at_800_passes": r(st.mean(at800), 3),
             "E143_w": b["burst_w"], "E160_minus_E143_w_at_800": r(st.mean(at800) - b["burst_w"], 3)}
m2["zeros_anchors_byte_identical"] = z
rep = {}
for k, t in R["replicate"]["tiles"].items():
    rep[k] = {"E160_mhz": t["burst_mhz"], "E143_mhz": t["e143_mhz"], "d_mhz": t["d_mhz_vs_e143"], "E160_w": t["burst_w"], "E143_w": t["e143_w"], "d_w": t["d_w_vs_e143"]}
m2["replicates_vs_E143"] = rep
out["M2_session_vs_E143"] = m2
for k, v in m2.items():
    print(f"  {k}: {json.dumps(v)}")

# ---------------------------------------------------------------- (M3)
print("\n(M3) what M8 leaves on this card")
W0, WSTAR = P["relation"]["W0_w"], 65.58008573814928   # M8's refitted cap; M7's (m8.json aifoundry2.M7_frozen.W_star_w)
capped = sorted(n for n, t in T.items() if t["group"] == "governed" and P["tiles"][n]["models"]["M8"]["burst_board_w"] >= W0 - 0.1)
cw = [T[n]["burst_w"] for n in capped]
m3 = {"capped_tiles": len(capped), "capped_measured_board_mean_w": r(st.mean(cw), 3), "capped_measured_board_range_w": [min(cw), max(cw)],
      "against_M8_cap_w": r(st.mean(cw) - W0, 3), "against_M7_cap_w": r(st.mean(cw) - WSTAR, 3),
      "capped_by_type_mean_w": {ty: r(st.mean(T[n]["burst_w"] for n in capped if P["tiles"][n]["type"] == ty), 3) for ty in ("fp32", "fp16")}}
pin = sorted(n for n, t in T.items() if t["group"] == "pinned")
e = {n: T[n]["burst_w"] - P["tiles"][n]["models"]["M8"]["burst_board_w"] for n in pin}
zl = -1.20   # E143 corrections C1 (docs/reports/data/2026-11-02-e143-blind5-aifoundry2/README.md), committed on 2 Nov before E160's registration
own = {ty: T[f"{ty}.anchor6_zeros"]["burst_w"] - P["tiles"][f"{ty}.anchor6_zeros"]["models"]["M8"]["burst_board_w"] for ty in ("fp32", "fp16", "int8")}
nz = [n for n in pin if not n.endswith("anchor6_zeros")]
m3["pinned"] = {"n": len(pin), "rms_w_as_frozen": r(rms(e.values())), "mean_w_as_frozen": r(st.mean(e.values())),
                "rms_w_with_E143_zeros_level": r(rms([v - zl for v in e.values()])), "mean_w_with_E143_zeros_level": r(st.mean([v - zl for v in e.values()])),
                "own_zeros_offset_w": {k: r(v) for k, v in own.items()},
                "nonzeros_n": len(nz), "nonzeros_rms_w_as_frozen": r(rms([e[n] for n in nz])),
                "nonzeros_rms_w_with_own_zeros_anchor": r(rms([e[n] - own[P["tiles"][n]["type"]] for n in nz])),
                "nonzeros_mean_w_with_own_zeros_anchor": r(st.mean([e[n] - own[P["tiles"][n]["type"]] for n in nz]))}
xs = [(P["tiles"][n]["models"]["M8"]["burst_board_w"], T[n]["burst_w"] - P["tiles"][n]["models"]["M8"]["burst_board_w"]) for n in nz]
mx, my = st.mean(x for x, _ in xs), st.mean(y for _, y in xs)
m3["pinned"]["nonzeros_error_slope_w_per_w"] = r(sum((x - mx) * (y - my) for x, y in xs) / sum((x - mx) ** 2 for x, _ in xs), 4)
out["M3_what_M8_leaves"] = m3
for k, v in m3.items():
    print(f"  {k}: {json.dumps(v)}")

# ---------------------------------------------------------------- (M4)
print("\n(M4) F2 with the two pinned passes that carry a mid-burst idle status set aside")
idle_runs = {x["run"] for x in m1["E160"]["which"]}
f2 = []
for n in pin:
    t = T[n]
    runs = [(f, p) for f, p in zip(t["burst_mhz_runs"], t["passes"])]
    kept = [f for f, p in runs if not any(x.endswith(f"-b6-{n}-r{p}") for x in idle_runs)]
    f2.append(st.mean(kept) - P["tiles"][n]["models"]["M8"]["burst_mhz"])
reg = R["score"]["rules"]["E160-F2"]
m4 = {"registered_rms_mhz": reg["rms"], "set_aside_runs": sorted(x for x in idle_runs if any(x.endswith(f"-b6-{n}-r{p}") for n in pin for p in (1, 2, 3))),
      "rms_mhz_with_them_set_aside": r(rms(f2)), "mean_mhz_with_them_set_aside": r(st.mean(f2))}
out["M4_F2_without_idle_passes"] = m4
print("  ", json.dumps(m4))

# ---------------------------------------------------------------- (M5)
print("\n(M5) the one tile over M8's 95% peak (fp32.b_onebit_b20_third): when each pass's highest samples came")
rows = jl(os.path.join(A2, "s1", "runs.jsonl"))
m5 = []
for x in rows:
    if x["label"] != "b6-fp32.b_onebit_b20_third":
        continue
    s = jl(os.path.join(A2, "s1", x["tel"]))
    t0 = x["t_first_ms"]
    top = sorted(((d["board_w"], round((d["t_ms"] - t0) / 1000, 1), d["mhz"]["minion"]) for d in s if d.get("board_w") is not None), reverse=True)[:3]
    work = [d["board_w"] for d in s if d.get("board_w") is not None and t0 + 1500 <= d["t_ms"] <= x["t_last_ms"]]
    m5.append({"run": x["run"], "highest_three_w_s_mhz": top, "burst_window_mean_w": r(st.mean(work), 2) if work else None})
out["M5_peak_miss"] = m5
for x in m5:
    print("  ", json.dumps(x))

# ---------------------------------------------------------------- (M6)
print("\n(M6) int8's 32-bit wrap: launches with a wrapped C word at their own n, and their verdicts")
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "ccheck"))
import ccheck as CC  # noqa: E402  (its exact_terms only)
V = json.load(gzip.open(os.path.join(HERE, "ccheck-s1.json.gz"), "rt"))["launches"]
terms, m6 = {}, {}
for v in V:
    if v["type"] != "int8":
        continue
    rel = v["values"][5:]
    if rel not in terms:
        terms[rel] = CC.exact_terms("int8", open(os.path.join(ROOT, rel), "rb").read())
    w = sum(abs(v["n"] * int(terms[rel][(i, j)][0])) >= (1 << 31) for i in range(16) for j in range(16))
    b = m6.setdefault(os.path.basename(rel), {"launches": 0, "with_a_wrapped_word": 0, "most_wrapped_words": 0, "PASS": 0, "wrapped_PASS": 0})
    b["launches"] += 1
    b["PASS"] += v["verdict"] == "PASS"
    if w:
        b["with_a_wrapped_word"] += 1
        b["most_wrapped_words"] = max(b["most_wrapped_words"], w)
        b["wrapped_PASS"] += v["verdict"] == "PASS"
tot = {"int8_launches": sum(b["launches"] for b in m6.values()), "with_a_wrapped_word": sum(b["with_a_wrapped_word"] for b in m6.values()),
       "tiles_with_a_wrapped_word": sum(1 for b in m6.values() if b["with_a_wrapped_word"]),
       "wrapped_launches_PASS": sum(b["wrapped_PASS"] for b in m6.values()),
       "all_int8_PASS": all(b["PASS"] == b["launches"] for b in m6.values())}
out["M6_int8_wrap"] = {"total": tot, "by_tile": m6}
print("  ", json.dumps(tot))
for k, b in sorted(m6.items()):
    print(f"    {k:32s} {json.dumps(b)}")

# ---------------------------------------------------------------- (M7)
print("\n(M7) within a session: the board W and the burst clock against the die reading at the burst's start")
import random  # noqa: E402


def within_slope(res, keep, key):
    by = {}
    for x in res["run_rows"]:
        if x.get("burst_mhz") is not None and x.get("die_start") is not None and x.get("complete", True):
            by.setdefault(x["label"], []).append(x)
    tiles = [v for v in by.values() if len(v) >= 2 and keep(v)]

    def fit(ts):
        sxx = sxy = 0.0
        for v in ts:
            mx, my = st.mean(q["die_start"] for q in v), st.mean(q[key] for q in v)
            for q in v:
                sxx += (q["die_start"] - mx) ** 2
                sxy += (q["die_start"] - mx) * (q[key] - my)
        return sxy / sxx if sxx else None
    rng = random.Random(1607)
    bs = sorted(b for b in (fit([tiles[rng.randrange(len(tiles))] for _ in tiles]) for _ in range(4000)) if b is not None)
    return {"tiles": len(tiles), "slope_per_c": r(fit(tiles), 3), "ci95": [r(bs[int(0.025 * len(bs))], 3), r(bs[int(0.975 * len(bs))], 3)]}


m7 = {}
for lab, res in (("E160", R), ("E143", R143)):
    gov = lambda v: st.mean(q["burst_mhz"] for q in v) < 790
    pin = lambda v: min(q["burst_mhz"] for q in v) >= 799 and st.mean(q["burst_w"] for q in v) > 40
    m7[lab] = {"governed_board_w": within_slope(res, gov, "burst_w"), "governed_clock_mhz": within_slope(res, gov, "burst_mhz"),
               "pinned_800_board_w": within_slope(res, pin, "burst_w")}
    print(f"  {lab}: {json.dumps(m7[lab])}")
out["M7_die_start_within_session"] = m7

json.dump(out, open(os.path.join(HERE, "posthoc-more.json"), "w"), indent=1)
