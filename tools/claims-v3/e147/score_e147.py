#!/usr/bin/env python3
"""E147 scorer (Q138): every price, ratio, contrast and registered rule, from the reduction's per-run tables. Standard
library only; written and committed before any E147 block is read. Every threshold and frozen prediction is
predictions-e147.json's; nothing numeric about a rule is written here except what reads them.

    python3 tools/claims-v3/e147/score_e147.py --primary <runs.csv>,<e147.json> [--arm name=<runs.csv>,<e147.json>,<value>,<gate>] ...
        --md results.md --json scored.json

A price is E134's (tools/claims-v3/e134/score_e134.py `Book`, unchanged but for E147's block numbers):
  per run     the primary value is the BOARD's p_raw, the mean board power over [t0+1 s, t0+3 s) with no temperature term.
              Arms: rail_raw, p80, E134's 4 W dip line, dips kept, gates off.
  per block   each item's run minus its OWN zero (e147-tiles.json `zero`) interpolated linearly in time between that zero's
              reads in the block; settling runs (segment -1) never count; divided by (designed flips per op x the run's rate)
              for fJ per flipped bit.
  the train gate  a zero's interior read more than 0.25 W off the straight line through its two neighbouring reads of the
              same zero, on the board's p_raw, sets the block aside; E78's pass gates set a block aside too. Off in the
              gates-off arm only.
  over blocks the mean of the per-block values, t(0.975, n-1) x SE over blocks. A contrast is a per-block combination of
              items, paired inside each block. A ratio is the ratio of the per-block means with its 95% Fieller interval.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e147.json")
TILES = os.path.join(HERE, "e147", "e147-tiles.json")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
A79_BITS = (8, 9, 10, 12, 13, 14, 15, 17, 18, 19, 21, 24, 25, 26, 28, 29)
A67_BITS = (9, 17, 18, 19)
B_BITS = (1, 2, 3, 4, 5, 17, 18, 19, 21, 24, 25, 26, 28, 29)
B_LINK = (16,)


def t975(df):
    return T975.get(df, 1.96 + 2.4 / max(df, 1))


def block_of(p):
    p = int(p)
    return "A" if 14710 <= p <= 14719 else "B" if 14720 <= p <= 14729 else "S"


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
    """One arm: per (item, block) the step over the item's own zero in W and in fJ per flipped bit (E134's, unchanged)."""

    def __init__(self, runs, tiles, value="p_raw", gate=True, gate_w=0.25, red=None):
        self.tiles = tiles
        self.value = value
        self.gate = gate
        self.gate_w = gate_w
        self.set_aside = []
        self.blocks = {"A": [], "B": []}
        self.steps = {}
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
    ser = {t: book.series(t, key) for t in combo}
    keys = set.intersection(*[set(s) for s in ser.values()]) if ser else set()
    return {p: sum(w * ser[t][p] for t, w in combo.items()) for p in sorted(keys)}


def contrasts(reg):
    """Every contrast the rules and the report read, in W, per block (paired)."""
    sb = reg["design"]["balanced_to_allin_flip_scale_B"]          # 4096 / 3968
    sa = reg["design"]["balanced_to_allin_flip_scale_A"]          # 2048 / 1920
    out = {}
    for j in A67_BITS:
        out[f"A_word_allin_{j}"] = {f"a67j_{j}": 1.0, f"aj_{j}": -1.0}
        out[f"A_word_bal_{j}"] = {f"a67p_{j}": 1.0, f"ap_{j}": -1.0}
    for j in A79_BITS:
        out[f"A_swing_{j}"] = {f"aj_{j}": 1.0, f"ap_{j}": -sa}
    for j in B_BITS + B_LINK:
        out[f"B_swing_{j}"] = {f"bj_{j}": 1.0, f"bp_{j}": -sb}
    low = reg["rules"]["E147-R1"]["bits"]                         # R1's pooled contrast: the mean swing over B bits 1-5
    out["B_swing_low_mean"] = {}
    for j in low:
        out["B_swing_low_mean"][f"bj_{j}"] = 1.0 / len(low)
        out["B_swing_low_mean"][f"bp_{j}"] = -sb / len(low)
    return out


def ratios():
    out = {}
    for j in A79_BITS:
        out[f"A_W79_allin_over_bal_{j}"] = (f"aj_{j}", f"ap_{j}")
    for j in A67_BITS:
        out[f"A_W67_allin_over_bal_{j}"] = (f"a67j_{j}", f"a67p_{j}")
        out[f"A_word_allin_ratio_{j}"] = (f"a67j_{j}", f"aj_{j}")
    for j in B_BITS + B_LINK:
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
    """B's low bits carry no swing: FLAT / SWING / INCONCLUSIVE, on the mean swing over bits 1-5 (paired by block), with
    every single bit's swing guarding against one bit's swing hiding in the mean."""
    R = reg["rules"]["E147-R1"]
    if n_kept(book, "B") < reg["plan"]["min_kept_blocks"]:
        return "NOT SCORED", {}
    band = R["none_band_w"]
    rows = {j: st["contrasts_W"][f"B_swing_{j}"] for j in R["bits"]}
    pooled = st["contrasts_W"]["B_swing_low_mean"]
    det = {"pooled": pooled, "bits": rows}
    if pooled["lo"] is None or any(c["lo"] is None for c in rows.values()):
        return "NOT SCORED", det
    if pooled["lo"] > band or any(c["lo"] > band for c in rows.values()):
        return "SWING", det
    if pooled["lo"] >= -band and pooled["hi"] <= band:
        return "FLAT", det
    return "INCONCLUSIVE", det


def rule_inverted(book, st, reg, rule, kind, rname):
    """An exponent's reversal: INVERTED if every ratio's upper bound < 1; NOT INVERTED if any lower bound >= 1."""
    R = reg["rules"][rule]
    if n_kept(book, kind) < reg["plan"]["min_kept_blocks"]:
        return "NOT SCORED", {}
    rows = {j: st["ratios_per_flip"][rname.format(j=j)] for j in R["bits"]}
    if any(r.get("lo") is not None and r["lo"] >= R["threshold"] for r in rows.values()):
        return "NOT INVERTED", rows
    if any(r.get("hi") is None for r in rows.values()):
        return "INCONCLUSIVE (a ratio is unbounded)", rows
    if all(r["hi"] < R["threshold"] for r in rows.values()):
        return "INVERTED", rows
    return "INCONCLUSIVE", rows


def rule_r4(book, st, reg):
    """The bench's word differences above bit 7 (E134-R5's form): AGREES / DISAGREES / INCONCLUSIVE."""
    R = reg["rules"]["E147-R4"]
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


def rule_r5(book, st, reg):
    """E134's digit-class reading above bit 7: HOLDS / FAILS / INCONCLUSIVE."""
    R = reg["rules"]["E147-R5"]
    if n_kept(book, "A") < reg["plan"]["min_kept_blocks"]:
        return "NOT SCORED", {}
    rows, resolved, against = {}, 0, 0
    for j, sgn in R["signed_bits"].items():
        c = st["contrasts_W"][f"A_word_allin_{j}"]
        res = c["lo"] is not None and (c["lo"] > 0 or c["hi"] < 0)
        ok = res and ((c["lo"] > 0) == (sgn > 0))
        resolved += bool(res)
        against += bool(res and not ok)
        rows[j] = {"measured": c.get("mean"), "lo": c.get("lo"), "hi": c.get("hi"), "reading_sign": sgn, "resolved": res}
    c = st["contrasts_W"][f"A_word_allin_{R['same_bit']}"]
    band = R["same_band_w"]
    same_in = c["lo"] is not None and c["lo"] >= -band and c["hi"] <= band
    same_out = c["lo"] is not None and (c["lo"] > band or c["hi"] < -band)
    rows[R["same_bit"]] = {"measured": c.get("mean"), "lo": c.get("lo"), "hi": c.get("hi"), "band_w": band,
                           "inside": same_in, "outside": same_out}
    if against or same_out:
        return "FAILS", rows
    if resolved >= R["min_resolved"] and same_in:
        return "HOLDS", rows
    return "INCONCLUSIVE", rows


