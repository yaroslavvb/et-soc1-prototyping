#!/usr/bin/env python3
"""Q140(q) part B: SM, a block-stride term from the L3's public set mapping, as registered in REGISTRATION.md (49575094).

    nice -n 10 python3 -B stride_sm.py > stride-sm.txt        (writes stride-sm.json and predictions-e169.json; 4 worker processes)

THE TERM. E146's tile-level L3 trace (tools/claims-v3/e146/desk/reuse_e146.py l3_steps: all 32 shires in lock step, two passes,
per op step the A tiles of 32 rows and the B tiles of 32 columns at one k, C's tiles stored after each row half), with E146's
fully associative 32 MB LRU replaced by the L3 of the ET-SoC-1's public register definitions: a 64 B line at physical address
PA sits in L3 shire PA[10:6], bank PA[12:11], sub-bank PA[14:13], set PA[22:15] (256 L3 sets per sub-bank at 32 MB), 4 ways,
true LRU within a set (assumed). A 1 KB tile's 16 lines go to 16 shires at one bank, sub-bank and set, so at tile level the set
is address bits [22:10]: 8,192 sets of 4 tiles. The buffers sit as the runtime's first-fit allocator places the host's `out`,
`a`, `b`: C at 0, A at C's size, B at C's + A's size (only differences matter). Everything else is E146's split() unchanged
(E136's L2 model, shires (0, 0) and (3, 5), the second pass) and MAB's frozen prices (E146 predictions-e146.json fitted.<t>.ab)
with E119's c1 base, through E158's model_e158.price; T(f) = C/f + M through 600 and 800 MHz. Nothing is fitted.

Beside it, frozen and unchanged: STRICT (strict LRU at 32 MB with C, E146's MAB lines) and ISO (E158's retention curve, w 0.9,
results.json rules.R2.iso), both through model_e158.T_model on E158's desk records (reuse_e158.json; for shapes not there the
records are rebuilt with reuse_e158.distances / lines, unchanged). Sensitivity arms (registered, never selected): ALIGNED, all
three buffers 8 MB aligned (E146's model addresses); A_STRICT, A's lines classed by strict LRU as E158 did, only B's by SM.
SPDX-License-Identifier: Apache-2.0
"""
import collections
import hashlib
import json
import math
import os
import sys
from multiprocessing import Pool

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
for p in ("tools/claims-v3/e136/desk", "tools/claims-v3/e146/desk", "tools/claims-v3/e158", "tools/claims-v3/e158/desk"):
    sys.path.insert(0, os.path.join(REPO, p))
import reuse_e136 as D  # noqa: E402  (E136's desk: shire_ops, l2_pass, cache constants; unchanged)
import reuse_e146 as D146  # noqa: E402  (E146's desk: l3_steps, to_l3_addr, A0, B0, LA0, LB0, LC0; unchanged)
import model_e158 as ME  # noqa: E402  (E158's frozen model: prices, price, T_model, iso_curve, curve_strict; unchanged)
import reuse_e158 as D158  # noqa: E402  (E158's desk: distances, lines; unchanged)

ABLK, BBLK, CBLK = D.ABLK, D.BBLK, D.CBLK
NSETS, WAYS = 8192, 4
TYPES = ("fp32", "fp16", "int8")
SHAPES = collections.OrderedDict()
for nb in range(4, 14):
    SHAPES[f"K2n{nb}"] = (1, nb, 2)
for nb in range(2, 9):
    SHAPES[f"K4n{nb}"] = (1, nb, 4)
for nb in range(1, 7):
    SHAPES[f"K6n{nb}"] = (1, nb, 6)
SHAPES.update(D146.SHAPES)                                   # E146: L1 L2 L4 L8 D1 D2 D4 D8 F6
E169 = {"P1": (1, 8, 5), "P2": (2, 8, 3), "P3": (1, 4, 8), "N1": (1, 7, 5), "N2": (2, 6, 3), "N3": (1, 5, 8)}
E168 = {"S1": (1, 3, 3), "S2": (3, 3, 2), "S3": (3, 5, 3)}
E159 = {"H1": (2, 4, 8), "H2": (4, 2, 4), "H3": (1, 2, 2)}
for d in (E169, E168, E159):
    SHAPES.update(d)
POW2 = ("P1", "P2", "P3")
COLLAPSES = ("K6n4", "K4n8", "D4", "D8")


