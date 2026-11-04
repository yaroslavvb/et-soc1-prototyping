#!/usr/bin/env python3
"""E160 (Q139): POST HOC, never a verdict. Reads the collected sessions (aifoundry2/) and results.json; changes nothing frozen. E143's posthoc_e143.py
with E160's names and four additions (6-9).

    python3 docs/reports/data/2026-11-03-e160-blind6-aifoundry2/posthoc_e160.py > docs/reports/data/2026-11-03-e160-blind6-aifoundry2/posthoc.txt

  (1) the rest reading, the card time, and how many device commands of each kind the records show
  (2) the stop-path tests and the smoke's checks, from the queue's records
  (3) the sampled clock against the kernel's own clock (cycles over wall time from 1.5 s on), per tile
  (4) the passes: how far each tile's clock and board W moved between passes
  (5) the config read at the queue's start and end
  (6) the C log's cost: launch gaps and device-held times in the session, against E143's (E80's host, no C log)
  (7) the residency queries (every one refused at the argument check, rc 2) and the idle-login decisions (counts only)
  (8) the peaks: every burst's highest board sample against M8's expected and 95% peak, the highest ten
  (9) the burst D's error by format against M8, and the board error against M8's predicted board W (offset or scale)
"""
import glob
import gzip
import json
import math
import os
import re
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
A2 = os.path.join(HERE, "aifoundry2")
R = json.load(open(os.path.join(HERE, "results.json")))
P = json.load(open(os.path.join(ROOT, "tools/claims-v3/e160/predictions-e160.json")))
out = {}


def jl(p):
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as f:
        return [json.loads(x) for x in f if x.startswith("{")]


print("(1) the rest reading, card time, commands")
rest = None
for L in glob.glob(os.path.join(A2, "smoke/tel/*rest*.jsonl*")):
    rows = jl(L)
    ws = [r["board_w"] for r in rows if r.get("board_w") is not None][-300:]
    dies = [r["temp_c"]["minshire"][0] for r in rows if (r.get("temp_c") or {}).get("minshire")][-300:]
    if ws:
        rest = {"board_w": round(sum(ws) / len(ws), 2), "die_c": round(sum(dies) / len(dies), 2), "n": len(ws)}
print("  the smoke's rest reading (last 30 s):", rest)
q = [json.loads(x) for x in open(os.path.join(A2, "queue.jsonl"))]
qs = next(x for x in q if x["kind"] == "queue_start")["t_ms"]
qe = max(x["t_ms"] for x in q)
t0 = min(x["t_ms"] for x in q if x["kind"] == "session_start")
t1 = max(x["t_ms"] for x in q if x["kind"] == "session_end")
tel = sum(len(jl(p)) for p in glob.glob(os.path.join(A2, "*/tel/*.jsonl*")))
nruns = sum(1 for p in glob.glob(os.path.join(A2, "*/runs.jsonl")) for _ in open(p))
nq = sum(1 for p in glob.glob(os.path.join(A2, "*/queries.jsonl")) for _ in open(p))
print(f"  card time, the queue's start (its first config read) to its end: {(qe - qs) / 60000:.2f} min; first session start to last session end: "
      f"{(t1 - t0) / 60000:.2f} min; sampler lines {tel}; runs with an after-run config read {nruns}; session start/end query records {nq}; queue snapshots 2")
out.update({"rest": rest, "card_min_queue": round((qe - qs) / 60000, 2), "card_min_sessions": round((t1 - t0) / 60000, 2), "sampler_lines": tel,
            "runs_incl_smoke_and_tests": nruns, "session_queries": nq, "queue_start_ms": qs, "queue_end_ms": qe})

print("\n(2) the smoke's checks and the stop-path tests (the queue's records)")
for x in q:
    if x["kind"] in ("smoke_check", "stoptest_detail", "stoptest_check", "queue_halt"):
        print("  ", json.dumps(x)[:500])
out["stoptests"] = [x for x in q if x["kind"] in ("smoke_check", "stoptest_detail", "stoptest_check")]

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

