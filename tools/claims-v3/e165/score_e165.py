#!/usr/bin/env python3
"""E165 (Q141(g)): the registered reduction and scoring. Standard library only. It is E160's reduce_e160.py (E143's reduce_e143.py) with pool 7,
M9's aifoundry2 part as the primary model RECOMPUTED PER TILE from the session's own reads (M8, M7 and M6 as frozen beside it), Q139(k)'s check of C
joined to every launch, and Q139's final critic's rank-2 rule as the primary verdict.

    python3 tools/claims-v3/ccheck/ccheck.py check <RUNDIR>/c-log.jsonl --out <data dir>/ccheck-<session>.json --jobs 2     # at the desk, per session
    python3 -B tools/claims-v3/e165/score_e165.py <RUNDIR> [<RUNDIR> ...] --ccheck <ccheck-<session>.json> [...] [--out results.json] > score.txt

PER RUN (block BURST only), E80's metrics, imported and called unchanged (as E143 and E160): reduce_hpl.run_metrics and reduce_kspeed.burst_extra
(burst_mhz = the mean sampled clock from 1.5 s after the first launch to the end of the work, burst_w = the mean board W over the same samples, c_w;
die_start = the first die reading inside the work, die_max its largest); peak_w, the highest board sample of the run's whole trace; the C check of
every launch (ccheck.py's verdict joined on t_start_ms and t_end_ms); whether the host stopped on its device-time budget. The run's PASS is the
registered order's (predictions-e165.json order[idx].pass; the protocol lists the 171 runs in that order, so run_hpl's rep is 1 throughout), and
the run's label must be the order's label at its idx, else the reduction refuses.
A run is COMPLETE if every launch of it ran and was ok and burst_mhz, burst_w, die_start, die_max exist; COUNTED if complete AND every SPARSITY line
of it has a C record that reads PASS (on the toy card, --dry, no C log exists: complete = counted, labelled).

PER TILE, over its counted passes: burst_mhz, burst_w and the die rise (die_max - die_start) are the means of the passes; die_start_runs are the
passes' die starts; the burst D is the mean over passes of burst_w less the burst_w of the same type's zeros anchor in the same pass (reported).

THE PRIMARY (E165.md): for each scored tile, predict_m9_a2.burst(D, t, anchors, die_starts, D_band_hw), the frozen code called unchanged, with D and
D_band_hw M9's frozen D at 600 MHz and its half-band (predictions-e165.json), anchors the session's zeros-anchor reads ({format: [{burst_w,
burst_mhz, die_start}] over every counted burst of pool 7's three anchor7_zeros tiles}) and die_starts the tile's own counted bursts' die starts. The
groups are fixed by the frozen file (M9.a2_q140l.group). The zeros anchors are inputs and are not scored.

THE RULES (E165.md "Decision rules"; groups fixed by the frozen file; at least 2 counted passes a tile, else the tile is left out and named; fewer
than 2 counted passes in all: every rule NOT SCORED):
  E165-R2   rank 2 (Q139's final critic), on the primary: G governed clock rms <= 4.0 MHz, |mean| <= 2.0 MHz, resolved better than M7 as frozen;
            Bg governed board |mean| <= 0.5 W, resolved better than M7; Bp pinned board |mean| <= 0.5 W, rms <= 1.0 W, resolved better than M7.
            "Resolved better" = the 95% interval of rms(M9 primary) - rms(M7 as frozen) over the set's tiles (paired bootstrap, 20,000 draws, seed
            1651) lies below 0. R2 PASS if G, Bg and Bp all PASS; FAIL if any FAILs; else NOT SCORED (fewer than 8 tiles in a set).
  E165-F1   governed clock rms against the 2.5-97.5% range of the rms of n errors drawn from Q140(l)'s end-to-end governed clock errors (36 cells)
  E165-F2   pinned clock, the same with the 42 pinned cells
  E165-W1   governed board, the same     E165-W2   pinned board, the same
  E165-F3   clock, all scored: coverage of the primary's 95% band as burst() returns it (the frozen half-widths): PASS if inside >= the 2.5% point of
            Binomial(n, 0.95)                         E165-W3   board, the same          E165-H3   die rise, the same (+-1.41 C)
  E165-H1   die rise, all scored, against the burst heat law's 112 leave-one-kind-out residuals (E160-H1's reference)
  E165-C    the check of C: PASS if every launch of every BURST run has a C record and reads PASS (it decides which runs count)
  E165-R0   E80's two replicate tiles each within 25 MHz and 3.37 W of E80's and E83's mean cell (a diagnostic), E143's and E160's cells beside
REPORTED, never a verdict: the frozen file's M9.a2_q140l block as frozen, M8, M7 and M6 on every set and line, with paired differences; the arms
that split the primary's two inputs (the anchors read in pass 1 only, before any pool tile; the fallback offset with the die starts; the session's
anchors at T_ref); the zeros anchors' own errors under the fallback; the frozen bands' coverage as frozen and at the nested widths (A1-3); the peaks
against M9's and M8's peak predictions; k_T per burst (the within-tile slope of the pinned bursts' board on the die start, against 0.395 W/C); the
burst D; per pass, per format, per class, priority 1, real tiles, the sets split by the measured clock; the heat law on the measured board W; the
kernel's own clock; every rule over the complete runs (C not required) beside the counted; budget stops; the session's peaks.

The parent's registered scoring is reproduced by score_parent_e160() on E160's committed session with this file's own collect, cells and rule
helpers (selftest_score_e165.py).
"""
import argparse
import glob
import gzip
import json
import os
import random
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "hpl"))
sys.path.insert(0, os.path.join(HERE, "..", "kspeed"))
import e165_common as C  # noqa: E402
import reduce_hpl as R  # noqa: E402
import reduce_kspeed as RK  # noqa: E402

