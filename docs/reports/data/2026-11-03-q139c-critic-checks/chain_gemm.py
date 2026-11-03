#!/usr/bin/env python3
"""Q139(c) check (a), POST HOC (desk only, Tue 3 Nov 2026): Q138(t)'s frozen aifoundry2 heat chain run open loop on the four
large-GEMM sessions (E119, E126, E136, E146), scored on each sustained run's window die, beside E136's frozen sustained law on
the same measured watts; and, for E146's never-run shape F6, the chain fed G2's (and P0's) frozen sustained power instead of the
measured trace.

Written independently of Q138's final critic's scripts (its work/ folder was read only to compare at the end). Nothing here is
registered: the chain (model-q138t.json, a2, frozen at f5473428 and amended at c2f9920d with no number changed) was fitted on
E111 + E133 (the kinds loop) and frozen before E146 was registered, but this scoring was designed after every number it reads.

What is read (all committed):
  docs/reports/data/2026-11-02-q138t-heat-model/model-q138t.json   a2: tau_s, R_C_per_W (the frozen chain)
  docs/reports/data/<session>/aifoundry2/history-before.jsonl       the 5 s host log of the card before the session (die, W)
  docs/reports/data/<session>/aifoundry2/{smoke,s1}/runs.jsonl      runs, gate readings, telemetry file names
  docs/reports/data/<session>/aifoundry2/{smoke,s1}/tel/*.jsonl.gz  10 Hz telemetry: t_ms, board_w, temp_c.minshire[0]
  docs/reports/data/<session>/aifoundry2/s1/launches.jsonl(.gz)     work processes and their dispatch windows
  docs/reports/data/<session>/results.json                          cells' sus_die / sus_w / sus_die_start (to check this reader)
  tools/claims-v3/e136/predictions-e136.json                        heat: E136's frozen burst and sustained laws
  tools/claims-v3/e146/predictions-e146.json                        cells F6-*: G2's and P0's frozen sustained / 800 MHz power

The chain (model-q138t.json's own form): T(t) = T_anchor + sum_i R_i x_i(t), dx_i/dt = (P(t) - P_ref - x_i) / tau_i, open loop on
the measured board watts (which carry the leakage). Integrated here on the telemetry's own sample times with the exact update for
an input held piecewise constant at the mean of each interval's two end samples (gaps longer than 0.4 s, between the history,
the smoke and s1, are filled at 0.2 s by linear interpolation, as the frozen code's grid() does everywhere).

The sustained window is the registered reducers' (reduce_hpl.run_metrics, SUS_LAST_S = 40): samples inside any dispatch window
of the run's work processes and at or after (last work end - 40 s); the window die is the mean of minshire[0] there, the window
board W the mean of board_w, die_start the first in-work die sample.

Anchors (three arms; the chain itself is identical in all three):
  rest   Q138(t)'s A1.3 definition carried over: the chain starts from rest at the start of the 120 s of rest before the
         session's first launch (the host history, then the smoke's 31 s SMOKE-00-rest run on the same sampler), P_ref the
         time-weighted mean board W over that window, T_anchor the time-weighted mean of mean(measured - chain) over it; the
         chain then runs through the smoke and s1. This is the protocol's own anchor.
  gate   the session's first s1 gate reading (die, board W), the chain from rest at s1's first sample (it ignores the smoke's
         heat): the arm Q138's critic called "first gate".
  start  like for like with E136's law, which takes the run's die_start: the rest arm's chain states, re-anchored per run so
         that the chain equals die_start at the run's first in-work sample (the chain predicts the rise from the start only).
Usage: python3 chain_gemm.py [--json out.json] [--txt out.txt] [--frozen-check]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(ROOT, "docs", "reports", "data")
MODEL = os.path.join(DATA, "2026-11-02-q138t-heat-model", "model-q138t.json")
E136P = os.path.join(ROOT, "tools", "claims-v3", "e136", "predictions-e136.json")
E146P = os.path.join(ROOT, "tools", "claims-v3", "e146", "predictions-e146.json")
SESSIONS = [("E119", "2026-11-01-e119-gemm-speed"), ("E126", "2026-11-02-e126-gemm-arms"),
            ("E136", "2026-11-02-e136-large-gemm"), ("E146", "2026-11-02-e146-gemm-stores")]
SUS_LAST_S = 40.0      # reduce_hpl.SUS_LAST_S
REST_S = 120.0         # Q138(t) A1.3: the rest die over the last 120 s of rest
FILL_S = 0.2           # gap fill step and grid step (the frozen code's grid)
MODE = "grid"         # the chain's numerics (see chain())


def jl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path = path + ".gz"
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt") as f:
        for ln in f:
            if ln.startswith("{"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def tel_rows(path):
    """(t_s, board_w, die_fw) for every telemetry row that has both"""
    out = []
    for r in jl(path):
        try:
            out.append((r["t_ms"] / 1000.0, float(r["board_w"]), float(r["temp_c"]["minshire"][0])))
        except (KeyError, TypeError, ValueError, IndexError):
            pass
    return out


def session_samples(base, sub):
    rows = []
    for r in jl(os.path.join(base, sub, "runs.jsonl")):
        rows += tel_rows(os.path.join(base, sub, r["tel"]))
    return rows


def fill(series):
    """sort by time, drop duplicate times, and fill gaps longer than 2*FILL_S by linear interpolation at FILL_S"""
    series = sorted(series)
    out = []
    for s in series:
        if out and s[0] <= out[-1][0]:
            continue
        if out and s[0] - out[-1][0] > 2 * FILL_S:
            t0, p0, d0 = out[-1]
            n = int((s[0] - t0) / FILL_S)
            for k in range(1, n):
                f = k * FILL_S / (s[0] - t0)
                out.append((t0 + k * FILL_S, p0 + f * (s[1] - p0), None))  # filled points carry no die reading
        out.append(s)
    return out


def chain(series, tau, R, p_ref, t_from, mode="grid"):
    """open-loop chain from rest at t_from. Returns a function t -> chain rise (C) for t >= t_from.
    mode "grid" (primary): the frozen code's numerics (heat_q138t.grid + states): the board W linearly interpolated onto a
    uniform 0.2 s grid from t_from, x_k = a x_(k-1) + (1 - a) (P_k - P_ref), a = exp(-0.2 / tau); read back by linear
    interpolation. mode "trap" (sensitivity): the telemetry's own sample times, each interval held at the mean of its two ends."""
    pts = [(t, P) for t, P, _ in series if t >= t_from]
    if mode == "grid":
        ts, ps = [], []
        j = 0
        t = pts[0][0]
        a = [math.exp(-FILL_S / tk) for tk in tau]
        x = [0.0] * len(tau)
        while t <= pts[-1][0]:
            while j + 1 < len(pts) and pts[j + 1][0] < t:
                j += 1
            if j + 1 < len(pts):
                (t0, p0), (t1, p1) = pts[j], pts[j + 1]
                P = p0 + (p1 - p0) * ((t - t0) / (t1 - t0) if t1 > t0 else 0.0)
            else:
                P = pts[j][1]
            u = P - p_ref
            for i in range(len(tau)):
                x[i] = a[i] * x[i] + (1.0 - a[i]) * u
            ts.append(t)
            ps.append(sum(R[i] * x[i] for i in range(len(tau))))
            t += FILL_S
    else:
        ts, ps = [], []
        x = [0.0] * len(tau)
        prev = None
        for t, P in pts:
            if prev is not None:
                dt = t - prev[0]
                u = 0.5 * (P + prev[1]) - p_ref
                for i in range(len(tau)):
                    aa = math.exp(-dt / tau[i])
                    x[i] = aa * x[i] + (1.0 - aa) * u
            ts.append(t)
            ps.append(sum(R[i] * x[i] for i in range(len(tau))))
            prev = (t, P)

    def at(tq):
        lo, hi = 0, len(ts) - 1
        if tq <= ts[0]:
            return ps[0]
        if tq >= ts[-1]:
            return ps[-1]
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if ts[mid] <= tq:
                lo = mid
            else:
                hi = mid
        f = (tq - ts[lo]) / (ts[hi] - ts[lo])
        return ps[lo] + f * (ps[hi] - ps[lo])
    return at


