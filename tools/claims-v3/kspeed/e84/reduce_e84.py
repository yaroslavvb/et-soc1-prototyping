#!/usr/bin/env python3
"""E84 (Q130): the registered reduction -- each kind's burst and sustained speed, board power and die temperature on
aifoundry1's card 0 under its own governor, the limiting test read from the service processor's trace ring, and the
three directional predictions of README.md scored against the frozen predictions.json.

    python3 reduce_e84.py <RUNDIR> [--pred predictions.json] [--e80 <E80 results.json>] [--out results.json] > reduce.txt

PER RUN, the metrics are reduce_hpl.py's `run_metrics` (E64's and E80's registered reduction), imported and called
unchanged (a SUS2 run is passed to it as block SUS, which is what it is: a second sustained run). On top of them:

  idle_w, idle_die, idle_mhz   card 0's own idle level: the sampler's readings between the sampler's start and the
                               first launch (median board W, mean die, the most common clock)
  burst_mhz     the mean sampled clock from 1.5 s after the first launch to the end of the work, over the samples
                inside a kernel launch, at EVERY clock the card reads (card 0 has a 300 MHz point; E80 kept only
                600/700/800 because aifoundry2 has no other); burst_w the mean board W over the same samples
  burst_rate    the kernel's own operations over its own wall time, launches that start >= 1.5 s in (TFLOPS for fp32
                and fp16, TOPS for int8)
  burst_limit   from the trace ring: the first throttle-down line in the work (power_down -> power, thermal_down ->
                thermal), else none. Beside it, the governor's own inputs as the sampler reads them (never a verdict):
                a below-800 sample after the first 800 one with the PMIC running average (sp.board_avg_w) over the
                TDP in the prior 0.5 s -> power; a die reading >= 66 C in the prior 2 s -> thermal
  sus_label     (SUS) every in-work sample of the last 40 s of the work, in the governor's own priority order:
                  800       it reads 800 MHz;
                  thermal   the last throttle-down line since the sample's process started is thermal, or a die
                            reading >= 66 C in the prior 2 s (the thermal arm wins every pass on which T > 65);
                  power     the last throttle-down line since the process started is power, or, where the ring does
                            not reach (it keeps only its last ~67 entries), sp.board_avg_w over the TDP in the prior
                            0.5 s (the power arm holds the clock while its average is over the TDP);
                  ramp      none of those, and no 800 MHz sample yet in its process: the climb after the idle point
                            at a process start (card 0's firmware idles at 300 MHz between processes);
                  other     anything else.
                The limit: `none` if >= 90% of the non-ramp samples read 800 MHz; else `thermal` if the thermal label
                covers >= 50% of the non-ramp samples below 800; else `power` if the power label does; else
                `unresolved`. The share of ramp samples is reported beside it (it costs speed on every kind).

PER KIND: the burst cell is the mean of its two BURST passes (interval: the two passes); the sustained cell is the mean
of its sustained runs (two for fp32 zeros and fp32 randn). p800_sw is p800 minus the same type's zeros p800.

THE RULES (README.md "Decision rules"; frozen with predictions.json):
  E84-P1  zeros at least as fast as random data in every format: for fp32 (randn), fp16 (randn) and int8 (full),
          burst and sustained, clock(zeros) - clock(heavy) >= -10 MHz in all six comparisons      (primary)
  E84-P2  int8 the least throttled: deficit = 800 - clock; deficit(int8 full) <= deficit(fp16 randn) + 5 and
          <= deficit(fp32 randn) + 5 MHz, in the burst and in the sustained cells                  (primary)
  E84-P3  the limiting test read from the trace ring matches the frozen label for >= 9 of 11 kinds in the burst
          block and >= 9 of 11 in the sustained block (a kind is right only if every run carries the label)  (primary)
  E84-S1  P2 on the format means over all the kinds measured (sustained)                          (secondary)
Context, never a verdict: the same cells on aifoundry2 from E80 (and E64 for fp32 zeros and ones), and the zeros-over-
random speed ratio on both cards.
"""
import argparse
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "hpl"))
import reduce_hpl as R  # noqa: E402

