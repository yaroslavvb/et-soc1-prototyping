#!/usr/bin/env python3
"""E130 scorer (Q136): every price, statistic and registered rule, from the reduction's per-run tables. Standard library only;
written and committed before any E130 block is read. The rules, thresholds, bands and the four netlists' frozen predictions
are predictions-e130.json's (copied there from Q136(a)'s predictions.json by make_predictions_e130.py); nothing numeric
about a rule is written here except what reads them.

    python3 tools/claims-v3/e130/score_e130.py --primary <runs.csv>,<e130.json> [--arm name=<runs.csv>,<e130.json>,<value>,<gate>] ...
        --md results.md --json scored.json

A price (README.md, "Analysis"; E102's trains, tools/claims-v3/kinds/score_e102.py `Book`, ported):
  per run     the primary value is the BOARD's p_raw, the mean board power over [t0+1 s, t0+3 s) with no temperature term
              (E102's trains: a whole-degree reading only adds noise to a pair a few hundredths of a degree apart). Arms:
              rail_raw (the minion rail, [t0+2, t0+4)), p80 (E78's temperature term at the reduction's slope), dips kept,
              gates off.
  per block   each item's run minus its OWN zero (e130-items.json `zero`) interpolated linearly in time between that zero's
              reads in the block (each item has one on each side); settling runs (segment -1) never count; the mean over
              the item's runs in the block; divided by (designed flips per op x the run's rate) for fJ per flipped bit.
  the train gate  a zero's interior read more than 0.25 W off the straight line through its two neighbours, on the board's
              p_raw, sets the block aside (E102's gate, on the primary's meter); E78's pass gates (reduce_e78.py:
              passes_set_aside, passes_config_flags) set a block aside too. Off in the gates-off arm only.
  over blocks the mean of the per-block values, its SE from the between-block scatter, t(0.975, n-1) x SE. The block is the
              unit of replication. A statistic is a per-block combination of items, paired inside each block. A ratio is
              the ratio of the per-block means with its 95% Fieller interval, paired by block.
"""
import argparse
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "predictions-e130.json")
ITEMS = os.path.join(HERE, "e130-items.json")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def t975(df):
    return T975.get(df, 1.96 + 2.4 / max(df, 1))


