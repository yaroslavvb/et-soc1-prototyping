#!/usr/bin/env python3
"""V3-CAT helpers shared by block.sh's post-pass check and reduce.py (off-card only: reads files, never the card).

    python3 tools/claims-v3/cat/catlib.py check <pass-dir> --card <host> --root <tree root>
        writes <pass-dir>/check.json and prints "<status> <note>" (status ok | offclock | fail)

Per pass directory (one block): runs.jsonl[.gz] and telemetry.jsonl[.gz] as run_catalogue.py writes them, plus
marks.jsonl[.gz] (heater and prefill intervals), configs.json and pass.json from block.sh.
Bursts are cut by workloads/enercat/analyze_catalogue.py's own bursts_of() (unchanged, imported from the tree), one
directory at a time, so every pass has its own idle brackets. Drop rules, exactly as registered (PLAN3 V3-CAT and
R-clock), applied after bursts_of:
  - aifoundry2: a burst whose busy samples are not all at mhz.minion = 600 (mhz_busy_all_600 false: V3-CAT's
    registered sampler rule); or with any sample of its idle brackets (the before, rail-idle and after windows
    bursts_of averages, exactly as it cuts them) off 600 MHz (R-clock: "any sample at mhz.minion != 600"; the idle
    at 700-800 MHz is 5-9 W higher, which would enter the burst's over-idle power); or with a launch whose implied
    clock (cycles_max / wall_s) is outside 0.595-0.605 GHz (R-clock);
  - both cards: a burst whose idle brackets overlap a heater launch. The launch is padded -0.2 s before and +2.3 s
    after, the settling time analyze_catalogue itself leaves after a preceding burst (prev_hi + 2.3); the brackets
    are lo - 3.5 s .. hi + 5.5 s, the widest analyze_catalogue uses. run_catalogue_t10.py's --hold-after and
    --heat-settle keep this from happening; the rule only guards the brackets the registered reduction assumes idle.
Not a drop rule here: the sampler's latency (sampler_median_ms is reported; analyze_catalogue keeps slow bursts and
V3-CAT registered no starvation rule: the sampler-starvation rule of R-clock's header is registered by V3-WIRE and
V3-RL only).
"""
import argparse
import gzip
import importlib
import json
import math
import os
import re
import sys

import numpy as np

sys.dont_write_bytecode = True
A2, A3 = "aifoundry2", "aifoundry3"
CLOCK_LO, CLOCK_HI = 0.595, 0.605
HEAT_PAD_BEFORE, HEAT_PAD_AFTER = 0.2, 2.3   # s: a heater launch's reach (see the header)
_AC = {}


def analyzer(root):
    """workloads/enercat/analyze_catalogue.py of the tree at root, imported unchanged."""
    if root not in _AC:
        sys.path.insert(0, os.path.join(root, "workloads", "enercat"))
        _AC[root] = importlib.import_module("analyze_catalogue")
        sys.path.pop(0)
    return _AC[root]


def jl(path):
    if os.path.exists(path + ".gz"):
        return [json.loads(l) for l in gzip.open(path + ".gz", "rt") if l.startswith("{")]
    if os.path.exists(path):
        return [json.loads(l) for l in open(path) if l.startswith("{")]
    return []


def jload(path, default=None):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return default


def load_block_json(path):
    """block.json as lib.sh's block_end writes it. When die_c comes back empty, block_end prints "die_c_end":,
    (invalid JSON); read such a file with the empty fields as null rather than lose the pass."""
    try:
        txt = open(path).read()
    except OSError:
        return None
    try:
        return json.loads(txt)
    except ValueError:
        try:
            return json.loads(re.sub(r'":\s*(?=[,}])', '":null', txt))
        except ValueError:
            return None


def value(b):
    """The catalogue's energy: pJ per byte for byte configurations, pJ per operation otherwise."""
    return b["pj_per_byte"] if b["bytes"] else b["pj_per_op"]


