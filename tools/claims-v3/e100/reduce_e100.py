#!/usr/bin/env python3
"""E100: the scorer, committed before any pass is read. No third-party modules.

    python3 reduce_e100.py <RUNDIR> [--out results.json] > reduce.txt

A FALL is a sampler reading of 600 MHz straight after a reading above 600 MHz, in a work process, more than 1.5 s after the process started and more than 0.3 s before it ended.
HEARTBEATS exposed are that window's length over 1000.01 ms. A process with any reading at die >= 65 C or board >= 65 W is left out and named (no limit may be in reach);
none is expected at about 35 W. The kernel counters are a second channel, reported beside: kernel j at 0.55-0.62 GHz straight after a kernel at 0.69 GHz or more.

D1  the rate follows the gap (primary). Pooled over the rounds, each of A100, A20 and A0 inside its band: from the lower Poisson limit of the predicted rate at w = 1.3 ms to the upper Poisson
    limit at w = 2.5 ms, at the heartbeats really exposed (predictions.json).
D2  one long launch has no fall inside (primary). N: no fall in a kernel after its climb, over at least 100 heartbeats inside kernels (fewer: NOT SCORED).
D3  the gap decides each heartbeat (secondary). A lattice (period and phase) fitted on one round's readings predicts the other round's A20 and A100, each way. For each lattice point with the clock
    above 600 MHz just before it: in a gap or in a kernel (1 ms either side of a kernel's edge is left out), against a 600 MHz reading in the next 250 ms. PASS at sensitivity >= 90% and specificity >= 95%, pooled.
D4  a fall lasts one heartbeat (secondary). First 600 reading to first higher reading: median 1.0-1.25 s, and 3-35% of A100's falls last 1.9 s or more, a second heartbeat landing in a gap (model: 13.9%).
D5  (secondary, if R ran) R's falls inside A20's band: the statistics reset does not cause falls.
"""
import argparse
import bisect
import gzip
import json
import math
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
Q_MS = 1000.01
BLOCK = re.compile(r"^R([12])(A0|A5|A20|A100|N|R)$")
OVERHEAD_S = 0.00047


def jl(path):
    out = []
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        lines = gzip.open(path + ".gz", "rt")
    elif os.path.exists(path):
        lines = open(path)
    else:
        return out
    for ln in lines:
        ln = ln.strip()
        if ln.startswith("{"):
            try:
                out.append(json.loads(ln))
            except ValueError:
                pass
    return out


def tel(path):
    s = []
    for d in jl(path):
        try:
            ms = d.get("temp_c", {}).get("minshire") or [None]
            s.append((int(d["t_ms"]), ms[0], d.get("board_w"), (d.get("mhz") or {}).get("minion"), d.get("since_reset_ms")))
        except (KeyError, TypeError, ValueError, AttributeError):
            pass
    s.sort()
    return s


def g_eff(k):
    w = k["wall_s"] - OVERHEAD_S
    return k["cycles_max"] / w / 1e9 if w > 0 else None


def poisson_lo(mu, tail=0.025):
    L, c = 0, 0.0
    while True:
        c += math.exp(-mu) * mu ** L / math.factorial(L)
        if c > tail:
            return L
        L += 1


def poisson_hi(mu, tail=0.025):
    H, c = 0, math.exp(-mu)
    while 1 - c > tail:
        H += 1
        c += math.exp(-mu) * mu ** H / math.factorial(H)
    return H


def load(rundir):
    runs = jl(os.path.join(rundir, "runs.jsonl"))
    L = jl(os.path.join(rundir, "launches.jsonl"))
    by = {}
    for x in L:
        if x.get("role") == "work":
            by.setdefault(x["run"], []).append(x)
    out = []
    for r in runs:
        m = BLOCK.match(r.get("block") or "")
        if not m:
            continue
        T = tel(os.path.join(rundir, "tel", r["run"] + ".jsonl"))
        procs = []
        for x in sorted(by.get(r["run"], []), key=lambda y: y["t_start_ms"]):
            ks = [k for k in x.get("sparsity", []) if k.get("t_start_ms") and k.get("wall_s")]
            procs.append({"t0": x["t_start_ms"], "t1": x["t_end_ms"], "rc": x.get("rc"), "kernels": ks})
        out.append({"run": r["run"], "round": int(m.group(1)), "arm": m.group(2), "tel": T, "procs": procs})
    return out


