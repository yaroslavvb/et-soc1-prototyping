#!/usr/bin/env python3
"""1119-mmsweep5: a session directory into per-run and per-arm numbers (E190's reducer form, tools/claims-v3/e190/reduce_e190.py
in the public lab repo, extended). Python's own modules only; it changes nothing it reads. Every rule here is registered before
any datum exists (request.md section 8).

    python3 -I -B src/reduce_mms.py <session dir> --out data-mms.json [--txt reduce-mms.txt]
    python3 -I -B src/reduce_mms.py --combine data-1.json data-2.json ... --out combined.json [--txt combined.txt]

LAUNCHES: fma launches with launch >= 0, ok, wall_s >= 0.1 s, passes >= 1 (every process of a run: three in the sus3 form);
each launch's kernel clock is cycles_max / wall_s.
BLOCK ARMS (the host's block, stream and TenB arms; src/mms_common.py arm_of): read by the same rules from the same records
(ops a minion = the launch record's iters, the host's passes x its ops a pass); a run of one also carries arm_token,
arm_family, ops_pass (ops a minion a pass by the host's grammar), macs_minion_pass (x the type's multiply-adds an op) and
ops_pass_ok (every counted launch's iters = passes x ops_pass). A gemmL run's keys are unchanged.

VIEWS of a run (each: n_launch, T_op_us = sum wall / sum ops a minion, cycles an op (max and mean), the kernel clock, t_pass_s,
and, where energy is read, the board and the rails):
  band <b>  the launches in a clock band (governed cards: 800, 700, 600 MHz; card 1: 600). On the governed cards the bands give
            TIME ONLY (no board, no rails: the 600 MHz launch sits in the governor's step and the meter's refresh).
  win       governed cards: the launches starting WIN_LO_S-WIN_HI_S (1.0-3.5 s) after their own process's launch 0 started and in
            the 800 MHz band, pooled over the run's processes: the same part of every burst for every arm. THE PRIMARY VIEW there.
  burst     every launch of the run at the governor's own clock mix, with its clock histogram (10 MHz bins) and the launches'
            own records (start, end, wall, ops, clock, board): the whole-burst figure, for scoring on the measured clock trace.
  The primary view: `win` on the governed cards, `band 600` on card 1; on a governed card whose governor never left 600 MHz in
  the run (every launch in the 600 band), `band 600` read for energy and the run flagged no_step. A view needs MIN_LAUNCH
  launches and MIN_SAMPLES board samples (the window: MIN_LAUNCH_WIN and MIN_SAMPLES_WIN), else it is thin and carries no energy.
CAPPED (governed cards): of the run's launches starting WIN_LO_S or more after their process's launch 0 (past the governor's step
  from its 600 MHz start), fewer than CAPPED_FRAC (80%) in the 800 MHz band. A capped run's energy is not read nor contrasted with an
  uncapped run's (its power is the governor's set point, not the arm's); a `time` run is never read for energy.
BOARD in a view: the 10 Hz samples inside its launches, less those the reader took over SLOW_SAMPLE_MS to read; p_med (median)
  and p_mean (the mean after the dip rule: a sample under median - 4 x 1.4826 x MAD, MAD at least 0.05 W, is a dip and left out).
BASELINES, each evaluated at the view's centre (the mean time of its samples):
  line      a least-squares line through the board over the whole rest before the run's first process (10 s; 20 s in sus3)
  plain     the median of the last 5 s of that rest (E190's footing)
  bracket   the straight line through the mean of the last 5 s of the rest and the mean of the tail from 3 s after the last
            process to the tail's end (the burst's own heat lifts the tail: for small lifts only)
  primary   line in the burst form; bracket in the sus3 form. dP = p_mean - primary; J_op = dP x T_op / minions over idle;
            pJ_mac; J_pass over idle and with the card at rest (p_mean x t_pass). dP_med, dP_plain, dP_line, dP_bracket beside.
RAILS (minion, SRAM, mesh): the rails are the PMIC's running averages, a first-order filter (tau per card and rail, the lab's
  tools/ettelem/deconv.py offline fits) reaching the host one service-processor pass late. Each segment of the stream is undone on
  its own pass grid (a pass: a sample where any SP value changed, timed half a sampling interval before it; its value describes
  the pass before it): x_k = (y_k - a_k y_(k-1)) / (1 - a_k), a_k = exp(-(te_k - te_(k-1)) / tau), the mean power over
  (te_(k-1), te_k] (the lab's exact inverse, without its smoothing, which a window mean does not need); before it, a rail average
  equal to its running maximum and over 1.2 x the last good value (card 1's spike) is replaced by that value. A rail's lift in a view
  is the time-weighted mean of x over the view's launches less the same baseline rule applied to x over the rest (and tail), so
  the board and the rails are read over the same window; with the rail's mV, J and electrons an op by rail. rails_late beside
  it: the raw reading's mean over the last 1.5 s of the run's last process's launches less the raw rest median (no 0.94).
DIE: die_start_c (the mean of the last 5 s of rest), die_win_c (the view's mean), die_max_c, die_tail_c.
DDR DROOP (the lab's droop meter's windows, tools/ettelem/fit_unmetered.py): the mean on-die DDR monitor voltage from 2.5 to
  0.2 s before the run's first process less its mean over the view's samples from 0.5 s after the view's first launch: a witness
  of DRAM traffic per run (with the minion monitor's droop beside it).
NULL runs: the same windows with no process (pretend launches of 0.5 s from 0.6 s into the window): every rule's reading at zero
  signal; the session's null readings (mean, sd) are the baseline rules' bias and scatter.
PER SESSION: per arm the mean over its runs of the primary view (time-only runs: time); the anchors in order (drift); the nulls;
  THE DIE-START CORRECTION: dP_corr = dP / (1 + s (die_start - die_ref)), die_ref the session's median start die over the runs
  read for energy, s = the slope fitted on the session's anchors (dP against die_start, as a fraction of their mean) when their
  starts span 3 C or more and its standard error is under 0.0015 a degree, else DIE_SLOPE (the lab's 0.48 %/C on aifoundry2).
COMBINE (--combine): per card and arm, the mean over every session's runs of the primary figures (dP_corr, J_op_corr, T_op,
  rails), their sd and n, and an error: sd / sqrt(n) with n >= 2, else the session anchors' relative sd x the value; the nulls'
  bias per rule pooled.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import bisect
import gzip
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mms_common as C  # noqa: E402

RAILS = ("minion", "sram", "noc")
E_CHARGE = 1.602176634e-19
GAP_S = 1.0          # a longer gap in the stream is a sampler restart: a new segment for the rails' inverse


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def med(v):
    v = [x for x in v if x is not None]
    return statistics.median(v) if v else None


def sd(v):
    v = [x for x in v if x is not None]
    return statistics.stdev(v) if len(v) > 1 else None


def linfit(ts, ys):
    """(intercept, slope) of a least-squares line, or None with fewer than 3 points or no spread"""
    pts = [(t, y) for t, y in zip(ts, ys) if t is not None and y is not None]
    if len(pts) < 3:
        return None
    mt = sum(t for t, _ in pts) / len(pts)
    my = sum(y for _, y in pts) / len(pts)
    sxx = sum((t - mt) ** 2 for t, _ in pts)
    if sxx <= 0:
        return None
    b = sum((t - mt) * (y - my) for t, y in pts) / sxx
    return my - b * mt, b


# ---------------------------------------------------------------------------------------------------- the telemetry
class Tel:
    """The session's samples, sorted by time (s), with the rails' inverse on each segment's pass grid."""

    def __init__(self, rows, card, sc=1.0):
        self.rows = rows
        self.t = [r["t"] for r in rows]
        self.card, self.sc = card, sc
        self.spikes = self._despike()
        self.dec = {r: self._deconvolve(r) for r in RAILS}
        self.dec_a = {r: [d[0] for d in self.dec[r]] for r in RAILS}      # interval starts, sorted, for bisect

    def _despike(self):
        """card 1's spike (version 1's rule): a rail's average that equals its running maximum and is over 1.2 x the last good
        value is a spike; the last good value stands in for it, so it neither starts a pass nor enters the inverse"""
        n = {}
        for rail in RAILS:
            prev = None
            for row in self.rows:
                y, ymax = row.get(rail), row.get(rail + "_max")
                if y is None:
                    continue
                if prev is not None and ymax is not None and abs(y - ymax) < 1e-3 and y > 1.2 * prev:
                    row[rail] = prev
                    n[rail] = n.get(rail, 0) + 1
                    continue
                prev = y
        for row in self.rows:
            row["spkey"] = row["spkey"][:2] + tuple(row.get(r) for r in RAILS)
        return n

    def between(self, lo, hi):
        i, j = bisect.bisect_left(self.t, lo), bisect.bisect_right(self.t, hi)
        return self.rows[i:j]

    def _deconvolve(self, rail):
        """[(te_prev, te, x)]: the rail's mean power over each pass interval (te_prev, te], segment by segment"""
        tau = C.CARDS[self.card]["tau_s"][rail] * self.sc
        out = []
        segs, lo = [], 0
        for i in range(1, len(self.rows) + 1):
            if i == len(self.rows) or self.t[i] - self.t[i - 1] > GAP_S * self.sc:
                segs.append((lo, i))
                lo = i
        for lo, hi in segs:
            rows = self.rows[lo:hi]
            if len(rows) < 4:
                continue
            dts = [rows[k]["t"] - rows[k - 1]["t"] for k in range(1, len(rows))]
            step_med = statistics.median(dts) if dts else 0.1 * self.sc
            passes = []
            for k, r in enumerate(rows):
                if k == 0 or r["spkey"] != rows[k - 1]["spkey"]:
                    step = min(step_med, rows[k]["t"] - rows[k - 1]["t"]) if k else step_med
                    passes.append((r["t"] - 0.5 * step, r.get(rail)))
            if len(passes) < 3:
                continue
            tp = [p[0] for p in passes]
            ys = [p[1] for p in passes]
            dt = [tp[k] - tp[k - 1] for k in range(1, len(tp)) if tp[k] - tp[k - 1] < 1.0 * self.sc]
            P = sum(dt) / len(dt) if dt else 0.15 * self.sc
            te = [tp[0] - P] + tp[:-1] if C.LAG_PASSES else list(tp)     # one pass late: a value describes the pass before it
            if C.LAG_PASSES:                                             # after a pass not seen (over 3 periods), one period
                for k in range(1, len(tp)):
                    if tp[k] - tp[k - 1] > 3 * P:
                        te[k] = tp[k] - P
            for k in range(1, len(te)):
                if ys[k] is None or ys[k - 1] is None or te[k] <= te[k - 1]:
                    continue
                a = math.exp(-(te[k] - te[k - 1]) / tau)
                out.append((te[k - 1], te[k], (ys[k] - a * ys[k - 1]) / (1.0 - a)))
        return out

    def rail_mean(self, rail, intervals):
        """time-weighted mean of the rail's inverse over a union of intervals (s)"""
        num = den = 0.0
        d, starts = self.dec[rail], self.dec_a[rail]
        for lo, hi in intervals:
            i = max(0, bisect.bisect_left(starts, lo) - 1)
            while i < len(d) and d[i][0] < hi:
                a, b, x = d[i]
                i += 1
                if b <= lo:
                    continue
                w = min(b, hi) - max(a, lo)
                num += w * x
                den += w
        return num / den if den > 0 else None

    def rail_points(self, rail, lo, hi):
        """(mid, x) of the pass intervals inside [lo, hi], for the baseline fits"""
        d, starts = self.dec[rail], self.dec_a[rail]
        i, out = bisect.bisect_left(starts, lo), []
        while i < len(d) and d[i][0] < hi:
            a, b, x = d[i]
            i += 1
            if b <= hi:
                out.append(((a + b) / 2, x))
        return out


