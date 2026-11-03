#!/usr/bin/env python3
"""E143 (Q138): the registered reduction and scoring. Standard library only.

    python3 tools/claims-v3/e143/reduce_e143.py <RUNDIR> [<RUNDIR> ...] [--pred predictions-e143.json] [--out results.json] > reduce.txt

PER RUN (block BURST only), E80's metrics, imported and called unchanged: reduce_hpl.run_metrics (E64's registered reduction: the sampler trace placed
on the work windows, die_start = the first die reading inside the work, die_max its largest) and reduce_kspeed.burst_extra (burst_mhz = the mean
sampled clock from 1.5 s after the first launch to the end of the work, burst_w = the mean board W over the same samples, c_w, burst_rate). These are
the quantities M7's aifoundry2 term was fitted on (E80's and E83's results.json cells: burst_mhz, burst_w, burst_die_start, burst_die_max).
A run counts if every launch of it ran and passed its check (launch_ok == launch_n >= 1) and burst_mhz, burst_w, die_start and die_max exist.

PER TILE, over its counted passes (the pass is the unit of replication): burst_mhz, burst_w and the die rise (die_max - die_start) are the means of the
passes; the burst D is the mean over passes of burst_w less the burst_w of the same type's zeros anchor IN THE SAME PASS (M7's burst_D_w: board W less
zeros' board W in their own burst). A tile with fewer than 2 counted passes is left out and named.

THE RULES (E143.md "Decision rules"), each tile's group frozen in predictions-e143.json (governed: M7 predicts the burst below 795 MHz):
  E143-F1  clock, governed tiles (19, at least 8): rms(measured - M7) against the 2.5-97.5% range of the rms of n errors drawn with replacement
           from M7's end-to-end clock errors on the kinds bursts it predicted governed (17 rows): PASS at or below the 97.5% point, FAIL above;
           below the 2.5% point "better than the reference says"
  E143-F2  clock, pinned tiles (17, at least 8): as F1, the 39 rows predicted pinned
  E143-F3  clock, all 36: coverage of M7's frozen 95% band (+-21.3 MHz, 800 the top): PASS if at least the 2.5% point of Binomial(n, 0.95)
  E143-W1  board W at the clock, governed tiles: as F1 with the governed rows' board errors
  E143-W2  board W, pinned tiles: as F2 with the pinned rows' board errors
  E143-W3  board W, all 36: coverage of +-3.37 W
  E143-H1  die rise, all 36 (at least 10): as F1 with the burst heat law's 112 leave-one-kind-out residuals (0.6845 C rms)
  E143-H3  die rise, all 36: coverage of +-1.41 C
  E143-R0  the card's drift check: E80's three replicate tiles each within 25 MHz and 3.37 W of E80's and E83's mean cell (a diagnostic: it
           qualifies, never changes, the verdicts above)
Fewer than 2 counted passes in all: every rule NOT SCORED. REPORTED, never a verdict: M6's and M5's rms on every set beside M7's and the paired
difference with a bootstrap interval over tiles; the burst D against each model's burst_D_w and its band; the heat law on the measured board W
(the rise less 0.140 C/W x (measured burst W - 21.5 W)); the same sets split by the measured clock; priority-1 tiles alone; per format; every pass
scored on its own; the kernel's own clock (its cycles over its wall time from 1.5 s on, burst_extra's burst_ghz_kernel: E136's cross-check of the
sampled clock); the session's peaks.
"""
import argparse
import glob
import gzip
import json
import math
import os
import random
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "hpl"))
sys.path.insert(0, os.path.join(HERE, "..", "kspeed"))
import e143_common as C  # noqa: E402
import reduce_hpl as R  # noqa: E402
import reduce_kspeed as RK  # noqa: E402

KSPEED_PRED = os.path.join(HERE, "..", "kspeed", "predictions.json")
MODELS = ("M7", "M6", "M5")


def mean(xs):
    xs = [x for x in xs if x is not None]
    return st.mean(xs) if xs else None


def rnd(x, n=3):
    return None if x is None else round(x, n)


