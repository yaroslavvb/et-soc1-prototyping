#!/usr/bin/env python3
"""E102 scorer (Q132): every price, ratio and registered rule, from the reduction's per-run table. Standard library only; written and committed before any pass is
read. The rules and their thresholds are predictions-e102.json's; nothing numeric about a rule is written here except what reads them.

    python3 tools/claims-v3/kinds/score_e102.py --dir <reduced dir holding e102.json, runs.csv and the arms> --md results.md --json scored.json

A price, per block, per arm (E102.md, "Analysis"):
  per run     board: p80 in block G (E78's launch gate, frozen slope); p_raw in the trains T and I (no temperature term: a whole-degree reading can only add noise to a
              pair that differs by a few hundredths of a degree). rail: rail_raw, the mean minion rail over [t0+2 s, t0+4 s), uncorrected, in every block (E79's rail arm).
  per pass    each item's run minus its OWN zero (e102.json `zero`) interpolated linearly in time between that zero's reads in the pass, flat beyond them; settling runs (segment
              -1) never count. Mean over the item's runs in the pass. Divide by (designed flips per op x the run's rate) for fJ per flipped bit.
  over passes the mean, its SE from the between-pass scatter, t(0.975, n-1) x SE. The pass is the unit of replication. A price whose interval contains zero is a BOUND.
  A rule whose input rests on fewer than three kept passes is NOT SCORED.
"""
import argparse
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e102.json")
TILES = os.path.join(HERE, "e102", "e102.json")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179}


def t975(df):
    return T975.get(df, 1.96 + 2.4 / max(df, 1))


def block_of(p):
    p = int(p)
    return "G" if 10210 <= p <= 10219 else "T" if 10220 <= p <= 10229 else "I" if 10230 <= p <= 10239 else "S"


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


def fieller(xs, ys, scale=1.0):
    """The ratio of two means with its 95% Fieller interval. xs and ys are {pass-key: value}: when their keys are the same set the pair is treated as paired, else independent.
    Returns mean ratio x scale, lo, hi; lo and hi are None when the denominator's own interval contains zero (the ratio is unbounded)."""
    kx, ky = sorted(xs), sorted(ys)
    nx, ny = len(kx), len(ky)
    if nx < 2 or ny < 2:
        return {"ratio": None, "lo": None, "hi": None, "n": min(nx, ny), "paired": False, "df": 0}
    paired = kx == ky
    a = [xs[k] for k in kx]
    b = [ys[k] for k in ky]
    mx, my = sum(a) / nx, sum(b) / ny
    sx2 = sum((x - mx) ** 2 for x in a) / (nx - 1) / nx
    sy2 = sum((y - my) ** 2 for y in b) / (ny - 1) / ny
    c = sum((x - mx) * (y - my) for x, y in zip(a, b)) / (nx - 1) / nx if paired else 0.0
    df = nx - 1 if paired else min(nx, ny) - 1
    t = t975(df)
    if my == 0:
        return {"ratio": None, "lo": None, "hi": None, "n": min(nx, ny), "paired": paired, "df": df}
    r = mx / my
    g = t * t * sy2 / (my * my)
    if g >= 1:
        return {"ratio": r * scale, "lo": None, "hi": None, "n": min(nx, ny), "paired": paired, "df": df, "unbounded": True}
    disc = sx2 - 2 * r * c + r * r * sy2 - g * (sx2 - (c * c / sy2 if sy2 > 0 else 0))
    disc = max(disc, 0.0)
    cen = r - g * c / sy2 if sy2 > 0 else r
    half = (t / abs(my)) * math.sqrt(disc)
    lo, hi = (cen - half) / (1 - g), (cen + half) / (1 - g)
    return {"ratio": r * scale, "lo": lo * scale, "hi": hi * scale, "n": min(nx, ny), "paired": paired, "df": df}


def interp(pts, t):
    """Linear in time through (t, value) points, flat beyond the first and the last (E78's interp_zero)."""
    if not pts:
        return None
    pts = sorted(pts)
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
        out.append({"pass": int(r["pass"]), "item": r["item"], "segment": int(float(r["segment"])) if r.get("segment") not in (None, "") else None,
                    "t0": num(r["t0_ms"]), "p_raw": num(r.get("p_raw")), "p80": num(r.get("p80")), "rail": num(r.get("rail_raw")), "rate": num(r.get("rate")),
                    "fail": int(float(r.get("fail") or 0)), "t_win": num(r.get("t_win")), "start_c": num(r.get("start_c")), "D": num(r.get("D")),
                    "mv": num(r.get("mv")), "pos": int(float(r.get("pos") or 0))})
    return out