KSPEED_PRED = os.path.join(HERE, "..", "kspeed", "predictions.json")
MEAS = {"mhz": "burst_mhz", "w": "burst_w", "rise": "rise_c", "D": "D_w"}
PRED = {"mhz": "burst_mhz", "w": "burst_board_w", "rise": "burst_die_rise_c", "D": "burst_D_w"}
BAND = {"mhz": "burst_mhz_95", "w": "burst_board_95", "rise": "burst_die_rise_95", "D": "burst_D_95"}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return st.mean(xs) if xs else None


def rnd(x, n=3):
    return None if x is None else round(x, n)


# ------------------------------------------------------------------------------------------------ the reduction (E160's, ported)
def load_ccheck(paths):
    """{(t_start_ms, t_end_ms): verdict record} over every ccheck.py check output given"""
    out = {}
    for p in paths or []:
        for v in json.load(open(p)).get("launches", []):
            out[(v.get("t_start_ms"), v.get("t_end_ms"))] = v
    return out


def pass_by_rep(r):
    """E160's convention: the pass is run_hpl's rep"""
    return r.get("rep")


def pass_by_order(P):
    """E165's convention: the pass is the registered order's at the run's idx, whose label must be the run's"""
    order = P["order"]

    def f(r):
        i = r.get("idx")
        if not isinstance(i, int) or not 0 <= i < len(order) or order[i]["label"] != r.get("label"):
            raise SystemExit(f"refused: run {r.get('run')} (idx {i}, label {r.get('label')}) is not the registered order's run at that idx")
        return order[i]["pass"]
    return f


def collect(rundirs, cc, pass_of=pass_by_rep, block="BURST"):
    """every BURST run's E80 metrics, with its session and pass, its peak, its C check (reduce_e160.collect, the pass by pass_of)"""
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
            if r["block"] != block:
                continue
            procs = byrun.get(r["run"], [])
            m = R.run_metrics(rd, r, procs, evs.get(r["run"]), fit)
            m["session"] = os.path.basename(os.path.normpath(rd))
            m["dry"] = bool(sess.get("dry"))
            m["pass"] = pass_of(r)
            m["idx"] = r.get("idx")
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


def cells_of(runs, meta, zeros, passes=None, key="counted"):
    """per pool tile and per replicate: the means over the runs that pass `key` (counted, or complete), restricted to `passes` if given
    (reduce_e160.cells_of; meta = {name: {label, type, group, priority, anchor}}, zeros = {type: the zeros anchor's label})"""
    lab2name = {t["label"]: n for n, t in meta.items()}
    by = {}
    for m in runs:
        if not m[key] or (passes is not None and m["pass"] not in passes):
            continue
        by.setdefault(m["label"], {})[m["pass"]] = m
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
            t = meta[name]
            zl = zeros.get(t["type"])
            dz = [per[p]["burst_w"] - by[zl][p]["burst_w"] for p in ps if zl in by and p in by[zl]]
            cz = [per[p]["c_w"] - by[zl][p]["c_w"] for p in ps if zl in by and p in by[zl] and per[p].get("c_w") is not None and by[zl][p].get("c_w") is not None]
            c["D_runs"] = [round(x, 3) for x in dz]
            c["D_w"] = rnd(mean(dz), 3)
            c["c_minus_zeros_w"] = rnd(mean(cz), 4)
            c["name"], c["type"], c["group"], c["priority"], c["anchor"] = name, t["type"], t["group"], t["priority"], t["anchor"]
        cells[lab] = c
    return cells


def c_rule(runs, cc_given):
    """the check of C over every BURST run's launches (E160-C's form)"""
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


# ------------------------------------------------------------------------------------------------ the rule helpers (E160's, generic)
def verdict(x, lo, hi):
    if x is None or hi is None:
        return "NOT SCORED"
    if x > hi:
        return "FAIL"
    if x < lo:
        return "PASS (better than the reference says)"
    return "PASS"


def paired_boot(a, b, draws=5000, seed=1601):
    """E160's reported paired interval of rms(a) - rms(b) over tiles (a, b paired by tile)"""
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
    """E160's reported percentile bootstrap 95% interval of the rms over tiles"""
    if len(e) < 2:
        return None
    rng = random.Random(seed + len(e))
    vals = sorted(C.rms([e[rng.randrange(len(e))] for _ in e]) for _ in range(draws))
    return [round(vals[int(0.025 * (draws - 1))], 3), round(vals[int(0.975 * (draws - 1))], 3)]


def errs(names, q, tiles, predmap):
    """measured - predicted for the named tiles that have the measured quantity; predmap[name] is the prediction record"""
    return [tiles[n][MEAS[q]] - predmap[n][PRED[q]] for n in names if tiles[n].get(MEAS[q]) is not None]


def inside(names, q, tiles, predmap):
    k = 0
    for n in names:
        lo, hi = predmap[n][BAND[q]]
        v = tiles[n].get(MEAS[q])
        if v is not None and lo - 1e-9 <= v <= hi + 1e-9:
            k += 1
    return k


