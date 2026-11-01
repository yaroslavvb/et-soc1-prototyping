#!/usr/bin/env python3
"""Q132(g): the die line between sessions, kind by kind, against the room at rest. POST HOC, desk only, no card.

Kind effects are about as large as the drift (the lines' rms is 0.3-0.7 C), so sessions are compared on the kinds they
share: for a kind in both, d = (die_B - k W_B) - (die_A - k W_A), with k the pooled within-session slope.

The room reading for a session is taken at rest: the 30 to 5 minutes before the session's first card use, from the
boxes' own 5 s history, with the card idle (a2's own reading, then the other boxes').

    drift_paired.py <repo> <hist-dir> [--out drift-paired.json] > drift-paired.txt
"""
import argparse
import glob
import json
import math
import os
import statistics as st
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import die_lines as DL

os.environ["TZ"] = "America/Los_Angeles"
time.tzset()


def kind_of(exp, r):
    v = r.get("values") or ""
    v = v.split("/")[-1].replace(".bin", "")
    t = r.get("type")
    return f"{t}/{v}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("hist")
    ap.add_argument("--out")
    a = ap.parse_args()
    data = os.path.join(a.repo, "docs/reports/data")
    H = {b: DL.Hist(os.path.join(a.hist, b)) for b in DL.BOXES}
    runs = {}
    first = {}
    for exp, box, card, res, dirs in DL.SESSIONS:
        R = json.load(open(os.path.join(data, res)))
        times = {}
        for d in dirs:
            rows = [json.loads(ln) for ln in open(os.path.join(data, d, "runs.jsonl"))]
            for r in rows:
                times[r["run"]] = (r.get("t_first_ms"), r.get("t_last_ms"))
                if r.get("t_first_ms"):
                    first[exp] = min(first.get(exp, 1e18), r["t_first_ms"])
            # the smoke before a session counts as card use
        for r in R["runs"]:
            if not str(r.get("block", "")).startswith("SUS") or r.get("sus_w_mean") is None:
                continue
            if exp == "E64" and r.get("minions") not in (1024, None):
                continue
            t = times.get(r["run"])
            if not t or not t[0]:
                continue
            k = kind_of(exp, r)
            runs.setdefault(exp, []).append({"run": r["run"], "kind": k, "w": r["sus_w_mean"], "die": r["sus_die_mean"],
                                             "die_start": r.get("die_start"), "t0": t[0], "t1": t[1], "mhz": r.get("sus_mhz_mean"),
                                             "label": r.get("label")})
    K = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "die-lines.json")))["pooled_k_c_per_w"]
    print(f"k = {K} C per W (pooled within-session slope on aifoundry2, die-lines.txt)")
    exps = ["E64", "E69", "E80", "E83", "E87"]
    # kinds per session
    for e in exps:
        print(e, "kinds:", sorted({r["kind"] for r in runs[e]}))
    # pairs against E80
    out = {"k": K, "pairs": {}, "rest": {}}
    print("\nPaired on shared kinds: (die - k W) in B minus in A; each kind's runs averaged first.")

    def kindmean(e):
        d = {}
        for r in runs[e]:
            d.setdefault(r["kind"], []).append(r["die"] - K * r["w"])
        return {k: st.mean(v) for k, v in d.items()}

    KM = {e: kindmean(e) for e in exps}
    for A, B in (("E80", "E64"), ("E80", "E83"), ("E80", "E87"), ("E83", "E87"), ("E83", "E64"), ("E87", "E64"), ("E80", "E69"), ("E87", "E69")):
        sh = sorted(set(KM[A]) & set(KM[B]))
        if not sh:
            print(A, B, "no shared kinds")
            continue
        d = [KM[B][k] - KM[A][k] for k in sh]
        m = st.mean(d)
        se = st.stdev(d) / math.sqrt(len(d)) if len(d) > 1 else None
        print(f"{B} - {A}: {m:+.2f} C" + (f" +- {se:.2f} s.e." if se else "") + f" over {len(sh)} kinds: " + ", ".join(f"{k} {x:+.2f}" for k, x in zip(sh, d)))
        out["pairs"][f"{B}-{A}"] = {"mean_c": round(m, 3), "se_c": round(se, 3) if se else None, "n": len(sh), "by_kind": {k: round(x, 3) for k, x in zip(sh, d)}}
    # the room at rest before each session's first run
    print("\nThe room at rest, 30 to 5 min before each session's first run (a card held or above its idle bar is left out)")
    print("exp   first run          a2 W   a2 die  a2 nic a2 nvme a2 cpu | a3 W   a3 die a3 nic a3 nvme | a1c0 W a1c0 die a1c1 W a1 nic a1 nvme")
    for e in exps + ["E84"]:
        t0 = first[e]
        rest = {}
        for b in DL.BOXES:
            rest[b] = H[b].proxy(t0 - 30 * 60000, t0 - 5 * 60000)
        out["rest"][e] = {"t0_ms": t0, **{b: rest[b] for b in DL.BOXES}}
        def c(b, n, key):
            q = rest[b]["cards"].get(n)
            return q[key] if q else None
        print(f"{e:5s} {DL.fmt(t0):17s}  {c('aifoundry2', 0, 'w')} {c('aifoundry2', 0, 'die')} {rest['aifoundry2']['nic']} {rest['aifoundry2']['nvme']} {rest['aifoundry2']['cpu']} "
              f"| {c('aifoundry3', 0, 'w')} {c('aifoundry3', 0, 'die')} {rest['aifoundry3']['nic']} {rest['aifoundry3']['nvme']} (load {rest['aifoundry3']['load']}) "
              f"| {c('aifoundry1', 0, 'w')} {c('aifoundry1', 0, 'die')} {c('aifoundry1', 1, 'w')} {rest['aifoundry1']['nic']} {rest['aifoundry1']['nvme']} (load {rest['aifoundry1']['load']})")
    # the session-level test: the line's shift on shared kinds against each rest reading's shift, all from E80
    print("\nThe line's shift from E80 (shared kinds, above) against each reading's shift from E80 at rest. Through the origin, weighted by the shift's s.e.")
    print("E80 is a common baseline, so the three points are not independent; n = 4 sessions; post hoc.")
    shifts = {e: out["pairs"][f"{e}-E80"] for e in ("E83", "E87", "E64")}
    def reading(e, b, key, n=None):
        r = out["rest"][e][b]
        if n is None:
            return r.get(key)
        c = r["cards"].get(n)
        return c[key] if c else None
    cand = [("a2 card idle die", "aifoundry2", "die", 0), ("a2 card idle W", "aifoundry2", "w", 0), ("a2 NIC", "aifoundry2", "nic", None), ("a2 NVMe", "aifoundry2", "nvme", None), ("a2 CPU", "aifoundry2", "cpu", None),
            ("a3 NIC", "aifoundry3", "nic", None), ("a3 NVMe", "aifoundry3", "nvme", None), ("a1 NIC", "aifoundry1", "nic", None), ("a1 NVMe", "aifoundry1", "nvme", None),
            ("a1c0 idle die", "aifoundry1", "die", 0), ("a1c0 idle W", "aifoundry1", "w", 0), ("a1c1 idle W", "aifoundry1", "w", 1)]
    print(f"{'reading':16s} {'E83':>7s} {'E87':>7s} {'E64':>7s}  {'slope':>7s} {'s.e.':>6s} {'chi2':>6s}   slope on 31 Oct alone, and E64 predicted by it (measured +{shifts['E64']['mean_c']:.2f})")
    table = {}
    for name, b, key, n in cand:
        base = reading("E80", b, key, n)
        dx = {e: (reading(e, b, key, n) - base) if reading(e, b, key, n) is not None and base is not None else None for e in shifts}
        if any(v is None for v in dx.values()):
            continue
        sw = sum(dx[e] ** 2 / shifts[e]["se_c"] ** 2 for e in shifts)
        sl = sum(dx[e] * shifts[e]["mean_c"] / shifts[e]["se_c"] ** 2 for e in shifts) / sw
        se = 1 / math.sqrt(sw)
        chi = sum((shifts[e]["mean_c"] - sl * dx[e]) ** 2 / shifts[e]["se_c"] ** 2 for e in shifts)
        sw2 = sum(dx[e] ** 2 / shifts[e]["se_c"] ** 2 for e in ("E83", "E87"))
        sl2 = sum(dx[e] * shifts[e]["mean_c"] / shifts[e]["se_c"] ** 2 for e in ("E83", "E87")) / sw2 if sw2 else float("nan")
        se2 = 1 / math.sqrt(sw2) if sw2 else float("nan")
        print(f"{name:16s} {dx['E83']:+7.2f} {dx['E87']:+7.2f} {dx['E64']:+7.2f}  {sl:7.3f} {se:6.3f} {chi:6.2f}   {sl2:+.3f} +- {se2:.3f}, predicts {sl2 * dx['E64']:+.2f} +- {se2 * abs(dx['E64']):.2f}")
        table[name] = {"dx": {k: round(v, 3) for k, v in dx.items()}, "slope": round(sl, 4), "se": round(se, 4), "chi2": round(chi, 3), "slope_31oct": round(sl2, 4), "se_31oct": round(se2, 4), "predict_e64": round(sl2 * dx["E64"], 3)}
    out["session_level"] = table
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