def collect(rundirs):
    """every BURST run's E80 metrics, with its session and pass"""
    B = {int(k): v for k, v in json.load(open(KSPEED_PRED))["constants"]["B_registered_w"].items()}
    runs = []
    for rd in rundirs:
        sess, rr, launches, q0 = R.load_session(rd)
        evs = R.sp_events_by_run(rd, sess, rr, q0)
        byrun = {}
        for L in launches:
            byrun.setdefault(L["run"], []).append(L)
        fit = R.fit_clock(evs, launches, sess)
        for r in rr:
            if r["block"] != "BURST":
                continue
            m = R.run_metrics(rd, r, byrun.get(r["run"], []), evs.get(r["run"]), fit)
            m["session"] = os.path.basename(os.path.normpath(rd))
            m["dry"] = bool(sess.get("dry"))
            m["pass"] = r.get("rep")
            m.update(RK.burst_extra(m, byrun.get(r["run"], []), B))
            m["counted"] = bool(m.get("launch_n") and m.get("launch_ok") == m.get("launch_n") and None not in
                                (m.get("burst_mhz"), m.get("burst_w"), m.get("die_start"), m.get("die_max")))
            m["rise_c"] = (m["die_max"] - m["die_start"]) if m["counted"] else None
            runs.append(m)
    return runs


def peaks(rundirs):
    """the safety record (no rule reads it): the highest board reading and die readings in every sampler line of every session"""
    out = {"board_max_w": None, "board_run": None, "die_mean_max_c": None, "die_high_max_c": None, "samples": 0}
    for rd in rundirs:
        for p in sorted(glob.glob(os.path.join(rd, "tel", "*.jsonl")) + glob.glob(os.path.join(rd, "tel", "*.jsonl.gz"))):
            op = gzip.open if p.endswith(".gz") else open
            with op(p, "rt") as f:
                for ln in f:
                    if not ln.startswith("{"):
                        continue
                    try:
                        d = json.loads(ln)
                    except ValueError:
                        continue
                    out["samples"] += 1
                    w = d.get("board_w")
                    ms = (d.get("temp_c") or {}).get("minshire") or [None, None, None]
                    if w is not None and (out["board_max_w"] is None or w > out["board_max_w"]):
                        out["board_max_w"], out["board_run"] = w, f"{os.path.basename(os.path.normpath(rd))}/{os.path.basename(p)}"
                    if ms[0] is not None and (out["die_mean_max_c"] is None or ms[0] > out["die_mean_max_c"]):
                        out["die_mean_max_c"] = ms[0]
                    if len(ms) > 2 and ms[2] is not None and (out["die_high_max_c"] is None or ms[2] > out["die_high_max_c"]):
                        out["die_high_max_c"] = ms[2]
    return out


def cells_of(runs, P, passes=None):
    """per pool tile and per replicate: the means over counted passes (passes: restrict to these pass numbers)"""
    lab2name = {t["label"]: n for n, t in P["tiles"].items()}
    by = {}
    for m in runs:
        if not m["counted"] or (passes is not None and m["pass"] not in passes):
            continue
        by.setdefault(m["label"], {})[m["pass"]] = m           # one counted run per label and pass (a rerun would replace it: none is planned)
    zeros = {t["type"]: t["label"] for t in P["tiles"].values() if t["anchor"] and t["models"]["M7"]["burst_D_w"] == 0.0}
    cells = {}
    for lab, per in by.items():
        ps = sorted(per)
        c = {"label": lab, "passes": ps, "n": len(ps),
             "burst_mhz_runs": [per[p]["burst_mhz"] for p in ps], "burst_w_runs": [per[p]["burst_w"] for p in ps],
             "rise_runs": [per[p]["rise_c"] for p in ps], "die_start_runs": [per[p]["die_start"] for p in ps], "die_max_runs": [per[p]["die_max"] for p in ps],
             "p800_w_runs": [per[p].get("p800_w") for p in ps], "c_w_runs": [per[p].get("c_w") for p in ps], "rate_runs": [per[p].get("burst_rate") for p in ps],
             "first_down": [per[p].get("first_down_kind") for p in ps],
             "kernel_mhz_runs": [None if per[p].get("burst_ghz_kernel") is None else round(per[p]["burst_ghz_kernel"] * 1000, 1) for p in ps]}
        c["burst_mhz"] = rnd(mean(c["burst_mhz_runs"]), 2)
        c["burst_w"] = rnd(mean(c["burst_w_runs"]), 3)
        c["rise_c"] = rnd(mean(c["rise_runs"]), 3)
        c["kernel_mhz"] = rnd(mean(c["kernel_mhz_runs"]), 1)
        name = lab2name.get(lab)
        if name is not None:
            t = P["tiles"][name]
            zl = zeros.get(t["type"])
            dz = [per[p]["burst_w"] - by[zl][p]["burst_w"] for p in ps if zl in by and p in by[zl]]
            c["D_runs"] = [round(x, 3) for x in dz]
            c["D_w"] = rnd(mean(dz), 3)
            c["name"], c["type"], c["group"], c["priority"], c["anchor"] = name, t["type"], t["group"], t["priority"], t["anchor"]
        cells[lab] = c
    return cells


