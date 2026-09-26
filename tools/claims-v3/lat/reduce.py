#!/usr/bin/env python3
"""V3-LAT reducer: the registered prediction items LAT-M1 ... LAT-R of PLAN3.md §2 "V3-LAT", exactly as registered.

    python3 tools/claims-v3/lat/reduce.py --data <dir> --out <verdicts.json> [--no-search] [--cards c1,c2,...]

<dir> holds one directory per card (aifoundry2/, aifoundry3/, aifoundry1-c0/, aifoundry1-c1/, ...), each laid out
like DATA_ROOT (build/claims-v3/<card>/lat/p<N>/...).
A block counts only if its block.json says "ok"; a unit (mc ms noc sp e4x x3 sg hl rl div) counts only if the
block's marks.jsonl has its "end" mark. Pass K is assembled from block p<K> or from its halves p<K>1 + p<K>2;
blocks 4, 5 and 41-49 are the divergence-only short blocks. Runs on partial data: an item with fewer kept repeats
than it needs on a card is INSUFFICIENT.

Drop rules (registered, aifoundry2 only; aifoundry3 is pinned at 600 MHz and nothing is dropped there):
  - every launch: dropped if a telemetry sample within 0.2 s of it (or, when none falls there, the nearest sample
    on each side) reads mhz.minion != 600, if it has no sample at all, or if its cycles / wall time > 0.6 GHz;
  - memhier chases: also dropped if analyze.py's point_ghz >= 0.65;
  - sgemm (no sampler may run while it holds the management node): kept only if the sampler bursts right before
    and right after the process all read 600 MHz.
A repeat (pass or short block) counts for an item only if every launch the item uses in it is kept (the plan
says "dropped and re-run": a pass with a dropped launch is re-run as pass 6-9).

Outcomes per item: PASS (holds on both cards), FAIL (fails on both), CARD-DIFFERENT (holds on one, fails on the
other), INSUFFICIENT (fewer than the needed kept repeats on a card; 3 passes, 5 short blocks for LAT-S5).

Four cards (amendment for aifoundry1's two cards, README "Four cards"). "outcome" is the registered outcome, computed
exactly as registered from aifoundry2 and aifoundry3 only. "all_cards" adds the same test over every card: the four
campaign cards (aifoundry1-c0, aifoundry1-c1, aifoundry2, aifoundry3; one with no data is INSUFFICIENT) plus any other
card directory under --data, or the list given by --cards. PASS if the item holds on every card, CARD-DIFFERENT if on
some, FAIL if on none, INSUFFICIENT if a card lacks its repeats; a registered either-card rule ("any deviation
falsifies", "dropped on either card") becomes an any-card rule and decides FAIL as before. Parts whose registered band
is a committed value of aifoundry2 or aifoundry3 (LAT-H P1c's per-card host fractions, LAT-R (ii)'s per-card lines and
(v)'s per-card ratios) are REPORTED on the other cards against both committed values, not tested; every other band is
registered for each card and applies unchanged. per_card holds every card's values.
Drop rule on aifoundry1's cards (governor free; card 0's firmware idles the minions at 300 MHz between kernels):
  - a sample that reads the card's idle point (a reading below 600 MHz of the blocks' idle probes, idle.jsonl, or
    300 MHz, the cards' low-power point queried on aifoundry1-c0 on 25 Sep) and lies outside every kernel window of
    its unit is an idle sample: it is set aside, it neither drops nor supports a launch;
  - the registered rule then applies to the remaining samples (within 0.2 s of the launch, else the nearest on each
    side within 5 s: all must read 600 MHz; cycles / wall time > 0.6 GHz drops);
  - a kernel of >= 5 ms whose cycles / wall time is below 0.45 GHz is dropped (it ran at the idle point; the committed
    600 MHz records of nocbench, sparsity, onchip and enercat never read below 0.45 GHz at that length);
  - a launch whose only samples within reach are idle samples is kept on its own implied clock when the kernel is
    >= 5 ms, else on its unit's verdict: kept if the unit has busy evidence and all of it (every non-idle sample, every
    implied clock of a >= 5 ms kernel) reads 600 MHz / 0.45-0.6 GHz; a launch with no sample at all is dropped;
  - sgemm (no sampler while it runs): kept if every bracket sample reads 600 MHz; if some read the idle point and none
    reads anything else, kept only if every other unit of the same block has the verdict above "kept".
aifoundry2 keeps the registered rule unchanged; aifoundry3 is pinned (nothing dropped).
"""
import argparse
import collections
import glob
import gzip
import importlib.util
import json
import math
import os
import re
import statistics
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import campaign  # noqa: E402  (the campaign's cards: amendments A2 and A4)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CARDS = ("aifoundry2", "aifoundry3")    # the registered outcome: these two cards, exactly as registered
CAMPAIGN = tuple(sorted(campaign.CAMPAIGN))   # the campaign's cards for all_cards (amendments A2, A4)
PINNED = {"aifoundry3"}                  # lib.sh: GOV_FREE on every other card
REGISTERED_RULE = {"aifoundry2"}         # governor-free cards judged by the registered drop rule
# the low-power operating point of aifoundry1's cards (300 MHz / 398 mV, queried on c0, firmware 1.4.1, 25 Sep): an
# idle point on both (c1 was seen idling at 600, but if it enters that state its idle samples must not drop its
# bursts); the blocks' idle probes add what they read below 600 MHz
REGISTERED_IDLE = {"aifoundry1-c0": 300, "aifoundry1-c1": 300}
IMPLIED_MIN_GHZ, IMPLIED_MIN_WALL_S = 0.45, 0.005   # aifoundry1's cards: a >= 5 ms kernel below 0.45 GHz is dropped
NEED = 3          # kept repeats per card (common rule)
NEED_SHORT = 5    # LAT-S5: 5 independent short blocks per card (df 4)
T995 = {1: 63.657, 2: 9.925, 3: 5.841, 4: 4.604, 5: 4.032, 6: 3.707, 7: 3.499, 8: 3.355, 9: 3.250, 10: 3.169,
        11: 3.106, 12: 3.055, 13: 3.012, 14: 2.977, 15: 2.947, 16: 2.921, 17: 2.898, 18: 2.878, 19: 2.861,
        20: 2.845, 25: 2.787, 30: 2.750, 40: 2.704, 60: 2.660, 120: 2.617}


def t995(df):
    if df in T995:
        return T995[df]
    ks = sorted(T995)
    if df > ks[-1]:
        return 2.576
    hi = min(k for k in ks if k > df)
    lo = max(k for k in ks if k < df)
    return T995[lo] + (T995[hi] - T995[lo]) * (df - lo) / (hi - lo)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


NOC = load_module(os.path.join(ROOT, "workloads", "nocbench", "analyze.py"), "lat_noc")
MEM = load_module(os.path.join(ROOT, "workloads", "memhier", "analyze.py"), "lat_mem")
ONC = load_module(os.path.join(ROOT, "workloads", "onchip", "analyze_onchip.py"), "lat_onc")
REF = json.load(open(os.path.join(HERE, "ref_committed.json")))


# ------------------------------------------------------------------------------------------------ small helpers
def ci99(vals):
    v = [float(x) for x in vals if x is not None]
    n = len(v)
    if n == 0:
        return {"n": 0}
    m = statistics.mean(v)
    if n < 2:
        return {"n": 1, "mean": m}
    s = statistics.stdev(v)
    h = t995(n - 1) * s / math.sqrt(n)
    return {"n": n, "mean": m, "sd": s, "lo": m - h, "hi": m + h}


def inb(x, lo, hi):
    return x is not None and lo <= x <= hi


def pm(x, tol):
    return (x - tol, x + tol)


def rnd(x, k=4):
    if isinstance(x, float):
        return round(x, k) if math.isfinite(x) else None   # verdicts.json stays valid JSON
    if isinstance(x, dict):
        return {a: rnd(b, k) for a, b in x.items()}
    if isinstance(x, (list, tuple)):
        return [rnd(b, k) for b in x]
    return x


def open_any(path):
    if os.path.exists(path):
        return open(path)
    if os.path.exists(path + ".gz"):
        return gzip.open(path + ".gz", "rt")
    return None


NONHOST = {"telemetry.jsonl", "brackets.jsonl", "launches.jsonl", "marks.jsonl"}   # block files, not host output


