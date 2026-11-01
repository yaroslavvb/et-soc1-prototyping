#!/usr/bin/env python3
"""Q132(g), item 10: the lattice and the 98% that were not hit. POST HOC, desk only, no card.

    ir_lattice.py <repo> <ir-hits.json> [--out ir-lattice.json] > ir-lattice.txt

1. THE RING'S OWN LATTICE. All POWER_IDLE records in a session's rings (dips and the ordinary end-of-process idles): the period that
   lines them up, the circular R, the residuals.
2. THE HITS' LATTICE ON THE HOST CLOCK. Each session's hit kernels' start stamps (host ms): the one period and phase that fit them,
   leave-one-out residuals, and the chance of that.
3. EVERY KERNEL BOUNDARY AT 800 MHZ against that lattice: distance of each boundary from the nearest lattice point, boundaries and hits
   per 1 ms bin. The hits fix the lattice, so the test is what happens to the boundaries they did not choose.
"""
import argparse
import json
import math
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ir_lib as L


def lattice_host(t, q_lo=999.9, q_hi=1000.1, step=0.0002):
    t0 = t[0]
    best = None
    n = int((q_hi - q_lo) / step)
    for i in range(n + 1):
        q = q_lo + i * step
        c = sum(math.cos(2 * math.pi * ((x - t0) % q) / q) for x in t)
        s = sum(math.sin(2 * math.pi * ((x - t0) % q) / q) for x in t)
        r = math.hypot(c, s) / len(t)
        if best is None or r > best[0]:
            best = (r, q, math.atan2(s, c))
    r, q, ph = best
    p = t0 + ph / (2 * math.pi) * q
    pts = [(round((x - p) / q), x) for x in t]
    a, b, rms = L.fit_line(pts)
    return {"p": a, "q": b, "R": r, "rms": rms, "k": [k for k, _ in pts], "res": [x - (a + b * k) for k, x in pts]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("hits")
    ap.add_argument("--out")
    a = ap.parse_args()
    H = json.load(open(a.hits))["hits"]
    allclean = [h for h in H if h.get("x_ms") is not None and -40 <= h["x_ms"] < 40 and h.get("prev_g") and h["prev_g"] >= 0.79]
    clean = [h for h in allclean if h["how"] == "S"]
    konly = [h for h in allclean if h["how"] == "K"]
    print(f"kernel-rule hits the sampler rule did not flag (out of sample for the lattice): {[(h['exp'], h['run'][:30], h['kernel'], h['since_proc_s'], h['x_ms']) for h in konly]}")
    print(f"clean mid-launch resets: {len(clean)} of {len(H)} flagged (the others: {[(h['exp'], h['run'][:26], h.get('x_ms'), h.get('k_g')) for h in H if h not in clean]})")
    xs = sorted(h["x_ms"] for h in clean)
    print(f"x, the time the hit kernel ran at 800 MHz before the fall: min {xs[0]}, median {st.median(xs)}, max {xs[-1]} ms; the kernels are {min(h['k_wall_s'] for h in clean):.3f}-{max(h['k_wall_s'] for h in clean):.3f} s long")
    print(f"the kernel before the hit: g {min(h['prev_g'] for h in clean)}-{max(h['prev_g'] for h in clean)} GHz")
    out = {"sessions": {}, "n_clean": len(clean), "x_ms": xs}
    print("\n1. The ring's own POWER_IDLE records")
    S = {}
    for exp, (box, card, dirs) in L.SESSIONS.items():
        runs = []
        ring = {}
        for rel in dirs:
            s = L.load_rundir(a.repo, rel)
            for r in s["runs"]:
                r["exp"] = exp
                runs.append(r)
            for e in s["ring"]:
                ring[(e["ts"], e["kind"])] = e
        S[exp] = runs
        ring_list = sorted(ring.values(), key=lambda e: e["ts"])
        # the session's own markers only: within the session's span of ring time (drop stale entries from long before)
        tsmax = ring_list[-1]["ts"]
        span_s = (max(r["t_last"] or 0 for r in runs) - min(r["t_first"] or 1e18 for r in runs)) / 1000.0
        mk = [e["ts"] for e in ring_list if e["kind"] == "pstat" and e.get("throttle_state") == 0 and e["ts"] > tsmax - (span_s + 600) * 1e6]
        f = L.fit_lattice(mk)
        res = sorted(x / 1000.0 for x in f["res_us"])
        rec = {"box": box, "ring_markers": len(mk), "ring_period_us": round(f["q_us"], 1), "ring_R": round(f["R"], 4),
               "ring_res_ms_p10_p50_p90": [round(res[len(res) // 10], 1), round(res[len(res) // 2], 1), round(res[9 * len(res) // 10], 1)],
               "ring_res_ms_minmax": [round(res[0], 1), round(res[-1], 1)]}
        out["sessions"][exp] = rec
        print(f"  {exp} {box}: {len(mk)} records, period {f['q_us'] / 1e6:.6f} s on the SP's tick, R {f['R']:.4f}, residual p10/50/90 {rec['ring_res_ms_p10_p50_p90']} ms, min/max {rec['ring_res_ms_minmax']} ms")
    print("\n2. The hits on the host clock (start stamps of the hit kernels)")
    for exp in ("E80", "E83", "E87"):
        v = sorted([h for h in clean if h["exp"] == exp], key=lambda h: h["k_t0"])
        t = [h["k_t0"] for h in v]
        f = lattice_host(t)
        rec = out["sessions"][exp]
        loo = []
        for i in range(len(t)):
            pts = [(k, x) for j, (k, x) in enumerate(zip(f["k"], t)) if j != i]
            aa, bb, _ = L.fit_line(pts)
            loo.append(round(t[i] - (aa + bb * f["k"][i]), 2))
        rec.update({"host_period_ms": round(f["q"], 4), "host_rms_ms": round(f["rms"], 3), "host_res_ms": [round(x, 2) for x in f["res"]], "host_loo_ms": loo, "n_hits": len(t)})
        print(f"  {exp}: {len(t)} hits, period {f['q']:.4f} ms, rms {f['rms']:.2f} ms, residuals {[round(x, 1) for x in f['res']]}, leave-one-out {loo}")
        # 3. every boundary
        p, q = f["p"], f["q"]
        hitset = {(h["run"], h["proc"], h["kernel"]) for h in v}
        kset = {(h["run"], h["proc"], h["kernel"]) for h in konly if h["exp"] == exp}
        rows = []
        for r in S[exp]:
            for pr in r["procs"]:
                ks = pr["kernels"]
                for j in range(1, len(ks)):
                    g0 = L.g_eff(ks[j - 1])
                    if g0 is None or g0 < 0.79:
                        continue
                    if ks[j - 1].get("launch", -1) < 0:
                        continue
                    t0 = ks[j]["t_start_ms"]
                    k = round((t0 - p) / q)
                    d = t0 - (p + q * k)  # kernel start stamp minus the nearest lattice point
                    key = (r["run"], pr["proc"], ks[j].get("launch"))
                    rows.append((d, key in hitset or key in kset, r["run"], ks[j].get("launch"), L.g_eff(ks[j]), t0 - ks[j - 1]["t_end_ms"], key in kset))
        rec["exposed_boundaries"] = len(rows)
        hist = {}
        for d, hit, *_ in rows:
            b = math.floor(d)
            if -12 <= b < 12:
                x = hist.setdefault(b, [0, 0])
                x[0] += 1
                x[1] += 1 if hit else 0
        print(f"     exposed boundaries (kernel before at 800 MHz): {len(rows)}; by distance from the lattice, kernel start stamp minus lattice point, ms: boundaries / hits")
        print("     " + "  ".join(f"[{b}]{hist[b][0]}/{hist[b][1]}" for b in sorted(hist)))
        rec["hist_ms"] = {str(b): hist[b] for b in sorted(hist)}
        near = sorted([x for x in rows if abs(x[0]) < 2.5], key=lambda x: x[0])
        print("     every boundary within 2.5 ms: " + "; ".join(f"{x[0]:+.1f}{' FELL' if x[1] else ''}{' (not used in the fit)' if x[6] else ''} (next g {x[4]:.3f})" for x in near))
        rec["near"] = [{"d": round(x[0], 2), "fell": x[1], "not_in_fit": x[6], "next_g": round(x[4], 4), "run": x[2], "kernel": x[3]} for x in near]
        far = [x for x in rows if abs(x[0]) > 1.2]
        close = [x for x in rows if abs(x[0]) <= 1.2]
        rec["within_1p2ms"] = {"boundaries": len(close), "fell": sum(1 for x in close if x[1])}
        rec["beyond_1p2ms"] = {"boundaries": len(far), "fell": sum(1 for x in far if x[1]), "max_abs_d_fell": round(max([abs(x[0]) for x in rows if x[1]] or [0]), 2)}
        print(f"     within 1.2 ms of the lattice: {rec['within_1p2ms']}; beyond: {rec['beyond_1p2ms']}")
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