def verdict(x, lo, hi):
    if x is None or hi is None:
        return "NOT SCORED"
    if x > hi:
        return "FAIL"
    if x < lo:
        return "PASS (better than the reference says)"
    return "PASS"


def paired_boot(a, b, draws=5000, seed=1431):
    """the 95% interval of rms(a) - rms(b) over tiles drawn with replacement (a, b paired by tile)"""
    if len(a) < 2:
        return None
    rng = random.Random(seed + len(a))
    vals = []
    for _ in range(draws):
        idx = [rng.randrange(len(a)) for _ in a]
        vals.append(C.rms([a[i] for i in idx]) - C.rms([b[i] for i in idx]))
    vals.sort()
    return [round(vals[int(0.025 * (draws - 1))], 3), round(vals[int(0.975 * (draws - 1))], 3)]


def score(cells, P, min_passes):
    tiles = {c["name"]: c for c in cells.values() if c.get("name") and c["n"] >= min_passes}
    left_out = sorted(n for n in P["tiles"] if n not in tiles)
    ref = P["reference"]
    mt = P["rules"]["min_tiles"]
    out = {"tiles_scored": len(tiles), "left_out": left_out, "rules": {}, "reported": {}}

    def errs(names, q, m="M7"):
        meas = {"mhz": "burst_mhz", "w": "burst_w", "rise": "rise_c", "D": "D_w"}[q]
        pk = {"mhz": "burst_mhz", "w": "burst_board_w", "rise": "burst_die_rise_c", "D": "burst_D_w"}[q]
        return [tiles[n][meas] - P["tiles"][n]["models"][m][pk] for n in names if tiles[n].get(meas) is not None]

    def inside(names, q, m="M7"):
        meas = {"mhz": "burst_mhz", "w": "burst_w", "rise": "rise_c", "D": "D_w"}[q]
        bk = {"mhz": "burst_mhz_95", "w": "burst_board_95", "rise": "burst_die_rise_95", "D": "burst_D_95"}[q]
        k = 0
        for n in names:
            lo, hi = P["tiles"][n]["models"][m][bk]
            v = tiles[n].get(meas)
            if v is not None and lo - 1e-9 <= v <= hi + 1e-9:
                k += 1
        return k

    gov = sorted(n for n in tiles if P["tiles"][n]["group"] == "governed")
    pin = sorted(n for n in tiles if P["tiles"][n]["group"] == "pinned")
    alln = sorted(tiles)

    def boot_rule(rid, names, q, refe, need):
        e = errs(names, q)
        x = C.rms(e) if e else None
        lo, hi = C.boot_rms_range(refe, len(e)) if e else (None, None)
        v = verdict(x, lo, hi) if len(e) >= need else f"NOT SCORED (n {len(e)} < {need})"
        out["rules"][rid] = {"n": len(e), "rms": rnd(x, 3), "range_2.5_97.5": [rnd(lo, 3), rnd(hi, 3)], "verdict": v,
                             "mean_err": rnd(mean(e), 3), "ref_rms": rnd(C.rms(refe), 3)}

    def cov_rule(rid, names, q, need):
        n = len([x for x in names if tiles[x].get({"mhz": "burst_mhz", "w": "burst_w", "rise": "rise_c"}[q]) is not None])
        k = inside(names, q)
        line = C.coverage_line(n)
        v = ("PASS" if k >= line else "FAIL") if n >= need else f"NOT SCORED (n {n} < {need})"
        out["rules"][rid] = {"n": n, "inside": k, "line": line, "verdict": v}

    boot_rule("E143-F1", gov, "mhz", ref["governed"]["mhz_err"], mt["F1"])
    boot_rule("E143-F2", pin, "mhz", ref["pinned"]["mhz_err"], mt["F2"])
    cov_rule("E143-F3", alln, "mhz", mt["coverage"])
    boot_rule("E143-W1", gov, "w", ref["governed"]["w_err"], mt["W1"])
    boot_rule("E143-W2", pin, "w", ref["pinned"]["w_err"], mt["W2"])
    cov_rule("E143-W3", alln, "w", mt["coverage"])
    boot_rule("E143-H1", alln, "rise", ref["heat"]["rise_err_c"], mt["H1"])
    cov_rule("E143-H3", alln, "rise", mt["coverage"])

    # reported: every model on every set, the paired differences, D, the heat law on the measured W, priority 1, per format, the measured split
    rep = out["reported"]
    sets = {"governed": gov, "pinned": pin, "all": alln, "priority1": sorted(n for n in alln if P["tiles"][n]["priority"] == 1)}
    for ty in ("fp32", "fp16", "int8"):
        sets[ty] = sorted(n for n in alln if P["tiles"][n]["type"] == ty)
    meas_gov = sorted(n for n in alln if tiles[n]["burst_mhz"] < C.GOVERNED_BELOW_MHZ)
    sets["measured_governed"] = meas_gov
    sets["measured_pinned"] = sorted(n for n in alln if n not in meas_gov)
    nonzero = sorted(n for n in alln if P["tiles"][n]["models"]["M7"]["burst_D_w"] != 0.0)
    rep["by_set"] = {}
    for sname, names in sets.items():
        row = {"n": len(names)}
        for q in ("mhz", "w", "rise", "D"):
            nm = [n for n in names if n in nonzero] if q == "D" else names
            for m in MODELS:
                e = errs(nm, q, m)
                row[f"{m}_{q}_rms"] = rnd(C.rms(e), 3) if e else None
                row[f"{m}_{q}_mean"] = rnd(mean(e), 3) if e else None
                row[f"{m}_{q}_inside"] = inside(nm, q, m) if e else None
            if q in ("mhz", "w", "D"):
                a, b6, b5 = errs(nm, q, "M7"), errs(nm, q, "M6"), errs(nm, q, "M5")
                row[f"M7_minus_M6_{q}_rms_95"] = paired_boot(a, b6)
                row[f"M7_minus_M5_{q}_rms_95"] = paired_boot(a, b5)
        rep["by_set"][sname] = row
    k = P["relation"]["heat_k_c_per_w"]
    p0 = P["relation"]["P_idle_w"]
    hl = [tiles[n]["rise_c"] - k * (tiles[n]["burst_w"] - p0) for n in alln]
    rep["heat_law_on_measured_w"] = {"n": len(hl), "rms_c": rnd(C.rms(hl), 3), "mean_c": rnd(mean(hl), 3), "k": k, "P_idle_w": p0}
    rep["tiles"] = {n: {"group": P["tiles"][n]["group"], "priority": P["tiles"][n]["priority"], "passes": tiles[n]["passes"],
                        "burst_mhz": tiles[n]["burst_mhz"], "burst_mhz_runs": tiles[n]["burst_mhz_runs"], "burst_w": tiles[n]["burst_w"],
                        "burst_w_runs": tiles[n]["burst_w_runs"], "rise_c": tiles[n]["rise_c"], "rise_runs": tiles[n]["rise_runs"],
                        "die_start_runs": tiles[n]["die_start_runs"], "D_w": tiles[n].get("D_w"), "D_runs": tiles[n].get("D_runs"),
                        "p800_w_runs": tiles[n]["p800_w_runs"], "first_down": tiles[n]["first_down"], "kernel_mhz": tiles[n].get("kernel_mhz"),
                        **{f"{m}_{q}": P["tiles"][n]["models"][m][pk] for m in MODELS for q, pk in
                           (("mhz", "burst_mhz"), ("w", "burst_board_w"), ("rise", "burst_die_rise_c"), ("D", "burst_D_w"))}}
                    for n in alln}
    return out