def load_tel(sd_, card, sc):
    p = os.path.join(sd_, "telemetry.jsonl.gz")
    rows = []
    if not os.path.exists(p):
        return Tel(rows, card, sc)
    with gzip.open(p, "rt") as f:
        for ln in f:
            if not ln.startswith("{"):
                continue
            try:
                s = json.loads(ln)
            except ValueError:
                continue
            if s.get("t_ms") is None:
                continue
            sp = s.get("sp") or {}
            dm = s.get("die_mv") or {}
            row = {"t": s["t_ms"] / 1000.0, "bw": s.get("board_w"), "die": C.die_of(s), "mhz": (s.get("mhz") or {}).get("minion"),
                   "took": s.get("took_ms"), "ddr_mv": dm.get("ddr"), "minion_dmv": dm.get("minion")}
            key = [s.get("board_w"), sp.get("board_avg_w")]
            for r in RAILS:
                w, mv = sp.get(r + "_w") or [None, None, None], sp.get(r + "_mv") or [None]
                row[r] = w[0]
                row[r + "_max"] = w[2] if len(w) > 2 else None
                row[r + "_mv"] = mv[0]
                key.append(w[0])
            row["spkey"] = tuple(key)
            rows.append(row)
    rows.sort(key=lambda x: x["t"])
    return Tel(rows, card, sc)


