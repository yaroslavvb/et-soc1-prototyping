#!/usr/bin/env python3
"""E138 scorer (Q137, kinds page section 11 item 12): E130's B list again on aifoundry3 card 0, with the MINION RAIL as the
registered primary. It imports E130's registered scorer, tools/claims-v3/e130/score_e130.py, UNCHANGED (its sha256 is checked
against predictions-e138.json first) and uses its Book (each item's step over its own zero interpolated in time, the train gate
on the board's p_raw at 0.25 W, E78's pass gates), its statistics (B's odd (1, 3, 5) minus even (0, 2, 4) bits, the Fieller
ratio odd / even) and its three-way rule; only the pass numbers (E138's B blocks are 13810-13819) and the meter differ.

    python3 tools/claims-v3/e138/score_e138.py --primary <runs.csv>,<reduce json> [--arm name=<csv>,<json>,<value>,<on|off>]...
        [--pool-e130 <E130 runs.csv>,<E130 reduce json>] --md results.md --json scored.json
    python3 tools/claims-v3/e138/score_e138.py --selftest-e130 <E130 runs.csv>,<E130 reduce json>

The registered rules (README.md, predictions-e138.json > rules), on the primary (rail_raw, board-equivalent fJ = rail fJ / c_rb,
c_rb = 0.81 frozen, E78's `reduce_e78.py --c-rb`):
  E138-R1   B's odd - even against T_B = 30.68 (E130's): RECODED / FLAT / INCONCLUSIVE; NOT SCORED under 3 kept blocks
  E138-R1n  the same interval against the two groups' frozen bands: IN BOOTH ON B's BAND / IN NO RECODER's BAND /
            NEITHER (BETWEEN | ABOVE | BELOW) / INCONCLUSIVE (touches both)
  E138-R1q  B's odd / even on the rail (no unit, no c_rb) against the two groups' frozen ratio bands: as R1n
  E138-R4   which multiplier: E138-R1 with E130's registered R2 FLAT and R3 RISES (E130's primary, b259be11)
Reported, never a verdict: every arm (the board's p_raw = E130's primary; p80; dips kept; gates off) scored the same way; the pool
of E130's six rail blocks with E138's; the c_rb at which R1's reading would change; B's rail / board level ratio; every item.
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
REG = os.path.join(HERE, "predictions-e138.json")
ITEMS = os.path.join(HERE, "e130-items.json")
S130_PATH = os.path.join(ROOT, "tools", "claims-v3", "e130", "score_e130.py")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_s130():
    spec = importlib.util.spec_from_file_location("score_e130", S130_PATH)
    m = importlib.util.module_from_spec(spec)
    sys.modules["score_e130"] = m
    spec.loader.exec_module(m)
    return m


S = load_s130()
_block_of_e130 = S.block_of


def block_of_e138(p):
    p = int(p)
    return "B" if 13810 <= p <= 13819 else "A" if 13820 <= p <= 13829 else "S"


def classify(lo, hi, band_hi_group, band_lo_group):
    """lo, hi: the card's interval. band_hi_group: (lo, hi) of Booth on B; band_lo_group: (lo, hi) of the others."""
    if lo is None or hi is None:
        return "NOT SCORED"
    in_hi = not (hi < band_hi_group[0] or lo > band_hi_group[1])
    in_lo = not (hi < band_lo_group[0] or lo > band_lo_group[1])
    if in_hi and in_lo:
        return "INCONCLUSIVE"
    if in_hi:
        return "IN BOOTH ON B's BAND"
    if in_lo:
        return "IN NO RECODER's BAND"
    if lo > band_lo_group[1] and hi < band_hi_group[0]:
        return "NEITHER (BETWEEN)"
    return "NEITHER (ABOVE)" if lo > band_hi_group[1] else "NEITHER (BELOW)"


