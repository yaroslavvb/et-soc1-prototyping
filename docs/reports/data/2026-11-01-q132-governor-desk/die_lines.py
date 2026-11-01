#!/usr/bin/env python3
"""Q132(g), the heat path's drift, looking back. POST HOC, desk only, no card.

Every sustained run's (board W, die C) from the committed reductions, its clock time from runs.jsonl, and the room
proxies at that time from the boxes' own 5 s history (tools/lab/live/live-collector.py, ~/live/history on each box,
copied to <hist>/<box>/*.jsonl; a thinned copy is committed beside this script).

    die_lines.py <repo> <hist-dir> [--out die-lines.json] > die-lines.txt

No third-party modules.
"""
import argparse
import bisect
import glob
import json
import math
import os
import statistics as st
import time

os.environ["TZ"] = "America/Los_Angeles"
time.tzset()

SESSIONS = [
    # exp, box, card, results file, session dirs
    ("E64", "aifoundry2", 0, "2026-10-23-e64-horace-power-limit/results.json", ["2026-10-23-e64-horace-power-limit/s1", "2026-10-23-e64-horace-power-limit/s2"]),
    ("E69", "aifoundry2", 0, "2026-10-27-e69-governor-knob/results_hpl.json", ["2026-10-27-e69-governor-knob/s1", "2026-10-27-e69-governor-knob/s2", "2026-10-27-e69-governor-knob/s3"]),
    ("E80", "aifoundry2", 0, "2026-10-31-e80-kinds-speed/results.json", ["2026-10-31-e80-kinds-speed/s1"]),
    ("E83", "aifoundry2", 0, "2026-10-31-e83-kinds-speed-rest/results.json", ["2026-10-31-e83-kinds-speed-rest/s1"]),
    ("E87", "aifoundry2", 0, "2026-10-31-e87-real-tensors-speed/results.json", ["2026-10-31-e87-real-tensors-speed/s1"]),
    ("E84", "aifoundry1", 0, "2026-10-31-e84-speed-aifoundry1-card0/results.json", ["2026-10-31-e84-speed-aifoundry1-card0/s1"]),
]
BOXES = ("aifoundry1", "aifoundry2", "aifoundry3")


def fmt(ms):
    return time.strftime("%a %d %b %H:%M", time.localtime(ms / 1000.0))


class Hist:
    """One box's 5 s records: t (ms) sorted; temps and cards."""

    def __init__(self, d):
        rows = []
        for f in sorted(glob.glob(os.path.join(d, "*.jsonl"))):
            for ln in open(f):
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                T = r.get("temps") or {}
                cards = {c["n"]: c for c in (r.get("cards") or [])}
                rows.append((r["t"], T.get("nvme"), T.get("nic"), T.get("cpu"), r.get("load"), cards))
        rows.sort(key=lambda x: x[0])
        self.rows = rows
        self.t = [x[0] for x in rows]

    def window(self, a, b):
        i, j = bisect.bisect_left(self.t, a), bisect.bisect_right(self.t, b)
        return self.rows[i:j]

    def proxy(self, a, b):
        w = self.window(a, b)
        out = {"n": len(w)}
        for k, name in ((1, "nvme"), (2, "nic"), (3, "cpu")):
            v = [x[k] for x in w if x[k] is not None]
            out[name] = round(st.mean(v), 2) if v else None
        lv = [x[4] for x in w if x[4] is not None]
        out["load"] = round(st.mean(lv), 2) if lv else None
        cards = {}
        for x in w:
            for n, c in x[5].items():
                if c.get("die") is not None and not c.get("held"):
                    cards.setdefault(n, []).append((c["die"], c.get("w")))
        out["cards"] = {n: {"die": round(st.mean(a0 for a0, _ in v), 2),
                            "w": round(st.mean(b0 for _, b0 in v if b0 is not None), 3), "n": len(v)}
                        for n, v in cards.items() if any(b0 is not None for _, b0 in v)}
        return out


def fit(xy):
    n = len(xy)
    mx, my = sum(x for x, _ in xy) / n, sum(y for _, y in xy) / n
    sxx = sum((x - mx) ** 2 for x, _ in xy)
    sxy = sum((x - mx) * (y - my) for x, y in xy)
    k = sxy / sxx if sxx else float("nan")
    a = my - k * mx
    res = [y - (a + k * x) for x, y in xy]
    rms = math.sqrt(sum(r * r for r in res) / n)
    se = math.sqrt(sum(r * r for r in res) / (n - 2) / sxx) if n > 2 and sxx else None
    return a, k, rms, se


