#!/usr/bin/env python3
"""E160 (Q139): the registered reduction and scoring. Standard library only. It is E143's reduce_e143.py with pool 6, M8 as the primary model (M7 and
M6 beside it), Q139(k)'s check of C joined to every launch, and two more rules (the peak, PK; the C check, C).

    python3 tools/claims-v3/ccheck/ccheck.py check <RUNDIR>/c-log.jsonl --out <data dir>/ccheck-<session>.json --jobs 6     # at the desk, per session
    python3 tools/claims-v3/e160/reduce_e160.py <RUNDIR> [<RUNDIR> ...] --ccheck <ccheck-<session>.json> [...] [--a3-d <json>] [--out results.json] > reduce.txt

PER RUN (block BURST only), E80's metrics, imported and called unchanged (as E143): reduce_hpl.run_metrics and reduce_kspeed.burst_extra (burst_mhz =
the mean sampled clock from 1.5 s after the first launch to the end of the work, burst_w = the mean board W over the same samples, c_w, burst_rate;
die_start = the first die reading inside the work, die_max its largest). Added: peak_w, the highest board sample of the run's whole trace (M8's peak
rule's quantity: fit_m8.py's, over E143's traces); the C check of every launch (ccheck.py's verdict joined on t_start_ms and t_end_ms); whether the host
stopped on its device-time budget.
A run is COMPLETE (E143's "counted") if every launch of it ran and was ok (launch_ok == launch_n >= 1) and burst_mhz, burst_w, die_start and die_max
exist. It is COUNTED (E160's primary) if it is complete AND every SPARSITY line of it has a C record that reads PASS (bit-exact against Q139(k)'s
reference; ROUNDING, UNMODELLED, FAIL and a missing record are not checked). On the toy card (--dry) no C log exists: complete = counted, labelled.

PER TILE, over its counted passes (the pass is the unit of replication): burst_mhz, burst_w and the die rise (die_max - die_start) are the means of the
passes; the burst D is the mean over passes of burst_w less the burst_w of the same type's zeros anchor IN THE SAME PASS. A tile with fewer than 2
counted passes is left out of F/W/H and named.

THE RULES (E160.md "Decision rules"), each tile's group frozen in predictions-e160.json (governed: M8 predicts the burst below 795 MHz):
  E160-F1  clock, governed tiles (17, at least 8): rms(measured - M8) against the 2.5-97.5% range of the rms of n errors drawn with replacement from
           M8's end-to-end clock errors on the 36 kinds bursts it predicted governed: PASS at or below the 97.5% point, FAIL above; below the 2.5% point
           "better than the reference says"
  E160-F2  clock, pinned tiles (31, at least 8): as F1, the 56 reference rows predicted pinned
  E160-F3  clock, all: coverage of M8's frozen 95% band (+-16.9 MHz, 800 the top): PASS if inside >= the 2.5% point of Binomial(n, 0.95)
  E160-W1  board W at the clock, governed: as F1 with the governed rows' board errors
  E160-W2  board W, pinned: as F2 with the pinned rows' board errors
  E160-W3  board W, all: coverage of +-3.50 W
  E160-H1  die rise, all (at least 10): as F1 with the burst heat law's 112 leave-one-kind-out residuals (0.6845 C rms)
  E160-H3  die rise, all: coverage of +-1.41 C
  E160-PK  M8's peak rule: per tile with a counted burst, its highest board sample over its counted bursts at or below M8's frozen 95% upper peak
           (peak_board_hi95_w); coverage as F3 (at least 10 tiles)
  E160-C   the check of C: PASS if every launch of every BURST run has a C record and reads PASS; else FAIL with the counts (it decides which runs count)
  E160-R0  the card's drift check: E80's two replicate tiles each within 25 MHz and 3.37 W of E80's and E83's mean cell (a diagnostic: it qualifies,
           never changes, the verdicts above); E143's own cells of 2 Nov reported beside
  E160-S   rank 5, aifoundry2's scale: s = the median over pinned float tiles (measured 795-800 MHz, aifoundry3 D600 >= 5 W) of (c - c_zeros) / D600,
           c the tile's mean burst c_w and c_zeros its type's zeros anchor's in the same passes; int8 the same with D600 >= 1 W; D600 = aifoundry3's
           MEASURED D (E153's, given by --a3-d); PASS if card-scale-blind6.json's V600^2 physical prediction is within 1% of s. Without --a3-d: NOT
           SCORED, and s against M8's predicted D600 reported instead.
Fewer than 2 counted passes in all: F/W/H NOT SCORED. REPORTED, never a verdict: M7's and M6's rms on every set beside M8's and the paired differences
with a bootstrap interval over tiles; the burst D against each model's burst_D_w; the heat law on the measured board W; the sets split by the measured
clock; priority 1; per format and class; the real tiles; every pass scored on its own; the kernel's own clock; the same rules over the COMPLETE runs (E143's
counting) beside the counted; the peak's per-burst error against M8's expected peak; budget stops; the session's peaks.
"""
import argparse
import glob
import gzip
import json
import math
import os
import random
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "hpl"))
sys.path.insert(0, os.path.join(HERE, "..", "kspeed"))
import e160_common as C  # noqa: E402
import reduce_hpl as R  # noqa: E402
import reduce_kspeed as RK  # noqa: E402