def e138_rules(book, reg, scale):
    """The E138 rules on one Book. scale: board-equivalent fJ per unit of the book's fJ (1 / c_rb for the rail, 1 for the board)."""
    mn = reg["plan"]["min_kept_blocks"]
    nB = len(book.blocks["B"])
    st = S.statistics(book)
    d = st["B_odd_minus_even_fJ"]
    q = st["B_odd_over_even"]
    eq = {k: (None if d.get(k) is None else d[k] * scale) for k in ("mean", "lo", "hi")}
    eq["n"] = d.get("n")
    T = reg["thresholds"]["T_B"]["value"]
    gb = reg["group_bands"]
    v = {}
    if nB < mn:
        v["E138-R1"] = v["E138-R1n"] = v["E138-R1q"] = v["E138-R4"] = "NOT SCORED"
    else:
        v["E138-R1"] = S.three_way(eq, T, "RECODED", "FLAT", mn, nB)
        v["E138-R1n"] = classify(eq["lo"], eq["hi"], gb["B_odd_minus_even_fJ"]["booth_on_b"], gb["B_odd_minus_even_fJ"]["no_recoder_on_b"])
        v["E138-R1q"] = classify(q.get("lo"), q.get("hi"), gb["B_odd_over_even"]["booth_on_b"], gb["B_odd_over_even"]["no_recoder_on_b"])
        v["E138-R4"] = {"RECODED": "BOOTH ON B", "FLAT": "NO BOOTH",
                        "INCONCLUSIVE": "INCONCLUSIVE between BOOTH ON B / NO BOOTH"}.get(v["E138-R1"], "NOT SCORED")
    flip = {}
    if d.get("lo") is not None and d["lo"] > 0:
        flip["c_rb_at_which_low_end_meets_T_B"] = d["lo"] / T     # at c_rb <= this, RECODED
        flip["c_rb_at_which_high_end_meets_T_B"] = d["hi"] / T    # at c_rb >= this, FLAT
    return {"verdicts": v, "B_odd_minus_even_book_fJ": {k: d.get(k) for k in ("mean", "lo", "hi", "n", "se")},
            "B_odd_minus_even_board_equivalent_fJ": eq, "B_odd_over_even": {k: q.get(k) for k in ("ratio", "lo", "hi", "n")},
            "per_block_book_fJ": d.get("per_block"), "n_B_blocks": nB, "scale_to_board_fJ": scale, "c_rb_flip_points": flip,
            "blocks": book.blocks, "set_aside": book.set_aside,
            "prices_book_fJ": {t: book.price(t) for t in sorted({k[5:] for k in book.steps})},
            "zero_residual_sd_value": S.sd(book.zero_resid), "zero_residual_n": len(book.zero_resid)}


def make_book(csvp, redp, value, gate, reg, tiles, e130_numbers=False):
    S.block_of = _block_of_e130 if e130_numbers else block_of_e138
    b = S.Book(S.load_runs(csvp), tiles, value, gate, reg["plan"]["train_gate_w"], json.load(open(redp)))
    S.block_of = block_of_e138
    return b


def pooled(book138, book130, reg, scale):
    a = book138 and S.per_block_stat(book138, S.combos()["B_odd_minus_even_fJ"]) or {}
    b = book130 and S.per_block_stat(book130, S.combos()["B_odd_minus_even_fJ"]) or {}
    vals = list(a.values()) + list(b.values())
    m = S.mean_ci(vals)
    eq = {k: (None if m.get(k) is None else m[k] * scale) for k in ("mean", "lo", "hi")}
    eq["n"] = m.get("n")
    T = reg["thresholds"]["T_B"]["value"]
    gb = reg["group_bands"]["B_odd_minus_even_fJ"]
    return {"n_E138": len(a), "n_E130": len(b), "book_fJ": {k: m.get(k) for k in ("mean", "lo", "hi", "n")}, "board_equivalent_fJ": eq,
            "R1_reading": S.three_way(eq, T, "RECODED", "FLAT", reg["plan"]["min_kept_blocks"], len(vals)),
            "R1n_reading": classify(eq["lo"], eq["hi"], gb["booth_on_b"], gb["no_recoder_on_b"])}


