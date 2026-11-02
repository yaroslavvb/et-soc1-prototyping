#!/usr/bin/env python3
"""E77, corrections after verification (Sun 1 Nov 2026, written at the desk after the run; no card touched).

Recomputes, from the committed files of this directory only, every number the README's and the change record's
corrections cite:

  A  the residency reads: raw states 2, 3 and 4 at each management burst, the state-4 error lines in the rings, the
     SP clock aligned to those lines, and the host kernel log's 22 SP Runtime Error events against the reads (F1)
  B  the return burst in the ring: the entries the RETURN dump holds beyond the SETTLE dump, on the PST clock (F3)
  C  the conduction bound: the frozen conversion R*(21/V_A)^2 beside the model's own total-current increment,
     R*[((m0 + 21)/V_A)^2 - (m0/V_A)^2], at the measured idle minion rail m0, for every fit (F2, F4)
  D  the post hoc per-hart ratio and operating-point step with passes as the unit, 99% intervals (F4)
  E  the launch readings against departure 3's registered 55-58 C (F5)

    python3 docs/reports/data/2026-11-01-e77-rail-one-temperature/corrections-check.py > \\
        docs/reports/data/2026-11-01-e77-rail-one-temperature/corrections-check.txt
"""
import datetime as dt
import gzip
import json
import math
import os
import re
import statistics as st
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
RAW = os.path.join(HERE, "raw")
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "hpl"))
import sptrace_full as sf  # noqa: E402  (E64 amendment A1: the whole ring, binary records included)

PST = dt.timezone(dt.timedelta(hours=-8))
PUBLISHED_MINION = 0.18789339920416637      # tools/claims-v3/e77/reduce_e77.py PUBLISHED["minion"]
ROW_PJ = 0.875                              # reduce_e77.py ROW_PJ
T995 = {2: 9.925}                           # t(0.995, 2): three passes


def pst(t_s):
    return dt.datetime.fromtimestamp(t_s, PST).strftime("%H:%M:%S.%f")[:-3]


def jl(path):
    return [json.loads(x) for x in open(path) if x.strip().startswith("{")]


def ci99(vals):
    m, sd = float(np.mean(vals)), float(np.std(vals, ddof=1))
    h = T995[len(vals) - 1] * sd / math.sqrt(len(vals))
    return m, m - h, m + h


print("E77 corrections-check: every number below is recomputed from this directory's committed files.\n")

# ---------------------------------------------------------------------------------------------------- A
print("== A. The residency reads, the state-4 error lines and the kernel events (F1)")
gates = json.load(open(os.path.join(RAW, "gates.json")))
smoke = json.load(open(os.path.join(RAW, "smoke", "smoke.json")))
bursts = [{"tag": "gates", "residency": gates["residency"], "dump": "sp/gates.bin"},
          {"tag": "smoke", "residency": smoke["queries"]["residency"], "dump": "smoke/sp/smoke.bin"}]
for q in jl(os.path.join(RAW, "queries.jsonl")):
    bursts.append({"tag": q["tag"], "residency": q["residency"], "dump": f"sp/{q['tag']}.bin"})
phase = {"gates": "gate reads", "smoke": "smoke", "start": "session start", "B1": "after arm B pass 1",
         "B2": "after arm B pass 2", "A1": "after arm A pass 1 (TDP 0)", "A2": "after arm A pass 2 (TDP 0)",
         "A3": "after arm A pass 3 (TDP 0)", "SETTLE": "before the restore (TDP 0)",
         "RETURN": "after the return burst", "B3": "after arm B pass 3"}
print("  At et-platform 836a4ab (BL2 0.22.0) the throttle states are IDLE 0, UP 1, DOWN 2, SAFE 3, and 4 is the")
print("  enum's UNKNOWN sentinel (device-api/include/management-api/device_mgmt_api_spec.h:280-285). The run read raw")
print("  2, 3 and 4 and labelled them POWER_UP, POWER_DOWN, THERMAL_DOWN, the 0.20.0/0.18.0 seven-state names.\n")
print("  burst   phase                         state-4 read (PST)  raw 2 = POWER_DOWN cum. s   raw 3 = POWER_SAFE cum. s   raw 4 rc")
prev2 = None
for b in bursts:
    r = {e["state"]: e for e in b["residency"]}
    b["t4"] = r[4]["t_ms"] / 1000.0
    c2 = r[2]["cumulative_us"] / 1e6
    grow = "" if prev2 is None else f" (+{c2 - prev2:.3f})"
    print(f"  {b['tag']:7s} {phase[b['tag']]:29s} {pst(b['t4'])}        {c2:12.3f}{grow:12s}      "
          f"{r[3]['cumulative_us'] / 1e6:8.3f}                  {r[4]['rc']}")
    prev2 = c2
