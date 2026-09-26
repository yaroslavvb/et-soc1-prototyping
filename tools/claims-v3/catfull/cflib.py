#!/usr/bin/env python3
"""V3-CATFULL helpers shared by block.sh and reduce.py (off-card only: they read files, never the card).

    python3 tools/claims-v3/catfull/cflib.py plan --root <tree> --pass K --part S [--parts 3]
        the part's configurations and seeds as JSON (the pass's shuffle, cut into parts)
    python3 tools/claims-v3/catfull/cflib.py plan --root <tree> --smoke
        the smoke's three configurations
    python3 tools/claims-v3/catfull/cflib.py missing <block-dir>
        the configurations of the block's configs.json with no launch in its runs.jsonl (comma list; empty if none)
    python3 tools/claims-v3/catfull/cflib.py check <block-dir> --card <id> --gov-free 0|1 --root <tree>
        the post-block check: writes <block-dir>/check.json and prints "<status> <note>" (ok | offclock | partial | fail)

The catalogue is workloads/enercat/run_catalogue.py's configs() (imported from the tree, never copied), minus the two
dramrow/stride256K configurations (EXCLUDED below). A pass is the whole catalogue once; its order is
random.Random(40<K>).shuffle over the catalogue, cut into PARTS consecutive parts of equal count, one block per part;
tools/claims-v3/cat/run_catalogue_t10.py runs a part with --seed 40<K><S> (its own shuffle inside the part).

Bursts are cut by workloads/enercat/analyze_catalogue.py's own bursts_of() (imported unchanged), one block directory
at a time, so every part has its own idle brackets. Drop rules (catfull's amendment; decided before any data):
  - governor-free cards (every card except aifoundry3; lib.sh GOV_FREE): a burst whose BUSY samples (bursts_of's
    busy window, lo + 0.5 s .. hi) are not all at mhz.minion = 600 (bursts_of's mhz_busy_all_600), or one of whose
    launches has an implied clock cycles_max / wall_s outside 0.595-0.605 GHz (as V3-CAT's R-clock rule). The idle
    brackets are never tested: aifoundry1 card 0 (firmware 1.4.1) idles in its low_power state at 300 MHz between
    kernels, so its brackets are off 600 MHz by design. One exception to the launch rule: when the idle bracket
    BEFORE the burst is not all at 600 MHz (the card was in another idle state), the burst's first launch is recorded
    (first_launch_ghz, first_launch_tested false) but not tested, because it carries the wake-up from that state;
    on a card that idled at 600 MHz every launch is tested (the 23 Sep first launches: 0.598-0.600 GHz on both cards).
    A bracket's clock never drops a burst;
  - aifoundry3 (pinned at 600 MHz by its boot service): no clock rule; its clocks are recorded all the same;
  - every card: a burst bursts_of cannot cut (too few samples), and a burst whose brackets (lo - 3.5 .. hi + 5.5 s)
    overlap a heater launch in marks.jsonl padded -0.2/+2.3 s (catfull runs no heater inside a part: a guard only).
Every burst records the clock of its idle brackets (idle_mhz: "600", "300", another single value, or "mixed:a/b"),
the fraction of those samples at 600 MHz, and its busy clock; the block's check.json and the reducer report them.
"""
import argparse
import gzip
import importlib
import json
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict

import numpy as np

sys.dont_write_bytecode = True

PARTS = 3
EXCLUDED_PREFIXES = ("dramrow/stride256K/",)
EXCLUDED_WHY = ("2,048 slices of 8 MB each (16.4 GB of card DRAM, and the host fills the same 16 GB in its own memory "
                "first); on 23 Sep they printed no launch on either card, so the catalogue has no value for them")
SMOKE_CFGS = ["fmul.ps/random/h2", "tload/scp/random", "dramrow2/seq/random"]   # compute, prefill, --jump-every
CLOCK_MHZ = 600
CLOCK_LO, CLOCK_HI = 0.595, 0.605
HEAT_PAD_BEFORE, HEAT_PAD_AFTER = 0.2, 2.3
PINNED = {"aifoundry3"}                     # lib.sh: GOV_FREE is empty on aifoundry3 only
REGISTERED = ["aifoundry2", "aifoundry3"]   # the two cards of the committed 23 Sep catalogue
FOUR_CARDS = ["aifoundry1-c0", "aifoundry1-c1", "aifoundry2", "aifoundry3"]
REFERENCE = "aifoundry2"                    # the committed catalogue's ratios are aifoundry3 / aifoundry2
_MOD = {}