def process_view(run):
    """Per process: heartbeats exposed, falls, kernel-channel falls, limit flag, inside-kernel falls."""
    T = run["tel"]
    res = []
    for pr in run["procs"]:
        S = [x for x in T if pr["t0"] <= x[0] <= pr["t1"] and x[3] is not None]
        a, b = pr["t0"] + 1500, pr["t1"] - 300
        limit = any((x[1] or 0) >= 65 or (x[2] or 0) >= 65 for x in S)
        falls = []
        for i in range(1, len(S)):
            if S[i][3] == 600 and S[i - 1][3] > 600 and a < S[i][0] < b:
                falls.append({"t600": S[i][0], "from": S[i - 1][3], "t_before": S[i - 1][0]})
        for f in falls:
            after = [x for x in S if x[0] > f["t600"]]
            up = next((x[0] for x in after if x[3] > 600), None)
            f["at600_s"] = (up - f["t600"]) / 1000.0 if up else None
            f["since_reset_ms"] = next((x[4] for x in S if x[0] == f["t600"]), None)
        ks = pr["kernels"]
        kf = 0
        for j in range(1, len(ks)):
            g0, g1 = g_eff(ks[j - 1]), g_eff(ks[j])
            if ks[j - 1].get("launch", -1) >= 0 and g0 and g1 and 0.55 <= g1 < 0.62 and g0 >= 0.69:
                kf += 1
        inside = sum(1 for f in falls if any(k["t_start_ms"] + 2 <= f["t_before"] and f["t600"] <= k["t_end_ms"] for k in ks))
        kernel_hb = sum(max(0, min(k["t_end_ms"], b) - max(k["t_start_ms"], a)) for k in ks) / Q_MS
        res.append({"hb": max(0, b - a) / Q_MS, "falls": falls, "kernel_falls": kf, "limit": limit, "inside": inside, "kernel_hb": kernel_hb, "n_kernels": len(ks), "rc": pr["rc"]})
    return res


class Round:
    """Per-ms arrays over one round, for the lattice: scope 0 out, 1 in a kernel, 2 in a gap, 3 too near an edge; arm code; clock-before; fell."""

    def __init__(self, runs):
        self.runs = runs
        tt = [x[0] for r in runs for x in r["tel"]]
        self.t0, self.t1 = min(tt), max(tt)
        n = self.t1 - self.t0 + 1
        self.scope = bytearray(n)
        self.arm = bytearray(n)
        self.exposed = bytearray(n)
        self.fell = bytearray(n)
        codes = {"A0": 1, "A5": 2, "A20": 3, "A100": 4, "N": 5, "R": 6}
        for r in runs:
            for pr in r["procs"]:
                ks = pr["kernels"]
                if not ks:
                    continue
                a, b = ks[0]["t_start_ms"] - self.t0, ks[-1]["t_end_ms"] - self.t0
                for i in range(max(0, a), min(n, b + 1)):
                    self.scope[i] = 2
                    self.arm[i] = codes[r["arm"]]
                for k in ks:
                    s, e = k["t_start_ms"] - self.t0, k["t_end_ms"] - self.t0
                    for i in range(max(0, s), min(n, e + 1)):
                        self.scope[i] = 1
                    for i in range(max(0, s - 1), min(n, s + 2)):
                        self.scope[i] = 3
                    for i in range(max(0, e - 1), min(n, e + 2)):
                        self.scope[i] = 3
            T = [x for x in r["tel"] if x[3] is not None]
            # a lattice point at i is exposed if the last reading at or before i - 20 ms read above 600 MHz; it fell if a reading in (i, i + 250] reads 600 MHz
            for u in range(1, len(T)):
                t, m = T[u - 1], T[u]
                lo, hi = t[0] + 20 - self.t0, m[0] + 20 - self.t0
                if t[3] > 600:
                    for i in range(max(0, lo), min(n, hi)):
                        self.exposed[i] = 1
            for u in range(len(T)):
                if T[u][3] == 600:
                    hi = T[u][0] - self.t0
                    for i in range(max(0, hi - 250), min(n, hi)):
                        self.fell[i] = 1

    def score(self, p, q, arms=None):
        """TP in gap and fell, FN in gap no fall, FP in kernel and fell, TN in kernel no fall."""
        tp = fn = fp = tn = 0
        k0 = math.ceil((self.t0 - p) / q)
        k1 = math.floor((self.t1 - p) / q)
        sc, ex, fe, ar, t0 = self.scope, self.exposed, self.fell, self.arm, self.t0
        for k in range(k0, k1 + 1):
            i = int(p + q * k - t0)
            if i < 0 or i >= len(sc) or not ex[i]:
                continue
            s = sc[i]
            if s not in (1, 2) or (arms is not None and ar[i] not in arms):
                continue
            if s == 2:
                if fe[i]:
                    tp += 1
                else:
                    fn += 1
            else:
                if fe[i]:
                    fp += 1
                else:
                    tn += 1
        return tp, fn, fp, tn


