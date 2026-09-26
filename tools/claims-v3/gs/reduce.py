#!/usr/bin/env python3
"""V3-GS (E48) reduction: the items of the design's section 4.4 (README "Items"), per card and over the cards.

    python3 tools/claims-v3/gs/reduce.py --data <dir> --out verdicts.json [--gs-out gs.json] [--cards a,b,c] [--root <tree>]

<dir>/<card>/gs/p<KS>/ for every card present (aifoundry2, aifoundry3, aifoundry1-c1; the queue's DATA_ROOT/gs
collected per card). workloads/enercat/analyze_gs.py computes the values (gs.json); this file applies the rules.

Unit: the pass (one E and one R block each). Intervals: 99% two-sided t over pass values. A card needs >= 3 passes
for a TESTED item, else INSUFFICIENT on that card. Per card a TESTED item is PASS when its 99% interval lies inside
the item's range (all of its conditions), FAIL when the interval lies wholly outside a range, INCONCLUSIVE otherwise;
over the cards (expected: aifoundry2, aifoundry3, aifoundry1-c1): PASS if PASS on every card, FAIL if FAIL on every
card, CARD-DIFFERENT if PASS on some and FAIL on others, INCONCLUSIVE / INSUFFICIENT otherwise. The tested items
check the design's section 1.5 model; a FAIL says the model is wrong, never changes a measured value.

Items:
  GS-RATE     reported  elements/s, cycles per instruction and pJ per element for every E configuration (per card and
                        pooled) and the R rates
  GS-L1       tested    fgw.ps rand from L1 (512 B per hart): cycles per instruction per minion in [7, 12]
  GS-MH       tested    fgw.ps rand from L2 (4 KB) and own scratchpad (16 KB): elements/s within 0.5-2x the
                        2-miss-handler bound (23.9 G/s), and h2/h1 <= 1.2 (L2: n1024 h2 4 KB vs h1 8 KB; scratchpad:
                        R nM1 h2 vs h1)
  GS-UC       tested    fgwl.ps rand L2 (4 KB), one minion: h2/h1 elements/s in [1.6, 2.4] (strict per-thread order)
  GS-DRAM     tested    fgw.ps rand 256 KB per hart: line bytes/s within +-25% of 76 GB/s
  GS-ADD      reported  updates/s and nJ per update for upd (L1, L2, scratchpad, DRAM), famoaddl.pi (shire table),
                        famoaddg.pi (chip table), amoaddl.w, amoaddg.w; the first method over 10 G updates/s
  GS-CONFLICT reported  the lane whose value remains when every lane of a scatter hits one word, per card and op
  GS-CHECK    tested    every C launch passes on every card (the verify launches are what detects erratum 1.3's skipped
                        elements), and every launch of every used E and R block ends with gsc_progress = 0 on every
                        hart and ok (a sanity check: a skipped element leaves gsc_progress at 0)
  GS-CARD     reported  each card's median ratio to aifoundry2 over configurations (pJ/element, elements/s); the
                        catalogue's aifoundry3/aifoundry2 0.950 beside
"""
import argparse
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXPECTED = ["aifoundry2", "aifoundry3", "aifoundry1-c1"]
MIN_PASSES = 3
MH_BOUND = 1024 * 2 / 51.5 * 0.6e9     # 2 miss handlers, one line per 51.5 cycles per handler (design 1.5)
DRAM_LINE_BPS = 76e9
CATALOGUE_GAP = 0.950

C = lambda op, tgt, pat="rand", data="random", h=2, m="ff", n="n1024", s="E": f"gs/{s}/{op}/{tgt}/{pat}/{data}/h{h}/m{m}/{n}"
L1 = C("fgw.ps", "dram-512B")
L2 = C("fgw.ps", "dram-4K")
L2H1 = C("fgw.ps", "dram-8K", h=1)
SCP = C("fgw.ps", "scp-16K")
SCP_H1 = C("fgw.ps", "scp-16K", h=1, n="nM1", s="R")
SCP_H2 = C("fgw.ps", "scp-16K", h=2, n="nM1", s="R")
UC_H1 = C("fgwl.ps", "dram-4K", h=1, n="nM1", s="R")
UC_H2 = C("fgwl.ps", "dram-4K", h=2, n="nM1", s="R")
DRAM = C("fgw.ps", "dram-256K")
ADD = [("upd L1", C("upd", "dram-512B")), ("upd L2", C("upd", "dram-4K")), ("upd scratchpad", C("upd", "scp-16K")),
       ("upd DRAM", C("upd", "dram-256K")), ("famoaddl.pi shire table", C("famoaddl.pi", "shire-256K", data="zeros")),
       ("famoaddg.pi chip table", C("famoaddg.pi", "chip-8M", data="zeros")),
       ("famoaddl.pi private word", C("famoaddl.pi", "dram-512B", pat="bcast", data="zeros")),
       ("famoaddg.pi private word", C("famoaddg.pi", "dram-512B", pat="bcast", data="zeros")),
       ("amoaddl.w shire table", C("amoaddl.w", "shire-256K", data="zeros")),
       ("amoaddg.w chip table", C("amoaddg.w", "chip-8M", data="zeros"))]