def boot_rule(e, refe, need, seed):
    x = C.rms(e) if e else None
    lo, hi = C.boot_rms_range(refe, len(e), seed=seed) if e else (None, None)
    v = verdict(x, lo, hi) if len(e) >= need else f"NOT SCORED (n {len(e)} < {need})"
    return {"n": len(e), "rms": rnd(x, 3), "range_2.5_97.5": [rnd(lo, 3), rnd(hi, 3)], "verdict": v,
            "mean_err": rnd(mean(e), 3), "ref_rms": rnd(C.rms(refe), 4), "rms_95_over_tiles": rms_ci(e)}


def cov_rule(names, q, tiles, predmap, need):
    n = len([x for x in names if tiles[x].get(MEAS[q]) is not None])
    k = inside(names, q, tiles, predmap)
    line = C.coverage_line(n)
    v = ("PASS" if k >= line else "FAIL") if n >= need else f"NOT SCORED (n {n} < {need})"
    return {"n": n, "inside": k, "line": line, "verdict": v}


def replicate(cells, reps, rules, beside=("e143", "e160")):
    out = {"verdict": None, "tiles": {}}
    ok = True
    for lab, r in reps.items():
        c = cells.get(lab)
        if not c:
            out["tiles"][lab] = {"n": 0}
            ok = None if ok is not False else False
            continue
        dm, dw = c["burst_mhz"] - r["ref_burst_mhz"], c["burst_w"] - r["ref_burst_w"]
        good = abs(dm) <= rules["replicate_mhz"] and abs(dw) <= rules["replicate_w"]
        row = {"n": c["n"], "burst_mhz": c["burst_mhz"], "ref_mhz": r["ref_burst_mhz"], "d_mhz": rnd(dm, 2), "burst_w": c["burst_w"],
               "ref_w": r["ref_burst_w"], "d_w": rnd(dw, 3), "rise_c": c["rise_c"], "within": good}
        for s in beside:
            if f"{s}_burst_mhz" in r:
                row[f"{s}_mhz"] = r[f"{s}_burst_mhz"]
                row[f"d_mhz_vs_{s}"] = rnd(c["burst_mhz"] - r[f"{s}_burst_mhz"], 2)
                row[f"{s}_w"] = r[f"{s}_burst_w"]
                row[f"d_w_vs_{s}"] = rnd(c["burst_w"] - r[f"{s}_burst_w"], 3)
        row["peak_w"] = c.get("peak_w")
        out["tiles"][lab] = row
        if not good:
            ok = False
    out["verdict"] = "NOT SCORED" if ok is None else ("PASS" if ok else "FAIL")
    return out


# ------------------------------------------------------------------------------------------------ the parent's registered scoring (self-test)
def score_parent_e160(cells, P, min_passes):
    """E160's registered rules F1-F3, W1-W3, H1, H3 and PK on E160's frozen predictions, with this file's helpers (reduce_e160.score's rules)"""
    tiles = {c["name"]: c for c in cells.values() if c.get("name") and c["n"] >= min_passes}
    ran = {c["name"]: c for c in cells.values() if c.get("name") and c["n"] >= 1}
    pm = {n: P["tiles"][n]["models"]["M8"] for n in P["tiles"]}
    ref, mt, seed = P["reference"], P["rules"]["min_tiles"], P["rules"]["boot"]["seed"]
    gov = sorted(n for n in tiles if P["tiles"][n]["group"] == "governed")
    pin = sorted(n for n in tiles if P["tiles"][n]["group"] == "pinned")
    alln = sorted(tiles)
    out = {}
    out["E160-F1"] = boot_rule(errs(gov, "mhz", tiles, pm), ref["governed"]["mhz_err"], mt["F1"], seed)
    out["E160-F2"] = boot_rule(errs(pin, "mhz", tiles, pm), ref["pinned"]["mhz_err"], mt["F2"], seed)
    out["E160-F3"] = cov_rule(alln, "mhz", tiles, pm, mt["coverage"])
    out["E160-W1"] = boot_rule(errs(gov, "w", tiles, pm), ref["governed"]["w_err"], mt["W1"], seed)
    out["E160-W2"] = boot_rule(errs(pin, "w", tiles, pm), ref["pinned"]["w_err"], mt["W2"], seed)
    out["E160-W3"] = cov_rule(alln, "w", tiles, pm, mt["coverage"])
    out["E160-H1"] = boot_rule(errs(alln, "rise", tiles, pm), ref["heat"]["rise_err_c"], mt["H1"], seed)
    out["E160-H3"] = cov_rule(alln, "rise", tiles, pm, mt["coverage"])
    pkn = sorted(n for n in ran if ran[n].get("peak_w") is not None)
    k = sum(1 for n in pkn if ran[n]["peak_w"] <= pm[n]["peak_board_hi95_w"] + 1e-9)
    line = C.coverage_line(len(pkn))
    over = [{"tile": n, "peak_w": ran[n]["peak_w"], "hi95_w": pm[n]["peak_board_hi95_w"]} for n in pkn if ran[n]["peak_w"] > pm[n]["peak_board_hi95_w"] + 1e-9]
    burst_err = [x - pm[n]["peak_board_w"] for n in pkn for x in ran[n]["peak_w_runs"] if x is not None]
    burst_in = [x <= pm[n]["peak_board_hi95_w"] + 1e-9 for n in pkn for x in ran[n]["peak_w_runs"] if x is not None]
    out["E160-PK"] = {"n": len(pkn), "inside": k, "line": line, "over": over,
                      "verdict": ("PASS" if k >= line else "FAIL") if len(pkn) >= mt["PK"] else f"NOT SCORED (n {len(pkn)} < {mt['PK']})",
                      "per_burst": {"n": len(burst_err), "inside": sum(burst_in), "rms_vs_expected_w": rnd(C.rms(burst_err), 3),
                                    "mean_vs_expected_w": rnd(mean(burst_err), 3)}}
    return {"tiles_scored": len(tiles), "left_out": sorted(n for n in P["tiles"] if not P["tiles"][n]["dropped"] and n not in tiles), "rules": out}


