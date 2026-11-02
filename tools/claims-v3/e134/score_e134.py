#!/usr/bin/env python3
"""E134 scorer (Q136): every price, ratio, contrast and registered rule, from the reduction's per-run tables. Standard
library only; written and committed before any E134 block is read. Every threshold and frozen prediction is
predictions-e134.json's; nothing numeric about a rule is written here except what reads them.

    python3 tools/claims-v3/e134/score_e134.py --primary <runs.csv>,<e134.json> [--arm name=<runs.csv>,<e134.json>,<value>,<gate>] ...
        --md results.md --json scored.json

A price (README.md, "Analysis"; E102's trains and E130's scorer, tools/claims-v3/e130/score_e130.py `Book`, ported to fp32):
  per run     the primary value is the BOARD's p_raw, the mean board power over [t0+1 s, t0+3 s) with no temperature term
              (E102's and E130's trains). Arms: rail_raw (the minion rail, [t0+2, t0+4)), p80 (E78's temperature term at the
              reduction's slope), dips kept, gates off.
  per block   each item's run minus its OWN zero (e134-tiles.json `zero`) interpolated linearly in time between that zero's
              reads in the block (the nearest read on each side is its own zero); settling runs (segment -1) never count;
              divided by (designed flips per op x the run's rate) for fJ per flipped bit.
  the train gate  a zero's interior read more than 0.25 W off the straight line through its two neighbouring reads of the
              same zero, on the board's p_raw, sets the block aside (E102's and E130's gate); E78's pass gates
              (reduce_e78.py: passes_set_aside, passes_config_flags) set a block aside too. Off in the gates-off arm only.
  over blocks the mean of the per-block values, its SE from the between-block scatter, t(0.975, n-1) x SE. The block is the
              unit of replication. A contrast is a per-block combination of items, paired inside each block. A ratio is
              the ratio of the per-block means with its 95% Fieller interval, paired by block.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e134.json")
TILES = os.path.join(HERE, "e134", "e134-tiles.json")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
A_BITS = tuple(range(8))
B_BITS = tuple(range(6, 17))


def t975(df):
    return T975.get(df, 1.96 + 2.4 / max(df, 1))


def block_of(p):
    p = int(p)
    return "A" if 13410 <= p <= 13419 else "B" if 13420 <= p <= 13429 else "S"


def mean_ci(v):
    v = [float(x) for x in v if x is not None]
    if not v:
        return {"mean": None, "se": None, "n": 0, "ci95": None, "lo": None, "hi": None}
    m = sum(v) / len(v)
    if len(v) < 2:
        return {"mean": m, "se": None, "n": 1, "ci95": None, "lo": None, "hi": None}
    s = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)) / math.sqrt(len(v))
    h = s * t975(len(v) - 1)
    return {"mean": m, "se": s, "n": len(v), "ci95": h, "lo": m - h, "hi": m + h}


def fieller(xs, ys):
    """The ratio of two per-block means with its 95% Fieller interval, paired by block (xs, ys: {block: value}).
    lo and hi are None when the denominator's own interval reaches zero (the ratio is unbounded)."""
    keys = sorted(set(xs) & set(ys))
    n = len(keys)
    if n < 2:
        return {"ratio": None, "lo": None, "hi": None, "n": n}
    a = [xs[k] for k in keys]
    b = [ys[k] for k in keys]
    mx, my = sum(a) / n, sum(b) / n
    if my == 0:
        return {"ratio": None, "lo": None, "hi": None, "n": n}
    sx2 = sum((x - mx) ** 2 for x in a) / (n - 1) / n
    sy2 = sum((y - my) ** 2 for y in b) / (n - 1) / n
    c = sum((x - mx) * (y - my) for x, y in zip(a, b)) / (n - 1) / n
    t = t975(n - 1)
    r = mx / my
    g = t * t * sy2 / (my * my)
    if g >= 1:
        return {"ratio": r, "lo": None, "hi": None, "n": n, "unbounded": True}
    disc = max((sx2 - 2 * r * c + r * r * sy2) - g * (sx2 - (c * c / sy2 if sy2 > 0 else 0)), 0.0)
    cen = r - g * c / sy2 if sy2 > 0 else r
    half = (t / abs(my)) * math.sqrt(disc)
    return {"ratio": r, "lo": (cen - half) / (1 - g), "hi": (cen + half) / (1 - g), "n": n}