OPS = R.OPS
BURST_FROM_S = 1.5
SUS_LAST_S = 40.0
NONE_SHARE = 0.9
HOT_C = 66
P1_TOL = -10.0
P2_TOL = 5.0
P3_RIGHT = 9
HEAVY = {"fp32": "fp32/randn", "fp16": "fp16/randn", "int8": "int8/full"}
ZEROS = {"fp32": "fp32/zeros", "fp16": "fp16/zeros", "int8": "int8/zeros"}


def kind_of(values):
    if not str(values).startswith("file:"):
        return None
    p = values[5:].split("/")
    return f"{p[-2]}/{p[-1][:-4]}"


def mean(xs):
    xs = [x for x in xs if x is not None]
    return st.mean(xs) if xs else None


def rnd(x, n=1):
    return round(x, n) if x is not None else None


def tel_full(path):
    """(t_ms, die mean, die high, board W, MHz, PMIC running average W) per sampler line, sorted."""
    out = []
    for d in R.jl(path):
        try:
            ms = d.get("temp_c", {}).get("minshire") or [None, None, None]
            out.append((int(d["t_ms"]), ms[0], ms[2] if len(ms) > 2 else None, d.get("board_w"),
                        d.get("mhz", {}).get("minion"), (d.get("sp") or {}).get("board_avg_w")))
        except (KeyError, TypeError, ValueError, AttributeError):
            pass
    out.sort()
    return out