def jlines(path):
    """JSON lines of a host printout: '{...}' or 'PREFIX {...}'; missing file -> []."""
    f = open_any(path)
    if f is None:
        return []
    out = []
    for line in f:
        line = line.strip()
        if not line:
            continue
        if not line.startswith("{"):
            head, _, rest = line.partition(" ")
            if not (head.isupper() and rest.startswith("{")):
                continue
            line = rest
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def fit(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    A = np.vstack([np.ones_like(x), x]).T
    (a, b), *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(a), float(b), float(np.abs(y - (a + b * x)).max())


# ------------------------------------------------------------------------------------------------ clock checks
class Clock:
    """mhz.minion samples of one unit (its sampler, or sgemm's bracket bursts)."""

    def __init__(self, unit_dir=None, t=None, m=None):
        if unit_dir is None:      # a filtered copy (aifoundry1's cards: the idle samples set aside)
            self.t, self.m = t, m
            return
        s = []
        for name in ("telemetry.jsonl", "brackets.jsonl"):
            for r in jlines(os.path.join(unit_dir, name)):
                try:
                    s.append((int(r["t_ms"]), int(r["mhz"]["minion"])))
                except (KeyError, TypeError, ValueError):
                    pass
        s.sort()
        self.t = np.array([a for a, _ in s], dtype=np.int64)
        self.m = np.array([b for _, b in s], dtype=np.int64)

    def window(self, t0, t1, margin=200, reach=5000):
        """True/False: the samples within `margin` ms of [t0, t1] (else the nearest on each side, each within
        `reach` ms) all read 600 MHz; None: no sample to tell."""
        if t0 is None or not len(self.t):
            return None
        t1 = t0 if t1 is None else t1
        i0, i1 = np.searchsorted(self.t, t0 - margin, "left"), np.searchsorted(self.t, t1 + margin, "right")
        vals = list(self.m[i0:i1])
        if not vals:
            if i0 == 0 or i1 >= len(self.t):
                return None
            if t0 - self.t[i0 - 1] > reach or self.t[i1] - t1 > reach:
                return None
            vals = [self.m[i0 - 1], self.m[i1]]
        return all(v == 600 for v in vals)

    def brackets(self, t0, t1, reach=10000):
        """sgemm: every sample in the reach before t0 and after t1; at least one on each side; all 600."""
        if t0 is None or not len(self.t):
            return None
        pre = self.m[(self.t >= t0 - reach) & (self.t <= t0)]
        post = self.m[(self.t >= t1) & (self.t <= t1 + reach)]
        if not len(pre) or not len(post):
            return None
        return bool((pre == 600).all() and (post == 600).all())


def rec_ghz(r):
    if r.get("ghz") is not None:
        return float(r["ghz"])
    if r.get("cycles_max") and r.get("wall_s"):
        return r["cycles_max"] / r["wall_s"] / 1e9
    return None


def drop_rule(card):
    """pinned (aifoundry3: nothing dropped), registered (aifoundry2), idle-aware (every other governor-free card)."""
    return "pinned" if card in PINNED else "registered" if card in REGISTERED_RULE else "idle-aware"


class Unit:
    def __init__(self, card, path, idle=None, block=None):
        self.card, self.path = card, path
        self.rule = drop_rule(card)
        self.gov_free = self.rule != "pinned"
        self.idle = idle if idle is not None else set()   # the card's idle points; Card fills it before any keep()
        self.block = block if block is not None else []    # the units of the same block (sgemm's evidence)
        self.clock = Clock(path)
        self._ia = None
        self.basis = {}                                    # idle-aware: launch (t0, t1) -> how it was judged

    def f(self, name):
        return os.path.join(self.path, name)

    def keep(self, t0, t1=None, ghz=None, wall=None):
        """The drop rule for one launch: the registered rule on aifoundry2 (wall is not used), the amended rule on
        aifoundry1's cards (module docstring), nothing dropped on aifoundry3 (pinned)."""
        if self.rule == "pinned":
            return True
        if ghz is not None and ghz > 0.6:
            return False if self.rule == "registered" else self._judge(t0, t1, False, "dropped: implied clock > 0.6 GHz")
        if self.rule == "registered":
            return self.clock.window(t0, t1) is True
        return self._keep_idle_aware(t0, t1, ghz, wall)

    def keep_rec(self, r):
        return self.keep(r.get("t_start_ms"), r.get("t_end_ms"), rec_ghz(r), r.get("wall_s"))

    # ---- aifoundry1's cards
    def _judge(self, t0, t1, verdict, why):
        self.basis[(t0, t1)] = why
        return verdict

    def ia(self):
        """Idle-aware view of the unit: its samples with the idle samples set aside, and the unit's verdict."""
        if self._ia is not None:
            return self._ia
        c = self.clock
        recs = [r for p in glob.glob(self.f("*.jsonl")) if os.path.basename(p) not in NONHOST for r in jlines(p)]
        wins = sorted((int(r["t_start_ms"]), int(r.get("t_end_ms") or r["t_start_ms"])) for r in recs
                      if isinstance(r.get("t_start_ms"), (int, float)))
        merged = []
        for a, b in wins:
            if merged and a <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        inside = np.zeros(len(c.t), bool)
        if merged and len(c.t):
            st = np.array([a for a, _ in merged], dtype=np.int64)
            en = np.array([b for _, b in merged], dtype=np.int64)
            i = np.searchsorted(st, c.t, "right") - 1
            inside = (i >= 0) & (c.t <= en[np.maximum(i, 0)])
        idle = np.zeros(len(c.t), bool)
        if self.idle and len(c.t):
            idle = np.isin(c.m, sorted(self.idle)) & ~inside
        busy = Clock(t=c.t[~idle], m=c.m[~idle])
        implied = [g for g, w in ((rec_ghz(r), r.get("wall_s")) for r in recs)
                   if g is not None and w is not None and w >= IMPLIED_MIN_WALL_S]
        verdict = None
        if len(busy.t) or implied:
            verdict = bool((busy.m == 600).all()) and all(IMPLIED_MIN_GHZ <= g <= 0.6 for g in implied)
        self._ia = {"busy": busy, "verdict": verdict, "samples": int(len(c.t)), "idle_set_aside": int(idle.sum()),
                    "inside_kernels": int(inside.sum()), "implied_clocks": len(implied),
                    "inside_mhz": dict(collections.Counter(int(x) for x in c.m[inside])),
                    "kept_samples_off600": dict(collections.Counter(int(x) for x in busy.m if x != 600))}
        return self._ia

    def _keep_idle_aware(self, t0, t1, ghz, wall):
        ia = self.ia()
        measurable = ghz is not None and wall is not None and wall >= IMPLIED_MIN_WALL_S
        if measurable and ghz < IMPLIED_MIN_GHZ:
            return self._judge(t0, t1, False, "dropped: implied clock < 0.45 GHz")
        v = ia["busy"].window(t0, t1)
        if v is not None:
            return self._judge(t0, t1, v, "kept on samples" if v else "dropped on samples")
        if self.clock.window(t0, t1) is None:            # no sample at all, idle or not: dropped, as registered
            return self._judge(t0, t1, False, "dropped: no sample")
        if measurable:
            return self._judge(t0, t1, True, "kept on its implied clock (idle samples only)")
        v = ia["verdict"] is True
        return self._judge(t0, t1, v, "kept on the unit verdict (idle samples only)" if v else
                           "dropped: idle samples only, unit verdict not 600 MHz")

    def bracket_ok(self, t0, t1, reach=10000):
        """sgemm: the registered bracket rule on aifoundry2; on aifoundry1's cards bracket samples at the idle point
        are allowed (they show no lift) when every other unit of the block has the verdict "600 MHz"."""
        if self.rule == "pinned":
            return True
        if self.rule == "registered":
            return self.clock.brackets(t0, t1, reach) is True
        c = self.clock
        if t0 is None or not len(c.t):
            return self._judge(t0, t1, False, "dropped: no bracket")
        pre = c.m[(c.t >= t0 - reach) & (c.t <= t0)]
        post = c.m[(c.t >= t1) & (c.t <= t1 + reach)]
        if not len(pre) or not len(post):
            return self._judge(t0, t1, False, "dropped: no bracket on one side")
        vals = [int(x) for x in list(pre) + list(post)]
        if all(v == 600 for v in vals):
            return self._judge(t0, t1, True, "kept on brackets at 600 MHz")
        if any(v != 600 and v not in self.idle for v in vals):
            return self._judge(t0, t1, False, "dropped: bracket off 600 MHz and off the idle point")
        others = [u.ia()["verdict"] for u in self.block if u is not self]
        others = [v for v in others if v is not None]
        ok = bool(others) and all(others)
        return self._judge(t0, t1, ok, "kept: brackets at the idle point, the block's bursts at 600 MHz" if ok else
                           "dropped: brackets at the idle point, the block's bursts not shown at 600 MHz")


# ------------------------------------------------------------------------------------------------ data layout
def classify(arg):
    s = str(arg)
    if re.fullmatch(r"[1236789]", s):
        return "full", arg
    if re.fullmatch(r"[1236789][12]", s):
        return "half", int(s[0])
    if re.fullmatch(r"4|5|4[1-9]", s):
        return "div", arg
    return None, None


def block_status(path):
    """The "status" of a block.json. lib.sh's block_end writes "die_c_end":, (invalid JSON) when the die cannot be
    read at the end of a block, so fall back to a regex rather than lose (or crash on) a finished block."""
    if not os.path.exists(path):
        return None
    txt = open(path).read()
    try:
        return json.loads(txt).get("status")
    except ValueError:
        m = re.search(r'"status"\s*:\s*"(\w+)"', txt)
        return m.group(1) if m else None


class Card:
    def __init__(self, data, card):
        self.card = card
        self.present = os.path.isdir(os.path.join(data, card, "lat"))
        self.passes = {}      # K -> {unit: Unit}
        self.short = []       # (label, Unit) for the divergence subset: e4x of each pass, div blocks
        self.blocks, self.skipped = [], []
        # idle points (used on aifoundry1's cards only): readings below 600 MHz of the blocks' idle probes, and the
        # registered one; the set is shared with the units and complete before any launch is judged
        self.idle = {REGISTERED_IDLE[card]} if card in REGISTERED_IDLE else set()
        self.idle_probes = collections.Counter()
        root = os.path.join(data, card, "lat")
        dirs = []
        for d in glob.glob(os.path.join(root, "p*")):
            m = re.fullmatch(r"p(\d+)", os.path.basename(d))
            if m:
                dirs.append((int(m.group(1)), d))
        for arg, d in sorted(dirs):
            kind, K = classify(arg)
            st = block_status(os.path.join(d, "block.json"))
            if kind is None or st != "ok":
                self.skipped.append({"block": arg, "status": st, "kind": kind})
                continue
            done = []
            for m in jlines(os.path.join(d, "marks.jsonl")):
                if m.get("ev") == "end" and m.get("unit") and os.path.isdir(os.path.join(d, m["unit"])):
                    done.append(m["unit"])
            self.blocks.append({"block": arg, "kind": kind, "pass": K, "units": done})
            for r in jlines(os.path.join(d, "idle.jsonl")):
                m = r.get("mhz")
                if isinstance(m, (int, float)):
                    self.idle_probes[int(m)] += 1
                    if m < 600:
                        self.idle.add(int(m))
            block_units = []
            for u in done:
                U = Unit(card, os.path.join(d, u), self.idle, block_units)
                block_units.append(U)
                if kind == "div":
                    if u == "div":
                        self.short.append((f"block {arg}", U))
                    continue
                self.passes.setdefault(K, {}).setdefault(u, U)
        for K in sorted(self.passes):
            if "e4x" in self.passes[K]:
                self.short.append((f"pass {K}", self.passes[K]["e4x"]))

    def units(self, name):
        return [(K, us[name]) for K, us in sorted(self.passes.items()) if name in us]

    def all_units(self):
        seen = {}
        for us in self.passes.values():
            for U in us.values():
                seen[U.path] = U
        for _, U in self.short:
            seen[U.path] = U
        return [seen[p] for p in sorted(seen)]

    def summary(self):
        """How the drop rule judged this card's launches (aifoundry1's cards), and its idle clock."""
        out = {"rule": drop_rule(self.card), "data": self.present,
               "idle_probes_mhz": {str(k): v for k, v in sorted(self.idle_probes.items())},
               "idle_points_mhz": sorted(self.idle) if drop_rule(self.card) == "idle-aware" else []}
        if drop_rule(self.card) != "idle-aware":
            return out
        basis, inside, kept_off = collections.Counter(), collections.Counter(), collections.Counter()
        verdicts = collections.Counter()
        for U in self.all_units():
            basis.update(U.basis.values())
            if U.clock.t.size:
                ia = U.ia()
                inside.update(ia["inside_mhz"])
                kept_off.update(ia["kept_samples_off600"])
                verdicts[str(ia["verdict"])] += 1
        out.update({"launches_by_basis": dict(sorted(basis.items())),
                    "samples_inside_kernels_mhz": {str(k): v for k, v in sorted(inside.items())},
                    "non_idle_samples_off600_mhz": {str(k): v for k, v in sorted(kept_off.items())},
                    "unit_verdicts": dict(verdicts)})
        return out


# ------------------------------------------------------------------------------------------------ per-card driver
def per_card_result(passes, need=NEED):
    """passes: list of per-pass dicts with 'kept' (bool) and 'holds' (bool). Returns counts; holds decided later."""
    kept = [p for p in passes if p.get("kept")]
    return kept, {"n": len(kept), "n_dropped": len(passes) - len(kept),
                  "failing_passes": [p["pass"] for p in kept if p.get("holds") is False]}


def every_pass(passes, need=NEED, decisive=False):
    """Deterministic items: holds iff every kept pass holds, with >= need kept passes. decisive=True (registered as
    "any deviation falsifies"): one failing kept pass makes the card fail whatever the count."""
    kept, out = per_card_result(passes)
    if decisive and any(p["holds"] is False for p in kept):
        out["holds"], out["decisive_fail"] = False, True
    else:
        out["holds"] = None if len(kept) < need else all(p["holds"] for p in kept)
    return kept, out


# ------------------------------------------------------------------------------------------------ memhier
def memhier_rows(U, names):
    rows = {}
    for n in names:
        rows[n] = jlines(U.f(f"{n}.jsonl"))
    return rows


def chase_kept(U, r):
    if not U.gov_free:
        return True
    if MEM.point_ghz(r) >= 0.65:
        return False
    return U.keep(r.get("t_start_ms"), r.get("t_end_ms"))


MC_FILES = ["chase-dram", "chase-dram-sweep-from24", "chase-dram-thread1", "chase-dram-from7", "chase-dram-from24",
            "chase-dram-from31", "chase-dram-from0-repeat", "chase-dram-placement", "chase-dram-offsets"]
MS_FILES = ["chase-scp-local", "chase-scp-map", "chase-scp-map-from7", "chase-scp-map-from24", "chase-scp-map-from31"]


def lat_m1(C):
    passes = []
    for K, us in sorted(C.passes.items()):
        if "mc" not in us or "ms" not in us:
            continue
        mc, ms = us["mc"], us["ms"]
        R = memhier_rows(mc, MC_FILES)
        R.update(memhier_rows(ms, MS_FILES))
        used, bad, vals = [], [], {"L1": [], "RB": [], "L2": [], "hart1": {}}
        present = True
        for name, U in (("chase-dram", mc), ("chase-dram-sweep-from24", mc), ("chase-scp-local", ms)):
            rs = R[name]
            if not rs:
                present = False
            for r in rs:
                s, c = r["size"], r["cycles_per_load"]
                lim = 2 << 20 if name == "chase-scp-local" else 512 << 10
                if s <= 512:
                    used.append((U, r)); vals["L1"].append(c); ok = abs(c - 5.25) <= 0.01
                elif 768 <= s <= 2048:
                    used.append((U, r)); vals["RB"].append(c); ok = abs(c - 36.00) <= 0.05
                elif 4096 <= s <= lim:
                    used.append((U, r)); vals["L2"].append(c); ok = abs(c - 47.00) <= 0.05
                else:
                    continue
                if not ok:
                    bad.append(f"{name}@{s}={c}")
            sizes = {r["size"] for r in rs}
            if not {512, 768, 2048, 4096} <= sizes:
                present = False
        t1 = R["chase-dram-thread1"]
        if not t1:
            present = False
        for r in t1:
            s, c = r["size"], r["cycles_per_load"]
            used.append((mc, r)); vals["hart1"][s] = c
            want = (5.25, 0.01) if s <= 512 else (39.0, 0.05) if s <= 2048 else (50.0, 0.05)
            if abs(c - want[0]) > want[1]:
                bad.append(f"hart1@{s}={c}")
        all_ok = all(r.get("ok") for rs in R.values() for r in rs)
        kept = present and all(chase_kept(U, r) for U, r in used)
        passes.append({"pass": K, "kept": kept, "holds": present and not bad and all_ok,
                       "L1": [min(vals["L1"]), max(vals["L1"])] if vals["L1"] else None,
                       "RB": [min(vals["RB"]), max(vals["RB"])] if vals["RB"] else None,
                       "L2": [min(vals["L2"]), max(vals["L2"])] if vals["L2"] else None,
                       "hart1": vals["hart1"], "pointer_checks_ok": all_ok, "misses": bad[:8]})
    kept, out = every_pass(passes)
    out["passes"] = passes
    return out


L3_BAND = {0: (168.0, 170.0), 7: (159.7, 161.7), 24: (158.3, 160.3), 31: (167.9, 169.9)}
DRAM_BAND = {0: (291, 301), 31: (291, 301), 7: (283, 293), 24: (283, 293)}


def lat_m2(C):
    passes = []
    for K, mc in C.units("mc"):
        L3, DR, ndrop = {s: [] for s in L3_BAND}, {s: [] for s in L3_BAND}, 0
        for n in MC_FILES:
            for r in jlines(mc.f(f"{n}.jsonl")):
                if r.get("where") != "dram" or r.get("thread") != 0 or r.get("chaser_shire") not in L3_BAND:
                    continue
                if r["size"] not in (4 << 20, 256 << 20):
                    continue
                if not chase_kept(mc, r):
                    ndrop += 1
                    continue
                (L3 if r["size"] == 4 << 20 else DR)[r["chaser_shire"]].append(r["cycles_per_load"])
        valid = all(L3[s] and DR[s] for s in L3_BAND)
        l3 = {s: statistics.median(v) for s, v in L3.items() if v}
        dr = {s: statistics.median(v) for s, v in DR.items() if v}
        tol = valid and all(inb(l3[s], *L3_BAND[s]) for s in L3_BAND) and all(inb(dr[s], *DRAM_BAND[s]) for s in L3_BAND)
        passes.append({"pass": K, "kept": valid, "holds": tol, "L3": l3, "DRAM": dr,
                       "req_effect": l3[0] - l3[24] if valid else None, "chases_dropped": ndrop})
    kept, out = every_pass(passes)
    ce = ci99([p["req_effect"] for p in kept])
    out["requester_effect_ci99"] = ce
    ce_ok = ce.get("lo") is not None and (ce["lo"] > 0 or ce["hi"] < 0) and ce["lo"] <= 11.2 and ce["hi"] >= 8.2
    out["requester_effect_ok"] = ce_ok if ce.get("lo") is not None else None
    if out["holds"] is not None:
        out["tolerances_every_pass"] = out["holds"]
        out["holds"] = out["holds"] and bool(ce_ok)
    out["passes"] = passes
    return out


def lat_m3(C):
    passes = []
    rows_of = {0: "chase-scp-map", 7: "chase-scp-map-from7", 24: "chase-scp-map-from24", 31: "chase-scp-map-from31"}
    for K, ms in C.units("ms"):
        rows, kept, present = {}, True, True
        for src, n in rows_of.items():
            rs = jlines(ms.f(f"{n}.jsonl"))
            row = {r["scp_shire"]: r for r in rs}
            if len([t for t in row if t != src]) < 31:
                present = False
            kept &= all(chase_kept(ms, r) for t, r in row.items() if t != src)
            rows[src] = {t: r["cycles_per_load"] for t, r in row.items()}
        if not present:
            passes.append({"pass": K, "kept": False, "holds": False, "note": "rows incomplete"})
            continue
        res = [c - (99.84 + 12.00 * NOC.hops(s, t)) for s, row in rows.items() for t, c in row.items() if t != s]
        frac = sum(abs(x) <= 1.0 for x in res) / len(res)
        pairs = {f"{a}-{b}": rows[a][b] - rows[b][a] for a in rows for b in rows if a < b}
        xs = [NOC.hops(0, t) for t in rows[0] if t != 0]
        _, slope, _ = fit(xs, [rows[0][t] for t in rows[0] if t != 0])
        holds = frac >= 0.95 and all(abs(v) <= 0.5 for v in pairs.values()) and abs(slope - 12.00) <= 0.05
        passes.append({"pass": K, "kept": kept, "holds": holds, "frac_within_1": frac,
                       "worst_resid": max(abs(x) for x in res), "a_to_b_minus_b_to_a": pairs, "row0_slope": slope})
    kept, out = every_pass(passes)
    out["passes"] = passes
    return out


# ------------------------------------------------------------------------------------------------ nocbench
class NocPass:
    def __init__(self, U):
        self.U = U
        self.files = {os.path.basename(p)[:-6]: jlines(p) for p in glob.glob(U.f("*.jsonl"))
                      if os.path.basename(p) not in NONHOST}

    def kept_file(self, name):
        """All launch-level records of the file kept (pair lines inherit their launch line)."""
        rs = self.files.get(name) or []
        tops = [r for r in rs if r.get("kind") in ("launch", "allreduce", "barrier")]
        if not tops:
            return False
        return all(self.U.keep_rec(r) for r in tops)

    def pairs(self, name):
        return list(NOC.pairs_with_launch(self.files.get(name) or []))

    def matrix(self, name):
        return {(min(p["a_shire"], p["b_shire"]), max(p["a_shire"], p["b_shire"])): p["cycles_per_iter"]
                for p in self.pairs(name)}


TREE = {(0, 1), (0, 2), (0, 4), (2, 3), (4, 5), (4, 6), (6, 7)}
TREE_PAIRS = sorted((a + 8 * n, b + 8 * n) for n in range(4) for a, b in TREE)


def noc_item(C, need_files, fn):
    passes = []
    for K, U in C.units("noc"):
        P = NocPass(U)
        present = all(P.files.get(n) for n in need_files)
        if not present:
            passes.append({"pass": K, "kept": False, "holds": False, "note": "files missing"})
            continue
        kept = all(P.kept_file(n) for n in need_files)
        d = fn(P)
        d.update({"pass": K, "kept": kept})
        passes.append(d)
    kept, out = every_pass(passes)
    out["passes"] = passes
    return out, kept


def lat_n1(C):
    def fn(P):
        d, ok = {}, True
        for name in ("intra-pingpong", "intra-pingpong-s24"):
            ps = P.pairs(name)
            fast = sorted((p["a_minion"], p["b_minion"]) for p in ps if p["cycles_per_iter"] < 90)
            fv = [p["cycles_per_iter"] for p in ps if p["cycles_per_iter"] < 90]
            sv = [p["cycles_per_iter"] for p in ps if p["cycles_per_iter"] >= 90]
            same = fast == TREE_PAIRS
            ok &= same and len(sv) == 468 and all(67 <= v <= 69 for v in fv) and all(113.5 <= v <= 115 for v in sv)
            d[name] = {"fast_is_tree": same, "n_fast": len(fv), "n_other": len(sv),
                       "fast": [min(fv), max(fv)] if fv else None, "other": [min(sv), max(sv)] if sv else None}
        b = {n: [r["cycles_per_iter_mean"] for r in P.files[n] if r.get("kind") == "barrier"]
             for n in ("barrier-shire1", "barrier-shire32")}
        a32 = [r["cycles_per_iter"] for r in P.files["allreduce-c1"]
               if r.get("kind") == "allreduce" and r["minions"] == 32 and r.get("trees", 1) == 1]
        ok &= all(v and all(236 <= x <= 238 for x in v) for v in b.values()) and bool(a32) and all(430 <= x <= 434 for x in a32)
        d.update({"shire_barrier": b, "allreduce32": a32, "holds": bool(ok)})
        return d
    out, _ = noc_item(C, ["intra-pingpong", "intra-pingpong-s24", "barrier-shire1", "barrier-shire32", "allreduce-c1"], fn)
    return out


def lat_n2(C, search=True):
    def fn(P):
        d = {}
        m0 = P.matrix("matrix-pingpong")
        a, b, worst = fit([NOC.hops(i, j) for i, j in m0], list(m0.values()))
        d["pingpong_fit"] = {"a": a, "b": b, "worst": worst, "n_pairs": len(m0)}
        ok = len(m0) == 496 and inb(a, 149.0, 151.0) and inb(b, 11.97, 12.07) and worst <= 2.0
        m31 = P.matrix("matrix-pingpong-m31")
        diffs = [m31[k] - m0[k] for k in m0 if k in m31]
        d["m31_minus_m0_absmax"] = max(abs(x) for x in diffs) if diffs else None
        ok &= len(diffs) == 496 and d["m31_minus_m0_absmax"] <= 1.5
        c32 = P.matrix("matrix-pingpong-c32")
        near = [(NOC.hops(i, j), v) for (i, j), v in c32.items() if NOC.hops(i, j) <= 5]
        far = [(NOC.hops(i, j), v) for (i, j), v in c32.items() if NOC.hops(i, j) > 5]
        bn = fit(*zip(*near))[1] if near else None
        bf = fit(*zip(*far))[1] if far else None
        d["c32_slope_to5"], d["c32_slope_beyond5"] = bn, bf
        ok &= inb(bn, 11.9, 12.1) and inb(bf, 35.0, 37.0)
        fc = P.matrix("matrix-fcc")
        fa, fb, _ = fit([NOC.hops(i, j) for i, j in fc], list(fc.values()))
        d["credit_fit"] = {"a": fa, "b": fb}
        ok &= inb(fa, 145.0, 151.0) and inb(fb, 12.0, 12.4)
        blk = [p["cycles_per_iter"] for p in P.pairs("fcc-inshire-block")]
        d["blocking_credit_in_shire"] = [min(blk), max(blk)] if blk else None
        ok &= bool(blk) and all(119 <= v <= 121 for v in blk)
        if search:
            shires = sorted({s for p in m0 for s in p})
            _, _, runs = NOC.search_layout(shires, m0)
            same = sum(1 for r in runs if r[1])
            d["search_same_as_marty"] = f"{same}/{len(runs)}"
            d["holds"] = bool(ok) and same == 12 and len(runs) == 12
        else:
            d["search_same_as_marty"] = "not run (--no-search)"
            d["holds"] = None if ok else False
        return d
    passes = []
    for K, U in C.units("noc"):
        P = NocPass(U)
        need = ["matrix-pingpong", "matrix-pingpong-m31", "matrix-pingpong-c32", "matrix-fcc", "fcc-inshire-block"]
        if not all(P.files.get(n) for n in need):
            passes.append({"pass": K, "kept": False, "holds": False, "note": "files missing"})
            continue
        d = fn(P)
        d.update({"pass": K, "kept": all(P.kept_file(n) for n in need)})
        passes.append(d)
    kept, out = per_card_result(passes)
    hs = [p["holds"] for p in kept]
    out["holds"] = None if len(kept) < NEED else False if False in hs else None if None in hs else True
    out["passes"] = passes
    return out


def flag_bootstrap(mats, draws=10000, seed=1):
    """Shire-block bootstrap of the OLS slope of cycles on MARTY hops, over every pass's 496 pairs."""
    I, J, X, Y = [], [], [], []
    for m in mats:
        for (i, j), v in m.items():
            I.append(i); J.append(j); X.append(NOC.hops(i, j)); Y.append(v)
    I, J, X, Y = map(np.asarray, (I, J, X, Y))
    X, Y = X.astype(float), Y.astype(float)
    rng = np.random.default_rng(seed)
    out = []
    for start in range(0, draws, 500):
        k = min(500, draws - start)
        cnt = np.zeros((k, 32))
        pick = rng.integers(0, 32, size=(k, 32))
        for r in range(k):
            cnt[r] = np.bincount(pick[r], minlength=32)
        W = cnt[:, I] * cnt[:, J]
        sw = W.sum(1)
        ok = sw > 0
        mx = (W * X).sum(1) / np.where(ok, sw, 1)
        my = (W * Y).sum(1) / np.where(ok, sw, 1)
        sxx = (W * (X - mx[:, None]) ** 2).sum(1)
        sxy = (W * (X - mx[:, None]) * (Y - my[:, None])).sum(1)
        good = ok & (sxx > 0)
        out.extend((sxy[good] / sxx[good]).tolist())
    return np.asarray(out)


def lat_n3(C):
    passes, mats = [], []
    for K, U in C.units("noc"):
        P = NocPass(U)
        if not P.files.get("matrix-flag"):
            continue
        m = P.matrix("matrix-flag")
        kept = P.kept_file("matrix-flag") and len(m) == 496
        med = statistics.median(m.values())
        _, slope, _ = fit([NOC.hops(i, j) for i, j in m], list(m.values()))
        passes.append({"pass": K, "kept": kept, "median": med, "slope": slope,
                       "holds": inb(med, 475, 595) and slope < 6})
        if kept:
            mats.append(m)
    kept, out = per_card_result(passes)
    out["passes"] = passes
    if len(kept) < NEED:
        out["holds"] = None
        return out
    bs = flag_bootstrap(mats)
    lo, hi = float(np.percentile(bs, 0.5)), float(np.percentile(bs, 99.5))
    _, pooled, _ = fit([NOC.hops(i, j) for m in mats for (i, j) in m], [v for m in mats for v in m.values()])
    out.update({"pooled_slope": pooled, "bootstrap99": [lo, hi], "draws": int(len(bs)),
                "medians_in_band": all(inb(p["median"], 475, 595) for p in kept),
                "every_pass_slope_below_6": all(p["slope"] < 6 for p in kept)})
    if hi < 6 and out["every_pass_slope_below_6"]:
        out["decision"] = "kept as 'less than half of TensorSend's 12 cycles/hop'"
    elif hi >= 12.02:
        out["decision"] = "dropped"
    else:
        out["decision"] = "neither kept nor dropped (bound between +6 and +12.02)"
    out["holds"] = out["decision"].startswith("kept") and out["medians_in_band"]
    if out["decision"] == "dropped":   # registered: "dropped if the bound is >= +12.02 on either card"
        out["decisive_fail"] = True
    return out


STREAM_REF = {"0.0-0.1": (40, 2.33), "0.0-0.7": (86, 4.00), "0.0-8.0": (135, 3.00), "0.0-31.0": (224, 4.64)}


def lat_n4(C):
    def fn(P):
        d, ok = {"stream": {}}, True
        per = {}
        for p in P.pairs("counts-stream"):
            per.setdefault(f"{p['a_shire']}.{p['a_minion']}-{p['b_shire']}.{p['b_minion']}", []).append(
                (p["count"], p["cycles_per_iter"]))
        for key, (ra, rb) in STREAM_REF.items():
            pts = per.get(key)
            if not pts or len(pts) < 3:
                ok = False
                continue
            a, b, _ = fit(*zip(*pts))
            d["stream"][key] = {"a": a, "b": b}
            ok &= abs(a - ra) <= 3 and abs(b - rb) <= 0.1
        cp = {(p["a_shire"], p["a_minion"], p["b_shire"], p["b_minion"], p["count"]): p["cycles_per_iter"]
              for p in P.pairs("counts-pingpong")}
        diffs = []
        for f in ("iadd", "imax", "fadd", "fmax"):
            for p in P.pairs(f"functs-{f}"):
                k = (p["a_shire"], p["a_minion"], p["b_shire"], p["b_minion"], p["count"])
                if k in cp:
                    diffs.append(p["cycles_per_iter"] - cp[k])
        d["combine_minus_move"] = [min(diffs), max(diffs)] if diffs else None
        ok &= len(diffs) == 16 and all(abs(x) <= 0.5 for x in diffs)
        x1024 = [r["cycles_per_iter"] for r in P.files["xallreduce-c1"] if r.get("kind") == "allreduce" and r["minions"] == 1024]
        d["allreduce_1024"] = x1024
        ok &= bool(x1024) and all(1358 <= v <= 1378 for v in x1024)
        worst = 0.0
        for c in ("c1", "c8", "c32"):
            al = {r["minions"]: r["cycles_per_iter"] for r in P.files[f"allreduce-{c}"] if r.get("kind") == "allreduce"}
            aa = {r["minions"]: r["cycles_per_iter"] for r in P.files[f"allreduce-all-{c}"] if r.get("kind") == "allreduce"}
            if not al or set(al) != set(aa):
                ok = False
                continue
            worst = max(worst, max(abs(aa[k] - al[k]) for k in al))
        d["all32_minus_alone_absmax"] = worst
        ok &= worst <= 1.0
        bc = {n: [r["cycles_per_iter_mean"] for r in P.files[n] if r.get("kind") == "barrier"] for n in ("barrier-chip1", "barrier-chip32")}
        d["chip_barrier"] = bc
        ok &= bool(bc["barrier-chip1"]) and all(4970 <= v <= 5020 for v in bc["barrier-chip1"])
        ok &= bool(bc["barrier-chip32"]) and all(4993 <= v <= 5043 for v in bc["barrier-chip32"])
        nbad = sum(1 for rs in P.files.values() for r in rs if r.get("ok") is False)
        d["ok_false_lines"] = nbad
        ok &= nbad == 0
        d["holds"] = bool(ok)
        return d
    need = ["counts-stream", "counts-pingpong", "functs-iadd", "functs-imax", "functs-fadd", "functs-fmax",
            "xallreduce-c1", "allreduce-c1", "allreduce-all-c1", "allreduce-c8", "allreduce-all-c8", "allreduce-c32",
            "allreduce-all-c32", "barrier-chip1", "barrier-chip32"]
    out, _ = noc_item(C, need, fn)
    return out


# ------------------------------------------------------------------------------------------------ sparsity
def sp_lines(U, name):
    return jlines(U.f(f"{name}.jsonl"))


def sp_kept(U, rs):
    return bool(rs) and all(U.keep_rec(r) for r in rs)


def lat_s1(C):
    groups = {"546.0": (["fma-fp32-elem", "fma-fp32-col", "fma-fp32-row", "fma-fp16-elem", "fma-fp16-pair",
                         "fma-fp32-bsparse", "fma-fp32-bsparse90", "fma-fp32-rowmask-0xFFFF"], 546.0),
              "318.0": (["fma-int8-elem"], 318.0), "529.1": (["fma-fp32-elem-tenb"], 529.1),
              "544.0": ([f"fma-fp32-rowmask-{m}" for m in ("0x00FF", "0x000F", "0x0001", "0x0000")], 544.0),
              "546.1": (["fma-fp32-elem-all"], 546.1)}
    passes = []
    for K, U in C.units("sp"):
        d, ok, kept, present = {}, True, True, True
        for lab, (names, want) in groups.items():
            vals = []
            for n in names:
                rs = sp_lines(U, n)
                present &= bool(rs)
                kept &= sp_kept(U, rs)
                vals += [r["cycles_per_op"] for r in rs]
            d[lab] = [min(vals), max(vals)] if vals else None
            ok &= bool(vals) and all(abs(v - want) <= 0.1 for v in vals)
        pair = {round(r["sparsity"], 3): r["result"] for r in sp_lines(U, "fma-fp16-pair")}
        d["fp16_pair_result"] = pair
        ok &= pair.get(0.5) == "math" and pair.get(1.0) == "math"
        allrs = [r for p in glob.glob(U.f("*.jsonl")) if os.path.basename(p) not in NONHOST for r in jlines(p)]
        d["ok_false_lines"] = sum(1 for r in allrs if "test" in r and r.get("ok") is not True)
        ok &= d["ok_false_lines"] == 0
        passes.append({"pass": K, "kept": kept and present, "holds": ok and present, **d})
    kept, out = every_pass(passes, decisive=True)
    out["passes"] = passes
    return out


def tl(U, name, lines=None, iters=None):
    for r in sp_lines(U, name):
        if (lines is None or r["lines"] == lines) and (iters is None or r["iters"] == iters):
            return r
    return None


def pass_values(C, unit_names, fn):
    """fn(units) -> (values dict, list of records used) or None; returns list of per-pass dicts (kept flag)."""
    passes = []
    for K, us in sorted(C.passes.items()):
        if not all(u in us for u in unit_names):
            continue
        got = fn(*[us[u] for u in unit_names])
        if got is None:
            continue
        vals, used = got
        kept = all(r is not None for _, r in used) and all(
            U.keep_rec(r) for U, r in used)
        passes.append({"pass": K, "kept": kept, **vals})
    return passes


def means(passes, keys):
    kept = [p for p in passes if p["kept"]]
    return {k: ci99([p.get(k) for p in kept]) for k in keys}, len(kept)


def lat_s2(C):
    def fn(U):
        used, v = [], {}
        for w in ("l2", "scp", "dram"):
            for L in (16, 8, 4):
                r = tl(U, f"tload-{w}-one", L)
                used.append((U, r))
                v[f"{w}{L}"] = r["cycles_per_load"] if r else None
        return v, used
    passes = pass_values(C, ["sp"], fn)
    keys = [f"{w}{L}" for w in ("l2", "scp", "dram") for L in (16, 8, 4)]
    M, n = means(passes, keys)
    bands = {"l216": pm(160, 2), "l28": pm(81, 2), "l24": (43, 49), "scp16": pm(160, 2), "scp8": pm(81, 2),
             "scp4": (43, 49), "dram16": (730 * 0.95, 730 * 1.05), "dram8": (320 * 0.95, 320 * 1.05),
             "dram4": (144 * 0.95, 144 * 1.05)}
    res = {k: inb(M[k].get("mean"), *bands[k]) for k in keys}
    return {"n": n, "holds": None if n < NEED else all(res.values()), "pass_means": M, "in_band": res,
            "bands": bands, "passes": passes}


def lat_s3(C):
    def fn(sp, ex):
        used, v = [], {}
        for L in (16, 8, 4, 1):
            r = tl(sp, "tload-dram-all", L, 2000)
            used.append((sp, r)); v[f"dram_all{L}"] = r["cycles_per_load"] if r else None
        for n in (2000, 20000, 200000):
            r = tl(ex, f"tload-l2-all-n{n}", 16)
            used.append((ex, r)); v[f"l2_n{n}"] = r["cycles_per_load"] if r else None
        for n in (2000, 20000):
            r = tl(ex, f"tload-dram-all-n{n}", 16)
            used.append((ex, r)); v[f"dram_n{n}"] = r["cycles_per_load"] if r else None
        v["l2_diff_2k_20k"] = (v["l2_n2000"] - v["l2_n20000"]) if v["l2_n2000"] and v["l2_n20000"] else None
        return v, used
    passes = pass_values(C, ["sp", "e4x"], fn)
    keys = ["dram_all16", "dram_all8", "dram_all4", "dram_all1", "l2_n2000", "l2_n20000", "l2_n200000", "dram_n2000",
            "dram_n20000", "l2_diff_2k_20k"]
    M, n = means(passes, keys)
    res = {}
    if n:
        m = lambda k: M[k].get("mean")
        res["dram_all16"] = inb(m("dram_all16"), 8300 * 0.95, 8300 * 1.05)
        for L in (8, 4, 1):
            res[f"dram_all{L}_within20pct"] = m(f"dram_all{L}") is not None and m("dram_all16") is not None and \
                abs(m(f"dram_all{L}") / m("dram_all16") - 1) <= 0.20
        res["l2_n2000"] = inb(m("l2_n2000"), 277, 301)
        res["l2_n20000"] = inb(m("l2_n20000"), 257.8, 260.8)
        res["l2_n200000"] = inb(m("l2_n200000"), 256.0, 256.6)
        res["dram_n2000"] = inb(m("dram_n2000"), 8300 * 0.97, 8300 * 1.03)
        res["dram_n20000"] = inb(m("dram_n20000"), 8300 * 0.97, 8300 * 1.03)
        dci = M["l2_diff_2k_20k"]
        res["l2_diff_excludes_0"] = dci.get("lo") is not None and (dci["lo"] > 0 or dci["hi"] < 0)
    out = {"n": n, "holds": None if n < NEED else all(res.values()), "pass_means": M, "checks": res,
           "passes": passes}
    # registered: the difference must exclude 0 "on both cards" for the page's attribution: one card is enough to fail
    if n >= NEED and not res["l2_diff_excludes_0"]:
        out["decisive_fail"] = True
    return out


def gemv_at(U, name, s):
    for r in sp_lines(U, name):
        if abs(r["sparsity"] - s) < 1e-6:
            return r
    return None


def lat_s4(C):
    def fn(sp, ex):
        used, v = [], {}
        for key, U, name, s in (("masked0", sp, "gemv-tree-masked", 0.0), ("plain0", sp, "gemv-tree-dense", 0.0),
                                ("skip99", sp, "gemv-tree-skip", 0.99), ("seed2_99", ex, "gemv-tree-skip-seed2", 0.99),
                                ("seed3_99", ex, "gemv-tree-skip-seed3", 0.99)):
            r = gemv_at(U, name, s)
            used.append((U, r))
            v[key] = r["cycles_per_layer_mean"] / 600.0 if r else None   # us at 600 MHz
        return v, used
    passes = pass_values(C, ["sp", "e4x"], fn)
    keys = ["masked0", "plain0", "skip99", "seed2_99", "seed3_99"]
    M, n = means(passes, keys)
    bands = {"masked0": pm(7.54, 0.1), "plain0": pm(7.31, 0.1), "skip99": pm(2.14, 0.1), "seed2_99": (1.9, 2.5),
             "seed3_99": (1.9, 2.5)}
    res = {k: inb(M[k].get("mean"), *bands[k]) for k in keys}
    return {"n": n, "holds": None if n < NEED else all(res.values()), "pass_means_us": M, "in_band": res,
            "passes": passes}


def tfma(r):
    return 8 * r["useful_lane_iters"] / r["cycles_mean"] * 600 / 1e6


def lat_s5(C):
    ref = REF["diverge_18sep"]
    passes = []
    for K, U in C.units("sp"):
        rows, used, present = {}, [], True
        for a in ("0", "3", "2", "1.5", "1.2"):
            for v in ("static", "refill", "scalar"):
                rs = sp_lines(U, f"diverge-{v}-a{a}")
                if not rs:
                    present = False
                    continue
                rows[f"{v}|{float(a):g}"] = rs[0]
                used.append(rs[0])
        if not present:
            passes.append({"pass": K, "kept": False, "holds": False, "note": "diverge group incomplete"})
            continue
        lane_same = all(round(rows[k]["lane_efficiency"], 4) == round(ref[k]["lane_efficiency"], 4) for k in ref)
        thr = {k: tfma(r) / ref[k]["tfma_600"] - 1 for k, r in rows.items()}
        s_minus_r3 = tfma(rows["static|3"]) - tfma(rows["refill|3"])
        kept = all(U.keep_rec(r) for r in used)
        passes.append({"pass": K, "kept": kept, "lane_eff_identical": lane_same,
                       "throughput_rel_worst": max(thr.values(), key=abs), "static_minus_refill_a3": s_minus_r3,
                       "holds": lane_same and all(abs(x) <= 0.03 for x in thr.values()) and s_minus_r3 > 0.1})
    kept, out = every_pass(passes)
    out["passes"] = passes
    shorts = []
    for label, U in C.short:
        st = [r for r in sp_lines(U, "div-static-a2")]
        rf = [r for r in sp_lines(U, "div-refill-a2")]
        if not st or not rf:
            continue
        k = all(U.keep_rec(r) for r in st[:1] + rf[:1])
        shorts.append({"block": label, "kept": k, "refill_minus_static_a2": tfma(rf[0]) - tfma(st[0])})
    ks = [s for s in shorts if s["kept"]]
    dci = ci99([s["refill_minus_static_a2"] for s in ks])
    out["short_blocks"] = shorts
    out["n_short"] = len(ks)
    out["refill_minus_static_a2_ci99"] = dci
    if len(ks) < NEED_SHORT:
        out["crossover"] = None
        out["holds"] = None
        return out
    out["crossover"] = "from alpha = 2" if dci["lo"] > 0 else "between alpha = 3 and 2"
    if dci["lo"] <= 0:   # registered: must exclude 0 positive "on both cards" to keep "from alpha = 2"
        out["decisive_fail"] = True
    out["mean_in_0.017pm0.02"] = inb(dci["mean"], -0.003, 0.037)
    if out["holds"] is not None:
        out["every_pass_parts"] = out["holds"]
        out["holds"] = out["holds"] and dci["lo"] > 0 and out["mean_in_0.017pm0.02"]
    return out


# ------------------------------------------------------------------------------------------------ sgemm
SG_REF = {1: ("-n 64 --shires 0x1", 0.31), 2: ("-n 512 --shires 0x1", 68.0), 3: ("-n 512", 2.37), 4: ("-n 1024", 16.8)}


def parse_sgemm(path):
    if not os.path.exists(path):
        return None
    txt = open(path).read()
    ms = [float(x) for x in re.findall(r"^launch \d+: ([0-9.eE+-]+) ms", txt, re.M)]
    mm = re.search(r"mismatches (\d+)/(\d+)", txt)
    held = re.search(r"device held for ([0-9.eE+-]+) s total", txt)
    rss = re.search(r"Maximum resident set size \(kbytes\): (\d+)", txt)
    el = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): ([0-9:.]+)", txt)
    wall = None
    if el:
        parts = [float(x) for x in el.group(1).split(":")]
        wall = sum(p * 60 ** i for i, p in enumerate(reversed(parts)))
    return {"launch_ms": ms, "mean_ms": statistics.mean(ms) if ms else None,
            "mismatches": int(mm.group(1)) if mm else None, "outputs": int(mm.group(2)) if mm else None,
            "held_s": float(held.group(1)) if held else None, "rss_gb": int(rss.group(1)) / 1024 / 1024 if rss else None,
            "elapsed_s": wall, "pass": bool(re.search(r"^PASS$", txt, re.M))}