print("\n(6) the C log's cost: launch gaps and device-held times, the session against E143's")
def gaps_held(paths):
    gaps, held, nl, bud = [], [], [], 0
    for p in paths:
        for L in jl(p):
            if L.get("role") != "work":
                continue
            sp = L.get("sparsity") or []
            nl.append(len([s for s in sp if s.get("launch", 0) >= 0]))
            gaps += [b["t_start_ms"] - a["t_end_ms"] for a, b in zip(sp, sp[1:])]
            m = re.search(r"device held for ([0-9.]+) s", L.get("stderr_tail") or "")
            if m:
                held.append(float(m.group(1)))
            bud += "device-time budget" in (L.get("stderr_tail") or "")
    return {"procs": len(nl), "gap_ms_median": st.median(gaps) if gaps else None, "gap_ms_max": max(gaps) if gaps else None,
            "launches_median": st.median(nl) if nl else None, "launches_min": min(nl) if nl else None, "launches_max": max(nl) if nl else None,
            "held_s_median": st.median(held) if held else None, "held_s_max": max(held) if held else None, "budget_stops": bud}
g160 = gaps_held(glob.glob(os.path.join(A2, "s1", "launches.jsonl*")))
g143 = gaps_held(glob.glob(os.path.join(ROOT, "docs/reports/data/2026-11-02-e143-blind5-aifoundry2/aifoundry2/s1/launches.jsonl*")))
print("  E160 s1 (the C-logging host):", json.dumps(g160))
print("  E143 s1 (E80's host):       ", json.dumps(g143))
out["dma"] = {"e160_s1": g160, "e143_s1": g143}

print("\n(7) the residency queries and the idle-login decisions")
rc = {}
for p in glob.glob(os.path.join(A2, "*", "runs.jsonl")):
    for ln in open(p):
        r = json.loads(ln)
        k = (r.get("queries") or {}).get("residency_rc")
        rc[str(k)] = rc.get(str(k), 0) + 1
print("  residency_rc after each run:", rc)
out["residency_rc"] = rc
il = os.path.join(A2, "idle_logins.jsonl")
if os.path.exists(il):
    rows = [json.loads(x) for x in open(il)]
    others = sum(1 for r in rows if (r.get("others") or r.get("n_others") or r.get("count") or 0))
    print(f"  idle-login decisions {len(rows)}; with another user counted {others} (counts only)")
    out["idle_login_decisions"] = {"n": len(rows), "with_other": others}

print("\n(8) the peaks: each burst's highest board sample against M8's expected / 95% peak (the ten highest)")
rows = []
for r in R["run_rows"]:
    lab = r["label"]
    n = lab[3:] if lab.startswith("b6-") else None
    if n in P["tiles"] and r.get("peak_w") is not None:
        m = P["tiles"][n]["models"]["M8"]
        rows.append((r["peak_w"], r["run"], m["peak_board_w"], m["peak_board_hi95_w"], r.get("p800_w")))
rows.sort(reverse=True)
for pk, run, ex, hi, p8 in rows[:10]:
    print(f"  {run:48s} peak {pk:6.2f} W  M8 {ex:6.2f} / {hi:6.2f} W  first second {p8}")
over82 = [x for x in rows if x[0] >= 82.0]
print(f"  bursts at or over 82 W: {len(over82)}; at or over 85 W: {sum(1 for x in rows if x[0] >= 85.0)}")
out["peaks_top"] = [{"run": r, "peak_w": p, "M8_peak_w": e, "M8_hi95_w": h, "p800_w": f} for p, r, e, h, f in rows[:10]]

print("\n(9) the errors' shape: burst D by format, and the board error against M8's predicted board W")
T = R["score"]["reported"]["tiles"] if "rules" in R["score"] else {}
for ty in ("fp32", "fp16", "int8"):
    e = [t["D_w"] - t["M8_D"] for n, t in T.items() if P["tiles"][n]["type"] == ty and t.get("D_w") is not None and not n.endswith("anchor6_zeros")]
    if e:
        print(f"  {ty}: burst D measured - M8 over {len(e)} tiles: mean {st.mean(e):+.3f} W, rms {math.sqrt(sum(x * x for x in e) / len(e)):.3f} W")
xs = [(t["M8_w"], t["burst_w"] - t["M8_w"]) for t in T.values()]
if len(xs) >= 3:
    mx = st.mean(x for x, _ in xs)
    my = st.mean(y for _, y in xs)
    sxx = sum((x - mx) ** 2 for x, _ in xs)
    b = sum((x - mx) * (y - my) for x, y in xs) / sxx
    print(f"  board error against M8's board W over {len(xs)} tiles: slope {b:+.4f} W per W, mean {my:+.3f} W")
    out["board_err_slope"] = round(b, 4)
z = {n: t["burst_w"] - t["M8_w"] for n, t in T.items() if n.endswith("anchor6_zeros")}
print("  zeros anchors, board measured - M8:", {k: round(v, 3) for k, v in z.items()})
out["zeros_board_err"] = {k: round(v, 3) for k, v in z.items()}

json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)
