#!/usr/bin/env python3
"""Shared reduction core for the V3-ABL-A, V3-ABL-B and V3-X5 blocks (tools/claims-v3/{abla,ablb,x5}).

One run = one host process = one configuration in one block. Its numbers come from the session directory the block
wrote (telemetry.jsonl[.gz], runs.jsonl, starts.jsonl, ends.jsonl) with the windows of
tools/ettelem/analyze_ablation.py:
  t0, t1      first launch start, last launch end (the calibration launch included, as analyze_ablation.py)
  p_before    mean board power over [t0-2.0, t0-0.3] s
  p_early     mean board power over [t0+1, t0+3] s; t_early the mean minion-shire temperature there
  p80         p_early - leak * (t_early - launch_temp)           (analyze_ablation.py's p80)
  dyn         p80 - p_before                                      (analyze_ablation.py's "dyn"; the V3-ABL-B metric)
  switching   the same with p_early after the pre-registered dropout rule: power samples more than 2 W below the
              window median in seconds 1-3 are dropped, the number dropped is reported (V3-ABL-A and V3-X5 metric)
  mean_dyn    p_mean - p_before, p_mean over [t0+0.3, t1]         (the robustness metric of V3-ABL-A)
  per_s       work per second as analyze_ablation.py (MAC/s for fma, instructions/s for spin); layers/s for gemv
              as sum(iters) / (t1 - t0) from runs.jsonl (analyze_ablation.py leaves gemv work empty)
A run is KEPT when every launch printed ok, it has at least one timed launch (launch >= 0), the telemetry covers
both windows, and every mhz.minion sample in [t0-2.0, t1] (all samples its metrics read) is 600. This registered
rule decides the REGISTERED outcome, over aifoundry2 and aifoundry3 (CARDS), exactly as before the four-card campaign.

Four cards (25 Sep 2026: aifoundry1's two cards joined; README "Four cards"): a run is also judged by the BUSY rule
(kept_busy): the same conditions, but the clock test covers only the samples the busy metrics read, [t0+0.3, t1]
(p_mean's window, which holds p_early's). The idle bracket's clock is recorded instead of tested (idle_state,
idle_mhz_min/max, idle_mv), because aifoundry1 card 0's firmware idles at 300 MHz / 398 mV between kernels, which
the registered rule would count against every burst. The ALL-CARDS outcome of every item uses the busy rule on every
card (all_cards_block); aifoundry1's cards take aifoundry2's reduction parameters (params_card). Card 0 can also idle at
600 MHz after a launch, so its brackets may be in different states from run to run: a card whose kept runs idled in
more than one state is flagged (idle_mixed_on), and the item on each state's runs alone (state_view) is reported
beside the outcome as by_idle_state, never deciding it.
"""
import collections
import glob
import gzip
import json
import math
import os
import re

import numpy as np

CARDS = ("aifoundry2", "aifoundry3")          # the registered cards: the registered outcome is over these two
CAMPAIGN = ("aifoundry2", "aifoundry3", "aifoundry1-c0", "aifoundry1-c1")   # the four-card campaign (all_cards)
PINNED = ("aifoundry3",)                       # clock pinned at 600 MHz by a boot service; every other card is governor-free
SHORT = {"aifoundry2": "a2", "aifoundry3": "a3", "aifoundry1-c0": "a1c0", "aifoundry1-c1": "a1c1"}
BUSY_S = 0.3                                   # the busy window starts where p_mean's does: [t0 + 0.3 s, t1]
MAC_PER_OP = {"fp32": 4096, "fp16": 8192, "int8": 16384}
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


# ------------------------------------------------------------------------------------------------ loading
def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return []
    out = []
    op = gzip.open(path, "rt") if path.endswith(".gz") else open(path)
    with op as f:
        for line in f:
            try:
                out.append(json.loads(line))
            except Exception:
                pass  # a line cut when a process stopped
    return out


def load_json(path):
    try:
        return json.load(open(path))
    except Exception:
        return None