KSPEED_PRED = os.path.join(HERE, "..", "kspeed", "predictions.json")
MODELS = C.MODELS


def mean(xs):
    xs = [x for x in xs if x is not None]
    return st.mean(xs) if xs else None


def rnd(x, n=3):
    return None if x is None else round(x, n)


def load_ccheck(paths):
    """{(t_start_ms, t_end_ms): verdict record} over every ccheck.py check output given"""
    out = {}
    for p in paths or []:
        for v in json.load(open(p)).get("launches", []):
            out[(v.get("t_start_ms"), v.get("t_end_ms"))] = v
    return out


def collect(rundirs, cc):
    """every BURST run's E80 metrics, with its session and pass, its peak, its C check"""
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
            procs = byrun.get(r["run"], [])
            m = R.run_metrics(rd, r, procs, evs.get(r["run"]), fit)
            m["session"] = os.path.basename(os.path.normpath(rd))
            m["dry"] = bool(sess.get("dry"))
            m["pass"] = r.get("rep")
            m.update(RK.burst_extra(m, procs, B))
            m["complete"] = bool(m.get("launch_n") and m.get("launch_ok") == m.get("launch_n") and None not in
                                 (m.get("burst_mhz"), m.get("burst_w"), m.get("die_start"), m.get("die_max")))
            s = R.tel(os.path.join(rd, r["tel"]))
            bw = [x[3] for x in s if x[3] is not None]
            m["peak_w"] = max(bw) if bw else None
            lines = [sp for L in procs if L.get("role") == "work" for sp in (L.get("sparsity") or [])]
            ver = []
            for sp in lines:
                v = cc.get((sp.get("t_start_ms"), sp.get("t_end_ms")))
                ver.append("NO_RECORD" if v is None else v.get("verdict"))
            m["c_lines"] = len(lines)
            m["c_verdicts"] = {k: ver.count(k) for k in sorted(set(ver))}
            m["c_pass"] = bool(lines) and all(x == "PASS" for x in ver)
            m["budget_stop"] = any("device-time budget" in (L.get("stderr_tail") or "") for L in procs if L.get("role") == "work")
            m["counted"] = m["complete"] and (m["c_pass"] or m["dry"])
            m["rise_c"] = (m["die_max"] - m["die_start"]) if m["complete"] else None
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


def zeros_labels(P):
    return {t["type"]: t["label"] for n, t in P["tiles"].items() if t["anchor"] and n.endswith("anchor6_zeros")}


