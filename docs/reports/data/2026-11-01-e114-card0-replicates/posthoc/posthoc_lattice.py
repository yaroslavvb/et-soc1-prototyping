#!/usr/bin/env python3
"""E114 (Q133), POST HOC, labelled, never a verdict: Q132(g)'s heartbeat lattice (its section b), run on E114's own session
with Q132(g)'s committed code unchanged (ir_hits.proc_hits for the falls, ir_lattice.lattice_host for the lattice, the gap
test of ir_gaps.py part A, its climb test part B). Written at the desk after the data and after the verifier's report
(Sun 1 Nov 2026); no card was touched and nothing was re-run.

1. The falls inside a process: ir_hits.py's sampler rule S and kernel rule K, over every process of the 15 sustained runs;
   clean ones as ir_gaps.py keeps them (x within -40..40 ms, the kernel before at 0.79 GHz or more).
2. One lattice from those falls alone, the period searched in 999.95-1000.07 ms, as Q132(g) fitted E84's three falls.
3. Out of sample for that lattice: every gap between two processes whose earlier process's last kernel ran at 0.79 GHz or
   more. Is a lattice point inside the gap, and did the clock fall (a 600 MHz reading from the end of the last kernel to
   400 ms into the next process)? The same 2 x 2 table as Q132(g)'s ir-gaps.txt.
4. The climb after a fall in a gap: the next process's first 800 MHz reading, from its start and from the first lattice
   point that falls inside one of its kernels (ir_gaps.py part B's measure, applied to the later starts).

    python3 posthoc_lattice.py > lattice.txt        # in this directory (writes lattice.json beside it)
"""
import json
import math
import os
import statistics as st
import sys
import time

sys.dont_write_bytecode = True
if not hasattr(time, "tzset"):   # some Python builds lack it; ir_hits.py calls it at import, for printing times only
    time.tzset = lambda: None
D = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(os.path.dirname(D))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(DATA)))
sys.path.insert(0, os.path.join(DATA, "2026-11-01-q132-governor-desk"))
import ir_lib as L  # noqa: E402
import ir_hits as H  # noqa: E402
import ir_lattice as IL  # noqa: E402

REL = "2026-11-01-e114-card0-replicates/s1"
runs = [r for r in L.load_rundir(REPO, REL)["runs"] if r["block"] == "SUS"]
print(f"E114 session {REL}: {len(runs)} sustained runs, {sum(len(r['procs']) for r in runs)} processes, "
      f"{sum(len(p['kernels']) for r in runs for p in r['procs'])} kernels")

# 1. the falls inside a process
hits = []
for r in runs:
    for p in r["procs"]:
        for h in H.proc_hits(r, p):
            j = h["j"]
            if j is None:
                hits.append({"run": r["run"], "proc": p["proc"], "how": h["how"], "j": None})
                continue
            ks = p["kernels"]
            k, k0 = ks[j], ks[j - 1] if j > 0 else None
            hits.append({"run": r["run"], "kind": L.kind_of(r), "proc": p["proc"], "how": h["how"], "kernel": k.get("launch"),
                         "k_t0": k["t_start_ms"], "x_ms": round(L.x_ms(k), 1), "k_g": round(L.g_eff(k), 4),
                         "prev_g": round(L.g_eff(k0), 4) if k0 else None,
                         "gap_before_ms": k["t_start_ms"] - k0["t_end_ms"] if k0 else None,
                         "since_proc_s": round((k["t_start_ms"] - p["t0"]) / 1000.0, 3)})
clean = sorted([h for h in hits if h.get("x_ms") is not None and -40 <= h["x_ms"] < 40 and h.get("prev_g") and h["prev_g"] >= 0.79],
               key=lambda h: h["k_t0"])
print(f"\n1. Falls inside a process, rules S and K: {len(hits)}; clean (x -40..40 ms, kernel before >= 0.79 GHz): {len(clean)}")
for h in hits:
    print(f"   {h}")

out = {"hits": hits}
if len(clean) < 2:
    print("\nFewer than two clean falls: no lattice can be fitted from them alone; nothing further.")
    json.dump(out, open(os.path.join(D, "lattice.json"), "w"), indent=1)
    sys.exit(0)

# 2. the lattice from those falls alone
f = IL.lattice_host([h["k_t0"] for h in clean], q_lo=999.95, q_hi=1000.07, step=0.0005)
p0, q = f["p"], f["q"]
span_s = (clean[-1]["k_t0"] - clean[0]["k_t0"]) / 1000.0
print(f"\n2. Lattice from the {len(clean)} clean falls: period {q:.4f} ms, R {f['R']:.4f}, residuals "
      f"{[round(x, 2) for x in f['res']]} ms, the falls {span_s:.0f} s apart (beats {[k - f['k'][0] for k in f['k']]})")
print("   Q132(g)'s E84 lattice on this card, 31 Oct: 1000.0186 ms from 3 falls (its ir-gaps.txt); aifoundry2's three "
      "sessions 1000.0098-1000.0105 ms")


def lattice_points(t0, t1):
    k0, k1 = math.ceil((t0 - p0) / q), math.floor((t1 - p0) / q)
    return [p0 + q * k for k in range(k0, k1 + 1)]