def lat_g(C):
    passes = []
    for K, U in C.units("sg"):
        L = {r["name"]: r for r in jlines(U.f("launches.jsonl"))}
        d = {"pass": K, "configs": {}}
        for i in SG_REF:
            s = parse_sgemm(U.f(f"sgemm-{i}.log"))
            lr = L.get(f"sgemm-{i}")
            # A process that timed out or stopped on a kernel error prints no "mismatches" line: it is not a
            # mismatch, it is a missing repeat (not kept), listed under "incomplete".
            complete = s is not None and s["mismatches"] is not None and bool(s["launch_ms"])
            clock_ok = lr is not None and U.bracket_ok(lr["t0_ms"], lr["t1_ms"])
            d["configs"][i] = {**(s or {}), "complete": complete, "kept": complete and clock_ok}
        passes.append(d)
    out = {"passes": passes}
    per, holds, n_min = {}, True, 99
    for i, (args, v) in SG_REF.items():
        ks = [p["configs"][i] for p in passes if p["configs"][i]["kept"]]
        c = ci99([k["mean_ms"] for k in ks])
        n_min = min(n_min, len(ks))
        ok = c.get("lo") is not None and c["lo"] >= 0.95 * v and c["hi"] <= 1.05 * v
        per[args] = {"page_ms": v, "ci99_ms": c, "within_5pct": ok}
        holds &= ok
    out["incomplete"] = [f"pass {p['pass']} sgemm-{i}" for p in passes for i in SG_REF if not p["configs"][i]["complete"]]
    kept_cfg = [p["configs"][i] for p in passes for i in SG_REF if p["configs"][i]["kept"]]
    out["mismatches_total"] = sum(k["mismatches"] for k in kept_cfg) if kept_cfg else None
    out["mismatches_in_dropped_runs"] = sum(p["configs"][i]["mismatches"] for p in passes for i in SG_REF
                                            if p["configs"][i]["complete"] and not p["configs"][i]["kept"])
    out["any_mismatch"] = bool(out["mismatches_total"])
    # held time and peak RSS: per pass, the mean over its kept processes; the band applies to the mean of those
    held_means, rss_means = [], []
    for p in passes:
        h = [p["configs"][i]["held_s"] for i in SG_REF if p["configs"][i]["kept"] and p["configs"][i].get("held_s") is not None]
        r = [p["configs"][i]["rss_gb"] for i in SG_REF if p["configs"][i]["kept"] and p["configs"][i].get("rss_gb") is not None]
        if h:
            held_means.append(statistics.mean(h))
        if r:
            rss_means.append(statistics.mean(r))
    out["held_s_pass_means"] = held_means
    out["rss_gb_pass_means"] = rss_means
    out["per_config"] = per
    out["n"] = n_min if n_min != 99 else 0
    # a part with fewer than NEED pass means has no verdict (e.g. no /usr/bin/time on a card: no RSS at all)
    held_ok = None if len(held_means) < NEED else inb(statistics.mean(held_means), 0.2, 0.4)
    rss_ok = None if len(rss_means) < NEED else inb(statistics.mean(rss_means), 1.5, 2.5)
    out["launch_times_within_5pct"] = holds if out["n"] >= NEED else None
    out["held_in_0.2_0.4"], out["rss_in_1.5_2.5GB"] = held_ok, rss_ok
    if out["mismatches_total"]:            # "any mismatch on either card falsifies": decisive at any n
        out["holds"], out["decisive_fail"] = False, True
        return out
    if out["n"] < NEED or held_ok is None or rss_ok is None:
        out["holds"] = None
        return out
    out["holds"] = holds and held_ok and rss_ok
    return out


