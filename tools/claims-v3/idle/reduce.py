#!/usr/bin/env python3
"""V3-IDLE reducer: the pre-registered items IDLE-0, a, b, c, d, e, f, k, L of PLAN3 §2 "V3-IDLE" (plan3.json
experiments[V3-IDLE].predictions and components_detail), on the heat/cool cycles written by block.sh.

    reduce.py --data <dir with one directory per card, each laid out like DATA_ROOT> --out verdicts.json
    reduce.py --check-pass <pass dir>        (used by block.sh at the end of a block: stdlib only, prints a note)

Layout read: <data>/<card>/idle/p<N>/{telemetry.jsonl.gz, launches.jsonl, marks.jsonl, cycle.json, block.json}, for
every <card> directory present (aifoundry2, aifoundry3, aifoundry1-c0, aifoundry1-c1, ...).
Passes 1-9 are short cycles (900 s of cooling), 11-19 IDLE-LONG cycles (5400 s aifoundry2 and aifoundry1's cards,
2700 s aifoundry3). A pass is kept when block.json says ok, it is not a dry run, and marks.jsonl has cool_start and
cool_end.

Unit of replication: the heat/cool cycle. Items 0, a-f and k use every kept cycle, short or long, each with its
first 900 s of cooling only (a long cycle is a short cycle whose cooling was extended, PLAN3 "IDLE-LONG variant:
extend each cycle's cooling"); item L uses the long cycles only, with their whole cooling.

Sample rules (as registered):
  rule A (items 0, a-f; PLAN3 V3-IDLE "Sampler"/"Reduction", EXP-EM1 "test"): samples inside the cycle's cooling
      window, none from 1 s before to 6 s after any launch, aifoundry2 samples with mhz.minion != 600 dropped;
      whole-degree bins of temp_c.minshire[0] with n >= 20 per cycle.
  rule K (item k; EXP-dvfs-4): the 10 Hz grid of flip_thermal_model.py, samples >= 20 s after the last burst,
      inside the first 900 s of cooling, mhz.minion == 600; the idle fit of flip_thermal_model.py step 2a
      (3 s smoothing of the reading, NNLS with a free constant, T_L on its grid) per cycle.
  rule F (item L; horace-lowpower-X4): flip_thermal_model.py step 2a exactly: no launch within 4.5 s, the first
      20 s of the session skipped, mhz.minion == 600, 3 s smoothing; the pass is the session.
99% intervals: two-sided Student t on the cycle-level values (df = cycles - 1). A test "inside [lo, hi]" means the
whole interval lies inside. Fewer than 3 kept cycles on a card for an item -> INSUFFICIENT.

Four cards (amendment A2, written before any data of aifoundry1's cards):
  - `outcome` is the REGISTERED outcome, computed exactly as before from aifoundry2 and aifoundry3 only.
  - Every IDLE item's band is specific to aifoundry2 or aifoundry3 (a value given for one card), so aifoundry1's
    cards are REPORTED, not tested: per_card has their values, computed exactly as for the registered card, with
    `tested: false` and, for information only, whether the registered card's band would hold.
  - `all_cards` is the outcome over every TESTED card with enough kept repeats (PASS on every card, CARD-DIFFERENT
    on some, FAIL on none, INSUFFICIENT if a tested card lacks repeats); for these items the tested cards are the
    registered ones, so it equals `outcome`, and it lists the reported cards.
  - The idle clock. aifoundry2's registered rule keeps 600 MHz samples; aifoundry3 is pinned (off-600 counted, not
    dropped). On aifoundry1's governor-free cards rules A, K and F keep the samples at the card's idle clock, other
    clocks dropped: the expected clock is 600 MHz on both. aifoundry1-c1 (firmware 1.2.0, "managed_power") idles at
    600 MHz / 499 mV like aifoundry2. aifoundry1-c0 (firmware 1.4.1) rests in "low_power" at 300 MHz / 398 mV, but in
    the 25 Sep clock test it moved to 600 MHz during its first launch and stayed there idle afterwards, so its cooling
    after the heater is expected at 600 MHz. If fewer than half of a card's cooling samples (rule-A window, pooled
    over its kept cycles) are at the expected clock, its most common cooling clock is used instead (for example 300 MHz
    if c0 falls back into low_power), and the idle-clock note and reading_all_cards say so. Every pass records its
    cooling clock histogram and its idle state before heating and at the end of the cooling, and each item carries a
    note of each card's idle clock and firmware.
"""
import argparse
import bisect
import collections
import gzip
import json
import math
import os
import re
import sys
import time
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import campaign  # noqa: E402  (the campaign's cards: amendments A2 and A4)

A2, A3 = "aifoundry2", "aifoundry3"
C0, C1 = "aifoundry1-c0", "aifoundry1-c1"
CARDS = (A2, A3)                  # the registered cards (PLAN3)
KNOWN = (A2, A3, C0, C1)          # the four-card campaign (amendment A2)
LISTED = tuple(c for c in campaign.CAMPAIGN if c not in (A2, A3))   # always listed, data or not (A4: not card 0)
PINNED = {A3}                     # clock pinned at 600 MHz by a boot service: off-600 samples counted, not dropped
# the idle clock rules A/K/F keep on each governor-free card (aifoundry2: the registered 600 MHz; amendment A2 for
# aifoundry1's cards, the expected clock after the heater: c1 idles at 600 MHz / 499 mV "managed_power"; c0 rests at
# 300 MHz / 398 mV "low_power" but after a launch stayed idle at 600 MHz / ~510 mV (25 Sep clock test); the modal
# fallback below covers c0 returning to 300 MHz)
IDLE_MHZ = {A2: 600, A3: 600, C0: 600, C1: 600}
DEFAULT_IDLE_MHZ = 600
# the firmware each card ran on 25 Sep (validate3/lessons.md): it sets the idle state, so it goes into the clock note
FIRMWARE = {A2: "1.3.1", A3: "1.3.1", C0: "1.4.1", C1: "1.2.0"}
IDLE_SHARE_MIN = 0.5              # below this share at the expected clock, a non-registered card uses its modal clock
# ---- registered constants (the published values the predictions refer to)
# the idle law: docs/reports/data/2026-09-21-horace-aifoundry2/model.json "power" (P_fix, A_leak_at_80, T_L)
LAW = (12.634918235027182, 23.25676120777849, 36.0)
# the aifoundry2 SRAM idle law: docs/reports/data/2026-09-23-energy-manual/catalogue.json cards.aifoundry2.sram_leakage.fit
SRAM_LAW_A2 = (-0.3226299730631029, 2.80914818057031, 36.0)
# the 22 Sep idle split at 73 C (dvfs.json idle_check; energy-manual-18)
SPLIT_22SEP = {"minion": 11.05, "sram": 2.00, "noc": 3.64, "unsensed": 15.10}
BUSY_80 = 63.9          # the random-data matmul at 80 C (dvfs.json busy_randn_80c), as registered in IDLE-k
TL_GRID = [16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 45, 50, 60, 80]   # flip_thermal_model.py step 2a
BIN_MIN_N = 20
CYCLE_COOL_S = 900
MIN_REPEATS = 3
DT = 0.1

T995 = {1: 63.657, 2: 9.925, 3: 5.841, 4: 4.604, 5: 4.032, 6: 3.707, 7: 3.499, 8: 3.355, 9: 3.250, 10: 3.169,
        11: 3.106, 12: 3.055, 13: 3.012, 14: 2.977, 15: 2.947, 16: 2.921, 17: 2.898, 18: 2.878, 19: 2.861,
        20: 2.845, 21: 2.831, 22: 2.819, 23: 2.807, 24: 2.797, 25: 2.787, 26: 2.779, 27: 2.771, 28: 2.763,
        29: 2.756, 30: 2.750}


def t995(df):
    if df in T995:
        return T995[df]
    z = 2.5758293035489
    return z + (z ** 3 + z) / (4 * df) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * df ** 2)   # Cornish-Fisher


def law(T, p=LAW):
    return p[0] + p[1] * math.exp((T - 80.0) / p[2])


def mean(v):
    return sum(v) / len(v) if v else None


def median(v):
    v = sorted(x for x in v if x is not None)
    if not v:
        return None
    k = len(v) // 2
    return v[k] if len(v) % 2 else (v[k - 1] + v[k]) / 2.0


def ci99(vals):
    """(mean, lo, hi, n) of a 99% two-sided t interval; lo/hi None when n < 2."""
    vals = [v for v in vals if v is not None]
    n = len(vals)
    if n == 0:
        return None, None, None, 0
    m = mean(vals)
    if n < 2:
        return m, None, None, n
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (n - 1))
    h = t995(n - 1) * sd / math.sqrt(n)
    return m, m - h, m + h, n


def inside(lo, hi, band):
    return lo is not None and hi is not None and band[0] <= lo and hi <= band[1]