def parent_meta(P):
    return ({n: {"label": t["label"], "type": t["type"], "group": t["group"], "priority": t["priority"], "anchor": t["anchor"]} for n, t in P["tiles"].items()},
            {t["type"]: t["label"] for n, t in P["tiles"].items() if t["anchor"] and n.endswith("anchor6_zeros")})


# ------------------------------------------------------------------------------------------------ E165's primary and its scoring
def meta_of(P):
    return ({n: {"label": t["label"], "type": t["type"], "group": t["group"], "priority": t["priority"], "anchor": t["anchor"]} for n, t in P["tiles"].items()},
            {P["tiles"][n]["type"]: C.label_of(n) for n in C.ZEROS_ANCHORS})


def anchors_from(cells, P, passes=None):
    """the session's zeros-anchor reads as burst() takes them: {format: [{burst_w, burst_mhz, die_start}, ...]} over the anchors' counted bursts
    (in `passes` if given); None if no anchor burst exists (burst() then takes the frozen fallback)"""
    out = {}
    for n in C.ZEROS_ANCHORS:
        c = cells.get(C.label_of(n))
        if not c:
            continue
        rr = [{"burst_w": w, "burst_mhz": f, "die_start": T} for p, w, f, T in zip(c["passes"], c["burst_w_runs"], c["burst_mhz_runs"], c["die_start_runs"])
              if (passes is None or p in passes) and None not in (w, f, T)]
        if rr:
            out[P["tiles"][n]["type"]] = rr
    return out or None


def predict(P, tiles, anchors, die_mode="own"):
    """the primary's recompute per scored tile (die_mode 'own': the tile's counted bursts' die starts; 'tref': none given, T_ref)"""
    out = {}
    for n, c in tiles.items():
        m9 = P["tiles"][n]["models"]["M9"]
        ds = [x for x in c["die_start_runs"] if x is not None] if die_mode == "own" else None
        out[n] = C.primary(m9["D600_a3_footing_w"], P["tiles"][n]["type"], anchors, ds or None, m9["D_band_hw"])
    return out


def frozen_map(P, names, model):
    if model == "M9_as_frozen":
        return {n: P["tiles"][n]["models"]["M9"]["a2_q140l"] for n in names}
    return {n: P["tiles"][n]["models"][model] for n in names}


def rank2(gov, pin, tiles, pm, p7, P):
    """E165-R2 on one prediction map pm, against M7 as frozen (p7)"""
    L, need = P["rules"]["rank2_lines"], P["rules"]["min_tiles"]
    res = {}

    def res_vs_m7(names, q):
        a, b = errs(names, q, tiles, pm), errs(names, q, tiles, p7)
        r = C.paired_rms_diff(a, b)
        if r is None:
            return None, None
        return r, r["ci95"][1] < 0
    # G
    e = errs(gov, "mhz", tiles, pm)
    r7, better = res_vs_m7(gov, "mhz")
    g = {"n": len(e), "rms": rnd(C.rms(e), 3), "mean": rnd(mean(e), 3), "rms_le_line": None, "mean_within_line": None, "vs_M7": r7, "resolved_better_than_M7": better}
    if len(e) >= need["R2_governed"]:
        g["rms_le_line"] = C.rms(e) <= L["G_rms_max_mhz"]
        g["mean_within_line"] = abs(mean(e)) <= L["G_abs_mean_max_mhz"]
        g["verdict"] = "PASS" if (g["rms_le_line"] and g["mean_within_line"] and better) else "FAIL"
    else:
        g["verdict"] = f"NOT SCORED (n {len(e)} < {need['R2_governed']})"
    res["G"] = g
    # Bg
    e = errs(gov, "w", tiles, pm)
    r7, better = res_vs_m7(gov, "w")
    b = {"n": len(e), "rms": rnd(C.rms(e), 3), "mean": rnd(mean(e), 3), "mean_within_line": None, "vs_M7": r7, "resolved_better_than_M7": better}
    if len(e) >= need["R2_governed"]:
        b["mean_within_line"] = abs(mean(e)) <= L["Bg_abs_mean_max_w"]
        b["verdict"] = "PASS" if (b["mean_within_line"] and better) else "FAIL"
    else:
        b["verdict"] = f"NOT SCORED (n {len(e)} < {need['R2_governed']})"
    res["Bg"] = b
    # Bp
    e = errs(pin, "w", tiles, pm)
    r7, better = res_vs_m7(pin, "w")
    p = {"n": len(e), "rms": rnd(C.rms(e), 3), "mean": rnd(mean(e), 3), "mean_within_line": None, "rms_le_line": None, "vs_M7": r7, "resolved_better_than_M7": better}
    if len(e) >= need["R2_pinned"]:
        p["mean_within_line"] = abs(mean(e)) <= L["Bp_abs_mean_max_w"]
        p["rms_le_line"] = C.rms(e) <= L["Bp_rms_max_w"]
        p["verdict"] = "PASS" if (p["mean_within_line"] and p["rms_le_line"] and better) else "FAIL"
    else:
        p["verdict"] = f"NOT SCORED (n {len(e)} < {need['R2_pinned']})"
    res["Bp"] = p
    vs = [res[k]["verdict"] for k in ("G", "Bg", "Bp")]
    res["verdict"] = "FAIL" if "FAIL" in vs else ("PASS" if all(v == "PASS" for v in vs) else "NOT SCORED")
    return res