# ------------------------------------------------------------------------------------------------ ridge-X3
def lat_r3(C):
    def fn(sp, x3):
        used, v = [], {}
        d16, d4, d1 = tl(sp, "tload-dram-one", 16), tl(sp, "tload-dram-one", 4), tl(sp, "tload-dram-one", 1)
        l16, s16 = tl(sp, "tload-l2-one", 16), tl(sp, "tload-scp-one", 16)
        used += [(sp, d16), (sp, d4), (sp, d1), (sp, l16), (sp, s16)]
        bpc = lambda r, L: L * 64 * r["iters"] / r["cycles_max"] if r else None
        v["dram16_B"], v["dram4_B"] = bpc(d16, 16), bpc(d4, 4)
        v["dram1_cyc"] = d1["cycles_per_load"] if d1 else None
        v["k_hat"] = 32 * d1["cycles_per_load"] / d16["cycles_per_load"] if d1 and d16 else None
        v["l2_16_B"], v["scp16_B"] = bpc(l16, 16), bpc(s16, 16)
        for m in ("1", "32"):
            rs = [r for r in jlines(x3.f(f"x3-m{m}.jsonl")) if "pattern" in r]
            if not rs or not all(r.get("ok") is True for r in rs):   # a failed launch: the pass is not kept
                used.append((x3, None)); v[f"enercat_m{m}"] = None
                continue
            used += [(x3, r) for r in rs]
            v[f"enercat_m{m}"] = statistics.mean(r["bytes"] / r["participants"] / r["cycles_max"] for r in rs)
        v["enercat_one_minus_32"] = (v["enercat_m1"] - v["enercat_m32"]) if v["enercat_m1"] and v["enercat_m32"] else None
        return v, used
    passes = pass_values(C, ["sp", "x3"], fn)
    keys = ["dram16_B", "dram4_B", "dram1_cyc", "k_hat", "l2_16_B", "scp16_B", "enercat_m1", "enercat_m32",
            "enercat_one_minus_32"]
    M, n = means(passes, keys)
    out = {"n": n, "pass_means": M, "passes": passes}
    if n < NEED:
        out["holds"] = None
        return out
    m = lambda k: M[k].get("mean")
    k = M["k_hat"]
    ch = {"dram16_B": inb(m("dram16_B"), 1.33, 1.47), "dram4_B": inb(m("dram4_B"), 1.68, 1.88),
          "dram1_cyc": inb(m("dram1_cyc"), 69, 77), "k_hat_ci_in_2.5_4.5": k["lo"] >= 2.5 and k["hi"] <= 4.5,
          "l2_16_within10pct_of_6.4": M["l2_16_B"]["lo"] >= 5.76 and M["l2_16_B"]["hi"] <= 7.04,
          "scp16_within10pct_of_6.4": M["scp16_B"]["lo"] >= 5.76 and M["scp16_B"]["hi"] <= 7.04,
          "dram16_within10pct_of_1.4": M["dram16_B"]["lo"] >= 1.26 and M["dram16_B"]["hi"] <= 1.54,
          "enercat_m1_1.40pm0.10": inb(m("enercat_m1"), 1.30, 1.50),
          "enercat_m32_0.88pm0.03": inb(m("enercat_m32"), 0.85, 0.91),
          "one_minus_32_excludes_0_positive": M["enercat_one_minus_32"]["lo"] > 0}
    out["checks"] = ch
    out["k_hat_decision"] = ("ridge-68 consistent" if ch["k_hat_ci_in_2.5_4.5"] else
                             "drop '4 lines per round trip'" if k["lo"] > 4.5 else "neither (interval straddles a bound)")
    out["holds"] = all(ch.values())
    # registered "either card" / "both cards" page actions: k_hat above 4.5 on either card drops the sentence; the
    # concurrency sentence needs (one - 32) > 0 on both, so one card failing it decides
    if k["lo"] > 4.5 or not ch["one_minus_32_excludes_0_positive"]:
        out["decisive_fail"] = True
    return out


