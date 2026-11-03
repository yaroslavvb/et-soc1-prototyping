#!/usr/bin/env python3
"""E151 scorer (Q139, kinds page section 11 item 12, critic rank 11): E145's design (E138's B blocks, E130's A blocks as the control) on
aifoundry3 card 0, the MINION RAIL as the registered primary with E151's rail filter. It loads E145's registered scorer,
tools/claims-v3/e145/score_e145.py, UNCHANGED (which loads E138's and E130's, unchanged; all three sha256 checked against
predictions-e151.json first) and uses their Book (each item's step over its own zero interpolated in time, the train gate on the board's
p_raw at 0.25 W, E78's pass gates), their statistics (E145's exact t beyond n - 1 = 10), their rules and their reported quantities.
E151's changes, each registered in README.md before any E151 data:

  1. the pass numbers: B 15110-15129, A 15130-15139 (block_of_e151), added to E145's numbering table;
  2. the rule names E151-*, E145's rules on this session (E145-C1's words say "card 0" for E130's registered A side: on aifoundry3 that
     is this card, so E151-C1 reads REPRODUCES E130 / DIFFERS from E130);
  3. E151-R4, the registered "which multiplier": E138-R4's rule on E151-R1 (BOOTH ON B if RECODED, NO BOOTH if FLAT, else INCONCLUSIVE
     between the two), with this card's A side as E130 registered it (R2 FLAT, R3 RISES; E138 used the same). E145-R4's form (E130-R4 on
     this session's own R1, R2, R3) is kept as E151-R4s, NOT SCORED unless three A blocks are kept;
  4. reported, registered here: the pools (card 0's three sessions E130 + E138 + E151; E151 + E138; two cards, E151 + E145 under E151's
     rail filter); card 0's earlier per-bit rail prices (E130's and E138's, frozen in predictions-e151.json > card0_prices_rail_fJ, the
     prices E145 was scored against) predicting this session's; card 1's per-bit prices under E151's filter (frozen,
     card1_prices_rail_fJ_filtered) predicting this session's; and what the rail filter moved (the primary against the filter-off arm).

    python3 tools/claims-v3/e151/score_e151.py --primary <runs.csv>,<reduce json> [--arm name=<csv>,<json>,<value>,<on|off>]...
        [--pool E130=<csv>,<json>] [--pool E138=<csv>,<json>] [--pool E145f=<csv>,<json>] --md results.md --json scored.json
    python3 tools/claims-v3/e151/score_e151.py --selftest NAME=<csv>,<json>,<numbering> ...

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REG = os.path.join(HERE, "predictions-e151.json")
ITEMS = os.path.join(HERE, "e130-items.json")
S145_PATH = os.path.join(ROOT, "tools", "claims-v3", "e145", "score_e145.py")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


S145 = _load("score_e145", S145_PATH)      # loads score_e138 and score_e130, unchanged
S = S145.S


def block_of_e151(p):                                                                           # E151 change 1
    p = int(p)
    return "B" if 15110 <= p <= 15129 else "A" if 15130 <= p <= 15139 else "S"


S145.BLOCK_OF["e151"] = block_of_e151
RULES = ("R1", "R1n", "R1q", "R2", "R3", "C1", "R4", "R4s", "R5", "R6")
R4_FROM_R1 = {"RECODED": "BOOTH ON B", "FLAT": "NO BOOTH", "INCONCLUSIVE": "INCONCLUSIVE between BOOTH ON B / NO BOOTH"}


def arm_rules(book_unit, book_beq, reg, scale):
    """E145's arm_rules (unchanged) with E151's names (changes 2 and 3)."""
    a = S145.arm_rules(book_unit, book_beq, reg, scale)
    v = a["verdicts"]
    w = {"E151-R1": v["E145-R1"], "E151-R1n": v["E145-R1n"], "E151-R1q": v["E145-R1q"], "E151-R2": v["E145-R2"],
         "E151-R3": v["E145-R3"], "E151-R4s": v["E145-R4"], "E151-R5": v["E145-R5"], "E151-R6": v["E145-R6"],
         "E151-N": v["E145-N"]}
    w["E151-C1"] = v["E145-C1"].replace("card 0", "E130")
    w["E151-R4"] = R4_FROM_R1.get(v["E145-R1"], "NOT SCORED")
    a["verdicts"] = w
    a["consistency_E130-R1_equals_E151-R1"] = a.pop("consistency_E130-R1_equals_E145-R1")
    return a


def check_reg(reg):
    h = reg["harness"]
    for rel, want in (("tools/claims-v3/e145/score_e145.py", h["score_e145_sha256"]),
                      ("tools/claims-v3/e138/score_e138.py", h["score_e138_sha256"]),
                      ("tools/claims-v3/e130/score_e130.py", h["score_e130_sha256"])):
        have = sha(os.path.join(ROOT, rel))
        if have != want:
            raise SystemExit(f"{rel} sha256 {have} != registered {want}")


def cross(book_rail, reg, key):
    """E145's cross_card (unchanged) with another frozen price list in the card-0 slot."""
    r2 = copy.deepcopy(reg)
    r2["card0_prices_rail_fJ"] = reg[key]
    return S145.cross_card(book_rail, r2)


