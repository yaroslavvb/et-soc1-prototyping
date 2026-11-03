#!/usr/bin/env python3
"""E159 POST HOC (labelled; written after the registered reduction, changes no verdict). Reads results.json (reduce_e159.py's) and the session's records.

    /usr/bin/python3 posthoc_e159.py > posthoc.txt      (writes posthoc.json)

  1. intervals: 95% bootstrap (10,000 resamples over the holds, seed 159) on each arm's rms, all nine and the registered subset; the paired gain, E136's
     law's rms minus G3's;
  2. by kind: fp32 random, int8 full, zeros; each arm's mean and rms error;
  3. the clock inside each hold's window: the share of in-kernel samples at 800 MHz, the mean of the rest, the lowest;
  4. P0's level: the first second at 800 MHz (p800, the scorer's) against P0(800), per hold; zeros beside E158's zeros bursts;
  5. the nominal frozen numbers (gate57) beside the measured and the registered primary (from each hold's own start);
  6. the session: the rest reading, the gates, the stop tests, card time, the device commands counted from the records.
"""
import gzip
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
RES = json.load(open(os.path.join(HERE, "results.json")))
A2 = os.path.join(HERE, "aifoundry2")
PRED = json.load(open(os.path.join(HERE, "../2026-11-03-q139q-gemm-g3/predictions-e159.json")))
ARMS = ("G3", "G3_q138t_constants", "E136_law", "chain_on_measured", "G3_given_p800")
Q = ("mhz", "w", "die")
SUBSET = PRED["design"]["registered_subset"]


def rms(v):
    return (sum(x * x for x in v) / len(v)) ** 0.5 if v else None