def cells_of(runs, P, passes=None, key="counted"):
    """per pool tile and per replicate: the means over the runs that pass `key` (counted, or complete), restricted to `passes` if given"""
    lab2name = {t["label"]: n for n, t in P["tiles"].items()}
    by = {}
    for m in runs:
        if not m[key] or (passes is not None and m["pass"] not in passes):
            continue
        by.setdefault(m["label"], {})[m["pass"]] = m
    zeros = zeros_labels(P)
    cells = {}
    for lab, per in by.items():
        ps = sorted(per)
        c = {"label": lab, "passes": ps, "n": len(ps),
             "burst_mhz_runs": [per[p]["burst_mhz"] for p in ps], "burst_w_runs": [per[p]["burst_w"] for p in ps],
             "rise_runs": [per[p]["rise_c"] for p in ps], "die_start_runs": [per[p]["die_start"] for p in ps], "die_max_runs": [per[p]["die_max"] for p in ps],
             "p800_w_runs": [per[p].get("p800_w") for p in ps], "c_w_runs": [per[p].get("c_w") for p in ps], "rate_runs": [per[p].get("burst_rate") for p in ps],
             "peak_w_runs": [per[p].get("peak_w") for p in ps], "first_down": [per[p].get("first_down_kind") for p in ps],
             "kernel_mhz_runs": [None if per[p].get("burst_ghz_kernel") is None else round(per[p]["burst_ghz_kernel"] * 1000, 1) for p in ps]}
        c["burst_mhz"] = rnd(mean(c["burst_mhz_runs"]), 2)
        c["burst_w"] = rnd(mean(c["burst_w_runs"]), 3)
        c["rise_c"] = rnd(mean(c["rise_runs"]), 3)
        c["c_w"] = rnd(mean(c["c_w_runs"]), 3)
        c["kernel_mhz"] = rnd(mean(c["kernel_mhz_runs"]), 1)
        c["peak_w"] = max([x for x in c["peak_w_runs"] if x is not None], default=None)
        name = lab2name.get(lab)
        if name is not None:
            t = P["tiles"][name]
            zl = zeros.get(t["type"])
            dz = [per[p]["burst_w"] - by[zl][p]["burst_w"] for p in ps if zl in by and p in by[zl]]
            cz = [per[p]["c_w"] - by[zl][p]["c_w"] for p in ps if zl in by and p in by[zl] and per[p].get("c_w") is not None and by[zl][p].get("c_w") is not None]
            c["D_runs"] = [round(x, 3) for x in dz]
            c["D_w"] = rnd(mean(dz), 3)
            c["c_minus_zeros_w"] = rnd(mean(cz), 4)
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


def paired_boot(a, b, draws=5000, seed=1601):
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


def rms_ci(e, draws=5000, seed=1602):
    """a percentile bootstrap 95% interval of the rms over tiles (reported)"""
    if len(e) < 2:
        return None
    rng = random.Random(seed + len(e))
    vals = sorted(C.rms([e[rng.randrange(len(e))] for _ in e]) for _ in range(draws))
    return [round(vals[int(0.025 * (draws - 1))], 3), round(vals[int(0.975 * (draws - 1))], 3)]


MEAS = {"mhz": "burst_mhz", "w": "burst_w", "rise": "rise_c", "D": "D_w"}
PRED = {"mhz": "burst_mhz", "w": "burst_board_w", "rise": "burst_die_rise_c", "D": "burst_D_w"}
BAND = {"mhz": "burst_mhz_95", "w": "burst_board_95", "rise": "burst_die_rise_95", "D": "burst_D_95"}