# ------------------------------------------------------------------------------------------------ hot line
HOT_COMMITTED = [f"fairness|{h}|0xffffffff|32|0" for h in (0, 7, 15, 31)] + ["fairness|0|0xffffffff|1|0"] + \
    [f"placement|{h}|0xffffffff|32|0" for h in ("0", "scp:0", "own", "scp:own")] + \
    [f"local|{h}|{m}|32|0" for h in ("scplocal:0", "dramlocal:0", "scpstream:0", "dramstream:0") for m in ("0x1", "0xffffffff")] + \
    [f"requesters|scplocal:0|0x3|{n}|0" for n in (1, 2, 4, 8, 12, 16, 20, 24, 32)] + \
    [f"shires|scplocal:0|{m}|32|0" for m in ("0x3", "0x7", "0x1f", "0x1ff", "0x1ffff", "0xffffffff")] + \
    [f"pace|scplocal:0|0xffffffff|32|{p}" for p in (0, 1000, 4000, 8000, 10000, 12000, 16000, 20000, 40000, 100000)]


def host_ops(r):
    s = r["home"].split(":")[-1]
    if s == "own":
        return None, None
    h = int(s)
    for x in r["shire"]:
        if x["s"] == h:
            return x["ops"], x["minions"]
    return None, None


class HotPass:
    def __init__(self, K, U):
        self.K, self.U = K, U
        cfg = {}
        f = open_any(U.f("configs.txt"))
        for line in (f or []):
            p = line.rstrip("\n").split("|", 2)
            if len(p) == 3:
                cfg[int(p[0])] = (p[1], p[2])
        self.by = {}
        for r in jlines(U.f("sweep.jsonl")):
            if r.get("test") != "hotline" or r.get("cfg") not in cfg:
                continue
            args = cfg[r["cfg"]][1].split()
            warm = int(args[args.index("--warmup") + 1]) if "--warmup" in args else 5
            key = f'{r["group"]}|{r["home"]}|{r["shire_mask"]}|{r["per_shire"]}|{r["pace"]}'
            if r["window_cycles"] != 6000000:
                key += f'|W{r["window_cycles"]}'
            if warm != 5:
                key += f"|w{warm}"
            r["_kept"] = U.keep_rec(r)
            self.by[key] = r

    def get(self, key):
        """(record, kept) or (None, False)."""
        r = self.by.get(key)
        return (r, bool(r and r["_kept"]))

    def host(self, key):
        r, k = self.get(key)
        if r is None:
            return None, False
        return host_ops(r)[0], k


