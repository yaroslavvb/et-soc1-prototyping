#!/usr/bin/env python3
"""V3-RL reducer: the pre-registered prediction items RL-a .. RL-h, RL-X3 and RL-X4 of PLAN3 (section 2, V3-RL).

    python3 tools/claims-v3/rl/reduce.py --data <dir> --out <verdicts.json> [--flop <flop.json>] [--no-legacy]

<dir> holds aifoundry2/ and aifoundry3/, each laid out like DATA_ROOT: <card>/rl/p<K>/{A,B,relay}/ written by
block.sh (telemetry.jsonl[.gz], runs.jsonl), with block.json and pass.json. Either card, and any number of passes,
may be missing: an item without enough kept repeats says INSUFFICIENT.

Reduction (as registered):
  * every burst is reduced by a verbatim copy of tools/ettelem/analyze_reruns.reduce_dir (bracketing idle,
    leakage-corrected); a burst is dropped when the minion clock left 600 MHz in > 2% of its samples or the
    sampler's median latency was > 60 ms (V3-RL sampler rule); an aifoundry2 pass with ANY telemetry sample off
    600 MHz is dropped whole (PLAN3 common rules: such aifoundry2 repeats are dropped and re-run; aifoundry3 is
    pinned and has only the burst rule); only passes whose block.json says "ok" are used (failed passes are
    re-run by scheduling them again);
  * the unit is the pass; 99% t intervals on pass-level values; Welch between cards; >= 3 kept passes per card
    (per contents group for RL-h) or the item is INSUFFICIENT;
  * decisions use the new passes only, except RL-X4, whose byte side pools the 23 Sep rl-passes (committed under
    docs/reports/data/2026-09-23-reruns-*) with the new ones, as registered; its FLOP side comes from V3-ABL-A
    through --flop (see README.md for the format).

Outcomes: PASS (the claim holds on both cards, or on the one card the rule names), FAIL, CARD-DIFFERENT,
INSUFFICIENT. "prediction_held" separately says whether the registered numbers (bands) came true; a failed
prediction is reported as failed and the page takes the measured value.
"""
import argparse
import glob
import gzip
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A2, A3 = "aifoundry2", "aifoundry3"
CARDS = (A2, A3)
NMIN = 3          # PLAN3 common rules: fewer than 3 kept repeats on a card leaves the claim as it is
CLOCK_FRAC, STARVED_MS = 0.02, 60.0   # V3-RL burst drop rule
# Mean hops of the xshire:K rings (workloads/nocbench/analyze.py hops over s -> s+K, as reruns_perpass.py computed)
HOPS = {"xshire8": 1.625, "xshire16": 2.125, "xshire1": 3.5, "xshire4": 3.6875, "xshire2": 4.5, "xshire6": 4.6875}
FIVE = ["xshire8", "xshire1", "xshire4", "xshire2", "xshire6"]   # the five 1 KB cross-shire rings (xshire16 starves a2)
RINGS = ["pair", "neigh", "shire", "xshire1", "xshire16", "xshire8", "xshire2", "xshire4", "xshire6", "shire-c4", "xshire1-c4"]
INSIDE = ["pair", "neigh", "shire"]
LEVELS = ["l1", "l2", "scp-local", "l3", "dram", "scp-remote"]
MEDIA = ["dram", "scp", "hop"]

# ---------------------------------------------------------------- statistics (scipy is not installed on the hosts)


