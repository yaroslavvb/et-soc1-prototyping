#!/usr/bin/env python3
"""Round B's critic (Q145(b)), POST HOC, its own code written from the text of amendment A1 (REGISTRATION.md.dated-note-4.md) and the
registration's section 1; it imports none of the dip lane's code. It uses only the lab's SP ring decoder
(tools/claims-v3/hpl/sptrace_full.py, scan) to read the committed rings.

  python3 -I -B docs/reports/data/2026-11-06-q145b-dips-posthoc/posthoc_climbs_note2.py . <out.json>

1. A1's DT-N on E173, E174 and E175 (BURST blocks): eligible gaps, expected at delta 0 / 0.7 / 1.2 ms, band, falls, by own code.
2. The late climbs at a process start, at the 10 Hz sampler's resolution: for each burst process, the observed first 800 MHz
   reading after the first launch (as the study reads it) against the term's predicted climb end on the ORACLE lattice (fitted
   on all of the session's A1 falls with the card's period prior; post hoc by construction), with the registered start climb
   c8 (aifoundry2 0.31 s, card 0 0.39 s). Counts above 1.5 s and above 1.6 s (one sample past the window's opening), and the
   distribution of observed minus predicted.
"""
import gzip
import json
import math
import os
import statistics as st
import sys

LAB = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(LAB, "tools", "claims-v3", "hpl"))
import sptrace_full as spf  # noqa: E402  (the lab's ring decoder only)

D = os.path.join(LAB, "docs", "reports", "data")
SES = {"E173": ("2026-11-05-e173-blind8-aifoundry2/aifoundry2/s1", "a2"),
       "E174": ("2026-11-05-e174-blind8-card0/aifoundry1-c0/s1", "c0"),
       "E175": ("2026-11-05-e175-governed-aifoundry2/aifoundry2/s1", "a2")}
P0 = {"a2": (1000.0095, 0.0015), "c0": (1000.0190, 0.0010)}
C8_START = {"a2": 0.31, "c0": 0.39}
A_MS = 0.7


