#!/usr/bin/env python3
"""E145 scorer (Q138, kinds page section 11 item 12): E138's B design and E130's A design on aifoundry1 card 1, the MINION RAIL as the
registered primary, A's single bits as the control. It imports E138's registered scorer, tools/claims-v3/e138/score_e138.py, UNCHANGED
(it loads E130's, tools/claims-v3/e130/score_e130.py, UNCHANGED; both sha256 checked against predictions-e145.json first) and uses
their Book (each item's step over its own zero interpolated in time, the train gate on the board's p_raw at 0.25 W, E78's pass
gates), their statistics and their rules. E145's changes, each registered in README.md before any E145 data:

  1. the pass numbers: B 14510-14529, A 14530-14539 (block_of_e145);
  2. the exact t(0.975, n - 1) for n - 1 > 10 (E130's table stops at 10 and approximates beyond, 1.96 + 2.4 / df; E138's C5): the
     table to 30 and a Cornish-Fisher expansion beyond; for n - 1 <= 10 it is E130's table, unchanged;
  3. the A rules, E130's R2-R6 and its per-netlist test, on THIS session's A and B blocks, in board-equivalent fJ (the rail's
     rail_raw / c_rb, c_rb = 0.81 frozen), through score_e130.score unchanged; and the control rule E145-C1.

    python3 tools/claims-v3/e145/score_e145.py --primary <runs.csv>,<reduce json> [--arm name=<csv>,<json>,<value>,<on|off>]...
        [--pool e130=<csv>,<json>] [--pool e138=<csv>,<json>] --md results.md --json scored.json
    python3 tools/claims-v3/e145/score_e145.py --selftest <E130 csv>,<E130 json> <E138 csv>,<E138 json>

The registered rules (README.md "Decision rules", predictions-e145.json > rules), on the primary (rail_raw, board-equivalent fJ):
  E145-R1   B's odd - even against T_B = 30.68 (E138-R1's rule): RECODED / FLAT / INCONCLUSIVE; NOT SCORED under 3 kept B blocks
  E145-R1n  the same interval against the two groups' frozen bands (E138-R1n's)
  E145-R1q  B's odd / even on the rail (no unit) against the two groups' frozen ratio bands (E138-R1q's)
  E145-R2   A's odd - even against T_A = 27.58 (E130-R2's): RECODED / FLAT / INCONCLUSIVE; NOT SCORED under 3 kept A blocks
  E145-R3   A's sign, B = 0x55 minus B = 1, against T_S = 18.07 (E130-R3's): RISES / FLAT / INCONCLUSIVE
  E145-C1   the control: REPRODUCES card 0 (R2 FLAT and R3 RISES, E130's registered primary) / DIFFERS (R2 RECODED or R3 FLAT) /
            INCONCLUSIVE / NOT SCORED
  E145-R4   which multiplier, on card 1 alone: E130-R4's rule on (E145-R1, E145-R2, E145-R3)
  E145-R5, E145-R6   the shared predictions (sign bits, word 2 / word 1), E130-R5/R6's
  E145-N    each netlist's frozen prediction on E130's three separators (E130-N's)
Reported, never a verdict: every arm; the pools with E130's and E138's B blocks (card 0); the card's own rail-per-board scale from
A's bits 0-6 and R1 read at it; the c_rb flip points; card 0's frozen per-bit prices predicting card 1's (flat, parity, per position).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REG = os.path.join(HERE, "predictions-e145.json")
ITEMS = os.path.join(HERE, "e130-items.json")
S138_PATH = os.path.join(ROOT, "tools", "claims-v3", "e138", "score_e138.py")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


S138 = _load("score_e138", S138_PATH)     # loads score_e130 (unchanged) as S138.S
S = S138.S
BLOCK_OF = {"e130": S138._block_of_e130, "e138": S138.block_of_e138}


def block_of_e145(p):                                                                            # E145 change 1
    p = int(p)
    return "B" if 14510 <= p <= 14529 else "A" if 14530 <= p <= 14539 else "S"


BLOCK_OF["e145"] = block_of_e145
S.block_of = block_of_e145

T_EXACT = {11: 2.2010, 12: 2.1788, 13: 2.1604, 14: 2.1448, 15: 2.1314, 16: 2.1199, 17: 2.1098, 18: 2.1009, 19: 2.0930,
           20: 2.0860, 21: 2.0796, 22: 2.0739, 23: 2.0687, 24: 2.0639, 25: 2.0595, 26: 2.0555, 27: 2.0518, 28: 2.0484,
           29: 2.0452, 30: 2.0423}
_t975_e130 = S.t975


def t975_e145(df):                                                                               # E145 change 2
    if df <= 10:
        return _t975_e130(df)
    if df in T_EXACT:
        return T_EXACT[df]
    z = 1.959964
    return z + (z ** 3 + z) / (4 * df) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * df ** 2)


S.t975 = t975_e145


def load_runs(csvp, c_rb):
    rr = S.load_runs(csvp)
    for r in rr:
        r["rail_beq"] = None if r["rail_raw"] is None else r["rail_raw"] / c_rb
    return rr


def make_book(csvp, redp, value, gate, reg, tiles, numbering="e145"):
    S.block_of = BLOCK_OF[numbering]
    try:
        return S.Book(load_runs(csvp, reg["plan"]["c_rb"]), tiles, value, gate, reg["plan"]["train_gate_w"], json.load(open(redp)))
    finally:
        S.block_of = block_of_e145


def control(v2, v3):
    if "NOT SCORED" in (v2, v3):
        return "NOT SCORED"
    if v2 == "FLAT" and v3 == "RISES":
        return "REPRODUCES card 0"
    if v2 == "RECODED" or v3 == "FLAT":
        return "DIFFERS from card 0"
    return "INCONCLUSIVE"


def arm_rules(book_unit, book_beq, reg, scale):
    """All E145 rules on one arm. book_unit: the meter's own fJ (rail fJ or board fJ); book_beq: board-equivalent fJ (rail / c_rb,
    or the board itself); scale: board-equivalent per unit of book_unit."""
    r138 = S138.e138_rules(book_unit, reg, scale)
    sc = S.score(book_beq, reg)
    v = {"E145-R1": r138["verdicts"]["E138-R1"], "E145-R1n": r138["verdicts"]["E138-R1n"], "E145-R1q": r138["verdicts"]["E138-R1q"],
         "E145-R2": sc["verdicts"]["E130-R2"], "E145-R3": sc["verdicts"]["E130-R3"], "E145-R4": sc["verdicts"]["E130-R4"],
         "E145-R5": sc["verdicts"]["E130-R5"], "E145-R6": sc["verdicts"]["E130-R6"]}
    v["E145-C1"] = control(v["E145-R2"], v["E145-R3"])
    v["E145-N"] = {n: e["verdict"] for n, e in sc["netlists"].items()}
    st = sc["statistics"]
    keep = ("mean", "lo", "hi", "n", "se", "ratio")
    return {"verdicts": v, "consistency_E130-R1_equals_E145-R1": sc["verdicts"]["E130-R1"] == v["E145-R1"],
            "B_odd_minus_even_board_equivalent_fJ": r138["B_odd_minus_even_board_equivalent_fJ"],
            "B_odd_minus_even_book_fJ": r138["B_odd_minus_even_book_fJ"], "B_odd_over_even": r138["B_odd_over_even"],
            "per_block_book_fJ": r138["per_block_book_fJ"], "c_rb_flip_points": r138["c_rb_flip_points"],
            "statistics_board_equivalent": {k: {kk: st[k].get(kk) for kk in keep} for k in st},
            "netlists": {n: {"verdict": e["verdict"], "statistics": e["statistics"], "item_counts": e["item_counts"],
                             "rms_fJ": e["rms_fJ"]} for n, e in sc["netlists"].items()},
            "blocks": book_beq.blocks, "set_aside": book_beq.set_aside,
            "prices_unit_fJ": {t: book_unit.price(t) for t in sorted({k[5:] for k in book_unit.steps})},
            "prices_board_equivalent_fJ": sc["prices"],
            "zero_residual_sd_W_unit": S.sd(book_unit.zero_resid), "zero_residual_n": len(book_unit.zero_resid)}


def pooled(books_rail, reg):
    """Reported: B odd - even per block over several sessions' rail books (rail fJ), board-equivalent at c_rb."""
    c = reg["plan"]["c_rb"]
    vals, n = [], {}
    for name, b in books_rail.items():
        s = S.per_block_stat(b, S.combos()["B_odd_minus_even_fJ"])
        vals += list(s.values())
        n[name] = len(s)
    m = S.mean_ci(vals)
    eq = {k: (None if m.get(k) is None else m[k] / c) for k in ("mean", "lo", "hi")}
    eq["n"] = m.get("n")
    T = reg["thresholds"]["T_B"]["value"]
    return {"n": n, "board_equivalent_fJ": eq,
            "R1_reading": S.three_way(eq, T, "RECODED", "FLAT", reg["plan"]["min_kept_blocks"], len(vals))}


