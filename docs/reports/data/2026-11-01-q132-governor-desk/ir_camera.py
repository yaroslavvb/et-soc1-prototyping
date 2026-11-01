#!/usr/bin/env python3
"""Q132(g), item 10: the camera sessions (E63 s1, s2; E73; E85), whose sampler sent the statistics reset once a second and whose launch logs
carry no per-kernel records. POST HOC, desk only, no card.

These runs start one process on a fixed 10 s grid, so a one-second heartbeat keeps nearly the same place inside every process: dips should pile
up at one fraction of a second from process start, and the first heartbeat should sit at one place near the first kernels.

    ir_camera.py <repo> [--out ir-camera.json] > ir-camera.txt
"""
import argparse
import json
import math
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ir_lib as L

SESS = [("E63-s1", "2026-10-23-e63-camera-hamming-ladder/s1"), ("E63-s2", "2026-10-23-e63-camera-hamming-ladder/s2"),
        ("E73", "2026-10-27-e73-camera-frequencies"), ("E85", "2026-10-31-e85-camera-kinds")]


def circ(phases):
    c = sum(math.cos(2 * math.pi * x) for x in phases)
    s = sum(math.sin(2 * math.pi * x) for x in phases)
    n = len(phases)
    R = math.hypot(c, s) / n
    mean = (math.atan2(s, c) / (2 * math.pi)) % 1.0
    # Rayleigh p, the usual approximation
    Z = n * R * R
    p = math.exp(-Z) * (1 + (2 * Z - Z * Z) / (4 * n) - (24 * Z - 132 * Z ** 2 + 76 * Z ** 3 - 9 * Z ** 4) / (288 * n * n))
    return round(mean, 3), round(R, 3), max(p, 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--out")
    a = ap.parse_args()
    data = os.path.join(a.repo, "docs/reports/data")
    out = {}
    for name, rel in SESS:
        d = os.path.join(data, rel, "session")
        launches = [x for x in L.jl(os.path.join(d, "launches.jsonl")) if x.get("t_start_ms") and not x.get("dry")]
        T = L.tel(os.path.join(d, "tel.jsonl"))
        times = [x[0] for x in T]
        rows = []
        for l in launches:
            t0, t1 = l["t_start_ms"], l["t_end_ms"]
            S = [x for x in T if t0 <= x[0] <= t1 and x[4] is not None]
            if len(S) < 10:
                continue
            first700 = next((x[0] for x in S if x[4] >= 700), None)
            first800 = next((x[0] for x in S if x[4] == 800), None)
            # mid-launch falls: 800 then 600, after the first 800
            falls = []
            for i in range(1, len(S)):
                if S[i][4] == 600 and S[i - 1][4] == 800:
                    falls.append({"t_s": round((S[i][0] - t0) / 1000.0, 2), "since_reset_ms": S[i][6], "took_ms": S[i][5], "prev_took_ms": S[i - 1][5], "before_end_s": round((t1 - S[i][0]) / 1000.0, 2)})
            # the ordinary fall after the process ended: the first 600 reading after the end
            after = [x for x in T if t1 <= x[0] <= t1 + 1500 and x[4] is not None]
            endfall = next((x[0] for x in after if x[4] == 600), None)
            check = next((x for x in S if x[0] - t0 >= 1500), None)
            rows.append({"n": l.get("n"), "block": l.get("block"), "set": l.get("set"), "t0": t0, "t1": t1, "first700_s": (first700 - t0) / 1000.0 if first700 else None,
                         "first800_s": (first800 - t0) / 1000.0 if first800 else None, "falls": falls,
                         "endfall_phase": (endfall % 1000) / 1000.0 if endfall else None, "endfall_t": endfall,
                         "check_since_reset": check[6] if check else None, "check_mhz": check[4] if check else None})
        # the lattice's place from the ordinary falls at each process's end (host ms mod 1000, a 10 Hz reading)
        ep = [r["endfall_phase"] for r in rows if r["endfall_phase"] is not None]
        mids = []
        for r in rows:
            for f in r["falls"]:
                if f["t_s"] > 1.5 and f["before_end_s"] > 0.3:
                    mids.append((r, f))
        # phases of the falls on the host clock, allowing for the slow walk of a 1000.01 ms period: use the same-epoch phase
        q = 1000.01
        tref = rows[0]["t0"]
        ph_end = [((r["endfall_t"] - tref) % q) / q for r in rows if r["endfall_t"]]
        ph_mid = [((r["t0"] + f["t_s"] * 1000 - tref) % q) / q for r, f in mids]
        print(f"== {name}: {len(rows)} launches, process-start spacing median {st.median(rows[i + 1]['t0'] - rows[i]['t0'] for i in range(len(rows) - 1))} ms")
        print(f"   ordinary end falls: n {len(ph_end)}, circular mean phase, R, Rayleigh p: {circ(ph_end)}")
        if ph_mid:
            print(f"   mid-launch falls: n {len(ph_mid)}, circular mean phase, R, Rayleigh p: {circ(ph_mid)}")
            print("   mid-launch falls: onset s from process start: " + ", ".join(f"{f['t_s']:.2f}" for r, f in mids))
            print("   their since_reset_ms: " + ", ".join(str(f["since_reset_ms"]) for r, f in mids) + "; sampler took_ms: " + ", ".join(str(f["took_ms"]) for r, f in mids) + "; the sample before: " + ", ".join(str(f["prev_took_ms"]) for r, f in mids))
        f8 = sorted(r["first800_s"] for r in rows if r["first800_s"] is not None)
        hist = {}
        for x in f8:
            b = round(math.floor(x * 10) / 10.0, 1)
            hist[b] = hist.get(b, 0) + 1
        print("   first 800 reading from process start, 0.1 s bins: " + " ".join(f"{b:.1f}:{hist[b]}" for b in sorted(hist)))
        # the late-climb link with the reset (E85's C9): the check sample at 1.5 s
        la = [r for r in rows if r["check_mhz"] is not None and r["check_mhz"] != 800]
        print(f"   not at 800 MHz at the 1.5 s check: {len(la)} of {len(rows)}; of those first 800 under 1.9 s: {sum(1 for r in la if (r['first800_s'] or 9) < 1.9)}, 1.9 s or later: {sum(1 for r in la if (r['first800_s'] or 0) >= 1.9)}")
        rr = [r for r in rows if r["check_since_reset"] in (0, 100)]
        nr = [r for r in rows if r["check_since_reset"] not in (0, 100) and r["check_since_reset"] is not None]
        if rr and nr:
            a0 = sum(1 for r in rr if r["check_mhz"] != 800)
            c0 = sum(1 for r in nr if r["check_mhz"] != 800)
            print(f"   right after a reset (since_reset 0 or 100): {a0} of {len(rr)} not at 800 at the check, otherwise {c0} of {len(nr)}")
            # only the full-second misses
            a1 = sum(1 for r in rr if (r["first800_s"] or 0) >= 1.9)
            c1 = sum(1 for r in nr if (r["first800_s"] or 0) >= 1.9)
            p = L.fisher_one_sided(a1, len(rr) - a1, c1, len(nr) - c1)
            print(f"   the same counting only climbs a full second late (first 800 at 1.9 s or later): {a1} of {len(rr)} against {c1} of {len(nr)}, one-sided Fisher p {p:.3g}")
            # the slightly late
            a2 = sum(1 for r in rr if r["check_mhz"] != 800 and (r["first800_s"] or 9) < 1.9)
            c2 = sum(1 for r in nr if r["check_mhz"] != 800 and (r["first800_s"] or 9) < 1.9)
            p2 = L.fisher_one_sided(a2, len(rr) - a2, c2, len(nr) - c2)
            print(f"   only the slightly late (not at 800 at the check, first 800 under 1.9 s): {a2} of {len(rr)} against {c2} of {len(nr)}, one-sided Fisher p {p2:.3g}")
        hb = sum((r["t1"] - r["t0"]) / 1000.0 for r in rows)
        print(f"   heartbeats inside work about {hb:.0f}; mid-launch falls per heartbeat {len(mids) / hb * 100:.2f}%")
        out[name] = {"launches": len(rows), "mid_falls": [{"n": r["n"], **f} for r, f in mids], "end_phase": circ(ph_end), "mid_phase": circ(ph_mid) if ph_mid else None,
                     "first800_hist": {str(k): v for k, v in sorted(hist.items())}, "work_s": round(hb)}
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