# ---------------------------------------------------------------------------------------------------- one view
def board_stats(rows):
    keep = [x["bw"] for x in rows if x["bw"] is not None and not (x.get("took") is not None and x["took"] > C.SLOW_SAMPLE_MS)]
    n_slow = sum(1 for x in rows if x.get("took") is not None and x["took"] > C.SLOW_SAMPLE_MS)
    if not keep:
        return None, None, 0, 0, n_slow
    m = statistics.median(keep)
    mad = max(0.05, 1.4826 * statistics.median([abs(v - m) for v in keep]))
    kept = [v for v in keep if v >= m - 4.0 * mad]
    return m, sum(kept) / len(kept), len(keep), len(keep) - len(kept), n_slow


def baselines(tel, t_first, rest0, tail0, tail1, tc, sc):
    """the three baseline rules for the board, at the time tc: {'line', 'plain', 'bracket'}"""
    rest = tel.between(rest0, t_first - 0.001 * sc)
    out = {}
    f = linfit([x["t"] for x in rest if x["bw"] is not None], [x["bw"] for x in rest if x["bw"] is not None])
    out["line"] = f[0] + f[1] * tc if f else None
    out["line_slope_w_s"] = f[1] / sc if f else None
    last5 = tel.between(t_first - 5.0 * sc, t_first - 0.001 * sc)
    out["plain"] = med([x["bw"] for x in last5])
    pre = [x for x in last5 if x["bw"] is not None]
    post = [x for x in tel.between(tail0, tail1) if x["bw"] is not None]
    if pre and post:
        tp, yp = mean([x["t"] for x in pre]), mean([x["bw"] for x in pre])
        tq, yq = mean([x["t"] for x in post]), mean([x["bw"] for x in post])
        out["bracket"] = yp + (yq - yp) * (tc - tp) / (tq - tp) if tq > tp else None
    else:
        out["bracket"] = None
    return out


def rail_baseline(tel, rail, t_first, rest0, tail0, tail1, tc, rule, sc):
    pts = tel.rail_points(rail, rest0, t_first)
    if rule == "line":
        f = linfit([p[0] for p in pts], [p[1] for p in pts])
        return f[0] + f[1] * tc if f else None
    if rule == "plain":
        return med([p[1] for p in tel.rail_points(rail, t_first - 5.0 * sc, t_first)])
    pre = tel.rail_points(rail, t_first - 5.0 * sc, t_first)
    post = tel.rail_points(rail, tail0, tail1)
    if not pre or not post:
        return None
    tp, yp = mean([p[0] for p in pre]), mean([p[1] for p in pre])
    tq, yq = mean([p[0] for p in post]), mean([p[1] for p in post])
    return yp + (yq - yp) * (tc - tp) / (tq - tp) if tq > tp else None