def offsets(MB, NB, KB, aligned=False):
    if aligned:
        return {"A": D146.LA0, "B": D146.LB0, "C": D146.LC0}
    c, a = MB * NB * CBLK, MB * KB * ABLK
    return {"C": 0, "A": c, "B": c + a}


def dev_addr(t, off):
    """an E146 l3_model tile address -> its device address under the offsets"""
    if t >= D146.LC0:
        return off["C"] + (t - D146.LC0)
    if t >= D146.LB0:
        return off["B"] + (t - D146.LB0)
    return off["A"] + (t - D146.LA0)


def l3_flags_sm(shape, off):
    """E146's l3_flags with the set-mapped 4-way LRU L3: per second-pass op step the set of its operand tiles found in the L3,
    and h_C (C's stores finding their tile in the L3)"""
    sets = collections.defaultdict(list)
    memo = {}

    def touch(t):
        s = memo.get(t)
        if s is None:
            s = (dev_addr(t, off) >> 10) & (NSETS - 1)
            memo[t] = s
        L = sets[s]
        if t in L:
            L.remove(t)
            L.append(t)
            return True
        L.append(t)
        if len(L) > WAYS:
            del L[0]
        return False
    flags = []
    hc = nc = 0
    for p in range(2):
        for a, b, c in D146.l3_steps(shape):
            if c is not None:
                for t in c:
                    h = touch(t)
                    if p == 1:
                        hc += h
                        nc += 1
                continue
            hit = set()
            for t in a + b:
                if touch(t):
                    hit.add(t)
            if p == 1:
                flags.append(hit)
    return flags, hc / nc


def split_from(missed_by_shire, flagsA, flagsB):
    """E146's split() accounting, A's lines classed by flagsA and B's by flagsB (both per step)"""
    out = collections.Counter()
    nops = 0
    for missed in missed_by_shire:
        assert len(missed) == len(flagsA) == len(flagsB)
        for i, mo in enumerate(missed):
            nops += 1
            na = nb = 0
            for t in mo:
                side = "B" if t >= D146.B0 else "A"
                fl = flagsB if side == "B" else flagsA
                where = "L3" if D146.to_l3_addr(t) in fl[i] else "F"
                out[f"{side}_{where}"] += 1
                if side == "A":
                    na += 1
                else:
                    nb += 1
            out["A_L2"] += 64 - na
            out["B_L2"] += 128 - nb
    res = {k: out[k] / nops for k in ("A_L2", "A_L3", "A_F", "B_L2", "B_L3", "B_F")}
    res["n_L3"] = res["A_L3"] + res["B_L3"]
    res["n_F"] = res["A_F"] + res["B_F"]
    return res


def desk_record(shape):
    """E158's desk record (bins of stack distances) for a shape, rebuilt with reuse_e158 unchanged"""
    _, MB, NB, KB = shape
    steps, _ = D158.distances(shape)
    hist, strict, l2h, nops = D158.lines(shape, steps)
    bins = [[side, a, c, round(v / nops, 5)] for (side, a, c), v in sorted(hist.items(), key=lambda x: (x[0][0], -1 if x[0][1] is None else x[0][1], -1 if x[0][2] is None else x[0][2]))]
    return {"arm": f"gemmL{MB}x{NB}x{KB}", "bins": bins, "strict": {f"{cap}MB": {k: round(strict[cap][k] / nops, 3) for k in ("A_L3", "A_F", "B_L3", "B_F")} for cap in strict}}


def work(item):
    lab, (MB, NB, KB), need_desk = item
    shape = ("large", MB, NB, KB)
    missed_by_shire = []
    for s0, s1 in ((0, 0), (3, 5)):
        ops = D.shire_ops(shape, s0, s1, D146.A0, D146.B0)
        sets = collections.defaultdict(list)
        D.l2_pass(ops, sets, True)
        _, _, missed = D.l2_pass(ops, sets, True)
        missed_by_shire.append(missed)
    fsm, hc = l3_flags_sm(shape, offsets(MB, NB, KB))
    fal, hca = l3_flags_sm(shape, offsets(MB, NB, KB, aligned=True))
    ffa, hcf = D146.l3_flags(shape, 32 * 1024)          # E146's fully associative strict LRU at 32 MB (the A_STRICT arm's A lines)
    out = {"label": lab, "blocks": [MB, NB, KB], "arm": f"gemmL{MB}x{NB}x{KB}",
           "SM": dict(split_from(missed_by_shire, fsm, fsm), h_C=hc),
           "ALIGNED": dict(split_from(missed_by_shire, fal, fal), h_C=hca),
           "A_STRICT": dict(split_from(missed_by_shire, ffa, fsm), h_C=hc),
           "STRICT_FA": dict(split_from(missed_by_shire, ffa, ffa), h_C=hcf)}
    if need_desk:
        out["desk"] = desk_record(shape)
    return out


