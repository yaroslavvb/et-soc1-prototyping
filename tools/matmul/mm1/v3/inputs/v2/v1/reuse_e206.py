#!/usr/bin/env python3
"""E206 (Q198) desk: the lines a shire-op of every E206 GEMM - how many of an op's 192 operand lines miss the shire's L2, and of those how many the
L3 still holds (n_L3) and how many are fresh (n_fresh) - by E136's desk model UNCHANGED (tools/claims-v3/e136/desk/reuse_e136.py, imported:
l2_model, l3_model), plus one new function for the shire subsets. No card. Standard library only.

    python3 -I -B tools/claims-v3/e206/desk/reuse_e206.py > tools/claims-v3/e206/desk/reuse-e206.txt     (writes reuse-e206.json beside it)

THE TIES, before any use (the script stops, exit 3, if one fails):
  1. g2k and g4k through l2_model and l3_model at 32, 28 and 24 MB equal E136's committed reuse_e136.json to the last digit;
  2. E190's three 8,192^3 shapes give E190's committed lines (reuse_e190.json, n_L3 and n_fresh at 32, 28 and 24 MB) by the convention below;
  3. the new subset function at the full mask equals l3_model on g2k, g4k, gemmL4x8x4, gemmL1x1x1 and gemmL8x16x4, at every cap.
THE CONVENTION (E136's, as its predictions-e136.py applied it to g2k and g4k): miss = the L2 model's steady missing lines a shire-op; the L3 model's
shares of A's and B's requests found in the L3 (A_in, B_in; an op asks 64 A lines and 128 B lines); n_fresh = min(miss, 64 (1 - A_in) + 128
(1 - B_in)); n_L3 = miss - n_fresh. With miss = 192 this is E190's form (n_L3 = 64 A_in + 128 B_in).
THE L2 MODEL is run on every distinct shape (E190 ran it at 8,192^3 too). A shire subset's L2 is its full-chip shape's: each participating shire
runs the full-chip GEMM's own stream (the same op list, the same addresses up to the shire offset).
THE SUBSET FUNCTION l3_model_masked(shape, cap, mask): l3_model's steps with each step's tile lists restricted to the participating shires. Shire s
asks the A row tiles of row group s >> 2 (q = 4 (s >> 2) .. +4 in l3_model's numbering) and the B column tiles of column group s & 3 (c = 8 (s & 3)
.. +8); an A tile counts once for each participating shire of its row group (4 at the full mask, as in l3_model), a B tile once for each
participating shire of its column group (8 at the full mask); C tiles are stored only by their own shire (s = 4 (q // 4) + c // 8).
THE LAW ARMS (gemmc1, gemmc8s, gemmc16s, rgm107's run_gemm): their lines are E136's classes by construction and measurement (reuse_e136.py's
section 3): c1 none missing (0, 0); c8s 128 L3-served (E107 R4) (128, 0); c16s 128 fresh, each block's first touch (0, 128).
SPDX-License-Identifier: Apache-2.0
"""
import collections
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E206 = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E136_DESK = os.path.join(REPO, "tools", "claims-v3", "e136", "desk")
E190_DESK = os.path.join(REPO, "tools", "claims-v3", "e190", "desk")
sys.path.insert(0, E136_DESK)
import reuse_e136 as R  # noqa: E402  (E136's desk model, unchanged)

FULL = 0xFFFFFFFF
CAPS = (32, 28, 24)
LAW_ARMS = {"gemmc1": (0.0, 0.0, "none missing (one block repeated: 0 missing lines an op in the steady state)"),
            "gemmc8s": (128.0, 0.0, "128 L3-served (E107 R4: c8s's 26 MB, C included, served by the L3)"),
            "gemmc16s": (0.0, 128.0, "128 fresh (each block's first touch, by construction)")}