def rnd(x, k=4):
    if isinstance(x, float):
        return round(x, k)
    if isinstance(x, (list, tuple)):
        return [rnd(v, k) for v in x]
    if isinstance(x, dict):
        return {a: rnd(b, k) for a, b in x.items()}
    return x


def stat(vals, band=None):
    m, lo, hi, n = ci99(vals)
    out = {"per_cycle": rnd(list(vals)), "n": n, "mean": rnd(m), "ci99": [rnd(lo), rnd(hi)]}
    if band is not None:
        out["band"] = list(band)
        out["inside_band"] = bool(n >= MIN_REPEATS and inside(lo, hi, band))
    return out


def slope(xs, ys):
    """least-squares slope of y on x (unweighted); None with fewer than 2 distinct x."""
    if len(xs) < 2 or len(set(xs)) < 2:
        return None
    mx, my = mean(xs), mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def card_order(cards):
    """the four known cards first (registered ones first), then any other card directory, by name"""
    return sorted(set(cards), key=lambda c: (KNOWN.index(c) if c in KNOWN else len(KNOWN), c))


# ---------------------------------------------------------------------------------------------- loading
def jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return []
    out = []
    with (gzip.open(path, "rt") if path.endswith(".gz") else open(path)) as f:
        for line in f:
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass       # a line cut by the SIGTERM
    return out


