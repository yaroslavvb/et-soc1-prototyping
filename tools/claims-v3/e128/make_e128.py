#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E128 (Q136, the kinds page's section 11 item 5): a random sign's rest in fp16, and the part that goes with the sums changing.
The tiles and the expected accumulators. Desk compute only; nothing here opens a card. The registration is tools/claims-v3/e128/E128.md.

    python3 tools/claims-v3/e128/make_e128.py            # writes e128/tiles/<type>/<kind>.bin and e128/e128.json
    python3 tools/claims-v3/e128/make_e128.py --check    # rebuilds in memory, compares with disk

WHAT E108 LEFT. On aifoundry1 card 1 (E108) and aifoundry3 (E122), in fp32, a tile held by zero products within each op at a walking
tile's op-end sums (`b_B_z`) carries 0.97 and 0.95 of B's rest (`b_B_w` - `z_s`), but the three tiles alternate between adding and
subtracting different numbers of times an op (`z_s` 2,268, `b_B_z` 1,800, `b_B_w` 2,016), so how much of the rest goes with the sums
changing was read only with the alternations priced post hoc (0.68-1.05). And fp16's rest was located on neither card.

THE MATCHED TRIPLE (new). A lane's eff_sub on a micro-op is sign(C) xor sign(a) xor sign(b) (txfma_c2.v; fp16: one per product). In
E104's z_s (A = -0 at k >= 1, B = E88's random +-1, k = 0 (2^50, 2^50), C = n 2^100 > 0) it is NOT sign(b) at k >= 1 and 0 at k = 0.
Two new tiles keep z_s's B stream at k >= 1 and C > 0 in every column, so their eff_sub sequence is z_s's micro-op for micro-op and
the three alternate exactly as often:
    b_B_zm   A = -0 at k >= 1 (z_s's), k = 0 (1, S_j): zero products hold C = n S_j, the walking tile's sums at every op's end
    b_B_wm   A = -1 at k >= 1 (sign 1, as -0's), k = 0 (1, b0): every product -B[k][j] is exact, C walks to n S_j
             S_j = b0 - R_j, R_j = sum_k>=1 B[k][j], b0 the smallest that makes every S_j >= 1 (fp32) or >= 2 and even (fp16)
So b_B_zm - z_s is the accumulators differing (z_s's are all equal), b_B_wm - b_B_zm the sums changing (nonzero products, a different
word written back every micro-op), with no difference in the alternations, and their sum b_B_wm - z_s is B's rest on zero products.
fp16 the same, with E104's fp16.z_s (A words (-0, -0) at k-group >= 1, B = E90's fp16.signs B, k-group 0 (2^15, 2^15) x (2^15, 2^15)):
b_B_zm k-group 0 A (1, 1) x B (S_j / 2, S_j / 2), b_B_wm A words (-1, -1) at k-group >= 1 and k-group 0 (1, 1) x (b0 / 2, b0 / 2), so both
of a micro-op's products keep z_s's eff_sub1 and eff_sub2.

THE PORT (new, fp16): E108's design as it is, on fp16.z_s's B stream: b_B_w = A words (1, 1) everywhere, B words (1, 1) at k-group 0,
C walks to n Q_j, Q_j = 2 + R_j; b_B_z = z_s with k-group 0 A (1, 1) x B (Q_j / 2, Q_j / 2) (-0 halves where Q_j = 0, so no word is raw zero),
zero products hold n Q_j. Its alternations differ from z_s's as E108's fp32 tiles' do.

REUSED BYTE FOR BYTE: E104's fp32.z_s and fp16.z_s, E108's fp32.b_B_z and b_B_w (E108-R12's three, a third session on card 1), E92's
signs and c_abs (each format's step and its zero-product held share) and fp32.w_h_add, E104's fp32.m_h_sub, fp16.w_h_add and fp16.m_h_sub
(E104-R6 / E108-R10's moving-sum ratio), E78's ones (run as E78's items).

THE COUNTS. `real` from accum.c (the RTL's arithmetic: fp32 FMA in RNE, fp16 fp16_model), `manual` (the manual's sentence; equal to
accum.c in fp32) and `fl` (C = fl(n S)), at every read-back length; they must coincide on every tile, so a read-back miss means the tile is
not what it is called. `dp_counts` (make_e104): eff_sub alternations, the lane's C read and result words, the store bits, from the real
accumulators at two op indices; the matched tiles' alternations must equal z_s's exactly (checked, and the build fails otherwise).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = os.path.abspath(os.path.join(HERE, "..", "kinds"))
sys.path.insert(0, KINDS)
import make_e104 as e  # noqa: E402

me, m90, mk = e.me, e.m90, e.mk
OUT = os.path.join(HERE, "e128")
ROOT = e.ROOT
READS = (2, 1000, 199874, 541999)
# E104's moving tiles reach 2^24 (fp32, 31 n) and 2^25 (fp16, 62 n) at op 541,200: E104 read them at 500,000, and so did E108; so does E128.
READ_MOVING = (1000, 199874, 500000)
MOVING = ("fp32.w_h_add", "fp32.m_h_sub", "fp16.w_h_add", "fp16.m_h_sub")
LAUNCH_OPS = 542000
NEW = ("fp32.b_B_zm", "fp32.b_B_wm", "fp16.b_B_zm", "fp16.b_B_wm", "fp16.b_B_z", "fp16.b_B_w")
REUSED = {
    "fp32.ones": "tools/claims-v3/kinds/tiles/", "fp16.ones": "tools/claims-v3/kinds/tiles/",
    "fp32.signs": "tools/claims-v3/kinds/e92/tiles/", "fp16.signs": "tools/claims-v3/kinds/e92/tiles/",
    "fp32.c_abs": "tools/claims-v3/kinds/e92/tiles/", "fp16.c_abs": "tools/claims-v3/kinds/e92/tiles/",
    "fp32.z_s": "tools/claims-v3/kinds/e104/tiles/", "fp16.z_s": "tools/claims-v3/kinds/e104/tiles/",
    "fp32.b_B_z": "tools/claims-v3/signloc/e108/tiles/", "fp32.b_B_w": "tools/claims-v3/signloc/e108/tiles/",
    "fp32.w_h_add": "tools/claims-v3/kinds/e92/tiles/", "fp32.m_h_sub": "tools/claims-v3/kinds/e104/tiles/",
    "fp16.w_h_add": "tools/claims-v3/kinds/e104/tiles/", "fp16.m_h_sub": "tools/claims-v3/kinds/e104/tiles/",
}
# beside the tiles, once a pass, as E106 and E108 ran them: E78's fp32.ones and fp16.ones (e128_common.COMPARE); every other tile is in POWER
COMPARE = ("fp32.ones", "fp16.ones")
POWER = tuple(sorted([n for n in NEW] + [n for n in REUSED if n not in COMPARE]))
SMOKE = ("anchor_pi", "fp32.b_B_wm", "fp32.b_B_zm", "fp16.b_B_wm", "fp16.b_B_zm", "fp32.zeros", "fp32.randn", "fp16.zeros")
# the matched triples: these tiles' eff_sub alternations must equal the first one's exactly
MATCHED = {"fp32": ("fp32.z_s", "fp32.b_B_zm", "fp32.b_B_wm"), "fp16": ("fp16.z_s", "fp16.b_B_zm", "fp16.b_B_wm")}
GROUPS = {
    "fp32.ones": "the +1 side of the step", "fp16.ones": "the +1 side of the step", "fp32.signs": "the +-1 side of the step", "fp16.signs": "the +-1 side of the step",
    "fp32.c_abs": "held baseline", "fp16.c_abs": "held baseline",
    "fp32.z_s": "held, zero products, B's signs, equal accumulators", "fp16.z_s": "held, zero products, B's signs, equal accumulators",
    "fp32.b_B_z": "E108's: held, zero products, at b_B_w's sums", "fp32.b_B_w": "E108's: B's signs walking",
    "fp16.b_B_z": "E108's design in fp16: held, zero products, at b_B_w's sums", "fp16.b_B_w": "E108's design in fp16: B's signs walking",
    "fp32.b_B_zm": "matched: held, zero products, at b_B_wm's sums", "fp32.b_B_wm": "matched: B's signs walking, alternations as z_s",
    "fp16.b_B_zm": "matched: held, zero products, at b_B_wm's sums", "fp16.b_B_wm": "matched: B's signs walking, alternations as z_s",
    "fp32.w_h_add": "fixed product sign, walking", "fp32.m_h_sub": "product sign alternating, walking",
    "fp16.w_h_add": "fixed product sign, walking", "fp16.m_h_sub": "product sign alternating, walking",
}


def read_lengths(name):
    return READ_MOVING if name in MOVING else READS


def z_s_streams():
    """E104's fp32.z_s and fp16.z_s, as words and as elements."""
    out = {}
    for ty in ("fp32", "fp16"):
        raw = open(os.path.join(ROOT, REUSED[f"{ty}.z_s"], ty, "z_s.bin"), "rb").read()
        aw, bw = me.words_from_tile(raw)
        A, B = me.elements(ty, aw, bw)
        out[ty] = (aw, bw, A, B)
    return out


def column_sums(ty, B):
    """R_j: one op's sum of B's elements at k >= 1 (fp16: both halves of every k-group >= 1)."""
    return B[1:, :].sum(axis=0) if ty == "fp32" else B[1:, :, :].sum(axis=(0, 2))


def new_designs():
    zs = z_s_streams()
    out, meta = {}, {}
    # ---- fp32
    aw, bw, A, B = zs["fp32"]
    assert np.all(A[:, 1:] == 0) and np.all(np.signbit(A[:, 1:])) and np.all(A[:, 0] == 2.0 ** 50) and np.all(B[0, :] == 2.0 ** 50)
    assert np.all(np.abs(B[1:, :]) == 1.0)
    R = column_sums("fp32", B)
    b0 = float(max(R.max(), 0.0) + 1.0)
    S = b0 - R
    assert np.all(S >= 1.0)
    Az = np.array(A)
    Az[:, 0] = 1.0                                    # k >= 1 stays z_s's -0
    Bz = np.array(B)
    Bz[0, :] = S
    out["fp32.b_B_zm"] = (me.f32w(Az.astype(np.float32)), me.f32w(Bz.astype(np.float32)),
                          f"E104's fp32.z_s (A = -0 at k>=1, E88's B at k>=1) with k=0 (1, S_j), S_j = b0 - R_j, R_j = sum_k>=1 B[k][j], b0 = {b0:g}: zero products hold C = n S_j > 0, b_B_wm's sums at every op's end; eff_sub as z_s's on every micro-op")
    Aw = np.full((16, 16), -1.0)
    Aw[:, 0] = 1.0
    Bw = np.array(B)
    Bw[0, :] = b0
    out["fp32.b_B_wm"] = (me.f32w(Aw.astype(np.float32)), me.f32w(Bw.astype(np.float32)),
                          f"A = -1 at k>=1, E88's B at k>=1 (z_s's); k=0 (1, {b0:g}): every product -B[k][j], exact; C walks to n S_j > 0; eff_sub as z_s's on every micro-op")
    meta["fp32"] = {"R_j": R.tolist(), "b0": b0, "S_j": S.tolist(), "max_C_at_launch_end": float(S.max() * LAUNCH_OPS), "two24": 2 ** 24}
    # ---- fp16
    aw, bw, A, B = zs["fp16"]
    w16 = e.w16
    nz = w16(-0.0, -0.0)
    assert np.all(aw[:, 1:] == nz) and np.all(aw[:, 0] == w16(2.0 ** 15, 2.0 ** 15)) and np.all(bw[0, :] == w16(2.0 ** 15, 2.0 ** 15))
    assert np.all(np.abs(B[1:, :, :]) == 1.0)
    R = column_sums("fp16", B)
    assert np.all(R % 2 == 0)
    b0 = float(max(R.max(), 0.0) + 2.0)
    S = b0 - R
    assert np.all(S >= 2.0) and np.all(S % 2 == 0)
    awz = np.array(aw)
    awz[:, 0] = w16(1.0, 1.0)
    bwz = np.array(bw)
    for j in range(16):
        bwz[0, j] = w16(S[j] / 2, S[j] / 2)
    out["fp16.b_B_zm"] = (awz, bwz, f"E104's fp16.z_s (A words (-0, -0) at k-group>=1, E90's fp16.signs B at k-group>=1) with k-group 0 (1, 1) x (S_j/2, S_j/2), S_j = b0 - R_j, R_j = one op's sum of B's elements at k-group>=1, b0 = {b0:g}: zero products hold C = n S_j > 0, b_B_wm's sums at every op's end; eff_sub1 and eff_sub2 as z_s's on every micro-op")
    aww = np.full((16, 16), w16(-1.0, -1.0), np.uint32)
    aww[:, 0] = w16(1.0, 1.0)
    bww = np.array(bw)
    bww[0, :] = w16(b0 / 2, b0 / 2)
    out["fp16.b_B_wm"] = (aww, bww, f"A words (-1, -1) at k-group>=1, fp16.z_s's B at k-group>=1; k-group 0 (1, 1) x ({b0 / 2:g}, {b0 / 2:g}): every product -B, exact; C walks to n S_j > 0; eff_sub1 and eff_sub2 as z_s's on every micro-op")
    meta["fp16"] = {"R_j": R.tolist(), "b0": b0, "S_j": S.tolist(), "max_C_at_launch_end": float(S.max() * LAUNCH_OPS), "two24": 2 ** 24}
    # ---- fp16, E108's design ported as it is
    Q = 2.0 + R
    awp = np.full((16, 16), w16(1.0, 1.0), np.uint32)
    bwp = np.array(bw)
    bwp[0, :] = w16(1.0, 1.0)
    out["fp16.b_B_w"] = (awp, bwp, "E108's b_B_w in fp16: A words (1, 1) at every k-group, fp16.z_s's B at k-group>=1, B words (1, 1) at k-group 0: C walks to n Q_j, Q_j = 2 + R_j, one value a column")
    awq = np.array(aw)
    awq[:, 0] = w16(1.0, 1.0)
    bwq = np.array(bw)
    for j in range(16):
        q = Q[j] / 2
        bwq[0, j] = w16(q, q) if q != 0 else nz
    out["fp16.b_B_z"] = (awq, bwq, "E108's b_B_z in fp16: E104's fp16.z_s (A words (-0, -0) at k-group>=1) with k-group 0 (1, 1) x (Q_j/2, Q_j/2), Q_j = 2 + R_j ((-0, -0) where Q_j = 0, so no word is raw zero): zero products hold C = n Q_j, b_B_w's sums at every op's end")
    meta["fp16_port"] = {"Q_j": Q.tolist(), "max_abs_C_at_launch_end": float(np.abs(Q).max() * LAUNCH_OPS)}
    for name, (wa, wb, rule) in out.items():
        assert np.all(np.asarray(wa) != 0) and np.all(np.asarray(wb) != 0), name     # no raw-zero word: the zero gate compares raw words (E93)
        out[name] = (np.asarray(wa, np.uint32), np.asarray(wb, np.uint32), rule)
    return out, meta


def expected_c(name, ty, raw, n):
    """What the design says C holds after n ops (the rule, independent of accum.c): n x one op's exact sum, every new tile."""
    aw, bw = me.words_from_tile(raw)
    A, B = me.elements(ty, aw, bw)
    S = me.per_op_sum(ty, A, B)
    return np.asarray(S * n, dtype=np.float32).view(np.uint32).reshape(256)


def build():
    accum = e.accum_binary()
    spec = {"experiment": "E128", "date": "2026-11-02", "generator": "tools/claims-v3/e128/make_e128.py", "power": list(POWER), "compare": list(COMPARE), "smoke": list(SMOKE),
            "matched": {k: list(v) for k, v in MATCHED.items()}, "readback": {}, "tiles": {}, "reused_from": {}, "groups": GROUPS}
    new, meta = new_designs()
    spec["design"] = meta
    names = [(n, "new") for n in NEW] + [(n, "reused") for n in REUSED]
    raws, rules = {}, {}
    for name, how in names:
        ty, kind = name.split(".")
        if how == "new":
            aw, bw, rule = new[name]
            raws[name] = me.tile_from_words(aw, bw)
        else:
            raws[name] = open(os.path.join(ROOT, REUSED[name], ty, kind + ".bin"), "rb").read()
            rule = f"{REUSED[name]}{ty}/{kind}.bin, byte for byte"
            spec["reused_from"][name] = REUSED[name] + f"{ty}/{kind}.bin"
        rules[name] = rule
    lens = {n: read_lengths(n) for n, _ in names}
    with ThreadPoolExecutor(int(os.environ.get("E104_JOBS", "3"))) as ex:
        list(ex.map(lambda nh: e.real_c(nh[0].split(".")[0], raws[nh[0]], tuple(lens[nh[0]]) + tuple(n - 1 for n in e.DP_NS), accum), names))
        list(ex.map(lambda nh: e.manual_c(nh[0].split(".")[0], raws[nh[0]], lens[nh[0]], accum), names))
    problems = []
    for name, how in names:
        ty, kind = name.split(".")
        raw = raws[name]
        st = mk.tile_stats(raw, ty)
        fa, fb = m90.sign_flips_per_op(raw, ty)
        real = e.real_c(ty, raw, lens[name], accum)
        man = e.manual_c(ty, raw, lens[name], accum)
        cnt = e.dp_counts(ty, raw, accum, list(e.DP_NS))
        spec["readback"][name] = list(lens[name])
        ent = {"type": ty, "kind": kind, "how": how, "rule": rules[name], "group": GROUPS[name], "file": f"tiles/{ty}/{kind}.bin", "bytes": len(raw), "sha256": e.sha(raw),
               "sha256_a": e.sha(raw[:1024]), "sha256_b": e.sha(raw[1024:]),
               "stats": {"gated_lane_frac": st["gated_lane_frac"], "bus_bits_per_op": st["bus_bits_per_op"], "sign_flips_per_op_a": fa, "sign_flips_per_op_b": fb},
               "counts_real": cnt, "read": {}}
        for n, v in real.items():
            f = e.fl_c(ty, raw, n)
            mv = man[n]
            ent["read"][str(n)] = {"rtl_hex": v.tobytes().hex(), "fl_hex": f.tobytes().hex(), "manual_hex": mv.tobytes().hex(), "words_rtl_vs_fl": int((v != f).sum()),
                                   "words_rtl_vs_manual": int((v != mv).sum()), "words_fl_vs_manual": int((f != mv).sum()),
                                   "distinct": {"rtl": len(set(v.tolist())), "fl": len(set(f.tolist())), "manual": len(set(mv.tolist()))},
                                   "c00": {"rtl": f"{int(v[0]):08x}", "fl": f"{int(f[0]):08x}", "manual": f"{int(mv[0]):08x}"}, "c08": {"rtl": f"{int(v[8]):08x}", "fl": f"{int(f[8]):08x}", "manual": f"{int(mv[8]):08x}"}}
            if int((v != f).sum()) or int((v != mv).sum()):
                problems.append(f"{name} n={n}: rtl!=fl {int((v != f).sum())}, rtl!=manual {int((v != mv).sum())}")
            if how == "new":
                want = expected_c(name, ty, raw, n)
                if not np.array_equal(v.view(np.float32), want.view(np.float32)):        # by value: a held +-0 may carry either sign
                    problems.append(f"{name} n={n}: accum.c differs from the design's sum on {int((v.view(np.float32) != want.view(np.float32)).sum())} words")
        spec["tiles"][name] = ent
        r = ent["read"][str(lens[name][-1])]
        print(f"{name:14s} {how:6s} bus {st['bus_bits_per_op']:6d} signflips A {fa:5d} B {fb:5d} alt {cnt['alt1']:7.1f} {cnt['alt2']:7.1f} cbus {cnt['cbus']:8.1f} rbus {cnt['rbus']:8.1f} "
              f"store {cnt['store']:8.1f} chg {cnt['chg']:.3f} words {r['distinct']['rtl']} C00 {r['c00']['rtl']} C08 {r['c08']['rtl']}", flush=True)
    for ty, trio in MATCHED.items():
        alts = [(spec["tiles"][n]["counts_real"]["alt1"], spec["tiles"][n]["counts_real"]["alt2"]) for n in trio]
        spec.setdefault("matched_alternations", {})[ty] = {n: list(a) for n, a in zip(trio, alts)}
        if len(set(alts)) != 1:
            problems.append(f"{ty}: the matched triple's alternations differ: {dict(zip(trio, alts))}")
    return spec, raws, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--designs-only", action="store_true", help="print the design numbers (column sums, b0, S_j) and stop: no accumulators")
    a = ap.parse_args()
    if a.designs_only:
        _, meta = new_designs()
        print(json.dumps(meta, indent=1))
        return
    spec, raws, problems = build()
    if a.check:
        bad = [n for n, r in raws.items() if open(os.path.join(OUT, spec["tiles"][n]["file"]), "rb").read() != r]
        old = json.load(open(os.path.join(OUT, "e128.json")))
        if old.get("tiles") != json.loads(json.dumps(spec["tiles"])):
            bad.append("e128.json tiles differ from the rebuild")
        print(json.dumps({"tiles": len(raws), "problems": bad, "readings_differ": problems}))
        sys.exit(1 if bad or problems else 0)
    for name, raw in raws.items():
        p = os.path.join(OUT, spec["tiles"][name]["file"])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(raw)
    json.dump(spec, open(os.path.join(OUT, "e128.json"), "w"), indent=1)
    print(json.dumps({"tiles": len(raws), "readings_differ": problems, "matched_alternations": spec.get("matched_alternations")}))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