def l3_model_masked(shape, cap_tiles, mask):
    """l3_model restricted to the shires of `mask` (see the module text); at mask 0xffffffff it is l3_model step for step."""
    _, MB, NB, KB = shape
    A0, B0, C0 = 0, 1 << 30, 1 << 31
    KT, NT = R.KT, R.NT
    lru = collections.OrderedDict()

    def touch(t):
        if t in lru:
            lru.move_to_end(t)
            return True
        lru[t] = 1
        if len(lru) > cap_tiles:
            lru.popitem(last=False)
        return False
    sh = [s for s in range(32) if (mask >> s) & 1]
    rows = collections.Counter(s >> 2 for s in sh)          # row group -> participating shires that ask its A tiles
    cols = collections.Counter(s & 3 for s in sh)           # column group -> participating shires that ask its B tiles
    qs = [q for q in range(32) if (q // 4) in rows]
    cs = [c for c in range(NT) if (c // 8) in cols]
    wA = {q: rows[q // 4] for q in qs}
    wB = {c: cols[c // 8] for c in cs}
    shset = set(sh)
    cpairs = [(q, c) for q in range(32) for c in range(NT) if (4 * (q // 4) + c // 8) in shset]

    def steps():
        for mb in range(MB):
            for nb in range(NB):
                cb = C0 + (mb * NB + nb) * R.CBLK
                for r in range(2):
                    for kb in range(KB):
                        ab, bb = A0 + (mb * KB + kb) * R.ABLK, B0 + (kb * NB + nb) * R.BBLK
                        for k in range(KT):
                            yield ([(ab + ((2 * q + r) * KT + k) * 1024, wA[q]) for q in qs], [(bb + (c * KT + k) * 1024, wB[c]) for c in cs], None)
                    yield (None, None, [cb + ((2 * q + r) * NT + c) * 1024 for q, c in cpairs])
    out = []
    for p in range(2):
        hitA = hitB = nA = nB = 0
        for a, b, c in steps():
            if c is not None:
                for t in c:
                    touch(t)
                continue
            for t, w in a:
                h = touch(t)
                hitA += w * h
                nA += w
            for t, w in b:
                h = touch(t)
                hitB += w * h
                nB += w
        out.append({"A_in_L3": round(hitA / nA, 4), "B_in_L3": round(hitB / nB, 4)})
    return out[1]


def lines_of(miss, l3):
    fresh = min(miss, 64.0 * (1 - l3["A_in_L3"]) + 128.0 * (1 - l3["B_in_L3"]))
    return {"l2_missing": miss, "n_L3": round(miss - fresh, 3), "n_fresh": round(fresh, 3)}


def shapes_of_e206():
    pts = json.load(open(os.path.join(E206, "points-e206.json")))["points"]
    full, masked = set(), set()
    for p in pts:
        if p["shape"]["kind"] != "gemmL":
            continue
        MB, NB, KB = p["shape"]["blocks"]
        m = int(p["shire_mask"], 16)
        (full if m == FULL else masked).add((MB, NB, KB, m))
        if m != FULL:
            full.add((MB, NB, KB, FULL))
    return sorted(full), sorted(masked)


def main():
    t0 = time.time()
    print(__doc__.split("\n\n")[0])
    ok = True
    # ---- tie 1: g2k and g4k against E136's committed numbers
    com = json.load(open(os.path.join(E136_DESK, "reuse_e136.json")))["gemms"]
    ties = {}
    for g, shp in (("g2k", (2, 2, 2)), ("g4k", (4, 8, 8))):
        l2 = R.l2_model(("large",) + shp)
        l3 = {f"{c}MB": R.l3_model(("large",) + shp, c * 1024) for c in CAPS}
        eq = l2 == com[g]["L2"] and all(l3[k] == com[g]["L3"][k] for k in com[g]["L3"])
        mk = {f"{c}MB": l3_model_masked(("large",) + shp, c * 1024, FULL) for c in CAPS}
        eqm = mk == l3
        ties[g] = {"l2": l2, "l3": l3, "equal_e136_committed": eq, "masked_full_equals_l3_model": eqm}
        print(f"tie {g}: L2 and L3 equal reuse_e136.json: {eq}; the subset function at the full mask equals l3_model: {eqm}")
        ok = ok and eq and eqm
    # ---- tie 2: E190's three shapes against E190's committed lines
    c190 = json.load(open(os.path.join(E190_DESK, "reuse_e190.json")))["shapes"]
    cache = {}
    for t, shp in (("fp32", (8, 16, 16)), ("fp16", (8, 16, 8)), ("int8", (8, 16, 4))):
        l2 = R.l2_model(("large",) + shp)
        l3 = {f"{c}MB": R.l3_model(("large",) + shp, c * 1024) for c in CAPS}
        ln = {k: lines_of(l2["steady_missing_lines_per_op"], v) for k, v in l3.items()}
        eq = all(ln[k]["n_L3"] == c190[t]["lines_per_shire_op"][k]["n_L3"] and ln[k]["n_fresh"] == c190[t]["lines_per_shire_op"][k]["n_fresh"]
                 for k in ln) and l2 == c190[t]["L2"]
        extra = {}
        if t == "int8":
            extra["masked_full_equals_l3_model"] = {f"{c}MB": l3_model_masked(("large",) + shp, c * 1024, FULL) for c in CAPS} == l3
            ok = ok and extra["masked_full_equals_l3_model"]
        ties[f"e190.{t}"] = {"l2": l2, "l3": l3, "lines": ln, "equal_e190_committed": eq, **extra}
        cache[(shp[0], shp[1], shp[2], FULL)] = {"L2": l2, "L3": l3}
        print(f"tie E190 {t} gemmL{shp[0]}x{shp[1]}x{shp[2]}: lines equal reuse_e190.json: {eq}" + (f"; subset function at the full mask == l3_model: "
                                                                                                    f"{extra['masked_full_equals_l3_model']}" if extra else ""))
        ok = ok and eq
    if not ok:
        print("TIE FAILED: the model is not the one E136 and E190 froze, or the subset function differs from l3_model at the full mask")
        json.dump({"ties": ties, "tie_ok": False}, open(os.path.join(HERE, "reuse-e206.json"), "w"), indent=1)
        sys.exit(3)
    # ---- every E206 shape
    full, masked = shapes_of_e206()
    res = {}
    for (MB, NB, KB, m) in full:
        key = f"gemmL{MB}x{NB}x{KB}@0x{m:x}"
        if (MB, NB, KB, m) in cache:
            l2, l3 = cache[(MB, NB, KB, m)]["L2"], cache[(MB, NB, KB, m)]["L3"]
        else:
            l2 = R.l2_model(("large", MB, NB, KB))
            l3 = {f"{c}MB": R.l3_model(("large", MB, NB, KB), c * 1024) for c in CAPS}
        rec = {"blocks": [MB, NB, KB], "shire_mask": f"0x{m:x}", "shires": 32, "L2": l2, "L3": l3, "model": "l2_model and l3_model (E136, unchanged)",
               "lines": {k: lines_of(l2["steady_missing_lines_per_op"], v) for k, v in l3.items()}}
        if (MB, NB, KB) in ((4, 8, 4), (1, 1, 1)):
            mk = {f"{c}MB": l3_model_masked(("large", MB, NB, KB), c * 1024, FULL) for c in CAPS}
            rec["masked_full_equals_l3_model"] = mk == l3
            ok = ok and rec["masked_full_equals_l3_model"]
        res[key] = rec
        L = rec["lines"]
        print(f"{key}: L2 steady missing {l2['steady_missing_lines_per_op']} of {l2['lines_per_op']} (first pass {l2['first_pass_missing_lines_per_op']}); "
              + "; ".join(f"{k} A {l3[k]['A_in_L3']:.4f} B {l3[k]['B_in_L3']:.4f} -> L3 {L[k]['n_L3']:.3f} fresh {L[k]['n_fresh']:.3f}" for k in l3)
              + (f"; subset function at the full mask == l3_model: {rec['masked_full_equals_l3_model']}" if "masked_full_equals_l3_model" in rec else ""))
    if not ok:
        print("TIE FAILED: the subset function differs from l3_model at the full mask")
        sys.exit(3)
    for (MB, NB, KB, m) in masked:
        key = f"gemmL{MB}x{NB}x{KB}@0x{m:x}"
        l2 = res[f"gemmL{MB}x{NB}x{KB}@0x{FULL:x}"]["L2"]
        l3 = {f"{c}MB": l3_model_masked(("large", MB, NB, KB), c * 1024, m) for c in CAPS}
        rec = {"blocks": [MB, NB, KB], "shire_mask": f"0x{m:x}", "shires": bin(m).count("1"), "L2": l2, "L3": l3,
               "model": "the full-chip shape's l2_model (a shire's own stream); l3_model_masked (new, this file)",
               "lines": {k: lines_of(l2["steady_missing_lines_per_op"], v) for k, v in l3.items()}}
        res[key] = rec
        L = rec["lines"]
        print(f"{key} ({rec['shires']} shires): L2 as the full shape {l2['steady_missing_lines_per_op']}; "
              + "; ".join(f"{k} A {l3[k]['A_in_L3']:.4f} B {l3[k]['B_in_L3']:.4f} -> L3 {L[k]['n_L3']:.3f} fresh {L[k]['n_fresh']:.3f}" for k in l3))
    arms = {a: {"n_L3": v[0], "n_fresh": v[1], "class": v[2]} for a, v in LAW_ARMS.items()}
    for a, v in arms.items():
        print(f"{a}: lines (L3, fresh) = ({v['n_L3']:.0f}, {v['n_fresh']:.0f}): {v['class']}")
    out = {"what": "E206 desk: lines a shire-op of every E206 GEMM by E136's desk model (unchanged) and the subset function (new); models, not "
                   "measurements", "model": "tools/claims-v3/e136/desk/reuse_e136.py (imported)", "caps_MB": list(CAPS),
           "convention": "n_fresh = min(miss, 64 (1 - A_in) + 128 (1 - B_in)); n_L3 = miss - n_fresh (E136's, E190's at miss 192)",
           "ties": ties, "tie_ok": True, "shapes": res, "law_arms": arms, "interpreter": sys.executable + " " + sys.version.split()[0]}
    json.dump(out, open(os.path.join(HERE, "reuse-e206.json"), "w"), indent=1, sort_keys=True)
    print(f"{len(res)} shapes ({len(full)} full-chip, {len(masked)} subsets); every tie PASS")
    sys.stderr.write(f"reuse_e206: {time.time() - t0:.1f} s\n")


if __name__ == "__main__":
    main()