class Session:
    """The telemetry and launches of one session directory (one sampler run)."""

    def __init__(self, d):
        self.dir = d
        tel = [s for s in load_jsonl(os.path.join(d, "telemetry.jsonl")) if "t_ms" in s and "board_w" in s]
        tel.sort(key=lambda s: s["t_ms"])
        self.n_samples = len(tel)
        self.t = np.array([s["t_ms"] for s in tel], dtype=float) / 1000.0
        self.P = np.array([float(s["board_w"]) for s in tel])
        self.T = np.array([float(s.get("temp_c", {}).get("minshire", [np.nan])[0]) for s in tel])
        self.mhz = np.array([float(s.get("mhz", {}).get("minion", np.nan)) for s in tel])
        self.mv = np.array([float(s.get("die_mv", {}).get("minion", np.nan)) for s in tel])
        self.launches = collections.OrderedDict()
        for r in load_jsonl(os.path.join(d, "runs.jsonl")):
            if r.get("block", -9) >= 0 and "config" in r:
                self.launches.setdefault((r["block"], r["config"]), []).append(r)
        self.starts = {(s.get("block"), s.get("config")): s for s in load_jsonl(os.path.join(d, "starts.jsonl"))}
        self.ends = {(s.get("block"), s.get("config")): s for s in load_jsonl(os.path.join(d, "ends.jsonl"))}
        self.order = []
        for f in sorted(glob.glob(os.path.join(d, "order.*"))):
            b = f.rsplit(".", 1)[-1]
            if b.isdigit():
                self.order += [(int(b), ln.split()[0]) for ln in open(f) if ln.strip()]
        self.session = load_json(os.path.join(d, "session.json")) or {}

    def sel(self, lo, hi):
        return (self.t >= lo) & (self.t <= hi)


