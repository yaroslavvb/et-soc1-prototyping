#!/usr/bin/env python3
"""DV2 per-run observables (DESIGN §6 'Standard per-run observables', A2's TRIG-A definitions; PREREG-DEV §1.1), from a
run's 10 Hz telemetry and its heater output. Used live by block.sh (DEV-1 needs trip_s and 'qualifies') and by
reduce_dv2.py.

  t0      the measured launch's first kernel start (its launch -1 SPARSITY line); t_end its last kernel end
  t_up    the first sample at 800 MHz at or after t0
  t_m     the first sample at or after t0 with the mean >= K
  t_spm   the first sample at or after t0 with sp.minion_c's max >= K
  t_hi    the first sample at 800 MHz at or after t0 with the high >= K; t_hi2 the same with >= K + 1
  t_down  the first one-point 800 -> 700 step after t_up (a single 800 -> 600 change is an idle reset: excluded)
  trip_s  t_down - t_up; qualifies (DEV-1): the trip falls in [t_up + 1.5 s, t_end - 0.5 s]
  separating (G1-T): (a) t_m - t_hi >= 1.5 s, or (b) the high reads >= K + 1 at t_up and the clock holds 800 for
          >= 0.5 s; fits H-mean if t_down in [t_m - 0.3, t_m + 0.6] s (or under (b)); fits H-max if t_down in
          [t_hi - 0.3, t_hi + 0.6] s
  G1-H    the largest (high - thr) at a sample at 800 MHz that stays at 800 for >= 1.0 s after, with a rise >= 2 C in
          the high since t0 (reported)
  P_x     board W over [t_up + 0.3, t_up + 2.3] s (the ADD run's own: minus the idle W over [t0 - 2, t0])
  C1m     t_c = the first sample at or after t0 with the mean >= target; off600 = samples off 600 MHz in [t0, t_end]
"""
import json
import sys

from dv2lib import heater_lines, load_jsonl, median, sample_fields


def _sp_max(s):
    v = ((s.get("sp") or {}).get("minion_c") or [None, None, None])
    m = v[2] if len(v) > 2 else None
    return None if m is None or m in (0, 65535) else m


