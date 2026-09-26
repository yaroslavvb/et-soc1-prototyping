#!/usr/bin/env python3
"""V3-RL reducer: the pre-registered prediction items RL-a .. RL-h, RL-X3 and RL-X4 of PLAN3 (section 2, V3-RL).

    python3 tools/claims-v3/rl/reduce.py --data <dir> --out <verdicts.json> [--flop <flop.json>] [--no-legacy]

<dir> holds one directory per card, each laid out like DATA_ROOT: <card>/rl/p<K>/{A,B,relay}/ written by block.sh
(telemetry.jsonl[.gz], runs.jsonl), with block.json and pass.json. Every card directory with an rl/ inside is read
(aifoundry2, aifoundry3, aifoundry1-c0, aifoundry1-c1, ...). Any card, and any number of passes, may be missing: an
item without enough kept repeats says INSUFFICIENT.

Two outcomes per item (README "Four cards"; AMENDMENTS):
  * "outcome": the REGISTERED outcome, computed from aifoundry2 and aifoundry3 exactly as registered, whatever other
    cards the data holds;
  * "all_cards": the same claim over every card of the campaign (--cards; default aifoundry1-c0, aifoundry1-c1,
    aifoundry2, aifoundry3 and any other card present). A claim tested on each card: PASS if it holds on every card,
    CARD-DIFFERENT if on some, FAIL if on none. A comparison of the cards: the registered comparison over every pair
    of cards (Welch, Bonferroni over the pairs), CARD-DIFFERENT if any pair differs, else PASS (pooled). INSUFFICIENT
    if a card lacks repeats (the verdict over the cards that have them is given for information). Bands or values
    registered for aifoundry2 or aifoundry3 only are reported for the other cards, not tested; an item decided on one
    named card (RL-b on aifoundry2, RL-c on aifoundry3) stays decided there.
  * "per_card" holds every card's values; "idle_clock_mhz" / "idle_note" say when a card's idle brackets are not at
    600 MHz (aifoundry1's card 0 idles in a low-power state at 300 MHz), since every V3-RL value is energy over idle.

Reduction (as registered):
  * every burst is reduced by a verbatim copy of tools/ettelem/analyze_reruns.reduce_dir (bracketing idle,
    leakage-corrected); a burst is dropped when the minion clock left 600 MHz in > 2% of its samples or the
    sampler's median latency was > 60 ms (V3-RL sampler rule); an aifoundry2 pass with ANY telemetry sample off
    600 MHz is dropped whole (PLAN3 common rules: such aifoundry2 repeats are dropped and re-run; aifoundry3 is
    pinned and has only the burst rule); only passes whose block.json says "ok" are used (failed passes are
    re-run by scheduling them again);
  * the other governor-free cards (aifoundry1-c0, -c1; amendment) have the same two rules on BUSY samples only
    (quality.py's windows: inside a burst's window, launch gaps left out): a pass with any busy sample off 600 MHz
    is dropped, and a burst with > 2% of its busy samples off 600 MHz; the idle brackets never drop anything;
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
import itertools
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import quality as Q  # noqa: E402  (the block's windows: busy samples, launch gaps, idle brackets)

A2, A3 = "aifoundry2", "aifoundry3"
CARDS = (A2, A3)  # the registered cards: every registered outcome is computed from these two only
A1C0, A1C1 = "aifoundry1-c0", "aifoundry1-c1"
KNOWN = (A1C0, A1C1, A2, A3)   # the four cards of the 25 Sep campaign, in the order the page shows them
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import campaign  # noqa: E402  (the campaign's cards: amendments A2 and A4)


def clock_rule(card):
    """The card's 600 MHz rules (block.sh OFF600): "all" = registered for aifoundry2 (a pass with any sample off 600
    MHz is dropped; the burst rule counts the burst and its idle brackets); "none" = registered for the pinned
    aifoundry3 (burst rule only, burst and brackets); "busy" = every other card, all governor-free (amendment: both
    rules on busy samples only, never on idle brackets or launch gaps)."""
    return "all" if card == A2 else "none" if card == A3 else "busy"


def short(c):
    return {A2: "a2", A3: "a3"}.get(c, c.replace("aifoundry", "a").replace("-", ""))


def card_order(cs):
    cs = set(cs)
    return [c for c in KNOWN if c in cs] + sorted(cs - set(KNOWN))
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


def reduce_dir(pd, variant="std", clock="all"):
    """Verbatim copy of tools/ettelem/analyze_reruns.reduce_dir (variant "std"), plus the robustness variants of
    validate3/verify-memhier-onchip/rl.py: "noleak" (bracketing idle, no leakage term), "before" (idle before only).
    clock="all" is the registered clock_moved_frac (the burst and its idle brackets); clock="busy" (aifoundry1's
    cards) counts the burst's busy samples only (quality.py: launch gaps left out). Every burst also carries its
    brackets' and busy samples' clock (median MHz, fraction at 600 MHz) and median minion voltage, for information;
    none of them changes a value."""
    tp = os.path.join(pd, "telemetry.jsonl")
    tel = [json.loads(l) for l in _open(tp) if l.startswith("{")]
    runs = [json.loads(l) for l in open(os.path.join(pd, "runs.jsonl"))]
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    w = np.array([s["board_w"] for s in tel])
    T = np.array([s["temp_c"]["minshire"][0] for s in tel])
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    took = np.array([s.get("took_ms", 0) for s in tel])
    mv = np.array([Q.mv_of(s) if Q.mv_of(s) is not None else np.nan for s in tel], float)
    win = np.array(Q.sample_windows([float(x) for x in t], [r for r in runs if "t_start_ms" in r and "t_end_ms" in r]))
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
        busy_only = busy & (win == "busy")
        if clock == "busy":
            moved = float((mhz[busy_only] != 600).mean()) if busy_only.sum() else 1.0   # no clean busy sample: unknown
        brk = before | after
        starved = float(np.median(took[busy])) if busy.sum() else 0.0
        if variant == "before" or after.sum() < 5:
            idle = float(w[before].mean())
        else:
            idle = 0.5 * (float(w[before].mean()) + float(w[after].mean()))
        Tb = float(T[busy].mean())
        Ti = float(np.concatenate([T[before], T[after]]).mean()) if (after.sum() >= 5 and variant != "before") else float(T[before].mean())
        over = float(w[busy].mean()) - idle - (leak_slope(0.5 * (Tb + Ti)) * (Tb - Ti) if variant == "std" else 0.0)
        rs = [r for r in runs if r["label"] == lab]
        out[lab] = {"over_idle_w": over, "wall_s": hi - lo, "runs": rs, "die_c": Tb, "clock_moved_frac": moved, "sampler_median_ms": starved,
                    "bracket_mhz": float(np.median(mhz[brk])), "bracket_at600_frac": float((mhz[brk] == 600).mean()),
                    "bracket_minion_mv": float(np.nanmedian(mv[brk])) if np.isfinite(mv[brk]).any() else None,
                    "busy_mhz": float(np.median(mhz[busy_only])) if busy_only.sum() else None,
                    "busy_minion_mv": float(np.nanmedian(mv[busy_only])) if busy_only.sum() and np.isfinite(mv[busy_only]).any() else None}
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
                    "die_c": round(b["die_c"], 2), "bracket_mhz": b.get("bracket_mhz"), "busy_mhz": b.get("busy_mhz")}
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
    """The new passes of one card: [(pass, contents, values)], plus a per-pass log and the dropped bursts.
    aifoundry2 and aifoundry3 follow the registered rules unchanged; other cards follow clock_rule(card)."""
    rule = clock_rule(card)
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
        if meta.get("off600_scope") and meta["off600_scope"] != rule:
            entry["warning"] = f"block.sh applied the 600 MHz rule '{meta['off600_scope']}', the reducer applies '{rule}' to {card}"
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
                halves[half] = reduce_dir(hd, variant, "busy" if rule == "busy" else "all")
            except Exception as e:  # noqa: BLE001 - a damaged half is reported, not fatal
                entry.setdefault("errors", []).append(f"{half}: {e!r}")
        entry["samples"], entry["off600"] = n_all, off_all
        # the windows (quality.py): each window's clock, the idle clock, and the busy-sample count of the busy rule
        try:
            qw = Q.summarize(pd, rule)
        except Exception as e:  # noqa: BLE001
            qw = None; entry.setdefault("errors", []).append(f"windows: {e!r}")
        if qw:
            entry["windows"] = {w: {"n": qw[w]["n"], "off600": qw[w]["off600"], "clock_mhz": qw[w]["clock_mhz"],
                                    "minion_mv_median": qw[w]["minion_mv_median"]} for w in ("busy", "gap", "bracket")}
            entry["idle_clock_mhz"] = qw["idle_clock_mhz"]
        st = os.path.join(pd, "state.jsonl")
        if os.path.exists(st):   # block.sh card_state: ettelem config at the pass's start and end
            entry["card_state"] = [json.loads(l) for l in open(st) if l.startswith("{")]
        # PLAN3 common rules: "aifoundry2 repeats with any sample off 600 MHz are dropped and re-run". aifoundry3 is
        # pinned at 600 MHz and has no pass-level rule: its bursts fall under the V3-RL burst rule (> 2% off 600).
        if off_all > 0 and card == A2:
            entry["skipped"] = f"{off_all} of {n_all} samples off 600 MHz: pass dropped (common rule, aifoundry2), re-run it"
            log.append(entry); continue
        # the other governor-free cards (amendment): the same rule on busy samples only; card 0's idle is 300 MHz
        if rule == "busy" and (qw is None or qw["busy"]["off600"] > 0):
            entry["skipped"] = (f"{qw['busy']['off600']} of {qw['busy']['n']} busy samples off 600 MHz: pass dropped (busy rule, {card}), re-run it"
                                if qw else "busy windows unreadable: pass dropped (busy rule)")
            log.append(entry); continue
        V = pass_values(halves, dropped, f"{card}/p{K}", variant)
        entry["kept_bursts"] = sum(1 for b in V["bursts"].values() if not b.get("dropped"))
        entry["dropped_bursts"] = [k for k, b in V["bursts"].items() if b.get("dropped")]
        log.append(entry)
        out.append((K, contents, V))
    return out, log, dropped


def load_legacy(card, dropped):
    """The committed 23 Sep rl-passes (RL-X4's byte side): docs/reports/data/2026-09-23-reruns-*/rl-pass<k>."""
    d = {A2: "2026-09-23-reruns-aifoundry2-warm", A3: "2026-09-23-reruns-aifoundry3"}.get(card)
    out = []
    if d is None:
        return out            # no 23 Sep passes on the other cards
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

# ---------------------------------------------------------------- all_cards: the claim over every card of the campaign


def welch_conf(a, b, conf):
    """a - b on repeat-level values: Welch interval at level conf (the all_cards pairwise comparisons; the registered
    outcomes use welch() above)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2:
        return None
    d = float(a.mean() - b.mean())
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    se = math.sqrt(va + vb)
    if se == 0:
        return {"diff": d, "se": 0.0, "df": None, "ci": [d, d], "conf": round(conf, 5)}
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    h = t_ppf(1 - (1 - conf) / 2, df) * se
    return {"diff": round(d, 4), "se": round(se, 4), "df": round(df, 2), "ci": [round(d - h, 4), round(d + h, 4)], "conf": round(conf, 5)}


def cards_list(cs):
    return ", ".join(short(c) for c in cs)


def ac_each(exp, n_of, holds, what, reported=(), info=None):
    """A claim tested on each card: PASS if it holds on every card, CARD-DIFFERENT if on some, FAIL if on none;
    INSUFFICIENT if a tested card has fewer than NMIN kept repeats (the verdict over the other cards is given as
    over_sufficient, for information). reported: cards shown in per_card but not tested (a band registered for
    another card only)."""
    tested = [c for c in exp if c not in reported]
    lack = {c: n_of(c) for c in tested if n_of(c) < NMIN}
    ok = [c for c in tested if c not in lack]
    h = {c: bool(holds(c)) for c in ok}

    def verdict(cs):
        if not cs:
            return None
        n = sum(h[c] for c in cs)
        return "PASS" if n == len(cs) else "CARD-DIFFERENT" if n else "FAIL"

    res = {"test": f"on each card: {what}", "cards": tested, "reported_cards": [c for c in exp if c in reported], "holds": h}
    if not tested:
        res.update(outcome="INSUFFICIENT", reading=f"{what}: no card to test")
    elif lack:
        v = verdict(ok)
        res.update(outcome="INSUFFICIENT", lacking=lack, over_sufficient={"cards": ok, "outcome": v},
                   reading=f"{what}: fewer than {NMIN} kept repeats on " + ", ".join(f"{short(c)} (n={n})" for c, n in lack.items())
                   + (f"; over {cards_list(ok)} alone: {v}" if v else ""))
    else:
        v = verdict(tested)
        res.update(outcome=v, reading=f"{what}: " + {"PASS": f"holds on every card ({cards_list(tested)})",
                                                     "CARD-DIFFERENT": f"holds on {cards_list(c for c in tested if h[c])} only, not on {cards_list(c for c in tested if not h[c])}",
                                                     "FAIL": f"holds on no card ({cards_list(tested)})"}[v])
    if info:
        res.update(info)
    return res


def pairwise(cs, series):
    """Welch between every pair of cards, each at 1 - 0.01/pairs (Bonferroni over the pairs; with two cards this is
    the registered 99%)."""
    pairs = list(itertools.combinations(cs, 2))
    if not pairs:
        return None, []
    conf = 1 - 0.01 / len(pairs)
    W = {f"{short(a)} - {short(b)}": welch_conf(vals(series[a]), vals(series[b]), conf) for a, b in pairs}
    return {"pair_conf": round(conf, 5), "pairs": W}, [k for k, w in W.items() if w and excl0(w["ci"])]


def ac_between(exp, series, what, unit, log=False, info=None):
    """A comparison of the cards (the registered Welch between aifoundry2 and aifoundry3) over every pair of cards:
    CARD-DIFFERENT if any pair differs (per-card values), else PASS (the pooled value). log: the series holds logs
    (the pooled value and the per-card means are then geometric)."""
    lack = {c: series[c]["n"] for c in exp if series[c]["n"] < NMIN}
    ok = [c for c in exp if c not in lack]

    def verdict(cs):
        det, diff = pairwise(cs, series)
        if det is None:
            return None, {}
        pooled = float(np.mean(np.concatenate([vals(series[c]) for c in cs])))
        det.update(differing_pairs=diff, pooled=round(math.exp(pooled) if log else pooled, 4))
        return ("CARD-DIFFERENT" if diff else "PASS"), det

    def m(c):
        s = series[c]
        return None if not s["n"] else round(math.exp(s["mean"]), 4) if log else s["mean"]

    res = {"test": f"every pair of cards: Welch on per-pass {what}{' (logs)' if log else ''}, each pair at 1 - 0.01/pairs (Bonferroni)",
           "cards": list(exp), "per_card_mean": {c: m(c) for c in exp}}
    if lack:
        v, det = verdict(ok)
        res.update(outcome="INSUFFICIENT", lacking=lack, over_sufficient={"cards": ok, "outcome": v, **det},
                   reading=f"{what}: fewer than {NMIN} kept passes on " + ", ".join(f"{short(c)} (n={n})" for c, n in lack.items())
                   + (f"; over {cards_list(ok)} alone: {v}" if v else ""))
    else:
        v, det = verdict(list(exp))
        if v is None:
            res.update(outcome="INSUFFICIENT", reading=f"{what}: one card only, nothing to compare")
        else:
            res.update(outcome=v, **det)
            per = ", ".join(f"{short(c)} {m(c):.3f}" for c in exp)
            res["reading"] = (f"{what}: cards differ ({'; '.join(det['differing_pairs'])} at {det['pair_conf']:.4f}); per card {per} {unit}"
                              if v == "CARD-DIFFERENT" else f"{what}: no pair of cards differs; pooled {det['pooled']:.3f} {unit} (per card {per})")
    if info:
        res.update(info)
    return res


def ac_named(card, exp, n_of, holds, what, info=None):
    """An item the registered rule decides on one named card (RL-b on aifoundry2, RL-c on aifoundry3): the other
    cards are reported, not tested."""
    res = ac_each([card], n_of, holds, what, info=dict(info or {}, reported_cards=[c for c in exp if c != card],
                                                          note=f"decided on {card} as registered; the other cards are reported in per_card"))
    if res["outcome"] in ("PASS", "FAIL"):
        res["reading"] = f"{what}: {'holds' if res['outcome'] == 'PASS' else 'does not hold'} on {card}, where the item is decided (the other cards are reported)"
    return res


def idle_summary(log):
    """A card's idle clock over its kept passes: the idle brackets' clock (MHz -> samples), their median minion
    voltage, the busy samples' clock, and the power-state names block.sh read (ettelem config)."""
    kept = [e for e in log if "skipped" not in e and "windows" in e]
    hist, bh, mvs, states = {}, {}, [], {}   # states: "<at>: <power state> <MHz> <mV>" -> passes
    for e in kept:
        for k, v in e["windows"]["bracket"]["clock_mhz"].items():
            hist[k] = hist.get(k, 0) + v
        for k, v in e["windows"]["busy"]["clock_mhz"].items():
            bh[k] = bh.get(k, 0) + v
        mvs.append(e["windows"]["bracket"]["minion_mv_median"])
        for st in e.get("card_state", []):
            cfg = st.get("config") or {}
            if cfg.get("power_state_name"):
                k = f"{st.get('at')}: {cfg['power_state_name']} {cfg.get('minion_mhz', '?')} MHz {cfg.get('minion_mv', '?')} mV"
                states[k] = states.get(k, 0) + 1
    n = sum(hist.values())
    # for information: the same over every finished pass with windows, dropped ones included (a card whose passes
    # were all dropped by its 600 MHz rule still shows which idle and busy clocks it ran at)
    ah, abh = {}, {}
    for e in log:
        if "windows" in e:
            for k, v in e["windows"]["bracket"]["clock_mhz"].items():
                ah[k] = ah.get(k, 0) + v
            for k, v in e["windows"]["busy"]["clock_mhz"].items():
                abh[k] = abh.get(k, 0) + v
    return {"passes": len(kept), "idle_clock_mhz": Q.mode_clock(hist), "bracket_clock_mhz": hist,
            "bracket_at600_frac": round(hist.get("600", 0) / n, 4) if n else None,
            "bracket_minion_mv_median": Q.median(mvs), "busy_clock_mhz": Q.mode_clock(bh), "card_state": states,
            "all_finished_passes": {"passes": sum(1 for e in log if "windows" in e), "bracket_clock_mhz": ah,
                                    "busy_clock_mhz": abh}}


def idle_note(IDLE, cards):
    """The page's note when a card's idle brackets are not at 600 MHz: its over-idle values then include the step
    from its idle state up to the bursts' operating point."""
    odd = [c for c in cards if IDLE[c]["idle_clock_mhz"] is not None and
           (IDLE[c]["idle_clock_mhz"] != 600 or (IDLE[c]["bracket_at600_frac"] or 0) < 0.98)]
    if not odd:
        return None
    return ("; ".join(f"{c} idles at {IDLE[c]['idle_clock_mhz']} MHz ({IDLE[c]['bracket_at600_frac']:.0%} of its idle-bracket samples at 600 MHz"
                      + (f", minion {IDLE[c]['bracket_minion_mv_median']:.0f} mV" if IDLE[c]["bracket_minion_mv_median"] else "") + ")" for c in odd)
            + ": on such a card every over-idle watt and pJ/B includes the step from its idle state up to the bursts' 600 MHz "
              "operating point, so its values are not comparable with a card idling at 600 MHz; a difference between two bursts "
              "of the same card (spin - ring, c4 - c1, L2 - scratchpad, random - zeros) largely cancels it")


def build(data, flop, legacy=True, include_failed=False, expected=None, low_edge=None):
    # every card directory under --data with an rl/ inside (a card id: aifoundry<N> or aifoundry<N>-c<M>)
    present = [d for d in sorted(os.listdir(data)) if re.match(r"^aifoundry\d+(-c\d+)?$", d)
               and os.path.isdir(os.path.join(data, d, "rl"))] if os.path.isdir(data) else []
    EXP = card_order(expected) if expected else card_order(set(campaign.CAMPAIGN) | set(present))
    ALL = card_order(set(EXP) | set(CARDS) | set(present))
    P, LOG, DROP = {}, {}, []
    for c in ALL:
        P[c], LOG[c], dr = load_new(data, c, include_failed)
        DROP += dr
    IDLE = {c: idle_summary(LOG[c]) for c in ALL}
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
    S = {c: summ(per_pass(P[c], lambda V, _: slope_fit(V)[0])) for c in ALL}
    it = card_diff_item("RL-a", "mesh slope (five 1 KB xshire rings)", CL["a"],
                        "mesh slope over the five 1 KB cross-shire rings a2 2.3+-0.5, a3 1.3+-0.5 pJ/B per hop.",
                        "Welch 99% of the per-pass slope difference excludes 0 (6 new passes per card) -> CARD-DIFFERENT stands with per-card slopes; else pooled with +-50%.",
                        S, {A2: (1.8, 2.8), A3: (0.8, 1.8)}, +1, "slopes (pJ/B per mean hop, xshire8/1/4/2/6)", "pJ/B/hop",
                        " (+-50% on the page)")
    it["all_cards"] = ac_between(EXP, S, "mesh slope", "pJ/B/hop", info={"bands_reported_only_for_other_cards": "the per-card bands are registered for aifoundry2 and aifoundry3 only"})
    items.append(it)

    # ---- RL-b: aifoundry2 "leaving the shire" step = intercept - shire ring - one hop
    S = {c: summ(per_pass(P[c], lambda V, _: slope_fit(V)[1] - V["ring_pj"]["shire"] - slope_fit(V)[0])) for c in ALL}
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
    items[-1]["all_cards"] = ac_named(A2, EXP, lambda c: S[c]["n"], lambda c: S[c]["ci99"][0] > 0, "leaving-the-shire step > 0 at 99%",
                                      info={"info_step_ci99": {c: S[c].get("ci99") for c in ALL}})

    # ---- RL-c: small messages (128 B rows) on aifoundry3, each difference on its own
    for a, b, pv in (("shire-c4", "shire", 1.0), ("xshire1-c4", "xshire1", 3.6)):
        S = {c: summ(per_pass(P[c], lambda V, _, a=a, b=b: V["ring_pj"][a] - V["ring_pj"][b])) for c in ALL}
        part = f"{a} - {b}"
        pred = "aifoundry3: shire-c4 - shire = +1.0 and xshire1-c4 - xshire1 = +3.6 pJ/B."
        rule = "99% t excludes 0 (6 passes) on aifoundry3 -> \"small messages cost more\" on both cards."
        s3 = S[A3]
        ac = ac_named(A3, EXP, lambda c, S=S: S[c]["n"], lambda c, S=S: S[c]["ci99"][0] > 0, f"{part} > 0 at 99%",
                      info={"info_sign_each_card": {c: (None if S[c]["n"] < NMIN else "> 0" if S[c]["ci99"][0] > 0 else "not > 0") for c in ALL}})
        if s3["n"] < NMIN:
            items.append(entry("RL-c", part, CL["c"], pred, rule, S, "99% t on per-pass paired differences, aifoundry3",
                               "INSUFFICIENT", f"{part}: fewer than {NMIN} kept aifoundry3 passes (n={s3['n']})", predicted=pv, all_cards=ac))
            continue
        ok = s3["ci99"][0] > 0
        a2note = ""
        if S[A2]["n"] >= NMIN:
            a2note = "; a2 " + ("also > 0" if S[A2]["ci99"][0] > 0 else "NOT > 0 in the new passes") + f" {fmt(S[A2])}"
        items.append(entry("RL-c", part, CL["c"], pred, rule, S, "99% t on per-pass paired differences, aifoundry3 (aifoundry2 shown)",
                           "PASS" if ok else "FAIL",
                           f"{part} a3 {fmt(s3)} pJ/B (predicted {pv:+.1f}): " + ("small messages cost more" if ok else "not established") + a2note,
                           ok, predicted=pv, predicted_in_ci99=bool(s3["ci99"][0] <= pv <= s3["ci99"][1]), all_cards=ac))

    # ---- RL-d: relay DRAM / next shire, per card; relay DRAM a3/a2 (Welch 99% on logs)
    pred = "relay DRAM/next-shire ratio a2 11.2+-0.6, a3 13.5+-0.8; relay DRAM a3/a2 1.07+-0.03."
    rule = "Welch 99% on log ratios."
    L = {c: summ(per_pass(P[c], lambda V, _: math.log(V["relay_pj"]["dram"] / V["relay_pj"]["hop"]))) for c in ALL}
    media = {c: {m: summ(per_pass(P[c], lambda V, _, m=m: V["relay_pj"][m])) for m in MEDIA} for c in ALL}
    S = {}
    for c, band in [(A2, (10.6, 11.8)), (A3, (12.7, 14.3))] + [(c, None) for c in ALL if c not in CARDS]:
        S[c] = {"n": L[c]["n"], "passes": L[c]["passes"], "ratio_per_pass": [round(math.exp(x), 3) for x in L[c]["values"]],
                "relay_pj_per_byte": media[c]}
        if band:
            S[c]["band"] = band
        if L[c]["n"]:
            S[c]["ratio_geo_mean"] = round(math.exp(L[c]["mean"]), 3)
            if band:
                S[c]["in_band"] = inband(S[c]["ratio_geo_mean"], *band)
        if "ci99" in L[c]:
            S[c]["ratio_ci99"] = [round(math.exp(x), 3) for x in L[c]["ci99"]]
    ac = ac_between(EXP, L, "relay DRAM / next-shire ratio", "x", log=True)
    if not enough(L[A2], L[A3]):
        items.append(entry("RL-d", "relay DRAM / next shire", CL["d"], pred, rule, S, "Welch 99% on per-pass log(DRAM/next shire), a2 vs a3",
                           "INSUFFICIENT", f"relay ratio: fewer than {NMIN} kept passes on a card (a2 n={L[A2]['n']}, a3 n={L[A3]['n']})", all_cards=ac))
    else:
        w = welch(vals(L[A2]), vals(L[A3]))
        r = {k: (round(math.exp(v), 4) if k == "diff" else [round(math.exp(x), 4) for x in v] if k == "ci99" else v) for k, v in w.items()}
        pooled = math.exp(float(np.mean(np.concatenate([vals(L[A2]), vals(L[A3])]))))
        held = S[A2].get("in_band") and S[A3].get("in_band")
        if excl0(w["ci99"]):
            items.append(entry("RL-d", "relay DRAM / next shire", CL["d"], pred, rule, S, "Welch 99% on per-pass log(DRAM/next shire), a2 vs a3",
                               "CARD-DIFFERENT", f"relay DRAM/next shire differs by card: a2 {S[A2]['ratio_geo_mean']}x, a3 {S[A3]['ratio_geo_mean']}x "
                               f"(a2/a3 {r['diff']:.3f}, 99% [{r['ci99'][0]:.3f}, {r['ci99'][1]:.3f}])", held, welch_log=w, ratio_a2_over_a3=r, all_cards=ac))
        else:
            items.append(entry("RL-d", "relay DRAM / next shire", CL["d"], pred, rule, S, "Welch 99% on per-pass log(DRAM/next shire), a2 vs a3",
                               "PASS", f"relay DRAM/next shire the same on both cards at 99%: pooled {pooled:.2f}x (a2/a3 99% [{r['ci99'][0]:.3f}, {r['ci99'][1]:.3f}])",
                               held, welch_log=w, ratio_a2_over_a3=r, pooled_ratio=round(pooled, 3), all_cards=ac))
    L = {c: summ(per_pass(P[c], lambda V, _: math.log(V["relay_pj"]["dram"]))) for c in ALL}
    S = {c: {"n": L[c]["n"], "passes": L[c]["passes"], "relay_dram_pj_per_byte": media[c]["dram"]} for c in ALL}
    ac = ac_between(EXP, L, "log relay DRAM pJ/B", "pJ/B", log=True,
                    info={"info_ratio_to_aifoundry2": {c: (round(math.exp(L[c]["mean"] - L[A2]["mean"]), 4) if L[c]["n"] and L[A2]["n"] else None) for c in ALL},
                          "note": "the registered ratio a3/a2 1.07+-0.03 is specific to those two cards: the other cards' ratios to aifoundry2 are reported"})
    if not enough(L[A2], L[A3]):
        items.append(entry("RL-d", "relay DRAM a3/a2", CL["d"], pred, rule, S, "Welch 99% on per-pass log(relay DRAM pJ/B), a3 vs a2",
                           "INSUFFICIENT", f"relay DRAM: fewer than {NMIN} kept passes on a card (a2 n={L[A2]['n']}, a3 n={L[A3]['n']})", all_cards=ac))
    else:
        w = welch(vals(L[A3]), vals(L[A2]))
        rr, ci = math.exp(w["diff"]), [math.exp(x) for x in w["ci99"]]
        held = inband(rr, 1.04, 1.10)
        oc = "CARD-DIFFERENT" if excl0(w["ci99"]) else "PASS"
        rd = (f"relay DRAM a3/a2 {rr:.3f} (99% [{ci[0]:.3f}, {ci[1]:.3f}]): " +
              ("the cards differ" if oc == "CARD-DIFFERENT" else "the same on both cards at 99%") +
              f"; a2 {fmt(media[A2]['dram'], 1)}, a3 {fmt(media[A3]['dram'], 1)} pJ/B")
        items.append(entry("RL-d", "relay DRAM a3/a2", CL["d"], pred, rule, S, "Welch 99% on per-pass log(relay DRAM pJ/B), a3 vs a2",
                           oc, rd, held, welch_log=w, ratio_a3_over_a2={"ratio": round(rr, 4), "ci99": [round(x, 4) for x in ci]}, all_cards=ac))

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
    # the other cards: the same test against their own catalogue's low edge (--low-edge, from V3-CATFULL); the 23 Sep
    # catalogue has aifoundry2 and aifoundry3 only
    below_all = dict(below)
    for c in ALL:
        if c in CARDS:
            continue
        m, lo_c = media[c]["scp"], list((low_edge or {}).get(c) or [])
        S[c] = {"measured": m, "low_edge_per_catalogue_pass": lo_c or None, "low_edge_source": "--low-edge" if lo_c else None, "n": m["n"]}
        if m["n"]:
            S[c]["measured_in_band"] = inband(m["mean"], 3.95, 4.05)
        if lo_c:
            S[c]["low_edge_mean"] = round(float(np.mean(lo_c)), 4); S[c]["low_edge_in_band"] = inband(S[c]["low_edge_mean"], 4.30, 4.40)
        if m["n"] >= NMIN and len(lo_c) >= 2:
            w = welch(vals(m), lo_c); S[c]["welch_measured_minus_low"] = w
            below_all[c] = w["ci99"][1] < 0
            S[c]["side"] = "below" if below_all[c] else "above" if w["ci99"][0] > 0 else "at"
    lo_n = {c: (len(low.get(c) or []) if c in CARDS else len((low_edge or {}).get(c) or [])) for c in ALL}
    ac = ac_each(EXP, lambda c: media[c]["scp"]["n"] if (lo_n[c] >= 2 and c in below_all) else min(media[c]["scp"]["n"], lo_n[c]),
                 lambda c: below_all[c], "relay own scratchpad below its card's catalogue low edge (Welch 99%)",
                 info={"low_edge_passes": lo_n, "note": "the low edge is each card's own catalogue: 23 Sep for aifoundry2 and aifoundry3, "
                       "--low-edge (V3-CATFULL) for the other cards; a card without one is INSUFFICIENT"})
    if not ok_n:
        items.append(entry("RL-f", "relay own scratchpad vs bracket low edge", CL["f"], pred, rule, S, "Welch 99% (new relay scp passes - catalogue low edge per pass), each card",
                           "INSUFFICIENT", f"relay own scratchpad: fewer than {NMIN} kept passes on a card (a2 n={media[A2]['scp']['n']}, a3 n={media[A3]['scp']['n']})",
                           all_cards=ac))
    else:
        nb = sum(below.values())
        oc = "PASS" if nb == 2 else "CARD-DIFFERENT" if nb == 1 else "FAIL"
        rd = (f"relay own scratchpad a2 {fmt(media[A2]['scp'])}, a3 {fmt(media[A3]['scp'])} vs low edge a2 {S[A2]['low_edge_mean']:.2f}, a3 {S[A3]['low_edge_mean']:.2f}: " +
              {"PASS": "below its bracket on both cards", "CARD-DIFFERENT": "below on " + ",".join(c for c in CARDS if below[c]) + " only",
               "FAIL": "at the low edge (not below at 99%)"}[oc] +
              "".join(f"; {c} ABOVE the low edge at 99%" for c in CARDS if S[c]["side"] == "above"))
        items.append(entry("RL-f", "relay own scratchpad vs bracket low edge", CL["f"], pred, rule, S,
                           "Welch 99% (new relay scp passes - catalogue low edge per pass), each card", oc, rd, held, all_cards=ac))

    # ---- RL-g: L1 level a2 - a3, own-scratchpad level a3 - a2 (all passes), L2 - scratchpad per card
    lev = {c: {l: summ(per_pass(P[c], lambda V, _, l=l: V["level_pj"][l])) for l in LEVELS} for c in ALL}
    pred_g = ("L1 level a2 - a3 = +0.18+-0.06 pJ/B; own-scratchpad level a3 - a2 = +0.23+-0.06; "
              "L2 - scratchpad a2 +0.18+-0.15, a3 -0.28+-0.15.")
    rule_g = "as RL-a; both L2 - scratchpad intervals containing 0 -> \"the same within +-10%\"."
    it = card_diff_item("RL-g", "L1 level a2 - a3", CL["g"], pred_g, rule_g, {c: dict(lev[c]["l1"]) for c in ALL},
                        {"diff": (0.12, 0.24)}, +1, "L1 level (pJ/B)", "pJ/B", "")
    it["all_cards"] = ac_between(EXP, {c: lev[c]["l1"] for c in ALL}, "L1 level", "pJ/B",
                                 info={"note": "the registered difference a2 - a3 = +0.18+-0.06 is specific to those two cards; the other cards are compared, not banded"})
    items.append(it)
    it = card_diff_item("RL-g", "own-scratchpad level a3 - a2", CL["g"], pred_g, rule_g, {c: dict(lev[c]["scp-local"]) for c in ALL},
                        {"diff": (0.17, 0.29)}, -1, "own-scratchpad level (pJ/B), all passes (both contents)", "pJ/B", "")
    if it["outcome"] != "INSUFFICIENT":
        it["reading"] += " [confounded: every pass is prefilled, zeros/random alternating; see RL-h]"
    it["note"] = ("every V3-RL pass is prefilled (odd zeros, even random, the same schedule on both cards), so this compares the cards "
                  "averaged over the two contents; RL-h compares them at equal contents")
    it["info_by_contents"] = {k: {c: summ(per_pass([x for x in P[c] if x[1] == k], lambda V, _: V["level_pj"]["scp-local"])) for c in ALL}
                              for k in ("zeros", "random")}
    it["all_cards"] = ac_between(EXP, {c: lev[c]["scp-local"] for c in ALL}, "own-scratchpad level (both contents)", "pJ/B",
                                 info={"note": "confounded by the contents arm as the registered part is; RL-h compares at equal contents"})
    items.append(it)
    S = {c: summ(per_pass(P[c], lambda V, _: V["l2_minus_scp"])) for c in ALL}
    for c, band in ((A2, (0.03, 0.33)), (A3, (-0.43, -0.13))):
        S[c]["band"] = band
        if S[c]["n"]:
            S[c]["in_band"] = inband(S[c]["mean"], *band)
    for c in ALL:
        S[c]["l2_level"] = lev[c]["l2"]; S[c]["scp_local_level"] = lev[c]["scp-local"]
    ac = ac_between(EXP, S, "L2 - own scratchpad", "pJ/B")
    if ac["outcome"] == "PASS":        # no pair differs: then, as registered, each card's interval against 0
        c0 = {c: not excl0(S[c]["ci99"]) for c in EXP}
        n0 = sum(c0.values())
        ac["contains_0"] = c0
        ac["outcome"] = "PASS" if n0 == len(EXP) else "CARD-DIFFERENT" if n0 else "FAIL"
        ac["reading"] = ("L2 - own scratchpad: " + {"PASS": "the same within +-10% on every card",
                                                    "CARD-DIFFERENT": f"the same on {cards_list(c for c in EXP if c0[c])} only",
                                                    "FAIL": "L2 and own scratchpad differ on every card, with no card difference"}[ac["outcome"]]
                         + " [confounded by the contents arm; see RL-h]")
    if not enough(S[A2], S[A3]):
        items.append(entry("RL-g", "L2 - own scratchpad", CL["g"], pred_g, rule_g, S, "99% t per card on per-pass (L2 - scp-local), mean of the ABBA bursts; Welch between cards",
                           "INSUFFICIENT", f"L2 - scratchpad: fewer than {NMIN} kept passes with all four ABBA bursts on a card (a2 n={S[A2]['n']}, a3 n={S[A3]['n']})",
                           all_cards=ac))
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
                           info_l2_level_a2_minus_a3=welch(vals(lev[A2]["l2"]), vals(lev[A3]["l2"])) if enough(lev[A2]["l2"], lev[A3]["l2"]) else None,
                           all_cards=ac))

    # ---- RL-h: the contents arm
    pred_h = ("contents arm: each card's scp-local level follows the prefill (zeros 2.0+-0.3, random 4.2+-0.5 pJ/B) and at equal "
              "contents a3 - a2 is within +-0.1 pJ/B.")
    rule_h = "as RL-a on the prefilled passes; a3 - a2 inside +-0.1 -> the card difference is contents, and the page says so."
    G = {k: {c: summ(per_pass([x for x in P[c] if x[1] == k], lambda V, _: V["level_pj"]["scp-local"])) for c in ALL} for k in ("zeros", "random")}
    bands = {"zeros": (1.7, 2.3), "random": (3.7, 4.7)}
    S = {c: {k: dict(G[k][c], band=bands[k], in_band=inband(G[k][c].get("mean"), *bands[k]) if G[k][c]["n"] else None) for k in G} for c in ALL}
    gn = {c: min(G[k][c]["n"] for k in G) for c in ALL}
    ac1 = ac_each(EXP, lambda c: gn[c], lambda c: bool(S[c]["zeros"]["in_band"] and S[c]["random"]["in_band"]),
                  "scp-local level in the zeros band (1.7-2.3) on zeros passes and the random band (3.7-4.7) on random passes")
    for c in ALL:
        if c not in CARDS and gn[c] >= NMIN:
            S[c]["welch_random_minus_zeros"] = welch(vals(G["random"][c]), vals(G["zeros"][c]))
    # part 2 over every pair of cards, each contents group on its own (Bonferroni over the pairs)
    lack = {c: gn[c] for c in EXP if gn[c] < NMIN}
    okc = [c for c in EXP if c not in lack]

    def h2(cs):
        dets = {k: pairwise(cs, G[k]) for k in G}
        if any(d[0] is None for d in dets.values()):
            return None, {}
        diff = any(d[1] for d in dets.values())
        inside = all(abs(w["diff"]) <= 0.1 for d in dets.values() for w in d[0]["pairs"].values() if w)
        return ("CARD-DIFFERENT" if diff else "PASS" if inside else "FAIL"), {k: dict(d[0], differing_pairs=d[1]) for k, d in dets.items()}

    ac2 = {"test": "every pair of cards, Welch within each contents group, each pair at 1 - 0.01/pairs (Bonferroni): a pair differs -> "
                   "CARD-DIFFERENT; else every pairwise difference within +-0.1 pJ/B in both groups -> PASS; else FAIL", "cards": EXP}
    if lack:
        v, det = h2(okc)
        ac2.update(outcome="INSUFFICIENT", lacking=lack, over_sufficient={"cards": okc, "outcome": v, "by_contents": det},
                   reading="contents arm: fewer than 3 kept passes of each contents on " + ", ".join(f"{short(c)} (n={n})" for c, n in lack.items())
                   + (f"; over {cards_list(okc)} alone: {v}" if v else ""))
    else:
        v, det = h2(EXP)
        ac2.update(outcome=v or "INSUFFICIENT", by_contents=det,
                   reading="at equal contents: " + {"CARD-DIFFERENT": "some cards still differ", "PASS": "every pair within +-0.1 pJ/B: the card difference is contents",
                                                    "FAIL": "no pair differs at the corrected level, but not every pair within +-0.1", None: "one card only"}[v])
    if not all(G[k][c]["n"] >= NMIN for k in G for c in CARDS):
        items.append(entry("RL-h", "scp-local level follows the prefill", CL["h"], pred_h, rule_h, S,
                           "per-card means of the zeros-prefill and random-prefill passes against the registered bands; Welch random - zeros per card for information",
                           "INSUFFICIENT", "contents arm: fewer than 3 kept passes of each contents on a card: " +
                           ", ".join(f"{c[-1]} {k} n={G[k][c]['n']}" for c in CARDS for k in G), all_cards=ac1))
        items.append(entry("RL-h", "a3 - a2 at equal contents", CL["h"], pred_h, rule_h, S, "Welch 99% a3 - a2 within each contents group",
                           "INSUFFICIENT", "contents arm: fewer than 3 kept passes of each contents on a card", all_cards=ac2))
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
                           n == 2, all_cards=ac1))
        W = {k: welch(vals(G[k][A3]), vals(G[k][A2])) for k in G}
        diff = any(excl0(W[k]["ci99"]) for k in G)
        inside = all(abs(W[k]["diff"]) <= 0.1 for k in G)
        oc = "CARD-DIFFERENT" if diff else "PASS" if inside else "FAIL"
        rd = ("a3 - a2 at equal contents: " + "; ".join(f"{k} {W[k]['diff']:+.3f} [{W[k]['ci99'][0]:+.3f}, {W[k]['ci99'][1]:+.3f}]" for k in G) + " pJ/B: " +
              {"CARD-DIFFERENT": "the cards still differ at equal contents", "PASS": "inside +-0.1: the card difference is contents",
               "FAIL": "no difference at 99% but not inside +-0.1: not established"}[oc])
        items.append(entry("RL-h", "a3 - a2 at equal contents", CL["h"], pred_h, rule_h, {c: {k: G[k][c] for k in G} for c in ALL},
                           "Welch 99% a3 - a2 within each contents group (3 passes per card each)", oc, rd, inside,
                           welch_a3_minus_a2=W, info_interval_inside_0p1={k: bool(-0.1 <= W[k]["ci99"][0] and W[k]["ci99"][1] <= 0.1) for k in G},
                           all_cards=ac2))

    # ---- RL-X3 (a): nocbench spin - ring over idle, per pass (spin = mean of the kept first/last brackets)
    pred_x3 = ("(a) nocbench spin - ring over idle per pass: pair +0.0..+0.5 W; neigh and shire within +-0.4 W; xshire2/4/6 >= +0.4 W on both cards; "
               "(d) memhier two-hart spin 2.3-2.8 W, nocbench one-hart spin 2.2-2.6 W; (e) inside-shire ring power above mesh-ring power and "
               "scp-remote cheaper than s->s+8 and s->s+16 in every pass.")
    rule_x3 = ("(a) \"less than spinning\" kept for a ring only if its interval is > 0 on both cards, else \"about as much as spinning (+-x W)\"; "
               "(d), (e) every pass on both cards -> PROVEN-BOTH.")
    RB = {"pair": (0.0, 0.5), "neigh": (-0.4, 0.4), "shire": (-0.4, 0.4), "xshire2": (0.4, math.inf), "xshire4": (0.4, math.inf), "xshire6": (0.4, math.inf)}
    robust = {}
    for var in ("noleak", "before"):
        robust[var] = {c: load_new(data, c, include_failed, var)[0] for c in ALL}
    for r in RINGS:
        S = {c: summ(per_pass(P[c], lambda V, _, r=r: V["nspin_w"] - V["ring_w"][r])) for c in ALL}
        if r in RB:
            for c in ALL:        # registered for "both cards": the bands apply to every card
                S[c]["band"] = [RB[r][0], None if RB[r][1] == math.inf else RB[r][1]]
                if S[c]["n"]:
                    S[c]["in_band"] = inband(S[c]["mean"], *RB[r])
        rob = {var: {c: summ(per_pass(robust[var][c], lambda V, _, r=r: V["nspin_w"] - V["ring_w"][r])).get("ci99") for c in ALL} for var in robust}
        part = f"(a) spin - {r}"
        ac = ac_each(EXP, lambda c, S=S: S[c]["n"], lambda c, S=S: S[c]["ci99"][0] > 0, f"spin - {r} > 0 at 99% (less than spinning)",
                     info={"prediction_held": all(S[c].get("in_band") for c in EXP) if r in RB and all(S[c]["n"] for c in EXP) else None})
        if not enough(S[A2], S[A3]):
            items.append(entry("RL-X3", part, CL["X3"], pred_x3, rule_x3, S, "99% t per card on per-pass (nocbench spin W - ring W over idle)",
                               "INSUFFICIENT", f"spin - {r}: fewer than {NMIN} kept passes on a card (a2 n={S[A2]['n']}, a3 n={S[A3]['n']})",
                               robustness_ci99=rob, all_cards=ac))
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
                           robustness_ci99=rob, all_cards=ac))
    # ---- RL-X3 (d): spin power per pass in its band on every pass
    for key, lab, band in (("nspin_w", "(d) nocbench one-hart spin", (2.2, 2.6)), ("mspin_w", "(d) memhier two-hart spin", (2.3, 2.8))):
        S = {c: summ(per_pass(P[c], lambda V, _, key=key: V[key])) for c in ALL}
        every = {}
        for c in ALL:            # registered for "both cards": the band applies to every card
            S[c]["band"] = band
            every[c] = S[c]["n"] >= NMIN and all(inband(v, *band) for v in S[c]["values"])
            S[c]["every_pass_in_band"] = every[c]
        ac = ac_each(EXP, lambda c, S=S: S[c]["n"], lambda c, every=every: every[c], f"{lab} W over idle in {band[0]}-{band[1]} on every pass")
        if not enough(S[A2], S[A3]):
            items.append(entry("RL-X3", lab, CL["X3"], pred_x3, rule_x3, S, "each pass's over-idle W (mean of the kept first/last brackets) in the band",
                               "INSUFFICIENT", f"{lab}: fewer than {NMIN} kept passes on a card", all_cards=ac))
            continue
        n = sum(every[c] for c in CARDS)
        oc = "PASS" if n == 2 else "CARD-DIFFERENT" if n == 1 else "FAIL"
        items.append(entry("RL-X3", lab, CL["X3"], pred_x3, rule_x3, S, "each pass's over-idle W (mean of the kept first/last brackets) in the band", oc,
                           f"{lab} W over idle: a2 {r2(S[A2]['values'])}, a3 {r2(S[A3]['values'])} (band {band[0]}-{band[1]}): "
                           + ("every pass in band on both cards" if n == 2 else "in band every pass on " + (",".join(c for c in CARDS if every[c]) or "neither card")),
                           n == 2, all_cards=ac))
    # ---- RL-X3 (e1): inside-shire ring power above mesh-ring power in every pass (means over the 1 KB rings)
    def ins_acr(V, _):
        wi = [V["ring_w"][k] for k in INSIDE]; wa = [V["ring_w"][k] for k in FIVE]
        return float(np.mean(wi) - np.mean(wa))
    S = {c: summ(per_pass(P[c], ins_acr)) for c in ALL}
    for c in ALL:
        S[c]["info_min_inside_minus_max_across"] = summ(per_pass(P[c], lambda V, _: min(V["ring_w"][k] for k in INSIDE) - max(V["ring_w"][k] for k in FIVE)))
    items.append(every_pass_item("RL-X3", "(e) inside-shire ring W above mesh-ring W", CL["X3"], pred_x3, rule_x3, S,
                                 "per pass: mean over-idle W of pair/neigh/shire minus mean of the five 1 KB xshire rings (8,1,4,2,6) > 0",
                                 lambda v: v > 0, "inside minus across W", EXP))
    # ---- RL-X3 (e2): scp-remote cheaper than s->s+8 and s->s+16 in every pass (s+16 where its burst was kept)
    def remote_margin(V, _):
        rs = [V["ring_pj"][k] for k in ("xshire8", "xshire16") if V["ring_pj"].get(k) is not None]
        return min(rs) - V["level_pj"]["scp-remote"] if rs and "xshire8" in V["ring_pj"] else None
    S = {c: summ(per_pass(P[c], remote_margin)) for c in ALL}
    for c in ALL:
        S[c]["passes_with_xshire16"] = [K for K, _, V in P[c] if V["ring_pj"].get("xshire16") is not None]
    it = every_pass_item("RL-X3", "(e) scp-remote cheaper than s->s+8 and s->s+16", CL["X3"], pred_x3, rule_x3, S,
                         "per pass: min(xshire8, xshire16 if kept) pJ/B - scp-remote pJ/B > 0", lambda v: v > 0,
                         "ring minus scp-remote pJ/B", EXP)
    no16 = [c for c in CARDS if S[c]["n"] and len(S[c]["passes_with_xshire16"]) < S[c]["n"]]
    if no16 and it["outcome"] != "INSUFFICIENT":
        it["reading"] += "; s->s+16 untested in passes where its burst was dropped (" + ", ".join(
            f"{c} kept in {len(S[c]['passes_with_xshire16'])} of {S[c]['n']}" for c in no16) + ")"
    it["all_cards"]["info_xshire16_kept"] = {c: f"{len(S[c]['passes_with_xshire16'])} of {S[c]['n']}" for c in EXP}
    items.append(it)

    # ---- RL-X4: balance points against the ridges (byte side 23 Sep + V3-RL passes, FLOP side V3-ABL-A blocks)
    items += ridge_items(P, flop, legacy, DROP, CL["X4"], ALL, EXP)

    # ---- every V3-RL value is energy over idle: each card's idle clock, and a note when one is not 600 MHz
    note = idle_note(IDLE, ALL)
    for it in items:
        it["idle_clock_mhz"] = {c: IDLE[c]["idle_clock_mhz"] for c in ALL}
        it["idle_note"] = note
    return {"experiment": "V3-RL", "plan": "docs/reports/data/2026-09-25-claims-v3/PLAN3.md section 2 V3-RL", "data": os.path.abspath(data),
            "cards": {"registered": list(CARDS), "all_cards": EXP, "present": present, "per_card": ALL},
            "rules": {"burst_drop": f"clock off 600 MHz in > {CLOCK_FRAC:.0%} of the burst's samples, or sampler median > {STARVED_MS:.0f} ms",
                      "pass_drop": "aifoundry2: any telemetry sample of the pass off 600 MHz (common rules); both cards: block.json status not ok",
                      "clock_rule_per_card": {c: clock_rule(c) for c in ALL},
                      "clock_rules": {"all": "registered (aifoundry2): pass dropped on any sample off 600 MHz; burst rule over the burst and its idle brackets",
                                      "none": "registered (aifoundry3, pinned): burst rule over the burst and its idle brackets",
                                      "busy": "amendment (other governor-free cards): pass dropped on any busy sample off 600 MHz; burst rule over busy samples; "
                                              "idle brackets and launch gaps never drop (quality.py)"},
                      "all_cards": "each-card claims: PASS on every card / CARD-DIFFERENT on some / FAIL on none; comparisons: every pair of cards, "
                                   "Welch at 1 - 0.01/pairs; INSUFFICIENT if a card lacks 3 kept repeats; bands registered for one card are reported only",
                      "min_kept_repeats": NMIN, "interval": "99% t on pass-level values; Welch between cards"},
            "idle_clock": IDLE, "idle_note": note,
            "passes": LOG, "dropped_bursts": DROP, "items": items}