def model_errors(book, reg, model, kinds):
    d = []
    for k in kinds:
        pr = reg["items"]["fp32." + k]["pred_W"].get(model)
        m = book.price(k)["W"]["mean"]
        if pr is not None and m is not None:
            d.append((k, m - pr))
    return d


def rule_m1(book, reg):
    """M6's frozen steps at the new positions: HOLDS if its rms <= its own nested fp32 rms on aifoundry3, else FAILS."""
    R = reg["rules"]["E147-M1"]
    if n_kept(book, "A") < reg["plan"]["min_kept_blocks"] or n_kept(book, "B") < reg["plan"]["min_kept_blocks"]:
        return "NOT SCORED", {}
    d = model_errors(book, reg, "m6", reg["lists"]["new_items"])
    if len(d) < R["min_items"]:
        return "NOT SCORED", {"n": len(d)}
    rms = math.sqrt(sum(x * x for _, x in d) / len(d))
    inside = sum(1 for _, x in d if abs(x) <= reg["model_notes"]["m6_row_band_w"])
    det = {"n": len(d), "rms_w": rms, "bias_w": sum(x for _, x in d) / len(d), "line_w": R["rms_line_w"],
           "inside_row_band": inside, "worst": sorted(d, key=lambda kv: -abs(kv[1]))[:8]}
    return ("HOLDS" if rms <= R["rms_line_w"] else "FAILS"), det