def first(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v if isinstance(v, (int, float)) else None


def read_json(path):
    """A small JSON file written by printf in the shell. lib.sh's block_end writes die_c's output unquoted, so a die
    reading that failed (ettelem does not start in about one try in three right after a previous instance) leaves
    `"die_c_end":,` in block.json. Empty values become null; a file still unreadable keeps only its status."""
    if not os.path.exists(path):
        return None
    txt = open(path).read()
    try:
        return json.loads(txt)
    except ValueError:
        pass
    try:
        return json.loads(re.sub(r':\s*(?=[,}])', ':null', txt))
    except ValueError:
        m = re.search(r'"status"\s*:\s*"(\w+)"', txt)
        return {"status": m.group(1) if m else None, "unparsed": True}


def load_pass(pdir, card=None):
    rd = lambda n: read_json(os.path.join(pdir, n))
    cyc, blk = rd("cycle.json") or {}, rd("block.json")
    m = re.search(r"/p(\d+)$", pdir.rstrip("/"))
    pnum = int(m.group(1)) if m else cyc.get("pass")
    card = card or cyc.get("card") or (blk or {}).get("card")
    samples = []           # (t_ms, T, P, mhz, minion, sram, noc, minion_mv)
    for s in jsonl(os.path.join(pdir, "telemetry.jsonl")):
        try:
            T, P = first(s["temp_c"]["minshire"]), float(s["board_w"])
            t = int(s["t_ms"])
        except (KeyError, TypeError, ValueError):
            continue
        if T is None:
            continue
        sp = s.get("sp") or {}
        samples.append((t, T, P, (s.get("mhz") or {}).get("minion"),
                        first(sp.get("minion_w")), first(sp.get("sram_w")), first(sp.get("noc_w")),
                        (s.get("die_mv") or {}).get("minion")))
    samples.sort()
    launches = sorted((int(r["t_start_ms"]), int(r["t_end_ms"]), r.get("rc", 0))
                      for r in jsonl(os.path.join(pdir, "launches.jsonl")) if "t_start_ms" in r and "t_end_ms" in r)
    marks = {}
    for mk in jsonl(os.path.join(pdir, "marks.jsonl")):
        marks.setdefault(mk.get("ev"), mk)
    variant = cyc.get("variant") or ("long" if pnum and pnum >= 11 else "short")
    return {"dir": pdir, "card": card, "pass": pnum, "variant": variant, "cycle": cyc, "block": blk,
            "samples": samples, "launches": launches, "marks": marks}


def merged_windows(launches, pre_ms, post_ms):
    out = []
    for a, b, _ in sorted(launches):
        a, b = a - pre_ms, b + post_ms
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def in_windows(t, wins, starts):
    k = bisect.bisect_right(starts, t) - 1
    return k >= 0 and wins[k][0] <= t <= wins[k][1]


def cool_window(p, cool_s):
    cs, ce = p["marks"]["cool_start"]["t_ms"], p["marks"]["cool_end"]["t_ms"]
    return cs, (min(ce, cs + cool_s * 1000) if cool_s else ce)


# ---------------------------------------------------------------------------------------------- the idle clock
def cool_clock_hist(p, cool_s=CYCLE_COOL_S):
    """The minion clock of the rule-A window's samples (cooling window, launch windows excluded), before any clock
    rule: ({mhz: n}, {mhz: [minion mV]})."""
    t0, t1 = cool_window(p, cool_s)
    wins = merged_windows(p["launches"], 1000, 6000)
    starts = [w[0] for w in wins]
    h, mv = collections.Counter(), collections.defaultdict(list)
    for s in p["samples"]:
        if t0 <= s[0] <= t1 and not in_windows(s[0], wins, starts):
            h[s[3]] += 1
            if len(s) > 7 and s[7] is not None:
                mv[s[3]].append(s[7])
    return h, mv


def idle_clock_rule(card, hist):
    """(keep_mhz, drop, how): the clock rules A, K and F keep on this card, and whether other clocks are dropped.
    aifoundry2 and aifoundry3 exactly as registered; other cards per amendment A2 (see the module docstring)."""
    if card in PINNED:
        return 600, False, "pinned at 600 MHz: samples off 600 MHz counted, not dropped (registered)"
    if card == A2:
        return 600, True, "registered: samples with mhz.minion != 600 dropped"
    reg = IDLE_MHZ.get(card, DEFAULT_IDLE_MHZ)
    tot = sum(hist.values())
    at = hist.get(reg, 0)
    if tot and at < IDLE_SHARE_MIN * tot:
        known = [k for k in hist if k is not None]
        if known:
            modal = max(known, key=lambda k: hist[k])
            return modal, True, (f"amendment A2 fallback: only {100.0 * at / tot:.0f}% of the cooling samples at the expected "
                                 f"{reg} MHz; the card's most common cooling clock, {modal} MHz, is used, other clocks dropped")
    return reg, True, f"amendment A2: the card's idle clock {reg} MHz kept, other clocks dropped"


def hist_json(h):
    return {("none" if k is None else str(k)): v for k, v in sorted(h.items(), key=lambda kv: (kv[0] is None, kv[0] or 0))}


def rule_a_bins(p, cool_s=CYCLE_COOL_S, keep_mhz=600, drop=None):
    """Whole-degree idle bins of one cycle (rule A). Returns (rows by T, counters). `drop` None: the registered rule
    (aifoundry2 drops samples off 600 MHz, other cards count them)."""
    if drop is None:
        drop = p["card"] == A2
    t0, t1 = cool_window(p, cool_s)
    wins = merged_windows(p["launches"], 1000, 6000)
    starts = [w[0] for w in wins]
    bins = collections.defaultdict(list)
    cnt = collections.Counter()
    for s in p["samples"]:
        t, T, P, mhz = s[:4]
        if t < t0 or t > t1:
            continue
        cnt["window"] += 1
        if in_windows(t, wins, starts):
            cnt["launch_excluded"] += 1
            continue
        if mhz != 600:
            cnt["off600"] += 1
        if mhz != keep_mhz:
            if keep_mhz != 600:
                cnt["off_idle_clock"] += 1
            if drop:
                continue
        bins[int(T)].append(s)
    rows = {}
    for T, v in sorted(bins.items()):
        if len(v) < BIN_MIN_N:
            cnt["small_bin_samples"] += len(v)
            continue
        full = [s for s in v if None not in s[4:7]]
        r = {"T": T, "n": len(v), "board": mean([s[2] for s in v])}
        if full:
            r.update({"minion": mean([s[4] for s in full]), "sram": mean([s[5] for s in full]),
                      "noc": mean([s[6] for s in full]), "unsensed": mean([s[2] - s[4] - s[5] - s[6] for s in full]),
                      "rails": mean([s[4] + s[5] + s[6] for s in full]), "n_rails": len(full)})
        r["resid"] = r["board"] - law(T)
        if "sram" in r:
            r["sram_excess"] = r["sram"] - law(T, SRAM_LAW_A2)
        rows[T] = r
    return rows, cnt


def tmax(p):
    return max((s[1] for s in p["samples"]), default=None)


# ------------------------------------------------------------- flip_thermal_model.py step 2a (scratch copy)
def nnls(X, y, free=1, iters=200):
    """Lawson-Hanson non-negative least squares; the first `free` columns are unconstrained (flip_thermal_model.py)."""
    import numpy as np
    n = X.shape[1]
    G, h = X.T @ X, X.T @ y
    passive = list(range(free))
    coef = np.zeros(n)

    def solve(cols):
        c = np.zeros(n)
        c[cols] = np.linalg.lstsq(G[np.ix_(cols, cols)], h[cols], rcond=None)[0]
        return c

    coef = solve(passive)
    for _ in range(iters):
        w = h - G @ coef
        cand = [j for j in range(free, n) if j not in passive and w[j] > 1e-9]
        if not cand:
            break
        passive.append(max(cand, key=lambda j: w[j]))
        while True:
            c = solve(passive)
            neg = [j for j in passive if j >= free and c[j] <= 0]
            if not neg:
                coef = c
                break
            alpha = min(coef[j] / (coef[j] - c[j]) for j in neg if coef[j] - c[j] > 0) if any(coef[j] - c[j] > 0 for j in neg) else 0.0
            coef = coef + alpha * (c - coef)
            passive = [j for j in passive if j < free or coef[j] > 1e-12]
    return coef


def ftm_grid(p):
    """The session on flip_thermal_model.py's 0.1 s grid: tt (s), P (interpolated), T (held), mhz (held), act."""
    import numpy as np
    S = p["samples"]
    t = np.array([s[0] for s in S]) / 1000.0
    tt = np.arange(t[0], t[-1], DT)
    P = np.interp(tt, t, np.array([s[2] for s in S], float))
    idx = np.clip(np.searchsorted(t, tt, side="right") - 1, 0, len(t) - 1)
    T = np.array([float(s[1]) for s in S])[idx]
    mhz = np.array([s[3] if s[3] is not None else -1 for s in S])[idx]
    act = np.zeros(len(tt))
    for a, b, _ in p["launches"]:
        i0, i1 = np.searchsorted(tt, [a / 1000.0, b / 1000.0])
        act[i0:i1] = 1024
    return tt, P, T, mhz, act


def ftm_smooth(x, half=15):
    import numpy as np
    pad = np.concatenate([np.full(half, x[0]), x, np.full(half, x[-1])])
    return np.convolve(pad, np.ones(2 * half + 1) / (2 * half + 1), mode="valid")


def leak_profile(Ts, Ps):
    """P = P_fix + A exp((T-80)/T_L) on the T_L grid (NNLS, free constant): [(T_L, P_fix, A80, rms)], best."""
    import numpy as np
    prof, best = [], None
    for T_L in TL_GRID:
        X = np.column_stack([np.ones(len(Ts)), np.exp((Ts - 80.0) / T_L)])
        c = nnls(X, Ps, free=1)
        rms = float(np.sqrt(np.mean((X @ c - Ps) ** 2)))
        prof.append((T_L, float(c[0]), float(c[1]), rms))
        if best is None or rms < best[3]:
            best = prof[-1]
    return prof, best


def ftm_idle_samples(p, keep_mhz=600):
    """rule F: flip_thermal_model.py step 2a's own idle rule over the whole pass (clock: 600 MHz as registered;
    a non-registered card's idle clock, amendment A2)."""
    import numpy as np
    tt, P, T, mhz, act = ftm_grid(p)
    busy = np.convolve((act > 0).astype(float), np.ones(91), mode="same") > 0
    ok = ~busy & (mhz == keep_mhz)
    ok[:int(20 / DT)] = False
    return ftm_smooth(T)[ok], P[ok], int(ok.sum())


def k_idle_samples(p, keep_mhz=600):
    """rule K: >= 20 s after the last burst, inside the first 900 s of cooling, 600 MHz (a non-registered card: its
    idle clock), 3 s smoothing."""
    import numpy as np
    tt, P, T, mhz, act = ftm_grid(p)
    t0, t1 = cool_window(p, CYCLE_COOL_S)
    # the last burst's end; a pass that found the die already at its target made no burst: its cooling start
    last_end = (max(b for a, b, _ in p["launches"]) if p["launches"] else t0) / 1000.0
    ok = (tt >= last_end + 20.0) & (tt >= t0 / 1000.0) & (tt <= t1 / 1000.0) & (mhz == keep_mhz)
    return ftm_smooth(T)[ok], P[ok], T[ok], int(ok.sum())


def binned_resid(Tint, P, lo=None, hi=None):
    """mean over whole-degree bins (n >= 20) of bin mean - law; bins between lo and hi."""
    bins = collections.defaultdict(list)
    for T, w in zip(Tint, P):
        T = int(T)
        if (lo is None or T >= lo) and (hi is None or T <= hi):
            bins[T].append(float(w))
    rows = [(T, mean(v) - law(T)) for T, v in sorted(bins.items()) if len(v) >= BIN_MIN_N]
    return (mean([r for _, r in rows]) if rows else None), [T for T, _ in rows]


# ------------------------------------------------------------------------------------------------ items
def card_verdicts(holds, cards):
    """PASS / FAIL / CARD-DIFFERENT / INSUFFICIENT from {card: True|False|None} over the registered cards."""
    vals = [holds.get(c) for c in cards]
    if any(v is None for v in vals):
        return "INSUFFICIENT"
    if all(vals):
        return "PASS"
    if not any(vals):
        return "FAIL"
    return "CARD-DIFFERENT"


def na(card):
    return {"registered": False, "n": 0, "note": f"no prediction registered for {card}"}


def fmt_ci(s, k=2):
    lo, hi = s["ci99"]
    return f"{s['mean']:.{k}f} [{lo:.{k}f}, {hi:.{k}f}]" if lo is not None else (f"{s['mean']:.{k}f}" if s["mean"] is not None else "-")


def others(C):
    """the cards that are not registered, in order: the campaign's others (LISTED, always) and any other card present"""
    return [c for c in card_order(list(C) + list(LISTED)) if c not in CARDS]


def reported(entry, holds, band_of, n_key="n"):
    """a non-registered card's entry: its values, computed as for the registered card; not tested (amendment A2)"""
    n = entry.get(n_key, 0) or 0
    entry.update({"registered": False, "tested": False, "registered_band_of": band_of,
                  "status": "REPORTED" if n >= MIN_REPEATS else "INSUFFICIENT",
                  "info_registered_band_holds": holds,
                  "note": (f"reported, not tested: the registered band is {' / '.join(band_of)}'s (amendment A2)"
                           + ("" if n >= MIN_REPEATS else f"; {n} kept cycles, fewer than {MIN_REPEATS}"))})
    return entry


def all_cards(holds, tested, C, extra_note=""):
    """The all_cards outcome: over every tested card (here the registered ones: every IDLE band is one card's),
    PASS if it holds on every card, CARD-DIFFERENT on some, FAIL on none, INSUFFICIENT if a tested card lacks
    repeats; the other cards are reported."""
    rep = others(C)
    return {"outcome": card_verdicts(holds, tested), "tested_cards": list(tested), "holds": {c: holds.get(c) for c in tested},
            "reported_cards": rep,
            "note": ("the registered band is specific to " + " and ".join(tested) + ": " + ", ".join(rep)
                     + " reported, not tested (amendment A2)" + extra_note)}


def finish(item, holds_reg, tested, C, IC, rep_txt):
    """attach all_cards, the idle-clock note and the reported cards' reading to an item"""
    item["all_cards"] = all_cards(holds_reg, tested, C)
    # a card with no kept cooling sample has no idle clock (None), whatever its expected one
    item["idle_clocks_MHz"] = {c: ((IC.get(c) or {}).get("used_mhz") if (IC.get(c) or {}).get("n_samples") else None)
                               for c in card_order(list(C) + list(LISTED))}
    item["idle_clock_note"] = clock_note(IC, C)
    fb = fallback_txt(IC, C)
    item["reading_all_cards"] = (item["reading"] + ("; reported, not tested: " + "; ".join(rep_txt) if rep_txt else "")
                                 + ("; " + fb if fb else ""))
    return item


def fallback_txt(IC, C):
    """the cards whose idle clock came from amendment A2's fallback (their most common cooling clock), for the readings"""
    fb = []
    for c in card_order(list(C) + list(LISTED)):
        x = IC.get(c) or {}
        if x.get("n_samples") and x.get("used_mhz") != x.get("expected_mhz"):
            fb.append(f"{c} at {x['used_mhz']} MHz, not the expected {x['expected_mhz']} MHz "
                      f"({100.0 * (x.get('share_expected') or 0):.0f}% of its cooling samples there)")
    return ("idle-clock fallback (amendment A2): " + "; ".join(fb)) if fb else ""


def clock_note(IC, C):
    parts, diff = [], []
    for c in card_order(list(C) + list(LISTED)):
        x = IC.get(c) or {}
        if not x.get("n_samples"):
            parts.append(f"{c} no kept cooling samples")
            continue
        mv, fw = x.get("minion_mv_median_at_used"), x.get("firmware")
        par = ([f"firmware {fw}"] if fw else []) + ([f"fallback: expected {x['expected_mhz']} MHz"]
                                                    if x["used_mhz"] != x.get("expected_mhz") else [])
        parts.append(f"{c} {x['used_mhz']} MHz" + (f" / {mv:.0f} mV" if mv is not None else "")
                     + (f" ({'; '.join(par)})" if par else ""))
        if x["used_mhz"] != 600:
            diff.append(c)
    txt = "idle clocks: " + ", ".join(parts)
    reg_fw = sorted({FIRMWARE[c] for c in CARDS if c in FIRMWARE})
    ofw = [c for c in card_order(list(C) + list(LISTED)) if (IC.get(c) or {}).get("n_samples") and c not in CARDS
           and (IC[c].get("firmware") or FIRMWARE.get(c)) not in reg_fw]
    if ofw:
        txt += ("; " + " and ".join(f"{c} ({IC[c].get('firmware') or FIRMWARE.get(c) or 'unknown'})" for c in ofw)
                + (" runs" if len(ofw) == 1 else " run") + " other firmware than " + " and ".join(CARDS)
                + f" ({', '.join(reg_fw)}); the firmware sets the idle state, so the idle power is stated per card")
    if diff:
        one = len(diff) == 1
        txt += ("; " + " and ".join(diff) + (" idles" if one else " idle") + " at a different operating point than the 600 MHz of "
                "aifoundry2, aifoundry3 and the law, so " + ("its" if one else "their") + " idle power is not comparable with "
                "the law's or the other cards' at equal temperature")
    return txt


def calc_0(cyc):
    tm = [c["tmax"] for c in cyc]
    holds = (all(60 <= t <= 66 for t in tm) if len(tm) >= MIN_REPEATS else None)
    return {"tmax_per_cycle": tm, "n": len(tm), "band": [60, 66], "all_inside": holds,
            "heat_reason_per_cycle": [c["heat_reason"] for c in cyc]}, holds


def item_0(C, IC):
    tm = [c["tmax"] for c in C[A3]]
    e3, holds = calc_0(C[A3])
    pc = {A3: e3, A2: na(A2)}
    pc[A2]["info_tmax_per_cycle"] = [c["tmax"] for c in C[A2]]
    rep = []
    for c in others(C):
        e, h = calc_0(C.get(c, []))
        pc[c] = reported(e, h, [A3])
        rep.append(f"{c} Tmax {min(e['tmax_per_cycle'])}-{max(e['tmax_per_cycle'])} C ({e['n']} cycles, heat ended by {'/'.join(sorted(set(map(str, e['heat_reason_per_cycle']))))})"
                   if e["tmax_per_cycle"] else f"{c} no kept cycle")
    out = card_verdicts({A3: holds}, [A3])
    rd = (f"aifoundry3's plateau under the heater: {min(tm)}-{max(tm)} C over {len(tm)} cycles (predicted 60-66 C)"
          if tm else "no aifoundry3 cycle yet")
    return finish({"item": "IDLE-0", "claims": ["energy-manual-22"], "per_card": pc,
                   "test": "every kept aifoundry3 cycle's highest reading (heat to 90 C or 150 bursts / 900 s) inside 60-66 C; logged, sets the range of (a) and (e)",
                   "outcome": out, "reading": rd}, {A3: holds}, [A3], C, IC, rep)


def calc_a(cyc):
    offs, slopes, info = [], [], []
    for c in cyc:
        rows = [r for T, r in c["bins"].items() if 51 <= T <= c["tmax"]]
        offs.append(mean([r["resid"] for r in rows]) if rows else None)
        slopes.append(slope([r["T"] for r in rows], [r["resid"] for r in rows]))
        info.append({"pass": c["pass"], "bins": [r["T"] for r in rows], "resid_by_bin": {r["T"]: rnd(r["resid"], 3) for r in rows}})
    so, ss = stat([o for o in offs if o is not None], (0.3, 0.9)), stat([s for s in slopes if s is not None], (-0.05, 0.05))
    n = min(so["n"], ss["n"])
    holds = (so["inside_band"] and ss["inside_band"]) if n >= MIN_REPEATS else None
    allbins = [v for i in info for v in i["resid_by_bin"].values()]
    return {"n": n, "offset_W": so, "resid_slope_W_per_C": ss, "cycles": info,
            "info_prediction": {"offset_point": 0.61, "every_bin_in_0.3_0.9": bool(allbins) and all(0.3 <= v <= 0.9 for v in allbins),
                                "slope_point_within_0.03": ss["mean"] is not None and abs(ss["mean"]) <= 0.03}}, holds


def item_a(C, IC):
    e3, holds = calc_a(C[A3])
    so, ss, n = e3["offset_W"], e3["resid_slope_W_per_C"], e3["n"]
    pc = {A3: e3, A2: na(A2)}
    rep = []
    for c in others(C):
        e, h = calc_a(C.get(c, []))
        pc[c] = reported(e, h, [A3])
        rep.append(f"{c} no kept cycle" if not C.get(c) else f"{c} idle - law {fmt_ci(e['offset_W'])} W, residual slope {fmt_ci(e['resid_slope_W_per_C'], 3)} W/C ({e['n']} cycles)")
    out = card_verdicts({A3: holds}, [A3])
    rd = (f"aifoundry3 idle - aifoundry2 law {fmt_ci(so)} W, residual slope {fmt_ci(ss, 3)} W/C over {n} cycles"
          + ("; the law with +0.6 W describes aifoundry3 at 51-Tmax C" if holds else "; the +0.6 W statement is not established" if holds is False else ""))
    return finish({"item": "IDLE-a", "claims": ["energy-manual-145", "energy-manual-01", "dvfs-63", "energy-manual-16", "horace-lowpower-124"],
                   "per_card": pc, "test": "99% t over cycles (aifoundry3): mean residual over bins 51..Tmax inside [0.3, 0.9] W and the residual's slope over those bins inside [-0.05, +0.05] W/C",
                   "outcome": out, "reading": rd}, {A3: holds}, [A3], C, IC, rep)


def per_bin(cycles, key, lo_T=None, hi_T=None, tmax_cap=False):
    """For every whole-degree bin: the cycles' bin values of `key` and their 99% t interval over cycles.
    A bin is testable when >= 3 kept cycles visited it (n >= 20 samples in each)."""
    vals = collections.defaultdict(list)
    for c in cycles:
        for T, r in c["bins"].items():
            if key in r and (lo_T is None or T >= lo_T) and (hi_T is None or T <= hi_T) and (not tmax_cap or T <= c["tmax"]):
                vals[T].append(r[key])
    out = {}
    for T in sorted(vals):
        m, lo, hi, n = ci99(vals[T])
        out[T] = {"n_cycles": n, "mean": rnd(m), "ci99": [rnd(lo), rnd(hi)], "testable": n >= MIN_REPEATS}
    return out


def calc_b(cyc):
    band = (-0.53, 0.07)
    # Amendment A1 (25 Sep, before any idle data; AMENDMENTS.md): each cycle's first and last whole-degree bin is
    # left out, since readings in whole degrees bias the edge bins by 0.1-0.3 W on aifoundry2.
    trimmed = [dict(c, bins={T: r for T, r in c["bins"].items() if T not in (min(c["bins"]), max(c["bins"]))})
               for c in cyc if c["bins"]]
    pb = per_bin(trimmed, "resid")
    for r in pb.values():
        r["inside_band"] = bool(r["testable"] and inside(r["ci99"][0], r["ci99"][1], band))
    testable = [T for T, r in pb.items() if r["testable"]]
    bad = [T for T in testable if not pb[T]["inside_band"]]
    offs = [mean([r["resid"] for r in c["bins"].values()]) for c in cyc if c["bins"]]
    so = stat(offs, band)
    n = len(cyc)
    # a bin visited by fewer than 3 kept cycles has fewer than the needed repeats: no testable bin is INSUFFICIENT
    holds = (not bad) if (n >= MIN_REPEATS and testable) else None
    return {"n": n, "bins": pb, "testable_bins": testable, "bins_outside_band": bad,
            "info_cycle_offset_W": so, "cycles_T_range": {c["pass"]: [min(c["bins"]), max(c["bins"])] for c in cyc if c["bins"]}}, holds


def item_b(C, IC):
    e2, holds = calc_b(C[A2])
    testable, bad, so, n = e2["testable_bins"], e2["bins_outside_band"], e2["info_cycle_offset_W"], e2["n"]
    pc = {A2: e2, A3: na(A3)}
    rep = []
    for c in others(C):
        e, h = calc_b(C.get(c, []))
        pc[c] = reported(e, h, [A2])
        rep.append(f"{c} no kept cycle" if not C.get(c) else f"{c} idle - law cycle mean {fmt_ci(e['info_cycle_offset_W'])} W ({e['n']} cycles"
                   + (f", bins {e['testable_bins'][0]}-{e['testable_bins'][-1]} C" if e["testable_bins"] else "") + ")")
    out = card_verdicts({A2: holds}, [A2])
    rd = ((f"aifoundry2 idle - law in {len(testable)} bins {testable[0]}-{testable[-1]} C over {n} cycles: "
           + ("every bin's 99% interval inside -0.23 +- 0.3 W" if not bad else f"bins {bad} outside -0.23 +- 0.3 W")
           + f"; cycle mean {fmt_ci(so)} W") if testable else f"no bin visited by 3 kept cycles ({n} cycles)")
    return finish({"item": "IDLE-b", "claims": ["energy-manual-06", "energy-manual-15", "dvfs-61"], "per_card": pc,
                   "test": "aifoundry2, every whole-degree bin visited by >= 3 kept cycles (each cycle's first and last bin left out, amendment A1): the 99% t interval over cycles of (bin mean - law) inside [-0.53, +0.07] W (-0.23 +- 0.3); at least one such bin",
                   "outcome": out, "reading": rd}, {A2: holds}, [A2], C, IC, rep)


def calc_c(cyc):
    us, rs, info = [], [], []
    for c in cyc:
        u = [r for T, r in c["bins"].items() if 74 <= T <= 88 and "unsensed" in r]
        m = [r for T, r in c["bins"].items() if 75 <= T <= 80 and "rails" in r]
        us.append(slope([r["T"] for r in u], [r["unsensed"] for r in u]))
        rs.append(slope([r["T"] for r in m], [r["rails"] for r in m]))
        info.append({"pass": c["pass"], "unsensed_bins": [r["T"] for r in u], "rail_bins": [r["T"] for r in m]})
    su, sr = stat([v for v in us if v is not None]), stat([v for v in rs if v is not None], (0.44, 0.58))
    n = su["n"]
    holds = (su["ci99"][1] is not None and su["ci99"][1] < 0.15) if n >= MIN_REPEATS else None
    return {"n": n, "unsensed_slope_W_per_C_74_88": su, "upper_bound_below_0.15": holds,
            "info_metered_rail_slope_W_per_C_75_80": sr, "info_point_prediction": {"unsensed": 0.055, "rails": "0.51 +- 0.07"},
            "cycles": info}, holds


def unsensed_slope_all_bins(cyc):
    return rnd([slope([r["T"] for r in c["bins"].values() if "unsensed" in r],
                      [r["unsensed"] for r in c["bins"].values() if "unsensed" in r]) for c in cyc])


def item_c(C, IC):
    e2, holds = calc_c(C[A2])
    su, sr, n = e2["unsensed_slope_W_per_C_74_88"], e2["info_metered_rail_slope_W_per_C_75_80"], e2["n"]
    pc = {A2: e2, A3: na(A3)}
    pc[A3]["info_unsensed_slope_per_cycle"] = unsensed_slope_all_bins(C[A3])
    rep = []
    for c in others(C):
        e, h = calc_c(C.get(c, []))
        e["info_unsensed_slope_per_cycle_all_bins"] = unsensed_slope_all_bins(C.get(c, []))
        pc[c] = reported(e, h, [A2])
        rep.append(f"{c} no kept cycle" if not C.get(c) else f"{c} unsensed slope 74-88 C {fmt_ci(e['unsensed_slope_W_per_C_74_88'], 3)} W/C ({e['n']} cycles)")
    out = card_verdicts({A2: holds}, [A2])
    rd = f"aifoundry2 unsensed idle slope 74-88 C {fmt_ci(su, 3)} W/C ({n} cycles; holds if the upper end < 0.15); metered rails 75-80 C {fmt_ci(sr, 3)} W/C"
    return finish({"item": "IDLE-c", "claims": ["energy-manual-11", "energy-manual-12", "energy-manual-13", "energy-manual-163"], "per_card": pc,
                   "test": "(c) holds if the 99% t upper bound over cycles of aifoundry2's unsensed (board - three rails) slope over bins 74-88 C is < 0.15 W/C; the metered-rail slope over 75-80 C is reported against 0.51 +- 0.07",
                   "outcome": out, "reading": rd}, {A2: holds}, [A2], C, IC, rep)


def calc_d(cyc):
    comp = {k: [] for k in SPLIT_22SEP}
    boards, used = [], []
    for c in cyc:
        r = c["bins"].get(73)
        if r and "unsensed" in r:
            used.append(c["pass"]); boards.append(r["board"])
            for k in comp:
                comp[k].append(r[k])
    st = {k: stat(v, (SPLIT_22SEP[k] - 0.2, SPLIT_22SEP[k] + 0.2)) for k, v in comp.items()}
    n = len(used)
    holds = all(s["inside_band"] for s in st.values()) if n >= MIN_REPEATS else None
    return {"n": n, "passes_with_73C_bin": used, "components_W": st, "info_board_W": stat(boards), "reference_22Sep": SPLIT_22SEP,
            "cycles_without_73C_bin": [c["pass"] for c in cyc if c["pass"] not in used]}, holds


def item_d(C, IC):
    e2, holds = calc_d(C[A2])
    st, n = e2["components_W"], e2["n"]
    pc = {A2: e2, A3: na(A3)}
    rep = []
    for c in others(C):
        e, h = calc_d(C.get(c, []))
        pc[c] = reported(e, h, [A2])
        rep.append(f"{c} 73 C split over {e['n']} cycles: " + " / ".join(f"{k} {fmt_ci(s)}" for k, s in e["components_W"].items())
                   if e["n"] else f"{c} no 73 C idle bin")
    out = card_verdicts({A2: holds}, [A2])
    rd = (f"aifoundry2 73 C split over {n} cycles: " + " / ".join(f"{k} {fmt_ci(s)}" for k, s in st.items())) if n else \
         "no aifoundry2 cycle reached a 73 C idle bin (n >= 20) in its 900 s of cooling"
    return finish({"item": "IDLE-d", "claims": ["energy-manual-18", "dvfs-62", "hub-080"], "per_card": pc,
                   "test": "99% t over the aifoundry2 cycles with a 73 C bin: minion, SRAM, mesh and unsensed each inside the 22 Sep value +- 0.2 W",
                   "outcome": out, "reading": rd}, {A2: holds}, [A2], C, IC, rep)


def calc_e(cyc):
    sl, info = [], []
    for c in cyc:
        rows = [r for T, r in c["bins"].items() if 51 <= T <= c["tmax"] and "sram" in r]
        sl.append(slope([r["T"] for r in rows], [r["sram"] for r in rows]))
        info.append({"pass": c["pass"], "sram_by_bin": {r["T"]: rnd(r["sram"], 3) for r in rows}})
    ss = stat([v for v in sl if v is not None], (0.017, 0.077))
    pb = per_bin(cyc, "sram_excess", lo_T=51, tmax_cap=True)
    for r in pb.values():
        r["ge_0.8"] = bool(r["testable"] and r["ci99"][0] >= 0.8)
    testable = [T for T, r in pb.items() if r["testable"]]
    bad = [T for T in testable if not pb[T]["ge_0.8"]]
    n = ss["n"]
    # the slope part fails on its own; otherwise a bin test with no bin in >= 3 kept cycles is INSUFFICIENT
    if n < MIN_REPEATS:
        holds = None
    elif not ss["inside_band"]:
        holds = False
    else:
        holds = (not bad) if testable else None
    return {"n": n, "sram_slope_W_per_C": ss, "excess_over_a2_sram_law_by_bin": pb, "testable_bins": testable,
            "bins_below_0.8": bad, "cycles": info}, holds


def item_e(C, IC):
    e3, holds = calc_e(C[A3])
    ss, pb, testable, n = e3["sram_slope_W_per_C"], e3["excess_over_a2_sram_law_by_bin"], e3["testable_bins"], e3["n"]
    pc = {A3: e3, A2: na(A2)}
    rep = []
    for c in others(C):
        e, h = calc_e(C.get(c, []))
        pc[c] = reported(e, h, [A3])
        ex = [e["excess_over_a2_sram_law_by_bin"][T]["mean"] for T in e["testable_bins"]]
        rep.append(f"{c} no kept cycle" if not C.get(c) else f"{c} SRAM slope {fmt_ci(e['sram_slope_W_per_C'], 3)} W/C ({e['n']} cycles)"
                   + (f", excess over the aifoundry2 SRAM law {min(ex):.2f}-{max(ex):.2f} W" if ex else ""))
    out = card_verdicts({A3: holds}, [A3])
    lows = [pb[T]["ci99"][0] for T in testable]
    rd = (f"aifoundry3 SRAM rail slope {fmt_ci(ss, 3)} W/C (predicted 0.047 +- 0.03) over {n} cycles; excess over the aifoundry2 SRAM law "
          + (f"99% lower ends {min(lows):.2f}-{max(lows):.2f} W in bins {testable[0]}-{testable[-1]} C" if testable else "untestable (no bin in 3 cycles)"))
    return finish({"item": "IDLE-e", "claims": ["energy-manual-19", "energy-manual-20", "energy-manual-22"], "per_card": pc,
                   "test": "aifoundry3, bins 51..Tmax: 99% t over cycles of the SRAM rail's slope inside [0.017, 0.077] W/C, and in every bin visited by >= 3 kept cycles the lower end of the 99% t interval of (SRAM - (-0.32 + 2.81 e^((T-80)/36))) >= 0.8 W",
                   "outcome": out, "reading": rd}, {A3: holds}, [A3], C, IC, rep)


def own_unsensed(cs):
    v = [mean([r["unsensed"] for r in c["bins"].values() if "unsensed" in r]) for c in cs if c["bins"]]
    Ts = [T for c in cs for T in c["bins"]]
    return {"unsensed_W_mean_over_own_bins": stat([x for x in v if x is not None]), "T_range": [min(Ts), max(Ts)] if Ts else None}


def unsensed_70(cs):
    return [c["bins"][70]["unsensed"] for c in cs if 70 in c["bins"] and "unsensed" in c["bins"][70]]


def item_f(C, IC):
    a3_70, a2_70 = unsensed_70(C[A3]), unsensed_70(C[A2])
    met = len(a3_70) >= MIN_REPEATS
    pc = {A3: {"n": len(C[A3]), "n_cycles_with_70C_bin": len(a3_70), "tmax_per_cycle": [c["tmax"] for c in C[A3]], "own_temperature": own_unsensed(C[A3])},
          A2: {"n": len(C[A2]), "n_cycles_with_70C_bin": len(a2_70), "own_temperature": own_unsensed(C[A2]), "reference_W_at_70C": 14.7}}
    if met:
        s = stat(a3_70, (12.9, 13.9))
        pc[A3]["unsensed_70C_W"] = s
        pc[A2]["unsensed_70C_W"] = stat(a2_70)
        out = "PASS" if s["inside_band"] else "FAIL"
        rd = f"aifoundry3 unsensed at 70 C {fmt_ci(s)} W against aifoundry2's 14.7 W (predicted 12.9-13.9)"
    elif len(C[A3]) >= MIN_REPEATS and len(C[A2]) >= MIN_REPEATS:
        out = "CARD-DIFFERENT"
        o3, o2 = pc[A3]["own_temperature"], pc[A2]["own_temperature"]
        rd = (f"condition not met (aifoundry3 idled at 70 C in {len(a3_70)} cycles): the unsensed stays per card, "
              f"aifoundry2 {fmt_ci(o2['unsensed_W_mean_over_own_bins'])} W at {o2['T_range']} C, aifoundry3 {fmt_ci(o3['unsensed_W_mean_over_own_bins'])} W at {o3['T_range']} C")
    else:
        out = "INSUFFICIENT"
        rd = "fewer than 3 kept cycles on a card"
    rep = []
    for c in others(C):
        cs = C.get(c, [])
        v70 = unsensed_70(cs)
        e = {"n": len(cs), "n_cycles_with_70C_bin": len(v70), "tmax_per_cycle": [x["tmax"] for x in cs], "own_temperature": own_unsensed(cs)}
        h = None
        if len(v70) >= MIN_REPEATS:
            e["unsensed_70C_W"] = stat(v70, (12.9, 13.9))
            h = e["unsensed_70C_W"]["inside_band"]
        pc[c] = reported(e, h, [A3])
        o = e["own_temperature"]
        rep.append(f"{c} unsensed {fmt_ci(o['unsensed_W_mean_over_own_bins'])} W at {o['T_range']} C"
                   + (f", at 70 C {fmt_ci(e['unsensed_70C_W'])} W" if "unsensed_70C_W" in e else "") if o["T_range"] else f"{c} no kept cycle")
    # the registered outcome is decided by the condition (not by holds per card): all_cards repeats it
    item = finish({"item": "IDLE-f", "claims": ["energy-manual-163"], "per_card": pc, "condition_met": met,
                   "test": "conditional: only if >= 3 aifoundry3 cycles have a 70 C idle bin, 99% t of its unsensed inside [12.9, 13.9] W; otherwise the values stay per card at each card's own temperature (outcome CARD-DIFFERENT, condition_met false)",
                   "outcome": out, "reading": rd}, {}, [A3], C, IC, rep)
    item["all_cards"].update({"outcome": out, "tested_cards": [A2, A3], "holds": None,
                              "note": "conditional item registered on aifoundry3 against aifoundry2's 14.7 W: its outcome is the registered one; "
                                      + ", ".join(others(C)) + " reported, not tested (amendment A2)"})
    return item


def calc_k(cyc_all):
    cyc = [c for c in cyc_all if c["tmax"] is not None and c["tmax"] >= 86]
    rows, bestTL, shares_ok, tl_ok, low_share, resid = [], [], [], [], [], []
    for c in cyc:
        k = c.get("k")
        if not k:
            continue
        rows.append(k)
        bestTL.append(k["best_T_L"]); tl_ok.append(30 <= k["best_T_L"] <= 48)
        shares_ok.append(0.31 <= k["share_range"][0] and k["share_range"][1] <= 0.47)
        low_share.append(k["share_range"][0])
        if k["resid_70_85"] is not None:
            resid.append(k["resid_70_85"])
    n = len(rows)
    sr = stat(resid, (-0.4, 0.0))
    established = n >= MIN_REPEATS and all(s > 0.30 for s in low_share)
    holds = (all(tl_ok) and all(shares_ok) and sr["inside_band"]) if n >= MIN_REPEATS and sr["n"] >= MIN_REPEATS else None
    e = {"n": n, "cycles_from_86C": [c["pass"] for c in cyc], "cycles_below_86C": [c["pass"] for c in cyc_all if not (c["tmax"] is not None and c["tmax"] >= 86)],
         "per_cycle": rows, "best_T_L_all_in_30_48": all(tl_ok) if rows else None,
         "shares_all_in_0.31_0.47": all(shares_ok) if rows else None, "law_resid_70_85_W": sr,
         "decision_busy_leakage_above_Kanter_30pct": "established" if established else "not established: the page states the range"}
    return e, holds, bestTL, low_share, established


def item_k(C, IC):
    e2, holds, bestTL, low_share, established = calc_k(C[A2])
    n, sr = e2["n"], e2["law_resid_70_85_W"]
    pc = {A2: e2, A3: na(A3)}
    rep = []
    for c in others(C):
        e, h, btl, ls, _ = calc_k(C.get(c, []))
        pc[c] = reported(e, h, [A2])
        rep.append(f"{c} cooling from >= 86 C, {e['n']} cycles: best T_L {btl}, busy share down to {min(ls):.2f}, law residual 70-85 C {fmt_ci(e['law_resid_70_85_W'])} W"
                   if e["n"] else f"{c} no cycle cooled from >= 86 C")
    out = card_verdicts({A2: holds}, [A2])
    lo = min(low_share) if low_share else None
    rd = (f"aifoundry2 cooling from >= 86 C, {n} cycles: best T_L {bestTL}, busy share over the flat range down to {lo:.2f}; "
          f"law residual 70-85 C {fmt_ci(sr)} W; Kanter 30%: {'established' if established else 'not established'}") if n else "no aifoundry2 cycle cooled from >= 86 C"
    return finish({"item": "IDLE-k", "claims": ["dvfs-05", "dvfs-06", "energy-manual-147", "energy-manual-149"], "per_card": pc,
                   "test": "aifoundry2 cycles from >= 86 C, samples >= 20 s after the last burst: each cycle's profile-best T_L inside 30-48 C and its busy shares A80/63.9 W over the T_L range within 0.005 W rms of the best inside 0.31-0.47; 99% t of the cycle residual to the law over 70-85 C inside [-0.4, 0.0] W. Decision: 'busy leakage above Kanter's 30%' only if every cycle's lowest share > 0.30",
                   "outcome": out, "decision": pc[A2]["decision_busy_leakage_above_Kanter_30pct"], "reading": rd}, {A2: holds}, [A2], C, IC, rep)


def calc_L2(xs):
    a2 = [x for x in xs if x.get("fit")]
    s_tl = stat([x["fit"]["T_L"] for x in a2], (30, 45))
    s_a = stat([x["fit"]["A80"] for x in a2], (19, 29))
    s_sl = stat([x["fit"]["slope80"] for x in a2], (0.62, 0.68))
    ident = s_a["ci99"][0] is not None and (s_a["ci99"][1] - s_a["ci99"][0]) / 2 < 3.0
    e = {"n": len(a2), "best_T_L_C": s_tl, "A80_W": s_a, "slope80_W_per_C": s_sl,
         "leakage_split": "identified" if (len(a2) >= MIN_REPEATS and ident) else "not identified: the pages give 20-29 W and quote the slope",
         "per_pass": [{"pass": x["pass"], **x["fit"], "profile": x["profile"]} for x in a2]}
    holds = (s_tl["inside_band"] and s_a["inside_band"] and s_sl["inside_band"]) if len(a2) >= MIN_REPEATS else None
    return e, holds


def calc_L3(xs):
    a3 = [x for x in xs if x.get("fit")]
    s_56 = stat([x["fit"]["slope56"] for x in a3], (0.22, 0.38))
    s_off = stat([x["offset"] for x in a3 if x.get("offset") is not None], (0.3, 1.1))
    e = {"n": len(a3), "slope56_W_per_C": s_56, "offset_from_law_W": s_off,
         "per_pass": [{"pass": x["pass"], **x["fit"], "offset": rnd(x.get("offset")), "profile": x["profile"]} for x in a3]}
    holds = (s_56["inside_band"] and s_off["inside_band"]) if len(a3) >= MIN_REPEATS and s_off["n"] >= MIN_REPEATS else None
    return e, holds


def item_L(L, C, IC):
    pc, holds = {}, {}
    pc[A2], holds[A2] = calc_L2(L[A2])
    pc[A3], holds[A3] = calc_L3(L[A3])
    s_tl, s_a, s_sl = pc[A2]["best_T_L_C"], pc[A2]["A80_W"], pc[A2]["slope80_W_per_C"]
    s_56, s_off = pc[A3]["slope56_W_per_C"], pc[A3]["offset_from_law_W"]
    a2, a3 = pc[A2]["n"], pc[A3]["n"]
    rep = []
    for c in others(C):
        e2, h2 = calc_L2(L.get(c, []))
        e3, h3 = calc_L3(L.get(c, []))
        e = dict(e2)
        e.update({k: v for k, v in e3.items() if k not in ("n", "per_pass")})
        e["per_pass"] = e3["per_pass"]          # the same fits, with each pass's offset from the law
        pc[c] = reported(e, None, [A2, A3])
        pc[c]["info_registered_band_holds"] = {A2: h2, A3: h3}
        rep.append(f"{c} no long pass" if not L.get(c) else f"{c} T_L {fmt_ci(e['best_T_L_C'], 0)} C, A80 {fmt_ci(e['A80_W'], 1)} W, slope80 {fmt_ci(e['slope80_W_per_C'], 3)} W/C, "
                   f"slope56 {fmt_ci(e['slope56_W_per_C'], 3)} W/C, offset {fmt_ci(e['offset_from_law_W'])} W ({e['n']} passes, split {e['leakage_split'].split(':')[0]})")
    out = card_verdicts(holds, [A2, A3])
    rd = (f"IDLE-LONG: aifoundry2 T_L {fmt_ci(s_tl, 0)} C, A80 {fmt_ci(s_a, 1)} W, slope80 {fmt_ci(s_sl, 3)} W/C ({a2} passes, split {pc[A2]['leakage_split'].split(':')[0]}); "
          f"aifoundry3 slope56 {fmt_ci(s_56, 3)} W/C, offset {fmt_ci(s_off)} W ({a3} passes)")
    return finish({"item": "IDLE-L", "claims": ["energy-manual-10", "horace-lowpower-084", "horace-lowpower-087", "horace-lowpower-088", "horace-lowpower-139",
                                                "horace-lowpower-158", "horace-lowpower-142", "anatomy-115", "hub-009", "dvfs-59", "pt-spatial-05", "horace-lowpower-187"],
                   "per_card": pc, "test": "IDLE-LONG passes only, one-sample 99% t over passes of flip_thermal_model.py step 2a's idle fit: aifoundry2 best T_L inside [30, 45] C, A80 inside [19, 29] W, A80/T_L inside [0.62, 0.68] W/C; aifoundry3 slope at 56 C inside [0.22, 0.38] W/C and offset from the law inside [0.3, 1.1] W. The split is 'identified' only if A80's interval is narrower than +-3 W",
                   "outcome": out, "reading": rd}, holds, [A2, A3], C, IC, rep)


# ------------------------------------------------------------------------------------------------ driver
def discover(data):
    """every card directory under data that has an idle/ directory, plus the registered cards (possibly empty)"""
    cards = [A2, A3]
    if os.path.isdir(data):
        cards += [n for n in os.listdir(data) if os.path.isdir(os.path.join(data, n, "idle"))]
    out = {}
    for card in card_order(cards):
        out[card] = []
        root = os.path.join(data, card, "idle")
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root), key=lambda n: (len(n), n)):     # p2 before p11
            if re.fullmatch(r"p\d+", name):
                out[card].append(os.path.join(root, name))
    return out