def interp(pts, t):
    """Linear in time through (t, value) points, flat beyond the first and the last (E78's interp_zero)."""
    pts = sorted(pts)
    if not pts:
        return None
    if len(pts) == 1 or t <= pts[0][0]:
        return pts[0][1]
    if t >= pts[-1][0]:
        return pts[-1][1]
    for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
        if t1 <= t <= t2:
            return v1 + (v2 - v1) * (t - t1) / max(t2 - t1, 1e-9)
    return pts[-1][1]


def num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(v) else v


def load_runs(path):
    out = []
    for r in csv.DictReader(open(path)):
        out.append({"pass": int(float(r["pass"])), "item": r["item"],
                    "segment": int(float(r["segment"])) if r.get("segment") not in (None, "") else None,
                    "t0": num(r.get("t0_ms")), "p_raw": num(r.get("p_raw")), "p80": num(r.get("p80")),
                    "rail_raw": num(r.get("rail_raw")), "rate": num(r.get("rate")),
                    "fail": int(float(r.get("fail") or 0)), "fail_reasons": r.get("fail_reasons", ""),
                    "t_win": num(r.get("t_win")), "start_c": num(r.get("start_c")), "mv": num(r.get("mv")),
                    "pos": int(float(r.get("pos") or 0))})
    return out


class Book:
    """One arm: per (item, block) the step over the item's own zero in W and in fJ per flipped bit."""

    def __init__(self, runs, tiles, value="p_raw", gate=True, gate_w=0.25, red=None):
        self.tiles = tiles                     # full name ("fp32.<kind>") -> tile entry (e134-tiles.json)
        self.value = value
        self.gate = gate
        self.gate_w = gate_w
        self.set_aside = []
        self.blocks = {"A": [], "B": []}
        self.steps = {}                        # item -> {"W": {pass: W}, "fJ": {pass: fJ}}
        self.zero_resid = []
        e78_bad = set()
        if red and gate:
            for x in red.get("passes_set_aside", []) + red.get("passes_config_flags", []):
                e78_bad.add(int(x["pass"]))
                self.set_aside.append({"pass": int(x["pass"]), "why": ["E78 pass gate: " + json.dumps(x.get("why", x))[:300]]})
        self._build(runs, e78_bad)

    def _build(self, runs, e78_bad):
        by_pass = {}
        for r in runs:
            if r["fail"] or block_of(r["pass"]) == "S" or r["item"] not in self.tiles:
                continue
            by_pass.setdefault(r["pass"], []).append(r)
        for p, rr in sorted(by_pass.items()):
            if p in e78_bad:
                continue
            blk = block_of(p)
            zeros = {}
            for r in rr:
                if self.tiles[r["item"]]["zero"] is None and r["segment"] != -1:
                    zeros.setdefault(r["item"], []).append(r)
            bad = []
            for z, reads in zeros.items():
                reads = sorted(reads, key=lambda r: r["t0"])
                for a, b, c in zip(reads, reads[1:], reads[2:]):
                    if None in (a["p_raw"], b["p_raw"], c["p_raw"]):
                        continue
                    line = a["p_raw"] + (c["p_raw"] - a["p_raw"]) * (b["t0"] - a["t0"]) / max(c["t0"] - a["t0"], 1.0)
                    dev = b["p_raw"] - line
                    if abs(dev) > self.gate_w:
                        bad.append((z, round(dev, 3)))
                    va, vb, vc = a[self.value], b[self.value], c[self.value]
                    if None not in (va, vb, vc):
                        self.zero_resid.append(vb - (va + (vc - va) * (b["t0"] - a["t0"]) / max(c["t0"] - a["t0"], 1.0)))
            if bad and self.gate:
                self.set_aside.append({"pass": p, "why": [f"train gate: {z} interior read {d:+.3f} W off its line" for z, d in bad]})
                continue
            self.blocks[blk].append(p)
            per = {}
            for r in rr:
                t = self.tiles[r["item"]]
                if t["zero"] is None or r["segment"] == -1:
                    continue
                zr = zeros.get(t["zero"])
                if not zr:
                    continue
                v = r[self.value]
                pts = [(q["t0"], q[self.value]) for q in zr if q[self.value] is not None]
                zh = interp(pts, r["t0"]) if pts else None
                if v is None or zh is None:
                    continue
                e = per.setdefault(r["item"], {"W": [], "fJ": []})
                e["W"].append(v - zh)
                if r["rate"]:
                    e["fJ"].append(1e15 * (v - zh) / (t["designed_flips_per_op"] * r["rate"]))
            for item, e in per.items():
                s = self.steps.setdefault(item, {"W": {}, "fJ": {}})
                for k in ("W", "fJ"):
                    if e[k]:
                        s[k][p] = sum(e[k]) / len(e[k])

    def series(self, kind, key="fJ"):
        return dict(self.steps.get("fp32." + kind, {}).get(key, {}))

    def price(self, kind):
        return {"W": mean_ci(self.series(kind, "W").values()), "fJ": mean_ci(self.series(kind, "fJ").values())}