def in_session_scale(book_rail, book_board, side):
    """Reported: the card's own rail-per-board level ratio over one side's bits 0-6 (Fieller, paired by block)."""
    key = f"{side}_mean_bits0to6_fJ"
    return S.fieller(S.per_block_stat(book_rail, S.combos()[key]), S.per_block_stat(book_board, S.combos()[key]))


def cross_card(book_rail, reg):
    """Reported (registered before the data): card 1's per-bit prices of bits 0-6 (rail fJ) predicted from card 0's frozen ones
    (predictions-e145.json > card0_prices_rail_fJ: E130's and E138's B blocks pooled, E130's A blocks) under three per-flip models:
    flat (card 0's mean over bits 0-6), parity (card 0's odd-bit mean for 1, 3, 5 and even-bit mean for 0, 2, 4, 6) and per
    position (card 0's own price of that bit); each model's rms error in rail fJ and as a share of card 1's mean."""
    out = {}
    for side in ("B", "A"):
        c0 = reg["card0_prices_rail_fJ"][side]
        ts = [f"{side.lower()}1_{j}" for j in range(7)]
        c1 = {t: book_rail.price(t)["fJ"]["mean"] for t in ts}
        if None in c1.values():
            out[side] = None
            continue
        flat = sum(c0[t] for t in ts) / 7
        odd = sum(c0[t] for t in ts if int(t[-1]) % 2) / 3
        even = sum(c0[t] for t in ts if not int(t[-1]) % 2) / 4
        models = {"flat": {t: flat for t in ts}, "parity": {t: (odd if int(t[-1]) % 2 else even) for t in ts},
                  "per_position": {t: c0[t] for t in ts}}
        m1 = sum(c1.values()) / 7
        rms = {k: math.sqrt(sum((v[t] - c1[t]) ** 2 for t in ts) / 7) for k, v in models.items()}
        out[side] = {"rms_rail_fJ": rms, "share_of_card1_mean": {k: x / m1 for k, x in rms.items()}, "card1_mean_rail_fJ": m1,
                     "card0_mean_rail_fJ": flat, "card1_over_card0_mean": m1 / flat, "card1_rail_fJ": c1, "card0_rail_fJ": c0}
    return out


