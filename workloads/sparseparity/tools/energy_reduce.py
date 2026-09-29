#!/usr/bin/env python3
"""Board energy per solve from one energy.sh run (off the card: it reads files only).

    python3 workloads/sparseparity/tools/energy_reduce.py DIR [--json OUT] [--truth FILE]
        DIR is energy.sh's output: telemetry.jsonl[.gz] (ettelem sample, 10 Hz by default), host.json
        (sparseparity_host's JSON line), run.json (energy.sh's marks). Writes DIR/energy.json and prints a summary.
        --truth (energy.sh --dry) compares the result with the energies the test double injected and exits 1 if
        they disagree by more than the accuracy claimed below.
    python3 workloads/sparseparity/tools/energy_reduce.py combine DIR [DIR ...] [--label NAME] [--json OUT]
        the per-solve energies of the slices of ONE solve added up (the two halves of (256,5), f5h0 + f5h1). It
        refuses (exit 2) unless every part is the same instance (hash), variant and kernel, and the parts' slices are
        I/N for one N with every I in 0..N-1 exactly once (a rerun of a half is not a third part).

The burst is [lo, hi] = the host's launch_epoch_ms (the first launch's start, the last completed launch's end); a
host without it (built before 29 September's change) falls back to the board's own edges (below). Per solve means
over the host's reps_done launches: the launches, the host's ~4 ms per launch of record clearing and readback between
them, and nothing else.

THE HEADLINE, J per solve over idle: the SP's board average (sp.board_avg_w, the PMIC's own running average of its
input power, tau ~1 s; unit gain: 1.00-1.01 against first-order-filtered board_w on E58's aifoundry3 bursts, and the
firmware reads it from the PMIC's average, thermal_pwr_mgmt.c:811), integrated over the long window [lo - 1, hi + 6]
(5.7 tau past the end) above the before bracket's mean, less the leakage's rise: the catalogue's law (below) times
the measured die temperature over the before bracket's, sample by sample. A unit-gain filter moves energy in time
but keeps its total, so no filter correction is needed, and an average does not alias the gaps between launches.
Claimed accuracy +-3% (the die temperature reads in whole degrees, and the law is aifoundry2's: aifoundry3's own
idle curve is 0.26-0.30 W/C at 55-57 C against the law's 0.33); energy_stub.py's two cards, README "Energy per solve".
Beside it: the uncorrected value (flat at the before bracket: all of the leakage's rise), and the ramp baseline (no
temperature, no law: the before bracket's mean until lo, the late bracket's [hi + 6, hi + 8] from hi, a straight line
between), which misses the fast thermal stages (11-thermal-model.md: 1.5 s and 4 s, 0.16 C/W; they heat the die
within the burst and let it cool within seconds of its end) and so overstates: +4% on the alt test card.
The three rails (the PMIC's running averages of the minion, SRAM and NoC regulators' output power, tau ~1.05 s, E58)
are integrated over the long window above the ramp baseline (no law is known per rail), so each keeps part of its own
leakage's rise: upper bounds, -2% to +7% on the test cards. Unmetered = the headline minus the rails (a small
difference of larger numbers: +-15%). The board total per solve (idle included) = the before bracket's idle over the
burst + the leakage's rise within it (the law) + the headline: +-2%.

CROSS-CHECK, the energy catalogue's method (workloads/enercat/analyze_catalogue.py bursts_of, the same windows and
law), so that these numbers sit beside the catalogue's: busy = [lo + 0.5, hi]; idle = the mean of the brackets
[lo - 3.5, lo - 0.3] and [hi + 2.3, hi + 5.5] (before only if the after bracket has < 4 samples); over_raw =
mean(busy) - idle; over = over_raw - s(T_mid) (T_busy - T_idle), s(T) = 23.257/36 e^((T-80)/36) W/C (the idle law's
slope, aifoundry2's, used on every card as the catalogue does), T the minion shires' mean temperature
(temp_c.minshire[0], whole degrees); J per solve = over x (hi - lo) / reps. Its weakness in one run: board_w is a
point sample held for one SP pass (E58 on aifoundry3: 0.296 s under a 20 Hz sampler, 0.255 s at 10 Hz), and a pass
that falls in a gap between two launches reads idle for the whole pass (aifoundry3's 2026-09-22 Horace telemetry
shows such passes): unbiased over many runs (the expected number is the busy passes x the gaps' share of the burst),
but each such pass more or fewer than expected moves one run by 1/N of its step, N the busy passes (4-6% at 17-26
passes). The reducer counts them (busy_readings_at_idle, and the expected number from the host's clock). Claimed
accuracy: 3% (the whole-degree temperature in its leakage correction) plus one pass of the step per reading at idle
more or fewer than expected, and one more (the card's gaps are longer than the host's by its launch latency). Also, the integral of board_w over
[lo - 1, hi + 2.3] with the same law applied sample by sample (its edges good to one pass each).
Fallback edges: the first and last samples inside the host process's span above the midpoint of idle and busy.
Flags: minion clock off 600 MHz in a busy sample, the sampler's median request over 60 ms (a starved meter,
19-observability), few samples in a window, the telemetry ending before the long window does,
the host short of its reps or not PASS, a foreign device process during the run (run.json), a dry run, the catalogue
method off the headline by more than both their claims (3% + 3% and one SP pass per busy reading at idle, and one).

THE HOST'S SHARE. The card does not solve alone: the host process drives it (the runtime polls the device) and its
package idles meanwhile. Its package energy is not readable without root on aifoundry3 (below), so it is bounded:
package idle HOST_IDLE_W over the burst's wall time plus HOST_CORE_W per busy core-second, the busy core-seconds the
host's own CPU time over the burst (host_cpu_s.burst, getrusage over launch_epoch_ms; a host without it: energy.sh's
measured CPU time of the whole process, flagged as an upper bound).

CPU comparison: the host's package power is not readable without root on aifoundry3 (RAPL energy_uj 0400 root,
/dev/cpu/*/msr 0600 root, perf_event_paranoid 2, sudo only for et-holders; checked 29 September 2026, and energy.sh
records it again per run), so the CPU's energy per solve is its measured 6-thread time x an assumed 125-251 W (the
i7-11700K's PL1 and PL2, which its board lifts to 4,095 W, so they bound nothing: cpu/data/2026-09-29-aifoundry3-r),
idle included. The CPU's time is its fastest method that keeps the secret with P(loss) <= 1e-4 (the card's
one-stage scan loses nothing): each method is listed with its P(loss). Two ratios: CPU / the card's board alone (the
host not counted), and CPU / (the card's board + the host's package, bounds).
"""
import argparse
import gzip
import json
import math
import os
import sys