def view(card, launches, tel, ctx, energy, rule, thin_at):
    """the figures of one view over its launches; energy False: time only"""
    if not launches:
        return None
    sc = ctx["sc"]
    wall = sum(L["wall_s"] for L in launches)
    ops = sum(L["iters"] for L in launches)
    passes = sum(L["passes"] for L in launches)
    out = {"n_launch": len(launches), "ops_minion": ops, "passes": passes, "wall_s": round(wall, 6),
           "T_op_us": wall / ops * 1e6 if ops else None,
           "cyc_op_max": sum(L["cycles_max"] for L in launches) / ops if ops else None,
           "cyc_op_mean": sum(L.get("cycles_mean") or 0 for L in launches) / ops if ops else None,
           "kclock_mhz": sum(L["cycles_max"] for L in launches) / wall / 1e6 if wall else None,
           "t_pass_s": wall / passes if passes else None}
    if card == "a1c1":
        out["launch_overhead_ms"] = med([(L["wall_s"] - L["cycles_max"] / 600e6) * 1000 for L in launches])
    if not energy:
        return out
    ivs = [(L["t_start_ms"] / 1000.0, L["t_end_ms"] / 1000.0) for L in launches]
    rows = [x for lo, hi in ivs for x in tel.between(lo, hi)]
    p_med, p_mean, n_s, n_dip, n_slow = board_stats(rows)
    out.update(n_samples=n_s, n_dips=n_dip, n_slow_samples=n_slow, p_med_w=p_med, p_mean_w=p_mean,
               mhz_mean=mean([x["mhz"] for x in rows]), mhz_min=min([x["mhz"] for x in rows if x["mhz"] is not None], default=None))
    if len(launches) < thin_at[0] or n_s < thin_at[1] or p_mean is None:
        out["thin"] = True
        return out
    tc = mean([x["t"] for x in rows])
    bl = baselines(tel, ctx["t_first"], ctx["rest0"], ctx["tail0"], ctx["tail1"], tc, sc)
    base = bl.get(rule)
    out.update(baseline_rule=rule, baselines={k: v for k, v in bl.items()}, t_centre_s=tc)
    for k in ("line", "plain", "bracket"):
        out[f"dP_{k}"] = p_mean - bl[k] if bl.get(k) is not None else None
    if base is None:
        out["thin"] = True
        return out
    minions, macs = ctx["minions"], ctx["macs_op"]
    dP = p_mean - base
    T = out["T_op_us"] * 1e-6
    out.update(dP_w=dP, dP_med_w=p_med - base, J_op=dP * T / minions, pJ_mac=dP * T / minions / macs * 1e12,
               J_pass_over=dP * out["t_pass_s"], J_pass_with=p_mean * out["t_pass_s"])
    rails = {}
    for r in RAILS:
        x = tel.rail_mean(r, ivs)
        b = rail_baseline(tel, r, ctx["t_first"], ctx["rest0"], ctx["tail0"], ctx["tail1"], tc, rule, sc)
        mv = med([y[r + "_mv"] for y in rows])
        if x is None or b is None:
            continue
        d = x - b
        rails[r] = {"dW": d, "mV": mv, "rest_W": b, "J_op": d * T / minions,
                    "electrons_op": (d * T / minions) / (E_CHARGE * mv / 1000.0) if mv else None}
    out["rails"] = rails
    out["die_win_c"] = mean([x["die"] for x in rows])
    out["die_max_c"] = max([x["die"] for x in rows if x["die"] is not None], default=None)
    lo0 = min(lo for lo, _ in ivs) + 0.5 * sc
    busy = [x for lo, hi in ivs for x in tel.between(max(lo, lo0), hi)]
    idle = tel.between(ctx["t_first"] - 2.5 * sc, ctx["t_first"] - 0.2 * sc)
    for k, f in (("ddr", "ddr_mv"), ("minion", "minion_dmv")):
        a, b = mean([x[f] for x in idle]), mean([x[f] for x in busy])
        out[f"droop_{k}_mv"] = a - b if a is not None and b is not None else None
    return out


def clock_hist(launches):
    h = {}
    for L in launches:
        f = C.kclock(L)
        if f is None:
            continue
        b = f"{int(f // 10) * 10}"
        h[b] = h.get(b, 0) + 1
    return dict(sorted(h.items(), key=lambda kv: int(kv[0])))