def score_session(primary, arm_specs, pools, reg, tiles, numbering="e151"):
    csvp, redp = primary
    c = reg["plan"]["c_rb"]
    rail = S145.make_book(csvp, redp, "rail_raw", True, reg, tiles, numbering)
    beq = S145.make_book(csvp, redp, "rail_beq", True, reg, tiles, numbering)
    board = S145.make_book(csvp, redp, "p_raw", True, reg, tiles, numbering)
    res = {"experiment": "E151", "primary_arm": reg["plan"]["primary"], "primary": arm_rules(rail, beq, reg, 1.0 / c), "arms": {}}
    for name, (cp, rp, value, gate) in arm_specs.items():
        if value.startswith("rail"):
            bu = S145.make_book(cp, rp, "rail_raw", gate, reg, tiles, numbering)
            bq = S145.make_book(cp, rp, "rail_beq", gate, reg, tiles, numbering)
            res["arms"][name] = arm_rules(bu, bq, reg, 1.0 / c)
        else:
            bu = S145.make_book(cp, rp, value, gate, reg, tiles, numbering)
            res["arms"][name] = arm_rules(bu, bu, reg, 1.0)
    rep = {"scale_A": S145.in_session_scale(rail, board, "A"), "scale_B": S145.in_session_scale(rail, board, "B")}
    d = res["primary"]["B_odd_minus_even_book_fJ"]
    cA = rep["scale_A"].get("ratio")
    if cA and d.get("lo") is not None:
        eq = {"mean": d["mean"] / cA, "lo": d["lo"] / cA, "hi": d["hi"] / cA, "c_rb": cA}
        rep["R1_at_A_scale"] = eq | {"reading": S.three_way(eq, reg["thresholds"]["T_B"]["value"], "RECODED", "FLAT",
                                                              reg["plan"]["min_kept_blocks"], len(rail.blocks["B"]))}
    if "rail_filter_off" in res["arms"]:
        off = res["arms"]["rail_filter_off"]["B_odd_minus_even_board_equivalent_fJ"]
        on = res["primary"]["B_odd_minus_even_board_equivalent_fJ"]
        rep["rail_filter_moved"] = {"primary": on, "filter_off": off,
                                    "mean_shift_board_equivalent_fJ": None if None in (on.get("mean"), off.get("mean")) else on["mean"] - off["mean"]}
    try:
        rep["samples_removed"] = json.load(open(redp)).get("reducer", {}).get("samples_removed")
    except (OSError, ValueError):
        pass
    res["reported"] = rep
    pb = {"E151": rail}
    for name, (cp, rp) in pools.items():
        num = {"E130": "e130", "E138": "e138", "E145f": "e145"}[name]
        pb[name] = S145.make_book(cp, rp, "rail_raw", True, reg, tiles, num)
    P = {}
    if "E130" in pb and "E138" in pb:
        P["card 0: E130+E138+E151"] = S145.pooled({k: pb[k] for k in ("E151", "E130", "E138")}, reg)
        P["card 0 before today: E130+E138"] = S145.pooled({k: pb[k] for k in ("E130", "E138")}, reg)
    if "E138" in pb:
        P["E151+E138"] = S145.pooled({k: pb[k] for k in ("E151", "E138")}, reg)
    if "E145f" in pb:
        P["two cards: E151+E145 (E151's filter)"] = S145.pooled({k: pb[k] for k in ("E151", "E145f")}, reg)
    if len(pb) == 4:
        P["all four sessions"] = S145.pooled(pb, reg)
    res["pools"] = P
    res["cross_session_card0"] = S145.cross_card(rail, reg)
    res["cross_card_from_card1_filtered"] = cross(rail, reg, "card1_prices_rail_fJ_filtered")
    pv = res["primary"]["verdicts"]
    res["arm_sensitive"] = {r: [n for n, x in res["arms"].items() if x["verdicts"].get(r) != pv[r]] for r in pv}
    return res


def fmt(x, nd=1, sign=True):
    if x is None:
        return "-"
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