def lines_only(gov, pin, tiles, pm):
    """rank 2's lines on any prediction map, no resolution test (reported)"""
    eg, ew, ep = errs(gov, "mhz", tiles, pm), errs(gov, "w", tiles, pm), errs(pin, "w", tiles, pm)
    epm = errs(pin, "mhz", tiles, pm)
    return {"G_rms": rnd(C.rms(eg), 3), "G_mean": rnd(mean(eg), 3), "Bg_rms": rnd(C.rms(ew), 3), "Bg_mean": rnd(mean(ew), 3),
            "Bp_rms": rnd(C.rms(ep), 3), "Bp_mean": rnd(mean(ep), 3), "Gp_rms": rnd(C.rms(epm), 3), "Gp_mean": rnd(mean(epm), 3),
            "n_governed": len(eg), "n_pinned": len(ep)}


def nested_cover(names, tiles, pm, P, idx):
    """the reported coverage at the nested widths of A1-3 (idx 0: inner rule 2 of 3, 1: 3 of 3), around the prediction, by the frozen group"""
    W = P["reference"]["nested_widths"]
    k = {"mhz": 0, "w": 0}
    for n in names:
        g = P["tiles"][n]["group"]
        f, w = pm[n]["burst_mhz"], pm[n]["burst_board_w"]
        hm, hw = W[g]["mhz"][idx], W[g]["board_w"][idx]
        if tiles[n].get("burst_mhz") is not None and f - hm - 1e-9 <= tiles[n]["burst_mhz"] <= min(800.0, f + hm) + 1e-9:
            k["mhz"] += 1
        if tiles[n].get("burst_w") is not None and w - hw - 1e-9 <= tiles[n]["burst_w"] <= w + hw + 1e-9:
            k["w"] += 1
    return {"n": len(names), "inside_mhz": k["mhz"], "inside_board": k["w"], "line": C.coverage_line(len(names))}


def kT_per_burst(runs, P, key="counted", min_mhz=795.0, draws=5000, seed=1653):
    """reported: the within-tile slope of the pinned scored tiles' burst board on the burst's die start (bursts at >= 795 MHz), pooled, with a
    bootstrap over tiles; against M9's k_T (0.395 W/C, fitted as a session-fixed-effect slope over the pinned runs of four sessions)"""
    by = {}
    for m in runs:
        n = C.name_of(m["label"])
        if not m[key] or n is None or n not in P["tiles"] or not P["tiles"][n]["scored"] or P["tiles"][n]["group"] != "pinned":
            continue
        if m.get("burst_mhz") is None or m["burst_mhz"] < min_mhz or m.get("die_start") is None:
            continue
        by.setdefault(n, []).append((float(m["die_start"]), float(m["burst_w"])))
    groups = [v for v in by.values() if len(v) >= 2 and len({t for t, _ in v}) >= 2]

    def slope(gs):
        sxy = sxx = 0.0
        for v in gs:
            mt = sum(t for t, _ in v) / len(v)
            mw = sum(w for _, w in v) / len(v)
            sxy += sum((t - mt) * (w - mw) for t, w in v)
            sxx += sum((t - mt) ** 2 for t, _ in v)
        return sxy / sxx if sxx > 0 else None
    s = slope(groups)
    ci = None
    if s is not None and len(groups) >= 4:
        rng = random.Random(seed + len(groups))
        vals = []
        for _ in range(draws):
            x = slope([groups[rng.randrange(len(groups))] for _ in groups])
            if x is not None:
                vals.append(x)
        vals.sort()
        ci = [round(vals[int(0.025 * (len(vals) - 1))], 4), round(vals[int(0.975 * (len(vals) - 1))], 4)]
    return {"n_tiles": len(groups), "n_bursts": sum(len(v) for v in groups), "slope_w_per_c": rnd(s, 4), "ci95": ci,
            "M9_kT_w_per_c": P["relation"]["kT_w_per_c"], "note": "reported, never a verdict; whole-degree die readings"}