# 3. the gaps between processes, out of sample
table = {(True, True): 0, (True, False): 0, (False, True): 0, (False, False): 0}
gaps, rows, exceptions = [], [], []
for r in runs:
    for i in range(1, len(r["procs"])):
        prev, cur = r["procs"][i - 1], r["procs"][i]
        if not prev["kernels"] or not cur["kernels"]:
            continue
        last = prev["kernels"][-1]
        g = L.g_eff(last)
        if g is None or g < 0.79:
            continue
        t_a, t_b = last["t_end_ms"], cur["kernels"][0]["t_start_ms"]
        gaps.append(t_b - t_a)
        samples = [x for x in r["tel"] if t_a <= x[0] <= t_b + 400 and x[4] is not None]
        fell = any(x[4] == 600 for x in samples)
        pts = lattice_points(t_a - 1.0, t_b + 1.0)
        table[(bool(pts), fell)] += 1
        pos = round(pts[0] - t_a, 1) if pts else None
        rows.append({"run": r["run"], "proc": cur["proc"], "gap_ms": t_b - t_a, "lattice_ms_after_last_kernel": pos, "fell": fell})
        if bool(pts) != fell:
            k = round(((t_a + t_b) / 2 - p0) / q)
            exceptions.append({"run": r["run"], "proc": cur["proc"], "gap_ms": t_b - t_a, "lattice_in_gap": bool(pts), "fell": fell,
                               "to_a_ms": round(min(abs(p0 + q * k2 - t_a) for k2 in (k - 1, k, k + 1)), 1),
                               "to_b_ms": round(min(abs(p0 + q * k2 - t_b) for k2 in (k - 1, k, k + 1)), 1)})
n = sum(table.values())
print(f"\n3. Gaps between processes whose earlier process ended at 800 MHz: {n}; gap median {st.median(gaps)} ms, "
      f"range {min(gaps)}-{max(gaps)} ms")
print(f"   lattice point in the gap and the clock fell {table[(True, True)]}; in the gap, no fall {table[(True, False)]}; "
      f"not in the gap, fell {table[(False, True)]}; not in the gap, no fall {table[(False, False)]}  "
      f"-> {table[(True, True)] + table[(False, False)]} of {n} predicted")
for e in exceptions:
    print(f"   exception {e}")
inb = [x["lattice_ms_after_last_kernel"] for x in rows if x["lattice_ms_after_last_kernel"] is not None]
if inb:
    print(f"   where the lattice point sits in the gaps that hold one (ms after the last kernel's end): min {min(inb)}, "
          f"median {st.median(inb)}, max {max(inb)}")
skipped = sum(len(r["procs"]) - 1 for r in runs) - n
print(f"   gaps left out (the earlier process's last kernel under 0.79 GHz: random fp16 at its trip): {skipped}")

# the same gaps against posthoc/climb.json's long climbs (> 0.4 s) at the next process's start
cl = json.load(open(os.path.join(D, "climb.json")))["E114"]
climb = {(rec["run"], i): c for recs in cl.values() for rec in recs for i, c in enumerate(rec["climb_s"])}
agree = sum(1 for x in rows if (climb.get((x["run"], x["proc"])) or 0) > 0.4)
both = sum(1 for x in rows if x["fell"] and (climb.get((x["run"], x["proc"])) or 0) > 0.4)
print(f"   of these gaps, the next process's climb was long (> 0.4 s, posthoc/climb.json) after {agree}; "
      f"fell and long {both}; fell {sum(1 for x in rows if x['fell'])}")

# 4. the climb after a fall in a gap, from the first lattice point inside a kernel
B = []
for r in runs:
    for i in range(1, len(r["procs"])):
        pr = r["procs"][i]
        ks = pr["kernels"]
        if not ks:
            continue
        a = ks[0]["t_start_ms"]
        T = [x for x in r["tel"] if a <= x[0] <= pr["t1"] and x[4] is not None]
        if not T or T[0][4] != 600:
            continue
        t800 = next((x[0] for x in T if x[4] == 800), None)
        if t800 is None:
            continue
        if any((x[1] or 0) >= 65 or (x[3] or 0) >= 65 for x in T if x[0] <= t800):
            continue
        intervals = [(k["t_start_ms"], k["t_end_ms"]) for k in ks]
        tau = next((pt for pt in lattice_points(a - 1.0, pr["t1"]) if any(i0 + 1.2 <= pt <= i1 for i0, i1 in intervals)), None)
        if tau is None:
            continue
        B.append({"run": r["run"], "proc": pr["proc"], "t800_from_start": (t800 - a) / 1000.0, "t800_from_tau": (t800 - tau) / 1000.0,
                  "tau_from_start": (tau - a) / 1000.0})
if B:
    s = lambda k: (round(st.median(x[k] for x in B), 3), round(st.pstdev([x[k] for x in B]), 3), round(min(x[k] for x in B), 3),
                   round(max(x[k] for x in B), 3))
    print(f"\n4. Later process starts that began at 600 MHz, no limit in reach during the climb: {len(B)} (median, sd, min, max, s)")
    print(f"   first 800 reading from the process's first kernel {s('t800_from_start')}; from the first lattice point inside a "
          f"kernel {s('t800_from_tau')}; that lattice point from the first kernel {s('tau_from_start')}")
    print("   Q132(g) on E84's first processes, the same measure: from that heartbeat median 0.383 s, sd 0.188 (its ir-gaps.txt)")
out.update({"lattice": {"p_ms": p0, "q_ms": q, "R": f["R"], "res_ms": f["res"], "n_falls": len(clean)},
            "gaps": {"n": n, "table": {f"{k[0]}_{k[1]}": v for k, v in table.items()}, "exceptions": exceptions, "rows": rows},
            "climbs": B})
json.dump(out, open(os.path.join(D, "lattice.json"), "w"), indent=1)