class Book:
    """One arm: per (block, item, pass): the board and rail steps over the own zero, and fJ per flipped bit."""

    def __init__(self, runs, tiles, gate, board_trains="p_raw", set_aside=()):
        self.tiles = tiles
        self.gate = gate
        self.set_aside = set(set_aside)
        self.own_gate = []
        self.steps = {}        # (block, item) -> {"board": {pass: W}, "rail": {pass: W}, "fj_board": {pass: fJ}, "fj_rail": {pass: fJ}}
        self.passes = {}
        self.board_trains = board_trains
        self._build(runs)

    def _value(self, r, block, arm):
        if arm == "rail":
            return r["rail"]
        return r["p80"] if block == "G" else r[self.board_trains]

    def _build(self, runs):
        by_pass = {}
        for r in runs:
            if r["fail"]:
                continue
            by_pass.setdefault(r["pass"], []).append(r)
        for p, rr in sorted(by_pass.items()):
            block = block_of(p)
            if block == "S" or p in self.set_aside:
                continue
            zeros = {}
            for z in {t["zero"] for t in self.tiles.values() if t["zero"]}:
                reads = [r for r in rr if r["item"] == z and r["segment"] != -1]
                if reads:
                    zeros[z] = reads
            # the trains' own gate: a zero's interior read off the straight line through its neighbours, on the rail
            lim = self.gate["train_zero_mid_departure_rail_w"]
            bad = []
            if block in "TI":
                for z, reads in zeros.items():
                    reads = sorted(reads, key=lambda r: r["t0"])
                    for a, b, c in zip(reads, reads[1:], reads[2:]):
                        if None in (a["rail"], b["rail"], c["rail"]):
                            continue
                        line = a["rail"] + (c["rail"] - a["rail"]) * (b["t0"] - a["t0"]) / max(c["t0"] - a["t0"], 1.0)
                        if abs(b["rail"] - line) > lim:
                            bad.append((z, round(b["rail"] - line, 3)))
            if bad:
                self.own_gate.append({"pass": p, "why": bad})
                continue
            self.passes.setdefault(block, []).append(p)
            per = {}
            for r in rr:
                t = self.tiles.get(r["item"])
                if not t or not t["zero"] or r["segment"] == -1 or t["layout"] == "zero":
                    continue
                z = zeros.get(t["zero"])
                if not z:
                    continue
                e = per.setdefault(r["item"], {"board": [], "rail": [], "fj_board": [], "fj_rail": []})
                for arm in ("board", "rail"):
                    v = self._value(r, block, arm)
                    pts = [(q["t0"], self._value(q, block, arm)) for q in z if self._value(q, block, arm) is not None]
                    zh = interp(pts, r["t0"])
                    if v is None or zh is None:
                        continue
                    d = v - zh
                    e[arm].append(d)
                    if r["rate"] and t["designed_flips_per_op"]:
                        e["fj_" + arm].append(1e15 * d / (t["designed_flips_per_op"] * r["rate"]))
            for item, e in per.items():
                s = self.steps.setdefault((block, item), {"board": {}, "rail": {}, "fj_board": {}, "fj_rail": {}})
                for k, v in e.items():
                    if v:
                        s[k][p] = sum(v) / len(v)

    def price(self, block, item, arm="board"):
        s = self.steps.get((block, item))
        if not s:
            return {"W": mean_ci([]), "fJ": mean_ci([]), "bound": None}
        w = mean_ci(s[arm].values())
        f = mean_ci(s["fj_" + arm].values())
        bound = None if f["lo"] is None else (f["lo"] <= 0 <= f["hi"])
        return {"W": w, "fJ": f, "bound": bound}

    def series(self, block, item, arm, key="W"):
        s = self.steps.get((block, item))
        if not s:
            return {}
        return dict(s[arm] if key == "W" else s["fj_" + arm])


def where(tiles, name):
    """The block a position's list value comes from: the train where the item runs in one, else the gate."""
    b = tiles[name]["block"]
    return "I" if "I" in b else "T" if "T" in b else "G"


def per_bit_ratio(book, tiles, top, bot, arm, top_block=None, bot_block=None):
    """(top's price per flipped bit) / (bot's), Fieller over passes, each item's mean step divided by its own designed count. Same block: paired by pass."""
    tb = top_block or where(tiles, top)
    bb = bot_block or where(tiles, bot)
    xs = book.series(tb, top, arm)
    ys = book.series(bb, bot, arm)
    if tb == bb:
        keep = sorted(set(xs) & set(ys))
        xs = {k: xs[k] for k in keep}
        ys = {k: ys[k] for k in keep}
    scale = tiles[bot]["designed_flips_per_op"] / tiles[top]["designed_flips_per_op"]
    r = fieller(xs, ys, scale)
    r.update({"top": top, "bot": bot, "top_block": tb, "bot_block": bb, "arm": arm})
    return r