def per_block(book, combo, key="W"):
    """combo: {kind: weight}. Per block: sum of weight x value, for blocks holding every kind of combo."""
    ser = {t: book.series(t, key) for t in combo}
    keys = set.intersection(*[set(s) for s in ser.values()]) if ser else set()
    return {p: sum(w * ser[t][p] for t, w in combo.items()) for p in sorted(keys)}


def contrasts(reg):
    """Every contrast the rules and the report read, in W, per block (paired)."""
    sc = reg["design"]["balanced_to_allin_flip_scale_B"]          # 4096 / 3968
    out = {}
    for j in A_BITS:
        out[f"A_word_allin_{j}"] = {f"a67j_{j}": 1.0, f"aj_{j}": -1.0}
        out[f"A_word_bal_{j}"] = {f"a67p_{j}": 1.0, f"ap_{j}": -1.0}
    for j in B_BITS:
        out[f"B_swing_{j}"] = {f"bj_{j}": 1.0, f"bp_{j}": -sc}
    return out


def ratios():
    out = {}
    for j in A_BITS:
        out[f"A_W79_allin_over_bal_{j}"] = (f"aj_{j}", f"ap_{j}")
        out[f"A_W67_allin_over_bal_{j}"] = (f"a67j_{j}", f"a67p_{j}")
        out[f"A_word_allin_ratio_{j}"] = (f"a67j_{j}", f"aj_{j}")
    for j in B_BITS:
        out[f"B_allin_over_bal_{j}"] = (f"bj_{j}", f"bp_{j}")
    return out


def statistics(book, reg):
    st = {"contrasts_W": {}, "ratios_per_flip": {}}
    for name, c in contrasts(reg).items():
        s = per_block(book, c, "W")
        st["contrasts_W"][name] = mean_ci(s.values()) | {"per_block": s}
    for name, (a, b) in ratios().items():
        st["ratios_per_flip"][name] = fieller(book.series(a, "fJ"), book.series(b, "fJ"))
    return st


def n_kept(book, kind):
    return len(book.blocks[kind])


def rule_r1(book, st, reg):
    """A's low bits on W79 (E102-R2's low half): POSITION / CONSTANT / INCONCLUSIVE."""
    th = reg["rules"]["E134-R1"]["threshold"]
    if n_kept(book, "A") < reg["plan"]["min_kept_blocks"]:
        return "NOT SCORED", {}
    r = {j: st["ratios_per_flip"][f"A_W79_allin_over_bal_{j}"] for j in reg["rules"]["E134-R1"]["bits"]}
    if any(x["hi"] is None for x in r.values()):
        return "INCONCLUSIVE (a ratio is unbounded)", r
    if all(x["hi"] < th for x in r.values()):
        return "POSITION", r
    if all(x["lo"] >= th for x in r.values()):
        return "CONSTANT", r
    return "INCONCLUSIVE", r


def rule_r2(book, st, reg):
    """The word sets an A bit's price: WORD / SAME / INCONCLUSIVE, on the registered contrast."""
    R = reg["rules"]["E134-R2"]
    if n_kept(book, "A") < reg["plan"]["min_kept_blocks"]:
        return "NOT SCORED", {}
    c = st["contrasts_W"][R["contrast"]]
    if c["lo"] is None:
        return "NOT SCORED", c
    s = R["sign"]
    lo, hi = (c["lo"], c["hi"]) if s > 0 else (-c["hi"], -c["lo"])
    if lo >= R["word_threshold_w"]:
        return "WORD", c
    if lo >= -R["same_band_w"] and hi <= R["same_band_w"]:
        return "SAME", c
    return "INCONCLUSIVE", c


