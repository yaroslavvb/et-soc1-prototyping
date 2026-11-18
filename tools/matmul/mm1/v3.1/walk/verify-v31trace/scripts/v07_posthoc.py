#!/usr/bin/env python3
"""verify-v31trace (Q217) v07: desk checks of v31-trace's model numbers and its post hoc layout table, by this lane's own code.
(1) The chip's strict LRU at 32 MB over the active shires' lock-step stream at 2x4x16 (rgm136 gemmL, masks 0xf and 0x1111), by an
    OrderedDict LRU (not the walk's Fenwick stack distances): A and B in-L3 shares of the distinct requests and the chip's fresh lines a
    step, against walk_predictions.json (frozen).
(2) E212's measured spread/compact ratios re-read from the committed data files (LAB, GitHub main), against layout_table_v31.json.
(3) The sign tallies per (pair, session) call, as the table counts them, and per PAIR (one call a pair when its sessions agree).
/usr/bin/python3 3.12.3, standard library; reads only.
"""
import collections
import json
import sys

V = "<W>/out/v31-trace"
LAB = "<LAB>"
TILE = 1024
ABLK, BBLK, CBLK = 2048, 1024, 2048   # in tiles


def chip_stream(MB, NB, KB, mask, walk="mn"):
    sh = [s for s in range(32) if (mask >> s) & 1]
    rg = sorted({(s >> 2) & 7 for s in sh})
    cg = sorted({s & 3 for s in sh})
    blocks = [(mb, nb) for mb in range(MB) for nb in range(NB)] if walk == "mn" else [(mb, nb) for nb in range(NB) for mb in range(MB)]
    for mb, nb in blocks:
        for r in (0, 1):
            for kb in range(KB):
                for k in range(32):
                    A = [("A", (mb * KB + kb) * ABLK + (8 * g + 2 * d + r) * 32 + k) for g in rg for d in range(4)]
                    B = [("B", (kb * NB + nb) * BBLK + (8 * c + p) * 32 + k) for c in cg for p in range(8)]
                    yield "op", A, B
            C = [("C", (mb * NB + nb) * CBLK + (2 * q + r) * 32 + c) for q in range(32) for c in range(32) if 4 * (q // 4) + c // 8 in sh]
            yield "st", C, None


def lru_levels(MB, NB, KB, mask, cap_tiles, walk="mn"):
    stream = list(chip_stream(MB, NB, KB, mask, walk))
    lru = collections.OrderedDict()
    res = None
    for p in range(2):
        nA = nB = hA = hB = steps = 0
        for kind, X, Y in stream:
            lists = [X] if kind == "st" else [X, Y]
            for li, lst in enumerate(lists):
                for t in lst:
                    hit = t in lru
                    if hit:
                        lru.move_to_end(t)
                    else:
                        lru[t] = 1
                        if len(lru) > cap_tiles:
                            lru.popitem(last=False)
                    if kind == "op":
                        if li == 0:
                            nA += 1
                            hA += hit
                        else:
                            nB += 1
                            hB += hit
            steps += kind == "op"
        res = {"A_in_L3_share": round(hA / nA, 6), "B_in_L3_share": round(hB / nB, 6),
               "chip_fresh_lines_per_step": round(16 * ((nA - hA) + (nB - hB)) / steps, 6), "steps": steps}
    return res


def main():
    out = {}
    fz = json.load(open(V + "/walk/walk_predictions.json"))
    for run, mask, walk in (("t1-gemmL-2x4x16-0xf", 0xf, "mn"), ("t2-gemmL-2x4x16-0x1111", 0x1111, "mn"),
                            ("t3-gemmLn-2x4x16-0xf", 0xf, "nm"), ("t4-gemmLn-2x4x16-0x1111", 0x1111, "nm")):
        mine = lru_levels(2, 4, 16, mask, 32 * 1024, walk)
        w = fz["runs"][run]["walk_summary"]["l3_strict_by_cap"]["32"]
        out["lru_" + run] = {"mine_OrderedDict": mine, "walk_frozen": {k: w[k] for k in ("A_in_L3_share_distinct", "B_in_L3_share_distinct",
                                                                                       "chip_fresh_lines_per_step")}}
    lt = json.load(open(V + "/walk/layout_table_v31.json"))
    rows_out = []
    per_call = collections.Counter()
    per_pair = collections.defaultdict(collections.Counter)
    for r in lt["rows"]:
        shape, cm, sm = r["shape"], r["compact"], r["spread"]
        cs, ss = {"0xf": "s4", "0xff": "s8", "0xffff": "s16", "0xffffff": "s24"}[cm], \
            {"0x1111": "m1111", "0x11111111": "m11111111", "0x33333333": "m33333333", "0x77777777": "m77777777"}[sm]
        remeas = []
        for m in r["measured"]:
            s = m["session"]
            d = json.load(open(LAB + "/docs/reports/data/2026-11-17-e212-mmsweep2-%s/data-e212-%s.json" % (s, s)))
            pv = d["primary_view"]
            arms = d["arms"]
            full = "%s-fp32-zeros" % shape

            def g(k):
                return (arms[k]["views"].get(pv) or arms[k]["views"]["burst"])["cyc_op_max"]
            rat = round(g("%s-%s" % (full, ss)) / g("%s-%s" % (full, cs)), 4)
            remeas.append({"session": s, "spread_over_compact_mine": rat, "table": m["spread_over_compact"], "equal": rat == m["spread_over_compact"]})
        keys = ("sign_strict_shire", "sign_strict_chip", "sign_v3ret_shire", "sign_v3ret_chip", "sign_more_shared_slower")
        for k in keys:
            calls = r[k]
            for c in calls:
                per_call[(k, c)] += 1
            nontie = [c for c in calls if c != "tie"]
            if nontie:
                if all(c == nontie[0] for c in nontie):
                    per_pair[k][nontie[0]] += 1
                else:
                    per_pair[k]["mixed"] += 1
            else:
                per_pair[k]["tie"] += 1
        rows_out.append({"shape": shape, "n": r["n"], "remeasured": remeas})
    out["e212_ratios"] = rows_out
    out["e212_ratios_all_equal"] = all(m["equal"] for x in rows_out for m in x["remeasured"])
    out["calls_total"] = sum(len(x["remeasured"]) for x in rows_out)
    tally = {}
    for k in ("sign_strict_shire", "sign_strict_chip", "sign_v3ret_shire", "sign_v3ret_chip", "sign_more_shared_slower"):
        right, wrong, tie = per_call[(k, "right")], per_call[(k, "wrong")], per_call[(k, "tie")]
        pp = per_pair[k]
        tally[k] = {"per_call": "%d right of %d non-tied (pair, session) calls; %d tied" % (right, right + wrong, tie),
                    "per_pair": "%d right of %d non-tied pairs (%d tied, %d mixed)" % (pp["right"], pp["right"] + pp["wrong"], pp["tie"], pp["mixed"])}
    out["tallies"] = tally
    out["table_says"] = lt["sign_agreement"]
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