def run_metrics(S, key, leak, launch):
    """Metrics of the run `key` = (block, config) of Session S; see the module docstring."""
    block, cfg = key
    ls = S.launches.get(key, [])
    st = S.starts.get(key, {})
    en = S.ends.get(key, {})
    r = {"block": block, "config": cfg, "launches": len(ls), "rc": en.get("rc"), "start_temp": st.get("start_temp"),
         "approach_ms": st.get("approach_ms"), "heats": st.get("heats"), "preheat_reached": st.get("preheat_reached"),
         "seed": st.get("seed"), "waited_ms": st.get("waited_ms"), "kept": False, "reason": "",
         "kept_busy": False, "reason_busy": "", "idle_mhz_start": st.get("idle_mhz"), "idle_mv_start": st.get("idle_mv")}
    if not ls:
        r["reason"] = r["reason_busy"] = "no launch output" + (f" (host exit {en.get('rc')})" if en else "")
        return r
    r0 = ls[0]
    timed = [x for x in ls if x.get("launch", 0) >= 0]
    t0, t1 = ls[0]["t_start_ms"] / 1000.0, ls[-1]["t_end_ms"] / 1000.0
    dur = t1 - t0
    r.update({"test": r0.get("test"), "type": r0.get("type"), "values": r0.get("values"), "minions": r0.get("minions"),
              "b_stream": r0.get("b_stream"), "t0": t0, "t1": t1, "dur": dur,
              "all_ok": all(bool(x.get("ok")) for x in ls), "timed_launches": len(timed),
              "results": sorted({str(x.get("result")) for x in ls if "result" in x})})
    if r0.get("test") == "fma":
        r.update({"nnz_a": r0.get("nnz_a"), "a_elems": r0.get("a_elems"), "row_mask": r0.get("row_mask", "0xffff"),
                  "cycles_timed": [x["cycles_per_op"] for x in timed],
                  "cycles_calib": [x["cycles_per_op"] for x in ls if x.get("launch", 0) < 0],
                  "cycles_per_op": float(np.mean([x["cycles_per_op"] for x in (ls[1:] if len(ls) > 1 else ls)]))})
    if S.n_samples == 0:
        r["reason"] = r["reason_busy"] = "no telemetry"
        return r
    early, before, run_w = S.sel(t0 + 1.0, t0 + 3.0), S.sel(t0 - 2.0, t0 - 0.3), S.sel(t0 + 0.3, t1)
    clock_w = S.sel(t0 - 2.0, t1)
    if early.sum() < 5 or before.sum() < 3 or run_w.sum() < 3:
        r["reason"] = r["reason_busy"] = f"telemetry gap (early {int(early.sum())}, before {int(before.sum())} samples)"
        return r
    Pe, Te = S.P[early], S.T[early]
    med = float(np.median(Pe))
    keep = Pe >= med - 2.0
    p_early, t_early = float(Pe.mean()), float(np.nanmean(Te))
    p_early_d = float(Pe[keep].mean())
    p_before = float(S.P[before].mean())
    p80 = p_early - leak * (t_early - launch)
    p80_d = p_early_d - leak * (t_early - launch)
    mz = S.mhz[clock_w]
    mz = mz[~np.isnan(mz)]
    bz = S.mhz[S.sel(t0 + BUSY_S, t1)]          # the busy samples (four-card rule)
    bz = bz[~np.isnan(bz)]
    iz = S.mhz[before]                          # the idle bracket p_before reads: recorded, not tested
    iz = iz[~np.isnan(iz)]
    iv, bv = S.mv[before], S.mv[run_w]
    iv, bv = iv[~np.isnan(iv)], bv[~np.isnan(bv)]
    r.update({"idle_mhz_min": float(iz.min()) if len(iz) else None, "idle_mhz_max": float(iz.max()) if len(iz) else None,
              "idle_state": (f"{int(iz.min())}" if iz.min() == iz.max() else f"mixed {int(iz.min())}-{int(iz.max())}") if len(iz) else None,
              "idle_mv": float(iv.mean()) if len(iv) else None, "busy_mv": float(bv.mean()) if len(bv) else None,
              "busy_mhz_min": float(bz.min()) if len(bz) else None, "busy_mhz_max": float(bz.max()) if len(bz) else None})
    i0 = int(np.searchsorted(S.t, t0)) - 1
    r.update({"p_before": p_before, "p_early": p_early, "p_early_d": p_early_d, "dropped_samples": int((~keep).sum()),
              "t_early": t_early, "p80": p80, "p80_d": p80_d, "dyn": p80 - p_before, "switching": p80_d - p_before,
              "p_mean": float(S.P[run_w].mean()), "mean_dyn": float(S.P[run_w].mean()) - p_before,
              "t_launch": float(S.T[i0]) if i0 >= 0 else None,
              "t_end": float(np.nanmean(S.T[S.sel(t1 - 0.5, t1)])) if S.sel(t1 - 0.5, t1).any() else None,
              "mhz_min": float(mz.min()) if len(mz) else None, "mhz_max": float(mz.max()) if len(mz) else None})
    # work rate (analyze_ablation.py), and layers/s for gemv
    if r0.get("test") == "fma" and r0.get("type") in MAC_PER_OP:
        r["per_s"] = sum(x["iters"] for x in ls) * r0["minions"] * MAC_PER_OP[r0["type"]] / dur
        r["unit"] = "MAC"
    elif r0.get("test") == "spin":
        r["per_s"] = sum(x["iters"] for x in ls) * 5 * r0["minions"] / dur
        r["unit"] = "instruction"
    elif r0.get("test") == "gemv":
        r["per_s"] = sum(x["iters"] for x in ls) / dur
        r["unit"] = "layer"
        r["cycles_per_layer"] = float(np.mean([x.get("cycles_per_layer_mean", 0) for x in timed])) if timed else None
    # within-run drift of power against temperature (runs that heat the die by >= 3 C), as analyze_horace_strict.py
    g = S.sel(t0 + 1.0, t1 - 0.2)
    if g.sum() >= 10 and np.nanmax(S.T[g]) - np.nanmin(S.T[g]) >= 3:
        r["drift_w_per_c"] = float(np.polyfit(S.T[g], S.P[g], 1)[0])
    # keep / drop (registered rule: kept; four-card busy rule: kept_busy)
    if not r["all_ok"]:
        r["reason"] = r["reason_busy"] = "a launch did not print ok"
    elif not timed:
        r["reason"] = r["reason_busy"] = "no timed launch"
    else:
        if len(mz) == 0:
            r["reason"] = "no clock samples"
        elif mz.min() != 600 or mz.max() != 600:
            r["reason"] = f"mhz.minion {int(mz.min())}-{int(mz.max())} != 600"
        else:
            r["kept"] = True
        if len(bz) == 0:
            r["reason_busy"] = "no clock samples in the burst"
        elif bz.min() != 600 or bz.max() != 600:
            r["reason_busy"] = f"busy mhz.minion {int(bz.min())}-{int(bz.max())} != 600"
        else:
            r["kept_busy"] = True
    return r


