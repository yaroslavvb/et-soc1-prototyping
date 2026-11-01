#!/usr/bin/env python3
"""Q132(g), item 10: the other gaps and the climbs, against the lattice the mid-launch hits fixed. POST HOC, desk only, no card.

The lattice for each session comes ONLY from the mid-launch hits (ir_hits.py), so everything below is out of sample for it.

    ir_gaps.py <repo> <ir-hits.json> [--out ir-gaps.json] > ir-gaps.txt

A. Between processes. In a sustained run nine processes follow each other. The last kernel of one ends, the next process opens the card and
   starts its first kernel a fraction of a second later. For every such gap whose earlier process ended at 800 MHz: does a lattice point
   fall inside the gap, and did the clock fall? The firmware reading says these are the same question.
B. The climb. A run's first process starts from the idle clock. The climb can start only after the first heartbeat that sees a kernel in use.
   For every first process: time from process start to the first reading at 700 and at 800 MHz, and the same measured from the first
   lattice point that falls inside a kernel. The first should scatter over a second, the second should not.
C. The host's gap between kernels: its size per session, and the expected hits from the exposed boundaries.
"""
import argparse
import bisect
import json
import math
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ir_lib as L
import ir_lattice as IL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("hits")
    ap.add_argument("--out")
    a = ap.parse_args()
    H = json.load(open(a.hits))["hits"]
    allclean = [h for h in H if h.get("x_ms") is not None and -40 <= h["x_ms"] < 40 and h.get("prev_g") and h["prev_g"] >= 0.79]
    out = {}
    for exp in ("E80", "E83", "E87", "E64", "E69", "E84"):
        box, card, dirs = L.SESSIONS[exp]
        # E80, E83, E87: the lattice from the sampler-rule hits alone. E64, E69, E84 have 2-3 hits in all, so all of them fix the lattice there,
        # with a narrow period range (the card's own timer, within 70 ppm of a second).
        if exp in ("E80", "E83", "E87"):
            v = sorted([h for h in allclean if h["exp"] == exp and h["how"] == "S"], key=lambda h: h["k_t0"])
            f = IL.lattice_host([h["k_t0"] for h in v])
        else:
            v = sorted([h for h in allclean if h["exp"] == exp], key=lambda h: h["k_t0"])
            f = IL.lattice_host([h["k_t0"] for h in v], q_lo=999.95, q_hi=1000.07, step=0.0005)
        print(f"{exp}: lattice from {len(v)} hits: period {f['q']:.4f} ms, residuals {[round(x, 2) for x in f['res']]} ms")
        p, q = f["p"], f["q"]
        runs = []
        for rel in dirs:
            runs += L.load_rundir(a.repo, rel)["runs"]

        def lattice_points(t0, t1):
            k0, k1 = math.ceil((t0 - p) / q), math.floor((t1 - p) / q)
            return [p + q * k for k in range(k0, k1 + 1)]

        # A. between processes
        table = {(True, True): 0, (True, False): 0, (False, True): 0, (False, False): 0}
        gaps, exceptions = [], []
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
                # the sampler: any 600 MHz reading from the end of the last kernel to 400 ms into the next process's first kernels
                samples = [x for x in r["tel"] if t_a <= x[0] <= t_b + 400 and x[4] is not None]
                fell = any(x[4] == 600 for x in samples)
                pts = lattice_points(t_a - 1.0, t_b + 1.0)
                table[(bool(pts), fell)] += 1
                if bool(pts) != fell:
                    near = None
                    k = round(((t_a + t_b) / 2 - p) / q)
                    exceptions.append({"run": r["run"], "proc": cur["proc"], "gap_ms": t_b - t_a, "lattice_in_gap": bool(pts), "fell": fell,
                                       "to_a_ms": round(min(abs(p + q * k2 - t_a) for k2 in (k - 1, k, k + 1)), 1),
                                       "to_b_ms": round(min(abs(p + q * k2 - t_b) for k2 in (k - 1, k, k + 1)), 1),
                                       "n_samples": len(samples)})
        n = sum(table.values())
        print(f"{exp} A. gaps between processes, earlier process ending at 800 MHz: {n}; gap median {st.median(gaps) if gaps else None} ms, range {min(gaps) if gaps else None}-{max(gaps) if gaps else None} ms")
        print(f"     lattice point in the gap and clock fell {table[(True, True)]}; in the gap, no fall {table[(True, False)]}; not in the gap, fell {table[(False, True)]}; not in the gap, no fall {table[(False, False)]}")
        for e in exceptions[:12]:
            print("       exception", e)
        # C. the host's gap between kernels and the exposed count
        hostgaps = []
        exposed = 0
        for r in runs:
            for pr in r["procs"]:
                ks = pr["kernels"]
                for j in range(1, len(ks)):
                    if ks[j - 1].get("launch", -1) >= 0:
                        # the start-to-start interval less the earlier kernel's wall: sub-ms on average though the stamps are in ms
                        hostgaps.append(ks[j]["t_start_ms"] - ks[j - 1]["t_start_ms"] - ks[j - 1]["wall_s"] * 1000.0)
                        g0 = L.g_eff(ks[j - 1])
                        if g0 is not None and g0 >= 0.79:
                            exposed += 1
        hg = st.mean(hostgaps) if hostgaps else None
        print(f"     C. host gap between kernels, start to start less wall: mean {hg:.3f} ms over {len(hostgaps)}; median stamp gap {st.median(ks2 for ks2 in [round(x) for x in hostgaps])} ms; exposed boundaries {exposed}")
        # B. the climb from idle
        rows = []
        for r in runs:
            if not r["procs"]:
                continue
            pr = r["procs"][0]
            ks = pr["kernels"]
            if not ks:
                continue
            T = [x for x in r["tel"] if pr["t0"] <= x[0] <= pr["t1"] and x[4] is not None]
            if not T or T[0][4] != 600:
                continue
            t700 = next((x[0] for x in T if x[4] >= 700), None)
            t800 = next((x[0] for x in T if x[4] == 800), None)
            if t700 is None or t800 is None:
                continue
            # is a power or thermal limit holding it? the rule of E80's late ramp view: a die under 65 C and a board under 65 W until then
            hold = [x for x in T if x[0] <= t800]
            if any((x[1] or 0) >= 65 or (x[3] or 0) >= 65 for x in hold):
                continue
            # the first lattice point inside a kernel (not within 1.2 ms of a kernel's start, nor in a gap)
            intervals = [(k["t_start_ms"], k["t_end_ms"]) for k in ks]
            tau = None
            first_hb = None
            for pt in lattice_points(ks[0]["t_start_ms"] - 1000, pr["t1"]):
                if pt < ks[0]["t_start_ms"] - 1.0:
                    continue
                if first_hb is None:
                    first_hb = pt
                inside = any(i0 + 1.2 <= pt <= i1 - 0.0 for i0, i1 in intervals)
                if inside:
                    tau = pt
                    break
            if tau is None:
                continue
            rows.append({"run": r["run"], "t700_from_start": (t700 - pr["t0"]) / 1000.0, "t800_from_start": (t800 - pr["t0"]) / 1000.0,
                         "t700_from_tau": (t700 - tau) / 1000.0, "t800_from_tau": (t800 - tau) / 1000.0, "tau_from_start": (tau - pr["t0"]) / 1000.0,
                         "missed_first": first_hb != tau})
        if rows:
            s = lambda k: (round(st.median(x[k] for x in rows), 3), round(st.pstdev([x[k] for x in rows]), 3), round(min(x[k] for x in rows), 3), round(max(x[k] for x in rows), 3))
            print(f"     B. climbs from idle: {len(rows)} first processes, die under 65 C and board under 65 W throughout the climb (median, sd, min, max, s)")
            print(f"        first 700 reading, from process start {s('t700_from_start')}; from the first heartbeat inside a kernel {s('t700_from_tau')}")
            print(f"        first 800 reading, from process start {s('t800_from_start')}; from the first heartbeat inside a kernel {s('t800_from_tau')}")
            late = [x for x in rows if x["t800_from_start"] > 1.2]
            print(f"        late climbs (first 800 reading more than 1.2 s after process start): {len(late)}; of them the first lattice point fell outside a kernel: {sum(1 for x in late if x['missed_first'])}; their first 800 reading from the heartbeat that did count: {[round(x['t800_from_tau'], 2) for x in late]}")
            print(f"        the heartbeat that counted, from process start: {sorted(round(x['tau_from_start'], 2) for x in late)}")
        out[exp] = {"lattice": {"p": p, "q": q}, "gaps": {"n": n, "table": {f"{k[0]}_{k[1]}": v2 for k, v2 in table.items()}, "gap_ms_median": st.median(gaps) if gaps else None, "exceptions": exceptions},
                    "host_gap_ms_mean": round(hg, 3) if hg else None, "exposed": exposed, "climbs": rows}
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
