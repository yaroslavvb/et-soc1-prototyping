#!/usr/bin/env python3
"""E211 (Q204): THE DESK MAP - a matmul kernel's tile order to lines by operand and place, by an EXACT LRU stack-distance run over the whole
chip's request stream, for rgm136's walk (mn) and rgm211's (nm). mm-kernel2's stackmap_e211.py (Q202) with critic-kernel2's fix 1: the
CHIP-LEVEL DISTINCT LINES by operand and place (an A tile is read by the 4 shires of a row group and a B tile by the 8 shires of a column group,
so a fresh A line a shire-op is a quarter of a DRAM line and a fresh B line an eighth), and MM1-v1's stride term applied step by step. Desk: a
model of the kernels' own addresses, never measured. No card, no simulator, no device. /usr/bin/python3 3.12.3 and numpy.

    python3 -I -B tools/claims-v3/e211/desk/map_e211.py --out map-e211.json            the map of every E211 shape, both walks, and the anchors
    python3 -I -B tools/claims-v3/e211/desk/map_e211.py --tie tie-e211.json             THE TIE: rgm136's walk against E206's registered lines
    python3 -I -B tools/claims-v3/e211/desk/map_e211.py --check                         re-makes map-e211.json and tie-e211.json in memory and
                                                                                       compares them with the committed files (exit 0 = PASS)

THE TWO WALKS (rgm136's SP_GEMM_LARGE partition, cooperative loads, op order and TensorStore unchanged; only the C-block order differs):
  mn  rgm136 (run_gemm_large):      for mb { for nb { for r in 0,1 { for kb { for k < 32 { op } } TensorStore } } }
  nm  rgm211 (run_gemm_large_nm):   for nb { for mb { ...the same... } }
  At MB = 1 or NB = 1 the two walks are one op stream (the exact controls).
THE CHIP MODEL (E136's reuse_e136.py: its tile order and conventions kept, the walk a parameter):
  - one step = every minion's op at one k in lock step: the A tiles of 32 rows (row 2q + r, q < 32; an A tile is asked by 4 shires) and the B
    tiles of 32 columns (a B tile is asked by 8 shires); 1 tile = 1 KB = 16 lines; C's TensorStores (1,024 tiles a half block) allocate.
  - THE L3: one fully associative LRU over 1 KB tiles; every operand request gets its EXACT stack distance d (distinct tiles touched since its
    tile's last touch; a Fenwick tree over access times), so any retention applies afterwards: strict LRU at L MB is d < 1,024 L; MM1-v1's
    logistic retention is r(d) = 1 / (1 + exp((d/1,024 - x50)/s)). Steady state: the second pass.
  - THE L2: E105/E136's desk L2 model unchanged (2,048 sets x 4 ways of 64 B lines, LRU, one shire's own line stream, lines interleaved as
    l2sim.py issues them), shires (s0, s1) = (0, 0) and (3, 5), second pass; hits counted per operand and row half.
OUTPUTS per shape and walk (every number desk):
  strict lines (E136's convention; F1's, F2's and the chip-lines null's input): at 32, 28 and 24 MB, A_in and B_in (the shares of A's and B's
    requests found in the L3), l2_missing (the L2 model's steady missing lines a shire-op), n_fresh = min(l2_missing, 64 (1 - A_in) + 128 (1 -
    B_in)), n_L3 = l2_missing - n_fresh; THE CHIP: the DRAM lines a step by operand, A 512 (1 - A_in) c and B 512 (1 - B_in) c (c = n_fresh over
    the unclamped count, 1 unless the L2 clamps), and n_fresh_chip = n_fresh + 64 (1 - A_in) c, the fresh lines a shire-op with each A line
    counted twice (the chip's DRAM lines a step / 4: normalized to B's eight-way sharing, so a walk whose fresh lines are B's alone keeps
    n_fresh).
  MM1-v1's op classes (its logistic retention): per step the 32 A tiles and 32 B tiles meet in all 1,024 minion pairs, so a step's class
    weights are outer(pA, pB), pX = [h_X, (1 - h_X) mean r(d), (1 - h_X)(1 - mean r(d))] with h_X the L2 model's hit share of X in that row
    half; Q0 and Q1 = the mean over the steps of row half 0 (A with B's first use in the C block) and 1 (B's second use); Q0z and Q1z the same
    with B's retention x zeta step by step (MM1-v1's stride term: its frozen rule 'r1' takes Q1z for Q1 when NB is a power of two >= 4 and the
    footprint passes 32 MB). Lines a shire-op by operand and place (A 64 x its marginal, B 128 x its marginal) and THE CHIP'S DISTINCT LINES A
    STEP by operand and place (512 x each marginal: the step's 512 distinct A lines and 512 distinct B lines split by where their requests are
    served; the chip's DRAM lines a step = A_F + B_F), each for the walk's own rule and for no stride term.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PARAMS_REL = "tools/matmul/mm1/v1/out/mm1_v1_params.json"
PARAMS_SHA = "4e97654ea01e293bc61fab0fa73e8c25128af574a602e7384a14683d3b208408"
REUSE_REL = "tools/claims-v3/e206/desk/reuse-e206.json"
REUSE_SHA = "7229f3a213f65a23d9f989bc00c2634e42a8b1e58e5e084216770c1a22454561"
P136_REL = "tools/claims-v3/e136/predictions-e136.json"
R146_REL = "tools/claims-v3/e146/desk/reuse_e146.json"
MAP_OUT = os.path.join(HERE, "map-e211.json")
TIE_OUT = os.path.join(HERE, "tie-e211.json")

KT, NT, MT = 32, 32, 64
ABLK, BBLK, CBLK = MT * KT * 1024, KT * NT * 1024, MT * NT * 1024
SETS, WAYS = 2048, 4
INF = 1 << 40
CAPS = (32, 28, 24)
# E211's shapes (both walks): family W, the controls X, family C's (rgm136's walk only needed; both made), the smoke, and the stride readings
E211_SHAPES = ["2x3x2", "3x3x4", "3x6x3", "2x8x4", "2x9x4", "3x5x7", "3x6x6", "4x3x6", "6x6x6", "1x5x5", "3x1x8", "2x2x2", "2x7x4"]
ANCHORS = {"4x8x8": "F1's fp32 and fp16 anchor g4k (E136; tools/claims-v3/e136/predictions-e136.json lines.g4k.P1)",
           "4x8x4": "F1's int8 anchor D4 (E146; tools/claims-v3/e146/desk/reuse_e146.json shapes.D4.lines.32MB)"}
TIE_SHAPES = ["1x1x1", "1x1x2", "1x2x1", "1x2x2", "1x1x4", "1x1x8", "1x4x4", "2x1x4", "2x2x4", "2x4x1", "2x4x2", "2x4x4", "2x4x8", "2x8x4",
              "3x6x3", "3x5x7", "3x6x6", "4x4x4", "4x8x2", "4x8x4", "8x1x4", "8x4x4", "1x15x4", "1x16x4", "1x1x16", "1x1x32", "2x16x4",
              "2x4x16", "8x16x1", "8x1x16", "4x8x8"]


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def r6(x):
    return float(round(float(x), 6))


def block_order(walk, MB, NB):
    if walk == "mn":
        return [(mb, nb) for mb in range(MB) for nb in range(NB)]
    if walk == "nm":
        return [(mb, nb) for nb in range(NB) for mb in range(MB)]
    raise ValueError(walk)


def chip_steps(walk, MB, NB, KB):
    """the whole chip in lock step, E136's l3_model tile lists, tile ids = byte address >> 10"""
    A0, B0, C0 = 0, 1 << 30, 1 << 31
    for mb, nb in block_order(walk, MB, NB):
        cb = C0 + (mb * NB + nb) * CBLK
        for r in range(2):
            for kb in range(KB):
                ab, bb = A0 + (mb * KB + kb) * ABLK, B0 + (kb * NB + nb) * BBLK
                for k in range(KT):
                    yield (r, [(ab + ((2 * q + r) * KT + k) * 1024) >> 10 for q in range(32)],
                           [(bb + (c * KT + k) * 1024) >> 10 for c in range(NT)], None)
            yield (r, None, None, [(cb + ((2 * q + r) * NT + c) * 1024) >> 10 for q in range(32) for c in range(NT)])


