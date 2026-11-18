#!/usr/bin/env python3
"""v31-trace (Q217), POST HOC desk table: the masked walk's numbers at every equal-shire-count layout pair E212 ran (rgm136's gemmL, fp32 zeros:
1x16x4, 1x1x16, 2x4x16, 4x8x4 at n = 4, 8, 16, 24), beside E212's measured wall cycles an op over the same session's full chip (committed
data, docs/reports/data/2026-11-17-e212-mmsweep2-*/data-e212-*.json, each session's primary view). Nothing is fitted here: the walk's request
streams and exact LRU stack distances (lock step), strict LRU at 32 MB (no constant), and MM1-v3's FROZEN retention (its fitted x1, w1, pB, x2,
w2 from tools/matmul/mm1/v3/out/mm1_v3_params.json, applied to the walk's masked distances: A one edge (x1, w1), B two edges). The sign
check: does the layout with fewer fresh lines run faster? (post hoc; E212's data existed before this table). /usr/bin/python3 3.12.3.

    python3 -I -B layout_table_v31.py --out layout_table_v31.json
"""
import argparse
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import walk_v31 as W  # noqa: E402

# t7-0xf (Q221) scrub: the lab checkout from ET_LAB, else from this file's place in it (tools/matmul/mm1/v3.1/walk/walk/).
LAB = os.environ.get("ET_LAB") or os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
DATA = LAB + "/docs/reports/data/2026-11-17-e212-mmsweep2-%s/data-e212-%s.json"
PARAMS = LAB + "/tools/matmul/mm1/v3/out/mm1_v3_params.json"
PAIRS = [(4, "0xf", "s4", "0x1111", "m1111"), (8, "0xff", "s8", "0x11111111", "m11111111"),
         (16, "0xffff", "s16", "0x33333333", "m33333333"), (24, "0xffffff", "s24", "0x77777777", "m77777777")]
SESS = {"1x16x4": ["a1c0-S1", "a1c1-S1", "a2c0-S1", "a1c1-S3"], "1x1x16": ["a1c0-S1", "a1c1-S1", "a2c0-S1", "a1c1-S3"],
        "2x4x16": ["a1c1-S3"], "4x8x4": ["a2c0-S4"]}


def ret_fns(th):
    def rA(d):
        return 1.0 / (1.0 + math.exp(max(-50.0, min(50.0, (d - th["x1"]) / th["w1"]))))

    def rB(d):
        e1 = 1.0 / (1.0 + math.exp(max(-50.0, min(50.0, (d - th["x1"]) / th["w1"]))))
        e2 = 1.0 / (1.0 + math.exp(max(-50.0, min(50.0, (d - th["x2"]) / th["w2"]))))
        return (1.0 - th["pB"]) * e1 + th["pB"] * e2
    return rA, rB