def diff_w(book, tiles, a, b, arm, block_a=None, block_b=None):
    """step(a) - step(b) in watts over passes: paired in one block, else independent (a Welch-free, conservative df = min(n) - 1)."""
    ba = block_a or where(tiles, a)
    bb = block_b or where(tiles, b)
    xa = book.series(ba, a, arm)
    xb = book.series(bb, b, arm)
    if ba == bb:
        keep = sorted(set(xa) & set(xb))
        out = mean_ci([xa[k] - xb[k] for k in keep])
        out["paired"] = True
        return out
    ma, mb = mean_ci(xa.values()), mean_ci(xb.values())
    if ma["se"] is None or mb["se"] is None:
        return {"mean": None, "ci95": None, "lo": None, "hi": None, "n": 0, "paired": False}
    se = math.sqrt(ma["se"] ** 2 + mb["se"] ** 2)
    h = se * t975(min(ma["n"], mb["n"]) - 1)
    m = ma["mean"] - mb["mean"]
    return {"mean": m, "se": se, "ci95": h, "lo": m - h, "hi": m + h, "n": min(ma["n"], mb["n"]), "paired": False}


def inside(lo, hi, a, b):
    return lo is not None and hi is not None and a <= lo and hi <= b


def outside(lo, hi, a, b):
    return lo is not None and hi is not None and (hi < a or lo > b)