# ---------------------------------------------------------------------------------------------------- one run
def reduce_run(sd_, rdir, card, tel, sc=1.0):
    rec = C.load(os.path.join(rdir, "run.json"))
    out = {"run": rec["run"], "i": rec["i"], "arm": rec["arm"], "role": rec["role"], "block": rec["block"], "ran": rec.get("ran"),
           "form": rec.get("form", "burst"), "flags": rec.get("flags", [])}
    K = C.CARDS[card]
    governed = K["governed"]
    s = rec.get("sched") or {}
    tail = rec.get("tail") or {}
    if not rec.get("ran"):
        out["why"] = rec.get("why")
        return out
    rest0 = rec["rest"]["t0_ms"] / 1000.0
    if out["form"] == "null":
        w0, w1 = rec["null"]["t0_ms"] / 1000.0, rec["null"]["t1_ms"] / 1000.0
        launches, t = [], w0 + 0.6 * sc
        n = 0
        while t + 0.5 * sc <= w1:      # pretend launches: what the views read in the same windows with no process
            launches.append({"test": "fma", "launch": n, "ok": True, "wall_s": 0.5, "passes": 1, "iters": 1, "cycles_max":
                             (800e6 if governed else 600e6) * 0.5, "t_start_ms": t * 1000, "t_end_ms": (t + 0.5 * sc) * 1000,
                             "proc": 0})
            t += 0.5 * sc
            n += 1
        procs_t = [(w0, w1)]
        minions, macs, t_type = 1024, 4096, None
    else:
        launches = []
        procs_t = []
        for k, p in enumerate(rec.get("procs") or []):
            path = os.path.join(rdir, p.get("name", "proc") + ".out")
            if not os.path.exists(path):
                path = os.path.join(rdir, "proc.out")
            sp = C.parse_sparsity(open(path).read()) if os.path.exists(path) else []
            for L in sp:
                if C.ok_launch(L):
                    launches.append(dict(L, proc=k))
            procs_t.append((p["t0_ms"] / 1000.0, p["t1_ms"] / 1000.0))
            chk = [x for x in sp if x.get("test") == "check"]
            out.setdefault("checks", []).append(chk[-1].get("result") if chk else None)
            out.setdefault("rcs", []).append(p.get("rc"))
        minions = 32 * bin(int(s["shires"], 16)).count("1")
        t_type = s["type"]
        macs = {"fp32": 4096, "fp16": 8192, "int8": 16384}[t_type]
        out.update(type=t_type, values=s.get("values"), shires=s.get("shires"), minions=minions)
        g = C.arm_of(s.get("values"))
        if g and g["family"] != "gemmL":
            # a block, stream or TenB arm (this sweep): its ops a minion a pass by the host's grammar, the multiply-adds a minion
            # a pass, and whether every counted launch's ops (the record's iters) are its passes x that; cycles an op, T an op and
            # J an op are read from the records' iters exactly as for a gemmL arm (a gemmL run's keys are unchanged)
            out.update(arm_token=g["token"], arm_family=g["family"], ops_pass=g["ops_pass"], macs_minion_pass=g["ops_pass"] * macs,
                       ops_pass_ok=bool(launches) and all(L["iters"] == L["passes"] * g["ops_pass"] for L in launches))
    if not procs_t:
        out["why"] = "no process record"
        return out
    t_first, t_last = procs_t[0][0], procs_t[-1][1]
    tail0 = t_last + 3.0 * sc if out["form"] in ("sus3", "null") else t_last + 2.0 * sc
    tail1 = tail.get("t1_ms", 0) / 1000.0 if tail else t_last + 5.0 * sc
    ctx = {"sc": sc, "t_first": t_first, "rest0": rest0, "tail0": tail0, "tail1": tail1, "minions": minions, "macs_op": macs}
    rule = "bracket" if out["form"] in ("sus3",) else "line"
    energy_ok = out["role"] != "time"
    last5 = tel.between(t_first - 5.0 * sc, t_first - 0.001 * sc)
    out.update(n_launch=len(launches), die_start_c=mean([x["die"] for x in last5]),
               die_tail_c=mean([x["die"] for x in tel.between(tail0, tail1)]), p_rest_plain_w=med([x["bw"] for x in last5]),
               gate=rec.get("gate"), views={}, baseline_rule=rule)
    # the clock bands: time only on the governed cards
    for band in K["bands"]:
        Ls = [L for L in launches if C.band_of(card, L) == band]
        v = view(card, Ls, tel, ctx, energy=(not governed and energy_ok), rule=rule, thin_at=(C.MIN_LAUNCH, C.MIN_SAMPLES))
        if v:
            out["views"][f"band{band}"] = v
    # the whole burst at the governor's own clock mix
    vb = view(card, launches, tel, ctx, energy=energy_ok, rule=rule, thin_at=(C.MIN_LAUNCH, C.MIN_SAMPLES))
    if vb:
        vb["clock_hist_10mhz"] = clock_hist(launches)
        vb["launches"] = [{"proc": L.get("proc"), "launch": L["launch"], "t_start_ms": L["t_start_ms"], "t_end_ms": L["t_end_ms"],
                           "wall_s": L["wall_s"], "ops": L["iters"], "kclock_mhz": C.kclock(L),
                           "board_w": mean([x["bw"] for x in tel.between(L["t_start_ms"] / 1000.0, L["t_end_ms"] / 1000.0)])}
                          for L in launches]
        out["views"]["burst"] = vb
    if governed:
        win, after = [], []
        for k in sorted({L["proc"] for L in launches}):
            Lk = [L for L in launches if L["proc"] == k]
            l0 = min((L for L in Lk), key=lambda L: L["launch"])
            t0k = l0["t_start_ms"] / 1000.0
            inw = [L for L in Lk if C.WIN_LO_S * sc <= L["t_start_ms"] / 1000.0 - t0k <= C.WIN_HI_S * sc]
            after += [L for L in Lk if L["t_start_ms"] / 1000.0 - t0k >= C.WIN_LO_S * sc]
            out.setdefault("win_counts", []).append({"proc": k, "in_window": len(inw),
                                                     "in_band": sum(1 for L in inw if C.band_of(card, L) == "800")})
            win += [L for L in inw if C.band_of(card, L) == "800"]
        vw = view(card, win, tel, ctx, energy=energy_ok, rule=rule, thin_at=(C.MIN_LAUNCH_WIN, C.MIN_SAMPLES_WIN))
        if vw:
            out["views"]["win"] = vw
        n800 = sum(1 for L in launches if C.band_of(card, L) == "800")
        out["frac_800"] = n800 / len(launches) if launches else None
        # CAPPED: of the launches starting WIN_LO_S or more after their process's launch 0 (past the governor's step from its 600
        # MHz start), fewer than CAPPED_FRAC in the 800 MHz band (E146: its L2, L4 and L8 random fp32 runs; none of its D-shapes,
        # zeros or int8; E190's bursts: none)
        out["frac_800_after_step"] = sum(1 for L in after if C.band_of(card, L) == "800") / len(after) if after else None
        out["capped"] = bool(after) and out["frac_800_after_step"] < C.CAPPED_FRAC and out["form"] != "null"
        out["primary_view"] = "win"
        # NO STEP: a governed card whose governor never left 600 MHz in the run (every launch in the 600 band: a light arm on a
        # few shires may not lift it) is read for energy over its whole burst in the 600 band, flagged no_step, never capped
        if launches and n800 == 0 and all(C.band_of(card, L) == "600" for L in launches):
            v6 = view(card, launches, tel, ctx, energy=energy_ok, rule=rule, thin_at=(C.MIN_LAUNCH, C.MIN_SAMPLES))
            if v6:
                out["views"]["band600"] = v6
            out.update(primary_view="band600", capped=False, no_step=True)
    else:
        out["capped"] = False
        out["primary_view"] = "band600"
    # rails_late: the raw reading over the last 1.5 s of the last process's launches, over the raw rest median (no 0.94)
    lastp = [L for L in launches if L.get("proc") == max((x.get("proc", 0) for x in launches), default=0)]
    if lastp and energy_ok:
        end = max(L["t_end_ms"] for L in lastp) / 1000.0
        late = tel.between(end - 1.5 * sc, end)
        rest3 = tel.between(t_first - 3.0 * sc, t_first - 0.001 * sc)
        out["rails_late"] = {r: (mean([x[r] for x in late]) - med([x[r] for x in rest3]))
                             if mean([x[r] for x in late]) is not None and med([x[r] for x in rest3]) is not None else None
                             for r in RAILS}
    chl = []
    for k, p in enumerate(rec.get("procs") or []):
        path = os.path.join(rdir, p.get("name", "proc") + ".out")
        if os.path.exists(path):
            chl += [x for x in C.parse_sparsity(open(path).read()) if x.get("test") == "fma" and x.get("launch") == -3]
    if chl:
        L = chl[-1]
        out["check_launch"] = {"wall_ms": L.get("wall_s", 0) * 1000, "cycles_max": L.get("cycles_max"),
                               "kernel_ms_at_600": (L.get("cycles_max") or 0) / 600e6 * 1000}
    return out