def rule_r3(book, st, reg):
    """Where the word's cost sits: FLIP (all-in = balanced per flip) / SWING / INCONCLUSIVE."""
    R = reg["rules"]["E134-R3"]
    if n_kept(book, "A") < reg["plan"]["min_kept_blocks"]:
        return "NOT SCORED", {}
    r = st["ratios_per_flip"][R["ratio"]]
    if r["hi"] is None:
        return "INCONCLUSIVE (unbounded)", r
    if r["lo"] >= R["flip_band"][0] and r["hi"] < R["flip_band"][1]:
        return "FLIP", r
    if r["lo"] >= R["swing_threshold"]:
        return "SWING", r
    return "INCONCLUSIVE", r


def rule_r4(book, st, reg):
    """Where the accumulators' swing starts on B: AT <j> / EARLIER / LATER / INCONCLUSIVE."""
    R = reg["rules"]["E134-R4"]
    if n_kept(book, "B") < reg["plan"]["min_kept_blocks"]:
        return "NOT SCORED", {}
    lo_bit, hi_bit = R["quiet_bit"], R["onset_bit"]
    q = st["contrasts_W"][f"B_swing_{lo_bit}"]
    o = st["contrasts_W"][f"B_swing_{hi_bit}"]
    if q["lo"] is None or o["lo"] is None:
        return "NOT SCORED", {"quiet": q, "onset": o}
    band = R["none_band_w"]
    q_none = q["lo"] >= -band and q["hi"] <= band
    q_some = q["lo"] > 0
    o_some = o["lo"] > 0
    o_none = o["lo"] >= -band and o["hi"] <= band
    if q_some:
        v = "EARLIER"
    elif q_none and o_some:
        v = f"AT {hi_bit}"
    elif q_none and o_none:
        v = "LATER"
    else:
        v = "INCONCLUSIVE"
    return v, {"quiet": q, "onset": o}


def rule_r5(book, st, reg):
    """The bench's word differences over A's low bits: AGREES / DISAGREES / INCONCLUSIVE."""
    R = reg["rules"]["E134-R5"]
    if n_kept(book, "A") < reg["plan"]["min_kept_blocks"]:
        return "NOT SCORED", {}
    rows, resolved, against = {}, 0, 0
    for j in R["bits"]:
        c = st["contrasts_W"][f"A_word_allin_{j}"]
        b = reg["contrasts_pred_W"][f"A_word_allin_{j}"]["bench"]
        res = c["lo"] is not None and (c["lo"] > 0 or c["hi"] < 0)
        same_sign = res and ((c["lo"] > 0) == (b > 0))
        resolved += bool(res)
        against += bool(res and not same_sign)
        rows[j] = {"measured": c.get("mean"), "lo": c.get("lo"), "hi": c.get("hi"), "bench": b, "resolved": res,
                   "bench_sign": bool(same_sign)}
    if not R["bits"]:
        return "NOT SCORED", rows
    if against:
        return "DISAGREES", rows
    if resolved >= len(R["bits"]) / 2:
        return "AGREES", rows
    return "INCONCLUSIVE", rows


def rule_s1(book, reg):
    """E67's own tiles on this card against E67's own list: PASS if at least the registered number lie in their bands."""
    R = reg["rules"]["E134-S1"]
    if n_kept(book, "A") < reg["plan"]["min_kept_blocks"]:
        return "NOT SCORED", {}
    rows = {}
    inside = 0
    for j in A_BITS:
        ref = reg["published"]["e67_allin_W"][str(j)]
        p = book.price(f"a67j_{j}")["W"]
        se = reg["published"]["e67_allin_se_W"][str(j)]
        band = max(R["band_abs_w"], R["band_rel"] * abs(ref), R["band_se_mult"] * se)
        ok = p["mean"] is not None and abs(p["mean"] - ref) <= band
        inside += bool(ok)
        rows[j] = {"e67_W": ref, "e134_W": p["mean"], "ci95": p["ci95"], "band_w": band, "inside": ok}
    return ("PASS" if inside >= R["min_inside"] else "FAIL"), {"inside": inside, "rows": rows}