def rule_s1(book, reg):
    """The session link: E134's bj_16 and bp_16 against E134's own values (E134-S1's bands)."""
    R = reg["rules"]["E147-S1"]
    if n_kept(book, "B") < reg["plan"]["min_kept_blocks"]:
        return "NOT SCORED", {}
    rows, inside = {}, 0
    for k, ref in R["e134_W"].items():
        p = book.price(k)["W"]
        band = max(R["band_abs_w"], R["band_rel"] * abs(ref["mean"]), R["band_se_mult"] * ref["se"])
        ok = p["mean"] is not None and abs(p["mean"] - ref["mean"]) <= band
        inside += bool(ok)
        rows[k] = {"e134_W": ref["mean"], "e147_W": p["mean"], "ci95": p["ci95"], "band_w": band, "inside": ok}
    return ("PASS" if inside >= R["min_inside"] else "FAIL"), {"inside": inside, "rows": rows}


def e67_check(book, reg):
    """Reported: E67's own four tiles above bit 7 (a67j_9, 17, 18, 19) against E67's list, with E134-S1's bands."""
    R = reg["rules"]["E147-S1"]
    rows = {}
    for j in A67_BITS:
        ref = reg["published"]["e67_allin_W"][str(j)]
        se = reg["published"]["e67_allin_se_W"][str(j)]
        p = book.price(f"a67j_{j}")["W"]
        band = max(R["band_abs_w"], R["band_rel"] * abs(ref), R["band_se_mult"] * se)
        rows[j] = {"e67_W": ref, "e147_W": p["mean"], "band_w": band,
                   "inside": p["mean"] is not None and abs(p["mean"] - ref) <= band}
    return rows


def models_report(book, reg):
    out = {}
    for lname, kinds in reg["lists"].items():
        out[lname] = {}
        for model in reg["models"]:
            d = [x for _, x in model_errors(book, reg, model, kinds)]
            if d:
                out[lname][model] = {"n": len(d), "rms_w": math.sqrt(sum(x * x for x in d) / len(d)),
                                     "bias_w": sum(d) / len(d)}
    return out