def seed_pass(k):
    return int(f"40{k}")


def seed_run(k, s):
    return int(f"40{k}{s}")


def gov_free(card):
    return card not in PINNED


def _import(root, name):
    key = (root, name)
    if key not in _MOD:
        sys.path.insert(0, os.path.join(root, "workloads", "enercat"))
        try:
            _MOD[key] = importlib.import_module(name)
        finally:
            sys.path.pop(0)
    return _MOD[key]


def analyzer(root):
    """workloads/enercat/analyze_catalogue.py of the tree at root, imported unchanged."""
    return _import(root, "analyze_catalogue")


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
    """block.json as lib.sh's block_end writes it; an empty die reading ("die_c_end":,) is read as null."""
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
    """The catalogue's energy: pJ per byte for byte configurations, pJ per operation otherwise (as analyze_catalogue)."""
    return b["pj_per_byte"] if b["bytes"] else b["pj_per_op"]


def clock_state(mhz_values):
    """"600", "300", another single value, "mixed:a/b" (several clocks), or "none" (no samples)."""
    u = sorted({int(v) for v in mhz_values})
    if not u:
        return "none"
    return str(u[0]) if len(u) == 1 else "mixed:" + "/".join(str(v) for v in u)


# ---------------- the plan: which configurations a block runs ----------------
def catalogue(root):
    """(every configuration of run_catalogue.configs(), the ones catfull runs, the excluded ones)."""
    rc = _import(root, "run_catalogue")
    allc = [c["cfg"] for c in rc.configs()]
    excluded = [n for n in allc if n.startswith(EXCLUDED_PREFIXES)]
    return allc, [n for n in allc if n not in excluded], excluded


def plan(root, k=0, s=0, parts=PARTS, smoke=False):
    allc, names, excluded = catalogue(root)
    if smoke:
        bad = [n for n in SMOKE_CFGS if n not in names]
        if bad:
            raise SystemExit(f"smoke configurations not in the catalogue: {bad}")
        sel, sp, sr = list(SMOKE_CFGS), None, 1
    else:
        if not (1 <= k <= 9 and 1 <= s <= parts):
            raise SystemExit(f"pass {k} part {s}: need pass 1-9 and part 1-{parts}")
        order = list(range(len(names)))
        sp, sr = seed_pass(k), seed_run(k, s)
        random.Random(sp).shuffle(order)
        cut = [round(i * len(names) / parts) for i in range(parts + 1)]
        sel = [names[i] for i in order[cut[s - 1]:cut[s]]]
    # the runner selects by prefix: every name must select itself and nothing else
    amb = [n for n in sel if sum(1 for m in allc if m.startswith(n)) != 1]
    if amb:
        raise SystemExit(f"names that do not select exactly one configuration: {amb}")
    return {"pass": k, "part": s, "parts": parts, "smoke": smoke, "seed_pass": sp, "seed_run": sr, "n": len(sel),
            "n_total": len(names), "n_catalogue": len(allc), "excluded": excluded, "excluded_why": EXCLUDED_WHY,
            "names": sel}


def missing(d):
    cj = jload(os.path.join(d, "configs.json"), {}) or {}
    have = {r["cfg"] for r in jl(os.path.join(d, "runs.jsonl"))}
    return [c["cfg"] for c in cj.get("cfgs", []) if c["cfg"] not in have]