def models_report(book, reg):
    """Each frozen model's rms and bias over each list, board W (reported, never a verdict)."""
    out = {}
    lists = {"A_W79": [f"aj_{j}" for j in A_BITS] + [f"ap_{j}" for j in A_BITS],
             "A_W67": [f"a67j_{j}" for j in A_BITS] + [f"a67p_{j}" for j in A_BITS],
             "A_allin_both_words": [f"aj_{j}" for j in A_BITS] + [f"a67j_{j}" for j in A_BITS],
             "B": [f"bj_{j}" for j in B_BITS] + [f"bp_{j}" for j in B_BITS]}
    for lname, kinds in lists.items():
        out[lname] = {}
        for model in reg["models"]:
            d = []
            for k in kinds:
                pr = reg["items"]["fp32." + k]["pred_W"].get(model)
                m = book.price(k)["W"]["mean"]
                if pr is not None and m is not None:
                    d.append(m - pr)
            if d:
                out[lname][model] = {"n": len(d), "rms_w": math.sqrt(sum(x * x for x in d) / len(d)), "bias_w": sum(d) / len(d)}
    return out


def score(runs, red, tiles, reg, value="p_raw", gate=True):
    book = Book(runs, tiles, value=value, gate=gate, gate_w=reg["plan"]["train_gate_w"], red=red)
    st = statistics(book, reg)
    rules = {}
    for name, fn in (("E134-R1", rule_r1), ("E134-R2", rule_r2), ("E134-R3", rule_r3), ("E134-R4", rule_r4),
                     ("E134-R5", rule_r5)):
        v, d = fn(book, st, reg)
        rules[name] = {"verdict": v, "detail": d}
    v, d = rule_s1(book, reg)
    rules["E134-S1"] = {"verdict": v, "detail": d}
    prices = {k[5:]: book.price(k[5:]) for k in tiles if tiles[k]["zero"] is not None}
    zr = book.zero_resid
    noise = {"n": len(zr), "rms_w": math.sqrt(sum(x * x for x in zr) / len(zr)) if zr else None}
    return {"blocks": book.blocks, "set_aside": book.set_aside, "rules": rules, "prices": prices, "statistics": st,
            "models": models_report(book, reg), "zero_scatter": noise}


def fmt(x, d=3):
    return "-" if x is None else f"{x:+.{d}f}" if isinstance(x, float) else str(x)


def ci(c, d=3):
    if not c or c.get("mean") is None:
        return "-"
    if c.get("lo") is None:
        return f"{c['mean']:.{d}f} (n {c.get('n')})"
    return f"{c['mean']:.{d}f} [{c['lo']:.{d}f}, {c['hi']:.{d}f}] (n {c['n']})"


def rci(r):
    if not r or r.get("ratio") is None:
        return "-"
    if r.get("lo") is None:
        return f"{r['ratio']:.2f} (unbounded, n {r['n']})"
    return f"{r['ratio']:.2f} [{r['lo']:.2f}, {r['hi']:.2f}] (n {r['n']})"


