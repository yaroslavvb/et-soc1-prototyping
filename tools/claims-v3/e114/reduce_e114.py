#!/usr/bin/env python3
"""E114 (Q133): the registered reduction -- card 0's fp16 and int8 sustained cells from three passes, E84's single
runs scored against them, the zeros-over-heavy speed ratios with intervals, the limiting test, and aifoundry2 beside.

    python3 reduce_e114.py <RUNDIR> [--pred predictions-e114.json] [--out results.json] > reduce.txt

PER RUN, the metrics are E84's, unchanged: reduce_hpl.run_metrics (E64's and E80's registered reduction) and
reduce_e84.run_extra (card 0's idle level, the last-40-s labels, the sustained limit), imported and called exactly as
reduce_e84.py calls them. The quantities read here:
  sus_rate_t      the kernel's own operations over its own wall time, launches that start in the last 40 s of the
                  work (TFLOPS for fp16, TOPS for int8): "the sustained rate", the speed the rules use
  sus_mhz_all     the mean sampled clock over the last 40 s, every in-work sample (E84's sustained clock)
  sus_mhz_nonramp, sus_w_mean (board W), sus_die_mean, sus_die_max, sus_ramp_share, sus_limit, idle_w, gate

PER KIND (the five of predictions-e114.json): n runs, mean, sd, the 95% interval t(0.975, n-1) x sd / sqrt(n), and the
95% prediction interval for one new run, t(0.975, n-1) x sd x sqrt(1 + 1/n).

PER FORMAT: rho = the mean over passes of rate(zeros, pass p) / rate(heavy, pass p), heavy = randn for fp16, full for
int8, over the passes where both ran; its 95% interval as above over the pass ratios.

THE RULES (frozen in predictions-e114.json with E114.md):
  E114-R1  E84's single run of each kind inside E114's 95% prediction interval, on the sustained rate: PASS when
           >= 4 of the 5 kinds are inside; FAIL when >= 2 scored kinds (n >= 3) are outside; else UNDER-RESOLVED
                                                                                                              (primary)
  E114-R2  rho16's 95% interval: PASS when its lower end >= 1.15, FAIL when its upper end < 1.15, else
           INCONCLUSIVE; UNDER-RESOLVED below three pairs                                                    (primary)
  E114-R3  rho8's reading: FASTER (lower end > 1), SLOWER (upper end < 1), SAME_WITHIN_BAR (holds 1 and lies
           inside [0.98, 1.02]), else INCONCLUSIVE; UNDER-RESOLVED below three pairs; scored RIGHT when it equals
           the frozen reading                                                                                 (primary)
  E114-R4  each run's sustained limit equals E84's for its kind: PASS when <= 1 of >= 14 runs differs, FAIL when
           >= 2 differ, else UNDER-RESOLVED                                                                   (primary)
  E114-S1  rho(card 0) - rho(aifoundry2, ratio of mean rates over E80/E83/E87/E96): ALIKE inside +-bar (fp16 0.05,
           int8 0.02), DIFFERENT when the interval excludes 0, else INCONCLUSIVE                             (secondary)
Context, never a verdict: the cells' other quantities with intervals, pass-paired zeros-minus-heavy clocks, each run's
die against E84's die line, rho as a ratio of means, the idle level and the gates.
"""
import argparse
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kspeed", "e84"))
sys.path.insert(0, os.path.join(HERE, "..", "hpl"))
import reduce_e84 as E  # noqa: E402  (E84's registered per-run code, unchanged)
import reduce_hpl as R  # noqa: E402

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086}
HEAVY = {"fp16": "fp16/randn", "int8": "int8/full"}
ZEROS = {"fp16": "fp16/zeros", "int8": "int8/zeros"}
QTY = {"rate": "sus_rate_t", "mhz": "sus_mhz_all", "mhz_nonramp": "sus_mhz_nonramp", "w": "sus_w_mean",
       "die": "sus_die_mean"}


def t975(df):
    return T975.get(df, 1.96) if df >= 1 else None


def summ(xs):
    xs = [x for x in xs if x is not None]
    n = len(xs)
    out = {"n": n, "runs": xs, "mean": round(st.mean(xs), 4) if n else None}
    if n >= 2:
        sd = st.stdev(xs)
        t = t975(n - 1)
        out.update({"sd": round(sd, 4), "ci95": round(t * sd / math.sqrt(n), 4),
                    "pi95": round(t * sd * math.sqrt(1 + 1 / n), 4)})
    return out