def session_runs(d, leak, launch, extra=None):
    """All runs of one session directory (the order file's list, so a run with no output still appears)."""
    S = Session(d)
    keys = list(S.order) or list(S.launches.keys())
    for k in S.launches:
        if k not in keys:
            keys.append(k)
    out = []
    for k in keys:
        r = run_metrics(S, k, leak, launch)
        if extra:
            r.update(extra)
        out.append(r)
    return out


# ------------------------------------------------------------------------------------------------ cards
def short(card):
    return SHORT.get(card, card)


def params_card(card):
    """The registered card whose reduction parameters (leak, launch temperature, targets) a card takes: aifoundry3's
    for the pinned card, aifoundry2's for every governor-free card (aifoundry1's two cards: same TDP 65 W and 65 C
    threshold, heated to the same launch temperatures; their own leakage slopes are unmeasured)."""
    return "aifoundry3" if card in PINNED else "aifoundry2"


def cards_present(data, exp):
    """Card directories under `data` that hold an `exp` directory (any name: campaign cards first)."""
    try:
        found = sorted(d for d in os.listdir(data) if os.path.isdir(os.path.join(data, d, exp)))
    except OSError:
        found = []
    return [c for c in CAMPAIGN if c in found] + [c for c in found if c not in CAMPAIGN]


def card_list(data, exp, expect=CAMPAIGN):
    """The cards an all-cards outcome covers: the expected ones (present or not) and any other card with data."""
    return list(expect) + [c for c in cards_present(data, exp) if c not in expect]


def busy_view(runs):
    """The runs with `kept` / `reason` taken from the four-card busy rule (copies; the originals are unchanged)."""
    out = []
    for r in runs:
        q = dict(r)
        q["kept"], q["reason"] = r.get("kept_busy", False), r.get("reason_busy", r.get("reason", ""))
        out.append(q)
    return out


def state_view(runs, state):
    """The busy view restricted to the runs whose idle bracket was in `state` ("600", "300", "mixed 300-600", ...):
    for a card whose kept runs idled in more than one state (aifoundry1-c0: after a launch it can stay at 600 MHz for a
    while, after a long idle it drops to 300 MHz), so that a difference between two configurations is taken between
    runs that subtract the same idle state. Reported beside the all-cards outcome, never deciding it."""
    out = []
    for q in busy_view(runs):
        if q["kept"] and (q.get("idle_state") or "unknown") != state:
            q["kept"], q["reason"] = False, f"idle state {q.get('idle_state')} (view: {state} only)"
        out.append(q)
    return out


def mixed_states(idle_sum):
    """The idle states of a card's busy-rule-kept runs when there is more than one, else []."""
    st = sorted((idle_sum or {}).get("idle_states_mhz", {}))
    return st if len(st) > 1 else []


def pass_dirs(data, card, exp):
    """[(pass, dir)] of passes whose block.json says ok, and the list of passes skipped (not ok / no block.json)."""
    ok, skipped = [], []
    for d in sorted(glob.glob(os.path.join(data, card, exp, "p*"))):
        m = re.fullmatch(r"p(\d+)", os.path.basename(d))
        if not m or not os.path.isdir(d):
            continue
        bj = load_json(os.path.join(d, "block.json"))
        if bj and bj.get("status") == "ok":
            ok.append((int(m.group(1)), d))
        else:
            skipped.append({"pass": int(m.group(1)), "status": (bj or {}).get("status", "no block.json"), "note": (bj or {}).get("note")})
    ok.sort()
    return ok, skipped