def primary(r):
    v = (r.get("views") or {}).get(r.get("primary_view") or "")
    return v or {}


def energy_read(r):
    """a run whose energy is read: ran, an fma run of role arm or anchor, not capped, its primary view not thin"""
    p = primary(r)
    return r.get("ran") and r.get("form") != "null" and r.get("role") in ("arm", "anchor") and not r.get("capped") \
        and not p.get("thin") and p.get("dP_w") is not None


# ---------------------------------------------------------------------------------------------------- one session
def die_slope(runs):
    """the registered die-start slope: the session's anchors' fit when their starts span 3 C or more and its standard error is
    under 0.0015 a degree, else DIE_SLOPE"""
    pts = [(r["die_start_c"], primary(r)["dP_w"]) for r in runs if r["role"] == "anchor" and energy_read(r) and r.get("die_start_c") is not None]
    info = {"n_anchors": len(pts), "rule": "default", "slope": C.DIE_SLOPE}
    if len(pts) >= 4:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        f = linfit(xs, ys)
        span = max(xs) - min(xs)
        info["span_c"] = span
        if f:
            my = sum(ys) / len(ys)
            res = [y - (f[0] + f[1] * x) for x, y in pts]
            sxx = sum((x - sum(xs) / len(xs)) ** 2 for x in xs)
            se = math.sqrt(sum(e * e for e in res) / (len(pts) - 2) / sxx) if sxx > 0 and len(pts) > 2 else None
            info.update(fit_slope=f[1] / my, fit_se=(se / my) if se is not None else None)
            if span >= 3.0 and se is not None and se / my < 0.0015:
                info.update(rule="anchors", slope=f[1] / my)
    return info