def every_pass_item(item, part, claims, pred, rule, S, test, ok, what, exp=CARDS):
    every = {c: S[c]["n"] >= NMIN and all(ok(v) for v in S[c]["values"]) for c in S}
    for c in S:
        S[c]["every_pass"] = every[c]
    ac = ac_each(exp, lambda c: S[c]["n"], lambda c: every[c], f"{what} > 0 in every pass")
    if not enough(S[A2], S[A3]):
        return entry(item, part, claims, pred, rule, S, test, "INSUFFICIENT", f"{part}: fewer than {NMIN} kept passes on a card (a2 n={S[A2]['n']}, a3 n={S[A3]['n']})",
                     all_cards=ac)
    n = sum(every[c] for c in CARDS)
    oc = "PASS" if n == 2 else "CARD-DIFFERENT" if n == 1 else "FAIL"
    return entry(item, part, claims, pred, rule, S, test, oc,
                 f"{part}: {what} a2 {r2(S[A2]['values'])}, a3 {r2(S[A3]['values'])}: " +
                 ("every pass on both cards" if n == 2 else "every pass on " + (",".join(c for c in CARDS if every[c]) or "neither card")), n == 2, all_cards=ac)


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


def ridge_items(P, flop, legacy, DROP, claims, ALL=CARDS, EXP=CARDS):
    pred = ("L3 random vs spec 3.0 -> 3.6+-0.5 (above); other shire random -> 2.3+-0.6 (below); zeros in-shire TensorSend vs 8.8 -> 10.0+-1.5 (above).")
    rule = ("byte side 99% t over all passes per card (23 Sep + V3-RL), FLOP side over V3-ABL-A blocks; balance interval [byte lo / FLOP hi, "
            "byte hi / FLOP lo]; a verdict only when both cards' intervals lie on the same side of the ridge, else \"ranges overlap: no verdict\". "
            "ridge-89, ridge-92 and the pairs half of ridge-91 are not tested (margins need 11 to > 100 passes).")
    RG, rsrc = ridges()
    LEG = {c: (load_legacy(c, DROP) if legacy else []) for c in ALL}
    rows = [("L3, random, spec ridge", "l3", "spec", "random", lambda V: V["level_pj"]["l3"], "above", (3.1, 4.1)),
            ("other shire's scratchpad, random, spec ridge", "scp_remote", "spec", "random", lambda V: V["level_pj"]["scp-remote"], "below", (1.7, 2.9)),
            ("in-shire TensorSend (shire ring), zeros, measured ridge", "xbar", "measured", "zeros", lambda V: V["ring_pj"]["shire"], "above", (8.5, 11.5))]
    out = []
    fu = 0.5 if flop and str(flop.get("unit", "pJ/FLOP")).lower() in ("pj/mac", "pj_per_mac") else 1.0
    for part, key, basis, op, get, side_pred, band in rows:
        rg = RG[(key, basis)]
        S = {}
        for c in ALL:
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
        # all cards: the registered rule over every card (aifoundry1's cards have no 23 Sep passes: V3-RL alone)
        lack = {c: min(S[c]["n_new"], S[c]["flop_pj_per_flop"]["n"]) for c in EXP if "side" not in S[c]}

        def x4(cs):
            sides = {S[c]["side"] for c in cs}
            if not cs:
                return None
            if sides == {side_pred}:
                return "PASS"
            if "overlap" in sides:
                return "FAIL"
            return "FAIL" if len(sides) == 1 else "CARD-DIFFERENT"
        okc = [c for c in EXP if c not in lack]
        ac = {"test": "the registered rule over every card: all on the predicted side -> PASS; any overlap -> FAIL (no verdict); all on the other "
                      "side -> FAIL; cards on opposite sides -> CARD-DIFFERENT", "cards": EXP, "sides": {c: S[c].get("side") for c in EXP}}
        if not flop:
            ac.update(outcome="INSUFFICIENT", reading=f"{part}: FLOP side (V3-ABL-A blocks, --flop) not supplied")
        elif lack:
            ac.update(outcome="INSUFFICIENT", lacking=lack, over_sufficient={"cards": okc, "outcome": x4(okc)},
                      reading=f"{part}: fewer than {NMIN} new V3-RL passes or FLOP blocks on " + ", ".join(f"{short(c)} (n={n})" for c, n in lack.items()))
        else:
            v = x4(EXP)
            ac.update(outcome=v, reading=f"{part}: " + ", ".join(f"{short(c)} {S[c]['side']}" for c in EXP) + f" its ridge (predicted {side_pred})")
        if not flop:
            out.append(entry("RL-X4", part, claims, pred, rule, S, test, "INSUFFICIENT",
                             f"{part}: FLOP side (V3-ABL-A blocks, --flop) not supplied", ridge=rg, all_cards=ac)); continue
        if not all("side" in S[c] for c in CARDS):
            out.append(entry("RL-X4", part, claims, pred, rule, S, test, "INSUFFICIENT",
                             f"{part}: fewer than {NMIN} new V3-RL passes or FLOP blocks on a card: " +
                             ", ".join(f"{c[-1]} bytes n={S[c]['n_new']} new + {S[c]['n_legacy']} 23 Sep, flops n={S[c]['flop_pj_per_flop']['n']}" for c in CARDS),
                             ridge=rg, all_cards=ac)); continue
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
                         all(S[c]["point_in_band"] for c in CARDS), ridge=rg, predicted_side=side_pred, all_cards=ac))
    return out