def jl(p):
    op = gzip.open if p.endswith(".gz") else open
    out = []
    with op(p, "rt") as f:
        for ln in f:
            if ln.startswith("{"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


rows = RES["rows"]
out = {"what": "E159 post hoc, labelled: after the registered reduction (results.json); no verdict changes"}

# 1. intervals
rng = random.Random(159)


def boot(rs, arm, q, n=10000):
    e = [x["err"][arm][q] for x in rs if arm in x["err"] and q in x["err"][arm]]
    if not e:
        return None
    vals = sorted(rms([e[rng.randrange(len(e))] for _ in e]) for _ in range(n))
    return [round(vals[int(0.025 * n)], 3), round(vals[int(0.975 * n)], 3)]


def boot_pair(rs, q, n=10000):
    idx = [i for i, x in enumerate(rs)]
    d = []
    for _ in range(n):
        s = [rs[idx[rng.randrange(len(idx))]] for _ in idx]
        d.append(rms([x["err"]["E136_law"][q] for x in s]) - rms([x["err"]["G3"][q] for x in s]))
    d.sort()
    return [round(d[int(0.025 * n)], 3), round(d[int(0.975 * n)], 3)]


iv = {}
print("1. INTERVALS (post hoc): 95% bootstrap over the holds (10,000 resamples, seed 159) on each arm's rms; measured - predicted")
for tag, rs in (("all9", rows), ("subset6", [x for x in rows if x["cell"] in SUBSET])):
    iv[tag] = {}
    for a in ARMS:
        for q in Q:
            e = [x["err"][a][q] for x in rs if a in x["err"] and q in x["err"][a]]
            if e:
                iv[tag][f"{a}.{q}"] = {"rms": round(rms(e), 3), "ci95": boot(rs, a, q), "n": len(e)}
    for q in Q:
        iv[tag][f"gain_E136_law_minus_G3.{q}"] = {"point": round(rms([x["err"]["E136_law"][q] for x in rs]) - rms([x["err"]["G3"][q] for x in rs]), 3), "ci95": boot_pair(rs, q)}
    print(f"  {tag}:")
    for k, v in iv[tag].items():
        print(f"    {k:34s} {v.get('rms', v.get('point')):8.3f}  [{v['ci95'][0]}, {v['ci95'][1]}]")
out["intervals"] = iv

# 2. by kind
print("\n2. BY KIND (post hoc): mean and rms of measured - predicted, per arm")
kinds = {"fp32 random": "fp32-randn", "int8 full": "int8-full", "zeros": "fp32-zeros"}
bk = {}
for name, suf in kinds.items():
    rs = [x for x in rows if x["cell"].endswith(suf)]
    bk[name] = {}
    line = []
    for a in ("G3", "E136_law", "chain_on_measured", "G3_given_p800"):
        for q in Q:
            e = [x["err"][a][q] for x in rs if a in x["err"] and q in x["err"][a]]
            if e:
                bk[name][f"{a}.{q}"] = {"mean": round(sum(e) / len(e), 3), "rms": round(rms(e), 3), "per_hold": [round(v, 3) for v in e]}
    print(f"  {name} ({[x['cell'] for x in rs]}):")
    for k, v in bk[name].items():
        print(f"    {k:28s} mean {v['mean']:+8.3f}  rms {v['rms']:7.3f}  per hold {v['per_hold']}")
out["by_kind"] = bk

# 3. the clock inside each window
print("\n3. THE CLOCK INSIDE EACH HOLD'S WINDOW (post hoc): in-kernel samples of the last 40 s (the scorer's window)")
s1 = os.path.join(A2, "s1")
runs = {r["run"]: r for r in jl(os.path.join(s1, "runs.jsonl"))}
L = jl(os.path.join(s1, "launches.jsonl.gz"))
clk = {}
for x in rows:
    r = runs[x["run"]]
    tel = jl(os.path.join(s1, "tel", x["run"] + ".jsonl.gz"))
    procs = [p for p in L if p["run"] == x["run"] and p.get("role") == "work"]
    kw = [(k["t_start_ms"], k["t_end_ms"]) for p in procs for k in p.get("sparsity", []) if k.get("t_start_ms") and k.get("t_end_ms")]
    t1 = max(p["t_end_ms"] for p in procs)
    w = [d for d in tel if any(a <= d["t_ms"] <= b for a, b in kw) and t1 - 40000 <= d["t_ms"] <= t1]
    f = [d["mhz"]["minion"] for d in w if (d.get("mhz") or {}).get("minion") is not None]
    at800 = sum(1 for v in f if v >= 800) / len(f)
    rest = [v for v in f if v < 800]
    clk[x["cell"]] = {"samples": len(f), "share_at_800": round(at800, 3), "mean_below_800": round(sum(rest) / len(rest), 1) if rest else None,
                      "lowest": min(f), "mean": round(sum(f) / len(f), 1), "levels": sorted({int(v) for v in f})}
    print(f"  {x['cell']:16s} {len(f):4d} samples: {100 * at800:5.1f}% at 800 MHz; mean {clk[x['cell']]['mean']:6.1f}; below 800: mean {clk[x['cell']]['mean_below_800']}, lowest {min(f)}; clock levels seen {clk[x['cell']]['levels'][:12]}")
out["clock_in_window"] = clk

# 3b. where the samples under 800 MHz fall: seconds since the hold's first process, and since the start of their own process
print("\n3b. WHERE THE SAMPLES UNDER 800 MHz FALL (post hoc): in-kernel samples of the whole hold; runs of consecutive samples under 800 MHz, their start since the hold's first process and since their own process's start")
dips = {}
for x in rows:
    tel = jl(os.path.join(s1, "tel", x["run"] + ".jsonl.gz"))
    procs = sorted([p for p in L if p["run"] == x["run"] and p.get("role") == "work"], key=lambda p: p["t_start_ms"])
    kw = [(k["t_start_ms"], k["t_end_ms"]) for p in procs for k in p.get("sparsity", []) if k.get("t_start_ms") and k.get("t_end_ms")]
    t0 = procs[0]["t_start_ms"]
    inside = [d for d in tel if any(a <= d["t_ms"] <= b for a, b in kw) and (d.get("mhz") or {}).get("minion") is not None]
    runs_, cur = [], None
    for d in inside:
        low = d["mhz"]["minion"] < 800
        if low and cur is None:
            cur = [d["t_ms"], d["t_ms"], 1, d["mhz"]["minion"]]
        elif low:
            cur[1], cur[2], cur[3] = d["t_ms"], cur[2] + 1, min(cur[3], d["mhz"]["minion"])
        elif cur is not None:
            runs_.append(cur)
            cur = None
    if cur is not None:
        runs_.append(cur)
    starts = [round((r[0] - t0) / 1000.0, 1) for r in runs_]
    inproc = []
    for r in runs_:
        p = max((p for p in procs if p["t_start_ms"] <= r[0]), key=lambda p: p["t_start_ms"], default=None)
        inproc.append(round((r[0] - p["t_start_ms"]) / 1000.0, 2) if p else None)
    gaps = [round(b - a, 1) for a, b in zip(starts, starts[1:])]
    dips[x["cell"]] = {"n_runs": len(runs_), "samples_low": sum(r[2] for r in runs_), "samples": len(inside), "start_s": starts, "since_own_process_s": inproc,
                       "gaps_s": gaps, "lowest": [r[3] for r in runs_]}
    print(f"  {x['cell']:16s} {len(runs_):3d} runs of low samples ({sum(r[2] for r in runs_)} of {len(inside)}); since the hold's start {starts[:14]}{' ...' if len(starts) > 14 else ''}; "
          f"since their own process's start {inproc[:14]}{' ...' if len(inproc) > 14 else ''}")
out["dips"] = dips

# 4. P0's level
print("\n4. P0'S LEVEL (post hoc): the first second at 800 MHz (p800, the scorer's) against P0(800); the registered attribution band is 4 W")
lev = {}
for x in rows:
    d = x["p800"] - x["P0_800"] if x["p800"] is not None else None
    lev[x["cell"]] = {"p800": round(x["p800"], 2) if x["p800"] else None, "P0_800": x["P0_800"], "diff": round(d, 2) if d is not None else None}
    print(f"  {x['cell']:16s} p800 {x['p800']:6.2f} W  P0(800) {x['P0_800']:6.2f} W  difference {d:+6.2f} W")
z = [lev[c]["diff"] for c in lev if c.endswith("zeros")]
print(f"  zeros: p800 - P0(800) {z} (E158's zeros bursts on other shapes: P0 high by 2.7-4.4 W, docs/reports/data/2026-11-03-e158-l3-retention/results.json rules.R7)")
out["P0_level"] = lev

# 5. nominal frozen numbers beside the measured
print("\n5. THE NOMINAL FROZEN NUMBERS (gate57, predictions-e159.txt) beside the measured and the registered primary (from each hold's own start)")
nom = {}
for x in rows:
    g57 = PRED["cells"][x["cell"]]["nominal"]["gate57"]["G3"]
    m, g = x["meas"], x["pred"]["G3"]
    nom[x["cell"]] = {"measured": {q: round(m[q], 2) for q in Q}, "primary": {q: round(g[q], 2) for q in Q}, "nominal_gate57": {"mhz": g57["mhz"], "w": g57["w"], "die": g57["die"]},
                      "die_start_measured": round(x["die_start"], 1), "nominal_die_start": g57["die_start"]}
    print(f"  {x['cell']:16s} measured {m['mhz']:6.1f} {m['w']:6.2f} {m['die']:6.2f} | primary {g['mhz']:6.1f} {g['w']:6.2f} {g['die']:6.2f} | nominal gate57 {g57['mhz']:6.1f} {g57['w']:6.2f} {g57['die']:6.2f} | die start {x['die_start']:.0f} C (nominal {g57['die_start']:.1f})")
out["nominal_vs_measured"] = nom

# 6. the session
print("\n6. THE SESSION (post hoc)")
q = jl(os.path.join(A2, "queue.jsonl"))
det = [x for x in q if x.get("kind") == "stoptest_detail"]
for d in det:
    print(f"  stop test {d['name']}: trip {d['trip_after_line_ms']} ms after the {'third live line over 30 W' if d['stop'] == 'board' else 'first live line at or above 30 C'}"
          + (f"; the launch ended {d['launch_end_after_trip_ms']} ms after the trip" if d["stop"] == "board" else "; before any launch"))
rest = jl(os.path.join(s1, "tel", "R-00-rest-r1.jsonl.gz"))
rw = [d["board_w"] for d in rest if d.get("board_w")]
rd = [d["temp_c"]["minshire"][0] for d in rest if (d.get("temp_c") or {}).get("minshire")]
print(f"  the session's rest reading (R, 30 s, no launch): {sum(rw) / len(rw):.2f} W, die {sum(rd) / len(rd):.2f} C ({len(rw)} samples)")
gates = {r["label"]: r.get("gate") for r in runs.values() if r.get("processes", 0) >= 2}
for k, g in gates.items():
    print(f"  gate {k:16s} held {g.get('held_s')} s, reading {g.get('reading')}")
n_samples, n_cfg, n_trace, n_res2 = 0, 0, 0, 0
for sess in ("smoke", "stoptest-board", "stoptest-die", "s1"):
    sd = os.path.join(A2, sess)
    for f in os.listdir(os.path.join(sd, "tel")):
        n_samples += len(jl(os.path.join(sd, "tel", f)))
    for r in (jl(os.path.join(sd, "runs.jsonl")) if os.path.exists(os.path.join(sd, "runs.jsonl")) else []):   # a stop test ends at its trip: no run recorded
        qq = r.get("queries") or {}
        n_cfg += 1 if qq.get("config_rc") == 0 else 0
        n_trace += 1 if qq.get("sptrace_rc") == 0 else 0
        n_res2 += 1 if qq.get("residency_rc") == 2 else 0
sess_q = sum(len(jl(os.path.join(A2, s, "queries.jsonl"))) for s in ("smoke", "stoptest-board", "stoptest-die", "s1") if os.path.exists(os.path.join(A2, s, "queries.jsonl")))
ct = RES["safety"]["card_time"]
print(f"  device commands counted: {n_samples} sampler samples (each GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE, "
      f"GET_ASIC_FREQUENCIES: all READ); ettelem config after {n_cfg} runs, plus {sess_q} session start/end query records and the queue's two snapshots; ettelem sptrace after {n_trace} runs "
      f"(MMIO copy); the residency rewrite answered rc 2 (not sent) {n_res2} times; no statistics reset, no firmware-revisions query, no set")
print(f"  card time: {ct['minutes']} min from the first card touch (snapshot-start, {ct['first_touch_ms']}) to the queue's end ({ct['card_free_ms']}); the session s1 "
      f"{RES['safety']['end'].get('s1', {}).get('card_min')} card-minutes")
print(f"  peaks: {RES['safety']['peaks']}; config read (TDP W, threshold C): {RES['safety']['config_read']}")
out["session"] = {"stoptests": det, "rest_w": round(sum(rw) / len(rw), 2), "rest_die_c": round(sum(rd) / len(rd), 2), "gates": gates,
                  "commands": {"sampler_samples": n_samples, "config_after_runs": n_cfg, "session_query_records": sess_q, "sptrace": n_trace, "residency_rc2": n_res2},
                  "card_time": ct, "peaks": RES["safety"]["peaks"]}
json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)