def stack_distances(walk, MB, NB, KB, passes=2):
    """exact LRU stack distances (tiles) of every operand request in the last pass: arrays (steps x 32) for A and B, and each step's row half"""
    n_steps = MB * NB * 2 * KB * KT
    total = passes * (n_steps * 64 + MB * NB * 2 * 1024)
    tree = [0] * (total + 1)
    last = {}
    T = 0
    ndist = 0
    recA, recB, recR = [], [], []
    for p in range(passes):
        rec = p == passes - 1
        for r, A, B, C in chip_steps(walk, MB, NB, KB):
            lists = (C,) if C is not None else (A, B)
            out = []
            for lst in lists:
                ds = []
                for x in lst:
                    T += 1
                    L = last.get(x)
                    if L is None:
                        d = INF
                        ndist += 1
                    else:
                        s = 0
                        i = L
                        while i > 0:
                            s += tree[i]
                            i -= i & -i
                        d = ndist - s
                        i = L
                        while i <= total:
                            tree[i] -= 1
                            i += i & -i
                    i = T
                    while i <= total:
                        tree[i] += 1
                        i += i & -i
                    last[x] = T
                    ds.append(d)
                out.append(ds)
            if C is None and rec:
                recA.append(out[0])
                recB.append(out[1])
                recR.append(r)
    assert T == total, (T, total)
    return np.array(recA, dtype=np.int64), np.array(recB, dtype=np.int64), np.array(recR, dtype=np.int8)