def tw_mean(pts, t0, t1):
    """time-weighted mean of a step-held series of (t, v) over [t0, t1] (each value held until the next point)"""
    pts = sorted(p for p in pts if p[1] is not None)
    acc = w = 0.0
    for k, (t, v) in enumerate(pts):
        a = max(t, t0)
        b = min(pts[k + 1][0] if k + 1 < len(pts) else t1, t1)
        if b > a:
            acc += v * (b - a)
            w += b - a
    return acc / w if w else None


def launches_by_run(base):
    out = {}
    for L in jl(os.path.join(base, "s1", "launches.jsonl")):
        if L.get("role") == "work":
            out.setdefault(L["run"], []).append(L)
    return out


def run_window(procs):
    """dispatch windows of the work processes, and the last work end (reduce_hpl.run_metrics)"""
    wins = [(p["t_start_ms"] / 1000.0, p["t_end_ms"] / 1000.0) for p in procs]
    kw = [(k["t_start_ms"] / 1000.0, k["t_end_ms"] / 1000.0) for p in procs for k in p.get("sparsity", [])
          if k.get("t_start_ms") and k.get("t_end_ms")]
    return (kw or wins), min(a for a, _ in wins), max(b for _, b in wins)


def inside(t, kw):
    return any(a <= t <= b for a, b in kw)