def pass_bursts(d, card, root):
    """(kept bursts, dropped [{cfg, why}], expected cfgs, info) for one pass directory."""
    ac = analyzer(root)
    tel, runs = jl(os.path.join(d, "telemetry.jsonl")), jl(os.path.join(d, "runs.jsonl"))
    marks = jl(os.path.join(d, "marks.jsonl"))
    cj = jload(os.path.join(d, "configs.json"), {}) or {}
    expected = [c["cfg"] for c in cj.get("cfgs", [])]
    info = {"n_tel": len(tel), "n_runs": len(runs), "cfgs_with_runs": len({r["cfg"] for r in runs})}
    if len(tel) < 50 or not runs:
        return [], [], expected, info
    bursts = ac.bursts_of(tel, runs)[0]
    # the time axis and the burst spans exactly as bursts_of builds them (computed here, so an older copy of
    # analyze_catalogue.py with a different return tuple on the other host cannot break the check)
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    grp = {}
    for r in runs:
        grp.setdefault((r["cfg"], r["pass"]), []).append(r)
    spans = sorted((min(r["t_start_ms"] for r in rs) / 1000.0, max(r["t_end_ms"] for r in rs) / 1000.0) for rs in grp.values())
    los = np.array([s[0] for s in spans])
    info["samples_off_600"] = int((mhz != 600).sum())
    by_cfg = {}
    for r in runs:
        by_cfg.setdefault(r["cfg"], []).append(r)
    heat = [(m["t_start_ms"] / 1000.0 - HEAT_PAD_BEFORE, m["t_end_ms"] / 1000.0 + HEAT_PAD_AFTER)
            for m in marks if m.get("kind") == "heater"]
    kept, dropped = [], []
    cut = {b["cfg"] for b in bursts}
    for cfg in sorted(set(by_cfg) - cut):
        dropped.append({"cfg": cfg, "why": "too few telemetry samples in the burst or its brackets (bursts_of)"})
    for b in bursts:
        clk = [r["cycles_max"] / r["wall_s"] / 1e9 for r in by_cfg[b["cfg"]] if r.get("wall_s")]
        b["implied_ghz_min"] = float(min(clk)) if clk else None
        b["implied_ghz_max"] = float(max(clk)) if clk else None
        # the idle samples bursts_of averaged for this burst, cut exactly as it cuts them
        lo, hi = b["t_lo"], b["t_hi"]
        i = int(np.searchsorted(los, lo))
        prev_hi = spans[i - 1][1] if i > 0 else t[0]
        next_lo = spans[i + 1][0] if i + 1 < len(spans) else t[-1]
        idle = (((t >= max(prev_hi + 2.3, lo - 3.5)) & (t <= lo - 0.3)) | ((t >= hi + 2.3) & (t <= min(next_lo - 0.3, hi + 5.5))))
        b["mhz_idle_all_600"] = bool((mhz[idle] == 600).all())
        why = None
        if card == A2 and not b["mhz_busy_all_600"]:
            why = "clock left 600 MHz (busy samples)"
        elif card == A2 and not b["mhz_idle_all_600"]:
            why = "clock left 600 MHz (idle-bracket samples, R-clock)"
        elif card == A2 and clk and not all(CLOCK_LO <= g <= CLOCK_HI for g in clk):
            why = f"implied clock outside {CLOCK_LO}-{CLOCK_HI} GHz"
        elif any(h0 < hi + 5.5 and h1 > lo - 3.5 for h0, h1 in heat):
            why = "heater launch inside the idle brackets"
        if why:
            dropped.append({"cfg": b["cfg"], "why": why})
        else:
            b["value"] = value(b)
            kept.append(b)
    info["heater_launches"] = len(heat)
    return kept, dropped, expected, info


# ---------------- statistics (no scipy on the lab hosts) ----------------
def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d; d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(c) > 1e-300 else 1e300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d; d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(c) > 1e-300 else 1e300
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-14:
            break
    return h


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_p2(t, df):
    """Two-sided p of |T| >= |t| with df degrees of freedom."""
    return betainc(df / 2.0, 0.5, df / (df + t * t))


def t_crit(df, conf=0.99):
    """Two-sided critical value: P(|T| > c) = 1 - conf."""
    lo, hi = 0.0, 1e4
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_p2(mid, df) > 1 - conf:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def f_sf(F, d1, d2):
    """P(F' >= F) for F(d1, d2)."""
    if F <= 0:
        return 1.0
    return betainc(d2 / 2.0, d1 / 2.0, d2 / (d2 + d1 * F))