print("\n  The rings (tools/claims-v3/hpl/sptrace_full.py): entries new in each dump since the one before, and its")
print("  state-4 error lines ('Unexpected power throtlling state: 4', 'thermal pwr mgmt error: get_throttle_time()').")
print("  A dump is taken before the burst's residency read (run_e77.py queries()), so its new error lines are the")
print("  previous burst's state-4 read.")
prev, pairs = None, []
for i, b in enumerate(bursts):
    cur = sf.scan(open(os.path.join(RAW, b["dump"]), "rb").read()) or []
    b["entries"] = cur
    new = sf.since(prev, cur) if prev is not None else cur
    noise = [e for e in new if e["kind"] == "query_noise"]
    s4 = [e for e in noise if "state: 4" in e["text"]]
    gtt = [e for e in noise if "get_throttle_time" in e["text"]]
    allnoise = sum(1 for e in cur if e["kind"] == "query_noise")
    line = f"  {b['tag']:7s} {len(cur):3d} entries, {len(new):3d} new; new error lines: {len(s4)} state-4 + {len(gtt)} get_throttle_time"
    if s4 and i > 0:
        sp_t = s4[0]["ts"] / 1e6
        pairs.append((bursts[i - 1]["tag"], bursts[i - 1]["t4"], sp_t))
        line += f" at SP {sp_t:.3f} s <- the {bursts[i - 1]['tag']} read"
    elif i > 0 and len(new) >= 60:
        line += " (the ring overwritten by the pass's governor entries)"
    line += f"; error lines in the whole dump {allnoise}"
    print(line)
    prev = cur
offs = [t4 - sp for _, t4, sp in pairs]
off = st.median(offs)
print(f"\n  SP clock aligned on those {len(pairs)} pairs: PST = SP + {off:.3f} s; residuals (ms): "
      + ", ".join(f"{tag} {1000 * (t4 - sp - off):+.1f}" for tag, t4, sp in pairs))
ev_txt = open(os.path.join(RAW, "kernel-events.txt")).read()
by_sec = [(m.group(1), int(m.group(2))) for m in re.finditer(r"(\d\d:\d\d:\d\d) (\d+)", ev_txt.split("By second", 1)[1])]
ev = [(dt.datetime(2026, 11, 1, int(h[:2]), int(h[3:5]), int(h[6:8]), tzinfo=PST).timestamp(), n) for h, n in by_sec]
print(f"\n  Host kernel log (raw/kernel-events.txt): {sum(n for _, n in ev)} SP Runtime Error events in {len(ev)} seconds; "
      f"{len(bursts)} state-4 reads.")
used = set()
for b in bursts:
    hit = [(t, n) for t, n in ev if 0 <= t - b["t4"] <= 10 and t not in used]
    if hit:
        t, n = hit[0]
        used.add(t)
        print(f"    {b['tag']:7s} read {pst(b['t4'])}: {n} events stamped {pst(t)[:8]}, {t - b['t4']:.1f}-{t + 1 - b['t4']:.1f} s later")
    else:
        print(f"    {b['tag']:7s} read {pst(b['t4'])}: no event within 10 s")
print(f"  Events not matched to a read: {sum(n for t, n in ev if t not in used)}")
print("  Source at 836a4ab: get_throttle_residency's default branch logs 'Unexpected power throtlling state: %d' at")
print("  LOG_LEVEL_ERROR (services/thermal_pwr_mgmt.c:1477-1501); the handler logs 'thermal pwr mgmt error:")
print("  get_throttle_time()' at LOG_LEVEL_ERROR (services/thermal_power_monitor.c:596-610); every ERROR line increments")
print("  RT_Error_Count and, past RT_ERROR_THRESHOLD, pushes one SP_RUNTIME_ERROR event to the host (services/log.c:371-389,")
print("  410-428). Two ERROR lines per state-4 read: two events per read.")