import numpy as np

A_LEAK_80, T_L = 23.257, 36.0          # analyze_catalogue.py: the idle law (aifoundry2's), used on every card
TAU_RAIL = 1.05                          # E58: the rails' running average, 1.01-1.10 s
BUSY_SKIP, BEFORE, AFTER = 0.5, (3.5, 0.3), (2.3, 5.5)   # bursts_of's windows
INT_PRE, INT_POST_BOARD, INT_POST_RAIL, RAIL_RESID = 1.0, 2.3, 6.0, 2.0
RAILS = ("minion_w", "sram_w", "noc_w")
CPU_W = (125.0, 251.0)
# The host's package while it drives the card (assumed: RAPL is root-only): idle, plus per busy core. The upper per-core
# figure is the CPU side's own assumption spread over its 6 busy cores, (251 - 20) / 6; the lower, a scalar poll loop.
HOST_IDLE_W = (10.0, 20.0)
HOST_CORE_W = (10.0, 38.5)
P_LOSS_MAX = 1e-4
# The CPU's methods per instance, 6 threads on aifoundry3's i7-11700K (cpu/data/2026-09-29-aifoundry3-r and
# data/2026-09-29-aifoundry3-sysemu-m5/cpu2s.jsonl): seconds and the chance each loses the secret (beyond m's own 1%)
CPU = {
    (512, 4, 0.3, 448): {"name": "L1", "methods": [
        ("mitm, random halving, expected time over 10 seeds", 0.148, 0.0),
        ("vexh two-stage, m1 320, tau1 66", 0.166, 8.8e-5),
        ("vexh one-stage scan", 0.180, 0.0)]},
    (512, 4, 0.4, 1850): {"name": "L2", "methods": [
        ("vexh two-stage, m1 1152, tau1 106", 0.508, 8.9e-5),
        ("vexh two-stage, m1 1024, tau1 104", 0.459, 6.2e-4),
        ("vexh one-stage scan", 0.693, 0.0)]},
    (256, 5, 0.4, 1925): {"name": "(256,5)", "methods": [
        ("vexh two-stage, m1 1152, tau1 106", 1.769, 8.9e-5),
        ("vexh two-stage, m1 1024, tau1 104", 1.58, 6.2e-4),
        ("vexh one-stage scan", 2.57, 0.0)]},
}


def leak_slope(T):
    return A_LEAK_80 / T_L * math.exp((T - 80.0) / T_L)


def jl(path):
    if os.path.exists(path + ".gz"):
        return [json.loads(l) for l in gzip.open(path + ".gz", "rt") if l.startswith("{")]
    if os.path.exists(path):
        out = []
        for l in open(path):
            if l.startswith("{"):
                try:
                    out.append(json.loads(l))
                except ValueError:       # a line cut by the sampler's stop
                    pass
        return out
    return []


def last_json(path):
    try:
        lines = [l for l in open(path).read().splitlines() if l.startswith("{")]
        return json.loads(lines[-1]) if lines else {}
    except (OSError, ValueError):
        return {}


def integrate(t, y, a, b, step=0.005):
    """The integral of the samples (linear between them) over [a, b]."""
    if b <= a:
        return 0.0
    g = np.arange(a, b, step)
    return float(np.interp(g, t, y).sum() * step)


def mean(x):
    return float(np.mean(x)) if len(x) else float("nan")