def keep_reason(p):
    b = p["block"]
    if not b:
        return "no block.json (running or interrupted)"
    if b.get("status") != "ok":
        return f"status {b.get('status')}: {b.get('note', '')}"
    if p["cycle"].get("dry"):
        return "dry run"
    if "cool_start" not in p["marks"] or "cool_end" not in p["marks"]:
        return "no cool_start/cool_end mark"
    if not p["samples"]:
        return "no telemetry samples"
    return None


def pass_clock_record(p, h, mv):
    tot = sum(h.values())
    known = [k for k in h if k is not None]
    modal = max(known, key=lambda k: h[k]) if known else None
    cs, ce = p["marks"].get("cycle_start", {}), p["marks"].get("cool_end", {})
    return {"cool_hist_MHz": hist_json(h), "cool_modal_MHz": modal,
            "cool_modal_share": rnd(h[modal] / tot, 3) if modal is not None and tot else None,
            "minion_mv_median_at_modal": median(mv.get(modal, [])),
            "before_heating": {"mhz": cs.get("idle_mhz"), "minion_mv": cs.get("idle_minion_mv")},
            "end_of_cooling": {"mhz": ce.get("idle_mhz"), "minion_mv": ce.get("idle_minion_mv")},
            "polls": ce.get("polls"), "other_card_polls": ce.get("other_card_polls")}