def interval(st):
    if not st or st.get("n", 0) < MIN_PASSES or not st.get("ci99"):
        return None
    return st["ci99"]


def judge(iv, lo, hi):
    """PASS if the interval lies in [lo, hi], FAIL if wholly outside, INCONCLUSIVE otherwise; None -> INSUFFICIENT."""
    if iv is None:
        return "INSUFFICIENT"
    a, b = iv
    if lo <= a and b <= hi:
        return "PASS"
    if b < lo or a > hi:
        return "FAIL"
    return "INCONCLUSIVE"


def combine(outcomes):
    """Several conditions on one card: FAIL if any fails, else INSUFFICIENT/INCONCLUSIVE if any, else PASS."""
    if "FAIL" in outcomes:
        return "FAIL"
    for o in ("INSUFFICIENT", "INCONCLUSIVE"):
        if o in outcomes:
            return o
    return "PASS"


def over_cards(per_card, expected):
    vals = [per_card.get(c, {}).get("outcome", "INSUFFICIENT") for c in expected]
    if all(v == "PASS" for v in vals):
        o = "PASS"
    elif all(v == "FAIL" for v in vals):
        o = "FAIL"
    elif "PASS" in vals and "FAIL" in vals:
        o = "CARD-DIFFERENT"
    elif "INSUFFICIENT" in vals:
        o = "INSUFFICIENT"
    else:
        o = "INCONCLUSIVE"
    return {"outcome": o, "cards": expected, "outcomes": {c: per_card.get(c, {}).get("outcome", "INSUFFICIENT") for c in expected}}