def fmt(x, nd=1, sign=True):
    if x is None:
        return "-"
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


def markdown(res, reg):
    p = res["primary"]
    arms = res["arms"]
    rules = ["E145-R1", "E145-R1n", "E145-R1q", "E145-R2", "E145-R3", "E145-C1", "E145-R4", "E145-R5", "E145-R6"]
    L = [f"# E145 results (generated by score_e145.py; primary: {reg['plan']['primary']})", "",
         f"Kept blocks (primary): B {p['blocks']['B']}, A {p['blocks']['A']}; set aside: {json.dumps(p['set_aside'])[:500]}", "",
         "| rule | primary (rail) | " + " | ".join(arms) + " |", "|---|---|" + "---|" * len(arms)]
    for r in rules:
        L.append(f"| {r} | **{p['verdicts'][r]}** | " + " | ".join(a["verdicts"][r] for a in arms.values()) + " |")
    for n in reg["netlists"]:
        L.append(f"| E145-N `{n}` | **{p['verdicts']['E145-N'][n]}** | " + " | ".join(a["verdicts"]["E145-N"][n] for a in arms.values()) + " |")
    L += ["", "| reading | n | value | 95% |", "|---|---|---|---|"]
    for name, x in [("primary (rail)", p)] + list(arms.items()):
        e = x["B_odd_minus_even_board_equivalent_fJ"]
        L.append(f"| {name}: B odd - even, board-equivalent fJ | {e['n']} | {fmt(e['mean'])} | [{fmt(e['lo'])}, {fmt(e['hi'])}] |")
        q = x["B_odd_over_even"]
        L.append(f"| {name}: B odd / even | {q.get('n')} | {fmt(q.get('ratio'), 2, False)} | [{fmt(q.get('lo'), 2, False)}, {fmt(q.get('hi'), 2, False)}] |")
        for k in ("A_odd_minus_even_fJ", "A_sign_dense_minus_one_fJ"):
            s = x["statistics_board_equivalent"][k]
            L.append(f"| {name}: {k}, board-equivalent | {s.get('n')} | {fmt(s.get('mean'))} | [{fmt(s.get('lo'))}, {fmt(s.get('hi'))}] |")
    for name, P in res.get("pools", {}).items():
        e = P["board_equivalent_fJ"]
        L.append(f"| pool {name} {json.dumps(P['n'])}, rail, board-equivalent (reported) | {e['n']} | {fmt(e['mean'])} | "
                 f"[{fmt(e['lo'])}, {fmt(e['hi'])}] ({P['R1_reading']}) |")
    rep = res.get("reported", {})
    L += ["", f"T_B = {reg['thresholds']['T_B']['value']:.2f} board fJ; c_rb = {reg['plan']['c_rb']} (frozen); c_rb flip points (primary): "
          f"{json.dumps({k: round(v, 3) for k, v in p['c_rb_flip_points'].items()})}",
          f"Card 1's own rail/board scale (reported): A bits 0-6 {json.dumps(rep.get('scale_A'))}; B bits 0-6 {json.dumps(rep.get('scale_B'))}",
          f"R1 read at the A-based scale (reported): {json.dumps(rep.get('R1_at_A_scale'))}", "",
          "| item | rail fJ (primary) | 95% | board-equivalent fJ | board fJ (board arm) | 95% |", "|---|---|---|---|---|---|"]
    bo = arms.get("board", {}).get("prices_unit_fJ", {})
    for t in reg["item_order"]:
        pr = p["prices_unit_fJ"].get(t)
        if not pr:
            continue
        f = pr["fJ"]
        g = bo.get(t, {}).get("fJ", {})
        L.append(f"| {t} | {fmt(f.get('mean'))} | [{fmt(f.get('lo'))}, {fmt(f.get('hi'))}] | "
                 f"{fmt(None if f.get('mean') is None else f['mean'] / reg['plan']['c_rb'])} | {fmt(g.get('mean'))} | "
                 f"[{fmt(g.get('lo'))}, {fmt(g.get('hi'))}] |")
    cc = res.get("cross_card")
    if cc:
        L += ["", "| card 0's prices predicting card 1's, bits 0-6 (rail fJ, reported) | flat | parity | per position | card 1 / card 0 |",
              "|---|---|---|---|---|"]
        for side, x in cc.items():
            if not x:
                continue
            r, s = x["rms_rail_fJ"], x["share_of_card1_mean"]
            L.append(f"| {side} | {r['flat']:.1f} ({100 * s['flat']:.0f}%) | {r['parity']:.1f} ({100 * s['parity']:.0f}%) | "
                     f"{r['per_position']:.1f} ({100 * s['per_position']:.0f}%) | {x['card1_over_card0_mean']:.3f} |")
    return "\n".join(L) + "\n"