def welch(a, b, conf=0.99):
    """Welch interval for mean(a) - mean(b); None when a group has fewer than 2 values."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2:
        return None
    d = float(a.mean() - b.mean())
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    se = math.sqrt(va + vb)
    if se == 0:
        return {"diff": d, "se": 0.0, "df": None, "lo": d, "hi": d, "p": 0.0 if d else 1.0, "n": [len(a), len(b)]}
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    h = t_crit(df, conf) * se
    return {"diff": d, "se": se, "df": df, "lo": d - h, "hi": d + h, "p": t_p2(d / se, df), "n": [len(a), len(b)]}


def anova1(groups):
    """One-way ANOVA: F, df and p over the groups (lists of values)."""
    g = [np.asarray(x, float) for x in groups]
    allv = np.concatenate(g)
    gm = allv.mean()
    ssb = sum(len(x) * (x.mean() - gm) ** 2 for x in g)
    ssw = sum(((x - x.mean()) ** 2).sum() for x in g)
    d1, d2 = len(g) - 1, len(allv) - len(g)
    if d2 <= 0:
        return None
    if ssw == 0:
        return {"F": float("inf") if ssb else 0.0, "df": [d1, d2], "p": 0.0 if ssb else 1.0}
    F = (ssb / d1) / (ssw / d2)
    return {"F": float(F), "df": [d1, d2], "p": float(f_sf(F, d1, d2))}


def rnd(x, nd=4):
    if isinstance(x, dict):
        return {k: rnd(v, nd) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rnd(v, nd) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if (math.isnan(x) or math.isinf(x)) else round(float(x), nd)
    if isinstance(x, np.integer):
        return int(x)
    return x


def check(d, card, root):
    """block.sh's post-pass check: writes check.json, returns (status, note)."""
    kept, dropped, expected, info = pass_bursts(d, card, root)
    runs = jl(os.path.join(d, "runs.jsonl"))
    have = {r["cfg"] for r in runs}
    missing = [c for c in expected if c not in have]
    off = [x for x in dropped if "clock" in x["why"]]
    pj = jload(os.path.join(d, "pass.json"), {}) or {}
    hold = pj.get("hold_c")
    res = {"card": card, "expected": len(expected), "missing": missing, "kept": len(kept), "dropped": dropped, **info,
           "die_c_busy_mean": rnd(float(np.mean([b["die_c_busy"] for b in kept]))) if kept else None,
           "die_c_before_min": rnd(float(min(b["die_c_before"] for b in kept))) if kept else None,
           "die_c_before_max": rnd(float(max(b["die_c_before"] for b in kept))) if kept else None,
           "sampler_median_ms": rnd(float(np.median([b["sampler_median_ms"] for b in kept]))) if kept else None,
           "sampler_over_60ms": sum(1 for b in kept if b["sampler_median_ms"] > 60)}
    if hold is not None and kept:
        res["hold_c"] = hold
        res["frac_before_at_hold"] = rnd(float(np.mean([b["die_c_before"] >= hold - 1 for b in kept])))
    if info["n_tel"] < 50 or not runs or len(missing) > len(expected) // 2:
        st, note = "fail", (f"no data (telemetry lines {info['n_tel']}, launches {len(runs)}, "
                            f"{len(missing)} of {len(expected)} configurations without a launch)")
    elif card == A2 and off:
        st, note = "offclock", f"{len(off)} bursts off 600 MHz: re-run this pass (R-clock); reduce.py drops those bursts"
    elif missing:
        # a launch that failed once (the burst process printed no ENERCAT line): the rest of the pass is good data,
        # so reduce.py uses it; the queue treats it as not done and re-runs it if the schedule is run again
        st, note = "partial", f"{len(missing)} of {len(expected)} configurations have no launch: {','.join(missing)[:200]}"
    else:
        st = "ok"
        note = (f"{len(kept)}/{len(expected)} bursts kept, die {res['die_c_busy_mean']} C busy"
                + (f", {len(dropped)} dropped" if dropped else ""))
    res.update({"status": st, "note": note})
    json.dump(res, open(os.path.join(d, "check.json"), "w"), indent=1)
    return st, note


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check"])
    ap.add_argument("dir")
    ap.add_argument("--card", required=True)
    ap.add_argument("--root", required=True)
    a = ap.parse_args()
    st, note = check(a.dir, a.card, a.root)
    print(f"{st} {note}")