def hot_sub(C, fn):
    """fn(HotPass) -> dict with 'value'/'holds' or None (a needed launch missing or dropped)."""
    out = []
    for K, U in C.units("hl"):
        P = HotPass(K, U)
        d = fn(P)
        out.append({"pass": K, **d} if d else {"pass": K, "kept": False})
    return out


def common_hot_ref():
    """A card with no committed hot-line run (aifoundry1's): a configuration is stopped (unstopped) when it is on
    every committed card (it is the same 42-row split on aifoundry2 and aifoundry3); frac = None where they differ."""
    out = {}
    for key in REF["hotline"][CARDS[0]]:
        fs = [REF["hotline"][c].get(key, {}).get("frac") for c in CARDS]
        if any(f is None for f in fs):
            out[key] = {"frac": None}
        elif all(f < 0.01 for f in fs):
            out[key] = {"frac": max(fs)}
        elif all(f >= 0.01 for f in fs):
            out[key] = {"frac": min(fs)}
        else:
            out[key] = {"frac": None}
    return out


def lat_h(C):
    card = C.card
    has_ref = card in REF["hotline"]           # P1c's band is the committed value of this card
    ref = REF["hotline"][card] if has_ref else common_hot_ref()
    subs = {}

    def alone32(P, home):
        return P.host(f"local|{home}|0x1|32|0")

    def aloneN(P, n):
        return P.host(f"alone|scplocal:0|0x1|{n}|0")

    # P1a: stopped scratchpad-homed host counts (binary, every launch, every pass)
    def p1a(P):
        chk, kept = {}, True
        for key in HOT_COMMITTED:
            g, home, mask, n, pace = key.split("|")
            if home not in ("scplocal:0", "scpstream:0") or ref[key].get("frac") is None or ref[key]["frac"] >= 0.01:
                continue
            v, k = P.host(key)
            kept &= k
            band = pm(295, 16) if g == "requesters" and n == "24" else pm(390, 16) if mask == "0x3" and n == "32" else pm(384, 16)
            chk[key] = (v, inb(v, *band))
        return {"kept": kept and bool(chk), "holds": all(x[1] for x in chk.values()), "counts": {k: v[0] for k, v in chk.items()}}

    # P1b: DRAM-homed <= 0.05% of the same-pass alone count, every launch
    def p1b(P):
        chk, kept = {}, True
        for home in ("dramlocal:0", "dramstream:0"):
            v, k = P.host(f"local|{home}|0xffffffff|32|0")
            a, ka = alone32(P, home)
            kept &= k and ka
            chk[home] = (v / a if (v is not None and a) else None)
        return {"kept": kept, "holds": all(x is not None and x <= 0.0005 for x in chk.values()), "frac": chk}

    # P1c: unstopped host fractions (magnitude: pass means within +-2 pp of the committed per-card value)
    def p1c(P):
        vals, kept = {}, True
        for key in HOT_COMMITTED:
            g, home, mask, n, pace = key.split("|")
            f0 = ref[key].get("frac")
            if f0 is None or f0 < 0.01 or (g == "local" and mask == "0x1"):
                continue
            r, k = P.get(key)
            a, ka = alone32(P, home)
            kept &= k and ka
            if r is None or not a:
                vals[key] = None
                continue
            ho, hm = host_ops(r)
            vals[key] = ho / hm / (a / 32)
        return {"kept": kept, "fracs": vals}

    # P1d: 10 ms shares; P1e: cycles per atomic (magnitudes on pass means)
    SHARE_ROWS = [f"fairness|{h}|0xffffffff|32|0" for h in (0, 7, 15, 31)] + \
        [f"placement|{h}|0xffffffff|32|0" for h in ("0", "scp:0", "own", "scp:own")]
    CPO10 = [f"fairness|{h}|0xffffffff|32|0" for h in (0, 7, 15, 31)] + ["fairness|0|0xffffffff|1|0"] + \
        [f"placement|{h}|0xffffffff|32|0" for h in ("0", "scp:0")]
    CPO031 = [f"placement|{h}|0xffffffff|32|0" for h in ("own", "scp:own")]

    def p1de(P):
        d, kept = {"shares": {}, "cpo": {}}, True
        for key in SHARE_ROWS:
            r, k = P.get(key)
            kept &= k
            d["shares"][key] = {x["s"]: x["share"] for x in r["shire"]} if r else None
        for key in CPO10 + CPO031:
            r, k = P.get(key)
            kept &= k
            d["cpo"][key] = r["cycles_max"] / r["total_ops"] if r else None   # the host's cycles_per_op, unrounded
        d["kept"] = kept
        return d

    # P2 edge (binary)
    def p2(P):
        d, kept = {}, True
        for n in (19, 20, 21, 22, 23, 24):
            g = "req" if n in (19, 21, 22, 23) else "requesters"
            v, k = P.host(f"{g}|scplocal:0|0x3|{n}|0")
            a, ka = aloneN(P, n)
            kept &= k and ka
            d[n] = v / a if (v is not None and a) else None
        ok = all(d[n] is not None and d[n] >= 0.95 for n in (19, 20, 21)) and \
            all(d[n] is not None and d[n] <= 0.01 for n in (22, 23, 24))
        return {"kept": kept, "holds": ok, "host_over_aloneN": d}

    # P3 pacing
    def p3(P):
        d, kept = {}, True
        a, ka = alone32(P, "scplocal:0")
        kept &= ka
        for p in (0, 9000, 9500, 9800, 10000, 10500, 12000, 16000):
            r, k = P.get(f"pace|scplocal:0|0xffffffff|32|{p}")
            kept &= k
            d[p] = (r, host_ops(r)[0] / a if (r and a) else None)
        frac = {p: v[1] for p, v in d.items()}
        binary = all(frac[p] is not None and frac[p] <= 0.01 for p in (9000, 9500)) and \
            all(frac[p] is not None and frac[p] > 0.01 for p in (9800, 10500))
        r0, r10 = d[0][0], d[10000][0]
        ham = None
        if r0 and r10:
            ham = (r10["total_ops"] - host_ops(r10)[0]) / (r0["total_ops"] - host_ops(r0)[0])
        return {"kept": kept, "binary_holds": binary, "frac": frac, "hammering_rel": ham}

    # P4 windows (binary)
    def p4(P):
        d, kept = {}, True
        for h in ("scplocal:0", "dramlocal:0", "scpstream:0", "dramstream:0"):
            v3, k3 = P.host(f"win|{h}|0xffffffff|32|0|W3000000")
            v60, k60 = P.host(f"win|{h}|0xffffffff|32|0|W60000000")
            kept &= k3 and k60
            d[h] = [v3, v60]
        ok = all(v[0] is not None and v[1] is not None and v[1] <= 2 * v[0] for v in d.values())
        return {"kept": kept, "holds": ok, "host_3e6_60e6": d}

    # P5 pollers (binary)
    def p5(P):
        v, k = P.host("poll|scplocal:0|0xffffffff|1|0")
        a, ka = aloneN(P, 1)
        f = v / a if (v is not None and a) else None
        return {"kept": k and ka, "holds": f is not None and f <= 0.01, "host_over_alone1": f}

    # P6 N = 2..20 (magnitude on pass means)
    def p6(P):
        d, kept = {}, True
        for n in (2, 4, 8, 12, 16, 20):
            v, k = P.host(f"requesters|scplocal:0|0x3|{n}|0")
            a, ka = aloneN(P, n)
            kept &= k and ka
            d[n] = v / a if (v is not None and a) else None
        return {"kept": kept, "host_over_aloneN": d}

    # P7 warm-up (binary)
    def p7(P):
        v0, k0 = P.host("warm|scplocal:0|0xffffffff|32|0|w0")
        v10, k10 = P.host("warm|scplocal:0|0xffffffff|32|0|w10")
        return {"kept": k0 and k10, "holds": inb(v0, 512, 576) and inb(v10, 192, 256), "count_w0": v0, "count_w10": v10}

    def binary(name, fn):
        ps = hot_sub(C, fn)
        kept = [p for p in ps if p.get("kept")]
        subs[name] = {"n": len(kept), "holds": None if len(kept) < NEED else all(p["holds"] for p in kept),
                      "passes": [{k: v for k, v in p.items()} for p in ps]}

    binary("P1a_stopped_scp_counts", p1a)
    binary("P1b_dram_homed_le_0.05pct", p1b)
    binary("P2_edge", p2)
    binary("P4_windows", p4)
    binary("P5_pollers", p5)
    binary("P7_warmup", p7)
    # magnitudes
    ps = [p for p in hot_sub(C, p1c) if p.get("kept")]
    m = {}
    for key in (ps[0]["fracs"] if ps else {}):
        c = ci99([p["fracs"].get(key) for p in ps])
        if has_ref:
            m[key] = {"ci99": c, "committed": ref[key]["frac"],
                      "ok": c.get("mean") is not None and abs(c["mean"] - ref[key]["frac"]) <= 0.02}
        else:   # reported against both committed cards' values, not tested (the band is a per-card value)
            com = {rc: REF["hotline"][rc][key]["frac"] for rc in CARDS}
            m[key] = {"ci99": c, "committed": com,
                      "within_2pp_of": {rc: c.get("mean") is not None and abs(c["mean"] - v) <= 0.02 for rc, v in com.items()}}
    if has_ref:
        subs["P1c_unstopped_fracs"] = {"n": len(ps), "holds": None if len(ps) < NEED else all(v["ok"] for v in m.values()),
                                       "per_config": m}
    else:
        subs["P1c_unstopped_fracs"] = {"n": len(ps), "holds": None, "tested": False, "per_config": m,
                                       "reported": "band is aifoundry2's / aifoundry3's committed value: reported, not tested"}
    ps = [p for p in hot_sub(C, p1de) if p.get("kept")]
    sh_ok, cpo_ok, shares, cpos = True, True, {}, {}
    if ps:
        for key in ps[0]["shares"]:
            per_shire = {s: statistics.mean(p["shares"][key][s] for p in ps) for s in ps[0]["shares"][key]}
            shares[key] = [min(per_shire.values()), max(per_shire.values())]
            sh_ok &= all(0.997 <= x <= 1.005 for x in per_shire.values())
        for key in ps[0]["cpo"]:
            mcpo = statistics.mean(p["cpo"][key] for p in ps)
            cpos[key] = mcpo
            cpo_ok &= inb(mcpo, 9.98, 10.02) if key in CPO10 else inb(mcpo, 0.30, 0.32)
    subs["P1d_shares"] = {"n": len(ps), "holds": None if len(ps) < NEED else sh_ok, "pass_mean_share_range": shares}
    subs["P1e_cycles_per_atomic"] = {"n": len(ps), "holds": None if len(ps) < NEED else cpo_ok, "pass_means": cpos}
    ps3 = hot_sub(C, p3)
    k3 = [p for p in ps3 if p.get("kept")]
    mag = {}
    if k3:
        for p_, band in ((10000, (0.50, 0.60)), (12000, (0.82, 0.90)), (16000, (0.93, 0.97))):
            c = ci99([p["frac"][p_] for p in k3])
            mag[p_] = {"ci99": c, "ok": inb(c.get("mean"), *band)}
        c = ci99([p["hammering_rel"] for p in k3])
        mag["hammering_10000"] = {"ci99": c, "ok": inb(c.get("mean"), 0.94, 0.98)}
    subs["P3_pacing"] = {"n": len(k3), "holds": None if len(k3) < NEED else
                         (all(p["binary_holds"] for p in k3) and all(v["ok"] for v in mag.values())),
                         "binary_every_pass": [p.get("binary_holds") for p in k3], "magnitudes": mag,
                         "passes": ps3}
    ps6 = [p for p in hot_sub(C, p6) if p.get("kept")]
    m6 = {n: ci99([p["host_over_aloneN"][n] for p in ps6]) for n in (2, 4, 8, 12, 16, 20)} if ps6 else {}
    subs["P6_N2_20"] = {"n": len(ps6), "holds": None if len(ps6) < NEED else all(c["mean"] >= 0.97 for c in m6.values()),
                        "pass_means": m6,
                        "within_about_a_percent": (all(c["mean"] >= 0.985 for c in m6.values()) if m6 else None)}
    hs = [s["holds"] for s in subs.values() if s.get("tested", True)]
    holds = None if any(h is None for h in hs) else all(hs)
    # hotline-relay-l2-52 (the scpself bus error) is in LAT-H's claim list with no registered band: when the optional
    # probe ran (LAT_SCPSELF=1), report what it did per pass, for the page's qualifier; it does not enter "holds"
    probe = []
    for K, U in C.units("hl"):
        runs = {r["name"]: r.get("rc") for r in jlines(U.f("launches.jsonl")) if r.get("name") in ("self", "health")}
        if not runs:
            continue
        lines = {r["group"]: r.get("ok") for r in jlines(U.f("sweep.jsonl")) if r.get("group") in ("self", "health")}
        probe.append({"pass": K, "self_rc": runs.get("self"), "self_printed_ok": lines.get("self"),
                      "health_rc": runs.get("health"), "health_ok": lines.get("health")})
    out = {"n": min(s["n"] for s in subs.values()) if subs else 0, "holds": holds, "sub": subs,
           "scpself_probe": probe or "not run (LAT_SCPSELF unset)"}
    if not has_ref:
        out["reported_not_tested"] = ["P1c_unstopped_fracs"]
    return out