# ------------------------------------------------------------------------------------------------ selection
def pick(runs, config, registered, value="switching"):
    """Kept runs of `config`: those of the registered passes, then (to replace dropped or missing ones, as the plan's
    'dropped and re-run') runs of later passes, up to the registered count. Returns the list of run dicts."""
    reg = [r for r in runs if r["config"] == config and r["kept"] and r["pass"] in registered and r.get(value) is not None]
    ext = sorted([r for r in runs if r["config"] == config and r["kept"] and r["pass"] not in registered and r.get(value) is not None],
                 key=lambda r: r["pass"])
    reg.sort(key=lambda r: r["pass"])
    return (reg + ext)[:len(registered)] if len(reg) < len(registered) else reg


def pick_blocks(runs, configs, registered, value="dyn"):
    """Passes in which every one of `configs` has a kept run (paired, within-block analyses): registered passes first,
    then later passes as replacements, up to the registered count. Returns [{config: run}] per pass."""
    by = collections.defaultdict(dict)
    for r in runs:
        if r["config"] in configs and r["kept"] and r.get(value) is not None:
            by[r["pass"]][r["config"]] = r
    full = [p for p in sorted(by) if all(c in by[p] for c in configs)]
    reg = [p for p in full if p in registered]
    ext = [p for p in full if p not in registered]
    use = (reg + ext)[:len(registered)] if len(reg) < len(registered) else reg
    return [by[p] for p in use]


# ------------------------------------------------------------------------------------------------ statistics
def _betacf(a, b, x, itmax=300, eps=3e-14):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d; d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d; d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        de = d * c; h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def _betainc(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1 - x) / b


def t_sf(t, df):
    p = 0.5 * _betainc(df / 2.0, 0.5, df / (df + t * t))
    return p if t >= 0 else 1.0 - p


def t_ppf(q, df):
    """The t with P(T <= t) = q (Student t, df may be fractional); no scipy on the lab hosts."""
    lo, hi = -1e7, 1e7
    for _ in range(400):
        mid = (lo + hi) / 2
        if 1.0 - t_sf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def tcrit(alpha, df):
    """Two-sided critical value."""
    return t_ppf(1.0 - alpha / 2.0, df)


def one_sample(x, alpha, mu=0.0):
    x = [float(v) for v in x]
    n = len(x)
    out = {"n": n, "values": x}
    if n == 0:
        return out
    m = float(np.mean(x))
    out["mean"] = m
    out["point"] = m - mu
    if n < 2:
        return out
    sd = float(np.std(x, ddof=1)); se = sd / math.sqrt(n); tc = tcrit(alpha, n - 1)
    out.update({"sd": sd, "se": se, "df": n - 1, "t_crit": tc, "lo": m - mu - tc * se, "hi": m - mu + tc * se, "alpha": alpha})
    return out


def welch(x, y, alpha):
    """Welch interval of mean(x) - mean(y)."""
    x = [float(v) for v in x]; y = [float(v) for v in y]
    out = {"n_x": len(x), "n_y": len(y), "values_x": x, "values_y": y}
    if not x or not y:
        return out
    mx, my = float(np.mean(x)), float(np.mean(y))
    out.update({"mean_x": mx, "mean_y": my, "point": mx - my})
    if len(x) < 2 or len(y) < 2:
        return out
    vx, vy = float(np.var(x, ddof=1)) / len(x), float(np.var(y, ddof=1)) / len(y)
    se = math.sqrt(vx + vy)
    if se == 0:
        df = len(x) + len(y) - 2
    else:
        df = (vx + vy) ** 2 / ((vx ** 2 / (len(x) - 1) if vx else 0) + (vy ** 2 / (len(y) - 1) if vy else 0) or 1e-300)
    tc = tcrit(alpha, df)
    out.update({"se": se, "df": df, "t_crit": tc, "lo": mx - my - tc * se, "hi": mx - my + tc * se, "alpha": alpha})
    return out