def block_of(p):
    p = int(p)
    return "B" if 13010 <= p <= 13019 else "A" if 13020 <= p <= 13029 else "S"


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
    """The ratio of two per-block means with its 95% Fieller interval, paired by block (xs, ys: {block: value}, same keys).
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
        self.tiles = tiles                     # name -> tile entry (e130-items.json, keyed "int8.<tile>")
        self.value = value
        self.gate = gate
        self.gate_w = gate_w
        self.set_aside = []                    # {"pass", "why"}
        self.blocks = {"B": [], "A": []}
        self.steps = {}                        # item -> {"W": {pass: W}, "fJ": {pass: fJ}}
        self.zero_resid = []                   # interior zero reads minus the line through their neighbours (W, the value)
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
                t = self.tiles[r["item"]]
                if t["zero"] is None and r["segment"] != -1:
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
                zr = zeros.get("int8." + t["zero"])
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

    def series(self, tile, key="fJ"):
        return dict(self.steps.get("int8." + tile, {}).get(key, {}))

    def price(self, tile):
        return {"W": mean_ci(self.series(tile, "W").values()), "fJ": mean_ci(self.series(tile, "fJ").values())}


def per_block_stat(book, combo):
    """combo: {tile: weight}. Per block: sum of weight x fJ, for blocks holding every tile of combo."""
    ser = {t: book.series(t) for t in combo}
    keys = set.intersection(*[set(s) for s in ser.values()]) if ser else set()
    return {p: sum(w * ser[t][p] for t, w in combo.items()) for p in sorted(keys)}


ODD_B, EVEN_B = ("b1_1", "b1_3", "b1_5"), ("b1_0", "b1_2", "b1_4")
ODD_A, EVEN_A = ("a1_1", "a1_3", "a1_5"), ("a1_0", "a1_2", "a1_4")


def combos():
    def mean_of(ts, w=1.0):
        return {t: w / len(ts) for t in ts}

    def diff(p, m):
        d = dict(p)
        for t, w in m.items():
            d[t] = d.get(t, 0.0) - w
        return d
    return {
        "B_odd_minus_even_fJ": diff(mean_of(ODD_B), mean_of(EVEN_B)),
        "A_odd_minus_even_fJ": diff(mean_of(ODD_A), mean_of(EVEN_A)),
        "A_sign_dense_minus_one_fJ": {"a1d_7": 1.0, "a1_7": -1.0},
        "B_sign_dense_minus_one_fJ": {"b1d_7": 1.0, "b1_7": -1.0},
        "B_mean_bits0to6_fJ": mean_of([f"b1_{j}" for j in range(7)]),
        "A_mean_bits0to6_fJ": mean_of([f"a1_{j}" for j in range(7)]),
        "B_sign_w2_minus_w1_fJ": {"b2_7": 1.0, "b1_7": -1.0},
        "A_sign_w2_minus_w1_fJ": {"a2_7": 1.0, "a1_7": -1.0},
    }


RATIOS = {   # numerator combo, denominator combo
    "B_odd_over_even": ({t: 1 / 3 for t in ODD_B}, {t: 1 / 3 for t in EVEN_B}),
    "A_odd_over_even": ({t: 1 / 3 for t in ODD_A}, {t: 1 / 3 for t in EVEN_A}),
    "B_sign_w2_over_w1": ({"b2_7": 1.0}, {"b1_7": 1.0}),
    "A_sign_w2_over_w1": ({"a2_7": 1.0}, {"a1_7": 1.0}),
    "B_sign_dense_over_one": ({"b1d_7": 1.0}, {"b1_7": 1.0}),
    "A_sign_dense_over_one": ({"a1d_7": 1.0}, {"a1_7": 1.0}),
}


def statistics(book):
    out = {}
    for name, c in combos().items():
        s = per_block_stat(book, c)
        out[name] = mean_ci(s.values()) | {"per_block": s}
    for name, (num_, den) in RATIOS.items():
        out[name] = fieller(per_block_stat(book, num_), per_block_stat(book, den))
    return out


def three_way(st, thr, hi_word, lo_word, min_n, n_blocks):
    if n_blocks < min_n or st.get("lo") is None:
        return "NOT SCORED"
    if st["lo"] >= thr:
        return hi_word
    if st["hi"] <= thr:
        return lo_word
    return "INCONCLUSIVE"


def overlap(lo, hi, blo, bhi):
    if lo is None or hi is None:
        return None
    if hi < blo:
        return "BELOW"
    if lo > bhi:
        return "ABOVE"
    return "CONSISTENT"


def score(book, reg):
    R = reg["rules"]
    th = reg["thresholds"]
    mn = reg["plan"]["min_kept_blocks"]
    nB, nA = len(book.blocks["B"]), len(book.blocks["A"])
    st = statistics(book)
    v = {}
    v["E130-R1"] = three_way(st["B_odd_minus_even_fJ"], th["T_B"]["value"], "RECODED", "FLAT", mn, nB)
    v["E130-R2"] = three_way(st["A_odd_minus_even_fJ"], th["T_A"]["value"], "RECODED", "FLAT", mn, nA)
    v["E130-R3"] = three_way(st["A_sign_dense_minus_one_fJ"], th["T_S"]["value"], "RISES", "FLAT", mn, nA)
    expect = R["E130-R4"]["groups"]
    if "NOT SCORED" in (v["E130-R1"], v["E130-R2"]):
        v["E130-R4"] = "NOT SCORED"
        remaining = []
    else:
        remaining = [g for g, e in expect.items()
                     if all(v[r] in ("INCONCLUSIVE", "NOT SCORED") or v[r] == e[r] for r in ("E130-R1", "E130-R2", "E130-R3"))]
        decided = sum(1 for r in ("E130-R1", "E130-R2", "E130-R3") if v[r] not in ("INCONCLUSIVE", "NOT SCORED"))
        if not remaining:
            v["E130-R4"] = "NONE OF THE FOUR"
        elif len(remaining) == 1:
            v["E130-R4"] = R["E130-R4"]["names"][remaining[0]] + ("" if decided == 3 else f" ({decided} of 3 rules decided)")
        else:
            v["E130-R4"] = "INCONCLUSIVE between " + " / ".join(R["E130-R4"]["names"][g] for g in remaining)
    for rule, key, n in (("E130-R5", "A_sign_w2_over_w1", nA), ("E130-R6", "B_sign_w2_over_w1", nB)):
        f = st[key]
        b = reg["shared_bands"][key]
        if n < mn or f.get("lo") is None:
            v[rule] = "NOT SCORED"
        else:
            o = overlap(f["lo"], f["hi"], b["lo"], b["hi"])
            v[rule] = "HOLDS" if o == "CONSISTENT" else "FAILS (" + o + ")"
    # per netlist: each separating statistic against the netlist's frozen band (both merges, k +- 2 s.e.)
    nets = {}
    for net, P in reg["netlists"].items():
        e = {"group": P["group"], "statistics": {}, "items": {}}
        for key, band in P["bands"].items():
            s = st.get(key, {})
            lo, hi = (s.get("lo"), s.get("hi"))
            e["statistics"][key] = {"band": band, "card": {k: s.get(k) for k in ("mean", "ratio", "lo", "hi", "n")},
                                    "verdict": overlap(lo, hi, band["lo"], band["hi"]) if (n_ok(key, nA, nB, mn)) else "NOT SCORED"}
        seps = reg["separators"]
        sv = [e["statistics"][k]["verdict"] for k in seps]
        if "NOT SCORED" in sv or None in sv:
            e["verdict"] = "NOT SCORED" if "NOT SCORED" in sv else "UNBOUNDED"
        else:
            out_ = [k for k in seps if e["statistics"][k]["verdict"] != "CONSISTENT"]
            e["verdict"] = "SURVIVES" if not out_ else "EXCLUDED by " + ", ".join(out_)
        cnt = {"CONSISTENT": 0, "ABOVE": 0, "BELOW": 0, None: 0}
        sq = {"map": [], "hier": []}
        for tile, pr in P["items"].items():
            c = book.price(tile)["fJ"]
            o = overlap(c["lo"], c["hi"], pr["band_lo"], pr["band_hi"])
            e["items"][tile] = {"card_fJ": c["mean"], "card_lo": c["lo"], "card_hi": c["hi"], "n": c["n"],
                                "fJ_map": pr["fJ_map"], "fJ_hier": pr["fJ_hier"], "band": [pr["band_lo"], pr["band_hi"]], "verdict": o}
            cnt[o] = cnt.get(o, 0) + 1
            if c["mean"] is not None:
                sq["map"].append((c["mean"] - pr["fJ_map"]) ** 2)
                sq["hier"].append((c["mean"] - pr["fJ_hier"]) ** 2)
        e["item_counts"] = {str(k): n for k, n in cnt.items() if n}
        e["rms_fJ"] = {m: (math.sqrt(sum(x) / len(x)) if x else None) for m, x in sq.items()}
        for side, tiles in (("B", [f"b1_{j}" for j in range(8)]), ("A", [f"a1_{j}" for j in range(8)])):
            card = [book.price(t)["fJ"]["mean"] for t in tiles]
            if None not in card:
                e[f"spearman_{side}_list_map"] = spearman(card, [P["items"][t]["fJ_map"] for t in tiles])
        nets[net] = e
    return {"verdicts": v, "statistics": st, "netlists": nets, "blocks": book.blocks, "set_aside": book.set_aside,
            "n_blocks": {"B": nB, "A": nA},
            "prices": {t: book.price(t) for t in sorted({k[5:] for k in book.steps})},
            "zero_residual_sd_W": sd(book.zero_resid), "zero_residual_n": len(book.zero_resid)}


def n_ok(key, nA, nB, mn):
    return (nA if key.startswith("A_") else nB) >= mn


def sd(v):
    if len(v) < 2:
        return None
    m = sum(v) / len(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def spearman(x, y):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    c = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    d = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return c / d if d else None


def fmt(x, nd=1):
    return "-" if x is None else f"{x:+.{nd}f}" if isinstance(x, float) else str(x)


def ci(s, nd=1, ratio=False):
    if not s:
        return "-"
    m = s.get("ratio") if ratio else s.get("mean")
    if m is None:
        return "-"
    if s.get("lo") is None:
        return f"{m:.{nd}f} (unbounded)" if ratio else f"{m:+.{nd}f}"
    return (f"{m:.{nd + 1}f} [{s['lo']:.{nd + 1}f}, {s['hi']:.{nd + 1}f}]" if ratio
            else f"{m:+.{nd}f} [{s['lo']:+.{nd}f}, {s['hi']:+.{nd}f}]")


def markdown(res, reg):
    P = res["primary"]
    L = ["# E130 results (generated by score_e130.py; README.md is the reading)", "",
         f"Blocks kept (primary): B {P['blocks']['B']}, A {P['blocks']['A']}; set aside: {P['set_aside'] or 'none'}.",
         f"Zero reads' scatter about their neighbours' line (primary value): sd {fmt(P['zero_residual_sd_W'], 4)} W over "
         f"{P['zero_residual_n']} interior reads.", "", "## Registered verdicts (primary, then each arm)", "",
         "| rule | primary | " + " | ".join(res["arms"]) + " |", "|---|---|" + "---|" * len(res["arms"])]
    for r in sorted(P["verdicts"]):
        L.append(f"| {r} | **{P['verdicts'][r]}** | " + " | ".join(res["arms"][a]["verdicts"].get(r, "-") for a in res["arms"]) + " |")
    L += ["", "## Statistics (fJ per flipped bit, board; 95% over blocks)", "",
          "| statistic | card | " + " | ".join(reg["netlists"]) + " (`nets_map`; `nets_hier`) |", "|---|---|" + "---|" * len(reg["netlists"])]
    for key in list(combos()) + list(RATIOS):
        s = P["statistics"][key]
        row = f"| `{key}` | {ci(s, 1, key in RATIOS)} | "
        cells = []
        for net, N in reg["netlists"].items():
            pm, ph = N["stats"]["map"].get(key.replace("_fJ", "_fJ")), N["stats"]["hier"].get(key)
            cells.append(f"{pm:.2f}; {ph:.2f}" if isinstance(pm, (int, float)) and isinstance(ph, (int, float)) else "-")
        L.append(row + " | ".join(cells) + " |")
    L += ["", "## Each netlist's frozen prediction, scored", "", "| netlist | group | separators | items CONSISTENT / ABOVE / BELOW | rms fJ map; hier | Spearman B list; A list (map) |", "|---|---|---|---|---|---|"]
    for net, e in P["netlists"].items():
        c = e["item_counts"]
        L.append(f"| `{net}` | {e['group']} | **{e['verdict']}** | {c.get('CONSISTENT', 0)} / {c.get('ABOVE', 0)} / {c.get('BELOW', 0)} | "
                 f"{fmt(e['rms_fJ']['map'])}; {fmt(e['rms_fJ']['hier'])} | {fmt(e.get('spearman_B_list_map'), 2)}; {fmt(e.get('spearman_A_list_map'), 2)} |")
    L += ["", "| netlist | statistic | band (frozen) | card | verdict |", "|---|---|---|---|---|"]
    for net, e in P["netlists"].items():
        for key, s in e["statistics"].items():
            b = s["band"]
            m = s["card"].get("mean") if s["card"].get("mean") is not None else s["card"].get("ratio")
            L.append(f"| `{net}` | `{key}` | [{b['lo']:.2f}, {b['hi']:.2f}] | {fmt(m, 2)} [{fmt(s['card'].get('lo'), 2)}, {fmt(s['card'].get('hi'), 2)}] | {s['verdict']} |")
    L += ["", "## Every item (fJ per flipped bit, board, primary; W of step)", "",
          "| tile | blocks | card fJ [95%] | step W | " + " | ".join(f"`{n}` map; hier" for n in reg["netlists"]) + " |",
          "|---|---|---|---|" + "---|" * len(reg["netlists"])]
    for tile in reg["item_order"]:
        pr = P["prices"].get(tile)
        if not pr:
            L.append(f"| `{tile}` | 0 | - | - |" + " - |" * len(reg["netlists"]))
            continue
        cells = [f"{reg['netlists'][n]['items'][tile]['fJ_map']:.1f}; {reg['netlists'][n]['items'][tile]['fJ_hier']:.1f}" for n in reg["netlists"]]
        L.append(f"| `{tile}` | {pr['fJ']['n']} | {ci(pr['fJ'])} | {ci(pr['W'], 3)} | " + " | ".join(cells) + " |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", required=True, help="<runs.csv>,<reduce json>")
    ap.add_argument("--arm", action="append", default=[], help="name=<runs.csv>,<reduce json>,<value>,<gate on|off>")
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    tiles = {"int8." + t["tile"]: t for t in json.load(open(ITEMS))["tiles"]}
    csvp, redp = a.primary.split(",")[:2]
    prim = Book(load_runs(csvp), tiles, "p_raw", True, reg["plan"]["train_gate_w"], json.load(open(redp)))
    res = {"experiment": "E130", "primary_arm": reg["plan"]["primary"], "primary": score(prim, reg), "arms": {}}
    for spec in a.arm:
        name, rest = spec.split("=", 1)
        parts = rest.split(",")
        book = Book(load_runs(parts[0]), tiles, parts[2], parts[3] == "on", reg["plan"]["train_gate_w"], json.load(open(parts[1])))
        res["arms"][name] = score(book, reg)
    pv = res["primary"]["verdicts"]
    res["arm_sensitive"] = {r: [n for n, x in res["arms"].items() if x["verdicts"].get(r) != pv[r]] for r in pv}
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, default=lambda o: None)
    md = markdown(res, reg)
    if a.md:
        open(a.md, "w").write(md)
    print("\n".join(f"{r}: {pv[r]}" + (f"   (differs in: {', '.join(res['arm_sensitive'][r])})" if res["arm_sensitive"][r] else "")
                    for r in sorted(pv)))


if __name__ == "__main__":
    main()