def rnd(x, nd=4):
    if isinstance(x, dict):
        return {k: rnd(v, nd) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rnd(v, nd) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if (math.isnan(x) or math.isinf(x)) else round(float(x), nd)
    if isinstance(x, (np.integer,)):
        return int(x)
    return x


def cpu_note(inst, sl):
    key = (inst.get("n"), inst.get("k"), round(float(inst.get("eta", 0)), 3), inst.get("m"))
    c = CPU.get(key)
    if not c:
        return None
    ok = [x for x in c["methods"] if x[2] <= P_LOSS_MAX]
    name, best_s, best_p = min(ok, key=lambda x: x[1])
    out = {"instance": c["name"], "cpu_6t_best_s": best_s, "cpu_6t_best": name, "cpu_6t_best_p_loss": best_p,
           "p_loss_max": P_LOSS_MAX,
           "cpu_6t_methods": [{"method": m, "s": t, "p_loss": pl} for m, t, pl in c["methods"]],
           "assumed_w": list(CPU_W), "cpu_6t_best_j": [best_s * w for w in CPU_W],
           "note": "CPU energy assumed (package power x measured 6-thread time, idle included), not measured"}
    if sl and sl != "0/1":
        out["partial"] = f"slice {sl}: part of one solve; add the parts (energy_reduce.py combine) before comparing"
    return out


def ratios(c, card_j, host_j):
    """CPU over the card's board alone, and over the card's board plus the host's package (bounds)."""
    c["card_board_total_j"] = card_j
    c["host_package_j"] = host_j
    c["cpu_over_card_board"] = [c["cpu_6t_best_j"][0] / card_j, c["cpu_6t_best_j"][1] / card_j]
    c["cpu_over_card_board_note"] = "the card's board alone: the host that drives it is not counted"
    if host_j:
        c["cpu_over_card_and_host"] = [c["cpu_6t_best_j"][0] / (card_j + host_j[1]),
                                       c["cpu_6t_best_j"][1] / (card_j + host_j[0])]
    return c


def reduce_dir(d):
    tel = jl(os.path.join(d, "telemetry.jsonl"))
    h = last_json(os.path.join(d, "host.json"))
    run = {}
    try:
        run = json.load(open(os.path.join(d, "run.json")))
    except (OSError, ValueError):
        pass
    flags, hard = [], []
    res = {"dir": os.path.abspath(d), "run": run, "flags": flags, "hard": hard}
    if len(tel) < 20:
        hard.append(f"telemetry: {len(tel)} lines")
        res["ok"] = False
        return res
    tel = [s for s in tel if "board_w" in s and "sp" in s and "temp_c" in s]
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    w = np.array([s["board_w"] for s in tel], float)
    T = np.array([s["temp_c"]["minshire"][0] for s in tel], float)
    Thi = np.array([s["temp_c"]["minshire"][2] for s in tel], float)
    mhz = np.array([s.get("mhz", {}).get("minion", -1) for s in tel])      # -1: the sample has no clock reading
    took = np.array([s.get("took_ms", 0) for s in tel], float)
    rails = {k: np.array([s["sp"][k][0] for s in tel], float) for k in RAILS}
    bavg = np.array([s["sp"].get("board_avg_w", s["board_w"]) for s in tel], float)

    reps = int(h.get("reps_done", 0) or 0)
    launch_s = [float(x) for x in h.get("launch_s", [])]
    ep = h.get("launch_epoch_ms") or [0, 0]
    host_t0 = run.get("host_t0_ms", 0) / 1000.0
    host_t1 = run.get("host_t1_ms", 0) / 1000.0
    src = "host launch_epoch_ms"
    if ep[0] and ep[1] and ep[1] > ep[0]:
        lo, hi = ep[0] / 1000.0, ep[1] / 1000.0
    else:
        src = None
    # the board's own edges inside the host process's span (a cross-check; the fallback without launch_epoch_ms)
    span = (t >= (host_t0 or t[0]) - 0.5) & (t <= (host_t1 or t[-1]) + 1.0)
    pre = t < (host_t0 or (lo if src else t[0] + 3)) - 0.3
    edges = None
    if span.any() and pre.sum() >= 4:
        base = float(np.median(w[pre]))
        top = float(np.percentile(w[span], 90))
        if top - base > 1.0:
            thr = base + 0.5 * (top - base)
            idx = np.where(span & (w > thr))[0]
            if len(idx):
                edges = [float(t[idx[0]]), float(t[idx[-1]])]
    if src is None:
        if not edges:
            hard.append("no burst window: the host has no launch_epoch_ms and the board shows no step")
            res["ok"] = False
            res["host"] = h
            return res
        lo, hi, src = edges[0], edges[1], "board edges (fallback: the host has no launch_epoch_ms)"
        flags.append("burst window from the board's edges (+-1 SP pass)")
    wall = hi - lo
    busy = (t >= lo + BUSY_SKIP) & (t <= hi)
    before = (t >= lo - BEFORE[0]) & (t <= lo - BEFORE[1])
    after = (t >= hi + AFTER[0]) & (t <= hi + AFTER[1])
    if busy.sum() < 5:
        hard.append(f"busy window: {int(busy.sum())} samples")
    if before.sum() < 4:
        hard.append(f"before bracket: {int(before.sum())} samples")
    if after.sum() < 4:
        flags.append(f"after bracket: {int(after.sum())} samples (idle from the before bracket alone)")
    if hard:
        res.update({"ok": False, "host": h})
        return res

    # ---- board: the catalogue's method
    idle_b = mean(w[before])
    idle_a = mean(w[after]) if after.sum() >= 4 else float("nan")
    idle = idle_b if math.isnan(idle_a) else 0.5 * (idle_b + idle_a)
    Tb = mean(T[busy])
    Tbef = mean(T[before])
    Ti = mean(np.concatenate([T[before], T[after]])) if after.sum() >= 4 else Tbef
    p = mean(w[busy])
    over_raw = p - idle
    slope = leak_slope(0.5 * (Tb + Ti))
    over = over_raw - slope * (Tb - Ti)
    # the integral, corrected sample by sample
    ia, ib = lo - INT_PRE, hi + INT_POST_BOARD
    s_int = leak_slope(0.5 * (Tbef + Tb))
    e_int = integrate(t, w - idle_b - s_int * (T - Tbef), ia, ib)
    e_int_raw = integrate(t, w - idle_b, ia, ib)
    # ---- the long window, [lo - 1, hi + 6] (5.7 tau past the end): the SP's board average (the PMIC's running
    # average of the board, tau ~1 s: 2026-09-22-horace-aifoundry3) and the three rails. Integrated, a unit-gain
    # filter's output keeps the step's energy, so no filter correction; and an average does not alias the gaps between
    # launches, which the point-sampled board_w can hold at idle for a whole pass. Their leakage correction uses no
    # temperature (the sensor reads whole degrees): the baseline is the before bracket's mean until lo, the late
    # bracket's [hi + 6, hi + 8] (the die still warm, the filter settled) from hi, and a straight line between; the
    # uncorrected values (flat at the before bracket) are kept beside them.
    la, lb = lo - INT_PRE, hi + INT_POST_RAIL
    late = (t >= lb) & (t <= lb + RAIL_RESID)
    if t[-1] < lb:
        flags.append(f"telemetry ends {lb - t[-1]:.1f} s before the long window does (SP average and rails understated)")
    if late.sum() < 4:
        flags.append(f"late bracket [hi + 6, hi + 8]: {int(late.sum())} samples (long-window values uncorrected)")
    lb_eff = min(lb, t[-1])

    def long_window(v):
        base = mean(v[before])
        top = mean(v[late]) if late.sum() >= 4 else base
        bl = np.where(t <= lo, base, np.where(t >= hi, top, base + (top - base) * (t - lo) / max(wall, 1e-9)))
        return base, top, integrate(t, v - bl, la, lb_eff), integrate(t, v - base, la, lb_eff)

    bavg_b, bavg_late, e_avg, e_avg_raw = long_window(bavg)
    # THE HEADLINE: the same integral above the before bracket, less the catalogue's leakage law on the measured die
    # temperature sample by sample (the fast thermal stages, which heat the die within the burst and let it cool
    # within seconds of its end, are in the sensor's reading; the late bracket misses them: the ramp baseline
    # overstates the energy when they matter, +4% on energy_stub.py's alt card, which has 11-thermal-model.md's chain)
    e_avg_law = integrate(t, bavg - bavg_b - s_int * (T - Tbef), la, lb_eff)
    leak_burst = s_int * integrate(t, T - Tbef, lo, hi)          # the leakage's rise within the burst, by the law
    # board_w passes inside the burst that read below the midpoint (a pass that sampled a gap between launches)
    bw = w[busy]
    vals = [bw[0]] + [x for x0, x in zip(bw[:-1], bw[1:]) if x != x0]
    dips = sum(1 for x in vals if x < idle + 0.5 * over_raw)
    chg = np.where(np.diff(w[busy]) != 0)[0]
    refresh = float(np.median(np.diff(t[busy][chg + 1]))) if len(chg) > 2 else None
    # a pass lands in a gap between launches with the gaps' share of the burst: the number expected at idle
    gap_share = max(0.0, 1.0 - sum(launch_s) / wall) if launch_s and wall > 0 else 0.0
    dips_exp = len(vals) * gap_share
    per = (lambda x: x / reps) if reps else (lambda x: None)
    board = {"headline": "the SP's board average over the long window above the before bracket, less the leakage law "
                         "on the measured die temperature",
             "j_per_solve": per(e_avg_law), "j_per_solve_raw": per(e_avg_raw),
             "j_per_solve_sp_avg_ramp": per(e_avg),
             "sp_avg_idle_w": bavg_b, "sp_avg_late_w": bavg_late, "leak_slope_w_per_c": s_int,
             "leak_rise_j_per_solve": per(leak_burst),
             # idle included: the before bracket's idle over the burst, the leakage's rise within it, the headline
             "j_per_solve_total": per(bavg_b * wall + leak_burst + e_avg_law),
             "catalogue": {"note": "the energy catalogue's method (analyze_catalogue.py): a cross-check; one run moves by "
                                   "one SP pass of its step per busy reading at idle",
                           "idle_w": idle, "idle_before_w": idle_b, "idle_after_w": idle_a, "busy_w": p,
                           "over_idle_raw_w": over_raw, "over_idle_w": over, "leak_correction_w": over_raw - over,
                           "leak_slope_w_per_c": slope,
                           "j_per_solve": per(over * wall), "j_per_solve_raw": per(over_raw * wall),
                           "j_per_solve_integral": per(e_int), "j_per_solve_integral_raw": per(e_int_raw),
                           "j_per_solve_total": per(p * wall),
                           "busy_readings": len(vals), "busy_readings_at_idle": dips,
                           "busy_readings_at_idle_expected": dips_exp, "gap_share": gap_share,
                           "one_pass_j_per_solve": per(refresh * over * 1.0) if refresh else None},
             "windows_s": {"busy": [BUSY_SKIP, 0.0], "before": [-BEFORE[0], -BEFORE[1]], "after": list(AFTER),
                           "integral": [-INT_PRE, INT_POST_BOARD], "long": [-INT_PRE, INT_POST_RAIL],
                           "late": [INT_POST_RAIL, INT_POST_RAIL + RAIL_RESID]}}
    tail_w = (t >= hi - 0.6) & (t <= hi)
    fill = 1.0 - math.exp(-max(wall - 0.3, 0.0) / TAU_RAIL)
    rail = {}
    for k, v in rails.items():
        base, top, e, e_raw = long_window(v)
        plat = (mean(v[tail_w]) - base) / fill if tail_w.any() and fill > 0 else float("nan")
        rail[k] = {"idle_w": base, "late_minus_idle_w": top - base,
                   "j_per_solve": e / reps if reps else None, "j_per_solve_raw": e_raw / reps if reps else None,
                   "over_idle_w_plateau": plat, "j_per_solve_plateau": plat * wall / reps if reps else None}
    rail["unmetered"] = {
        "j_per_solve": (e_avg_law - sum(rail[k]["j_per_solve"] for k in RAILS) * reps) / reps if reps else None,
        "j_per_solve_raw": (e_avg_raw - sum(rail[k]["j_per_solve_raw"] for k in RAILS) * reps) / reps if reps else None,
        "note": "the headline minus the three rails (a small difference of two larger numbers: +-15%)"}

    if dips:
        flags.append(f"{dips} of {len(vals)} busy board_w readings at idle (a pass between launches; {dips_exp:.1f} expected): "
                     f"the catalogue value is about {(dips - dips_exp) / len(vals):.0%} low in this run; the SP average (the "
                     f"headline) does not alias them")
    cat = board["catalogue"]
    if reps and refresh and board["j_per_solve"]:
        # the two estimates should agree within both claims: 3% each, and the catalogue's aliasing (a pass of the
        # step for each busy reading at idle more or fewer than expected)
        allow = 0.06 * abs(board["j_per_solve"]) + (abs(dips - dips_exp) + 1) * cat["one_pass_j_per_solve"]
        if abs(cat["j_per_solve"] - board["j_per_solve"]) > allow:
            flags.append(f"the catalogue method ({cat['j_per_solve']:.3f} J) is off the headline ({board['j_per_solve']:.3f} J) "
                         f"by more than 6% and {abs(dips - dips_exp) + 1:.1f} SP pass(es) of the step")
    # ---- checks on the meter and the run
    mhz_busy = sorted({int(x) for x in mhz[busy] if x >= 0})
    if any(x != 600 for x in mhz_busy):
        hard.append(f"minion clock in busy samples: {mhz_busy} MHz (the governor moved it)")
    elif not mhz_busy:
        flags.append("no clock reading in the busy samples")
    took_med, took_max = float(np.median(took[busy])), float(took[busy].max())
    if took_med > 60:
        flags.append(f"sampler median {took_med:.0f} ms in the burst (a starved meter)")
    if h.get("status") != "PASS":
        # a host that only stopped short of its --reps (its --budget rule) measured what it ran: a flag, not a failure
        short_only = h.get("problems") and all(p.startswith("reps:") for p in h["problems"]) and reps > 0
        (flags if short_only else hard).append(
            f"host status {h.get('status')} ({'; '.join(h.get('problems', [])) or h.get('launch_error', '')})")
    if h.get("reps_done") != h.get("reps_requested"):
        flags.append(f"host ran {h.get('reps_done')} of {h.get('reps_requested')} launches ({h.get('stop_reason')})")
    if h.get("reps_consistent") not in (None, "ok"):
        hard.append(f"reps_consistent {h.get('reps_consistent')}")
    if run.get("foreign"):
        hard.append(f"foreign device process during the run: {run['foreign']}")
    if run.get("host_rc") not in (None, 0):
        flags.append(f"host exit code {run.get('host_rc')}")
    if run.get("dry") or h.get("stub"):
        flags.append("DRY: test doubles, not a measurement")
    if edges:
        d_lo, d_hi = edges[0] - lo, edges[1] - hi
        if src.startswith("host") and (abs(d_lo) > 0.8 or abs(d_hi) > 0.8):
            flags.append(f"the board's edges are {d_lo:+.2f} / {d_hi:+.2f} s off the host's launch times")
    inst = h.get("instance", {})
    sl = h.get("plan", {}).get("slice", "0/1")
    res.update({
        "host": {k: h.get(k) for k in ("status", "reps_requested", "reps_done", "reps_consistent", "stop_reason",
                                        "open_s", "setup_s", "device_held_s", "process_s", "launch_epoch_ms")},
        "instance": inst, "slice": sl, "variant": h.get("m4"),
        "plan": {k: h.get("plan", {}).get(k) for k in ("ops", "candidates", "model_s", "guard_s", "timeout_s", "coverage")},
        "result": {k: h.get("result", {}).get(k) for k in ("solved", "unique", "answer")},
        "kernel_clock_mhz_est": h.get("kernel", {}).get("clock_mhz_est"),
        "window": {"source": src, "lo_ms": int(lo * 1000), "hi_ms": int(hi * 1000), "wall_s": wall,
                   "board_edges_minus_host_s": [edges[0] - lo, edges[1] - hi] if edges else None},
        "solves": reps, "solves_per_s": reps / wall if wall > 0 else None,
        "launch_s_mean": mean(launch_s), "launch_s_min": min(launch_s) if launch_s else None,
        "launch_s_max": max(launch_s) if launch_s else None,
        "solves_per_s_kernel": len(launch_s) / sum(launch_s) if launch_s else None,
        "board": board, "rails": rail,
        "die_c": {"before": Tbef, "busy": Tb, "idle_brackets": Ti, "after": mean(T[after]) if after.any() else None,
                  "max_avg": float(T[busy].max()), "max_high": float(Thi[busy].max()),
                  "busy_start": float(T[busy][0]), "busy_end": float(T[busy][-1])},
        "meter": {"samples": len(t), "busy": int(busy.sum()), "before": int(before.sum()), "after": int(after.sum()),
                  "sample_period_ms": float(np.median(np.diff(t))) * 1000, "took_ms_median": took_med,
                  "took_ms_max": took_max, "board_refresh_s": refresh, "minion_mhz_busy": mhz_busy},
        "cpu": cpu_note(inst, sl), "rapl": run.get("rapl"),
    })
    # ---- the host's share: its package idle over the burst, and its busy core-seconds over the burst
    hc = h.get("host_cpu_s") or {}
    ext = run.get("host_cpu_ext_s")
    cpu_src, core_s = None, None
    if hc.get("burst") and launch_s:
        core_s, cpu_src = float(sum(hc["burst"])), "host_cpu_s.burst (getrusage over launch_epoch_ms)"
    elif ext:
        core_s, cpu_src = float(sum(ext)), "energy.sh's CPU time of the whole host process (an upper bound for the burst)"
        flags.append("the host has no host_cpu_s: its share uses the whole process's CPU time (an upper bound)")
    if core_s is not None and reps:
        host_j = [(HOST_IDLE_W[0] * wall + HOST_CORE_W[0] * core_s) / reps,
                  (HOST_IDLE_W[1] * wall + HOST_CORE_W[1] * core_s) / reps]
        res["host_share"] = {"cpu_s_burst": core_s, "source": cpu_src, "busy_cores_mean": core_s / wall if wall > 0 else None,
                             "host_cpu_s": hc or None, "host_cpu_ext_s": ext,
                             "assumed_idle_w": list(HOST_IDLE_W), "assumed_core_w": list(HOST_CORE_W),
                             "j_per_solve": host_j,
                             "note": "assumed package power (RAPL is root-only): idle over the burst + per busy core-second"}
    else:
        res["host_share"] = None
        flags.append("no host CPU time: the host's share is not bounded")
    if res["cpu"] and sl == "0/1" and board["j_per_solve"]:
        ratios(res["cpu"], board["j_per_solve_total"], (res["host_share"] or {}).get("j_per_solve"))
        res["cpu"]["card_over_idle_j"] = board["j_per_solve"]
    res["ok"] = not hard
    return res


def fmt_ratio(c):
    out = (f"x{c['cpu_over_card_board'][0]:.1f}-{c['cpu_over_card_board'][1]:.1f} the card's board alone (the host not "
           f"counted)")
    if c.get("cpu_over_card_and_host"):
        out += (f"; x{c['cpu_over_card_and_host'][0]:.1f}-{c['cpu_over_card_and_host'][1]:.1f} the card's board + the "
                f"host's package ({c['host_package_j'][0]:.2f}-{c['host_package_j'][1]:.2f} J assumed)")
    return out


def summary(r):
    if not r.get("board"):
        return f"energy: no result ({'; '.join(r.get('hard', []))})"
    b, ra, dc = r["board"], r["rails"], r["die_c"]
    cat = b["catalogue"]
    inst = r.get("instance", {})
    name = (r.get("cpu") or {}).get("instance") or f"({inst.get('n')},{inst.get('k')},{inst.get('eta')},{inst.get('m')})"
    sl = r.get("slice", "0/1")
    lines = [
        f"{name}{'' if sl == '0/1' else ' slice ' + sl}: {r['solves']} solves in {r['window']['wall_s']:.3f} s "
        f"({r['solves_per_s']:.3f}/s; kernel {r['launch_s_mean']:.4f} s each, {r['solves_per_s_kernel']:.3f}/s)",
        f"  J per solve over idle (the SP's board average, the law on the die temperature): {b['j_per_solve']:.3f} "
        f"(uncorrected {b['j_per_solve_raw']:.3f}, ramp baseline {b['j_per_solve_sp_avg_ramp']:.3f}; the leakage's rise "
        f"{b['leak_rise_j_per_solve']:.3f}); board total per solve, idle included, {b['j_per_solve_total']:.3f} J",
        f"  catalogue method (cross-check): {cat['j_per_solve']:.3f} J (uncorrected {cat['j_per_solve_raw']:.3f}, integral "
        f"{cat['j_per_solve_integral']:.3f}; {cat['busy_readings_at_idle']} of {cat['busy_readings']} busy readings at idle, "
        f"{cat['busy_readings_at_idle_expected']:.1f} expected, "
        f"one pass = {(cat['one_pass_j_per_solve'] or 0):.3f} J per solve); board {cat['busy_w']:.2f} W in the burst, idle "
        f"{cat['idle_w']:.2f} W: +{cat['over_idle_raw_w']:.2f} W, +{cat['over_idle_w']:.2f} W leakage-corrected "
        f"({cat['leak_correction_w']:+.2f} W at {cat['leak_slope_w_per_c']:.3f} W/C)",
        f"  die {dc['before']:.1f} C before, {dc['busy']:.1f} C busy (max {dc['max_avg']:.0f}), {dc['idle_brackets']:.1f} C brackets",
        f"  rails, J per solve: minion {ra['minion_w']['j_per_solve']:.3f}, SRAM {ra['sram_w']['j_per_solve']:.3f}, "
        f"NoC {ra['noc_w']['j_per_solve']:.3f} (ramp baseline: upper bounds), unmetered {ra['unmetered']['j_per_solve']:.3f} "
        f"(the headline minus the rails)",
    ]
    hs = r.get("host_share")
    if hs:
        lines.append(f"  host: {hs['cpu_s_burst']:.3f} CPU s over the burst ({hs['busy_cores_mean']:.2f} cores busy on average; "
                     f"{hs['source']}); its package, assumed, {hs['j_per_solve'][0]:.2f}-{hs['j_per_solve'][1]:.2f} J per solve")
    c = r.get("cpu")
    if c:
        lines.append(f"  CPU 6T best at P(loss) <= {c['p_loss_max']:g} ({c['cpu_6t_best']}, P(loss) {c['cpu_6t_best_p_loss']:g}, "
                     f"{c['cpu_6t_best_s']} s): {c['cpu_6t_best_j'][0]:.1f}-{c['cpu_6t_best_j'][1]:.1f} J at an assumed "
                     f"{CPU_W[0]:.0f}-{CPU_W[1]:.0f} W" + ("; " + fmt_ratio(c) if c.get("cpu_over_card_board")
                                                           else f" ({c.get('partial', '')})"))
    if r.get("rapl"):
        lines.append(f"  RAPL on the host: {r['rapl']}")
    lines.append(("  OK" if r["ok"] else "  NOT OK: " + "; ".join(r["hard"])) +
                 (" | " + "; ".join(r["flags"]) if r["flags"] else ""))
    return "\n".join(lines)


def check_truth(r, path):
    """The reduced values against the energies the test double injected, at the accuracy claimed (the module's
    docstring): the headline within 3%, the board total within 2%, each rail within -2%..+7% (or 5 mJ), the unmetered
    part within 15% (or 10 mJ); the catalogue method within 3% plus one SP pass of the step for each busy reading at
    idle more or fewer than expected (the busy passes x the gaps' share of the burst, the gaps by the host's clock),
    and one more (the card's own gaps are longer than the host's by its launch latency), its integral one pass more
    (its edges); the burst's edges within 10 ms."""
    tr = json.load(open(path))
    bad = []

    def near(name, got, want, rel, absd=0.0, hi_rel=None):
        """got within want -max(rel |want|, absd) .. +max(hi_rel |want|, absd) (hi_rel defaults to rel)."""
        lo_tol = max(rel * abs(want or 0), absd)
        hi_tol = max((rel if hi_rel is None else hi_rel) * abs(want or 0), absd)
        ok = got is not None and want is not None and -lo_tol <= got - want <= hi_tol
        err = (got - want) / want * 100 if got is not None and want else float("nan")
        print(f"  truth {name}: reduced {got if got is None else round(got, 4)} vs injected "
              f"{want if want is None else round(want, 4)} ({err:+.2f}%, allowed -{lo_tol:.4f}/+{hi_tol:.4f}) "
              f"{'ok' if ok else 'OFF'}")
        if not ok:
            bad.append(name)
    near("reps", r.get("solves"), tr.get("reps"), 0.0)
    want = tr["board_dyn_j_per_solve"]
    b, cat = r["board"], r["board"]["catalogue"]
    near("board J/solve (headline: SP average, law on T)", b["j_per_solve"], want, 0.03)
    if tr.get("board_total_j_per_solve") is not None:
        near("board total J/solve (idle included)", b["j_per_solve_total"], tr["board_total_j_per_solve"], 0.02)
    one = cat.get("one_pass_j_per_solve") or 0.0
    alias = abs(cat.get("busy_readings_at_idle", 0) - cat.get("busy_readings_at_idle_expected", 0))
    near("board J/solve (catalogue method)", cat["j_per_solve"], want, 0.0, 0.03 * abs(want) + (alias + 1) * one)
    near("board J/solve (catalogue integral)", cat["j_per_solve_integral"], want, 0.0, 0.03 * abs(want) + (alias + 2) * one)
    for k in RAILS:
        near(f"{k} J/solve (ramp baseline)", r["rails"][k]["j_per_solve"], tr["rails_dyn_j_per_solve"][k], 0.02, 0.005, 0.07)
    if tr.get("unmetered_dyn_j_per_solve") is not None:
        near("unmetered J/solve", r["rails"]["unmetered"]["j_per_solve"], tr["unmetered_dyn_j_per_solve"], 0.15, 0.01)
    print(f"  (not checked: the ramp baseline {b['j_per_solve_sp_avg_ramp']:.4f} J, "
          f"{(b['j_per_solve_sp_avg_ramp'] / want - 1) * 100:+.2f}% of the injected)")
    burst = tr.get("burst")
    if burst:
        near("burst start (s)", r["window"]["lo_ms"] / 1000.0, burst[0], 0.0, 0.01)
        near("burst end (s)", r["window"]["hi_ms"] / 1000.0, burst[1], 0.0, 0.01)
    return bad


class Refused(Exception):
    pass


def combine(dirs, label):
    """The slices of one solve added up; Refused unless they are exactly the slices 0..N-1 of one N of one instance,
    variant and kernel."""
    parts = []
    for d in dirs:
        p = os.path.join(d, "energy.json")
        parts.append(json.load(open(p)) if os.path.exists(p) else reduce_dir(d))
    why = []
    for p in parts:
        if not p.get("board"):
            why.append(f"{p.get('dir')}: no result ({'; '.join(p.get('hard', []))})")
    if why:
        raise Refused("; ".join(why))

    def ident(p):
        inst = p.get("instance") or {}
        return (inst.get("hash") or "no hash: " + json.dumps({k: inst.get(k) for k in ("n", "k", "eta", "m", "seed")}),
                json.dumps(p.get("variant"), sort_keys=True), (p.get("run") or {}).get("kernel_text_sha256"))
    ids = {ident(p) for p in parts}
    if len(ids) != 1:
        why.append("the parts are not one instance, variant and kernel: " + "; ".join(
            f"{os.path.basename(p['dir'])}: hash {ident(p)[0]}, kernel {str(ident(p)[2])[:12]}" for p in parts))
    sl = []
    for p in parts:
        try:
            i, n = (int(x) for x in str(p.get("slice", "")).split("/"))
            sl.append((i, n))
        except ValueError:
            why.append(f"{p['dir']}: slice {p.get('slice')!r} is not I/N")
    if sl and not why:
        ns = {n for _, n in sl}
        idx = sorted(i for i, _ in sl)
        if len(ns) != 1 or idx != list(range(next(iter(ns)))):
            why.append(f"the slices {[f'{i}/{n}' for i, n in sl]} are not 0..N-1 of one N, each once")
    if len({bool((p.get('run') or {}).get('dry')) for p in parts}) != 1:
        why.append("dry and card runs mixed")
    if why:
        raise Refused("; ".join(why))
    keys = ["j_per_solve", "j_per_solve_raw", "j_per_solve_sp_avg_ramp", "j_per_solve_total"]
    ckeys = ["j_per_solve", "j_per_solve_raw", "j_per_solve_integral", "j_per_solve_total"]
    hs = [p.get("host_share") for p in parts]
    out = {"label": label, "parts": [p["dir"] for p in parts], "slices": [p.get("slice") for p in parts],
           "instance": parts[0].get("instance"), "variant": parts[0].get("variant"),
           "kernel_text_sha256": (parts[0].get("run") or {}).get("kernel_text_sha256"),
           "ok": all(p.get("ok") for p in parts),
           "wall_s_per_solve": sum(p["window"]["wall_s"] / p["solves"] for p in parts),
           "kernel_s_per_solve": sum(p["launch_s_mean"] for p in parts),
           "board": {k: sum(p["board"][k] for p in parts) for k in keys},
           "board_catalogue": {k: sum(p["board"]["catalogue"][k] for p in parts) for k in ckeys},
           "rails": {k: sum(p["rails"][k]["j_per_solve"] for p in parts) for k in RAILS + ("unmetered",)},
           "host_share_j_per_solve": [sum(h["j_per_solve"][0] for h in hs), sum(h["j_per_solve"][1] for h in hs)]
           if all(hs) else None,
           "die_c_busy": [p["die_c"]["busy"] for p in parts]}
    c = cpu_note(out["instance"] or {}, "0/1")
    if c:
        ratios(c, out["board"]["j_per_solve_total"], out["host_share_j_per_solve"])
        c["card_over_idle_j"] = out["board"]["j_per_solve"]
    out["cpu"] = c
    return out


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "combine":
        ap = argparse.ArgumentParser()
        ap.add_argument("cmd")
        ap.add_argument("dirs", nargs="+")
        ap.add_argument("--label", default="combined")
        ap.add_argument("--json")
        a = ap.parse_args()
        try:
            out = combine(a.dirs, a.label)
        except Refused as e:
            print(f"{a.label}: REFUSED: {e}")
            return 2
        b = out["board"]
        print(f"{a.label}: {len(a.dirs)} parts ({', '.join(out['slices'])}), {out['wall_s_per_solve']:.3f} s per solve "
              f"(kernel {out['kernel_s_per_solve']:.3f} s); J per solve over idle (the headline) {b['j_per_solve']:.3f} "
              f"(uncorrected {b['j_per_solve_raw']:.3f}; catalogue method {out['board_catalogue']['j_per_solve']:.3f}), "
              f"total {b['j_per_solve_total']:.3f}; minion {out['rails']['minion_w']:.3f}, SRAM {out['rails']['sram_w']:.3f}, "
              f"NoC {out['rails']['noc_w']:.3f}, unmetered {out['rails']['unmetered']:.3f}" + ("" if out["ok"] else " (a part is NOT OK)"))
        if out["host_share_j_per_solve"]:
            print(f"  host package, assumed: {out['host_share_j_per_solve'][0]:.2f}-{out['host_share_j_per_solve'][1]:.2f} J per solve")
        if out["cpu"]:
            c = out["cpu"]
            print(f"  CPU 6T best at P(loss) <= {c['p_loss_max']:g} ({c['cpu_6t_best']}, {c['cpu_6t_best_s']} s): "
                  f"{c['cpu_6t_best_j'][0]:.0f}-{c['cpu_6t_best_j'][1]:.0f} J assumed; " + fmt_ratio(c))
        if a.json:
            json.dump(rnd(out), open(a.json, "w"), indent=1)
        return 0 if out["ok"] else 1
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--json")
    ap.add_argument("--truth")
    a = ap.parse_args()
    r = reduce_dir(a.dir)
    json.dump(rnd(r, 5), open(a.json or os.path.join(a.dir, "energy.json"), "w"), indent=1)
    print(summary(r))
    rc = 0 if r.get("ok") else 1
    if a.truth:
        bad = check_truth(r, a.truth)
        print("  TRUTH " + ("PASS" if not bad else "FAIL: " + ", ".join(bad)) +
              " (a test of the reducer against the test double's card, not a measurement)")
        rc = 1 if bad else 0
    return rc


if __name__ == "__main__":
    sys.exit(main())