def score(cells, P, min_passes, runs=None, light=False):
    """the registered rules on the primary, and the reported readings (light: the rules, the lines by arm and the coverage only, for per-pass scoring
    and the self-test; the paired differences, the rank-2 rule on the other arms and k_T are left out)"""
    tiles = {c["name"]: c for c in cells.values() if c.get("name") and P["tiles"][c["name"]]["scored"] and c["n"] >= min_passes}
    ran = {c["name"]: c for c in cells.values() if c.get("name") and c["n"] >= 1}
    scored = [n for n in P["tiles"] if P["tiles"][n]["scored"]]
    left = sorted(n for n in scored if n not in tiles)
    gov = sorted(n for n in tiles if P["tiles"][n]["group"] == "governed")
    pin = sorted(n for n in tiles if P["tiles"][n]["group"] == "pinned")
    alln = sorted(tiles)
    mt, ref, seed = P["rules"]["min_tiles"], P["reference"], P["rules"]["boot"]["seed"]
    anchors = anchors_from(cells, P)
    pm = predict(P, tiles, anchors, "own")
    maps = {"M9_primary": pm, "M9_as_frozen": frozen_map(P, alln, "M9_as_frozen"), "M8": frozen_map(P, alln, "M8"), "M7": frozen_map(P, alln, "M7"),
            "M6": frozen_map(P, alln, "M6")}
    a1 = anchors_from(cells, P, passes={1})
    maps["M9_anchors_pass1_only"] = predict(P, tiles, a1, "own")
    maps["M9_fallback_with_die_starts"] = predict(P, tiles, None, "own")
    maps["M9_session_anchors_at_Tref"] = predict(P, tiles, anchors, "tref")
    out = {"tiles_scored": len(tiles), "left_out": left, "left_out_by_name": P["left_out"], "rules": {}, "reported": {},
           "anchors": anchors, "anchor_delta": {"delta_w": pm[alln[0]]["delta_w"], "delta_source": pm[alln[0]]["delta_source"]} if alln else None}
    out["rules"]["E165-R2"] = rank2(gov, pin, tiles, pm, maps["M7"], P)
    eg = ref["e2e"]
    out["rules"]["E165-F1"] = boot_rule(errs(gov, "mhz", tiles, pm), eg["governed"]["mhz_err"], mt["F1"], seed)
    out["rules"]["E165-F2"] = boot_rule(errs(pin, "mhz", tiles, pm), eg["pinned"]["mhz_err"], mt["F2"], seed)
    out["rules"]["E165-W1"] = boot_rule(errs(gov, "w", tiles, pm), eg["governed"]["w_err"], mt["W1"], seed)
    out["rules"]["E165-W2"] = boot_rule(errs(pin, "w", tiles, pm), eg["pinned"]["w_err"], mt["W2"], seed)
    out["rules"]["E165-F3"] = cov_rule(alln, "mhz", tiles, pm, mt["coverage"])
    out["rules"]["E165-W3"] = cov_rule(alln, "w", tiles, pm, mt["coverage"])
    out["rules"]["E165-H1"] = boot_rule(errs(alln, "rise", tiles, pm), ref["heat"]["rise_err_c"], mt["H1"], seed)
    out["rules"]["E165-H3"] = cov_rule(alln, "rise", tiles, pm, mt["coverage"])

    rep = out["reported"]
    rep["lines_by_arm"] = {k: lines_only(gov, pin, tiles, v) for k, v in maps.items()}
    if not light:
        rep["rank2_as_rule_on_other_arms"] = {k: rank2(gov, pin, tiles, maps[k], maps["M7"], P) for k in ("M9_as_frozen", "M8", "M9_anchors_pass1_only")}
        rep["paired_vs"] = {}
        for other in ("M9_as_frozen", "M8", "M7", "M6"):     # reported: E160's paired_boot form (5,000 draws)
            rep["paired_vs"][other] = {f"{s}_{q}": paired_boot(errs(nm, q, tiles, pm), errs(nm, q, tiles, maps[other]))
                                       for s, nm in (("governed", gov), ("pinned", pin), ("all", alln)) for q in ("mhz", "w", "rise")}
    rep["coverage_by_arm"] = {k: {q: inside(alln, q, tiles, v) for q in ("mhz", "w", "rise")} for k, v in maps.items()}
    rep["coverage_line"] = C.coverage_line(len(alln))
    rep["coverage_at_nested_widths_A1_3"] = {"inner_2_of_3": nested_cover(alln, tiles, pm, P, 0), "inner_3_of_3": nested_cover(alln, tiles, pm, P, 1),
                                             "frozen": {"inside_mhz": inside(alln, "mhz", tiles, pm), "inside_board": inside(alln, "w", tiles, pm)}}
    # the zeros anchors themselves under the fallback (the frozen zeros level, tested directly), and their recomputed level (in sample by construction)
    za = {}
    for n in C.ZEROS_ANCHORS:
        c = cells.get(C.label_of(n))
        if not c or c["n"] < 1:
            continue
        fz = P["tiles"][n]["models"]["M9"]["a2_q140l"]
        za[n] = {"n": c["n"], "burst_mhz": c["burst_mhz"], "burst_w": c["burst_w"], "die_start_runs": c["die_start_runs"],
                 "as_frozen_err_mhz": rnd(c["burst_mhz"] - fz["burst_mhz"], 3), "as_frozen_err_w": rnd(c["burst_w"] - fz["burst_board_w"], 3),
                 "M8_err_w": rnd(c["burst_w"] - P["tiles"][n]["models"]["M8"]["burst_board_w"], 3)}
    rep["zeros_anchors"] = za
    # the peaks against M9's and M8's peak predictions (reported; E160-PK's form)
    pk = {}
    for model, keyf in (("M9", lambda n: P["tiles"][n]["models"]["M9"]["a2_q140l"]), ("M8", lambda n: P["tiles"][n]["models"]["M8"])):
        pkn = sorted(n for n in ran if ran[n].get("peak_w") is not None)
        k = sum(1 for n in pkn if ran[n]["peak_w"] <= keyf(n)["peak_board_hi95_w"] + 1e-9)
        over = [{"tile": n, "peak_w": ran[n]["peak_w"], "hi95_w": keyf(n)["peak_board_hi95_w"]} for n in pkn if ran[n]["peak_w"] > keyf(n)["peak_board_hi95_w"] + 1e-9]
        be = [x - keyf(n)["peak_board_w"] for n in pkn for x in ran[n]["peak_w_runs"] if x is not None]
        bi = [x <= keyf(n)["peak_board_hi95_w"] + 1e-9 for n in pkn for x in ran[n]["peak_w_runs"] if x is not None]
        pk[model] = {"n": len(pkn), "inside": k, "line": C.coverage_line(len(pkn)), "over": over,
                     "per_burst": {"n": len(be), "inside": sum(bi), "rms_vs_expected_w": rnd(C.rms(be), 3), "mean_vs_expected_w": rnd(mean(be), 3)}}
    rep["peaks_vs_predictions"] = pk
    if runs is not None and not light:
        rep["kT_per_burst"] = kT_per_burst(runs, P)
    sets = {"governed": gov, "pinned": pin, "all": alln, "priority1": sorted(n for n in alln if P["tiles"][n]["priority"] == 1),
            "real": sorted(n for n in alln if P["tiles"][n]["real"])}
    for ty in ("fp32", "fp16", "int8"):
        sets[ty] = sorted(n for n in alln if P["tiles"][n]["type"] == ty)
    for cl in sorted({P["tiles"][n]["class"] for n in alln}):
        sets[f"class_{cl}"] = sorted(n for n in alln if P["tiles"][n]["class"] == cl)
    mg = sorted(n for n in alln if tiles[n]["burst_mhz"] < C.GOVERNED_BELOW_MHZ)
    sets["measured_governed"] = mg
    sets["measured_pinned"] = sorted(n for n in alln if n not in mg)
    rep["by_set"] = {}
    for sname, names in sets.items():
        row = {"n": len(names)}
        for q in ("mhz", "w", "rise", "D"):
            for mname in ("M9_primary", "M9_as_frozen", "M8", "M7", "M6"):
                e = errs(names, q, tiles, maps[mname]) if q != "D" else [tiles[n]["D_w"] - maps[mname][n]["burst_D_w"] for n in names if tiles[n].get("D_w") is not None]
                row[f"{mname}_{q}_rms"] = rnd(C.rms(e), 3) if e else None
                row[f"{mname}_{q}_mean"] = rnd(mean(e), 3) if e else None
        rep["by_set"][sname] = row
    kh, p0 = P["relation"]["heat_k_c_per_w"], P["relation"]["P_idle_w"]
    hl = [tiles[n]["rise_c"] - kh * (tiles[n]["burst_w"] - p0) for n in alln]
    rep["heat_law_on_measured_w"] = {"n": len(hl), "rms_c": rnd(C.rms(hl), 3), "mean_c": rnd(mean(hl), 3), "k": kh, "P_idle_w": p0}
    ks = [tiles[n]["kernel_mhz"] - tiles[n]["burst_mhz"] for n in alln if tiles[n].get("kernel_mhz") is not None]
    rep["kernel_clock_minus_sampled_mhz"] = {"n": len(ks), "mean": rnd(mean(ks), 2)}
    rep["tiles"] = {n: {"group": P["tiles"][n]["group"], "priority": P["tiles"][n]["priority"], "class": P["tiles"][n]["class"], "passes": tiles[n]["passes"],
                        "burst_mhz": tiles[n]["burst_mhz"], "burst_mhz_runs": tiles[n]["burst_mhz_runs"], "burst_w": tiles[n]["burst_w"],
                        "burst_w_runs": tiles[n]["burst_w_runs"], "rise_c": tiles[n]["rise_c"], "die_start_runs": tiles[n]["die_start_runs"],
                        "D_w": tiles[n].get("D_w"), "peak_w_runs": tiles[n]["peak_w_runs"], "kernel_mhz": tiles[n].get("kernel_mhz"),
                        "primary": {k: pm[n][k] for k in ("burst_mhz", "burst_mhz_95", "burst_board_w", "burst_board_95", "burst_die_rise_c", "burst_die_rise_95",
                                                          "burst_D_w", "group", "delta_source", "die_start_source")},
                        **{f"{m}_{q}": maps[m][n][PRED[q]] for m in ("M9_as_frozen", "M8", "M7") for q in ("mhz", "w", "rise")}}
                    for n in alln}
    return out