def score(runs, red, tiles, reg, value="p_raw", gate=True):
    book = Book(runs, tiles, value=value, gate=gate, gate_w=reg["plan"]["train_gate_w"], red=red)
    st = statistics(book, reg)
    rules = {}
    v, d = rule_r1(book, st, reg)
    rules["E147-R1"] = {"verdict": v, "detail": d}
    v, d = rule_inverted(book, st, reg, "E147-R2", "B", "B_allin_over_bal_{j}")
    rules["E147-R2"] = {"verdict": v, "detail": d}
    v, d = rule_inverted(book, st, reg, "E147-R3", "A", "A_W79_allin_over_bal_{j}")
    rules["E147-R3"] = {"verdict": v, "detail": d}
    v, d = rule_r4(book, st, reg)
    rules["E147-R4"] = {"verdict": v, "detail": d}
    v, d = rule_r5(book, st, reg)
    rules["E147-R5"] = {"verdict": v, "detail": d}
    v, d = rule_m1(book, reg)
    rules["E147-M1"] = {"verdict": v, "detail": d}
    v, d = rule_s1(book, reg)
    rules["E147-S1"] = {"verdict": v, "detail": d}
    prices = {k[5:]: book.price(k[5:]) for k in tiles if tiles[k]["zero"] is not None}
    zr = book.zero_resid
    noise = {"n": len(zr), "rms_w": math.sqrt(sum(x * x for x in zr) / len(zr)) if zr else None}
    return {"blocks": book.blocks, "set_aside": book.set_aside, "rules": rules, "prices": prices, "statistics": st,
            "models": models_report(book, reg), "e67_check": e67_check(book, reg), "zero_scatter": noise}


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
    L = ["# E147 results (generated by score_e147.py; primary = board p_raw, own zeros, dips removed at 2 W, E78's gates and the train gate)", ""]
    L.append(f"Kept blocks: A {p['blocks']['A']}, B {p['blocks']['B']}; set aside: {p['set_aside']}")
    L.append(f"Zero reads' scatter about their neighbours' line: rms {fmt(p['zero_scatter']['rms_w'])} W over {p['zero_scatter']['n']}")
    L.append("")
    L.append("| rule | primary | " + " | ".join(res["arms"].keys()) + " |")
    L.append("|---|---|" + "---|" * len(res["arms"]))
    for r in p["rules"]:
        L.append(f"| {r} | **{p['rules'][r]['verdict']}** | " + " | ".join(a["rules"][r]["verdict"] for a in res["arms"].values()) + " |")
    L.append("")
    it = reg["items"]
    for title, aj, ap_, bits, rn in (("A, word W79 (E79's / E102's / E134's)", "aj", "ap", A79_BITS, "A_W79_allin_over_bal_"),
                                     ("A, word W67 (E67's)", "a67j", "a67p", A67_BITS, "A_W67_allin_over_bal_"),
                                     ("B, E79's eight words", "bj", "bp", B_BITS + B_LINK, "B_allin_over_bal_")):
        L.append(f"## {title}: the per-position table (board; fJ per flipped bit; W over the own zero)")
        L.append("")
        L.append("| bit | all-in fJ | balanced fJ | ratio per flip | all-in W | M6 all-in W | bench all-in W | balanced W | M6 balanced W | bench balanced W |")
        L.append("|---:|---|---|---|---|---:|---:|---|---:|---:|")
        for j in bits:
            a_, b_ = f"{aj}_{j}", f"{ap_}_{j}"
            pa, pb = it["fp32." + a_]["pred_W"], it["fp32." + b_]["pred_W"]
            L.append(f"| {j} | {ci(p['prices'][a_]['fJ'], 0)} | {ci(p['prices'][b_]['fJ'], 0)} | {rci(p['statistics']['ratios_per_flip'][rn + str(j)])} | "
                     f"{ci(p['prices'][a_]['W'])} | {fmt(pa.get('m6'))} | {fmt(pa.get('bench'))} | {ci(p['prices'][b_]['W'])} | {fmt(pb.get('m6'))} | {fmt(pb.get('bench'))} |")
        L.append("")
    L.append("## The word above bit 7: W67 minus W79, board W, paired by block")
    L.append("")
    L.append("| bit | all-in: measured | bench | M6 | digit-class reading | balanced: measured | bench |")
    L.append("|---:|---|---:|---:|---|---|---:|")
    for j in A67_BITS:
        c1 = p["statistics"]["contrasts_W"][f"A_word_allin_{j}"]
        c2 = p["statistics"]["contrasts_W"][f"A_word_bal_{j}"]
        cp = reg["contrasts_pred_W"]
        L.append(f"| {j} | {ci(c1)} | {fmt(cp[f'A_word_allin_{j}']['bench'])} | {fmt(cp[f'A_word_allin_{j}']['m6'])} | "
                 f"{cp[f'A_word_allin_{j}']['reading']} | {ci(c2)} | {fmt(cp[f'A_word_bal_{j}']['bench'])} |")
    L.append("")
    L.append("## The swing (all-in minus balanced scaled to the all-in count), board W")
    L.append("")
    L.append("| side, bit | swing W | count model | bench | M6 | real-sum result bits an op, all-in over balanced |")
    L.append("|---|---|---:|---:|---:|---:|")
    for j in B_BITS + B_LINK:
        c = p["statistics"]["contrasts_W"][f"B_swing_{j}"]
        cp = reg["contrasts_pred_W"][f"B_swing_{j}"]
        L.append(f"| B {j} | {ci(c)} | {fmt(cp.get('count_model'))} | {fmt(cp.get('bench'))} | {fmt(cp.get('m6'))} | {fmt(cp.get('res_bits_allin_minus_bal'), 0)} |")
    for j in A79_BITS:
        c = p["statistics"]["contrasts_W"][f"A_swing_{j}"]
        cp = reg["contrasts_pred_W"][f"A_swing_{j}"]
        L.append(f"| A {j} | {ci(c)} | - | {fmt(cp.get('bench'))} | {fmt(cp.get('m6'))} | {fmt(cp.get('res_bits_allin_minus_bal'), 0)} |")
    L.append("")
    L.append("## Frozen models, rms and bias over each list (board W; reported; E147-M1 is the registered rule)")
    L.append("")
    for lname, mm in p["models"].items():
        L.append(f"- {lname}: " + "; ".join(f"{m} rms {v['rms_w']:.3f} bias {v['bias_w']:+.3f} (n {v['n']})" for m, v in mm.items()))
    L.append("")
    m1 = p["rules"]["E147-M1"]["detail"]
    if m1.get("worst"):
        L.append("M6's largest misses (measured minus M6, W): " + ", ".join(f"`{k}` {x:+.3f}" for k, x in m1["worst"]))
        L.append("")
    L.append("## E147-S1 (the session link) and E67's four tiles above bit 7 (reported)")
    L.append("")
    s1 = p["rules"]["E147-S1"]["detail"]
    for k, row in (s1.get("rows") or {}).items():
        L.append(f"- {k}: E134 {row['e134_W']:.3f} W, E147 {fmt(row['e147_W'])} W (band ±{row['band_w']:.3f}): {'inside' if row['inside'] else 'OUTSIDE'}")
    for j, row in p["e67_check"].items():
        L.append(f"- a67j_{j}: E67 {row['e67_W']:.3f} W, E147 {fmt(row['e147_W'])} W (band ±{row['band_w']:.3f}): {'inside' if row['inside'] else 'OUTSIDE'}")
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
    res = {"experiment": "E147", "primary": score(load_runs(csvp), red, tiles, reg), "arms": {}}
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
