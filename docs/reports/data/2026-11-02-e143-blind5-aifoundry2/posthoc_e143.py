#!/usr/bin/env python3
"""E143 (Q138): POST HOC, never a verdict. Reads the collected sessions (aifoundry2/) and results.json; changes nothing frozen.

    python3 docs/reports/data/2026-11-02-e143-blind5-aifoundry2/posthoc_e143.py > docs/reports/data/2026-11-02-e143-blind5-aifoundry2/posthoc.txt

  (1) the rest reading, the card time, and how many device commands of each kind the records show (E146's posthoc section 5)
  (2) the stop-path tests, from the queue's records
  (3) the sampled clock against the kernel's own clock (cycles over wall time from 1.5 s on), per tile
  (4) the passes: how far each tile's clock and board W moved between passes
  (5) the config read at the queue's start and end
"""
import glob
import gzip
import json
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
A2 = os.path.join(HERE, "aifoundry2")
R = json.load(open(os.path.join(HERE, "results.json")))
out = {}

print("(1) the rest reading, card time, commands")
rest = None
for L in glob.glob(os.path.join(A2, "smoke/tel/*rest*.jsonl*")):
    op = gzip.open if L.endswith(".gz") else open
    rows = [json.loads(x) for x in op(L, "rt") if x.startswith("{")]
    ws = [r["board_w"] for r in rows if r.get("board_w") is not None][-300:]
    dies = [r["temp_c"]["minshire"][0] for r in rows if (r.get("temp_c") or {}).get("minshire")][-300:]
    if ws:
        rest = {"board_w": round(sum(ws) / len(ws), 2), "die_c": round(sum(dies) / len(dies), 2), "n": len(ws)}
print("  the smoke's rest reading (last 30 s):", rest)
q = [json.loads(x) for x in open(os.path.join(A2, "queue.jsonl"))]
t0 = min(x["t_ms"] for x in q if x["kind"] == "session_start")
t1 = max(x["t_ms"] for x in q if x["kind"] == "session_end")
tel = 0
for p in glob.glob(os.path.join(A2, "*/tel/*.jsonl*")):
    op = gzip.open if p.endswith(".gz") else open
    tel += sum(1 for x in op(p, "rt") if x.startswith("{"))
nruns = sum(1 for p in glob.glob(os.path.join(A2, "*/runs.jsonl")) for _ in open(p))
nq = sum(1 for p in glob.glob(os.path.join(A2, "*/queries.jsonl")) for _ in open(p))
print(f"  card time, first session start to last session end: {(t1 - t0) / 60000:.2f} min; sampler lines {tel}; runs with an after-run config read {nruns}; "
      f"session start/end query records {nq}; queue snapshots 2")
out.update({"rest": rest, "card_min_sessions": round((t1 - t0) / 60000, 2), "sampler_lines": tel, "runs_incl_smoke_and_tests": nruns, "session_queries": nq,
            "first_session_start_ms": t0, "last_session_end_ms": t1})

print("\n(2) the stop-path tests (the queue's records)")
for x in q:
    if x["kind"] in ("stoptest_detail", "stoptest_check", "smoke_check", "queue_halt"):
        print("  ", json.dumps(x)[:400])
out["stoptests"] = [x for x in q if x["kind"] in ("stoptest_detail", "stoptest_check")]

print("\n(3) the sampled clock against the kernel's own clock (MHz), per tile, mean over passes")
d = []
for lab, c in sorted(R["cells"].items()):
    if c.get("kernel_mhz") is None or c.get("burst_mhz") is None:
        continue
    d.append(c["kernel_mhz"] - c["burst_mhz"])
    print(f"  {lab:36s} sampled {c['burst_mhz']:7.2f}  kernel {c['kernel_mhz']:7.1f}  diff {c['kernel_mhz'] - c['burst_mhz']:+6.1f}")
if d:
    print(f"  kernel - sampled over {len(d)} cells: mean {st.mean(d):+.2f} MHz, rms {math.sqrt(sum(x * x for x in d) / len(d)):.2f}")
    out["kernel_minus_sampled_mhz"] = {"n": len(d), "mean": round(st.mean(d), 2), "rms": round(math.sqrt(sum(x * x for x in d) / len(d)), 2)}

print("\n(4) the passes: the spread of a tile's clock and board W between its passes (max - min)")
sm, sw = [], []
for lab, c in sorted(R["cells"].items()):
    if c["n"] >= 2:
        sm.append(max(c["burst_mhz_runs"]) - min(c["burst_mhz_runs"]))
        sw.append(max(c["burst_w_runs"]) - min(c["burst_w_runs"]))
if sm:
    print(f"  {len(sm)} cells: clock spread median {st.median(sm):.1f} MHz, max {max(sm):.1f}; board spread median {st.median(sw):.2f} W, max {max(sw):.2f}")
    out["pass_spread"] = {"n": len(sm), "mhz_median": round(st.median(sm), 2), "mhz_max": round(max(sm), 2), "w_median": round(st.median(sw), 3), "w_max": round(max(sw), 3)}
    big = sorted(((max(c["burst_mhz_runs"]) - min(c["burst_mhz_runs"]), lab, c["burst_mhz_runs"]) for lab, c in R["cells"].items() if c["n"] >= 2), reverse=True)[:6]
    for s, lab, runs in big:
        print(f"    {lab:36s} {s:6.1f} MHz  {runs}")

print("\n(5) the config at the queue's start and end")
for tag in ("start", "end"):
    p = os.path.join(A2, f"config-{tag}.txt")
    if os.path.exists(p):
        txt = open(p).read().strip().splitlines()
        print(f"  {tag}: {txt[-1][:300] if txt else ''}")
        out[f"config_{tag}"] = txt[-1] if txt else None

json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)