def reduce_all(data, out_path):
    import numpy as np
    found = discover(data)
    cards = list(found)
    C = {c: [] for c in cards}         # cycles for items 0, a-f, k
    L = {c: [] for c in cards}         # long passes for item L
    passes = {c: [] for c in cards}
    IC = {}                            # the idle clock per card
    for card, dirs in found.items():
        kept = []
        for d in dirs:
            p = load_pass(d, card)
            why = keep_reason(p)
            t0 = (p["block"] or {}).get("t0_ms")
            rec = {"pass": p["pass"], "variant": p["variant"], "kept": why is None, "why_dropped": why,
                   "date_utc": time.strftime("%Y-%m-%d", time.gmtime(t0 / 1000.0)) if isinstance(t0, (int, float)) else None}
            passes[card].append(rec)
            if why:
                continue
            h, mv = cool_clock_hist(p)
            rec["idle_clock"] = pass_clock_record(p, h, mv)
            kept.append((p, rec, h, mv))
        # the card's idle clock from its kept cycles' cooling samples (first 900 s, launch windows excluded)
        H, MV = collections.Counter(), collections.defaultdict(list)
        for _, _, h, mv in kept:
            H.update(h)
            for k, v in mv.items():
                MV[k].extend(v)
        keep_mhz, drop, how = idle_clock_rule(card, H)
        tot = sum(H.values())
        IC[card] = {"expected_mhz": IDLE_MHZ.get(card, DEFAULT_IDLE_MHZ), "firmware": FIRMWARE.get(card), "used_mhz": keep_mhz, "off_clock_dropped": drop, "rule": how,
                    "n_samples": tot, "share_at_used": rnd(H.get(keep_mhz, 0) / tot, 3) if tot else None,
                    "share_expected": rnd(H.get(IDLE_MHZ.get(card, DEFAULT_IDLE_MHZ), 0) / tot, 3) if tot else None,
                    "cool_hist_MHz": hist_json(H), "minion_mv_median_at_used": median(MV.get(keep_mhz, [])),
                    "passes_modal_not_used": [r["pass"] for _, r, _, _ in kept if r["idle_clock"]["cool_modal_MHz"] not in (None, keep_mhz)],
                    "other_card_polls": sum(r["idle_clock"]["other_card_polls"] or 0 for _, r, _, _ in kept),
                    "polls": sum(r["idle_clock"]["polls"] or 0 for _, r, _, _ in kept)}
        # the registered cards keep exactly the registered sample rules (drop None: aifoundry2 drops off 600 MHz)
        reg_drop = None if card in CARDS else drop
        for p, rec, _, _ in kept:
            bins, cnt = rule_a_bins(p, keep_mhz=keep_mhz, drop=reg_drop)
            he = p["marks"].get("heat_end", {})
            c = {"pass": p["pass"], "variant": p["variant"], "tmax": tmax(p), "bins": bins, "counts": dict(cnt),
                 "heat_reason": he.get("reason"), "heat_end_c": he.get("die_c")}
            rec.update({"tmax": c["tmax"], "bins": sorted(bins), "counts": dict(cnt), "heat_reason": c["heat_reason"]})
            if card not in PINNED and c["tmax"] is not None and c["tmax"] >= 86:
                Ts, Ps, Traw, nk = k_idle_samples(p, keep_mhz)
                if nk >= BIN_MIN_N:
                    prof, best = leak_profile(Ts, Ps)
                    rng = [x for x in prof if x[3] <= best[3] + 0.005]
                    sh = [x[2] / BUSY_80 for x in rng]
                    r, rb = binned_resid(Traw, Ps, 70, 85)
                    c["k"] = {"pass": p["pass"], "n_samples": nk, "T_span": [rnd(float(Ts.min()), 2), rnd(float(Ts.max()), 2)],
                              "best_T_L": best[0], "best_rms": rnd(best[3]), "T_L_range": [rng[0][0], rng[-1][0]],
                              "T_L_in_range": [x[0] for x in rng], "share_range": [rnd(min(sh)), rnd(max(sh))],
                              "resid_70_85": rnd(r), "resid_bins": rb,
                              "profile": [{"T_L": x[0], "P_fix": rnd(x[1], 3), "A80": rnd(x[2], 3), "rms": rnd(x[3], 4)} for x in prof]}
            C[card].append(c)
            if p["variant"] == "long":
                Ts, Ps, nf = ftm_idle_samples(p, keep_mhz)
                x = {"pass": p["pass"], "n_samples": nf}
                if nf >= BIN_MIN_N:
                    prof, best = leak_profile(Ts, Ps)
                    T_L, Pf, A = best[0], best[1], best[2]
                    x["fit"] = {"T_L": T_L, "P_fix": rnd(Pf, 3), "A80": rnd(A, 3), "slope80": rnd(A / T_L, 4),
                                "slope56": rnd(A / T_L * math.exp((56 - 80) / T_L), 4), "rms": rnd(best[3], 4),
                                "T_span": [rnd(float(Ts.min()), 2), rnd(float(Ts.max()), 2)]}
                    x["profile"] = [{"T_L": q[0], "A80": rnd(q[2], 3), "rms": rnd(q[3], 4)} for q in prof]
                    lb, _ = rule_a_bins(p, cool_s=0, keep_mhz=keep_mhz, drop=reg_drop)
                    x["offset"] = mean([r["resid"] for r in lb.values()]) if lb else None
                L[card].append(x)
    for c in LISTED:                   # the campaign's other cards are always listed, with or without data
        C.setdefault(c, []); L.setdefault(c, []); passes.setdefault(c, [])
        IC.setdefault(c, {"expected_mhz": IDLE_MHZ[c], "firmware": FIRMWARE.get(c), "used_mhz": None, "n_samples": 0, "rule": "no data"})
    items = [item_0(C, IC), item_a(C, IC), item_b(C, IC), item_c(C, IC), item_d(C, IC), item_e(C, IC), item_f(C, IC), item_k(C, IC), item_L(L, C, IC)]
    allc = card_order(C)
    res = {"experiment": "V3-IDLE", "plan": "docs/reports/data/2026-09-25-claims-v3/PLAN3.md section V3-IDLE; AMENDMENTS.md A1, A2",
           "data": os.path.abspath(data), "cards": allc, "registered_cards": list(CARDS), "passes": passes,
           "cycles_used": {c: [x["pass"] for x in C[c]] for c in allc}, "long_passes_used": {c: [x["pass"] for x in L[c]] for c in allc},
           # PLAN3 order rule "cycles on at least two different days": reported, not a reduction rule
           "info_days_of_kept_cycles_utc": {c: sorted({r["date_utc"] for r in passes[c] if r["kept"] and r["date_utc"]}) for c in allc},
           "idle_clocks": IC, "idle_clock_note": clock_note(IC, C),
           "constants": {"law": LAW, "sram_law_a2": SRAM_LAW_A2, "split_22sep": SPLIT_22SEP, "busy_80": BUSY_80, "T_L_grid": TL_GRID,
                         "bin_min_n": BIN_MIN_N, "cycle_cool_s": CYCLE_COOL_S, "idle_mhz": IDLE_MHZ, "idle_share_min": IDLE_SHARE_MIN},
           "items": items}
    with open(out_path, "w") as f:
        json.dump(res, f, indent=1, default=float)
    for it in items:
        print(f"{it['item']:7s} {it['outcome']:14s} all_cards {it['all_cards']['outcome']:14s} {it['reading']}")
    print(res["idle_clock_note"])
    return res