def tsplit(ln, ab, c1, t):
    v = {f: ME.price(ln, ab, c1, t, f) for f in (600, 800)}
    C = (v[600] - v[800]) / (1 / 600.0 - 1 / 800.0)
    return {"T600": v[600], "T800": v[800], "C": C, "M": v[800] - C / 800.0}


def r4(x, n=4):
    return None if x is None else round(x, n)


def rms(v):
    v = [x for x in v if x is not None]
    return None if not v else math.sqrt(sum(x * x for x in v) / len(v))


def main():
    ab, c1 = ME.load_prices()
    desk = ME.load_desk()
    R158 = json.load(open(os.path.join(REPO, "docs/reports/data/2026-11-03-e158-l3-retention/results.json")))
    R146 = json.load(open(os.path.join(REPO, "docs/reports/data/2026-11-02-e146-gemm-stores/results.json")))
    iso_fit = R158["rules"]["R2"]["iso"]
    iso = (ME.iso_curve(iso_fit), iso_fit["w"])
    strict = (ME.curve_strict(32.0), 1.0)
    items = [(lab, sh, lab not in desk["shapes"]) for lab, sh in SHAPES.items()]
    with Pool(4) as pool:
        res = {r["label"]: r for r in pool.map(work, items, chunksize=1)}
    # the check: SM's fully associative arm reproduces E146's desk split exactly on E146's nine shapes
    e146d = json.load(open(os.path.join(REPO, "tools/claims-v3/e146/desk/reuse_e146.json")))
    chk = {}
    for s in D146.SHAPES:
        ref = e146d["shapes"][s]["lines"]["32MB"]
        mine = res[s]["STRICT_FA"]
        chk[s] = max(abs(ref[k] - mine[k]) for k in ("A_L2", "A_L3", "A_F", "B_L2", "B_L3", "B_F"))
    print("CHECK: E146's fully associative split reproduced on its nine shapes, worst |diff| %.4f lines an op" % max(chk.values()))
    if max(chk.values()) > 0.002:
        raise SystemExit("the fully associative arm does not reproduce E146's split")

    def rec_of(s):
        return desk["shapes"][s] if s in desk["shapes"] else res[s]["desk"]
    pred = {}
    for s in SHAPES:
        for t in TYPES:
            rec = rec_of(s)
            p = {m: tsplit(res[s][m], ab, c1, t) for m in ("SM", "ALIGNED", "A_STRICT")}
            p["ISO"] = ME.T_model(rec, iso[0], iso[1], ab, c1, t)
            p["STRICT"] = ME.T_model(rec, strict[0], strict[1], ab, c1, t)
            pred[f"{s}.{t}"] = {m: {k: r4(v[k], 5) for k in ("T600", "T800", "C", "M")} for m, v in p.items()}
    # measured T800: E158 (this ladder, F6, D2, D4) and E146 (its ladder and F6)
    meas = {}
    for k, v in R158["per_shape"].items():
        meas[f"E158:{k}"] = v["T800"]
    for k, v in R146["per_shape"].items():
        meas[f"E146:{k}"] = v["T800"]
    models = ("SM", "ALIGNED", "A_STRICT", "ISO", "STRICT")
    rows = []
    for key, T8 in sorted(meas.items()):
        sess, cell = key.split(":")
        s, t = cell.split(".")
        if f"{s}.{t}" not in pred or T8 is None:
            continue
        row = {"session": sess, "cell": cell, "T800_meas": r4(T8), "shape": s, "type": t}
        for m in models:
            row[m] = {"T800": pred[cell][m]["T800"], "rel": r4(T8 / pred[cell][m]["T800"] - 1)}
        rows.append(row)

    def subset(fn):
        sel = [r for r in rows if fn(r)]
        return {m: {"rms": r4(rms([r[m]["rel"] for r in sel])), "n": len(sel)} for m in models}
    ladder = list(SHAPES)[:23]
    e158_far = [s for s in ladder if s != "K6n1"]
    scores = {
        "S1_E146_ladder_all24": subset(lambda r: r["session"] == "E146" and r["shape"] != "F6"),
        "S1_E146_ladder_kb2_18": subset(lambda r: r["session"] == "E146" and r["shape"] in ("L2", "L4", "L8", "D2", "D4", "D8")),
        "S1_E158_22_rungs_fp32": subset(lambda r: r["session"] == "E158" and r["type"] == "fp32" and r["shape"] in e158_far),
        "E158_K4_fp16_int8": subset(lambda r: r["session"] == "E158" and r["type"] != "fp32" and r["shape"].startswith("K4")),
        "F6_both_sessions": subset(lambda r: r["shape"] == "F6"),
        "E158_D2_D4": subset(lambda r: r["session"] == "E158" and r["shape"] in ("D2", "D4")),
        "all_cells": subset(lambda r: True),
    }
    s2 = {}
    for r in rows:
        if r["shape"] in COLLAPSES and r["type"] == "fp32":
            s2[f"{r['session']}:{r['cell']}"] = {m: r[m]["rel"] for m in models} | {"SM_within_3pct": abs(r["SM"]["rel"]) <= 0.03}
    # S3: the far-B share, SM against E158's measured share (both through MAB's frozen prices, E158's share_of axis)
    s3 = {}
    for s in e158_far:
        rec = desk["shapes"][s]
        tf, tl, n = ME.share_axis(rec, ab, c1, "fp32")
        if not n:
            continue
        T8m = R158["per_shape"].get(f"{s}.fp32", {}).get("T800")
        T8s = pred[f"{s}.fp32"]["SM"]["T800"]
        s3[s] = {"measured_share": r4(ME.share_of(T8m, rec, ab, c1, "fp32")), "SM_share": r4((tf - T8s) / (tf - tl)), "n_far": r4(n, 2)}
    # E169's frozen predictions
    e169 = {}
    for s, (MB, NB, KB) in E169.items():
        cell = {"arm": f"gemmL{MB}x{NB}x{KB}", "blocks": [MB, NB, KB], "power_of_two_panel_stride": s in POW2,
                "footprint_MB": {"A": MB * KB * 2, "B": KB * NB, "C": MB * NB * 2, "total": MB * KB * 2 + KB * NB + MB * NB * 2},
                "lines_SM": {k: r4(v, 3) for k, v in res[s]["SM"].items()}, "lines_STRICT": rec_of(s).get("strict", {}).get("32MB")}
        for t in TYPES:
            cell[t] = {m: pred[f"{s}.{t}"][m] for m in ("SM", "ISO", "STRICT", "ALIGNED", "A_STRICT")}
            sm, isv = cell[t]["SM"]["T800"], cell[t]["ISO"]["T800"]
            cell[t]["SM_minus_ISO_rel"] = r4(sm / isv - 1)
        e169[s] = cell
    out = {"what": "Q140(q) part B, SM: the block-stride term from the L3's public set mapping; scored on committed data (out of sample for SM: nothing fitted) and E169's frozen predictions",
           "registration": "docs/reports/data/2026-11-04-q140q-gemm-g4-stride/REGISTRATION.md (49575094)",
           "mapping": {"line": "shire PA[10:6], bank PA[12:11], sub-bank PA[14:13], set PA[22:15]", "ways": WAYS, "tile_sets": NSETS, "replacement": "true LRU (assumed)",
                       "offsets": "C 0, A C's size, B C's + A's size"},
           "check_fully_associative_vs_E146": chk, "lines": {s: {m: {k: r4(v, 3) for k, v in res[s][m].items()} for m in ("SM", "ALIGNED", "A_STRICT", "STRICT_FA")} for s in SHAPES},
           "predictions": pred, "rows": rows, "scores": scores, "S2_collapses": s2, "S3_shares": s3,
           "iso_fit": {"w": iso_fit["w"], "source": "docs/reports/data/2026-11-03-e158-l3-retention/results.json rules.R2.iso"}}
    json.dump(out, open(os.path.join(HERE, "stride-sm.json"), "w"), indent=1)
    P = {"what": "Q140(q): E169's frozen time-per-op predictions (fp32 zeros bursts on aifoundry2, its own governor; T800 from launches at or above 790 MHz, E158's reduction)",
         "date": "2026-11-04", "registration": "49575094", "term": "SM (stride_sm.py)", "beside": ["ISO (E158's frozen retention curve)", "STRICT (E146's MAB lines)"],
         "rules": {"point": "SM's T800 within 3% on every one of the six shapes (fp32; fp16 and int8 printed if run)",
                   "resolved": "on each power-of-two shape (P1-P3): |T_SM - T_ISO| / T_ISO >= 3% and the measured T800 closer to SM than to ISO"},
         "shapes": e169}
    json.dump(P, open(os.path.join(HERE, "predictions-e169.json"), "w"), indent=1)
    print("Q140(q) SM (the L3's public set mapping), every number from committed inputs; nothing fitted")
    print(f"{'cell':22s} {'meas':>7s} | {'SM':>7s} {'rel':>7s} | {'ISO':>7s} {'rel':>7s} | {'STRICT':>7s} {'rel':>7s} | {'ALIGNED':>7s} {'A_STR':>7s}")
    for r in rows:
        print(f"{r['session'] + ':' + r['cell']:22s} {r['T800_meas']:7.4f} | {r['SM']['T800']:7.4f} {r['SM']['rel']:+7.4f} | {r['ISO']['T800']:7.4f} {r['ISO']['rel']:+7.4f} | "
              f"{r['STRICT']['T800']:7.4f} {r['STRICT']['rel']:+7.4f} | {r['ALIGNED']['rel']:+7.4f} {r['A_STRICT']['rel']:+7.4f}")
    print("\nSCORES (rms of measured / predicted - 1):")
    for k, v in scores.items():
        print(f"  {k:26s} " + "  ".join(f"{m} {v[m]['rms']:.4f}" for m in models) + f"  (n {v['SM']['n']})")
    print("\nS2, the power-of-two collapses (fp32):")
    for k, v in s2.items():
        print(f"  {k:18s} SM {v['SM']:+.4f} ISO {v['ISO']:+.4f} STRICT {v['STRICT']:+.4f} ALIGNED {v['ALIGNED']:+.4f} A_STRICT {v['A_STRICT']:+.4f}  SM within 3%: {v['SM_within_3pct']}")
    print("\nS3, far-B share, measured vs SM:")
    for s, v in s3.items():
        print(f"  {s:6s} measured {v['measured_share']:+.3f}  SM {v['SM_share']:+.3f}  (far lines {v['n_far']})")
    print("\nE169 frozen (fp32 T800 us): shape, SM, ISO, STRICT, SM/ISO - 1; SM lines (A_L3 A_F B_L3 B_F)")
    for s, c in e169.items():
        L = c["lines_SM"]
        print(f"  {s} {c['arm']:12s} SM {c['fp32']['SM']['T800']:.4f} ISO {c['fp32']['ISO']['T800']:.4f} STRICT {c['fp32']['STRICT']['T800']:.4f} "
              f"{c['fp32']['SM_minus_ISO_rel']:+.4f} | {L['A_L3']:.1f} {L['A_F']:.1f} {L['B_L3']:.1f} {L['B_F']:.1f}")
    print("\nE168 / E159 shapes, line split SM vs STRICT (A_L3 A_F B_L3 B_F) and fp32 T800:")
    for s in list(E168) + list(E159):
        a, b = res[s]["SM"], res[s]["STRICT_FA"]
        print(f"  {s} {res[s]['arm']:12s} SM {a['A_L3']:.1f} {a['A_F']:.1f} {a['B_L3']:.1f} {a['B_F']:.1f} | FA {b['A_L3']:.1f} {b['A_F']:.1f} {b['B_L3']:.1f} {b['B_F']:.1f} | "
              f"T800 SM {pred[s + '.fp32']['SM']['T800']:.4f} STRICT {pred[s + '.fp32']['STRICT']['T800']:.4f} ISO {pred[s + '.fp32']['ISO']['T800']:.4f}")
    print("\ninputs sha256: model_e158.py " + hashlib.sha256(open(ME.__file__, "rb").read()).hexdigest()[:16] +
          ", reuse_e146.py " + hashlib.sha256(open(D146.__file__, "rb").read()).hexdigest()[:16])


if __name__ == "__main__":
    main()