# ---------------- bursts of one block ----------------
def pass_bursts(d, gov, root):
    """(kept bursts, dropped [{cfg, why, kind}], expected cfgs, info, rail-fall curves) for one block directory."""
    ac = analyzer(root)
    tel, runs = jl(os.path.join(d, "telemetry.jsonl")), jl(os.path.join(d, "runs.jsonl"))
    marks = jl(os.path.join(d, "marks.jsonl"))
    cj = jload(os.path.join(d, "configs.json"), {}) or {}
    expected = [c["cfg"] for c in cj.get("cfgs", [])]
    have = {r["cfg"] for r in runs}
    info = {"n_tel": len(tel), "n_runs": len(runs), "cfgs_with_runs": len(have),
            "missing": [c for c in expected if c not in have]}
    if len(tel) < 50 or not runs:
        return [], [], expected, info, []
    res = ac.bursts_of(tel, runs)
    bursts = res[0] if isinstance(res, tuple) else res
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    w = np.array([s["board_w"] for s in tel], float)
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    grp = defaultdict(list)
    for r in runs:
        grp[(r["cfg"], r["pass"])].append(r)
    spans = sorted((min(r["t_start_ms"] for r in rs) / 1000.0, max(r["t_end_ms"] for r in rs) / 1000.0) for rs in grp.values())
    los = np.array([s[0] for s in spans])
    info["samples_off_600"] = int((mhz != CLOCK_MHZ).sum())
    # the runner's lead: idle before the first configuration (after the heater, before any prefill or burst)
    first = min([spans[0][0]] + [m["t_start_ms"] / 1000.0 for m in marks]) if spans else t[-1]
    lead = t <= first - 0.3
    info["lead_mhz"] = clock_state(mhz[lead])
    info["lead_w"] = float(w[lead].mean()) if lead.any() else None
    heat = [(m["t_start_ms"] / 1000.0 - HEAT_PAD_BEFORE, m["t_end_ms"] / 1000.0 + HEAT_PAD_AFTER)
            for m in marks if m.get("kind") == "heater"]
    kept, dropped = [], []
    cut = {(b["cfg"], b["pass"]) for b in bursts}
    for key in sorted(set(grp) - cut):
        dropped.append({"cfg": key[0], "why": "too few telemetry samples in the burst or its brackets (bursts_of)", "kind": "cut"})
    idle_union = np.zeros(len(t), bool)
    for b in bursts:
        rs = sorted(grp[(b["cfg"], b["pass"])], key=lambda r: r["t_start_ms"])
        clk = [r["cycles_max"] / r["wall_s"] / 1e9 for r in rs if r.get("wall_s")]
        lo, hi = b["t_lo"], b["t_hi"]
        i = int(np.searchsorted(los, lo))
        prev_hi = spans[i - 1][1] if i > 0 else t[0]
        next_lo = spans[i + 1][0] if i + 1 < len(spans) else t[-1]
        before = (t >= max(prev_hi + 2.3, lo - 3.5)) & (t <= lo - 0.3)          # bursts_of's windows, cut as it cuts them
        after = (t >= hi + 2.3) & (t <= min(next_lo - 0.3, hi + 5.5))
        idle = before | after if after.sum() >= 4 else before
        idle_union |= idle
        busy = (t >= lo + 0.5) & (t <= hi)
        # the first launch is tested unless the card came out of another idle state just before the burst
        before_600 = bool(before.any() and (mhz[before] == CLOCK_MHZ).all())
        tested = clk if before_600 else clk[1:]
        b["first_launch_ghz"] = float(clk[0]) if clk else None
        b["first_launch_tested"] = before_600
        b["implied_ghz_min"] = float(min(tested)) if tested else None
        b["implied_ghz_max"] = float(max(tested)) if tested else None
        b["idle_before_mhz"] = clock_state(mhz[before])
        b["idle_mhz"] = clock_state(mhz[idle])
        b["idle_frac_600"] = float((mhz[idle] == CLOCK_MHZ).mean()) if idle.any() else None
        b["busy_mhz"] = clock_state(mhz[busy])
        b["busy_off_600"] = int((mhz[busy] != CLOCK_MHZ).sum())
        why, kind = None, None
        if gov and not b["mhz_busy_all_600"]:
            why, kind = f"clock off 600 MHz in busy samples ({b['busy_mhz']} MHz)", "clock"
        elif gov and tested and not all(CLOCK_LO <= g <= CLOCK_HI for g in tested):
            why, kind = (f"implied clock of a launch{'' if before_600 else ' after the first'} outside "
                         f"{CLOCK_LO}-{CLOCK_HI} GHz ({min(tested):.4f}-{max(tested):.4f})"), "clock"
        elif any(h0 < hi + 5.5 and h1 > lo - 3.5 for h0, h1 in heat):
            why, kind = "heater launch inside the idle brackets", "heater"
        if why:
            dropped.append({"cfg": b["cfg"], "why": why, "kind": kind, "idle_mhz": b["idle_mhz"], "busy_mhz": b["busy_mhz"]})
        else:
            b["value"] = value(b)
            kept.append(b)
    info["idle_mhz_hist"] = {str(k): int(v) for k, v in sorted(Counter(int(x) for x in mhz[idle_union]).items())}
    info["idle_w_by_mhz"] = {str(k): float(w[idle_union & (mhz == k)].mean()) for k in sorted(set(int(x) for x in mhz[idle_union]))}
    info["heater_launches"] = len(heat)
    curves = []
    if isinstance(res, tuple) and len(res) >= 3 and kept and hasattr(ac, "rail_fall_curves"):
        try:
            curves = ac.rail_fall_curves(kept, res[1], res[2])
        except Exception:   # an older analyze_catalogue on another host: the rail filter is optional
            curves = []
    return kept, dropped, expected, info, curves