def ratio(x, y, alpha, scale=1.0):
    """Interval of scale * mean(x) / mean(y): Welch on logs when every value is positive, else the delta method."""
    x = [float(v) for v in x]; y = [float(v) for v in y]
    out = {"n_x": len(x), "n_y": len(y), "values_x": x, "values_y": y}
    if not x or not y or np.mean(y) == 0:
        return out
    out["point"] = scale * float(np.mean(x)) / float(np.mean(y))
    if len(x) < 2 or len(y) < 2:
        return out
    if min(x) > 0 and min(y) > 0:
        w = welch([math.log(v) for v in x], [math.log(v) for v in y], alpha)
        out.update({"method": "welch on logs", "df": w["df"], "t_crit": w["t_crit"],
                    "point": scale * math.exp(w["point"]), "lo": scale * math.exp(w["lo"]), "hi": scale * math.exp(w["hi"]),
                    "log_lo": w["lo"], "log_hi": w["hi"], "alpha": alpha})
    else:
        mx, my = float(np.mean(x)), float(np.mean(y))
        vx, vy = float(np.var(x, ddof=1)) / len(x) / mx ** 2 if mx else 0.0, float(np.var(y, ddof=1)) / len(y) / my ** 2
        rr = scale * mx / my
        se = abs(rr) * math.sqrt(vx + vy)
        df = (vx + vy) ** 2 / ((vx ** 2 / (len(x) - 1)) + (vy ** 2 / (len(y) - 1)) or 1e-300) if (vx + vy) else len(x) + len(y) - 2
        tc = tcrit(alpha, df)
        out.update({"method": "delta", "df": df, "t_crit": tc, "point": rr, "lo": rr - tc * se, "hi": rr + tc * se, "alpha": alpha})
    return out


def linfit(xs, ys, alpha):
    """Least-squares line y = b0 + b1 x with t intervals (df n-2) and the rms residual."""
    xs = np.asarray(xs, float); ys = np.asarray(ys, float)
    n = len(xs)
    out = {"n": n}
    if n < 2 or np.ptp(xs) == 0:
        return out
    X = np.column_stack([np.ones(n), xs])
    b, *_ = np.linalg.lstsq(X, ys, rcond=None)
    res = ys - X @ b
    out.update({"intercept": float(b[0]), "slope": float(b[1]), "rms": float(math.sqrt(np.mean(res ** 2)))})
    if n > 2:
        s2 = float(res @ res) / (n - 2)
        cov = s2 * np.linalg.inv(X.T @ X)
        tc = tcrit(alpha, n - 2)
        out.update({"df": n - 2, "t_crit": tc, "intercept_lo": float(b[0] - tc * math.sqrt(cov[0, 0])),
                    "intercept_hi": float(b[0] + tc * math.sqrt(cov[0, 0])),
                    "slope_lo": float(b[1] - tc * math.sqrt(cov[1, 1])), "slope_hi": float(b[1] + tc * math.sqrt(cov[1, 1]))})
    return out


# ------------------------------------------------------------------------------------------------ decisions
def difference_ok(ci, pred=None, tol=None, band=None, sign=+1):
    """'Difference' rule: the interval excludes 0 with the predicted sign AND the point estimate is inside the
    tolerance (pred +- tol, or band [lo, hi], or '> band[0]' when band[1] is None)."""
    if "lo" not in ci:
        return None
    excl = ci["lo"] > 0 if sign > 0 else ci["hi"] < 0
    p = ci["point"]
    if band is not None:
        inside = p > band[0] if band[1] is None else band[0] <= p <= band[1]
    elif pred is not None:
        inside = abs(p - pred) <= tol
    else:
        inside = True
    return bool(excl and inside)


def equivalence_ok(ci, tol):
    """'Equivalence' rule: the interval lies inside +-tol."""
    if "lo" not in ci:
        return None
    return bool(-tol <= ci["lo"] and ci["hi"] <= tol)


def card_outcome(results):
    """A card's outcome from its sub-test results (True / False / None = not enough kept repeats)."""
    if any(v is None for v in results):
        return "INSUFFICIENT"
    return "PASS" if all(results) else "FAIL"


def combine(per_card):
    """Item outcome from the two cards' outcomes: PASS on both; FAIL on both; CARD-DIFFERENT when it holds on one and
    fails on the other; INSUFFICIENT when either card lacks the kept repeats (the claim stays as it is)."""
    oc = [per_card.get(c, {}).get("outcome", "INSUFFICIENT") for c in CARDS]
    if "INSUFFICIENT" in oc:
        return "INSUFFICIENT"
    if all(o == "PASS" for o in oc):
        return "PASS"
    if all(o == "FAIL" for o in oc):
        return "FAIL"
    return "CARD-DIFFERENT"