# ---------------------------------------------------------------------------------------------------- B
print("\n== B. The return burst in the ring (F3)")
by = {b["tag"]: b for b in bursts}
new = sf.since(by["SETTLE"]["entries"], by["RETURN"]["entries"])
gov = jl(os.path.join(RAW, "gov.jsonl"))
t_restore = [g for g in gov if g.get("event") == "set" and g["asked"]["tdp_w"] == 65][0]["sent"][0]["t_ms"] / 1000.0
ret = [x for x in jl(os.path.join(RAW, "launches.jsonl")) if x.get("role") == "return"][0]
print(f"  restore written {pst(t_restore)}; the return launch {pst(ret['t_start_ms'] / 1000)}-{pst(ret['t_end_ms'] / 1000)}")
print(f"  RETURN.bin holds {len(new)} entries newer than SETTLE.bin:")
for e in new:
    t = e["ts"] / 1e6 + off
    what = e.get("text") or f"power-status record: {e['mhz']} MHz, throttle state {e['throttle_state']}, {e['power_w']} W"
    print(f"    SP {e['ts'] / 1e6:.3f} s = {pst(t)} PST  {e['kind']:12s} {what}")
ups = [e for e in new if e["kind"] == "power_up"]
print(f"  Power throttle up lines after the restore: {len(ups)}"
      + (f", {(ups[1]['ts'] - ups[0]['ts']) / 1e6:.3f} s apart, {ups[0]['ts'] / 1e6 + off - ret['t_start_ms'] / 1000:.2f} s "
         f"and {ups[-1]['ts'] / 1e6 + off - ret['t_start_ms'] / 1000:.2f} s into the launch" if len(ups) == 2 else ""))
rq = [q for q in jl(os.path.join(RAW, "queries.jsonl")) if q["tag"] == "RETURN"][0]
print(f"  The runner's live count (every 'Throttle up' in the whole dump, stale ones included): {rq['throttle_up_lines']}")
mhz = {}
first = {}
for x in gzip.open(os.path.join(RAW, "tel", "RETURN.jsonl.gz"), "rt"):
    if not x.startswith("{"):
        continue
    try:
        d = json.loads(x)
    except ValueError:
        continue
    f = (d.get("mhz") or {}).get("minion")
    if f is None:
        continue
    mhz[int(f)] = mhz.get(int(f), 0) + 1
    first.setdefault(int(f), d["t_ms"] / 1000.0) if int(f) != 600 else None
print("  10 Hz telemetry (raw/tel/RETURN.jsonl.gz): " + ", ".join(f"{k} MHz {v}" for k, v in sorted(mhz.items()))
      + "; first 700 at " + pst(first.get(700, float("nan"))) + ", first 800 at " + pst(first.get(800, float("nan"))))

# ---------------------------------------------------------------------------------------------------- C
print("\n== C. The conduction bound: the frozen conversion beside the model's total-current increment (F2, F4)")
R = json.load(open(os.path.join(HERE, "results.json")))
P = json.load(open(os.path.join(HERE, "posthoc.json")))
rowsA = [r for r in R["rows"] if r.get("arm") == "A" and r.get("role") == "work" and r.get("kept")]
m0 = float(np.mean([r["minion_idle"] for r in rowsA]))
v0 = float(np.mean([r["mv_idle"] for r in rowsA])) / 1000
VA = R["moves"]["V_A"]
print(f"  arm A, {len(rowsA)} kept launches: idle minion rail m0 = {m0:.3f} W (range {min(r['minion_idle'] for r in rowsA):.3f}-"
      f"{max(r['minion_idle'] for r in rowsA):.3f}), idle {1000 * v0:.1f} mV; window V_A = {1000 * VA:.0f} mV "
      f"(results.json moves.V_A); I0 = {m0 / VA:.1f} A")
lit = (21.0 / VA) ** 2
tot = ((m0 + 21.0) / VA) ** 2 - (m0 / VA) ** 2
print(f"  per ohm at a 21 W rail delta: literal (21/V_A)^2 = {lit:.1f} A^2; total-current increment = {tot:.1f} A^2 "
      f"(x{tot / lit:.3f})")
pj = ROW_PJ / (PUBLISHED_MINION * 21.0)
print(f"  pJ of the row = W x 0.875 / (0.18789 x 21 W) = W x {pj:.5f}; the whole row is 0.18789 x 21 = "
      f"{PUBLISHED_MINION * 21:.3f} W\n")
fits = [("registered, drift_split (verdict)", R["moves"]["R_mean_mohm"], R["moves"]["R_ci99_mohm"]),
        ("secondary, published small rails", None, None),
        ("post hoc, arm-B offset", P["fit_offset"]["R_mean_mohm"], P["fit_offset"]["R_ci99_mohm"]),
        ("post hoc, offset + SRAM and NoC", P["fit_offset_plus_small_rails"]["R_mean_mohm"],
         P["fit_offset_plus_small_rails"]["R_ci99_mohm"])]