def ratio_interval(a, b):
    """A conservative interval for a/b from the two 99% intervals (both positive)."""
    ia, ib = interval(a), interval(b)
    if ia is None or ib is None or ib[0] <= 0:
        return None
    return [ia[0] / ib[1], ia[1] / ib[0]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gs-out")
    ap.add_argument("--cards", default="")
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.root, "workloads", "enercat"))
    import analyze_gs as AG   # noqa: E402
    cards = [c for c in a.cards.split(",") if c] or None
    gs = AG.analyze(a.root, a.data, cards)
    if a.gs_out:
        json.dump(AG.rnd(gs), open(a.gs_out, "w"), indent=1)
    expected = sorted(set(EXPECTED) | set(gs["cards"]))
    cfg = lambda card, name: gs["cards"].get(card, {}).get("configs", {}).get(name, {})
    items = {}

    # GS-RATE (reported)
    items["GS-RATE"] = {"kind": "REPORTED", "per_card": {card: {n: {k: c.get(k) for k in ("elements_per_s", "pj_per_element",
                        "pj_per_byte", "cpi_med", "cpi_minion", "line_bytes_per_s") if c.get(k)}
                                                              for n, c in cd["configs"].items()}
                                                       for card, cd in gs["cards"].items()},
                        "pooled": {n: {k: v for k, v in c.items() if k in ("elements_per_s", "pj_per_element", "pj_per_byte", "cpi_med", "cards")}
                                   for n, c in gs["combined"].items()},
                        # the energy manual's catalogue card set (aifoundry2 + aifoundry3), for rows set beside its tables
                        "pooled_catalogue_cards": {n: {k: v for k, v in c.items() if k in ("elements_per_s", "pj_per_element",
                                                                                            "pj_per_byte", "cpi_med", "cards")}
                                                   for n, c in gs.get("combined_catalogue", {}).items()}}

    # GS-L1
    pc = {}
    for card in gs["cards"]:
        st = cfg(card, L1).get("cpi_minion")
        pc[card] = {"cpi_minion": st, "outcome": judge(interval(st), 7, 12)}
    items["GS-L1"] = {"kind": "TESTED", "cfg": L1, "range": [7, 12], "per_card": pc, **over_cards(pc, expected)}

    # GS-MH
    pc = {}
    for card in gs["cards"]:
        l2, scp = cfg(card, L2).get("elements_per_s"), cfg(card, SCP).get("elements_per_s")
        r_l2 = ratio_interval(cfg(card, L2).get("elements_per_s"), cfg(card, L2H1).get("elements_per_s"))
        r_scp = ratio_interval(cfg(card, SCP_H2).get("elements_per_s"), cfg(card, SCP_H1).get("elements_per_s"))
        conds = [judge(interval(l2), 0.5 * MH_BOUND, 2 * MH_BOUND), judge(interval(scp), 0.5 * MH_BOUND, 2 * MH_BOUND),
                 judge(r_l2, 0, 1.2), judge(r_scp, 0, 1.2)]
        pc[card] = {"l2": l2, "scp": scp, "h2_over_h1_l2": r_l2, "h2_over_h1_scp": r_scp, "conditions": conds,
                    "outcome": combine(conds)}
    items["GS-MH"] = {"kind": "TESTED", "bound_elements_per_s": MH_BOUND, "range_x_bound": [0.5, 2], "h2_over_h1_max": 1.2,
                      "cfgs": [L2, SCP, L2H1, SCP_H1, SCP_H2], "per_card": pc, **over_cards(pc, expected)}

    # GS-UC
    pc = {}
    for card in gs["cards"]:
        r = ratio_interval(cfg(card, UC_H2).get("elements_per_s"), cfg(card, UC_H1).get("elements_per_s"))
        pc[card] = {"h2_over_h1": r, "outcome": judge(r, 1.6, 2.4)}
    items["GS-UC"] = {"kind": "TESTED", "cfgs": [UC_H1, UC_H2], "range": [1.6, 2.4], "per_card": pc, **over_cards(pc, expected)}

    # GS-DRAM
    pc = {}
    for card in gs["cards"]:
        st = cfg(card, DRAM).get("line_bytes_per_s")
        pc[card] = {"line_bytes_per_s": st, "outcome": judge(interval(st), 0.75 * DRAM_LINE_BPS, 1.25 * DRAM_LINE_BPS)}
    items["GS-DRAM"] = {"kind": "TESTED", "cfg": DRAM, "range": [0.75 * DRAM_LINE_BPS, 1.25 * DRAM_LINE_BPS], "per_card": pc,
                        **over_cards(pc, expected)}

    # GS-ADD (reported)
    rows, first = [], None
    for label, name in ADD:
        comb = gs["combined"].get(name, {})
        eps, pj = comb.get("elements_per_s"), comb.get("pj_per_element")
        rows.append({"method": label, "cfg": name, "updates_per_s": eps, "nj_per_update": {k: (v / 1000 if isinstance(v, (int, float)) and k in ("mean", "min", "max") else v)
                                                                                               for k, v in (pj or {}).items()} or None})
        if first is None and eps and eps["mean"] > 10e9:
            first = label
    items["GS-ADD"] = {"kind": "REPORTED", "rows": rows, "first_over_10G_updates_per_s": first,
                       "reference": {"spread global atomics (energy manual section 6)": {"updates_per_s": 1.92e9, "nj": 1.16}}}

    # GS-CONFLICT (reported)
    pc = {}
    for card, chks in gs["checks"].items():
        last = chks[-1] if chks else {}
        pc[card] = {"winners_by_op": last.get("winners_by_op"), "probe_winner_lane": (last.get("probe") or {}).get("winner_lane")}
    items["GS-CONFLICT"] = {"kind": "REPORTED", "prediction": "lane 7 (the highest active lane; sys_emu's order)", "per_card": pc}

    # GS-CHECK: the latest C block passed every verify launch (the only detector of elements erratum 1.3 skips: a
    # skipped element leaves gsc_progress at 0), and every launch of every used E and R block (kept or dropped burst
    # alike) ended with gsc_progress = 0 on every hart and printed ok
    pc = {}
    for card in expected:
        chks = gs["checks"].get(card, [])
        last = chks[-1] if chks else None
        lc = gs["cards"].get(card, {}).get("launch_checks", {})
        if last is None:
            pc[card] = {"outcome": "INSUFFICIENT", "launch_checks": lc}
            continue
        failed = last.get("failed", [])
        probe_bad = ((last.get("probe") or {}).get("cases_failed") or {})
        bad = (failed or probe_bad or last.get("gsc_nonzero_launches", 0) or lc.get("gsc_nonzero_launches", 0)
               or lc.get("not_ok_launches", 0))
        pc[card] = {"failed": failed, "probe_cases_failed": probe_bad,
                    "c_gsc_nonzero_launches": last.get("gsc_nonzero_launches", 0), "launch_checks": lc,
                    "outcome": "FAIL" if bad else "PASS"}
    items["GS-CHECK"] = {"kind": "TESTED", "per_card": pc, **over_cards(pc, expected)}

    # GS-CARD (reported)
    items["GS-CARD"] = {"kind": "REPORTED", "ratios": gs["cross_card"], "catalogue_aifoundry3_over_aifoundry2": CATALOGUE_GAP}

    out = {"exp": "V3-GS", "experiment": "E48", "data": os.path.abspath(a.data), "cards": expected,
           "passes": {c: {"E": gs["cards"].get(c, {}).get("passes_E", []), "R": gs["cards"].get(c, {}).get("passes_R", [])} for c in expected},
           "blocks": {c: gs["cards"].get(c, {}).get("blocks", []) for c in expected},
           "rules": {"unit": "pass", "interval": "99% two-sided t over pass values", "min_passes": MIN_PASSES,
                     "per_card": "PASS inside the range, FAIL wholly outside, INCONCLUSIVE otherwise",
                     "over_cards": "PASS all / FAIL all / CARD-DIFFERENT mixed / INCONCLUSIVE / INSUFFICIENT"},
           "items": items}
    json.dump(AG.rnd(out), open(a.out, "w"), indent=1)
    for k, v in items.items():
        print(f"{k:12s} {v['kind']:9s} {v.get('outcome', '')} {v.get('outcomes', '')}")


if __name__ == "__main__":
    main()