def score(cells, P, min_passes):
    tiles = {c["name"]: c for c in cells.values() if c.get("name") and c["n"] >= min_passes}
    ran = {c["name"]: c for c in cells.values() if c.get("name") and c["n"] >= 1}
    run_names = [n for n in P["tiles"] if not P["tiles"][n]["dropped"]]
    left_out = sorted(n for n in run_names if n not in tiles)
    ref = P["reference"]
    mt = P["rules"]["min_tiles"]
    out = {"tiles_scored": len(tiles), "left_out": left_out, "dropped": P["dropped"], "rules": {}, "reported": {}}

    def errs(names, q, m="M8", src=None):
        src = src or tiles
        return [src[n][MEAS[q]] - P["tiles"][n]["models"][m][PRED[q]] for n in names if src[n].get(MEAS[q]) is not None]

    def inside(names, q, m="M8"):
        k = 0
        for n in names:
            lo, hi = P["tiles"][n]["models"][m][BAND[q]]
            v = tiles[n].get(MEAS[q])
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
                             "mean_err": rnd(mean(e), 3), "ref_rms": rnd(C.rms(refe), 4), "rms_95_over_tiles": rms_ci(e)}

    def cov_rule(rid, names, q, need):
        n = len([x for x in names if tiles[x].get(MEAS[q]) is not None])
        k = inside(names, q)
        line = C.coverage_line(n)
        v = ("PASS" if k >= line else "FAIL") if n >= need else f"NOT SCORED (n {n} < {need})"
        out["rules"][rid] = {"n": n, "inside": k, "line": line, "verdict": v}

    boot_rule("E160-F1", gov, "mhz", ref["governed"]["mhz_err"], mt["F1"])
    boot_rule("E160-F2", pin, "mhz", ref["pinned"]["mhz_err"], mt["F2"])
    cov_rule("E160-F3", alln, "mhz", mt["coverage"])
    boot_rule("E160-W1", gov, "w", ref["governed"]["w_err"], mt["W1"])
    boot_rule("E160-W2", pin, "w", ref["pinned"]["w_err"], mt["W2"])
    cov_rule("E160-W3", alln, "w", mt["coverage"])
    boot_rule("E160-H1", alln, "rise", ref["heat"]["rise_err_c"], mt["H1"])
    cov_rule("E160-H3", alln, "rise", mt["coverage"])
    # PK: every tile with a counted burst, its highest board sample against M8's frozen 95% upper peak
    pkn = sorted(n for n in ran if ran[n].get("peak_w") is not None)
    k = sum(1 for n in pkn if ran[n]["peak_w"] <= P["tiles"][n]["models"]["M8"]["peak_board_hi95_w"] + 1e-9)
    line = C.coverage_line(len(pkn))
    over = [{"tile": n, "peak_w": ran[n]["peak_w"], "hi95_w": P["tiles"][n]["models"]["M8"]["peak_board_hi95_w"]} for n in pkn
            if ran[n]["peak_w"] > P["tiles"][n]["models"]["M8"]["peak_board_hi95_w"] + 1e-9]
    burst_err = [x - P["tiles"][n]["models"]["M8"]["peak_board_w"] for n in pkn for x in ran[n]["peak_w_runs"] if x is not None]
    burst_in = [x <= P["tiles"][n]["models"]["M8"]["peak_board_hi95_w"] + 1e-9 for n in pkn for x in ran[n]["peak_w_runs"] if x is not None]
    out["rules"]["E160-PK"] = {"n": len(pkn), "inside": k, "line": line, "over": over,
                               "verdict": ("PASS" if k >= line else "FAIL") if len(pkn) >= mt["PK"] else f"NOT SCORED (n {len(pkn)} < {mt['PK']})",
                               "per_burst": {"n": len(burst_err), "inside": sum(burst_in), "rms_vs_expected_w": rnd(C.rms(burst_err), 3),
                                             "mean_vs_expected_w": rnd(mean(burst_err), 3)}}

    rep = out["reported"]
    sets = {"governed": gov, "pinned": pin, "all": alln, "priority1": sorted(n for n in alln if P["tiles"][n]["priority"] == 1),
            "new_kinds": sorted(n for n in alln if not P["tiles"][n]["anchor"]), "real": sorted(n for n in alln if P["tiles"][n]["real"])}
    for ty in ("fp32", "fp16", "int8"):
        sets[ty] = sorted(n for n in alln if P["tiles"][n]["type"] == ty)
    for cl in sorted({P["tiles"][n]["class"] for n in alln}):
        sets[f"class_{cl}"] = sorted(n for n in alln if P["tiles"][n]["class"] == cl)
    meas_gov = sorted(n for n in alln if tiles[n]["burst_mhz"] < C.GOVERNED_BELOW_MHZ)
    sets["measured_governed"] = meas_gov
    sets["measured_pinned"] = sorted(n for n in alln if n not in meas_gov)
    nonzero = sorted(n for n in alln if not n.endswith("anchor6_zeros"))
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
                a, b7, b6 = errs(nm, q, "M8"), errs(nm, q, "M7"), errs(nm, q, "M6")
                row[f"M8_minus_M7_{q}_rms_95"] = paired_boot(a, b7)
                row[f"M8_minus_M6_{q}_rms_95"] = paired_boot(a, b6)
            if q in ("mhz", "w", "rise"):
                row[f"M8_{q}_rms_95"] = rms_ci(errs(nm, q, "M8"))
        rep["by_set"][sname] = row
    kh = P["relation"]["heat_k_c_per_w"]
    p0 = P["relation"]["P_idle_w"]
    hl = [tiles[n]["rise_c"] - kh * (tiles[n]["burst_w"] - p0) for n in alln]
    rep["heat_law_on_measured_w"] = {"n": len(hl), "rms_c": rnd(C.rms(hl), 3), "mean_c": rnd(mean(hl), 3), "k": kh, "P_idle_w": p0}
    ks = [tiles[n]["kernel_mhz"] - tiles[n]["burst_mhz"] for n in alln if tiles[n].get("kernel_mhz") is not None]
    rep["kernel_clock_minus_sampled_mhz"] = {"n": len(ks), "mean": rnd(mean(ks), 2), "governed_mean": rnd(mean([tiles[n]["kernel_mhz"] - tiles[n]["burst_mhz"] for n in gov if tiles[n].get("kernel_mhz") is not None]), 2)}
    rep["tiles"] = {n: {"group": P["tiles"][n]["group"], "priority": P["tiles"][n]["priority"], "class": P["tiles"][n]["class"], "passes": tiles[n]["passes"],
                        "burst_mhz": tiles[n]["burst_mhz"], "burst_mhz_runs": tiles[n]["burst_mhz_runs"], "burst_w": tiles[n]["burst_w"],
                        "burst_w_runs": tiles[n]["burst_w_runs"], "rise_c": tiles[n]["rise_c"], "rise_runs": tiles[n]["rise_runs"],
                        "die_start_runs": tiles[n]["die_start_runs"], "D_w": tiles[n].get("D_w"), "D_runs": tiles[n].get("D_runs"),
                        "p800_w_runs": tiles[n]["p800_w_runs"], "peak_w_runs": tiles[n]["peak_w_runs"], "first_down": tiles[n]["first_down"],
                        "kernel_mhz": tiles[n].get("kernel_mhz"), "c_minus_zeros_w": tiles[n].get("c_minus_zeros_w"),
                        "M8_peak": P["tiles"][n]["models"]["M8"]["peak_board_w"], "M8_peak_hi95": P["tiles"][n]["models"]["M8"]["peak_board_hi95_w"],
                        **{f"{m}_{q}": P["tiles"][n]["models"][m][PRED[q]] for m in MODELS for q in ("mhz", "w", "rise", "D")}}
                    for n in alln}
    return out