def runobs(tel_path, heater_path, K=66, thr=65, target=None, stop_ms=None):
    raw = load_jsonl(tel_path)
    tel = sorted([(sample_fields(s), _sp_max(s)) for s in raw if s.get("t_ms") is not None], key=lambda x: x[0][0])
    hl = heater_lines(heater_path)
    o = {"K": K, "flags": [], "void": []}
    if not hl:
        o["void"].append("no heater output")
        return o
    t0 = min(h["t_start_ms"] for h in hl if h.get("launch") == -1) if any(h.get("launch") == -1 for h in hl) else min(h["t_start_ms"] for h in hl)
    t_end = max(h["t_end_ms"] for h in hl)
    o["t0_ms"], o["t_end_ms"] = t0, t_end
    o["launch_s"] = round((t_end - t0) / 1000.0, 3)
    if not tel:
        o["void"].append("no telemetry")
        return o
    F = [x for x, _ in tel]
    ts = [x[0] for x in F if t0 - 2000 <= x[0] <= t_end]
    gap = max((b - a for a, b in zip(ts, ts[1:])), default=None)
    o["max_gap_ms"] = gap
    if gap is None or gap > 1000:
        o["void"].append("sampler gap > 1 s (max %s ms)" % gap)
    after = [(x, spm) for x, spm in tel if x[0] >= t0]

    def first(pred):
        for x, spm in after:
            if pred(x, spm):
                return x[0]
        return None
    t_up = first(lambda x, s: x[5] == 800)
    o["t_up"] = t_up
    o["t_m"] = first(lambda x, s: x[1] is not None and x[1] >= K)
    o["t_spm"] = first(lambda x, s: s is not None and s >= K)
    o["t_hi"] = first(lambda x, s: x[5] == 800 and x[3] is not None and x[3] >= K)
    o["t_hi2"] = first(lambda x, s: x[5] == 800 and x[3] is not None and x[3] >= K + 1)
    t_down = None
    if t_up is not None:
        prev = None
        for x, _ in after:
            if x[0] < t_up:
                continue
            if prev is not None and prev == 800 and x[5] == 700:
                t_down = x[0]
                break
            if x[5] is not None:
                prev = x[5]
    o["t_down"] = t_down
    o["trip_s"] = round((t_down - t_up) / 1000.0, 3) if t_down is not None and t_up is not None else None
    o["censored"] = t_down is None
    o["qualifies"] = bool(t_down is not None and t_up + 1500 <= t_down <= t_end - 500)
    # 700 dwell and climb shape (G2 host bands)
    o["mhz_set"] = sorted({x[5] for x, _ in after if x[5] is not None and x[0] <= t_end + 10000})
    # separating runs (G1-T) and the fits
    sep = None
    if o["t_m"] is not None and o["t_hi"] is not None and o["t_m"] - o["t_hi"] >= 1500:
        sep = "a"
    if t_up is not None:
        at_up = next((x for x, _ in after if x[0] == t_up), None)
        hold = [x for x, _ in after if t_up <= x[0] <= t_up + 500]
        if at_up and at_up[3] is not None and at_up[3] >= K + 1 and hold and all(x[5] == 800 for x in hold) and hold[-1][0] >= t_up + 400:
            sep = sep or "b"
    o["separating"] = sep
    fm = fx = None
    if t_down is not None:
        if o["t_m"] is not None:
            fm = o["t_m"] - 300 <= t_down <= o["t_m"] + 600
        if sep == "b":
            fm = True if fm is None else fm
        if o["t_hi"] is not None:
            fx = o["t_hi"] - 300 <= t_down <= o["t_hi"] + 600
    o["fits_mean"], o["fits_max"] = fm, fx
    # G1-H: the hot hold
    hi0 = next((x[3] for x, _ in tel if x[0] >= t0 - 300 and x[3] is not None), None)
    best = None
    for i, (x, _) in enumerate(after):
        if x[5] != 800 or x[3] is None:
            continue
        nxt = [y for y, _ in after[i:] if y[0] <= x[0] + 1000]
        if nxt and nxt[-1][0] >= x[0] + 900 and all(y[5] == 800 for y in nxt):
            if hi0 is not None and x[3] - hi0 >= 2:
                v = x[3] - thr
                best = v if best is None else max(best, v)
    o["g1h_max_over_thr"] = best
    # DEV-3: a 600 MHz sample between the trip and the planned stop
    if t_down is not None and stop_ms is not None:
        o["saw600_before_stop"] = any(x[5] == 600 for x, _ in after if t_down <= x[0] <= stop_ms)
    # power windows
    pre = [x[4] for x in F if t0 - 2000 <= x[0] < t0 and x[4] is not None]
    o["W_idle"] = median(pre)
    if t_up is not None:
        o["W_800"] = median([x[4] for x in F if t_up + 300 <= x[0] <= t_up + 2300 and x[4] is not None])
    else:
        o["W_800"] = None
    o["P_up_W"] = (o["W_800"] - o["W_idle"]) if o["W_800"] is not None and o["W_idle"] is not None else None
    # C1m
    if target is not None:
        o["target"] = target
        tc = first(lambda x, s: x[1] is not None and x[1] >= target)
        o["t_c_s"] = round((tc - t0) / 1000.0, 3) if tc is not None and tc <= t_end + 200 else None
        o["censored_c"] = o["t_c_s"] is None
        o["off600"] = sum(1 for x, _ in after if x[0] <= t_end and x[5] is not None and x[5] != 600)
        if o["off600"]:
            o["void"].append("C1m: %d samples off 600 MHz" % o["off600"])
        o["W_load"] = median([x[4] for x in F if t0 + 1000 <= x[0] <= (tc if tc is not None else t_end) and x[4] is not None])
    return o


if __name__ == "__main__":
    a = sys.argv[1:]
    kw = {}
    if "--target" in a:
        kw["target"] = int(a[a.index("--target") + 1])
    if "--K" in a:
        kw["K"] = int(a[a.index("--K") + 1])
    print(json.dumps(runobs(a[0], a[1], **kw)))