def shire_ops(walk, MB, NB, KB, s0, s1, A0, B0):
    ops = []
    for mb, nb in block_order(walk, MB, NB):
        for r in range(2):
            for kb in range(KB):
                ab, bb = A0 + (mb * KB + kb) * ABLK, B0 + (kb * NB + nb) * BBLK
                for k in range(KT):
                    ops.append((r, [ab + ((s1 * 8 + d * 2 + r) * KT + k) * 1024 for d in range(4)],
                                [bb + ((s0 * 8 + p) * KT + k) * 1024 for p in range(8)]))
    return ops


def l2_model(walk, MB, NB, KB):
    """E136's l2_model with the walk as a parameter: per operand and half, the L2-hit lines an op in the second pass (mean of two shires)"""
    A0, B0 = 1 << 32, (1 << 32) + (1 << 30)
    acc = {(r, o): [0, 0] for r in (0, 1) for o in "AB"}   # hits, ops
    miss_tot = 0
    nops = 0
    first_miss = 0
    for s0, s1 in ((0, 0), (3, 5)):
        ops = shire_ops(walk, MB, NB, KB, s0, s1, A0, B0)
        sets = collections.defaultdict(list)
        for p in range(2):
            for r, a, b in ops:
                mA = mB = 0
                tiles = a + b
                for i in range(16):
                    for j, t in enumerate(tiles):
                        line = (t >> 6) + i
                        s = sets[line & (SETS - 1)]
                        if line in s:
                            s.remove(line)
                            s.append(line)
                        else:
                            if j < 4:
                                mA += 1
                            else:
                                mB += 1
                            s.append(line)
                            if len(s) > WAYS:
                                s.pop(0)
                if p == 0:
                    first_miss += mA + mB
                else:
                    acc[(r, "A")][0] += 64 - mA
                    acc[(r, "A")][1] += 1
                    acc[(r, "B")][0] += 128 - mB
                    acc[(r, "B")][1] += 1
                    miss_tot += mA + mB
                    nops += 1
    hits = {f"{o}_r{r}": acc[(r, o)][0] / acc[(r, o)][1] for r in (0, 1) for o in "AB"}
    return {"steady_missing_lines_per_op": miss_tot / nops, "first_pass_missing_lines_per_op": first_miss / nops,
            "hit_lines_per_op_in_half": hits}