def markdown(res, reg):
    p = res["primary"]
    arms = res["arms"]
    L = [f"# E151 results (generated by score_e151.py; primary: {reg['plan']['primary']})", "",
         f"Kept blocks (primary): B {p['blocks']['B']}, A {p['blocks']['A']}; set aside: {json.dumps(p['set_aside'])[:500]}", "",
         "| rule | primary (rail, filtered) | " + " | ".join(arms) + " |", "|---|---|" + "---|" * len(arms)]
    for r in RULES:
        k = "E151-" + r
        L.append(f"| {k} | **{p['verdicts'][k]}** | " + " | ".join(a["verdicts"][k] for a in arms.values()) + " |")
    for n in reg["netlists"]:
        L.append(f"| E151-N `{n}` | **{p['verdicts']['E151-N'][n]}** | " + " | ".join(a["verdicts"]["E151-N"][n] for a in arms.values()) + " |")
    L += ["", "| reading | n | value | 95% |", "|---|---|---|---|"]
    for name, x in [("primary (rail, filtered)", p)] + list(arms.items()):
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
    pb = p["per_block_book_fJ"] or {}
    L += ["", "Per-block B odd - even, rail fJ (primary): " + ", ".join(f"{k} {v:+.1f}" for k, v in sorted(pb.items())),
          "", f"T_B = {reg['thresholds']['T_B']['value']:.2f} board fJ; c_rb = {reg['plan']['c_rb']} (frozen); c_rb flip points (primary): "
          f"{json.dumps({k: round(v, 3) for k, v in p['c_rb_flip_points'].items()})}",
          f"This card's own rail/board scale (reported): A bits 0-6 {json.dumps(rep.get('scale_A'))}; B bits 0-6 {json.dumps(rep.get('scale_B'))}",
          f"R1 read at the A-based scale (reported): {json.dumps(rep.get('R1_at_A_scale'))}",
          f"What the rail filter moved (reported): {json.dumps(rep.get('rail_filter_moved'))}", "",
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
    for title, cc in (("card 0's earlier sessions (E130, E138) predicting today's, bits 0-6 (rail fJ, reported)", res.get("cross_session_card0")),
                      ("card 1's prices under E151's filter (E145) predicting today's, bits 0-6 (rail fJ, reported)", res.get("cross_card_from_card1_filtered"))):
        if not cc:
            continue
        L += ["", f"| {title} | flat | parity | per position | today / predictor mean |", "|---|---|---|---|---|"]
        for side, x in cc.items():
            if not x:
                continue
            r, s = x["rms_rail_fJ"], x["share_of_card1_mean"]
            L.append(f"| {side} | {r['flat']:.1f} ({100 * s['flat']:.0f}%) | {r['parity']:.1f} ({100 * s['parity']:.0f}%) | "
                     f"{r['per_position']:.1f} ({100 * s['per_position']:.0f}%) | {x['card1_over_card0_mean']:.3f} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary")
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--pool", action="append", default=[], help="E130=<csv>,<json>, E138=<csv>,<json>, E145f=<csv>,<json>")
    ap.add_argument("--selftest", nargs="+", metavar="NAME=CSV,JSON,NUMBERING")
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    check_reg(reg)
    tiles = {"int8." + t["tile"]: t for t in json.load(open(ITEMS))["tiles"]}
    if a.selftest:
        out = {}
        for spec in a.selftest:
            name, rest = spec.split("=", 1)
            cp, rp, num = rest.split(",")
            r = score_session((cp, rp), {"board": (cp, rp, "p_raw", True)}, {}, reg, tiles, num)
            p = r["primary"]
            out[name] = {"verdicts_rail": p["verdicts"], "B_odd_minus_even_board_equivalent_fJ": p["B_odd_minus_even_board_equivalent_fJ"],
                         "B_odd_minus_even_rail_fJ": p["B_odd_minus_even_book_fJ"], "B_odd_over_even": p["B_odd_over_even"],
                         "A_odd_minus_even_beq": p["statistics_board_equivalent"]["A_odd_minus_even_fJ"],
                         "A_sign_dense_minus_one_beq": p["statistics_board_equivalent"]["A_sign_dense_minus_one_fJ"],
                         "blocks": p["blocks"], "c_rb_flip_points": p["c_rb_flip_points"], "scale_A": r["reported"]["scale_A"],
                         "prices_rail_fJ_bits0to6": {f"b1_{j}": (p["prices_unit_fJ"].get(f"b1_{j}") or {}).get("fJ", {}).get("mean") for j in range(7)}
                         | {f"a1_{j}": (p["prices_unit_fJ"].get(f"a1_{j}") or {}).get("fJ", {}).get("mean") for j in range(7)},
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
