#!/usr/bin/env python3
"""Q132(g), item 10: find every mid-launch idle reset in the committed sessions and place it against the kernels. POST HOC, desk only.

    ir_hits.py <repo> [--out ir-hits.json] > ir-hits.txt

A HIT is found two independent ways and both are reported:
  S  (sampler, E80's rule, any die): a work sample at 600 MHz whose previous sample read 800 MHz, more than 1.5 s after its process
     started and more than 0.3 s before it ended. (A power or a thermal step goes one point at a time.)
  K  (kernel counters): kernel j whose mean clock is 0.55-0.62 GHz, straight after a kernel at 0.79 GHz or more, at any time in the process.
     Only the hits S misses are listed as K. The lattice of ir_lattice.py is fitted on S alone, so K's are out of sample for it.
For each hit: which kernel the fall landed in, how long that kernel ran at 800 MHz before the fall (x), the kernels either side, the
ring's marker if the ring reaches it, and the conditions.
"""
import argparse
import json
import os
import statistics as st
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ir_lib as L

os.environ["TZ"] = "America/Los_Angeles"
time.tzset()


def fmt(ms):
    return time.strftime("%d %b %H:%M:%S", time.localtime(ms / 1000.0))


def proc_hits(run, proc):
    T = [x for x in run["tel"] if proc["t0"] <= x[0] <= proc["t1"]]
    ks = proc["kernels"]
    hits = []
    # sampler rule
    S = []
    for i in range(1, len(T)):
        if T[i][4] == 600 and T[i - 1][4] == 800 and (T[i][0] - proc["t0"]) > 1500 and (proc["t1"] - T[i][0]) > 300:
            S.append((T[i - 1][0], T[i][0], T[i][1], T[i - 1][3]))
    # kernel rule
    K = []
    for j in range(1, len(ks)):
        g0, g1 = L.g_eff(ks[j - 1]), L.g_eff(ks[j])
        if g0 is None or g1 is None:
            continue
        if ks[j].get("launch", -1) < 0 or ks[j - 1].get("launch", -1) < 0:
            continue
        # any time in the process; 0.55 GHz keeps out the 300 MHz safe state of card 0's PMIC alarm
        if 0.55 <= g1 < 0.62 and g0 >= 0.79:
            K.append(j)
    # join: for every sampler hit, the kernel whose span holds the last 800 sample or the first 600 sample and which shows the shortfall
    used = set()
    for (t8, t6, die, w) in S:
        best = None
        for j, k in enumerate(ks):
            if k.get("launch", -1) < 0:
                continue
            if k["t_end_ms"] >= t8 and k["t_start_ms"] <= t6:
                g = L.g_eff(k)
                if g is not None and g < 0.79 and best is None:
                    best = j
        hits.append({"how": "S", "t800": t8, "t600": t6, "die": die, "w_before": w, "j": best})
        if best is not None:
            used.add(best)
    for j in K:
        if j not in used:
            hits.append({"how": "K", "t800": None, "t600": None, "die": None, "w_before": None, "j": j})
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--out")
    a = ap.parse_args()
    allhits = []
    summary = {}
    for exp, (box, card, dirs) in L.SESSIONS.items():
        runs = []
        for rel in dirs:
            S = L.load_rundir(a.repo, rel)
            for r in S["runs"]:
                r["exp"] = exp
                runs.append(r)
        ov = L.launch_overhead(runs)
        np_ = sum(len(r["procs"]) for r in runs)
        nk = sum(len(p["kernels"]) for r in runs for p in r["procs"])
        hits = 0
        for r in runs:
            for p in r["procs"]:
                for h in proc_hits(r, p):
                    j = h["j"]
                    ks = p["kernels"]
                    rec = {"exp": exp, "box": box, "run": r["run"], "session": r["session"], "block": r["block"], "kind": L.kind_of(r), "minions": r.get("minions"),
                           "proc": p["proc"], "how": h["how"], "t_proc0_ms": p["t0"], "t_proc1_ms": p["t1"], "t800_ms": h["t800"], "t600_ms": h["t600"], "die": h["die"], "w_before": h["w_before"]}
                    if j is not None:
                        k, k0 = ks[j], ks[j - 1] if j > 0 else None
                        k1 = ks[j + 1] if j + 1 < len(ks) else None
                        rec.update({"kernel": k.get("launch"), "k_wall_s": k["wall_s"], "k_g": round(L.g_eff(k), 4), "x_ms": round(L.x_ms(k), 1),
                                    "k_t0": k["t_start_ms"], "k_t1": k["t_end_ms"],
                                    "prev_g": round(L.g_eff(k0), 4) if k0 else None, "prev_t1": k0["t_end_ms"] if k0 else None,
                                    "next_g": round(L.g_eff(k1), 4) if k1 else None,
                                    "gap_before_ms": k["t_start_ms"] - k0["t_end_ms"] if k0 else None,
                                    "since_proc_s": round((k["t_start_ms"] - p["t0"]) / 1000.0, 3),
                                    "before_proc_end_s": round((p["t1"] - k["t_end_ms"]) / 1000.0, 3)})
                    allhits.append(rec)
                    hits += 1
        summary[exp] = {"box": box, "runs": len(runs), "processes": np_, "kernels": nk, "hits": hits, "overhead_ms": round(ov * 1000, 3) if ov else None}
    print("session  box          runs  processes  kernels  hits   launch overhead ms")
    for e, s in summary.items():
        print(f"{e:7s} {s['box']:11s} {s['runs']:5d} {s['processes']:9d} {s['kernels']:8d} {s['hits']:5d}   {s['overhead_ms']}")
    print("\nexp run                             how  time             since_proc_s  kernel  wall_s   g      x_ms  prev_g  next_g  gap_ms  die  W_before")
    for h in allhits:
        print(f"{h['exp']:4s} {h['run'][:32]:32s} {h['how']:2s} {fmt(h.get('k_t0') or h['t600_ms'] or 0)} {h.get('since_proc_s')} k{h.get('kernel')} {h.get('k_wall_s')} {h.get('k_g')} x {h.get('x_ms')} prev {h.get('prev_g')} next {h.get('next_g')} gap {h.get('gap_before_ms')} die {h.get('die')} W {h.get('w_before')}")
    if a.out:
        json.dump({"summary": summary, "hits": allhits}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