def per_run(rundirs):
    runs = []
    for rd in rundirs:
        sess, rr, launches, q0 = R.load_session(rd)
        start_cfg = next(((q.get("config") or {}) for q in q0 if q.get("tag") == "start"), {}) or {}
        tdp_w = float(start_cfg.get("tdp_w") or 65)
        evs = R.sp_events_by_run(rd, sess, rr, q0)
        byrun = {}
        for L in launches:
            byrun.setdefault(L["run"], []).append(L)
        fit = R.fit_clock(evs, launches, sess)
        for r in rr:
            if r["block"] not in ("SUS", "SUS2"):
                continue
            rm = dict(r, block="SUS")
            m = R.run_metrics(rd, rm, byrun.get(r["run"], []), evs.get(r["run"]), fit)
            m["block"] = r["block"]
            m["session"] = os.path.basename(os.path.normpath(rd))
            m["dry"] = bool(sess.get("dry"))
            m["kind"] = E.kind_of(r["values"])
            m["config_after"] = (r.get("queries") or {}).get("config")
            m.update(E.run_extra(rd, r, byrun.get(r["run"], []), m, tdp_w))
            m.pop("trace", None)
            runs.append(m)
    return runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e114.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    P = json.load(open(a.pred))
    rules_p = P["rules"]
    runs = per_run(a.rundirs)
    kinds = list(P["kinds"])
    cells = {}
    for k in kinds:
        K = P["kinds"][k]
        su = sorted([m for m in runs if m["kind"] == k], key=lambda m: (m["rep"], m["run"]))
        c = {"kind": k, "type": K["type"], "n": len(su), "runs": [m["run"] for m in su], "reps": [m["rep"] for m in su],
             "limits": [m.get("sus_limit") for m in su], "ramp_share": [m.get("sus_ramp_share") for m in su],
             "die_max": [m.get("sus_die_max") for m in su], "die_start": [m.get("die_start") for m in su],
             "gate_reading_c": [(m.get("gate") or {}).get("reading", [None])[0] for m in su],
             "gate_held_s": [(m.get("gate") or {}).get("held_s") for m in su],
             "idle_w": [m.get("idle_w") for m in su], "idle_mhz": [m.get("idle_mhz") for m in su],
             "sus_counts": [m.get("sus_counts") for m in su], "sus_avg_w": [m.get("sus_avg_w") for m in su],
             "e84": {q: K.get(f"e84_sus_{q}") for q in ("rate", "mhz", "mhz_nonramp", "w", "die", "die_max",
                                                        "limit", "ramp_share")}}
        for q, key in QTY.items():
            c[q] = summ([m.get(key) for m in su])
            s, x = c[q], K.get(f"e84_sus_{q}")
            if x is not None and s.get("pi95") is not None:
                s["e84"] = x
                s["e84_minus_mean"] = round(x - s["mean"], 4)
                s["e84_inside_pi95"] = abs(x - s["mean"]) <= s["pi95"]
        cells[k] = c

    def pairs(f):
        z = {m["rep"]: m for m in runs if m["kind"] == ZEROS[f]}
        h = {m["rep"]: m for m in runs if m["kind"] == HEAVY[f]}
        out = []
        for p in sorted(set(z) & set(h)):
            rz, rh = z[p].get("sus_rate_t"), h[p].get("sus_rate_t")
            if rz and rh:
                out.append({"pass": p, "zeros": rz, "heavy": rh, "ratio": round(rz / rh, 5),
                            "mhz_zeros_minus_heavy": round(z[p]["sus_mhz_all"] - h[p]["sus_mhz_all"], 1)})
        return out

    rho = {}
    for f in ZEROS:
        pr = pairs(f)
        s = summ([x["ratio"] for x in pr])
        if s.get("ci95") is not None:
            s["lo"], s["hi"] = round(s["mean"] - s["ci95"], 4), round(s["mean"] + s["ci95"], 4)
        z, h = cells[ZEROS[f]]["rate"], cells[HEAVY[f]]["rate"]
        rom = None
        if z.get("sd") is not None and h.get("sd") is not None:
            r0 = z["mean"] / h["mean"]
            se = r0 * math.sqrt((z["sd"] ** 2 / z["n"]) / z["mean"] ** 2 + (h["sd"] ** 2 / h["n"]) / h["mean"] ** 2)
            rom = {"ratio": round(r0, 4), "se_delta": round(se, 4)}
        rho[f] = dict(s, pairs=pr, ratio_of_means=rom, e84=P["e84_ratio_zeros_over_heavy_sus_rate"][f])

    rules = {}
    # E114-R1
    RP = rules_p["E114-R1"]
    rows, scored, inside = [], 0, 0
    for k in kinds:
        s = cells[k]["rate"]
        if s["n"] >= RP["min_runs_per_kind"] and s.get("pi95") is not None:
            scored += 1
            ok = s["e84_inside_pi95"]
            inside += 1 if ok else 0
            rows.append([k, s["n"], s["mean"], s["pi95"], s["e84"], s["e84_minus_mean"], "inside" if ok else "OUTSIDE"])
        else:
            rows.append([k, s["n"], s.get("mean"), s.get("pi95"), cells[k]["e84"]["rate"], None, "not scored"])
    out_n = scored - inside
    if inside >= RP["need_kinds"]:
        v = "PASS"
    elif out_n >= len(kinds) - RP["need_kinds"] + 1:
        v = "FAIL"
    else:
        v = "UNDER-RESOLVED"
    rules["E114-R1"] = {"rows": rows, "scored": scored, "inside": inside, "need": RP["need_kinds"], "verdict": v,
                        "expected": RP["expected"]}
    # E114-R2
    RP, s = rules_p["E114-R2"], rho["fp16"]
    if s["n"] < RP["min_pairs"]:
        v = "UNDER-RESOLVED"
    elif s["lo"] >= RP["bar"]:
        v = "PASS"
    elif s["hi"] < RP["bar"]:
        v = "FAIL"
    else:
        v = "INCONCLUSIVE"
    rules["E114-R2"] = {"rho16": s["mean"], "ci95": s.get("ci95"), "lo": s.get("lo"), "hi": s.get("hi"), "n_pairs": s["n"],
                        "bar": RP["bar"], "verdict": v, "expected": RP["expected"], "e84": s["e84"]}
    # E114-R3
    RP, s = rules_p["E114-R3"], rho["int8"]
    if s["n"] < RP["min_pairs"]:
        rd_ = "UNDER-RESOLVED"
    elif s["lo"] > 1:
        rd_ = "FASTER"
    elif s["hi"] < 1:
        rd_ = "SLOWER"
    elif s["lo"] >= 1 - RP["bar"] and s["hi"] <= 1 + RP["bar"]:
        rd_ = "SAME_WITHIN_BAR"
    else:
        rd_ = "INCONCLUSIVE"
    rules["E114-R3"] = {"rho8": s["mean"], "ci95": s.get("ci95"), "lo": s.get("lo"), "hi": s.get("hi"), "n_pairs": s["n"],
                        "bar": RP["bar"], "reading": rd_, "expected": RP["expected"],
                        "verdict": ("UNDER-RESOLVED" if rd_ == "UNDER-RESOLVED" else
                                    ("RIGHT" if rd_ == RP["expected"] else "WRONG")), "e84": s["e84"]}
    # E114-R4
    RP = rules_p["E114-R4"]
    mism, n_runs, rows = [], 0, []
    for k in kinds:
        want = P["kinds"][k]["e84_sus_limit"]
        for rn, lim in zip(cells[k]["runs"], cells[k]["limits"]):
            n_runs += 1
            rows.append([rn, lim, want])
            if lim != want:
                mism.append([rn, lim, want])
    if len(mism) > RP["max_mismatch"]:
        v = "FAIL"
    elif n_runs >= RP["min_runs"]:
        v = "PASS"
    else:
        v = "UNDER-RESOLVED"
    rules["E114-R4"] = {"runs": n_runs, "mismatches": mism, "rows": rows, "verdict": v, "expected": RP["expected"]}
    # E114-S1 (secondary)
    RP, S1 = rules_p["E114-S1"], {}
    for f in ZEROS:
        A = P["aifoundry2_pool"][f]
        ra2 = A["zeros_mean"] / A["heavy_mean"]
        se_a2 = ra2 * math.sqrt((A["zeros_sd"] ** 2 / A["n_zeros"]) / A["zeros_mean"] ** 2 +
                                (A["heavy_sd"] ** 2 / A["n_heavy"]) / A["heavy_mean"] ** 2)
        s = rho[f]
        if s["n"] >= 2 and s.get("sd") is not None:
            se_c0 = s["sd"] / math.sqrt(s["n"])
            df = min(s["n"], A["n_zeros"], A["n_heavy"]) - 1
            half = t975(df) * math.sqrt(se_c0 ** 2 + se_a2 ** 2)
            dl = s["mean"] - ra2
            lo, hi = dl - half, dl + half
            bar = RP["bars"][f]
            reading = ("ALIKE" if (lo >= -bar and hi <= bar) else ("DIFFERENT" if (lo > 0 or hi < 0) else
                                                                     "INCONCLUSIVE"))
            S1[f] = {"rho_card0": s["mean"], "rho_aifoundry2": round(ra2, 4), "se_card0": round(se_c0, 4),
                     "se_aifoundry2": round(se_a2, 4), "df": df, "delta": round(dl, 4), "ci95": round(half, 4),
                     "lo": round(lo, 4), "hi": round(hi, 4), "bar": bar, "reading": reading,
                     "expected": RP["expected"][f]}
        else:
            S1[f] = {"reading": "UNDER-RESOLVED", "expected": RP["expected"][f]}
    rules["E114-S1"] = S1

    # context, never a verdict
    L = P["e84_die_line"]
    resid = [m["sus_die_mean"] - (L["a_c"] + L["b_c_per_w"] * m["sus_w_mean"]) for m in runs
             if m.get("sus_die_mean") is not None and m.get("sus_w_mean") is not None]
    die_line = dict(summ([round(x, 3) for x in resid]), line=L)
    xs, ys = [m["sus_w_mean"] for m in runs], [m["sus_die_mean"] for m in runs]
    if len(xs) >= 3:
        mx, my = st.mean(xs), st.mean(ys)
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        die_line["e114_own_line"] = {"a_c": round(my - b * mx, 3), "b_c_per_w": round(b, 4), "n": len(xs)}
    cfgs = [m.get("config_after") for m in runs]
    ctx = {"die_vs_e84_line": die_line,
           "config_after_every_run": sorted({json.dumps({k: (c or {}).get(k) for k in ("tdp_w", "temp_threshold_c")})
                                             for c in cfgs}),
           "idle_w_range": [min(m["idle_w"] for m in runs if m.get("idle_w") is not None),
                            max(m["idle_w"] for m in runs if m.get("idle_w") is not None)] if runs else None}
    res = {"experiment": "E114", "card": "aifoundry1-c0", "pred_sha_note": "predictions-e114.json as frozen",
           "rules": rules, "cells": cells, "rho": rho, "context": ctx, "runs": runs}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=str)

    print("E114 on aifoundry1 card 0: sustained cells (last 40 s of nine 8 s processes), mean +- 95% interval "
          "[prediction interval]; E84's single run beside")
    for k, c in cells.items():
        r, mz = c["rate"], c["mhz"]
        print(f"{k:11s} n={c['n']} rate {r.get('mean')} +- {r.get('ci95')} [pi {r.get('pi95')}] runs {r['runs']} "
              f"e84 {c['e84']['rate']} | MHz {mz.get('mean')} +- {mz.get('ci95')} runs {mz['runs']} e84 "
              f"{c['e84']['mhz']} | W {c['w'].get('mean')} die {c['die'].get('mean')} max {c['die_max']} | "
              f"limits {c['limits']} ramp {c['ramp_share']}")
    for f, s in rho.items():
        print(f"rho {f}: {s.get('mean')} +- {s.get('ci95')} (pairs {[x['ratio'] for x in s['pairs']]}), "
              f"ratio of means {s['ratio_of_means']}, e84 {s['e84']}")
    for name, rr in rules.items():
        if name == "E114-S1":
            for f, x in rr.items():
                print(f"E114-S1 {f}: {x.get('reading')} (expected {x.get('expected', '')[:40]}) "
                      f"delta {x.get('delta')} +- {x.get('ci95')}")
            continue
        print(name, rr["verdict"], json.dumps({kk: vv for kk, vv in rr.items() if kk not in ("verdict", "rows")},
                                               default=str)[:500])
    print("die vs E84's line:", json.dumps({k: v for k, v in die_line.items() if k != "runs"}))
    print("config after every run:", ctx["config_after_every_run"], "idle W", ctx["idle_w_range"])


if __name__ == "__main__":
    main()