def reduce_session(sd_):
    q = C.load(os.path.join(sd_, "queue.json")) if os.path.exists(os.path.join(sd_, "queue.json")) else {}
    card = q.get("card")
    if card not in C.CARDS:
        raise SystemExit(f"refused: {sd_} has no queue.json naming a card")
    sc = float(q.get("scale") or 1.0)       # a dry session's time scale: its windows are that much shorter
    tel = load_tel(sd_, card, sc)
    runs = []
    rd = os.path.join(sd_, "runs")
    for key in sorted(os.listdir(rd)) if os.path.isdir(rd) else []:
        if os.path.exists(os.path.join(rd, key, "run.json")):
            runs.append(reduce_run(sd_, os.path.join(rd, key), card, tel, sc))
    ds = die_slope(runs)
    starts = [r["die_start_c"] for r in runs if energy_read(r) and r.get("die_start_c") is not None]
    die_ref = med(starts)
    for r in runs:
        p = primary(r)
        if energy_read(r) and die_ref is not None and r.get("die_start_c") is not None:
            f = 1.0 + ds["slope"] * (r["die_start_c"] - die_ref)
            p["dP_corr_w"] = p["dP_w"] / f
            p["J_op_corr"] = p["J_op"] / f
    cells = {}
    for r in runs:
        if r.get("ran") and r.get("form") != "null" and r.get("views"):
            cells.setdefault(r["arm"], []).append(r)
    agg = {}
    keys_t = ("T_op_us", "cyc_op_max", "cyc_op_mean", "kclock_mhz", "t_pass_s")
    keys_e = ("p_mean_w", "p_med_w", "dP_w", "dP_corr_w", "dP_med_w", "dP_plain", "dP_line", "dP_bracket", "J_op", "J_op_corr",
              "pJ_mac", "J_pass_over", "J_pass_with", "droop_ddr_mv", "droop_minion_mv")
    for arm, rs in sorted(cells.items()):
        a = {"n_runs": len(rs), "role": rs[0]["role"], "form": rs[0]["form"], "checks": sorted({str(c) for r in rs for c in r.get("checks", [])}),
             "die_start_c": mean([r.get("die_start_c") for r in rs]), "capped_runs": sum(1 for r in rs if r.get("capped")),
             "views": {}}
        for vn in sorted({v for r in rs for v in r["views"]}):
            fs = [r["views"][vn] for r in rs if vn in r["views"]]
            b = {k: mean([f.get(k) for f in fs]) for k in keys_t}
            b["n_runs"] = len(fs)
            ee = [f for r, f in zip([r for r in rs if vn in r["views"]], fs) if energy_read(r) and f.get("dP_w") is not None and not f.get("thin")]
            if ee:
                b.update({k: mean([f.get(k) for f in ee]) for k in keys_e})
                b["n_energy_runs"] = len(ee)
                if len(ee) > 1:
                    b["J_op_sd"] = sd([f["J_op"] for f in ee])
                b["rails"] = {r_: {"dW": mean([f.get("rails", {}).get(r_, {}).get("dW") for f in ee]),
                                   "electrons_op": mean([f.get("rails", {}).get(r_, {}).get("electrons_op") for f in ee])} for r_ in RAILS}
            a["views"][vn] = b
        agg[arm] = a
    anchors = [{"i": r["i"], "J_op": primary(r).get("J_op"), "dP_w": primary(r).get("dP_w"), "T_op_us": primary(r).get("T_op_us"),
                "die_start_c": r.get("die_start_c")} for r in runs if r["role"] == "anchor" and r.get("ran")]
    nulls = [r for r in runs if r.get("form") == "null" and r.get("ran")]
    null_sum = {}
    for vn in ("win", "band600", "burst"):
        for k in ("dP_line", "dP_plain", "dP_bracket"):
            v = [(r["views"].get(vn) or {}).get(k) for r in nulls]
            v = [x for x in v if x is not None]
            if v:
                null_sum[f"{vn}.{k}"] = {"n": len(v), "mean": sum(v) / len(v), "sd": sd(v)}
    smoke = []
    sm = os.path.join(sd_, "smoke")
    for arm in sorted(os.listdir(sm)) if os.path.isdir(sm) else []:
        p = os.path.join(sm, arm, "smoke.json")
        if os.path.exists(p):
            j = C.load(p)
            smoke.append({"arm": arm, "rc": j.get("rc"), "check": j.get("check"), "good": j.get("good"),
                          "rise_w": (j.get("board_rise") or {}).get("rise_w")})
    return {"kit": C.KIT, "reducer": "src/reduce_mms.py", "session": os.path.basename(os.path.normpath(sd_)), "card": card,
            "dry": bool(q.get("dry")), "scale": sc, "primary_view": "win" if C.CARDS[card]["governed"] else "band600",
            "n_samples": len(tel.rows), "rail_spikes": tel.spikes, "queue": {k: q.get(k) for k in ("stop", "card_min", "rest_die_c", "rest_board_w", "n_ran",
                                                                          "sched", "sched_sha256", "leftover")},
            "die_slope": ds, "die_ref_c": die_ref, "smoke": smoke, "runs": runs, "arms": agg, "anchors": anchors, "nulls": null_sum}


# ---------------------------------------------------------------------------------------------------- combining sessions
def combine(datas):
    out = {"kit": C.KIT, "reducer": "src/reduce_mms.py --combine", "sessions": [d["session"] for d in datas], "cards": {}}
    for d in datas:
        card = d["card"]
        c = out["cards"].setdefault(card, {"sessions": [], "arms": {}, "nulls": {}, "anchor_rel_sd": []})
        c["sessions"].append(d["session"])
        a_j = [x["J_op"] for x in d["anchors"] if x.get("J_op")]
        if len(a_j) > 1:
            c["anchor_rel_sd"].append(sd(a_j) / mean(a_j))
        for k, v in d["nulls"].items():
            c["nulls"].setdefault(k, []).append(v)
        for r in d["runs"]:
            if not r.get("ran") or r.get("form") == "null" or not r.get("views"):
                continue
            p = primary(r)
            e = c["arms"].setdefault(r["arm"], {"role": r["role"], "form": r["form"], "runs": []})
            e["runs"].append({"session": d["session"], "i": r["i"], "capped": r.get("capped"), "energy": bool(energy_read(r)),
                              "T_op_us": p.get("T_op_us"), "kclock_mhz": p.get("kclock_mhz"), "dP_corr_w": p.get("dP_corr_w"),
                              "J_op_corr": p.get("J_op_corr"), "dP_w": p.get("dP_w"), "J_op": p.get("J_op"),
                              "die_start_c": r.get("die_start_c"),
                              "rails_dW": {k: v.get("dW") for k, v in (p.get("rails") or {}).items()}})
    for card, c in out["cards"].items():
        rel = mean(c["anchor_rel_sd"])
        c["anchor_rel_sd_mean"] = rel
        for k, vs in list(c["nulls"].items()):
            n = sum(v["n"] for v in vs)
            c["nulls"][k] = {"n": n, "mean": sum(v["mean"] * v["n"] for v in vs) / n}
        for arm, e in c["arms"].items():
            rs = e["runs"]
            e["n_runs"] = len(rs)
            e["T_op_us"] = mean([x["T_op_us"] for x in rs])
            e["T_op_sd"] = sd([x["T_op_us"] for x in rs])
            er = [x for x in rs if x["energy"] and x.get("J_op_corr") is not None]
            e["n_energy_runs"] = len(er)
            if er:
                for k in ("dP_corr_w", "J_op_corr", "dP_w", "J_op"):
                    e[k] = mean([x[k] for x in er])
                s_ = sd([x["J_op_corr"] for x in er])
                e["J_op_corr_sd"] = s_
                e["J_op_corr_err"] = s_ / math.sqrt(len(er)) if s_ is not None else (rel * abs(e["J_op_corr"]) if rel else None)
                e["rails_dW"] = {r_: mean([x["rails_dW"].get(r_) for x in er]) for r_ in RAILS}
    return out