def oos(book138, book130):
    """Reported (registered before the data): E130's rail per-item prices of B bits 0-6 predicted from E138's under three
    per-flip models - flat (one price for every B bit: the mean of E138's bits 0-6), parity (E138's odd-bit mean for 1, 3, 5,
    its even-bit mean for 0, 2, 4, 6) and per position (E138's own price of that bit) - each model's rms error in rail fJ."""
    ts = [f"b1_{j}" for j in range(7)]
    m138 = {t: book138.price(t)["fJ"]["mean"] for t in ts}
    m130 = {t: book130.price(t)["fJ"]["mean"] for t in ts}
    if None in m138.values() or None in m130.values():
        return None
    flat = sum(m138.values()) / len(ts)
    odd = sum(m138[f"b1_{j}"] for j in (1, 3, 5)) / 3
    even = sum(m138[f"b1_{j}"] for j in (0, 2, 4, 6)) / 4
    models = {"flat": {t: flat for t in ts}, "parity": {t: (odd if int(t[-1]) % 2 else even) for t in ts}, "per_position": m138}
    rms = {k: math.sqrt(sum((v[t] - m130[t]) ** 2 for t in ts) / len(ts)) for k, v in models.items()}
    return {"rms_rail_fJ": rms, "e130_mean_rail_fJ": sum(m130.values()) / len(ts), "items": ts}


def fmt(x, nd=1):
    return "-" if x is None else f"{x:+.{nd}f}"


def markdown(res, reg):
    p = res["primary"]
    L = [f"# E138 results (generated by score_e138.py; primary: {reg['plan']['primary']})", "",
         "| rule | primary (rail) | " + " | ".join(res["arms"]) + " |", "|---|---|" + "---|" * len(res["arms"])]
    for r in ("E138-R1", "E138-R1n", "E138-R1q", "E138-R4"):
        L.append(f"| {r} | **{p['verdicts'][r]}** | " + " | ".join(a["verdicts"][r] for a in res["arms"].values()) + " |")
    L += ["", "| reading | n | mean | 95% |", "|---|---|---|---|"]
    for name, x in [("primary (rail)", p)] + list(res["arms"].items()):
        e = x["B_odd_minus_even_board_equivalent_fJ"]
        L.append(f"| {name}: B odd - even, board-equivalent fJ | {e['n']} | {fmt(e['mean'])} | [{fmt(e['lo'])}, {fmt(e['hi'])}] |")
        q = x["B_odd_over_even"]
        L.append(f"| {name}: B odd / even | {q.get('n')} | {fmt(q.get('ratio'), 2)} | [{fmt(q.get('lo'), 2)}, {fmt(q.get('hi'), 2)}] |")
    if res.get("pool_with_e130"):
        P = res["pool_with_e130"]
        e = P["board_equivalent_fJ"]
        L.append(f"| pool E130 ({P['n_E130']}) + E138 ({P['n_E138']}), rail, board-equivalent fJ (reported) | {e['n']} | "
                 f"{fmt(e['mean'])} | [{fmt(e['lo'])}, {fmt(e['hi'])}] |")
    L += ["", f"T_B = {reg['thresholds']['T_B']['value']:.2f} board fJ; c_rb = {reg['plan']['c_rb']} (frozen); "
          f"c_rb flip points (primary): {json.dumps({k: round(v, 3) for k, v in p['c_rb_flip_points'].items()})}",
          f"Kept B blocks: {p['blocks']['B']}; set aside: {json.dumps(p['set_aside'])[:400]}", "",
          "| item | rail fJ (primary) | 95% | board fJ (board arm) | 95% |", "|---|---|---|---|---|"]
    bo = res["arms"].get("board", {}).get("prices_book_fJ", {})
    for t, pr in p["prices_book_fJ"].items():
        f = pr["fJ"]
        g = bo.get(t, {}).get("fJ", {})
        L.append(f"| {t} | {fmt(f.get('mean'))} | [{fmt(f.get('lo'))}, {fmt(f.get('hi'))}] | {fmt(g.get('mean'))} | "
                 f"[{fmt(g.get('lo'))}, {fmt(g.get('hi'))}] |")
    return "\n".join(L) + "\n"