def footprint_MB(MB, NB, KB):
    return 2.0 * MB * KB + NB * KB + 2.0 * MB * NB


def is_pow2(x):
    return x > 0 and (x & (x - 1)) == 0


def logistic(dt, x50, s):
    z = np.clip((dt / 1024.0 - x50) / s, -50, 50)
    return 1.0 / (1.0 + np.exp(z))


def marg_lines(Q):
    pA, pB = Q.sum(axis=1), Q.sum(axis=0)
    return {"A_lines_L2_L3_F_per_shire_op": [r6(64.0 * v) for v in pA], "B_lines_L2_L3_F_per_shire_op": [r6(128.0 * v) for v in pB],
            "lines_L2_L3_F_per_shire_op": [r6(64.0 * pA[i] + 128.0 * pB[i]) for i in range(3)],
            "chip_distinct_lines_per_step": {"A_L2_L3_F": [r6(512.0 * v) for v in pA], "B_L2_L3_F": [r6(512.0 * v) for v in pB],
                                             "DRAM_lines": r6(512.0 * (pA[2] + pB[2])), "L3_served_distinct": r6(512.0 * (pA[1] + pB[1]))},
            "op_share_A_fresh_B_not": r6(Q[2, 0] + Q[2, 1]), "op_share_B_fresh_A_not": r6(Q[0, 2] + Q[1, 2]), "op_share_both_fresh": r6(Q[2, 2])}


def analyse(walk, MB, NB, KB, dA, dB, R, l2, th):
    F = footprint_MB(MB, NB, KB)
    res = {"walk": walk, "blocks": [MB, NB, KB], "footprint_MB": r6(F), "steps_per_pass": int(len(R)),
           "NB_power_of_two_ge4": bool(is_pow2(NB) and NB >= 4)}
    dist = {}
    for r in (0, 1):
        for o, d in (("A", dA), ("B", dB)):
            x = d[R == r].ravel() / 1024.0
            fin = x[x < 1e6]
            dist[f"{o}_r{r}"] = {"mean_MB": r6(fin.mean()) if len(fin) else None, "p10": r6(np.percentile(x, 10)), "p50": r6(np.percentile(x, 50)),
                                 "p90": r6(np.percentile(x, 90)), "share_never_seen": r6(np.mean(x >= 1e6))}
    res["distance_MB"] = dist
    miss = l2["steady_missing_lines_per_op"]
    strict = {}
    for cap in CAPS:
        A_in = float((dA < cap * 1024).mean())
        B_in = float((dB < cap * 1024).mean())
        unclamped = 64 * (1 - A_in) + 128 * (1 - B_in)
        nF = min(miss, unclamped)
        c = nF / unclamped if unclamped > 0 else 0.0
        strict[f"{cap}MB"] = {"A_in_L3": round(A_in, 4), "B_in_L3": round(B_in, 4), "l2_missing": round(miss, 3), "n_L3": round(miss - nF, 3),
                              "n_fresh": round(nF, 3), "clamp": r6(c),
                              "chip_DRAM_lines_per_step_A": r6(512 * (1 - A_in) * c), "chip_DRAM_lines_per_step_B": r6(512 * (1 - B_in) * c),
                              "n_fresh_chip": round(nF + 64 * (1 - A_in) * c, 3)}
    res["strict_lines"] = strict
    rA = logistic(dA, th["x50"], th["s"])
    rB = logistic(dB, th["x50"], th["s"])
    h = l2["hit_lines_per_op_in_half"]
    Qh, Qz = [], []
    for r in (0, 1):
        sel = R == r
        hA = h[f"A_r{r}"] / 64.0
        hB = h[f"B_r{r}"] / 128.0
        mA = rA[sel].mean(axis=1)
        mB = rB[sel].mean(axis=1)
        pA = np.stack([np.full_like(mA, hA), (1 - hA) * mA, (1 - hA) * (1 - mA)], axis=1)
        pB = np.stack([np.full_like(mB, hB), (1 - hB) * mB, (1 - hB) * (1 - mB)], axis=1)
        mBz = mB * th["zeta"]
        pBz = np.stack([np.full_like(mB, hB), (1 - hB) * mBz, (1 - hB) * (1 - mBz)], axis=1)
        Qh.append(np.einsum("si,sj->ij", pA, pB) / len(mA))
        Qz.append(np.einsum("si,sj->ij", pA, pBz) / len(mA))
    rule_applies = bool(is_pow2(NB) and NB >= 4 and F > 32.0)
    lg = {"x50_MB": th["x50"], "s_MB": th["s"], "zeta": th["zeta"],
          "Q0": [[r6(v) for v in row] for row in Qh[0]], "Q1": [[r6(v) for v in row] for row in Qh[1]],
          "Q0z": [[r6(v) for v in row] for row in Qz[0]], "Q1z": [[r6(v) for v in row] for row in Qz[1]],
          "r1_rule_applies": rule_applies,
          "no_stride_term": marg_lines(0.5 * (Qh[0] + Qh[1])),
          "frozen_rule_r1": marg_lines(0.5 * (Qh[0] + (Qz[1] if rule_applies else Qh[1])))}
    res["mm1v1_logistic"] = lg
    res["l2_model"] = {k: (r6(v) if not isinstance(v, dict) else {a: r6(b) for a, b in v.items()}) for k, v in l2.items()}
    return res