def check_reg(reg):
    h = reg["harness"]
    for rel, want in (("tools/claims-v3/e138/score_e138.py", h["score_e138_sha256"]), ("tools/claims-v3/e130/score_e130.py", h["score_e130_sha256"])):
        have = sha(os.path.join(ROOT, rel))
        if have != want:
            raise SystemExit(f"{rel} sha256 {have} != registered {want}")


def score_session(primary, arm_specs, pools, reg, tiles, numbering="e145"):
    csvp, redp = primary
    c = reg["plan"]["c_rb"]
    rail = make_book(csvp, redp, "rail_raw", True, reg, tiles, numbering)
    beq = make_book(csvp, redp, "rail_beq", True, reg, tiles, numbering)
    board = make_book(csvp, redp, "p_raw", True, reg, tiles, numbering)
    res = {"experiment": "E145", "primary_arm": reg["plan"]["primary"], "primary": arm_rules(rail, beq, reg, 1.0 / c), "arms": {}}
    for name, (cp, rp, value, gate) in arm_specs.items():
        if value.startswith("rail"):
            bu = make_book(cp, rp, "rail_raw", gate, reg, tiles, numbering)
            bq = make_book(cp, rp, "rail_beq", gate, reg, tiles, numbering)
            res["arms"][name] = arm_rules(bu, bq, reg, 1.0 / c)
        else:
            bu = make_book(cp, rp, value, gate, reg, tiles, numbering)
            res["arms"][name] = arm_rules(bu, bu, reg, 1.0)
    rep = {"scale_A": in_session_scale(rail, board, "A"), "scale_B": in_session_scale(rail, board, "B")}
    d = res["primary"]["B_odd_minus_even_book_fJ"]
    cA = rep["scale_A"].get("ratio")
    if cA and d.get("lo") is not None:
        eq = {"mean": d["mean"] / cA, "lo": d["lo"] / cA, "hi": d["hi"] / cA, "c_rb": cA}
        rep["R1_at_A_scale"] = eq | {"reading": S.three_way(eq, reg["thresholds"]["T_B"]["value"], "RECODED", "FLAT",
                                                              reg["plan"]["min_kept_blocks"], len(rail.blocks["B"]))}
    res["reported"] = rep
    pb = {"E145": rail}
    for name, (cp, rp) in pools.items():
        pb[name] = make_book(cp, rp, "rail_raw", True, reg, tiles, name.lower())
    if len(pb) > 1:
        res["pools"] = {"+".join(pb): pooled(pb, reg)}
        if "E138" in pb:
            res["pools"]["E145+E138"] = pooled({"E145": rail, "E138": pb["E138"]}, reg)
        res["pools"]["card 0 alone"] = pooled({k: v for k, v in pb.items() if k != "E145"}, reg)
    res["cross_card"] = cross_card(rail, reg)
    pv = res["primary"]["verdicts"]
    res["arm_sensitive"] = {r: [n for n, x in res["arms"].items() if x["verdicts"].get(r) != pv[r]] for r in pv}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary")
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--pool", action="append", default=[], help="E130=<csv>,<json> or E138=<csv>,<json> (card 0's B blocks)")
    ap.add_argument("--selftest", nargs=2, metavar=("E130", "E138"))
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    check_reg(reg)
    tiles = {"int8." + t["tile"]: t for t in json.load(open(ITEMS))["tiles"]}
    if a.selftest:
        out = {}
        for name, spec, numbering in (("E130", a.selftest[0], "e130"), ("E138", a.selftest[1], "e138")):
            cp, rp = spec.split(",")
            r = score_session((cp, rp), {"board": (cp, rp, "p_raw", True)}, {}, reg, tiles, numbering)
            p = r["primary"]
            out[name] = {"verdicts_rail": p["verdicts"], "B_odd_minus_even_board_equivalent_fJ": p["B_odd_minus_even_board_equivalent_fJ"],
                         "B_odd_minus_even_rail_fJ": p["B_odd_minus_even_book_fJ"], "B_odd_over_even": p["B_odd_over_even"],
                         "A_odd_minus_even_beq": p["statistics_board_equivalent"]["A_odd_minus_even_fJ"],
                         "A_sign_dense_minus_one_beq": p["statistics_board_equivalent"]["A_sign_dense_minus_one_fJ"],
                         "c_rb_flip_points": p["c_rb_flip_points"], "scale_A": r["reported"]["scale_A"],
                         "board_verdicts": r["arms"]["board"]["verdicts"],
                         "board_B_odd_minus_even": r["arms"]["board"]["B_odd_minus_even_board_equivalent_fJ"]}
        print(json.dumps(out, indent=1, default=lambda o: None))
        return 0
    arms = {}
    for spec in a.arm:
        name, rest = spec.split("=", 1)
        parts = rest.split(",")
        arms[name] = (parts[0], parts[1], parts[2], parts[3] == "on")
    pools = {}
    for spec in a.pool:
        name, rest = spec.split("=", 1)
        pools[name] = tuple(rest.split(",")[:2])
    res = score_session(tuple(a.primary.split(",")[:2]), arms, pools, reg, tiles)
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, default=lambda o: None)
    md = markdown(res, reg)
    if a.md:
        open(a.md, "w").write(md)
    pv = res["primary"]["verdicts"]
    for r in sorted(pv):
        print(f"{r}: {pv[r]}" + (f"   (differs in: {', '.join(res['arm_sensitive'][r])})" if res["arm_sensitive"][r] else ""))
    e = res["primary"]["B_odd_minus_even_board_equivalent_fJ"]
    print(f"primary B odd - even {fmt(e['mean'])} [{fmt(e['lo'])}, {fmt(e['hi'])}] board-equivalent fJ, n {e['n']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