# ------------------------------------------------------------------------------------------------ all cards
TESTED = ("PASS", "FAIL", "INSUFFICIENT")
BUSY_RULE = ("busy rule on every card: a run is kept when every launch printed ok, it has a timed launch, the telemetry "
             "covers its windows and every mhz.minion sample in [t0+0.3 s, t1] is 600; the idle bracket [t0-2, t0-0.3 s] "
             "is not tested, its clock is recorded")
IDLE_EFFECT = {
    "difference": "the item compares over-idle values of configurations launched at the same temperature on the same card, "
                  "so the idle state enters both sides and cancels (up to the scatter of p_before)",
    "absolute": "the item uses over-idle values themselves: on a card whose idle bracket sits below the burst's operating "
                "point they include the step between idling at 600 MHz and idling at the card's idle clock, so they are "
                "not comparable with the other cards' values",
    "temperature": "the item compares over-idle values at two launch temperatures: with the idle bracket at a lower "
                   "operating point than the burst, hot - cool also carries (busy leakage slope - idle leakage slope) x the "
                   "temperature step, so it does not separate card from temperature on that card",
}


def combine_all(status):
    """All-cards outcome from per-card outcomes, over the cards on which the item is tested (REPORTED / N/A cards are
    left out): PASS on every card, FAIL on every card, CARD-DIFFERENT on some; INSUFFICIENT when a card lacks the
    kept repeats (or has no data)."""
    t = [o for o in status.values() if o in TESTED]
    if not t:
        return "N/A"
    if "INSUFFICIENT" in t:
        return "INSUFFICIENT"
    if all(o == "PASS" for o in t):
        return "PASS"
    if all(o == "FAIL" for o in t):
        return "FAIL"
    return "CARD-DIFFERENT"


def idle_summary(runs):
    """A card's idle operating point in an experiment: the idle-bracket clocks of its busy-rule-kept runs, and the
    idle bracket's board power (p_before, at the launch temperature) per idle state: the firmware releases idle at
    different powers even at 600 MHz (26 W on 1.4.1, 33-35 W on 1.2.0, 32 W on 1.3.1; aifoundry1 clock test, 25 Sep)."""
    ks = [r for r in runs if r.get("kept_busy")]
    states = collections.Counter(r.get("idle_state") or "unknown" for r in ks)
    mv = [r["idle_mv"] for r in ks if r.get("idle_mv") is not None]
    bmv = [r["busy_mv"] for r in ks if r.get("busy_mv") is not None]
    off = sum(n for st, n in states.items() if st != "600")
    pw = collections.defaultdict(list)
    for r in ks:
        if r.get("p_before") is not None:
            pw[r.get("idle_state") or "unknown"].append(r["p_before"])
    allw = [w for ws in pw.values() for w in ws]
    return {"kept_runs": len(ks), "idle_states_mhz": dict(states), "idle_mhz": states.most_common(1)[0][0] if states else None,
            "idle_mv": round(float(np.mean(mv)), 1) if mv else None, "busy_mhz": 600,
            "busy_mv": round(float(np.mean(bmv)), 1) if bmv else None, "runs_idle_off_600": off, "differs": off > 0,
            "idle_w": round(float(np.mean(allw)), 2) if allw else None,
            "idle_w_by_state": {st: round(float(np.mean(ws)), 2) for st, ws in pw.items()}}