sec = R.get("secondary_fixed_small_rails", {})
sfit = sec.get("fit", sec)
if "R_ci99_ohm" in sfit:
    fits[1] = ("secondary, published small rails", 1000 * sfit["R_mean_ohm"], [1000 * x for x in sfit["R_ci99_ohm"]])
else:
    fits.pop(1)
print("  fit                                   R mOhm [99%]              at the upper edge: literal W / pJ   total-current W / pJ   share of row")
for name, rm, (lo, hi) in [(n, a, b) for n, a, b in fits]:
    wl, wt = hi / 1000 * lit, hi / 1000 * tot
    print(f"  {name:37s} {rm:6.3f} [{lo:+.3f}, {hi:+.3f}]   {wl:5.2f} W / {wl * pj:4.2f} pJ          "
          f"{wt:5.2f} W / {wt * pj:4.2f} pJ      {wt / (PUBLISHED_MINION * 21):.0%}")
rm = R["moves"]["R_mean_mohm"] / 1000
print(f"  registered point estimate {1000 * rm:.3f} mOhm: literal {rm * lit:.2f} W / {rm * lit * pj:.2f} pJ; "
      f"total-current {rm * tot:.2f} W / {rm * tot * pj:.2f} pJ")
print(f"  verdict: the registered 99% interval contains 0 -> FAIL (the frozen rule); the pooled rms gain "
      f"{R['footings']['drift_split']['fit'].get('rms_improvement', float('nan')):.1%} is reported beside it")

# ---------------------------------------------------------------------------------------------------- D
print("\n== D. Post hoc, passes as the unit (99%: mean +- t(0.995, 2) x SD/sqrt(3)) (F4)")
rmn = R["footings"]["drift_split"]["rung_means"]
H = {"A": {1: 1024, 2: 768, 3: 544, 4: 288}, "B": {1: 544, 2: 416, 3: 288, 4: 160}}
per = {}
for p in ("1", "2", "3"):
    out = {}
    for arm in "AB":
        xs, ys, ss = [], [], []
        for k, v in rmn.items():
            if k[0] == arm and k[1] == p:
                g = int(k.split("-g")[1])
                xs.append(H[arm][g]); ys.append(v["minion"]); ss.append(v["sram"])
        sl, ic = np.polyfit(xs, ys, 1)
        out[arm] = (1000 * sl, ic, float(np.mean(ss)))
    per[p] = {"ratio": out["B"][0] / out["A"][0], "step_minion_w": out["B"][1] - out["A"][1],
              "step_sram_w": out["B"][2] - out["A"][2], "A_mW_per_hart": out["A"][0], "B_mW_per_hart": out["B"][0]}
for key in ("A_mW_per_hart", "B_mW_per_hart", "ratio", "step_minion_w", "step_sram_w"):
    vals = [per[p][key] for p in ("1", "2", "3")]
    m, lo, hi = ci99(vals)
    print(f"  {key:14s} per pass {', '.join(f'{v:.3f}' for v in vals)}; mean {m:.3f}, 99% [{lo:.3f}, {hi:.3f}]")
print(f"  pooled (posthoc.json): ratio {P['per_hart_ratio_B_over_A']:.3f} against f*V^2 = {P['fV2_measured']:.3f} at the "
      f"measured {1000 * P['A']['V_mean']:.0f}/{1000 * P['B']['V_mean']:.0f} mV; step {P['op_step_minion_w']:.2f} W minion, "
      f"{P['op_step_sram_w']:.2f} W SRAM")

# ---------------------------------------------------------------------------------------------------- E
print("\n== E. Launch readings against departure 3's registered 55-58 C (F5)")
for arm in "AB":
    rr = [r for r in R["rows"] if r.get("arm") == arm and r.get("role") == "work" and r.get("kept")]
    cnt = {}
    for r in rr:
        cnt[r["T_launch"]] = cnt.get(r["T_launch"], 0) + 1
    print(f"  arm {arm}: {len(rr)} kept launches, readings " + ", ".join(f"{k:g} C x{v}" for k, v in sorted(cnt.items()))
          + f"; mean {np.mean([r['T_launch'] for r in rr]):.2f} C; in 55-58 C: {sum(1 for r in rr if 55 <= r['T_launch'] <= 58)}"
          + f"; flagged below_floor: {sum(1 for r in rr if r['gate'].get('below_floor'))}")
print(f"  results.json launch_readings: {json.dumps(R['launch_readings'])}")