# ------------------------------------------------------------------------------------------------ relay
NEW_GEOM = [3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15]
LINE = {"aifoundry2": (941.0, -35.19), "aifoundry3": (930.3, -33.98)}


def spearman(x, y):
    rx, ry = _ranks(x), _ranks(y)
    if rx.std() == 0 or ry.std() == 0:   # a constant series has no rank order: rho = 0 (no monotone relation)
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def _ranks(v):
    v = np.asarray(v, float)
    order = np.argsort(v, kind="mergesort")
    r = np.empty(len(v))
    r[order] = np.arange(1, len(v) + 1)
    for val in np.unique(v):   # average ranks over ties
        idx = v == val
        r[idx] = r[idx].mean()
    return r


def perm_p(L, G, n=100000, seed=1):
    """One-sided: fraction of shuffles of G over L (ties in L kept) whose Spearman rho <= the observed rho."""
    rho = spearman(L, G)
    rl, rg = _ranks(L), _ranks(G)
    if rl.std() == 0 or rg.std() == 0:
        return rho, 1.0
    rl = (rl - rl.mean()) / np.sqrt(((rl - rl.mean()) ** 2).sum())
    rg = (rg - rg.mean()) / np.sqrt(((rg - rg.mean()) ** 2).sum())
    rng = np.random.default_rng(seed)
    cnt = 0
    for start in range(0, n, 10000):
        k = min(10000, n - start)
        perms = np.argsort(rng.random((k, len(rg))), axis=1)
        cnt += int(((rg[perms] * rl).sum(1) <= rho + 1e-12).sum())
    return rho, (cnt + 1) / (n + 1)


def rl_key(r):
    return (r["group"], r["medium"], r["stage_bytes"], r["stages"], r["work"], r["shires"], r["hop_distance"])


def lat_r(C):
    card = C.card
    # (ii)'s line and (v)'s size / intensity / stage ratios are committed per-card values: on a card without them
    # (aifoundry1's) both parts are reported against aifoundry2's and aifoundry3's values, not tested
    has_ref = card in LINE and card in REF["relay"]
    passes = []
    for K, U in C.units("rl"):
        recs = {}
        for r in jlines(U.f("sweep.jsonl")):
            if r.get("test") != "relay":
                continue
            recs[rl_key(r)] = (r["gb_s"], U.keep_rec(r), r.get("ok"))
        passes.append({"pass": K, "recs": recs})
    def pmean(key):
        v = [p["recs"][key][0] for p in passes if key in p["recs"] and p["recs"][key][1]]
        return (statistics.mean(v), len(v)) if v else (None, 0)
    off = {d: pmean(("offsets", "hop", 1 << 20, 8, 1, 32, d)) for d in range(1, 32)}
    n_off = min(v[1] for v in off.values())
    out = {"n": n_off, "offsets_pass_means": {d: v[0] for d, v in off.items()}}
    geo = {}
    for g in range(1, 17):
        a, b = off[g][0], off[32 - g][0]
        geo[g] = None if a is None or b is None else (a + b) / 2
    L = {g: ONC.longest_handoff(g)["hops"] for g in range(1, 17)}
    MH = {g: ONC.ring_hops(g)["mean"] for g in range(1, 17)}
    ch = {}
    if n_off >= NEED and all(v is not None for v in geo.values()):
        rho, p = perm_p([L[g] for g in NEW_GEOM], [geo[g] for g in NEW_GEOM])
        ch["i_spearman_le_-0.5_and_perm_p_lt_0.01"] = rho <= -0.5 and p < 0.01
        if not ch["i_spearman_le_-0.5_and_perm_p_lt_0.01"]:   # registered: "(i) fails on either card -> drop"
            out["decisive_fail"] = True
        out["i"] = {"rho": rho, "perm_p": p, "shuffles": 100000}
        if has_ref:
            a0, b0 = LINE[card]
            within = {g: abs(geo[g] / (a0 + b0 * L[g]) - 1) for g in NEW_GEOM}
            out["ii"] = {"within_5pct": sum(v <= 0.05 for v in within.values()), "rel_dev": within}
            ch["ii_ge_9_of_11_within_5pct"] = out["ii"]["within_5pct"] >= 9
        else:
            out["ii"] = {"reported_not_tested": True}
            for rc in CARDS:
                a0, b0 = LINE[rc]
                within = {g: abs(geo[g] / (a0 + b0 * L[g]) - 1) for g in NEW_GEOM}
                out["ii"][f"against_{rc}_line"] = {"within_5pct": sum(v <= 0.05 for v in within.values()),
                                                   "rel_dev": within}
        X = np.array([[1.0, L[g], MH[g]] for g in range(1, 17)])
        Y = np.array([geo[g] for g in range(1, 17)])
        beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
        res = Y - X @ beta
        s2 = float(res @ res) / (16 - 3)
        se = math.sqrt(s2 * np.linalg.inv(X.T @ X)[2, 2])
        lo, hi = beta[2] - t995(13) * se, beta[2] + t995(13) * se
        out["iii"] = {"mean_hops_coef": float(beta[2]), "ci99": [float(lo), float(hi)], "L_coef": float(beta[1])}
        ch["iii_mean_hops_ci_inside_pm10"] = lo >= -10 and hi <= 10
        mir = {d: off[32 - d][0] / off[d][0] - 1 for d in range(1, 16)}
        out["iv"] = {"worst_mirror_rel": max(mir.values(), key=abs)}
        ch["iv_mirror_within_2pct"] = all(abs(v) <= 0.02 for v in mir.values())
    # (v) ratios on pass means
    H = {m: pmean(("headline", m, 1 << 20, 8, 1, 32, 1)) for m in ("dram", "scp", "hop")}
    v5 = {}
    nv = min(x[1] for x in H.values())
    if nv >= NEED:
        v5["headline_hop_over_dram"] = H["hop"][0] / H["dram"][0]
        v5["headline_own_over_dram"] = H["scp"][0] / H["dram"][0]
        ch["v_headline_hop_in_11.5_13.2"] = inb(v5["headline_hop_over_dram"], 11.5, 13.2)
        ch["v_headline_own_in_29_33"] = inb(v5["headline_own_over_dram"], 29.0, 33.0)
    keyof = {"size": [(64 << 10) * 2 ** i for i in range(5)], "intensity": [2 ** i for i in range(9)],
             "stages": [1, 2, 4, 8, 16, 32]}
    worst, ratios_ok, n_rat = 0.0, True, 99
    ratio = {}
    worst_vs = {rc: 0.0 for rc in CARDS}      # no committed ratios (aifoundry1): worst deviation from each card's
    for grp, params in keyof.items():
        for prm in params:
            key = {"size": lambda m: (grp, m, prm, 8, 1, 32, 1), "intensity": lambda m: (grp, m, 1 << 20, 8, prm, 32, 1),
                   "stages": lambda m: (grp, m, 1 << 20, prm, 1, 32, 1)}[grp]
            M = {m: pmean(key(m)) for m in ("dram", "scp", "hop")}
            n_rat = min(n_rat, *(x[1] for x in M.values()))
            if any(x[0] is None for x in M.values()):
                ratios_ok = False
                continue
            new = {"scp_over_dram": M["scp"][0] / M["dram"][0], "hop_over_dram": M["hop"][0] / M["dram"][0]}
            ratio[f"{grp}|{prm}"] = new
            if not has_ref:
                for rc in CARDS:
                    r_ = REF["relay"][rc].get(f"{grp}|{prm}")
                    worst_vs[rc] = max([worst_vs[rc]] + [abs(new[q] / r_[q] - 1) for q in new])
                continue
            r_ = REF["relay"][card].get(f"{grp}|{prm}")
            for q in new:
                dev = new[q] / r_[q] - 1
                worst = max(worst, abs(dev))
                ratios_ok &= abs(dev) <= 0.05
    if has_ref:
        v5["ratio_worst_rel_dev"] = worst
    else:
        v5["ratio_worst_rel_dev_reported_not_tested"] = {f"vs_{rc}": w for rc, w in worst_vs.items()}
        v5["ratios"] = ratio
    if n_rat >= NEED:
        if has_ref:
            ch["v_size_intensity_stages_ratios_within_5pct"] = ratios_ok
        two = ratio["stages|2"]["hop_over_dram"]
        flat = statistics.mean(ratio[f"stages|{k}"]["hop_over_dram"] for k in (4, 8, 16, 32))
        v5["two_stage_over_flat"] = two / flat
        ch["v_two_stage_ge_1.05x_flat"] = two >= 1.05 * flat
    B2, B8 = pmean(("bigsize", "dram", 2 << 20, 8, 1, 32, 1)), pmean(("bigsize", "dram", 8 << 20, 8, 1, 32, 1))
    if min(B2[1], B8[1]) >= NEED:
        v5["dram_256MB_over_64MB"] = B8[0] / B2[0]
        ch["v_dram_256MB_ge_1.05x_64MB"] = B8[0] >= 1.05 * B2[0]
    out["v"] = v5
    out["checks"] = ch
    nwrong = sum(1 for p in passes for v in p["recs"].values() if v[2] is False)
    out["relay_ok_false_launches"] = nwrong
    complete = n_off >= NEED and nv >= NEED and n_rat >= NEED and min(B2[1], B8[1]) >= NEED and \
        len(ch) == (9 if has_ref else 7)
    out["holds"] = all(ch.values()) if complete else None
    out["n"] = min(n_off, nv, n_rat if n_rat != 99 else 0, B2[1], B8[1])
    if not has_ref:
        out["reported_not_tested"] = ["ii (per-card line)", "v size/intensity/stages ratios (per-card values)"]
    return out


