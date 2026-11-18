#!/usr/bin/env python3
"""E212 a1c1-S2, README dated note 1 (fix-e212d, round Q208c, Tue 17 Nov 2026; post hoc, after the data commit 7dfba40b): the rest
before each run, the board power against the die, read for a step. It restates README note 7's post hoc reading by a stated
procedure; it decides nothing and changes nothing it reads. Python's own modules only; it imports nothing from the kit or the
reducer.

    python3 -I -B posthoc_note1_e212.py <session dir> <data JSON> [--others <data folder> ...] --json <out.json>

For this session and each folder given by --others (a data folder holding session/ and its data-e212-<s>.json):
  1. Every run that ran, in run order. From the registered reduction (the data JSON): p_rest_plain_w, the median board power over the
     last 5 s before the run's first process (a null run: before its window), and die_start_c, the mean die (the shires' mean,
     temp_c.minshire[0]) over the same 5 s. Both re-derived here from session/ (telemetry.jsonl.gz and each run.json, the reducer's
     window: samples from 5 s before to 1 ms before that start) and compared exactly; the script exits 1 on any mismatch.
  2. Three readings of the rest, each a least-squares line of board power on die over the runs:
       W1 (the stated procedure) the last 5 s: board median (p_rest_plain_w) on die mean (die_start_c);
       W2 the last 5 s: board mean on die mean;
       W3 the whole rest (from the run record's rest start to 1 ms before the first process): board mean on die mean.
     For each: the slope (W a degree), the intercept, the residuals' sd; the halves (the first floor(n/2) runs and the rest): their
     mean residuals, the difference (second less first), its standard error sqrt(s1^2/n1 + s2^2/n2) and their ratio; a scan of every
     split with at least 10 runs on each side: the largest |difference / its standard error|, where, and its difference.
  3. The residual means of W1 in blocks of 10 runs; the anchors' primary-view power over idle (dP_w) in run order, with their start
     die; the power state of the session's config reads at its start and end.
Prints the lines (posthoc-note1-e212-a1c1-S2.txt) and writes the JSON. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import bisect
import gzip
import json
import math
import os
import statistics
import sys

SCAN_MIN = 10


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def sdev(v):
    if len(v) < 2:
        return None
    m = sum(v) / len(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def linfit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return my - b * mx, b


def telemetry(sess):
    rows = []
    with gzip.open(os.path.join(sess, "telemetry.jsonl.gz"), "rt") as f:
        for ln in f:
            if not ln.startswith("{"):
                continue
            try:
                s = json.loads(ln)
            except ValueError:
                continue
            if s.get("t_ms") is None:
                continue
            die = ((s.get("temp_c") or {}).get("minshire") or [None])[0]
            rows.append((s["t_ms"] / 1000.0, s.get("board_w"), die))
    rows.sort(key=lambda r: r[0])
    return rows


def halves_and_scan(res, labels):
    n = len(res)
    h = n // 2
    a, b = res[:h], res[h:]
    sa, sb = sdev(a), sdev(b)
    se = math.sqrt(sa ** 2 / len(a) + sb ** 2 / len(b))
    d = mean(b) - mean(a)
    out = {"n_first": len(a), "n_second": len(b), "first_runs": f"{labels[0]}-{labels[h - 1]}",
           "second_runs": f"{labels[h]}-{labels[-1]}", "mean_first_w": mean(a), "mean_second_w": mean(b), "diff_w": d,
           "se_w": se, "ratio": d / se}
    best = None
    for k in range(SCAN_MIN, n - SCAN_MIN + 1):
        a, b = res[:k], res[k:]
        se_k = math.sqrt(sdev(a) ** 2 / len(a) + sdev(b) ** 2 / len(b))
        d_k = mean(b) - mean(a)
        if best is None or abs(d_k / se_k) > abs(best["ratio"]):
            best = {"split_before_run": labels[k], "n_first": k, "n_second": n - k, "diff_w": d_k, "se_w": se_k, "ratio": d_k / se_k}
    out["scan"] = best
    return out


def one_session(sess, data_json):
    D = json.load(open(data_json))
    tel = telemetry(sess)
    ts = [r[0] for r in tel]

    def between(lo, hi):
        return tel[bisect.bisect_left(ts, lo):bisect.bisect_right(ts, hi)]

    runs, mism = [], []
    for r in sorted(D["runs"], key=lambda q: q["i"]):
        if not r.get("ran"):
            continue
        rec = json.load(open(os.path.join(sess, "runs", r["run"], "run.json")))
        rest0 = rec["rest"]["t0_ms"] / 1000.0
        t_first = (rec["null"]["t0_ms"] if r["form"] == "null" else rec["procs"][0]["t0_ms"]) / 1000.0
        last5 = between(t_first - 5.0, t_first - 0.001)
        whole = between(rest0, t_first - 0.001)
        b5 = [x[1] for x in last5 if x[1] is not None]
        d5 = [x[2] for x in last5 if x[2] is not None]
        ball = [x[1] for x in whole if x[1] is not None]
        dall = [x[2] for x in whole if x[2] is not None]
        q = {"i": r["i"], "run": r["run"], "role": r["role"], "form": r["form"],
             "p_rest_plain_w": r.get("p_rest_plain_w"), "die_start_c": r.get("die_start_c"),
             "rd_board_med5_w": statistics.median(b5) if b5 else None, "rd_die_mean5_c": mean(d5),
             "board_mean5_w": mean(b5), "board_mean_rest_w": mean(ball), "die_mean_rest_c": mean(dall),
             "rest_s": round(t_first - rest0, 3), "n_last5": len(b5), "n_rest": len(ball)}
        if q["p_rest_plain_w"] != q["rd_board_med5_w"] or q["die_start_c"] != q["rd_die_mean5_c"]:
            mism.append(r["run"])
        if r["role"] == "anchor":
            v = (r.get("views") or {}).get(r.get("primary_view")) or {}
            q["anchor_dP_w"] = v.get("dP_w")
            q["primary_view"] = r.get("primary_view")
        runs.append(q)
    readings = {}
    for key, yk, xk, what in (("W1", "p_rest_plain_w", "die_start_c", "the last 5 s: board median (p_rest_plain_w) on die mean (die_start_c)"),
                              ("W2", "board_mean5_w", "rd_die_mean5_c", "the last 5 s: board mean on die mean"),
                              ("W3", "board_mean_rest_w", "die_mean_rest_c", "the whole rest: board mean on die mean")):
        sel = [q for q in runs if q[yk] is not None and q[xk] is not None]
        xs, ys = [q[xk] for q in sel], [q[yk] for q in sel]
        a, b = linfit(xs, ys)
        res = [y - (a + b * x) for x, y in zip(xs, ys)]
        hs = halves_and_scan(res, [q["run"][:3] for q in sel])
        readings[key] = dict({"what": what, "n": len(sel), "slope_w_per_c": b, "intercept_w": a, "residual_sd_w": sdev(res)}, **hs)
        if key == "W1":
            readings[key]["residual_means_by_10"] = [mean(res[k:k + 10]) for k in range(0, len(res), 10)]
    cfg = {}
    for end in ("start", "end"):
        p = os.path.join(sess, f"config-{end}.json")
        c = json.load(open(p)) if os.path.exists(p) else {}
        cfg[end] = {"power_state": c.get("power_state"), "power_state_name": c.get("power_state_name")}
    return {"session": D.get("session"), "card": D.get("card"), "runs_read": len(runs), "rederive_mismatches": mism,
            "config_power_state": cfg, "readings": readings,
            "anchors": [{"run": q["run"], "dP_w": q["anchor_dP_w"], "die_start_c": q["die_start_c"], "view": q["primary_view"]}
                        for q in runs if q["role"] == "anchor"],
            "die_start_range_c": [min(q["die_start_c"] for q in runs), max(q["die_start_c"] for q in runs)],
            "rest_board_range_w": [min(q["p_rest_plain_w"] for q in runs), max(q["p_rest_plain_w"] for q in runs)],
            "runs": runs}


def lines_of(S):
    L = []
    c = S["config_power_state"]
    L.append(f"session {S['session']} (card {S['card']}): power state {c['start']['power_state']} ({c['start']['power_state_name']}) "
             f"at the start, {c['end']['power_state']} ({c['end']['power_state_name']}) at the end (config-start.json, config-end.json)")
    L.append(f"  re-derived from session/: {S['runs_read']} runs; p_rest_plain_w and die_start_c equal the reduction's in "
             f"{S['runs_read'] - len(S['rederive_mismatches'])} of {S['runs_read']} ({len(S['rederive_mismatches'])} mismatches)")
    L.append(f"  die_start {S['die_start_range_c'][0]:.2f}-{S['die_start_range_c'][1]:.2f} C; p_rest_plain_w "
             f"{S['rest_board_range_w'][0]:.2f}-{S['rest_board_range_w'][1]:.2f} W")
    for k, R in S["readings"].items():
        sc = R["scan"]
        L.append(f"  {k} {R['what']}: n {R['n']}, slope {R['slope_w_per_c']:.4f} W/C, intercept {R['intercept_w']:.3f} W, "
                 f"residual sd {R['residual_sd_w']:.4f} W; halves {R['n_first']}/{R['n_second']} (runs {R['first_runs']}, "
                 f"{R['second_runs']}): {R['mean_first_w']:+.4f} / {R['mean_second_w']:+.4f} W, difference {R['diff_w']:+.4f} W, "
                 f"se {R['se_w']:.4f} W, ratio {R['ratio']:+.2f}; split scan (at least {SCAN_MIN} runs a side): largest |ratio| "
                 f"{abs(sc['ratio']):.2f} before run {sc['split_before_run']} ({sc['n_first']}/{sc['n_second']}), difference "
                 f"{sc['diff_w']:+.4f} W")
    L.append("  W1 residual means by 10 runs (W): " + " ".join(f"{v:+.3f}" for v in S["readings"]["W1"]["residual_means_by_10"]))
    an = S["anchors"]
    if an:
        L.append(f"  anchors ({an[0]['view']} dP_w, W; start die, C; run order): " +
                 "; ".join(f"{a['run'][:3]} {a['dP_w']:.3f} ({a['die_start_c']:.2f})" for a in an) +
                 f"; range {min(a['dP_w'] for a in an):.3f}-{max(a['dP_w'] for a in an):.3f}")
    return L


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("data")
    ap.add_argument("--others", nargs="*", default=[])
    ap.add_argument("--json", required=True)
    a = ap.parse_args(argv)
    out = {"what": "E212 a1c1-S2 README dated note 1 (post hoc): the rest before each run, board power against the die, read for a "
                   "step; the stated procedure (W1) and two other windows; other card-1 sessions beside it",
           "python": sys.version.split()[0], "interpreter": sys.executable, "sessions": []}
    L = ["posthoc_note1_e212.py (E212 a1c1-S2 README dated note 1; post hoc; reads only)"]
    bad = False
    for sess, dj in [(a.session, a.data)] + [(os.path.join(f, "session"), os.path.join(f, [x for x in sorted(os.listdir(f))
                                              if x.startswith("data-e212-") and x.endswith(".json")][0])) for f in a.others]:
        S = one_session(sess, dj)
        bad = bad or bool(S["rederive_mismatches"])
        out["sessions"].append(S)
        L.extend(lines_of(S))
    with open(a.json, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print("\n".join(L))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