def jl(p):
    for q in (p, p + ".gz"):
        if os.path.exists(q):
            break
    else:
        return []
    op = gzip.open if q.endswith(".gz") else open
    out = []
    with op(q, "rt") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("{"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def procs_of(sdir):
    out = []
    for r in jl(os.path.join(sdir, "launches.jsonl")):
        if r.get("role") != "work":
            continue
        L = sorted(((int(k["t_start_ms"]), int(k["t_end_ms"]), float(k.get("ghz") or 0.0)) for k in r.get("sparsity", [])
                    if "t_start_ms" in k and "t_end_ms" in k))
        if L:
            out.append({"run": r["run"], "t0": int(r["t_start_ms"]), "L": L})
    out.sort(key=lambda p: p["L"][0][0])
    return out


def rings(sdir):
    """{run: (complete, new pstat entries)} in runs.jsonl order, each dump against the one before (start.bin first)."""
    sp = os.path.join(sdir, "sp")
    prev = None
    if os.path.exists(os.path.join(sp, "start.bin")):
        prev = spf.scan(open(os.path.join(sp, "start.bin"), "rb").read())
    out = {}
    for r in jl(os.path.join(sdir, "runs.jsonl")):
        fp = os.path.join(sp, r["run"] + ".bin")
        cur = spf.scan(open(fp, "rb").read()) if os.path.exists(fp) else None
        if not cur:
            out[r["run"]] = (False, [])
        else:
            complete = bool(prev) and min(e["ts"] for e in cur) <= max(e["ts"] for e in prev)
            t0 = max(e["ts"] for e in prev) if prev else None
            new = [e for e in cur if e.get("kind") == "pstat" and (t0 is None or e["ts"] > t0)]
            out[r["run"]] = (complete, new)
        prev = cur
    return out


def pois_cdf(k, mu):
    if k < 0:
        return 0.0
    s, t = 0.0, math.exp(-mu)
    for j in range(k + 1):
        if j:
            t *= mu / j
        s += t
    return s


def band(mu_lo, mu_hi):
    lo = 0
    while pois_cdf(lo, mu_lo) <= 0.025:
        lo += 1
    hi = 0
    while pois_cdf(hi, mu_hi) < 0.975:
        hi += 1
    return lo, hi


def fit(cal, card):
    p0, s0 = P0[card]
    c1 = cal[0][0]
    rows = [(round((c - c1) / p0), c, sd) for c, sd in cal]
    a11 = sum(1 / sd ** 2 for _, _, sd in rows)
    a12 = sum(k / sd ** 2 for k, _, sd in rows)
    a22 = sum(k * k / sd ** 2 for k, _, sd in rows) + 1 / s0 ** 2
    b1 = sum(c / sd ** 2 for _, c, sd in rows)
    b2 = sum(k * c / sd ** 2 for k, c, sd in rows) + p0 / s0 ** 2
    det = a11 * a22 - a12 * a12
    return (a22 * b1 - a12 * b2) / det, (a11 * b2 - a12 * b1) / det


def main():
    res = {"label": "POST HOC, round B's critic's own code (A1's text; the lab's ring decoder only)", "sessions": {}}
    for name, (rel, card) in SES.items():
        sdir = os.path.join(D, rel)
        ps = procs_of(sdir)
        rg = rings(sdir)
        p0 = P0[card][0]
        elig, falls, cal = [], [], []
        n_clear = n_scope = 0
        for p in ps:
            blk = p["run"].split("-", 1)[0]
            complete, new = rg.get(p["run"], (False, []))
            steps = sum(1 for e in new if e.get("throttle_state") != 0 and e.get("mhz") is not None and e["mhz"] <= 620)
            safe = any(e.get("throttle_state") == 3 for e in new)
            clear = bool(complete and new and steps == 0)
            L = p["L"]
            alarm = safe or any(L[i - 1][2] >= 0.65 and L[i][2] < 0.55 for i in range(1, len(L)))
            in_scope = blk == "BURST" and not alarm
            p["clear"], p["in_scope"] = clear, in_scope
            n_clear += clear
            n_scope += in_scope
            ts = L[0][0] + 0.5
            for i in range(1, len(L)):
                g = L[i][0] - L[i - 1][1]
                lo, hi = L[i - 1][1] + 0.5, L[i][0] + 0.5 + A_MS
                prev, nxt = L[i - 1][2], L[i][2]
                ok = in_scope and g >= 0 and lo >= ts + p0 and (prev >= 0.79 or (prev >= 0.65 and clear))
                if not ok:
                    continue
                elig.append(g)
                if 0.55 <= nxt <= 0.62:
                    falls.append({"run": p["run"], "gap": i, "prev_ghz": prev})
                    w = hi - lo
                    cal.append((0.5 * (lo + hi), math.sqrt(w * w / 12 + 0.3 ** 2)))
        n, s = len(elig), float(sum(elig))
        exp = [round((s + n * d) / p0, 3) for d in (0.0, 0.7, 1.2)]
        lo_, hi_ = band((s + n * 0.0) / p0, (s + n * 1.2) / p0)
        rec = {"processes": len(ps), "in_scope": n_scope, "clear": n_clear, "eligible_gaps": n, "expected_0_0.7_1.2": exp,
               "band_95": [lo_, hi_], "falls": len(falls), "fall_list": falls,
               "verdict": "PASS" if lo_ <= len(falls) <= hi_ else "FAIL"}
        # 2. late climbs on the oracle lattice against the 10 Hz telemetry
        phi, P = fit(cal, card)
        c8 = C8_START[card] * 1000.0
        rows = []
        for p in ps:
            if p["run"].split("-", 1)[0] != "BURST":
                continue
            L = p["L"]
            ts = L[0][0] + 0.5
            busy = [(a + 0.5 + A_MS, b + 0.5) for a, b, _ in L]
            k = math.ceil((ts - phi) / P)
            c0 = None
            while True:
                h = phi + k * P
                k += 1
                if h > L[-1][1] + 0.5:
                    break
                if any(a <= h <= b for a, b in busy):
                    c0 = h
                    break
            pred = (c0 + c8 - p["t0"]) / 1000.0 if c0 is not None else None
            tf = os.path.join(sdir, "tel", p["run"] + ".jsonl")
            s_ = sorted((int(d["t_ms"]), (d.get("mhz") or {}).get("minion")) for d in jl(tf) if "t_ms" in d)
            f8 = next((t for t, f in s_ if t >= L[0][0] and f is not None and f >= 800), None)
            obs = (f8 - p["t0"]) / 1000.0 if f8 is not None else None
            rows.append({"run": p["run"], "pred_climb_end_s": round(pred, 3) if pred is not None else None,
                         "obs_first_800_s": round(obs, 3) if obs is not None else None})
        both = [r for r in rows if r["pred_climb_end_s"] is not None and r["obs_first_800_s"] is not None]
        d = [r["obs_first_800_s"] - r["pred_climb_end_s"] for r in both]
        rec["late_climbs"] = {
            "n": len(both),
            "pred_gt_1.5": sum(r["pred_climb_end_s"] > 1.5 for r in both),
            "pred_gt_1.6": sum(r["pred_climb_end_s"] > 1.6 for r in both),
            "obs_gt_1.5": sum(r["obs_first_800_s"] > 1.5 for r in both),
            "obs_gt_1.6": sum(r["obs_first_800_s"] > 1.6 for r in both),
            "obs_minus_pred_s": {"median": round(st.median(d), 3), "p10": round(sorted(d)[len(d) // 10], 3),
                                 "p90": round(sorted(d)[9 * len(d) // 10], 3)} if d else None,
            "pred_late_list": [r for r in both if r["pred_climb_end_s"] > 1.5],
            "obs_late_list": [r for r in both if r["obs_first_800_s"] > 1.5],
            "oracle_lattice": {"phi_ms": round(phi, 3), "period_ms": round(P, 5), "falls": len(cal)}}
        res["sessions"][name] = rec
    open(sys.argv[2], "w").write(json.dumps(res, indent=1, sort_keys=True) + "\n")
    for name, rec in res["sessions"].items():
        lc = rec["late_climbs"]
        print(name, {k: rec[k] for k in ("processes", "in_scope", "clear", "eligible_gaps", "expected_0_0.7_1.2", "band_95", "falls", "verdict")})
        print("   late climbs:", {k: lc[k] for k in ("n", "pred_gt_1.5", "pred_gt_1.6", "obs_gt_1.5", "obs_gt_1.6", "obs_minus_pred_s")})


if __name__ == "__main__":
    main()