def fit_lattice(rnd, q0=Q_MS):
    """The period near q0 and the phase that agree best with one round. The period's range is the three fits of 31 October (1000.0098-1000.0105 ms) +- 0.005 ms:
    one round holds too few constraints to find it from scratch."""
    best = None
    for dq in range(-6, 7):
        q = q0 + dq * 0.001
        for pp in range(0, 1000, 4):
            p = rnd.t0 + pp
            tp, fn, fp, tn = rnd.score(p, q)
            # true-positive heavy: a lattice that never lands in a gap must not win on its kernels
            sc = tp - 3 * fp - fn
            if best is None or sc > best[0]:
                best = (sc, p, q)
    _, p0, q0b = best
    for dq in range(-2, 3):
        q = q0b + dq * 0.0005
        for pp in range(-8, 9):
            p = p0 + pp
            tp, fn, fp, tn = rnd.score(p, q)
            sc = tp - 3 * fp - fn
            if sc > best[0]:
                best = (sc, p, q)
    return best[1], best[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundir")
    ap.add_argument("--predictions", default=os.path.join(HERE, "predictions.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    P = json.load(open(a.predictions))
    runs = load(a.rundir)
    arms = {}
    per_round = {}
    left_out = []
    bad_rc = 0
    for r in runs:
        for pv in process_view(r):
            if pv["rc"] != 0:
                bad_rc += 1
                continue
            if pv["limit"]:
                left_out.append(r["run"])
                continue
            s = arms.setdefault(r["arm"], {"processes": 0, "hb": 0.0, "falls": 0, "kernel_falls": 0, "inside": 0, "kernel_hb": 0.0, "durations": [], "n_kernels": 0, "since_reset": []})
            s["processes"] += 1
            s["hb"] += pv["hb"]
            s["falls"] += len(pv["falls"])
            s["kernel_falls"] += pv["kernel_falls"]
            s["inside"] += pv["inside"]
            s["kernel_hb"] += pv["kernel_hb"]
            s["n_kernels"] += pv["n_kernels"]
            s["durations"] += [f["at600_s"] for f in pv["falls"] if f["at600_s"] is not None]
            s["since_reset"] += [f["since_reset_ms"] for f in pv["falls"] if f["since_reset_ms"] is not None]
            pr = per_round.setdefault(f"{r['arm']}/{r['round']}", {"hb": 0.0, "falls": 0})
            pr["hb"] += pv["hb"]
            pr["falls"] += len(pv["falls"])
    out = {"experiment": "E100", "arms": {}, "per_round": {k: {"hb": round(v["hb"], 1), "falls": v["falls"]} for k, v in per_round.items()}, "left_out_limit": left_out, "nonzero_rc": bad_rc, "rules": {}}
    print("arm    processes  heartbeats  falls  kernel-channel  falls per heartbeat  predicted (w 1.3, 2.0, 2.5)  band at these heartbeats  in band")
    def band(arm, hb):
        ar = P["arms"][arm]["falls_per_heartbeat"]
        return poisson_lo(ar["1.3"] * hb), poisson_hi(ar["2.5"] * hb)
    for arm in ("A0", "A5", "A20", "A100", "N", "R"):
        s = arms.get(arm)
        if not s:
            continue
        ar = P["arms"][arm]["falls_per_heartbeat"]
        lo, hi = band(arm, s["hb"]) if arm != "N" else (0, 0)
        inb = lo <= s["falls"] <= hi
        out["arms"][arm] = {"processes": s["processes"], "heartbeats": round(s["hb"], 1), "falls": s["falls"], "kernel_falls": s["kernel_falls"], "rate": round(s["falls"] / s["hb"], 5) if s["hb"] else None,
                            "predicted": ar, "predicted_falls_at_w2": round(ar["2.0"] * s["hb"], 2), "band": [lo, hi], "in_band": inb, "inside_kernel": s["inside"], "kernel_hb": round(s["kernel_hb"], 1), "n_kernels": s["n_kernels"]}
        print(f"{arm:6s} {s['processes']:9d} {s['hb']:11.1f} {s['falls']:6d} {s['kernel_falls']:15d} {100 * s['falls'] / s['hb'] if s['hb'] else 0:18.2f}%  {100 * ar['1.3']:.2f} {100 * ar['2.0']:.2f} {100 * ar['2.5']:.2f}%           {lo}-{hi}                     {inb}")
    print("per round:", json.dumps(out["per_round"]))
    print("left out for a limit in reach:", left_out, "; processes with a nonzero rc:", bad_rc)
    # D1
    need = ("A100", "A20", "A0")
    if all(x in out["arms"] for x in need):
        ok = all(out["arms"][x]["in_band"] for x in need)
        out["rules"]["D1"] = {"verdict": "PASS" if ok else "FAIL", "counts": {x: out["arms"][x]["falls"] for x in need}, "bands": {x: out["arms"][x]["band"] for x in need}}
    else:
        out["rules"]["D1"] = {"verdict": "NOT SCORED", "why": "an arm did not run"}
    # D2
    if "N" in out["arms"]:
        n = out["arms"]["N"]
        out["rules"]["D2"] = {"verdict": "NOT SCORED" if n["kernel_hb"] < 100 else ("PASS" if n["inside_kernel"] == 0 else "FAIL"), "inside_kernel": n["inside_kernel"], "heartbeats_inside_kernels": n["kernel_hb"]}
    else:
        out["rules"]["D2"] = {"verdict": "NOT SCORED", "why": "N did not run"}
    # D3: across the rounds
    r1 = [r for r in runs if r["round"] == 1]
    r2 = [r for r in runs if r["round"] == 2]
    if r1 and r2:
        R1, R2 = Round(r1), Round(r2)
        pa, qa = fit_lattice(R1)
        pb, qb = fit_lattice(R2)
        test = {3, 4}  # A20, A100
        t12 = R2.score(pa, qa, test)
        t21 = R1.score(pb, qb, test)
        tp, fn, fp, tn = [t12[i] + t21[i] for i in range(4)]
        sens = tp / (tp + fn) if tp + fn else None
        spec = tn / (tn + fp) if tn + fp else None
        ok = sens is not None and spec is not None and sens >= 0.90 and spec >= 0.95
        out["rules"]["D3"] = {"verdict": "PASS" if ok else "FAIL", "table_tp_fn_fp_tn": [tp, fn, fp, tn], "sensitivity": round(sens, 3) if sens is not None else None, "specificity": round(spec, 3) if spec is not None else None,
                              "lattice_round1": {"p_ms": pa, "q_ms": round(qa, 4)}, "lattice_round2": {"p_ms": pb, "q_ms": round(qb, 4)}, "fit1_test2": t12, "fit2_test1": t21,
                              "all_arms_fit1_test2": R2.score(pa, qa), "all_arms_fit2_test1": R1.score(pb, qb), "same_lattice_mod_q_ms": round((pb - pa) % qa, 2)}
        print("D3 lattice: round 1 period", round(qa, 4), "round 2 period", round(qb, 4), "table (gap fell, gap no fall, kernel fell, kernel no fall):", (tp, fn, fp, tn))
    else:
        out["rules"]["D3"] = {"verdict": "NOT SCORED", "why": "one round only"}
    # D4
    all_d = [d for s in arms.values() for d in s["durations"]]
    if all_d:
        med = st.median(all_d)
        a100 = (arms.get("A100") or {}).get("durations") or []
        long_share = sum(1 for d in a100 if d >= 1.9) / len(a100) if a100 else None
        ok = 1.0 <= med <= 1.25 and long_share is not None and 0.03 <= long_share <= 0.35
        out["rules"]["D4"] = {"verdict": "PASS" if ok else "FAIL", "median_at600_s": round(med, 3), "n": len(all_d), "a100_share_ge_1p9_s": round(long_share, 3) if long_share is not None else None, "a100_n": len(a100)}
    else:
        out["rules"]["D4"] = {"verdict": "NOT SCORED", "why": "no falls"}
    # D5
    if "R" in out["arms"] and "A20" in out["arms"]:
        n = out["arms"]["R"]
        lo, hi = band("A20", n["heartbeats"])
        out["rules"]["D5"] = {"verdict": "PASS" if lo <= n["falls"] <= hi else "FAIL", "falls": n["falls"], "band": [lo, hi], "since_reset_ms_at_falls": arms["R"]["since_reset"]}
    else:
        out["rules"]["D5"] = {"verdict": "NOT SCORED", "why": "R did not run"}
    print(json.dumps(out["rules"], indent=1))
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