def run_extra(rd, r, procs, m, tdp_w):
    s = tel_full(os.path.join(rd, r["tel"]))
    work = sorted([p for p in procs if p.get("role") == "work"], key=lambda p: p["t_start_ms"])
    kl = [k for p in work for k in p.get("sparsity", []) if k.get("t_start_ms") and k.get("t_end_ms")]
    kwins = [(k["t_start_ms"], k["t_end_ms"]) for k in kl] or [(p["t_start_ms"], p["t_end_ms"]) for p in work]
    t0 = min((p["t_start_ms"] for p in work), default=r["t_first_ms"])
    t1 = max((p["t_end_ms"] for p in work), default=r["t_last_ms"])
    pstarts = [p["t_start_ms"] for p in work]

    def in_work(t):
        return any(a <= t <= b for a, b in kwins)

    def proc_start(t):
        ps = [a for a in pstarts if a <= t]
        return ps[-1] if ps else t0

    ws = [x for x in s if in_work(x[0])]
    out = {}
    # card 0's own idle level: from the sampler's start to the first launch
    idle = [x for x in s if x[0] < t0]
    out["idle_w"] = rnd(R.med([x[3] for x in idle]), 2)
    out["idle_die"] = rnd(mean([x[1] for x in idle]), 1)
    mh = [x[4] for x in idle if x[4] is not None]
    out["idle_mhz"] = max(set(mh), key=mh.count) if mh else None
    out["idle_n"] = len(idle)
    # the burst window
    bw = [x for x in ws if x[0] >= t0 + BURST_FROM_S * 1000 and x[4] is not None]
    out["burst_mhz"] = rnd(mean([x[4] for x in bw]), 1)
    out["burst_w"] = rnd(mean([x[3] for x in bw]), 2)
    out["burst_n"] = len(bw)
    out["burst_share800"] = rnd(sum(1 for x in bw if x[4] == 800) / len(bw), 3) if bw else None
    out["burst_offpts"] = sorted({x[4] for x in bw if x[4] not in (600, 700, 800)})
    lw = [k for k in kl if k["t_start_ms"] >= t0 + BURST_FROM_S * 1000]
    wall = sum(k.get("wall_s", 0) for k in lw)
    ops = sum(k.get("minions", r["minions"]) * k.get("iters", 0) * OPS[r["type"]] for k in lw)
    out["burst_rate"] = rnd(ops / wall / 1e12, 3) if wall and ops else None
    out["burst_ghz_kernel"] = rnd(sum(k.get("cycles_max", 0) for k in lw) / wall / 1e9, 4) if wall else None
    # the governor's lines, placed on the host clock by run_metrics (t_s from t0)
    pe = [e for e in (m.get("event_list") or []) if e.get("t_s") is not None]
    covered_from = (t0 + min(e["t_s"] for e in pe) * 1000) if pe else None
    downs = [(t0 + e["t_s"] * 1000, e["kind"]) for e in pe if e["kind"] in ("power_down", "thermal_down")]
    out["ring_covers_from_s"] = rnd((covered_from - t0) / 1000.0, 1) if covered_from is not None else None
    out["ring_lines"] = {k: sum(1 for e in pe if e["kind"] == k) for k in sorted({e["kind"] for e in pe})}
    # the burst limit: the first throttle-down line in the work (E80's reading) ...
    fk = m.get("first_down_kind")
    out["burst_limit"] = {"power_down": "power", "thermal_down": "thermal"}.get(fk, "none")
    # ... and the governor's inputs as the sampler reads them, beside it
    first800 = next((x for x in ws if x[4] == 800), None)
    lab = {"power": 0, "thermal": 0, "below": 0}
    if first800:
        for x in ws:
            if x[0] <= first800[0] or x[4] is None or x[4] >= 800:
                continue
            lab["below"] += 1
            if any(y[1] is not None and y[1] >= HOT_C for y in s if x[0] - 2000 <= y[0] <= x[0]):
                lab["thermal"] += 1
            elif any(y[5] is not None and y[5] > tdp_w for y in s if x[0] - 500 <= y[0] <= x[0]):
                lab["power"] += 1
    out["burst_inputs"] = lab
    out["burst_limit_inputs"] = ("thermal" if lab["thermal"] and lab["thermal"] >= lab["power"] else
                                 ("power" if lab["power"] else "none"))
    out["burst_avg_max_w"] = rnd(max((x[5] for x in ws if x[5] is not None), default=None) or None, 2)
    out["burst_die_max"] = max((x[1] for x in ws if x[1] is not None), default=None)
    # the sustained labels
    if r["block"] in ("SUS", "SUS2") and ws:
        tl = t1 - SUS_LAST_S * 1000
        last = [x for x in ws if x[0] >= tl and x[4] is not None]
        c = {"800": 0, "thermal": 0, "power": 0, "ramp": 0, "other": 0}
        c_ring = {"thermal": 0, "power": 0, "covered_below": 0}
        labelled = []
        for x in last:
            if x[4] == 800:
                c["800"] += 1
                labelled.append((x, "800"))
                continue
            ps = proc_start(x[0])
            covered = covered_from is not None and x[0] >= covered_from
            prior = [k for t, k in downs if ps <= t <= x[0]]
            line = prior[-1] if (covered and prior) else None
            if covered:
                c_ring["covered_below"] += 1
                if line == "thermal_down":
                    c_ring["thermal"] += 1
                elif line == "power_down":
                    c_ring["power"] += 1
            hot = any(y[1] is not None and y[1] >= HOT_C for y in s if x[0] - 2000 <= y[0] <= x[0])
            over = any(y[5] is not None and y[5] > tdp_w for y in s if x[0] - 500 <= y[0] <= x[0])
            seen800 = any(y[4] == 800 for y in ws if ps <= y[0] < x[0])
            if line == "thermal_down" or hot:
                lb = "thermal"
            elif line == "power_down" or (not covered and over):
                lb = "power"
            elif not seen800:
                lb = "ramp"
            else:
                lb = "other"
            c[lb] += 1
            labelled.append((x, lb))
        n = len(last)
        nr = n - c["ramp"]
        below = nr - c["800"]
        out["sus_counts"] = dict(c, n=n)
        out["sus_ring"] = c_ring
        out["sus_ramp_share"] = rnd(c["ramp"] / n, 3) if n else None
        out["sus_share800_nonramp"] = rnd(c["800"] / nr, 3) if nr else None
        if not nr:
            lim = "unresolved"
        elif c["800"] / nr >= NONE_SHARE:
            lim = "none"
        elif below and c["thermal"] / below >= 0.5:
            lim = "thermal"
        elif below and c["power"] / below >= 0.5:
            lim = "power"
        else:
            lim = "unresolved"
        out["sus_limit"] = lim
        out["sus_mhz_nonramp"] = rnd(mean([x[4] for x, lb in labelled if lb != "ramp"]), 1)
        out["sus_avg_w"] = rnd(mean([x[5] for x in last if x[5] is not None]), 2)
        out["sus_die_max"] = max((x[1] for x in last if x[1] is not None), default=None)
        out["sus_mhz_all"] = rnd(mean([x[4] for x in last]), 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions.json"))
    ap.add_argument("--e80")
    ap.add_argument("--out")
    a = ap.parse_args()
    pred = json.load(open(a.pred))
    runs = []
    cfg_reads = []
    for rd in a.rundirs:
        sess, rr, launches, q0 = R.load_session(rd)
        start_cfg = next(((q.get("config") or {}) for q in q0 if q.get("tag") == "start"), {}) or {}
        tdp_w = float(start_cfg.get("tdp_w") or 65)
        cfg_reads += [{"tag": q.get("tag"), "config": q.get("config")} for q in q0]
        evs = R.sp_events_by_run(rd, sess, rr, q0)
        byrun = {}
        for L in launches:
            byrun.setdefault(L["run"], []).append(L)
        fit = R.fit_clock(evs, launches, sess)
        for r in rr:
            rm = dict(r, block="SUS") if r["block"] == "SUS2" else r
            m = R.run_metrics(rd, rm, byrun.get(r["run"], []), evs.get(r["run"]), fit)
            m["block"] = r["block"]
            m["session"] = os.path.basename(os.path.normpath(rd))
            m["dry"] = bool(sess.get("dry"))
            m["kind"] = kind_of(r["values"])
            m["config_after"] = (r.get("queries") or {}).get("config")
            m["residency_after"] = (r.get("queries") or {}).get("residency")
            m.update(run_extra(rd, r, byrun.get(r["run"], []), m, tdp_w))
            m.pop("trace", None)
            runs.append(m)
    kinds = list(pred["kinds"])
    cells = {}
    for k in kinds:
        P = pred["kinds"][k]
        bu = [m for m in runs if m["kind"] == k and m["block"] == "BURST"]
        su = [m for m in runs if m["kind"] == k and m["block"] in ("SUS", "SUS2")]
        c = {"kind": k, "type": P["type"], "n_burst": len(bu), "n_sus": len(su),
             "pred_burst_limit": P["burst_limit"], "pred_sus_limit": P["sus_limit"]}
        if bu:
            c.update({"burst_mhz": rnd(mean([m["burst_mhz"] for m in bu])), "burst_mhz_runs": [m["burst_mhz"] for m in bu],
                      "burst_rate": rnd(mean([m["burst_rate"] for m in bu]), 3),
                      "burst_rate_runs": [m["burst_rate"] for m in bu],
                      "burst_ghz_kernel_runs": [m["burst_ghz_kernel"] for m in bu],
                      "p800_w": rnd(mean([m["p800_w"] for m in bu]), 2), "p800_w_runs": [m["p800_w"] for m in bu],
                      "burst_w": rnd(mean([m["burst_w"] for m in bu]), 2),
                      "burst_avg_max_w_runs": [m["burst_avg_max_w"] for m in bu],
                      "idle_w_runs": [m["idle_w"] for m in bu], "idle_mhz_runs": [m["idle_mhz"] for m in bu],
                      "burst_die_start": [m["die_start"] for m in bu], "burst_die_max": [m["die_max"] for m in bu],
                      "t_to_800_s": [m.get("t_to_800_s") for m in bu],
                      "burst_limit_runs": [m["burst_limit"] for m in bu],
                      "burst_limit_inputs_runs": [m["burst_limit_inputs"] for m in bu],
                      "burst_power_downs": [len(m.get("work_power_down") or []) for m in bu],
                      "burst_thermal_downs": [len(m.get("work_thermal_down") or []) for m in bu],
                      "burst_offpts": sorted({p for m in bu for p in m["burst_offpts"]})})
            lr = c["burst_limit_runs"]
            c["burst_limit"] = lr[0] if len(set(lr)) == 1 else "/".join(lr)
        if su:
            c.update({"sus_mhz": rnd(mean([m["sus_mhz_all"] for m in su])), "sus_mhz_runs": [m["sus_mhz_all"] for m in su],
                      "sus_mhz_nonramp": rnd(mean([m["sus_mhz_nonramp"] for m in su])),
                      "sus_rate": rnd(mean([m.get("sus_rate_t") for m in su]), 3),
                      "sus_rate_runs": [m.get("sus_rate_t") for m in su],
                      "sus_rate_wall": rnd(mean([m.get("sus_rate_wall_t") for m in su]), 3),
                      "sus_w": rnd(mean([m.get("sus_w_mean") for m in su]), 2),
                      "sus_avg_w": rnd(mean([m.get("sus_avg_w") for m in su]), 2),
                      "sus_die": rnd(mean([m.get("sus_die_mean") for m in su]), 2),
                      "sus_die_max": [m.get("sus_die_max") for m in su],
                      "sus_die_start": [m["die_start"] for m in su],
                      "sus_ramp_share": [m.get("sus_ramp_share") for m in su],
                      "sus_counts": [m.get("sus_counts") for m in su], "sus_ring": [m.get("sus_ring") for m in su],
                      "sus_last_e64": [m.get("sus_last") for m in su],
                      "sus_limit_runs": [m.get("sus_limit") for m in su]})
            lr = c["sus_limit_runs"]
            c["sus_limit"] = lr[0] if len(set(lr)) == 1 else "/".join(lr)
        cells[k] = c
    for k, c in cells.items():
        z = cells.get(ZEROS[c["type"]])
        if z and c.get("p800_w") is not None and z.get("p800_w") is not None:
            c["p800_sw_w"] = round(c["p800_w"] - z["p800_w"], 2)

    rules = {}
    # E84-P1
    rows, ok, n = [], True, 0
    for f in ("fp32", "fp16", "int8"):
        z, h = cells.get(ZEROS[f], {}), cells.get(HEAVY[f], {})
        for q in ("burst_mhz", "sus_mhz"):
            if z.get(q) is None or h.get(q) is None:
                rows.append([f, q, None, None, None, "missing"])
                continue
            d = round(z[q] - h[q], 1)
            n += 1
            good = d >= P1_TOL
            ok = ok and good
            rows.append([f, q, z[q], h[q], d, "ok" if good else "MISS"])
    rules["E84-P1"] = {"rows": rows, "tol_mhz": P1_TOL, "population": n,
                       "verdict": ("PASS" if ok else "FAIL") if n == 6 else ("FAIL" if not ok else "UNDER-RESOLVED")}
    # E84-P2
    rows, ok, n = [], True, 0
    for q in ("burst_mhz", "sus_mhz"):
        d = {f: (800 - cells[HEAVY[f]][q]) if cells.get(HEAVY[f], {}).get(q) is not None else None
             for f in ("fp32", "fp16", "int8")}
        if None in d.values():
            rows.append([q, d, "missing"])
            continue
        n += 1
        good = d["int8"] <= d["fp16"] + P2_TOL and d["int8"] <= d["fp32"] + P2_TOL
        ok = ok and good
        rows.append([q, {f: round(v, 1) for f, v in d.items()}, "ok" if good else "MISS"])
    rules["E84-P2"] = {"rows": rows, "tol_mhz": P2_TOL, "population": n,
                       "verdict": ("PASS" if ok else "FAIL") if n == 2 else ("FAIL" if not ok else "UNDER-RESOLVED")}
    # E84-P3
    out3 = {}
    for blk, key, pk, rk in (("burst", "burst_limit_runs", "pred_burst_limit", "n_burst"),
                             ("sustained", "sus_limit_runs", "pred_sus_limit", "n_sus")):
        have = [c for c in cells.values() if c.get(rk)]
        right = [c["kind"] for c in have if all(x == c[pk] for x in c[key])]
        wrong = [[c["kind"], c[pk], c[key]] for c in have if c["kind"] not in right]
        out3[blk] = {"population": len(have), "right": len(right), "wrong": wrong,
                     "verdict": ("PASS" if len(right) >= P3_RIGHT else "FAIL") if len(have) == 11 else
                     ("FAIL" if len(have) - len(right) > 11 - P3_RIGHT else "UNDER-RESOLVED")}
    v = [x["verdict"] for x in out3.values()]
    rules["E84-P3"] = dict(out3, need=P3_RIGHT, verdict=("PASS" if all(x == "PASS" for x in v) else
                                                         ("FAIL" if "FAIL" in v else "UNDER-RESOLVED")))
    # E84-S1
    fm = {}
    for f in ("fp32", "fp16", "int8"):
        xs = [800 - c["sus_mhz"] for c in cells.values() if c["type"] == f and c.get("sus_mhz") is not None]
        fm[f] = round(mean(xs), 1) if xs else None
    good = None if None in fm.values() else (fm["int8"] <= fm["fp16"] + P2_TOL and fm["int8"] <= fm["fp32"] + P2_TOL)
    rules["E84-S1"] = {"format_mean_deficit_mhz": fm, "verdict": "UNDER-RESOLVED" if good is None else
                       ("PASS" if good else "FAIL")}

    # context: aifoundry2 (E80), never a verdict
    ctx = {}
    if a.e80 and os.path.exists(a.e80):
        E = json.load(open(a.e80)).get("cells", {})
        for k, c in cells.items():
            e = E.get(k)
            if not e:
                continue
            ctx[k] = {"a2_burst_mhz": e.get("burst_mhz"), "a2_sus_mhz": e.get("sus_mhz"),
                      "a2_burst_limit": e.get("burst_limit"), "a2_sus_limit": e.get("sus_limit"),
                      "a2_p800_w": e.get("burst_p800_w"), "a2_burst_rate": e.get("burst_rate"),
                      "a2_sus_rate": e.get("sus_rate"),
                      "c0_minus_a2_burst_mhz": rnd(c["burst_mhz"] - e["burst_mhz"]) if c.get("burst_mhz") is not None
                      and e.get("burst_mhz") is not None else None,
                      "c0_minus_a2_sus_mhz": rnd(c["sus_mhz"] - e["sus_mhz"]) if c.get("sus_mhz") is not None
                      and e.get("sus_mhz") is not None else None}
    ratio = {}
    for f in ("fp32", "fp16", "int8"):
        z, h = cells.get(ZEROS[f], {}), cells.get(HEAVY[f], {})
        ratio[f] = {q: (round(z[q] / h[q], 4) if z.get(q) and h.get(q) else None) for q in ("burst_mhz", "sus_mhz")}
    res = {"experiment": "E84", "card": "aifoundry1-c0", "config_reads": cfg_reads, "rules": rules, "cells": cells,
           "zeros_over_heavy_clock": ratio, "context_aifoundry2_e80": ctx, "runs": runs}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=str)
    # the console table
    print("E84 on aifoundry1 card 0: per kind (burst = mean of passes; sustained = last 40 s, all samples)")
    print(f"{'kind':16s} {'burst MHz':>16s} {'rate':>7s} {'p800 W':>7s} {'sw800':>6s} {'blim':>8s}/{'pred':<8s} "
          f"{'sus MHz':>8s} {'nonramp':>7s} {'ramp':>5s} {'sus W':>6s} {'die':>5s} {'slim':>10s}/{'pred':<8s}")
    for k, c in cells.items():
        print(f"{k:16s} {str(c.get('burst_mhz_runs')):>16s} {str(c.get('burst_rate')):>7s} {str(c.get('p800_w')):>7s} "
              f"{str(c.get('p800_sw_w')):>6s} {str(c.get('burst_limit')):>8s}/{c['pred_burst_limit']:<8s} "
              f"{str(c.get('sus_mhz')):>8s} {str(c.get('sus_mhz_nonramp')):>7s} "
              f"{str((c.get('sus_ramp_share') or [None])[0]):>5s} {str(c.get('sus_w')):>6s} {str(c.get('sus_die')):>5s} "
              f"{str(c.get('sus_limit')):>10s}/{c['pred_sus_limit']:<8s}")
    for name, rr in rules.items():
        print(name, rr["verdict"], json.dumps({kk: vv for kk, vv in rr.items() if kk != "verdict"}, default=str)[:600])
    print("zeros/heavy clock ratio:", json.dumps(ratio))
    if ctx:
        print("aifoundry2 (E80) beside:", json.dumps({k: [v["a2_burst_mhz"], v["a2_sus_mhz"], v["a2_burst_limit"],
                                                          v["a2_sus_limit"]] for k, v in ctx.items()}))


if __name__ == "__main__":
    main()