def check_pass(pdir):
    """Stdlib-only sanity check of one pass, run by block.sh at block end. Prints a one-line note (no double quotes);
    exit 1 if the pass cannot be used."""
    p = load_pass(pdir)
    cyc = p["cycle"]
    dry = bool(cyc.get("dry"))
    smoke = cyc.get("variant") == "smoke"
    L_ = p["launches"]
    he = p["marks"].get("heat_end", {})
    res = {"samples": len(p["samples"]), "bursts": len(L_), "burst_fail": sum(1 for x in L_ if x[2] != 0),
           "heat_reason": he.get("reason"), "heat_end_c": he.get("die_c"), "tmax": tmax(p)}
    problems, warnings = [], []
    if dry:
        note = f"dry run: {len(L_)} bursts logged, {res['heat_reason']}"
        json.dump({**res, "dry": True}, open(os.path.join(pdir, "check.json"), "w"))
        print(note)
        return 0
    if not p["samples"]:
        problems.append("no telemetry samples")
    if "cool_start" not in p["marks"] or "cool_end" not in p["marks"]:
        problems.append("no cool_start/cool_end mark")
    if not problems:
        cs, ce = p["marks"]["cool_start"]["t_ms"], p["marks"]["cool_end"]["t_ms"]
        cool = [s for s in p["samples"] if cs <= s[0] <= ce]
        ts = [s[0] for s in cool]
        gaps = [b - a for a, b in zip(ts, ts[1:])]
        res.update({"cool_s": round((ce - cs) / 1000.0, 1), "cool_samples": len(cool), "cool_max_gap_ms": max(gaps) if gaps else None,
                    "cool_T": [cool[0][1], cool[-1][1]] if cool else None,
                    "off600_cool": sum(1 for s in cool if s[3] != 600),
                    "rails_missing": sum(1 for s in cool if None in s[4:7])})
        # the idle clock of this pass: the cooling window's clock histogram (launch windows excluded; the whole cooling)
        h, mv = cool_clock_hist(p, cool_s=0)
        keep, drop, how = idle_clock_rule(p["card"], h)
        tot = sum(h.values())
        res.update({"idle_clock_hist_MHz": hist_json(h), "idle_mhz_used": keep, "idle_clock_rule": how,
                    "idle_share": round(h.get(keep, 0) / tot, 3) if tot else None, "idle_minion_mv_median": median(mv.get(keep, [])),
                    "idle_before_heating_mhz": p["marks"].get("cycle_start", {}).get("idle_mhz"),
                    "other_card_polls": p["marks"]["cool_end"].get("other_card_polls")})
        expect = cyc.get("cool_s", 0) * 10
        if len(cool) < 0.8 * expect:
            problems.append(f"only {len(cool)} cooling samples of {expect} expected")
        if res["rails_missing"] > 0.2 * max(1, len(cool)):
            problems.append("sp rails missing in the samples")
        if res["burst_fail"]:
            # a failed heater burst does not touch the idle samples (rule A drops every launch window, and block.sh
            # aborts after 3 failures in a row); it is noted, not a reason to lose the cycle
            warnings.append(f"{res['burst_fail']} heater bursts failed")
        if p["card"] not in CARDS and keep != IDLE_MHZ.get(p["card"], DEFAULT_IDLE_MHZ):
            warnings.append(f"idle clock {keep} MHz, not the expected {IDLE_MHZ.get(p['card'], DEFAULT_IDLE_MHZ)}")
        last_end = max((x[1] for x in L_), default=None)
        after = [s for s in cool if last_end is None or s[0] > last_end + 6000]
        res["idle_after_6s"] = len(after)
        if not after:
            problems.append("no sample 6 s after the last burst")
        if not smoke:
            # the registered cards: the registered rule; others: their idle clock (amendment A2)
            bins, cnt = rule_a_bins(p, keep_mhz=keep, drop=None if p["card"] in CARDS else drop)
            res["bins"] = sorted(bins)
            if not bins:
                problems.append("no whole-degree idle bin with n >= 20")
    json.dump({**res, "problems": problems, "warnings": warnings}, open(os.path.join(pdir, "check.json"), "w"))
    note = (f"{cyc.get('variant')}: {res['bursts']} bursts ({res['heat_reason']}), Tmax {res['tmax']} C; "
            f"cool {res.get('cool_s')} s, {res.get('cool_samples')} samples, max gap {res.get('cool_max_gap_ms')} ms, "
            f"T {res.get('cool_T')}, off600 {res.get('off600_cool')}"
            + (f", idle {res['idle_mhz_used']} MHz ({100 * res['idle_share']:.0f}%)" if res.get("idle_share") is not None else "")
            + (f", bins {res['bins'][0]}-{res['bins'][-1]}" if res.get("bins") else ""))
    if warnings:
        note += "; warning: " + "; ".join(warnings)
    if problems:
        note += "; PROBLEM: " + "; ".join(problems)
    print(note.replace('"', "'"))
    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data")
    ap.add_argument("--out")
    ap.add_argument("--check-pass")
    a = ap.parse_args()
    if a.check_pass:
        sys.exit(check_pass(a.check_pass))
    if not a.data or not a.out:
        ap.error("--data and --out are required (or --check-pass)")
    reduce_all(a.data, a.out)


if __name__ == "__main__":
    main()
