#!/usr/bin/env python3
"""E64 (Q123), Horace: power limit. The registered reduction: per-run metrics, the service processor's own governor
lines, the four decision rules of README.md, and the data the page draws.

    python3 reduce_hpl.py <RUNDIR> [<RUNDIR> ...] [--out results.json]

Every RUNDIR is one session of run_hpl.py (runs.jsonl, launches.jsonl, tel/<run>.jsonl, sp/<run>.bin). A dry
session (session.json "dry": true) carries the toy card's events in runs.jsonl instead of trace dumps.

What a run yields (README.md, "Measurements"):
  p800_w     the median board reading over the work samples at 800 MHz in the first 1.0 s after the clock first
             reads 800 (at least 2 samples; else the one sample): what the work draws at the top point
  mhz_*      the share of work samples at 600 / 700 / 800 MHz, and their mean
  ghz_eff    the kernel's own cycles over its wall time, summed over the launches (sparsity_host's `ghz`)
  rate       operations per second from the launches: minions x iters x 2*16*16*K / wall (K 16, 32, 64 for fp32,
             fp16, int8), in TFLOPS or TOPS
  events     the governor lines the SP logged since the previous dump (sptrace_events.since), by kind, each placed
             on the host clock by one session-wide fit (sptrace_events.fit_ticks: kernel starts and process ends)
"""
import argparse
import bisect
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "dv2"))
import sptrace_events as spe  # noqa: E402

OPS = {"fp32": 2 * 16 * 16 * 16, "fp16": 2 * 16 * 16 * 32, "int8": 2 * 16 * 16 * 64}
TDP_MW = 65000
R1_MIN_W, R2_MAX_W = 67.0, 62.0
SUS_LAST_S = 40.0
RAMP_S = 1.5


def jl(path):
    out = []
    if os.path.exists(path):
        for ln in open(path):
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
            ms = d.get("temp_c", {}).get("minshire") or [None, None, None]
            s.append((int(d["t_ms"]), ms[0], ms[2] if len(ms) > 2 else None, d.get("board_w"),
                      d.get("mhz", {}).get("minion")))
        except (KeyError, TypeError, ValueError, AttributeError):
            pass
    s.sort()
    return s