# ---------------------------------------------------------------------------------------------------- tables
def f_(x, w, p):
    return f"{x:{w}.{p}f}" if isinstance(x, (int, float)) and not isinstance(x, bool) else f"{'-':>{w}s}"


def table(d):
    pv = d["primary_view"]
    L = [f"1119-mmsweep5 reduced: session {d['session']}, card {d['card']}, {d['n_samples']} samples; card-minutes "
         f"{d['queue'].get('card_min')}; stop {d['queue'].get('stop')}; primary view {pv}; die slope {d['die_slope'].get('slope'):.4f}/C "
         f"({d['die_slope'].get('rule')}), die ref {f_(d.get('die_ref_c'), 4, 1)} C",
         f"{'arm':26s} {'role':6s} {'n':>2s} {'T_op us':>8s} {'cyc max':>8s} {'MHz':>5s} {'P W':>6s} {'dP W':>6s} {'dPcorr':>6s} "
         f"{'nJ/op':>7s} {'pJ/MAC':>7s} {'core dW':>7s} {'ddr mV':>6s} capped checks"]
    for arm, a in sorted(d["arms"].items()):
        b = a["views"].get(pv)
        if not b:
            L.append(f"{arm:26s} {a['role']:6s} no launch in the primary view")
            continue
        L.append(f"{arm:26s} {a['role']:6s} {b['n_runs']:2d} {f_(b.get('T_op_us'), 8, 3)} {f_(b.get('cyc_op_max'), 8, 1)} "
                 f"{f_(b.get('kclock_mhz'), 5, 0)} {f_(b.get('p_mean_w'), 6, 2)} {f_(b.get('dP_w'), 6, 2)} {f_(b.get('dP_corr_w'), 6, 2)} "
                 f"{f_((b.get('J_op') or 0) * 1e9 if b.get('J_op') is not None else None, 7, 2)} {f_(b.get('pJ_mac'), 7, 3)} "
                 f"{f_(((b.get('rails') or {}).get('minion') or {}).get('dW'), 7, 2)} {f_(b.get('droop_ddr_mv'), 6, 2)} "
                 f"{a['capped_runs']} {','.join(a['checks'])}")
    L.append("anchors (i, nJ/op, dP W, T_op us, die C): " + "; ".join(
        f"{x['i']} {f_((x['J_op'] or 0) * 1e9 if x.get('J_op') else None, 0, 2)} {f_(x.get('dP_w'), 0, 2)} {f_(x.get('T_op_us'), 0, 3)} "
        f"{f_(x.get('die_start_c'), 0, 1)}" for x in d["anchors"]))
    L.append("nulls (the baseline rules at zero signal, W): " + "; ".join(f"{k} {v['mean']:+.3f} (sd {f_(v['sd'], 0, 3)}, n {v['n']})"
                                                                            for k, v in sorted(d["nulls"].items())))
    return "\n".join(L) + "\n"


def table_combined(c):
    L = [f"1119-mmsweep5 combined: sessions {', '.join(c['sessions'])}"]
    for card, x in sorted(c["cards"].items()):
        L.append(f"card {card}: sessions {', '.join(x['sessions'])}; anchors' relative sd {f_(x['anchor_rel_sd_mean'], 0, 4)}; nulls " +
                 "; ".join(f"{k} {v['mean']:+.3f} W (n {v['n']})" for k, v in sorted(x["nulls"].items())))
        for arm, e in sorted(x["arms"].items()):
            L.append(f"  {arm:26s} {e['role']:6s} n {e['n_runs']:2d} (energy {e['n_energy_runs']:2d}) T {f_(e.get('T_op_us'), 8, 4)} us "
                     f"dPcorr {f_(e.get('dP_corr_w'), 6, 2)} W J {f_((e.get('J_op_corr') or 0) * 1e9 if e.get('J_op_corr') is not None else None, 7, 2)} "
                     f"+- {f_((e.get('J_op_corr_err') or 0) * 1e9 if e.get('J_op_corr_err') is not None else None, 5, 2)} nJ/op")
    return "\n".join(L) + "\n"


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("session", nargs="?")
    parser.add_argument("--combine", nargs="+")
    parser.add_argument("--out", required=True)
    parser.add_argument("--txt")
    a = parser.parse_args(argv)
    if a.combine:
        d = combine([C.load(p) for p in a.combine])
        t = table_combined(d)
    elif a.session:
        d = reduce_session(a.session)
        t = table(d)
    else:
        parser.error("a session dir, or --combine with reduced files")
    with open(a.out, "w") as f:
        json.dump(d, f, indent=1, sort_keys=True)
    if a.txt:
        with open(a.txt, "w") as f:
            f.write(t)
    sys.stdout.write(t)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