def _betacf(a, b, x, itmax=500, eps=3e-14):
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
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def _betainc(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    return bt * _betacf(a, b, x) / a if x < (a + 1) / (a + b + 2) else 1.0 - bt * _betacf(b, a, 1 - x) / b


def t_sf(t, df):
    p = 0.5 * _betainc(df / 2, 0.5, df / (df + t * t))
    return p if t >= 0 else 1 - p


def t_ppf(q, df):
    lo, hi = -1e4, 1e4
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if 1 - t_sf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def tcrit(df):
    return t_ppf(0.995, df)


def summ(pv):
    """pv: list of (pass, value). Mean, sd, se and the 99% t interval over the passes."""
    pv = [(p, float(v)) for p, v in pv if v is not None and np.isfinite(v)]
    v = np.array([x for _, x in pv], float)
    out = {"n": len(v), "passes": [p for p, _ in pv], "values": [float(x) for x in v]}
    if len(v):
        out["mean"] = round(float(v.mean()), 4)
    if len(v) >= 2:
        sd = float(v.std(ddof=1)); se = sd / math.sqrt(len(v)); h = tcrit(len(v) - 1) * se
        out.update(sd=round(sd, 4), se=round(se, 4), ci99=[round(float(v.mean()) - h, 4), round(float(v.mean()) + h, 4)])
    return out


def welch(a, b):
    """a - b on repeat-level values: Welch 99% interval and two-sided p."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2:
        return None
    d = float(a.mean() - b.mean())
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    se = math.sqrt(va + vb)
    if se == 0:
        return {"diff": d, "se": 0.0, "df": None, "ci99": [d, d], "p": 0.0 if d else 1.0}
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    h = tcrit(df) * se
    return {"diff": round(d, 4), "se": round(se, 4), "df": round(df, 2), "ci99": [round(d - h, 4), round(d + h, 4)],
            "p": float(2 * t_sf(abs(d) / se, df))}


def r2(xs):
    return [round(x, 2) for x in xs]


def excl0(ci):
    return ci is not None and (ci[0] > 0 or ci[1] < 0)


def vals(s):
    return np.array(s["values"], float)


def inband(x, lo, hi):
    return x is not None and lo <= x <= hi

# ---------------------------------------------------------------- burst reduction


A_LEAK_80, T_L = 23.257, 36.0


def leak_slope(T):
    return A_LEAK_80 / T_L * math.exp((T - 80.0) / T_L)


def _open(tp):
    return gzip.open(tp + ".gz", "rt") if os.path.exists(tp + ".gz") else open(tp)


def reduce_dir(pd, variant="std"):
    """Verbatim copy of tools/ettelem/analyze_reruns.reduce_dir (variant "std"), plus the robustness variants of
    validate3/verify-memhier-onchip/rl.py: "noleak" (bracketing idle, no leakage term), "before" (idle before only)."""
    tp = os.path.join(pd, "telemetry.jsonl")
    tel = [json.loads(l) for l in _open(tp) if l.startswith("{")]
    runs = [json.loads(l) for l in open(os.path.join(pd, "runs.jsonl"))]
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    w = np.array([s["board_w"] for s in tel])
    T = np.array([s["temp_c"]["minshire"][0] for s in tel])
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    took = np.array([s.get("took_ms", 0) for s in tel])
    labels = []
    for r in runs:
        if r["label"] not in labels:
            labels.append(r["label"])
    spans = {lab: (min(r["t_start_ms"] for r in runs if r["label"] == lab) / 1000.0,
                   max(r["t_end_ms"] for r in runs if r["label"] == lab) / 1000.0) for lab in labels}
    out = {}
    for i, lab in enumerate(labels):
        lo, hi = spans[lab]
        busy = (t >= lo + 0.5) & (t <= hi)
        prev_hi = spans[labels[i - 1]][1] if i else t[0]
        next_lo = spans[labels[i + 1]][0] if i + 1 < len(labels) else t[-1]
        before = (t >= max(prev_hi + 3.0, lo - 6.0)) & (t <= lo - 0.3)
        after = (t >= hi + 3.0) & (t <= min(next_lo - 0.3, hi + 8.0))
        if busy.sum() < 5 or before.sum() < 5:
            continue
        moved = float((mhz[busy | before | after] != 600).mean())
        starved = float(np.median(took[busy])) if busy.sum() else 0.0
        if variant == "before" or after.sum() < 5:
            idle = float(w[before].mean())
        else:
            idle = 0.5 * (float(w[before].mean()) + float(w[after].mean()))
        Tb = float(T[busy].mean())
        Ti = float(np.concatenate([T[before], T[after]]).mean()) if (after.sum() >= 5 and variant != "before") else float(T[before].mean())
        over = float(w[busy].mean()) - idle - (leak_slope(0.5 * (Tb + Ti)) * (Tb - Ti) if variant == "std" else 0.0)
        rs = [r for r in runs if r["label"] == lab]
        out[lab] = {"over_idle_w": over, "wall_s": hi - lo, "runs": rs, "die_c": Tb, "clock_moved_frac": moved, "sampler_median_ms": starved}
    return out


def telemetry_off600(pd):
    tp = os.path.join(pd, "telemetry.jsonl")
    if not (os.path.exists(tp) or os.path.exists(tp + ".gz")):
        return 0, 0
    n = off = 0
    for l in _open(tp):
        if l.startswith("{"):
            n += 1
            try:
                off += json.loads(l)["mhz"]["minion"] != 600
            except (KeyError, ValueError, TypeError):
                off += 1
    return n, off


def has_data(pd):
    tp = os.path.join(pd, "telemetry.jsonl"); rp = os.path.join(pd, "runs.jsonl")
    if not os.path.exists(rp) or os.path.getsize(rp) == 0:
        return False
    if os.path.exists(tp + ".gz"):
        return True
    return os.path.exists(tp) and os.path.getsize(tp) > 0


def pj(b):
    total = sum(r.get("bytes", 0) for r in b["runs"])
    return b["over_idle_w"] * b["wall_s"] / total * 1e12 if total else None


def base_label(lab):
    """ABBA / bracket labels to their configuration: l2-1 -> l2, scp-local-2 -> scp-local, nspin-first -> nspin."""
    m = re.match(r"^(.*?)-(1|2|first|last)$", lab)
    return m.group(1) if m and m.group(1) in ("l2", "scp-local", "nspin", "mspin") else lab


def pass_values(halves, dropped, where, variant="std"):
    """Per-pass values from the reduced halves {A: bursts, B: bursts, relay: bursts}; a legacy rl-pass (rings and
    levels under one sampler) comes as the single half "AB"."""
    V = {"ring_pj": {}, "ring_w": {}, "level_pj": {}, "relay_pj": {}, "bursts": {}}
    group = {}
    for half, bursts in halves.items():
        for lab, b in bursts.items():
            key = f"{half}:{lab}"
            info = {"over_idle_w": round(b["over_idle_w"], 4), "pj_per_byte": None if pj(b) is None else round(pj(b), 4),
                    "clock_moved_frac": round(b["clock_moved_frac"], 4), "sampler_median_ms": b["sampler_median_ms"],
                    "die_c": round(b["die_c"], 2)}
            if b["clock_moved_frac"] > CLOCK_FRAC or b["sampler_median_ms"] > STARVED_MS:
                info["dropped"] = True
                if variant == "std":
                    dropped.append({"where": where, "burst": key, "clock_moved_frac": round(b["clock_moved_frac"], 4),
                                    "sampler_median_ms": b["sampler_median_ms"]})
                V["bursts"][key] = info
                continue
            V["bursts"][key] = info
            base = base_label(lab)
            if half == "relay":
                if lab in MEDIA:
                    V["relay_pj"][lab] = pj(b)
            elif half in ("A", "AB") and (base in RINGS or base == "nspin"):
                group.setdefault(("A", base), []).append((lab, b))
            elif half in ("B", "AB") and (base in LEVELS or base == "mspin"):
                group.setdefault(("B", base), []).append((lab, b))
    for (half, base), bs in group.items():
        if base in ("nspin", "mspin"):
            V[base + "_w"] = float(np.mean([b["over_idle_w"] for _, b in bs]))   # mean of the kept brackets
            V[base + "_n"] = len(bs)
        elif half == "A":
            V["ring_pj"][base] = pj(bs[0][1]); V["ring_w"][base] = bs[0][1]["over_idle_w"]
        else:
            ps = [pj(b) for _, b in bs if pj(b) is not None]
            if ps:
                V["level_pj"][base] = float(np.mean(ps))       # mean of the kept ABBA bursts
                V["level_pj_n_" + base] = len(ps)
    # L2 - own scratchpad, paired within the pass: the mean of the two ABBA bursts each, all four kept
    l2 = [pj(b) for lab, b in group.get(("B", "l2"), []) if lab in ("l2-1", "l2-2")]
    sc = [pj(b) for lab, b in group.get(("B", "scp-local"), []) if lab in ("scp-local-1", "scp-local-2")]
    if len(l2) == 2 and len(sc) == 2:
        V["l2_minus_scp"] = float(np.mean(l2) - np.mean(sc))
    elif ("B", "l2") in group and ("B", "scp-local") in group and not any(lab.endswith(("-1", "-2")) for lab, _ in group[("B", "l2")]):
        V["l2_minus_scp"] = float(V["level_pj"]["l2"] - V["level_pj"]["scp-local"])   # legacy single bursts
    return V


def load_new(data, card, include_failed=False, variant="std"):
    """The new passes of one card: [(pass, contents, values)], plus a per-pass log and the dropped bursts."""
    out, log, dropped = [], [], []
    root = os.path.join(data, card, "rl")
    for pd in sorted(glob.glob(os.path.join(root, "p*")), key=lambda p: int(re.sub(r"\D", "", os.path.basename(p)) or 0)):
        m = re.match(r"^p(\d+)$", os.path.basename(pd))
        if not m or not os.path.isdir(pd):
            continue          # p<K>.attempt-<ts>: a failed attempt the queue set aside
        K = int(m.group(1))
        entry = {"pass": K}
        bj = os.path.join(pd, "block.json")
        if not os.path.exists(bj):
            entry["skipped"] = "no block.json (pass unfinished)"; log.append(entry); continue
        blk = json.load(open(bj)); entry["status"] = blk.get("status"); entry["note"] = blk.get("note")
        pj_ = os.path.join(pd, "pass.json")
        meta = json.load(open(pj_)) if os.path.exists(pj_) else {}
        if meta.get("dry"):
            entry["skipped"] = "dry run"; log.append(entry); continue
        contents = meta.get("contents") or ("zeros" if K % 2 else "random")
        entry["contents"] = contents
        if blk.get("status") != "ok" and not include_failed:
            entry["skipped"] = f"block status {blk.get('status')} (schedule the pass again)"; log.append(entry); continue
        halves, n_all, off_all = {}, 0, 0
        for half in ("A", "B", "relay"):
            hd = os.path.join(pd, half)
            if not has_data(hd):
                entry.setdefault("missing_halves", []).append(half); continue
            n, off = telemetry_off600(hd); n_all += n; off_all += off
            try:
                halves[half] = reduce_dir(hd, variant)
            except Exception as e:  # noqa: BLE001 - a damaged half is reported, not fatal
                entry.setdefault("errors", []).append(f"{half}: {e!r}")
        entry["samples"], entry["off600"] = n_all, off_all
        # PLAN3 common rules: "aifoundry2 repeats with any sample off 600 MHz are dropped and re-run". aifoundry3 is
        # pinned at 600 MHz and has no pass-level rule: its bursts fall under the V3-RL burst rule (> 2% off 600).
        if off_all > 0 and card == A2:
            entry["skipped"] = f"{off_all} of {n_all} samples off 600 MHz: pass dropped (common rule, aifoundry2), re-run it"
            log.append(entry); continue
        V = pass_values(halves, dropped, f"{card}/p{K}", variant)
        entry["kept_bursts"] = sum(1 for b in V["bursts"].values() if not b.get("dropped"))
        entry["dropped_bursts"] = [k for k, b in V["bursts"].items() if b.get("dropped")]
        log.append(entry)
        out.append((K, contents, V))
    return out, log, dropped


def load_legacy(card, dropped):
    """The committed 23 Sep rl-passes (RL-X4's byte side): docs/reports/data/2026-09-23-reruns-*/rl-pass<k>."""
    d = {A2: "2026-09-23-reruns-aifoundry2-warm", A3: "2026-09-23-reruns-aifoundry3"}[card]
    out = []
    for pd in sorted(glob.glob(os.path.join(REPO, "docs/reports/data", d, "rl-pass*[0-9]"))):
        log_ = pd + ".log"
        if not (os.path.exists(log_) and open(log_).read().rstrip().endswith("done")) or not has_data(pd):
            continue          # analyze_reruns.complete(): the runner finished and its sampler ran
        b = reduce_dir(pd)
        V = pass_values({"AB": b}, dropped, f"{card}/23sep-{os.path.basename(pd)}")
        out.append((f"23sep-{os.path.basename(pd)}", V))
    return out

# ---------------------------------------------------------------- items


def per_pass(P, fn):
    r = []
    for K, c, V in P:
        try:
            x = fn(V, c)
        except (KeyError, TypeError, ZeroDivisionError, ValueError):
            x = None
        if x is not None:
            r.append((K, x))
    return r


def slope_fit(V):
    ys = [V["ring_pj"][k] for k in FIVE]
    if any(y is None for y in ys):
        return None
    c = np.polyfit([HOPS[k] for k in FIVE], ys, 1)
    return float(c[0]), float(c[1])


def entry(item, part, claims, prediction, decision, per_card, test, outcome, reading, held=None, **extra):
    e = {"item": item, "part": part, "claims": claims, "prediction": prediction, "decision_rule": decision,
         "per_card": per_card, "test": test, "outcome": outcome, "prediction_held": held, "reading": reading}
    e.update(extra)
    return e


def enough(*ss):
    return all(s["n"] >= NMIN for s in ss)


def fmt(s, nd=2):
    if s["n"] == 0:
        return "no data"
    ci = s.get("ci99")
    return f"{s['mean']:.{nd}f}" + (f" [{ci[0]:.{nd}f}, {ci[1]:.{nd}f}]" if ci else "") + f" (n={s['n']})"


def card_diff_item(item, part, claims, pred, rule, S, bands, sign, test_what, unit, pooled_note):
    """The RL-a pattern: Welch 99% of the per-pass difference between the cards (sign: +1 a2 - a3, -1 a3 - a2)
    excludes 0 -> CARD-DIFFERENT with per-card values; else PASS with the pooled value (and its registered bar)."""
    s2, s3 = S[A2], S[A3]
    for c in CARDS:
        if c in bands and S[c]["n"]:
            S[c]["band"] = bands[c]; S[c]["in_band"] = inband(S[c]["mean"], *bands[c])
    if not enough(s2, s3):
        return entry(item, part, claims, pred, rule, S, f"Welch 99% on per-pass {test_what}", "INSUFFICIENT",
                     f"{part}: fewer than {NMIN} kept passes on a card (a2 n={s2['n']}, a3 n={s3['n']}): claim left as it is")
    w = welch(vals(s2), vals(s3)) if sign > 0 else welch(vals(s3), vals(s2))
    lab = "a2 - a3" if sign > 0 else "a3 - a2"
    held = all(S[c].get("in_band", True) for c in CARDS)
    if "diff" in bands:
        held = held and inband(w["diff"], *bands["diff"])
    pooled = float(np.mean(np.concatenate([vals(s2), vals(s3)])))
    if excl0(w["ci99"]):
        out, rd = "CARD-DIFFERENT", (f"{part}: cards differ, {lab} {w['diff']:+.3f} {unit} (99% [{w['ci99'][0]:+.3f}, {w['ci99'][1]:+.3f}]); "
                                     f"a2 {fmt(s2)}, a3 {fmt(s3)}")
    else:
        out, rd = "PASS", (f"{part}: no card difference at 99% ({lab} {w['diff']:+.3f}, [{w['ci99'][0]:+.3f}, {w['ci99'][1]:+.3f}]): "
                           f"pooled {pooled:.3f} {unit}{pooled_note}")
    return entry(item, part, claims, pred, rule, S, f"Welch 99% on per-pass {test_what}, {lab}", out, rd, held,
                 welch=w, pooled_mean=round(pooled, 4))


def build(data, flop, legacy=True, include_failed=False):
    P, LOG, DROP = {}, {}, []
    for c in CARDS:
        P[c], LOG[c], dr = load_new(data, c, include_failed)
        DROP += dr
    items = []
    CL = {"a": ["energy-manual-127", "memhier-onchip-112", "memhier-onchip-84"], "b": ["energy-manual-128"],
          "c": ["energy-manual-129", "memhier-onchip-83"],
          "d": ["energy-manual-121", "energy-manual-122", "energy-manual-131", "energy-manual-152", "energy-manual-171"],
          "f": ["energy-manual-153"],
          "g": ["energy-manual-83", "energy-manual-84", "energy-manual-87", "energy-manual-90", "memhier-onchip-34", "ridge-94",
                "ridge-96", "memhier-onchip-16", "hotline-relay-l2-73"],
          "h": ["energy-manual-87", "memhier-onchip-34"],
          "X3": ["memhier-onchip-88", "memhier-onchip-50", "memhier-onchip-51", "memhier-onchip-52", "memhier-onchip-89",
                 "memhier-onchip-90", "memhier-onchip-93"],
          "X4": ["ridge-88", "ridge-91"]}

    # ---- RL-a: per-hop slope over the five 1 KB cross-shire rings, per pass
    S = {c: summ(per_pass(P[c], lambda V, _: slope_fit(V)[0])) for c in CARDS}
    items.append(card_diff_item("RL-a", "mesh slope (five 1 KB xshire rings)", CL["a"],
                                "mesh slope over the five 1 KB cross-shire rings a2 2.3+-0.5, a3 1.3+-0.5 pJ/B per hop.",
                                "Welch 99% of the per-pass slope difference excludes 0 (6 new passes per card) -> CARD-DIFFERENT stands with per-card slopes; else pooled with +-50%.",
                                S, {A2: (1.8, 2.8), A3: (0.8, 1.8)}, +1, "slopes (pJ/B per mean hop, xshire8/1/4/2/6)", "pJ/B/hop",
                                " (+-50% on the page)"))

    # ---- RL-b: aifoundry2 "leaving the shire" step = intercept - shire ring - one hop
    S = {c: summ(per_pass(P[c], lambda V, _: slope_fit(V)[1] - V["ring_pj"]["shire"] - slope_fit(V)[0])) for c in CARDS}
    s2 = S[A2]
    if s2["n"]:
        s2["band"] = (1.3, 5.3); s2["in_band"] = inband(s2["mean"], 1.3, 5.3)
    rule = "99% t excludes 0 on that card."
    pred = "aifoundry2 \"leaving the shire\" step (intercept - shire ring - one hop) +3.3+-2 pJ/B."
    if s2["n"] < NMIN:
        items.append(entry("RL-b", "leaving-the-shire step, aifoundry2", CL["b"], pred, rule, S, "99% t on per-pass steps, aifoundry2 (aifoundry3 for information)",
                           "INSUFFICIENT", f"step: fewer than {NMIN} kept aifoundry2 passes (n={s2['n']})"))
    else:
        ok = s2["ci99"][0] > 0
        items.append(entry("RL-b", "leaving-the-shire step, aifoundry2", CL["b"], pred, rule, S,
                           "99% t on per-pass steps, aifoundry2 (aifoundry3 for information)", "PASS" if ok else "FAIL",
                           f"step a2 {fmt(s2)} pJ/B: " + ("above 0, leaving the shire is a step beyond one hop" if ok else "interval reaches 0, the step is not established")
                           + f"; a3 {fmt(S[A3])} (not decided)", s2.get("in_band")))

    # ---- RL-c: small messages (128 B rows) on aifoundry3, each difference on its own
    for a, b, pv in (("shire-c4", "shire", 1.0), ("xshire1-c4", "xshire1", 3.6)):
        S = {c: summ(per_pass(P[c], lambda V, _, a=a, b=b: V["ring_pj"][a] - V["ring_pj"][b])) for c in CARDS}
        part = f"{a} - {b}"
        pred = "aifoundry3: shire-c4 - shire = +1.0 and xshire1-c4 - xshire1 = +3.6 pJ/B."
        rule = "99% t excludes 0 (6 passes) on aifoundry3 -> \"small messages cost more\" on both cards."
        s3 = S[A3]
        if s3["n"] < NMIN:
            items.append(entry("RL-c", part, CL["c"], pred, rule, S, "99% t on per-pass paired differences, aifoundry3",
                               "INSUFFICIENT", f"{part}: fewer than {NMIN} kept aifoundry3 passes (n={s3['n']})", predicted=pv))
            continue
        ok = s3["ci99"][0] > 0
        a2note = ""
        if S[A2]["n"] >= NMIN:
            a2note = "; a2 " + ("also > 0" if S[A2]["ci99"][0] > 0 else "NOT > 0 in the new passes") + f" {fmt(S[A2])}"
        items.append(entry("RL-c", part, CL["c"], pred, rule, S, "99% t on per-pass paired differences, aifoundry3 (aifoundry2 shown)",
                           "PASS" if ok else "FAIL",
                           f"{part} a3 {fmt(s3)} pJ/B (predicted {pv:+.1f}): " + ("small messages cost more" if ok else "not established") + a2note,
                           ok, predicted=pv, predicted_in_ci99=bool(s3["ci99"][0] <= pv <= s3["ci99"][1])))

    # ---- RL-d: relay DRAM / next shire, per card; relay DRAM a3/a2 (Welch 99% on logs)
    pred = "relay DRAM/next-shire ratio a2 11.2+-0.6, a3 13.5+-0.8; relay DRAM a3/a2 1.07+-0.03."
    rule = "Welch 99% on log ratios."
    L = {c: summ(per_pass(P[c], lambda V, _: math.log(V["relay_pj"]["dram"] / V["relay_pj"]["hop"]))) for c in CARDS}
    media = {c: {m: summ(per_pass(P[c], lambda V, _, m=m: V["relay_pj"][m])) for m in MEDIA} for c in CARDS}
    S = {}
    for c, band in ((A2, (10.6, 11.8)), (A3, (12.7, 14.3))):
        S[c] = {"n": L[c]["n"], "passes": L[c]["passes"], "ratio_per_pass": [round(math.exp(x), 3) for x in L[c]["values"]],
                "relay_pj_per_byte": media[c], "band": band}
        if L[c]["n"]:
            S[c]["ratio_geo_mean"] = round(math.exp(L[c]["mean"]), 3); S[c]["in_band"] = inband(S[c]["ratio_geo_mean"], *band)
        if "ci99" in L[c]:
            S[c]["ratio_ci99"] = [round(math.exp(x), 3) for x in L[c]["ci99"]]
    if not enough(L[A2], L[A3]):
        items.append(entry("RL-d", "relay DRAM / next shire", CL["d"], pred, rule, S, "Welch 99% on per-pass log(DRAM/next shire), a2 vs a3",
                           "INSUFFICIENT", f"relay ratio: fewer than {NMIN} kept passes on a card (a2 n={L[A2]['n']}, a3 n={L[A3]['n']})"))
    else:
        w = welch(vals(L[A2]), vals(L[A3]))
        r = {k: (round(math.exp(v), 4) if k == "diff" else [round(math.exp(x), 4) for x in v] if k == "ci99" else v) for k, v in w.items()}
        pooled = math.exp(float(np.mean(np.concatenate([vals(L[A2]), vals(L[A3])]))))
        held = S[A2].get("in_band") and S[A3].get("in_band")
        if excl0(w["ci99"]):
            items.append(entry("RL-d", "relay DRAM / next shire", CL["d"], pred, rule, S, "Welch 99% on per-pass log(DRAM/next shire), a2 vs a3",
                               "CARD-DIFFERENT", f"relay DRAM/next shire differs by card: a2 {S[A2]['ratio_geo_mean']}x, a3 {S[A3]['ratio_geo_mean']}x "
                               f"(a2/a3 {r['diff']:.3f}, 99% [{r['ci99'][0]:.3f}, {r['ci99'][1]:.3f}])", held, welch_log=w, ratio_a2_over_a3=r))
        else:
            items.append(entry("RL-d", "relay DRAM / next shire", CL["d"], pred, rule, S, "Welch 99% on per-pass log(DRAM/next shire), a2 vs a3",
                               "PASS", f"relay DRAM/next shire the same on both cards at 99%: pooled {pooled:.2f}x (a2/a3 99% [{r['ci99'][0]:.3f}, {r['ci99'][1]:.3f}])",
                               held, welch_log=w, ratio_a2_over_a3=r, pooled_ratio=round(pooled, 3)))
    L = {c: summ(per_pass(P[c], lambda V, _: math.log(V["relay_pj"]["dram"]))) for c in CARDS}
    S = {c: {"n": L[c]["n"], "passes": L[c]["passes"], "relay_dram_pj_per_byte": media[c]["dram"]} for c in CARDS}
    if not enough(L[A2], L[A3]):
        items.append(entry("RL-d", "relay DRAM a3/a2", CL["d"], pred, rule, S, "Welch 99% on per-pass log(relay DRAM pJ/B), a3 vs a2",
                           "INSUFFICIENT", f"relay DRAM: fewer than {NMIN} kept passes on a card (a2 n={L[A2]['n']}, a3 n={L[A3]['n']})"))
    else:
        w = welch(vals(L[A3]), vals(L[A2]))
        rr, ci = math.exp(w["diff"]), [math.exp(x) for x in w["ci99"]]
        held = inband(rr, 1.04, 1.10)
        oc = "CARD-DIFFERENT" if excl0(w["ci99"]) else "PASS"
        rd = (f"relay DRAM a3/a2 {rr:.3f} (99% [{ci[0]:.3f}, {ci[1]:.3f}]): " +
              ("the cards differ" if oc == "CARD-DIFFERENT" else "the same on both cards at 99%") +
              f"; a2 {fmt(media[A2]['dram'], 1)}, a3 {fmt(media[A3]['dram'], 1)} pJ/B")
        items.append(entry("RL-d", "relay DRAM a3/a2", CL["d"], pred, rule, S, "Welch 99% on per-pass log(relay DRAM pJ/B), a3 vs a2",
                           oc, rd, held, welch_log=w, ratio_a3_over_a2={"ratio": round(rr, 4), "ci99": [round(x, 4) for x in ci]}))

    # ---- RL-f: relay own scratchpad against the bracket's low edge (catalogue 23 Sep: mean of l1fill/stride32/zeros and tstore/scp/zeros)
    pred = "relay own scratchpad 3.95-4.05 against a bracket low edge of 4.30-4.40."
    rule = "Welch 99% of measured - low edge excludes 0 on each card -> \"8% below its bracket\"; else \"at the low edge\"."
    low = catalogue_low_edge()
    S, below, ok_n = {}, {}, True
    for c in CARDS:
        m = media[c]["scp"]
        S[c] = {"measured": m, "low_edge_per_catalogue_pass": low.get(c), "n": m["n"]}
        if m["n"]:
            S[c]["measured_in_band"] = inband(m["mean"], 3.95, 4.05)
        if low.get(c):
            S[c]["low_edge_mean"] = round(float(np.mean(low[c])), 4); S[c]["low_edge_in_band"] = inband(S[c]["low_edge_mean"], 4.30, 4.40)
        if m["n"] < NMIN or not low.get(c):
            ok_n = False; continue
        w = welch(vals(m), low[c]); S[c]["welch_measured_minus_low"] = w
        below[c] = w["ci99"][1] < 0
        S[c]["side"] = "below" if below[c] else "above" if w["ci99"][0] > 0 else "at"
    held = all(S[c].get("measured_in_band") and S[c].get("low_edge_in_band") for c in CARDS)
    if not ok_n:
        items.append(entry("RL-f", "relay own scratchpad vs bracket low edge", CL["f"], pred, rule, S, "Welch 99% (new relay scp passes - catalogue low edge per pass), each card",
                           "INSUFFICIENT", f"relay own scratchpad: fewer than {NMIN} kept passes on a card (a2 n={media[A2]['scp']['n']}, a3 n={media[A3]['scp']['n']})"))
    else:
        nb = sum(below.values())
        oc = "PASS" if nb == 2 else "CARD-DIFFERENT" if nb == 1 else "FAIL"
        rd = (f"relay own scratchpad a2 {fmt(media[A2]['scp'])}, a3 {fmt(media[A3]['scp'])} vs low edge a2 {S[A2]['low_edge_mean']:.2f}, a3 {S[A3]['low_edge_mean']:.2f}: " +
              {"PASS": "below its bracket on both cards", "CARD-DIFFERENT": "below on " + ",".join(c for c in CARDS if below[c]) + " only",
               "FAIL": "at the low edge (not below at 99%)"}[oc] +
              "".join(f"; {c} ABOVE the low edge at 99%" for c in CARDS if S[c]["side"] == "above"))
        items.append(entry("RL-f", "relay own scratchpad vs bracket low edge", CL["f"], pred, rule, S,
                           "Welch 99% (new relay scp passes - catalogue low edge per pass), each card", oc, rd, held))

    # ---- RL-g: L1 level a2 - a3, own-scratchpad level a3 - a2 (all passes), L2 - scratchpad per card
    lev = {c: {l: summ(per_pass(P[c], lambda V, _, l=l: V["level_pj"][l])) for l in LEVELS} for c in CARDS}
    pred_g = ("L1 level a2 - a3 = +0.18+-0.06 pJ/B; own-scratchpad level a3 - a2 = +0.23+-0.06; "
              "L2 - scratchpad a2 +0.18+-0.15, a3 -0.28+-0.15.")
    rule_g = "as RL-a; both L2 - scratchpad intervals containing 0 -> \"the same within +-10%\"."
    items.append(card_diff_item("RL-g", "L1 level a2 - a3", CL["g"], pred_g, rule_g, {c: dict(lev[c]["l1"]) for c in CARDS},
                                {"diff": (0.12, 0.24)}, +1, "L1 level (pJ/B)", "pJ/B", ""))
    it = card_diff_item("RL-g", "own-scratchpad level a3 - a2", CL["g"], pred_g, rule_g, {c: dict(lev[c]["scp-local"]) for c in CARDS},
                        {"diff": (0.17, 0.29)}, -1, "own-scratchpad level (pJ/B), all passes (both contents)", "pJ/B", "")
    if it["outcome"] != "INSUFFICIENT":
        it["reading"] += " [confounded: every pass is prefilled, zeros/random alternating; see RL-h]"
    it["note"] = ("every V3-RL pass is prefilled (odd zeros, even random, the same schedule on both cards), so this compares the cards "
                  "averaged over the two contents; RL-h compares them at equal contents")
    it["info_by_contents"] = {k: {c: summ(per_pass([x for x in P[c] if x[1] == k], lambda V, _: V["level_pj"]["scp-local"])) for c in CARDS}
                              for k in ("zeros", "random")}
    items.append(it)
    S = {c: summ(per_pass(P[c], lambda V, _: V["l2_minus_scp"])) for c in CARDS}
    for c, band in ((A2, (0.03, 0.33)), (A3, (-0.43, -0.13))):
        S[c]["band"] = band
        if S[c]["n"]:
            S[c]["in_band"] = inband(S[c]["mean"], *band)
        S[c]["l2_level"] = lev[c]["l2"]; S[c]["scp_local_level"] = lev[c]["scp-local"]
    if not enough(S[A2], S[A3]):
        items.append(entry("RL-g", "L2 - own scratchpad", CL["g"], pred_g, rule_g, S, "99% t per card on per-pass (L2 - scp-local), mean of the ABBA bursts; Welch between cards",
                           "INSUFFICIENT", f"L2 - scratchpad: fewer than {NMIN} kept passes with all four ABBA bursts on a card (a2 n={S[A2]['n']}, a3 n={S[A3]['n']})"))
    else:
        w = welch(vals(S[A2]), vals(S[A3]))
        c0 = {c: not excl0(S[c]["ci99"]) for c in CARDS}
        if excl0(w["ci99"]):
            oc, rd = "CARD-DIFFERENT", "L2 - scratchpad differs by card"
        elif all(c0.values()):
            oc, rd = "PASS", "L2 and own scratchpad the same within +-10% on both cards"
        elif any(c0.values()):
            oc, rd = "CARD-DIFFERENT", "L2 and own scratchpad the same on " + ",".join(c for c in CARDS if c0[c]) + " only"
        else:
            oc, rd = "FAIL", "L2 and own scratchpad differ, in the same direction on both cards"
        items.append(entry("RL-g", "L2 - own scratchpad", CL["g"], pred_g, rule_g, S,
                           "99% t per card on per-pass (L2 - scp-local), mean of the two ABBA bursts each; Welch 99% a2 vs a3", oc,
                           f"{rd}: a2 {fmt(S[A2], 3)}, a3 {fmt(S[A3], 3)} pJ/B [confounded: the scratchpad bursts are prefilled, zeros/random alternating; see RL-h]",
                           S[A2].get("in_band") and S[A3].get("in_band"), welch=w,
                           note="the scratchpad bursts are prefilled (odd zeros, even random), so this difference mixes the two contents; see RL-h",
                           info_l2_level_a2_minus_a3=welch(vals(lev[A2]["l2"]), vals(lev[A3]["l2"])) if enough(lev[A2]["l2"], lev[A3]["l2"]) else None))

    # ---- RL-h: the contents arm
    pred_h = ("contents arm: each card's scp-local level follows the prefill (zeros 2.0+-0.3, random 4.2+-0.5 pJ/B) and at equal "
              "contents a3 - a2 is within +-0.1 pJ/B.")
    rule_h = "as RL-a on the prefilled passes; a3 - a2 inside +-0.1 -> the card difference is contents, and the page says so."
    G = {k: {c: summ(per_pass([x for x in P[c] if x[1] == k], lambda V, _: V["level_pj"]["scp-local"])) for c in CARDS} for k in ("zeros", "random")}
    bands = {"zeros": (1.7, 2.3), "random": (3.7, 4.7)}
    S = {c: {k: dict(G[k][c], band=bands[k], in_band=inband(G[k][c].get("mean"), *bands[k]) if G[k][c]["n"] else None) for k in G} for c in CARDS}
    if not all(G[k][c]["n"] >= NMIN for k in G for c in CARDS):
        items.append(entry("RL-h", "scp-local level follows the prefill", CL["h"], pred_h, rule_h, S,
                           "per-card means of the zeros-prefill and random-prefill passes against the registered bands; Welch random - zeros per card for information",
                           "INSUFFICIENT", "contents arm: fewer than 3 kept passes of each contents on a card: " +
                           ", ".join(f"{c[-1]} {k} n={G[k][c]['n']}" for c in CARDS for k in G)))
        items.append(entry("RL-h", "a3 - a2 at equal contents", CL["h"], pred_h, rule_h, S, "Welch 99% a3 - a2 within each contents group",
                           "INSUFFICIENT", "contents arm: fewer than 3 kept passes of each contents on a card"))
    else:
        fol = {c: bool(S[c]["zeros"]["in_band"] and S[c]["random"]["in_band"]) for c in CARDS}
        for c in CARDS:
            S[c]["welch_random_minus_zeros"] = welch(vals(G["random"][c]), vals(G["zeros"][c]))
        n = sum(fol.values())
        oc = "PASS" if n == 2 else "CARD-DIFFERENT" if n == 1 else "FAIL"
        items.append(entry("RL-h", "scp-local level follows the prefill", CL["h"], pred_h, rule_h, S,
                           "per-card means of the zeros-prefill and random-prefill passes against the registered bands; Welch random - zeros per card for information",
                           oc, "scp-local by prefill: " + "; ".join(f"{c[-1]} zeros {fmt(G['zeros'][c])}, random {fmt(G['random'][c])}" for c in CARDS)
                           + " pJ/B (" + ("in both bands on both cards" if n == 2 else "in the bands on " + (",".join(c for c in CARDS if fol[c]) or "neither card")) + ")",
                           n == 2))
        W = {k: welch(vals(G[k][A3]), vals(G[k][A2])) for k in G}
        diff = any(excl0(W[k]["ci99"]) for k in G)
        inside = all(abs(W[k]["diff"]) <= 0.1 for k in G)
        oc = "CARD-DIFFERENT" if diff else "PASS" if inside else "FAIL"
        rd = ("a3 - a2 at equal contents: " + "; ".join(f"{k} {W[k]['diff']:+.3f} [{W[k]['ci99'][0]:+.3f}, {W[k]['ci99'][1]:+.3f}]" for k in G) + " pJ/B: " +
              {"CARD-DIFFERENT": "the cards still differ at equal contents", "PASS": "inside +-0.1: the card difference is contents",
               "FAIL": "no difference at 99% but not inside +-0.1: not established"}[oc])
        items.append(entry("RL-h", "a3 - a2 at equal contents", CL["h"], pred_h, rule_h, {c: {k: G[k][c] for k in G} for c in CARDS},
                           "Welch 99% a3 - a2 within each contents group (3 passes per card each)", oc, rd, inside,
                           welch_a3_minus_a2=W, info_interval_inside_0p1={k: bool(-0.1 <= W[k]["ci99"][0] and W[k]["ci99"][1] <= 0.1) for k in G}))

    # ---- RL-X3 (a): nocbench spin - ring over idle, per pass (spin = mean of the kept first/last brackets)
    pred_x3 = ("(a) nocbench spin - ring over idle per pass: pair +0.0..+0.5 W; neigh and shire within +-0.4 W; xshire2/4/6 >= +0.4 W on both cards; "
               "(d) memhier two-hart spin 2.3-2.8 W, nocbench one-hart spin 2.2-2.6 W; (e) inside-shire ring power above mesh-ring power and "
               "scp-remote cheaper than s->s+8 and s->s+16 in every pass.")
    rule_x3 = ("(a) \"less than spinning\" kept for a ring only if its interval is > 0 on both cards, else \"about as much as spinning (+-x W)\"; "
               "(d), (e) every pass on both cards -> PROVEN-BOTH.")
    RB = {"pair": (0.0, 0.5), "neigh": (-0.4, 0.4), "shire": (-0.4, 0.4), "xshire2": (0.4, math.inf), "xshire4": (0.4, math.inf), "xshire6": (0.4, math.inf)}
    robust = {}
    for var in ("noleak", "before"):
        robust[var] = {c: load_new(data, c, include_failed, var)[0] for c in CARDS}
    for r in RINGS:
        S = {c: summ(per_pass(P[c], lambda V, _, r=r: V["nspin_w"] - V["ring_w"][r])) for c in CARDS}
        if r in RB:
            for c in CARDS:
                S[c]["band"] = [RB[r][0], None if RB[r][1] == math.inf else RB[r][1]]
                if S[c]["n"]:
                    S[c]["in_band"] = inband(S[c]["mean"], *RB[r])
        rob = {var: {c: summ(per_pass(robust[var][c], lambda V, _, r=r: V["nspin_w"] - V["ring_w"][r])).get("ci99") for c in CARDS} for var in robust}
        part = f"(a) spin - {r}"
        if not enough(S[A2], S[A3]):
            items.append(entry("RL-X3", part, CL["X3"], pred_x3, rule_x3, S, "99% t per card on per-pass (nocbench spin W - ring W over idle)",
                               "INSUFFICIENT", f"spin - {r}: fewer than {NMIN} kept passes on a card (a2 n={S[A2]['n']}, a3 n={S[A3]['n']})",
                               robustness_ci99=rob))
            continue
        pos = {c: S[c]["ci99"][0] > 0 for c in CARDS}
        x = max(abs(v) for c in CARDS for v in S[c]["ci99"])
        n = sum(pos.values())
        oc = "PASS" if n == 2 else "CARD-DIFFERENT" if n == 1 else "FAIL"
        rd = (f"spin - {r}: a2 {fmt(S[A2])}, a3 {fmt(S[A3])} W: " +
              {"PASS": "less than spinning on both cards", "CARD-DIFFERENT": "less than spinning on " + ",".join(c for c in CARDS if pos[c]) + " only",
               "FAIL": f"about as much as spinning (+-{x:.2f} W)"}[oc])
        held = (S[A2].get("in_band") and S[A3].get("in_band")) if r in RB else None
        items.append(entry("RL-X3", part, CL["X3"], pred_x3, rule_x3, S, "99% t per card on per-pass (nocbench spin W - ring W over idle)", oc, rd, held,
                           robustness_ci99=rob))
    # ---- RL-X3 (d): spin power per pass in its band on every pass
    for key, lab, band in (("nspin_w", "(d) nocbench one-hart spin", (2.2, 2.6)), ("mspin_w", "(d) memhier two-hart spin", (2.3, 2.8))):
        S = {c: summ(per_pass(P[c], lambda V, _, key=key: V[key])) for c in CARDS}
        every = {}
        for c in CARDS:
            S[c]["band"] = band
            every[c] = S[c]["n"] >= NMIN and all(inband(v, *band) for v in S[c]["values"])
            S[c]["every_pass_in_band"] = every[c]
        if not enough(S[A2], S[A3]):
            items.append(entry("RL-X3", lab, CL["X3"], pred_x3, rule_x3, S, "each pass's over-idle W (mean of the kept first/last brackets) in the band",
                               "INSUFFICIENT", f"{lab}: fewer than {NMIN} kept passes on a card"))
            continue
        n = sum(every.values())
        oc = "PASS" if n == 2 else "CARD-DIFFERENT" if n == 1 else "FAIL"
        items.append(entry("RL-X3", lab, CL["X3"], pred_x3, rule_x3, S, "each pass's over-idle W (mean of the kept first/last brackets) in the band", oc,
                           f"{lab} W over idle: a2 {r2(S[A2]['values'])}, a3 {r2(S[A3]['values'])} (band {band[0]}-{band[1]}): "
                           + ("every pass in band on both cards" if n == 2 else "in band every pass on " + (",".join(c for c in CARDS if every[c]) or "neither card")),
                           n == 2))
    # ---- RL-X3 (e1): inside-shire ring power above mesh-ring power in every pass (means over the 1 KB rings)
    def ins_acr(V, _):
        wi = [V["ring_w"][k] for k in INSIDE]; wa = [V["ring_w"][k] for k in FIVE]
        return float(np.mean(wi) - np.mean(wa))
    S = {c: summ(per_pass(P[c], ins_acr)) for c in CARDS}
    for c in CARDS:
        S[c]["info_min_inside_minus_max_across"] = summ(per_pass(P[c], lambda V, _: min(V["ring_w"][k] for k in INSIDE) - max(V["ring_w"][k] for k in FIVE)))
    items.append(every_pass_item("RL-X3", "(e) inside-shire ring W above mesh-ring W", CL["X3"], pred_x3, rule_x3, S,
                                 "per pass: mean over-idle W of pair/neigh/shire minus mean of the five 1 KB xshire rings (8,1,4,2,6) > 0",
                                 lambda v: v > 0, "inside minus across W"))
    # ---- RL-X3 (e2): scp-remote cheaper than s->s+8 and s->s+16 in every pass (s+16 where its burst was kept)
    def remote_margin(V, _):
        rs = [V["ring_pj"][k] for k in ("xshire8", "xshire16") if V["ring_pj"].get(k) is not None]
        return min(rs) - V["level_pj"]["scp-remote"] if rs and "xshire8" in V["ring_pj"] else None
    S = {c: summ(per_pass(P[c], remote_margin)) for c in CARDS}
    for c in CARDS:
        S[c]["passes_with_xshire16"] = [K for K, _, V in P[c] if V["ring_pj"].get("xshire16") is not None]
    it = every_pass_item("RL-X3", "(e) scp-remote cheaper than s->s+8 and s->s+16", CL["X3"], pred_x3, rule_x3, S,
                         "per pass: min(xshire8, xshire16 if kept) pJ/B - scp-remote pJ/B > 0", lambda v: v > 0,
                         "ring minus scp-remote pJ/B")
    no16 = [c for c in CARDS if S[c]["n"] and len(S[c]["passes_with_xshire16"]) < S[c]["n"]]
    if no16 and it["outcome"] != "INSUFFICIENT":
        it["reading"] += "; s->s+16 untested in passes where its burst was dropped (" + ", ".join(
            f"{c} kept in {len(S[c]['passes_with_xshire16'])} of {S[c]['n']}" for c in no16) + ")"
    items.append(it)

    # ---- RL-X4: balance points against the ridges (byte side 23 Sep + V3-RL passes, FLOP side V3-ABL-A blocks)
    items += ridge_items(P, flop, legacy, DROP, CL["X4"])
    return {"experiment": "V3-RL", "plan": "docs/reports/data/2026-09-25-claims-v3/PLAN3.md section 2 V3-RL", "data": os.path.abspath(data),
            "rules": {"burst_drop": f"clock off 600 MHz in > {CLOCK_FRAC:.0%} of the burst's samples, or sampler median > {STARVED_MS:.0f} ms",
                      "pass_drop": "aifoundry2: any telemetry sample of the pass off 600 MHz (common rules); both cards: block.json status not ok",
                      "min_kept_repeats": NMIN, "interval": "99% t on pass-level values; Welch between cards"},
            "passes": LOG, "dropped_bursts": DROP, "items": items}


def every_pass_item(item, part, claims, pred, rule, S, test, ok, what):
    every = {c: S[c]["n"] >= NMIN and all(ok(v) for v in S[c]["values"]) for c in CARDS}
    for c in CARDS:
        S[c]["every_pass"] = every[c]
    if not enough(S[A2], S[A3]):
        return entry(item, part, claims, pred, rule, S, test, "INSUFFICIENT", f"{part}: fewer than {NMIN} kept passes on a card (a2 n={S[A2]['n']}, a3 n={S[A3]['n']})")
    n = sum(every.values())
    oc = "PASS" if n == 2 else "CARD-DIFFERENT" if n == 1 else "FAIL"
    return entry(item, part, claims, pred, rule, S, test, oc,
                 f"{part}: {what} a2 {r2(S[A2]['values'])}, a3 {r2(S[A3]['values'])}: " +
                 ("every pass on both cards" if n == 2 else "every pass on " + (",".join(c for c in CARDS if every[c]) or "neither card")), n == 2)


def catalogue_low_edge():
    """Per catalogue pass (23 Sep energy manual): 0.5 * (l1fill/stride32/zeros + tstore/scp/zeros), as rings_relay_extra.py."""
    p = os.path.join(REPO, "docs/reports/data/2026-09-23-energy-manual/catalogue.json")
    if not os.path.exists(p):
        return {}
    cat = json.load(open(p))
    out = {}
    for c in CARDS:
        def ps(cfg):
            bs = sorted((b for b in cat["bursts"].get(c, []) if b["cfg"] == cfg), key=lambda b: b["pass"])
            return np.array([b["pj_per_byte"] for b in bs], float)
        a, b = ps("l1fill/stride32/zeros"), ps("tstore/scp/zeros")
        if len(a) and len(a) == len(b):
            out[c] = [round(float(x), 4) for x in 0.5 * (a + b)]
    return out


def ridges():
    """Time ridges from the ridge page's embedded data (as validate3/inv/ridge-work/e_energy.py reads them)."""
    fallback = {("l3", "spec"): [3.0, 3.0], ("scp_remote", "spec"): [3.0, 3.0], ("xbar", "measured"): [8.78, 8.78]}
    p = os.path.join(REPO, "docs/reports/2026-09-18-et-soc1-ridge-points.html")
    try:
        rd = json.loads(re.search(r'<script type="application/json" id="ridge-data">(.*?)</script>', open(p).read(), re.S).group(1))
        lv = {l["key"]: l for l in rd["levels"]}
        out = {}
        for (k, basis), fb in fallback.items():
            v = lv[k]["ridge"][basis]["fp32"]
            out[(k, basis)] = v if isinstance(v, list) else [v, v]
        return out, "ridge-points page"
    except Exception:  # noqa: BLE001
        return fallback, "fallback constants (ridge page not readable)"


def ridge_items(P, flop, legacy, DROP, claims):
    pred = ("L3 random vs spec 3.0 -> 3.6+-0.5 (above); other shire random -> 2.3+-0.6 (below); zeros in-shire TensorSend vs 8.8 -> 10.0+-1.5 (above).")
    rule = ("byte side 99% t over all passes per card (23 Sep + V3-RL), FLOP side over V3-ABL-A blocks; balance interval [byte lo / FLOP hi, "
            "byte hi / FLOP lo]; a verdict only when both cards' intervals lie on the same side of the ridge, else \"ranges overlap: no verdict\". "
            "ridge-89, ridge-92 and the pairs half of ridge-91 are not tested (margins need 11 to > 100 passes).")
    RG, rsrc = ridges()
    LEG = {c: (load_legacy(c, DROP) if legacy else []) for c in CARDS}
    rows = [("L3, random, spec ridge", "l3", "spec", "random", lambda V: V["level_pj"]["l3"], "above", (3.1, 4.1)),
            ("other shire's scratchpad, random, spec ridge", "scp_remote", "spec", "random", lambda V: V["level_pj"]["scp-remote"], "below", (1.7, 2.9)),
            ("in-shire TensorSend (shire ring), zeros, measured ridge", "xbar", "measured", "zeros", lambda V: V["ring_pj"]["shire"], "above", (8.5, 11.5))]
    out = []
    fu = 0.5 if flop and str(flop.get("unit", "pJ/FLOP")).lower() in ("pj/mac", "pj_per_mac") else 1.0
    for part, key, basis, op, get, side_pred, band in rows:
        rg = RG[(key, basis)]
        S = {}
        for c in CARDS:
            pv = [(K, get(V)) for K, V in LEG[c] if safe(get, V) is not None] + [(K, get(V)) for K, _, V in P[c] if safe(get, V) is not None]
            b = summ(pv)
            f = summ([(i + 1, x * fu) for i, x in enumerate((flop or {}).get(c, {}).get(op, []))])
            n_new = sum(1 for K, _ in pv if not str(K).startswith("23sep"))
            S[c] = {"byte_pj_per_byte": b, "flop_pj_per_flop": f, "n_legacy": b["n"] - n_new, "n_new": n_new, "n": b["n"]}
            if op == "random" and key == "scp_remote":
                S[c]["info_random_prefill_only"] = summ([(K, get(V)) for K, cc, V in P[c] if cc == "random" and safe(get, V) is not None])
            # the byte side pools 23 Sep with V3-RL as registered, but V3-RL itself must deliver >= 3 kept passes on
            # the card: otherwise the verdict would rest on the old passes alone
            if n_new >= NMIN and b["n"] >= NMIN and f["n"] >= NMIN:
                # a FLOP interval reaching 0 leaves the balance interval open above (never "below" its ridge)
                iv = [b["ci99"][0] / f["ci99"][1], b["ci99"][1] / f["ci99"][0] if f["ci99"][0] > 0 else math.inf]
                pt = b["mean"] / f["mean"]
                S[c].update(balance_point=round(pt, 3), balance_ci=[round(x, 3) if math.isfinite(x) else None for x in iv], point_in_band=inband(pt, *band),
                            side="above" if iv[0] > rg[1] else "below" if iv[1] < rg[0] else "overlap")
        test = f"per card: byte-side 99% t (23 Sep + V3-RL passes) / FLOP-side 99% t (V3-ABL-A blocks, fp32 {op}); ridge {rg[0]:.2f}-{rg[1]:.2f} ({rsrc})"
        if not flop:
            out.append(entry("RL-X4", part, claims, pred, rule, S, test, "INSUFFICIENT",
                             f"{part}: FLOP side (V3-ABL-A blocks, --flop) not supplied", ridge=rg)); continue
        if not all("side" in S[c] for c in CARDS):
            out.append(entry("RL-X4", part, claims, pred, rule, S, test, "INSUFFICIENT",
                             f"{part}: fewer than {NMIN} new V3-RL passes or FLOP blocks on a card: " +
                             ", ".join(f"{c[-1]} bytes n={S[c]['n_new']} new + {S[c]['n_legacy']} 23 Sep, flops n={S[c]['flop_pj_per_flop']['n']}" for c in CARDS), ridge=rg)); continue
        sides = {S[c]["side"] for c in CARDS}
        if sides == {side_pred}:
            oc, v = "PASS", f"{side_pred} its ridge on both cards"
        elif len(sides) == 1 and "overlap" not in sides:
            oc, v = "FAIL", f"{sides.pop()} its ridge on both cards (predicted {side_pred})"
        elif sides == {"above", "below"}:
            oc, v = "CARD-DIFFERENT", "opposite sides of the ridge on the two cards (no single verdict)"
        else:
            oc, v = "FAIL", "ranges overlap: no verdict"
        out.append(entry("RL-X4", part, claims, pred, rule, S, test, oc,
                         f"{part}: balance a2 {S[A2]['balance_point']} {S[A2]['balance_ci']}, a3 {S[A3]['balance_point']} {S[A3]['balance_ci']} FLOP/B vs ridge {rg[0]:.2f}: {v}",
                         all(S[c]["point_in_band"] for c in CARDS), ridge=rg, predicted_side=side_pred))
    return out


def safe(get, V):
    try:
        x = get(V)
        return x if x is not None and np.isfinite(x) else None
    except (KeyError, TypeError):
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", required=True, help="directory holding aifoundry2/ and aifoundry3/ laid out like DATA_ROOT")
    ap.add_argument("--out", required=True, help="verdicts JSON to write")
    ap.add_argument("--flop", help="V3-ABL-A FLOP side: {\"aifoundry2\": {\"random\": [pJ/FLOP per block], \"zeros\": [...]}, \"aifoundry3\": {...}, \"unit\": \"pJ/FLOP\"}")
    ap.add_argument("--no-legacy", action="store_true", help="RL-X4 byte side without the 23 Sep passes (not the registered rule; for tests)")
    ap.add_argument("--include-failed", action="store_true", help="also use passes whose block.json status is not ok (not the registered rule)")
    a = ap.parse_args()
    flop = json.load(open(a.flop)) if a.flop else None
    res = build(a.data, flop, legacy=not a.no_legacy, include_failed=a.include_failed)
    res["flop_source"] = os.path.abspath(a.flop) if a.flop else None
    json.dump(res, open(a.out, "w"), indent=1, default=lambda o: float(o) if isinstance(o, np.floating) else bool(o) if isinstance(o, np.bool_) else str(o))
    for c in CARDS:
        kept = [e["pass"] for e in res["passes"][c] if "skipped" not in e]
        print(f"{c}: kept passes {kept}; skipped " + "; ".join(f"p{e['pass']}: {e['skipped']}" for e in res["passes"][c] if "skipped" in e))
    print(f"dropped bursts: {len(res['dropped_bursts'])}")
    for e in res["items"]:
        print(f"{e['item']:6s} {e['outcome']:14s} {e['reading']}")


if __name__ == "__main__":
    main()