def all_cards_block(status, present, expect=CAMPAIGN, registered=None, idle=None, idle_effect=None, note=None,
                    by_state=None):
    """The `all_cards` field of an item. status: {card: PASS/FAIL/INSUFFICIENT/REPORTED/N/A} under the busy rule;
    registered: {card: registered outcome} of aifoundry2/aifoundry3, to flag where the busy rule changes a card's
    outcome; idle: {card: idle_summary} for items about energy over idle, with idle_effect a key of IDLE_EFFECT;
    by_state: {card: {idle state: outcome on that state's runs alone}} for cards whose runs idled in more than one
    state (state_view; reported, not deciding)."""
    d = {"outcome": combine_all(status), "per_card": dict(status), "rule": BUSY_RULE,
         "holds_on": [c for c, o in status.items() if o == "PASS"], "fails_on": [c for c, o in status.items() if o == "FAIL"],
         "insufficient_on": [c for c, o in status.items() if o == "INSUFFICIENT"],
         "reported_on": [c for c, o in status.items() if o not in TESTED],
         "cards_missing": [c for c in expect if c not in present]}
    if registered:
        d["registered_cards_busy_vs_registered_rule"] = {c: {"busy_rule": status.get(c), "registered_rule": o,
                                                             "same": status.get(c) == o} for c, o in registered.items()}
    if idle is not None:
        d["idle_clock"] = {c: idle[c] for c in status if c in idle}
        diff = [c for c in status if c in idle and idle[c].get("differs")]
        d["idle_differs_on"] = diff
        if diff:
            d["idle_note"] = ("; ".join(f"{c}: {idle[c]['runs_idle_off_600']} of {idle[c]['kept_runs']} kept runs had the idle "
                                        f"bracket off 600 MHz ({idle[c]['idle_states_mhz']}, {idle[c]['idle_mv']} mV idle vs "
                                        f"{idle[c]['busy_mv']} mV busy; idle W by state {idle[c].get('idle_w_by_state')})" for c in diff)
                              + (f". {IDLE_EFFECT[idle_effect][0].upper()}{IDLE_EFFECT[idle_effect][1:]}" if idle_effect else ""))
            mixed = [c for c in diff if mixed_states(idle[c])]
            if mixed:
                d["idle_mixed_on"] = mixed
                d["idle_note"] += (". MIXED idle states on " + ", ".join(mixed) + ": runs of one configuration or of two "
                                   "configurations idled in different states, so a difference between them carries the step "
                                   "between the states' idle powers and does NOT cancel; the outcome is computed as stated, and "
                                   "by_idle_state gives the item on each state's runs alone (reported, not deciding)")
    if by_state:
        d["by_idle_state"] = by_state
    if note:
        d["note"] = note
    return d


def reading_all(ac):
    """One line for the page: the all-cards outcome and each card's."""
    return (f"all cards: {ac['outcome']} (" + ", ".join(f"{short(c)} {o}" for c, o in ac["per_card"].items()) + ")"
            + (f"; missing {', '.join(ac['cards_missing'])}" if ac["cards_missing"] else "")
            + (f"; idle state differs on {', '.join(short(c) for c in ac['idle_differs_on'])}" if ac.get("idle_differs_on") else "")
            + (f" (mixed on {', '.join(short(c) for c in ac['idle_mixed_on'])}"
               + ("; by idle state " + "; ".join(f"{short(c)} {v}" for c, v in ac["by_idle_state"].items()) if ac.get("by_idle_state") else "")
               + ")" if ac.get("idle_mixed_on") else ""))


def jsonable(v):
    """numpy scalars, tuples and sets -> plain JSON types (recursively)."""
    if isinstance(v, dict):
        return {str(a): jsonable(b) for a, b in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [jsonable(b) for b in v]
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.floating):
        v = float(v)
    if isinstance(v, float) and not math.isfinite(v):
        return None
    return v


def rnd(v, k=3):
    if isinstance(v, (np.floating, np.integer, np.bool_)):
        v = jsonable(v)
    if isinstance(v, float):
        if not math.isfinite(v):
            return None
        return float(f"{v:.3g}") if 0 < abs(v) < 0.01 else round(v, k)
    if isinstance(v, dict):
        return {a: rnd(b, k) for a, b in v.items()}
    if isinstance(v, (list, tuple)):
        return [rnd(b, k) for b in v]
    return v


def fmt_ci(ci, unit="W", k=2):
    if "lo" not in ci:
        return f"n={ci.get('n', ci.get('n_x'))}" + (f", point {ci['point']:.{k}f} {unit}" if "point" in ci else "")
    return f"{ci['point']:+.{k}f} {unit} [{ci['lo']:+.{k}f}, {ci['hi']:+.{k}f}]"