def make_one(walk, sh, th):
    MB, NB, KB = (int(x) for x in sh.split("x"))
    dA, dB, R = stack_distances(walk, MB, NB, KB)
    l2 = l2_model(walk, MB, NB, KB)
    return analyse(walk, MB, NB, KB, dA, dB, R, l2, th)


def params():
    if sha_rel(PARAMS_REL) != PARAMS_SHA:
        sys.exit(f"map_e211: {PARAMS_REL} is not the pinned {PARAMS_SHA}")
    return json.load(open(os.path.join(REPO, PARAMS_REL)))["time"]["theta"]


def build_map():
    th = params()
    out = {"what": "E211's desk map: exact LRU stack distances over each walk's chip-wide request stream (map_e211.py); every number desk",
           "interpreter": "/usr/bin/python3 %s, numpy %s" % (sys.version.split()[0], np.__version__),
           "inputs_sha256": {PARAMS_REL: PARAMS_SHA}, "caps_MB": list(CAPS),
           "mm1v1_retention": {"x50_MB": th["x50"], "s_MB": th["s"], "zeta": th["zeta"]},
           "shapes": {}, "anchors": {}}
    for sh in E211_SHAPES:
        out["shapes"][sh] = {w: make_one(w, sh, th) for w in ("mn", "nm")}
    for sh, why in ANCHORS.items():
        out["anchors"][sh] = {"why": why, "mn": make_one("mn", sh, th)}
    return out