def scale(cells, P, a3d=None):
    """rank 5: aifoundry2's scale (c - c_zeros) / D600 over the pinned tiles (measured 795-800 MHz), by family; against the predicted scales"""
    out = {}
    lab2 = {t["label"]: n for n, t in P["tiles"].items()}
    for fam, types, dmin in (("floats", ("fp32", "fp16"), 5.0), ("int8", ("int8",), 1.0)):
        for src in ("M8_predicted_D600", "measured_D600"):
            if src == "measured_D600" and not a3d:
                continue
            ratios = []
            for lab, c in cells.items():
                n = lab2.get(lab)
                if n is None or c.get("c_minus_zeros_w") is None or c["n"] < 1 or P["tiles"][n]["type"] not in types:
                    continue
                if not (c["burst_mhz"] is not None and c["burst_mhz"] >= C.GOVERNED_BELOW_MHZ):
                    continue
                d6 = P["tiles"][n]["models"]["M8"]["D600_a3_footing_w"] if src == "M8_predicted_D600" else (a3d or {}).get(n)
                if d6 is None or d6 < dmin:
                    continue
                ratios.append(c["c_minus_zeros_w"] / d6)
            row = {"n": len(ratios), "median": rnd(st.median(ratios), 4) if ratios else None}
            if ratios and len(ratios) >= 4:
                q = sorted(ratios)
                row["iqr"] = [rnd(q[len(q) // 4], 4), rnd(q[(3 * len(q)) // 4], 4)]
            out[f"{fam}|{src}"] = row
        pred = P["scale"]["predicted"][fam]["cheap_read_predicted_scale"]
        out[f"{fam}|predicted"] = {k: rnd(v["pred_scale"], 4) for k, v in pred.items()}
    out["M8_applies_g"] = P["scale"]["M8_applies_g"]
    v = {}
    for fam in ("floats", "int8"):
        m = out.get(f"{fam}|measured_D600")
        pv = P["scale"]["predicted"][fam]["cheap_read_predicted_scale"]["V600_v|physical"]["pred_scale"]
        if not m or not m.get("median"):
            v[fam] = "NOT SCORED (no measured aifoundry3 D: E153's, --a3-d)"
        else:
            err = pv / m["median"] - 1
            v[fam] = f"{'PASS' if abs(err) <= P['rules']['scale_1pct'] else 'FAIL'} (V600^2 physical {pv:.4f} against {m['median']:.4f}: {100 * err:+.1f}%)"
    out["verdict_E160-S"] = v
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
                             "ref_w": r["ref_burst_w"], "d_w": rnd(dw, 3), "rise_c": c["rise_c"], "within": good,
                             "e143_mhz": r["e143_burst_mhz"], "d_mhz_vs_e143": rnd(c["burst_mhz"] - r["e143_burst_mhz"], 2),
                             "e143_w": r["e143_burst_w"], "d_w_vs_e143": rnd(c["burst_w"] - r["e143_burst_w"], 3), "peak_w": c.get("peak_w")}
        if not good:
            ok = False
    out["verdict"] = "NOT SCORED" if ok is None else ("PASS" if ok else "FAIL")
    return out


def c_rule(runs, cc_given):
    """E160-C over every BURST run's launches"""
    tot = {}
    for m in runs:
        for k, v in m["c_verdicts"].items():
            tot[k] = tot.get(k, 0) + v
    n = sum(tot.values())
    bad = [{"run": m["run"], "verdicts": m["c_verdicts"]} for m in runs if not m["c_pass"]]
    by_tile = {}
    for m in runs:
        d = by_tile.setdefault(m["label"], {})
        for k, v in m["c_verdicts"].items():
            d[k] = d.get(k, 0) + v
    if not cc_given:
        v = "NOT SCORED (no ccheck output given)"
    else:
        v = "PASS" if n and tot.get("PASS", 0) == n else "FAIL"
    return {"verdict": v, "launches": n, "by_verdict": tot, "runs_not_all_pass": bad, "by_tile": by_tile}


def scoring(runs, P, key):
    cells = cells_of(runs, P, key=key)
    mp = P["rules"]["min_passes"]
    passes_done = sorted({m["pass"] for m in runs if m[key]})
    res = {"key": key, "passes": passes_done, "cells": cells}
    if len(passes_done) < mp:
        res["score"] = {"note": f"fewer than {mp} {key} passes: every rule NOT SCORED"}
    else:
        res["score"] = score(cells, P, mp)
        res["per_pass"] = {}
        for p in passes_done:
            sc = score(cells_of(runs, P, passes={p}, key=key), P, 1)
            res["per_pass"][str(p)] = {k: {kk: v.get(kk) for kk in ("n", "rms", "inside", "verdict")} for k, v in sc["rules"].items()}
    res["replicate"] = replicate(cells, P)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e160.json"))
    ap.add_argument("--ccheck", nargs="*", default=[])
    ap.add_argument("--a3-d", default=None, help="a JSON {tile name: aifoundry3's measured D600 W} from E153's committed reduction")
    ap.add_argument("--out")
    a = ap.parse_args()
    bad = C.check_frozen(ccheck=False)
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    P = json.load(open(a.pred))
    cc = load_ccheck(a.ccheck)
    runs = collect(a.rundirs, cc)
    a3d = json.load(open(a.a3_d)) if a.a3_d else None
    prim = scoring(runs, P, "counted")
    comp = scoring(runs, P, "complete")
    res = {"experiment": "E160", "predictions_sha256": C.sha256_file(a.pred), "reducer_sha256": C.sha256_file(__file__),
           "common_sha256": C.sha256_file(C.__file__), "sessions": [os.path.basename(os.path.normpath(r)) for r in a.rundirs],
           "ccheck_files": {os.path.basename(p): C.sha256_file(p) for p in a.ccheck}, "dry": any(m["dry"] for m in runs), "runs": len(runs),
           "runs_complete": sum(1 for m in runs if m["complete"]), "runs_counted": sum(1 for m in runs if m["counted"]),
           "runs_not_complete": [m["run"] for m in runs if not m["complete"]], "runs_complete_not_counted": [m["run"] for m in runs if m["complete"] and not m["counted"]],
           "budget_stops": [m["run"] for m in runs if m["budget_stop"]], "passes": prim["passes"],
           "c_check": c_rule(runs, bool(a.ccheck)), "score": prim["score"], "per_pass": prim.get("per_pass"), "replicate": prim["replicate"],
           "scale": scale(prim["cells"], P, a3d), "as_e143_counted": {"score_rules": (comp["score"].get("rules") if "rules" in comp["score"] else comp["score"]),
                                                                     "replicate": comp["replicate"]},
           "peaks": peaks(a.rundirs), "cells": prim["cells"],
           "run_rows": [{k: m.get(k) for k in ("session", "run", "label", "pass", "complete", "counted", "c_pass", "c_lines", "c_verdicts", "budget_stop", "burst_mhz",
                                                "burst_w", "die_start", "die_max", "p800_w", "peak_w", "c_w", "burst_rate", "burst_ghz_kernel", "first_down_kind",
                                                "launch_ok", "launch_n", "work_s", "n_samples")} for m in runs]}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    print(f"E160 reduction: {res['runs']} burst runs, {res['runs_complete']} complete, {res['runs_counted']} counted (complete and every launch's C PASS), "
          f"passes {res['passes']}; dry {res['dry']}")
    print("  C check:", json.dumps({k: v for k, v in res["c_check"].items() if k != "by_tile"})[:600])
    if res["runs_not_complete"]:
        print("  not complete:", res["runs_not_complete"])
    if res["budget_stops"]:
        print("  budget stops:", res["budget_stops"])
    sc = res["score"]
    if "rules" in sc:
        print(f"tiles scored {sc['tiles_scored']}; left out {sc['left_out']}; dropped {sc['dropped']}")
        for k, v in sc["rules"].items():
            print(f"  {k:8s} {json.dumps(v)[:400]}")
        print("  R0      ", json.dumps(res["replicate"]))
        print("  S       ", json.dumps(res["scale"]))
        for sname, row in sc["reported"]["by_set"].items():
            print(f"  [{sname:17s}] n {row['n']:2d}  clock rms M8/M7/M6 {row['M8_mhz_rms']}/{row['M7_mhz_rms']}/{row['M6_mhz_rms']} MHz  board {row['M8_w_rms']}/{row['M7_w_rms']}/{row['M6_w_rms']} W"
                  f"  rise {row['M8_rise_rms']} C  D {row['M8_D_rms']}/{row['M7_D_rms']}/{row['M6_D_rms']} W  mean err M8 {row['M8_mhz_mean']} MHz {row['M8_w_mean']} W")
        print("  heat law on the measured W:", json.dumps(sc["reported"]["heat_law_on_measured_w"]))
        print("  kernel clock - sampled:", json.dumps(sc["reported"]["kernel_clock_minus_sampled_mhz"]))
        for p, rr in (res.get("per_pass") or {}).items():
            print(f"  pass {p}: " + "; ".join(f"{k} {v.get('rms') if v.get('rms') is not None else v.get('inside')} {v.get('verdict')}" for k, v in rr.items()))
        print("  as E143 counted (complete runs, C not required):", json.dumps({k: (v.get("rms"), v.get("inside"), v.get("verdict")) for k, v in
                                                                               (res["as_e143_counted"]["score_rules"] or {}).items()} if isinstance(res["as_e143_counted"]["score_rules"], dict) else res["as_e143_counted"]["score_rules"]))
        print("tile                                group    p  passes  MHz (M8)        W (M8)          rise C (M8)    D W (M8)     peak W (M8 exp / hi95)")
        for n, t in sorted(sc["reported"]["tiles"].items(), key=lambda kv: (kv[1]["group"], kv[0])):
            pk = max([x for x in t["peak_w_runs"] if x is not None], default=float("nan"))
            print(f"  {n:34s} {t['group']:8s} {t['priority']}  {len(t['passes'])}  {t['burst_mhz']:6.1f} ({t['M8_mhz']:6.1f})  {t['burst_w']:6.2f} ({t['M8_w']:6.2f})  "
                  f"{t['rise_c']:5.2f} ({t['M8_rise']:5.2f})  {t['D_w'] if t['D_w'] is not None else '-'} ({t['M8_D']})  {pk:6.2f} ({t['M8_peak']} / {t['M8_peak_hi95']})")
    else:
        print(sc["note"])
    print("peaks:", json.dumps(res["peaks"]))


if __name__ == "__main__":
    main()