def ols_r2(xs, ys):
    a, k, rms, se = fit(list(zip(xs, ys)))
    my = sum(ys) / len(ys)
    tot = sum((y - my) ** 2 for y in ys)
    return k, a, 1 - sum((y - (a + k * x)) ** 2 for x, y in zip(xs, ys)) / tot if tot else float("nan"), rms, se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("hist")
    ap.add_argument("--out")
    a = ap.parse_args()
    data = os.path.join(a.repo, "docs/reports/data")
    H = {b: Hist(os.path.join(a.hist, b)) for b in BOXES}
    runs = []
    for exp, box, card, res, dirs in SESSIONS:
        R = json.load(open(os.path.join(data, res)))
        times = {}
        for d in dirs:
            for ln in open(os.path.join(data, d, "runs.jsonl")):
                r = json.loads(ln)
                times[r["run"]] = (r.get("t_first_ms"), r.get("t_last_ms"), d.split("/")[-1], (r.get("gate") or {}).get("reading"))
        for r in R["runs"]:
            if not str(r.get("block", "")).startswith("SUS") or r.get("sus_w_mean") is None or r.get("sus_die_mean") is None:
                continue
            t = times.get(r["run"])
            if not t or not t[0]:
                continue
            runs.append({"exp": exp, "box": box, "card": card, "run": r["run"], "t0": t[0], "t1": t[1], "session": t[2],
                         "w": r["sus_w_mean"], "die": r["sus_die_mean"], "mhz": r.get("sus_mhz_mean"),
                         "gate": t[3], "values": r.get("values")})
    print(f"Sustained runs with W and die: {len(runs)}")
    # the free line per session, and the offset at a common slope
    a2 = [r for r in runs if r["box"] == "aifoundry2"]
    # the pooled within-session slope (aifoundry2), each session its own intercept
    mx = {}
    for e in {r["exp"] for r in a2}:
        v = [r for r in a2 if r["exp"] == e]
        mx[e] = (st.mean(r["w"] for r in v), st.mean(r["die"] for r in v))
    sxx = sum((r["w"] - mx[r["exp"]][0]) ** 2 for r in a2)
    sxy = sum((r["w"] - mx[r["exp"]][0]) * (r["die"] - mx[r["exp"]][1]) for r in a2)
    K = sxy / sxx
    print(f"pooled within-session slope on aifoundry2: {K:.4f} C/W over {len(a2)} runs")
    out = {"note": "post hoc, desk only", "pooled_k_c_per_w": round(K, 4), "sessions": {}, "runs": []}
    print("\nexp   box         start             end            n   free line (a + k W, rms C)        65.5C at W   offset at pooled k   first-gate idle (die, W)")
    base = None
    for exp, box, card, res, dirs in SESSIONS:
        v = [r for r in runs if r["exp"] == exp]
        if not v:
            continue
        xy = [(r["w"], r["die"]) for r in v]
        A, k, rms, se = fit(xy)
        off = st.mean(r["die"] - K * r["w"] for r in v)
        off_se = st.pstdev([r["die"] - K * r["w"] for r in v]) / math.sqrt(len(v))
        gate = sorted(v, key=lambda r: r["t0"])[0]["gate"]
        if exp == "E80":
            base = off
        out["sessions"][exp] = {"box": box, "card": card, "t0_ms": min(r["t0"] for r in v), "t1_ms": max(r["t1"] for r in v),
                                "n": len(v), "a_c": round(A, 3), "k_c_per_w": round(k, 4), "k_se": round(se, 4) if se else None,
                                "rms_c": round(rms, 3), "w_at_65_5": round((65.5 - A) / k, 2),
                                "offset_at_pooled_k_c": round(off, 3), "offset_se_c": round(off_se, 3),
                                "first_gate": gate}
        print(f"{exp:5s} {box:11s} {fmt(min(r['t0'] for r in v)):17s} {fmt(max(r['t1'] for r in v))[-5:]:6s} {len(v):4d}   "
              f"{A:6.2f} + {k:.4f} W, rms {rms:.2f}  (s.e. k {se if se else 0:.3f})   {(65.5 - A) / k:6.1f}     {off:7.2f} +- {off_se:.2f}     {gate}")
    # proxies, per run, from the other boxes (never the run's own box, whose case the card heats) and from its own box
    for r in runs:
        a0, b0 = r["t0"], r["t1"]
        r["proxy"] = {}
        for b in BOXES:
            r["proxy"][b] = H[b].proxy(a0, b0)
            r["proxy"][b + ":pre"] = H[b].proxy(a0 - 15 * 60 * 1000, a0)
    # the session view
    print("\nThe proxies by session (mean over the session's sustained-run spans; 'pre' = the 15 min before each run)")
    print("exp   | a2 nvme nic cpu (own box in E64-E87) | a3 nvme nic cpu load, die W | a1 nvme nic cpu load, c0 die W, c1 die W")
    for exp, box, card, res, dirs in SESSIONS:
        v = [r for r in runs if r["exp"] == exp]
        if not v:
            continue
        def m(b, key):
            q = [r["proxy"][b].get(key) for r in v if r["proxy"][b].get(key) is not None]
            return round(st.mean(q), 2) if q else None
        def c(b, n, key):
            q = [r["proxy"][b]["cards"][n][key] for r in v if n in r["proxy"][b]["cards"]]
            return round(st.mean(q), 2) if q else None
        s = out["sessions"][exp]
        s["proxy"] = {b: {"nvme": m(b, "nvme"), "nic": m(b, "nic"), "cpu": m(b, "cpu"), "load": m(b, "load")} for b in BOXES}
        s["proxy_cards"] = {"a3c0": {"die": c("aifoundry3", 0, "die"), "w": c("aifoundry3", 0, "w")},
                            "a1c0": {"die": c("aifoundry1", 0, "die"), "w": c("aifoundry1", 0, "w")},
                            "a1c1": {"die": c("aifoundry1", 1, "die"), "w": c("aifoundry1", 1, "w")},
                            "a2c0": {"die": c("aifoundry2", 0, "die"), "w": c("aifoundry2", 0, "w")}}
        print(f"{exp:5s} | {s['proxy']['aifoundry2']['nvme']} {s['proxy']['aifoundry2']['nic']} {s['proxy']['aifoundry2']['cpu']} "
              f"| {s['proxy']['aifoundry3']['nvme']} {s['proxy']['aifoundry3']['nic']} {s['proxy']['aifoundry3']['cpu']} l{s['proxy']['aifoundry3']['load']}, {s['proxy_cards']['a3c0']} "
              f"| {s['proxy']['aifoundry1']['nvme']} {s['proxy']['aifoundry1']['nic']} {s['proxy']['aifoundry1']['cpu']} l{s['proxy']['aifoundry1']['load']}, {s['proxy_cards']['a1c0']}, {s['proxy_cards']['a1c1']}")
    # the run-level regression on aifoundry2: residual of (die - K W) against each proxy
    print("\nRun-level, aifoundry2 only: (die - k W) against each proxy (k the pooled slope); r2 over the runs where the proxy exists.")
    print("A proxy from the same box is heated by the card itself, so it is shown only for its 'pre' window.")
    def proxies(r):
        p = {}
        for b in BOXES:
            tag = b.replace("aifoundry", "a")
            for win in (b, b + ":pre"):
                if b == "aifoundry2" and win == b:
                    continue
                suf = "" if win == b else "-pre"
                for key in ("nvme", "nic", "cpu"):
                    val = r["proxy"][win].get(key)
                    # the other box must be idle for its CPU and NVMe to read the room
                    if val is not None and (r["proxy"][win].get("load") or 0) < 2.0:
                        p[f"{tag}-{key}{suf}"] = val
                for n, cc in r["proxy"][win]["cards"].items():
                    p[f"{tag}c{n}-idle-w{suf}"] = cc["w"]
                    p[f"{tag}c{n}-idle-die{suf}"] = cc["die"]
        return p
    table = {}
    for r in a2:
        y = r["die"] - K * r["w"]
        for k0, val in proxies(r).items():
            table.setdefault(k0, []).append((val, y, r["exp"]))
    rows = []
    for k0, v in table.items():
        if len(v) < 20 or len({e for _, _, e in v}) < 3:
            continue
        xs, ys = [x for x, _, _ in v], [y for _, y, _ in v]
        if max(xs) - min(xs) < 1e-6:
            continue
        slope, icpt, r2, rms, se = ols_r2(xs, ys)
        rows.append((r2, k0, len(v), sorted({e for _, _, e in v}), slope, se, rms))
    rows.sort(reverse=True)
    print(f"{'proxy':22s} {'n':>4s} {'r2':>6s} {'slope C per unit':>18s} {'rms C':>7s}  sessions")
    for r2, k0, n, es, slope, se, rms in rows:
        print(f"{k0:22s} {n:4d} {r2:6.3f} {slope:9.3f} +- {se if se else 0:5.3f} {rms:7.3f}  {','.join(es)}")
    out["proxy_table"] = [{"proxy": k0, "n": n, "r2": round(r2, 3), "slope": round(slope, 4), "se": round(se, 4) if se else None,
                           "rms_c": round(rms, 3), "sessions": es} for r2, k0, n, es, slope, se, rms in rows]
    base_rms = st.pstdev([r["die"] - K * r["w"] for r in a2])
    print(f"\nrms of (die - k W) with one intercept and no proxy: {base_rms:.3f} C over {len(a2)} runs")
    out["no_proxy_rms_c"] = round(base_rms, 3)
    for r in runs:
        out["runs"].append({k: r[k] for k in ("exp", "box", "run", "t0", "t1", "w", "die", "mhz", "values")})
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
