#!/usr/bin/env python3
"""E190's reducer (Q169, the kit, Fri 13 Nov 2026, before any E190 datum): each arm's session directory into THE DATA the frozen scorer
reads (score_e190.py's docstring; E190.md section 6), and a table. Python's own modules only; run at the desk at the collection, on the
copied-back sessions; it changes nothing it reads.

    /usr/bin/python3 -I -B tools/claims-v3/e190/reduce_e190.py [--arm A=<session dir>] [--arm B=<session dir>] --out data-e190.json
        [--txt reduce-e190.txt]

PER RUN (a run that started a process; the registration's words, each choice the kit makes marked "kit"):
  counted launches   the run's fma launches with launch >= 0, ok, wall_s >= 0.1 s (kit: E119's clock_x floor), passes >= 1, and a kernel
                     clock (cycles_max / wall_s) at or above 790 MHz (arm A) or in 590-610 MHz (arm B); a sustained run's, inside its last
                     40 s (the launch's start and end inside [the work's end - 40 s, the work's end]; the work's end is the last process's)
  t_gemm_s, n_gemm   sum of wall_s / sum of passes over the counted launches; the sum of passes
  p_work_w           the median board W of the 10 Hz samples whose t_ms falls inside a counted launch [t_start_ms, t_end_ms]
  p_rest_w           the median board W of the samples in the last 5 s before the run's first process (its 10 s rest read's second half)
  die_start_c        the mean of the shires' mean over those same samples (kit: "the shires' mean then", read as their mean)
  die_c              a burst: the highest shires' mean in the work window (the first process's start to the last's end); a sustained run:
                     the mean of the shires' mean over its last 40 s
  mhz, mhz_min       the mean and the lowest minion clock of the samples inside the counted launches
  checks             every check of C the run's processes printed (exact / approx / wrong); a process with none is counted in
                     checks_missing (kit), never written as a check
THE SMOKE: every check of C of its three processes, and each format's cycles an op from its check record (the host's last launch's mean
cycles over its ops, as E146's queue read it). ARM A's x600 (E119's clock_x): each format's mean time an op of every counted-form launch
(the clock filter aside) at 590-610 MHz and at or above 790 MHz, and their counts. A run with no counted launch keeps t_gemm_s null with
its reason (the scorer skips it: NO DATA if no run of its cell has one). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e190_common as C  # noqa: E402


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def load_tel(sd):
    p = os.path.join(sd, "telemetry.jsonl.gz")
    out = []
    if not os.path.exists(p):
        return out
    with gzip.open(p, "rt") as f:
        for ln in f:
            if not ln.startswith("{"):
                continue
            try:
                s = json.loads(ln)
            except ValueError:
                continue
            ms = (s.get("temp_c") or {}).get("minshire") or [None]
            out.append((s.get("t_ms"), s.get("board_w"), ms[0], (s.get("mhz") or {}).get("minion")))
    return [x for x in out if x[0] is not None]


def proc_lines(d, name):
    p = os.path.join(d, name)
    return C.parse_sparsity(open(p).read()) if os.path.exists(p) else []


def reduce_run(d, rec, tel, arm):
    procs = rec.get("procs") or []
    launches, checks, missing = [], [], 0
    for p in procs:
        sp = proc_lines(d, p["name"] + ".out")
        launches += [x for x in sp if x.get("test") == "fma"]
        ch = [x.get("result") for x in sp if x.get("test") == "check"]
        checks += ch
        missing += 0 if ch else 1
    w0, w1 = (rec.get("work") or {}).get("t0_ms"), (rec.get("work") or {}).get("t1_ms")
    if procs:
        w0, w1 = procs[0]["t0_ms"], procs[-1]["t1_ms"]
    cnt = [L for L in launches if C.counted(L, arm)]
    if rec["kind"] == "sus" and w1 is not None:
        lo = w1 - C.SUS_WINDOW_S * 1000
        cnt = [L for L in cnt if L["t_start_ms"] >= lo and L["t_end_ms"] <= w1]
    out = {"run": rec["run"], "rep": rec["rep"], "n_procs": len(procs), "rcs": [p["rc"] for p in procs], "n_launch": len(launches),
           "n_launch_counted": len(cnt), "flags": rec.get("flags", []), "checks": checks, "checks_missing": missing}
    if procs:
        t_first = procs[0]["t0_ms"]
        rest = [x for x in tel if t_first - C.REST_WINDOW_S * 1000 <= x[0] < t_first]
        out["p_rest_w"] = statistics.median([x[1] for x in rest if x[1] is not None]) if any(x[1] is not None for x in rest) else None
        out["die_start_c"] = mean([x[2] for x in rest])
        out["n_rest_samples"] = len(rest)
        work = [x for x in tel if w0 <= x[0] <= w1]
        if rec["kind"] == "burst":
            out["die_c"] = max([x[2] for x in work if x[2] is not None], default=None)
        else:
            out["die_c"] = mean([x[2] for x in work if x[0] >= w1 - C.SUS_WINDOW_S * 1000])
    if not cnt:
        out.update({"t_gemm_s": None, "n_gemm": 0, "p_work_w": None, "mhz": None, "mhz_min": None,
                    "why": "no counted launch (none in the arm's clock band, or none ok)" if launches else "no launch"})
        return out
    out["t_gemm_s"] = sum(L["wall_s"] for L in cnt) / sum(L["passes"] for L in cnt)
    out["n_gemm"] = sum(L["passes"] for L in cnt)
    inside = [x for x in tel if any(L["t_start_ms"] <= x[0] <= L["t_end_ms"] for L in cnt)]
    bw = [x[1] for x in inside if x[1] is not None]
    mz = [x[3] for x in inside if x[3] is not None]
    out["p_work_w"] = statistics.median(bw) if bw else None
    out["n_work_samples"] = len(bw)
    out["mhz"] = mean(mz)
    out["mhz_min"] = min(mz) if mz else None
    out["kclock_mhz"] = mean([C.kclock(L) for L in cnt])
    return out


def x600(all_launches):
    """E119's clock_x on arm A's launches of one format: (T an op in us, f MHz) of every launch with launch >= 0, ok, wall_s >= 0.1."""
    rows = []
    for L in all_launches:
        if L.get("test") == "fma" and (L.get("launch") or 0) >= 0 and L.get("ok") and (L.get("wall_s") or 0) >= 0.1 and L.get("iters"):
            rows.append((C.kclock(L), L["wall_s"] / L["iters"] * 1e6))
    lo = [T for f, T in rows if f is not None and 590 <= f <= 610]
    hi = [T for f, T in rows if f is not None and f >= 790]
    return {"T600_us": mean(lo), "n600": len(lo), "T800_us": mean(hi), "n800": len(hi)}


def reduce_arm(sd, arm):
    tel = load_tel(sd)
    arm_out = {"session": os.path.basename(os.path.normpath(sd)), "n_samples": len(tel), "smoke": {"checks": [], "cycles_per_op": {}},
               "cells": {}, "runs_not_started": []}
    for fmt in C.FMTS:
        sp = proc_lines(os.path.join(sd, "smoke", fmt), "proc.out")
        ch = [x for x in sp if x.get("test") == "check"]
        arm_out["smoke"]["checks"] += [x.get("result") for x in ch]
        if ch and ch[-1].get("cycles_per_op"):
            arm_out["smoke"]["cycles_per_op"][fmt] = ch[-1]["cycles_per_op"]
    by_fmt = {t: [] for t in C.FMTS}
    rd = os.path.join(sd, "runs")
    for key in sorted(os.listdir(rd)) if os.path.isdir(rd) else []:
        p = os.path.join(rd, key, "run.json")
        if not os.path.exists(p):
            continue
        rec = C.load(p)
        if not rec.get("procs"):
            arm_out["runs_not_started"].append({"run": key, "why": rec.get("why")})
            continue
        r = reduce_run(os.path.join(rd, key), rec, tel, arm)
        arm_out["cells"].setdefault(rec["cell"], {"runs": []})["runs"].append(r)
        for pr in rec["procs"]:
            by_fmt[rec["format"]] += [x for x in proc_lines(os.path.join(rd, key), pr["name"] + ".out") if x.get("test") == "fma"]
    q = os.path.join(sd, "queue.json")
    if os.path.exists(q):
        qq = C.load(q)
        arm_out["queue"] = {"stop": qq.get("stop"), "card_min": qq.get("card_min"), "rest_die_c": qq.get("rest_die_c"),
                            "not_started": [x for x in qq.get("queue", []) if not x.get("ran")]}
    if arm == "A":
        arm_out["x600"] = {t: x600(by_fmt[t]) for t in C.FMTS}
    return arm_out


def table(data):
    L = ["E190 reduced (each run of each cell; J over idle = (p_work - p_rest) t_gemm, J with the card at rest = p_work t_gemm, the scorer's form)"]
    for arm, A in data["arms"].items():
        L.append(f"arm {arm} ({A.get('session')}): {A.get('n_samples')} samples; smoke checks {A['smoke']['checks']}, cycles an op "
                 f"{ {k: round(v, 1) for k, v in A['smoke']['cycles_per_op'].items()} }; queue {A.get('queue', {}).get('stop')}")
        for cell in sorted(A["cells"]):
            for r in A["cells"][cell]["runs"]:
                if r.get("t_gemm_s"):
                    jo = (r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"] if r.get("p_rest_w") is not None and r.get("p_work_w") is not None else None
                    jr = r["p_work_w"] * r["t_gemm_s"] if r.get("p_work_w") is not None else None
                    L.append(f"  {cell:11s} {r['run']:22s} t {r['t_gemm_s']:.4f} s over {r['n_gemm']} GEMMs; work {r['p_work_w']} W, rest "
                             f"{r['p_rest_w']} W; J over idle {jo if jo is None else round(jo, 3)}, at rest {jr if jr is None else round(jr, 3)}; "
                             f"die {r.get('die_start_c')} -> {r.get('die_c')} C; {r['mhz']:.0f} MHz (min {r['mhz_min']}); checks {sorted(set(r['checks']))}")
                else:
                    L.append(f"  {cell:11s} {r['run']:22s} NO COUNTED LAUNCH ({r.get('why')})")
        for x in A.get("runs_not_started", []):
            L.append(f"  not started: {x['run']} ({x['why']})")
        if arm == "A":
            L.append(f"  x600: {json.dumps(A.get('x600'))}")
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", action="append", default=[], help="A=<session dir> or B=<session dir>")
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt")
    a = ap.parse_args(argv)
    data = {"experiment": "E190", "reducer": "tools/claims-v3/e190/reduce_e190.py", "arms": {}}
    for spec in a.arm:
        arm, sd = spec.split("=", 1)
        if arm not in ("A", "B") or not os.path.isdir(sd):
            print(f"refused: --arm {spec}")
            return 2
        data["arms"][arm] = reduce_arm(sd, arm)
    with open(a.out, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)
    t = table(data)
    if a.txt:
        with open(a.txt, "w") as f:
            f.write(t)
    sys.stdout.write(t)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