def build_tie(mapj=None):
    if sha_rel(REUSE_REL) != REUSE_SHA:
        sys.exit(f"map_e211: {REUSE_REL} is not the pinned {REUSE_SHA}")
    th = params()
    reg = json.load(open(os.path.join(REPO, REUSE_REL)))["shapes"]
    out = {"what": "THE TIE: the exact map on rgm136's own walk against E206's registered LRU lines (reuse-e206.json) at strict caps of 32, 28 "
                   "and 24 MB (E136's convention), and against E136's and E146's anchor lines; desk",
           "interpreter": "/usr/bin/python3 %s, numpy %s" % (sys.version.split()[0], np.__version__),
           "inputs_sha256": {REUSE_REL: REUSE_SHA, P136_REL: sha_rel(P136_REL), R146_REL: sha_rel(R146_REL)}, "rows": [], "controls": []}
    worst = 0.0
    for sh in TIE_SHAPES:
        res = make_one("mn", sh, th)
        key = f"gemmL{sh}@0xffffffff"
        row = {"shape": sh, "registered_found": key in reg}
        if key in reg:
            diffs = []
            for cap in ("32MB", "28MB", "24MB"):
                mine = res["strict_lines"][cap]
                theirs = reg[key]["lines"][cap]
                d = max(abs(mine["l2_missing"] - theirs["l2_missing"]), abs(mine["n_L3"] - theirs["n_L3"]), abs(mine["n_fresh"] - theirs["n_fresh"]))
                diffs.append(d)
                row[cap] = {"exact_map": {k: mine[k] for k in ("l2_missing", "n_L3", "n_fresh")},
                            "registered": {k: theirs[k] for k in ("l2_missing", "n_L3", "n_fresh")}}
            row["max_abs_diff_lines"] = round(max(diffs), 4)
            worst = max(worst, max(diffs))
        out["rows"].append(row)
    out["worst_abs_diff_lines"] = round(worst, 4)
    out["rows_compared"] = sum(1 for r in out["rows"] if r["registered_found"])
    p136 = json.load(open(os.path.join(REPO, P136_REL)))["lines"]["g4k"]["P1"]
    d146 = json.load(open(os.path.join(REPO, R146_REL)))["shapes"]["D4"]["lines"]["32MB"]
    g = make_one("mn", "4x8x8", th)["strict_lines"]["32MB"]
    d = make_one("mn", "4x8x4", th)["strict_lines"]["32MB"]
    out["anchors"] = {"g4k gemmL4x8x8": {"exact_map_32MB": [g["n_L3"], g["n_fresh"]], "E136_P1": p136,
                                         "max_abs_diff": round(max(abs(g["n_L3"] - p136[0]), abs(g["n_fresh"] - p136[1])), 4)},
                      "D4 gemmL4x8x4": {"exact_map_32MB": [d["n_L3"], d["n_fresh"]], "E146": [d146["n_L3"], d146["n_F"]],
                                        "max_abs_diff": round(max(abs(d["n_L3"] - d146["n_L3"]), abs(d["n_fresh"] - d146["n_F"])), 4)}}
    # the exact controls: at MB = 1 or NB = 1 the two walks must give the same map, number for number
    for sh in ("1x5x5", "3x1x8", "1x3x2"):
        a, b = make_one("mn", sh, th), make_one("nm", sh, th)
        same = json.dumps({k: v for k, v in a.items() if k != "walk"}, sort_keys=True) == json.dumps({k: v for k, v in b.items() if k != "walk"}, sort_keys=True)
        out["controls"].append({"shape": sh, "mn_equals_nm": same})
    return out


def dump(obj, path):
    s = json.dumps(obj, indent=1, sort_keys=True) + "\n"
    if path:
        open(path, "w").write(s)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--tie")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        ok = True
        for name, mk, path in (("map-e211.json", build_map, MAP_OUT), ("tie-e211.json", build_tie, TIE_OUT)):
            same = dump(mk(), None) == open(path).read()
            ok &= same
            print(f"{name}: {'SAME' if same else 'DIFFERS'}")
        print("CHECK PASS" if ok else "CHECK FAILED")
        sys.exit(0 if ok else 1)
    if a.out:
        m = build_map()
        dump(m, a.out)
        for sh in E211_SHAPES:
            for w in ("mn", "nm"):
                x = m["shapes"][sh][w]
                s32 = x["strict_lines"]["32MB"]
                lg = x["mm1v1_logistic"]["frozen_rule_r1"]
                print(f"gemmL{sh}-{w}: F {x['footprint_MB']:.0f} MB; strict32 L3 {s32['n_L3']} F {s32['n_fresh']} Fchip {s32['n_fresh_chip']}; "
                      f"logistic L2/L3/F {lg['lines_L2_L3_F_per_shire_op']}; chip DRAM a step {lg['chip_distinct_lines_per_step']['DRAM_lines']}", flush=True)
    if a.tie:
        t = build_tie()
        dump(t, a.tie)
        print(f"tie: {t['rows_compared']} rows, worst {t['worst_abs_diff_lines']} lines; anchors {t['anchors']}; controls {t['controls']}")


if __name__ == "__main__":
    main()