def rms(v):
    return math.sqrt(sum(e * e for e in v) / len(v)) if v else None


def mean(v):
    return sum(v) / len(v) if v else None


def law_sus(H, die_start, p_sus):
    w = H["w_sus"]
    return min(H["trip_c"], (1 - w) * die_start + w * (H["die_idle_c"] + H["c_steady_c_per_w"] * (p_sus - H["P_idle_w"])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--txt")
    ap.add_argument("--frozen-check", action="store_true", help="also run Q138(t)'s own heat_q138t.states on a 0.2 s grid")
    ap.add_argument("--mode", choices=("grid", "trap"), default="grid", help="the chain's numerics (see chain())")
    a = ap.parse_args()
    global MODE
    MODE = a.mode
    M = json.load(open(MODEL))["a2"]
    tau, R = [float(x) for x in M["tau_s"]], [float(x) for x in M["R_C_per_W"]]
    H136 = json.load(open(E136P))["heat"]
    C146 = json.load(open(E146P))["cells"]
    lines = []
    pr = lines.append
    pr("Q139(c) check (a), post hoc: Q138(t)'s frozen aifoundry2 chain (model-q138t.json a2: tau %s s, R %s C/W, sum %.4f) "
       "on the large-GEMM sessions' sustained runs" % (tau, R, sum(R)))
    pr("error = measured window die - predicted (C); the window is the last %.0f s of work inside dispatch windows; "
       "numerics: %s" % (SUS_LAST_S, MODE))
    out = {"what": "Q139(c) check (a), post hoc", "numerics": MODE, "model": {"tau_s": tau, "R_C_per_W": R, "R_total": sum(R)},
           "e136_heat": H136, "sessions": {}}
    for tag, sd in SESSIONS:
        base = os.path.join(DATA, sd, "aifoundry2")
        res = json.load(open(os.path.join(DATA, sd, "results.json")))
        hist = jl(os.path.join(base, "history-before.jsonl"))
        smoke = jl(os.path.join(base, "smoke", "runs.jsonl"))
        s1 = jl(os.path.join(base, "s1", "runs.jsonl"))
        rest_run = next(r for r in smoke if r["block"] == "SMOKE" and "rest" in r["label"])
        rest_tel = tel_rows(os.path.join(base, "smoke", rest_run["tel"]))
        first_launch = min(L["t_start_ms"] / 1000.0 for r in smoke for L in r.get("launches", []))
        rest_end = min(first_launch, max(t for t, _, _ in rest_tel))
        rest_from = rest_end - REST_S
        hist_pts = [(h["t"] / 1000.0, float(h["cards"][0]["w"]), float(h["cards"][0]["die"])) for h in hist
                    if h.get("cards") and h["cards"][0].get("ok") and not h["cards"][0].get("held")]
        hist_pts = [p for p in hist_pts if p[0] < min(t for t, _, _ in rest_tel)]
        rest_pts = [p for p in hist_pts if p[0] >= rest_from - 5.0] + rest_tel
        p_ref = tw_mean([(t, P) for t, P, _ in rest_pts], rest_from, rest_end)
        die_rest = tw_mean([(t, d) for t, _, d in rest_pts], rest_from, rest_end)
        series = fill([p for p in hist_pts if p[0] >= rest_from - 600.0] + session_samples(base, "smoke") +
                      session_samples(base, "s1"))
        ch_rest = chain(series, tau, R, p_ref, series[0][0], MODE)
        anc_pts = [(t, d - ch_rest(t)) for t, P, d in series if d is not None and rest_from <= t <= rest_end]
        T_rest = tw_mean(anc_pts, rest_from, rest_end)
        g0 = s1[0]["gate"]["reading"]
        s1_first = min(t for t, _, _ in session_samples(base, "s1"))
        ch_gate = chain(series, tau, R, float(g0[2]), s1_first, MODE)
        lb = launches_by_run(base)
        cells = res["cells"]
        rows = []
        for r in s1:
            if r.get("processes", 1) < 2:
                continue
            procs = lb.get(r["run"], [])
            kw, t0, t1 = run_window(procs)
            work = [(t, P, d) for t, P, d in series if d is not None and t0 <= t <= t1 and inside(t, kw)]
            win = [(t, P, d) for t, P, d in work if t >= t1 - SUS_LAST_S]
            meas = mean([d for _, _, d in win])
            p_sus = mean([P for _, P, _ in win])
            die_start = work[0][2]
            c_rest = mean([ch_rest(t) for t, _, _ in win])
            c_gate = mean([ch_gate(t) for t, _, _ in win])
            c_start0 = ch_rest(work[0][0])
            pred = {"rest": T_rest + c_rest, "gate": float(g0[0]) + c_gate, "start": die_start + (c_rest - c_start0),
                    "e136_law": law_sus(H136, die_start, p_sus)}
            cell = cells.get(r["label"]) or {}
            row = {"run": r["run"], "label": r["label"], "t_from_s1_s": round(t0 - s1_first, 1), "n_win": len(win),
                   "die_win": round(meas, 3), "w_win": round(p_sus, 3), "die_start": die_start,
                   "registered": {"sus_die": cell.get("sus_die"), "sus_w": cell.get("sus_w"),
                                  "sus_die_start": (cell.get("sus_die_start") or [None])[0]},
                   "pred": {k: round(v, 3) for k, v in pred.items()},
                   "err": {k: round(meas - v, 3) for k, v in pred.items()}}
            # F6: the chain fed G2's (and P0's) frozen power in place of the measured trace during the run
            fz = C146.get(r["label"]) if tag == "E146" else None
            if fz:
                row["fed"] = {}
                for nm, pw in (("G2", float(fz["sus_w_G2"])), ("P0_800", float(fz["P0_w"]["800"]))):
                    for how in ("in_dispatch", "whole_span"):
                        sub = [(t, (pw if (t0 <= t <= t1 and (how == "whole_span" or inside(t, kw))) else P), d)
                               for t, P, d in series]
                        cr = chain(sub, tau, R, p_ref, series[0][0], MODE)
                        cg = chain(sub, tau, R, float(g0[2]), s1_first, MODE)
                        wr = mean([cr(t) for t, _, _ in win])
                        wg = mean([cg(t) for t, _, _ in win])
                        s0 = cr(work[0][0])
                        pf = {"rest": T_rest + wr, "gate": float(g0[0]) + wg, "start": die_start + (wr - s0),
                              "e136_law": law_sus(H136, die_start, pw)}
                        row["fed"][f"{nm}_{how}"] = {"power_w": pw, "pred": {k: round(v, 3) for k, v in pf.items()},
                                                     "err": {k: round(meas - v, 3) for k, v in pf.items()}}
            rows.append(row)
        chk = [abs(x["die_win"] - x["registered"]["sus_die"]) for x in rows if x["registered"]["sus_die"] is not None]
        chkw = [abs(x["w_win"] - x["registered"]["sus_w"]) for x in rows if x["registered"]["sus_w"] is not None]
        chks = [x["die_start"] == x["registered"]["sus_die_start"] for x in rows if x["registered"]["sus_die_start"] is not None]
        summ = {}
        for arm in ("rest", "gate", "start", "e136_law"):
            e = [x["err"][arm] for x in rows]
            summ[arm] = {"n": len(e), "rms": round(rms(e), 3), "mean": round(mean(e), 3), "min": round(min(e), 3),
                         "max": round(max(e), 3)}
        out["sessions"][tag] = {"dir": sd, "rest_window_s": [round(rest_from, 1), round(rest_end, 1)],
                                "p_ref_rest_w": round(p_ref, 3), "die_rest_c": round(die_rest, 3),
                                "T_anchor_rest_c": round(T_rest, 3), "first_gate": g0,
                                "reader_check": {"max_abs_die_vs_registered": round(max(chk), 4) if chk else None,
                                                 "max_abs_w_vs_registered": round(max(chkw), 4) if chkw else None,
                                                 "die_start_equal": f"{sum(chks)}/{len(chks)}"},
                                "summary": summ, "runs": rows}
        pr("")
        pr(f"{tag} ({sd}): {len(rows)} sustained runs; rest window {REST_S:.0f} s before the first launch: board "
           f"{p_ref:.3f} W, die {die_rest:.3f} C (anchor {T_rest:.3f}); first gate {g0[:3]}")
        pr(f"  reader against results.json cells: window die max |diff| {max(chk) if chk else None}, window W max |diff| "
           f"{max(chkw) if chkw else None}, die_start equal {sum(chks)}/{len(chks)}")
        for arm in ("rest", "gate", "start", "e136_law"):
            s = summ[arm]
            pr(f"  {arm:9s} rms {s['rms']:.3f}  mean {s['mean']:+.3f}  range {s['min']:+.3f} .. {s['max']:+.3f}  (n {s['n']})")
        for x in rows:
            if "fed" in x or tag == "E146":
                pr(f"  {x['run']}: measured {x['die_win']:.2f} C at {x['w_win']:.2f} W, start {x['die_start']}; err rest "
                   f"{x['err']['rest']:+.2f} gate {x['err']['gate']:+.2f} start {x['err']['start']:+.2f} law {x['err']['e136_law']:+.2f}")
                for k, v in x.get("fed", {}).items():
                    pr(f"     fed {k:22s} {v['power_w']:6.2f} W: err rest {v['err']['rest']:+.2f} gate {v['err']['gate']:+.2f} "
                       f"start {v['err']['start']:+.2f} law {v['err']['e136_law']:+.2f}")
    allrows = [x for s in out["sessions"].values() for x in s["runs"]]
    pr("")
    pr(f"all four sessions, {len(allrows)} sustained runs:")
    out["pooled"] = {}
    for arm in ("rest", "gate", "start", "e136_law"):
        e = [x["err"][arm] for x in allrows]
        out["pooled"][arm] = {"n": len(e), "rms": round(rms(e), 3), "mean": round(mean(e), 3)}
        pr(f"  {arm:9s} rms {rms(e):.3f}  mean {mean(e):+.3f}")
    if a.frozen_check:
        sys.path.insert(0, os.path.join(DATA, "2026-11-02-q138t-heat-model"))
        import numpy as np
        import heat_q138t as HQ
        pr("")
        pr("frozen-code check (Q138(t)'s own load_tel/grid/states on s1's telemetry, first-gate anchor) against this script's gate arm:")
        for tag, sd in SESSIONS:
            base = os.path.join(DATA, sd, "aifoundry2")
            s1 = jl(os.path.join(base, "s1", "runs.jsonl"))
            paths = [os.path.join(base, "s1", r["tel"]) for r in s1]
            paths = [p if os.path.exists(p) else p + ".gz" for p in paths]
            T = HQ.load_tel(paths, sensor="fw")
            g, P, Tm = HQ.grid(T)
            g0 = s1[0]["gate"]["reading"]
            X = HQ.states(P - float(g0[2]), tau)
            pred = float(g0[0]) + X @ np.asarray(R)
            diffs = []
            lb = launches_by_run(base)
            s1s = fill(session_samples(base, "s1"))
            for x in out["sessions"][tag]["runs"]:
                kw, t0, t1 = run_window(lb[x["run"]])
                ts = [t for t, _, d in s1s if d is not None and t0 <= t <= t1 and inside(t, kw) and t >= t1 - SUS_LAST_S]
                fz = float(np.mean(np.interp(ts, g, pred)))
                diffs.append(x["pred"]["gate"] - fz)
            out["sessions"][tag]["frozen_code_gate_diff_max_abs"] = round(max(abs(d) for d in diffs), 4)
            pr(f"  {tag}: max |this - frozen code| over {len(diffs)} windows = {max(abs(d) for d in diffs):.4f} C")
    txt = "\n".join(lines) + "\n"
    if a.txt:
        open(a.txt, "w").write(txt)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
    sys.stdout.write(txt)


if __name__ == "__main__":
    main()