def replicate(cells, P):
    out = {"verdict": None, "tiles": {}}
    ok = True
    for lab, r in P["replicate"].items():
        c = cells.get(lab)
        if not c:
            out["tiles"][lab] = {"n": 0}
            ok = None if ok is not False else False
            continue
        dm, dw = c["burst_mhz"] - r["ref_burst_mhz"], c["burst_w"] - r["ref_burst_w"]
        good = abs(dm) <= P["rules"]["replicate_mhz"] and abs(dw) <= P["rules"]["replicate_w"]
        out["tiles"][lab] = {"n": c["n"], "burst_mhz": c["burst_mhz"], "ref_mhz": r["ref_burst_mhz"], "d_mhz": rnd(dm, 2), "burst_w": c["burst_w"],
                             "ref_w": r["ref_burst_w"], "d_w": rnd(dw, 3), "rise_c": c["rise_c"], "within": good}
        if not good:
            ok = False
    out["verdict"] = "NOT SCORED" if ok is None else ("PASS" if ok else "FAIL")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e143.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    bad = C.check_frozen()
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    P = json.load(open(a.pred))
    runs = collect(a.rundirs)
    cells = cells_of(runs, P)
    mp = P["rules"]["min_passes"]
    passes_done = sorted({m["pass"] for m in runs if m["counted"]})
    res = {"experiment": "E143", "predictions_sha256": C.sha256_file(a.pred), "reducer_sha256": C.sha256_file(__file__),
           "common_sha256": C.sha256_file(C.__file__), "sessions": [os.path.basename(os.path.normpath(r)) for r in a.rundirs],
           "dry": any(m["dry"] for m in runs), "runs": len(runs), "runs_counted": sum(1 for m in runs if m["counted"]),
           "runs_not_counted": [m["run"] for m in runs if not m["counted"]], "passes": passes_done}
    if len(passes_done) < mp:
        res["score"] = {"note": f"fewer than {mp} counted passes: every rule NOT SCORED"}
    else:
        res["score"] = score(cells, P, mp)
        res["per_pass"] = {}
        for p in passes_done:
            sc = score(cells_of(runs, P, passes={p}), P, 1)
            res["per_pass"][str(p)] = {k: {kk: v.get(kk) for kk in ("n", "rms", "inside", "verdict")} for k, v in sc["rules"].items()}
    res["replicate"] = replicate(cells, P)
    res["peaks"] = peaks(a.rundirs)
    res["cells"] = cells
    res["run_rows"] = [{k: m.get(k) for k in ("session", "run", "label", "pass", "counted", "burst_mhz", "burst_w", "die_start", "die_max", "p800_w", "c_w",
                                                "burst_rate", "burst_ghz_kernel", "first_down_kind", "launch_ok", "launch_n", "work_s", "n_samples")} for m in runs]
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    print(f"E143 reduction: {res['runs']} burst runs, {res['runs_counted']} counted, passes {passes_done}; dry {res['dry']}")
    if res["runs_not_counted"]:
        print("  not counted:", res["runs_not_counted"])
    sc = res["score"]
    if "rules" in sc:
        print(f"tiles scored {sc['tiles_scored']}; left out {sc['left_out']}")
        for k, v in sc["rules"].items():
            print(f"  {k:8s} {json.dumps(v)}")
        print("  R0      ", json.dumps(res["replicate"]))
        for sname, row in sc["reported"]["by_set"].items():
            print(f"  [{sname:17s}] n {row['n']:2d}  clock rms M7/M6/M5 {row['M7_mhz_rms']}/{row['M6_mhz_rms']}/{row['M5_mhz_rms']} MHz  board {row['M7_w_rms']}/{row['M6_w_rms']}/{row['M5_w_rms']} W"
                  f"  rise {row['M7_rise_rms']} C  D {row['M7_D_rms']}/{row['M6_D_rms']}/{row['M5_D_rms']} W")
        print("  heat law on the measured W:", json.dumps(sc["reported"]["heat_law_on_measured_w"]))
        for p, rr in res.get("per_pass", {}).items():
            print(f"  pass {p}: " + "; ".join(f"{k} {v.get('rms') if v.get('rms') is not None else v.get('inside')} {v.get('verdict')}" for k, v in rr.items()))
        print("tile                                group    p  passes  MHz (M7)        W (M7)          rise C (M7)    D W (M7)")
        for n, t in sorted(sc["reported"]["tiles"].items(), key=lambda kv: (kv[1]["group"], kv[0])):
            print(f"  {n:34s} {t['group']:8s} {t['priority']}  {len(t['passes'])}  {t['burst_mhz']:6.1f} ({t['M7_mhz']:6.1f})  {t['burst_w']:6.2f} ({t['M7_w']:6.2f})  "
                  f"{t['rise_c']:5.2f} ({t['M7_rise']:5.2f})  {t['D_w'] if t['D_w'] is not None else '-'} ({t['M7_D']})")
    else:
        print(sc["note"])
    print("peaks:", json.dumps(res["peaks"]))


if __name__ == "__main__":
    main()