# ---------------- statistics (no scipy on the lab hosts; as tools/claims-v3/cat/catlib.py) ----------------
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
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_p2(t, df):
    return betainc(df / 2.0, 0.5, df / (df + t * t))


def t_crit(df, conf=0.99):
    lo, hi = 0.0, 1e4
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_p2(mid, df) > 1 - conf:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


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


def rnd(x, nd=4):
    if isinstance(x, dict):
        return {k: rnd(v, nd) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rnd(v, nd) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if (math.isnan(x) or math.isinf(x)) else round(float(x), nd)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


# ---------------- the post-block check ----------------
def check(d, card, gov, root):
    kept, dropped, expected, info, _ = pass_bursts(d, gov, root)
    miss = info["missing"]
    clock = [x for x in dropped if x["kind"] == "clock"]
    retry = jload(os.path.join(d, "retry", "configs.json"), None)
    res = {"card": card, "gov_free": bool(gov), "expected": len(expected), "missing": miss, "kept": len(kept),
           "dropped": dropped, **info,
           "retried": [c["cfg"] for c in retry.get("cfgs", [])] if retry else [],
           "idle_mhz_bursts": dict(Counter(b["idle_mhz"] for b in kept)),
           "busy_mhz_bursts": dict(Counter(b["busy_mhz"] for b in kept)),
           "first_launch_ghz_min": rnd(min((b["first_launch_ghz"] for b in kept if b["first_launch_ghz"]), default=None)),
           "first_launch_untested": sum(1 for b in kept if not b["first_launch_tested"]),
           "die_c_busy_mean": rnd(float(np.mean([b["die_c_busy"] for b in kept]))) if kept else None,
           "die_c_before_min": rnd(float(min(b["die_c_before"] for b in kept))) if kept else None,
           "die_c_before_max": rnd(float(max(b["die_c_before"] for b in kept))) if kept else None,
           "sampler_median_ms": rnd(float(np.median([b["sampler_median_ms"] for b in kept]))) if kept else None,
           "sampler_over_60ms": sum(1 for b in kept if b["sampler_median_ms"] > 60)}
    if info["n_tel"] < 50 or not info["n_runs"] or len(miss) > len(expected) // 2:
        st, note = "fail", (f"no data (telemetry lines {info['n_tel']}, launches {info['n_runs']}, "
                            f"{len(miss)} of {len(expected)} configurations without a launch)")
    elif gov and clock:
        st, note = "offclock", (f"{len(clock)} bursts off 600 MHz while busy: re-run this part; reduce.py drops those "
                                f"bursts ({clock[0]['why']})")
    elif miss:
        st, note = "partial", f"{len(miss)} of {len(expected)} configurations have no launch: {','.join(miss)[:200]}"
    else:
        st = "ok"
        note = f"{len(kept)}/{len(expected)} bursts kept, die {res['die_c_busy_mean']} C busy" + (
            f", {len(dropped)} dropped" if dropped else "")
    idle = ",".join(f"{k}:{v}" for k, v in sorted(res["idle_mhz_bursts"].items()))
    note += f"; idle brackets {idle or 'none'} MHz"
    res.update({"status": st, "note": note})
    json.dump(rnd(res), open(os.path.join(d, "check.json"), "w"), indent=1)
    return st, note


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "missing", "check"])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--root")
    ap.add_argument("--pass", dest="k", type=int, default=0)
    ap.add_argument("--part", dest="s", type=int, default=0)
    ap.add_argument("--parts", type=int, default=PARTS)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--card")
    ap.add_argument("--gov-free", type=int, choices=[0, 1])
    a = ap.parse_args()
    if a.cmd == "plan":
        print(json.dumps(plan(a.root, a.k, a.s, a.parts, a.smoke)))
    elif a.cmd == "missing":
        print(",".join(missing(a.dir)))
    else:
        if a.card is None or a.gov_free is None or not a.root:
            raise SystemExit("check needs --card, --gov-free and --root")
        st, note = check(a.dir, a.card, a.gov_free, a.root)
        print(f"{st} {note}")