def score(book, tiles, reg, runs):
    R = {}
    rules = reg["rules"]
    arms = ("board", "rail")
    primary_float, primary_int8 = reg["analysis"]["primary_arm_float"], reg["analysis"]["primary_arm_int8"]

    def enough(*ns):
        return all(n is not None and n >= reg["analysis"]["min_passes"] for n in ns)

    # ---- R1, R2: does the ratio all-in / balanced stay near 5-7x across the mantissa?
    for rid, side_all, side_bal, low, top in (("E102-R1", "bj", "bp", (0, 6), 22), ("E102-R2", "aj", "ap", (0, 6), 22)):
        th = rules[rid]
        out = {}
        for arm in arms:
            cells = {}
            for j in reg["analysis"]["fp32_mantissa_positions"]:
                bb = "G" if j == 22 else None     # bit 22's ratio is paired inside the gate, like E79's
                cells[j] = per_bit_ratio(book, tiles, f"fp32.{side_all}_{j}", f"fp32.{side_bal}_{j}", arm, top_block=None if j != 22 else "G", bot_block=bb)
            lows = [cells[j] for j in low]
            t = cells[top]
            if not enough(*[c["n"] for c in lows], t["n"]):
                v = "NOT SCORED"
            elif all(c["lo"] is not None and c["lo"] >= th["constant_low_lower_bound_at_least"] for c in lows):
                v = "CONSTANT"
            elif all(c["hi"] is not None and c["hi"] < th["position_low_upper_bound_below"] for c in lows) and t["lo"] is not None and t["lo"] >= th["position_top_lower_bound_at_least"]:
                v = "POSITION"
            else:
                v = "INCONCLUSIVE"
            out[arm] = {"verdict": v, "cells": {str(j): c for j, c in cells.items()}}
        R[rid] = {"verdict": out[primary_float]["verdict"], "arm": primary_float, "expected": th["expected"], **{f"{a}_arm": out[a] for a in arms}}

    # ---- R3: the exponent: which layout is dearer, and is a balanced exponent a composite like the mantissa's top
    th = rules["E102-R3"]
    out = {}
    for arm in arms:
        cells = {}
        for side_all, side_bal in (("bj", "bp"), ("aj", "ap")):
            for j in th["positions"]:
                d = diff_w(book, tiles, f"fp32.{side_bal}_{j}", f"fp32.{side_all}_{j}", arm)
                r = per_bit_ratio(book, tiles, f"fp32.{side_all}_{j}", f"fp32.{side_bal}_{j}", arm)
                cells[f"{side_all}_{j}"] = {"balanced_minus_all_in_w": d, "ratio_all_in_over_balanced": r}
        scored = [cells[f"bj_{j}"] for j in th["positions"]]
        if not enough(*[c["balanced_minus_all_in_w"]["n"] for c in scored]):
            v = "NOT SCORED"
        elif all(c["balanced_minus_all_in_w"]["lo"] is not None and c["balanced_minus_all_in_w"]["lo"] > 0 for c in scored):
            v = "INVERTED"
        elif all(c["ratio_all_in_over_balanced"]["lo"] is not None and c["ratio_all_in_over_balanced"]["lo"] >= th["composite_ratio_lower_bound_at_least"] for c in scored):
            v = "COMPOSITE"
        else:
            v = "INCONCLUSIVE"
        out[arm] = {"verdict": v, "cells": cells}
    R["E102-R3"] = {"verdict": out[primary_float]["verdict"], "arm": primary_float, "expected": th["expected"], **{f"{a}_arm": out[a] for a in arms}}

    # ---- R4: the sign: the balanced layout makes the adder alternate
    th = rules["E102-R4"]
    out = {}
    for arm in arms:
        cells = {}
        for name, a, b, floor_ in (("fp32 B", "fp32.bp_31", "fp32.bj_31", th["min_w"]["fp32 B"]), ("fp32 A", "fp32.ap_31", "fp32.aj_31", th["min_w"]["fp32 A"]), ("fp16 B", "fp16.bp_15", "fp16.bj_15", th["min_w"]["fp16 B"])):
            d = diff_w(book, tiles, a, b, arm)
            if d["n"] < reg["analysis"]["min_passes"] or d["lo"] is None:
                v_ = "NOT SCORED"
            elif d["lo"] >= floor_:
                v_ = "CONFIRMED"
            elif d["hi"] < th["refuted_below_w"]:
                v_ = "REFUTED"
            else:
                v_ = "INCONCLUSIVE"
            cells[name] = {"difference_w": d, "floor_w": floor_, "verdict": v_}
        vs = [c["verdict"] for c in cells.values()]
        v = "REFUTED" if "REFUTED" in vs else "CONFIRMED" if all(x == "CONFIRMED" for x in vs) else "NOT SCORED" if all(x == "NOT SCORED" for x in vs) else "INCONCLUSIVE"
        out[arm] = {"verdict": v, "cells": cells}
    R["E102-R4"] = {"verdict": out[primary_float]["verdict"], "arm": primary_float, "expected": th["expected"], **{f"{a}_arm": out[a] for a in arms}}

    # ---- R5: the ties to E79's numbers, carried to this card by E82's scale
    th = rules["E102-R5"]
    cells = {}
    for name, c in th["cells"].items():
        if c["kind"] == "price":
            p = book.price(c["block"], c["item"], "board")["fJ"]
            lo, hi, m, n = p["lo"], p["hi"], p["mean"], p["n"]
        else:
            r = per_bit_ratio(book, tiles, c["top"], c["bot"], "board", top_block=c["block"], bot_block=c["block"])
            lo, hi, m, n = r["lo"], r["hi"], r["ratio"], r["n"]
        if n < reg["analysis"]["min_passes"] or lo is None:
            v_ = "NOT SCORED" if n < reg["analysis"]["min_passes"] else "INCONCLUSIVE"
        elif inside(lo, hi, c["band"][0], c["band"][1]):
            v_ = "CONFIRMED"
        elif outside(lo, hi, c["band"][0], c["band"][1]):
            v_ = "REFUTED"
        else:
            v_ = "INCONCLUSIVE"
        cells[name] = {"value": m, "lo": lo, "hi": hi, "n": n, "band": c["band"], "verdict": v_}
    vs = [c["verdict"] for c in cells.values()]
    R["E102-R5"] = {"verdict": "REFUTED" if "REFUTED" in vs else "CONFIRMED" if all(x == "CONFIRMED" for x in vs) else "INCONCLUSIVE", "cells": cells}

    # ---- R6: the train reads what the gate reads, pooled over the four items read in both protocols
    th = rules["E102-R6"]
    out = {}
    for arm in arms:
        cells = {it: {"train_minus_gate_w": diff_w(book, tiles, it, it, arm, block_a="T", block_b="G")} for it in th["items"]}
        pooled = {}
        for blk in ("T", "G"):
            ser = [book.series(blk, it, arm) for it in th["items"]]
            keys = set(ser[0]).intersection(*ser[1:])
            pooled[blk] = mean_ci([sum(x[k] for x in ser) / len(ser) for k in keys])
        b_ = th["band_w"][arm]
        if pooled["T"]["se"] is None or pooled["G"]["se"] is None or min(pooled["T"]["n"], pooled["G"]["n"]) < reg["analysis"]["min_passes"]:
            v, d = "NOT SCORED", None
        else:
            m = pooled["T"]["mean"] - pooled["G"]["mean"]
            se = math.sqrt(pooled["T"]["se"] ** 2 + pooled["G"]["se"] ** 2)
            h = se * t975(min(pooled["T"]["n"], pooled["G"]["n"]) - 1)
            d = {"mean": m, "se": se, "ci95": h, "lo": m - h, "hi": m + h}
            v = "CONFIRMED" if inside(d["lo"], d["hi"], -b_, b_) else "REFUTED" if outside(d["lo"], d["hi"], -b_, b_) else "INCONCLUSIVE"
        out[arm] = {"verdict": v, "pooled_train_minus_gate_w": d, "band_w": b_, "cells": cells}
    R["E102-R6"] = {"verdict": out["rail"]["verdict"], "arm": "rail", **{f"{a}_arm": out[a] for a in arms}}

    # ---- R7: what share of the all-in excess is the adder's flop bits, at E92's frozen price
    th = rules["E102-R7"]
    out = {}
    for arm in arms:
        cells = {}
        for j in th["positions"]:
            a, b = f"fp32.bj_{j}", f"fp32.bp_{j}"
            sc = tiles[a]["designed_flips_per_op"] / tiles[b]["designed_flips_per_op"]
            xa = mean_ci(book.series(where(tiles, a), a, arm).values())
            xb = mean_ci(book.series(where(tiles, b), b, arm).values())
            if xa["mean"] is None or xb["mean"] is None:
                continue
            excess = xa["mean"] - sc * xb["mean"]
            flops = reg["positions"][a]["flops"] - sc * reg["positions"][b]["flops"]
            rate = reg["analysis"]["rate_ops_per_s"]["fp32"]
            fl_w = flops * th["fJ_per_flop_bit"] * 1e-15 * rate
            cells[str(j)] = {"excess_w": excess, "flops_per_op": flops, "flops_w_at_e92_price": fl_w, "share": fl_w / excess if excess > 0 else None,
                             "implied_fJ_per_flop_bit": excess / (flops * rate) * 1e15 if flops > 0 else None}
        sh = [c["share"] for c in cells.values() if c["share"] is not None]
        v = "NOT SCORED" if len(sh) < len(th["positions"]) else "CONFIRMED" if all(th["share_band"][0] <= s <= th["share_band"][1] for s in sh) else "REFUTED" if all(s < th["share_band"][0] or s > th["share_band"][1] for s in sh) else "INCONCLUSIVE"
        out[arm] = {"verdict": v, "cells": cells}
    R["E102-R7"] = {"verdict": out["board"]["verdict"], "arm": "board", "expected": th["expected"], **{f"{a}_arm": out[a] for a in arms}}      # E92's price is in board watts

    # ---- R8-R12: int8's B side
    th = rules["E102-R8"]
    out = {}
    for arm in arms:
        p = book.price("I", "int8.bk_ff", arm)
        f = p["fJ"]
        if f["n"] < reg["analysis"]["min_passes"] or f["lo"] is None:
            v = "NOT SCORED"
        elif f["lo"] <= 0:
            v = "BOUND"
        elif f["lo"] >= th["e79_level_lower_bound_at_least_fJ"][arm]:
            v = "E79-LEVEL"
        elif f["hi"] < th["bench_level_upper_bound_below_fJ"][arm]:
            v = "BENCH-LEVEL"
        else:
            v = "RESOLVED-BETWEEN"
        out[arm] = {"verdict": v, "price": p}
    R["E102-R8"] = {"verdict": out[primary_int8]["verdict"], "arm": primary_int8, "expected": th["expected"], **{f"{a}_arm": out[a] for a in arms}}

    # R9: both masks flip three bits; R10: both four. So the step's difference in watts is the per-bit difference, and it stays readable when either step is small.
    th = rules["E102-R9"]
    out = {}
    for arm in arms:
        d = diff_w(book, tiles, "int8.bk_2a", "int8.bk_15", arm, block_a="I", block_b="I")
        r = per_bit_ratio(book, tiles, "int8.bk_2a", "int8.bk_15", arm, top_block="I", bot_block="I")
        b_ = th["band_w"][arm]
        if d["n"] < reg["analysis"]["min_passes"] or d["lo"] is None:
            v = "NOT SCORED"
        elif d["lo"] >= b_:
            v = "SHAPE"
        elif inside(d["lo"], d["hi"], -b_, b_):
            v = "FLAT"
        else:
            v = "INCONCLUSIVE"
        out[arm] = {"verdict": v, "difference_w": d, "ratio": r, "band_w": b_}
    R["E102-R9"] = {"verdict": out[primary_int8]["verdict"], "arm": primary_int8, "expected": th["expected"], **{f"{a}_arm": out[a] for a in arms}}

    th = rules["E102-R10"]
    out = {}
    for arm in arms:
        d = diff_w(book, tiles, "int8.bk_f0", "int8.bk_0f", arm, block_a="I", block_b="I")
        r = per_bit_ratio(book, tiles, "int8.bk_f0", "int8.bk_0f", arm, top_block="I", bot_block="I")
        b_ = th["band_w"][arm]
        if d["n"] < reg["analysis"]["min_passes"] or d["lo"] is None:
            v = "NOT SCORED"
        elif d["lo"] > 0:
            v = "RISE"
        elif inside(d["lo"], d["hi"], -b_, b_):
            v = "FLAT"
        else:
            v = "INCONCLUSIVE"
        out[arm] = {"verdict": v, "difference_w": d, "ratio": r, "band_w": b_}
    R["E102-R10"] = {"verdict": out[primary_int8]["verdict"], "arm": primary_int8, "expected": th["expected"], **{f"{a}_arm": out[a] for a in arms}}

    th = rules["E102-R11"]
    out = {}
    for arm in arms:
        rr = {}
        ff = book.series("I", "int8.bk_ff", arm)
        for name, bots in (("ff - (0f + f0)", ["int8.bk_0f", "int8.bk_f0"]), ("ff - the sum of its eight singles", [f"int8.bk_{j}" for j in range(8)])):
            vals = []
            denom = {}
            for k in ff:
                parts = [book.series("I", b_, arm).get(k) for b_ in bots]
                if None not in parts:
                    vals.append(ff[k] - sum(parts))
                    denom[k] = sum(parts)
            rr[name] = {"difference_w": mean_ci(vals), "ratio": fieller({k: ff[k] for k in denom}, denom)}
        c = rr["ff - (0f + f0)"]["difference_w"]
        b_ = th["band_w"][arm]
        v = "NOT SCORED" if c["n"] < reg["analysis"]["min_passes"] or c["lo"] is None else "CONFIRMED" if inside(c["lo"], c["hi"], -b_, b_) else "REFUTED" if outside(c["lo"], c["hi"], -b_, b_) else "INCONCLUSIVE"
        out[arm] = {"verdict": v, "cells": rr, "band_w": b_}
    R["E102-R11"] = {"verdict": out[primary_int8]["verdict"], "arm": primary_int8, **{f"{a}_arm": out[a] for a in arms}}

    th = rules["E102-R12"]
    out = {}
    for arm in arms:
        singles = {j: book.price("I", f"int8.bk_{j}", arm) for j in range(8)}
        hw = [s["fJ"]["ci95"] for s in singles.values() if s["fJ"]["ci95"] is not None]
        res = sum(1 for s in singles.values() if s["bound"] is False)
        out[arm] = {"coefficients_of_8": res, "median_half_width_fJ": sorted(hw)[len(hw) // 2] if hw else None, "list": {str(j): s for j, s in singles.items()},
                    "registered_half_width_fJ": th["registered_half_width_fJ"][arm]}
    R["E102-R12"] = {"verdict": "REPORTED", "arm": primary_int8, **{f"{a}_arm": out[a] for a in arms}}

    # ---- S1: the session tie, E82's anchors on E78's D over the type's zeros (block G only)
    cells_ = {}
    gp = book.passes.get("G", [])
    for c, t in reg["session_tie"]["cells"].items():
        vals = {}
        for r in runs:
            if r["item"] == c and r["pass"] in gp and not r["fail"] and r["D"] is not None:
                vals.setdefault(r["pass"], []).append(r["D"])
        m = mean_ci([sum(v) / len(v) for v in vals.values()])
        d = None if m["mean"] is None else m["mean"] - t["ref_w"]
        cells_[c] = {"D_w": m, "ref_w": t["ref_w"], "difference_w": d, "band_w": t["band_w"], "inside": bool(d is not None and abs(d) <= t["band_w"])}
    R["E102-S1"] = {"verdict": "PASS" if cells_ and all(x["inside"] for x in cells_.values()) else "FAIL", "cells": cells_}
    return R


def lists(book, tiles, reg):
    """Every position's price in both arms, with its frozen predictions beside it."""
    out = {}
    for name, t in tiles.items():
        if t["layout"] == "zero":
            continue
        for block in t["block"]:
            ent = {"block": block, "layout": t["layout"], "side": t["side"], "type": t["type"], "bit": t["bit"], "mask": t["mask"], "designed_flips_per_op": t["designed_flips_per_op"]}
            for arm in ("board", "rail"):
                ent[arm] = book.price(block, name, arm)
            ent["predictions"] = reg["positions"].get(name, {}).get("pred_w")
            ent["predictions_fJ"] = reg["positions"].get(name, {}).get("pred_fJ")
            out[f"{name}@{block}"] = ent
    return out


def model_rms(ls, reg):
    """Each frozen predictor's rms error in watts over a list's positions (the primary board arm), with its bias."""
    groups = {"fp32 B balanced": lambda e: e["type"] == "fp32" and e["layout"] == "bp", "fp32 B all-in": lambda e: e["type"] == "fp32" and e["layout"] == "bj",
              "fp32 A balanced": lambda e: e["type"] == "fp32" and e["layout"] == "ap", "fp32 A all-in": lambda e: e["type"] == "fp32" and e["layout"] == "aj",
              "fp16 balanced": lambda e: e["type"] == "fp16" and e["layout"] in ("bp", "ap"), "fp16 all-in": lambda e: e["type"] == "fp16" and e["layout"] in ("bj", "aj"),
              "int8 B": lambda e: e["type"] == "int8"}
    out = {}
    for g, f in groups.items():
        rows = [e for e in ls.values() if f(e) and e["board"]["W"]["mean"] is not None and e["predictions"]]
        ent = {}
        for arm in ("board", "rail"):
            for model in sorted({m for e in rows for m in e["predictions"]}):
                ds = []
                for e in rows:
                    if e["predictions"].get(model) is None or e[arm]["W"]["mean"] is None:
                        continue
                    pred = e["predictions"][model] * (1.0 if arm == "board" else reg["analysis"]["rail_over_board"])
                    ds.append(e[arm]["W"]["mean"] - pred)
                if ds:
                    ent.setdefault(arm, {})[model] = {"rms_w": math.sqrt(sum(d * d for d in ds) / len(ds)), "mean_w": sum(ds) / len(ds), "n": len(ds)}
        out[g] = ent
    return out


def run_one(runs_csv, json_path, tiles, reg, board_trains="p_raw"):
    runs = load_runs(runs_csv)
    res = json.load(open(json_path))
    set_aside = {x["pass"] for x in res.get("passes_set_aside", [])} | {x["pass"] for x in res.get("passes_config_flags", [])}
    book = Book(runs, tiles, reg["analysis"]["gates"], board_trains=board_trains, set_aside=set_aside)
    R = score(book, tiles, reg, runs)
    ls = lists(book, tiles, reg)
    return {"passes_kept": book.passes, "passes_set_aside_by_e78_gates": res.get("passes_set_aside", []), "passes_set_aside_by_own_gate": book.own_gate,
            "failed_runs": res.get("failed", []), "leak": res.get("leak"), "clock_mhz": res.get("clock_mhz"), "v_mean": res.get("v_mean"),
            "runs": res.get("runs"), "kept": res.get("kept"), "rules": R, "prices": ls, "models": model_rms(ls, reg)}


def tally(R):
    out = {}
    for k, v in R.items():
        out.setdefault(v["verdict"], []).append(k)
    return out


def f(x, nd=3):
    return "—" if x is None else f"{x:.{nd}f}"


def fi(p, nd=0):
    if p["mean"] is None:
        return "—"
    if p["lo"] is None:
        return f"{p['mean']:.{nd}f}"
    return f"{p['mean']:.{nd}f} [{p['lo']:.{nd}f}, {p['hi']:.{nd}f}]"


def write_md(prim, arms, reg, tiles, path):
    L = ["# E102 results (written by score_e102.py)", ""]
    L.append(f"Passes kept: {prim['passes_kept']}. Set aside by E78's gates: {prim['passes_set_aside_by_e78_gates']}. By the trains' own gate: {prim['passes_set_aside_by_own_gate']}. Runs kept {prim['kept']} of {prim['runs']}; clock {prim['clock_mhz']} MHz; {f((prim['v_mean'] or 0) * 1000, 1)} mV; primary leakage slope {prim['leak']}.")
    L += ["", "## Rules", "", "| rule | verdict (primary arm) | arm | registered expectation | board arm | rail arm |", "|---|---|---|---|---|---|"]
    for k, v in prim["rules"].items():
        L.append(f"| {k} | **{v['verdict']}** | {v.get('arm', '')} | {v.get('expected', '')} | {v.get('board_arm', {}).get('verdict', '')} | {v.get('rail_arm', {}).get('verdict', '')} |")
    L += ["", f"Tally: {json.dumps(tally(prim['rules']))}", "", "## Every price", "",
          "| item | block | flips/op | board ΔW over own zero | board fJ per flipped bit [95%] | rail ΔW | rail fJ [95%] | n | bound? (board, rail) | E79, or the published list, or that list over the ratio | bench (map) | e88+flops |", "|---|---|---:|---|---|---|---|---:|---|---:|---:|---:|"]
    for name, e in sorted(prim["prices"].items(), key=lambda kv: (kv[1]["type"], kv[1]["layout"], kv[1]["bit"] if kv[1]["bit"] is not None else 99, kv[0])):
        p = e["predictions_fJ"] or {}
        pv = lambda m: f(p.get(m), 0)
        L.append(f"| {name.split('@')[0]} | {e['block']} | {e['designed_flips_per_op']} | {fi(e['board']['W'], 3)} | {fi(e['board']['fJ'])} | {fi(e['rail']['W'], 3)} | {fi(e['rail']['fJ'])} | {e['board']['W']['n']} | {e['board']['bound']}, {e['rail']['bound']} | {pv('e79_measured') if p.get('e79_measured') is not None else pv('all_in_list') if p.get('all_in_list') is not None else pv('ratio_hypothesis')} | {pv('bench_map')} | {pv('e88_flops_exact')} |")
    L += ["", "## The ratio all-in / balanced, per flipped bit", "", "| list | bit | board ratio [95%] | rail ratio [95%] | pairing |", "|---|---:|---|---|---|"]
    for rid, nm in (("E102-R1", "fp32 B"), ("E102-R2", "fp32 A")):
        for j, c in prim["rules"][rid]["board_arm"]["cells"].items():
            r = prim["rules"][rid]["rail_arm"]["cells"][j]
            L.append(f"| {nm} | {j} | {f(c['ratio'], 2)} [{f(c['lo'], 2)}, {f(c['hi'], 2)}] | {f(r['ratio'], 2)} [{f(r['lo'], 2)}, {f(r['hi'], 2)}] | {'paired' if c['paired'] else 'gate over train'} |")
    L += ["", "## Each frozen model's error over each list, watts", "", "| list | arm | model | rms | mean (measured − predicted) | n |", "|---|---|---|---:|---:|---:|"]
    for g, ent in prim["models"].items():
        for arm, ms in ent.items():
            for m, v in ms.items():
                L.append(f"| {g} | {arm} | {m} | {f(v['rms_w'])} | {f(v['mean_w'])} | {v['n']} |")
    L += ["", "## The arms", "", "| arm | passes kept | rule: verdict |", "|---|---|---|"]
    for name, a in arms.items():
        L.append(f"| {name} | {a['passes_kept']} | " + "; ".join(f"{k.split('-')[1]} {v['verdict']}" for k, v in a["rules"].items()) + " |")
    L += ["", "## int8's B side: bk_ff under each slope, the way E79 reduced it (board p80 in the train, the run's own whole-degree reading)", "", "| arm | ΔW | fJ per flipped bit [95%] | bound? |", "|---|---|---|---|"]
    for name, a in arms.items():
        e = a["prices"].get("int8.bk_ff@I")
        if e:
            L.append(f"| {name} | {fi(e['board']['W'], 3)} | {fi(e['board']['fJ'])} | {e['board']['bound']} |")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="holds e102.json, runs.csv and the arms' files, as collect_e102.sh writes them")
    ap.add_argument("--md", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--reg", default=REG)
    ap.add_argument("--tiles", default=TILES)
    a = ap.parse_args()
    reg = json.load(open(a.reg))
    tiles = json.load(open(a.tiles))["tiles"]
    prim = run_one(os.path.join(a.dir, "runs.csv"), os.path.join(a.dir, "e102.json"), tiles, reg)
    arms = {}
    for name, stem, boardt in (("dips kept", "e102-dipskept", "p_raw"), ("gates off", "e102-gatesoff", "p_raw"),
                               ("E79's way at 0.2414 (p80 in the trains)", "", "p80"), ("E79's way at the session's auto slope", "e102-auto", "p80"),
                               ("E79's way at 0.1994", "e102-leak0.1994", "p80"), ("E79's way at 0.3803", "e102-leak0.3803", "p80"), ("E79's way at 0.545", "e102-leak0.545", "p80"),
                               ("no temperature term in block G either (0)", "e102-leak0", "p80")):
        rc = "runs" + ("-" + stem.split("-", 1)[1] if stem else "") + ".csv"
        js = (stem or "e102") + ".json"
        if os.path.exists(os.path.join(a.dir, rc)) and os.path.exists(os.path.join(a.dir, js)):
            arms[name] = run_one(os.path.join(a.dir, rc), os.path.join(a.dir, js), tiles, reg, board_trains=boardt)
    json.dump({"experiment": "E102", "primary": prim, "arms": arms, "tally": tally(prim["rules"])}, open(a.json, "w"), indent=1)
    write_md(prim, arms, reg, tiles, a.md)
    print(json.dumps({"passes": prim["passes_kept"], "tally": tally(prim["rules"])}))


if __name__ == "__main__":
    main()