def markdown(res, reg):
    p = res["primary"]
    L = ["# E134 results (generated by score_e134.py; primary = board p_raw, own zeros, dips removed, E78's gates and the train gate)", ""]
    L.append(f"Kept blocks: A {p['blocks']['A']}, B {p['blocks']['B']}; set aside: {p['set_aside']}")
    L.append(f"Zero reads' scatter about their neighbours' line: rms {fmt(p['zero_scatter']['rms_w'])} W over {p['zero_scatter']['n']}")
    L.append("")
    L.append("| rule | primary | " + " | ".join(res["arms"].keys()) + " |")
    L.append("|---|---|" + "---|" * len(res["arms"]))
    for r in p["rules"]:
        L.append(f"| {r} | **{p['rules'][r]['verdict']}** | " + " | ".join(a["rules"][r]["verdict"] for a in res["arms"].values()) + " |")
    L.append("")
    for side, kinds in (("A, word W79 (E79's / E102's)", [("aj", "ap")]), ("A, word W67 (E67's)", [("a67j", "a67p")])):
        L.append(f"## {side}: fJ per flipped bit, board, and the ratio all-in / balanced")
        L.append("")
        L.append("| bit | all-in fJ | balanced fJ | ratio per flip | all-in W | bench all-in W | E67 list W |")
        L.append("|---:|---|---|---|---|---:|---:|")
        for j in A_BITS:
            aj, ap = kinds[0][0] + f"_{j}", kinds[0][1] + f"_{j}"
            rname = ("A_W79" if kinds[0][0] == "aj" else "A_W67") + f"_allin_over_bal_{j}"
            it = reg["items"]["fp32." + aj]["pred_W"]
            L.append(f"| {j} | {ci(p['prices'][aj]['fJ'], 0)} | {ci(p['prices'][ap]['fJ'], 0)} | {rci(p['statistics']['ratios_per_flip'][rname])} | "
                     f"{ci(p['prices'][aj]['W'])} | {fmt(it.get('bench'))} | {fmt(it.get('position_only_e67'))} |")
        L.append("")
    L.append("## The word on A: W67 minus W79, board W, paired by block")
    L.append("")
    L.append("| bit | all-in: measured | all-in: bench | balanced: measured | balanced: bench | all-in ratio W67/W79 |")
    L.append("|---:|---|---:|---|---:|---|")
    for j in A_BITS:
        c1 = p["statistics"]["contrasts_W"][f"A_word_allin_{j}"]
        c2 = p["statistics"]["contrasts_W"][f"A_word_bal_{j}"]
        b1 = reg["contrasts_pred_W"][f"A_word_allin_{j}"]["bench"]
        b2 = reg["contrasts_pred_W"][f"A_word_bal_{j}"]["bench"]
        L.append(f"| {j} | {ci(c1)} | {fmt(b1)} | {ci(c2)} | {fmt(b2)} | {rci(p['statistics']['ratios_per_flip'][f'A_word_allin_ratio_{j}'])} |")
    L.append("")
    L.append("## B: fJ per flipped bit, the ratio, and the swing's watts (all-in minus balanced scaled to the all-in count)")
    L.append("")
    L.append("| bit | all-in fJ | balanced fJ | ratio per flip | swing W | swing W: count model | swing W: bench | real-sum result bits an op over hq |")
    L.append("|---:|---|---|---|---|---:|---:|---:|")
    for j in B_BITS:
        c = p["statistics"]["contrasts_W"][f"B_swing_{j}"]
        cp = reg["contrasts_pred_W"][f"B_swing_{j}"]
        L.append(f"| {j} | {ci(p['prices'][f'bj_{j}']['fJ'], 0)} | {ci(p['prices'][f'bp_{j}']['fJ'], 0)} | {rci(p['statistics']['ratios_per_flip'][f'B_allin_over_bal_{j}'])} | "
                 f"{ci(c)} | {fmt(cp.get('count_model'))} | {fmt(cp.get('bench'))} | {reg['items'][f'fp32.bj_{j}']['res_bits_over_zero']:.0f} |")
    L.append("")
    L.append("## Frozen models, rms and bias over each list (board W; reported)")
    L.append("")
    for lname, mm in p["models"].items():
        L.append(f"- {lname}: " + "; ".join(f"{m} rms {v['rms_w']:.3f} bias {v['bias_w']:+.3f} (n {v['n']})" for m, v in mm.items()))
    L.append("")
    L.append("## E134-S1: E67's own tiles against E67's list (this card)")
    L.append("")
    s1 = p["rules"]["E134-S1"]["detail"]
    for j, row in (s1.get("rows") or {}).items():
        L.append(f"- bit {j}: E67 {row['e67_W']:.3f} W, E134 {fmt(row['e134_W'])} W (band ±{row['band_w']:.3f}): {'inside' if row['inside'] else 'OUTSIDE'}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    tiles = json.load(open(TILES))["tiles"]
    csvp, redp = a.primary.split(",")
    red = json.load(open(redp))
    res = {"experiment": "E134", "primary": score(load_runs(csvp), red, tiles, reg), "arms": {}}
    for arm in a.arm:
        name, spec = arm.split("=", 1)
        c, rj, val, gate = spec.split(",")
        res["arms"][name] = score(load_runs(c), json.load(open(rj)), tiles, reg, value=val, gate=(gate == "on"))
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, default=lambda o: None)
    if a.md:
        open(a.md, "w").write(markdown(res, reg))
    for r, v in res["primary"]["rules"].items():
        print(f"{r}: {v['verdict']}" + "".join(f" | {n} {x['rules'][r]['verdict']}" for n, x in res["arms"].items()))


if __name__ == "__main__":
    main()