def check_reg(reg):
    want = reg["harness"]["score_e130_sha256"]
    have = sha(S130_PATH)
    if have != want:
        raise SystemExit(f"score_e130.py sha256 {have} != registered {want}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary")
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--pool-e130")
    ap.add_argument("--selftest-e130", help="score E130's committed runs with E138's code (pass numbers mapped 130xx -> 138xx)")
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = json.load(open(REG))
    check_reg(reg)
    tiles = {"int8." + t["tile"]: t for t in json.load(open(ITEMS))["tiles"]}
    c = reg["plan"]["c_rb"]
    if a.selftest_e130:
        csvp, redp = a.selftest_e130.split(",")
        b = make_book(csvp, redp, "rail_raw", True, reg, tiles, e130_numbers=True)
        S.block_of = _block_of_e130
        r = e138_rules(b, reg, 1.0 / c)
        bb = make_book(csvp, redp, "p_raw", True, reg, tiles, e130_numbers=True)
        S.block_of = _block_of_e130
        rb = e138_rules(bb, reg, 1.0)
        S.block_of = block_of_e138
        print(json.dumps({"rail": {k: r[k] for k in ("verdicts", "B_odd_minus_even_book_fJ", "B_odd_minus_even_board_equivalent_fJ",
                                                     "B_odd_over_even", "c_rb_flip_points")},
                          "board": {k: rb[k] for k in ("verdicts", "B_odd_minus_even_board_equivalent_fJ", "B_odd_over_even")}},
                         indent=1, default=lambda o: None))
        return 0
    csvp, redp = a.primary.split(",")[:2]
    prim = make_book(csvp, redp, "rail_raw", True, reg, tiles)
    res = {"experiment": "E138", "primary_arm": reg["plan"]["primary"], "primary": e138_rules(prim, reg, 1.0 / c), "arms": {}}
    for spec in a.arm:
        name, rest = spec.split("=", 1)
        parts = rest.split(",")
        book = make_book(parts[0], parts[1], parts[2], parts[3] == "on", reg, tiles)
        res["arms"][name] = e138_rules(book, reg, (1.0 / c) if parts[2].startswith("rail") else 1.0)
    if a.pool_e130:
        pc, pr = a.pool_e130.split(",")
        b130 = make_book(pc, pr, "rail_raw", True, reg, tiles, e130_numbers=True)
        S.block_of = _block_of_e130
        b130_stat_ready = b130
        S.block_of = block_of_e138
        res["pool_with_e130"] = pooled(prim, b130_stat_ready, reg, 1.0 / c)
        res["out_of_sample_e130"] = oos(prim, b130_stat_ready)
    lev = {}
    if "board" in res["arms"]:
        r_m = res["primary"]["prices_book_fJ"]
        b_m = res["arms"]["board"]["prices_book_fJ"]
        ts = [f"b1_{j}" for j in range(7)]
        rr = [r_m[t]["fJ"]["mean"] for t in ts if t in r_m and t in b_m]
        bbv = [b_m[t]["fJ"]["mean"] for t in ts if t in r_m and t in b_m]
        if rr and bbv and sum(bbv):
            lev["B_bits0to6_rail_over_board_level"] = sum(rr) / sum(bbv)
    res["reported"] = lev
    pv = res["primary"]["verdicts"]
    res["arm_sensitive"] = {r: [n for n, x in res["arms"].items() if x["verdicts"].get(r) != pv[r]] for r in pv}
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, default=lambda o: None)
    md = markdown(res, reg)
    if a.md:
        open(a.md, "w").write(md)
    print("\n".join(f"{r}: {pv[r]}" + (f"   (differs in: {', '.join(res['arm_sensitive'][r])})" if res["arm_sensitive"][r] else "")
                    for r in sorted(pv)))
    e = res["primary"]["B_odd_minus_even_board_equivalent_fJ"]
    print(f"primary B odd - even {fmt(e['mean'])} [{fmt(e['lo'])}, {fmt(e['hi'])}] board-equivalent fJ, n {e['n']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