# ------------------------------------------------------------------------------------------------ items
ITEMS = [
    ("LAT-M1", lat_m1, "every kept pass on each card inside the tolerances (L1 5.25+-0.01, RB 36.00+-0.05, L2/local scp 47.00+-0.05, knees, hart 1 39.0/50.0+-0.05, all pointer checks ok); >= 3 kept passes"),
    ("LAT-M2", lat_m2, "tolerances every kept pass (per-requester median of the kept 4 MB / 256 MB chases); requester effect L3(0)-L3(24): 99% t over passes excludes 0 and overlaps 9.7+-1.5"),
    ("LAT-M3", lat_m3, "every kept pass: >= 95% of the 124 remote points within 1.0 of 99.84 + 12.00 x MARTY hops; a->b = b->a within 0.5 (6 pairs); row-0 slope 12.00+-0.05"),
    ("LAT-N1", lat_n1, "deterministic tolerance every kept pass"),
    ("LAT-N2", lat_n2, "deterministic tolerance every kept pass; --search 12/12 restarts recover MARTY's distances"),
    ("LAT-N3", lat_n3, "per card, OLS slope on MARTY hops over the kept passes' pairs, shire-block bootstrap (10,000 draws, two-sided 99% interval): kept if upper < +6 and every pass slope < +6; dropped if upper >= +12.02; medians 535+-60 every pass"),
    ("LAT-N4", lat_n4, "deterministic tolerance every kept pass"),
    ("LAT-S1", lat_s1, "deterministic: every kept pass on each card inside the bands; any deviation falsifies"),
    ("LAT-S2", lat_s2, "pass means (n >= 3) inside the bands on each card"),
    ("LAT-S3", lat_s3, "pass means inside the bands; L2 2,000 - 20,000 difference: 99% t excludes 0 on each card"),
    ("LAT-S4", lat_s4, "pass means inside the bands on each card"),
    ("LAT-S5", lat_s5, "every kept pass: lane efficiencies identical to 18 Sep, throughput within 3%, static-refill(a3) > 0.1 T/s; 5 short blocks: 99% t (df 4) of refill-static(a2) excludes 0 positive, mean in 0.017+-0.02"),
    ("LAT-G", lat_g, "pass means (n >= 3): 99% t inside +-5% of each page value; 0 mismatches; device-held 0.2-0.4 s and peak RSS 1.5-2.5 GB on pass means"),
    ("LAT-R3", lat_r3, "99% t (df n-1) per card: k_hat interval inside [2.5, 4.5]; lone-minion rates within 10%; enercat (one - 32) excludes 0 positive; bands on pass means"),
    ("LAT-H", lat_h, "binary parts (P1 stop counts, P1b, P2, P3 stop/no-stop, P4, P5, P7) in every kept pass (>= 3); magnitudes (P1 fractions, shares, cycles/atomic, P3 bands, P6) on pass means"),
    ("LAT-R", lat_r, "(i) Spearman rho <= -0.5 and one-sided permutation p < 0.01 over the 11 new geometries; (ii) >= 9 of 11 within 5%; (iii) mean-hops 99% CI inside +-10; (iv) mirrors within 2%; (v) ratios on pass means"),
]


def outcome(pc):
    # registered "either card" rules: any deviation (LAT-S1, sgemm mismatch), "dropped on either card" (LAT-N3,
    # LAT-R (i), k_hat > 4.5), "must hold on both cards" for one page action (LAT-S3 difference, LAT-S5 crossover,
    # LAT-R3 concurrency): one card that has its repeats and fails decides, whatever the other card shows
    if any(pc[c].get("decisive_fail") for c in CARDS):
        return "FAIL"
    hs = [pc[c].get("holds") for c in CARDS]
    if any(h is None for h in hs):
        return "INSUFFICIENT"
    if all(hs):
        return "PASS"
    if not any(hs):
        return "FAIL"
    return "CARD-DIFFERENT"


def fmt(x, k=2):
    return "-" if x is None else f"{x:.{k}f}" if isinstance(x, float) else str(x)


def reading(item, pc, oc):
    a2, a3 = pc["aifoundry2"], pc["aifoundry3"]
    ns = f"kept repeats a2 {a2.get('n', 0)}, a3 {a3.get('n', 0)}"
    extra = ""
    full = all((pc[c].get("n") or 0) >= NEED for c in CARDS)   # page actions only once both cards have their repeats
    if item == "LAT-M2":
        extra = "; requester effect a2 {} a3 {}".format(
            *[fmt(pc[c].get("requester_effect_ci99", {}).get("mean")) for c in CARDS])
    elif item == "LAT-N3":
        extra = "; " + ", ".join(f"a{c[-1]}: {pc[c].get('decision', '-')}" for c in CARDS)
    elif item == "LAT-S5":
        extra = "; crossover a2: {}, a3: {} (short blocks {}/{})".format(
            a2.get("crossover") or "-", a3.get("crossover") or "-", a2.get("n_short", 0), a3.get("n_short", 0))
        if a2.get("crossover") and a3.get("crossover"):
            extra += "; page: " + ("'from alpha = 2'" if a2["crossover"] == a3["crossover"] == "from alpha = 2"
                                   else "'between alpha = 3 and 2'")
    elif item == "LAT-S3":
        both = all(pc[c].get("checks", {}).get("l2_diff_excludes_0") for c in CARDS)
        if full:
            extra = "; " + ("page attributes the 2.03 TB/s to the probe's cold start" if both else
                            "cold-start attribution not supported on both cards")
    elif item == "LAT-R3":
        extra = "; k_hat a2: {}, a3: {}".format(a2.get("k_hat_decision", "-"), a3.get("k_hat_decision", "-"))
        conc = all(pc[c].get("checks", {}).get("one_minus_32_excludes_0_positive") for c in CARDS)
        if full:
            extra += "; " + ("page adds the concurrency sentence" if conc else "no concurrency sentence")
        e1 = [pc[c].get("pass_means", {}).get("enercat_m1", {}).get("mean") for c in CARDS]
        extra += "; one-minion enercat a2 {} a3 {} B/minion-cycle".format(*[fmt(x) for x in e1])
    elif item == "LAT-R":
        i_ok = all(pc[c].get("checks", {}).get("i_spearman_le_-0.5_and_perm_p_lt_0.01") for c in CARDS)
        have = full and all("i" in pc[c] for c in CARDS)
        if have:
            extra = "; " + ("keep 'falls with the longest hand-off'" if i_ok else
                            "drop 'falls with the longest hand-off', keep 'offset moves bandwidth by up to a quarter'")
    elif item == "LAT-H":
        w = [pc[c].get("sub", {}).get("P6_N2_20", {}).get("within_about_a_percent") for c in CARDS]
        extra = ("; 'within about a percent' " + ("holds" if all(x is True for x in w) else "not supported")) if full else ""
        bad = sorted({k for c in CARDS for k, s in pc[c].get("sub", {}).items() if s.get("holds") is False})
        if bad:
            extra += "; failing parts: " + ", ".join(bad)
    elif item == "LAT-G":
        if any(pc[c].get("any_mismatch") and pc[c].get("mismatches_total") for c in CARDS):
            extra = "; a mismatch falsifies 'silicon results were correct'"
        for c in CARDS:
            if (pc[c].get("n") or 0) >= NEED and pc[c].get("rss_in_1.5_2.5GB") is None:
                extra += f"; a{c[-1]}: no peak-RSS data (/usr/bin/time?)"
            if pc[c].get("incomplete"):
                extra += f"; a{c[-1]} incomplete runs: {len(pc[c]['incomplete'])}"
    dec = [f"a{c[-1]}" for c in CARDS if pc[c].get("decisive_fail")]
    if dec:
        extra += "; decided by " + " and ".join(dec) + " (registered either-card rule)"
    if oc == "INSUFFICIENT":
        fp = {c: pc[c].get("failing_passes") for c in CARDS if pc[c].get("failing_passes")}
        if fp:
            extra += "; failing kept passes so far: " + ", ".join(f"a{c[-1]} {v}" for c, v in fp.items())
    return f"{oc}: {ns}{extra}"


def short(c):
    m = re.fullmatch(r"aifoundry(\d+)(?:-c(\d+))?", c)
    return (f"a{m.group(1)}" + (f"c{m.group(2)}" if m.group(2) else "")) if m else c


def all_cards_outcome(pc, cards):
    """The registered test over every card: PASS on every card, CARD-DIFFERENT on some, FAIL on none, INSUFFICIENT if
    a card lacks its repeats; a registered either-card rule becomes an any-card rule and decides FAIL, as registered."""
    if any(pc[c].get("decisive_fail") for c in cards):
        return "FAIL"
    hs = [pc[c].get("holds") for c in cards]
    if any(h is None for h in hs):
        return "INSUFFICIENT"
    if all(hs):
        return "PASS"
    if not any(hs):
        return "FAIL"
    return "CARD-DIFFERENT"


REPORTED_PARTS = {"LAT-H": "P1c host fractions (a per-card committed value; shown against aifoundry2's and "
                           "aifoundry3's)",
                  "LAT-R": "(ii) the per-card 5-offset line and (v) the size / intensity / stage ratios (per-card "
                           "committed values; shown against aifoundry2's and aifoundry3's)"}
HOLD_WORD = {True: "holds", False: "fails", None: "undecided"}


def all_cards_reading(item, pc, oc, cards, info):
    parts = [f"{oc} over {len(cards)} cards: kept repeats " + ", ".join(f"{short(c)} {pc[c].get('n', 0)}" for c in cards),
             ", ".join(f"{short(c)} {HOLD_WORD.get(pc[c].get('holds'), pc[c].get('holds'))}" for c in cards)]
    dec = [short(c) for c in cards if pc[c].get("decisive_fail")]
    if dec:
        parts.append("decided by " + " and ".join(dec) + " (registered either-card rule, applied to every card)")
    nodata = [short(c) for c in cards if not info[c]["data"]]
    if nodata:
        parts.append("no data from " + ", ".join(nodata))
    rep = [short(c) for c in cards if pc[c].get("reported_not_tested")]
    if rep and item in REPORTED_PARTS:
        parts.append(f"reported, not tested, on {', '.join(rep)}: {REPORTED_PARTS[item]}")
    if item == "LAT-G":
        for c in cards:
            n = sum(v for k, v in info[c].get("launches_by_basis", {}).items() if k.startswith("kept: brackets at the idle"))
            if n:
                parts.append(f"{short(c)}: {n} sgemm processes kept with brackets at the idle point (clock during "
                             "sgemm not sampled; the block's other bursts read 600 MHz)")
    err = [f"{short(c)}: {pc[c]['error']}" for c in cards if pc[c].get("error")]
    if err:
        parts.append("errors: " + "; ".join(err))
    return "; ".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-search", action="store_true", help="skip LAT-N2's layout search (then LAT-N2 is INSUFFICIENT)")
    ap.add_argument("--cards", help="comma-separated cards for all_cards (default: the campaign's cards, tools/claims-v3/campaign.py, and every "
                                    "other card directory with a lat/ subdirectory under --data)")
    a = ap.parse_args()
    plan = {}
    pj = os.path.join(ROOT, "docs", "reports", "data", "2026-09-25-claims-v3", "plan3.json.gz")
    if os.path.exists(pj):
        p = json.load(gzip.open(pj, "rt"))
        e = next(x for x in p["experiments"] if x["id"] == "V3-LAT")
        plan = {x["item"]: x for x in e["predictions"]}
    present = sorted(d for d in os.listdir(a.data) if os.path.isdir(os.path.join(a.data, d, "lat")))
    allc = sorted({c.strip() for c in a.cards.split(",") if c.strip()}) if a.cards else sorted(set(CAMPAIGN) | set(present))
    every = sorted(set(allc) | set(CARDS))
    cards = {c: Card(a.data, c) for c in every}
    items = []
    for name, fn, test in ITEMS:
        pc = {}
        for c in every:
            try:
                pc[c] = fn(cards[c], search=not a.no_search) if fn is lat_n2 else fn(cards[c])
            except Exception as ex:   # a malformed file must not hide the other items
                pc[c] = {"n": 0, "holds": None, "error": f"{type(ex).__name__}: {ex}"}
        oc = outcome(pc)
        items.append({"item": name, "claims": plan.get(name, {}).get("claims", []),
                      "prediction": plan.get(name, {}).get("prediction"), "per_card": rnd(pc), "test": test,
                      "outcome": oc, "reading": reading(name, pc, oc), "_pc": pc})
    info = {c: cards[c].summary() for c in every}          # now with how each launch was judged
    for it in items:
        pc = it.pop("_pc")
        ao = all_cards_outcome(pc, allc)
        it["all_cards"] = {"cards": allc, "outcome": ao, "holds": {c: pc[c].get("holds") for c in allc},
                           "reading": all_cards_reading(it["item"], pc, ao, allc, info)}
    out = {"experiment": "V3-LAT", "data": os.path.abspath(a.data),
           "outcome_cards": list(CARDS), "all_cards": allc,
           "cards": {c: {"blocks": cards[c].blocks, "skipped": cards[c].skipped,
                         "passes": {K: sorted(u) for K, u in cards[c].passes.items()},
                         "short_blocks": [s[0] for s in cards[c].short], **info[c]} for c in every},
           "items": items}
    json.dump(rnd(out), open(a.out, "w"), indent=1, default=str, allow_nan=False)
    for c in every:
        if info[c]["rule"] == "idle-aware":
            print(f"{c}: idle points {info[c]['idle_points_mhz']} MHz (probes {info[c]['idle_probes_mhz']}); "
                  f"launches {info[c].get('launches_by_basis', {})}")
    for it in items:
        print(f"{it['item']:7s} {it['reading']}")
        print(f"{'':7s} all cards: {it['all_cards']['reading']}")


if __name__ == "__main__":
    main()