def stray_left_out(runs, P):
    """None, or why not: no run may be of a tile left out by name (the 82 W list)"""
    stray = sorted({m["label"] for m in runs if C.name_of(m["label"]) in set(P["left_out"])})
    return f"runs of tiles left out by name: {stray}" if stray else None


def scoring(runs, P, key):
    meta, zeros = meta_of(P)
    cells = cells_of(runs, meta, zeros, key=key)
    mp = P["rules"]["min_passes"]
    passes_done = sorted({m["pass"] for m in runs if m[key]})
    res = {"key": key, "passes": passes_done, "cells": cells}
    if len(passes_done) < mp:
        res["score"] = {"note": f"fewer than {mp} {key} passes: every rule NOT SCORED"}
    else:
        res["score"] = score(cells, P, mp, runs)
        res["per_pass"] = {}
        for p in passes_done:
            cp = cells_of(runs, meta, zeros, passes={p}, key=key)
            sc = score(cp, P, 1, light=True)
            res["per_pass"][str(p)] = {"R2": {k: sc["rules"]["E165-R2"][k].get("verdict") if isinstance(sc["rules"]["E165-R2"][k], dict) else sc["rules"]["E165-R2"][k]
                                              for k in ("G", "Bg", "Bp", "verdict")},
                                       "lines": sc["reported"]["lines_by_arm"]["M9_primary"],
                                       "rules": {k: {kk: v.get(kk) for kk in ("n", "rms", "inside", "verdict")} for k, v in sc["rules"].items() if k != "E165-R2"}}
    res["replicate"] = replicate(cells, P["replicate"], P["rules"])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e165.json"))
    ap.add_argument("--ccheck", nargs="*", default=[])
    ap.add_argument("--out")
    a = ap.parse_args()
    bad = C.check_frozen(ccheck=False)
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    P = json.load(open(a.pred))
    cc = load_ccheck(a.ccheck)
    runs = collect(a.rundirs, cc, pass_of=pass_by_order(P))
    why = stray_left_out(runs, P)
    if why:
        raise SystemExit(f"refused: {why}")
    prim = scoring(runs, P, "counted")
    comp = scoring(runs, P, "complete")
    res = {"experiment": "E165", "predictions_sha256": C.sha256_file(a.pred), "scorer_sha256": C.sha256_file(__file__), "common_sha256": C.sha256_file(C.__file__),
           "m9_a2_sha256": C.m9a2().M9_SHA256, "sessions": [os.path.basename(os.path.normpath(r)) for r in a.rundirs],
           "ccheck_files": {os.path.basename(p): C.sha256_file(p) for p in a.ccheck}, "dry": any(m["dry"] for m in runs), "runs": len(runs),
           "runs_complete": sum(1 for m in runs if m["complete"]), "runs_counted": sum(1 for m in runs if m["counted"]),
           "runs_not_complete": [m["run"] for m in runs if not m["complete"]], "runs_complete_not_counted": [m["run"] for m in runs if m["complete"] and not m["counted"]],
           "budget_stops": [m["run"] for m in runs if m["budget_stop"]], "passes": prim["passes"],
           "c_check": c_rule(runs, bool(a.ccheck)), "score": prim["score"], "per_pass": prim.get("per_pass"), "replicate": prim["replicate"],
           "as_complete_runs": {"score_rules": (comp["score"].get("rules") if "rules" in comp["score"] else comp["score"]), "replicate": comp["replicate"]},
           "peaks": peaks(a.rundirs), "cells": prim["cells"],
           "run_rows": [{k: m.get(k) for k in ("session", "run", "idx", "label", "pass", "complete", "counted", "c_pass", "c_lines", "c_verdicts", "budget_stop",
                                                "burst_mhz", "burst_w", "die_start", "die_max", "p800_w", "peak_w", "c_w", "burst_rate", "burst_ghz_kernel",
                                                "first_down_kind", "launch_ok", "launch_n", "work_s", "n_samples")} for m in runs]}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    print(f"E165 scoring: {res['runs']} burst runs, {res['runs_complete']} complete, {res['runs_counted']} counted (complete and every launch's C PASS), "
          f"passes {res['passes']}; dry {res['dry']}")
    print("  C check:", json.dumps({k: v for k, v in res["c_check"].items() if k != "by_tile"})[:600])
    if res["runs_not_complete"]:
        print("  not complete:", res["runs_not_complete"])
    if res["budget_stops"]:
        print("  budget stops:", res["budget_stops"])
    sc = res["score"]
    if "rules" in sc:
        print(f"tiles scored {sc['tiles_scored']}; left out (fewer than 2 counted passes) {sc['left_out']}; left out by name {sc['left_out_by_name']}")
        print("  anchors (the session's zeros-anchor reads):", json.dumps(sc["anchors"])[:500])
        r2 = sc["rules"]["E165-R2"]
        print(f"  E165-R2  {r2['verdict']}: G {json.dumps(r2['G'])[:300]}")
        print(f"           Bg {json.dumps(r2['Bg'])[:300]}")
        print(f"           Bp {json.dumps(r2['Bp'])[:300]}")
        for k, v in sc["rules"].items():
            if k != "E165-R2":
                print(f"  {k:8s} {json.dumps(v)[:400]}")
        print("  R0      ", json.dumps(res["replicate"]))
        for k, v in sc["reported"]["lines_by_arm"].items():
            print(f"  [{k:30s}] {json.dumps(v)}")
        print("  peaks vs predictions:", json.dumps(sc["reported"]["peaks_vs_predictions"])[:700])
        print("  kT per burst:", json.dumps(sc["reported"].get("kT_per_burst")))
        print("  coverage at the nested widths:", json.dumps(sc["reported"]["coverage_at_nested_widths_A1_3"]))
        print("  zeros anchors:", json.dumps(sc["reported"]["zeros_anchors"])[:700])
        for p, rr in (res.get("per_pass") or {}).items():
            print(f"  pass {p}: R2 {rr['R2']}; lines {json.dumps(rr['lines'])}")
        print("tile                                     group    p  passes  MHz (primary / as frozen)   W (primary / as frozen)    rise C (primary)")
        for n, t in sorted(sc["reported"]["tiles"].items(), key=lambda kv: (kv[1]["group"], kv[0])):
            pr = t["primary"]
            print(f"  {n:40s} {t['group']:8s} {t['priority']}  {len(t['passes'])}  {t['burst_mhz']:6.1f} ({pr['burst_mhz']:6.1f} / {t['M9_as_frozen_mhz']:6.1f})  "
                  f"{t['burst_w']:6.2f} ({pr['burst_board_w']:6.2f} / {t['M9_as_frozen_w']:6.2f})  {t['rise_c']:5.2f} ({pr['burst_die_rise_c']:5.2f})")
    else:
        print(sc["note"])
    print("peaks:", json.dumps(res["peaks"]))


if __name__ == "__main__":
    main()