def safe(get, V):
    try:
        x = get(V)
        return x if x is not None and np.isfinite(x) else None
    except (KeyError, TypeError):
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", required=True, help="directory holding one directory per card (aifoundry2/, aifoundry3/, aifoundry1-c0/, ...) laid out like DATA_ROOT")
    ap.add_argument("--out", required=True, help="verdicts JSON to write")
    ap.add_argument("--flop", help="V3-ABL-A FLOP side: {\"<card>\": {\"random\": [pJ/FLOP per block], \"zeros\": [...]}, ..., \"unit\": \"pJ/FLOP\"}")
    ap.add_argument("--low-edge", help="RL-f low edge for cards outside the 23 Sep catalogue: {\"<card>\": [0.5 * (l1fill/stride32/zeros + "
                                       "tstore/scp/zeros) pJ/B, one per catalogue pass], ...} (from V3-CATFULL); aifoundry2 and aifoundry3 always use 23 Sep")
    ap.add_argument("--cards", help="comma-separated cards the all_cards outcome covers (default: the campaign's cards, "
                                    "tools/claims-v3/campaign.py, and any other card under --data)")
    ap.add_argument("--no-legacy", action="store_true", help="RL-X4 byte side without the 23 Sep passes (not the registered rule; for tests)")
    ap.add_argument("--include-failed", action="store_true", help="also use passes whose block.json status is not ok (not the registered rule)")
    a = ap.parse_args()
    flop = json.load(open(a.flop)) if a.flop else None
    low_edge = json.load(open(a.low_edge)) if a.low_edge else None
    expected = [c.strip() for c in a.cards.split(",") if c.strip()] if a.cards else None
    res = build(a.data, flop, legacy=not a.no_legacy, include_failed=a.include_failed, expected=expected, low_edge=low_edge)
    res["flop_source"] = os.path.abspath(a.flop) if a.flop else None
    res["low_edge_source"] = os.path.abspath(a.low_edge) if a.low_edge else None
    json.dump(res, open(a.out, "w"), indent=1, default=lambda o: float(o) if isinstance(o, np.floating) else bool(o) if isinstance(o, np.bool_) else str(o))
    for c in res["cards"]["per_card"]:
        kept = [e["pass"] for e in res["passes"][c] if "skipped" not in e]
        ic = res["idle_clock"][c]
        print(f"{c}: kept passes {kept}; idle clock {ic['idle_clock_mhz']} MHz; skipped " +
              "; ".join(f"p{e['pass']}: {e['skipped']}" for e in res["passes"][c] if "skipped" in e))
    print(f"dropped bursts: {len(res['dropped_bursts'])}")
    if res["idle_note"]:
        print(f"idle note: {res['idle_note']}")
    for e in res["items"]:
        print(f"{e['item']:6s} {e['outcome']:14s} all_cards {e['all_cards']['outcome']:14s} {e['reading']}")


if __name__ == "__main__":
    main()