def med(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else None


def die_at(samples, t_ms):
    """The die reading at or just before t_ms."""
    ts = [x[0] for x in samples]
    i = bisect.bisect_right(ts, t_ms) - 1
    return samples[i][1] if i >= 0 else None


def load_session(rundir):
    sess = json.load(open(os.path.join(rundir, "session.json")))
    runs = jl(os.path.join(rundir, "runs.jsonl"))
    launches = jl(os.path.join(rundir, "launches.jsonl"))
    q0 = jl(os.path.join(rundir, "queries.jsonl"))
    return sess, runs, launches, q0


def sp_events_by_run(rundir, sess, runs, q0):
    """{run: [event]} with the events new since the previous dump, in SP order."""
    out = {}
    if sess.get("dry"):
        for r in runs:
            out[r["run"]] = [{"kind": k, "ts": i, "pwr_mw": v if "power" in k else None,
                              "T": v if "thermal" in k else None} for i, (k, v) in
                             enumerate(r["queries"].get("sp_events", []))]
        return out
    prev = []
    start = os.path.join(rundir, "sp", "start.bin")
    if os.path.exists(start):
        prev = spe.events(open(start, "rb").read())
    for r in runs:
        p = os.path.join(rundir, "sp", f"{r['run']}.bin")
        if not os.path.exists(p):
            out[r["run"]] = None
            continue
        cur = spe.events(open(p, "rb").read())
        new = spe.since(prev, cur) if prev else [e for e in cur if e["ts"] is not None]
        out[r["run"]] = [e for e in new if e["kind"] in spe.GOVERNOR]
        out[r["run"] + "#overlap"] = spe.overlap(prev, cur) if prev else None
        prev = cur
    return out


def fit_clock(evs_by_run, launches, sess):
    """One host_ms = a + b * ts fit for the session (sptrace_events.fit_ticks), or None."""
    if sess.get("dry"):
        return None
    sp, anchors = [], []
    for run, evs in evs_by_run.items():
        if run.endswith("#overlap") or not evs:
            continue
        idle = True
        for e in evs:
            if e["kind"] == "power_idle":
                sp.append((e["ts"], "end"))
                idle = True
            elif e["kind"] in spe.POWER_START and idle:
                sp.append((e["ts"], "start"))
                idle = False
    for L in launches:
        anchors.append((L["t_start_ms"], "start"))
        anchors.append((L["t_end_ms"], "end"))
    return spe.fit_ticks(sp, anchors, lag_ms=(0.0, 1600.0))


def run_metrics(rundir, r, procs, evs, fit):
    s = tel(os.path.join(rundir, r["tel"]))
    work_procs = [p for p in procs if p.get("role") == "work"]
    lw = []
    for p in work_procs:
        for k in p.get("sparsity", []):
            if k.get("t_start_ms") and k.get("t_end_ms"):
                lw.append(k)
    wins = [(p["t_start_ms"], p["t_end_ms"]) for p in work_procs]
    t0 = min((a for a, _ in wins), default=r["t_first_ms"])
    t1 = max((b for _, b in wins), default=r["t_last_ms"])
    if lw:
        kwins = [(k["t_start_ms"], k["t_end_ms"]) for k in lw]
    else:
        kwins = wins

    def in_work(t):
        return any(a <= t <= b for a, b in kwins)
    ws = [x for x in s if in_work(x[0])]
    m = {"run": r["run"], "block": r["block"], "label": r["label"], "type": r["type"], "values": r["values"],
         "minions": r["minions"], "rep": r["rep"], "gate": r["gate"], "n_samples": len(ws),
         "work_s": round((t1 - t0) / 1000.0, 2)}
    mh = [x[4] for x in ws if x[4] is not None]
    for f in (600, 700, 800):
        m[f"mhz_{f}"] = round(sum(1 for v in mh if v == f) / len(mh), 3) if mh else None
    m["mhz_mean"] = round(st.mean(mh), 1) if mh else None
    first800 = next((x for x in ws if x[4] == 800), None)
    m["t_to_800_s"] = round((first800[0] - t0) / 1000.0, 2) if first800 else None
    if first800:
        early = [x[3] for x in ws if x[4] == 800 and first800[0] <= x[0] <= first800[0] + 1000]
        m["p800_w"] = round(med(early), 2) if len(early) >= 2 else (early[0] if early else None)
        after = [x for x in ws if x[0] > first800[0]]
        down = next((x for x in after if x[4] is not None and x[4] < 800), None)
        if down:
            prev = [x for x in ws if x[0] < down[0]][-3:]
            m["first_down"] = {"t_s": round((down[0] - t0) / 1000.0, 2), "to_mhz": down[4], "die": down[1],
                               "die_prev": prev[-1][1] if prev else None,
                               "w_prev": [x[3] for x in prev]}
        else:
            m["first_down"] = None
    else:
        m["p800_w"], m["first_down"] = None, None
    for f in (600, 700, 800):
        m[f"p{f}_med_w"] = med([x[3] for x in ws if x[4] == f])
    dies = [x[1] for x in ws if x[1] is not None]
    m["die_start"] = dies[0] if dies else None
    m["die_max"] = max(dies) if dies else None
    m["die_end"] = dies[-1] if dies else None
    # the kernel's own count: cycles over wall, and the rate
    cyc = sum(k.get("cycles_max", 0) for k in lw)
    wall = sum(k.get("wall_s", 0) for k in lw)
    ops = sum(k.get("minions", r["minions"]) * k.get("iters", 0) * OPS[r["type"]] for k in lw)
    m["ghz_eff"] = round(cyc / wall / 1e9, 4) if wall and cyc else None
    m["rate_t"] = round(ops / wall / 1e12, 3) if wall and ops else None
    m["cycles_per_op"] = med([k.get("cycles_per_op") for k in lw])
    m["launch_ok"] = sum(1 for k in lw if k.get("ok"))
    m["launch_n"] = len(lw)
    m["results"] = sorted({k.get("result") for k in lw if k.get("result")})
    # governor events
    if evs is None:
        m["events"] = None
    else:
        kinds = {}
        for e in evs:
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
        m["events"] = kinds
        placed = []
        for e in evs:
            h = fit["a_ms"] + fit["b_ms_per_tick"] * e["ts"] if (fit and e.get("ts") is not None) else None
            placed.append({"kind": e["kind"], "pwr_mw": e.get("pwr_mw"), "T": e.get("T"),
                           "t_s": round((h - t0) / 1000.0, 2) if h is not None else None,
                           "die": die_at(s, h) if h is not None else None,
                           "in_work": (h is not None and t0 - 200 <= h <= t1 + 1500)})
        m["event_list"] = placed
        work_ev = [e for e in placed if e["in_work"]] if fit else placed
        m["work_power_down"] = [e for e in work_ev if e["kind"] == "power_down"]
        m["work_thermal_down"] = [e for e in work_ev if e["kind"] == "thermal_down"]
        first_kinds = [e["kind"] for e in work_ev if e["kind"] in ("power_down", "thermal_down")]
        m["first_down_kind"] = first_kinds[0] if first_kinds else None
    # the sustained runs: the last SUS_LAST_S seconds of work
    if r["block"] == "SUS" and ws:
        tl = t1 - SUS_LAST_S * 1000
        last = [x for x in ws if x[0] >= tl]
        starts = [p["t_start_ms"] for p in work_procs]
        lab = {"800": 0, "thermal": 0, "power": 0, "ramp": 0, "other": 0}
        pe = [e for e in (m.get("event_list") or []) if e["t_s"] is not None]
        for x in last:
            if x[4] == 800:
                lab["800"] += 1
                continue
            recent_hot = any(y[1] is not None and y[1] >= 66 for y in ws if x[0] - 2000 <= y[0] <= x[0])
            prior = [e for e in pe if t0 + e["t_s"] * 1000 <= x[0] and e["kind"] != "power_up"]
            last_ev = prior[-1]["kind"] if prior else None
            ramp = any(0 <= x[0] - a <= RAMP_S * 1000 for a in starts)
            if recent_hot or last_ev in ("thermal_down",):
                lab["thermal"] += 1
            elif last_ev == "power_down":
                lab["power"] += 1
            elif ramp:
                lab["ramp"] += 1
            else:
                lab["other"] += 1
        n = len(last)
        m["sus_last"] = {k: round(v / n, 3) for k, v in lab.items()} if n else None
        lw_last = [k for k in lw if k["t_start_ms"] >= tl]
        wl = sum(k.get("wall_s", 0) for k in lw_last)
        ol = sum(k.get("minions", r["minions"]) * k.get("iters", 0) * OPS[r["type"]] for k in lw_last)
        cl = sum(k.get("cycles_max", 0) for k in lw_last)
        m["sus_rate_t"] = round(ol / wl / 1e12, 3) if wl and ol else None
        m["sus_ghz_eff"] = round(cl / wl / 1e9, 4) if wl and cl else None
        m["sus_mhz_mean"] = round(st.mean([x[4] for x in last if x[4] is not None]), 1)
        m["sus_die_mean"] = round(st.mean([x[1] for x in last if x[1] is not None]), 1)
        m["sus_w_mean"] = round(st.mean([x[3] for x in last if x[3] is not None]), 2)
        # wall-clock duty: the work's ops over the whole span, gaps between processes included
        span = (t1 - tl) / 1000.0
        m["sus_rate_wall_t"] = round(ol / span / 1e12, 3) if span > 0 and ol else None
        bins = []
        for b0 in range(int(t0), int(t1), 2000):
            xs = [x for x in ws if b0 <= x[0] < b0 + 2000]
            if xs:
                bins.append({"t_s": round((b0 - t0) / 1000.0, 1),
                             "mhz": round(st.mean([x[4] for x in xs if x[4]]), 1),
                             "die": round(st.mean([x[1] for x in xs if x[1] is not None]), 2),
                             "w": round(st.mean([x[3] for x in xs if x[3] is not None]), 2)})
        m["sus_bins"] = bins
    # the clock trace, thinned, for the page
    m["trace"] = [[round((x[0] - t0) / 1000.0, 2), x[1], x[3], x[4]] for x in s
                  if t0 - 3000 <= x[0] <= t1 + 4000][::1]
    return m


def rules(metrics):
    out = {}
    lad = [m for m in metrics if m["block"] in ("LAD", "MIN") and m.get("p800_w") is not None]
    hi = [m for m in lad if m["p800_w"] >= R1_MIN_W]
    lo = [m for m in lad if m["p800_w"] <= R2_MAX_W]

    def r1_ok(m):
        pd = [e for e in (m.get("work_power_down") or []) if (e.get("pwr_mw") or 0) > TDP_MW]
        return bool(pd) and m.get("first_down_kind") == "power_down"
    n1 = sum(1 for m in hi if r1_ok(m))
    out["R1"] = {"population": len(hi), "with_power_down_first": n1,
                 "die_le_65_at_first_step": sum(1 for m in hi if m.get("first_down")
                                                and (m["first_down"].get("die_prev") or 99) <= 65),
                 "verdict": ("PASS" if hi and n1 >= 0.9 * len(hi) else "FAIL") if len(hi) >= 4 else "UNDER-RESOLVED",
                 "runs": [[m["run"], m["p800_w"], r1_ok(m)] for m in hi]}
    n2 = sum(1 for m in lo if m.get("work_power_down"))
    out["R2"] = {"population": len(lo), "with_power_down": n2,
                 "verdict": ("PASS" if n2 <= 0.1 * len(lo) else "FAIL") if len(lo) >= 4 else "UNDER-RESOLVED",
                 "runs": [[m["run"], m["p800_w"], bool(m.get("work_power_down"))] for m in lo]}
    hot = [m for m in metrics if m["block"] == "HOT"]
    a_runs = [m for m in hot if "edge67" in m["label"]]
    b_runs = [m for m in hot if "edge63" in m["label"]]

    def a_ok(m):
        bad = 0
        for t, die, w, mhz in m["trace"]:
            if t < 0:
                continue
            if die is not None and die <= 65:
                break
            if mhz is not None and mhz > 600 and t <= m["work_s"]:
                bad += 1
        return bad <= 1

    def b_applies(m):
        """The die read 66 or more during the work within 1.0 s of a sample at 800 MHz (the step comes within a
        pass or two of the reading, so requiring both in one 100 ms sample would be a race)."""
        tr = [x for x in m["trace"] if 0 <= x[0] <= m["work_s"]]
        return any(x[1] is not None and x[1] >= 66 and any(y[3] == 800 and x[0] - 1.0 <= y[0] <= x[0] for y in tr)
                   for x in tr)

    def b_ok(m):
        return bool(m.get("work_thermal_down")) and not m.get("work_power_down")
    a_n = sum(1 for m in a_runs if a_ok(m))
    b_ap = [m for m in b_runs if b_applies(m)]
    b_n = sum(1 for m in b_ap if b_ok(m))
    ok_a = len(a_runs) >= 2 and a_n == len(a_runs)
    ok_b = len(b_ap) >= 2 and b_n == len(b_ap)
    out["R3"] = {"a_population": len(a_runs), "a_held_600_until_65": a_n, "b_population_reaching_66": len(b_ap),
                 "b_thermal_not_power": b_n,
                 "verdict": "PASS" if ok_a and ok_b else ("UNDER-RESOLVED" if len(b_ap) < 2 or len(a_runs) < 2
                                                          else "FAIL"),
                 "runs": [[m["run"], a_ok(m) if m in a_runs else None,
                           (b_applies(m), b_ok(m)) if m in b_runs else None] for m in hot]}
    sus = [m for m in metrics if m["block"] == "SUS" and m.get("sus_last")]
    rows = []
    for m in sus:
        sl = m["sus_last"]
        below = 1 - sl["800"]
        th_share = sl["thermal"] / below if below > 0 else None
        rows.append({"run": m["run"], "type": m["type"], "values": m["values"], "at_800": sl["800"],
                     "thermal_share_of_below": round(th_share, 3) if th_share is not None else None,
                     "power_share_of_below": round(sl["power"] / below, 3) if below > 0 else None,
                     "rate_t": m.get("sus_rate_t"), "die": m.get("sus_die_mean")})
    rnd = [x for x in rows if x["values"] in ("randn",)]
    zer = [x for x in rows if x["values"] == "zeros"]
    p4a = all((x["thermal_share_of_below"] or 0) >= 0.6 for x in rnd) if rnd else None
    p4b = all(x["at_800"] >= 0.9 for x in zer) if zer else None
    out["R4"] = {"rows": rows, "randn_thermal_share_ge_0.6": p4a, "zeros_at_800_ge_0.9": p4b,
                 "verdict": ("PASS" if p4a and p4b else "FAIL") if rnd and zer else "UNDER-RESOLVED"}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--out")
    a = ap.parse_args()
    metrics, fits = [], {}
    for rd in a.rundirs:
        sess, runs, launches, q0 = load_session(rd)
        evs = sp_events_by_run(rd, sess, runs, q0)
        byrun = {}
        for L in launches:
            byrun.setdefault(L["run"], []).append(L)
        fit = fit_clock(evs, launches, sess)
        fits[rd] = fit
        for r in runs:
            metrics.append(run_metrics(rd, r, byrun.get(r["run"], []), evs.get(r["run"]), fit))
    res = {"fits": fits, "rules": rules(metrics), "runs": metrics}
    for m in metrics:
        fd = m.get("first_down") or {}
        print(f"{m['run']:40s} p800 {m.get('p800_w')!s:>6} mhz {m.get('mhz_mean')!s:>6} ghz {m.get('ghz_eff')!s:>6} "
              f"rate {m.get('rate_t')!s:>7} die {m.get('die_start')}->{m.get('die_max')} "
              f"down@{fd.get('t_s')}s die{fd.get('die_prev')} first={m.get('first_down_kind')} ev={m.get('events')}")
    for k, v in res["rules"].items():
        print(k, v.get("verdict"), {x: y for x, y in v.items() if x not in ("runs", "rows", "verdict")})
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