def walk_numbers(shape, mask, rA, rB):
    MB, NB, KB = W.parse_shape(shape)
    recA, recB = W.l3_distances("rgm136.gemmL", MB, NB, KB, mask)
    cap = 32 * 1024
    nst = len(recA)
    # per shire-op: the shire's 4 A and 8 B requests, each with its tile's distance; a fresh tile shared by w shires: one chip read
    shA = shB = 0.0
    frA = frB = 0.0          # strict: shire requests whose tile is not in the L3 (per shire-op, lines)
    chip_fresh = 0.0         # strict: distinct fresh tiles a step (lines)
    rtA = rtB = 0.0          # MM1-v3 retention: expected shire requests served by the L3
    chip_fresh_ret = 0.0
    nreqA = nreqB = 0
    for sa, sb in zip(recA, recB):
        for d, who in sa:
            w = len(who)
            nreqA += w
            dm = d / 1024.0 if d < W.INF else 1e9
            frA += w * (d >= cap)
            rtA += w * rA(dm)
            chip_fresh += (d >= cap)
            chip_fresh_ret += 1.0 - rA(dm)
            shA += (w > 1) * w
        for d, who in sb:
            w = len(who)
            nreqB += w
            dm = d / 1024.0 if d < W.INF else 1e9
            frB += w * (d >= cap)
            rtB += w * rB(dm)
            chip_fresh += (d >= cap)
            chip_fresh_ret += 1.0 - rB(dm)
            shB += (w > 1) * w
    n = len(W.mask_shires(mask))
    per = n * nst            # shire-ops
    return {"shire_op_lines_fresh_strict": round(16 * (frA + frB) / per, 3), "A_fresh_strict": round(16 * frA / per, 3),
            "B_fresh_strict": round(16 * frB / per, 3), "chip_fresh_lines_step_strict": round(16 * chip_fresh / nst, 3),
            "shire_op_lines_fresh_v3ret": round(16 * ((nreqA - rtA) + (nreqB - rtB)) / per, 3),
            "chip_fresh_lines_step_v3ret": round(16 * chip_fresh_ret / nst, 3),
            "shared_requests_per_shire_op": {"A": round(shA / per, 3), "B": round(shB / per, 3)},
            "footprint_MB": W.footprint_tiles("rgm136.gemmL", MB, NB, KB, mask)["MB"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    th = json.load(open(PARAMS))["time"]["theta"]
    rA, rB = ret_fns(th)
    rows = []
    agree = {"strict_shire": [0, 0], "strict_chip": [0, 0], "v3ret_shire": [0, 0], "v3ret_chip": [0, 0], "more_shared_slower": [0, 0]}
    for shape, sessions in SESS.items():
        for n, cm, cs, sm, ss in PAIRS:
            meas = []
            for s in sessions:
                d = json.load(open(DATA % (s, s)))
                pv = d["primary_view"]
                arms = d["arms"]
                full = "%s-fp32-zeros" % shape
                kc, ks = "%s-%s" % (full, cs), "%s-%s" % (full, ss)
                if kc in arms and ks in arms and full in arms:
                    g = lambda k: (arms[k]["views"].get(pv) or arms[k]["views"]["burst"])["cyc_op_max"]
                    meas.append({"session": s, "compact_over_full": round(g(kc) / g(full), 4), "spread_over_full": round(g(ks) / g(full), 4),
                                 "spread_over_compact": round(g(ks) / g(kc), 4)})
            if not meas:
                continue
            wc, ws = walk_numbers(shape, cm, rA, rB), walk_numbers(shape, sm, rA, rB)
            msign = [m["spread_over_compact"] for m in meas]
            row = {"shape": shape, "n": n, "compact": cm, "spread": sm, "measured": meas, "walk_compact": wc, "walk_spread": ws}
            # sign check per session: measured spread faster (ratio < 1) vs walk spread with fewer fresh lines
            for key, field in (("strict_shire", "shire_op_lines_fresh_strict"), ("strict_chip", "chip_fresh_lines_step_strict"),
                               ("v3ret_shire", "shire_op_lines_fresh_v3ret"), ("v3ret_chip", "chip_fresh_lines_step_v3ret")):
                diff = ws[field] - wc[field]
                calls = []
                for r in msign:
                    if abs(r - 1.0) < 0.01 or abs(diff) < 1e-6:
                        calls.append("tie")
                        continue
                    ok = (diff < 0) == (r < 1.0)
                    agree[key][0] += ok
                    agree[key][1] += 1
                    calls.append("right" if ok else "wrong")
                row["sign_" + key] = calls
            # the other simple rule: the layout with more shared requests a shire-op runs slower
            shc = sum(wc["shared_requests_per_shire_op"].values())
            shs = sum(ws["shared_requests_per_shire_op"].values())
            calls = []
            for r in msign:
                if abs(r - 1.0) < 0.01 or abs(shs - shc) < 1e-9:
                    calls.append("tie")
                    continue
                ok = (shs > shc) == (r > 1.0)
                agree["more_shared_slower"][0] += ok
                agree["more_shared_slower"][1] += 1
                calls.append("right" if ok else "wrong")
            row["sign_more_shared_slower"] = calls
            rows.append(row)
            print(shape, n, cm, sm, "measured spread/compact", msign, "| walk fresh lines a shire-op strict %.1f / %.1f, chip a step %.1f / %.1f;"
                  " v3 retention shire-op %.1f / %.1f" % (wc["shire_op_lines_fresh_strict"], ws["shire_op_lines_fresh_strict"],
                                                         wc["chip_fresh_lines_step_strict"], ws["chip_fresh_lines_step_strict"],
                                                         wc["shire_op_lines_fresh_v3ret"], ws["shire_op_lines_fresh_v3ret"]), flush=True)
    res = {"what": "POST HOC desk table: the masked walk at E212's equal-shire-count layout pairs beside E212's measured ratios (no fit)",
           "python": sys.version.split()[0], "mm1_v3_retention": {k: th[k] for k in ("x1", "w1", "pB", "x2", "w2")},
           "sign_agreement": {k: "%d of %d (ties within 1%% of measured or 0 walk difference left out)" % tuple(v) for k, v in agree.items()},
           "rows": rows}
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(res["sign_agreement"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
